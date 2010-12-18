"""hooks/on_field_validation

you can set hooks on single field validation. It will be called from within
the field 


"""
from sqlkit.exc import ValidationError

class Hooks(object):

    def on_field_validation__year(self, mask, field_name, field_value, field):
        if field_value > 2020:
            raise ValidationError("Hei: how can you know the future!")


lay = """
   title
   year
   director_id
   m2m=genres -
   """

t = SqlMask(model.Movie, layout=lay, label_map={'genres.name':'genres'},
         dbproxy=db, hooks=Hooks())

t.reload()

