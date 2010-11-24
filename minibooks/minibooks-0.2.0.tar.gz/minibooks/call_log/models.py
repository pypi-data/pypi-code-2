from django.db import models
import logging
import psycopg2
import psycopg2.extensions

# Create your models here.

#class Call(models.Model):
#    call_start = models.DateTimeField()
#    call_end = models.DateTimeField()
#    caller_id = models.CharField()
#    number_from = models.CharField()
#    number_to = models.CharField()

class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        logger.info(self.mogrify(sql, args))

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception, exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise
