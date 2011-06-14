from zarkov import model

def setup_time_aggregates(object_collection='event'):
    model.AggDef.query.remove()
    defs = dict(
        sum_by_second='this.timestamp.getSeconds()',
        sum_by_minute='this.timestamp.getMinutes()',
        sum_by_hour='this.timestamp.getHours()',
        sum_by_date='''{y:this.timestamp.getFullYear(),
          m:this.timestamp.getMonth(),
          d:this.timestamp.getDate()}''',
        sum_by_month='''{y:this.timestamp.getFullYear(),
          m:this.timestamp.getMonth()}''',
        sum_by_year='''this.timestamp.getFullYear()''')
    for name, key in defs.iteritems():
        model.AggDef.simple_count(object_collection, name, key)

    model.orm_session.flush()
