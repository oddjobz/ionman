##############################################################################
#
#   DEMO Application
#
##############################################################################
from pymongo        import MongoClient                                       #
from jinja2         import Environment,FileSystemLoader                      #
from twisted.python import log                                               #
from autobahn       import wamp                                              #
##############################################################################

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
        self.env = Environment(loader=FileSystemLoader('../../static/html'),extensions=["jinja2.ext.do",])
    #
    #   Ok, we need this to resolve sessions back to authid's
    #   Hopefully when we get passed authid's , this will get easier
    #
    def getSession(self,details):
        """ lookup details for the current user """
        id = getattr(details,'caller')
        if not id:
            log.msg("% ERROR - missing caller field")
            return None
        session = self.mongo.ionman.sessions.find_one({'session':id})
        if not session:
            log.msg("% ERROR - missing session record")
            return None

        user = self.mongo.ionman.users.find_one({'authid':session.get('authid','')})
        if not user:
            log.msg("% ERROR - missing user record")
            return None

        return user

    @wamp.register(u'demo.page.render')
    def app_load_preferences(self,params,details):
        """ load up a requested page """
        try:
            user = self.getSession(details)
            page = params.get('uri','welcome.html');
            tmpl = self.env.get_template(page)
            my_dict = {
                'name'      : user.get('name',''),
                'role'      : user.get('role',''),
                'authid'    : user.get('authid',''),
                'uri'       : page
            }
            log.msg(my_dict)
            return { 'html':tmpl.render(my_dict) }
        except:
            log.err()
            return { 'html':'' }