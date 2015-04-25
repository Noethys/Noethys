#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import wx
import datetime
import copy
import sys
import traceback
import wx.lib.agw.pybusyinfo as PBI

import UTILS_Conversion
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")
MONNAIE_SINGULIER = UTILS_Config.GetParametre("monnaie_singulier", u"Euro")
MONNAIE_DIVISION = UTILS_Config.GetParametre("monnaie_division", u"Centime")

import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
import UTILS_Titulaires
import UTILS_Questionnaires
import UTILS_Impression_facture
import UTILS_Dates
import DLG_Apercu_facture
from UTILS_Decimal import FloatToDecimal as FloatToDecimal
import UTILS_Infos_individus



class Facturation():
    def __init__(self):
        """ R�cup�ration de toutes les donn�es de base """
        
        DB = GestionDB.DB()
            
        # R�cup�ration de tous les individus de la base
        req = """SELECT IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid
        FROM individus;""" 
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()  
        self.dictIndividus = {}
        for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid in listeIndividus :
            self.dictIndividus[IDindividu] = {"IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":date_naiss, "adresse_auto":adresse_auto, "rue_resid":rue_resid, "cp_resid":cp_resid, "ville_resid":ville_resid}

        # R�cup�ration de tous les messages familiaux � afficher
        req = """SELECT IDmessage, IDcategorie, date_parution, priorite, IDfamille, nom, texte
        FROM messages
        WHERE afficher_facture=1 AND IDfamille IS NOT NULL;"""
        DB.ExecuterReq(req)
        listeMessagesFamiliaux = DB.ResultatReq()  
        self.dictMessageFamiliaux = {}
        for IDmessage, IDcategorie, date_parution, priorite, IDfamille, nom, texte in listeMessagesFamiliaux :
            date_parution = UTILS_Dates.DateEngEnDateDD(date_parution)
            if self.dictMessageFamiliaux.has_key(IDfamille) == False :
                self.dictMessageFamiliaux[IDfamille] = []
            self.dictMessageFamiliaux[IDfamille].append({"IDmessage":IDmessage, "IDcategorie":IDcategorie, "date_parution":date_parution, "priorite":priorite, "nom":nom, "texte":texte})

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
        
        # Get noms Titulaires
        self.dictNomsTitulaires = UTILS_Titulaires.GetTitulaires() 

        # Recherche des num�ros d'agr�ments
        req = """SELECT IDactivite, agrement, date_debut, date_fin
        FROM agrements
        ORDER BY date_debut;"""
        DB.ExecuterReq(req)
        self.listeAgrements = DB.ResultatReq()  

        DB.Close() 

        # R�cup�ration des questionnaires
        self.Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")
        
        # R�cup�ration des infos de base familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 


    def RechercheAgrement(self, IDactivite, date):
        for IDactiviteTmp, agrement, date_debut, date_fin in self.listeAgrements :
            if IDactivite == IDactiviteTmp and date >= date_debut and date <= date_fin :
                return agrement
        return None

    def Supprime_accent(self, texte):
        liste = [ (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"a"), (u"�", u"a"), (u"�", u"u"), (u"�", u"o"), (u"�", u"c"), (u"�", u"i"), (u"�", u"i"), (u"/", u""), (u"\\", u""), ]
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
    
    def RemplaceMotsCles(self, texte="", dictValeurs={}):
        for key, valeur, in dictValeurs.iteritems() :
            if key in texte :
                texte = texte.replace(key, valeur)
        return texte

    def GetDonnees(self, listeFactures=[], liste_activites=[], date_debut=None, date_fin=None, date_edition=None, date_echeance=None, prestations=["consommation", "cotisation", "autre"], typeLabel=0):
        """ Recherche des factures � cr�er """      
        
        dictFactures = {}
        listeIDfactures = []
        for dictTemp in listeFactures :
            listeIDfactures.append(dictTemp["IDfacture"])
            dictFactures[dictTemp["IDfacture"]] = dictTemp
              
        # Cr�ation des conditions SQL
        if len(liste_activites) == 0 : conditionActivites = "()"
        elif len(liste_activites) == 1 : conditionActivites = "(%d)" % liste_activites[0]
        else : conditionActivites = str(tuple(liste_activites))
        
        if len(listeFactures) == 0 :
            conditionFactures = "IS NULL"
        else:
            if len(listeIDfactures) == 0 : conditionFactures = "()"
            elif len(listeIDfactures) == 1 : conditionFactures = "(%d)" % listeIDfactures[0]
            else : conditionFactures = str(tuple(listeIDfactures))
        
        conditionDates = " prestations.date>='%s' AND prestations.date<='%s' AND IDfacture %s" % (date_debut, date_fin, conditionFactures)
        
        if len(prestations) == 1 :
            conditionPrestations = " prestations.categorie='%s'" % prestations[0]
        else :
            conditionPrestations = " prestations.categorie IN %s" % str(tuple(prestations)).replace("u'", "'")
        
        DB = GestionDB.DB()
        
        # Recherche des prestations de la p�riode
        if len(listeFactures) == 0 :
            conditions = "WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL) AND %s AND %s" % (conditionActivites, conditionDates, conditionPrestations)
        else :
            conditions = "WHERE prestations.IDfacture IN %s" % conditionFactures
        req = """
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, prestations.date, categorie, 
        label, prestations.montant_initial, prestations.montant, prestations.tva, 
        prestations.IDactivite, activites.nom, activites.abrege,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, IDfacture, 
        prestations.IDindividu, prestations.IDfamille
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON tarifs.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % conditions
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()  
        
        # Recherche de la ventilation des prestations
        if len(listeFactures) == 0 :
            conditions = "WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL) AND %s" % (conditionActivites, conditionDates)
        else :
            conditions = "WHERE prestations.IDfacture IN %s" % conditionFactures
        req = """
        SELECT ventilation.IDprestation, SUM(ventilation.montant) AS montant_ventilation
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % conditions
        DB.ExecuterReq(req)
        listeVentilationPrestations = DB.ResultatReq()  
        dictVentilationPrestations = {}
        for IDprestation, montant_ventilation in listeVentilationPrestations :
            dictVentilationPrestations[IDprestation] = montant_ventilation
            
        # Recherche des QF aux dates concern�es
        if len(listeFactures) == 0 :
            conditions = ""
        else :
            date_min = datetime.date(9999, 12, 31)
            date_max = datetime.date(1, 1, 1)
            for IDprestation, IDcompte_payeur, date, categorie, label, montant_initial, montant, tva, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDfamille in listePrestations :
                if dictFactures[IDfacture]["date_debut"] < date_min :
                    date_min = dictFactures[IDfacture]["date_debut"]
                if dictFactures[IDfacture]["date_fin"] > date_max :
                    date_max = dictFactures[IDfacture]["date_fin"]
            conditions = "WHERE quotients.date_fin>='%s' AND quotients.date_debut<='%s' " % (date_min, date_max)
        req = """
        SELECT quotients.IDfamille, quotients.quotient, quotients.date_debut, quotients.date_fin
        FROM quotients
        %s
        ORDER BY quotients.date_debut
        ;""" % conditions
        DB.ExecuterReq(req)
        listeQfdates = DB.ResultatReq()
            
        # Recherche des anciennes prestations impay�es (=le report ant�rieur)
        if len(listeFactures) == 0 :
            conditions = "WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL) AND prestations.date<'%s' " % (conditionActivites, date_debut)
        else :
            conditions = ""
        req = """
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, prestations.date, categorie, 
        label, prestations.montant, 
        prestations.IDactivite, activites.nom, activites.abrege,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, IDfacture, 
        prestations.IDindividu, prestations.IDfamille
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON tarifs.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % conditions
        DB.ExecuterReq(req)
        listeReports = DB.ResultatReq()  
        
        # Recherche de la ventilation des reports
        if len(listeFactures) == 0 :
            conditions = "WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL) AND prestations.date<'%s' " % (conditionActivites, date_debut)
        else :
            conditions = ""
        req = """
        SELECT ventilation.IDprestation, SUM(ventilation.montant) AS montant_ventilation
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        %s 
        GROUP BY prestations.IDprestation
        ;""" % conditions
        DB.ExecuterReq(req)
        listeVentilationReports = DB.ResultatReq()  
        dictVentilationReports = {}
        for IDprestation, montant_ventilation in listeVentilationReports :
            dictVentilationReports[IDprestation] = montant_ventilation

        # Recherche des d�ductions
        if len(listeFactures) == 0 :
            conditions = ""
        else :
            conditions = "WHERE prestations.IDfacture IN %s" % conditionFactures
        req = u"""
        SELECT IDdeduction, deductions.IDprestation, deductions.date, deductions.montant, deductions.label, deductions.IDaide
        FROM deductions
        LEFT JOIN prestations ON prestations.IDprestation = deductions.IDprestation
        %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDeductionsTemp = DB.ResultatReq()  
        dictDeductions = {}
        for IDdeduction, IDprestation, date, montant, label, IDaide in listeDeductionsTemp :
            if dictDeductions.has_key(IDprestation) == False :
                dictDeductions[IDprestation] = []
            dictDeductions[IDprestation].append({"IDdeduction":IDdeduction, "date":date, "montant":montant, "label":label, "IDaide":IDaide})
        
        # Recherche des consommations (sert pour les forfaits)
        if len(listeFactures) == 0 :
            conditions = "WHERE prestations.IDactivite IN %s AND %s" % (conditionActivites, conditionDates)
        else :
            conditions = ""
        req = """
        SELECT IDconso, consommations.date, consommations.IDprestation, consommations.etat
        FROM consommations
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()  
        dictConsommations = {}
        for IDconso, date, IDprestation, etat in listeConsommations :
            if dictConsommations.has_key(IDprestation) == False :
                dictConsommations[IDprestation] = []
            dictConsommations[IDprestation].append({"date" : UTILS_Dates.DateEngEnDateDD(date), "etat" : etat})
            
        DB.Close() 

        # Analyse et regroupement des donn�es
        num_facture = 0
        dictComptes = {}
        dictComptesPayeursFactures = {}
        for IDprestation, IDcompte_payeur, date, categorie, label, montant_initial, montant, tva, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDfamille in listePrestations :
            montant = FloatToDecimal(montant) 
            
            if dictComptesPayeursFactures.has_key(IDcompte_payeur) == False :
                dictComptesPayeursFactures[IDcompte_payeur] = []
            if IDfacture not in dictComptesPayeursFactures[IDcompte_payeur] :
                dictComptesPayeursFactures[IDcompte_payeur].append(IDfacture)
            
            if len(listeFactures) == 0 :
                ID = IDcompte_payeur
            else :
                ID = IDfacture
                date_debut = dictFactures[IDfacture]["date_debut"]
                date_fin = dictFactures[IDfacture]["date_fin"]
                date_edition = dictFactures[IDfacture]["date_edition"]
                date_echeance = dictFactures[IDfacture]["date_echeance"]
            
            # Regroupement par compte payeur
            if dictComptes.has_key(ID) == False and self.dictNomsTitulaires.has_key(IDfamille) :
                
                # Recherche des titulaires
                dictInfosTitulaires = self.dictNomsTitulaires[IDfamille]
                nomsTitulairesAvecCivilite = dictInfosTitulaires["titulairesAvecCivilite"]
                nomsTitulairesSansCivilite = dictInfosTitulaires["titulairesSansCivilite"]
                rue_resid = dictInfosTitulaires["adresse"]["rue"]
                cp_resid = dictInfosTitulaires["adresse"]["cp"]
                ville_resid = dictInfosTitulaires["adresse"]["ville"]
                            
                # M�morisation des infos
                dictComptes[ID] = {
                    
                    "date_debut" : date_debut,
                    "date_fin" : date_fin,
                    "liste_activites" : liste_activites,
                
                    "{FAMILLE_NOM}" : nomsTitulairesAvecCivilite,
                    "nomSansCivilite" : nomsTitulairesSansCivilite,
                    "IDfamille" : IDfamille,
                    "{IDFAMILLE}" : str(IDfamille),
                    "{FAMILLE_RUE}" : rue_resid,
                    "{FAMILLE_CP}" : cp_resid,
                    "{FAMILLE_VILLE}" : ville_resid,
                    "individus" : {},
                    "listePrestations" : [],
                    "listeDeductions" : [],
                    "prestations_familiales" : [],
                    "total" : FloatToDecimal(0.0),
                    "ventilation" : FloatToDecimal(0.0),
                    "solde" : FloatToDecimal(0.0),
                    "qfdates" : {},
                    "reports" : {},
                    "total_reports" : FloatToDecimal(0.0),
                    "{TOTAL_REPORTS}" : u"0.00 %s" % SYMBOLE,
                    "num_facture" : None,
                    "select" : True,
                    "messages_familiaux" : [],
                    "{NOM_LOT}" : "",
                    
                    "date_edition" : date_edition,
                    "{DATE_EDITION_LONG}" : UTILS_Dates.DateComplete(date_edition),
                    "{DATE_EDITION_COURT}" : UTILS_Dates.DateEngFr(str(date_edition)),

                    "numero" : u"Facture n�%06d" % num_facture,
                    "num_facture" : num_facture,
                    "{NUM_FACTURE}" : u"%06d" % num_facture,
                    "{CODEBARRES_NUM_FACTURE}" :"F%06d" % num_facture,

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

                # Ajoute les informations de base famille
                dictComptes[ID].update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))

                # Date �ch�ance
                if date_echeance != None :
                    if date_echeance != None :
                        dictComptes[ID]["date_echeance"] = date_echeance
                        dictComptes[ID]["{DATE_ECHEANCE_LONG}"] = UTILS_Dates.DateComplete(date_echeance)
                        dictComptes[ID]["{DATE_ECHEANCE_COURT}"] = UTILS_Dates.DateEngFr(str(date_echeance)) 
                        dictComptes[ID]["{TEXTE_ECHEANCE}"] = u"Ech�ance du r�glement : %s" % UTILS_Dates.DateEngFr(str(date_echeance)) 
                else:
                    dictComptes[ID]["date_echeance"] = None
                    dictComptes[ID]["{DATE_ECHEANCE_LONG}"] = ""
                    dictComptes[ID]["{DATE_ECHEANCE_COURT}"] = ""
                    dictComptes[ID]["{TEXTE_ECHEANCE}"] = ""

                # Ajoute les r�ponses des questionnaires
                for dictReponse in self.Questionnaires.GetDonnees(IDfamille) :
                    dictComptes[ID][dictReponse["champ"]] = dictReponse["reponse"]
                    if dictReponse["controle"] == "codebarres" :
                        dictComptes[ID]["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]
                
                # Ajoute les messages familiaux
                if self.dictMessageFamiliaux.has_key(IDfamille) :
                    dictComptes[ID]["messages_familiaux"] = self.dictMessageFamiliaux[IDfamille]
                    
                    
            # Insert les montants pour le compte payeur
            if dictVentilationPrestations.has_key(IDprestation) :
                montant_ventilation = FloatToDecimal(dictVentilationPrestations[IDprestation])
            else :
                montant_ventilation = FloatToDecimal(0.0)

            dictComptes[ID]["total"] += montant
            dictComptes[ID]["ventilation"] += montant_ventilation
            dictComptes[ID]["solde"] = dictComptes[ID]["total"] - dictComptes[ID]["ventilation"]
            
            dictComptes[ID]["{TOTAL_PERIODE}"] = u"%.02f %s" % (dictComptes[ID]["total"], SYMBOLE)
            dictComptes[ID]["{TOTAL_REGLE}"] = u"%.02f %s" % (dictComptes[ID]["ventilation"], SYMBOLE)
            dictComptes[ID]["{SOLDE_DU}"] = u"%.02f %s" % (dictComptes[ID]["solde"], SYMBOLE)

            # Ajout d'une prestation familiale
            if IDindividu == None : 
                IDindividu = 0
            if IDactivite == None :
                IDactivite = 0
            
            # Ajout d'un individu
            if dictComptes[ID]["individus"].has_key(IDindividu) == False :
                if self.dictIndividus.has_key(IDindividu) :

                    # Si c'est bien un individu
                    IDcivilite = self.dictIndividus[IDindividu]["IDcivilite"]
                    nomIndividu = self.dictIndividus[IDindividu]["nom"]
                    prenomIndividu = self.dictIndividus[IDindividu]["prenom"]
                    dateNaiss = self.dictIndividus[IDindividu]["date_naiss"]
                    if dateNaiss != None : 
                        if DICT_CIVILITES[IDcivilite]["sexe"] == "M" :
                            texteDateNaiss = u", n� le %s" % UTILS_Dates.DateEngFr(str(dateNaiss))
                        else:
                            texteDateNaiss = u", n�e le %s" % UTILS_Dates.DateEngFr(str(dateNaiss))
                    else:
                        texteDateNaiss = u""
                    texteIndividu = u"<b>%s %s</b><font size=7>%s</font>" % (nomIndividu, prenomIndividu, texteDateNaiss)
                    nom = u"%s %s" % (nomIndividu, prenomIndividu)
                    
                else:
                    # Si c'est pour une prestation familiale on cr�� un individu ID 0 :
                    nom = u"Prestations familiales"
                    texteIndividu = u"<b>%s</b>" % nom
                    
                dictComptes[ID]["individus"][IDindividu] = { "texte" : texteIndividu, "activites" : {}, "total" : FloatToDecimal(0.0), "ventilation" : FloatToDecimal(0.0), "total_reports" : FloatToDecimal(0.0), "nom" : nom, "select" : True }
            
            # Ajout de l'activit�
            if dictComptes[ID]["individus"][IDindividu]["activites"].has_key(IDactivite) == False :
                texteActivite = nomActivite
                agrement = self.RechercheAgrement(IDactivite, date)
                if agrement != None :
                    texteActivite += u" - n� agr�ment : %s" % agrement
                dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite] = { "texte" : texteActivite, "presences" : {} }
            
            # Ajout de la pr�sence
            if dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite]["presences"].has_key(date) == False :
                dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite]["presences"][date] = { "texte" : UTILS_Dates.DateEngFr(str(date)), "unites" : [], "total" : FloatToDecimal(0.0) }

            # Recherche du nbre de dates pour cette prestation
            if dictConsommations.has_key(IDprestation) :
                listeDates = dictConsommations[IDprestation]
            else:
                listeDates = []

            # Recherche des d�ductions
            if dictDeductions.has_key(IDprestation) :
                deductions = dictDeductions[IDprestation]
            else :
                deductions = []

            # M�morisation des d�ductions pour total
            for dictDeduction in deductions :
                dictComptes[ID]["listeDeductions"].append(dictDeduction)

            # Adaptation du label
            if typeLabel == 2 and IDtarif != None :
                label = nomTarif
            if typeLabel == 3 and IDtarif != None :
                label = nomActivite
            if typeLabel == 1 and IDtarif != None :
                if dictConsommations.has_key(IDprestation) :
                    nbreAbsences = 0
                    for dictTemp in dictConsommations[IDprestation] :
                        if dictTemp["etat"] == "absenti" :
                            nbreAbsences += 1
                    # Si toutes les consommations attach�es � la prestation sont sur l'�tat "Absence injustifi�e" :
                    if nbreAbsences == len(dictConsommations[IDprestation]) :
                        label = label + u" (Absence injustifi�e)"

            # M�morisation de la prestation
            dictPrestation = {
                "IDprestation" : IDprestation, "date" : date, "categorie" : categorie, "label" : label,
                "montant_initial" : montant_initial, "montant" : montant, "tva" : tva, 
                "IDtarif" : IDtarif, "nomTarif" : nomTarif, "nomCategorieTarif" : nomCategorieTarif, 
                "montant_ventilation" : montant_ventilation, "listeDatesConso" : listeDates,
                "deductions" : deductions,
                }

            dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["unites"].append(dictPrestation)
            
            # Ajout des totaux
            if montant != None : 
                dictComptes[ID]["individus"][IDindividu]["total"] += montant
                dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["total"] += montant
            if montant_ventilation != None : 
                dictComptes[ID]["individus"][IDindividu]["ventilation"] += montant_ventilation
                        
            # Stockage des IDprestation pour saisir le IDfacture apr�s cr�ation de la facture
            dictComptes[ID]["listePrestations"].append( (IDindividu, IDprestation) )
            
            # Int�gration des qf aux dates concern�es
            for qf_idfamille, quotient, qfdate_debut, qfdate_fin in listeQfdates :
                qfdate_debut = UTILS_Dates.DateEngEnDateDD(qfdate_debut)
                qfdate_fin = UTILS_Dates.DateEngEnDateDD(qfdate_fin)
                if qf_idfamille == IDfamille and qfdate_debut <= date_fin and qfdate_fin >= date_debut :
                    if qfdate_debut < date_debut :
                        plage = "du %s " % UTILS_Dates.DateEngFr(str(date_debut))
                    else :
                        plage = "du %s " % UTILS_Dates.DateEngFr(str(qfdate_debut))
                    if qfdate_fin > date_fin :
                        plage = plage + "au %s" % UTILS_Dates.DateEngFr(str(date_fin))
                    else :
                        plage = plage + "au %s" % UTILS_Dates.DateEngFr(str(qfdate_fin))
                    dictComptes[ID]["qfdates"][plage] = quotient
                
        
        # Int�gration des total des d�ductions
        for ID, valeurs in dictComptes.iteritems() :
            totalDeductions = 0.0
            for dictDeduction in dictComptes[ID]["listeDeductions"] :
                totalDeductions += dictDeduction["montant"]
            dictComptes[ID]["{TOTAL_DEDUCTIONS}"] = u"%.02f %s" % (totalDeductions, SYMBOLE)

        # Int�gration du REPORT des anciennes prestations NON PAYEES
        for IDprestation, IDcompte_payeur, date, categorie, label, montant, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDfamille in listeReports :
            montant = FloatToDecimal(montant) 
            
            if dictVentilationReports.has_key(IDprestation) :
                montant_ventilation = FloatToDecimal(dictVentilationReports[IDprestation])
            else :
                montant_ventilation = FloatToDecimal(0.0)
            
            montant_impaye = montant - montant_ventilation
            date = UTILS_Dates.DateEngEnDateDD(date)
            mois = date.month
            annee = date.year
            periode = (annee, mois)
            
            if montant_ventilation != montant : # Avant c'�tait : montant_ventilation < montant mais j'ai chang� pour le pb des prestations avec montant n�gatif

                if len(listeFactures) == 0 :
                    
                    if dictComptes.has_key(IDcompte_payeur) :
                        if dictComptes[IDcompte_payeur]["reports"].has_key(periode) == False :
                            dictComptes[IDcompte_payeur]["reports"][periode] = FloatToDecimal(0.0)
                        dictComptes[IDcompte_payeur]["reports"][periode] += montant_impaye
                        dictComptes[IDcompte_payeur]["total_reports"] += montant_impaye
                        dictComptes[IDcompte_payeur]["{TOTAL_REPORTS}"] = u"%.02f %s" % (dictComptes[IDcompte_payeur]["total_reports"], SYMBOLE)
                
                else :
                    
                    if dictComptesPayeursFactures.has_key(IDcompte_payeur) :
                        for IDfacture in dictComptesPayeursFactures[IDcompte_payeur] :
                            if date < dictComptes[IDfacture]["date_debut"] :
                                
                                if dictComptes[IDfacture]["reports"].has_key(periode) == False :
                                    dictComptes[IDfacture]["reports"][periode] = FloatToDecimal(0.0)
                                dictComptes[IDfacture]["reports"][periode] += montant_impaye
                                dictComptes[IDfacture]["total_reports"] += montant_impaye
                                dictComptes[IDfacture]["{TOTAL_REPORTS}"] = u"%.02f %s" % (dictComptes[IDfacture]["total_reports"], SYMBOLE)
            
            
        return dictComptes







    def GetDonneesImpression(self, listeFactures=[], dictOptions=None):
        """ Impression des factures """
        dlgAttente = PBI.PyBusyInfo(u"Recherche des donn�es de facturation...", parent=None, title=u"Veuillez patienter...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        try :
            wx.Yield() 
        except :
            pass
        
        # R�cup�re les donn�es de la facture
        if len(listeFactures) == 0 : conditions = "()"
        elif len(listeFactures) == 1 : conditions = "(%d)" % listeFactures[0]
        else : conditions = str(tuple(listeFactures))
        
        DB = GestionDB.DB()
        req = """
        SELECT 
        factures.IDfacture, factures.numero, factures.IDcompte_payeur, factures.activites, factures.individus,
        factures.date_edition, factures.date_echeance, factures.IDutilisateur,
        factures.date_debut, factures.date_fin, factures.total, factures.regle, factures.solde,
        factures.prestations, lots_factures.nom
        FROM factures
        LEFT JOIN lots_factures ON lots_factures.IDlot = factures.IDlot
        WHERE factures.IDfacture IN %s
        GROUP BY factures.IDfacture
        ORDER BY factures.date_edition
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     

        # R�cup�ration des pr�l�vements
        req = """SELECT 
        prelevements.IDprelevement, prelevements.prelevement_numero, prelevements.prelevement_iban,
        prelevements.IDfacture, prelevements.montant, prelevements.statut, 
        comptes_payeurs.IDcompte_payeur, lots_prelevements.date,
        prelevement_reference_mandat, comptes_bancaires.code_ics
        FROM prelevements
        LEFT JOIN lots_prelevements ON lots_prelevements.IDlot = prelevements.IDlot
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = prelevements.IDfamille
        LEFT JOIN comptes_bancaires ON comptes_bancaires.IDcompte = lots_prelevements.IDcompte
        WHERE prelevements.IDfacture IN %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listePrelevements = DB.ResultatReq()
        dictPrelevements = {}
        for IDprelevement, numero_compte, iban, IDfacture, montant, statut, IDcompte_payeur, datePrelevement, rum, code_ics in listePrelevements :
            datePrelevement = UTILS_Dates.DateEngEnDateDD(datePrelevement)
            dictPrelevements[IDfacture] = {
                "IDprelevement" : IDprelevement, "numero_compte" : numero_compte, "montant" : montant, 
                "statut" : statut, "IDcompte_payeur" : IDcompte_payeur, "datePrelevement" : datePrelevement, 
                "iban" : iban, "rum" : rum, "code_ics" : code_ics,
                }
        
        DB.Close() 
        if len(listeDonnees) == 0 : 
            del dlgAttente
            return False
        
        listeFactures = []
        index = 0
        for IDfacture, numero, IDcompte_payeur, activites, individus, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, typesPrestations, nomLot in listeDonnees :
            
            self.EcritStatusbar(u"Recherche de la facture %d sur %d" % (index+1, len(listeDonnees)))
            
            if numero == None : numero = 0
            date_edition = UTILS_Dates.DateEngEnDateDD(date_edition) 
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            date_echeance = UTILS_Dates.DateEngEnDateDD(date_echeance)       

            if typesPrestations != None :
                prestations = typesPrestations.split(";")
            else :
                prestations = ["consommation", "cotisation", "autre"]

            liste_activites = []
            for IDactivite in activites.split(";") :
                liste_activites.append(int(IDactivite))
                
            liste_individus = []
            for IDindividu in individus.split(";") :
                liste_individus.append(int(IDindividu))

            dictFacture = {
                "IDfacture" : IDfacture, "numero" : numero, "IDcompte_payeur" : IDcompte_payeur, "date_edition" : date_edition, "date_echeance" : date_echeance,
                "IDutilisateur" : IDutilisateur, "date_debut" : date_debut, "date_fin" : date_fin, "total" : total, "regle" : regle, "solde" : solde, 
                "activites" : liste_activites, "individus" : liste_individus, "prestations" : prestations,
                }
            listeFactures.append(dictFacture) 
            index +=1
        
        # R�cup�ration des donn�es de facturation
        typeLabel = 0
        if dictOptions != None and dictOptions.has_key("intitules") :
            typeLabel = dictOptions["intitules"]
            
        dictComptes = self.GetDonnees(listeFactures=listeFactures, typeLabel=typeLabel)
        
        dictFactures = {}
        dictChampsFusion = {}
        
        for IDfacture, numero, IDcompte_payeur, activites, individus, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, typesPrestations, nomLot in listeDonnees :
            total = FloatToDecimal(total) 
            regle = FloatToDecimal(regle)
            solde = FloatToDecimal(solde) 
            
            if dictComptes.has_key(IDfacture) :
                
                dictCompte = dictComptes[IDfacture]

                dictCompte["select"] = True
                dictCompte["ventilation"] = regle
                dictCompte["solde"] = solde
                # Attribue un num�ro de facture
                dictCompte["num_facture"] = numero
                dictCompte["num_codeBarre"] = "%07d" % numero
                dictCompte["numero"] = u"Facture n�%07d" % numero
                dictCompte["{NUM_FACTURE}"] = u"%06d" % numero
                dictCompte["{CODEBARRES_NUM_FACTURE}"] = "F%06d" % numero
                dictCompte["{NUMERO_FACTURE}"] = dictCompte["{NUM_FACTURE}"]
                dictCompte["{DATE_DEBUT}"] = UTILS_Dates.DateEngFr(str(date_debut))
                dictCompte["{DATE_FIN}"] = UTILS_Dates.DateEngFr(str(date_fin))
                dictCompte["{DATE_EDITION_FACTURE}"] = UTILS_Dates.DateEngFr(str(date_edition))
                dictCompte["{DATE_ECHEANCE}"] = UTILS_Dates.DateEngFr(str(date_echeance))
                dictCompte["{SOLDE}"] = u"%.2f %s" % (solde, SYMBOLE)
                dictCompte["{SOLDE_LETTRES}"] = UTILS_Conversion.trad(solde, MONNAIE_SINGULIER, MONNAIE_DIVISION).strip().capitalize() 

                if nomLot == None :
                    nomLot = ""
                dictCompte["{NOM_LOT}"] = nomLot
                
                for IDindividu, dictIndividu in dictCompte["individus"].iteritems() :
                    dictIndividu["select"] = True
                
                # Recherche de pr�l�vements
                if dictPrelevements.has_key(IDfacture) :
                    if datePrelevement < dictCompte["date_edition"] :
                        verbe = u"a �t�"
                    else :
                        verbe = u"sera"
                    montant = dictPrelevements[IDfacture]["montant"]
                    datePrelevement = dictPrelevements[IDfacture]["datePrelevement"]
                    iban = dictPrelevements[IDfacture]["iban"]
                    rum = dictPrelevements[IDfacture]["rum"]
                    code_ics = dictPrelevements[IDfacture]["code_ics"]
                    if iban != None :
                        dictCompte["prelevement"] = u"La somme de %.2f %s %s pr�lev�e le %s sur le compte ***%s" % (montant, SYMBOLE, verbe, UTILS_Dates.DateEngFr(str(datePrelevement)), iban[-7:])
                    else :
                        dictCompte["prelevement"] = u"La somme de %.2f %s %s pr�lev�e le %s" % (montant, SYMBOLE, verbe, UTILS_Dates.DateEngFr(str(datePrelevement)))
                    if rum != None :
                        dictCompte["prelevement"] += u"<br/>R�f. mandat unique : %s / Code ICS : %s" % (rum, code_ics)
                else :
                    dictCompte["prelevement"] = None

                # Champs de fusion pour Email
                dictChampsFusion[IDfacture] = {}
                dictChampsFusion[IDfacture]["{NUMERO_FACTURE}"] = dictCompte["{NUM_FACTURE}"]
                dictChampsFusion[IDfacture]["{DATE_DEBUT}"] = UTILS_Dates.DateEngFr(str(date_debut))
                dictChampsFusion[IDfacture]["{DATE_FIN}"] = UTILS_Dates.DateEngFr(str(date_fin))
                dictChampsFusion[IDfacture]["{DATE_EDITION_FACTURE}"] = UTILS_Dates.DateEngFr(str(date_edition))
                dictChampsFusion[IDfacture]["{DATE_ECHEANCE}"] = UTILS_Dates.DateEngFr(str(date_echeance))
                dictChampsFusion[IDfacture]["{SOLDE}"] = u"%.2f %s" % (solde, SYMBOLE)
                
                # Fusion pour textes personnalis�s
                dictCompte["texte_titre"] = self.RemplaceMotsCles(dictOptions["texte_titre"], dictCompte)
                dictCompte["texte_introduction"] = self.RemplaceMotsCles(dictOptions["texte_introduction"], dictCompte)
                dictCompte["texte_conclusion"] = self.RemplaceMotsCles(dictOptions["texte_conclusion"], dictCompte)
                
                # M�morisation de la facture
                dictFactures[IDfacture] = dictCompte
            
            index += 1
        
        del dlgAttente      
        self.EcritStatusbar("")   
        
        if len(dictFactures) == 0 :
            return False
           
        return dictFactures, dictChampsFusion




    def Impression(self, listeFactures=[], nomDoc=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False):
        """ Impression des factures """
        # R�cup�ration des param�tres d'affichage
        if dictOptions == None :
            if afficherDoc == False :
                dlg = DLG_Apercu_facture.Dialog(None, titre=u"S�lection des param�tres de la facture", intro=u"S�lectionnez ici les param�tres d'affichage de la facture � envoyer par Email.")
                dlg.bouton_ok.SetBitmapLabel(wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
            else :
                dlg = DLG_Apercu_facture.Dialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                dictOptions = dlg.GetParametres()
                dlg.Destroy()
            else :
                dlg.Destroy()
                return False

        # R�cup�ration des donn�es � partir des IDfacture
        resultat = self.GetDonneesImpression(listeFactures, dictOptions)
        if resultat == False :
            return False
        dictFactures, dictChampsFusion = resultat
                
        # Cr�ation des PDF � l'unit�
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgAttente = PBI.PyBusyInfo(u"G�n�ration des factures � l'unit� au format PDF...", parent=None, title=u"Veuillez patienter...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            try :
                wx.Yield() 
            except :
                pass
            try :
                index = 0
                for IDfacture, dictFacture in dictFactures.iteritems() :
                    if dictFacture["select"] == True :
                        num_facture = dictFacture["num_facture"]
                        nomTitulaires = self.Supprime_accent(dictFacture["nomSansCivilite"])
                        nomFichier = u"Facture %d - %s" % (num_facture, nomTitulaires)
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDfacture : dictFacture}
                        self.EcritStatusbar(u"Edition de la facture %d/%d : %s" % (index, len(dictFactures), nomFichier))
                        UTILS_Impression_facture.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDfacture] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                del dlgAttente
                return dictPieces
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, u"D�sol�, le probl�me suivant a �t� rencontr� dans l'�dition des factures : \n\n%s" % err, u"Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # R�pertoire souhait� par l'utilisateur
        if repertoire not in (None, "") :
            resultat = CreationPDFunique(repertoire)
            if resultat == False :
                return False

        # R�pertoire TEMP (pour Emails)
        dictPieces = {}
        if repertoireTemp == True :
            dictPieces = CreationPDFunique("Temp")
            if dictPieces == False :
                return False

        # Fabrication du PDF global
        if repertoireTemp == False :
            dlgAttente = PBI.PyBusyInfo(u"Cr�ation du PDF des factures...", parent=None, title=u"Veuillez patienter...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            try :
                wx.Yield() 
            except :
                pass
            self.EcritStatusbar(u"Cr�ation du PDF des factures en cours... veuillez patienter...")
            try :
                UTILS_Impression_facture.Impression(dictFactures, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                err = str(err).decode("iso-8859-15")
                dlg = wx.MessageDialog(None, u"D�sol�, le probl�me suivant a �t� rencontr� dans l'�dition des factures : \n\n%s" % err, u"Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces






def SuppressionFacture(listeFactures=[]):
    """ Suppression d'une facture """
    dlgAttente = PBI.PyBusyInfo(u"Suppression des factures en cours...", parent=None, title=u"Veuillez patienter...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
    wx.Yield() 
    DB = GestionDB.DB()
    for IDfacture in listeFactures :
        DB.ReqMAJ("prestations", [("IDfacture", None ),], "IDfacture", IDfacture)
        DB.ReqDEL("factures", "IDfacture", IDfacture)
    DB.Close() 
    del dlgAttente
    return True
        



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    # Test du module Facturation :
    facturation = Facturation() 
##    print facturation.GetDonnees(IDfacture=None, liste_activites=[], date_debut=datetime.date(2013, 1, 1), date_fin=datetime.date(2013, 12, 31), date_edition=datetime.date.today(), date_echeance=datetime.date(2013, 2, 28), prestations=["consommation", "cotisation", "autre"] )
##    print facturation.Impression(listeFactures=[92, 93], nomDoc=None, afficherDoc=True, dictOptions=None)
##    print len(facturation.GetDonnees2(listeFactures=range(3240, 3400)))
##    facturation.GetDonneesImpression2(listeFactures=range(3240, 3400))
    print "resultats =", facturation.Impression(listeFactures=[77,])
    app.MainLoop()
