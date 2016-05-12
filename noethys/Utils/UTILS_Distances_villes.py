#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


def GetDistances(origine="", destinations=[]) :
    """ Récupère sur Googlemaps les distances entre les villes """
    dictResultats = {}
    
    try :

        # Création de la requete URL
        texteOrigine = "%s%%20%s" % (origine[0], origine[1])
        texteDestinations = ""
        for cp, ville in destinations :
            ville = ville.replace(" ", "%20")
            texteDestinations += "%s%%20%s|" % (cp, ville)
        texteDestinations = texteDestinations[:-1]
        url = """http://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&sensor=false&userip=192.168.1.1""" % (texteOrigine, texteDestinations)
        
        # Récupère les distances sur Google maps
        import urllib2
        f = urllib2.urlopen(url, timeout=10)
        texteReponse = f.read()
        
        # Transforme le résultat en dictionnaire Python
        import json
        dictReponse = json.loads(texteReponse)
        
        index = 0
        for cp, ville in destinations :
            donnees = dictReponse["rows"][0]["elements"][index]
            if donnees["status"] == "OK" :
                tempsMinutes = donnees["duration"]["value"]
                distanceMetres = donnees["distance"]["value"]
                distanceTexte = donnees["distance"]["text"]
                
                dictResultats[(cp, ville)] = {
                    "temps_minutes" : tempsMinutes,
                    "distance_metres" : distanceMetres,
                    "distance_texte" : distanceTexte,
                    }
                    
            index += 1
    
    except :
        dictResultats = {}
        
    return dictResultats


if __name__ == '__main__':
    dictResultats = GetDistances(origine=("29870", "LANNILIS"), destinations=[("29200", "BREST"), ("29000", "QUIMPER")]) 
    # Affichage des résultats
    for key, resultat in dictResultats.iteritems() :
        print key, " ->", resultat
