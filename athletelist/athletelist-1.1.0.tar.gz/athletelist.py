class AthleteList(list):
    """Represents the concept of an Athlete derived from a list with
    the following additional attributes:
        name: Name of athlete
        dob:  The date of birther of athlete
    """
    def __init__(self, a_name, a_dob=None, a_times=[]):
        list.__init__([])
        self.name = a_name
        self.dob = a_dob
        self.extend(a_times)
        
    def top3(self):
        #Gets the top 3 times for this athlete
        return(sorted(set([sanitize(x) for x in self]))[0:3])

def sanitize(run_time):
    """Sanitizes the 'run_time' parameter by replacing ':' and '-' with '.'
       to make sure input data is consistent"""
    if "-" in run_time:
        token = "-"
    elif ":" in run_time:
        token = ":"
    else:
        return(run_time)

    (mins, secs) = run_time.split(token)
    return(mins + "." + secs)
