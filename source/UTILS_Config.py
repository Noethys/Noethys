#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import wx
import CTRL_Bouton_image
import os


class FichierConfig():
    def __init__(self, nomFichier="" ):
        self.nomFichier = nomFichier
        
    def GetDictConfig(self):
        """ Recupere une copie du dictionnaire du fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "r")
        dictDonnees = {}
        for key in db.keys():
            dictDonnees[key] = db[key]
            #print key, db[key]
        db.close()
        return dictDonnees
    
    def SetDictConfig(self, dictConfig={} ):
        """ Remplace le fichier de config pr�sent sur le disque dur par le dict donn� """
        import shelve
        db = shelve.open(self.nomFichier, "n")
        for key in dictConfig.keys():
            db[key] = dictConfig[key]
        db.close()
        
    def GetItemConfig(self, key, defaut=None):
        """ R�cup�re une valeur du dictionnaire du fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "r")
        if db.has_key(key) :
            valeur = db[key]
        else:
            valeur = defaut
        db.close()
        return valeur
    
    def SetItemConfig(self, key, valeur ):
        """ Remplace une valeur dans le fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "w")
        db[key] = valeur
        db.close()

    def SetItemsConfig(self, dictParametres={}):
        """ Remplace plusieurs valeur dans le fichier de config """
        """ dictParametres = {nom : valeur, nom : valeur...} """
        import shelve
        db = shelve.open(self.nomFichier, "w")
        for key, valeur in dictParametres.iteritems() :
            db[key] = valeur
        db.close()

    def DelItemConfig(self, key ):
        """ Supprime une valeur dans le fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "w")
        del db[key]
        db.close()



def GetParametre(nomParametre="", defaut=None):
    parametre = None
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est charg�e, on y r�cup�re le dict de config
        if topWindow.userConfig.has_key(nomParametre) :
            parametre = topWindow.userConfig[nomParametre]
        else :
            parametre = defaut
    else:
        # R�cup�ration du nom de la DB directement dans le fichier de config sur le disque dur
        nomFichierConfig = "Data/Config.dat"
        cfg = FichierConfig(nomFichierConfig)
        parametre = cfg.GetItemConfig(nomParametre, defaut)
    return parametre

def SetParametre(nomParametre="", parametre=None):
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est charg�e, on y r�cup�re le dict de config
        topWindow.userConfig[nomParametre] = parametre
    else:
        # Enregistrement du nom de la DB directement dans le fichier de config sur le disque dur
        nomFichierConfig = "Data/Config.dat"
        cfg = FichierConfig(nomFichierConfig)
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
        
    # Cherche la sources des donn�es
    if nomWindow == "general" : 
        dictSource = topWindow.userConfig
    else :
        nomFichierConfig = "Data/Config.dat"
        cfg = FichierConfig(nomFichierConfig)
        dictSource = cfg.GetDictConfig()
        
    # Lit les donn�es
    for nom, valeur in dictParametres.iteritems() :
        if dictSource.has_key(nom) :
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
        # Si la frame 'General' est charg�e, on y r�cup�re le dict de config
        for nom, valeur in dictParametres.iteritems() :
            topWindow.userConfig[nom] = valeur
    else:
        # Enregistrement dans le fichier de config sur le disque dur
        nomFichierConfig = "Data/Config.dat"
        cfg = FichierConfig(nomFichierConfig)
        cfg.SetItemsConfig(dictParametres)
    return dictParametres



# --------------- TESTS ----------------------------------------------------------------------------------------------------------
if __name__ == u"__main__":
    print "GET :", GetParametres( {"impression_factures_impayes" : 0} ) 
    print "SET :", SetParametres( {"test1" : True, "test2" : True} )
    
