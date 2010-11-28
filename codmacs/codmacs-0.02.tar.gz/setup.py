from distutils.core import setup
setup(name='codmacs',
      version='0.02',
      description = 'Python meta-programming implementation',
      author = 'Martin Cerdeira (mRt)',
      author_email = 'martincerdeira@gmail.com',
      url = 'http://www.codmacs.blogspot.com/',
      py_modules=['CMCore','CMFunc','CodMACs'],
      data_files=[('sql', ['MSSQL.sql','MYSQL.sql','ORACLE.sql','PostgreSQL.sql','Firebird.sql'],
                   'examples',['abm.cod','otro.cod','write.cod'], 
                   'misc', ['README','manual/Documentation.odt']      
                  )],
      )

