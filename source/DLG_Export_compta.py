#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import os
import datetime
import GestionDB
import CTRL_Bandeau
import CTRL_Saisie_date
import UTILS_Dates
import UTILS_Titulaires
from UTILS_Decimal import FloatToDecimal as FloatToDecimal
import FonctionsPerso
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import wx.lib.agw.labelbook as LB
import wx.propgrid as wxpg
import wx.lib.dialogs as dialogs
import wx.lib.agw.pybusyinfo as PBI


def FormateDate(dateDD=None, format="%d/%m/%Y") :
    if dateDD == None or dateDD == "" :
        return ""
    else :
        return dateDD.strftime(format)
    
    
    
class Donnees():
    def __init__(self, dictParametres={}):
        self.date_debut = dictParametres["date_debut"]
        self.date_fin =dictParametres["date_fin"]
        self.dictParametres = dictParametres
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires()
    
    def GetVentes(self):
        DB = GestionDB.DB() 
        
        dlgAttente = PBI.PyBusyInfo(u"Recherche des données en cours...", parent=None, title=u"Patientez...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        # Récupération des factures
        req = """
        SELECT factures.IDfacture, factures.numero, factures.IDcompte_payeur, comptes_payeurs.IDfamille,
        factures.date_edition, factures.date_echeance, 
        factures.date_debut, factures.date_fin, factures.total, factures.regle, factures.solde,
        lots_factures.nom, familles.code_comptable
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille
        LEFT JOIN lots_factures ON lots_factures.IDlot = factures.IDlot
        WHERE date_edition>='%s' AND date_edition<='%s'
        GROUP BY factures.IDfacture
        ORDER BY factures.date_edition
        ;""" % (self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeFactures = []
        for IDfacture, numero, IDcompte_payeur, IDfamille, date_edition, date_echeance, date_debut, date_fin, total, regle, solde, nomLot, code_comptable_famille in listeDonnees :
            if nomLot == None : nomLot = ""
            dictTemp = {
                "IDfacture" : IDfacture, "numero" : numero, "IDcompte_payeur" : IDcompte_payeur, "IDfamille" : IDfamille,
                "date_edition" : UTILS_Dates.DateEngEnDateDD(date_edition), "date_echeance" : UTILS_Dates.DateEngEnDateDD(date_echeance), 
                "date_debut" : UTILS_Dates.DateEngEnDateDD(date_debut), "date_fin" : UTILS_Dates.DateEngEnDateDD(date_fin), 
                "total" : FloatToDecimal(total), "regle" : FloatToDecimal(regle), "solde" : FloatToDecimal(solde), "nomLot" : nomLot, "code_comptable_famille" : code_comptable_famille,
                }
            listeFactures.append(dictTemp)

        # Récupération des prestations des factures
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
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq() 
        dictPrestations = {}
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
            if dictPrestations.has_key(IDfacture) == False :
                dictPrestations[IDfacture] = []
            dictPrestations[IDfacture].append(dictTemp)
        
        DB.Close()
        
        # Analyse des factures
        listeLignes = []
        listeCodesManquants = []
        listeAnomalies = []
        dictCodes = {}
        for dictFacture in listeFactures :
            
            if dictFacture["total"] != FloatToDecimal(0.0) :
                
                if self.dictTitulaires.has_key(dictFacture["IDfamille"]) :
                    nomFamille = self.dictTitulaires[dictFacture["IDfamille"]]["titulairesSansCivilite"]
                else :
                    nomFamille = ""
                
                # Formatage libellé facture
                libelle_facture = self.dictParametres["format_facture"]
                listeMotsCles = [
                    ("{IDFACTURE}", str(dictFacture["IDfacture"])),
                    ("{NOM_FAMILLE}", nomFamille), 
                    ("{NUMERO}", str(dictFacture["numero"])),
                    ("{DATE_EDITION}", FormateDate(dictFacture["date_edition"])),
                    ("{DATE_ECHEANCE}", FormateDate(dictFacture["date_echeance"])),
                    ("{DATE_DEBUT}", FormateDate(dictFacture["date_debut"])),
                    ("{DATE_FIN}", FormateDate(dictFacture["date_fin"])),
                    ("{NOM_LOT}", dictFacture["nomLot"]),
                    ]
                for motcle, valeur in listeMotsCles :
                    libelle_facture = libelle_facture.replace(motcle, valeur)
                
                # Mémorisation ligne facture
                listeLignes.append({
                    "type" : "facture",
                    "IDfacture" : IDfacture,
                    "date_edition" : dictFacture["date_edition"],
                    "libelle_facture" : libelle_facture,
                    "numero" : dictFacture["numero"],
                    "montant" : dictFacture["total"],
                    "date_echeance" : dictFacture["date_echeance"],
                    "famille" : nomFamille,
                    "date_debut" : dictFacture["date_debut"],
                    "date_fin" : dictFacture["date_fin"],
                    "code_comptable_famille" : dictFacture["code_comptable_famille"],
                    })

                # Analyse des prestations
                if dictPrestations.has_key(dictFacture["IDfacture"]) :
                    totalPrestationsFacture = FloatToDecimal(0.0)
                    for dictPrestation in dictPrestations[dictFacture["IDfacture"]] :
                        
                        if dictPrestation["montant"] != FloatToDecimal(0.0) :
                            
                            totalPrestationsFacture += dictPrestation["montant"]
                            
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
                            
                            # Vérifie si code compta présent
                            if dictPrestation["nomAbregeActivite"] in (None, ""):
                                labelActivite = ""
                            else :
                                labelActivite = u"%s - " % dictPrestation["nomAbregeActivite"]
                            intituleTemp = "%s%s" % (labelActivite, dictPrestation["label"])
                            if code_compta == "" :
                                if intituleTemp not in listeCodesManquants :
                                    listeCodesManquants.append(intituleTemp)
                                code_compta = self.dictParametres["code_ventes"]
                            dictCodes[intituleTemp] = code_compta
                            
                            # Formatage libellé prestation
                            libelle_prestation = self.dictParametres["format_prestation"]
                            listeMotsCles = [
                                ("{IDPRESTATION}", str(dictPrestation["IDprestation"])),
                                ("{DATE}", FormateDate(dictPrestation["date_prestation"])),
                                ("{LIBELLE}", dictPrestation["label"]),
                                ("{ACTIVITE}", dictPrestation["nomActivite"]),
                                ("{ACTIVITE_ABREGE}", dictPrestation["nomAbregeActivite"]),
                                ("{TARIF}", dictPrestation["nomTarif"]),
                                ("{INDIVIDU_NOM}", dictPrestation["nomIndividu"]),
                                ("{INDIVIDU_PRENOM}", dictPrestation["prenomIndividu"]),
                                ]
                            for motcle, valeur in listeMotsCles :
                                libelle_prestation = libelle_prestation.replace(motcle, valeur)

                            listeLignes.append({
                                "type" : "prestation",
                                "date_prestation" : dictPrestation["date_prestation"],
                                "date_facture" : dictFacture["date_edition"],
                                "code_compta" : code_compta,
                                "libelle_prestation" : libelle_prestation,
                                "libelle_original" : dictPrestation["label"],
                                "numero_facture" : dictFacture["numero"],
                                "montant" : dictPrestation["montant"],
                                "date_echeance" : dictFacture["date_echeance"],
                                "individu_nom" : dictPrestation["nomIndividu"],
                                "individu_prenom" : dictPrestation["prenomIndividu"],
                                "intituleTemp" : intituleTemp,
                                })
                
                # Vérifie que le total des prestations correspond au montant de la facture
                if dictFacture["total"] != totalPrestationsFacture :
                    listeAnomalies.append(u"- Le total des prestations de la facture n°%s du %s (%s) ne correspond pas au montant initial de la facture." % (dictFacture["numero"], FormateDate(dictFacture["date_edition"], "%d/%m/%Y"), nomFamille) )
            
            
##        if len(listeCodesManquants) > 0 :
##            message1 = u"""Des codes comptables sont manquants pour les prestations ci-dessous.\n
##Vous pouvez attribuer les codes comptables à des activités (Depuis le paramétrage 
##de l'activité), ou à des tarifs (Depuis le paramétrage des tarifs), ou à des cotisations
##(depuis le paramétrage des cotisations) ou à des prestations (depuis la fiche familiale 
##Onglet Prestations)."""
##            message2 = u"\n- " .join(listeCodesManquants)
##            dlg = dialogs.MultiMessageDialog(None, message1, caption=u"Codes comptables manquants", msg2=u"- " + message2, style = wx.ICON_ERROR | wx.OK, btnLabels={wx.ID_OK : u"Ok"})
##            dlg.ShowModal() 
##            dlg.Destroy() 
##            return False
        
        del dlgAttente
        
        # Affichage des anomalies
        if len(listeAnomalies) > 0 :
##            if len(listeAnomalies) > 1 :
##                message1 = u"%d anomalies ont été détectées :" % len(listeAnomalies)
##            else :
##                message1 = u"1 anomalie a été détectée :"
##            message2 = u"\n" .join(listeAnomalies)
##            dlg = dialogs.MultiMessageDialog(None, message1, caption=u"Anomalies", msg2=message2 + "\n\n\n", style = wx.ICON_ERROR | wx.OK, btnLabels={wx.ID_OK : u"Ok"})
##            dlg.ShowModal() 
##            dlg.Destroy() 
##            return False
        
            # Propose le correcteur d'anomalies
            dlg = wx.MessageDialog(None, u"Des anomalies ont été détectées dans certaines factures.\n\nSouhaitez-vous lancer le correcteur d'anomalies afin de les corriger dès à présent (Conseillé) ?", u"Anomalies", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse == wx.ID_YES :
                import DLG_Depannage
                dlg = DLG_Depannage.Dialog(None)
                dlg.ShowModal() 
                dlg.Destroy()
            return False

        # Affichage des codes comptables
        dlg = Dialog_codes(None, donnees=dictCodes)
        if dlg.ShowModal() == wx.ID_OK :
            dictCodes = dlg.GetCodes() 
            dlg.Destroy() 
        else :
            dlg.Destroy() 
            return False
        index = 0
        for dictTemp in listeLignes :
            if dictTemp["type"] == "prestation" :
                intituleTemp = dictTemp["intituleTemp"] 
                if dictCodes.has_key(intituleTemp) :
                    listeLignes[index]["code_compta"] = dictCodes[intituleTemp]
            index += 1
            
        # Recherche des prestations de la période non facturées
        DB = GestionDB.DB() 
        req = """SELECT IDprestation, date, label, montant, IDfamille, activites.abrege
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        WHERE IDfacture IS NULL AND date>='%s' AND date<='%s'
        ORDER BY date
        ;""" % (self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq() 
        DB.Close()
        listePrestationsSansFactures = []
        totalPrestationsSansFactures = FloatToDecimal(0.0)
        for IDprestation, date, label, montant, IDfamille, abregeActivite in listeDonnees :
            totalPrestationsSansFactures += FloatToDecimal(montant)
            date = FormateDate(UTILS_Dates.DateEngEnDateDD(date), "%d/%m/%Y")
            if self.dictTitulaires.has_key(IDfamille) :
                nomFamille = self.dictTitulaires[IDfamille]["titulairesSansCivilite"]
            else :
                nomFamille = u"Famille inconnue"
            montant = u"%.2f %s" % (montant, SYMBOLE)
            if abregeActivite != None :
                label = u"%s - %s" % (abregeActivite, label)
            listePrestationsSansFactures.append(u"- %s : %s (%s | %s)" % (date, label, montant, nomFamille))
        
        if len(listePrestationsSansFactures) > 0 :
            message1 = u"Attention, %d prestations (%s) de cette période n'apparaissent sur aucune facture. Ces prestations ne figureront pas dans les écritures comptables. Il est donc conseillé de quitter et générer depuis le menu Facturation les factures correspondantes avant de lancer l'export des écritures comptables.\n\nSouhaitez-vous quand même continuer ?" % (len(listePrestationsSansFactures), u"%.2f %s" % (totalPrestationsSansFactures, SYMBOLE))
            message2 = u"\n" .join(listePrestationsSansFactures)
            dlg = dialogs.MultiMessageDialog(None, message1, caption=u"Avertissement", msg2=message2 + "\n\n\n", style = wx.ICON_EXCLAMATION | wx.OK | wx.CANCEL, icon=None, btnLabels={wx.ID_OK : u"Oui", wx.ID_CANCEL : u"Non"})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            if reponse != wx.ID_OK :
                return False
        
        return listeLignes


    def GetDepots(self, typeComptable="banque"):
        DB = GestionDB.DB() 
        
        # Dépôts de règlements
        req = """SELECT 
        depots.IDdepot, depots.date, depots.nom, reglements.IDmode, modes_reglements.label, modes_reglements.type_comptable,
        SUM(reglements.montant), COUNT(reglements.IDreglement)
        FROM depots
        LEFT JOIN reglements ON reglements.IDdepot = depots.IDdepot
        LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
        WHERE depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s' AND modes_reglements.type_comptable='%s'
        GROUP BY depots.IDdepot, reglements.IDmode
        ORDER BY depots.date;""" % (self.date_debut, self.date_fin, typeComptable)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeDepots = []
        for IDdepot, date, nomDepot, IDmode, nomMode, type_comptable, montant, nbreReglements in listeDonnees :
            listeDepots.append({
                "IDdepot" : IDdepot, "date_depot" : UTILS_Dates.DateEngEnDateDD(date), "nom_depot" : nomDepot, "IDmode" : IDmode, "nomMode" : nomMode, 
                "type_comptable" : type_comptable, "montant" : FloatToDecimal(montant), "nbreReglements" : nbreReglements, 
                })
        
        # Règlements
        req = """SELECT 
        reglements.IDreglement, reglements.IDcompte_payeur, reglements.date, 
        reglements.IDmode, modes_reglements.label, 
        reglements.numero_piece, reglements.montant, 
        payeurs.IDpayeur, payeurs.nom, 
        numero_quittancier, reglements.IDcompte, date_differe, 
        encaissement_attente, 
        reglements.IDdepot, depots.date, depots.nom,  
        date_saisie, comptes_payeurs.IDfamille
        FROM reglements
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        WHERE reglements.IDdepot IS NOT NULL AND depots.date IS NOT NULL AND depots.date>='%s' AND depots.date<='%s'
        GROUP BY reglements.IDreglement
        ORDER BY reglements.date;
        """ % (self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        dictReglementsDepots = {}
        for IDreglement, IDcompte_payeur, dateReglement, IDmode, labelMode, numero_piece, montant, IDpayeur, nomPayeur, numero_quittancier, IDcompte, date_differe, attente, IDdepot, dateDepot, nomDepot, date_saisie, IDfamille in listeDonnees :
            if dictReglementsDepots.has_key(IDdepot) == False :
                dictReglementsDepots[IDdepot] = []
            dictReglementsDepots[IDdepot].append({
                "IDreglement" : IDreglement, "IDcompte_payeur" : IDcompte_payeur, "dateReglement" : UTILS_Dates.DateEngEnDateDD(dateReglement), "IDmode" : IDmode, "labelMode" : labelMode, "numero_piece" : numero_piece, 
                "montant" : FloatToDecimal(montant), "IDpayeur" : IDpayeur, "nomPayeur" : nomPayeur, "numero_quittancier" : numero_quittancier, "IDcompte" : IDcompte, "date_differe" : UTILS_Dates.DateEngEnDateDD(date_differe), 
                "attente" : attente, "dateDepot" : UTILS_Dates.DateEngEnDateDD(dateDepot), "nomDepot" : nomDepot, "date_saisie" : date_saisie, "IDfamille" : IDfamille,
                })
        
        # Analyse des dépôts
        listeLignes = []
        for dictDepot in listeDepots :
            
            # Formatage libellé dépôt
            libelle_depot = self.dictParametres["format_depot"]
            listeMotsCles = [
                ("{IDDEPOT}", str(dictDepot["IDdepot"])),
                ("{NOM_DEPOT}", dictDepot["nom_depot"]), 
                ("{DATE_DEPOT}", FormateDate(dictDepot["date_depot"])), 
                ("{MODE_REGLEMENT}", dictDepot["nomMode"]),
                ("{TYPE_COMPTABLE}", dictDepot["type_comptable"]),
                ("{NBRE_REGLEMENTS}", str(dictDepot["nbreReglements"])),
                ]
            for motcle, valeur in listeMotsCles :
                libelle_depot = libelle_depot.replace(motcle, valeur)
            
            # Mémorisation ligne dépôt
            listeLignes.append({
                "type" : "depot",
                "IDdepot" : dictDepot["IDdepot"],
                "libelle_depot" : libelle_depot,
                "nom_depot" : dictDepot["nom_depot"],
                "date_depot" : dictDepot["date_depot"],
                "mode_reglement" : dictDepot["nomMode"],
                "montant" : str(dictDepot["montant"]),
                })
                        
            # Analyse des règlements
            if dictReglementsDepots.has_key(dictDepot["IDdepot"]) :
                for dictReglement in dictReglementsDepots[dictDepot["IDdepot"]] :

                    if self.dictTitulaires.has_key(dictReglement["IDfamille"]) :
                        nomFamille = self.dictTitulaires[dictReglement["IDfamille"]]["titulairesSansCivilite"]
                    else :
                        nomFamille = ""

                    # Formatage libellé Règlement
                    libelle_reglement = self.dictParametres["format_reglement"]
                    listeMotsCles = [
                        ("{IDREGLEMENT}", str(dictReglement["IDreglement"])),
                        ("{NOM_FAMILLE}", nomFamille),
                        ("{DATE}", FormateDate(dictReglement["dateReglement"])),
                        ("{MODE_REGLEMENT}", dictReglement["labelMode"]),
                        ("{NUMERO_PIECE}", dictReglement["numero_piece"]),
                        ("{NOM_PAYEUR}", dictReglement["nomPayeur"]),
                        ("{NUMERO_QUITTANCIER}", dictReglement["numero_quittancier"]),
                        ("{DATE_DEPOT}", FormateDate(dictReglement["dateDepot"])),
                        ("{NOM_DEPOT}", dictReglement["nomDepot"]),
                        ]
                    for motcle, valeur in listeMotsCles :
                        if valeur == None : valeur = ""
                        libelle_reglement = libelle_reglement.replace(motcle, valeur)

                    listeLignes.append({
                        "type" : "reglement",
                        "IDreglement" : dictReglement["IDreglement"],
                        "dateReglement" : dictReglement["dateReglement"],
                        "nomFamille" : nomFamille,
                        "libelle_reglement" : libelle_reglement,
                        "IDmode" : dictReglement["IDmode"],
                        "labelMode" : dictReglement["labelMode"],
                        "numero_piece" : dictReglement["numero_piece"],
                        "montant" : dictReglement["montant"],
                        "nomPayeur" : dictReglement["nomPayeur"],
                        "numero_quittancier" : dictReglement["numero_quittancier"],
                        "date_differe" : dictReglement["date_differe"],
                        "attente" : dictReglement["attente"],
                        "date_depot" : dictReglement["dateDepot"],
                        "nom_depot" : dictReglement["nomDepot"],
                        })

        return listeLignes
        
        
        
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wxpg.PropertyGrid) :
    def __init__(self, parent, listeDonnees=[]):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=wxpg.PG_SPLITTER_AUTO_CENTER )
        self.parent = parent
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        couleurFond = "#e5ecf3"
        self.SetCaptionBackgroundColour(couleurFond)
        self.SetMarginColour(couleurFond)
        for valeur in listeDonnees :
            if type(valeur) == dict :
                propriete = wxpg.StringProperty(label=valeur["label"], name=valeur["code"], value=valeur["defaut"])
                propriete.SetHelpString(valeur["tip"]) 
                self.Append(propriete)
            else :
                self.Append(wxpg.PropertyCategory(valeur))

    def Validation(self):
        # Période
        if self.parent.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement renseigner la date de début de période", u"Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.parent.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement renseigner la date de fin de période", u"Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Paramètres
        for valeur in self.listeDonnees :
            if type(valeur) == dict :
                if valeur["type"] == "chaine" and self.GetPropertyValue(valeur["code"]) == "" :
                    dlg = wx.MessageDialog(self, u"Vous devez obligatoirement renseigner l'information '%s' !" % valeur["description"], u"Information", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        return True

    def GetParametres(self):
        dictParametres = self.GetPropertyValues()
        dictParametres["date_debut"] = self.parent.ctrl_date_debut.GetDate() 
        dictParametres["date_fin"] = self.parent.ctrl_date_fin.GetDate() 
        return dictParametres

    def CreationFichier(self, nomFichier="", texte=""):
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier texte (*.txt)|*.txt|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = u"Veuillez sélectionner le répertoire de destination et le nom du fichier", defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?", "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Création du fichier texte
        f = open(cheminFichier, "w")
        f.write(texte.encode("iso-8859-15"))
        f.close()
        
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = u"Le fichier a été créé avec succès.\n\nSouhaitez-vous l'ouvrir dès maintenant ?"
        dlgConfirm = wx.MessageDialog(None, txtMessage, u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres_ebp(CTRL_Parametres) :
    def __init__(self, parent):
        self.listeDonnees = [
            u"Codes journaux",
            {"type":"chaine", "label":u"Ventes", "description":u"Code journal des ventes", "code":"journal_ventes", "tip":u"Saisissez le code journal des ventes", "defaut":u"VE"},
            {"type":"chaine", "label":u"Banque", "description":u"Code journal de la banque", "code":"journal_banque", "tip":u"Saisissez le code journal de la banque", "defaut":u"BP"},
            {"type":"chaine", "label":u"Caisse", "description":u"Code journal de la caisse", "code":"journal_caisse", "tip":u"Saisissez le code journal de la caisse", "defaut":u"CA"},
            u"Codes comptables",
            {"type":"chaine", "label":u"Ventes", "description":u"Code comptable des ventes", "code":"code_ventes", "tip":u"Saisissez le code comptable des ventes (Peut être ajusté en détail dans le paramétrage des activités, des cotisations, des tarifs et des prestations)", "defaut":u"706"},
            {"type":"chaine", "label":u"Clients", "description":u"Code comptable des clients", "code":"code_clients", "tip":u"Saisissez le code comptable des clients (Peut- être ajusté en détail dans la fiche famille)", "defaut":u"411"},
            {"type":"chaine", "label":u"Banque", "description":u"Code comptable de la banque", "code":"code_banque", "tip":u"Saisissez le code comptable de la banque", "defaut":u"512"},
            {"type":"chaine", "label":u"Caisse", "description":u"Code comptable de la caisse", "code":"code_caisse", "tip":u"Saisissez le code comptable de la caisse", "defaut":u"531"},
            u"Formats libellés",
            {"type":"chaine", "label":u"Facture", "description":u"Format du libellé des factures", "code":"format_facture", "tip":u"Saisissez le format du libellé des factures. Vous pouvez utiliser les mots-clés suivants : {IDFACTURE} {NOM_FAMILLE} {NUMERO} {DATE_EDITION} {DATE_ECHEANCE} {DATE_DEBUT} {DATE_FIN} {NOM_LOT}.", "defaut":u"Facture {NOM_FAMILLE}"},
            {"type":"chaine", "label":u"Prestation", "description":u"Format du libellé des prestations", "code":"format_prestation", "tip":u"Saisissez le format du libellé des prestations. Vous pouvez utiliser les mots-clés suivants : {IDPRESTATION} {DATE} {LIBELLE} {ACTIVITE} {ACTIVITE_ABREGE} {TARIF} {INDIVIDU_NOM} {INDIVIDU_PRENOM}", "defaut":u"{LIBELLE} {INDIVIDU_NOM} {INDIVIDU_PRENOM}"},
            {"type":"chaine", "label":u"Dépôt", "description":u"Format du libellé des dépôts", "code":"format_depot", "tip":u"Saisissez le format du libellé des dépôts. Vous pouvez utiliser les mots-clés suivants : {IDDEPOT} {NOM_DEPOT} {DATE_DEPOT} {MODE_REGLEMENT} {TYPE_COMPTABLE} {NBRE_REGLEMENTS}.", "defaut":u"{NOM_DEPOT}"},
            {"type":"chaine", "label":u"Règlement", "description":u"Format du libellé des règlements", "code":"format_reglement", "tip":u"Saisissez le format du libellé des règlements. Vous pouvez utiliser les mots-clés suivants : {IDREGLEMENT} {DATE} {MODE_REGLEMENT} {NOM_FAMILLE} {NUMERO_PIECE} {NOM_PAYEUR} {NUMERO_QUITTANCIER} {DATE_DEPOT} {NOM_DEPOT}.", "defaut":u"{MODE_REGLEMENT} {NOM_FAMILLE}"},
            ]
        CTRL_Parametres.__init__(self, parent, self.listeDonnees)

    def Generation(self):
        if self.Validation() == False : return False
        
        # Récupération des paramètres
        dictParametres = self.GetParametres() 
        donnees = Donnees(dictParametres)
        lignesVentes = donnees.GetVentes() 
        if lignesVentes == False : 
            return False
    
        numLigne = 1
        listeLignesTxt = []
        
        # Ventes
        for ligne in lignesVentes :
            
            # Facture
            if ligne["type"] == "facture" :

                if ligne["code_comptable_famille"] not in ("", None):
                    code_comptable = ligne["code_comptable_famille"]
                else :
                    code_comptable = dictParametres["code_clients"]
                
                ligneTemp = [
                    str(numLigne),
                    FormateDate(ligne["date_edition"], "%d%m%Y"),
                    dictParametres["journal_ventes"],
                    code_comptable,
                    "",
                    u'"%s"' % ligne["libelle_facture"],
                    u'"%s"' % ligne["numero"],
                    str(ligne["montant"]),
                    "D",
                    FormateDate(ligne["date_echeance"], "%d%m%Y"),
                    "EUR",
                    ]
                listeLignesTxt.append(",".join(ligneTemp))
                numLigne += 1

            # Prestation
            if ligne["type"] == "prestation" :

                ligneTemp = [
                    str(numLigne),
                    FormateDate(ligne["date_facture"], "%d%m%Y"),
                    dictParametres["journal_ventes"],
                    ligne["code_compta"],
                    "",
                    u'"%s"' % ligne["libelle_prestation"],
                    u'"%s"' % ligne["numero_facture"],
                    str(ligne["montant"]),
                    "C",
                    FormateDate(ligne["date_echeance"], "%d%m%Y"),
                    "EUR",
                    ]
                listeLignesTxt.append(",".join(ligneTemp))
                numLigne += 1
        
        # Banque
        for typeComptable in ("banque", "caisse") :
            
            lignesTemp = donnees.GetDepots(typeComptable=typeComptable) 
            for ligne in lignesTemp :
                
                # Dépôts
                if ligne["type"] == "depot" :

                    ligneTemp = [
                        str(numLigne),
                        FormateDate(ligne["date_depot"], "%d%m%Y"),
                        dictParametres["journal_%s" % typeComptable],
                        dictParametres["code_%s" % typeComptable],
                        "",
                        u'"%s"' % ligne["libelle_depot"],
                        u'""',
                        str(ligne["montant"]),
                        "D",
                        "",
                        "EUR",
                        ]
                    listeLignesTxt.append(",".join(ligneTemp))
                    numLigne += 1
            
                # Règlements
                if ligne["type"] == "reglement" :
                        
                    ligneTemp = [
                        str(numLigne),
                        FormateDate(ligne["date_depot"], "%d%m%Y"),
                        dictParametres["journal_%s" % typeComptable],
                        dictParametres["code_clients"],
                        "",
                        u'"%s"' % ligne["libelle_reglement"],
                        u'"%s"' % ligne["IDreglement"],
                        str(ligne["montant"]),
                        "C",
                        "",
                        "EUR",
                        ]
                    listeLignesTxt.append(",".join(ligneTemp))
                    numLigne += 1
        
        # Finalisation du texte
        texte = "\n".join(listeLignesTxt)
        self.CreationFichier(nomFichier=u"Export.txt", texte=texte)
        
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        # Bandeau
        intro = u"Sélectionnez les dates de la période à exporter, choisissez un logiciel de destination puis renseignez les paramètres nécessaires avant de lancer l'exportation."
        titre = u"Export des écritures comptables"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Export_comptable.png")
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Période")
        self.label_date_debut = wx.StaticText(self, wx.ID_ANY, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, wx.ID_ANY, u"au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, wx.ID_ANY, u"Paramètres")
        self.ctrl_labelbook = LB.FlatImageBook(self, -1, agwStyle=LB.INB_LEFT | LB.INB_BORDER | LB.INB_BOLD_TAB_SELECTION)
        self.InitLabelbook() 

        # Boutons
        self.bouton_aide = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(u"Saisissez la date de début de la période à exporter")
        self.ctrl_date_fin.SetToolTipString(u"Saisissez la date de fin de la période à exporter")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour lancer la génération des fichiers d'exportation")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize((500, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(1, 5, 5, 5)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_periode, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        box_parametres.Add(self.ctrl_labelbook, 1, wx.ALL | wx.EXPAND, 10)
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

    def InitLabelbook(self):
        self.listePages = [
            {"index":0, "label":u"EBP Compta", "ctrl":CTRL_Parametres_ebp(self), "image":wx.Bitmap('Images/48x48/Logiciel_ebp.png', wx.BITMAP_TYPE_PNG)},
            {"index":1, "label":u"CIEL Compta", "ctrl":CTRL_Parametres_ebp(self), "image":wx.Bitmap('Images/48x48/Logiciel_ciel.png', wx.BITMAP_TYPE_PNG)},
            ]
        # Création de l'ImageList
        il = wx.ImageList(48, 48)
        for dictPage in self.listePages:
            il.Add(dictPage["image"])
        self.ctrl_labelbook.AssignImageList(il)
        # Création des pages
        for dictPage in self.listePages:
            self.ctrl_labelbook.AddPage(dictPage["ctrl"], dictPage["label"], imageId=dictPage["index"])

    def OnBoutonAide(self, event):  
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        indexPage = self.ctrl_labelbook.GetSelection()
        ctrl = self.listePages[indexPage]["ctrl"]
        ctrl.Generation()
        
        



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Codes(wxpg.PropertyGrid) :
    def __init__(self, parent, donnees=None):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=wxpg.PG_SPLITTER_AUTO_CENTER )
        self.parent = parent
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        couleurFond = "#e5ecf3"
        self.SetCaptionBackgroundColour(couleurFond)
        self.SetMarginColour(couleurFond)
        for label, valeur in donnees.iteritems() :
            if valeur == None : valeur = ""
            propriete = wxpg.StringProperty(label=label, name=label, value=valeur)
            self.Append(propriete)

    def Validation(self):
        for label, valeur in self.GetPropertyValues().iteritems() :
            if valeur == "" :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement le code comptable de la prestation '%s' !" % label, u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

    def GetCodes(self):
        dictCodes = self.GetPropertyValues()
        return dictCodes




class Dialog_codes(wx.Dialog):
    def __init__(self, parent, donnees=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.donnees = donnees
        
        self.label_intro = wx.StaticText(self, wx.ID_ANY, u"Veuillez vérifier ci-dessous que les codes comptables attribués à chaque prestation facturée sont exacts. \nVous pouvez les renseigner de 2 façons : depuis le paramétrage des activites, des cotisations, des tarifs \nou des prestations - ou provisoirement dans le tableau ci-desssous : ")
        self.ctrl_codes = CTRL_Codes(self, donnees=donnees)
        self.bouton_ok = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        # Propriétés
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize((590, 600))
        
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
    dlg.ctrl_date_debut.SetDate("2013-01-01")
    dlg.ctrl_date_fin.SetDate("2013-01-05")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()


##    donnees = {
##        u"journée sans repas" : None,
##        u"Demi-journée avec repas" : u"706ALSH",
##        }
##    dlg = Dialog_codes(None, donnees=donnees)
##    app.SetTopWindow(dlg)
##    dlg.ShowModal()
##    app.MainLoop()
