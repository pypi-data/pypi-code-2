from django.db.models import get_model


class RelatedField(object):
    def __init__(self, model, field_name=''):
        self.model = model
        self.field_name = field_name

    def get_model(self):
        '''
        Returns the model to use for the field.

        :rtype: ``django.db.models.Model``
        '''
        model = self.model

        if isinstance(model, str): 
            app_name, model_name = model.split('.')
            model = get_model(app_name, model_name)

        return model


class ForeignKey(RelatedField):
    '''
    Emulates Django's ``ForeignKey`` field, but is able to do lookups
    and sets even when the value is in a different database than the
    model the field is attached to.

    Example usage::

        from django.db import models

        import multidb

        from people.models import Person


        class Book(models.Model):
            author_fk = models.IntegerField()
            author = multidb.ForeignKey(Person, field_name='author_fk')

    This is equivalent to

    ::

        class Book(models.Model):
            author_fk = models.IntegerField()

            @property
            def author(self):
                return Person.objects.get(id=self.author_fk)

            @author.setter
            def author(self, person):
                self.author_fk = person.id

    The constructor takes two arguments: ``model`` and 
    ``field_name``:

    ``model``
      The model to refer to with the foreign key.

    ``field_name``
      The name of the field that refers to the model id.
    '''
    def __get__(self, obj, objtype=None):
        obj_id = getattr(obj, self.field_name, None)
        model = self.get_model()

        try:
            return model.objects.get(id=obj_id)
        except model.DoesNotExist:
            return None

    def __set__(self, obj, value):
        setattr(obj, self.field_name, value.id)


class RelatedSet(RelatedField):
    '''
    Emulates the related sets Django provides for models when other
    models have foreign keys to them. In a multi-database situation
    in which Django's ``ForeignKey`` field cannot be used, this 
    functionality is lost; ``RelatedSet`` provides it again.

    Example usage::

        from django.db import models

        import multidb

        from books.models import Book

        
        class Author(models.Model):
            book_set = multidb.RelatedSet(Book, field_name='author')

    This is equivalent to

    ::

        class Author(models.Model):
            @property
            def book_set(self):
                return Book.objects.filter(author=self)

    The constructor takes two arguments: ``model`` and 
    ``field_name``:

    ``model``
      The model to do the related set lookup on.

    ``field_name``
      The name of the model field to do the lookup on.
    '''
    def __get__(self, obj, objtype=None):
        lookup_data = {self.field_name: obj}
        model = self.get_model()
        return model.objects.filter(**lookup_data)
