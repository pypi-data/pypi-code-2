import cx_Oracle
import dbapiext

cn = cx_Oracle.connect('eqdbw/barqs@orcl')
cu = cn.cursor()

qry = 'SELECT * FROM lt_installation WHERE cs_description_tx = %(descrip)S'
res1 = dbapiext.execute_f(cu, qry, paramstyle='absurd', descrip='Eglin AFB')
print res1.fetchall()