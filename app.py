#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-2.0-or-later
# See LICENSE.md for details

import os
import login
import requests
from flask import Flask

app = Flask(__name__, template_folder="templates")
app.register_blueprint(login.bp)

@app.route('/')
def hello():
	return 'hello'

@app.route('/bills')
def allbills():
	response = run_query(QUERY)
	return response

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

if __name__ == '__main__':
	app.run()
