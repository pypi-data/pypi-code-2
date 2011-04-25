# -*- coding: utf-8 -*-

import csv
import transaction

from papydvd.models import DBSession
from papydvd.models import Movie

def importMovies(path):
    """Import movies from CSV"""
    reader = csv.reader(open(path, 'r'), delimiter='\t', quotechar='\"')
    session = DBSession()
    for row in reader:
        movie_id, title, genre_id, primary_number, secondary_number, director_id, year, add_date = row
        movie = Movie(title=title, primary_number=primary_number, secondary_number=secondary_number or 0, 
                      genre_id=genre_id or None, director_id=director_id or None, year=year or None)
        session.add(movie)
    session.flush()
    transaction.commit()