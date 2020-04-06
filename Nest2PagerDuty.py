
import gmail
import json
import requests
import re

from sekret import api_key, GNAME, GP, ROUTING_KEY, INCIDENT_KEY

extsub = ''
nest_url = ''

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

# Login to gmail, yes this mechanism is insecure
g = gmail.login(GNAME, GP)

def trigger_nest_incident():
    # Triggers a PagerDuty incident without a previously generated incident key
    # Uses Events V2 API - documentation: https://v2.developer.pagerduty.com/docs/send-an-event-events-api-v2

    header = {
        "Content-Type": "application/json"
    }

    payload = {  # Payload is built with the least amount of fields required to trigger an incident
        "routing_key": ROUTING_KEY,
        "event_action": "trigger",
        "dedup_key": INCIDENT_KEY,
        "payload": {
            "summary": extsub,
            "source": "Nest Camera Infra",
            "severity": "warning",
            "class": "security"
        },
        "links": [{
            "href": nest_url,
            "text": ">>> CLICK HERE to view the footage <<<"
        }]

    }

    response = requests.post('https://events.pagerduty.com/v2/enqueue',
                             data=json.dumps(payload),
                             headers=header)

    if response.json()["status"] == "success":
        print('Incident Created')
    else:
        print(response.text)  # print error message if not successful



def trigger_sar_incident():
    # Triggers a PagerDuty incident without a previously generated incident key
    # Uses Events V2 API - documentation: https://v2.developer.pagerduty.com/docs/send-an-event-events-api-v2

    header = {
        "Content-Type": "application/json"
    }

    payload = {  # Payload is built with the least amount of fields required to trigger an incident
        "routing_key": ROUTING_KEY,
        "event_action": "trigger",
        "dedup_key": INCIDENT_KEY,
        "payload": {
            "summary": extsub,
            "source": "KCSAR",
            "severity": "critical",
            "class": "search and rescue"
        }
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


    if number.fr == "Team20th <notifications@nest.com>":
        if nest_html is not None:
            soup = BeautifulSoup(nest_html, features="html.parser")

            for link in soup.findAll('a', attrs={'href': re.compile("^https://home.nest.com/camera")}):
       #     print link.get('href')
                nest_url = link.get('href')


            spans = soup.find_all('span')
            for span in spans:
                extsub = span.text
                break

       #

    # Let's check out any attachments
    #goodies = number.attachments
    #image = goodies[0]
    #print "URL - '" + nest_url + "'"
    #print "SUBJECT - '" + extsub  + "'"

        trigger_nest_incident()

    else:

        extsub = number.body
        trigger_sar_incident()

 # Mark message as read
    number.read()




if not unread:
    print "No new alerts, exiting" + "\n"
