"""base/movie mask

base editing mode: mask view

Double click on the arrow in director_id field to mimic an 'enum' field

"""

lay = """
    title
    date_release
    TXS=description 
    director_id
    """
t = SqlMask('movie', dbproxy=db, layout=lay)
t.reload()
