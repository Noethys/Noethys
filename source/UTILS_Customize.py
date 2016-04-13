#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import os
import ConfigParser
import UTILS_Fichiers


LISTE_DONNEES = [
    ("interface", [
        ("theme", "Vert"),
    ]),
    ("utilisateur", [
        ("pass", ""),
    ]),
    ("journal", [
        ("actif", "1"),
        ("nom", "journal.log"),
    ]),
    ("correction_anomalies", [
        ("actif", "1"),
    ]),
]


def GetNomFichier(nomFichier="Customize.ini"):
    return UTILS_Fichiers.GetRepUtilisateur(nomFichier)


class Customize():
    def __init__(self):
        self.nomFichier = GetNomFichier()
        self.cfg = ConfigParser.ConfigParser()
        self.InitFichier()


    def InitFichier(self):
        """ Création d'un nouveau fichier ou vérification du fichier existant """
        # Lit le fichier s'il existe
        if os.path.isfile(self.nomFichier) :
            self.cfg.read(self.nomFichier)

        dirty = False

        # Remplissage du cfg
        for section, valeurs in LISTE_DONNEES :
            if section not in self.cfg.sections() :
                self.cfg.add_section(section)
                dirty = True

            for cle, valeur in valeurs :
                if cle not in self.cfg.options(section) :
                    self.cfg.set(section, cle, valeur)
                    dirty = True

        # Enregistrement du fichier
        if dirty :
            self.Enregistrement()

    def GetCfg(self):
        return self.cfg

    def GetValeur(self, section="", cle="", defaut="", type_valeur=str):
        if self.cfg.has_section(section) and self.cfg.has_option(section, cle) :
            # Si la clé existe
            if type_valeur == int :
                return self.cfg.getint(section, cle)
            elif type_valeur == float :
                return self.cfg.getfloat(section, cle)
            elif type_valeur == bool :
                return self.cfg.getboolean(section, cle)
            else :
                return self.cfg.get(section, cle)
        else:
            # Si la clé n'existe pas
            self.cfg.SetValeur(section, cle, defaut)
            self.Enregistrement()
            return defaut

    def SetValeur(self, section="", cle="", valeur=""):
        if self.cfg.has_section(section) == False :
            self.cfg.add_section(section)
        self.cfg.set(section, cle, valeur)

    def Enregistrement(self):
        """ Enregistrement du fichier sur le disque dur """
        fichier = open(self.nomFichier, "w")
        self.cfg.write(fichier)
        fichier.close()


def GetCustomize():
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" :
        return topWindow.GetCustomize()
    else:
        return Customize()


def GetValeur(section="", cle="", defaut="", type_valeur=str):
    customize = GetCustomize()
    return customize.GetValeur(section, cle, defaut, type_valeur)

def SetValeur(section="", cle="", valeur=""):
    customize = GetCustomize()
    customize.SetValeur(section, cle, valeur)
    customize.Enregistrement()




# --------------- TESTS ----------------------------------------------------------------------------------------------------------
if __name__ == u"__main__":
    print "GET :", GetValeur("interface", "theme", "Vert")
    #print "SET :", GetValeur("interface", "theme", "Rouge")
    
