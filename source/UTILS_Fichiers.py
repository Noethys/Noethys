#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os
import sys
import shutil
import platform
import subprocess
import UTILS_Customize
import appdirs


def GetRepData(fichier=""):
    # V�rifie si un r�pertoire 'Portable' existe
    chemin = "Portable"
    if os.path.isdir(chemin):
        chemin = os.path.join(chemin, "Data")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)
        return os.path.join(chemin, fichier)

    # Recherche s'il existe un chemin personnalis� dans le Customize.ini
    chemin = UTILS_Customize.GetValeur("repertoire_donnees", "chemin", "")
    chemin = chemin.decode("iso-8859-15")
    if chemin != "" and os.path.isdir(chemin):
        return os.path.join(chemin, fichier)

    if platform.release() == "Vista" :

        # Cr�ation du r�pertoire Data s'il n'existe pas
        chemin = os.path.join(GetRepUtilisateur(), "Data")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)

    else :

        # Recherche le chemin du r�pertoire des donn�es pour noethys
        chemin = appdirs.user_data_dir(appname="noethys", appauthor=False)
        chemin = chemin.decode("iso-8859-15")

        # Cr�ation du r�pertoire s'il n'existe pas
        if not os.path.isdir(chemin):
            os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)


def GetRepTemp(fichier=""):
    chemin = GetRepUtilisateur("Temp")
    return os.path.join(chemin, fichier)

def GetRepUpdates(fichier=""):
    chemin = GetRepUtilisateur("Updates")
    return os.path.join(chemin, fichier)

def GetRepLang(fichier=""):
    chemin = GetRepUtilisateur("Lang")
    return os.path.join(chemin, fichier)

def GetRepSync(fichier=""):
    chemin = GetRepUtilisateur("Sync")
    return os.path.join(chemin, fichier)

def GetRepUtilisateur(fichier=""):
    """ Recherche le r�pertoire Utilisateur pour stockage des fichiers de config et provisoires """
    chemin = None

    # # Variable d'environnement
    # for evar in ('XDG_CONFIG_HOME', 'APPDATA', 'LOCALAPPDATA'):
    #     path = os.environ.get(evar, None)
    #     if path and os.path.isdir(path):
    #         chemin = path
    #         break
    # if not chemin:
    #     # ... ou r�pertoire de l'utilisateur
    #     path = os.path.expanduser("~")
    #     if path != "~" and os.path.isdir(path):
    #         if sys.platform.startswith('linux'):
    #             chemin = os.path.join(path, '.config')
    #         else:
    #             chemin = path
    #     # ... ou dossier courrant.
    #     else:
    #         chemin = os.path.dirname(os.path.abspath(__file__))

    # V�rifie si un r�pertoire 'Portable' existe
    chemin = "Portable"
    if os.path.isdir(chemin):
        return os.path.join(chemin, fichier)

    # Recherche le chemin du r�pertoire de l'utilisateur
    chemin = appdirs.user_config_dir(appname=None, appauthor=False, roaming=True)
    chemin = chemin.decode("iso-8859-15")

    # Ajoute 'noethys' dans le chemin et cr�ation du r�pertoire
    chemin = os.path.join(chemin, "noethys")
    if not os.path.isdir(chemin):
        os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)

def DeplaceFichiers():
    """ V�rifie si des fichiers du r�pertoire Data ou du r�pertoire Utilisateur sont � d�placer vers le r�pertoire Utilisateur>AppData>Roaming """

    # D�place les fichiers de config et le journal
    for nom in ("journal.log", "Config.dat", "Customize.ini") :
        for rep in ("", "Data", os.path.join(os.path.expanduser("~"), "noethys")) :
            fichier = os.path.join(rep, nom)
            if os.path.isfile(fichier) :
                shutil.move(fichier, GetRepUtilisateur(nom))

    # D�place les fichiers xlang
    for nomFichier in os.listdir("Lang/") :
        if nomFichier.endswith(".xlang") :
            shutil.move(u"Lang/%s" % nomFichier, GetRepLang(nomFichier))

    # D�place les fichiers du r�pertoire Sync
    if os.path.isdir("Sync/") :
        for nomFichier in os.listdir("Sync/") :
            shutil.move(u"Sync/%s" % nomFichier, GetRepSync(nomFichier))

    # D�place les fichiers de donn�es du r�pertoire Data
    if GetRepData() != "Data/" :
        for nomFichier in os.listdir("Data/") :
            if nomFichier.endswith(".dat") and "_" in nomFichier and "EXEMPLE_" not in nomFichier and "_archive.dat" not in nomFichier :
                # D�place le fichier vers le r�pertoire des fichiers de donn�es
                shutil.copy(u"Data/%s" % nomFichier, GetRepData(nomFichier))
                # Renomme le fichier de donn�es en archive (par s�curit�)
                os.rename(u"Data/%s" % nomFichier, u"Data/%s" % nomFichier.replace(".dat", "_archive.dat"))

def DeplaceExemples():
    """ D�place les fichiers exemples vers le r�pertoire des fichiers de donn�es """
    if GetRepData() != "Data/" :
        for nomFichier in os.listdir("Data/") :
            if nomFichier.endswith(".dat") and "EXEMPLE_" in nomFichier :
                # D�place le fichier vers le r�pertoire des fichiers de donn�es
                shutil.copy(u"Data/%s" % nomFichier, GetRepData(nomFichier))

def OuvrirRepertoire(rep):
    if platform.system() == "Windows":
        subprocess.Popen(["explorer", rep])
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", rep])
    else:
        subprocess.Popen(["xdg-open", rep])



if __name__ == "__main__":
    # Teste les d�placements de fichiers
    # DeplaceFichiers()

    # R�pertoire utilisateur
    print GetRepUtilisateur()

    # R�pertoire des donn�es
    chemin = GetRepData()
    print 1, os.path.join(chemin, u"Test�.pdf")
    print 2, os.path.join(chemin, "Test.pdf")
