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
import six
import shutil
from Utils import UTILS_Fichiers
from Utils import UTILS_Json




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
    if os.path.isfile(nom_fichier_dat) and six.PY2:
        print("Importation de l'ancien config de config dat")
        nom_fichier_dat = nom_fichier_dat.encode("iso-8859-15")

        import shelve
        db = shelve.open(nom_fichier_dat, "r")
        for key in list(db.keys()):
            dictDonnees[key] = db[key]
        db.close()
        nouveau_fichier = False

        # Supprime l'ancien fichier dat
        os.remove(nom_fichier_dat)

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
            "pool_mysql": 0,
            }

    # Création d'un nouveau fichier json
    cfg = FichierConfig()
    cfg.SetDictConfig(dictConfig=dictDonnees)

    print("nouveau_fichier = %s" % nouveau_fichier)
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
        data = {}
        try :
            data = UTILS_Json.Lire(self.nomFichier)
        except:
            nom_fichier_bak = self.nomFichier + ".bak"
            if os.path.isfile(nom_fichier_bak):
                print("Recuperation de config.json.bak")
                data = UTILS_Json.Lire(nom_fichier_bak)
        return data

    def SetDictConfig(self, dictConfig={}):
        """ Remplace le fichier de config présent sur le disque dur par le dict donné """
        UTILS_Json.Ecrire(nom_fichier=self.nomFichier, data=dictConfig)
        # Création d'une copie de sauvegarde du config
        shutil.copyfile(self.nomFichier, self.nomFichier + ".bak")

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

