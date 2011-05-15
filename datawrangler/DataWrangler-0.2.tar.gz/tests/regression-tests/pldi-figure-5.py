# The example from Figure 5 of Harris and Gulwani's PLDI 2011 paper

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

# Delete  rows where split2 is null
w.add(dw.Filter(column=[],
                table=0,
                status="active",
                drop=False,
                row=dw.Row(column=[],
             table=0,
             status="active",
             drop=False,
             conditions=[dw.IsNull(column=[],
                table=0,
                status="active",
                drop=False,
                lcol="split2",
                value=None,
                op_str="is null")])))

# Drop split4
w.add(dw.Drop(column=["split4"],
              table=0,
              status="active",
              drop=True))

# Drop split1
w.add(dw.Drop(column=["split1"],
              table=0,
              status="active",
              drop=True))

w.apply_to_file('pldi-figure-5.csv').print_csv('out.csv')
