from os import environ
import pymongo


client = pymongo.MongoClient(environ.get('MONGODB_URI'))
db = client.get_database('sloovitask')