#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED
import datetime
import copy
import sys
import wx.lib.agw.pybusyinfo as PBI
from Utils import UTILS_Organisateur
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import GestionDB
from Data import DATA_Civilites as Civilites
import CTRL_Saisie_euros
import FonctionsPerso
import CTRL_Attestations_options

from Utils import UTILS_Titulaires
from Utils import UTILS_Utilisateurs
DICT_CIVILITES = Civilites.GetDictCivilites()

from Utils import UTILS_Infos_individus



COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)
            
def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    if dateDD == None : return u""
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete


# -------------------------------------------------------------------------------------------------------------------------------------------------

def Importation(liste_activites=[], date_debut=None, date_fin=None, date_edition=None, dateNaiss=None, listePrestations=[], typeLabel="original"):
    """ Recherche des attestations à créer """        
    # Conditions
    if len(liste_activites) == 0 : conditionActivites = "()"
    elif len(liste_activites) == 1 : conditionActivites = "(%d)" % liste_activites[0]
    else : conditionActivites = str(tuple(liste_activites))
    
    conditionDates = " prestations.date>='%s' AND prestations.date<='%s' " % (date_debut, date_fin)
    
    # Condition date Naissance
    if dateNaiss != None :
        conditionDateNaiss = "AND individus.date_naiss >= '%s' " % dateNaiss
    else:
        conditionDateNaiss = ""

    DB = GestionDB.DB()
    
    # Récupération de tous les individus de la base
    req = """
    SELECT IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid
    FROM individus
    ;""" 
    DB.ExecuterReq(req)
    listeIndividus = DB.ResultatReq()  
    dictIndividus = {}
    for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid in listeIndividus :
        dictIndividus[IDindividu] = {"IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":date_naiss, "adresse_auto":adresse_auto, "rue_resid":rue_resid, "cp_resid":cp_resid, "ville_resid":ville_resid}
    
    # Recherche des prestations de la période
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
    LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
    WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL)
    AND %s
    %s
    GROUP BY prestations.IDprestation
    ORDER BY prestations.date
    ;""" % (conditionActivites, conditionDates, conditionDateNaiss)
    DB.ExecuterReq(req)
    listePrestationsTemp = DB.ResultatReq()  

    # Récupération de la ventilation
    req = """
    SELECT prestations.IDprestation, SUM(ventilation.montant)
    FROM ventilation
    LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
    LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
    LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
    WHERE (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL)
    AND %s
    %s
    GROUP BY prestations.IDprestation
    ;""" % (conditionActivites, conditionDates, conditionDateNaiss)
    DB.ExecuterReq(req)
    listeVentilation = DB.ResultatReq()  
    dictVentilation = {}
    for IDprestation, totalVentilation in listeVentilation :
        dictVentilation[IDprestation] = totalVentilation

    # Recherche des déductions
    req = u"""
    SELECT IDdeduction, IDprestation, date, montant, label, IDaide
    FROM deductions
    LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = deductions.IDcompte_payeur
    ;"""
    DB.ExecuterReq(req)
    listeDeductionsTemp = DB.ResultatReq()  
    dictDeductions = {}
    for IDdeduction, IDprestation, date, montant, label, IDaide in listeDeductionsTemp :
        if dictDeductions.has_key(IDprestation) == False :
            dictDeductions[IDprestation] = []
        dictDeductions[IDprestation].append({"IDdeduction":IDdeduction, "date":date, "montant":montant, "label":label, "IDaide":IDaide})

    # Recherche des consommations (sert pour les forfaits)
    req = """
    SELECT IDconso, consommations.date, consommations.IDprestation
    FROM consommations
    LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
    WHERE prestations.IDactivite IN %s
    AND %s
    ;""" % (conditionActivites, conditionDates)
    DB.ExecuterReq(req)
    listeConsommations = DB.ResultatReq()  
    dictConsommations = {}
    for IDconso, date, IDprestation in listeConsommations :
        date = DateEngEnDateDD(date)
        if dictConsommations.has_key(IDprestation) == False :
            dictConsommations[IDprestation] = []
        if date not in dictConsommations[IDprestation] :
            dictConsommations[IDprestation].append(date)
    
    # Recherche des numéros d'agréments
    req = """
    SELECT IDactivite, agrement, date_debut, date_fin
    FROM agrements
    WHERE IDactivite IN %s
    ORDER BY date_debut
    """ % conditionActivites
    DB.ExecuterReq(req)
    listeAgrements = DB.ResultatReq()  
            
    # Récupération des infos sur l'organisme
    req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape
    FROM organisateur
    WHERE IDorganisateur=1;""" 
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()      
    dictOrganisme = {}
    for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees :
        dictOrganisme["nom"] = nom
        dictOrganisme["rue"] = rue
        dictOrganisme["cp"] = cp
        if ville != None : ville = ville.capitalize()
        dictOrganisme["ville"] = ville
        dictOrganisme["tel"] = tel
        dictOrganisme["fax"] = fax
        dictOrganisme["mail"] = mail
        dictOrganisme["site"] = site
        dictOrganisme["num_agrement"] = num_agrement
        dictOrganisme["num_siret"] = num_siret
        dictOrganisme["code_ape"] = code_ape
    
    # Get noms Titulaires
    dictNomsTitulaires = UTILS_Titulaires.GetTitulaires() 
        
    DB.Close() 
    
    # Analyse et regroupement des données
    def isPrestationSelection(label, IDactivite):
        for track in listePrestations :
            if label == track["label"] and IDactivite == track["IDactivite"] :
                return True
        return False
    
    # Récupération des infos de base individus et familles
    infosIndividus = UTILS_Infos_individus.Informations() 

    dictComptes = {}
    for IDprestation, IDcompte_payeur, date, categorie, label, montant_initial, montant, tva, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDfamille in listePrestationsTemp :
        montant_initial = FloatToDecimal(montant_initial) 
        montant = FloatToDecimal(montant)
        
        if isPrestationSelection(label, IDactivite) == True :
            
            # Regroupement par compte payeur
            if dictComptes.has_key(IDcompte_payeur) == False :
                
                # Recherche des titulaires
                dictInfosTitulaires = dictNomsTitulaires[IDfamille]
                nomsTitulairesAvecCivilite = dictInfosTitulaires["titulairesAvecCivilite"]
                nomsTitulairesSansCivilite = dictInfosTitulaires["titulairesSansCivilite"]
                rue_resid = dictInfosTitulaires["adresse"]["rue"]
                cp_resid = dictInfosTitulaires["adresse"]["cp"]
                ville_resid = dictInfosTitulaires["adresse"]["ville"]
                
                if cp_resid == None : cp_resid = u""
                if ville_resid == None : ville_resid = u""
                destinataire_ville = u"%s %s" % (cp_resid, ville_resid)
                
                # Mémorisation des infos
                dictComptes[IDcompte_payeur] = {
                    "{FAMILLE_NOM}" : nomsTitulairesAvecCivilite,
                    "{DESTINATAIRE_NOM}" : nomsTitulairesAvecCivilite,
                    "nomSansCivilite" : nomsTitulairesSansCivilite,
                    "IDfamille" : IDfamille,
                    "{IDFAMILLE}" : str(IDfamille),
                    "{FAMILLE_RUE}" : rue_resid,
                    "{FAMILLE_CP}" : cp_resid,
                    "{FAMILLE_VILLE}" : ville_resid,
                    "{DESTINATAIRE_RUE}" : rue_resid,
                    "{DESTINATAIRE_CP}" : cp_resid,
                    "{DESTINATAIRE_VILLE}" : destinataire_ville,
                    "individus" : {},
                    "listeNomsIndividus" : [],
                    "listePrestations" : [],
                    "prestations_familiales" : [],
                    "total" : FloatToDecimal(0.0),
                    "ventilation" : FloatToDecimal(0.0),
                    "solde" : FloatToDecimal(0.0),
                    "num_attestation" : None,
                    "select" : True,
                    "intro" : "",
                    "date_debut" : date_debut,
                    "date_fin" : date_fin,

                    "{DATE_DEBUT}" : DateEngFr(str(date_debut)),
                    "{DATE_FIN}" : DateEngFr(str(date_fin)),

                    "{DATE_EDITION_LONG}" : DateComplete(date_edition),
                    "{DATE_EDITION_COURT}" : DateEngFr(str(date_edition)),
                    "{DATE_EDITION}" : DateEngFr(str(date_edition)),
                    
                    "{ORGANISATEUR_NOM}" : dictOrganisme["nom"],
                    "{ORGANISATEUR_RUE}" : dictOrganisme["rue"],
                    "{ORGANISATEUR_CP}" : dictOrganisme["cp"],
                    "{ORGANISATEUR_VILLE}" : dictOrganisme["ville"],
                    "{ORGANISATEUR_TEL}" : dictOrganisme["tel"],
                    "{ORGANISATEUR_FAX}" : dictOrganisme["fax"],
                    "{ORGANISATEUR_MAIL}" : dictOrganisme["mail"],
                    "{ORGANISATEUR_SITE}" : dictOrganisme["site"],
                    "{ORGANISATEUR_AGREMENT}" : dictOrganisme["num_agrement"],
                    "{ORGANISATEUR_SIRET}" : dictOrganisme["num_siret"],
                    "{ORGANISATEUR_APE}" : dictOrganisme["code_ape"],
                    }

                dictComptes[IDcompte_payeur].update(infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))

            # Insert les montants pour le compte payeur
            if dictVentilation.has_key(IDprestation) :
                montant_ventilation = FloatToDecimal(dictVentilation[IDprestation])
            else :
                montant_ventilation = FloatToDecimal(0.0)

            dictComptes[IDcompte_payeur]["total"] += montant
            dictComptes[IDcompte_payeur]["ventilation"] += montant_ventilation
            dictComptes[IDcompte_payeur]["solde"] = dictComptes[IDcompte_payeur]["total"] - dictComptes[IDcompte_payeur]["ventilation"]
            
            dictComptes[IDcompte_payeur]["{TOTAL_PERIODE}"] = u"%.02f %s" % (dictComptes[IDcompte_payeur]["total"], SYMBOLE)
            dictComptes[IDcompte_payeur]["{TOTAL_REGLE}"] = u"%.02f %s" % (dictComptes[IDcompte_payeur]["ventilation"], SYMBOLE)
            dictComptes[IDcompte_payeur]["{SOLDE_DU}"] = u"%.02f %s" % (dictComptes[IDcompte_payeur]["solde"], SYMBOLE)


            # Ajout d'une prestation familiale
            if IDindividu == None : 
                IDindividu = 0
            if IDactivite == None :
                IDactivite = 0
            
            # Ajout d'un individu
            if dictComptes[IDcompte_payeur]["individus"].has_key(IDindividu) == False :
                if dictIndividus.has_key(IDindividu) :
                    
                    # Si c'est bien un individu
                    IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                    nomIndividu = dictIndividus[IDindividu]["nom"]
                    prenomIndividu = dictIndividus[IDindividu]["prenom"]
                    dateNaiss = dictIndividus[IDindividu]["date_naiss"]
                    if dateNaiss != None : 
                        if DICT_CIVILITES[IDcivilite]["sexe"] == "M" :
                            texteDateNaiss = _(u", né le %s") % DateEngFr(str(dateNaiss))
                        else:
                            texteDateNaiss = _(u", née le %s") % DateEngFr(str(dateNaiss))
                    else:
                        texteDateNaiss = u""
                    texteIndividu = _(u"<b>%s %s</b><font size=7>%s</font>") % (nomIndividu, prenomIndividu, texteDateNaiss)
                    nom = u"%s %s" % (nomIndividu, prenomIndividu)
                    
                    # créé le texte complet des noms des individus pour l'intro de l'attestation
                    dictComptes[IDcompte_payeur]["listeNomsIndividus"].append(u"%s %s" % (prenomIndividu, nomIndividu))
                    
                else:
                    # Si c'est pour une prestation familiale on créé un individu ID 0 :
                    nom = _(u"Prestations familiales")
                    texteIndividu = u"<b>%s</b>" % nom
                    
                dictComptes[IDcompte_payeur]["individus"][IDindividu] = { "texte" : texteIndividu, "activites" : {}, "total" : FloatToDecimal(0.0), "ventilation" : FloatToDecimal(0.0), "total_reports" : FloatToDecimal(0.0), "nom" : nom, "select" : True }
            
            # Ajout de l'activité
            if dictComptes[IDcompte_payeur]["individus"][IDindividu]["activites"].has_key(IDactivite) == False :
                texteActivite = nomActivite
                agrement = RechercheAgrement(listeAgrements, IDactivite, date)
                if agrement != None :
                    texteActivite += _(u" - n° agrément : %s") % agrement
                dictComptes[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite] = { "texte" : texteActivite, "presences" : {} }
            
            # Ajout de la présence
            if dictComptes[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"].has_key(date) == False :
                dictComptes[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date] = { "texte" : DateEngFr(str(date)), "unites" : [], "total" : FloatToDecimal(0.0) }
            
            # Recherche du nbre de dates pour cette prestation
            if dictConsommations.has_key(IDprestation) :
                listeDates = dictConsommations[IDprestation]
            else:
                listeDates = []

            # Recherche des déductions
            if dictDeductions.has_key(IDprestation) :
                deductions = dictDeductions[IDprestation]
            else :
                deductions = []

            # Adaptation du label
            if typeLabel == 2 :
                label = nomTarif
            if typeLabel == 3 :
                label = nomActivite

            # Mémorisation de la prestation
            dictPrestation = {
                "IDprestation" : IDprestation, "date" : date, "categorie" : categorie, "label" : label,
                "montant_initial" : montant_initial, "montant" : montant, "tva" : tva, 
                "IDtarif" : IDtarif, "nomTarif" : nomTarif, "nomCategorieTarif" : nomCategorieTarif, 
                "montant_ventilation" : montant_ventilation, "listeDatesConso" : listeDates,
                "deductions" : deductions,
                }

            dictComptes[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["unites"].append(dictPrestation)
            
            # Ajout des totaux
            if montant != None : 
                dictComptes[IDcompte_payeur]["individus"][IDindividu]["total"] += montant
                dictComptes[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["total"] += montant
            if montant_ventilation != None : 
                dictComptes[IDcompte_payeur]["individus"][IDindividu]["ventilation"] += montant_ventilation
            
            # Stockage des IDprestation pour saisir le IDfacture après création de la facture
            dictComptes[IDcompte_payeur]["listePrestations"].append( (IDindividu, IDprestation) )
    
    return dictComptes

def RechercheAgrement(listeAgrements, IDactivite, date):
    for IDactiviteTmp, agrement, date_debut, date_fin in listeAgrements :
        if IDactivite == IDactiviteTmp and date >= date_debut and date <= date_fin :
            return agrement
    return None


# ---------------------------------------------------------------------------------------------------------------------------------------------------

            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, date_debut=None, date_fin=None, dateNaiss=None, listeActivites=[], listePrestations=[], typeLabel=0): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.dateNaiss = dateNaiss
        self.listeActivites = listeActivites
        self.listePrestations = listePrestations
        self.typeLabel = typeLabel
        
        # Création des colonnes
        listeColonnes = [
            ( _(u"Famille/Individu"), 270, wx.ALIGN_LEFT),
            ( _(u"Total"), 80, wx.ALIGN_RIGHT),
            ( _(u"Réglé"), 80, wx.ALIGN_RIGHT),
            ( _(u"Solde"), 80, wx.ALIGN_RIGHT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(TR_COLUMN_LINES | wx.TR_HAS_BUTTONS |wx.TR_HIDE_ROOT  | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT | HTL.TR_AUTO_CHECK_CHILD | HTL.TR_AUTO_CHECK_PARENT) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu) 
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
        
    def AfficheNbreComptes(self, nbreComptes=0):
        if self.parent.GetName() == "DLG_Attestations_selection" :
            if nbreComptes == 0 : label = _(u"Aucune attestation sélectionnée")
            elif nbreComptes == 1 : label = _(u"1 attestation sélectionnée")
            else: label = _(u"%d attestations sélectionnées") % nbreComptes
            self.parent.staticbox_attestations_staticbox.SetLabel(label)
        
    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            if self.GetPyData(item)["type"] == "individu" :
                # Récupère les données sur le compte payeur
                itemParent = self.GetItemParent(item)
                IDcompte_payeur = self.GetPyData(itemParent)["valeur"]
                compte_total = self.dictComptes[IDcompte_payeur]["total"]
                compte_ventilation = self.dictComptes[IDcompte_payeur]["ventilation"]
                # Récupère les données sur l'individu
                IDindividu = self.GetPyData(item)["valeur"]
                individu_total = self.dictComptes[IDcompte_payeur]["individus"][IDindividu]["total"]
                individu_ventilation = self.dictComptes[IDcompte_payeur]["individus"][IDindividu]["ventilation"]
                
            self.AfficheNbreComptes(len(self.GetCoches()))
                
    def CocheTout(self):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            self.CheckItem(item, True)
        self.MAJenCours = False
        self.AfficheNbreComptes(len(self.GetCoches()))

    def DecocheTout(self):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            self.CheckItem(item, False)
        self.MAJenCours = False
        self.AfficheNbreComptes(len(self.GetCoches()))
    
    def SelectPayes(self):
        """ Sélectionne uniquement les familles avec un compte créditeur """
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            if self.GetPyData(item)["type"] == "compte" :
                IDcompte_payeur = self.GetPyData(item)["valeur"]
                total = self.dictComptes[IDcompte_payeur]["total"]
                ventilation = self.dictComptes[IDcompte_payeur]["ventilation"]
                solde = total - ventilation
                if solde <= 0.0 :
                    self.CheckItem(item, True)
                else:
                    self.CheckItem(item, False)
        self.MAJenCours = False
        self.AfficheNbreComptes(len(self.GetCoches()))
        
    def GetCoches(self):
        dictCoches = {}
        # Parcours des items COMPTE
        parent = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            parent = self.GetNext(parent) 
            if self.IsItemChecked(parent) :
                IDcompte_payeur = self.GetPyData(parent)["valeur"]
                # Parcours des items INDIVIDUS
                listeIDindividus = []
                item, cookie = self.GetFirstChild(parent)
                for index in range(0, self.GetChildrenCount(parent)):
                    if self.IsItemChecked(item) or 1 == 1 : # <<<<<<<<<<<< ICI j'ai désactivé la recherche des individus COCHES
                        IDindividu = self.GetPyData(item)["valeur"]
                        listeIDindividus.append(IDindividu)
                    item = self.GetNext(item) 
                if len(listeIDindividus) > 0 :
                    # Mémorisation de la famille et des individus cochés
                    dictCoches[IDcompte_payeur] = listeIDindividus
        return dictCoches

    def GetDonnees(self, dictOptions={}, infosSignataire={}):
        """ Crée la liste finale des données pour l'impression """
        dictCoches = self.GetCoches() 
        # Recherche numéro d'attestation suivant
        DB = GestionDB.DB()
        req = """SELECT MAX(numero) FROM attestations;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()  
        DB.Close() 
        if listeDonnees[0][0] == None :
            num_attestation = 1
        else:
            num_attestation = listeDonnees[0][0] + 1
        for IDcompte_payeur, dictCompte in self.dictComptes.iteritems() :
            if dictCoches.has_key(IDcompte_payeur) :
                dictCompte["select"] = True
                # Attribue un numéro de facture
                dictCompte["numero"] = _(u"Attestation n°%06d") % num_attestation
                dictCompte["num_attestation"] = num_attestation
                dictCompte["{NUM_ATTESTATION}"] = u"%06d" % num_attestation
                dictCompte["{CODEBARRES_NUM_ATTESTATION}"] = "F%06d" % num_attestation
                num_attestation += 1 

                # Fusion pour textes personnalisés
                listeNoms = dictCompte["listeNomsIndividus"]
                texteNoms = u""
                nbreIndividus = len(listeNoms)
                if nbreIndividus == 0 : texteNoms = u""
                if nbreIndividus == 1 : texteNoms = listeNoms[0]
                if nbreIndividus == 2 : texteNoms = _(u"%s et %s") % (listeNoms[0], listeNoms[1])
                if nbreIndividus > 2 :
                    for texteNom in listeNoms[:-2] :
                        texteNoms += u"%s, " % texteNom
                    texteNoms += _(u"%s et %s") % (listeNoms[-2], listeNoms[-1])
                dictCompte["{NOMS_INDIVIDUS}"] = texteNoms
    
                dictCompte["{SIGNATAIRE_NOM}"] = infosSignataire["nom"]
                dictCompte["{SIGNATAIRE_FONCTION}"] = infosSignataire["fonction"]
                if infosSignataire["sexe"] == "H" :
                    dictCompte["{SIGNATAIRE_GENRE}"] = u""
                else:
                    dictCompte["{SIGNATAIRE_GENRE}"] = u"e"

                dictCompte["texte_titre"] = CTRL_Attestations_options.RemplaceMotsCles(dictOptions["texte_titre"], dictCompte)
                dictCompte["texte_introduction"] = CTRL_Attestations_options.RemplaceMotsCles(dictOptions["texte_introduction"], dictCompte)
                dictCompte["texte_conclusion"] = CTRL_Attestations_options.RemplaceMotsCles(dictOptions["texte_conclusion"], dictCompte)

                # Sélectionne uniquement les individus cochés dans la liste
                for IDindividu, dictIndividu in dictCompte["individus"].iteritems() :
                    if IDindividu in dictCoches[IDcompte_payeur] :
                        dictIndividu["select"] = True
                    else:
                        dictIndividu["select"] = False
            else:
                dictCompte["select"] = False
        return self.dictComptes

    def GetListeComptes(self):
        return self.dictComptes.keys() 
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.CocheTout() 

    def Remplissage(self):
        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des prestations en cours..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        try :
            wx.Yield() 
        except :
            pass
        
        self.dictComptes = Importation(   liste_activites=self.listeActivites,
                                                        date_debut=self.date_debut, 
                                                        date_fin=self.date_fin, 
                                                        date_edition=datetime.date.today(),
                                                        dateNaiss = self.dateNaiss,
                                                        listePrestations=self.listePrestations,
                                                        typeLabel=self.typeLabel,
                                                        )
        
        del dlgAttente
    
        # Branches COMPTE
        listeNomsSansCivilite = []
        for IDcompte_payeur, dictCompte in self.dictComptes.iteritems() :
            listeNomsSansCivilite.append((dictCompte["nomSansCivilite"], IDcompte_payeur))
        listeNomsSansCivilite.sort() 
        
        for nomSansCivilite, IDcompte_payeur in listeNomsSansCivilite :
            dictCompte = self.dictComptes[IDcompte_payeur]
            IDfamille = dictCompte["IDfamille"]
            total = dictCompte["total"]
            ventilation = dictCompte["ventilation"]
                        
            niveauCompte = self.AppendItem(self.root, nomSansCivilite, ct_type=1)
            self.SetPyData(niveauCompte, {"type" : "compte", "valeur" : IDcompte_payeur, "IDfamille" : IDfamille, "nom" : nomSansCivilite})
            
            self.SetItemText(niveauCompte, u"%.02f %s" % (total, SYMBOLE), 1)
            self.SetItemText(niveauCompte, u"%.02f %s" % (ventilation, SYMBOLE), 2)
            self.SetItemText(niveauCompte, u"%.02f %s" % (total-ventilation, SYMBOLE), 3)
            
            # Branches INDIVIDUS
            listeIndividus = []
            for IDindividu, dictIndividu in dictCompte["individus"].iteritems() :
                nomIndividu = dictIndividu["nom"]
                listeIndividus.append((nomIndividu, IDindividu))
            listeIndividus.sort() 
            
            for nomIndividu, IDindividu in listeIndividus :
                dictIndividu = dictCompte["individus"][IDindividu]
                total = dictIndividu["total"]
                ventilation = dictIndividu["ventilation"]
                            
                niveauIndividu = self.AppendItem(niveauCompte, nomIndividu)#, ct_type=1)
                self.SetPyData(niveauIndividu, {"type" : "individu", "valeur" : IDindividu, "dictIndividu" : dictIndividu})
                
                self.SetItemText(niveauIndividu, u"%.02f %s" % (total, SYMBOLE), 1)
                self.SetItemText(niveauIndividu, u"%.02f %s" % (ventilation, SYMBOLE), 2)
                self.SetItemText(niveauIndividu, u"%.02f %s" % (total-ventilation, SYMBOLE), 3)
                
                
        
        #self.ExpandAllChildren(self.root)
    
    def OnCompareItems(self, item1, item2):
        if self.GetPyData(item1) > self.GetPyData(item2) :
            return 1
        elif self.GetPyData(item1) < self.GetPyData(item2) :
            return -1
        else:
            return 0
                        
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        if type != "compte" : return
        nomIndividu = dictItem["nom"]
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille de %s") % nomIndividu)
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        type = dictItem["type"]
        if type != "compte" : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = dictItem["IDfamille"]
        
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ() 
        
    def ImpressionListe(self):
        """ Imprime la liste des comptes sélectionnés """
        # Récupère les noms des colonnes
        listeColonnes = []
        for numColonne in range(0, self.GetColumnCount()) :
            labelColonne = self.GetColumnText(numColonne)
            largeurColonne = self.GetColumnWidth(numColonne)
            listeColonnes.append((labelColonne, largeurColonne / 1.3 ))
        # Récupère les lignes du tableau
        listeLignes = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            ligne = []
            item = self.GetNext(item) 
            if self.GetPyData(item)["type"] == "compte" and self.IsItemChecked(item) :
                for numColonne in range(0, self.GetColumnCount()) :
                    texte = item.GetText(numColonne)
                    ligne.append(texte)
                listeLignes.append(ligne)
        
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Initialisation du PDF
        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_ATTESTATIONS", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = 520
        
        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (420, 100) )
            dateDuJour = DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Liste des attestations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                    ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                    ('ALIGN', (0,0), (0,0), 'LEFT'), 
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                    ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                    ('FONT',(1,0),(1,0), "Helvetica", 6), 
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0,20))       
        
        # Insère un header
        Header() 
        
        # Noms de colonnes
        dataTableau = []
        largeursColonnes = []
        
        ligne = []
        for labelColonne, largeurColonne in listeColonnes :
            ligne.append(labelColonne)
            largeursColonnes.append(largeurColonne)
        dataTableau.append(ligne)
        
        # Création des lignes
        for ligne in listeLignes :
            dataTableau.append(ligne)
        
        couleurFond = (0.9, 0.9, 0.9) 
        listeStyles = [
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                
                ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Centre les cases
                
                ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                
                ]
                
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        # Données pour les tests
        date_debut = datetime.date(2012, 1, 1)
        date_fin = datetime.date(2012, 12, 31)
        liste_activites = [1,]
        
        self.myOlv = CTRL(panel)
        self.myOlv.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
