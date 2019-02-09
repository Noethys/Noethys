#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
import os
import sys
import shutil
import platform
import subprocess
from Utils import UTILS_Customize
import appdirs
import six


def GetRepData(fichier=""):
    # Vérifie si un répertoire 'Portable' existe
    chemin = Chemins.GetMainPath("Portable")
    if os.path.isdir(chemin):
        chemin = os.path.join(chemin, "Data")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)
        return os.path.join(chemin, fichier)

    # Recherche s'il existe un chemin personnalisé dans le Customize.ini
    chemin = UTILS_Customize.GetValeur("repertoire_donnees", "chemin", "")
    #chemin = chemin.decode("iso-8859-15")
    if chemin != "" and os.path.isdir(chemin):
        return os.path.join(chemin, fichier)

    # Recherche le chemin du répertoire des données
    if sys.platform == "win32" and platform.release() != "Vista" :

        chemin = appdirs.site_data_dir(appname=None, appauthor=False)
        #chemin = chemin.decode("iso-8859-15")

        chemin = os.path.join(chemin, "noethys")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)

    else :

        chemin = appdirs.user_data_dir(appname=None, appauthor=False)
        #chemin = chemin.decode("iso-8859-15")

        chemin = os.path.join(chemin, "noethys")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)

        chemin = os.path.join(chemin, "Data")
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
    """ Recherche le répertoire Utilisateur pour stockage des fichiers de config et provisoires """
    chemin = None

    # Vérifie si un répertoire 'Portable' existe
    chemin = Chemins.GetMainPath("Portable")
    if os.path.isdir(chemin):
        return os.path.join(chemin, fichier)

    # Recherche le chemin du répertoire de l'utilisateur
    chemin = appdirs.user_config_dir(appname=None, appauthor=False, roaming=True)
    #chemin = chemin.decode("iso-8859-15")

    # Ajoute 'noethys' dans le chemin et création du répertoire
    chemin = os.path.join(chemin, "noethys")
    if not os.path.isdir(chemin):
        os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)

def DeplaceFichiers():
    """ Vérifie si des fichiers du répertoire Data ou du répertoire Utilisateur sont à déplacer vers le répertoire Utilisateur>AppData>Roaming """

    # Déplace les fichiers de config et le journal
    for nom in ("journal.log", "Config.json", "Customize.ini") :
        for rep in ("", Chemins.GetMainPath("Data"), os.path.join(os.path.expanduser("~"), "noethys")) :
            fichier = os.path.join(rep, nom)
            if os.path.isfile(fichier) :
                print(["deplacement fichier config :", fichier, " > ", GetRepUtilisateur(nom)])
                shutil.move(fichier, GetRepUtilisateur(nom))

    # Déplace les fichiers xlang
    if os.path.isdir(Chemins.GetMainPath("Lang")) :
        for nomFichier in os.listdir(Chemins.GetMainPath("Lang")) :
            if nomFichier.endswith(".xlang") :
                print(["deplacement fichier xlang :", fichier, " > ", GetRepLang(nomFichier)])
                shutil.move(u"Lang/%s" % nomFichier, GetRepLang(nomFichier))

    # Déplace les fichiers du répertoire Sync
    if os.path.isdir(Chemins.GetMainPath("Sync")) :
        for nomFichier in os.listdir(Chemins.GetMainPath("Sync")) :
            shutil.move(Chemins.GetMainPath("Sync/%s" % nomFichier), GetRepSync(nomFichier))

    # Déplace les fichiers de données du répertoire Data
    if GetRepData() != "Data/" and os.path.isdir(Chemins.GetMainPath("Data")) :
        for nomFichier in os.listdir(Chemins.GetMainPath("Data")) :
            if six.PY2:
                nomFichier = nomFichier.decode("iso-8859-15")
            if nomFichier.endswith(".dat") and "_" in nomFichier and "EXEMPLE_" not in nomFichier and "_archive.dat" not in nomFichier :
                # Déplace le fichier vers le répertoire des fichiers de données
                print(["copie base de donnees :", nomFichier, " > ", GetRepData(nomFichier)])
                shutil.copy(Chemins.GetMainPath(u"Data/%s" % nomFichier), GetRepData(nomFichier))
                # Renomme le fichier de données en archive (par sécurité)
                try :
                    os.rename(Chemins.GetMainPath(u"Data/%s" % nomFichier), Chemins.GetMainPath(u"Data/%s" % nomFichier.replace(".dat", "_archive.dat")))
                except :
                    pass

def DeplaceExemples():
    """ Déplace les fichiers exemples vers le répertoire des fichiers de données """
    if GetRepData() != "Data/" :
        chemin = Chemins.GetStaticPath("Exemples")
        for nomFichier in os.listdir(chemin) :
            if nomFichier.endswith(".dat") and "EXEMPLE_" in nomFichier :
                # Déplace le fichier vers le répertoire des fichiers de données
                shutil.copy(os.path.join(chemin, nomFichier), GetRepData(nomFichier))

def OuvrirRepertoire(rep):
    if platform.system() == "Windows":
        subprocess.Popen(["explorer", rep])
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", rep])
    else:
        subprocess.Popen(["xdg-open", rep])



if __name__ == "__main__":
    # Teste les déplacements de fichiers
    # DeplaceFichiers()

    # Répertoire utilisateur
    print(GetRepUtilisateur())

    # Répertoire des données
    chemin = GetRepData()
    print(1, os.path.join(chemin, u"Testé.pdf"))
    print(2, os.path.join(chemin, "Test.pdf"))