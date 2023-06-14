#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
import os
import re
import six
from Utils import UTILS_Fichiers
from Utils import UTILS_Json
import codecs


DICT_TRADUCTIONS = None

def ChargeTraduction(nom=""):
    """ Charge un fichier de langage """
    global DICT_TRADUCTIONS
    dictTraductions = {}
    
    # Recherche le fichier de langage par défaut ".lang" puis un éventuel fichier perso ".xlang"
    for rep in (Chemins.GetStaticPath("Lang"), UTILS_Fichiers.GetRepLang()) :
        for extension in ("lang", "xlang") :
            nomFichier = os.path.join(rep, u"%s.%s" % (nom, extension))
            if os.path.isfile(nomFichier) :
                data = UTILS_Json.Lire(nomFichier, conversion_auto=True)
                for key, valeur in data.items():
                    dictTraductions[key] = valeur

    # Mémorise les traductions
    DICT_TRADUCTIONS = dictTraductions
    
    
    
def _(chaine) :
    """ Traduit une chaîne """
    # Recherche si une traduction existe
    if DICT_TRADUCTIONS != None :
        if chaine in DICT_TRADUCTIONS :
            return DICT_TRADUCTIONS[chaine]
    
    # Sinon renvoie la chaine par défaut
    return chaine



def GenerationFichierTextes() :
    chemin_noethys = Chemins.GetMainPath()
    dictTextes = {}
    # Recherche des textes
    exp = re.compile(r"_\(u\".*?\"\)")

    listeFichiers = {}
    for rep in ("Dlg", "Ctrl", "Ol", "Utils"):
        if rep not in listeFichiers:
            listeFichiers[rep] = []
        listeFichiers[rep] = os.listdir(chemin_noethys + "/" + rep)

    for rep, liste in listeFichiers.items() :
        for nomFichier in liste :
            chemin_fichier = chemin_noethys + "/" + rep + "/" + nomFichier
    
            if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False and nomFichier not in ("CreateurMAJ.py", "CreateurANNONCES.py") :
                # Ouverture du fichier
                fichier = codecs.open(chemin_fichier, encoding='utf8', mode='r')
                texte = "\n".join(fichier.readlines())
                fichier.close()

                # Analyse du fichier
                listeChaines = re.findall(exp, texte)
                for chaine in listeChaines :
                    chaine = chaine [4:-2]

                    valide = False
                    for caract in "abceghijklmopqrtvwxyz" :
                        if caract in chaine.lower() :
                            valide = True
                    if len(chaine) < 2 :
                        valide = False
                    if "Images/" in chaine :
                        valide = False

                    if valide == True :
                        if (chaine in dictTextes) == False :
                            dictTextes[chaine] = []
                        dictTextes[chaine].append(nomFichier)

    # Génération du fichier
    nomFichier = Chemins.GetStaticPath("Databases/Textes.dat")
    UTILS_Json.Ecrire(nomFichier, data=dictTextes)
    print("Generation du fichier de textes terminee.")

def ConvertJsonEnTexte():
    """ Convertit le fichier Textes.dat en fichier Textes.txt """
    # Lecture du fichier dat
    data = UTILS_Json.Lire(Chemins.GetStaticPath("Databases/Textes.dat"), conversion_auto=True)
    listeTextes = []
    for texte, listeFichiers in data.items():
        listeTextes.append(texte)
    listeTextes.sort()
    
    # Enregistrement du fichier texte
    fichier = open(UTILS_Fichiers.GetRepTemp(fichier="Textes.txt"), "w")
    for texte in listeTextes :
        fichier.write(texte + "\n")
    fichier.close()
    print("Fini !")

def FusionneFichiers(code="en_GB"):
    # Lecture du fichier xlang
    data = UTILS_Json.Lire(UTILS_Fichiers.GetRepLang(u"%s.xlang" % code), conversion_auto=True)
    dictDonnees = {}
    for texte, traduction in data.items() :
        if texte != "###INFOS###" :
            dictDonnees[texte] = traduction

    # Lecture du fichier lang
    data = UTILS_Json.Lire("Lang/%s.lang" % code)
    for texte, traduction in dictDonnees.items():
        data[texte] = traduction
    UTILS_Json.Ecrire("Lang/%s.lang" % code, data=data)
    print("Fusion de %d traductions terminee !" % len(dictDonnees))




if __name__ == "__main__":
    # ConvertJsonEnTexte()
    # FusionneFichiers("en_GB")

    GenerationFichierTextes()
    data = UTILS_Json.Lire(Chemins.GetStaticPath("Databases/Textes.dat"), conversion_auto=True)
    print(data)
    print(len(data))
