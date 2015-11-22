##############################################################################
#                                                                            #
#   CrossBar Authentication and Authorization                                #
#                                                                            #
##############################################################################
#                                                                            #
from twisted.internet.defer     import inlineCallbacks                       #
from autobahn.twisted.wamp      import ApplicationSession                    #
from autobahn                   import wamp                                  #
from twisted.python             import log                                   #
from pymongo                    import MongoClient                           #
from datetime                   import datetime                              #
#                                                                            #
##############################################################################
class Subscriptions:
    """handle class subscriptions"""
    def __init__(self):
        self.mongo = MongoClient()

    @inlineCallbacks
    def session_join_event(self,event):
        """ login has been successful """
        log.msg("{}> Join ({}) as ({})".format(event['session'],event['authid'],event['authrole']))

        session = event.get('session',None)
        authid = event.get('authid',None)
        if not (session and authid):
            log.msg('% ERROR - missing session or authid')
            return

        record = yield self.mongo.ionman.users.find_one({'authid':authid})
        if not record:
            log.msg("% ERROR - missing user record")
            return

        update = {
            'authid'    : authid,
            'session'   : session,
            'when'      : datetime.now()
        }
        yield self.mongo.ionman.sessions.update({'session':session},{'$set':update},upsert=True)

    @inlineCallbacks
    def session_leave_event(self,event):
        """ come here when the session terminates """
        log.msg("{}> Leave".format(event))
        yield self.mongo.ionman.sessions.remove({'session':event})

    @wamp.subscribe(u'wamp.session.on_join')
    def session_join(self,event):
        """ on_join wrapper """
        try:
            return self.session_join_event(event)
        except Exception as e:
            log.err()

    @wamp.subscribe(u'wamp.session.on_leave')
    def session_leave(self,event):
        """ on_leave wrapper """
        try:
            return self.session_leave_event(event)
        except Exception as e:
            log.err()

class Registrations:
    """handle class registrations"""
    def __init__(self):
        """ set up a connection to the database """
        self.mongo = MongoClient()

    @wamp.register(u'ionman.security.authenticate')
    def security_authenticate(self,realm, authid, extra=None):
        """ authenticate the user / session """
        log.msg('{}> Authenticate ({})'.format(extra['session'],authid))
        user = self.mongo.ionman.users.find_one({'authid':authid})
        if user: return { 'secret':user.get('digest',''),'role':user.get('role','guest') }
        log.msg('{}> No such user ({})'.format(extra['session'],authid))
        return { 'secret':'','role':'' }

    @wamp.register(u'ionman.security.authorize')
    def security_authorize(self,session, uri, action):
        """ we need to add checks here to validate the caller is allowed """
        log.msg('{}> Authorize - {}({})'.format(session['session'],action,uri))
        return True

class ionman(ApplicationSession):
    """ when a connection is made, activate registrations and subscriptions """
    @inlineCallbacks
    def onJoin(self, details):
        """ this will happen whenever the client (re)connects """
        #try:
        yield self.subscribe(Subscriptions())
        yield self.register(Registrations())
        #except Exception:
        #    log.err()