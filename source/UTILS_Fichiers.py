#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os


def GetRepTemp(fichier=""):
    chemin = GetRepUtilisateur("Temp")
    return os.path.join(chemin, fichier)

def GetRepUpdates(fichier=""):
    chemin = GetRepUtilisateur("Updates")
    return os.path.join(chemin, fichier)


def GetRepUtilisateur(fichier=""):
    """'safer' function to find user path."""
    chemin = None

    try:
        path = os.path.expanduser("~")
        if os.path.isdir(path):
            chemin = path
    except:
        pass

    # Autre méthode
    if chemin == None :
        for evar in ('HOME', 'USERPROFILE', 'TMP'):
            try:
                path = os.environ[evar]
                if os.path.isdir(path):
                    chemin = path
                    break
            except:
                pass

    if chemin == None :
        chemin = os.path.dirname(os.path.abspath(__file__))

    # Création du répertoire noethys si besoin
    chemin = os.path.join(chemin, "noethys")
    if os.path.isdir(chemin) == False :
        os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)


if __name__ == "__main__":
    print "Chemin Fichier config =", GetRepUtilisateur("Config.dat")
    print "Repertoire Temp =", GetRepTemp()
    print "Fichier Txt dans repertoire Temp =", GetRepTemp("Test.txt")