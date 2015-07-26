import urllib2
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vCalAddress, vText, vDatetime
from dateutil.parser import parse as date_parser
from datetime import timedelta
from pytimeparse.timeparse import timeparse
import pytz

output_file = 'output/SGDQ.ics'
schedule_url = "https://gamesdonequick.com/schedule"
twitch_base_url = 'http://www.twitch.com/'


url_opener = urllib2.build_opener()
url_opener.addheaders = [('User-agent', 'Mozilla/5.0')]

html_doc = url_opener.open(schedule_url).read()

soup = BeautifulSoup(html_doc, 'html.parser')

#Parse column name
column_name = []
for column in soup.thead.find_all('td'):
    column_name.append(column.string.lower())

#Parse events
events = []
run_table = soup.find(id='runTable')
for row in run_table.find_all('tr'):
    event = {}
    for i, column in enumerate(row.find_all('td')):
        event[column_name[i]] = column.string
    events.append(event)


#Write iCal
calendar = Calendar()
calendar.add('prodid', 'GDQ Summer 2015 Schedule')
calendar.add('version', '2.0')

def event_add(ical_event, key, value):
    if key and value:
        ical_event[key] = value

def remove_spaces(s):
    return s.replace(" ", "")

for event in events:
    ical_event = Event()

    comment = '({})'.format(event['comments']) if event['comments'] and event['comments'] != "" else ""
    event_add(ical_event, 'summary', '[{}] {} {} by {}'.format(event['console'], event['game'], comment, event['runners']))

    start_time = pytz.timezone('America/Chicago').localize(date_parser(event['date and time'])).astimezone(pytz.utc)
    event_add(ical_event, 'dtstart', vDatetime(start_time))

    setup_in_seconds = timeparse(event['setup'])
    estimate_in_seconds = timeparse(event['estimate'])
    end_time = start_time + timedelta(seconds=estimate_in_seconds+setup_in_seconds)
    event_add(ical_event, 'dtend', vDatetime(end_time))

    twitch_links = []
    if event['twitch channels']:
        twitch_links = [twitch_base_url + streamer for streamer in map(remove_spaces, event['twitch channels'].split(","))]
        event_add(ical_event, 'location', '\n'.join(twitch_links))

    runners = [runner for runner in map(remove_spaces, event['runners'].split(","))]
    runner_links = ['LINK:' + twitch_base_url + streamer for streamer in runners]
    organizer = vCalAddress(','.join(runner_links))
    organizer.params['cn'] = vText(', '.join(runners))
    event_add(ical_event, 'organizer', organizer)

    event_add(ical_event, 'uid', event['game'] + '@gdq')

    event_details = [
        ('Game', event['game']),
        ('Runners', event['runners']),
        ('Console', event['console']),
        ('Estimate', event['estimate'] + ' (Setup: {})'.format(event['setup'])),
        ('Comments', event['comments']),
        ('Couch Commentators', event['couch commentators']),
        ('Prizes', event['prizes']),
        ('Twitch Channels', ' '.join(twitch_links)),
    ]
    formatted_events = '\n'.join(["{}: {}".format(a, b) for a, b in event_details if b])
    event_add(ical_event, 'description', formatted_events)

    calendar.add_component(ical_event)


f = open(output_file, 'wb')
f.write(calendar.to_ical())
f.close()

print 'Wrote calendar to: ' + output_file

