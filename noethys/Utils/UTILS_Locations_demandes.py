#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import GestionDB
import traceback
import datetime
import copy
import sys
import six
from Utils import UTILS_Dates
from Utils import UTILS_Texte
from Utils import UTILS_Filtres_questionnaires

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Utils import UTILS_Dates
from Dlg import DLG_Apercu_location_demande
from Utils import UTILS_Conversion
from Utils import UTILS_Infos_individus
from Utils import UTILS_Divers
from Utils import UTILS_Fichiers




class Demande():
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
        self.Questionnaires_demandes = UTILS_Questionnaires.ChampsEtReponses(type="location_demande")

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

    def GetDonneesImpression(self, listeDemandes=[]):
        """ Impression des locations """
        dlgAttente = wx.BusyInfo(_(u"Recherche des données..."), None)

        # Récupère les données de la facture
        if len(listeDemandes) == 0:
            conditions = "()"
        elif len(listeDemandes) == 1:
            conditions = "(%d)" % listeDemandes[0]
        else:
            conditions = str(tuple(listeDemandes))

        DB = GestionDB.DB()

        # Importation des catégories de produits
        req = """SELECT IDcategorie, nom
        FROM produits_categories;"""
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        self.dictCategories = {}
        for IDcategorie, nom in listeCategories :
            self.dictCategories[IDcategorie] = nom

        # Importation des produits
        req = """SELECT IDproduit, nom
        FROM produits;"""
        DB.ExecuterReq(req)
        listeProduits = DB.ResultatReq()
        self.dictProduits = {}
        for IDproduit, nom in listeProduits :
            self.dictProduits[IDproduit] = nom

        # # Importation des critères
        # req = """SELECT IDfiltre, IDquestion, categorie, choix, criteres FROM questionnaire_filtres WHERE categorie='location_demande' AND IDdonnee IN %s;""" % conditions
        # DB.ExecuterReq(req)
        # listeFiltres = DB.ResultatReq()
        #
        # req = """SELECT IDquestion, label, controle
        # FROM questionnaire_questions;"""
        # DB.ExecuterReq(req)
        # listeQuestions = DB.ResultatReq()
        # DICT_QUESTIONS = {}
        # for IDquestion, label, controle in listeQuestions:
        #     DICT_QUESTIONS[IDquestion] = {"label": label, "controle": controle}
        #
        # # Importation des choix
        # req = """SELECT IDchoix, IDquestion, label
        # FROM questionnaire_choix
        # ORDER BY ordre;"""
        # DB.ExecuterReq(req)
        # listeChoix = DB.ResultatReq()
        # DICT_CHOIX = {}
        # for IDchoix, IDquestion, label in listeChoix:
        #     DICT_CHOIX[IDchoix] = {"label": label, "IDquestion": IDquestion, }

        # Recherche les locations
        req = """SELECT IDdemande, date, IDfamille, observations, categories, produits, statut, motif_refus, IDlocation
        FROM locations_demandes
        WHERE IDdemande IN %s;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0:
            del dlgAttente
            return False

        dictDonnees = {}
        dictChampsFusion = {}
        for item in listeDonnees:

            IDdemande = item[0]
            date = item[1]
            IDfamille = item[2]
            observations = item[3]
            categories = item[4]
            produits = item[5]
            statut = item[6]
            motif_refus = item[7]
            IDlocation = item[8]

            # Date de la demande
            if isinstance(date, str) or isinstance(date, six.text_type):
                date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date_texte = datetime.datetime.strftime(date, "%d/%m/%Y")
            heure_texte = datetime.datetime.strftime(date, "%Hh%M")

            # Catégories
            categories = UTILS_Texte.ConvertStrToListe(categories, siVide=[])
            liste_labels = []
            for IDcategorie in categories:
                if IDcategorie in self.dictCategories:
                    liste_labels.append(self.dictCategories[IDcategorie])
            texte_categories = ", ".join(liste_labels)

            # Produits
            produits = UTILS_Texte.ConvertStrToListe(produits, siVide=[])
            liste_labels = []
            for IDproduit in produits:
                if IDproduit in self.dictProduits:
                    liste_labels.append(self.dictProduits[IDproduit])
            texte_produits = ", ".join(liste_labels)

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

            # Mémorisation des données
            dictDonnee = {
                "select": True,
                "{IDDEMANDE}": str(IDdemande),
                "{DATE}": date_texte,
                "{HEURE}": heure_texte,
                "{CATEGORIES}": texte_categories,
                "{PRODUITS}": texte_produits,
                "{NOTES}": observations,

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

            for dictReponse in self.Questionnaires_demandes.GetDonnees(IDdemande):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            dictDonnees[IDdemande] = dictDonnee

            # Champs de fusion pour Email
            dictChampsFusion[IDdemande] = {}
            for key, valeur in dictDonnee.items():
                if key[0] == "{":
                    dictChampsFusion[IDdemande][key] = valeur

        del dlgAttente
        return dictDonnees, dictChampsFusion

    def Impression(self, listeDemandes=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des demandes """
        from Utils import UTILS_Impression_location

        # Récupération des données à partir des IDdemande
        resultat = self.GetDonneesImpression(listeDemandes)
        if resultat == False:
            return False
        dictDemandes, dictChampsFusion = resultat

        # Récupération des paramètres d'affichage
        if dictOptions == None:
            if afficherDoc == False:
                dlg = DLG_Apercu_location_demande.Dialog(None, titre=_(u"Sélection des paramètres de la demande"), intro=_(u"Sélectionnez ici les paramètres d'affichage de la demande."))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else:
                dlg = DLG_Apercu_location_demande.Dialog(None)
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
                for IDdemande, dictDemande in dictDemandes.items():
                    if dictDemande["select"] == True:
                        nomTitulaires = self.Supprime_accent(dictDemande["{FAMILLE_NOM}"])
                        nomFichier = _(u"Demande %d - %s") % (IDdemande, nomTitulaires)
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDdemande: dictDemande}
                        self.EcritStatusbar(_(u"Edition de la demande %d/%d : %s") % (index, len(dictDemande), nomFichier))
                        UTILS_Impression_location.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDdemande] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception as err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des demandes : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
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
            for IDreponse, IDdemande in listeReponses :
                dictReponses[IDdemande] = IDreponse

            DB = GestionDB.DB(suffixe="DOCUMENTS")
            for IDdemande, cheminFichier in dictPieces.items():
                # Préparation du blob
                fichier = open(cheminFichier, "rb")
                data = fichier.read()
                fichier.close()
                buffer = six.BytesIO(data)
                blob = buffer.read()
                # Recherche l'IDreponse
                if IDdemande in dictReponses:
                    IDreponse = dictReponses[IDdemande]
                else :
                    # Création d'une réponse de questionnaire
                    listeDonnees = [
                        ("IDquestion", IDquestion),
                        ("reponse", "##DOCUMENTS##"),
                        ("type", "location_demande"),
                        ("IDdonnee", IDdemande),
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
            self.EcritStatusbar(_(u"Création du PDF des demandes en cours... veuillez patienter..."))
            try:
                UTILS_Impression_location.Impression(dictDemandes, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception as err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, u"Désolé, le problème suivant a été rencontré dans l'édition des demandes : \n\n%s" % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces






if __name__=='__main__':
    pass