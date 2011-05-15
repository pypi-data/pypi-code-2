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

# Delete rows 1,2
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.RowIndex(column=[],
                  table=0,
                  status="active",
                  drop=False,
                  indices=[0,1])])))

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

# Transpose table
w.add(dw.Transpose(column=[],
                   table=0,
                   status="active",
                   drop=False))

# Fill transpose  with values from above
w.add(dw.Fill(column=["transpose"],
              table=0,
              status="active",
              drop=False,
              direction="down",
              method="copy",
              row=None))

# Fill transpose1  with values from above
w.add(dw.Fill(column=["transpose1"],
              table=0,
              status="active",
              drop=False,
              direction="down",
              method="copy",
              row=None))

w.apply_to_file('migration.csv').print_csv('out.csv')
