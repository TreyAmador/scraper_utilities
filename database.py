# database interface
from pymongo.errors import PyMongoError
from pymongo import MongoClient
from scrutil import print_safe
from movie import Movie
import subprocess


class Database:


    def __init__(self):
        mongod = 'mongod'
        mongo = 'C:\\Program Files\\MongoDB\\Server\\3.2\\bin\\mongo'
        dbpath = '--dbpath'
        datapath = 'C:\\data\\db'
        self.mongod = subprocess.Popen([mongod,dbpath,datapath])

        client = MongoClient('localhost',27017)
        database = client['imdb']
        self.db = database['movies']


    def __del__(self):
        self.terminate()


    def insert(self,movie):
        if isinstance(movie,Movie):
            movie = movie.retrieve()
        try:
            mid = self.db.insert_one(movie)
        except PyMongoError as err:
            print('Database error:\n',err.args)
            print_safe('Movie not entered:',movie)
        else:
            print('Entry',mid,'inserted into database')


    def terminate(self):
        self.mongod.terminate()
        print('Database closed.')

