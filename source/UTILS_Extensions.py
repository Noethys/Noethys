#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import sys
import importlib


def Extensions(ext="py"):
    """ Chargement d'une extension """
    # Recherche d'extensions dans le r�pertoire
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
        dlg = wx.MessageDialog(None, _(u"Aucune extension n'est install�e !"), _(u"Extensions"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False

    # Demande l'extension � charger
    dlg = wx.SingleChoiceDialog(None, _(u"S�lectionnez une extension dans la liste propos�e :"), "Chargement d'une extension", listeExtensions)
    dlg.SetSize((500, 400))
    dlg.CenterOnScreen() 
    nomExtension = None
    if dlg.ShowModal() == wx.ID_OK :
        nomExtension = dlg.GetStringSelection()
    dlg.Destroy()
    
    if nomExtension == None :
        return False
    
    # Ex�cution de l'extension
    sys.path.append(chemin)
    module = importlib.import_module(nomExtension)
    module.Extension()



if __name__ == u"__main__":
    app = wx.App(0)
    Extensions()
    app.MainLoop()
