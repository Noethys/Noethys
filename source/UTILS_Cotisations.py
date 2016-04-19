#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
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
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")
MONNAIE_SINGULIER = UTILS_Config.GetParametre("monnaie_singulier", _(u"Euro"))
MONNAIE_DIVISION = UTILS_Config.GetParametre("monnaie_division", _(u"Centime"))

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Impression_cotisation
import UTILS_Dates
import DLG_Apercu_cotisation
import UTILS_Conversion
import UTILS_Infos_individus
import UTILS_Divers
import UTILS_Fichiers


class Cotisation():
    def __init__(self):
        """ R�cup�ration de toutes les donn�es de base """
        
        DB = GestionDB.DB()
            
        # R�cup�ration des infos sur l'organisme
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
        
        # R�cup�ration des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 

        # R�cup�ration des questionnaires
        self.Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")

    def Supprime_accent(self, texte):
        liste = [ (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"a"), (u"�", u"u"), (u"�", u"o"), (u"�", u"c"), (u"�", u"i"), (u"�", u"i"),]
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
        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des donn�es..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        # R�cup�re les donn�es de la facture
        if len(listeCotisations) == 0 : conditions = "()"
        elif len(listeCotisations) == 1 : conditions = "(%d)" % listeCotisations[0]
        else : conditions = str(tuple(listeCotisations))

        DB = GestionDB.DB()
        
        # R�cup�ration des activit�s
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC;"""
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        dictActivites = {}
        for IDactivite, nom, abrege in listeTemp :
            dictTemp = {"IDactivite":IDactivite, "nom":nom, "abrege":abrege}
            dictActivites[IDactivite] = dictTemp

        # R�cup�re les prestations
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
        
        # R�cup�re la ventilation
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
            if dictFacturation.has_key(IDcotisation) :
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
        
        # Cr�ation des dictRappels
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
            
            # Activit�s
            texte = ""
            if len(activites) > 0 :
                listeTemp = []
                listeIDactivites = UTILS_Divers.ConvertChaineEnListe(activites)
                for IDactivite in listeIDactivites :
                    if dictActivites.has_key(IDactivite) :
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
                        
            # D�p�t
            if IDdepot_cotisation == None :
                depotStr = _(u"Non d�pos�e")
            else:
                depotStr = _(u"D�p�t n�%d") % IDdepot_cotisation

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
            
            if IDindividu != None and self.dictIndividus.has_key(IDindividu) :
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
            
            if dictFacturation.has_key(IDcotisation):
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

            # M�morisation des donn�es
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
            
            # Ajoute les r�ponses des questionnaires
            for dictReponse in self.Questionnaires.GetDonnees(IDfamille) :
                dictDonnee[dictReponse["champ"]] = dictReponse["reponse"]
                if dictReponse["controle"] == "codebarres" :
                    dictDonnee["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

            dictDonnees[IDcotisation] = dictDonnee
            
            # Champs de fusion pour Email
            dictChampsFusion[IDcotisation] = {}
            for key, valeur in dictDonnee.iteritems() :
                if key[0] == "{" :
                    dictChampsFusion[IDcotisation][key] = valeur

        del dlgAttente      
        return dictDonnees, dictChampsFusion


    def Impression(self, listeCotisations=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des factures """
        # R�cup�ration des donn�es � partir des IDrappel
        resultat = self.GetDonneesImpression(listeCotisations)
        if resultat == False :
            return False
        dictCotisations, dictChampsFusion = resultat
        
        # R�cup�ration des param�tres d'affichage
        if dictOptions == None :
            if afficherDoc == False :
                dlg = DLG_Apercu_cotisation.Dialog(None, titre=_(u"S�lection des param�tres de la cotisation"), intro=_(u"S�lectionnez ici les param�tres d'affichage de la cotisation."))
                dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
            else :
                dlg = DLG_Apercu_cotisation.Dialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                dictOptions = dlg.GetParametres()
                dlg.Destroy()
            else :
                dlg.Destroy()
                return False

        # Cr�ation des PDF � l'unit�
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgAttente = PBI.PyBusyInfo(_(u"G�n�ration des cotisations � l'unit� au format PDF..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            try :
                index = 0
                for IDcotisation, dictCotisation in dictCotisations.iteritems() :
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
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"D�sol�, le probl�me suivant a �t� rencontr� dans l'�dition des cotisations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # R�pertoire souhait� par l'utilisateur
        if repertoire != None :
            resultat = CreationPDFunique(repertoire)
            if resultat == False :
                return False

        # R�pertoire TEMP (pour Emails)
        dictPieces = {}
        if repertoireTemp == True :
            dictPieces = CreationPDFunique(UTILS_Fichiers.GetRepTemp())
            if dictPieces == False :
                return False

        # Fabrication du PDF global
        if repertoireTemp == False :
            dlgAttente = PBI.PyBusyInfo(_(u"Cr�ation du PDF des cotisations..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            self.EcritStatusbar(_(u"Cr�ation du PDF des cotisations en cours... veuillez patienter..."))
            try :
                UTILS_Impression_cotisation.Impression(dictCotisations, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, u"D�sol�, le probl�me suivant a �t� rencontr� dans l'�dition des cotisations : \n\n%s" % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
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
