# The example from Figure 6 of Harris and Gulwani's PLDI 2011 paper

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

# Fold split1, split2  using  1 as a key
w.add(dw.Fold(column=["split1","split2"],
              table=0,
              status="active",
              drop=False,
              keys=[0]))

# Drop fold
w.add(dw.Drop(column=["fold"],
              table=0,
              status="active",
              drop=True))

w.apply_to_file('pldi-figure-6.csv').print_csv('out.csv')
