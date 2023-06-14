#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
from Ctrl import CTRL_Bouton_image


def GetIDutilisateur():
    """ Récupère le IDutilisateur actif dans la fenêtre principale """
    IDutilisateur = None
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
    if nomWindow == "general" : 
        dictUtilisateur = topWindow.dictUtilisateur
        if dictUtilisateur != None :
            IDutilisateur = dictUtilisateur["IDutilisateur"]
    return IDutilisateur
    

def GetDictUtilisateur():
    """ Récupère le dictUtilisateur actif dans la fenêtre principale """
    dictUtilisateur = None
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
    if nomWindow == "general" : 
        dictUtilisateur = topWindow.dictUtilisateur
    return dictUtilisateur

def GetAutreDictUtilisateur(IDutilisateur=None):
    """ Récupère un dictUtilisateur autre que l'utilisateur actif """
    dictUtilisateur = None
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
    if nomWindow == "general" : 
        listeUtilisateurs = topWindow.listeUtilisateurs
        for dictTemp in listeUtilisateurs :
            if dictTemp["IDutilisateur"] == IDutilisateur :
                return dictTemp
    return dictUtilisateur
