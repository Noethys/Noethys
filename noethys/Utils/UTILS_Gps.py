#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import urllib2, json


def GPS(numero="", rue="", cp="", ville="", pays=""):
    try :
        req = "http://maps.google.com/maps/api/geocode/json?address=%s ,%s ,%s ,%s ,%s &&sensor=false" % (numero, rue, cp, ville, pays)
        req = req.replace(' ','%20')
        f = urllib2.urlopen(req, timeout=5)
        xml = f.read()
        data = json.loads(xml)
        
        # Recherche coordonnées
        lat = data['results'][0]['geometry']['location']['lat']
        long = data['results'][0]['geometry']['location']['lng']
        # Recherche Pays
        pays = ""
        for dictTemp in data['results'][0]['address_components'] :
            if dictTemp.has_key("types") :
                if "country" in dictTemp["types"] :
                    pays = dictTemp["long_name"]
            
        return {'lat':lat, 'long':long, 'pays':pays}
    except :
        return None


if __name__ == "__main__":
    g = GPS(cp="29200", ville="BREST", pays="France")
    print g
