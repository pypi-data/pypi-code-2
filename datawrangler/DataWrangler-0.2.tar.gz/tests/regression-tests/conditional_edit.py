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

# Edit data  rows where data = 'Women'  to ' WOMEN '
w.add(dw.Edit(column=["data"],
              table=0,
              status="active",
              drop=False,
              result="column",
              update=True,
              insert_position="right",
              row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.Eq(column=[],
            table=0,
            status="active",
            drop=False,
            lcol="data",
            value="Women",
            op_str="=")]),
              on=None,
              before=None,
              after=None,
              ignore_between=None,
              which=1,
              max=1,
              positions=None,
              to="WOMEN",
              update_method=None))

w.apply_to_file('men-women.csv').print_csv('out.csv')
