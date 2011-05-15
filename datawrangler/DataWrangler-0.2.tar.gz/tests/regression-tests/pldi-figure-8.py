# The example from Figure 8 of Harris and Gulwani's PLDI 2011 paper

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

# Fill split  with values from above
w.add(dw.Fill(column=["split"],
              table=0,
              status="active",
              drop=False,
              direction="down",
              method="copy",
              row=None))

# Unfold split1  on  split2
w.add(dw.Unfold(column=["split1"],
                table=0,
                status="active",
                drop=False,
                measure="split2"))

w.apply_to_file('pldi-figure-8.csv').print_csv('out.csv')
