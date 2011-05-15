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

# Delete empty rows
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.Empty(column=[],
               table=0,
               status="active",
               drop=False)])))

# Extract from split after 'in '
w.add(dw.Extract(column=["split"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on=".*",
                 before=None,
                 after="in ",
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Fill extract  with values from below
# (here is where this test differs from crime_5.py)
w.add(dw.Fill(column=["extract"],
              table=0,
              status="active",
              drop=False,
              direction="up",
              method="copy",
              row=None))

w.apply_to_file('crime.csv').print_csv('out.csv')
