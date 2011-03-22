from pywebsite import sqlitepickle

db = sqlitepickle.SQLPickle()

db.save('some key', dict(a=2))
print db.get('some key')






