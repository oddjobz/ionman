##############################################################################
#                                                                            #
#   Basic INI file handler                                                   #
#                                                                            #
##############################################################################
import distutils.util

class Config():

    DEBUG = False

    def getOpt(self,section_name,option,default):
        """ wrapper for .ini file option 'get' """
        if not self.config.has_option(section_name,option): return default
        return self.config.get(section_name,option)

    def __init__(self, *args, **kwargs):
        """ read in/set values or default values for all our variables """
        from hashlib import md5
        from ConfigParser import RawConfigParser
        import sys

        opt = self.getOpt

        self.config   = RawConfigParser()
        self.ini      = kwargs.get('ini',None)

        if not self.ini:
            print("No Configuration file specified!")
            sys.exit(1)

        self.callback = kwargs.get('callback',None)
        self.options  = self.config.read(self.ini)
        #
        self.DEBUG    = opt('global','debug','True')
        self.REALM    = opt('global','realm','')
        self.USER     = opt('global','user','')
        self.HOST     = opt('global','host','')
        self.PORT     = opt('global','port','0')
        self.APP_NAME = opt('global','app','')
        self.TITLE    = opt('global','title','')
        self.HANDLER  = opt('global','handler','')
        self.LOGFILE  = opt('global','logfile',self.APP_NAME+'.log')
        self.LOGPATH  = opt('global','logpath','.')
        self.PASS     = opt('global','password','')
        self.CHANNEL  = opt('global','channel',None)
        self.PASS     = md5(self.PASS.encode()).hexdigest().encode('utf8')
        self.PORT     = int(self.PORT)
        self.DEBUG    = distutils.util.strtobool(self.DEBUG)
        #
        if not self.callback:
            print("No CALLBACK specified")
            sys.exit(1)
        #
    def set(self,option,value):
        """ update an ini value """
        self.config.set('global',option,value)
        with open(self.ini,'wb') as inifile: self.config.write(inifile)