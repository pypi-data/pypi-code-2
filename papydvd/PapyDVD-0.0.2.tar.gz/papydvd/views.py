# -*- coding: utf-8 -*-

from datetime import datetime
import json
from StringIO import StringIO

from repoze.bfg.i18n import TranslationStringFactory

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

    def __call__(self):
        dbsession = DBSession()
        request = self.request
        last_movie = dbsession.query(Movie).order_by(Movie.add_date.desc()).first()
        return {'last_movie': last_movie,
                'appId': '0.0.2',
                'project':'PapyDVD'}

    def getAllMovies(self):
        dbsession = DBSession()  
        movies = Movie.all()
        return movies

    @property
    def all_genres(self):
        genres = Genre.all_by_name()
        return [{'name': x.name, 'id': x.genre_id} for x in genres]

    @property
    def all_directors(self):
        directors = Director.all_by_name()
        return [{'name': x.name, 'id': x.director_id} for x in directors]        

    @property
    def this_year(self):
        return self.now.year


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
