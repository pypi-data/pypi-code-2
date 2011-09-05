# coding: utf-8
"""
Helpers to properly print date and time (strftime replacement).
"""
months = {
    "english": (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ),
    # TODO: Use gettext (or similar)
    "german": (
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember",
    ),
}

# TODO: weekdays


formatables = (
    "year",
    "month", "month_name",
    "day", "day_suffixed",
    "weekday", # "weekday_name",
    "hour",
    "minute",
    "second",

    # uaah
    "ctime",
    "isocalendar",
    "isoformat",
    "isoweekday",
)


# TODO: be a true replacement for datetime altogether
class FormatableDatetime(object):
    """
    Holds attrs for formatable datetimes
    """
    def __init__(self, datetime, language="english"):
        self.datetime = datetime
        self._language = language
    
    def get_language(self):
        return self._language.lower()
    def set_language(self, language):
        self._language = language
    def del_language(self):
        self._language = "english"

    language = property(get_language, set_language, del_language)

    @property
    def month_name(self):
        return months[self.language][self.datetime.month-1]
    # Same for weekdays
    
    @property
    def day_suffixed(self):
        """
        Author: Michael Brickenstein
        """
        day = self.datetime.day
        if self.language != "english": return str(day)

        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            # white magic
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return str(day) + suffix

    def __getattr__(self, attr):
        return getattr(self.datetime, attr)

    def __dir__(self):
        return dir(self.__class__) + self.__dict__.keys() + dir(self.datetime)

    def format(self, str):
        """
        Format the str using self's attrs
        """
        # white magic
        attrs = dict(((attr, getattr(self,attr)) for attr in dir(self) if attr in formatables))
        return str.format(**attrs)
        

def format_datetime(datetime, str, language="english"):
    """
    Return the formatted string using the datetime object.

    Works with datetime.datetime, datetime.date.
    (not for datetime.time yet)

    >>> import datetime
    >>> format_datetime(datetime.date(2011, 9, 5), "{month_name} {day_suffixed}, {year}")
    'September 5th, 2011'
    """
    return FormatableDatetime(datetime, language).format(str)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
