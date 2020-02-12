#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
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
    4 : _(u"Création d'une famille"),
    5 : _(u"Suppression d'une famille"),
    6 : _(u"Saisie d'un règlement"),
    7 : _(u"Modification d'un règlement"),
    8 : _(u"Suppression d'un règlement"),
    9 : _(u"Saisie de consommations"),
    10 : _(u"Suppression de consommations"),
    11 : _(u"Création d'un individu"),
    12 : _(u"Suppression d'un individu"),
    13 : _(u"Rattachement d'un individu"),
    14 : _(u"Détachement d'un individu"),
    15 : _(u"Saisie d'une pièce"),
    16 : _(u"Modification d'une pièce"),
    17 : _(u"Suppression d'une pièce"),
    18 : _(u"Inscription à une activité"),
    19 : _(u"Désinscription d'une activité"),
    20 : _(u"Modification de l'inscription à une activité"),
    21 : _(u"Saisie d'une cotisation"),
    22 : _(u"Modification d'une cotisation"),
    23 : _(u"Suppression d'une cotisation"),
    24 : _(u"Saisie d'un message"),
    25 : _(u"Modification d'un message"),
    26 : _(u"Suppression d'un message"),
    27 : _(u"Edition d'une attestation de présence"),
    28 : _(u"Edition d'un reçu de règlement"),
    29 : _(u"Modification de consommations"),
    30 : _(u"Inscription scolaire"),
    31 : _(u"Modification d'une inscription scolaire"),
    32 : _(u"Suppression d'une inscription scolaire"),
    33 : _(u"Envoi d'un Email"),
    34 : _(u"Edition d'une confirmation d'inscription"),
    35 : _(u"Génération d'un fichier XML SEPA"),
    36 : _(u"Edition d'un devis"),
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
    """ dictAction = { IDutilisateur : None, IDfamille : None, IDindividu : None, IDcategorie : None, action : u"" } """
    date = str(datetime.date.today())
    heure = "%02d:%02d:%02d" % (datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
    
    # Traitement des actions
    listeAjouts = []
    for dictAction in listeActions :
        if "IDutilisateur" in dictAction : 
            IDutilisateur = dictAction["IDutilisateur"]
        else : 
            IDutilisateur = UTILS_Identification.GetIDutilisateur()
        if "IDfamille" in dictAction : 
            IDfamille = dictAction["IDfamille"]
        else : 
            IDfamille = None
        if "IDindividu" in dictAction : 
            IDindividu = dictAction["IDindividu"]
        else : 
            IDindividu = None
        if "IDcategorie" in dictAction : 
            IDcategorie = dictAction["IDcategorie"]
        else : 
            IDcategorie = None
        if "action" in dictAction : 
            action = dictAction["action"]
        else : 
            action = u""
        if len(action) >= 500 :
            action = action[:495] + "..." # Texte limité à 499 caractères
        
        listeAjouts.append((date, heure, IDutilisateur, IDfamille, IDindividu, IDcategorie, action))
    
    # Enregistrement dans la base
    if len(listeAjouts) > 0 :
        req = u"INSERT INTO historique (date, heure, IDutilisateur, IDfamille, IDindividu, IDcategorie, action) VALUES (?, ?, ?, ?, ?, ?, ?)"
        if DB == None :
            DB = GestionDB.DB()
            DB.Executermany(req, listeAjouts, commit=False)
            DB.Commit()
            DB.Close()
        else :
            DB.Executermany(req, listeAjouts, commit=False)








            
            
##if __name__ == '__main__':
##    Start()