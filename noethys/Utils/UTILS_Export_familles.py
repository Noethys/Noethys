#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _
from xml.dom.minidom import Document
import GestionDB
from Utils import UTILS_Infos_individus
from Utils import UTILS_Dates
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
import six


class Export():
    def __init__(self, IDfamille=None):
        """ si IDfamille == None : Toutes les familles sont sélectionnées"""
        self.IDfamille = IDfamille

    def GetDoc(self):
        # Importation des données de la DB
        DB = GestionDB.DB()

        if self.IDfamille == None :
            conditions = ""
            req = """SELECT IDfamille, date_creation FROM familles;"""
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            liste_IDfamille = []
            for IDfamille, date_creation in listeDonnees :
                liste_IDfamille.append(IDfamille)
        else :
            conditions = "WHERE IDfamille=%d" % self.IDfamille
            liste_IDfamille = [self.IDfamille,]

        # Importation des pièces fournies
        req = """SELECT pieces.IDpiece, pieces.date_debut, pieces.date_fin,
        types_pieces.public, types_pieces.nom, 
        individus.IDindividu, pieces.IDfamille, individus.prenom
        FROM pieces 
        LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        LEFT JOIN individus ON individus.IDindividu = pieces.IDindividu
        ORDER BY date_debut;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictPieces = {"familles" : {}, "individus" : {}}
        for IDpiece, date_debut, date_fin, public, nom_piece, IDindividu, IDfamille, prenom in listeDonnees :
            dictPiece = {"IDpiece" : IDpiece, "nom_piece" : nom_piece,
                         "date_debut" : UTILS_Dates.DateEngEnDateDD(date_debut),
                         "date_fin": UTILS_Dates.DateEngEnDateDD(date_fin)}

            if public == "famille" :
                if (IDfamille in dictPieces["familles"]) == False :
                    dictPieces["familles"][IDfamille] = []
                dictPieces["familles"][IDfamille].append(dictPiece)
            if public == "individu" :
                if (IDindividu in dictPieces["individus"]) == False :
                    dictPieces["individus"][IDindividu] = []
                dictPieces["individus"][IDindividu].append(dictPiece)

        # Importation des cotisations
        champs_cotisations = [
            ("IDcotisation", "cotisations.IDcotisation"),
            ("IDfamille", "cotisations.IDfamille"),
            ("IDindividu", "cotisations.IDindividu"),
            ("date_saisie", "cotisations.date_saisie"),
            ("date_creation_carte", "cotisations.date_creation_carte"),
            ("numero", "cotisations.numero"),
            ("date_debut", "cotisations.date_debut"),
            ("date_fin", "cotisations.date_fin"),
            ("observations", "cotisations.observations"),
            ("activites", "cotisations.activites"),
            ("type_cotisation", "types_cotisations.nom"),
            ("type", "types_cotisations.type"),
            ("nom_unite_cotisation", "unites_cotisations.nom"),
            ]
        req = """
        SELECT %s
        FROM cotisations 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN unites_cotisations ON unites_cotisations.IDunite_cotisation = cotisations.IDunite_cotisation
        ORDER BY cotisations.date_debut
        ;""" % ", ".join([champ for nom, champ in champs_cotisations])
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictCotisations = {"familles" : {}, "individus" : {}}
        for donnees in listeDonnees :
            dictCotisation = {}
            for index in range(0, len(champs_cotisations)):
                dictCotisation[champs_cotisations[index][0]] = donnees[index]

            if dictCotisation["type"] == "famille" :
                IDfamille = dictCotisation["IDfamille"]
                if (IDfamille in dictCotisations["familles"]) == False :
                    dictCotisations["familles"][IDfamille] = []
                dictCotisations["familles"][IDfamille].append(dictCotisation)
            if dictCotisation["type"] == "individu" :
                IDindividu = dictCotisation["IDindividu"]
                if (IDindividu in dictCotisations["individus"]) == False :
                    dictCotisations["individus"][IDindividu] = []
                dictCotisations["individus"][IDindividu].append(dictCotisation)

        # Importation des prestations
        champs_prestations = [
            ("IDprestation", "prestations.IDprestation"),
            ("date", "prestations.date"),
            ("label", "prestations.label"),
            ("montant", "prestations.montant"),
            ("numero_facture", "factures.numero"),
            ("activite", "activites.nom"),
            ("prenom", "individus.prenom"),
            ("IDfamille", "prestations.IDfamille"),
            ("IDindividu", "prestations.IDindividu"),
            ]

        req = """
        SELECT %s
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN factures ON prestations.IDfacture = factures.IDfacture
        %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % (", ".join([champ for nom, champ in champs_prestations]), conditions)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictPrestations = {}
        for donnees in listeDonnees :
            dictPrestation = {}
            for index in range(0, len(champs_prestations)):
                dictPrestation[champs_prestations[index][0]] = donnees[index]

            if dictPrestation["numero_facture"] == None : dictPrestation["numero_facture"] = ""
            if dictPrestation["prenom"] == None : dictPrestation["prenom"] = ""

            IDfamille = dictPrestation["IDfamille"]
            if (IDfamille in dictPrestations) == False :
                dictPrestations[IDfamille] = []
            dictPrestations[IDfamille].append(dictPrestation)

        # Importation des consommations
        req = """
        SELECT IDconso, date, activites.nom, consommations.etat, 
        unites.nom, consommations.IDindividu, comptes_payeurs.IDfamille
        FROM consommations
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        %s
        GROUP BY consommations.IDconso
        ORDER BY date
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictConsommations = {}
        for IDconso, date, nomActivite, etat, nomUnite, IDindividu, IDfamille in listeDonnees :
            dictConso = {
                "IDconso" : IDconso, "date" : date, "nomActivite" : nomActivite,
                "etat" : etat, "nomUnite" : nomUnite,
                }
            if (IDfamille in dictConsommations) == False :
                dictConsommations[IDfamille] = {}
            if (IDindividu in dictConsommations[IDfamille]) == False :
                dictConsommations[IDfamille][IDindividu] = []
            dictConsommations[IDfamille][IDindividu].append(dictConso)

        # Importation des factures

        # Récupération des totaux des prestations pour chaque facture
        req = """
        SELECT prestations.IDfacture, SUM(prestations.montant)
        FROM prestations
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        GROUP BY prestations.IDfacture
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictPrestationsFactures = {}
        for IDfacture, totalPrestations in listeDonnees :
            if IDfacture != None :
                dictPrestationsFactures[IDfacture] = totalPrestations

        # Récupération des factures
        req = """
        SELECT factures.IDfacture, factures.numero, factures.date_edition, factures.date_debut, 
        factures.date_fin, factures.total, factures.regle, factures.solde, comptes_payeurs.IDfamille
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        %s
        ORDER BY factures.date_edition
        ;""" % conditions
        DB.ExecuterReq(req)
        listeFactures = DB.ResultatReq()

        # Récupération de la ventilation
        req = """
        SELECT prestations.IDfacture, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = prestations.IDcompte_payeur
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        %s
        GROUP BY prestations.IDfacture
        ;""" % conditions.replace("IDfamille", "comptes_payeurs.IDfamille")
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()
        dictVentilationFactures = {}
        for IDfacture, montantVentilation in listeVentilation :
            if IDfacture != None :
                dictVentilationFactures[IDfacture] = montantVentilation

        dictFactures = {}
        for IDfacture, numero, date_edition, date_debut, date_fin, total, regle, solde, IDfamille in listeFactures :
            if numero == None : numero = 0
            total = FloatToDecimal(total)
            if IDfacture in dictVentilationFactures :
                totalVentilation = FloatToDecimal(dictVentilationFactures[IDfacture])
            else :
                totalVentilation = FloatToDecimal(0.0)
            if IDfacture in dictPrestationsFactures :
                totalPrestations = FloatToDecimal(dictPrestationsFactures[IDfacture])
            else :
                totalPrestations = FloatToDecimal(0.0)
            solde_actuel = totalPrestations - totalVentilation

            dictFacture = {
                "IDfacture" : IDfacture, "numero" : numero, "date_edition" : date_edition, "date_debut" : date_debut,
                "date_fin": date_fin, "montant" : float(totalPrestations), "montant_regle" : float(totalVentilation),
                "montant_solde" : float(solde_actuel),
                }

            if (IDfamille in dictFactures) == False :
                dictFactures[IDfamille] = []
            dictFactures[IDfamille].append(dictFacture)

        # Importation des règlements
        req = """SELECT
        reglements.IDreglement, comptes_payeurs.IDfamille,
        reglements.date, modes_reglements.label, emetteurs.nom, 
        reglements.numero_piece, reglements.montant, payeurs.nom, 
        reglements.observations, numero_quittancier, date_differe, 
        date_saisie, depots.date
        FROM reglements
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN emetteurs ON reglements.IDemetteur=emetteurs.IDemetteur
        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        %s
        GROUP BY reglements.IDreglement
        ORDER BY date_saisie
        ;""" % conditions.replace("IDfamille", "comptes_payeurs.IDfamille")
        DB.ExecuterReq(req)
        listeReglements = DB.ResultatReq()
        dictReglements = {}
        for IDreglement, IDfamille, date, mode, emetteur, numero, montant, payeur, observations, numero_quittancier, date_differe, date_saisie, date_encaissement in listeReglements :
            if numero == None : numero = ""
            if emetteur == None : emetteur = ""
            if observations == None: observations = ""
            if numero_quittancier == None: numero_quittancier = ""
            dictReglement = {
                "date" : date, "mode" : mode, "emetteur" : emetteur, "numero" : numero, "montant" : montant,
                "payeur": payeur, "observations" : observations, "numero_quittancier" : numero_quittancier,
                "date_differe" : date_differe, "date_saisie" : date_saisie, "date_encaissement": date_encaissement,
            }
            if (IDfamille in dictReglements) == False :
                dictReglements[IDfamille] = []
            dictReglements[IDfamille].append(dictReglement)


        DB.Close()

        # Récupération des infos individus
        infos = UTILS_Infos_individus.Informations()

        # Génération du XML
        doc = Document()

        # Racine Familles
        node_racine = doc.createElement("familles")
        doc.appendChild(node_racine)

        for IDfamille in liste_IDfamille :

            # Famille : Infos générales
            node_famille = doc.createElement("famille")
            node_famille.setAttribute("id", str(IDfamille))
            node_racine.appendChild(node_famille)

            for key, valeur in infos.dictFamilles[IDfamille].items():
                if key.startswith("FAMILLE_"):
                    node = doc.createElement(key.replace("FAMILLE_", "").lower())
                    node.setAttribute("valeur", unicode(valeur))
                    node_famille.appendChild(node)

            # Famille : Quotients
            if "qf" in infos.dictFamilles[IDfamille]:
                node_qf = doc.createElement(u"quotients_familiaux")
                node_famille.appendChild(node_qf)

                for dictQF in infos.dictFamilles[IDfamille]["qf"]:
                    node = doc.createElement(u"quotient")
                    node.setAttribute("date_debut", dictQF["date_debut"])
                    node.setAttribute("date_fin", dictQF["date_fin"])
                    node.setAttribute("quotient", str(dictQF["quotient"]))
                    node.setAttribute("observations", dictQF["observations"])
                    node_qf.appendChild(node)

            # Famille : Messages
            if "messages" in infos.dictFamilles[IDfamille]:
                node_messages = doc.createElement(u"messages")
                node_famille.appendChild(node_messages)

                for dictMessage in infos.dictFamilles[IDfamille]["messages"]["liste"]:
                    node = doc.createElement(u"message")
                    node.setAttribute("categorie_nom", dictMessage["categorie_nom"])
                    node.setAttribute("date_saisie", dictMessage["date_saisie"])
                    node.setAttribute("date_parution", dictMessage["date_parution"])
                    node.setAttribute("nom", dictMessage["nom"])
                    node.setAttribute("texte", dictMessage["texte"])
                    node_messages.appendChild(node)

            # Famille : Questionnaires
            if "questionnaires" in infos.dictFamilles[IDfamille]:
                node_questionnaires = doc.createElement(u"questionnaires")
                node_famille.appendChild(node_questionnaires)

                for dictQuestionnaire in infos.dictFamilles[IDfamille]["questionnaires"]:
                    node = doc.createElement(u"questionnaire")
                    node.setAttribute("question", dictQuestionnaire["label"])
                    node.setAttribute("reponse", unicode(dictQuestionnaire["reponse"]))
                    node_questionnaires.appendChild(node)

            # Famille : Pièces
            if IDfamille in dictPieces["familles"]:
                node_pieces = doc.createElement(u"pieces")
                node_famille.appendChild(node_pieces)

                for dictPiece in dictPieces["familles"][IDfamille]:
                    node = doc.createElement(u"piece")
                    node.setAttribute("nom_piece", dictPiece["nom_piece"])
                    node.setAttribute("date_debut", UTILS_Dates.DateDDEnFr(dictPiece["date_debut"]))
                    node.setAttribute("date_fin", UTILS_Dates.DateDDEnFr(dictPiece["date_fin"]))
                    node_pieces.appendChild(node)

            # Famille : Cotisations
            if IDfamille in dictCotisations["familles"]:
                node_cotisations = doc.createElement(u"cotisations")
                node_famille.appendChild(node_cotisations)

                for dictCotisation in dictCotisations["familles"][IDfamille]:
                    node = doc.createElement(u"cotisation")
                    node.setAttribute("date_saisie", UTILS_Dates.DateDDEnFr(dictCotisation["date_saisie"]))
                    node.setAttribute("date_creation_carte", UTILS_Dates.DateDDEnFr(dictCotisation["date_creation_carte"]))
                    node.setAttribute("date_debut", UTILS_Dates.DateDDEnFr(dictCotisation["date_debut"]))
                    node.setAttribute("date_fin", UTILS_Dates.DateDDEnFr(dictCotisation["date_fin"]))
                    node.setAttribute("numero", dictCotisation["numero"])
                    node.setAttribute("type_cotisation", dictCotisation["type_cotisation"])
                    node.setAttribute("nom_unite_cotisation", dictCotisation["nom_unite_cotisation"])
                    node.setAttribute("observations", dictCotisation["observations"])
                    node.setAttribute("activites", dictCotisation["activites"])
                    node_cotisations.appendChild(node)

            # Famille : Prestations
            if IDfamille in dictPrestations:
                node_prestations = doc.createElement(u"prestations")
                node_famille.appendChild(node_prestations)

                for dictPrestation in dictPrestations[IDfamille]:
                    node = doc.createElement(u"prestation")
                    node.setAttribute("date", UTILS_Dates.DateEngFr(dictPrestation["date"]))
                    node.setAttribute("label", dictPrestation["label"])
                    node.setAttribute("devise", SYMBOLE)
                    node.setAttribute("montant", u"%.2f" % dictPrestation["montant"])
                    node.setAttribute("numero_facture", str(dictPrestation["numero_facture"]))
                    node.setAttribute("activite", dictPrestation["activite"])
                    node.setAttribute("prenom", dictPrestation["prenom"])
                    node_prestations.appendChild(node)

                # Famille : Factures
                if IDfamille in dictFactures:
                    node_factures = doc.createElement(u"factures")
                    node_famille.appendChild(node_factures)

                    for dictFacture in dictFactures[IDfamille]:
                        node = doc.createElement(u"facture")
                        node.setAttribute("date_edition", UTILS_Dates.DateEngFr(dictFacture["date_edition"]))
                        node.setAttribute("date_debut", UTILS_Dates.DateEngFr(dictFacture["date_debut"]))
                        node.setAttribute("date_fin", UTILS_Dates.DateEngFr(dictFacture["date_fin"]))
                        node.setAttribute("numero_facture", str(dictFacture["numero"]))
                        node.setAttribute("devise", SYMBOLE)
                        node.setAttribute("montant", u"%.2f" % dictFacture["montant"])
                        node.setAttribute("montant_regle", u"%.2f" % dictFacture["montant_regle"])
                        node.setAttribute("montant_solde", u"%.2f" % dictFacture["montant_solde"])
                        node_factures.appendChild(node)

                # Famille : Règlements
                if IDfamille in dictReglements:
                    node_reglements = doc.createElement(u"reglements")
                    node_famille.appendChild(node_reglements)

                    for dictReglement in dictReglements[IDfamille]:
                        node = doc.createElement(u"reglement")
                        node.setAttribute("date", UTILS_Dates.DateEngFr(dictReglement["date"]))
                        node.setAttribute("date_differe", UTILS_Dates.DateEngFr(dictReglement["date_differe"]))
                        node.setAttribute("date_saisie", UTILS_Dates.DateEngFr(dictReglement["date_saisie"]))
                        node.setAttribute("date_encaissement", UTILS_Dates.DateEngFr(dictReglement["date_encaissement"]))
                        node.setAttribute("mode", dictReglement["mode"])
                        node.setAttribute("emetteur", dictReglement["emetteur"])
                        node.setAttribute("numero_piece", dictReglement["numero"])
                        node.setAttribute("devise", SYMBOLE)
                        node.setAttribute("montant", u"%.2f" % dictReglement["montant"])
                        node.setAttribute("payeur", dictReglement["payeur"])
                        node.setAttribute("observations", dictReglement["observations"])
                        node.setAttribute("numero_quittancier", dictReglement["numero_quittancier"])
                        node_reglements.appendChild(node)




            # Individus
            node_individus = doc.createElement(u"individus")
            node_famille.appendChild(node_individus)

            if IDfamille in infos.dictRattachements["familles"]:
                for dictRattachement in infos.dictRattachements["familles"][IDfamille]:
                    IDindividu = dictRattachement["IDindividu"]

                    node_individu = doc.createElement(u"individu")
                    node_individu.setAttribute("id", str(IDindividu))
                    node_individus.appendChild(node_individu)

                    # Individu : données générales
                    for key, champ in infos.GetListeChampsIndividus():
                        valeur = infos.dictIndividus[IDindividu][key]
                        if isinstance(valeur, (six.text_type, str)):
                            node = doc.createElement(key.replace("INDIVIDU_", "").lower())
                            node.setAttribute("valeur", six.text_type(valeur))
                            node_individu.appendChild(node)

                    # Individu : Messages
                    if "messages" in infos.dictIndividus[IDindividu]:
                        node_messages = doc.createElement(u"messages")
                        node_individu.appendChild(node_messages)

                        for dictMessage in infos.dictIndividus[IDindividu]["messages"]["liste"]:
                            node = doc.createElement(u"message")
                            node.setAttribute("categorie_nom", dictMessage["categorie_nom"])
                            node.setAttribute("date_saisie", dictMessage["date_saisie"])
                            node.setAttribute("date_parution", dictMessage["date_parution"])
                            node.setAttribute("nom", dictMessage["nom"])
                            node.setAttribute("texte", dictMessage["texte"])
                            node_messages.appendChild(node)

                    # Individu : Infos médicales
                    if "medical" in infos.dictIndividus[IDindividu]:
                        node_medicales = doc.createElement(u"infos_medicales")
                        node_individu.appendChild(node_medicales)

                        for dictMedicale in infos.dictIndividus[IDindividu]["medical"]["liste"]:
                            node = doc.createElement(u"info_medicale")
                            node.setAttribute("intitule", dictMedicale["intitule"])
                            node.setAttribute("description", dictMedicale["description"])
                            node.setAttribute("description_traitement", dictMedicale["description_traitement"])
                            node.setAttribute("date_debut_traitement", dictMedicale["date_debut_traitement"])
                            node.setAttribute("date_fin_traitement", dictMedicale["date_fin_traitement"])
                            node_medicales.appendChild(node)

                    # Individu : Inscriptions
                    if "inscriptions" in infos.dictIndividus[IDindividu]:
                        node_inscriptions = doc.createElement(u"inscriptions")
                        node_individu.appendChild(node_inscriptions)

                        for dictInscription in infos.dictIndividus[IDindividu]["inscriptions"]["liste"]:
                            node = doc.createElement(u"inscription")
                            node.setAttribute("activite", dictInscription["activite"])
                            node.setAttribute("groupe", dictInscription["groupe"])
                            node.setAttribute("categorie_tarif", dictInscription["categorie_tarif"])
                            node.setAttribute("parti", dictInscription["parti"])
                            node.setAttribute("date_inscription", dictInscription["date_inscription"])
                            node_inscriptions.appendChild(node)

                    # Individu : Questionnaires
                    if "questionnaires" in infos.dictIndividus[IDindividu]:
                        node_questionnaires = doc.createElement(u"questionnaires")
                        node_individu.appendChild(node_questionnaires)

                        for dictQuestionnaire in infos.dictIndividus[IDindividu]["questionnaires"]:
                            node = doc.createElement(u"questionnaire")
                            node.setAttribute("question", dictQuestionnaire["label"])
                            node.setAttribute("reponse", unicode(dictQuestionnaire["reponse"]))
                            node_questionnaires.appendChild(node)

                    # Individu : Scolarité
                    if "scolarite" in infos.dictIndividus[IDindividu]:
                        node_scolarite = doc.createElement(u"scolarite")
                        node_individu.appendChild(node_scolarite)

                        for dictScolarite in infos.dictIndividus[IDindividu]["scolarite"]["liste"]:
                            node = doc.createElement(u"etape")
                            node.setAttribute("date_debut", dictScolarite["date_debut"])
                            node.setAttribute("date_fin", dictScolarite["date_fin"])
                            node.setAttribute("ecole_nom", dictScolarite["ecole_nom"])
                            node.setAttribute("classe_nom", dictScolarite["classe_nom"])
                            node.setAttribute("niveau_nom", dictScolarite["niveau_nom"])
                            node.setAttribute("niveau_abrege", dictScolarite["niveau_abrege"])
                            node_scolarite.appendChild(node)

                    # Individu : Pièces
                    if IDindividu in dictPieces["individus"]:
                        node_pieces = doc.createElement(u"pieces")
                        node_individu.appendChild(node_pieces)

                        for dictPiece in dictPieces["individus"][IDindividu]:
                            node = doc.createElement(u"piece")
                            node.setAttribute("nom_piece", dictPiece["nom_piece"])
                            node.setAttribute("date_debut", UTILS_Dates.DateDDEnFr(dictPiece["date_debut"]))
                            node.setAttribute("date_fin", UTILS_Dates.DateDDEnFr(dictPiece["date_fin"]))
                            node_pieces.appendChild(node)

                    # Individu : Cotisations
                    if IDindividu in dictCotisations["individus"]:
                        node_cotisations = doc.createElement(u"cotisations")
                        node_individu.appendChild(node_cotisations)

                        for dictCotisation in dictCotisations["individus"][IDindividu]:
                            node = doc.createElement(u"cotisation")
                            node.setAttribute("date_saisie", UTILS_Dates.DateDDEnFr(dictCotisation["date_saisie"]))
                            node.setAttribute("date_creation_carte", UTILS_Dates.DateDDEnFr(dictCotisation["date_creation_carte"]))
                            node.setAttribute("date_debut", UTILS_Dates.DateDDEnFr(dictCotisation["date_debut"]))
                            node.setAttribute("date_fin", UTILS_Dates.DateDDEnFr(dictCotisation["date_fin"]))
                            node.setAttribute("numero", dictCotisation["numero"])
                            node.setAttribute("type_cotisation", dictCotisation["type_cotisation"])
                            node.setAttribute("nom_unite_cotisation", dictCotisation["nom_unite_cotisation"])
                            node.setAttribute("observations", dictCotisation["observations"])
                            node.setAttribute("activites", dictCotisation["activites"])
                            node_cotisations.appendChild(node)

                    # Individu : Consommations
                    if IDfamille in dictConsommations:
                        if IDindividu in dictConsommations[IDfamille]:
                            node_consommations = doc.createElement(u"consommations")
                            node_individu.appendChild(node_consommations)

                            for dictConso in dictConsommations[IDfamille][IDindividu]:
                                node = doc.createElement(u"consommation")
                                node.setAttribute("date", UTILS_Dates.DateEngFr(dictConso["date"]))
                                node.setAttribute("activite", dictConso["nomActivite"])
                                node.setAttribute("etat", dictConso["etat"])
                                node.setAttribute("unite", dictConso["nomUnite"])
                                node_consommations.appendChild(node)

        # Renvoie le doc
        return doc

    def GetPrettyXML(self):
        """ Renvoie le pretty XML """
        doc = self.GetDoc()
        pretty_xml = doc.toprettyxml(indent="  ", encoding="utf-8")
        return pretty_xml

    def Enregistrer(self, nomFichier=""):
        """ Enregistre le fichier XML """
        pretty_xml = self.GetPrettyXML()
        f = open(nomFichier, "w")
        try:
            f.write(pretty_xml)
        finally:
            f.close()



    
if __name__ == "__main__":
    export = Export(IDfamille=None)
    xml = export.GetPrettyXML()
    print(xml)
