import TheSubDB
import BierDopje
import logging

logging.basicConfig(level=logging.DEBUG)

filename = "/burn/30.Rock.S05E16.HDTV.XviD-LOL.avi"

p = TheSubDB.TheSubDB(None, None)
subfname = filename[:-3]+"srt"
logging.info("Processing %s" % filename)
subs = p.process(filename, ["en", "pt"])

print subs

if not subs:
    p.uploadFile(filename, subfname, 'en')
    subs = p.process(filename, ["en", "pt"])
    print subs


#bd = BierDopje.BierDopje()
#subs = bd.process(filename, ["en"])



