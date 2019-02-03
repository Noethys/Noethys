#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from six.moves.urllib.request import urlopen


def RechercheData(xml, nom="", positionDebut=0):
    posG = xml.find(nom, positionDebut) + len(nom) + 2
    posD = xml.find("/>", posG) - 1
    texte = xml[posG:posD]
    return posG, posD, texte


def Meteo(ville="", cp=""):
    """ Création d'un dictionnaire avec la météo Google """
    dictMeteo = { "jour" : {}, "previsions" : [] }
    
    try :
        # Récupère le fichier xml de Google
        url = "http://www.google.fr/ig/api?weather=%s%%20%s&lang=fr" % (ville, cp)
        url = url.replace(' ','%20')
        f = urlopen(url, timeout=5)
        xml = f.read()
        
        if "problem_cause" in xml : 
            return None

        # Lit la météo du jour
        posG, posD, dictMeteo["jour"]["condition"] = RechercheData(xml, "condition data", 0)
        posG, posD, dictMeteo["jour"]["temp"] = RechercheData(xml, "temp_c data", posD)
        posG, posD, dictMeteo["jour"]["humidite"] = RechercheData(xml, "humidity data", posD)
        posG, posD, dictMeteo["jour"]["image"] = RechercheData(xml, "icon data", posD)
        posG, posD, dictMeteo["jour"]["vent"] = RechercheData(xml, "wind_condition data", posD)

        # Lit les prévisions
        for numJour in range(0, 4) :
            dictTemp = {}
            posG, posD, dictTemp["jour"] = RechercheData(xml, "day_of_week data", posD)
            posG, posD, dictTemp["temp_min"] = RechercheData(xml, "low data", posD)
            posG, posD, dictTemp["temp_max"] = RechercheData(xml, "high data", posD)
            posG, posD, dictTemp["image"] = RechercheData(xml, "icon data", posD)
            posG, posD, dictTemp["condition"] = RechercheData(xml, "condition data", posD)
            dictMeteo["previsions"].append(dictTemp)

    except Exception as err:
        #print "Probleme dans la recherche du bulletin meteo. \nErreur detectee :%s" % err
        return None
        
    return dictMeteo

    
            
if __name__ == '__main__':
    print(Meteo("Lannilis", "29870"))
    
    