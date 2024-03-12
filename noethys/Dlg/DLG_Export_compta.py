#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import datetime
import codecs
import copy
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Utils import UTILS_Dates
from Utils import UTILS_Titulaires
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
import FonctionsPerso
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils import UTILS_Parametres
import six, csv
import wx.propgrid as wxpg
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox
from Ctrl import CTRL_Propertygrid
from Utils import UTILS_XImport
import xlsxwriter
import decimal
from Dlg import DLG_Messagebox


def FormateDate(dateDD=None, format="%d/%m/%Y") :
    if dateDD == None or dateDD == "" :
        return ""
    else :
        return dateDD.strftime(format)
    
def FormateLibelle(texte="", valeurs=[]):
    for motcle, valeur in valeurs :
        texte = texte.replace(motcle, valeur)
    return texte

def GetKeysDictTries(dictValeurs={}, key=""):
    """ Renvoie une liste de keys de dictionnaire triés selon la sous key indiquée """
    listeKeys = []
    for ID, dictTemp in dictValeurs.items() :
        listeKeys.append((dictTemp[key], ID))
    listeKeys.sort()
    listeResultats = []
    for keyTemp, ID in listeKeys() :
        listeResultats.append(ID)
    return listeResultats
    
    

def Export_ebp_compta(ligne, dictParametres, numLigne, typeComptable=None):
    """ Formate les lignes au format EBP Compta """
    montant = ligne["montant"]
    
    def GetSens(montant, sens):
        if FloatToDecimal(montant) < FloatToDecimal(0.0) :
            if isinstance(montant, str):
                montant = FloatToDecimal(montant)
            montant = -montant
            if sens == "D" : 
                sens = "C"
            else :
                sens = "D"
        return montant, sens            
        
    
    # Total prestations
    if ligne["type"] == "total_prestations" :
        montant, sens = GetSens(montant, "D")
        ligneTemp = [
            str(numLigne),
            FormateDate(dictParametres["date_fin"], "%d%m%y"),
            dictParametres["journal_ventes"],
            dictParametres["code_clients"],
            "",
            u'"%s"' % ligne["libelle"],
            "",
            str(montant),
            sens,
            "",
            "EUR",
            ]

    # Prestation
    if ligne["type"] == "prestation" :
        montant, sens = GetSens(montant, "C")
        ligneTemp = [
            str(numLigne),
            FormateDate(dictParametres["date_fin"], "%d%m%y"),
            dictParametres["journal_ventes"],
            ligne["code_compta"],
            "",
            ligne["intitule"],
            "",
            str(montant),
            sens,
            "",
            "EUR",
            ]
    
    # Dépôt
    if ligne["type"] == "depot" :
        montant, sens = GetSens(montant, "D")
        ligneTemp = [
            str(numLigne),
            FormateDate(ligne["date_depot"], "%d%m%y"),
            dictParametres["journal_%s" % typeComptable],
            ligne["code_compta"],
            "",
            u'"%s"' % ligne["libelle"],
            u'""',
            str(montant),
            sens,
            "",
            "EUR",
            ]

    # Total par mode de règlement
    if ligne["type"] == "total_mode" :
        montant, sens = GetSens(montant, "D")
        ligneTemp = [
            str(numLigne),
            FormateDate(dictParametres["date_fin"], "%d%m%y"),
            dictParametres["journal_%s" % typeComptable],
            ligne["code_compta"],
            "",
            u'"%s"' % ligne["libelle"],
            u'""',
            str(montant),
            sens,
            "",
            "EUR",
            ]

    # Règlements
    if ligne["type"] == "total_reglements" :
        montant, sens = GetSens(montant, "C")
        ligneTemp = [
            str(numLigne),
            FormateDate(dictParametres["date_fin"], "%d%m%y"),
            dictParametres["journal_%s" % typeComptable],
            dictParametres["code_clients"],
            "",
            u'"%s"' % ligne["libelle"],
            u"",
            str(montant),
            sens,
            "",
            "EUR",
            ]

    return ",".join(ligneTemp)

# ----------------------------------------------------------------------------------------------------------------------------------

class Donnees():
    def __init__(self, dictParametres={}):
        self.date_debut = dictParametres["date_debut"]
        self.date_fin =dictParametres["date_fin"]
        self.dictParametres = dictParametres
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires()
    
    def GetVentes(self):
        listeLignes = []

        if self.dictParametres["option_type_periode"] == 0 :
            condition = "prestations.date_valeur>='%s' AND prestations.date_valeur<='%s'" % (self.date_debut, self.date_fin)
        else :
            condition = "prestations.date>='%s' AND prestations.date<='%s'" % (self.date_debut, self.date_fin)

        # Récupération des prestations 
        DB = GestionDB.DB() 
        req = """
        SELECT prestations.IDprestation, prestations.date, categorie, prestations.code_compta, tarifs.code_compta,
        prestations.label, prestations.montant, 
        prestations.IDactivite, activites.nom, activites.abrege, activites.code_comptable,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, prestations.IDfacture,
        prestations.forfait, prestations.IDcategorie_tarif,
        prestations.IDindividu, individus.nom, individus.prenom,
        types_cotisations.code_comptable
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON prestations.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        LEFT JOIN cotisations ON cotisations.IDprestation = prestations.IDprestation
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        WHERE %s
        GROUP BY prestations.IDprestation, types_cotisations.IDtype_cotisation
        ORDER BY prestations.date
        ;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq() 
        DB.Close()
        listePrestations = []
        for IDprestation, datePrestation, categorie, code_compta_prestation, code_compta_tarif, label, montant, IDactivite, nomActivite, nomAbregeActivite, CodeComptableActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, forfait, IDcategorie_tarif, IDindividu, nomIndividu, prenomIndividu, code_comptable_type_cotisation in listeDonnees :
            if nomIndividu == None : nomIndividu = ""
            if prenomIndividu == None : prenomIndividu = ""
            if nomActivite == None : nomActivite = ""
            if nomAbregeActivite == None : nomAbregeActivite = ""
            if nomTarif == None : nomTarif = ""
            dictTemp = {
                "IDprestation" : IDprestation, "date_prestation" : UTILS_Dates.DateEngEnDateDD(datePrestation), "label" : label, "montant" : FloatToDecimal(montant),
                "code_compta_prestation" : code_compta_prestation, "code_compta_tarif" : code_compta_tarif,
                "IDactivite" : IDactivite, "nomActivite" : nomActivite, "nomAbregeActivite" : nomAbregeActivite, "code_compta_activite" : CodeComptableActivite,
                "IDtarif" : IDtarif, "nomTarif" : nomTarif, "nomCategorieTarif" : nomCategorieTarif, "forfait" : forfait, "IDcategorie_tarif" : IDcategorie_tarif,
                "IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu, "code_compta_type_cotisation" : code_comptable_type_cotisation,
                }
            listePrestations.append(dictTemp)
            
        # -------------- Ventes crédit : Ventilation par nom de prestation  ---------------
        dictCodesPrestations = {}
        for dictPrestation in listePrestations :
            
            if dictPrestation["montant"] != FloatToDecimal(0.0) :
                                
                # Si mode regroupement par type de prestation
                if self.dictParametres["option_regroupement_prestations"] == 0 :
                    if dictPrestation["nomAbregeActivite"] in (None, ""):
                        labelActivite = ""
                    else :
                        labelActivite = u"%s - " % dictPrestation["nomAbregeActivite"]
                    intituleTemp = "%s%s" % (labelActivite, dictPrestation["label"])
                
                # Si mode regroupement par activité
                if self.dictParametres["option_regroupement_prestations"] == 1 :
                    if dictPrestation["nomActivite"] != "" :
                        intituleTemp = dictPrestation["nomActivite"]
                    else :
                        intituleTemp = dictPrestation["label"]
                    
                # Mémorisation de la prestation
                if (intituleTemp in dictCodesPrestations) == False :
                    
                    # Recherche le code compta de la prestation
                    code_compta = dictPrestation["code_compta_prestation"]
                    if code_compta == None : 
                        code_compta = ""
                    if code_compta in (None, ""):
                        if dictPrestation["code_compta_tarif"] not in (None, ""):
                            code_compta = dictPrestation["code_compta_tarif"]
                        else :
                            if dictPrestation["code_compta_activite"] not in (None, ""):
                                code_compta = dictPrestation["code_compta_activite"]
                            else :
                                if dictPrestation["code_compta_type_cotisation"] not in (None, ""):
                                    code_compta = dictPrestation["code_compta_type_cotisation"]
                    if code_compta == "" :
                        code_compta = self.dictParametres["code_ventes"]
                        
                    # Mémorisation de la prestation
                    dictCodesPrestations[intituleTemp] = {"code_compta" : code_compta, "montant" : FloatToDecimal(0.0)}
                    
                dictCodesPrestations[intituleTemp]["montant"] += dictPrestation["montant"]

        # Vérification des codes comptables
        if len(dictCodesPrestations) > 0 :
            dlg = Dialog_codes(None, dictCodes=dictCodesPrestations, keyStr=True, titre=_(u"Vérification des codes comptables des prestations"))
            if dlg.ShowModal() == wx.ID_OK :
                dictCodesTemp = dlg.GetCodes() 
                dlg.Destroy() 
            else :
                dlg.Destroy() 
                return False
            for intitule, code_compta in dictCodesTemp.items() :
                dictCodesPrestations[intitule]["code_compta"] = code_compta
            
        # Mémorisation des lignes prestations
        listeIntitules = list(dictCodesPrestations.keys()) 
        listeIntitules.sort() 
        
        for intitule in listeIntitules :
            dictCode = dictCodesPrestations[intitule]

            # Formatage libellé prestation
            libelle = FormateLibelle(
                texte = self.dictParametres["format_prestation"],
                valeurs = [
                    ("{NOM_PRESTATION}", intitule), 
                    ("{DATE_DEBUT}", UTILS_Dates.DateDDEnFr(self.date_debut)),
                    ("{DATE_FIN}", UTILS_Dates.DateDDEnFr(self.date_fin)),
                    ])

            listeLignes.append({
                "type" : "prestation",
                "intitule" : libelle,
                "code_compta" : dictCode["code_compta"],
                "montant" : dictCode["montant"],
                })


        # -------------- Ventes débit : Total de la facturation ---------------
        montantTotal = FloatToDecimal(0.0)
        for labelPrestation, dictTemp in dictCodesPrestations.items() :
            if dictTemp["code_compta"] != "" :
                montantTotal += dictTemp["montant"]
            
        libelle = FormateLibelle(
            texte = self.dictParametres["format_total_ventes"],
            valeurs = [
                ("{DATE_DEBUT}", UTILS_Dates.DateDDEnFr(self.date_debut)),
                ("{DATE_FIN}", UTILS_Dates.DateDDEnFr(self.date_fin)),
                ])
        
        # Mémorisation ligne 
        listeLignes.append({
            "type" : "total_prestations",
            "libelle" : libelle,
            "montant" : montantTotal,
            })

        return listeLignes


    def GetReglements_Modes(self, typeComptable="banque"):
        DB = GestionDB.DB() 
        
        # Condition de sélection des règlements
        if self.dictParametres["option_selection_reglements"] == 0 :
            condition = "reglements.IDdepot IS NOT NULL AND depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s' AND modes_reglements.type_comptable='%s' " % (self.date_debut, self.date_fin, typeComptable)
        else :
            condition = "reglements.date>='%s' AND reglements.date<='%s' AND modes_reglements.type_comptable='%s' " % (self.date_debut, self.date_fin, typeComptable)

        # Récupération des règlements
        req = """SELECT 
        reglements.IDreglement, reglements.IDcompte_payeur, reglements.date, 
        reglements.IDmode, modes_reglements.label, 
        reglements.numero_piece, reglements.montant, 
        payeurs.IDpayeur, payeurs.nom, 
        numero_quittancier, reglements.IDcompte, date_differe, 
        encaissement_attente, 
        reglements.IDdepot, depots.date, depots.nom,  
        date_saisie, comptes_payeurs.IDfamille,
        modes_reglements.code_compta,
        comptes_bancaires.numero, comptes_bancaires.nom
        FROM reglements
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        LEFT JOIN comptes_bancaires ON comptes_bancaires.IDcompte = reglements.IDcompte
        WHERE %s
        GROUP BY reglements.IDreglement
        ORDER BY modes_reglements.label;
        """ % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        dictModesReglements = {}
        for IDreglement, IDcompte_payeur, dateReglement, IDmode, labelMode, numero_piece, montant, IDpayeur, nomPayeur, numero_quittancier, IDcompte, date_differe, attente, IDdepot, dateDepot, nomDepot, date_saisie, IDfamille, code_compta_mode, numeroCompte, nomCompte in listeDonnees :
            if code_compta_mode in (None, "") :
                code_compta = self.dictParametres["code_%s" % typeComptable]
            else :
                code_compta = code_compta_mode
            if (IDmode in dictModesReglements) == False :
                dictModesReglements[IDmode] = {
                    "IDmode" : IDmode, "label" : labelMode, "code_compta" : code_compta, "montant" : FloatToDecimal(0.0), 
                    "nbreReglements" : 0, "numeroCompte" : numeroCompte, "nomCompte" : nomCompte,
                    }
            dictModesReglements[IDmode]["montant"] += FloatToDecimal(montant)
            dictModesReglements[IDmode]["nbreReglements"] += 1

        # Vérification des codes comptables
        if len(dictModesReglements) > 0 :
            dlg = Dialog_codes(None, dictCodes=dictModesReglements, keyStr=False, titre=_(u"Vérification des codes comptables des modes de règlements de type %s") % typeComptable)
            if dlg.ShowModal() == wx.ID_OK :
                dictCodesTemp = dlg.GetCodes() 
                dlg.Destroy() 
            else :
                dlg.Destroy() 
                return False
            for ID, code_compta in dictCodesTemp.items() :
                dictModesReglements[int(ID)]["code_compta"] = code_compta

        # Analyse
        listeLignes = []
        for IDmode, dictMode in dictModesReglements.items() :
            
            if dictMode["code_compta"] != "" :
            
                # Formatage libellé dépôt
                libelle = FormateLibelle(
                    texte = self.dictParametres["format_mode"],
                    valeurs = [
                        ("{IDMODE}", str(dictMode["IDmode"])),
                        ("{NOM_MODE}", dictMode["label"]), 
                        ("{CODE_COMPTABLE}", dictMode["code_compta"]),
                        ("{NBRE_REGLEMENTS}", str(dictMode["nbreReglements"])),
                        ])
                
                # Mémorisation ligne
                listeLignes.append({
                    "type" : "total_mode",
                    "IDmode" : dictMode["IDmode"],
                    "libelle" : libelle,
                    "nom_mode" : dictMode["label"],
                    "code_compta" : code_compta,
                    "montant" : str(dictMode["montant"]),
                    "numeroCompte" : dictMode["numeroCompte"],
                    "nomCompte" : dictMode["nomCompte"],
                    })
        
        # Total des règlements
        if len(listeLignes) > 0 :

            montantTotal = FloatToDecimal(0.0)
            for IDmode, dictTemp in dictModesReglements.items() :
                if dictTemp["code_compta"] != "" :
                    montantTotal += dictTemp["montant"]

            libelle = FormateLibelle(
                texte = self.dictParametres["format_total_reglements"],
                valeurs = [
                    ("{DATE_DEBUT}", UTILS_Dates.DateDDEnFr(self.date_debut)),
                    ("{DATE_FIN}", UTILS_Dates.DateDDEnFr(self.date_fin)),
                    ])

            listeLignes.append({
                "type" : "total_reglements",
                "libelle" : libelle,
                "montant" : str(montantTotal),
                })

        return listeLignes
        

    def GetReglements_Depots(self, typeComptable="banque"):
        DB = GestionDB.DB() 
        
        # Condition de sélection des règlements
        if self.dictParametres["option_selection_reglements"] == 0 :
            condition = "reglements.IDdepot IS NOT NULL AND depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s' AND modes_reglements.type_comptable='%s' " % (self.date_debut, self.date_fin, typeComptable)
        else :
            condition = "reglements.date>='%s' AND reglements.date<='%s' AND modes_reglements.type_comptable='%s' " % (self.date_debut, self.date_fin, typeComptable)

        # Dépôts
        req = """SELECT 
        depots.IDdepot, depots.date, depots.nom, depots.code_compta, reglements.IDmode, modes_reglements.label, modes_reglements.type_comptable,
        SUM(reglements.montant), COUNT(reglements.IDreglement),
        comptes_bancaires.numero, comptes_bancaires.nom
        FROM depots
        LEFT JOIN reglements ON reglements.IDdepot = depots.IDdepot
        LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
        LEFT JOIN comptes_bancaires ON comptes_bancaires.IDcompte = depots.IDcompte
        WHERE %s
        GROUP BY depots.IDdepot, reglements.IDmode
        ORDER BY depots.date;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDepots = {}
        montantTotal = FloatToDecimal(0.0)
        for IDdepot, date, nomDepot, code_compta, IDmode, nomMode, type_comptable, montant, nbreReglements, numeroCompte, nomCompte in listeDonnees :
            if code_compta in (None, "") :
                code_compta = self.dictParametres["code_%s" % typeComptable]
            label = u"%s (%s)" % (nomDepot, FormateDate(UTILS_Dates.DateEngEnDateDD(date)))
            dictTemp = {
                "IDdepot" : IDdepot, "date_depot" : UTILS_Dates.DateEngEnDateDD(date), "nom_depot" : nomDepot, "code_compta" : code_compta, "IDmode" : IDmode, "nomMode" : nomMode, 
                "type_comptable" : type_comptable, "montant" : FloatToDecimal(montant), "nbreReglements" : nbreReglements, "label" : label,
                "numeroCompte" : numeroCompte, "nomCompte" : nomCompte,
                }
            dictDepots[IDdepot] = dictTemp
            montantTotal += FloatToDecimal(montant)
        
        # Vérification des codes comptables
        if len(dictDepots) > 0 :
            dlg = Dialog_codes(None, dictCodes=dictDepots, keyStr=False, titre=_(u"Vérification des codes comptables des dépôts de type %s") % typeComptable)
            if dlg.ShowModal() == wx.ID_OK :
                dictCodesTemp = dlg.GetCodes() 
                dlg.Destroy() 
            else :
                dlg.Destroy() 
                return False
            for ID, code_compta in dictCodesTemp.items() :
                dictDepots[int(ID)]["code_compta"] = code_compta

        # Analyse
        listeLignes = []

        for IDdepot, dictDepot in dictDepots.items() :

            if dictDepot["code_compta"] != "" :

                # Formatage libellé dépôt
                libelle = FormateLibelle(
                    texte = self.dictParametres["format_depot"],
                    valeurs = [
                        ("{IDDEPOT}", str(dictDepot["IDdepot"])),
                        ("{NOM_DEPOT}", dictDepot["nom_depot"]), 
                        ("{DATE_DEPOT}", FormateDate(dictDepot["date_depot"])), 
                        ("{MODE_REGLEMENT}", dictDepot["nomMode"]),
                        ("{TYPE_COMPTABLE}", dictDepot["type_comptable"]),
                        ("{NBRE_REGLEMENTS}", str(dictDepot["nbreReglements"])),
                        ])
                
                # Mémorisation ligne dépôt
                listeLignes.append({
                    "type" : "depot",
                    "IDdepot" : dictDepot["IDdepot"],
                    "libelle" : libelle,
                    "nom_depot" : dictDepot["nom_depot"],
                    "date_depot" : dictDepot["date_depot"],
                    "mode_reglement" : dictDepot["nomMode"],
                    "montant" : str(dictDepot["montant"]),
                    "code_compta" : dictDepot["code_compta"],
                    "numeroCompte" : dictDepot["numeroCompte"],
                    "nomCompte" : dictDepot["nomCompte"],
                    })
                                
        # Total des règlements
        if len(listeLignes) > 0 :
            
            montantTotal = FloatToDecimal(0.0)
            for IDdepot, dictTemp in dictDepots.items() :
                if dictTemp["code_compta"] != "" :
                    montantTotal += dictTemp["montant"]

            libelle = FormateLibelle(
                texte = self.dictParametres["format_total_reglements"],
                valeurs = [
                    ("{DATE_DEBUT}", UTILS_Dates.DateDDEnFr(self.date_debut)),
                    ("{DATE_FIN}", UTILS_Dates.DateDDEnFr(self.date_fin)),
                    ])

            listeLignes.append({
                "type" : "total_reglements",
                "libelle" : libelle,
                "montant" : str(montantTotal),
                })

        return listeLignes



##    def GetReglements(self, typeComptable="banque"):
##        DB = GestionDB.DB() 
##        
##        # Dépôts de règlements
##        req = """SELECT 
##        depots.IDdepot, depots.date, depots.nom, reglements.IDmode, modes_reglements.label, modes_reglements.type_comptable,
##        SUM(reglements.montant), COUNT(reglements.IDreglement)
##        FROM depots
##        LEFT JOIN reglements ON reglements.IDdepot = depots.IDdepot
##        LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
##        WHERE depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s' AND modes_reglements.type_comptable='%s'
##        GROUP BY depots.IDdepot, reglements.IDmode
##        ORDER BY depots.date;""" % (self.date_debut, self.date_fin, typeComptable)
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        listeDepots = []
##        for IDdepot, date, nomDepot, IDmode, nomMode, type_comptable, montant, nbreReglements in listeDonnees :
##            listeDepots.append({
##                "IDdepot" : IDdepot, "date_depot" : UTILS_Dates.DateEngEnDateDD(date), "nom_depot" : nomDepot, "IDmode" : IDmode, "nomMode" : nomMode, 
##                "type_comptable" : type_comptable, "montant" : FloatToDecimal(montant), "nbreReglements" : nbreReglements, 
##                })
##        
##        # Règlements
##        req = """SELECT 
##        reglements.IDreglement, reglements.IDcompte_payeur, reglements.date, 
##        reglements.IDmode, modes_reglements.label, 
##        reglements.numero_piece, reglements.montant, 
##        payeurs.IDpayeur, payeurs.nom, 
##        numero_quittancier, reglements.IDcompte, date_differe, 
##        encaissement_attente, 
##        reglements.IDdepot, depots.date, depots.nom,  
##        date_saisie, comptes_payeurs.IDfamille,
##        modes_reglements.code_compta
##        FROM reglements
##        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
##        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
##        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
##        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
##        WHERE reglements.IDdepot IS NOT NULL AND depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s'
##        GROUP BY reglements.IDreglement
##        ORDER BY reglements.date;
##        """ % (self.date_debut, self.date_fin)
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close() 
##        dictReglementsDepots = {}
##        for IDreglement, IDcompte_payeur, dateReglement, IDmode, labelMode, numero_piece, montant, IDpayeur, nomPayeur, numero_quittancier, IDcompte, date_differe, attente, IDdepot, dateDepot, nomDepot, date_saisie, IDfamille, code_compta_mode in listeDonnees :
##            if dictReglementsDepots.has_key(IDdepot) == False :
##                dictReglementsDepots[IDdepot] = []
##            if code_compta_mode == None :
##                code_compta_mode = ""
##            dictReglementsDepots[IDdepot].append({
##                "IDreglement" : IDreglement, "IDcompte_payeur" : IDcompte_payeur, "dateReglement" : UTILS_Dates.DateEngEnDateDD(dateReglement), "IDmode" : IDmode, "labelMode" : labelMode, "numero_piece" : numero_piece, 
##                "montant" : FloatToDecimal(montant), "IDpayeur" : IDpayeur, "nomPayeur" : nomPayeur, "numero_quittancier" : numero_quittancier, "IDcompte" : IDcompte, "date_differe" : UTILS_Dates.DateEngEnDateDD(date_differe), 
##                "attente" : attente, "dateDepot" : UTILS_Dates.DateEngEnDateDD(dateDepot), "nomDepot" : nomDepot, "date_saisie" : date_saisie, "IDfamille" : IDfamille, "code_compta_mode" : code_compta_mode,
##                })
##        
##        # Analyse des dépôts
##        listeLignes = []
##        for dictDepot in listeDepots :
##            
##            # Formatage libellé dépôt
##            libelle_depot = self.dictParametres["format_depot"]
##            listeMotsCles = [
##                ("{IDDEPOT}", str(dictDepot["IDdepot"])),
##                ("{NOM_DEPOT}", dictDepot["nom_depot"]), 
##                ("{DATE_DEPOT}", FormateDate(dictDepot["date_depot"])), 
##                ("{MODE_REGLEMENT}", dictDepot["nomMode"]),
##                ("{TYPE_COMPTABLE}", dictDepot["type_comptable"]),
##                ("{NBRE_REGLEMENTS}", str(dictDepot["nbreReglements"])),
##                ]
##            for motcle, valeur in listeMotsCles :
##                libelle_depot = libelle_depot.replace(motcle, valeur)
##            
##            # Mémorisation ligne dépôt
##            listeLignes.append({
##                "type" : "depot",
##                "IDdepot" : dictDepot["IDdepot"],
##                "libelle_depot" : libelle_depot,
##                "nom_depot" : dictDepot["nom_depot"],
##                "date_depot" : dictDepot["date_depot"],
##                "mode_reglement" : dictDepot["nomMode"],
##                "montant" : str(dictDepot["montant"]),
##                })
##                        
##            # Analyse des règlements
##            if dictReglementsDepots.has_key(dictDepot["IDdepot"]) :
##                for dictReglement in dictReglementsDepots[dictDepot["IDdepot"]] :
##
##                    if self.dictTitulaires.has_key(dictReglement["IDfamille"]) :
##                        nomFamille = self.dictTitulaires[dictReglement["IDfamille"]]["titulairesSansCivilite"]
##                    else :
##                        nomFamille = ""
##
##                    # Formatage libellé Règlement
##                    libelle_reglement = self.dictParametres["format_reglement"]
##                    listeMotsCles = [
##                        ("{IDREGLEMENT}", str(dictReglement["IDreglement"])),
##                        ("{NOM_FAMILLE}", nomFamille),
##                        ("{DATE}", FormateDate(dictReglement["dateReglement"])),
##                        ("{MODE_REGLEMENT}", dictReglement["labelMode"]),
##                        ("{NUMERO_PIECE}", dictReglement["numero_piece"]),
##                        ("{NOM_PAYEUR}", dictReglement["nomPayeur"]),
##                        ("{NUMERO_QUITTANCIER}", dictReglement["numero_quittancier"]),
##                        ("{DATE_DEPOT}", FormateDate(dictReglement["dateDepot"])),
##                        ("{NOM_DEPOT}", dictReglement["nomDepot"]),
##                        ]
##                    for motcle, valeur in listeMotsCles :
##                        if valeur == None : valeur = ""
##                        libelle_reglement = libelle_reglement.replace(motcle, valeur)
##
##                    listeLignes.append({
##                        "type" : "reglement",
##                        "IDreglement" : dictReglement["IDreglement"],
##                        "dateReglement" : dictReglement["dateReglement"],
##                        "nomFamille" : nomFamille,
##                        "libelle_reglement" : libelle_reglement,
##                        "IDmode" : dictReglement["IDmode"],
##                        "labelMode" : dictReglement["labelMode"],
##                        "numero_piece" : dictReglement["numero_piece"],
##                        "montant" : dictReglement["montant"],
##                        "nomPayeur" : dictReglement["nomPayeur"],
##                        "numero_quittancier" : dictReglement["numero_quittancier"],
##                        "date_differe" : dictReglement["date_differe"],
##                        "attente" : dictReglement["attente"],
##                        "date_depot" : dictReglement["dateDepot"],
##                        "nom_depot" : dictReglement["nomDepot"],
##                        })
##
##        return listeLignes
##        
        
        
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    
##class Donnees():
##    def __init__(self, dictParametres={}):
##        self.date_debut = dictParametres["date_debut"]
##        self.date_fin =dictParametres["date_fin"]
##        self.dictParametres = dictParametres
##        self.dictTitulaires = UTILS_Titulaires.GetTitulaires()
##    
##    def GetVentes(self):
##        DB = GestionDB.DB() 
##        
##        dlgAttente = wx.BusyInfo(_(u"Recherche des données en cours..."), None)
##        wx.Yield() 
##        
##        # Récupération des factures
##        req = """
##        SELECT factures.IDfacture, factures.numero, factures.IDcompte_payeur, comptes_payeurs.IDfamille,
##        factures.date_edition, factures.date_echeance, 
##        factures.date_debut, factures.date_fin, factures.total, factures.regle, factures.solde,
##        lots_factures.nom, familles.code_comptable
##        FROM factures
##        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
##        LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille
##        LEFT JOIN lots_factures ON lots_factures.IDlot = factures.IDlot
##        WHERE date_edition>='%s' AND date_edition<='%s'
##        GROUP BY factures.IDfacture
##        ORDER BY factures.date_edition
##        ;""" % (self.date_debut, self.date_fin)
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        listeFactures = []
##        for IDfacture, numero, IDcompte_payeur, IDfamille, date_edition, date_echeance, date_debut, date_fin, total, regle, solde, nomLot, code_comptable_famille in listeDonnees :
##            if nomLot == None : nomLot = ""
##            dictTemp = {
##                "IDfacture" : IDfacture, "numero" : numero, "IDcompte_payeur" : IDcompte_payeur, "IDfamille" : IDfamille,
##                "date_edition" : UTILS_Dates.DateEngEnDateDD(date_edition), "date_echeance" : UTILS_Dates.DateEngEnDateDD(date_echeance), 
##                "date_debut" : UTILS_Dates.DateEngEnDateDD(date_debut), "date_fin" : UTILS_Dates.DateEngEnDateDD(date_fin), 
##                "total" : FloatToDecimal(total), "regle" : FloatToDecimal(regle), "solde" : FloatToDecimal(solde), "nomLot" : nomLot, "code_comptable_famille" : code_comptable_famille,
##                }
##            listeFactures.append(dictTemp)
##
##        # Récupération des prestations des factures
##        req = """
##        SELECT prestations.IDprestation, prestations.date, categorie, prestations.code_compta, tarifs.code_compta,
##        prestations.label, prestations.montant, 
##        prestations.IDactivite, activites.nom, activites.abrege, activites.code_comptable,
##        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, prestations.IDfacture,
##        prestations.forfait, prestations.IDcategorie_tarif,
##        prestations.IDindividu, individus.nom, individus.prenom,
##        types_cotisations.code_comptable
##        FROM prestations
##        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
##        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
##        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
##        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
##        LEFT JOIN categories_tarifs ON prestations.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
##        LEFT JOIN cotisations ON cotisations.IDprestation = prestations.IDprestation
##        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
##        GROUP BY prestations.IDprestation
##        ORDER BY prestations.date
##        ;""" 
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq() 
##        dictPrestations = {}
##        for IDprestation, datePrestation, categorie, code_compta_prestation, code_compta_tarif, label, montant, IDactivite, nomActivite, nomAbregeActivite, CodeComptableActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, forfait, IDcategorie_tarif, IDindividu, nomIndividu, prenomIndividu, code_comptable_type_cotisation in listeDonnees :
##            if nomIndividu == None : nomIndividu = ""
##            if prenomIndividu == None : prenomIndividu = ""
##            if nomActivite == None : nomActivite = ""
##            if nomAbregeActivite == None : nomAbregeActivite = ""
##            if nomTarif == None : nomTarif = ""
##            dictTemp = {
##                "IDprestation" : IDprestation, "date_prestation" : UTILS_Dates.DateEngEnDateDD(datePrestation), "label" : label, "montant" : FloatToDecimal(montant),
##                "code_compta_prestation" : code_compta_prestation, "code_compta_tarif" : code_compta_tarif,
##                "IDactivite" : IDactivite, "nomActivite" : nomActivite, "nomAbregeActivite" : nomAbregeActivite, "code_compta_activite" : CodeComptableActivite,
##                "IDtarif" : IDtarif, "nomTarif" : nomTarif, "nomCategorieTarif" : nomCategorieTarif, "forfait" : forfait, "IDcategorie_tarif" : IDcategorie_tarif,
##                "IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu, "code_compta_type_cotisation" : code_comptable_type_cotisation,
##                }
##            if dictPrestations.has_key(IDfacture) == False :
##                dictPrestations[IDfacture] = []
##            dictPrestations[IDfacture].append(dictTemp)
##        
##        DB.Close()
##        
##        # Analyse des factures
##        listeLignes = []
##        listeCodesManquants = []
##        listeAnomalies = []
##        dictCodes = {}
##        for dictFacture in listeFactures :
##            
##            if dictFacture["total"] != FloatToDecimal(0.0) :
##                
##                if self.dictTitulaires.has_key(dictFacture["IDfamille"]) :
##                    nomFamille = self.dictTitulaires[dictFacture["IDfamille"]]["titulairesSansCivilite"]
##                else :
##                    nomFamille = ""
##                
##                # Formatage libellé facture
##                libelle_facture = self.dictParametres["format_facture"]
##                listeMotsCles = [
##                    ("{IDFACTURE}", str(dictFacture["IDfacture"])),
##                    ("{NOM_FAMILLE}", nomFamille), 
##                    ("{NUMERO}", str(dictFacture["numero"])),
##                    ("{DATE_EDITION}", FormateDate(dictFacture["date_edition"])),
##                    ("{DATE_ECHEANCE}", FormateDate(dictFacture["date_echeance"])),
##                    ("{DATE_DEBUT}", FormateDate(dictFacture["date_debut"])),
##                    ("{DATE_FIN}", FormateDate(dictFacture["date_fin"])),
##                    ("{NOM_LOT}", dictFacture["nomLot"]),
##                    ]
##                for motcle, valeur in listeMotsCles :
##                    libelle_facture = libelle_facture.replace(motcle, valeur)
##                
##                # Mémorisation ligne facture
##                listeLignes.append({
##                    "type" : "facture",
##                    "IDfacture" : IDfacture,
##                    "date_edition" : dictFacture["date_edition"],
##                    "libelle_facture" : libelle_facture,
##                    "numero" : dictFacture["numero"],
##                    "montant" : dictFacture["total"],
##                    "date_echeance" : dictFacture["date_echeance"],
##                    "famille" : nomFamille,
##                    "date_debut" : dictFacture["date_debut"],
##                    "date_fin" : dictFacture["date_fin"],
##                    "code_comptable_famille" : dictFacture["code_comptable_famille"],
##                    })
##
##                # Analyse des prestations
##                if dictPrestations.has_key(dictFacture["IDfacture"]) :
##                    totalPrestationsFacture = FloatToDecimal(0.0)
##                    for dictPrestation in dictPrestations[dictFacture["IDfacture"]] :
##                        
##                        if dictPrestation["montant"] != FloatToDecimal(0.0) :
##                            
##                            totalPrestationsFacture += dictPrestation["montant"]
##                            
##                            code_compta = dictPrestation["code_compta_prestation"]
##                            if code_compta == None : 
##                                code_compta = ""
##                            if code_compta in (None, ""):
##                                if dictPrestation["code_compta_tarif"] not in (None, ""):
##                                    code_compta = dictPrestation["code_compta_tarif"]
##                                else :
##                                    if dictPrestation["code_compta_activite"] not in (None, ""):
##                                        code_compta = dictPrestation["code_compta_activite"]
##                                    else :
##                                        if dictPrestation["code_compta_type_cotisation"] not in (None, ""):
##                                            code_compta = dictPrestation["code_compta_type_cotisation"]
##                            
##                            # Vérifie si code compta présent
##                            if dictPrestation["nomAbregeActivite"] in (None, ""):
##                                labelActivite = ""
##                            else :
##                                labelActivite = u"%s - " % dictPrestation["nomAbregeActivite"]
##                            intituleTemp = "%s%s" % (labelActivite, dictPrestation["label"])
##                            if code_compta == "" :
##                                if intituleTemp not in listeCodesManquants :
##                                    listeCodesManquants.append(intituleTemp)
##                                code_compta = self.dictParametres["code_ventes"]
##                            dictCodes[intituleTemp] = code_compta
##                            
##                            # Formatage libellé prestation
##                            libelle_prestation = self.dictParametres["format_prestation"]
##                            listeMotsCles = [
##                                ("{IDPRESTATION}", str(dictPrestation["IDprestation"])),
##                                ("{DATE}", FormateDate(dictPrestation["date_prestation"])),
##                                ("{LIBELLE}", dictPrestation["label"]),
##                                ("{ACTIVITE}", dictPrestation["nomActivite"]),
##                                ("{ACTIVITE_ABREGE}", dictPrestation["nomAbregeActivite"]),
##                                ("{TARIF}", dictPrestation["nomTarif"]),
##                                ("{INDIVIDU_NOM}", dictPrestation["nomIndividu"]),
##                                ("{INDIVIDU_PRENOM}", dictPrestation["prenomIndividu"]),
##                                ]
##                            for motcle, valeur in listeMotsCles :
##                                libelle_prestation = libelle_prestation.replace(motcle, valeur)
##
##                            listeLignes.append({
##                                "type" : "prestation",
##                                "date_prestation" : dictPrestation["date_prestation"],
##                                "date_facture" : dictFacture["date_edition"],
##                                "code_compta" : code_compta,
##                                "libelle_prestation" : libelle_prestation,
##                                "libelle_original" : dictPrestation["label"],
##                                "numero_facture" : dictFacture["numero"],
##                                "montant" : dictPrestation["montant"],
##                                "date_echeance" : dictFacture["date_echeance"],
##                                "individu_nom" : dictPrestation["nomIndividu"],
##                                "individu_prenom" : dictPrestation["prenomIndividu"],
##                                "intituleTemp" : intituleTemp,
##                                })
##                
##                # Vérifie que le total des prestations correspond au montant de la facture
##                if dictFacture["total"] != totalPrestationsFacture :
##                    listeAnomalies.append(_(u"- Le total des prestations de la facture n°%s du %s (%s) ne correspond pas au montant initial de la facture.") % (dictFacture["numero"], FormateDate(dictFacture["date_edition"], "%d/%m/%Y"), nomFamille) )
##                    
##        del dlgAttente
##        
##        # Affichage des anomalies
##        if len(listeAnomalies) > 0 :
##        
##            # Propose le correcteur d'anomalies
##            dlg = wx.MessageDialog(None, _(u"Des anomalies ont été détectées dans certaines factures.\n\nSouhaitez-vous lancer le correcteur d'anomalies afin de les corriger dès à présent (Conseillé) ?"), _(u"Anomalies"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
##            reponse = dlg.ShowModal() 
##            dlg.Destroy()
##            if reponse == wx.ID_YES :
##                import DLG_Depannage
##                dlg = DLG_Depannage.Dialog(None)
##                dlg.ShowModal() 
##                dlg.Destroy()
##            return False
##
##        # Affichage des codes comptables
##        dlg = Dialog_codes(None, donnees=dictCodes)
##        if dlg.ShowModal() == wx.ID_OK :
##            dictCodes = dlg.GetCodes() 
##            dlg.Destroy() 
##        else :
##            dlg.Destroy() 
##            return False
##        index = 0
##        for dictTemp in listeLignes :
##            if dictTemp["type"] == "prestation" :
##                intituleTemp = dictTemp["intituleTemp"] 
##                if dictCodes.has_key(intituleTemp) :
##                    listeLignes[index]["code_compta"] = dictCodes[intituleTemp]
##            index += 1
##            
##        # Recherche des prestations de la période non facturées
##        DB = GestionDB.DB() 
##        req = """SELECT IDprestation, date, label, montant, IDfamille, activites.abrege
##        FROM prestations
##        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
##        WHERE IDfacture IS NULL AND date>='%s' AND date<='%s'
##        ORDER BY date
##        ;""" % (self.date_debut, self.date_fin)
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq() 
##        DB.Close()
##        listePrestationsSansFactures = []
##        totalPrestationsSansFactures = FloatToDecimal(0.0)
##        for IDprestation, date, label, montant, IDfamille, abregeActivite in listeDonnees :
##            totalPrestationsSansFactures += FloatToDecimal(montant)
##            date = FormateDate(UTILS_Dates.DateEngEnDateDD(date), "%d/%m/%Y")
##            if self.dictTitulaires.has_key(IDfamille) :
##                nomFamille = self.dictTitulaires[IDfamille]["titulairesSansCivilite"]
##            else :
##                nomFamille = _(u"Famille inconnue")
##            montant = u"%.2f %s" % (montant, SYMBOLE)
##            if abregeActivite != None :
##                label = u"%s - %s" % (abregeActivite, label)
##            listePrestationsSansFactures.append(u"- %s : %s (%s | %s)" % (date, label, montant, nomFamille))
##        
##        if len(listePrestationsSansFactures) > 0 :
##            message1 = _(u"Attention, %d prestations (%s) de cette période n'apparaissent sur aucune facture. Ces prestations ne figureront pas dans les écritures comptables. Il est donc conseillé de quitter et générer depuis le menu Facturation les factures correspondantes avant de lancer l'export des écritures comptables.\n\nSouhaitez-vous quand même continuer ?") % (len(listePrestationsSansFactures), u"%.2f %s" % (totalPrestationsSansFactures, SYMBOLE))
##            message2 = u"\n" .join(listePrestationsSansFactures)
##            dlg = dialogs.MultiMessageDialog(None, message1, caption=_(u"Avertissement"), msg2=message2 + "\n\n\n", style = wx.ICON_EXCLAMATION | wx.OK | wx.CANCEL, icon=None, btnLabels={wx.ID_OK : _(u"Oui"), wx.ID_CANCEL : _(u"Non")})
##            reponse = dlg.ShowModal() 
##            dlg.Destroy() 
##            if reponse != wx.ID_OK :
##                return False
##        
##        return listeLignes
##
##
##    def GetReglements(self, typeComptable="banque"):
##        DB = GestionDB.DB() 
##        
##        # Dépôts de règlements
##        req = """SELECT 
##        depots.IDdepot, depots.date, depots.nom, reglements.IDmode, modes_reglements.label, modes_reglements.type_comptable,
##        SUM(reglements.montant), COUNT(reglements.IDreglement)
##        FROM depots
##        LEFT JOIN reglements ON reglements.IDdepot = depots.IDdepot
##        LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
##        WHERE depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s' AND modes_reglements.type_comptable='%s'
##        GROUP BY depots.IDdepot, reglements.IDmode
##        ORDER BY depots.date;""" % (self.date_debut, self.date_fin, typeComptable)
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        listeDepots = []
##        for IDdepot, date, nomDepot, IDmode, nomMode, type_comptable, montant, nbreReglements in listeDonnees :
##            listeDepots.append({
##                "IDdepot" : IDdepot, "date_depot" : UTILS_Dates.DateEngEnDateDD(date), "nom_depot" : nomDepot, "IDmode" : IDmode, "nomMode" : nomMode, 
##                "type_comptable" : type_comptable, "montant" : FloatToDecimal(montant), "nbreReglements" : nbreReglements, 
##                })
##        
##        # Règlements
##        req = """SELECT 
##        reglements.IDreglement, reglements.IDcompte_payeur, reglements.date, 
##        reglements.IDmode, modes_reglements.label, 
##        reglements.numero_piece, reglements.montant, 
##        payeurs.IDpayeur, payeurs.nom, 
##        numero_quittancier, reglements.IDcompte, date_differe, 
##        encaissement_attente, 
##        reglements.IDdepot, depots.date, depots.nom,  
##        date_saisie, comptes_payeurs.IDfamille
##        FROM reglements
##        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
##        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
##        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
##        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
##        WHERE reglements.IDdepot IS NOT NULL AND depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s'
##        GROUP BY reglements.IDreglement
##        ORDER BY reglements.date;
##        """ % (self.date_debut, self.date_fin)
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close() 
##        dictReglementsDepots = {}
##        for IDreglement, IDcompte_payeur, dateReglement, IDmode, labelMode, numero_piece, montant, IDpayeur, nomPayeur, numero_quittancier, IDcompte, date_differe, attente, IDdepot, dateDepot, nomDepot, date_saisie, IDfamille in listeDonnees :
##            if dictReglementsDepots.has_key(IDdepot) == False :
##                dictReglementsDepots[IDdepot] = []
##            dictReglementsDepots[IDdepot].append({
##                "IDreglement" : IDreglement, "IDcompte_payeur" : IDcompte_payeur, "dateReglement" : UTILS_Dates.DateEngEnDateDD(dateReglement), "IDmode" : IDmode, "labelMode" : labelMode, "numero_piece" : numero_piece, 
##                "montant" : FloatToDecimal(montant), "IDpayeur" : IDpayeur, "nomPayeur" : nomPayeur, "numero_quittancier" : numero_quittancier, "IDcompte" : IDcompte, "date_differe" : UTILS_Dates.DateEngEnDateDD(date_differe), 
##                "attente" : attente, "dateDepot" : UTILS_Dates.DateEngEnDateDD(dateDepot), "nomDepot" : nomDepot, "date_saisie" : date_saisie, "IDfamille" : IDfamille,
##                })
##        
##        # Analyse des dépôts
##        listeLignes = []
##        for dictDepot in listeDepots :
##            
##            # Formatage libellé dépôt
##            libelle_depot = self.dictParametres["format_depot"]
##            listeMotsCles = [
##                ("{IDDEPOT}", str(dictDepot["IDdepot"])),
##                ("{NOM_DEPOT}", dictDepot["nom_depot"]), 
##                ("{DATE_DEPOT}", FormateDate(dictDepot["date_depot"])), 
##                ("{MODE_REGLEMENT}", dictDepot["nomMode"]),
##                ("{TYPE_COMPTABLE}", dictDepot["type_comptable"]),
##                ("{NBRE_REGLEMENTS}", str(dictDepot["nbreReglements"])),
##                ]
##            for motcle, valeur in listeMotsCles :
##                libelle_depot = libelle_depot.replace(motcle, valeur)
##            
##            # Mémorisation ligne dépôt
##            listeLignes.append({
##                "type" : "depot",
##                "IDdepot" : dictDepot["IDdepot"],
##                "libelle_depot" : libelle_depot,
##                "nom_depot" : dictDepot["nom_depot"],
##                "date_depot" : dictDepot["date_depot"],
##                "mode_reglement" : dictDepot["nomMode"],
##                "montant" : str(dictDepot["montant"]),
##                })
##                        
##            # Analyse des règlements
##            if dictReglementsDepots.has_key(dictDepot["IDdepot"]) :
##                for dictReglement in dictReglementsDepots[dictDepot["IDdepot"]] :
##
##                    if self.dictTitulaires.has_key(dictReglement["IDfamille"]) :
##                        nomFamille = self.dictTitulaires[dictReglement["IDfamille"]]["titulairesSansCivilite"]
##                    else :
##                        nomFamille = ""
##
##                    # Formatage libellé Règlement
##                    libelle_reglement = self.dictParametres["format_reglement"]
##                    listeMotsCles = [
##                        ("{IDREGLEMENT}", str(dictReglement["IDreglement"])),
##                        ("{NOM_FAMILLE}", nomFamille),
##                        ("{DATE}", FormateDate(dictReglement["dateReglement"])),
##                        ("{MODE_REGLEMENT}", dictReglement["labelMode"]),
##                        ("{NUMERO_PIECE}", dictReglement["numero_piece"]),
##                        ("{NOM_PAYEUR}", dictReglement["nomPayeur"]),
##                        ("{NUMERO_QUITTANCIER}", dictReglement["numero_quittancier"]),
##                        ("{DATE_DEPOT}", FormateDate(dictReglement["dateDepot"])),
##                        ("{NOM_DEPOT}", dictReglement["nomDepot"]),
##                        ]
##                    for motcle, valeur in listeMotsCles :
##                        if valeur == None : valeur = ""
##                        libelle_reglement = libelle_reglement.replace(motcle, valeur)
##
##                    listeLignes.append({
##                        "type" : "reglement",
##                        "IDreglement" : dictReglement["IDreglement"],
##                        "dateReglement" : dictReglement["dateReglement"],
##                        "nomFamille" : nomFamille,
##                        "libelle_reglement" : libelle_reglement,
##                        "IDmode" : dictReglement["IDmode"],
##                        "labelMode" : dictReglement["labelMode"],
##                        "numero_piece" : dictReglement["numero_piece"],
##                        "montant" : dictReglement["montant"],
##                        "nomPayeur" : dictReglement["nomPayeur"],
##                        "numero_quittancier" : dictReglement["numero_quittancier"],
##                        "date_differe" : dictReglement["date_differe"],
##                        "attente" : dictReglement["attente"],
##                        "date_depot" : dictReglement["dateDepot"],
##                        "nom_depot" : dictReglement["nomDepot"],
##                        })
##
##        return listeLignes
##        
##        
##        
### -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Logiciel(BitmapComboBox):
    def __init__(self, parent, size=(-1,  -1)):
        BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        self.parent = parent
        self.listeFormats = [
            {"code": "ebp_compta", "label" : _(u"EBP Compta"), "image" : wx.Bitmap(Chemins.GetStaticPath('Images/48x48/Logiciel_ebp.png'), wx.BITMAP_TYPE_PNG)},
            {"code": "ciel_compta_ebp", "label" : _(u"CIEL Compta (Format EBP)"), "image" : wx.Bitmap(Chemins.GetStaticPath('Images/48x48/Logiciel_ciel.png'), wx.BITMAP_TYPE_PNG)},
            {"code": "ciel_compta_ximport", "label" : _(u"CIEL Compta (Format XImport)"), "image" : wx.Bitmap(Chemins.GetStaticPath('Images/48x48/Logiciel_ciel.png'), wx.BITMAP_TYPE_PNG)},
            {"code": "quadracompta", "label": _(u"QuadraCOMPTA"), "image": wx.Bitmap(Chemins.GetStaticPath('Images/48x48/Logiciel_quadra.png'), wx.BITMAP_TYPE_PNG)},
            {"code": "cerig", "label": _(u"Cerig"), "image": wx.Bitmap(Chemins.GetStaticPath('Images/48x48/Logiciel_cerig.png'), wx.BITMAP_TYPE_PNG)},
        ]
        for dictFormat in self.listeFormats :
            self.Append(dictFormat["label"], dictFormat["image"], dictFormat["label"])
        self.SetSelection(0)
        self.Importation() 
    
    def SetCode(self, code=""):
        index = 0
        for dictFormat in self.listeFormats :
            if dictFormat["code"] == code :
                 self.SetSelection(index)
            index += 1

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeFormats[index]["code"]
    
    def Importation(self):
        format = UTILS_Parametres.Parametres(mode="get", categorie="export_compta", nom="nom_format", valeur="ebp_compta")
        self.SetCode(format) 

    def Sauvegarde(self):
        UTILS_Parametres.Parametres(mode="set", categorie="export_compta", nom="nom_format", valeur=self.GetCode())
        
# -------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Parametres(CTRL_Propertygrid.CTRL):
    def __init__(self, parent, listeDonnees=[]):
        CTRL_Propertygrid.CTRL.__init__(self, parent, style=wxpg.PG_STATIC_SPLITTER)
        self.parent = parent
        self.listeDonnees = listeDonnees
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        couleurFond = "#e5ecf3"
        self.SetCaptionBackgroundColour(couleurFond)
        self.SetMarginColour(couleurFond)
        self.SetSplitterPosition(220)
    
    def Remplissage(self):
        # Autres lignes
        for valeur in self.listeDonnees :
            if type(valeur) == dict :
                if valeur["type"] == "chaine" :
                    propriete = wxpg.StringProperty(label=valeur["label"], name=valeur["code"], value=valeur["defaut"])
                if valeur["type"] == "choix" :
                    propriete = wxpg.EnumProperty(label=valeur["label"], name=valeur["code"], labels=valeur["choix"], values=range(0, len(valeur["choix"])), value=valeur["defaut"])
                if valeur["type"] == "check" :
                    propriete = wxpg.BoolProperty(label=valeur["label"], name=valeur["code"], value=valeur["defaut"])
                    propriete.SetAttribute("UseCheckbox", True)
                if valeur["type"] == "repertoire":
                    if 'phoenix' in wx.PlatformInfo:
                        propriete = wxpg.DirProperty(name=valeur["label"], label=valeur["code"], value=valeur["defaut"])
                    else:
                        propriete = wxpg.DirProperty(label=valeur["label"], name=valeur["code"], value=valeur["defaut"])
                propriete.SetHelpString(valeur["tip"])
                self.Append(propriete)
            else :
                self.Append(wxpg.PropertyCategory(valeur))

    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        # Recherche les paramètres mémorisés
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="export_compta", dictParametres=dictValeurs)
        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.items() :
            propriete = self.GetPropertyByName(nom)
            ancienneValeur = propriete.GetValue()
            if "EnumProperty" in str(propriete) :
                if valeur in ("", None):
                    valeur = None
                else :
                    valeur = int(valeur)
            if valeur != None :
                propriete.SetValue(valeur)
    
    def Sauvegarde(self, forcer=False):
        """ Mémorisation des valeurs du contrôle """
        if self.GetPropertyByName("memoriser_parametres").GetValue() == True or forcer == True :
            dictValeurs = copy.deepcopy(self.GetPropertyValues())
            UTILS_Parametres.ParametresCategorie(mode="set", categorie="export_compta", dictParametres=dictValeurs)

    def Validation(self):
        # Période
        if self.GetGrandParent().ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de début de période !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.GetGrandParent().ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de fin de période !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Paramètres
        for valeur in self.listeDonnees :
            if type(valeur) == dict :
                if valeur["type"] == "chaine" and valeur["obligatoire"] == True and self.GetPropertyValue(valeur["code"]) == "" :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner l'information '%s' !") % valeur["description"], _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        return True

    def GetParametres(self):
        dictParametres = self.GetPropertyValues()
        dictParametres["date_debut"] = self.GetGrandParent().ctrl_date_debut.GetDate()
        dictParametres["date_fin"] = self.GetGrandParent().ctrl_date_fin.GetDate()
        return dictParametres

    def CreationFichierTxt(self, nomFichier="", texte=""):
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier texte (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(None, message=_(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"),
            defaultDir=cheminDefaut, defaultFile=nomFichier, wildcard=wildcard, style=wx.FD_SAVE)
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True:
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return False
            else:
                dlg.Destroy()

        # Création du fichier texte
        if six.PY2:
            f = open(cheminFichier, "w")
            texte = texte.encode("utf8")
        else:
            f = codecs.open(cheminFichier, encoding='utf-8', mode='w')
        f.write(texte)
        f.close()

        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier a été créé avec succès.\n\nSouhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)



class Panel_parametres(wx.Panel):
    def __init__(self, parent, classe=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.ctrl_parametres = classe(self)
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_parametres.Add(self.ctrl_parametres, 1, wx.ALL | wx.EXPAND, 0)
        grid_sizer_parametres_boutons = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_parametres_boutons.Add(self.bouton_reinitialisation, 1, wx.ALL | wx.EXPAND, 0)
        grid_sizer_parametres_boutons.Add(self.bouton_sauvegarde, 1, wx.ALL | wx.EXPAND, 0)
        grid_sizer_parametres.Add(grid_sizer_parametres_boutons, 1, wx.ALL | wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_parametres, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()



class CTRL_Parametres_defaut(CTRL_Parametres) :
    def __init__(self, parent):
        self.listeDonnees = [
            _(u"Options générales"),
            {"type":"choix", "label":_(u"Type de période"), "description": _(u"Type de période"), "code": "option_type_periode", "tip": _(u"Sélectionnez le type de période à sélectionner"), "choix": [_(u"Selon la date de saisie de la prestation"), _(u"Selon la date de la prestation")], "defaut": 0, "obligatoire": True},
            {"type":"choix", "label":_(u"Regroupement des prestations"), "description":_(u"Mode de regroupement des prestations"), "code":"option_regroupement_prestations", "tip":_(u"Sélectionnez le mode de regroupement des prestations"), "choix":[_(u"Par nom de prestation"), _(u"Par nom d'activité")], "defaut":0, "obligatoire":True},
            {"type":"choix", "label":_(u"Regroupement des règlements"), "description":_(u"Mode de regroupement des règlements"), "code":"option_regroupement_reglements", "tip":_(u"Sélectionnez le mode de regroupement des règlements"), "choix":[_(u"Par mode de règlement"), _(u"Par dépôt de règlement")], "defaut":0, "obligatoire":True},
            {"type":"choix", "label":_(u"Sélection des règlements"), "description":_(u"Sélection des règlements"), "code":"option_selection_reglements", "tip":_(u"Sélectionnez le mode de sélection des règlements"), "choix":[_(u"Règlements déposés sur la période"), _(u"Règlements saisis sur la période")], "defaut":0, "obligatoire":True},
            {"type":"check", "label":_(u"Insérer entête noms des champs"), "description":_(u"Insérer ligne noms des champs"), "code":"ligne_noms_champs", "tip":_(u"Cochez cette case pour insérer en début de fichier une ligne avec les noms des champs"), "defaut":False, "obligatoire":True},
            {"type":"check", "label":_(u"Mémoriser les paramètres"), "description":_(u"Mémoriser les paramètres"), "code":"memoriser_parametres", "tip":_(u"Cochez cette case pour mémoriser les paramètres"), "defaut":True, "obligatoire":True},
            _(u"Codes journaux par défaut"),
            {"type":"chaine", "label":_(u"Ventes"), "description":_(u"Code journal des ventes"), "code":"journal_ventes", "tip":_(u"Saisissez le code journal des ventes"), "defaut":_(u"VE"), "obligatoire":True},
            {"type":"chaine", "label":_(u"Banque"), "description":_(u"Code journal de la banque"), "code":"journal_banque", "tip":_(u"Saisissez le code journal de la banque"), "defaut":_(u"BP"), "obligatoire":True},
            {"type":"chaine", "label":_(u"Caisse"), "description":_(u"Code journal de la caisse"), "code":"journal_caisse", "tip":_(u"Saisissez le code journal de la caisse"), "defaut":_(u"CA"), "obligatoire":False},
            _(u"Codes comptables par défaut"),
            {"type":"chaine", "label":_(u"Ventes"), "description":_(u"Code comptable des ventes"), "code":"code_ventes", "tip":_(u"Saisissez le code comptable des ventes (Peut être ajusté en détail dans le paramétrage des activités, des cotisations, des tarifs et des prestations)"), "defaut":u"706", "obligatoire":True},
            {"type":"chaine", "label":_(u"Clients"), "description":_(u"Code comptable des clients"), "code":"code_clients", "tip":_(u"Saisissez le code comptable des clients (Peut- être ajusté en détail dans la fiche famille)"), "defaut":u"411", "obligatoire":True},
            {"type":"chaine", "label":_(u"Banque"), "description":_(u"Code comptable de la banque"), "code":"code_banque", "tip":_(u"Saisissez le code comptable de la banque"), "defaut":u"512", "obligatoire":True},
            {"type":"chaine", "label":_(u"Caisse"), "description":_(u"Code comptable de la caisse"), "code":"code_caisse", "tip":_(u"Saisissez le code comptable de la caisse"), "defaut":u"531", "obligatoire":False},
            _(u"Formats des libellés"),
            {"type":"chaine", "label":_(u"Total des prestations"), "description":_(u"Format du libellé du total des ventes"), "code":"format_total_ventes", "tip":_(u"Saisissez le format du libellé du total des ventes. Vous pouvez utiliser les mots-clés suivants : {DATE_DEBUT} {DATE_FIN}."), "defaut":_(u"Prestations du {DATE_DEBUT} au {DATE_FIN}"), "obligatoire":True},
            {"type":"chaine", "label":_(u"Total des règlements"), "description":_(u"Format du libellé du total des règlements"), "code":"format_total_reglements", "tip":_(u"Saisissez le format du libellé du total des règlements. Vous pouvez utiliser les mots-clés suivants : {DATE_DEBUT} {DATE_FIN}."), "defaut":_(u"Règlements du {DATE_DEBUT} au {DATE_FIN}"), "obligatoire":True},
            #{"type":"chaine", "label":_(u"Prestation"), "description":_(u"Format du libellé des prestations"), "code":"format_prestation", "tip":_(u"Saisissez le format du libellé des prestations. Vous pouvez utiliser les mots-clés suivants : {IDPRESTATION} {DATE} {LIBELLE} {ACTIVITE} {ACTIVITE_ABREGE} {TARIF} {INDIVIDU_NOM} {INDIVIDU_PRENOM}"), "defaut":u"{LIBELLE} {INDIVIDU_NOM} {INDIVIDU_PRENOM}", "obligatoire":True},
            {"type":"chaine", "label":_(u"Prestation"), "description":_(u"Format du libellé des prestations"), "code":"format_prestation", "tip":_(u"Saisissez le format du libellé des prestations. Vous pouvez utiliser les mots-clés suivants : {NOM_PRESTATION} {DATE_DEBUT} {DATE_FIN}."), "defaut":u"{NOM_PRESTATION}", "obligatoire":True},
            {"type":"chaine", "label":_(u"Mode de règlement"), "description":_(u"Format du libellé des modes de règlements"), "code":"format_mode", "tip":_(u"Saisissez le format du libellé des modes de règlements. Vous pouvez utiliser les mots-clés suivants : {IDMODE} {NOM_MODE} {CODE_COMPTABLE} {NBRE_REGLEMENTS}."), "defaut":u"{NOM_MODE}", "obligatoire":True},
            {"type":"chaine", "label":_(u"Dépôt"), "description":_(u"Format du libellé des dépôts"), "code":"format_depot", "tip":_(u"Saisissez le format du libellé des dépôts. Vous pouvez utiliser les mots-clés suivants : {IDDEPOT} {NOM_DEPOT} {DATE_DEPOT} {MODE_REGLEMENT} {TYPE_COMPTABLE} {NBRE_REGLEMENTS}."), "defaut":u"{NOM_DEPOT} - {DATE_DEPOT}", "obligatoire":True},
            #{"type":"chaine", "label":_(u"Règlement"), "description":_(u"Format du libellé des règlements"), "code":"format_reglement", "tip":_(u"Saisissez le format du libellé des règlements. Vous pouvez utiliser les mots-clés suivants : {IDREGLEMENT} {DATE} {MODE_REGLEMENT} {NOM_FAMILLE} {NUMERO_PIECE} {NOM_PAYEUR} {NUMERO_QUITTANCIER} {DATE_DEPOT} {NOM_DEPOT}."), "defaut":u"{MODE_REGLEMENT} {NOM_FAMILLE}", "obligatoire":True},
            ]
        CTRL_Parametres.__init__(self, parent, self.listeDonnees)

    def Generation(self, format="ciel_compta"):
        if self.Validation() == False: return False

        # Récupération des paramètres
        dictParametres = self.GetParametres()
        donnees = Donnees(dictParametres)

        numLigne = 1
        listeLignesTxt = []

        # Ligne d'entête
        if dictParametres["ligne_noms_champs"] == True:
            listeLignesTxt.append(
                "numligne,date,journal,compte,libelleauto,libellemanuel,piece,montant,sens,echeance,devise")

        # Ventes
        lignesVentes = donnees.GetVentes()
        if lignesVentes == False:
            return False

        for ligne in lignesVentes:
            if ligne["montant"] != FloatToDecimal(0.0):
                listeLignesTxt.append(self.FormateLigne(format, ligne, dictParametres, numLigne))
                numLigne += 1

        # Banque
        for typeComptable in ("banque", "caisse"):

            if dictParametres["journal_%s" % typeComptable] != "":

                if dictParametres["option_regroupement_reglements"] == 0:
                    lignesTemp = donnees.GetReglements_Modes(typeComptable=typeComptable)
                if dictParametres["option_regroupement_reglements"] == 1:
                    lignesTemp = donnees.GetReglements_Depots(typeComptable=typeComptable)

                if lignesTemp == False:
                    return False

                for ligne in lignesTemp:
                    if ligne["montant"] != FloatToDecimal(0.0):
                        listeLignesTxt.append(self.FormateLigne(format, ligne, dictParametres, numLigne, typeComptable))
                        numLigne += 1

        # Finalisation du texte
        texte = "\n".join(listeLignesTxt)
        nomFichier = _(u"Export_%s_%s_%s") % (
        format, dictParametres["date_debut"].strftime("%d-%m-%Y"), dictParametres["date_fin"].strftime("%d-%m-%Y"))
        self.CreationFichierTxt(nomFichier=nomFichier, texte=texte)

    def FormateLigne(self, format, ligne, dictParametres, numLigne, typeComptable=None):
        if format == "ebp_compta" :
            return Export_ebp_compta(ligne, dictParametres, numLigne, typeComptable)
        if format == "ciel_compta_ebp" :
            return Export_ebp_compta(ligne, dictParametres, numLigne, typeComptable)
        if format == "ciel_compta_ximport" :
            return UTILS_XImport.XImportLine(ligne, dictParametres, numLigne, typeComptable).getData()

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres_quadracompta(CTRL_Parametres) :
    def __init__(self, parent):
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()

        self.listeDonnees = [
            _(u"Options générales"),
            {"type": "check", "label": _(u"Mémoriser les paramètres"), "description": _(u"Mémoriser les paramètres"), "code": "memoriser_parametres", "tip": _(u"Cochez cette case pour mémoriser les paramètres"), "defaut": True, "obligatoire": True},
            {"type": "repertoire", "label": _(u"Répertoire de destination"), "description": _(u"Répertoire de destination"), "code": "quadra_repertoire", "tip": _(u"Sélectionnez un répertoire de destination"), "defaut": cheminDefaut, "obligatoire": True},
            _(u"Données"),
            {"type":"choix", "label":_(u"Ventes"), "description": _(u"Type de données à afficher"), "code": "quadra_type_ventes", "tip": _(u"Sélectionnez le type de données à afficher"), "choix": [_(u"Factures de la période"), _(u"Prestations de la période")], "defaut": 0, "obligatoire": True},
            {"type":"choix", "label":_(u"Règlements"), "description": _(u"Type de données à afficher"), "code": "quadra_type_reglements", "tip": _(u"Sélectionnez le type de données à afficher"), "choix": [_(u"Règlements déposés sur la période"), _(u"Règlements saisis sur la période")], "defaut": 0, "obligatoire": True},
            {"type":"check", "label":_(u"Utiliser code compta de la famille"), "description": _(u"Utiliser le code comptable de la famille"), "code": "quadra_code_compta_famille", "tip": _(u"Cochez cette case pour utiliser le code comptable saisi dans l'onglet divers de la fiche famille. Sinon un code générique sera utilisé."), "defaut": True, "obligatoire": True},
            _(u"Affichage"),
            {"type": "check", "label": _(u"Insérer entête noms des champs"), "description": _(u"Insérer ligne noms des champs"), "code": "quadra_ligne_noms_champs", "tip": _(u"Cochez cette case pour insérer en début de fichier une ligne avec les noms des champs"), "defaut": True, "obligatoire": True},
            {"type": "check", "label": _(u"Séparer les écritures avec ligne vide"), "description": _(u"Séparer les écritures par une ligne vide"), "code": "quadra_ligne_vide", "tip": _(u"Séparer les écritures par une ligne vide"), "defaut": True, "obligatoire": True},
            _(u"Codes journaux par défaut"),
            {"type": "chaine", "label":_(u"Ventes"), "description":_(u"Code journal des ventes"), "code":"quadra_journal_ventes", "tip":_(u"Saisissez le code journal des ventes"), "defaut":_(u"VT"), "obligatoire":True},
            {"type": "chaine", "label": _(u"Règlements"), "description": _(u"Code journal des règlements"), "code": "quadra_journal_reglements", "tip": _(u"Saisissez le code journal des règlements"), "defaut": _(u"OD1"), "obligatoire": True},
            ]
        CTRL_Parametres.__init__(self, parent, self.listeDonnees)

    def Generation(self, format=None):
        if self.Validation() == False: return False

        # Récupération des paramètres
        dictParametres = self.GetParametres()

        # Importation des prestations
        if dictParametres["quadra_type_ventes"] == 0:
            condition = "factures.date_debut>='%s' AND factures.date_fin<='%s'" % (dictParametres["date_debut"], dictParametres["date_fin"])
        else:
            condition = "prestations.date_valeur>='%s' AND prestations.date_valeur<='%s'" % (dictParametres["date_debut"], dictParametres["date_fin"])

        DB = GestionDB.DB()
        req = """
        SELECT prestations.IDprestation, prestations.date, prestations.code_compta, prestations.IDfacture, prestations.label,
        prestations.montant, prestations.IDactivite, prestations.IDtarif, prestations.IDfamille, prestations.IDindividu, 
        activites.nom, activites.code_comptable,
        tarifs.code_compta,
        noms_tarifs.nom, 
        types_cotisations.code_comptable, types_cotisations.nom,
        factures.numero, factures.date_edition
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON prestations.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        LEFT JOIN cotisations ON cotisations.IDprestation = prestations.IDprestation
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        WHERE %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listePrestations = []
        for IDprestation, date, code_compta_prestation, IDfacture, label, montant, IDactivite, IDtarif, IDfamille, IDindividu, nom_activite, code_compta_activite, code_compta_tarif, nom_tarif, code_compta_type_cotisation, nom_type_cotisation, num_facture, date_edition in listeDonnees :
            if nom_activite == None: nom_activite = ""
            if nom_tarif == None: nom_tarif = ""
            dictTemp = {
                "IDprestation": IDprestation, "date_prestation": UTILS_Dates.DateEngEnDateDD(date), "label": label, "montant": FloatToDecimal(montant),
                "code_compta_prestation": code_compta_prestation, "code_compta_tarif": code_compta_tarif,
                "IDactivite": IDactivite, "nom_activite": nom_activite, "code_compta_activite": code_compta_activite,
                "IDtarif": IDtarif, "nom_tarif": nom_tarif, "IDfacture": IDfacture, "num_facture": num_facture, "date_edition_facture": UTILS_Dates.DateEngEnDateDD(date_edition),
                "code_compta_type_cotisation": code_compta_type_cotisation, "nom_type_cotisation": nom_type_cotisation,
                "IDfamille": IDfamille, "IDindividu": IDindividu,
                }
            listePrestations.append(dictTemp)

        # Importation des familles
        dictTitulaires = UTILS_Titulaires.GetTitulaires()

        if not dictParametres["quadra_code_compta_famille"]:
            for IDfamille in dictTitulaires:
                if not dictTitulaires[IDfamille]["code_comptable"]:
                    dictTitulaires[IDfamille]["code_comptable"] = "F%06d" % IDfamille

        # Regroupement des prestations
        anomalies = []
        dict_resultats = {}

        # Si mode FACTURES, on regroupe par IDFACTURE
        for prestation in listePrestations:
            if dictParametres["quadra_type_ventes"] == 0:
                cle_primaire = prestation["IDfacture"]
            else:
                cle_primaire = prestation["IDfamille"]

            if cle_primaire:

                # Regroupement primaire
                if cle_primaire not in dict_resultats:
                    code_comptable_famille = dictTitulaires[prestation["IDfamille"]]["code_comptable"]
                    noms_titulaires = dictTitulaires[prestation["IDfamille"]]["titulairesSansCivilite"]
                    dict_resultats[cle_primaire] = {
                        "IDfamille": prestation["IDfamille"], "code_comptable_famille": code_comptable_famille, "num_facture": prestation["num_facture"],
                        "date_edition_facture": prestation["date_edition_facture"], "montant_debit": FloatToDecimal(0.0), "lignes_credit": {},
                        "noms_titulaires": noms_titulaires,
                        }

                    # Si code compta famille manquant
                    if code_comptable_famille in ("", None):
                        txt = u"Le code comptable de la famille %s est manquant." % noms_titulaires
                        if txt not in anomalies:
                            anomalies.append(txt)

                # Recherche le code compta de la prestation
                code_compta = prestation["code_compta_prestation"]
                label_compta = ""
                if code_compta == None:
                    code_compta = ""
                if prestation["IDactivite"]:
                    label_compta = prestation["nom_activite"]
                if code_compta in (None, ""):
                    if prestation["code_compta_tarif"] not in (None, ""):
                        code_compta = prestation["code_compta_tarif"]
                        label_compta = prestation["nom_tarif"]
                    else:
                        if prestation["code_compta_activite"] not in (None, ""):
                            code_compta = prestation["code_compta_activite"]
                            label_compta = prestation["nom_activite"]
                        else:
                            if prestation["code_compta_type_cotisation"] not in (None, ""):
                                code_compta = prestation["code_compta_type_cotisation"]
                                label_compta = prestation["nom_type_cotisation"]
                if code_compta == "":
                    code_compta = ""
                    label_compta = ""

                if not code_compta:
                    if prestation["IDactivite"]:
                        txt = u"Le code comptable de l'activité %s est manquant." % prestation["nom_activite"]
                    else:
                        txt = u"Le code comptable de la prestation %s est manquant." % prestation["label"]
                    if txt not in anomalies:
                        anomalies.append(txt)

                # Regroupement secondaire
                cle_secondaire = code_compta

                if cle_secondaire not in dict_resultats[cle_primaire]["lignes_credit"]:
                    dict_resultats[cle_primaire]["lignes_credit"][cle_secondaire] = {"code_compta": code_compta, "label_compta": label_compta, "prestation": prestation, "montant_credit": FloatToDecimal(0.0)}
                dict_resultats[cle_primaire]["lignes_credit"][cle_secondaire]["montant_credit"] += prestation["montant"]
                dict_resultats[cle_primaire]["montant_debit"] += prestation["montant"]

        # Tri par IDfacture
        liste_clesprimaires = list(dict_resultats.keys())
        liste_clesprimaires.sort()

        # Création du fichier des ventes
        lignes = []
        for cle_primaire in liste_clesprimaires:
            IDfamille = dict_resultats[cle_primaire]["IDfamille"]
            code_comptable_famille = dict_resultats[cle_primaire]["code_comptable_famille"]
            code_journal_ventes = dictParametres["quadra_journal_ventes"]
            noms_titulaires = dict_resultats[cle_primaire]["noms_titulaires"]
            montant_debit = dict_resultats[cle_primaire]["montant_debit"]

            if dictParametres["quadra_type_ventes"] == 0:
                date = dict_resultats[cle_primaire]["date_edition_facture"]
                num_piece = dict_resultats[cle_primaire]["num_facture"]
            else:
                date = dictParametres["date_fin"]
                num_piece = ""

            # Ligne de débit
            lignes.append([code_journal_ventes, date, code_comptable_famille, noms_titulaires, noms_titulaires, montant_debit, "", num_piece])

            # Lignes de crédit
            for cle_secondaire, valeurs in dict_resultats[cle_primaire]["lignes_credit"].items():
                lignes.append([code_journal_ventes, date, valeurs["code_compta"], valeurs["label_compta"], noms_titulaires, "", valeurs["montant_credit"], num_piece])

            # Ligne vide
            if dictParametres["quadra_ligne_vide"]:
                lignes.append(None)

        # Création du fichier des ventes
        colonnes = [
            {"label": u"Code journal", "largeur": 12},
            {"label": u"Date", "largeur": 15},
            {"label": u"Compte", "largeur": 15},
            {"label": u"Intitulé", "largeur": 40},
            {"label": u"Libellé", "largeur": 40},
            {"label": u"Débit", "largeur": 12},
            {"label": u"Crédit", "largeur": 12},
            {"label": u"Num. Pièce", "largeur": 12},
            ]

        if not anomalies:
            succes = self.CreationFichierExcel(nom_fichier="ventes.xlsx", colonnes=colonnes, lignes=lignes)
            if not succes:
                return False

        # ----------------- Règlements -------------------

        # Condition de sélection des règlements
        if dictParametres["quadra_type_reglements"] == 0 :
            condition = "reglements.IDdepot IS NOT NULL AND depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s' " % (dictParametres["date_debut"], dictParametres["date_fin"])
        else :
            condition = "reglements.date>='%s' AND reglements.date<='%s' " % (dictParametres["date_debut"], dictParametres["date_fin"])

        # Récupération des règlements
        DB = GestionDB.DB()
        req = """SELECT 
        reglements.IDreglement, reglements.date, 
        modes_reglements.label, 
        reglements.numero_piece, reglements.montant, 
        depots.date, depots.nom,  
        date_saisie, comptes_payeurs.IDfamille,
        modes_reglements.code_compta,
        comptes_bancaires.numero, comptes_bancaires.nom,
        payeurs.nom
        FROM reglements
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        LEFT JOIN payeurs ON payeurs.IDpayeur = reglements.IDpayeur
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        LEFT JOIN comptes_bancaires ON comptes_bancaires.IDcompte = reglements.IDcompte
        WHERE %s
        GROUP BY reglements.IDreglement
        ORDER BY modes_reglements.label;
        """ % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        lignes = []
        for IDreglement, date_reglement, label_mode, numero_piece, montant, date_depot, nom_depot, date_saisie, IDfamille, code_compta_mode, numero_compte, nom_compte, nom_payeur in listeDonnees :
            date_reglement = UTILS_Dates.DateEngEnDateDD(date_reglement)
            date_depot = UTILS_Dates.DateEngEnDateDD(date_depot)

            code_journal = dictParametres["quadra_journal_reglements"]
            code_comptable_famille = dictTitulaires[IDfamille]["code_comptable"]
            noms_titulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]

            # Ligne débit
            lignes.append([code_journal, date_reglement, code_compta_mode, label_mode, noms_titulaires, numero_piece, FloatToDecimal(montant), ""])

            # Ligne crédit
            lignes.append([code_journal, date_reglement, code_comptable_famille, nom_payeur, noms_titulaires, numero_piece, "", FloatToDecimal(montant)])

            # Ligne vide
            if dictParametres["quadra_ligne_vide"]:
                lignes.append(None)

            # Anomalies
            if code_comptable_famille in ("", None):
                txt = u"Le code comptable de la famille %s est manquant." % noms_titulaires
                if txt not in anomalies:
                    anomalies.append(txt)

            if code_compta_mode in ("", None):
                txt = u"Le code comptable du mode de règlement %s est manquant." % label_mode
                if txt not in anomalies:
                    anomalies.append(txt)

        # Création du fichier des ventes
        colonnes = [
            {"label": u"Code journal", "largeur": 12},
            {"label": u"Date", "largeur": 15},
            {"label": u"Compte", "largeur": 15},
            {"label": u"Intitulé", "largeur": 40},
            {"label": u"Libellé", "largeur": 40},
            {"label": u"Num. Pièce", "largeur": 12},
            {"label": u"Débit", "largeur": 12},
            {"label": u"Crédit", "largeur": 12},
            ]
        if not anomalies:
            succes = self.CreationFichierExcel(nom_fichier="reglements.xlsx", colonnes=colonnes, lignes=lignes)
            if not succes:
                return False

        # Anomalies
        if anomalies:
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Anomalies"), introduction=_("Veuillez corriger les %d anomalies suivantes avant de pouvoir continuer :" % len(anomalies)), detail="\n".join(anomalies), icone=wx.ICON_ERROR, boutons=[_(u"Fermer"), ], defaut=0)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Succès
        dlg = wx.MessageDialog(self, _(u"Les fichiers ont été générés avec succès dans le répertoire %s.") % dictParametres["quadra_repertoire"], _(u"Succès"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True

    def CreationFichierExcel(self, nom_fichier="", colonnes=[], lignes=[]):
        dictParametres = self.GetParametres()

        cheminFichier = os.path.join(dictParametres["quadra_repertoire"], nom_fichier)

        # # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        # wildcard = "Fichiers Excel (*.xlsx)|*.xlsx|Tous les fichiers (*.*)|*.*"
        # cheminDefaut = dictParametres["quadra_repertoire"]
        # print("cheminDefaut=", cheminDefaut)
        # dlg = wx.FileDialog(None, message=_(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, defaultFile=nom_fichier, wildcard=wildcard, style=wx.FD_SAVE)
        # dlg.SetFilterIndex(0)
        # if dlg.ShowModal() == wx.ID_OK:
        #     cheminFichier = dlg.GetPath()
        #     dlg.Destroy()
        # else:
        #     dlg.Destroy()
        #     return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True:
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"),"Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_NO:
                return False

        # Création d'un classeur et d'une feuille
        classeur = xlsxwriter.Workbook(cheminFichier)
        feuille = classeur.add_worksheet()

        # Formats
        format_date = classeur.add_format({'num_format': 'dd/mm/yyyy'})
        format_money = classeur.add_format({'num_format': '# ##0.00'})
        format_label = classeur.add_format({'align': 'center', 'bold': True})

        # Création des labels de colonnes
        x, y = 0, 0
        for colonne in colonnes:
            if dictParametres["quadra_ligne_noms_champs"]:
                feuille.write(x, y, colonne["label"], format_label)
            feuille.set_column(y, y, colonne["largeur"])
            y += 1

        # Création des lignes
        x, y = 1, 0
        for valeurs in lignes:
            if valeurs :
                for valeur in valeurs:
                    if isinstance(valeur, datetime.date):
                        feuille.write_datetime(x, y, valeur, format_date)
                    elif isinstance(valeur, decimal.Decimal):
                        feuille.write(x, y, valeur, format_money)
                    else:
                        feuille.write(x, y, valeur)
                    y += 1
            x += 1
            y = 0

        # Finalisation du fichier xlsx
        try:
            classeur.close()
        except Exception as err:
            if "Permission denied" in six.text_type(err):
                texte = _(u"Impossible de créer le fichier !\n\nVérifiez qu'un fichier du même nom n'est pas déjà ouvert en arrière-plan.")
            else:
                texte = _(u"Erreur: %s" % err)
            dlg = wx.MessageDialog(self, texte, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        return True


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres_cerig(CTRL_Parametres) :
    def __init__(self, parent):
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()

        self.listeDonnees = [
            _(u"Options g�n�rales"),
            {"type": "check", "label": _(u"M�moriser les param�tres"), "description": _(u"M�moriser les param�tres"), "code": "memoriser_parametres", "tip": _(u"Cochez cette case pour m�moriser les param�tres"), "defaut": True, "obligatoire": True},
            {"type": "repertoire", "label": _(u"R�pertoire de destination"), "description": _(u"R�pertoire de destination"), "code": "cerig_repertoire", "tip": _(u"S�lectionnez un r�pertoire de destination"), "defaut": cheminDefaut, "obligatoire": True},
            _(u"Codes par d�faut"),
            {"type": "chaine", "label": _(u"Compte par d�faut"), "description": _(u"Code compte par d�faut"), "code": "cerig_code_comptable", "tip": _(u"Saisissez le code comptable par d�faut"), "defaut": _(u""), "obligatoire": False},
            {"type": "chaine", "label": _(u"Analytique par d�faut"), "description": _(u"Code analytique par d�faut"), "code": "cerig_code_analytique", "tip": _(u"Saisissez le code analytique par d�faut"), "defaut": _(u""), "obligatoire": False},
        ]
        CTRL_Parametres.__init__(self, parent, self.listeDonnees)

    def Generation(self, format=None):
        if self.Validation() == False: return False

        # R�cup�ration des param�tres
        dictParametres = self.GetParametres()

        # Importation des familles
        dictTitulaires = UTILS_Titulaires.GetTitulaires()

        # Importation des prestations
        condition = "factures.date_debut>='%s' AND factures.date_fin<='%s'" % (dictParametres["date_debut"], dictParametres["date_fin"])

        DB = GestionDB.DB()
        req = """
        SELECT prestations.IDprestation, prestations.date, prestations.code_compta, prestations.IDfacture, prestations.label,
        prestations.montant, prestations.IDactivite, prestations.IDtarif, prestations.IDfamille, prestations.IDindividu, 
        activites.nom, activites.code_comptable, activites.code_analytique,
        tarifs.code_compta,
        noms_tarifs.nom, 
        types_cotisations.code_comptable, types_cotisations.nom,
        factures.numero, factures.date_edition,
        individus.prenom
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON prestations.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        LEFT JOIN cotisations ON cotisations.IDprestation = prestations.IDprestation
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        WHERE %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        anomalies = []
        dict_resultats = {}
        for IDprestation, date, code_compta_prestation, IDfacture, label, montant, IDactivite, IDtarif, IDfamille, IDindividu, nom_activite, code_compta_activite, code_analytique_activite, code_compta_tarif, nom_tarif, code_compta_type_cotisation, nom_type_cotisation, num_facture, date_edition, prenom_individu in listeDonnees :
            montant = FloatToDecimal(montant)

            cle_primaire = IDfacture
            if cle_primaire:

                # Regroupement primaire
                if cle_primaire not in dict_resultats:
                    code_comptable_famille = dictTitulaires[IDfamille]["code_comptable"]
                    noms_titulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
                    dict_resultats[cle_primaire] = {
                        "IDfamille": IDfamille, "code_comptable_famille": code_comptable_famille, "num_facture": num_facture,
                        "date_edition_facture": UTILS_Dates.DateEngEnDateDD(date_edition), "montant_facture": FloatToDecimal(0.0), "lignes": {},
                        "noms_titulaires": noms_titulaires,
                        }

                # Recherche le code compta de la prestation
                code_compta = dictParametres["cerig_code_comptable"]
                if code_compta_prestation:
                    code_compta = code_compta_prestation
                if code_compta in (None, ""):
                    if code_compta_tarif not in (None, ""):
                        code_compta = code_compta_tarif
                    else:
                        if code_compta_activite not in (None, ""):
                            code_compta = code_compta_activite
                        else:
                            if code_compta_type_cotisation not in (None, ""):
                                code_compta = code_compta_type_cotisation

                if not code_compta:
                    if IDactivite:
                        txt = u"Le code comptable de l'activit� %s est manquant." % nom_activite
                    else:
                        txt = u"Le code comptable de la prestation %s est manquant." % label
                    if txt not in anomalies:
                        anomalies.append(txt)

                # Code analytique
                code_analytique = dictParametres["cerig_code_analytique"]
                if code_analytique_activite:
                    code_analytique = code_analytique_activite
                if not code_analytique:
                    anomalies.append(u"Le code analytique de la prestation %s est manquant." % label)

                # Cr�ation label
                if prenom_individu:
                    label = u"%s - %s" % (prenom_individu, label)

                # Regroupement secondaire
                cle_secondaire = code_compta

                if cle_secondaire not in dict_resultats[cle_primaire]["lignes"]:
                    dict_resultats[cle_primaire]["lignes"][cle_secondaire] = {"code_compta": code_compta, "code_analytique": code_analytique, "label": label, "montant": FloatToDecimal(0.0)}
                dict_resultats[cle_primaire]["lignes"][cle_secondaire]["montant"] += montant
                dict_resultats[cle_primaire]["montant_facture"] += montant

        # Tri par IDfacture
        liste_clesprimaires = list(dict_resultats.keys())
        liste_clesprimaires.sort()

        # Cr�ation du fichier
        lignes = []
        for cle_primaire in liste_clesprimaires:
            date_facture = dict_resultats[cle_primaire]["date_edition_facture"].strftime("%Y%m%d")
            noms_titulaires = dict_resultats[cle_primaire]["noms_titulaires"]
            label_facture = u"Facture %s" % dict_resultats[cle_primaire]["num_facture"]
            montant_facture = dict_resultats[cle_primaire]["montant_facture"]

            for cle_secondaire, valeurs in dict_resultats[cle_primaire]["lignes"].items():
                lignes.append((date_facture, noms_titulaires, label_facture, valeurs["label"], str(montant_facture), valeurs["code_compta"], valeurs["code_analytique"]))

        # Si vide:
        if not lignes:
            dlg = wx.MessageDialog(self, _(u"Aucune donn�e n'a �t� trouv�e sur la p�riode s�lectionn�e."), _(u"Erreur"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Affichage des anomalies
        if anomalies:
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Anomalies"), introduction=_("Veuillez corriger les %d anomalies suivantes avant de pouvoir continuer :" % len(anomalies)), detail="\n".join(anomalies), icone=wx.ICON_ERROR, boutons=[_(u"Fermer"), ], defaut=0)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # G�n�ration du fichier texte
        succes = self.CreationFichier(nom_fichier="export_cerig.txt", lignes=lignes)
        if not succes:
            return False

        # Succ�s
        dlg = wx.MessageDialog(self, _(u"Le fichier a �t� g�n�r� avec succ�s dans le r�pertoire %s.") % dictParametres["cerig_repertoire"], _(u"Succ�s"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True

    def CreationFichier(self, nom_fichier="", lignes=[]):
        dictParametres = self.GetParametres()

        cheminFichier = os.path.join(dictParametres["cerig_repertoire"], nom_fichier)
        if os.path.isfile(cheminFichier):
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"),"Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_NO:
                return False

        # Cr�ation d'un classeur et d'une feuille
        with codecs.open(cheminFichier, mode="w", encoding="utf-8") as fichier:
            for ligne in lignes:
                fichier.write(u";".join(ligne) + "\n")

        return True

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        # Bandeau
        intro = _(u"Sélectionnez les dates de la période à exporter, choisissez le format d'export correspondant à votre logiciel de compatibilité puis renseignez les paramètres nécessaires avant cliquer sur Générer. Vous obtiendrez un fichier qu'il vous suffira d'importer depuis votre logiciel de comptabilité.")
        titre = _(u"Export des écritures comptables")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Export_comptable.png")
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Période"))
        self.label_date_debut = wx.StaticText(self, wx.ID_ANY, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Logiciel de sortie
        self.box_logiciel_staticbox = wx.StaticBox(self, -1, _(u"Format d'export"))
        self.ctrl_logiciel = CTRL_Logiciel(self)

        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Paramètres"))
        self.pages = [
            {"code": "defaut", "logiciels": ["ebp_compta", "ciel_compta_ebp", "ciel_compta_ximport"], "ctrl": Panel_parametres(self, CTRL_Parametres_defaut)},
            {"code": "quadracompta", "logiciels": ["quadracompta"], "ctrl": Panel_parametres(self, CTRL_Parametres_quadracompta)},
            {"code": "cerig", "logiciels": ["cerig"], "ctrl": Panel_parametres(self, CTRL_Parametres_cerig)},
        ]

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer le fichier"), cheminImage="Images/32x32/Disk.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_COMBOBOX, self.OnChoixLogiciel, self.ctrl_logiciel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)

        self.OnChoixLogiciel()
        wx.CallAfter(self.ctrl_date_debut.SetFocus)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de la période à exporter")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de la période à exporter")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer la génération des fichiers d'exportation")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((700, 680))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)
        
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(2, 2, 5, 5)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(box_periode, 1, wx.EXPAND, 10)
        
        box_logiciel = wx.StaticBoxSizer(self.box_logiciel_staticbox, wx.VERTICAL)
        grid_sizer_logiciel = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_logiciel.Add(self.ctrl_logiciel, 0, wx.EXPAND, 0)
        grid_sizer_logiciel.AddGrowableCol(0)
        box_logiciel.Add(grid_sizer_logiciel, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(box_logiciel, 1, wx.EXPAND, 10)
        
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        for page in self.pages:
            box_parametres.Add(page["ctrl"], 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_base.Add(box_parametres, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        self.grid_sizer_base = grid_sizer_base

    def OnChoixLogiciel(self, event=None):
        code = self.ctrl_logiciel.GetCode()
        for page in self.pages:
            if code in page["logiciels"]:
                page["ctrl"].Show(True)
            else:
                page["ctrl"].Show(False)
        self.grid_sizer_base.Layout()

    def GetPageActive(self):
        for page in self.pages:
            if page["ctrl"].IsShown():
                return page["ctrl"]
        return None

    def OnBoutonAide(self, event):  
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Exportdesecriturescomptables")

    def OnBoutonFermer(self, event):
        self.GetPageActive().ctrl_parametres.Sauvegarde()
        self.ctrl_logiciel.Sauvegarde()
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        format = self.ctrl_logiciel.GetCode()
        self.GetPageActive().ctrl_parametres.Generation(format)




# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Codes(wxpg.PropertyGrid) :
    def __init__(self, parent, dictCodes=None, keyStr=False):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=wxpg.PG_SPLITTER_AUTO_CENTER )
        self.parent = parent
        self.dictCodes = dictCodes
        self.keyStr = keyStr
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        couleurFond = "#e5ecf3"
        self.SetCaptionBackgroundColour(couleurFond)
        self.SetMarginColour(couleurFond)
        
        # Remplissage des valeurs
        if keyStr == True :
            listeIntitules = list(dictCodes.keys()) 
            listeIntitules.sort() 
            for intitule in listeIntitules :
                valeur = dictCodes[intitule]["code_compta"]
                if valeur == None : valeur = ""
                propriete = wxpg.StringProperty(label=intitule, name=intitule, value=valeur)
                self.Append(propriete)
        else :
            for ID, dictValeurs in dictCodes.items() :
                valeur = dictValeurs["code_compta"]
                if valeur == None : valeur = ""
                if "label" in dictValeurs : intitule = dictValeurs["label"]
                if "intitule" in dictValeurs : intitule = dictValeurs["intitule"]
                propriete = wxpg.StringProperty(label=intitule, name=str(ID), value=valeur)
                self.Append(propriete)
                

    def Validation(self):
        for label, valeur in self.GetPropertyValues().items() :
            if valeur == "" :
                if self.keyStr == False :
                    ID = int(label)
                    if "label" in self.dictCodes[ID] : label = self.dictCodes[ID]["label"]
                    if "intitule" in self.dictCodes[ID] : label = self.dictCodes[ID]["intitule"]
                dlg = wx.MessageDialog(None, _(u"Vous n'avez pas renseigné le code comptable de la ligne '%s'.\n\nSouhaitez-vous tout de même continuer ? (Si oui, cette ligne ne sera pas exportée)") % label, _(u"Information manquante"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_NO:
                    return False

        return True

    def GetCodes(self):
        dictCodes = self.GetPropertyValues()
        return dictCodes




class Dialog_codes(wx.Dialog):
    def __init__(self, parent, dictCodes=None, keyStr=False, titre=_(u"Vérification des codes comptables")):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.dictCodes = dictCodes
        
        self.label_intro = wx.StaticText(self, wx.ID_ANY, _(u"Veuillez vérifier ci-dessous que les codes comptables attribués sont exacts. \nLaissez la ligne vide si vous souhaitez exclure celle-ci de l'export."))
        self.ctrl_codes = CTRL_Codes(self, dictCodes=dictCodes, keyStr=keyStr)
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        # Propriétés
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((590, 600))
        self.SetTitle(titre)
        
        # Affichage
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_codes, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        if self.ctrl_codes.Validation() == False :
            return False
        self.EndModal(wx.ID_OK)
        
    def GetCodes(self):
        return self.ctrl_codes.GetCodes() 
    
    
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    dlg.ctrl_date_debut.SetDate("2011-01-01")
    dlg.ctrl_date_fin.SetDate("2011-12-31")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()

