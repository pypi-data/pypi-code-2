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

# Fold split1, split2, split3, split4...  using  1 as a key
w.add(dw.Fold(column=["split1","split2","split3","split4","split5","split6"],
              table=0,
              status="active",
              drop=False,
              keys=[0]))

# Extract from fold after 'Total '
w.add(dw.Extract(column=["fold"],
                 table=0,
                 status="active",
                 drop=False,
                 result="column",
                 update=False,
                 insert_position="right",
                 row=None,
                 on=".*",
                 before=None,
                 after="Total ",
                 ignore_between=None,
                 which=1,
                 max=1,
                 positions=None))

# Fill extract  with values from below
w.add(dw.Fill(column=["extract"],
              table=0,
              status="active",
              drop=False,
              direction="up",
              method="copy",
              row=None))

# Cut from fold before ' any lowercase word   any number '
w.add(dw.Cut(column=["fold"],
             table=0,
             status="active",
             drop=False,
             result="column",
             update=True,
             insert_position="right",
             row=None,
             on=".*",
             before="[a-z]+ \\d+",
             after=None,
             ignore_between=None,
             which=1,
             max=1,
             positions=None))

# Cut from fold after 'Total'
w.add(dw.Cut(column=["fold"],
             table=0,
             status="active",
             drop=False,
             result="column",
             update=True,
             insert_position="right",
             row=None,
             on=".*",
             before=None,
             after="Total",
             ignore_between=None,
             which=1,
             max=1,
             positions=None))

# Unfold fold  on  value
w.add(dw.Unfold(column=["fold"],
                table=0,
                status="active",
                drop=False,
                measure="value"))

# Sort by  split
w.add(dw.Sort(column=["split"],
              table=0,
              status="active",
              drop=False,
              direction=[],
              as_type=[dw.String(column=[],
                table=0,
                status="active",
                drop=False)]))

w.apply_to_file('gender-and-state.csv').print_csv('out.csv')
