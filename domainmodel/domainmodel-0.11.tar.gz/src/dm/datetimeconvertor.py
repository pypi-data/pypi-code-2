import mx.DateTime
import datetime
import re as sre
import dm.times

class DateTimeConvertor(object):  
    "Converts between HTML (string) and Python (mx.DateTime.DateTime)."
        
    acceptableFormats = [
        "%H:%M:%S %d-%m-%Y",
        "%H:%M:%S %d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%H:%M %d-%m-%Y",
        "%H:%M %d/%m/%Y",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m",
        "%Y/%m",
        "%m-%Y",
        "%m/%Y",
        "%Y",
    ]
    normalFormat = "%Y-%m-%d %H:%M:%S"
    labelFormat = "%H:%M:%S, %a %e %b, %Y"
    
    def fromHTML(self, dateHtml):
        if dateHtml in ['', None]:
            return None
        if type(dateHtml) in [str, unicode]:
            if 'now' == dateHtml.strip():
                return dm.times.getLocalNow()
            dateTime = self.generouslyParse(dateHtml)
            if dateTime == None:
                msg = "Couldn't accept '%s' for a DateTime." % dateHtml
                raise Exception, msg
            else:
                return dateTime
        day, month, year = None, None, None
        min, hour = None, None
        if type(dateHtml) == datetime.date:
            day, month, year = dateHtml.day, dateHtml.month, dateHtml.year
            sec, min, hour = (0, 0, 0)
        elif type(dateHtml) == datetime.datetime:
            day = int(dateHtml.day)
            month = int(dateHtml.month)
            year = int(dateHtml.year)
            sec = int(dateHtml.second)
            min = int(dateHtml.minute)
            hour = int(dateHtml.hour)
        else:
            msg = "Unsupported date input type: %s" % type(dateHtml)
            raise Exception(msg)
        return mx.DateTime.DateTime(year, month, day, hour, min, sec)


    def toHTML(self, dateTimeObject):
        if dateTimeObject in ['', None]:
            return ''
        return dateTimeObject.strftime(self.normalFormat)

    def toLabel(self, dateTimeObject):
        if dateTimeObject in ['', None]:
            return ''
        return dateTimeObject.strftime(self.labelFormat)

    def generouslyParse(self, string):
        dateTime = None
        for format in self.acceptableFormats:
            try:
                dateTime = mx.DateTime.strptime(string, format)
            except:
                pass
        return dateTime


class RDateTimeConvertor(DateTimeConvertor):  
    normalFormat = "%H:%M:%S %d-%m-%Y"

class RNSDateTimeConvertor(DateTimeConvertor):  
    normalFormat = "%H:%M %d-%m-%Y"
    labelFormat = "%H:%M, %a %e %b, %Y"

class DateConvertor(DateTimeConvertor):  
    normalFormat = "%Y-%m-%d"
    labelFormat = "%a, %e %b, %Y"

class RDateConvertor(DateConvertor):  
    normalFormat = "%d-%m-%Y"
    labelFormat = "%a, %e %b, %Y"

class DateOfBirthConvertor(RDateConvertor):  
    normalFormat = "%d-%m-%Y"
    labelFormat = "%d/%m/%Y"

