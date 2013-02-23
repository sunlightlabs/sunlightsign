import gflags
import httplib2
import datetime
import pytz
from settings import *

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

def get_service_credentials():
		
	FLAGS = gflags.FLAGS

	# Set up a Flow object to be used if we need to authenticate. This
	# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
	# the information it needs to authenticate. Note that it is called
	# the Web Server Flow, but it can also handle the flow for native
	# applications
	# The client_id and client_secret are copied from the API Access tab on
	# the Google APIs Console
	FLOW = flow_from_clientsecrets(SECRETS_FILE, scope='https://www.googleapis.com/auth/calendar', redirect_uri='http://example.com/auth_return')

	# To disable the local server feature, uncomment the following line:
	# FLAGS.auth_local_webserver = False

	# If the Credentials don't exist or are invalid, run through the native client
	# flow. The Storage object will ensure that if successful the good
	# Credentials will get written back to a file.
	storage = Storage('calendar.dat')
	credentials = storage.get()
	if credentials is None or credentials.invalid == True:
		credentials = run(FLOW, storage)

	# Create an httplib2.Http object to handle our HTTP requests and authorize it
	# with our good Credentials.
	http = httplib2.Http()
	http = credentials.authorize(http)

	# Build a service object for interacting with the API. Visit
	# the Google APIs Console
	# to get a developerKey for your own application.
	service = build(serviceName='calendar', version='v3', http=http)

	return service

def get_events(start=None, end=None):
	start = start is not None and start or datetime.datetime.now(tz=pytz.timezone(TIMEZONE))
	end = end is not None and end or start + datetime.timedelta(days=7)

	service = get_service_credentials()
	events = service.events().list(calendarId=CALENDAR_ID, singleEvents=True, timeMin=start.isoformat(), timeMax=end.isoformat()).execute()
	return events

if __name__ == '__main__':
	get_service_credentials()