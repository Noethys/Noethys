#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import wx
import os
try :
    from Utils import UTILS_Adaptations
except:
    import UTILS_Adaptations
UTILS_Fichiers = UTILS_Adaptations.Import("Utils.UTILS_Fichiers")
UTILS_Dates = UTILS_Adaptations.Import("Utils.UTILS_Dates")
import six
import datetime
import decimal
import json



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
        # Si autre
        return json.JSONEncoder.default(self, objet)


def MyDecoder(objet):
    # Si datetime.date
    if objet.get('__type__') == 'datetime.date':
        return UTILS_Dates.DateEngEnDateDD(objet['data'])
    # Si datetime.datetime
    elif objet.get('__type__') == 'datetime.datetime':
        return UTILS_Dates.DateEngEnDateDDT(objet['data'])
    # Si decimal
    elif objet.get('__type__') == 'decimal.Decimal':
        return decimal.Decimal(objet['data'])
    # Si autre
    else:
        return objet



def GetNomFichierConfig(nomFichier="Config.json"):
    return UTILS_Fichiers.GetRepUtilisateur(nomFichier)

def IsFichierExists() :
    nomFichier = GetNomFichierConfig()
    return os.path.isfile(nomFichier)

def GenerationFichierConfig():
    dictDonnees = {}
    nouveau_fichier = True

    # Importe l'ancien fichier 'config' s'il existe
    nom_fichier_dat = UTILS_Fichiers.GetRepUtilisateur("Config.dat")
    if os.path.isfile(nom_fichier_dat):
        if six.PY2:
            nom_fichier_dat = nom_fichier_dat.encode("iso-8859-15")
        try:
            import shelve
            db = shelve.open(nom_fichier_dat, "r")
            for key in list(db.keys()):
                dictDonnees[key] = db[key]
            db.close()
            nouveau_fichier = False
        except:
            pass

        # Supprime l'ancien fichier dat
        try :
            os.remove(nom_fichier_dat)
        except:
            pass

    # Crée les nouvelles données
    if nouveau_fichier == True :
        dictDonnees = {
            "nomFichier": "",
            "derniersFichiers": [],
            "taille_fenetre": (0, 0),
            "dict_selection_periodes_activites": {
                'listeActivites': [],
                'listeSelections': (),
                'listePeriodes': [],
                'modeAffichage': 'nbrePlacesPrises',
                'dateDebut': None,
                'dateFin': None,
                'annee': None,
                'page': 0,
                },
            "assistant_demarrage": False,
            "perspectives": [],
            "perspective_active": None,
            "annonce": None,
            "autodeconnect": None,
            "interface_mysql": "mysqldb",
            }
    # Création d'un nouveau fichier json
    cfg = FichierConfig()
    cfg.SetDictConfig(dictConfig=dictDonnees)
    return nouveau_fichier

def SupprimerFichier():
    nomFichier = GetNomFichierConfig()
    os.remove(nomFichier)



class FichierConfig():
    def __init__(self):
        nomFichier = GetNomFichierConfig()
        if six.PY2:
            nomFichier = nomFichier.encode("iso-8859-15")
        self.nomFichier = nomFichier
        
    def GetDictConfig(self):
        """ Recupere une copie du dictionnaire du fichier de config """
        with open(self.nomFichier) as json_file:
            data = json.load(json_file, object_hook=MyDecoder)
        return data
    
    def SetDictConfig(self, dictConfig={} ):
        """ Remplace le fichier de config présent sur le disque dur par le dict donné """
        with open(self.nomFichier, 'w') as outfile:
            json.dump(dictConfig, outfile, cls=MyEncoder)

    def GetItemConfig(self, key, defaut=None):
        """ Récupère une valeur du dictionnaire du fichier de config """
        data = self.GetDictConfig()
        if key in data :
            valeur = data[key]
        else:
            valeur = defaut
        return valeur
    
    def SetItemConfig(self, key, valeur ):
        """ Remplace une valeur dans le fichier de config """
        data = self.GetDictConfig()
        data[key] = valeur
        self.SetDictConfig(data)

    def SetItemsConfig(self, dictParametres={}):
        """ Remplace plusieurs valeur dans le fichier de config """
        """ dictParametres = {nom : valeur, nom : valeur...} """
        data = self.GetDictConfig()
        for key, valeur in dictParametres.items():
            data[key] = valeur
        self.SetDictConfig(data)

    def DelItemConfig(self, key ):
        """ Supprime une valeur dans le fichier de config """
        data = self.GetDictConfig()
        del data[key]
        self.SetDictConfig(data)



def GetParametre(nomParametre="", defaut=None):
    parametre = None
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est chargée, on y récupère le dict de config
        if nomParametre in topWindow.userConfig :
            parametre = topWindow.userConfig[nomParametre]
        else :
            parametre = defaut
    else:
        # Récupération du nom de la DB directement dans le fichier de config sur le disque dur
        cfg = FichierConfig()
        parametre = cfg.GetItemConfig(nomParametre, defaut)
    return parametre

def SetParametre(nomParametre="", parametre=None):
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est chargée, on y récupère le dict de config
        topWindow.userConfig[nomParametre] = parametre
    else:
        # Enregistrement du nom de la DB directement dans le fichier de config sur le disque dur
        cfg = FichierConfig()
        cfg.SetItemConfig(nomParametre, parametre)



# --------------Traitement par lot ------------------------------------------------------------------------------------------

def GetParametres(dictParametres={}):
    """ dictParametres = {nom : valeur, nom: valeur...} """
    dictFinal = {}
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
        
    # Cherche la sources des données
    if nomWindow == "general" : 
        dictSource = topWindow.userConfig
    else :
        cfg = FichierConfig()
        dictSource = cfg.GetDictConfig()
        
    # Lit les données
    for nom, valeur in dictParametres.items() :
        if nom in dictSource :
            dictFinal[nom] = dictSource[nom]
        else :
            dictFinal[nom] = valeur
    return dictFinal



def SetParametres(dictParametres={}):
    """ dictParametres = {nom : valeur, nom: valeur...} """
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est chargée, on y récupère le dict de config
        for nom, valeur in dictParametres.items() :
            topWindow.userConfig[nom] = valeur
    else:
        # Enregistrement dans le fichier de config sur le disque dur
        cfg = FichierConfig()
        cfg.SetItemsConfig(dictParametres)
    return dictParametres



# --------------- TESTS ----------------------------------------------------------------------------------------------------------
if __name__ == u"__main__":
    print("GET :", GetParametres( {"impression_factures_impayes" : 0} ))
    #print("SET :", SetParametres( {"test1" : True, "test2" : True} ))

