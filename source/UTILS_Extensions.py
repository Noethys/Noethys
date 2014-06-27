#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import os
import sys
import importlib


def Extensions(ext="py"):
    """ Chargement d'une extension """
    # Recherche d'extensions dans le répertoire
    chemin = os.curdir
    fichiers = os.listdir(chemin)
    fichiers.sort()
    listeExtensions = []
    for fichier in fichiers :
        if fichier.endswith(ext) :
            nomFichier = os.path.split(fichier)[1]
            titre = nomFichier[:-(len(ext)+1)]
            listeExtensions.append(titre)
    
    if len(listeExtensions) == 0 :
        dlg = wx.MessageDialog(None, u"Aucune extension n'est installée !", u"Extensions", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False

    # Demande l'extension à charger
    dlg = wx.SingleChoiceDialog(None, u"Sélectionnez une extension dans la liste proposée :", "Chargement d'une extension", listeExtensions)
    dlg.SetSize((500, 400))
    dlg.CenterOnScreen() 
    nomExtension = None
    if dlg.ShowModal() == wx.ID_OK :
        nomExtension = dlg.GetStringSelection()
    dlg.Destroy()
    
    if nomExtension == None :
        return False
    
    # Exécution de l'extension
    sys.path.append(chemin)
    module = importlib.import_module(nomExtension)
    module.Extension()



if __name__ == u"__main__":
    app = wx.App(0)
    Extensions()
    app.MainLoop()
