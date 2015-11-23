##############################################################################
#   IMPORTS                                                                  #
##############################################################################
from autobahn.twisted.wamp      import ApplicationSession                    #
from autobahn.twisted           import wamp,websocket                        #
from twisted.internet.protocol  import ReconnectingClientFactory             #
from twisted.application        import service                               #
from autobahn.wamp              import auth,types                            #
from autobahn.wamp.types        import CallOptions                           #
from autobahn.wamp.types        import RegisterOptions                       #
from twisted.python             import log                                   #
from twisted.python.log         import ILogObserver, FileLogObserver         #
from twisted.python.logfile     import DailyLogFile                          #
from twisted.internet           import reactor                               #
from twisted.internet.defer     import inlineCallbacks                       #
from twisted.internet.task      import LoopingCall                           #
from sys                        import stdout,exit,argv                      #
from pymongo                    import MongoClient                           #
import config                                                                #
##############################################################################
#   Config - Load values from the .ini file                                  #
##############################################################################
conf = None
subscription_table  = []
registration_table  = []
deferred_message    = None
copts               = CallOptions(disclose_me=True)
##############################################################################
#   init()
##############################################################################
def init(WAMPClient):
    """ command line parameters passes as argument """
    Config(ini='ionman.ini',callback=WAMPClient.callback)
    for sub in WAMPClient.Subscriptions: Subscribe(sub)
    for reg in WAMPClient.Registrations: Register(reg)
    return Main('foreground' not in argv).run()
##############################################################################
#   Config()
##############################################################################
class Config(config.Config):
    """ global configuration """
    def __init__(self, *args, **kwargs):
        config.Config.__init__(self,*args,**kwargs)
        self.mongo = MongoClient()
        global conf
        conf = self
##############################################################################
def Register(fn,extra=None):
    registration_table.append(fn(conf,extra))
##############################################################################
def Subscribe(fn,extra=None):
    subscription_table.append(fn(conf,extra))
##############################################################################
#   ServerComponent - Handle the websockets connection                       #
##############################################################################
class ServerComponent(ApplicationSession):
    """ this handles connecting and authenticating with a router """
    def onConnect(self):
        """ on connection we need to join our chosen realm """
        log.msg("> connected to router")
        self.join(conf.REALM, [u"wampcra"], conf.USER)

    def onDisconnect(self):
        log.msg("> disconnected from router")

    def onChallenge(self, challenge):
        """ this is our challenge authentication """
        log.msg("> dealing with [{}] challenge".format(challenge.method))
        if challenge.method != u"wampcra":
            raise Exception("no authmethod {}".format(challenge.method))

        extra = challenge.extra['challenge'].encode("ascii")
        signature = auth.compute_wcs(conf.PASS,extra)
        return signature.decode('ascii')

    def onJoin(self, details):
        """this is what happens when we successfully join a router"""
        global deferred_message
        log.msg("> ({}) joined ({}) [{}] - {}".format(details.authid,details.realm,details.authrole,details.session))

        @inlineCallbacks
        def registration(fn):
            log.msg("> adding registration @@ {}".format(fn))
            options = RegisterOptions(details_arg = 'details')
            fn.server = self
            yield self.register(fn,None,options)

        @inlineCallbacks
        def subscription(fn):
            log.msg("> adding subscription @@ {}".format(fn))
            yield self.subscribe(fn)

        for fn in subscription_table: subscription(fn)
        for fn in registration_table: registration(fn)

        log.msg("> initialting callback loop")
        conf.application = self
        conf.lc = LoopingCall(conf.callback,self,conf)
        conf.lc.start(1)

##############################################################################
#   ComponentFactory - handle automatic websocket reconnection
##############################################################################
class ComponentFactory(websocket.WampWebSocketClientFactory,ReconnectingClientFactory):
    """ class to wrap the automatic WAMP reconnect function """
    maxDelay = 4
    initialDelay = 1
    factor = 1.1

    def clientConnectionFailed(self,conn,reason):
        log.msg('> connection to router failed')
        if not reactor.running: self.stopTrying()
        ReconnectingClientFactory.clientConnectionFailed(self,conn,reason)

    def clientConnectionLost(self,conn,reason):
        log.msg('> connection to router lost')
        if not reactor.running: self.stopTrying()
        ReconnectingClientFactory.clientConnectionLost(self,conn,reason)
##############################################################################
#   Main() - kick off here                                                   #
##############################################################################
class Main():
    def __init__(self,isBackground):
        """ setup the server session """
        component_config = types.ComponentConfig(realm = conf.REALM)
        factory = wamp.ApplicationSessionFactory(config = component_config)
        factory.session = ServerComponent
        self.factory = factory
        self.isBackground = isBackground
        if not isBackground: log.startLogging(stdout)

    def run(self):
        """ run the server up if foreground or background mode """
        server_url = "wss://%s:%d/ws" % (conf.HOST,conf.PORT)
        log.msg("Server>",server_url)
        transport = ComponentFactory(self.factory,server_url,
                        debug = conf.DEBUG, debugCodePaths = conf.DEBUG )
        transport.setProtocolOptions(acceptMaskedServerFrames = True)
        websocket.connectWS(transport)

        if not self.isBackground:
            reactor.run()
            exit(0)
        #
        #   In background mode we return here and twistd picks up the slack
        #
        application = service.Application(conf.APP_NAME)
        logfile = DailyLogFile(conf.LOGFILE,conf.LOGPATH)
        application.setComponent(ILogObserver,FileLogObserver(logfile).emit)
        return application
##############################################################################
