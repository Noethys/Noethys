#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import datetime
import six
import sys
import traceback
from Utils import UTILS_Conversion
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
MONNAIE_SINGULIER = UTILS_Config.GetParametre("monnaie_singulier", _(u"Euro"))
MONNAIE_DIVISION = UTILS_Config.GetParametre("monnaie_division", _(u"Centime"))

from Data import DATA_Codes_etab
from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Utils import UTILS_Impression_facture
from Utils import UTILS_Dates
from Dlg import DLG_Apercu_facture
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Infos_individus
from Utils import UTILS_Fichiers
from Utils import UTILS_Texte
from Utils.UTILS_Pes import GetCle_modulo23


def FormateMaj(nom_titulaires):
    """ Formate nom de fichier en majuscules et sans caractères spéciaux """
    nom_titulaires = UTILS_Texte.Supprime_accent(nom_titulaires)
    resultat = ""
    for caract in nom_titulaires :
        if caract in " abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" :
            resultat += caract.upper()
    resultat = resultat.replace(" ", "_")
    return resultat


class Facturation():
    def __init__(self):
        """ Récupération de toutes les données de base """
        
        DB = GestionDB.DB()
            
        # Récupération de tous les individus de la base
        req = """SELECT IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid
        FROM individus;""" 
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()  
        self.dictIndividus = {}
        for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid in listeIndividus :
            self.dictIndividus[IDindividu] = {"IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":date_naiss, "adresse_auto":adresse_auto, "rue_resid":rue_resid, "cp_resid":cp_resid, "ville_resid":ville_resid}

        # Récupération de tous les messages familiaux à afficher
        req = """SELECT IDmessage, IDcategorie, date_parution, priorite, IDfamille, nom, texte
        FROM messages
        WHERE afficher_facture=1 AND IDfamille IS NOT NULL;"""
        DB.ExecuterReq(req)
        listeMessagesFamiliaux = DB.ResultatReq()  
        self.dictMessageFamiliaux = {}
        for IDmessage, IDcategorie, date_parution, priorite, IDfamille, nom, texte in listeMessagesFamiliaux :
            date_parution = UTILS_Dates.DateEngEnDateDD(date_parution)
            if (IDfamille in self.dictMessageFamiliaux) == False :
                self.dictMessageFamiliaux[IDfamille] = []
            self.dictMessageFamiliaux[IDfamille].append({"IDmessage":IDmessage, "IDcategorie":IDcategorie, "date_parution":date_parution, "priorite":priorite, "nom":nom, "texte":texte})

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
        
        # Get noms Titulaires
        self.dictNomsTitulaires = UTILS_Titulaires.GetTitulaires(mode_adresse_facturation=True)

        # Recherche des numéros d'agréments
        req = """SELECT IDactivite, agrement, date_debut, date_fin
        FROM agrements
        ORDER BY date_debut;"""
        DB.ExecuterReq(req)
        self.listeAgrements = DB.ResultatReq()  

        DB.Close() 

        # Récupération des questionnaires
        self.Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")
        
        # Récupération des infos de base familles
        self.infosIndividus = UTILS_Infos_individus.Informations(mode_adresse_facturation=True)
        

    def RechercheAgrement(self, IDactivite, date):
        for IDactiviteTmp, agrement, date_debut, date_fin in self.listeAgrements :
            if IDactivite == IDactiviteTmp and date >= date_debut and date <= date_fin :
                return agrement
        return None

    def Supprime_accent(self, texte):
        liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"ä", u"a"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"), (u"/", u""), (u"\\", u""), ]
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
        if texte == None :
            texte = ""
        for key, valeur, in dictValeurs.items() :
            if key in texte and key.startswith("{"):
                texte = texte.replace(key, six.text_type(valeur))
        return texte

    def GetDonnees(self, listeFactures=[], liste_activites=[], date_debut=None, date_fin=None, date_edition=None, date_echeance=None, prestations=["consommation", "cotisation", "location", "autre"], typeLabel=0, date_anterieure=None, mention1="", mention2="", mention3=""):
        """ Recherche des factures à créer """      
        
        dictFactures = {}
        listeIDfactures = []
        for dictTemp in listeFactures :
            listeIDfactures.append(dictTemp["IDfacture"])
            dictFactures[dictTemp["IDfacture"]] = dictTemp
              
        # Création des conditions SQL
        if len(liste_activites) == 0 : conditionActivites = "()"
        elif len(liste_activites) == 1 : conditionActivites = "(%d)" % liste_activites[0]
        else : conditionActivites = str(tuple(liste_activites))
        
        if len(listeFactures) == 0 :
            conditionFactures = "IS NULL"
        else:
            if len(listeIDfactures) == 0 : conditionFactures = "()"
            elif len(listeIDfactures) == 1 : conditionFactures = "(%d)" % listeIDfactures[0]
            else : conditionFactures = str(tuple(listeIDfactures))

        # En cas d'intégration des prestations antérieures
        if date_anterieure == None :
            date_debut_temp = date_debut
        else :
            date_debut_temp = date_anterieure

        conditionDates = " prestations.date>='%s' AND prestations.date<='%s' AND IDfacture %s" % (date_debut_temp, date_fin, conditionFactures)

        if len(prestations) == 1 :
            conditionPrestations = " prestations.categorie='%s'" % prestations[0]
        else :
            conditionPrestations = " prestations.categorie IN %s" % str(tuple(prestations)).replace("u'", "'")
        
        DB = GestionDB.DB()
        
        # Recherche des prestations de la période
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
        SELECT ventilation.IDprestation, ventilation.IDreglement, ventilation.IDcompte_payeur, SUM(ventilation.montant) AS montant_ventilation,
        reglements.date, reglements.montant, reglements.numero_piece, modes_reglements.label, emetteurs.nom, payeurs.nom
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
        LEFT JOIN emetteurs ON emetteurs.IDemetteur = reglements.IDemetteur
        LEFT JOIN payeurs ON payeurs.IDpayeur = reglements.IDpayeur
        %s
        GROUP BY ventilation.IDprestation, ventilation.IDreglement
        ORDER BY prestations.date
        ;""" % conditions
        DB.ExecuterReq(req)
        listeVentilationPrestations = DB.ResultatReq()  
        dictVentilationPrestations = {}
        dictReglements = {}
        for IDprestation, IDreglement, IDcompte_payeur, montant_ventilation, date, montant, numero_piece, mode, emetteur, payeur in listeVentilationPrestations :
            date = UTILS_Dates.DateEngEnDateDD(date)
            montant = FloatToDecimal(montant)
            montant_ventilation = FloatToDecimal(montant_ventilation)
            
            # Mémorisation des règlements
            if (IDcompte_payeur in dictReglements) == False :
                dictReglements[IDcompte_payeur] = {}
            if (IDreglement in dictReglements[IDcompte_payeur]) == False :
                dictReglements[IDcompte_payeur][IDreglement] = {"date" : date, "montant" : montant, "mode" : mode, "emetteur" : emetteur, "numero" : numero_piece, "payeur" : payeur, "ventilation" : FloatToDecimal(0.0)}
            dictReglements[IDcompte_payeur][IDreglement]["ventilation"] += montant_ventilation
            
            # Mémorisation de la ventilation
            if (IDprestation in dictVentilationPrestations) == False :
                dictVentilationPrestations[IDprestation] = FloatToDecimal(0.0)
            dictVentilationPrestations[IDprestation] += montant_ventilation

        # Recherche des QF aux dates concernées
        if len(listeFactures) == 0 :
            date_min = date_debut
            date_max = date_fin
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
            
        # Recherche des anciennes prestations impayées (=le report antérieur)
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
        
        # Recherche des déductions
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
            if (IDprestation in dictDeductions) == False :
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
            if (IDprestation in dictConsommations) == False :
                dictConsommations[IDprestation] = []
            dictConsommations[IDprestation].append({"date" : UTILS_Dates.DateEngEnDateDD(date), "etat" : etat})

        # Recherche du solde du compte
        listeComptesPayeurs = []
        for temp in listePrestations :
            IDcompte_payeur = temp[1]
            if IDcompte_payeur not in listeComptesPayeurs :
                listeComptesPayeurs.append(IDcompte_payeur)
        if len(listeComptesPayeurs) == 0 : conditions_comptes_payeurs = "()"
        elif len(listeComptesPayeurs) == 1 : conditions_comptes_payeurs = "(%d)" % listeComptesPayeurs[0]
        else : conditions_comptes_payeurs = str(tuple(listeComptesPayeurs))

        req = """SELECT IDcompte_payeur, SUM(montant)
        FROM prestations
        WHERE IDcompte_payeur IN %s
        GROUP BY IDcompte_payeur
        ;""" % conditions_comptes_payeurs
        DB.ExecuterReq(req)
        liste_prestations = DB.ResultatReq()
        dict_prestations = {}
        for IDcompte_payeur, total_prestations in liste_prestations:
            dict_prestations[IDcompte_payeur] = total_prestations

        req = """SELECT IDcompte_payeur, SUM(montant)
        FROM reglements
        WHERE IDcompte_payeur IN %s
        GROUP BY IDcompte_payeur
        ;""" % conditions_comptes_payeurs
        DB.ExecuterReq(req)
        liste_reglements = DB.ResultatReq()
        dict_reglements = {}
        for IDcompte_payeur, total_reglements in liste_reglements:
            dict_reglements[IDcompte_payeur] = total_reglements

        dict_soldes_comptes = {}
        for IDcompte_payeur in listeComptesPayeurs:
            if IDcompte_payeur in dict_prestations:
                total_prestations = FloatToDecimal(dict_prestations[IDcompte_payeur])
            else :
                total_prestations = FloatToDecimal(0.0)
            if IDcompte_payeur in dict_reglements:
                total_reglements = FloatToDecimal(dict_reglements[IDcompte_payeur])
            else :
                total_reglements = FloatToDecimal(0.0)
            solde_compte = total_reglements - total_prestations

            if solde_compte > FloatToDecimal(0.0):
                solde_compte = u"+%.2f %s" % (solde_compte, SYMBOLE)
            else:
                solde_compte = u"%.2f %s" % (solde_compte, SYMBOLE)

            dict_soldes_comptes[IDcompte_payeur] = solde_compte

        DB.Close()

        # Analyse et regroupement des données
        num_facture = 0
        dictComptes = {}
        dictComptesPayeursFactures = {}
        for IDprestation, IDcompte_payeur, date, categorie, label, montant_initial, montant, tva, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDfamille in listePrestations :
            montant = FloatToDecimal(montant) 
            
            if (IDcompte_payeur in dictComptesPayeursFactures) == False :
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
                mention1 = dictFactures[IDfacture]["mention1"]
                mention2 = dictFactures[IDfacture]["mention2"]
                mention3 = dictFactures[IDfacture]["mention3"]
                            
            # Regroupement par compte payeur
            if (ID in dictComptes) == False and IDfamille in self.dictNomsTitulaires :
                
                # Recherche des titulaires
                dictInfosTitulaires = self.dictNomsTitulaires[IDfamille]
                nomsTitulairesAvecCivilite = dictInfosTitulaires["titulairesAvecCivilite"]
                nomsTitulairesSansCivilite = dictInfosTitulaires["titulairesSansCivilite"]
                rue_resid = dictInfosTitulaires["adresse"]["rue"]
                cp_resid = dictInfosTitulaires["adresse"]["cp"]
                ville_resid = dictInfosTitulaires["adresse"]["ville"]

                # Recherche des règlements
                if IDcompte_payeur in dictReglements :
                    dictReglementsCompte = dictReglements[IDcompte_payeur]
                else :
                    dictReglementsCompte = {}

                # Recherche du solde du compte
                if IDcompte_payeur in dict_soldes_comptes :
                    solde_compte = dict_soldes_comptes[IDcompte_payeur]
                else :
                    solde_compte = u"0.00 %s" % SYMBOLE

                # Mémorisation des infos
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
                    "listeIDprestations" : [],
                    "listeDeductions" : [],
                    "prestations_familiales" : [],
                    "total" : FloatToDecimal(0.0),
                    "ventilation" : FloatToDecimal(0.0),
                    "solde" : FloatToDecimal(0.0),
                    "qfdates" : {},
                    "reports" : {},
                    "total_reports" : FloatToDecimal(0.0),
                    "{TOTAL_REPORTS}" : u"0.00 %s" % SYMBOLE,
                    "solde_avec_reports" : FloatToDecimal(0.0),
                    "{SOLDE_AVEC_REPORTS}" : u"0.00 %s" % SYMBOLE,
                    "{SOLDE_COMPTE}" : solde_compte,
                    "select" : True,
                    "messages_familiaux" : [],
                    "{NOM_LOT}" : "",
                    "reglements" : dictReglementsCompte,
                    "texte_introduction" : "",
                    "texte_conclusion" : "",
                    
                    "date_edition" : date_edition,
                    "{DATE_EDITION_LONG}" : UTILS_Dates.DateComplete(date_edition),
                    "{DATE_EDITION_COURT}" : UTILS_Dates.DateEngFr(str(date_edition)),

                    "numero" : _(u"Facture n°%06d") % num_facture,
                    "num_facture" : num_facture,
                    "{NUM_FACTURE}" : u"%06d" % num_facture,
                    "{CODEBARRES_NUM_FACTURE}" :"F%06d" % num_facture,
                    "{INDIVIDUS_CONCERNES}" : [],

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

                # Date échéance
                if date_echeance != None :
                    if date_echeance != None :
                        dictComptes[ID]["date_echeance"] = date_echeance
                        dictComptes[ID]["{DATE_ECHEANCE_LONG}"] = UTILS_Dates.DateComplete(date_echeance)
                        dictComptes[ID]["{DATE_ECHEANCE_COURT}"] = UTILS_Dates.DateEngFr(str(date_echeance)) 
                        dictComptes[ID]["{TEXTE_ECHEANCE}"] = _(u"Echéance du règlement : %s") % UTILS_Dates.DateEngFr(str(date_echeance)) 
                else:
                    dictComptes[ID]["date_echeance"] = None
                    dictComptes[ID]["{DATE_ECHEANCE_LONG}"] = ""
                    dictComptes[ID]["{DATE_ECHEANCE_COURT}"] = ""
                    dictComptes[ID]["{TEXTE_ECHEANCE}"] = ""

                # Ajoute les réponses des questionnaires
                for dictReponse in self.Questionnaires.GetDonnees(IDfamille) :
                    dictComptes[ID][dictReponse["champ"]] = dictReponse["reponse"]
                    if dictReponse["controle"] == "codebarres" :
                        dictComptes[ID]["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]
                
                # Ajoute les messages familiaux
                if IDfamille in self.dictMessageFamiliaux :
                    dictComptes[ID]["messages_familiaux"] = self.dictMessageFamiliaux[IDfamille]

                # Ajoute les mentions
                dictComptes[ID]["{MENTION1}"] = mention1
                dictComptes[ID]["{MENTION2}"] = mention2
                dictComptes[ID]["{MENTION3}"] = mention3

            # Insert les montants pour le compte payeur
            if IDprestation in dictVentilationPrestations :
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
            if (IDindividu in dictComptes[ID]["individus"]) == False :
                if IDindividu in self.dictIndividus :

                    # Si c'est bien un individu
                    IDcivilite = self.dictIndividus[IDindividu]["IDcivilite"]
                    nomIndividu = self.dictIndividus[IDindividu]["nom"]
                    prenomIndividu = self.dictIndividus[IDindividu]["prenom"]
                    dateNaiss = self.dictIndividus[IDindividu]["date_naiss"]
                    if dateNaiss != None : 
                        if DICT_CIVILITES[IDcivilite]["sexe"] == "M" :
                            texteDateNaiss = _(u", né le %s") % UTILS_Dates.DateEngFr(str(dateNaiss))
                        else:
                            texteDateNaiss = _(u", née le %s") % UTILS_Dates.DateEngFr(str(dateNaiss))
                    else:
                        texteDateNaiss = u""
                    texteIndividu = _(u"<b>%s %s</b><font size=7>%s</font>") % (nomIndividu, prenomIndividu, texteDateNaiss)
                    nom = u"%s %s" % (nomIndividu, prenomIndividu)

                    dictComptes[ID]["{INDIVIDUS_CONCERNES}"].append(u"%s %s" % (nomIndividu, prenomIndividu))
                    
                else:
                    # Si c'est pour une prestation familiale on créé un individu ID 0 :
                    nom = _(u"Prestations diverses")
                    texteIndividu = u"<b>%s</b>" % nom

                dictComptes[ID]["individus"][IDindividu] = { "texte" : texteIndividu, "activites" : {}, "total" : FloatToDecimal(0.0), "ventilation" : FloatToDecimal(0.0), "total_reports" : FloatToDecimal(0.0), "nom" : nom, "select" : True }

            # Ajout de l'activité
            if (IDactivite in dictComptes[ID]["individus"][IDindividu]["activites"]) == False :
                texteActivite = nomActivite
                agrement = self.RechercheAgrement(IDactivite, date)
                if agrement != None :
                    texteActivite += _(u" - n° agrément : %s") % agrement
                dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite] = { "texte" : texteActivite, "presences" : {} }
            
            # Ajout de la présence
            if (date in dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite]["presences"]) == False :
                dictComptes[ID]["individus"][IDindividu]["activites"][IDactivite]["presences"][date] = { "texte" : UTILS_Dates.DateEngFr(str(date)), "unites" : [], "total" : FloatToDecimal(0.0) }

            # Recherche du nbre de dates pour cette prestation
            if IDprestation in dictConsommations :
                listeDates = dictConsommations[IDprestation]
            else:
                listeDates = []

            # Recherche des déductions
            if IDprestation in dictDeductions :
                deductions = dictDeductions[IDprestation]
            else :
                deductions = []

            # Mémorisation des déductions pour total
            for dictDeduction in deductions :
                dictComptes[ID]["listeDeductions"].append(dictDeduction)

            # Adaptation du label
            if typeLabel == 2 and IDtarif != None :
                label = nomTarif
            if typeLabel == 3 and IDtarif != None :
                label = nomActivite
            if typeLabel == 1 and IDtarif != None :
                if IDprestation in dictConsommations :
                    nbreAbsences = 0
                    for dictTemp in dictConsommations[IDprestation] :
                        if dictTemp["etat"] == "absenti" :
                            nbreAbsences += 1
                    # Si toutes les consommations attachées à la prestation sont sur l'état "Absence injustifiée" :
                    if nbreAbsences == len(dictConsommations[IDprestation]) :
                        label = label + _(u" (Absence injustifiée)")

            # Mémorisation de la prestation
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
                        
            # Stockage des IDprestation pour saisir le IDfacture après création de la facture
            dictComptes[ID]["listePrestations"].append((IDindividu, IDprestation))
            dictComptes[ID]["listeIDprestations"].append(IDprestation)

            # Intégration des qf aux dates concernées
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
                
        
        # Intégration des total des déductions
        for ID, valeurs in dictComptes.items() :
            totalDeductions = 0.0
            for dictDeduction in dictComptes[ID]["listeDeductions"] :
                totalDeductions += dictDeduction["montant"]
            dictComptes[ID]["{TOTAL_DEDUCTIONS}"] = u"%.02f %s" % (totalDeductions, SYMBOLE)

        # Intégration du REPORT des anciennes prestations NON PAYEES
        for IDprestation, IDcompte_payeur, date, categorie, label, montant, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDfamille in listeReports :
            montant = FloatToDecimal(montant) 
            
            if IDprestation in dictVentilationReports :
                montant_ventilation = FloatToDecimal(dictVentilationReports[IDprestation])
            else :
                montant_ventilation = FloatToDecimal(0.0)
            
            montant_impaye = montant - montant_ventilation
            date = UTILS_Dates.DateEngEnDateDD(date)
            mois = date.month
            annee = date.year
            periode = (annee, mois)
            
            if montant_ventilation != montant : # Avant c'était : montant_ventilation < montant mais j'ai changé pour le pb des prestations avec montant négatif

                if len(listeFactures) == 0 :
                    
                    #if dictComptes.has_key(IDcompte_payeur) :
                    if IDcompte_payeur in dictComptes and IDprestation not in dictComptes[IDcompte_payeur]["listeIDprestations"] :
                        if (periode in dictComptes[IDcompte_payeur]["reports"]) == False :
                            dictComptes[IDcompte_payeur]["reports"][periode] = FloatToDecimal(0.0)
                        dictComptes[IDcompte_payeur]["reports"][periode] += montant_impaye
                        dictComptes[IDcompte_payeur]["total_reports"] += montant_impaye
                        dictComptes[IDcompte_payeur]["{TOTAL_REPORTS}"] = u"%.02f %s" % (dictComptes[IDcompte_payeur]["total_reports"], SYMBOLE)
                
                else :
                    
                    if IDcompte_payeur in dictComptesPayeursFactures :
                        for IDfacture in dictComptesPayeursFactures[IDcompte_payeur] :
                            if date < dictComptes[IDfacture]["date_debut"] and IDprestation not in dictComptes[IDfacture]["listeIDprestations"] :
                                
                                if (periode in dictComptes[IDfacture]["reports"]) == False :
                                    dictComptes[IDfacture]["reports"][periode] = FloatToDecimal(0.0)
                                dictComptes[IDfacture]["reports"][periode] += montant_impaye
                                dictComptes[IDfacture]["total_reports"] += montant_impaye
                                dictComptes[IDfacture]["{TOTAL_REPORTS}"] = u"%.02f %s" % (dictComptes[IDfacture]["total_reports"], SYMBOLE)
        
        # Ajout des impayés au solde
        for ID, dictValeurs in dictComptes.items() :
            dictComptes[ID]["solde_avec_reports"] = dictComptes[ID]["solde"] + dictComptes[ID]["total_reports"]
            dictComptes[ID]["{SOLDE_AVEC_REPORTS}"] = u"%.02f %s" % (dictComptes[ID]["solde_avec_reports"], SYMBOLE)
            dictComptes[ID]["{INDIVIDUS_CONCERNES}"] = ", ".join(dictComptes[ID]["{INDIVIDUS_CONCERNES}"])

        return dictComptes







    def GetDonneesImpression(self, listeFactures=[], dictOptions=None):
        """ Impression des factures """
        dlgAttente = wx.BusyInfo(_(u"Recherche des données de facturation..."), None)
        try :
            if 'phoenix' not in wx.PlatformInfo:
                wx.Yield()
        except :
            pass
        
        # Récupère les données de la facture
        if len(listeFactures) == 0 : conditions = "()"
        elif len(listeFactures) == 1 : conditions = "(%d)" % listeFactures[0]
        else : conditions = str(tuple(listeFactures))
        
        DB = GestionDB.DB()
        req = """
        SELECT 
        factures.IDfacture, factures.IDprefixe, factures_prefixes.prefixe, factures.numero, factures.IDcompte_payeur, factures.activites, factures.individus,
        factures.date_edition, factures.date_echeance, factures.IDutilisateur,
        factures.date_debut, factures.date_fin, factures.total, factures.regle, factures.solde,
        factures.prestations, lots_factures.nom,
        factures.mention1, factures.mention2, factures.mention3
        FROM factures
        LEFT JOIN lots_factures ON lots_factures.IDlot = factures.IDlot
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe
        WHERE factures.IDfacture IN %s
        GROUP BY factures.IDfacture
        ORDER BY factures.date_edition
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     

        # Récupération des prélèvements
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

        # Pièces PES ORMC
        req = """SELECT
        pes_pieces.IDpiece, pes_pieces.numero, pes_pieces.prelevement_iban, pes_pieces.IDfacture,
        pes_pieces.montant, pes_pieces.prelevement_statut, comptes_payeurs.IDcompte_payeur,
        pes_lots.date_prelevement, pes_pieces.prelevement_IDmandat, comptes_bancaires.code_ics
        FROM pes_pieces
        LEFT JOIN pes_lots ON pes_lots.IDlot = pes_pieces.IDlot
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = pes_pieces.IDfamille
        LEFT JOIN comptes_bancaires ON comptes_bancaires.IDcompte = pes_lots.IDcompte
        WHERE pes_pieces.prelevement_IDmandat IS NOT NULL AND pes_pieces.prelevement=1 AND pes_pieces.IDfacture IN %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listePieces = DB.ResultatReq()
        dictPrelevements = {}
        for listeDonneesPrel in (listePrelevements, listePieces):
            for IDprelevement, numero_compte, iban, IDfacture, montant, statut, IDcompte_payeur, datePrelevement, rum, code_ics in (listeDonneesPrel):
                datePrelevement = UTILS_Dates.DateEngEnDateDD(datePrelevement)
                dictPrelevements[IDfacture] = {
                    "IDprelevement": IDprelevement, "numero_compte": numero_compte, "montant": montant,
                    "statut": statut, "IDcompte_payeur": IDcompte_payeur, "datePrelevement": datePrelevement,
                    "iban": iban, "rum": rum, "code_ics": code_ics,
                }

        # Infos PES ORMC
        req = """SELECT
        pes_pieces.IDlot, pes_pieces.IDfacture, pes_lots.nom, pes_lots.exercice, pes_lots.mois, pes_lots.objet_dette, pes_lots.id_bordereau, pes_lots.code_prodloc, pes_lots.code_etab,
        pes_lots.code_collectivite, pes_lots.id_collectivite, pes_lots.id_poste
        FROM pes_pieces
        LEFT JOIN pes_lots ON pes_lots.IDlot = pes_pieces.IDlot
        WHERE pes_pieces.IDfacture IN %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listeInfosPes = DB.ResultatReq()
        dictPes = {}
        for IDlot_pes, IDfacture, nom_lot_pes, exercice, mois, objet, id_bordereau, code_produit, code_etab, code_collectivite, id_collectivite, id_poste in (listeInfosPes):
            dictPes[IDfacture] = {
                "pes_IDlot": IDlot_pes, "pes_nom_lot": nom_lot_pes, "pes_lot_exercice": exercice, "pes_lot_mois": mois,
                "pes_lot_objet": objet, "pes_lot_id_bordereau": id_bordereau, "pes_lot_code_produit": code_produit,
                "pes_lot_code_collectivite": code_collectivite, "pes_lot_id_collectivite": id_collectivite,
                "pes_lot_id_poste": id_poste, "pes_lot_code_etab": code_etab,
            }
        if len(listeDonnees) == 0 :
            del dlgAttente
            DB.Close()
            return False
        
        listeFactures = []
        index = 0
        for IDfacture, IDprefixe, prefixe, numero, IDcompte_payeur, activites, individus, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, typesPrestations, nomLot, mention1, mention2, mention3 in listeDonnees :
            
            self.EcritStatusbar(_(u"Recherche de la facture %d sur %d") % (index+1, len(listeDonnees)))

            if numero == None : numero = 0
            date_edition = UTILS_Dates.DateEngEnDateDD(date_edition) 
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            date_echeance = UTILS_Dates.DateEngEnDateDD(date_echeance)       

            if typesPrestations != None :
                prestations = typesPrestations.split(";")
            else :
                prestations = ["consommation", "cotisation", "location", "autre"]

            liste_activites = []
            if len(activites) > 0:
                for IDactivite in activites.split(";") :
                    liste_activites.append(int(IDactivite))
                
            liste_individus = []
            for IDindividu in individus.split(";") :
                liste_individus.append(int(IDindividu))

            if not mention1 : mention1 = ""
            if not mention2 : mention2 = ""
            if not mention3 : mention3 = ""

            dictFacture = {
                "IDfacture" : IDfacture, "IDprefixe" : IDprefixe, "prefixe" : prefixe, "numero" : numero, "IDcompte_payeur" : IDcompte_payeur, "date_edition" : date_edition, "date_echeance" : date_echeance,
                "IDutilisateur" : IDutilisateur, "date_debut" : date_debut, "date_fin" : date_fin, "total" : total, "regle" : regle, "solde" : solde, 
                "activites" : liste_activites, "individus" : liste_individus, "prestations" : prestations, "mention1": mention1, "mention2": mention2, "mention3": mention3,
                }
            listeFactures.append(dictFacture) 
            index +=1

        DB.Close()

        # Récupération des données de facturation
        typeLabel = 0
        if dictOptions != None and "intitules" in dictOptions :
            typeLabel = dictOptions["intitules"]
            
        dictComptes = self.GetDonnees(listeFactures=listeFactures, typeLabel=typeLabel)
        
        dictFactures = {}
        dictChampsFusion = {}
        for IDfacture, IDprefixe, prefixe, numero, IDcompte_payeur, activites, individus, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, typesPrestations, nomLot, mention1, mention2, mention3 in listeDonnees :
            total = FloatToDecimal(total) 
            regle = FloatToDecimal(regle)
            solde = FloatToDecimal(solde)

            if IDfacture in dictComptes :
                
                dictCompte = dictComptes[IDfacture]
                dictCompte["select"] = True
                
                # Affichage du solde initial
                if dictOptions != None and dictOptions["affichage_solde"] == 1:
                    dictCompte["ventilation"] = regle
                    dictCompte["solde"] = solde
                
                # Attribue un numéro de facture
                if IDprefixe != None :
                    numeroStr = u"%s-%06d" % (prefixe, numero)
                else :
                    numeroStr = u"%06d" % numero

                dictCompte["{IDFACTURE}"] = str(IDfacture)
                dictCompte["num_facture"] = numeroStr
                dictCompte["num_codeBarre"] = numeroStr #"%07d" % numero
                dictCompte["numero"] = _(u"Facture n°%s") % numeroStr
                dictCompte["{NUM_FACTURE}"] = numeroStr #u"%06d" % numero
                dictCompte["{CODEBARRES_NUM_FACTURE}"] = u"F%s" % numeroStr
                dictCompte["{NUMERO_FACTURE}"] = dictCompte["{NUM_FACTURE}"]

                dictCompte["{DATE_DEBUT}"] = UTILS_Dates.DateEngFr(str(date_debut))
                dictCompte["{DATE_FIN}"] = UTILS_Dates.DateEngFr(str(date_fin))
                dictCompte["{DATE_EDITION_FACTURE}"] = UTILS_Dates.DateEngFr(str(date_edition))
                dictCompte["{DATE_ECHEANCE}"] = UTILS_Dates.DateEngFr(str(date_echeance))
                dictCompte["{SOLDE}"] = u"%.2f %s" % (dictCompte["solde"], SYMBOLE)
                dictCompte["{SOLDE_LETTRES}"] = UTILS_Conversion.trad(solde, MONNAIE_SINGULIER, MONNAIE_DIVISION).strip().capitalize() 
                dictCompte["{SOLDE_AVEC_REPORTS}"] = u"%.2f %s" % (dictCompte["solde_avec_reports"], SYMBOLE)
                dictCompte["{SOLDE_AVEC_REPORTS_LETTRES}"] = UTILS_Conversion.trad(solde+dictCompte["total_reports"], MONNAIE_SINGULIER, MONNAIE_DIVISION).strip().capitalize()

                if nomLot == None :
                    nomLot = ""
                dictCompte["{NOM_LOT}"] = nomLot
                
                for IDindividu, dictIndividu in dictCompte["individus"].items() :
                    dictIndividu["select"] = True

                # Recherche de prélèvements
                if IDfacture in dictPrelevements :
                    if datePrelevement < dictCompte["date_edition"] :
                        verbe = _(u"a été")
                    else :
                        verbe = _(u"sera")
                    montant = dictPrelevements[IDfacture]["montant"]
                    datePrelevement = dictPrelevements[IDfacture]["datePrelevement"]
                    iban = dictPrelevements[IDfacture]["iban"]
                    rum = dictPrelevements[IDfacture]["rum"]
                    code_ics = dictPrelevements[IDfacture]["code_ics"]
                    dictCompte["{DATE_PRELEVEMENT}"] = UTILS_Dates.DateEngFr(str(datePrelevement))
                    if iban != None :
                        dictCompte["prelevement"] = _(u"La somme de %.2f %s %s prélevée le %s sur le compte ***%s") % (montant, SYMBOLE, verbe, UTILS_Dates.DateEngFr(str(datePrelevement)), iban[-7:])
                    else :
                        dictCompte["prelevement"] = _(u"La somme de %.2f %s %s prélevée le %s") % (montant, SYMBOLE, verbe, UTILS_Dates.DateEngFr(str(datePrelevement)))
                    if rum != None :
                        dictCompte["prelevement"] += _(u"<br/>Réf. mandat unique : %s / Code ICS : %s") % (rum, code_ics)
                else :
                    dictCompte["prelevement"] = None
                    dictCompte["{DATE_PRELEVEMENT}"] = ""

                # Infos PES ORMC
                if IDfacture in dictPes :
                    dictCompte["dict_pes"] = dictPes[IDfacture]
                    try:
                        datamatrix = Calculer_datamatrix(dictCompte)
                    except Exception as err:
                        datamatrix = ""
                        print("ERREUR dans la generation du datamatrix :", err)
                    dictCompte["{PES_DATAMATRIX}"] = datamatrix
                    dictCompte["{PES_IDPIECE}"] = str(IDfacture)
                    dictCompte["{PES_IDLOT}"] = dictPes[IDfacture]["pes_IDlot"]
                    dictCompte["{PES_NOM_LOT}"] = dictPes[IDfacture]["pes_nom_lot"]
                    dictCompte["{PES_LOT_EXERCICE}"] = dictPes[IDfacture]["pes_lot_exercice"]
                    dictCompte["{PES_LOT_MOIS}"] = dictPes[IDfacture]["pes_lot_mois"]
                    dictCompte["{PES_LOT_OBJET}"] = dictPes[IDfacture]["pes_lot_objet"]
                    dictCompte["{PES_LOT_ID_BORDEREAU}"] = dictPes[IDfacture]["pes_lot_id_bordereau"]
                    dictCompte["{PES_LOT_CODE_PRODUIT}"] = dictPes[IDfacture]["pes_lot_code_produit"]
                else:
                    dictCompte["dict_pes"] = {}
                    dictCompte["{PES_DATAMATRIX}"] = ""
                    dictCompte["{PES_IDPIECE}"] = ""
                    dictCompte["{PES_IDLOT}"] = ""
                    dictCompte["{PES_NOM_LOT}"] = ""
                    dictCompte["{PES_LOT_EXERCICE}"] = ""
                    dictCompte["{PES_LOT_MOIS}"] = ""
                    dictCompte["{PES_LOT_OBJET}"] = ""
                    dictCompte["{PES_LOT_ID_BORDEREAU}"] = ""
                    dictCompte["{PES_LOT_CODE_PRODUIT}"] = ""

                # Champs de fusion pour Email
                dictChampsFusion[IDfacture] = {}
                dictChampsFusion[IDfacture]["{NUMERO_FACTURE}"] = dictCompte["{NUM_FACTURE}"]
                dictChampsFusion[IDfacture]["{DATE_DEBUT}"] = UTILS_Dates.DateEngFr(str(date_debut))
                dictChampsFusion[IDfacture]["{DATE_FIN}"] = UTILS_Dates.DateEngFr(str(date_fin))
                dictChampsFusion[IDfacture]["{DATE_EDITION_FACTURE}"] = UTILS_Dates.DateEngFr(str(date_edition))
                dictChampsFusion[IDfacture]["{DATE_ECHEANCE}"] = UTILS_Dates.DateEngFr(str(date_echeance))
                dictChampsFusion[IDfacture]["{SOLDE}"] = u"%.2f %s" % (dictCompte["solde"], SYMBOLE)
                dictChampsFusion[IDfacture]["{SOLDE_AVEC_REPORTS}"] = dictCompte["{SOLDE_AVEC_REPORTS}"]
                dictChampsFusion[IDfacture]["{SOLDE_COMPTE}"] = dictCompte["{SOLDE_COMPTE}"]
                dictChampsFusion[IDfacture]["{DATE_PRELEVEMENT}"] = dictCompte["{DATE_PRELEVEMENT}"]

                # Fusion pour textes personnalisés
                dictCompte["texte_titre"] = self.RemplaceMotsCles(dictOptions["texte_titre"], dictCompte)
                dictCompte["texte_introduction"] = self.RemplaceMotsCles(dictOptions["texte_introduction"], dictCompte)
                dictCompte["texte_conclusion"] = self.RemplaceMotsCles(dictOptions["texte_conclusion"], dictCompte)
                
                # Mémorisation de la facture
                dictFactures[IDfacture] = dictCompte
            
            index += 1
        
        del dlgAttente      
        self.EcritStatusbar("")   
        
        if len(dictFactures) == 0 :
            return False
           
        return dictFactures, dictChampsFusion




    def Impression(self, listeFactures=[], nomDoc=None, nomFichierUnique=None, afficherDoc=True, dictOptions=None, repertoire=None, repertoireTemp=False, afficherOptions=True):
        """ Impression des factures """
        # Récupération des paramètres d'affichage
        if dictOptions == None :
            if afficherOptions == True :

                if afficherDoc == False :
                    dlg = DLG_Apercu_facture.Dialog(None, titre=_(u"Sélection des paramètres de la facture"), intro=_(u"Sélectionnez ici les paramètres d'affichage de la facture puis cliquez sur le bouton OK."))
                    dlg.bouton_ok.SetImageEtTexte("Images/32x32/Valider.png", _("Ok"))
                else :
                    dlg = DLG_Apercu_facture.Dialog(None)
                if dlg.ShowModal() == wx.ID_OK:
                    dictOptions = dlg.GetParametres()
                    dlg.Destroy()
                else :
                    dlg.Destroy()
                    return False

            else :
                dlg = DLG_Apercu_facture.Dialog(None, titre=_(u"Sélection des paramètres de la facture"), intro=_(u"Sélectionnez ici les paramètres d'affichage de la facture puis cliquez sur le bouton OK."))
                dictOptions = dlg.GetParametres()
                dlg.Destroy()

        # Récupération des données à partir des IDfacture
        resultat = self.GetDonneesImpression(listeFactures, dictOptions)
        if resultat == False :
            return False
        dictFactures, dictChampsFusion = resultat
        
        # Création des PDF à l'unité
        def CreationPDFunique(repertoireCible=""):
            dictPieces = {}
            dlgProgress = wx.ProgressDialog(_(u"Génération des factures au format PDF"), _(u"Initialisation..."), maximum=len(dictFactures), parent=None, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
            try :
                if 'phoenix' not in wx.PlatformInfo:
                    wx.Yield()
            except :
                pass
            try :
                index = 0
                for IDfacture, dictFacture in dictFactures.items() :
                    if dictFacture["select"] == True :
                        num_facture = dictFacture["num_facture"]
                        nomTitulaires = self.Supprime_accent(dictFacture["nomSansCivilite"])
                        if nomFichierUnique == None :
                            nomFichier = _(u"Facture %s - %s") % (num_facture, nomTitulaires)
                        else :
                            nomFichier = nomFichierUnique
                            nomFichier = nomFichier.replace("{NUM_FACTURE}", num_facture)
                            nomFichier = nomFichier.replace("{NOM_TITULAIRES}", nomTitulaires)
                            nomFichier = nomFichier.replace("{NOM_TITULAIRES_MAJ}", FormateMaj(nomTitulaires))
                        cheminFichier = u"%s/%s.pdf" % (repertoireCible, nomFichier)
                        dictComptesTemp = {IDfacture : dictFacture}
                        texte = _(u"Facture %d/%d : %s") % (index, len(dictFactures), nomFichier)
                        self.EcritStatusbar(texte)
                        dlgProgress.Update(index + 1, texte)
                        UTILS_Impression_facture.Impression(dictComptesTemp, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=False, nomFichier=cheminFichier)
                        dictPieces[IDfacture] = cheminFichier
                        index += 1
                self.EcritStatusbar("")
                dlgProgress.Destroy()
                return dictPieces
            except Exception as err:
                dlgProgress.Destroy()
                traceback.print_exc(file=sys.stdout)
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des factures : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Répertoire souhaité par l'utilisateur
        if repertoire not in (None, "") :
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
            dlgAttente = wx.BusyInfo(_(u"Création du PDF des factures..."), None)
            try :
                if 'phoenix' not in wx.PlatformInfo:
                    wx.Yield()
            except :
                pass
            self.EcritStatusbar(_(u"Création du PDF des factures en cours... veuillez patienter..."))
            try :
                UTILS_Impression_facture.Impression(dictFactures, dictOptions, IDmodele=dictOptions["IDmodele"], ouverture=afficherDoc, nomFichier=nomDoc)
                self.EcritStatusbar("")
                del dlgAttente
            except Exception as err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                err = str(err)
                if six.PY2:
                    err = err.decode("iso-8859-15")
                dlg = wx.MessageDialog(None, _(u"Désolé, le problème suivant a été rencontré dans l'édition des factures : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return dictChampsFusion, dictPieces






def SuppressionFacture(listeFactures=[], mode="suppression"):
    """ Suppression d'une facture """
    dlgAttente = wx.BusyInfo(_(u"%s des factures en cours...") % mode.capitalize(), None)
    if 'phoenix' not in wx.PlatformInfo:
        wx.Yield()
    DB = GestionDB.DB()
    
    # Suppression
    if mode == "suppression" :
        for IDfacture in listeFactures :
            DB.ReqMAJ("prestations", [("IDfacture", None),], "IDfacture", IDfacture)
            DB.ReqDEL("factures", "IDfacture", IDfacture)
            
    # Annulation
    if mode == "annulation" :
        for IDfacture in listeFactures :
            DB.ReqMAJ("prestations", [("IDfacture", None),], "IDfacture", IDfacture)
            DB.ReqMAJ("factures", [("etat", "annulation"),], "IDfacture", IDfacture)
            
    DB.Close() 
    del dlgAttente
    return True


def ModificationFacture(listeFactures=[], dict_valeurs={}):
    """ Modification des caractéristique d'une facture """
    dlgAttente = wx.BusyInfo(_(u"Modification des factures en cours..."), None)
    if 'phoenix' not in wx.PlatformInfo:
        wx.Yield()
    DB = GestionDB.DB()

    for IDfacture in listeFactures:

        # Modification IDlot
        if "IDlot" in dict_valeurs :
            DB.ReqMAJ("factures", [("IDlot", dict_valeurs["IDlot"]), ], "IDfacture", IDfacture)

        # Modification Date émission
        if "date_emission" in dict_valeurs :
            DB.ReqMAJ("factures", [("date_emission", dict_valeurs["date_emission"]), ], "IDfacture", IDfacture)

        # Modification Date_échéance
        if "date_echeance" in dict_valeurs :
            DB.ReqMAJ("factures", [("date_echeance", dict_valeurs["date_echeance"]), ], "IDfacture", IDfacture)

        # Modification Mentions
        if "mention1" in dict_valeurs :
            DB.ReqMAJ("factures", [("mention1", dict_valeurs["mention1"]), ], "IDfacture", IDfacture)
        if "mention2" in dict_valeurs :
            DB.ReqMAJ("factures", [("mention2", dict_valeurs["mention2"]), ], "IDfacture", IDfacture)
        if "mention3" in dict_valeurs :
            DB.ReqMAJ("factures", [("mention3", dict_valeurs["mention3"]), ], "IDfacture", IDfacture)

    DB.Close()
    del dlgAttente
    return True


def Calculer_datamatrix(dictCompte):
    dict_pes = dictCompte["dict_pes"]
    elements = []

    # 1-40 : Données métiers (40 caractères)
    elements.append(" " * 40)

    # 41-64 : Zone d'espaces (24 caractères)
    elements.append(" " * 24)

    # 65-67 : Code établissement (3 caractères)
    if not dict_pes["pes_lot_code_etab"]:
        return ""
    code_etab = DATA_Codes_etab.Rechercher(str(dict_pes["pes_lot_code_etab"]))
    elements.append("%03d" % int(code_etab))

    # 68 : Code période (1 caractère)
    elements.append(str(dict_pes["pes_lot_mois"])[:1])

    # 69-71 : Deux premiers caractères du CodProdLoc (3 caractères)
    elements.append("%03d" % int(DATA_Codes_etab.Rechercher(str(dict_pes["pes_lot_code_produit"])[:2])))

    # 72-73 : deux zéros
    elements.append("00")

    # 74-75 : Deux derniers chiffres de la balise Exerc (2 caractères)
    elements.append(str(dict_pes["pes_lot_exercice"])[-2:])

    # 76 : Clé 5 (modulo 11)
    base = int("".join(elements[-5:]))
    cle = str(11 - (base % 11))[-1:]
    elements.append(cle)

    # 77-82 : Code émetteur (6 caractères)
    elements.append("940033")

    # 83-86 : Code établissement (=0001)
    elements.append("0001")

    # 87-88 : Clé 3 (Modulo 100)
    base = "".join(elements[-2:])
    cle = sum([rang * int(valeur) for rang, valeur in enumerate(base[::-1], 1)]) % 100
    elements.append("%02d" % cle)

    # 89 : Espace
    elements.append(" ")

    # 92-115 : Référence de l'opération (24 caractères)
    id_poste = "%06d" % int(dict_pes["pes_lot_id_poste"])

    num_dette = "%015d" % int(dictCompte["num_facture"])

    cle2 = GetCle_modulo23((str(dict_pes["pes_lot_exercice"])[-2:], str(dict_pes["pes_lot_mois"]), "00", u"{:0>13}".format(dictCompte["num_facture"])))
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXY"
    cle2 = "%02d" % (alphabet.index(cle2) + 1)
    elements.append("".join([cle2, num_dette, id_poste, "4"]))

    # 116 : Code document (=9)
    elements.append("9")

    # 90-91 : Clé 2 (Modulo 100)
    base = "".join(elements[-2:])
    cle = sum([rang * int(valeur) for rang, valeur in enumerate(base[::-1], 1)]) % 100
    elements.insert(len(elements)-2, "%02d" % cle)

    # 119 : Code nature (=8)
    elements.append("8")

    # 120-121 : Code de traitement BDF (=06)
    elements.append("06")

    # 122 : Espace
    elements.append(" ")

    # 123-130 : Montant (8 caractères)
    montant = "{: >8}".format(("%.2f" % dictCompte["solde"]).replace(".", ""))
    elements.append(montant)

    # 117-118 : Clé 1 (Modulo 100)
    base1 = "".join(elements[-4:-2]).replace(" ", "0")
    somme1 = sum([rang * int(valeur) for rang, valeur in enumerate(base1[::-1], 9)])

    base2 = "".join(elements[-1]).replace(" ", "0")
    somme2 = sum([rang * int(valeur) for rang, valeur in enumerate(base2[::-1], 1)])

    cle = (somme1 + somme2) % 100
    elements.insert(len(elements)-4, "%02d" % cle)

    # Finalisation du datamatrix
    datamatrix = "".join(elements)
    return datamatrix







if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    # Test du module Facturation :
    facturation = Facturation()

    # Recherche de factures à générer
    #liste_factures = facturation.GetDonnees(liste_activites=[1, 2, 3], date_debut=datetime.date(2017, 1, 1), date_fin=datetime.date(2017, 1, 31), date_edition=datetime.date.today(), date_echeance=datetime.date(2017, 2, 28), prestations=["consommation", "cotisation", "autre"] )
    #for IDfacture, facture in liste_factures.iteritems() :
    #    print "Facture =", IDfacture, facture
    #print "Nbre factures trouvees =", len(liste_factures)

    # Affichage d'une facture
    print("resultats =", facturation.Impression(listeFactures=[1,]))

    app.MainLoop()
