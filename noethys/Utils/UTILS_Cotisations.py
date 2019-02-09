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
from Utils.UTILS_Traduction import _

import wx
from Ctrl import CTRL_Bouton_image
import datetime
import decimal
import copy
import sys
import traceback

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
MONNAIE_SINGULIER = UTILS_Config.GetParametre("monnaie_singulier", _(u"Euro"))
MONNAIE_DIVISION = UTILS_Config.GetParametre("monnaie_division", _(u"Centime"))

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Utils import UTILS_Impression_cotisation
from Utils import UTILS_Dates
from Dlg import DLG_Apercu_cotisation
from Utils import UTILS_Conversion
from Utils import UTILS_Infos_individus
from Utils import UTILS_Divers
from Utils import UTILS_Fichiers


class Cotisation():
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
        
        # Récupération des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 

        # Récupération des questionnaires
        self.Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")

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

    def GetDonneesImpression(self, listeCotisations=[]):
        """ Impression des factures """
        dlgAttente = wx.BusyInfo(_(u"Recherche des données..."), None)
        if 'phoenix' not in wx.PlatformInfo:
            wx.Yield()
        
        # Récupère les données de la facture
        if len(listeCotisations) == 0 : conditions = "()"
        elif len(listeCotisations) == 1 : conditions = "(%d)" % listeCotisations[0]
        else : conditions = str(tuple(listeCotisations))

        DB = GestionDB.DB()
        
        # Récupération des activités
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC;"""
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        dictActivites = {}
        for IDactivite, nom, abrege in listeTemp :
            dictTemp = {"IDactivite":IDactivite, "nom":nom, "abrege":abrege}
            dictActivites[IDactivite] = dictTemp

        # Récupère les prestations
        dictFacturation = {}
        req = """SELECT IDcotisation, SUM(montant)
        FROM prestations
        LEFT JOIN cotisations ON cotisations.IDprestation = prestations.IDprestation
        WHERE cotisations.IDcotisation IN %s 
        GROUP BY cotisations.IDcotisation;""" % conditions
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        for IDcotisation, montant in listePrestations :
            dictFacturation[IDcotisation] = {"montant":montant, "ventilation":0.0, "dateReglement":None,"modeReglement":None}
        
        # Récupère la ventilation
        req = """SELECT IDcotisation, SUM(ventilation.montant), MIN(reglements.date), MIN(modes_reglements.label)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN cotisations ON cotisations.IDprestation = ventilation.IDprestation
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
        WHERE cotisations.IDcotisation IN %s 
        GROUP BY cotisations.IDcotisation;""" % conditions
        DB.ExecuterReq(req)
        listeVentilations = DB.ResultatReq()
        for IDcotisation, ventilation, dateReglement, modeReglement in listeVentilations :
            if IDcotisation in dictFacturation :
                dictFacturation[IDcotisation]["ventilation"] = ventilation
                dictFacturation[IDcotisation]["dateReglement"] = dateReglement
                dictFacturation[IDcotisation]["modeReglement"] = modeReglement
        
        # Recherche les cotisations
        req = """
        SELECT 
        cotisations.IDcotisation, 
        cotisations.IDfamille, cotisations.IDindividu, cotisations.IDtype_cotisation, cotisations.IDunite_cotisation,
        cotisations.date_saisie, cotisations.IDutilisateur, cotisations.date_creation_carte, cotisations.numero,
        cotisations.IDdepot_cotisation, cotisations.date_debut, cotisations.date_fin, cotisations.IDprestation, 
        types_cotisations.nom, types_cotisations.type, types_cotisations.carte,
        unites_cotisations.nom, comptes_payeurs.IDcompte_payeur, cotisations.observations, cotisations.activites
        FROM cotisations 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN unites_cotisations ON unites_cotisations.IDunite_cotisation = cotisations.IDunite_cotisation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = cotisations.IDfamille
        WHERE cotisations.IDcotisation IN %s 
        ORDER BY cotisations.date_saisie
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        if len(listeDonnees) == 0 : 
            del dlgAttente
            return False
        
        # Création des dictRappels
        dictDonnees = {}
        dictChampsFusion = {}
        for item in listeDonnees :

            IDcotisation = item[0]
            IDfamille = item[1]
            IDindividu = item[2]
            IDtype_cotisation = item[3]
            IDunite_cotisation = item[4]
            date_saisie = UTILS_Dates.DateEngEnDateDD(item[5])
            IDutilisateur = item[6]
            date_creation_carte = item[7]
            numero = item[8]
            IDdepot_cotisation = item[9]
            date_debut = UTILS_Dates.DateEngEnDateDD(item[10])
            date_fin = UTILS_Dates.DateEngEnDateDD(item[11])
            IDprestation = item[12]
            nomTypeCotisation = item[13]
            typeTypeCotisation = item[14]
            typeHasCarte = item[15]
            nomUniteCotisation = item[16]
            IDcompte_payeur = item[17]
            observations = item[18] 
            activites = item[19]
            if activites == None :
                activites = ""
            
            # Activités
            texte = ""
            if len(activites) > 0 :
                listeTemp = []
                listeIDactivites = UTILS_Divers.ConvertChaineEnListe(activites)
                for IDactivite in listeIDactivites :
                    if IDactivite in dictActivites :
                        nomActivite = dictActivites[IDactivite]["nom"]
                        listeTemp.append(nomActivite)
                if len(listeTemp) > 0 :
                    texte = ", ".join(listeTemp)
            activites = texte
            
            nomCotisation = u"%s - %s" % (nomTypeCotisation, nomUniteCotisation)
            
            # Type
            if typeTypeCotisation == "famille" :
                typeStr = _(u"Cotisation familiale")
            else:
                typeStr = _(u"Cotisation individuelle")
                        
            # Dépôt
            if IDdepot_cotisation == None :
                depotStr = _(u"Non déposée")
            else:
                depotStr = _(u"Dépôt n°%d") % IDdepot_cotisation

            # Nom des titulaires de famille
            beneficiaires = ""
            rue = ""
            cp = ""
            ville = ""
            
            if IDfamille != None :
                beneficiaires = self.dictTitulaires[IDfamille]["titulairesAvecCivilite"]
                rue = self.dictTitulaires[IDfamille]["adresse"]["rue"]
                cp = self.dictTitulaires[IDfamille]["adresse"]["cp"]
                ville = self.dictTitulaires[IDfamille]["adresse"]["ville"]
            
            if IDindividu != None and IDindividu in self.dictIndividus :
                beneficiaires = self.dictIndividus[IDindividu]["nom_complet"]
                rue = self.dictIndividus[IDindividu]["rue"]
                cp = self.dictIndividus[IDindividu]["cp"]
                ville = self.dictIndividus[IDindividu]["ville"]
            
            # Famille
            if IDfamille != None :
                nomTitulaires = self.dictTitulaires[IDfamille]["titulairesAvecCivilite"]
                famille_rue = self.dictTitulaires[IDfamille]["adresse"]["rue"]
                famille_cp = self.dictTitulaires[IDfamille]["adresse"]["cp"]
                famille_ville = self.dictTitulaires[IDfamille]["adresse"]["ville"]
            else :
                nomTitulaires = "Famille inconnue"
                famille_rue = ""
                famille_cp = ""
                famille_ville = ""
                
            # Facturation
            montant = 0.0
            ventilation = 0.0
            dateReglement = None
            modeReglement = None
            
            if IDcotisation in dictFacturation:
                montant = dictFacturation[IDcotisation]["montant"]
                ventilation = dictFacturation[IDcotisation]["ventilation"]
                dateReglement = dictFacturation[IDcotisation]["dateReglement"]
                modeReglement = dictFacturation[IDcotisation]["modeReglement"]
                
            solde = float(FloatToDecimal(montant) - FloatToDecimal(ventilation))
            
            montantStr = u"%.02f %s" % (montant, SYMBOLE)
            regleStr = u"%.02f %s" % (ventilation, SYMBOLE)
            soldeStr = u"%.02f %s" % (solde, SYMBOLE)
            montantStrLettres = UTILS_Conversion.trad(montant, MONNAIE_SINGULIER, MONNAIE_DIVISION)
            regleStrLettres = UTILS_Conversion.trad(ventilation, MONNAIE_SINGULIER, MONNAIE_DIVISION)
            soldeStrLettres = UTILS_Conversion.trad(solde, MONNAIE_SINGULIER, MONNAIE_DIVISION)

            # Mémorisation des données
            dictDonnee = {
                "select" : True,
                
                "{IDCOTISATION}" : str(IDcotisation),
                "{IDTYPE_COTISATION}" : str(IDtype_cotisation),
                "{IDUNITE_COTISATION}" : str(IDunite_cotisation),
                "{DATE_SAISIE}" : UTILS_Dates.DateDDEnFr(date_saisie),
                "{IDUTILISATEUR}" : str(IDutilisateur),
                "{DATE_CREATION_CARTE}" : UTILS_Dates.DateDDEnFr(date_creation_carte),
                "{NUMERO_CARTE}" : numero,
                "{IDDEPOT_COTISATION}" : str(IDdepot_cotisation),
                "{DATE_DEBUT}" : UTILS_Dates.DateDDEnFr(date_debut),
                "{DATE_FIN}" : UTILS_Dates.DateDDEnFr(date_fin),
                "{IDPRESTATION}" : str(IDprestation),
                "{NOM_TYPE_COTISATION}" : nomTypeCotisation,
                "{NOM_UNITE_COTISATION}" : nomUniteCotisation,
                "{COTISATION_FAM_IND}" : typeStr,
                "{IDCOMPTE_PAYEUR}" : str(IDcompte_payeur),
                "{NOM_COTISATION}" : nomCotisation,
                "{NOM_DEPOT}" : depotStr,
                "{MONTANT_FACTURE}" : montantStr,
                "{MONTANT_REGLE}" : regleStr,
                "{SOLDE_ACTUEL}" : soldeStr,
                "{MONTANT_FACTURE_LETTRES}" : montantStrLettres.capitalize(),
                "{MONTANT_REGLE_LETTRES}" : regleStrLettres.capitalize(),
                "{SOLDE_ACTUEL_LETTRES}" : soldeStrLettres.capitalize(),
                "{DATE_REGLEMENT}" : UTILS_Dates.DateDDEnFr(dateReglement),
                "{MODE_REGLEMENT}" : modeReglement,
                "{ACTIVITES}" : activites,
                "{NOTES}" : observations,
                
                "{IDINDIVIDU}" : IDindividu,
                "{BENEFICIAIRE_NOM}" :  beneficiaires,
                "{BENEFICIAIRE_RUE}" : rue,
                "{BENEFICIAIRE_CP}" : cp,
                "{BENEFICIAIRE_VILLE}" : ville,
                
                "{IDFAMILLE}" : str(IDfamille),
                "{FAMILLE_NOM}" :  nomTitulaires,
                "{FAMILLE_RUE}" : famille_rue,
                "{FAMILLE_CP}" : famille_cp,
                "{FAMILLE_VILLE}" : famille_ville,
                
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

                "{DATE_EDITION_COURT}" : UTILS_Dates.DateDDEnFr(datetime.date.today()),
                "{DATE_EDITION_LONG}" : UTILS_Dates.DateComplete(datetime.date.today()),
                }
            
            # Ajoute les informations de base individus et familles
            if IDindividu != None :
                dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="individu", ID=IDindividu, formatChamp=True))
            if IDfamille != None :
                dictDonnee.update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))
            
            # Ajoute les réponses des questionnaires
            for dictReponse in self.Questionnaires.GetDonnees(IDfamille) :
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres" :
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            dictDonnees[IDcotisation] = dictDonnee
            
            # Champs de fusion pour Email
            dictChampsFusion[IDcotisation] = {}
            for key, valeur in dictDonnee.items() :
                if key[0] == "{" :
                    dictChampsFusion[IDcotisation][key] = valeur

        del dlgAttente      
        return dictDonnees, dictChampsFusion


    def Impression(self, listeCotisations=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des factures """
        # Récupération des données à partir des IDrappel
        resultat = self.GetDonneesImpression(listeCotisations)
        if resultat == False :
            return False
        dictCotisations, dictChampsFusion = resultat
        
        # Récupération des paramètres d'affichage
        if dictOptions == None :
            if afficherDoc == False :
                dlg = DLG_Apercu_cotisation.Dialog(None, titre=_(u"Sélection des paramètres de la cotisation"), intro=_(u"Sélectionnez ici les paramètres d'affichage de la cotisation."))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else :
                dlg = DLG_Apercu_cotisation.Dialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                dictOptions = dlg.GetParametres()
                dlg.Destroy()
            else :
                dlg.Destroy()
                return False

        # Création des PDF à l'unité
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgAttente = wx.BusyInfo(_(u"Génération des cotisations à l'unité au format PDF..."), None)
            if 'phoenix' not in wx.PlatformInfo:
                wx.Yield()
            try :
                index = 0
                for IDcotisation, dictCotisation in dictCotisations.items() :
                    if dictCotisation["select"] == True :
                        numero_cotisation = str(dictCotisation["{NUMERO_CARTE}"])
                        nomTitulaires = self.Supprime_accent(dictCotisation["{FAMILLE_NOM}"])
                        nomFichier = _(u"Cotisation %s - %s") % (numero_cotisation, nomTitulaires)
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDcotisation : dictCotisation}
                        self.EcritStatusbar(_(u"Edition de la cotisation %d/%d : %s") % (index, len(dictCotisation), nomFichier))
                        UTILS_Impression_cotisation.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDcotisation] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception as err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des cotisations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
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
            dlgAttente = wx.BusyInfo(_(u"Création du PDF des cotisations..."), None)
            if 'phoenix' not in wx.PlatformInfo:
                wx.Yield()
            self.EcritStatusbar(_(u"Création du PDF des cotisations en cours... veuillez patienter..."))
            try :
                UTILS_Impression_cotisation.Impression(dictCotisations, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception as err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, u"Désolé, le problème suivant a été rencontré dans l'édition des cotisations : \n\n%s" % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces




        



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    # Test du module Facturation :
    cotisation = Cotisation() 
##    print len(cotisation.GetDonneesImpression(listeCotisations=[5, 6, 7, 8, 9]))
    cotisation.Impression(listeCotisations=range(5, 9))
    app.MainLoop()
