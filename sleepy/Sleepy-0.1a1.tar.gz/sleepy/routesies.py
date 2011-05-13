from sleepy.shorties import s
from sleepy.controllers import default_controller

def reorder( mapper,
             res ):
    mapper.link( rel="reorder",
                 name=s( "reorder_{{ name }}",
                         name=mapper.resource_name ),
                 action="reorder",
                 method="POST",
                 controller=default_controller,
                 names_path=res.path
                               .names_path )

def resurrect( mapper,
               res ):
    mapper.link( rel="resurrect",
                 name=s( "resurrect_{{ name }}",
                         name=mapper.resource_name ),
                 action="resurrect",
                 method="POST",
                 controller=default_controller,
                 names_path=res.path
                               .names_path )

def resurrection( mapper,
                  res ):
    mapper.link( rel="resurrection",
                 name=s( "resurrection_{{ name }}",
                         name=mapper.resource_name ),
                 action="resurrection",
                 method="GET",
                 controller=default_controller,
                 names_path=res.path
                               .names_path )
