#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import datetime
import GestionDB
from Utils import UTILS_Identification

CATEGORIES = {
    1 : _(u"Ouverture d'un fichier"),
    2 : _(u"Fermeture d'un fichier"),
    3 : _(u"Nouvel utilisateur"),
    4 : _(u"Cr�ation d'une famille"),
    5 : _(u"Suppression d'une famille"),
    6 : _(u"Saisie d'un r�glement"),
    7 : _(u"Modification d'un r�glement"),
    8 : _(u"Suppression d'un r�glement"),
    9 : _(u"Saisie de consommations"),
    10 : _(u"Suppression de consommations"),
    11 : _(u"Cr�ation d'un individu"),
    12 : _(u"Suppression d'un individu"),
    13 : _(u"Rattachement d'un individu"),
    14 : _(u"D�tachement d'un individu"),
    15 : _(u"Saisie d'une pi�ce"),
    16 : _(u"Modification d'une pi�ce"),
    17 : _(u"Suppression d'une pi�ce"),
    18 : _(u"Inscription � une activit�"),
    19 : _(u"D�sinscription d'une activit�"),
    20 : _(u"Modification de l'inscription � une activit�"),
    21 : _(u"Saisie d'une cotisation"),
    22 : _(u"Modification d'une cotisation"),
    23 : _(u"Suppression d'une cotisation"),
    24 : _(u"Saisie d'un message"),
    25 : _(u"Modification d'un message"),
    26 : _(u"Suppression d'un message"),
    27 : _(u"Edition d'une attestation de pr�sence"),
    28 : _(u"Edition d'un re�u de r�glement"),
    29 : _(u"Modification de consommations"),
    30 : _(u"Inscription scolaire"),
    31 : _(u"Modification d'une inscription scolaire"),
    32 : _(u"Suppression d'une inscription scolaire"),
    33 : _(u"Envoi d'un Email"),
    34 : _(u"Edition d'une confirmation d'inscription"),
    35 : _(u"G�n�ration d'un fichier XML SEPA"),
    36 : _(u"Edition d'un devis"),
    37 : _(u"Saisie d'une location"),
    38 : _(u"Modification d'une location"),
    39 : _(u"Suppression d'une location"),

}

DICT_COULEURS = {
    (166, 245, 156) : (4, 5),
    (236, 245, 156) : (6, 7, 8),
    (245, 208, 156) : (9, 10, 29),
    (245, 164, 156) : (11, 12, 13, 14),
    (156, 245, 160) : (15, 16, 17),
    (156, 245, 223) : (18, 19, 20),
    (156, 193, 245) : (21, 22, 23),
    (170, 156, 245) : (24, 25, 26),
    (231, 156, 245) : (27, 28),
    }


def InsertActions(listeActions=[], DB=None):
    """ dictAction = { IDutilisateur : None, IDfamille : None, IDindividu : None, IDcategorie : None, action : u"", IDdonnee: None } """
    date = str(datetime.date.today())
    heure = "%02d:%02d:%02d" % (datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
    
    # Traitement des actions
    listeAjouts = []
    for dictAction in listeActions :
        IDutilisateur = dictAction.get("IDutilisateur", UTILS_Identification.GetIDutilisateur())
        IDfamille = dictAction.get("IDfamille", None)
        IDindividu = dictAction.get("IDindividu", None)
        IDcategorie = dictAction.get("IDcategorie", None)
        action = dictAction.get("action", u"")
        if len(action) >= 500 :
            action = action[:495] + "..." # Texte limit� � 499 caract�res
        IDdonnee = dictAction.get("IDdonnee", None)
        listeAjouts.append((date, heure, IDutilisateur, IDfamille, IDindividu, IDcategorie, action, IDdonnee))
    
    # Enregistrement dans la base
    if len(listeAjouts) > 0 :
        req = u"INSERT INTO historique (date, heure, IDutilisateur, IDfamille, IDindividu, IDcategorie, action, IDdonnee) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        if DB == None :
            DB = GestionDB.DB()
            try:
                DB.Executermany(req, listeAjouts, commit=False)
            except:
                req = u"INSERT INTO historique (date, heure, IDutilisateur, IDfamille, IDindividu, IDcategorie, action) VALUES (?, ?, ?, ?, ?, ?, ?)"
                DB.Executermany(req, listeAjouts[:-1], commit=False)
            DB.Commit()
            DB.Close()
        else :
            DB.Executermany(req, listeAjouts, commit=False)
            DB.Commit()
