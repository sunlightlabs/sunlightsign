# create & download this file from https://code.google.com/apis/console/
SECRETS_FILE = 'client_secrets.json' 
OAUTH_TOKEN_FILE = 'calendar.dat'

# this string will look somewhat like the value to the left, and can be found in the 
# 'Calendar Address' section of 'Calendar Settings' in Google Calendar
CALENDAR_ID = 'sunlightfoundation.com_1a1234567890@resource.calendar.google.com' 

# Your timezone, as readable by pytz (http://pytz.sourceforge.net/)
TIMEZONE = 'US/Eastern'

# how many days into the future the app should look for upcoming meetings
MAX_DAYS_FORWARD = 7

# overkill, but I know I'll wind up committing our actual calendar ID if I don't
try:
	from local_settings import * 
except Exception, e:
	pass
