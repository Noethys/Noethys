#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import wx.lib.agw.hypertreelist as HTL

import CTRL_Bandeau
import UTILS_Identification
import GestionDB
from CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def ConvertStrToListe(texte=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None :
        return None
    listeResultats = []
    temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats




class Forfaits():
    def __init__(self, IDfamille=None, listeActivites=[], listeIndividus=[], saisieManuelle=True, saisieAuto=True):
        self.IDfamille = IDfamille
        self.listeActivites = listeActivites
        self.listeIndividus = listeIndividus
        self.saisieManuelle = saisieManuelle
        self.saisieAuto = saisieAuto
    
    def GetForfaits(self):
        """ Permet d'obtenir la liste des forfaits disponibles """
        DB = GestionDB.DB()
        
        # Recherche les activites disponibles
        dictActivites = {}
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        req = """SELECT activites.IDactivite, activites.nom, abrege, date_debut, date_fin
        FROM activites
        WHERE activites.IDactivite IN %s
        ORDER BY activites.nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()      
        for IDactivite, nom, abrege, date_debut, date_fin in listeActivites :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            dictTemp = { "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "tarifs" : [], "ouvertures" : {} }
            dictActivites[IDactivite] = dictTemp
        
        # Recherche des ouvertures des activités
        req = """SELECT IDouverture, IDactivite, IDunite, IDgroupe, date
        FROM ouvertures
        WHERE IDactivite IN %s
        ORDER BY date;""" % conditionActivites
        DB.ExecuterReq(req)
        listeOuvertures = DB.ResultatReq()      
        dictOuvertures = {}
        for IDouverture, IDactivite, IDunite, IDgroupe, date in listeOuvertures :
            date = DateEngEnDateDD(date)
            if dictActivites.has_key(IDactivite) :
                if dictActivites[IDactivite]["ouvertures"].has_key(IDgroupe) == False :
                    dictActivites[IDactivite]["ouvertures"][IDgroupe] = {}
                if dictActivites[IDactivite]["ouvertures"][IDgroupe].has_key(date) == False :
                    dictActivites[IDactivite]["ouvertures"][IDgroupe][date] = []
                dictActivites[IDactivite]["ouvertures"][IDgroupe][date].append((date, IDunite, IDgroupe))
                        
        # Recherche les combinaisons d'unités des tarifs
        req = """SELECT combi_tarifs_unites.IDcombi_tarif_unite, combi_tarifs_unites.IDcombi_tarif, 
        combi_tarifs_unites.IDtarif, combi_tarifs_unites.IDunite, date, type, IDgroupe
        FROM combi_tarifs_unites
        LEFT JOIN combi_tarifs ON combi_tarifs.IDcombi_tarif = combi_tarifs_unites.IDcombi_tarif
        WHERE type='FORFAIT';"""
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        dictCombiUnites = {}
        for IDcombi_tarif_unite, IDcombi_tarif, IDtarif, IDunite, date, type, IDgroupe in listeUnites :
            date = DateEngEnDateDD(date)
            if dictCombiUnites.has_key(IDtarif) == False :
                dictCombiUnites[IDtarif] = {}
            if dictCombiUnites[IDtarif].has_key(IDcombi_tarif) == False :
                dictCombiUnites[IDtarif][IDcombi_tarif] = []
            dictCombiUnites[IDtarif][IDcombi_tarif].append((date, IDunite, IDgroupe),)
        
        # Recherche des lignes de calcul
        champsTable = ", ".join(CHAMPS_TABLE_LIGNES)
        req = """SELECT %s
        FROM tarifs_lignes
        ORDER BY num_ligne;""" % champsTable
        DB.ExecuterReq(req)
        listeLignes = DB.ResultatReq()
        dictLignesCalcul = {}
        for valeurs in listeLignes :
            dictTemp = {}
            indexValeur = 0
            for valeur in valeurs :
                if valeur == "None" : valeur = None
                dictTemp[CHAMPS_TABLE_LIGNES[indexValeur]] = valeur
                indexValeur += 1
            if dictLignesCalcul.has_key(dictTemp["IDtarif"]) == False :
                dictLignesCalcul[dictTemp["IDtarif"]] = [dictTemp,]
            else:
                dictLignesCalcul[dictTemp["IDtarif"]].append(dictTemp)
        
        # Recherche des tarifs pour chaque activité
        condition = "WHERE type='FORFAIT' AND forfait_saisie_manuelle=%s AND forfait_saisie_auto=%d" % (int(self.saisieManuelle), int(self.saisieAuto))
        req = """SELECT 
        IDtarif, tarifs.IDactivite, tarifs.IDnom_tarif, nom, date_debut, date_fin, 
        forfait_saisie_manuelle, forfait_saisie_auto, forfait_suppression_auto,
        methode, categories_tarifs, groupes, options, date_facturation
        FROM tarifs
        LEFT JOIN noms_tarifs ON noms_tarifs.IDnom_tarif = tarifs.IDnom_tarif
        %s
        ORDER BY date_debut;""" % condition
        DB.ExecuterReq(req)
        listeTarifs = DB.ResultatReq()      
        for IDtarif, IDactivite, IDnom_tarif, nom, date_debut, date_fin, forfait_saisie_manuelle, forfait_saisie_auto, forfait_suppression_auto, methode, categories_tarifs, groupes, options, date_facturation in listeTarifs :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            listeCategoriesTarifs = ConvertStrToListe(categories_tarifs)
            listeGroupes = ConvertStrToListe(groupes)

            dictTemp = {
                "IDtarif" : IDtarif, "IDactivite" : IDactivite, 
                "IDnom_tarif" : IDnom_tarif, "nom_tarif" : nom, "date_debut" : date_debut, "date_fin" : date_fin, 
                "forfait_saisie_manuelle" : forfait_saisie_manuelle, "forfait_saisie_auto" : forfait_saisie_auto, 
                "forfait_suppression_auto" : forfait_suppression_auto, "methode" : methode,
                "categories_tarifs" : listeCategoriesTarifs, "groupes" : listeGroupes, "options" : options, "date_facturation" : date_facturation,
                "combinaisons" : [], "lignes_calcul" : [],
                }
                
            # Recherche si ce tarif a des combinaisons d'unités
            if dictCombiUnites.has_key(IDtarif) :
                listeCombinaisons = []
                for IDcombi, listeCombis in dictCombiUnites[IDtarif].iteritems() :
                    listeCombinaisons.append(tuple(listeCombis))
                listeCombinaisons.sort() 
                dictTemp["combinaisons"] = listeCombinaisons
                dictTemp["forfait_saisie_manuelle"] = forfait_saisie_manuelle
                dictTemp["forfait_saisie_auto"] = forfait_saisie_auto
                dictTemp["forfait_suppression_auto"] = forfait_suppression_auto
                
            # Recherche si ce tarif a des lignes de calcul
            if dictLignesCalcul.has_key(IDtarif):
                dictTemp["lignes_calcul"] = dictLignesCalcul[IDtarif]
            
            # Mémorisation de ce tarif
            if dictActivites.has_key(IDactivite) == True :
                dictActivites[IDactivite]["tarifs"].append(dictTemp)

        # Cloture de la base de données
        DB.Close()
        
        return dictActivites

    def Applique_forfait(self, selectionIDcategorie_tarif=None, selectionIDtarif=None, inscription=False, selectionIDactivite=None):
        """ Recherche et applique les forfaits auto à l'inscription """
        dictUnites = self.GetDictUnites() 
        dictInscriptions = self.GetInscriptions() 
        dictComptesPayeurs = self.GetComptesPayeurs() 
        dictQuotientsFamiliaux = self.GetQuotientsFamiliaux() 
        dictAides = self.GetAides() 
        dictActivites = self.GetForfaits()
        nbre_forfaits_saisis = 0

        for IDindividu in self.listeIndividus :
            for IDactivite, dictActivite in dictActivites.iteritems() :
                nomActivite = dictActivite["nom"]
                date_debut_activite = dictActivite["date_debut"]
                date_fin_activite = dictActivite["date_fin"]
                dictTarifs = dictActivite["tarifs"]
                
                # Récupération des informations sur l'inscription
                for dictInscription in dictInscriptions[IDindividu]["inscriptions"] :
                    if dictInscription["IDactivite"] == IDactivite :
                        IDinscription = dictInscription["IDinscription"] 
                        IDgroupe = dictInscription["IDgroupe"] 
                        IDcategorie_tarif_temp = dictInscription["IDcategorie_tarif"] 
                        break

                if selectionIDcategorie_tarif == None :
                    IDcategorie_tarif = IDcategorie_tarif_temp
                else :
                    IDcategorie_tarif = selectionIDcategorie_tarif
                
                dictUnitesPrestations = {}     
                listeNouvellesPrestations = []   
                
                for dictTarif in dictActivite["tarifs"] :
                    if True :
                        IDtarif = dictTarif["IDtarif"]
                        
                        # Sélectionne les combinaisons données ou les ouvertures de l'activités
                        options = dictTarif["options"]
                        if options != None and "calendrier" in options :
                            combinaisons = []
                            if dictActivites[IDactivite]["ouvertures"].has_key(IDgroupe) :
                                for dateTemp, listeCombis in dictActivites[IDactivite]["ouvertures"][IDgroupe].iteritems() :
                                    if dateTemp >= dictTarif["date_debut"] and (dictTarif["date_fin"] == None or dateTemp <= dictTarif["date_fin"]) :
                                        combinaisons.append(tuple(listeCombis))
                                combinaisons.sort() 
                        else :
                            combinaisons = dictTarif["combinaisons"]
                        
                        # Vérifie si groupe ok ?
                        listeGroupes = dictTarif["groupes"]
                        if listeGroupes == None :
                            groupeValide = True
                        else:
                            if IDgroupe in listeGroupes :
                                groupeValide = True
                            else:
                                groupeValide = False
                        
                        # Ne sélectionne que ceux qui doivent être saisis automatiquement à l'inscription
                        if groupeValide == True and IDcategorie_tarif in dictTarif["categories_tarifs"] :
                            if (inscription == False and selectionIDtarif == IDtarif) or (inscription == True and selectionIDactivite == IDactivite and dictTarif["forfait_saisie_auto"] == 1) :
                                
                                nom_tarif = dictTarif["nom_tarif"]
                                methode_calcul = dictTarif["methode"]
                                montant_tarif = 0.0
                                
                                # Recherche de la date de facturation
                                if len(combinaisons) > 0 :
                                    date_debut_forfait = combinaisons[0][0][0]
                                else:
                                    date_debut_forfait = date_debut_activite #datetime.date.today()

                                date_facturation_tarif = dictTarif["date_facturation"]
                                if date_facturation_tarif == "date_debut_forfait" : 
                                    date_facturation = date_debut_forfait
                                elif date_facturation_tarif == "date_saisie" : 
                                    date_facturation = datetime.date.today()
                                elif date_facturation_tarif == "date_debut_activite" : 
                                    date_facturation = date_debut_activite
                                elif date_facturation_tarif != None and date_facturation_tarif.startswith("date:") : 
                                    date_facturation = DateEngEnDateDD(date_facturation_tarif[5:])
                                else :
                                    date_facturation = date_debut_forfait
                                
                                # Suppression autorisée ?
                                if dictTarif["forfait_suppression_auto"] == 1 :
                                    type_forfait = 2
                                else:
                                    type_forfait = 1

                                # Récupération des consommations à créer
                                listeConsommations = []
                                listeDatesStr = []
                                for combi in combinaisons :
                                    for date, IDunite, IDgroupeTemp in combi :
                                        if IDgroupeTemp == IDgroupe or IDgroupeTemp == None :
                                            listeConsommations.append( {"date" : date, "IDunite" : IDunite} )
                                            if date not in listeDatesStr : listeDatesStr.append(str(date))
                                
                                # Vérifie que les dates ne sont pas déjà prises
                                DB = GestionDB.DB()
                                if len(listeDatesStr) == 0 : conditionDates = "()"
                                elif len(listeDatesStr) == 1 : conditionDates = "('%s')" % listeDatesStr[0]
                                else : conditionDates = str(tuple(listeDatesStr))
                                req = """SELECT IDconso, date, IDunite
                                FROM consommations 
                                WHERE IDindividu=%d AND date IN %s
                                ; """ % (IDindividu, conditionDates)
                                DB.ExecuterReq(req)
                                listeConsoExistantes = DB.ResultatReq()
                                DB.Close()
                                listeDatesPrises = []
                                for IDconso, dateConso, IDuniteConso in listeConsoExistantes :
                                    dateConso = DateEngEnDateDD(dateConso)
                                    if {"date" : dateConso, "IDunite" : IDuniteConso} in listeConsommations :
                                        if dateConso not in listeDatesPrises :
                                            listeDatesPrises.append(dateConso)
                                
                                if len(listeDatesPrises) > 0 :
                                    texteDatesPrises = u""
                                    for datePrise in listeDatesPrises :
                                        texteDatesPrises += u"   > %s\n" % DateComplete(datePrise)
                                    dlg = wx.MessageDialog(None, _(u"Il est impossible de saisir le forfait ! \n\nDes consommations existent déjà sur les dates suivantes :\n\n%s") % texteDatesPrises, "Erreur", wx.OK | wx.ICON_ERROR)
                                    dlg.ShowModal()
                                    dlg.Destroy()
                                    return False
                                
                                # Recherche du montant du tarif : MONTANT UNIQUE
                                if methode_calcul == "montant_unique" :
                                    lignes_calcul = dictTarif["lignes_calcul"]
                                    montant_tarif = lignes_calcul[0]["montant_unique"]
                                
                                # Recherche du montant à appliquer : QUOTIENT FAMILIAL
                                if methode_calcul == "qf" :
                                    montant_tarif = 0.0
                                    tarifFound = False
                                    lignes_calcul = dictTarif["lignes_calcul"]
                                    for ligneCalcul in lignes_calcul :
                                        qf_min = ligneCalcul["qf_min"]
                                        qf_max = ligneCalcul["qf_max"]
                                        montant_tarif = ligneCalcul["montant_unique"]
                                        if dictQuotientsFamiliaux.has_key(self.IDfamille) :
                                            listeQuotientsFamiliaux = dictQuotientsFamiliaux[self.IDfamille]
                                        else:
                                            listeQuotientsFamiliaux = []
                                        for date_debut, date_fin, quotient in listeQuotientsFamiliaux :
                                            if date_facturation >= date_debut and date_facturation <= date_fin and quotient >= qf_min and quotient <= qf_max :
                                                tarifFound = True
                                            if tarifFound == True :
                                                break
                                        if tarifFound == True :
                                            break
                                    
                                # ------------ Déduction d'une aide journalière --------------
                                
                                # Recherche si une aide est valable à cette date et pour cet individu et pour cette activité
                                listeAidesRetenues = []
                                for IDaide, dictAide in dictAides.iteritems() :
                                    IDfamilleTemp = dictAide["IDfamille"]
                                    listeBeneficiaires = dictAide["beneficiaires"]
                                    IDactiviteTemp = dictAide["IDactivite"]
                                    dateDebutTemp = dictAide["date_debut"]
                                    dateFinTemp = dictAide["date_fin"]
                                    
                                    for combi in combinaisons :
                                        date = combi[0][0]
                                        
                                        # Regroupement des unités de la date
                                        listeUnitesUtilisees = []
                                        for date, IDunite, IDgroupe in combi :
                                            listeUnitesUtilisees.append(IDunite)
                                        
                                        if self.IDfamille == IDfamilleTemp and date >= dateDebutTemp and date <= dateFinTemp and IDindividu in listeBeneficiaires and IDactiviteTemp == IDactivite :
                                            # Une aide valide a été trouvée...
                                            listeCombiValides = []
                                            
                                            # On recherche si des combinaisons sont présentes sur cette ligne
                                            dictMontants = dictAide["montants"]
                                            for IDaide_montant, dictMontant in dictMontants.iteritems() :
                                                montant = dictMontant["montant"]
                                                for IDaide_combi, combinaison in dictMontant["combinaisons"].iteritems() :
                                                    resultat = self.RechercheCombinaison(listeUnitesUtilisees, combinaison)
                                                    if resultat == True :
                                                        dictTmp = {
                                                            "nbre_max_unites_combi": len(combinaison),
                                                            "combi_retenue" : combinaison,
                                                            "montant" : montant,
                                                            "IDaide" : IDaide,
                                                            "date" : date,
                                                            }
                                                        listeCombiValides.append(dictTmp)
                                                        
                                                # Tri des combinaisons par nombre d'unités max dans les combinaisons
                                                listeCombiValides.sort(cmp=self.TriTarifs)
                                                
                                                # On conserve le combi qui a le plus grand nombre d'unités dedans
                                                if len(listeCombiValides) > 0 :
                                                    listeAidesRetenues.append( listeCombiValides[0] )
                            
                                
                                # Application de la déduction
                                montant_initial = montant_tarif
                                montant_final = montant_initial
                                for aideRetenue in listeAidesRetenues :
                                    montant_final = montant_final - aideRetenue["montant"]
                                
                                # Récupère l'IDcompte_payeur
                                IDcompte_payeur = dictComptesPayeurs[self.IDfamille]
                                                            
                                # Sauvegarde de la prestation
                                DB = GestionDB.DB()
                                listeDonnees = [
                                    ("IDcompte_payeur", IDcompte_payeur), 
                                    ("date", date_facturation),
                                    ("categorie", "consommation"),
                                    ("label", nom_tarif),
                                    ("montant_initial", montant_initial), 
                                    ("montant", montant_final), 
                                    ("IDactivite", IDactivite), 
                                    ("IDtarif", IDtarif), 
                                    ("IDfacture", None), 
                                    ("IDfamille", self.IDfamille),
                                    ("IDindividu", IDindividu),
                                    ("forfait", type_forfait), 
                                    ("IDcategorie_tarif", IDcategorie_tarif), 
                                    ]
                                IDprestation = DB.ReqInsert("prestations", listeDonnees)
                    
                                # Sauvegarde des déductions
                                for deduction in listeAidesRetenues :
                                    listeDonnees = [
                                        ("IDprestation", IDprestation),
                                        ("IDcompte_payeur", IDcompte_payeur), 
                                        ("date", deduction["date"]),
                                        ("montant", deduction["montant"]),
                                        ("label", dictAides[IDaide]["nomAide"]),
                                        ("IDaide", deduction["IDaide"]), 
                                        ]
                                    newIDdeduction = DB.ReqInsert("deductions", listeDonnees)
                                                    
                                # Sauvegarde des consommations
                                for conso in listeConsommations :
                                    date = conso["date"]
                                    IDunite = conso["IDunite"]
                                                                    
                                    # Récupération des données
                                    listeDonnees = [
                                        ("IDindividu", IDindividu), 
                                        ("IDinscription", IDinscription),
                                        ("IDactivite", IDactivite),
                                        ("date", str(date)),
                                        ("IDunite", IDunite), 
                                        ("IDgroupe", IDgroupe), 
                                        ("heure_debut", dictUnites[IDunite]["heure_debut"]), 
                                        ("heure_fin", dictUnites[IDunite]["heure_fin"]), 
                                        ("etat", "reservation"),
                                        ("verrouillage", False), 
                                        ("date_saisie", str(datetime.date.today())), 
                                        ("IDutilisateur", UTILS_Identification.GetIDutilisateur()),
                                        ("IDcategorie_tarif", IDcategorie_tarif),
                                        ("IDcompte_payeur", IDcompte_payeur),
                                        ("IDprestation", IDprestation),
                                        ("forfait", type_forfait), 
                                        ]
                                    IDconso = DB.ReqInsert("consommations", listeDonnees)
                                    
                                # Cloture de la DB
                                DB.Close()
                                
                                nbre_forfaits_saisis += 1
        
        return True


    def RechercheCombinaison(self, listeUnites, combinaison):
        """ Recherche une combinaison donnée dans une ligne de la grille """
        for IDunite_combi in combinaison :
            if IDunite_combi not in listeUnites :
                return False
        return True

    def TriTarifs(self, dictTarif1, dictTarif2, key="nbre_max_unites_combi") :
        """ Effectue un tri DECROISSANT des tarifs en fonction du nbre_max_unites_combi """
        if dictTarif1[key] < dictTarif2[key] :
            return 1
        elif dictTarif1[key] > dictTarif2[key] :
            return -1
        else:
            return 0

    def GetDictUnites(self):
        dictUnites = {}
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        DB = GestionDB.DB()
        # Récupère la liste des unités
        req = """SELECT IDunite, IDactivite, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin, ordre, touche_raccourci
        FROM unites 
        WHERE IDactivite IN %s
        ORDER BY ordre; """ % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDunite, IDactivite, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin, ordre, touche_raccourci in listeDonnees :
            dictTemp = { "unites_incompatibles" : [], "IDunite" : IDunite, "IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "type" : type, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre, "touche_raccourci" : touche_raccourci}
            dictUnites[IDunite] = dictTemp
        # Récupère les incompatibilités entre unités
        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
        FROM unites_incompat;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
            if dictUnites.has_key(IDunite) : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if dictUnites.has_key(IDunite_incompatible) : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)
        return dictUnites
    
    def GetInscriptions(self):
        DB = GestionDB.DB()
        if len(self.listeIndividus) == 0 : conditionIndividus = "()"
        elif len(self.listeIndividus) == 1 : conditionIndividus = "(%d)" % self.listeIndividus[0]
        else : conditionIndividus = str(tuple(self.listeIndividus))
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        req = """SELECT IDinscription, inscriptions.IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, IDcompte_payeur,
        nom, prenom
        FROM inscriptions
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        WHERE inscriptions.IDindividu IN %s AND IDactivite IN %s
        ORDER BY nom, prenom;""" % (conditionIndividus, conditionActivites)
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        DB.Close() 
        
        dictIndividus = {}
        for IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, IDcompte_payeur, nom, prenom in listeInscriptions :
            if dictIndividus.has_key(IDindividu) == False :
                dictIndividus[IDindividu] = {"nom" : nom, "prenom" : prenom, "inscriptions" : []}
            dictTemp = { "IDinscription" : IDinscription, "IDfamille" : IDfamille, "IDactivite" : IDactivite, "IDgroupe" : IDgroupe, "IDcategorie_tarif" : IDcategorie_tarif, "IDcompte_payeur" : IDcompte_payeur}
            dictIndividus[IDindividu]["inscriptions"].append(dictTemp)
        
        return dictIndividus

    def GetComptesPayeurs(self):
        dictComptesPayeurs = {}
        # Récupère le compte_payeur des ou de la famille
        DB = GestionDB.DB()
        req = """SELECT IDfamille, IDcompte_payeur
        FROM comptes_payeurs
        WHERE IDfamille=%d;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq() 
        for IDfamille, IDcompte_payeur in listeDonnees :
            dictComptesPayeurs[IDfamille] = IDcompte_payeur
        DB.Close() 
        return dictComptesPayeurs


    def GetQuotientsFamiliaux(self):
        dictQuotientsFamiliaux = {}
        # Récupère le QF de la famille
        DB = GestionDB.DB()
        req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient
        FROM quotients
        WHERE IDfamille=%d
        ORDER BY date_debut
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDquotient, IDfamille, date_debut, date_fin, quotient in listeDonnees :
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            if dictQuotientsFamiliaux.has_key(IDfamille) == False :
                dictQuotientsFamiliaux[IDfamille] = []
            dictQuotientsFamiliaux[IDfamille].append((date_debut, date_fin, quotient))
        DB.Close() 
        return dictQuotientsFamiliaux

    def GetAides(self):
        """ Récupère les aides journalières de la famille """
        dictAides = {}
        
        # Importation des aides
        DB = GestionDB.DB()
        req = """SELECT IDaide, IDfamille, IDactivite, aides.nom, date_debut, date_fin, caisses.IDcaisse, caisses.nom, montant_max, nbre_dates_max
        FROM aides
        LEFT JOIN caisses ON caisses.IDcaisse = aides.IDcaisse
        WHERE IDfamille=%d
        ORDER BY date_debut;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeAides = DB.ResultatReq()
        if len(listeAides) == 0 : return dictAides
        listeIDaides = []
        for IDaide, IDfamille, IDactivite, nomAide, date_debut, date_fin, IDcaisse, nomCaisse, montant_max, nbre_dates_max in listeAides :
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            dictTemp = {
                "IDaide" : IDaide, "IDfamille" : IDfamille, "IDactivite" : IDactivite, "nomAide" : nomAide, "date_debut" : date_debut, "date_fin" : date_fin, 
                "IDcaisse" : IDcaisse, "nomCaisse" : nomCaisse, "montant_max" : montant_max, "nbre_dates_max" : nbre_dates_max, 
                "beneficiaires" : [], "montants" : {} }
            dictAides[IDaide] = dictTemp
            listeIDaides.append(IDaide)
        
        if len(listeIDaides) == 0 : conditionAides = "()"
        elif len(listeIDaides) == 1 : conditionAides = "(%d)" % listeIDaides[0]
        else : conditionAides = str(tuple(listeIDaides))
        
        # Importation des bénéficiaires
        req = """SELECT IDaide_beneficiaire, IDaide, IDindividu
        FROM aides_beneficiaires
        WHERE IDaide IN %s;""" % conditionAides
        DB.ExecuterReq(req)
        listeBeneficiaires = DB.ResultatReq()
        for IDaide_beneficiaire, IDaide, IDindividu in listeBeneficiaires :
            if dictAides.has_key(IDaide) :
                dictAides[IDaide]["beneficiaires"].append(IDindividu)
        
        # Importation des montants, combinaisons et unités de combi
        req = """SELECT 
        aides_montants.IDaide, aides_combi_unites.IDaide_combi_unite, aides_combi_unites.IDaide_combi, aides_combi_unites.IDunite,
        aides_combinaisons.IDaide_montant, aides_montants.montant
        FROM aides_combi_unites
        LEFT JOIN aides_combinaisons ON aides_combinaisons.IDaide_combi = aides_combi_unites.IDaide_combi
        LEFT JOIN aides_montants ON aides_montants.IDaide_montant = aides_combinaisons.IDaide_montant
        WHERE aides_montants.IDaide IN %s;""" % conditionAides
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        
        for IDaide, IDaide_combi_unite, IDaide_combi, IDunite, IDaide_montant, montant in listeUnites :
            if dictAides.has_key(IDaide) :
                # Mémorisation du montant
                if dictAides[IDaide]["montants"].has_key(IDaide_montant) == False :
                    dictAides[IDaide]["montants"][IDaide_montant] = {"montant":montant, "combinaisons":{}}
                # Mémorisation de la combinaison
                if dictAides[IDaide]["montants"][IDaide_montant]["combinaisons"].has_key(IDaide_combi) == False :
                    dictAides[IDaide]["montants"][IDaide_montant]["combinaisons"][IDaide_combi] = []
                # Mémorisation des unités de combinaison
                dictAides[IDaide]["montants"][IDaide_montant]["combinaisons"][IDaide_combi].append(IDunite)
        
        DB.Close() 
        return dictAides



# ---------------------------------------------------------------------------------------------------------------------------------

class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, IDfamille, listeActivites=[], listeIndividus=[], saisieManuelle=True, saisieAuto=False): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.IDfamille = IDfamille
        self.listeActivites = listeActivites
        self.listeIndividus = listeIndividus
        self.saisieManuelle = saisieManuelle
        self.saisieAuto = saisieAuto
        
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_forfait = il.Add(wx.Bitmap("Images/16x16/Etiquette.png", wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Création des colonnes
        self.AddColumn(_(u"Individu/Activité/Prestation"))
        self.SetColumnWidth(0, 380)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
        
        self.AddColumn(_(u"Période du forfait"))
        self.SetColumnWidth(1, 320)
        self.SetColumnAlignment(1, wx.ALIGN_LEFT)
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT) #  | HTL.TR_NO_HEADER
        
        # Binds
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClick)
        
    def OnDoubleClick(self, event):
        item = event.GetItem()
        donnees = self.GetPyData(item)
        if donnees == None : return
        if donnees["type"] != "tarif" : return
        IDtarif = donnees["ID"]
        self.parent.OnBoutonOk(None)
        
        
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.Remplissage()
    
    def GetIDtarif(self):
        donnees = self.GetPyData(self.GetSelection())
        if donnees == None : return None
        if donnees["type"] != "tarif" : return None
        IDtarif = donnees["ID"]
        return IDtarif
    
    def Remplissage(self):        
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        # Récupération des forfaits
        f = Forfaits(self.IDfamille, self.listeActivites, self.listeIndividus, self.saisieManuelle, self.saisieAuto)
        dictForfaits = f.GetForfaits()
            
        # Récupération des données
        dictIndividus = f.GetInscriptions()
        
        # Création des branches
        for IDindividu, dictIndividu in dictIndividus.iteritems() :
            
            nom = dictIndividu["nom"]
            prenom = dictIndividu["prenom"]
            
            # Niveau 1 : noms Individus
            label = u"%s %s" % (nom, prenom)
            niveau1 = self.AppendItem(self.root, label)
            self.SetPyData(niveau1, {"type":"individu", "ID":IDindividu} )
            self.SetItemBold(niveau1, True)
            
            listeInscriptions = dictIndividu["inscriptions"]
            for dictInscription in listeInscriptions :
                
                # Niveau 2 : Activités
                IDactivite = dictInscription["IDactivite"]
                IDgroupe = dictInscription["IDgroupe"]
                IDcategorie_tarif = dictInscription["IDcategorie_tarif"]
                
                # Recherche s'il y a un forfait disponible dans l'activité correspondant à cette inscription
                if dictForfaits.has_key(IDactivite) and len(dictForfaits[IDactivite]["tarifs"])> 0 :
                    
                    dictActivite = dictForfaits[IDactivite]
                    nomActivite = dictActivite["nom"]
                    niveau2 = self.AppendItem(niveau1, nomActivite)
                    self.SetPyData(niveau2, {"type":"activite", "ID":IDactivite} )
                    
                    # Niveau 3 : Tarifs
                    for dictTarif in dictActivite["tarifs"] :
                        
                        # Ne sélectionne que ceux qui peuvent être saisis manuellement
                        if IDcategorie_tarif in dictTarif["categories_tarifs"] and dictTarif["forfait_saisie_manuelle"] == 1 :
                            
                            nomTarif = dictTarif["nom_tarif"]
                            methode = dictTarif["methode"]
                            combinaisons = dictTarif["combinaisons"]
                            IDtarif = dictTarif["IDtarif"]
                            lignes_calcul = dictTarif["lignes_calcul"]
                            options = dictTarif["options"]
                            
                            niveau3 = self.AppendItem(niveau2, nomTarif)
                            self.SetPyData(niveau3, {"type":"tarif", "ID":IDtarif} )
                            self.SetItemImage(niveau3, self.img_forfait, which=wx.TreeItemIcon_Normal)
                            
                            # Affiche les dates extrêmes du forfait
                            if len(combinaisons) > 0 :
                                # Combinaisons perso
                                date_debut_forfait, date_fin_forfait = DateComplete(combinaisons[0][0][0]), DateComplete(combinaisons[-1][0][0])
                            elif options != None and "calendrier" in options :
                                # Selon le calendrier des ouvertures
                                date_debut_forfait, date_fin_forfait = "?", "?"
                                if dictActivite["ouvertures"].has_key(IDgroupe) :
                                    dates = dictActivite["ouvertures"][IDgroupe].keys()
                                    dates.sort()
                                    if len(dates) > 0 :
                                        date_debut_forfait, date_fin_forfait = DateComplete(dates[0]), DateComplete(dates[-1])
                            else :
                                date_debut_forfait, date_fin_forfait = "?", "?"
                                
                            label = _(u"Du %s au %s") % (date_debut_forfait, date_fin_forfait)
                            self.SetItemText(niveau3, label, 1)

        
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT ) # | HTL.TR_NO_HEADER
            
        self.ExpandAllChildren(self.root)
        

# -----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, listeActivites=[], listeIndividus=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Appliquer_forfait", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDfamille = IDfamille
        self.listeActivites = listeActivites
        self.listeIndividus = listeIndividus
        
        intro = _(u"Vous pouvez ici appliquer un forfait daté. Ceux-ci peuvent être paramétrés dans la tarification. Sélectionnez un forfait pour l'individu et l'activité de votre choix puis cliquez sur Ok ou double-cliquez sur la ligne souhaitée.")
        titre = _(u"Appliquer un forfait daté")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Forfait.png")
        self.SetTitle(titre)

        self.staticbox_forfaits = wx.StaticBox(self, -1, _(u"Sélection d'un forfait"))
        self.ctrl_forfaits = CTRL(self, IDfamille, listeActivites, listeIndividus, saisieManuelle=True, saisieAuto=False)
        self.ctrl_forfaits.MAJ()
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.ctrl_forfaits.SetToolTipString(_(u"Double-cliquez sur un forfait pour l'appliquer"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((800, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        staticbox_forfaits = wx.StaticBoxSizer(self.staticbox_forfaits, wx.VERTICAL)
        staticbox_forfaits.Add(self.ctrl_forfaits, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_forfaits, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Activits1")

    def OnBoutonOk(self, event): 
        IDtarif = self.ctrl_forfaits.GetIDtarif() 
        if IDtarif == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun forfait à appliquer !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Application du forfait sélectionné
        f = Forfaits(IDfamille=self.IDfamille, listeActivites=self.listeActivites, listeIndividus=self.listeIndividus, saisieManuelle=True, saisieAuto=False)
        resultat = f.Applique_forfait(selectionIDtarif=IDtarif) 
        if resultat == False :
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=3, listeActivites=[2, 3], listeIndividus=[5,])
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
    
    
    
    
    
    