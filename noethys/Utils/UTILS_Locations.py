#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from UTILS_Traduction import _
import wx
import GestionDB
import traceback
import datetime
import copy
import sys
import cStringIO
from Utils import UTILS_Dates
from Utils import UTILS_Texte
from Utils import UTILS_Filtres_questionnaires

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Dates
from Dlg import DLG_Apercu_location
import UTILS_Conversion
import UTILS_Infos_individus
import UTILS_Divers
import UTILS_Fichiers




class Location():
    def __init__(self):
        """ Récupération de toutes les données de base """

        DB = GestionDB.DB()

        # Récupération des infos sur l'organisme
        req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape
        FROM organisateur
        WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictOrganisme = {}
        for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees:
            self.dictOrganisme["nom"] = nom
            self.dictOrganisme["rue"] = rue
            self.dictOrganisme["cp"] = cp
            if ville != None: ville = ville.capitalize()
            self.dictOrganisme["ville"] = ville
            self.dictOrganisme["tel"] = tel
            self.dictOrganisme["fax"] = fax
            self.dictOrganisme["mail"] = mail
            self.dictOrganisme["site"] = site
            self.dictOrganisme["num_agrement"] = num_agrement
            self.dictOrganisme["num_siret"] = num_siret
            self.dictOrganisme["code_ape"] = code_ape

        DB.Close()

        # Get noms Titulaires et individus
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires()
        self.dictIndividus = UTILS_Titulaires.GetIndividus()

        # Récupération des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations()

        # Récupération des questionnaires
        self.Questionnaires_familles = UTILS_Questionnaires.ChampsEtReponses(type="famille")
        self.Questionnaires_locations = UTILS_Questionnaires.ChampsEtReponses(type="location")
        self.Questionnaires_produits = UTILS_Questionnaires.ChampsEtReponses(type="produit")

    def Supprime_accent(self, texte):
        liste = [(u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"), ]
        for a, b in liste:
            texte = texte.replace(a, b)
            texte = texte.replace(a.upper(), b.upper())
        return texte

    def EcritStatusbar(self, texte=u""):
        try:
            topWindow = wx.GetApp().GetTopWindow()
            topWindow.SetStatusText(texte)
        except:
            pass

    def GetDonneesImpression(self, listeLocations=[]):
        """ Impression des locations """
        dlgAttente = wx.BusyInfo(_(u"Recherche des données..."), None)

        # Récupère les données de la facture
        if len(listeLocations) == 0:
            conditions = "()"
        elif len(listeLocations) == 1:
            conditions = "(%d)" % listeLocations[0]
        else:
            conditions = str(tuple(listeLocations))

        DB = GestionDB.DB()

        # Recherche les locations
        req = """SELECT locations.IDlocation, locations.IDfamille, locations.IDproduit, 
        locations.observations, locations.date_debut, locations.date_fin,
        produits.nom,
        produits_categories.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDlocation IN %s;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0:
            del dlgAttente
            return False

        dictDonnees = {}
        dictChampsFusion = {}
        for item in listeDonnees:

            IDlocation = item[0]
            IDfamille = item[1]
            IDproduit = item[2]
            observations = item[3]
            date_debut = item[4]
            date_fin = item[5]

            if isinstance(date_debut, str) or isinstance(date_debut, unicode):
                date_debut = datetime.datetime.strptime(date_debut, "%Y-%m-%d %H:%M:%S")
            date_debut_texte = datetime.datetime.strftime(date_debut, "%d/%m/%Y")
            heure_debut_texte = datetime.datetime.strftime(date_debut, "%Hh%M")

            date_fin_texte = ""
            heure_fin_texte = ""
            if isinstance(date_fin, str) or isinstance(date_fin, unicode):
                date_fin = datetime.datetime.strptime(date_fin, "%Y-%m-%d %H:%M:%S")
                date_fin_texte = datetime.datetime.strftime(date_fin, "%d/%m/%Y")
                heure_fin_texte = datetime.datetime.strftime(date_fin, "%Hh%M")

            nomProduit = item[6]
            nomCategorie = item[7]

            # if IDindividu != None and self.dictIndividus.has_key(IDindividu):
            #     beneficiaires = self.dictIndividus[IDindividu]["nom_complet"]
            #     rue = self.dictIndividus[IDindividu]["rue"]
            #     cp = self.dictIndividus[IDindividu]["cp"]
            #     ville = self.dictIndividus[IDindividu]["ville"]

            # Famille
            if IDfamille != None:
                nomTitulaires = self.dictTitulaires[IDfamille]["titulairesAvecCivilite"]
                famille_rue = self.dictTitulaires[IDfamille]["adresse"]["rue"]
                famille_cp = self.dictTitulaires[IDfamille]["adresse"]["cp"]
                famille_ville = self.dictTitulaires[IDfamille]["adresse"]["ville"]
            else:
                nomTitulaires = "Famille inconnue"
                famille_rue = ""
                famille_cp = ""
                famille_ville = ""

            # Facturation
            # montant = 0.0
            # ventilation = 0.0
            # dateReglement = None
            # modeReglement = None
            #
            # if dictFacturation.has_key(IDcotisation):
            #     montant = dictFacturation[IDcotisation]["montant"]
            #     ventilation = dictFacturation[IDcotisation]["ventilation"]
            #     dateReglement = dictFacturation[IDcotisation]["dateReglement"]
            #     modeReglement = dictFacturation[IDcotisation]["modeReglement"]
            #
            # solde = float(FloatToDecimal(montant) - FloatToDecimal(ventilation))
            #
            # montantStr = u"%.02f %s" % (montant, SYMBOLE)
            # regleStr = u"%.02f %s" % (ventilation, SYMBOLE)
            # soldeStr = u"%.02f %s" % (solde, SYMBOLE)
            # montantStrLettres = UTILS_Conversion.trad(montant, MONNAIE_SINGULIER, MONNAIE_DIVISION)
            # regleStrLettres = UTILS_Conversion.trad(ventilation, MONNAIE_SINGULIER, MONNAIE_DIVISION)
            # soldeStrLettres = UTILS_Conversion.trad(solde, MONNAIE_SINGULIER, MONNAIE_DIVISION)


            # Mémorisation des données
            dictDonnee = {
                "select": True,
                "{IDLOCATION}": str(IDlocation),
                "{IDPRODUIT}": str(IDproduit),
                "{DATE_DEBUT}": date_debut_texte,
                "{DATE_FIN}": date_fin_texte,
                "{HEURE_DEBUT}": heure_debut_texte,
                "{HEURE_FIN}": heure_fin_texte,
                "{NOM_PRODUIT}": nomProduit,
                "{NOM_CATEGORIE}": nomCategorie,
                "{NOTES}": observations,
                "{IDFAMILLE}": str(IDfamille),
                "{FAMILLE_NOM}": nomTitulaires,
                "{FAMILLE_RUE}": famille_rue,
                "{FAMILLE_CP}": famille_cp,
                "{FAMILLE_VILLE}": famille_ville,

                # "{MONTANT_FACTURE}": montantStr,
                # "{MONTANT_REGLE}": regleStr,
                # "{SOLDE_ACTUEL}": soldeStr,
                # "{MONTANT_FACTURE_LETTRES}": montantStrLettres.capitalize(),
                # "{MONTANT_REGLE_LETTRES}": regleStrLettres.capitalize(),
                # "{SOLDE_ACTUEL_LETTRES}": soldeStrLettres.capitalize(),
                # "{DATE_REGLEMENT}": UTILS_Dates.DateDDEnFr(dateReglement),

                "{ORGANISATEUR_NOM}": self.dictOrganisme["nom"],
                "{ORGANISATEUR_RUE}": self.dictOrganisme["rue"],
                "{ORGANISATEUR_CP}": self.dictOrganisme["cp"],
                "{ORGANISATEUR_VILLE}": self.dictOrganisme["ville"],
                "{ORGANISATEUR_TEL}": self.dictOrganisme["tel"],
                "{ORGANISATEUR_FAX}": self.dictOrganisme["fax"],
                "{ORGANISATEUR_MAIL}": self.dictOrganisme["mail"],
                "{ORGANISATEUR_SITE}": self.dictOrganisme["site"],
                "{ORGANISATEUR_AGREMENT}": self.dictOrganisme["num_agrement"],
                "{ORGANISATEUR_SIRET}": self.dictOrganisme["num_siret"],
                "{ORGANISATEUR_APE}": self.dictOrganisme["code_ape"],

                "{DATE_EDITION_COURT}": UTILS_Dates.DateDDEnFr(datetime.date.today()),
                "{DATE_EDITION_LONG}": UTILS_Dates.DateComplete(datetime.date.today()),
            }

            # Ajoute les informations de base individus et familles
            # if IDindividu != None:
            #     dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="individu", ID=IDindividu, formatChamp=True))
            if IDfamille != None:
                dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))

            # Ajoute les réponses des questionnaires
            for dictReponse in self.Questionnaires_familles.GetDonnees(IDfamille):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            for dictReponse in self.Questionnaires_locations.GetDonnees(IDlocation):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            for dictReponse in self.Questionnaires_produits.GetDonnees(IDproduit):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            dictDonnees[IDlocation] = dictDonnee

            # Champs de fusion pour Email
            dictChampsFusion[IDlocation] = {}
            for key, valeur in dictDonnee.iteritems():
                if key[0] == "{":
                    dictChampsFusion[IDlocation][key] = valeur

        del dlgAttente
        return dictDonnees, dictChampsFusion

    def Impression(self, listeLocations=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des locations """
        import UTILS_Impression_location

        # Récupération des données à partir des IDlocation
        resultat = self.GetDonneesImpression(listeLocations)
        if resultat == False:
            return False
        dictLocations, dictChampsFusion = resultat

        # Récupération des paramètres d'affichage
        if dictOptions == None:
            if afficherDoc == False:
                dlg = DLG_Apercu_location.Dialog(None, titre=_(u"Sélection des paramètres de la location"), intro=_(u"Sélectionnez ici les paramètres d'affichage de la location."))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else:
                dlg = DLG_Apercu_location.Dialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                dictOptions = dlg.GetParametres()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False

        # Création des PDF à l'unité
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgAttente = wx.BusyInfo(_(u"Génération des PDF à l'unité en cours..."), None)
            try:
                index = 0
                for IDlocation, dictLocation in dictLocations.iteritems():
                    if dictLocation["select"] == True:
                        nomTitulaires = self.Supprime_accent(dictLocation["{FAMILLE_NOM}"])
                        nomFichier = _(u"Location %d - %s") % (IDlocation, nomTitulaires)
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDlocation: dictLocation}
                        self.EcritStatusbar(_(u"Edition de la location %d/%d : %s") % (index, len(dictLocation), nomFichier))
                        UTILS_Impression_location.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDlocation] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des locations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Répertoire souhaité par l'utilisateur
        if repertoire != None:
            resultat = CreationPDFunique(repertoire)
            if resultat == False:
                return False

        # Répertoire TEMP (pour Emails)
        dictPieces = {}
        if repertoireTemp == True:
            dictPieces = CreationPDFunique(UTILS_Fichiers.GetRepTemp())
            if dictPieces == False:
                return False

        # Sauvegarde dans un porte-documents
        if dictOptions["questionnaire"] != None :
            # Création des PDF
            if len(dictPieces) == 0 :
                dictPieces = CreationPDFunique(UTILS_Fichiers.GetRepTemp())

            # Recherche des IDreponse
            IDquestion = dictOptions["questionnaire"]
            DB = GestionDB.DB()
            req = """SELECT IDreponse, IDdonnee
            FROM questionnaire_reponses
            WHERE IDquestion=%d
            ;""" % IDquestion
            DB.ExecuterReq(req)
            listeReponses = DB.ResultatReq()
            DB.Close()
            dictReponses = {}
            for IDreponse, IDlocation in listeReponses :
                dictReponses[IDlocation] = IDreponse

            DB = GestionDB.DB(suffixe="DOCUMENTS")
            for IDlocation, cheminFichier in dictPieces.iteritems():
                # Préparation du blob
                fichier = open(cheminFichier, "rb")
                data = fichier.read()
                fichier.close()
                buffer = cStringIO.StringIO(data)
                blob = buffer.read()
                # Recherche l'IDreponse
                if dictReponses.has_key(IDlocation):
                    IDreponse = dictReponses[IDlocation]
                else :
                    # Création d'une réponse de questionnaire
                    listeDonnees = [
                        ("IDquestion", IDquestion),
                        ("reponse", "##DOCUMENTS##"),
                        ("type", "location"),
                        ("IDdonnee", IDlocation),
                        ]
                    DB2 = GestionDB.DB()
                    IDreponse = DB2.ReqInsert("questionnaire_reponses", listeDonnees)
                    DB2.Close()
                # Sauvegarde du document
                listeDonnees = [("IDreponse", IDreponse), ("type", "pdf"), ("label", dictOptions["nomModele"]), ("last_update", datetime.datetime.now())]
                IDdocument = DB.ReqInsert("documents", listeDonnees)
                DB.MAJimage(table="documents", key="IDdocument", IDkey=IDdocument, blobImage=blob, nomChampBlob="document")
            DB.Close()

        # Fabrication du PDF global
        if repertoireTemp == False:
            dlgAttente = wx.BusyInfo(_(u"Création du PDF en cours..."), None)
            self.EcritStatusbar(_(u"Création du PDF des locations en cours... veuillez patienter..."))
            try:
                UTILS_Impression_location.Impression(dictLocations, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, u"Désolé, le problème suivant a été rencontré dans l'édition des locations : \n\n%s" % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces

# -------------------------------------------------------------------------------------------------------------------------------------------

def GetStockDisponible(DB=None, IDproduit=None, date_debut=None, date_fin=None, IDlocation_exception=None):
    """ Recherche si un produit est disponible sur une période donnée """
    if DB == None:
        DBT = GestionDB.DB()
    else:
        DBT = DB

    if IDlocation_exception == None :
        IDlocation_exception = 0

    if date_debut == None :
        date_debut = datetime.datetime(1900, 1, 1)

    if date_fin == None :
        date_fin = datetime.datetime(2999, 1, 1)

    # Recherche le stock initial
    req = """SELECT IDproduit, quantite
    FROM produits
    WHERE IDproduit=%d;""" % IDproduit
    DBT.ExecuterReq(req)
    listeDonnees = DBT.ResultatReq()
    stock_initial = listeDonnees[0][1]
    if stock_initial == None :
        stock_initial = 1

    # Recherche les locations du produit sur la période
    req = """SELECT IDlocation, IDfamille, date_debut, date_fin, quantite
    FROM locations
    WHERE locations.IDproduit=%d AND date_debut<='%s' AND (date_fin IS NULL OR date_fin>='%s') AND IDlocation<>%d
    ;""" % (IDproduit, date_fin, date_debut, IDlocation_exception)
    DBT.ExecuterReq(req)
    listeDonnees = DBT.ResultatReq()
    listeLocations = []
    listeDates = [date_debut, date_fin]
    for IDlocation, IDfamille, debut, fin, quantite in listeDonnees:
        debut = UTILS_Dates.DateEngEnDateDDT(debut)
        fin = UTILS_Dates.DateEngEnDateDDT(fin)
        if quantite == None:
            quantite = 1
        listeLocations.append({"IDlocation": IDlocation, "IDfamille": IDfamille, "date_debut": debut, "date_fin": fin, "quantite": quantite})
        if debut not in listeDates and debut > date_debut :
            listeDates.append(debut)
        if fin not in listeDates and fin != None and fin < date_fin :
            listeDates.append(fin)

    if DB == None:
        DBT.Close()

    # Analyse des périodes de disponibilités
    listeDates.sort()
    dictPeriodes = {}
    for index in range(0, len(listeDates)-1) :
        debut, fin = (listeDates[index], listeDates[index+1])
        disponible = int(stock_initial)
        loue = 0

        for dictLocation in listeLocations :
            if dictLocation["date_debut"] < fin and (dictLocation["date_fin"] == None or dictLocation["date_fin"] > debut) :
                disponible -= dictLocation["quantite"]
                loue += dictLocation["quantite"]

        dictPeriodes[(debut, fin)] = {"loue": loue, "disponible" : disponible}

    return dictPeriodes


# -------------------------------------------------------------------------------------------------------------------------------------------

def GetProduitsLoues(DB=None, date_reference=None):
    """ Recherche les produits loués à la date de référence """
    if DB == None:
        DBT = GestionDB.DB()
    else:
        DBT = DB

    if date_reference == None :
        date_reference = datetime.datetime.now()

    # Recherche les locations à la date de référence
    req = """SELECT IDlocation, IDproduit, IDfamille, date_debut, date_fin, quantite
    FROM locations
    WHERE date_debut<='%s' AND (date_fin IS NULL OR date_fin>='%s')
    ;""" % (date_reference, date_reference)
    DBT.ExecuterReq(req)
    listeLocations = DBT.ResultatReq()
    dictLocations = {}
    for IDlocation, IDproduit, IDfamille, date_debut, date_fin, quantite in listeLocations:
        date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
        date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
        if quantite == None :
            quantite = 1
        if dictLocations.has_key(IDproduit) == False:
            dictLocations[IDproduit] = []
        dictLocations[IDproduit].append({"IDlocation": IDlocation, "IDfamille": IDfamille, "date_debut": date_debut, "date_fin": date_fin, "quantite" : quantite})

    if DB == None:
        DBT.Close()

    return dictLocations



def GetPropositionsLocations(dictFiltresSelection={}, dictDemandeSelection=None, uniquement_disponibles=True):
    DB = GestionDB.DB()

    # Importation des questionnaires des produits
    req = """SELECT IDreponse, IDquestion, reponse, IDdonnee
    FROM questionnaire_reponses
    WHERE type='produit';"""
    DB.ExecuterReq(req)
    listeReponses = DB.ResultatReq()
    dictReponses = {}
    for IDreponse, IDquestion, reponse, IDproduit in listeReponses :
        dictTemp = {"IDreponse" : IDreponse, "IDquestion" : IDquestion, "reponse" : reponse}
        if dictReponses.has_key(IDproduit) == False :
            dictReponses[IDproduit] = []
        dictReponses[IDproduit].append(dictTemp)

    # Recherche les produits non disponibles
    dictLocations = GetProduitsLoues(DB=DB)

    # Importation des produits
    req = """SELECT IDproduit, IDcategorie, nom, quantite
    FROM produits;"""
    DB.ExecuterReq(req)
    listeProduitsTemp = DB.ResultatReq()
    listeProduits = []
    dictProduits = {}
    dictProduitsByCategories = {}
    for IDproduit, IDcategorie, nom, quantite in listeProduitsTemp :
        if quantite == None :
            quantite = 1

        # Recherche les réponses au questionnaire du produit
        if dictReponses.has_key(IDproduit) :
            reponses = dictReponses[IDproduit]
        else :
            reponses = []

        # Recherche les locations en cours du produit
        if dictLocations.has_key(IDproduit):
            disponible = quantite
            for dictLocation in dictLocations[IDproduit] :
                disponible -= dictLocation["quantite"]
        else :
            disponible = quantite

        if uniquement_disponibles == False or disponible > 0 :
            dictTemp = {"IDproduit" : IDproduit, "IDcategorie" : IDcategorie, "disponible" : disponible, "nom" : nom, "reponses" : reponses}
            listeProduits.append(dictTemp)
            dictProduits[IDproduit] = dictTemp

            if dictProduitsByCategories.has_key(IDcategorie) == False :
                dictProduitsByCategories[IDcategorie] = []
            dictProduitsByCategories[IDcategorie].append(dictTemp)

    # Recherche les filtres de questionnaires
    req = """SELECT IDfiltre, questionnaire_filtres.IDquestion, choix, criteres, IDdonnee, 
    questionnaire_categories.type, controle
    FROM questionnaire_filtres
    LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_filtres.IDquestion
    LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
    WHERE categorie='location_demande';"""
    DB.ExecuterReq(req)
    listeFiltres = DB.ResultatReq()
    dictFiltres = {}
    for IDfiltre, IDquestion, choix, criteres, IDdemande, type, controle in listeFiltres :
        if dictFiltres.has_key(IDdemande) == False :
            dictFiltres[IDdemande] = []
        dictFiltres[IDdemande].append({"IDfiltre":IDfiltre, "IDquestion":IDquestion, "choix":choix, "criteres":criteres, "type":type, "controle":controle})

    # Ajoute ou remplace avec le dictDemandeSelection
    if dictFiltresSelection != None :
        for IDdemande, listeFiltres in dictFiltresSelection.iteritems() :
            dictFiltres[IDdemande] = listeFiltres

    # Importation des demandes de locations
    # if dictDemande == None :
    #     req = """SELECT IDdemande, date, IDfamille, categories, produits
    #     FROM locations_demandes
    #     WHERE statut='attente'
    #     ORDER BY IDdemande;"""
    #     DB.ExecuterReq(req)
    #     listeDemandes = DB.ResultatReq()
    # else :
    #     listeDemandes = [dictDemande,]

    req = """SELECT IDdemande, date, IDfamille, categories, produits
    FROM locations_demandes
    WHERE statut='attente' 
    ORDER BY IDdemande;"""
    DB.ExecuterReq(req)
    listeDemandes = DB.ResultatReq()

    if dictDemandeSelection != None and dictDemandeSelection["IDdemande"] == None :
        listeDemandes.append(dictDemandeSelection)

    DB.Close()

    # Parcours les demandes
    dictControles = UTILS_Filtres_questionnaires.GetDictControles()

    dictPropositions = {}
    dictPositions = {}
    for demande in listeDemandes :

        # Met les données dans un dict
        if not isinstance(demande, dict) :
            categories = UTILS_Texte.ConvertStrToListe(demande[3], siVide=[])
            produits = UTILS_Texte.ConvertStrToListe(demande[4], siVide=[])
            dictDemandeTemp = {"IDdemande" : demande[0], "date" : demande[1], "IDfamille" : demande[2], "categories" : categories, "produits": produits}
        else :
            dictDemandeTemp = demande

        if dictDemandeSelection != None and dictDemandeSelection["IDdemande"] == dictDemandeTemp["IDdemande"]:
            dictDemandeTemp = dictDemandeSelection

        IDdemande = dictDemandeTemp["IDdemande"]

        # Pré-sélection des produits à étudier
        listeProduitsTemp = []

        if dictDemandeTemp["categories"] != [] :
            for IDcategorie in dictDemandeTemp["categories"] :
                if dictProduitsByCategories.has_key(IDcategorie) :
                    listeProduitsTemp.extend(dictProduitsByCategories[IDcategorie])

        if dictDemandeTemp["produits"] != []:
            for IDproduit in dictDemandeTemp["produits"]:
                dictProduit = dictProduits[IDproduit]
                if dictProduits.has_key(IDproduit) and dictProduit not in listeProduitsTemp :
                    if dictDemandeTemp["categories"] == [] or dictProduit["IDcategorie"] in dictDemandeTemp["categories"] :
                        listeProduitsTemp.append(dictProduit)

        if len(listeProduitsTemp) == 0 :
            listeProduitsTemp = listeProduits

        # Parcours les produits
        for dictProduit in listeProduitsTemp :
            valide = True

            # # Vérifie si le produit est dans la liste des catégories souhaitées
            # if valide == True and dictDemandeTemp["categories"] != [] and dictProduit["IDcategorie"] not in dictDemandeTemp["categories"] :
            #     valide = False
            #
            # # Vérifie si le produit est dans la liste des produits souhaités
            # if valide == True and dictDemandeTemp["produits"] != [] and dictProduit["IDproduit"] not in dictDemandeTemp["produits"] :
            #     valide = False

            # Vérifie si le produit répond aux filtres de la demande
            if valide == True and dictFiltres.has_key(IDdemande):
                for dictFiltre in dictFiltres[IDdemande]:
                    for dictReponse in dictProduit["reponses"]:
                        resultat = UTILS_Filtres_questionnaires.Filtre(controle=dictFiltre["controle"], choix=dictFiltre["choix"], criteres=dictFiltre["criteres"], reponse=dictReponse["reponse"], dictControles=dictControles)
                        if resultat == False:
                            valide = False

            # Mémorisation de la proposition
            if valide == True :

                # Position dans la liste du produit
                if dictPositions.has_key(dictProduit["IDproduit"]) == False :
                    dictPositions[dictProduit["IDproduit"]] = 0
                dictPositions[dictProduit["IDproduit"]] += 1
                position = dictPositions[dictProduit["IDproduit"]]

                # Proposition
                dictProduit = dict(dictProduit)
                if dictPropositions.has_key(IDdemande) == False :
                    dictPropositions[IDdemande] = []
                dictProduit["position"] = position
                dictPropositions[IDdemande].append(dictProduit)

    return dictPropositions

def GetMeilleurePosition(dictPropositions={}, IDdemande=None):
    position = None
    if dictPropositions.has_key(IDdemande):
        for dictProduit in dictPropositions[IDdemande] :
            if position == None or dictProduit["position"] < position :
                position = dictProduit["position"]
    return position



if __name__=='__main__':
    import time
    heure_debut = time.time()

    #print "produits loues :", len(GetProduitsLoues())
    #dictPropositions = GetPropositionsLocations(uniquement_disponibles=False)
    #print "dictPropositions =", len(dictPropositions)

    print GetStockDisponible(IDproduit=2, date_debut=datetime.datetime(2017, 1, 1), date_fin=datetime.datetime(2017, 12, 31), IDlocation_exception=0)

    print "Temps execution =", time.time() - heure_debut