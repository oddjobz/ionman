#!/usr/bin/python
##############################################################################
#
#
##############################################################################
__author__ = 'Gareth Bult <gareth@bult.co.uk>'

import demo
import ionman

class WAMPClient:
    """ standard format WAMP client """

    def __init__(self):
        """ set up the registrations and subscriptions """
        self.Registrations = []
        self.Subscriptions = []
        self.Registrations.append(demo.Registrations)
        self.Subscriptions.append(demo.Subscriptions)

    def callback(self,*args,**kwargs):
        """ optional callback routine executed on a timer """
        pass

application = ionman.init(WAMPClient())