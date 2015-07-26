import urllib2
from bs4 import BeautifulSoup


print 'Starting up'

schedule_url = "https://gamesdonequick.com/schedule"


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
for row in run_table.find_all('tr')[:5]:
    event = {}
    for i, column in enumerate(row.find_all('td')):
        event[column_name[i]] = column.string
    events.append(event)



