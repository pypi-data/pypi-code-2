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

# Fill  rows 1,2,3 with values from the left
w.add(dw.Fill(column=[],
             table=0,
             status="active",
             drop=False,
             direction="right",
             method="copy",
             row=dw.Row(column=[],
            table=0,
            status="active",
            drop=False,
            conditions=[dw.RowIndex(column=[],
                 table=0,
                 status="active",
                 drop=False,
                 indices=[0,1,2])])))

# Fold split1, split2, split3, split4...  using  1, 2, 3  as keys
w.add(dw.Fold(column=["split1","split2","split3","split4","split5","split6","split7","split8","split9","split10","split11","split12","split13","split14","split15","split16"],
             table=0,
             status="active",
             drop=False,
             keys=[0,1,2]))

w.apply_to_file('migration.csv').print_csv('out.csv')
