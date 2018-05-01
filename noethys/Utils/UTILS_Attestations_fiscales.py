#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _

import wx
from Ctrl import CTRL_Bouton_image
import datetime
import decimal
import copy
import sys
import traceback
import wx.lib.agw.pybusyinfo as PBI

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
MONNAIE_SINGULIER = UTILS_Config.GetParametre("monnaie_singulier", _(u"Euro"))
MONNAIE_DIVISION = UTILS_Config.GetParametre("monnaie_division", _(u"Centime"))

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Impression_attestation_fiscale
import UTILS_Dates
from Dlg import DLG_Apercu_attestation_fiscale
import UTILS_Conversion
import UTILS_Infos_individus
import UTILS_Fichiers

from Data import DATA_Civilites
DICT_CIVILITES = DATA_Civilites.GetDictCivilites()



class Attestations_fiscales():
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
        for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees :
            self.dictOrganisme["nom"] = nom
            self.dictOrganisme["rue"] = rue
            self.dictOrganisme["cp"] = cp
            if ville != None : ville = ville.capitalize()
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

        # Récupération des questionnaires
        self.Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")

        # Récupération des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 


    def Supprime_accent(self, texte):
        liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
        for a, b in liste :
            texte = texte.replace(a, b)
            texte = texte.replace(a.upper(), b.upper())
        return texte

    def EcritStatusbar(self, texte=u""):
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass

    def GetDonneesImpression(self, tracks=[], dictOptions={}):
        """ Impression des factures """
        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des données..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        try :
            wx.Yield()
        except :
            pass
        
        dictDonnees = {}
        dictChampsFusion = {}
        for track in tracks :
            IDfamille = track.IDfamille 
            IDcompte_payeur = track.IDcompte_payeur
            
            # Regroupement des enfants
            dictEnfants = {}
            for prestation in track.listePrestations :
                IDindividu = prestation["IDindividu"]
                if dictEnfants.has_key(IDindividu) == False : 
                    if prestation["prenom"] == None : 
                        prenom = ""
                    else :
                        prenom = prestation["prenom"]
                    if prestation["date_naiss"] == None : 
                        date_naiss = ""
                    else :
                        date_naiss = UTILS_Dates.DateEngFr(prestation["date_naiss"])
                    genre = ""
                    if prestation["IDcivilite"] != None :
                        sexe = DICT_CIVILITES[prestation["IDcivilite"]]["sexe"]
                        if sexe == "F" :
                            genre = "e"
                    nomComplet = u"%s %s" % (prestation["nom"], prenom)
                    dictEnfants[IDindividu] = {"nomComplet" : nomComplet, "nom" : prestation["nom"], "prenom" : prenom, "date_naiss" : date_naiss, "genre" : genre, "regle" : FloatToDecimal(0.0)}
                dictEnfants[IDindividu]["regle"] += prestation["regle"]
            
            listeIndividus = []
            for IDindividu, dictTemp in dictEnfants.iteritems() :
                listeIndividus.append((dictTemp["nomComplet"], dictTemp))
            listeIndividus.sort() 
                            
            # Formatage du texte d'intro
            textIntro = ""
            if dictOptions["intro"] != None :
                textIntro = dictOptions["intro"]
                textIntro = textIntro.replace("{GENRE}", dictOptions["signataire"]["genre"])
                textIntro = textIntro.replace("{NOM}", dictOptions["signataire"]["nom"])
                textIntro = textIntro.replace("{FONCTION}", dictOptions["signataire"]["fonction"])
                textIntro = textIntro.replace("{DATE_DEBUT}", UTILS_Dates.DateEngFr(str(dictOptions["date_debut"])))
                textIntro = textIntro.replace("{DATE_FIN}", UTILS_Dates.DateEngFr(str(dictOptions["date_fin"])))
            
            # Mémorisation des données
            dictDonnee = {
                "{ORGANISATEUR_NOM}" : self.dictOrganisme["nom"],
                "{ORGANISATEUR_RUE}" : self.dictOrganisme["rue"],
                "{ORGANISATEUR_CP}" : self.dictOrganisme["cp"],
                "{ORGANISATEUR_VILLE}" : self.dictOrganisme["ville"],
                "{ORGANISATEUR_TEL}" : self.dictOrganisme["tel"],
                "{ORGANISATEUR_FAX}" : self.dictOrganisme["fax"],
                "{ORGANISATEUR_MAIL}" : self.dictOrganisme["mail"],
                "{ORGANISATEUR_SITE}" : self.dictOrganisme["site"],
                "{ORGANISATEUR_AGREMENT}" : self.dictOrganisme["num_agrement"],
                "{ORGANISATEUR_SIRET}" : self.dictOrganisme["num_siret"],
                "{ORGANISATEUR_APE}" : self.dictOrganisme["code_ape"],

                "{IDFAMILLE}" : str(track.IDfamille),
                "{IDCOMPTE_PAYEUR}" : str(track.IDcompte_payeur),
                "{FAMILLE_NOM}" :  track.nomsTitulairesSansCivilite,
                "{FAMILLE_RUE}" : track.rue_resid,
                "{FAMILLE_CP}" : track.cp_resid,
                "{FAMILLE_VILLE}" : track.ville_resid,
                
                "{DATE_EDITION_COURT}" : UTILS_Dates.DateDDEnFr(datetime.date.today()),
                "{DATE_EDITION_LONG}" : UTILS_Dates.DateComplete(datetime.date.today()),
                "{DATE_DEBUT}" : UTILS_Dates.DateDDEnFr(dictOptions["date_debut"]),
                "{DATE_FIN}" : UTILS_Dates.DateDDEnFr(dictOptions["date_fin"]),

                "{MONTANT_FACTURE}" : u"%.2f %s" % (track.montant_total, SYMBOLE),
                "{MONTANT_REGLE}" : u"%.2f %s" % (track.montant_regle, SYMBOLE),
                "{MONTANT_IMPAYE}" : u"%.2f %s" % (track.montant_impaye, SYMBOLE),
                
                "{MONTANT_FACTURE_LETTRES}" : UTILS_Conversion.trad(track.montant_total, MONNAIE_SINGULIER, MONNAIE_DIVISION),
                "{MONTANT_REGLE_LETTRES}" : UTILS_Conversion.trad(track.montant_regle, MONNAIE_SINGULIER, MONNAIE_DIVISION),
                "{MONTANT_IMPAYE_LETTRES}" : UTILS_Conversion.trad(track.montant_impaye, MONNAIE_SINGULIER, MONNAIE_DIVISION),
                 
                "{INTRO}" : textIntro,
                "TXT_ENFANT_1" : "",
                "TXT_ENFANT_2" : "",
                "TXT_ENFANT_3" : "",
                "TXT_ENFANT_4" : "",
                "TXT_ENFANT_5" : "",
                "TXT_ENFANT_6" : "",
                
                "individus" : listeIndividus,
                }
            
            # Ajoute les infos de base familles
            dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))
            
            # Insertion des enfants
            index = 1
            for nomCompletIndividu, dictIndividu in listeIndividus :
                dictDonnee["TXT_ENFANT_%d" % index] = _(u"%.2f %s pour %s né%s le %s") % (dictIndividu["regle"], SYMBOLE, nomCompletIndividu, dictIndividu["genre"], dictIndividu["date_naiss"])
                index += 1
                
            # Ajoute les réponses des questionnaires
            for dictReponse in self.Questionnaires.GetDonnees(IDfamille) :
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres" :
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]
            
            dictDonnees[IDcompte_payeur] = dictDonnee
            
            # Champs de fusion pour Email
            dictChampsFusion[IDcompte_payeur] = {}
            for key, valeur in dictDonnee.iteritems() :
                if key[0] == "{" :
                    dictChampsFusion[IDcompte_payeur][key] = valeur

        del dlgAttente      
        return dictDonnees, dictChampsFusion


    def Impression(self, tracks=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des factures """
        # Récupération des données à partir des IDrappel
        resultat = self.GetDonneesImpression(tracks, dictOptions)
        if resultat == False :
            return False
        dictDonnees, dictChampsFusion = resultat
        
        # Récupération des paramètres d'affichage
        if dictOptions == None :
            if afficherDoc == False :
                dlg = DLG_Apercu_attestation_fiscale.Dialog(None, titre=_(u"Sélection des paramètres de l'attestation fiscale"), intro=_(u"Sélectionnez ici les paramètres d'affichage de l'attestation fiscale"))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else :
                dlg = DLG_Apercu_attestation_fiscale.Dialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                dictOptions = dlg.GetParametres()
                dlg.Destroy()
            else :
                dlg.Destroy()
                return False

        # Création des PDF à l'unité
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgAttente = PBI.PyBusyInfo(_(u"Génération des attestations fiscales à l'unité au format PDF..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            try :
                index = 0
                for IDcompte_payeur, dictAttestation in dictDonnees.iteritems() :
                    nomTitulaires = self.Supprime_accent(dictAttestation["{FAMILLE_NOM}"])
                    nomFichier = u"%s" % nomTitulaires
                    cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                    dictComptesTemp = {IDcompte_payeur : dictAttestation}
                    self.EcritStatusbar(_(u"Edition de l'attestation fiscale %d/%d : %s") % (index, len(dictAttestation), nomFichier))
                    UTILS_Impression_attestation_fiscale.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                    dictPieces[IDcompte_payeur] = cheminFichier
                    index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des attestations fiscales : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Répertoire souhaité par l'utilisateur
        if repertoire != None :
            resultat = CreationPDFunique(repertoire)
            if resultat == False :
                return False

        # Répertoire TEMP (pour Emails)
        dictPieces = {}
        if repertoireTemp == True :
            dictPieces = CreationPDFunique(UTILS_Fichiers.GetRepTemp())
            if dictPieces == False :
                return False

        # Fabrication du PDF global
        if repertoireTemp == False :
            dlgAttente = PBI.PyBusyInfo(_(u"Création du PDF des attestations fiscales..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
            try :
                wx.Yield()
            except :
                pass
            self.EcritStatusbar(_(u"Création du PDF des attestations fiscales en cours... veuillez patienter..."))
            try :
                UTILS_Impression_attestation_fiscale.Impression(dictDonnees, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des attestations fiscales : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces







if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    from Dlg import DLG_Attestations_fiscales_generation
    dlg = DLG_Attestations_fiscales_generation.Dialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()


