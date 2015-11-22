
from autobahn       import wamp                                              #
from twisted.python import log                                               #
from pymongo        import MongoClient,DESCENDING                            #
from jinja2         import Environment,FileSystemLoader                      #
from datetime       import datetime,timedelta                                #
from twisted.internet.defer import inlineCallbacks                           #
from bson.objectid  import ObjectId                                          #
#                                                                            #

class Subscriptions:
    """handle class subscriptions"""
    def __init__(self,conf=None,extra=None):
        self.conf = conf
        self.extra = extra

class Registrations:
    """handle class registrations"""
    def __init__(self,conf=None,extra=None):
        self.conf = conf
        self.extra = extra
        self.mongo = MongoClient()
        self.cache = {}
        self.env = Environment(loader=FileSystemLoader('../static/html'),extensions=["jinja2.ext.do",])
        self.unknown = {'name': 'Unknown', 'authid': 'unknown'}
        self.valid_fields = ['name','company','email','title','sector','location','desc']

