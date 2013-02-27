import os, sys, time, signal, datetime
import gcal
import dateutil.parser
import pytz
import alphasign
from settings import *

PID_FILE = 'sunlightsign.pid'
s = None # placeholder variable for sign        
log_target = None

class SunlightSign():

    UPDATE_INTERVAL = 60 # in seconds
    SUNLIGHT_ORANGE = alphasign.colors.rgb('E4701E')
    #SUNLIGHT_ORANGE = alphasign.colors.ORANGE
    MAX_MESSAGE_LENGTH = 126 # this seems to be a betabrite limitation

    def __init__(self, log_target=sys.stdout, debug=False):

        # initialize member variables        
        self.last_run = 0                   # last time we tried to update the sign
        self.sign_text = ""                 # used to tell whether the sign's text needs to be changed
        self.log_target = debug and sys.stdout or log_target
        self.in_loop = False
        self.shutting_down = False
        self.debug = debug


    def log(self, s):
        if self.log_target is None:
            return
            
        t = datetime.datetime.now().timetuple()
        self.log_target.write("%s %s.%d - %s\n" % ('-'.join(map(str, t[0:3])), ':'.join(map(lambda x: "%02d" % x, t[3:6])), t[7], s))
        self.log_target.flush()
        
    def setup(self):
        """ Sets initial sign conditions. Will result in a pause -- run only when necessary to reset the sign's mode. """

        if self.debug:
            return

        self.log("Initializing...")

        # open USB connection to sign
        self.sign = alphasign.USB(alphasign.devices.USB_BETABRITE_PRISM)
        self.sign.connect()
        self.sign.clear_memory()       
        self.sign.beep()

        # set up content and its container
        content = alphasign.String(size=255, label="A")
        content.data = "Welcome to the %sSunlight Foundation" % self.SUNLIGHT_ORANGE
        container = alphasign.Text(("%s%s" % (alphasign.charsets.SEVEN_HIGH_STD, content.call())), label="1", mode=alphasign.modes.ROTATE)

        # allocate memory for these objects on the sign
        self.sign.allocate((content, container))

        # tell sign to only display the single container object
        self.sign.set_run_sequence((container,))        

        # upload objects
        for obj in (content, container):
            self.sign.write(obj)

        self.log("Finished initialization.")
        
        
    def disconnect(self, *args, **kwargs):
        # don't shut down while things are still happening - this produces writes to closed files, among other things    
        self.shutting_down = True
        while self.in_loop:
            time.sleep(1)

        if self.debug:
            return
            
        self.log("Closing USB connection to sign...")
        self.sign.disconnect()
        self.log("Finished closing connection.")
        
    def _make_event_display_string(self, event):
        (summary, start, end) = event
        return "%s / %d:%02d-%d:%02d" % (summary, start.hour % 12, start.minute, end.hour % 12, end.minute)

    def _process_gcal_events(self, events):
        processed_events = []
        for e in events.get('items', []):
            processed_events.append((e.get('summary', 'TITLE NOT FOUND'), dateutil.parser.parse(e['start']['dateTime']), dateutil.parser.parse(e['end']['dateTime'])))
        processed_events.sort(key=lambda x:x[1])
        return processed_events

    def generate_message(self):
        now = datetime.datetime.now(tz=pytz.timezone(TIMEZONE))      

        self.log("Regenerating message at %s" % str(now))

        self.log("Fetching events")
        gcal_events = gcal.get_events()
        events = self._process_gcal_events(gcal_events)
        self.log("Done fetching events")
        
        for (i, event) in enumerate(events):
            (summary, start, end) = event
            
            if now>start and now<end:
                t = "%s%s" % (self.SUNLIGHT_ORANGE, self._make_event_display_string(event))
                if (i+1<len(events)):
                    (next_summary, next_start, next_end) = events[i+1]
                    # only append the "next meeting" string if the next meeting occurs less than one day from now
                    next_meeting_in = (next_start - start).seconds
                    if next_meeting_in < (8*60):
                        if next_meeting_in>3600:
                            color = alphasign.colors.GREEN
                        elif next_meeting_in>1200:
                            color = alphasign.colors.YELLOW
                        else:
                            color = alphasign.colors.RED
                        t += "              %sNEXT MEETING: %s" % (color, self._make_event_display_string(events[i+1]))
                return t
                
            elif now<start:
                d = start - now
                parts = [('d', lambda x: x.days), ('h', lambda x: x.seconds/3600), ('m', lambda x: ((x.seconds/60)%60))]
                result = []
                for (label, func) in parts:
                    val = func(d)
                    if val>0:
                        result.append("%d%s" % (val, label))

                if len(result)==0:
                    result.append('0m')

                if d.seconds>3600:
                    color = alphasign.colors.GREEN
                elif d.seconds>1200:
                    color = alphasign.colors.YELLOW
                else:
                    color = alphasign.colors.RED        

                return "%s%s in %s" % (color, summary, " ".join(result))        

        return "%sError: could not retrieve calendar data" % alphasign.colors.RED


    def set_message(self, t):
        """ sets the sign text (if necessary) """
        
        # only update the sign if there's been a change in its content (minimizes pauses)
        if t!=self.sign_text:
        
            self.log("Setting sign message to '%s'" % t)

            # create logical objects to work with
            content = alphasign.String(size=min(len(t), self.MAX_MESSAGE_LENGTH), label="A")
            content.data = t[:self.MAX_MESSAGE_LENGTH]
        
            # display the object
            if not self.debug:
                self.sign.write(content)

            # update record of text
            self.sign_text = t

            self.log("Finished updating sign text.")

        else:
                        
            self.log("Asked to set sign text to '%s', but it appears to already be set to that." % t)

        
    def run(self):        
        """ main loop """
    
        while not self.shutting_down:
            
            self.in_loop = True
            
            if (time.time() - self.last_run) > self.UPDATE_INTERVAL:
                # update time here to account for the slowness of generate_status() -- otherwise cycle would be 60s + t(rest of this loop)
                self.last_run = time.time() 
                
                # regenerate the sign text
                t = self.generate_message()

                # update sign with the results
                self.set_message(t)                    
            
            self.in_loop = False
            
            time.sleep(1)
        
        
def terminate(*args, **kwargs):
    # hang up USB connection
    if s is not None:
        s.disconnect()

    # close log file
    if log_target is not None:
        log_target.close()

    # remove pid file
    try:
        os.unlink(PID_FILE)
    except:
        pass
    
      
if __name__ == '__main__':

    if '--test' in sys.argv:
        import doctest
        sys.exit(doctest.testmod())
        

    if '--debug' in sys.argv:
        pid = False
    else:
        pid = os.fork()

    if pid:
        f = open(PID_FILE,'w')
        f.write(str(pid))
        f.close()

    else:        
        # clean up on process death
        signal.signal(signal.SIGTERM, terminate)
        signal.signal(signal.SIGHUP, terminate)             
        signal.signal(signal.SIGINT, terminate)
        
        log_target_name = len(sys.argv)>2 and sys.argv[2] or None
        if log_target_name is not None:
            log_target = open(log_target_name,'a')
        elif '--debug' in sys.argv:
            log_target = sys.stdout

        s = SunlightSign(log_target=log_target, debug=('--debug' in sys.argv))
        s.setup()
        s.run()
