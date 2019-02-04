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
from Utils.UTILS_Traduction import _
import wx
import GestionDB
import traceback
import datetime
import six
import sys
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
from Dlg import DLG_Apercu_inscription
from Utils import UTILS_Infos_individus
from Utils import UTILS_Fichiers




class Inscription():
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
        self.Questionnaires_individus = UTILS_Questionnaires.ChampsEtReponses(type="individu")
        self.Questionnaires_inscriptions = UTILS_Questionnaires.ChampsEtReponses(type="inscription")

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

    def GetDonneesImpression(self, listeInscriptions=[]):
        """ Impression des inscriptions """
        dlgAttente = wx.BusyInfo(_(u"Recherche des données..."), None)

        # Récupère les données de la facture
        if len(listeInscriptions) == 0:
            conditions = "()"
        elif len(listeInscriptions) == 1:
            conditions = "(%d)" % listeInscriptions[0]
        else:
            conditions = str(tuple(listeInscriptions))

        # Récupération des informations sur l'inscription
        dictChamps = {
            "inscriptions.IDinscription": "IDINSCRIPTION",
            "inscriptions.date_inscription": "DATE_INSCRIPTION",
            "inscriptions.date_desinscription": "EST_PARTI",

            "activites.IDactivite": "IDACTIVITE",
            "activites.nom": "ACTIVITE_NOM_LONG",
            "activites.abrege": "ACTIVITE_NOM_COURT",

            "groupes.IDgroupe": "IDGROUPE",
            "groupes.nom": "GROUPE_NOM_LONG",
            "groupes.abrege": "GROUPE_NOM_COURT",

            "categories_tarifs.IDcategorie_tarif": "IDCATEGORIETARIF",
            "categories_tarifs.nom": "NOM_CATEGORIE_TARIF",

            "individus.IDindividu": "IDINDIVIDU",
            "individus.IDcivilite": "IDCIVILITE",
            "individus.nom": "INDIVIDU_NOM",
            "individus.prenom": "INDIVIDU_PRENOM",
            "individus.date_naiss": "INDIVIDU_DATE_NAISS",
            "individus.cp_naiss": "INDIVIDU_CP_NAISS",
            "individus.ville_naiss": "INDIVIDU_VILLE_NAISS",
            "individus.adresse_auto": "INDIVIDU_ADRESSE_AUTO",
            "individus.rue_resid": "INDIVIDU_RUE",
            "individus.cp_resid": "INDIVIDU_CP",
            "individus.ville_resid": "INDIVIDU_VILLE",
            "individus.profession": "INDIVIDU_PROFESSION",
            "individus.employeur": "INDIVIDU_EMPLOYEUR",
            "individus.tel_domicile": "INDIVIDU_TEL_DOMICILE",
            "individus.tel_mobile": "INDIVIDU_TEL_MOBILE",
            "individus.tel_fax": "INDIVIDU_FAX",
            "individus.mail": "INDIVIDU_EMAIL",
            "individus.travail_tel": "INDIVIDU_TEL_PRO",
            "individus.travail_fax": "INDIVIDU_FAX_PRO",
            "individus.travail_mail": "INDIVIDU_EMAIL_PRO",

            "familles.IDfamille": "IDFAMILLE",
            "caisses.nom": "FAMILLE_CAISSE",
            "regimes.nom": "FAMILLE_REGIME",
            "familles.num_allocataire": "FAMILLE_NUMALLOC",
        }

        listeChamps = list(dictChamps.keys())

        DB = GestionDB.DB()
        req = """SELECT %s
        FROM inscriptions
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN familles ON familles.IDfamille = inscriptions.IDfamille
        LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
        LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
        WHERE IDinscription IN %s
        """ % (", ".join(listeChamps), conditions)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0:
            del dlgAttente
            return False

        dictDonnees = {}
        dictChampsFusion = {}
        for item in listeDonnees:

            dictDonnee = {}

            index = 0
            for nomChamp in listeChamps:
                code = dictChamps[nomChamp]
                valeur = item[index]
                dictDonnee["{%s}" % code] = valeur
                index += 1

            IDinscription = dictDonnee["{IDINSCRIPTION}"]
            IDfamille = dictDonnee["{IDFAMILLE}"]
            IDindividu = dictDonnee["{IDINDIVIDU}"]

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
            dictDonnee.update({
                "select": True,
                "{IDFAMILLE}": str(IDfamille),
                "{FAMILLE_NOM}": nomTitulaires,
                "{FAMILLE_RUE}": famille_rue,
                "{FAMILLE_CP}": famille_cp,
                "{FAMILLE_VILLE}": famille_ville,
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
                })

            # Formatage spécial
            dictDonnee["{DATE_INSCRIPTION}"] = UTILS_Dates.DateEngFr(dictDonnee["{DATE_INSCRIPTION}"])
            dictDonnee["{INDIVIDU_DATE_NAISS}"] = UTILS_Dates.DateEngFr(dictDonnee["{INDIVIDU_DATE_NAISS}"])

            # Autres données
            if IDfamille != None:
                dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))

            # Ajoute les réponses des questionnaires
            for dictReponse in self.Questionnaires_familles.GetDonnees(IDfamille):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            for dictReponse in self.Questionnaires_individus.GetDonnees(IDindividu):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            for dictReponse in self.Questionnaires_inscriptions.GetDonnees(IDinscription):
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres":
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            dictDonnees[IDinscription] = dictDonnee

            # Champs de fusion pour Email
            dictChampsFusion[IDinscription] = {}
            for key, valeur in dictDonnee.items():
                if key[0] == "{":
                    dictChampsFusion[IDinscription][key] = valeur

        del dlgAttente
        return dictDonnees, dictChampsFusion

    def Impression(self, listeInscriptions=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des inscriptions """
        from Utils import UTILS_Impression_inscription

        # Récupération des données à partir des IDinscription
        resultat = self.GetDonneesImpression(listeInscriptions)
        if resultat == False:
            return False
        dictInscriptions, dictChampsFusion = resultat

        # Récupération des paramètres d'affichage
        if dictOptions == None:
            if afficherDoc == False:
                dlg = DLG_Apercu_inscription.Dialog(None, titre=_(u"Sélection des paramètres de l'inscription"), intro=_(u"Sélectionnez ici les paramètres d'affichage de l'inscription."))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else:
                dlg = DLG_Apercu_inscription.Dialog(None)
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
                for IDinscription, dictInscription in dictInscriptions.items():
                    if dictInscription["select"] == True:
                        nomTitulaires = self.Supprime_accent(dictInscription["{FAMILLE_NOM}"])
                        nomFichier = _(u"Inscription %d - %s") % (IDinscription, nomTitulaires)
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDinscription: dictInscription}
                        self.EcritStatusbar(_(u"Edition de l'inscription %d/%d : %s") % (index, len(dictInscription), nomFichier))
                        UTILS_Impression_inscription.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDinscription] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception as err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des inscriptions : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
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
            for IDreponse, IDinscription in listeReponses :
                dictReponses[IDinscription] = IDreponse

            DB = GestionDB.DB(suffixe="DOCUMENTS")
            for IDinscription, cheminFichier in dictPieces.items():
                # Préparation du blob
                fichier = open(cheminFichier, "rb")
                data = fichier.read()
                fichier.close()
                buffer = six.BytesIO(data)
                blob = buffer.read()
                # Recherche l'IDreponse
                if IDinscription in dictReponses:
                    IDreponse = dictReponses[IDinscription]
                else :
                    # Création d'une réponse de questionnaire
                    listeDonnees = [
                        ("IDquestion", IDquestion),
                        ("reponse", "##DOCUMENTS##"),
                        ("type", "inscription"),
                        ("IDdonnee", IDinscription),
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
            self.EcritStatusbar(_(u"Création du PDF des inscriptions en cours... veuillez patienter..."))
            try:
                UTILS_Impression_inscription.Impression(dictInscriptions, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception as err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, u"Désolé, le problème suivant a été rencontré dans l'édition des inscriptions : \n\n%s" % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces




if __name__=='__main__':
   pass