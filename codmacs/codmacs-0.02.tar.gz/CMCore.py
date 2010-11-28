# -*- coding: utf-8 -*-

"""CodMACs Core File"""

__author__ = "mRt (martincerdeira@gmail.com)"
__version__ = "0.02"
__date__ = "$Date: 2009/09/17 17:47 $"
__license__ = "GPL v3"

class codTable(object):
    def __init__(self,shost,suser,spasswd,sdb,stabl=None,action="s",cn="MySQL"):        
       self.TableName = stabl                          
       cols = fetchSQLData(shost,suser,spasswd,sdb,stabl,action,cn)

       if action=="r" or action=="v" or action=="2" or action=="2v":
           self.cols = dict(((iden, codFields(iden,form,leng,desc,ispk,iske,anul,inde)) for iden,form,leng,desc,ispk,iske,anul,inde in cols))
    def __getitem__(self, n):
        return self.cols[n]

class codFields(object):
    def __init__(self, iden, form, leng, desc, ispk, iske, anul, inde):
        self.Identifier = iden
        self.Format = form
        self.Length = leng
        self.Description = desc
        self.IsPKey = ispk
        self.IsKey = iske
        self.Nullable = anul
        self.Index = inde

class codFile:        
    def __init__(self, templatePath, destinationPath):        
        vo = self.__parseF(templatePath)
        vd = self.__parseF(destinationPath)  
                
        if len(vd) == 2:            
            self.destFileName = vd[0]  
            self.destFileExt = vd[1]
            self.destFullFilename = vd[0] + "." + vd[1]        
        else:
            self.destFileName = vd[0]
            self.destFileExt = ""
            self.destFullFilename = vd[0]
        
        if len(vo) == 2:
            self.origFileName = vo[0]
            self.origFileExt = vo[1]
            self.origFullFilename = vo[0] + "." + vo[1]         
        else:
            self.origFileExt = vo[0]
            self.origFileName = ""
            self.origFullFilename = vo[0]
                                            
    def __parseF(self, fileN): #Or use os.path.split/splitext
        vtmp = fileN.split("/")        
        vtmp = vtmp[len(vtmp)-1].split(".")   
        return vtmp

def fetchSQLData(shost,suser,spasswd,sdb,stabl=None,action="s",cn="MySQL"):
    """SQL Data Recollection function"""
    # RecordSet Constants
    IDEN = 0
    FORM = 2
    LEN1 = 4
    LEN2 = 5
    DESC = 7
    ISPK = 6
    ISKE = 6
    ANUL = 3
    INDE = 1    
    # Connection Types    
    cn = str(cn).upper()    
    if cn=="MYSQL":
        import MySQLdb
        try:
            db = MySQLdb.connect(host=shost, user=suser, passwd=spasswd,db="information_schema")
            cursor = db.cursor()
        except MySQLdb.Error, e:
            print "A Mysql Error has ocurred. CodMACs is closing"
            print "Information:"
            print 
            print "MySQL Error %d: %s" % (e.args[0], e.args[1])
            raise SystemExit                      
    elif cn=="MSSQL": # Reserved for Microsoft MySQL
        import pymssql
        try:
            db = pymssql.connect(server=shost, user=suser, password=spasswd, database=sdb)
            cursor = db.cursor()
        except pymssql.Error, e:
            print "A MSSQL Error has ocurred. CodMACs is closing"
            print "Information:"
            print 
            print "MSSQL Error " + e.args[0]
            raise SystemExit
    elif cn=="ORACLE": # Reserved for Oracle
        print cn + " Not implemented"
        raise SystemExit
    elif cn=="POSTGRE": # Reserved for PostgreSQL
        print cn + " Not implemented"
        raise SystemExit
    elif cn=="FIREBIRD": # Reserved for Firebird SQL
        print cn + " Not implemented"
        raise SystemExit                
    elif cn=="VOID": # Do not connect to anything    
        pass
    else:
        print cn + " Not supported"          
        raise SystemExit       
               
    if cn == "VOID":
        ret = [] # Returned by function  
        return ret
    else:                    
        if stabl==None or stabl=="": # Return avaible tables                
            sql = fileSQL(cn,"tables").replace("$sdb",sdb).replace("$stabl",stabl)
            cursor.execute(sql)                   
            result = cursor.fetchall()   
            print "List of Tables in DataBase: " + sdb
            print "--------------"
            for rs in result:
                print "[" + rs[IDEN] + "]"
            print "--------------"
            cursor.close()
        else:      
            # Read Gathering Query from special file
            sql = fileSQL(cn,"columns").replace("$sdb",sdb).replace("$stabl",stabl)
            cursor.execute(sql)   
            result = cursor.fetchall()   
            # Verbose and/or Return
            if action=="s" or action=="v" or action=="2v":             
                print "Showing Information About: " + stabl  + " in " + sdb
                print "[" + stabl + "]"
                print "--------------"        
            if action=="r" or action=="v" or action=="2" or action=="2v":
                ret = [] # Returned by function     
            for rs in result:
                if action=="r" or action=="v" or action=="2" or action=="2v":
                    buf = (str(rs[IDEN]),str(rs[FORM]),toggleNull(rs[LEN1],rs[LEN2]),str(rs[DESC]),ifPK(rs[ISPK]),ifKE(rs[ISKE]),ifNULL(rs[ANUL]),rs[INDE])                                
                    ret.append(buf)                
                if action=="s" or action=="v" or action=="2v":
                    print str(rs[INDE]) + "-" + str(rs[IDEN]) + " " + (str(rs[FORM]) + "(" + str(toggleNull(rs[LEN1],rs[LEN2])) + ")").ljust(15) + str(rs[DESC])                                             
            if action=="s" or action=="v" or action=="2v":    
                print "--------------"        
            if action=="r" or action=="v" or action=="2" or action=="2v":
                return ret                
            cursor.close()

def fileSQL(f,t): #Opens file with SQL structure Query 
    try:
        fs = open(f + ".sql","r")  
        sql = ""
        gat = False
        for lin in fs:    
            if str(lin).find("<"+t+">") != -1:    
                gat = True
            elif str(lin).find("</"+t+">") != -1:    
                gat = False    
            else:
                if gat:    
                    sql += str(lin)  
        
        fs.close()  
        return sql
    except IOError:
        print "cannot open file", f + ".sql"
        raise SystemExit     

def toggleNull(v1,v2): #Removes MySQL Nulls
    if v1 == -1:
        return v2
    else:
        return v1          
        
def ifPK(v): #Is Primary Key       
    if v.upper() == "PRI":
        return True
    else:
        return False

def ifKE(v): #Is Key  
    if v.upper() == "MUL":
        return True
    else:
        return False
        
def ifNULL(v): #Allow Nulls
    if v.upper() == "YES" or v.upper() == "SI":
        return True
    else:
        return False                
                                              
