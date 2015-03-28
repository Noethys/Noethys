#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import datetime
import GestionDB
import UTILS_Identification

CATEGORIES = {
    1 : u"Ouverture d'un fichier",
    2 : u"Fermeture d'un fichier",
    3 : u"Nouvel utilisateur",
    4 : u"Création d'une famille",
    5 : u"Suppression d'une famille",
    6 : u"Saisie d'un règlement",
    7 : u"Modification d'un règlement",
    8 : u"Suppression d'un règlement",
    9 : u"Saisie de consommations",
    10 : u"Suppression de consommations",
    11 : u"Création d'un individu",
    12 : u"Suppression d'un individu",
    13 : u"Rattachement d'un individu",
    14 : u"Détachement d'un individu",
    15 : u"Saisie d'une pièce",
    16 : u"Modification d'une pièce",
    17 : u"Suppression d'une pièce",
    18 : u"Inscription à une activité",
    19 : u"Désinscription d'une activité",
    20 : u"Modification de l'inscription à une activité",
    21 : u"Saisie d'une cotisation",
    22 : u"Modification d'une cotisation",
    23 : u"Suppression d'une cotisation",
    24 : u"Saisie d'un message",
    25 : u"Modification d'un message",
    26 : u"Suppression d'un message",
    27 : u"Edition d'une attestation de présence",
    28 : u"Edition d'un reçu de règlement",
    29 : u"Modification de consommations",
    30 : u"Inscription scolaire",
    31 : u"Modification d'une inscription scolaire",
    32 : u"Suppression d'une inscription scolaire",
    33 : u"Envoi d'un Email",
    34 : u"Edition d'une confirmation d'inscription",
    35 : u"Génération d'un fichier XML SEPA",
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


def InsertActions(listeActions=[]):
    """ dictAction = { IDutilisateur : None, IDfamille : None, IDindividu : None, IDcategorie : None, action : u"" } """
    date = str(datetime.date.today())
    heure = "%02d:%02d:%02d" % (datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
    
    # Traitement des actions
    listeAjouts = []
    for dictAction in listeActions :
        if dictAction.has_key("IDutilisateur") : 
            IDutilisateur = dictAction["IDutilisateur"]
        else : 
            IDutilisateur = UTILS_Identification.GetIDutilisateur()
        if dictAction.has_key("IDfamille") : 
            IDfamille = dictAction["IDfamille"]
        else : 
            IDfamille = None
        if dictAction.has_key("IDindividu") : 
            IDindividu = dictAction["IDindividu"]
        else : 
            IDindividu = None
        if dictAction.has_key("IDcategorie") : 
            IDcategorie = dictAction["IDcategorie"]
        else : 
            IDcategorie = None
        if dictAction.has_key("action") : 
            action = dictAction["action"]
        else : 
            action = u""
        if len(action) >= 500 :
            action = action[:495] + "..." # Texte limité à 499 caractères
        
        listeAjouts.append((date, heure, IDutilisateur, IDfamille, IDindividu, IDcategorie, action))
    
    # Enregistrement dans la base
    if len(listeAjouts) > 0 :
        DB = GestionDB.DB()
        DB.Executermany(u"INSERT INTO historique (date, heure, IDutilisateur, IDfamille, IDindividu, IDcategorie, action) VALUES (?, ?, ?, ?, ?, ?, ?)", listeAjouts, commit=False)
        DB.Commit()
        DB.Close()









            
            
##if __name__ == '__main__':
##    Start()