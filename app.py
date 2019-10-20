#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-2.0-or-later
# See LICENSE.md for details

from quart import Quart
import aiohttp

app = Quart(__name__)

@app.route('/')
async def hello():
    return 'hello'

@app.route('/bills')
async def allbills():
    response = run_query(query)
    return response

headers = {"X-API-KEY": "***REMOVED***"}


def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://openstates.org/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        
# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.       
query = """
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
