# -*- encoding: utf-8 -*-
#
# geodata.py
# **********
# In here go functions related to the understanding of
# geographical information of the probe
#
# :authors: Arturo Filastò
# :licence: see LICENSE

import re
import os
import pygeoip

from twisted.web.client import Agent
from twisted.internet import reactor, defer, protocol

from ooni.utils import log, net
from ooni import config

@defer.inlineCallbacks
def myIP():
    target_site = 'https://check.torproject.org/'
    regexp = "Your IP address appears to be: <b>(.+?)<\/b>"
    myAgent = Agent(reactor)

    result = yield myAgent.request('GET', target_site)

    finished = defer.Deferred()
    result.deliverBody(net.BodyReceiver(finished))

    body = yield finished

    match = re.search(regexp, body)
    try:
        myip = match.group(1)
    except:
        myip = "unknown"

    defer.returnValue(myip)

class GeoIPDataFilesNotFound(Exception):
    pass

def IPToLocation(ipaddr):
    city_file = os.path.join(config.advanced.geoip_data_dir, 'GeoLiteCity.dat')
    country_file = os.path.join(config.advanced.geoip_data_dir, 'GeoIP.dat')
    asn_file = os.path.join(config.advanced.geoip_data_dir, 'GeoIPASNum.dat')

    location = {'city': None, 'countrycode': None, 'asn': None}
    try:
        city_dat = pygeoip.GeoIP(city_file)
        location['city'] = city_dat.record_by_addr(ipaddr)['city']

        country_dat = pygeoip.GeoIP(country_file)
        location['countrycode'] = country_dat.country_code_by_addr(ipaddr)

        asn_dat = pygeoip.GeoIP(asn_file)
        location['asn'] = asn_dat.org_by_addr(ipaddr)
    except IOError:
        log.err("Could not find GeoIP data files. Go into data/ "
                "and run make geoip")
        raise GeoIPDataFilesNotFound

    return location

