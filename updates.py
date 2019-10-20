#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-2.0-or-later
# See LICENSE.md for details
import psycopg2
import os
import login
from login import db
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def check_updates():
	with db().cursor() as cur:
		cur.execute("select bill_id, last_action from bills")
		bills = cur.fetchall()
		for bill in bills:
			query = f'{{ bill(jurisdiction: "Illinois", session: "101st", identifier: "{bill.bill_id}" {{ actions {{ description \n order }} }} }}'
			result = run_query(query)
			actions = sorted(result['data']['bill']['actions'], key=lambda x: x['order'])
			action = actions[len(actions)-1] #TODO: see other todo for identical line
			new_desc = action['description']
			if new_desc != bill.last_action:
				cur.execute("update bills set last_action = %s where bill_id = %s", [new_desc, bill_id])
				sendUpdateEmail(bill_id)

            

# TODO set User-Agent too
# TODO use g.session
HEADERS = {'X-API-KEY': os.environ['OPENSTATES_API_KEY']}

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
	request = requests.post('https://openstates.org/graphql', json={'query': query}, headers=HEADERS)
	if request.status_code == 200:
		return request.json()
	else:
		raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

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

if __name__ == '__main__':
	check_updates()
