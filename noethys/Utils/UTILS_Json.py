#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
import wx
import os
import datetime
import decimal
import json
import shelve
import six


def DateEngEnDateDD(dateEng):
    if dateEng in (None, "", "None") : return None
    if type(dateEng) == datetime.date : return dateEng
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngEnDateDDT(dateEng):
    if dateEng in (None, "", "None") : return None
    if type(dateEng) == datetime.datetime : return dateEng
    if len(dateEng) == 19 :
        return datetime.datetime.strptime(dateEng, "%Y-%m-%d %H:%M:%S")
    else :
        return datetime.datetime.strptime(dateEng, "%Y-%m-%d %H:%M:%S.%f")



class MyEncoder(json.JSONEncoder):
    def default(self, objet):
        # Si datetime.date
        if isinstance(objet, datetime.date):
            return {'__type__': "datetime.date", 'data': str(objet)}
        # Si datetime.datetime
        elif isinstance(objet, datetime.datetime):
            return {'__type__': "datetime.datetime", 'data': str(objet)}
        # Si decimal
        elif isinstance(objet, decimal.Decimal):
            return {'__type__': "decimal.Decimal", 'data': str(objet)}
        # Si wx.Colour
        elif isinstance(objet, wx.Colour):
            return {'__type__': "wx.Colour", 'data': objet.Get()}
        # Si wx.Point
        elif isinstance(objet, wx.Point):
            return {'__type__': "wx.Point", 'data': objet.Get()}
        # Si autre
        return json.JSONEncoder.default(self, objet)


def MyDecoder(objet):
    # Si datetime.date
    if objet.get('__type__') == 'datetime.date':
        return DateEngEnDateDD(objet['data'])
    # Si datetime.datetime
    elif objet.get('__type__') == 'datetime.datetime':
        return DateEngEnDateDDT(objet['data'])
    # Si decimal
    elif objet.get('__type__') == 'decimal.Decimal':
        return decimal.Decimal(objet['data'])
    # Si wx.Colour
    elif objet.get('__type__') == 'wx.Colour':
        return wx.Colour().Set(objet['data'])
    # Si wx.Point
    elif objet.get('__type__') == 'wx.Point':
        return wx.Point(objet['data'][0], objet['data'][1])
    # Si autre
    else:
        return objet


def Lire(nom_fichier="", conversion_auto=False):
    data = {}
    is_json = True

    # Essaye d'ouvrir un fichier Json
    if 'phoenix' in wx.PlatformInfo:
        try:
            with open(nom_fichier) as json_file:
                data = json.load(json_file, object_hook=MyDecoder)
        except json.decoder.JSONDecodeError:
            is_json = False
    else :
        try:
            with open(nom_fichier) as json_file:
                data = json.load(json_file, object_hook=MyDecoder)
        except Exception as err:
            is_json = False

    # Essaye d'ouvrir le fichier au format shelve
    if is_json == False:
        fichier = shelve.open(nom_fichier, "r")
        data = {}
        for key, valeur in fichier.items():
            if type(key) == str:
                key = key.decode("iso-8859-15")
            if type(valeur) == str:
                valeur = valeur.decode("iso-8859-15")
            data[key] = valeur
        fichier.close()

        # Convertit le fichier shelve au format Json
        if conversion_auto == True :
            Ecrire(nom_fichier=nom_fichier, data=data)
    return data

def Ecrire(nom_fichier="", data={}):
    with open(nom_fichier, 'w') as outfile:
        json.dump(data, outfile, indent=4, cls=MyEncoder)




if __name__ == u"__main__":
    # Test d'importation depuis un ancien fichier dat
    from Utils import UTILS_Fichiers
    nom_fichier_dat = UTILS_Fichiers.GetRepUtilisateur("Config_test.dat")
    dictDonnees = {}
    import shelve
    db = shelve.open(nom_fichier_dat, "r")
    for key in list(db.keys()):
        dictDonnees[key] = db[key]
    db.close()
    Ecrire(nom_fichier=UTILS_Fichiers.GetRepUtilisateur("Config_test.json"), data=dictDonnees)

