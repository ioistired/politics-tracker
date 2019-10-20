#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-2.0-or-later
# See LICENSE.md for details
import psycopg2
import os
import jinja2
import login
from flask_login import LoginManager, current_user
import requests
from flask import Flask, render_template
from flask_nav.elements import Navbar, View
from flask_nav import Nav
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__, template_folder="templates", static_url_path='', 
            static_folder='static',)

topbar = Navbar('',
	View('Home', 'frontend.index'),
	View('Your Account', 'frontend.account_info'),
)

nav = Nav()
nav.register_element('top', topbar)
nav.init_app(app)

app.register_blueprint(login.bp)
with open('secret_key.txt') as f:
    app.secret_key = f.read().strip()
login_manager = LoginManager()
login_manager.init_app(app)

conn = psycopg2.connect("dbname=politics user=postgres")
cur = conn.cursor()

@login_manager.user_loader
def load_user(user_id):
    cur.execute("select * from users where user_email = %s", [user_id])
    if cur.fetchone() != None:
        return login.User(True, True, False, user_id);

app.jinja_env.line_statement_prefix = '-- :'  # for SQL
app.jinja_env.loader = jinja2.ChoiceLoader([  # try templates/ first then sql/
	jinja2.FileSystemLoader('templates'),
])

with open('secret_key.txt') as f:
	app.secret_key = f.read().strip()

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/bills')
def allbills():
	response = run_query(QUERY)
	return response

@app.route('/bill/<bill_id>', methods=['POST'])
def follow(bill_id):
    if (current_user.is_authenticated):
        user_id = current_user.get_id()
        cur.execute(f'INSERT INTO preferred_bills VALUES (%s, %s);',[user_id,bill_id])
        conn.commit()
        return 'followed ' + bill_id + '!'

@app.route('/bill/<bill_id>')
def onebill(bill_id):
    # TODO: sanitize input
    bill = run_query(f"""
{{
	bill(jurisdiction: "Illinois", session: "101st", identifier: "{bill_id}") {{
		title
		sources {{
			url
		}}
		abstracts {{
			abstract
		}}
                actions {{
                        description
                        date
                        
                }}
	}}
}}
""")['data']['bill']
        
    title = bill['title']
    abstract = bill['abstracts'][0]['abstract']
    action_desc = bill['actions'][0]['description']
    action_date = bill['actions'][0]['date']
    # TODO: use url to get full bill text
    url = bill['sources'][0]['url']
    sendUpdateEmail(bill_id)
    return render_template('bill.html', title=title, abstract=abstract, action_desc=action_desc, action_date=action_date)

# TODO set User-Agent too
# TODO use g.session
HEADERS = {'X-API-KEY': os.environ['OPENSTATES_API_KEY']}

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
	request = requests.post('https://openstates.org/graphql', json={'query': query}, headers=HEADERS)
	if request.status_code == 200:
		return request.json()
	else:
		raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.
QUERY = """
{
  bills(jurisdiction: "Illinois", session: "101st", first: 20) {
	edges {
		node {
			title
			identifier
			otherTitles {
				title
				note
			}
			subject
			sources {
			  url
			}
			createdAt
			updatedAt
		}
	}
  }
}
"""

def sendUpdateEmail(bill_id):
    # TODO: sanitize input
    bill = run_query(f"""
{{
	bill(jurisdiction: "Illinois", session: "101st", identifier: "{bill_id}") {{
		identifier
		sources {{
			url
		}}
		actions {{
                        date
			description
		}}
	}}
}}
""")['data']['bill']
	
    ide = bill['identifier']
    date = bill['actions'][-1]['date']
    action = bill['actions'][-1]['description']
    # TODO: use url to get full bill text
    url = bill['sources'][0]['url']

    message = Mail(
        from_email='apeck2@hawk.iit.edu',
        to_emails=current_user.get_id(),
        subject='A bill you are following has been updated',
        html_content='<h1>' + ide + '</h1><p>New action has been taken on ' + ide + '</p><p>On ' + date + ', the following action occurred:</p><p>' + action + '</p>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

    #return render_template('index.html')




if __name__ == '__main__':
	app.run()
