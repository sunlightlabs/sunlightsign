Sunlight Sign
=============

Code for our BetaBrite conference room status sign. It pulls from a Google Calendar feed every minute and displays information about currently-occurring and upcoming meetings. This makes it easier to know what's going on, and to see when you can safely snag the conference room.


Requirements
------------

You should mostly be fine after running

> pip install -r requirements.txt

The exception is the alphasign library. Get it here: https://github.com/msparks/alphasign


Setup
-----

You'll need to get your Google API access in order, and to configure settings.py (or, optionally, to create local_settings.py to override the defaults).

* Head to https://code.google.com/apis/console/ and create a new authorized application. Your goal is to wind up with a client_secrets.json file (I suggest choosing 'web application' -- 'service application' is *not* what you want).

* You must then generate OAuth2 credentials. Do so by running `python gcal.py` on a machine with a web browser. Be sure to select an account that has access to the calendar! The result should be a calendar.dat file.

* You will also need to find the ID of your desired gCal. This is available on the calendar's settings page, near the "Calendar Address" heading.


Running
-------

> python sunlightsign.py


