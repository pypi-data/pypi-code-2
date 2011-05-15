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

# Fill extract  with values from above
w.add(dw.Fill(column=["extract"],
              table=0,
              status="active",
              drop=False,
              direction="down",
              method="copy",
              row=None))

# Delete  rows where split contains 'Reported'
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.Contains(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  lcol="split",
                  value="Reported",
                  op_str="contains")])))

# Set  split  name to  Year
w.add(dw.SetName(column=["split"],
                 table=0,
                 status="active",
                 drop=True,
                 names=["Year"],
                 header_row=None))

# Set  extract  name to  State
w.add(dw.SetName(column=["extract"],
                 table=0,
                 status="active",
                 drop=True,
                 names=["State"],
                 header_row=None))

# Set  split1  name to  Crime
w.add(dw.SetName(column=["split1"],
                 table=0,
                 status="active",
                 drop=True,
                 names=["Crime"],
                 header_row=None))

w.apply_to_file('crime.csv').print_csv('out.csv')
