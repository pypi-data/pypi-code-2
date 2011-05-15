from wrangler import dw

w = dw.DataWrangler()

# Split data repeatedly on newline  into  rows
w.add(dw.Split(column=["data"],
               table=0,
               status="active",
               drop=True,
               result="row",
               update=False,
               insert_position="right",
               row=None,
               on="\n",
               before=None,
               after=None,
               ignore_between=None,
               which=1,
               max=0,
               positions=None,
               quote_character=None))

# Split data repeatedly on ','
w.add(dw.Split(column=["data"],
               table=0,
               status="active",
               drop=True,
               result="column",
               update=False,
               insert_position="right",
               row=None,
               on=",",
               before=None,
               after=None,
               ignore_between=None,
               which=1,
               max=0,
               positions=None,
               quote_character=None))

# Cut from split on ' any word  '
w.add(dw.Cut(column=["split"],
             table=0,
             status="active",
             drop=False,
             result="column",
             update=True,
             insert_position="right",
             row=None,
             on="[a-zA-Z]+ ",
             before=None,
             after=None,
             ignore_between=None,
             which=1,
             max=1,
             positions=None))

w.apply_to_file('crime.csv').print_csv('out.csv')
