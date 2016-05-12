#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import re


def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte

def ConvertStrToListe(texte=None, siVide=[], separateur=";", typeDonnee="entier"):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None or texte == "" :
        return siVide
    listeResultats = []
    temp = texte.split(separateur)
    for ID in temp :
        if typeDonnee == "entier" :
            ID = int(ID)
        listeResultats.append(ID)
    return listeResultats


def ConvertListeToStr(liste=[], separateur=";"):
    """ Convertit une liste en texte """
    if liste == None : liste = []
    return separateur.join([str(x) for x in liste])

def Incrementer(s):
    """ look for the last sequence of number(s) in a string and increment """
    lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
    m = lastNum.search(s)
    if m:
        next = str(int(m.group(1))+1)
        start, end = m.span(1)
        s = s[:max(end-len(next), start)] + next + s[end:]
    return s

def T(_):
    print _, ">", Incrementer(_)
if __name__=='__main__':
    T("10dsc_0010.jpg")
    T("10dsc_0099.jpg")
    T("dsc_9.jpg")
    T("0000001.exe")
    T("9999999.exe")
    T("ref-04851")
    T("0000099")
    T("E9ABC")
