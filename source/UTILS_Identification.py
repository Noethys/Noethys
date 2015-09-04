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


def GetIDutilisateur():
    """ R�cup�re le IDutilisateur actif dans la fen�tre principale """
    IDutilisateur = None
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
    if nomWindow == "general" : 
        dictUtilisateur = topWindow.dictUtilisateur
        if dictUtilisateur != None :
            IDutilisateur = dictUtilisateur["IDutilisateur"]
    return IDutilisateur
    

def GetDictUtilisateur():
    """ R�cup�re le dictUtilisateur actif dans la fen�tre principale """
    dictUtilisateur = None
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
    if nomWindow == "general" : 
        dictUtilisateur = topWindow.dictUtilisateur
    return dictUtilisateur

def GetAutreDictUtilisateur(IDutilisateur=None):
    """ R�cup�re un dictUtilisateur autre que l'utilisateur actif """
    dictUtilisateur = None
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
    if nomWindow == "general" : 
        listeUtilisateurs = topWindow.listeUtilisateurs
        for dictTemp in listeUtilisateurs :
            if dictTemp["IDutilisateur"] == IDutilisateur :
                return dictTemp
    return dictUtilisateur
