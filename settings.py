# create & download this file from https://code.google.com/apis/console/
SECRETS_FILE = 'client_secrets.json' 

# this string will look somewhat like the value to the left, and can be found in the 
# 'Calendar Address' section of 'Calendar Settings' in Google Calendar
CALENDAR_ID = 'sunlightfoundation.com_1a1234567890@resource.calendar.google.com' 

# Your timezone, as readable by pytz (http://pytz.sourceforge.net/)
TIMEZONE = 'US/Eastern'

try:
	from local_settings import * 
except Exception, e:
	pass
