#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


""" Liste des civilités d'individus (pour la fiche individu)"""

LISTE_CIVILITES = (
    (u"ADULTE", 
        (
        (1, u"Monsieur", u"M.", "Homme.png", "M"),
        (2, u"Mademoiselle", u"Melle", "Femme.png", "F"),
        (3, u"Madame", u"Mme", "Femme.png", "F"),
        )),
    (u"ENFANT", 
        (
        (4, u"Garçon", None, "Garcon.png", "M"),
        (5, u"Fille", None, "Fille.png", "F"),
        )),
    (u"AUTRE", 
        (
        (6, u"Collectivité", None, "Organisme.png", None),
        (7, u"Association", None,  "Organisme.png", None),
        (8, u"Organisme", None, "Organisme.png", None),
        (9, u"Entreprise", None, "Organisme.png", None),
        )),
    ) # Rubrique > (ID, CiviliteLong, CiviliteAbrege, nomImage, Masculin/Féminin)


def GetDictCivilites():
    dictCivilites = {}
    for categorie, civilites in LISTE_CIVILITES :
        for IDcivilite, civiliteLong, civiliteAbrege, nomImage, sexe in civilites :
            dictCivilites[IDcivilite] = {"categorie" : categorie, "civiliteLong" : civiliteLong, "civiliteAbrege" : civiliteAbrege, "nomImage" : nomImage, "sexe" : sexe}
    return dictCivilites