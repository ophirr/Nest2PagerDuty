
import gmail
import json
import requests
from sekret import api_key, GNAME, GP, ROUTING_KEY, INCIDENT_KEY

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


g = gmail.login(GNAME, GP)

def trigger_incident():
    # Triggers a PagerDuty incident without a previously generated incident key
    # Uses Events V2 API - documentation: https://v2.developer.pagerduty.com/docs/send-an-event-events-api-v2

    header = {
        "Content-Type": "application/json"
    }

    payload = {  # Payload is built with the least amount of fields required to trigger an incident
        "routing_key": ROUTING_KEY,
        "event_action": "trigger",
        "dedup_key": INCIDENT_KEY,
        "class": "Security",
        "payload": {
            "summary": extsub,
            "source": "team20th Nest Infra",
            "severity": "warning"
        },
        "links": [{
            "href": nest_url,
            "text": "CLICK HERE to view the footage"
        }]
    }

    response = requests.post('https://events.pagerduty.com/v2/enqueue',
                             data=json.dumps(payload),
                             headers=header)

    if response.json()["status"] == "success":
        print('Incident Created')
    else:
        print(response.text)  # print error message if not successful


if not (g.logged_in):
    print '\n' + 'not logged in'
else :
    print '\n' + 'logged in, yay'

#unread = g.mailbox('NestAlerts').mail(unread = 'True', prefetch = 'True')
unread = g.mailbox('NestAlerts').mail(unread = 'True')


for number in unread:

    number.fetch()
    nest_html = number.html

    soup = BeautifulSoup(nest_html, features="html.parser")

    soup.find('a')
    for link in soup.find_all('a'):
        nest_url = link.get('href')
        break

    spans = soup.find_all('span')
    for span in spans:
        extsub = span.text
        break

    #print "URL - '" + nest_url + "'"
    #print "SUBJECT - '" + extsub  + "'"

    # Mark message as read
    number.read()

    trigger_incident()


if not unread:
    print "No new alerts, exiting" + "\n"
