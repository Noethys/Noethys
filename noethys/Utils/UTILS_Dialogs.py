#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
import wx
import os.path
from Utils import UTILS_Config


def GetNomModule(chemin_module=""):
    nom_module = os.path.basename(chemin_module)
    for extension in (".pyc", ".py") :
        nom_module = nom_module.replace(extension, "")
    return nom_module


def AjusteSizePerso(parent=None, chemin_module=""):
    """ Ajuste la taille de la fenêtre selon les souhaits de l'utilisateur """
    nom_module = GetNomModule(chemin_module)
    taille_fenetre = UTILS_Config.GetParametre(nom_module)
    if taille_fenetre != None :
        if taille_fenetre == (0, 0) or taille_fenetre == [0, 0]:
            parent.Maximize(True)
        else:
            parent.SetSize(taille_fenetre)


def SaveSizePerso(parent=None, chemin_module=""):
    """ Mémorise la taille de la fenêtre """
    nom_module = GetNomModule(chemin_module)
    if parent.IsMaximized() == True :
        taille_fenetre = (0, 0)
    else:
        taille_fenetre = tuple(parent.GetSize())
    UTILS_Config.SetParametre(nom_module, taille_fenetre)




if __name__ == "__main__":
    pass