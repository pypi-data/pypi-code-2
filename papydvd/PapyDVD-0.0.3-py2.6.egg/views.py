# -*- coding: utf-8 -*-

from datetime import datetime
import json
from StringIO import StringIO

from repoze.bfg.i18n import TranslationStringFactory
from repoze.bfg.chameleon_zpt import get_renderer

from papydvd.models import DBSession
from papydvd.models import Movie
from papydvd.models import Genre
from papydvd.models import Director
from papydvd.models import AppInfo
from papydvd.models import Image
from papydvd import utils

from webob.exc import HTTPFound
from webob import Response

_ = TranslationStringFactory('PapyDVD')


class MainView(object):

    def __init__(self, request):
        self.request = request
        self.now = datetime.now()
        self.error_message = ''

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        last_movie = dbsession.query(Movie).order_by(Movie.add_date.desc()).first()
        directors_count = dbsession.query(Director).count()
        genres_count = dbsession.query(Genre).count()
        movies_count = dbsession.query(Movie).count()
        main = get_renderer('templates/main_template.pt').implementation()
        return {'last_movie': last_movie,
                'directors_count': directors_count,
                'genres_count': genres_count,
                'movies_count': movies_count,
                'error_message': self.error_message,
                'appId': '0.0.3',
                'project':'PapyDVD',
                'main': main}

    @property
    def left_column(self):
        return AppInfo.getConfigurationValue('left_column')
    
    @property
    def right_column(self):
        return AppInfo.getConfigurationValue('right_column')

    @property
    def all_genres(self):
        genres = Genre.all_by_name()
        return [{'name': x.name,
                 'id': x.genre_id,
                 'description': x.description} for x in genres]

    @property
    def all_directors(self):
        directors = Director.all_by_name()
        return [{'name': x.name, 'id': x.director_id} for x in directors]        

    @property
    def this_year(self):
        return self.now.year

    @classmethod
    def parseSearchArgument(cls, search):
        """Given a string with spaces inside, return an array of words
        TODO: keep togheter word phrases, inside quoting character.
        """
        words = [x.strip() for x in search.split()]
        return words


class LoadMoviesView(MainView):
    """Called using AJAX for getting movies in the page"""
    
    def __call__(self):
        form = self.request.params
        search = self.parseSearchArgument(form.get('search', ''))
        b_start = form.get('b_start', '').isdigit() and int(form.get('b_start')) or 0
        b_size = form.get('b_size', '').isdigit() and int(form.get('b_size')) or 30
        movies = Movie.all(search, b_start, b_size)
        moviesCount = Movie.count(search, b_start, b_size) + b_start
        allMoviesCount = Movie.count(search=search, b_size=0)
        return Response(body=json.dumps({'movies': [{'id': x.movie_id,
                                          'primary_number': x.primary_number,
                                          'secondary_number': x.secondary_number,
                                          'title': x.title,
                                          'genre': x.genre and x.genre.name or None,
                                          'year': x.year,
                                          'director': x.director and x.director.name or None,
                                          } for x in movies],
                                         'canGoLeft': b_start>0,
                                         'canGoRight': allMoviesCount>moviesCount,
                                        }),
                        content_type='application/json')


class AddMovieView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        form = request.params
        cover = form['cover'] and form['cover'].file.read() or None
        movie = Movie(title=form['title'], genre_id=form['genre_id'], director_id=form['director_id'],
                      year=form['year'], story=u"", cover=cover)
        dbsession.add(movie)
        dbsession.flush()
        return HTTPFound(location='/')


class UpdateMovieView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        form = request.params
        cover = form['cover'] and form['cover'].file.read() or None
        movie = dbsession.query(Movie).filter(Movie.movie_id==form['movie_id']).one()
        movie.title = form['title']
        movie.primary_number = form['primary_number']
        movie.secondary_number = form['secondary_number'] or 0
        movie.year = form['year'] or None
        movie.genre_id = form['genre_id'] or None
        movie.director_id = form['director_id'] or None
        movie.modification_date = datetime.now()
        movie.cover = cover
        dbsession.flush()
        return HTTPFound(location='/')


class UpdateDirectorView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        dbsession = DBSession()
        form = self.request.params
        director = dbsession.query(Director).filter(Director.director_id==int(form['director_id'])).one()
        director.name = form['name']
        dbsession.flush()
        return HTTPFound(location='/directors')


class AddGenreView(MainView):

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        form = request.params
        genre = Genre(name=form['name'], description=form['description'])
        dbsession.add(genre)
        dbsession.flush()
        return Response(body=json.dumps([{'name':x['name'],
                                          'id':x['id'],
                                          'selected': x['name']==form['name']} for x in self.all_genres]),
                        content_type='application/json')


class AddDirectorView(MainView):

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        form = request.params
        genre = Director(name=form['name'])
        dbsession.add(genre)
        dbsession.flush()
        return Response(body=json.dumps([{'name': x['name'],
                                          'id': x['id'],
                                          'selected': x['name']==form['name']} for x in self.all_directors]),
                        content_type='application/json')


class LoadMovieView(MainView):

    def __call__(self):
        request = self.request
        form = request.params
        movie = Movie.getMovieById(form['movie_id'])
        return Response(body=json.dumps({'title': movie.title,
                                         'primary_number': movie.primary_number,
                                         'secondary_number': movie.secondary_number or 0,
                                         'genre_id': movie.genre and movie.genre.genre_id or '',
                                         'year': movie.year,
                                         'director_id': movie.director and movie.director.director_id or '',
                                        }),
                        content_type='application/json')


class LoadDirectorView(MainView):

    def __call__(self):
        request = self.request
        form = request.params
        movie = Director.getDirectorById(form['director_id'])
        return Response(body=json.dumps({'name': movie.name, }),
                        content_type='application/json')


class DeleteMovieView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        form = request.params
        movie = dbsession.query(Movie).filter(Movie.movie_id==form['movie_id']).one()
        dbsession.delete(movie)
        dbsession.flush()
        return HTTPFound(location='/')


class DeleteDirectorView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        form = request.params
        director = dbsession.query(Director).filter(Director.director_id==int(form['director_id'])).one()
        # before delete the director, let's null all movies that use this director
        movies = dbsession.query(Movie).filter(Movie.director==director).all()
        for movies in movies:
            # now delete the director
            dbsession.delete(director)
        dbsession.flush()
        return HTTPFound(location='/directors')


class DeleteGenreView(MainView):

    def __init__(self, request):
        MainView.__init__(self, request)

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        form = request.params
        genre = dbsession.query(Genre).filter(Genre.genre_id==int(form['genre_id'])).one()
        # before delete the genre, check if there are movies left
        movies_using_genre = dbsession.query(Movie).filter(Movie.genre==genre).count()
        if not movies_using_genre:
            # now delete the director
            dbsession.delete(genre)
            dbsession.flush()
            return HTTPFound(location='/genres')
        # error: movies with this genre left
        self.error_message = u'Non posso rimuovere il genere perché è usato ancora in %s film.' % movies_using_genre
        return MainView.__call__(self)



# Service views

class ImageView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        id = self.request.params['id']
        dbsession = DBSession()
        image = dbsession.query(Image).filter(Image.image_id==self.request.params['id']).one()
        return Response(body=image.data, content_type='image/jpg',
                        headerlist=[('Content-Type', 'image/jpg'),
                                    ('Content-Disposition', 'attachment; filename=%s' % image.name),
                                    ]
                        )

class DumpMoviesView(object):

    def __init__(self, request):
        self.request = request
    
    def __call__(self):
        dbsession = DBSession()
        movies = dbsession.query(Movie).all()
        out = StringIO()
        columns = ('movie_id', 'title', 'genre_id', 'primary_number', 'secondary_number',
                   'director_id', 'year', 'add_date')
        for row in movies:
            print >> out, '\t'.join([row.__getattribute__(x) and str(row.__getattribute__(x)) or '' for x in columns])
        return Response(body=out.getvalue(), content_type='text/csv',
                        headerlist=[('Content-Type', 'text/html'),
                                    ('Content-Disposition', 'attachment; filename=movies.csv'),]
                        )

class ImportMoviesView(object):

    def __init__(self, request):
        self.request = request
    
    def __call__(self):
        utils.importMovies(path=self.request.params['path'])
        return HTTPFound(location='/')
