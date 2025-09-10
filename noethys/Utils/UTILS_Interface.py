#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Utils import UTILS_Customize

THEMES = [
    ("Vert", _(u"Vert (Par défaut)")),
    ("Bleu", _(u"Bleu")),
    ("Noir", _(u"Noir")),
]

DONNEES = {

    "Vert" : {
        "couleur_tres_foncee" : wx.Colour(33, 104, 0), # Fond Astuces page d'accueil
        "couleur_claire" : wx.Colour(137, 206, 27), # Texte du splash screen
        "couleur_tres_claire" : wx.Colour(240, 251, 237), # Lignes des listes
        "couleur_tres_claire_2" : wx.Colour(214, 250, 199), # Cadre Contacts de la fiche famille
    },

    "Bleu" : {
        "couleur_tres_foncee" : wx.Colour(0, 50, 95),
        "couleur_claire" : wx.Colour(0, 121, 204),
        "couleur_tres_claire" : wx.Colour(234, 240, 255),
        "couleur_tres_claire_2" : wx.Colour(211, 224, 250),
    },

    "Noir" : {
        "couleur_tres_foncee" : wx.Colour(0, 0, 0),
        "couleur_claire" : wx.Colour(150, 150, 150),
        "couleur_tres_claire" : wx.Colour(240, 240, 240),
        "couleur_tres_claire_2" : wx.Colour(230, 230, 230),
    },

}

def GetTheme() :
    return UTILS_Customize.GetValeur("interface", "theme", "Vert")

def SetTheme(theme="Vert"):
    UTILS_Customize.SetValeur("interface", "theme", theme)

def GetValeur(cle="", defaut="", theme=None):
    # lecture du thème
    if theme == None :
        theme = UTILS_Customize.GetValeur("interface", "theme", "Vert")

    # Lecture de la valeur
    if theme in DONNEES :
        if cle in DONNEES[theme]:
            return DONNEES[theme][cle]

    # Sinon renvoie la valeur par défaut
    return defaut


if __name__ == '__main__':
    print(GetValeur("couleur_tres_fonce", wx.Colour(255, 0, 0)))