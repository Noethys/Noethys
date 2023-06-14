#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import re
try:
    from Utils.UTILS_Traduction import _
except:
    pass


def Parser_voie(texte=""):
    if not texte:
        return {}
    texte = texte.replace(",", "")
    types_voies = [u"rue", u"avenue", u"boulevard", u"bd", u"bvd", u"lieu dit", u"lieu-dit", u"route", u"clos", u"ldt", u"square", u"impasse", u"cours", u"esplanade", u"allée", u"résidence", u"chemin", u"place", u"cité", u"hameau", u"coteau"]
    liste_types_voies = []
    for type_voie in types_voies:
        liste_types_voies.extend([u"%s des" % type_voie, u"%s de la" % type_voie, u"%s de" % type_voie, u"%s du" % type_voie, type_voie])
    regex = re.compile(r"(?P<numero>.+)(?P<type>" + "|".join(liste_types_voies) + r")(?P<nom>.*)", re.S)
    resultat = regex.match(texte.lower())
    if not resultat:
        regex2 = re.compile(r"(?P<numero>[0-9]+)(?P<nom>.*)", re.S)
        resultat = regex2.match(texte.lower())
    if not resultat:
        return {"nom": texte.lower().capitalize()}
    dict_resultats = resultat.groupdict()
    dict_resultats["numero"] = dict_resultats.get("numero", "").strip().capitalize()
    dict_resultats["nom"] = dict_resultats.get("nom", "").strip().capitalize()
    dict_resultats["type"] = dict_resultats.get("type", "").strip().replace(" des", "").replace(" de la", "").replace(" du", "").replace(" de", "").capitalize()
    return dict_resultats


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

def ConvertListeToPhrase(liste):
    if len(liste) == 0:
        return _(u"")
    elif len(liste) == 1:
        return liste[0]
    elif len(liste) == 2:
        return _(u" et ").join(liste)
    else:
        return _(u"%s et %s") % (u", ".join(liste[:-1]), liste[-1])

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
    print(_, ">", Incrementer(_))


if __name__=='__main__':
    print(Parser_voie("21 rue des cormorans"))
