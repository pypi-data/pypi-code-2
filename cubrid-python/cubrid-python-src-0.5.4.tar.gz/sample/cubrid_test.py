import cubriddb
 
con = cubriddb.connect('localhost', 30000, 'demodb')
c = con.cursor()
 
c.execute('select * from code')
rows = c.fetchall()
 
for r in rows:
	'''print(r)'''
	print r

c.close()
con.close()