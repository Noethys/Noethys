#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _

import wx
import CTRL_Bouton_image
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

import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Impression_rappel
import UTILS_Dates
import DLG_Apercu_rappel
import UTILS_Conversion
import UTILS_Infos_individus

from DLG_Saisie_texte_rappel import MOTSCLES


class Facturation():
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


        # Récupération des textes de rappels
        req = """SELECT IDtexte, titre, texte_pdf
        FROM textes_rappels;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        self.dictTextesRappels = {}
        for IDtexte, titre, texte_pdf in listeDonnees :
            self.dictTextesRappels[IDtexte] = {"titre" : titre, "texte_pdf" : texte_pdf}

        DB.Close() 
        
        # Get noms Titulaires
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 

        # Récupération des questionnaires
        self.Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")

        # Récupération des infos de base familles
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



    def GetDonnees(self, listeRappels=[], liste_activites=[], listeExceptionsComptes=[], date_reference=None, date_edition=None, prestations=["consommation", "cotisation", "autre"]):
        """ Recherche des rappels à créer """   
       
        # Création des conditions SQL
        if len(liste_activites) == 0 : conditionActivites = "()"
        elif len(liste_activites) == 1 : conditionActivites = "(%d)" % liste_activites[0]
        else : conditionActivites = str(tuple(liste_activites))
        
        if len(listeExceptionsComptes) == 0 : conditionComptes = "()"
        elif len(listeExceptionsComptes) == 1 : conditionComptes = "(%d)" % listeExceptionsComptes[0]
        else : conditionComptes = str(tuple(listeExceptionsComptes))    

        if len(prestations) == 1 :
            conditionPrestations = " prestations.categorie='%s'" % prestations[0]
        else :
            conditionPrestations = " prestations.categorie IN %s" % str(tuple(prestations)).replace("u'", "'")

        DB = GestionDB.DB()
        
        # Recherche des prestations de la période
        req = """SELECT prestations.IDcompte_payeur, prestations.IDfamille,
        MIN(prestations.date),
        MAX(prestations.date),
        SUM(prestations.montant)
        FROM prestations
        WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL)
        AND prestations.date < '%s' AND prestations.IDcompte_payeur NOT IN %s AND %s
        GROUP BY prestations.IDcompte_payeur
        ;""" % (conditionActivites, str(date_reference), conditionComptes, conditionPrestations)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()  
        
        # Récupération de la ventilation
        req = """SELECT prestations.IDcompte_payeur, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL)
        AND prestations.date < '%s' AND prestations.IDcompte_payeur NOT IN %s
        GROUP BY prestations.IDcompte_payeur
        ;""" % (conditionActivites, str(date_reference), conditionComptes)
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()  
        dictVentilation = {}
        for IDcompte_payeur, totalVentilation in listeVentilation :
            dictVentilation[IDcompte_payeur] = totalVentilation
            
        DB.Close() 


        # Analyse et regroupement des données
        dictComptes = {}
        for IDcompte_payeur, IDfamille, date_min, date_max, montant in listePrestations :
            
            if dictVentilation.has_key(IDcompte_payeur) :
                montant_ventilation = dictVentilation[IDcompte_payeur]
            else:
                montant_ventilation = 0.0
            
            # Regroupement par compte payeur
            if montant_ventilation == None : 
                montant_ventilation = 0.0
            
            # conversion en decimal
            montant = decimal.Decimal(str(montant))
            montant_ventilation = decimal.Decimal(str(montant_ventilation))
            
            numero = 0
            solde = montant_ventilation - montant 
            
            if solde < decimal.Decimal("0.0") :
                
                dictComptes[IDcompte_payeur] = {
                    "{FAMILLE_NOM}" :  self.dictTitulaires[IDfamille]["titulairesAvecCivilite"],
                    "nomSansCivilite" :  self.dictTitulaires[IDfamille]["titulairesSansCivilite"],
                    "IDfamille" : IDfamille,
                    "{IDFAMILLE}" : IDfamille,
                    "{FAMILLE_RUE}" : self.dictTitulaires[IDfamille]["adresse"]["rue"],
                    "{FAMILLE_CP}" : self.dictTitulaires[IDfamille]["adresse"]["cp"],
                    "{FAMILLE_VILLE}" : self.dictTitulaires[IDfamille]["adresse"]["ville"],
                    "num_rappel" : numero,
                    "{NUM_RAPPEL}" : u"%06d" % numero,
                    "{NOM_LOT}" : "",
                    "solde_num" : -solde,
                    "solde" : u"%.02f %s" % (-solde, SYMBOLE),
                    "{SOLDE}" : u"%.02f %s" % (-solde, SYMBOLE),
                    "solde_lettres" : UTILS_Conversion.trad(-solde, MONNAIE_SINGULIER, MONNAIE_DIVISION),
                    "{SOLDE_LETTRES}" : UTILS_Conversion.trad(-solde, MONNAIE_SINGULIER, MONNAIE_DIVISION),
                    "select" : True,
                    "num_codeBarre" :  "%07d" % numero,
                    "numero" : _(u"Rappel n°%07d") % numero,
                    "{CODEBARRES_NUM_RAPPEL}" : "F%06d" % numero,

                    "date_min" : UTILS_Dates.DateEngEnDateDD(date_min),
                    "date_max" : UTILS_Dates.DateEngEnDateDD(date_max),
                    "{DATE_MIN}" : UTILS_Dates.DateEngEnDateDD(date_min),
                    "{DATE_MAX}" : UTILS_Dates.DateEngEnDateDD(date_max),

                    "{DATE_EDITION_LONG}" : UTILS_Dates.DateComplete(date_edition),
                    "{DATE_EDITION_COURT}" : UTILS_Dates.DateEngFr(str(date_edition)),
                    
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
                    }
                
                # Ajout les données de base familles
                dictComptes[IDcompte_payeur].update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))
                
                # Ajoute les réponses des questionnaires
                for dictReponse in self.Questionnaires.GetDonnees(IDfamille) :
                    dictComptes[IDcompte_payeur][dictReponse["champ"]] = dictReponse["reponse"]
                    if dictReponse["controle"] == "codebarres" :
                        dictComptes[IDcompte_payeur]["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]
                
        return dictComptes


    def GetDonneesImpression(self, listeRappels=[]):
        """ Impression des factures """
        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des données de facturation..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        # Récupère les données de la facture
        if len(listeRappels) == 0 : conditions = "()"
        elif len(listeRappels) == 1 : conditions = "(%d)" % listeRappels[0]
        else : conditions = str(tuple(listeRappels))

        DB = GestionDB.DB()
        req = """
        SELECT 
        rappels.IDrappel, rappels.numero, rappels.IDcompte_payeur, 
        rappels.date_edition, rappels.activites, rappels.IDutilisateur,
        rappels.IDtexte, rappels.date_reference, rappels.solde,
        rappels.date_min, rappels.date_max, rappels.prestations,
        comptes_payeurs.IDfamille, lots_rappels.nom
        FROM rappels
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = rappels.IDcompte_payeur
        LEFT JOIN lots_rappels ON lots_rappels.IDlot = rappels.IDlot
        WHERE rappels.IDrappel IN %s
        GROUP BY rappels.IDrappel
        ORDER BY rappels.date_edition
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        if len(listeDonnees) == 0 : 
            del dlgAttente
            return False
        
        # Création des dictRappels
        dictRappels = {}
        dictChampsFusion = {}
        for IDrappel, numero, IDcompte_payeur, date_edition, activites, IDutilisateur, IDtexte, date_reference, solde, date_min, date_max, prestations, IDfamille, nomLot in listeDonnees :

            if numero == None : numero = 0
            date_edition = UTILS_Dates.DateEngEnDateDD(date_edition) 
            date_reference = UTILS_Dates.DateEngEnDateDD(date_reference)    
            
            if nomLot == None :
                nomLot = ""   
            
            dictRappel = {
                "{FAMILLE_NOM}" :  self.dictTitulaires[IDfamille]["titulairesAvecCivilite"],
                "nomSansCivilite" :  self.dictTitulaires[IDfamille]["titulairesSansCivilite"],
                "IDfamille" : IDfamille,
                "{IDFAMILLE}" : IDfamille,
                "{FAMILLE_RUE}" : self.dictTitulaires[IDfamille]["adresse"]["rue"],
                "{FAMILLE_CP}" : self.dictTitulaires[IDfamille]["adresse"]["cp"],
                "{FAMILLE_VILLE}" : self.dictTitulaires[IDfamille]["adresse"]["ville"],
                "num_rappel" : numero,
                "{NUM_RAPPEL}" : u"%06d" % numero,
                "{NOM_LOT}" : nomLot,
                "solde_num" : -solde,
                "solde" : u"%.02f %s" % (solde, SYMBOLE),
                "{SOLDE}" : u"%.02f %s" % (-solde, SYMBOLE),
                "solde_lettres" : UTILS_Conversion.trad(solde, MONNAIE_SINGULIER, MONNAIE_DIVISION),
                "{SOLDE_LETTRES}" : UTILS_Conversion.trad(-solde, MONNAIE_SINGULIER, MONNAIE_DIVISION),
                "select" : True,
                "num_codeBarre" :  "%07d" % numero,
                "numero" : _(u"Rappel n°%07d") % numero,
                "{CODEBARRES_NUM_RAPPEL}" : "F%06d" % numero,

                "date_min" : date_min,
                "date_max" : date_max,
                "{DATE_MIN}" : date_min,
                "{DATE_MAX}" : date_max,

                "{DATE_EDITION_LONG}" : UTILS_Dates.DateComplete(date_edition),
                "{DATE_EDITION_COURT}" : UTILS_Dates.DateEngFr(str(date_edition)),
                
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
                
                "titre" : self.dictTextesRappels[IDtexte]["titre"],
                "IDtexte" : IDtexte,
                }

            dictRappel["texte"] = self.Fusion(IDtexte, dictRappel)

            # Ajout les données de base familles
            dictRappel.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))

            # Ajoute les réponses des questionnaires
            for dictReponse in self.Questionnaires.GetDonnees(IDfamille) :
                dictRappel[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres" :
                    dictRappel["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            dictRappels[IDrappel] = dictRappel
            
            # Champs de fusion pour Email
            dictChampsFusion[IDrappel] = {}
            dictChampsFusion[IDrappel]["{NUMERO_RAPPEL}"] = dictRappel["{NUM_RAPPEL}"]
            dictChampsFusion[IDrappel]["{DATE_MIN}"] = UTILS_Dates.DateEngFr(str(date_min))
            dictChampsFusion[IDrappel]["{DATE_MAX}"] = UTILS_Dates.DateEngFr(str(date_max))
            dictChampsFusion[IDrappel]["{DATE_EDITION_RAPPEL}"] = UTILS_Dates.DateEngFr(str(date_edition))
            dictChampsFusion[IDrappel]["{DATE_REFERENCE}"] = UTILS_Dates.DateEngFr(str(date_reference))
            dictChampsFusion[IDrappel]["{SOLDE_CHIFFRES}"] = dictRappel["solde"]
            dictChampsFusion[IDrappel]["{SOLDE_LETTRES}"] = dictRappel["{SOLDE_LETTRES}"]
        
        del dlgAttente      
        return dictRappels, dictChampsFusion

    def Fusion(self, IDtexte=None, dictRappel={}):
        # Fusion du texte avec les champs
        texte = self.dictTextesRappels[IDtexte]["texte_pdf"]
        for motCle, code in MOTSCLES :
            valeur = dictRappel[code]
            if type(valeur) == int : valeur = str(valeur)
            if type(valeur) == float : 
                if valeur < 0 : valeur = -valeur
                valeur = str(valeur)
            if type(valeur) == datetime.date : valeur = UTILS_Dates.DateEngFr(str(valeur))
            if valeur == None : valeur = u""
            texte = texte.replace(motCle, valeur)
        return texte


    def Impression(self, listeRappels=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des factures """
        # Récupération des données à partir des IDrappel
        resultat = self.GetDonneesImpression(listeRappels)
        if resultat == False :
            return False
        dictRappels, dictChampsFusion = resultat
        
        # Récupération des paramètres d'affichage
        if dictOptions == None :
            if afficherDoc == False :
                dlg = DLG_Apercu_rappel.Dialog(None, titre=_(u"Sélection des paramètres de la lettre de rappel"), intro=_(u"Sélectionnez ici les paramètres d'affichage du rappel à envoyer par Email."))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else :
                dlg = DLG_Apercu_rappel.Dialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                dictOptions = dlg.GetParametres()
                dlg.Destroy()
            else :
                dlg.Destroy()
                return False

        # Création des PDF à l'unité
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgAttente = PBI.PyBusyInfo(_(u"Génération des lettres de rappel à l'unité au format PDF..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            try :
                index = 0
                for IDrappel, dictRappel in dictRappels.iteritems() :
                    if dictRappel["select"] == True :
                        num_rappel = dictRappel["num_rappel"]
                        nomTitulaires = self.Supprime_accent(dictRappel["nomSansCivilite"])
                        nomFichier = _(u"Lettre de rappel %d - %s") % (num_rappel, nomTitulaires)
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDrappel : dictRappel}
                        self.EcritStatusbar(_(u"Edition de la lettre de rappel %d/%d : %s") % (index, len(dictRappel), nomFichier))
                        UTILS_Impression_rappel.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDrappel] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des lettres de rappel : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
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
            dictPieces = CreationPDFunique("Temp")
            if dictPieces == False :
                return False

        # Fabrication du PDF global
        if repertoireTemp == False :
            dlgAttente = PBI.PyBusyInfo(_(u"Création du PDF des lettres de rappel..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            self.EcritStatusbar(_(u"Création du PDF des lettres de rappel en cours... veuillez patienter..."))
            try :
                UTILS_Impression_rappel.Impression(dictRappels, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                err = str(err).decode("iso-8859-15")
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des lettres de rappel : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces




        



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    # Test du module Facturation :
    facturation = Facturation() 
##    print len(facturation.GetDonnees( listeRappels=[], liste_activites=[1, 2, 3], listeExceptionsComptes=[], date_reference=datetime.date.today(), date_edition=datetime.date.today(), prestations=["consommation", "cotisation", "autre"]))
##    print len(facturation.GetDonneesImpression(listeRappels=[1, 2, 3]))
    facturation.Impression(listeRappels=range(200, 210))
    app.MainLoop()
