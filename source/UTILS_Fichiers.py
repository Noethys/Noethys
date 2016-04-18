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
import sys


def GetRepTemp(fichier=""):
    chemin = GetRepUtilisateur("Temp")
    return os.path.join(chemin, fichier)

def GetRepUpdates(fichier=""):
    chemin = GetRepUtilisateur("Updates")
    return os.path.join(chemin, fichier)


def GetRepUtilisateur(fichier=""):
    """'safer' function to find user path."""
    chemin = None

    # Variable d'environnement
    for evar in ('XDG_CONFIG_HOME', 'LOCALAPPDATA', 'APPDATA'):
        path = os.environ.get(evar, None)
        if path and os.path.isdir(path):
            chemin = path
            break
    if not chemin:
        # ... ou répertoire de l'utilisateur
        path = os.path.expanduser("~")
        if path != "~" and os.path.isdir(path):
            if sys.platform.startswith('linux'):
                chemin = os.path.join(path, '.config')
            else:
                chemin = path
        # ... ou dossier courrant.
        else:
            chemin = os.path.dirname(os.path.abspath(__file__))

    # Ajoute 'noethys' dans le chemin et création du répertoire
    chemin = os.path.join(chemin, "noethys")
    if not os.path.isdir(chemin):
        os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)


if __name__ == "__main__":
    print "Chemin Fichier config =", GetRepUtilisateur("Config.dat")
    print "Repertoire Temp =", GetRepTemp()
    print "Fichier Txt dans repertoire Temp =", GetRepTemp("Test.txt")
