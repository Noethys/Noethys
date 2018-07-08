#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from GestionDB import DB
import datetime


def annuler(prestation_id, db=None):
    """
    Annuler une prestation en cr�ant une prestation d annulation avec un montant oppos�.

    :param prestation_id:   identifiant de prestation
    :param db:              connexion � la base de donn�es, si aucune connexion n'est pass�e, une nouvelle connexion
    sera cr��e (et cl�tur�e)
    :return:                la prestation d'annulation, en tant que liste
    """
    connexion = DB() if db is None else db
    req = """
    SELECT IDcompte_payeur, date, categorie, label, montant, IDfamille, IDindividu
    FROM prestations WHERE IDprestation = %d
    """ % prestation_id
    connexion.ExecuterReq(req)
    prestation_donnees = connexion.ResultatReq()
    if not prestation_donnees:
        # si pas de prestation, ne rien faire
        return None
    compte_payeur_id, date, categorie, label, montant, famille_id, individu_id = prestation_donnees[0]
    liste_donnees = [
        ("IDcompte_payeur", compte_payeur_id),
        ("date", date),
        ("categorie", categorie),
        ("label", label),
        ("montant_initial", -montant),
        ("montant", -montant),
        ("IDfamille", famille_id),
        ("IDindividu", individu_id),
        ("date_valeur", str(datetime.date.today())),
    ]
    connexion.ReqInsert("prestations", liste_donnees)
    if db is None:
        connexion.Close()
    return liste_donnees
