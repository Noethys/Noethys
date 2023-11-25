#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        # Si bytes
        elif isinstance(objet, bytes):
            return {'__type__': "bytes", 'data': objet.decode('utf8')}
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
        return wx.Colour(*objet['data'])
    # Si wx.Point
    elif objet.get('__type__') == 'wx.Point':
        return wx.Point(objet['data'][0], objet['data'][1])
    # Si bytes
    elif objet.get('__type__') == 'bytes':
        try:
            resultat = bytes(objet['data'], 'utf-8')
        except:
            resultat = bytes(objet['data'])
        return resultat
    # Si autre
    else:
        return objet


def Lire(nom_fichier="", conversion_auto=False):
    data = None
    is_json = True

    # Essaye d'ouvrir un fichier Json
    if six.PY3:
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
            print("Impossible d'ouvrir le fichier Json")
            print(err,)
            is_json = False

    if is_json == False :
        print("Ce n'est pas un fichier Json")

    # Essaye d'ouvrir le fichier au format shelve
    if is_json == False:
        try:
            fichier = shelve.open(nom_fichier, "r")
            data = {}
            for key, valeur in fichier.items():
                if type(key) == str:
                    key = key.decode("utf8")
                if type(valeur) == str:
                    valeur = valeur.decode("utf8")
                data[key] = valeur
            fichier.close()

            # Convertit le fichier shelve au format Json
            if conversion_auto == True :
                Ecrire(nom_fichier=nom_fichier, data=data)
        except Exception as err:
            print("Conversion du shelve en Json impossible :")
            print(err,)

    # Si aucune donnée trouvée, on lève une erreur
    if data == None :
        raise

    return data

def Ecrire(nom_fichier="", data={}):
    with open(nom_fichier, 'w') as outfile:
        json.dump(data, outfile, indent=4, cls=MyEncoder)




if __name__ == u"__main__":
    from Utils import UTILS_Fichiers

    # Test d'importation depuis un ancien fichier dat
    # nom_fichier_dat = UTILS_Fichiers.GetRepUtilisateur("Config_test.dat")
    # dictDonnees = {}
    # import shelve
    # db = shelve.open(nom_fichier_dat, "r")
    # for key in list(db.keys()):
    #     dictDonnees[key] = db[key]
    # db.close()
    # Ecrire(nom_fichier=UTILS_Fichiers.GetRepUtilisateur("Config_test.json"), data=dictDonnees)

    # Test de lecture du Config.json
    chemin_fichier = UTILS_Fichiers.GetRepUtilisateur("Config.json")
    with open(chemin_fichier) as json_file:
        data = json.load(json_file, object_hook=MyDecoder)
    print("data=", data)