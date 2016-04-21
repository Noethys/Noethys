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
import shutil


def GetRepTemp(fichier=""):
    chemin = GetRepUtilisateur("Temp")
    return os.path.join(chemin, fichier)

def GetRepUpdates(fichier=""):
    chemin = GetRepUtilisateur("Updates")
    return os.path.join(chemin, fichier)


def GetRepUtilisateur(fichier=""):
    """ Recherche le répertoire Utilisateur pour stockage des fichiers de config et provisoires """
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

def DeplaceFichiers():
    """ Vérifie si des fichiers du répertoire Data ou du répertoire Utilisateur sont à déplacer vers le répertoire Utilisateur>AppData>Roaming """
    for nom in ("journal.log", "Config.dat", "Customize.ini") :
        for rep in ("", "Data", os.path.join(os.path.expanduser("~"), "noethys")) :
            fichier = os.path.join(rep, nom)
            if os.path.isfile(fichier) :
                nouveauNom = GetRepUtilisateur(nom)
                shutil.move(fichier, nouveauNom)




if __name__ == "__main__":
    # Test les chemins
    print "Chemin Fichier config =", GetRepUtilisateur("Config.dat")

    # Test les déplacements de fichiers
    DeplaceFichiers()
