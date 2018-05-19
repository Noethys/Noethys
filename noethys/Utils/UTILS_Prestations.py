#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from GestionDB import DB
import datetime


def annuler(prestation_id, db=None):
    """
    Annuler une prestation en créant une prestation d annulation avec un montant opposé.

    :param prestation_id:   identifiant de prestation
    :param db: GestionDB    connexion à la base de données, si aucune connexion n'est passée, une nouvelle connexion
    sera créée (et clôturée)
    :return:                la prestation d'annulation, en tant que liste
    """
    connexion = db or DB()
    req = """
    SELECT IDcompte_payeur, date, categorie, label, montant, IDfamille, IDindividu, reglement_frais
    FROM prestations WHERE IDprestation = %d
    """ % prestation_id
    connexion.ExecuterReq(req)
    prestation_donnees = connexion.ResultatReq()
    if not prestation_donnees:
        # si pas de prestation, ne rien faire
        return None
    compte_payeur_id, date, categorie, label, montant, famille_id, individu_id, reglement_frais = prestation_donnees[0]
    montant = -montant if montant else None
    liste_donnees = [
        ("IDcompte_payeur", compte_payeur_id),
        ("date", date),
        ("categorie", categorie),
        ("label", label),
        ("montant_initial", montant),
        ("montant", montant),
        ("IDfamille", famille_id),
        ("IDindividu", individu_id),
        ("date_valeur", str(datetime.date.today())),
    ]
    connexion.ReqInsert("prestations", liste_donnees)
    # Si l'ancienne prestation correspond aux frais, modifier la
    if reglement_frais:
        req = """
        UPDATE prestations
        SET reglement_frais = NULL
        WHERE IDprestation = %d
        """ % prestation_id
    connexion.ExecuterReq(req)
    connexion.Commit()
    if db is None:
        connexion.Close()
    return liste_donnees
