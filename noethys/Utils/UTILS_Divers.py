#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import copy

def DictionnaireImbrique(dictionnaire={}, cles=[], valeur=None):
    """ Création de dictionnaires imbriqués """
    if len(cles) == 0 :
        return dictionnaire
    
    if (cles[0] in dictionnaire) == False :
        dictionnaire[cles[0]] = {}
    if len(cles) == 1 : 
        if dictionnaire[cles[0]] == {} : dictionnaire[cles[0]] = valeur
        return dictionnaire

    if (cles[1] in dictionnaire[cles[0]]) == False :
        dictionnaire[cles[0]][cles[1]] = {}
    if len(cles) == 2 : 
        if dictionnaire[cles[0]][cles[1]] == {} : dictionnaire[cles[0]][cles[1]] = valeur
        return dictionnaire

    if (cles[2] in dictionnaire[cles[0]][cles[1]]) == False :
        dictionnaire[cles[0]][cles[1]][cles[2]] = {}
    if len(cles) == 3 : 
        if dictionnaire[cles[0]][cles[1]][cles[2]] == {} : dictionnaire[cles[0]][cles[1]][cles[2]] = valeur
        return dictionnaire

    if (cles[3] in dictionnaire[cles[0]][cles[1]][cles[2]]) == False :
        dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]] = {}
    if len(cles) == 4 : 
        if dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]] == {} : dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]] = valeur
        return dictionnaire

    if (cles[4] in dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]]) == False :
        dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]][cles[4]] = {}
    if len(cles) == 5 : 
        if dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]][cles[4]] == {} : dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]][cles[4]] = valeur
        return dictionnaire

    if (cles[5] in dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]][cles[4]]) == False :
        dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]][cles[4]][cles[5]] = {}
    if len(cles) == 6 : 
        if dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]][cles[4]][cles[5]] == {} : dictionnaire[cles[0]][cles[1]][cles[2]][cles[3]][cles[4]][cles[5]] = valeur
        return dictionnaire

    return None


def ConvertChaineEnListe(chaine=""):
    if chaine == "" or chaine == None :
        return []
    liste2 = []
    for valeur in chaine.split(";") :
        liste2.append(int(valeur))
    return liste2


def ConvertListeEnChaine(liste=[]):
    if len(liste) == 0 :
        return None
    liste2 = []
    for num in liste :
        liste2.append(str(num))
    return ";".join(liste2)

def ConvertCouleurWXpourPDF(couleurwx=(0, 0, 0)):
    return (couleurwx[0]/255.0, couleurwx[1]/255.0, couleurwx[2]/255.0)

def ConvertCouleurPDFpourWX(couleurpdf=(0, 0, 0)):
    return (couleurpdf[0]*255.0, couleurpdf[1]*255.0, couleurpdf[2]*255.0)





if __name__ == "__main__":
    d = DictionnaireImbrique({}, [10, 20, 30, 40, 401], 888);print(d)
    d[10][20][30][40][401] +=1;print(d)
    d = DictionnaireImbrique(d, [10, 20, 30, 40, 401], 888);print(d)