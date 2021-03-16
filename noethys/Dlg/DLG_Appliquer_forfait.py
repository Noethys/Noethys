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
from Ctrl import CTRL_Bouton_image
import datetime
import wx.lib.agw.hypertreelist as HTL
import six
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Identification
from Utils import UTILS_Gestion
from Utils import UTILS_Dates
from Utils import UTILS_Texte
from Ctrl import CTRL_Saisie_date
import GestionDB
from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES

if six.PY3:
    import functools




class Forfaits():
    def __init__(self, IDfamille=None, listeActivites=[], listeIndividus=[], saisieManuelle=True, saisieAuto=True):
        self.IDfamille = IDfamille
        self.listeActivites = listeActivites
        self.listeIndividus = listeIndividus
        self.saisieManuelle = saisieManuelle
        self.saisieAuto = saisieAuto
        self.listeVacances = self.GetListeVacances()

        # Périodes de gestion
        self.gestion = UTILS_Gestion.Gestion(None)

    def GetListeVacances(self):
        DB = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        return listeDonnees

    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def VerificationPeriodes(self, jours_scolaires, jours_vacances, date):
        """ Vérifier si jour scolaire ou vacances """
        valide = False
        # Jours scolaires
        if jours_scolaires != None :
            if self.EstEnVacances(date) == False :
                if date.weekday() in jours_scolaires :
                    valide = True
        # Jours vacances
        if jours_vacances != None :
            if self.EstEnVacances(date) == True :
                if date.weekday() in jours_vacances :
                    valide = True
        return valide

    def GetForfaits(self, masquer_forfaits_obsoletes=False):
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
            if date_debut != None : date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
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
            date = UTILS_Dates.DateEngEnDateDD(date)
            if IDactivite in dictActivites :
                if (IDgroupe in dictActivites[IDactivite]["ouvertures"]) == False :
                    dictActivites[IDactivite]["ouvertures"][IDgroupe] = {}
                if (date in dictActivites[IDactivite]["ouvertures"][IDgroupe]) == False :
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
            date = UTILS_Dates.DateEngEnDateDD(date)
            if (IDtarif in dictCombiUnites) == False :
                dictCombiUnites[IDtarif] = {}
            if (IDcombi_tarif in dictCombiUnites[IDtarif]) == False :
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
            if (dictTemp["IDtarif"] in dictLignesCalcul) == False :
                dictLignesCalcul[dictTemp["IDtarif"]] = [dictTemp,]
            else:
                dictLignesCalcul[dictTemp["IDtarif"]].append(dictTemp)
        
        # Recherche des tarifs pour chaque activité
        condition = "WHERE type='FORFAIT' AND forfait_saisie_manuelle=%s AND forfait_saisie_auto=%d" % (int(self.saisieManuelle), int(self.saisieAuto))
        if masquer_forfaits_obsoletes == True :
            condition += " AND (date_fin>='%s' OR date_fin IS NULL)" % datetime.date.today()

        req = """SELECT 
        IDtarif, tarifs.IDactivite, tarifs.IDnom_tarif, nom, date_debut, date_fin, 
        forfait_saisie_manuelle, forfait_saisie_auto, forfait_suppression_auto,
        methode, categories_tarifs, groupes, options, date_facturation, IDtype_quotient
        FROM tarifs
        LEFT JOIN noms_tarifs ON noms_tarifs.IDnom_tarif = tarifs.IDnom_tarif
        %s
        ORDER BY date_debut;""" % condition
        DB.ExecuterReq(req)
        listeTarifs = DB.ResultatReq()      
        for IDtarif, IDactivite, IDnom_tarif, nom, date_debut, date_fin, forfait_saisie_manuelle, forfait_saisie_auto, forfait_suppression_auto, methode, categories_tarifs, groupes, options, date_facturation, IDtype_quotient in listeTarifs :
            if date_debut != None : date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            listeCategoriesTarifs = UTILS_Texte.ConvertStrToListe(categories_tarifs, siVide=None)
            listeGroupes = UTILS_Texte.ConvertStrToListe(groupes, siVide=None)
            inclure = True

            dictTemp = {
                "IDtarif" : IDtarif, "IDactivite" : IDactivite, 
                "IDnom_tarif" : IDnom_tarif, "nom_tarif" : nom, "date_debut" : date_debut, "date_fin" : date_fin, 
                "forfait_saisie_manuelle" : forfait_saisie_manuelle, "forfait_saisie_auto" : forfait_saisie_auto, 
                "forfait_suppression_auto" : forfait_suppression_auto, "methode" : methode,
                "categories_tarifs" : listeCategoriesTarifs, "groupes" : listeGroupes, "options" : options, "date_facturation" : date_facturation,
                "combinaisons" : [], "lignes_calcul" : [], "IDtype_quotient" : IDtype_quotient,
                "date_debut_forfait" : None, "date_fin_forfait" : None,
                }
                
            # Recherche si ce tarif a des combinaisons d'unités
            if IDtarif in dictCombiUnites :
                listeCombinaisons = []
                for IDcombi, listeCombis in dictCombiUnites[IDtarif].items() :
                    listeCombinaisons.append(tuple(listeCombis))
                listeCombinaisons.sort() 
                dictTemp["combinaisons"] = listeCombinaisons
                dictTemp["forfait_saisie_manuelle"] = forfait_saisie_manuelle
                dictTemp["forfait_saisie_auto"] = forfait_saisie_auto
                dictTemp["forfait_suppression_auto"] = forfait_suppression_auto

                # Recherche les dates extrêmes du forfait (si unités de conso associées)
                if len(listeCombinaisons) > 0:
                    # Combinaisons perso
                    date_debut_forfait, date_fin_forfait = listeCombinaisons[0][0][0], listeCombinaisons[-1][0][0]
                elif options != None and "calendrier" in options:
                    # Selon le calendrier des ouvertures
                    date_debut_forfait, date_fin_forfait = None, None
                    if IDgroupe in dictActivites[IDactivite]["ouvertures"]:
                        dates = list(dictActivites[IDactivite]["ouvertures"][IDgroupe].keys())
                        dates.sort()
                        if len(dates) > 0:
                            date_debut_forfait, date_fin_forfait = dates[0], dates[-1]
                else:
                    date_debut_forfait, date_fin_forfait = None, None

                dictTemp["date_debut_forfait"] = date_debut_forfait
                dictTemp["date_fin_forfait"] = date_fin_forfait

                if masquer_forfaits_obsoletes == True and date_fin_forfait != None and date_fin_forfait < datetime.date.today() :
                    inclure = False

            # Recherche si ce tarif a des lignes de calcul
            if IDtarif in dictLignesCalcul:
                dictTemp["lignes_calcul"] = dictLignesCalcul[IDtarif]
            
            # Mémorisation de ce tarif
            if (IDactivite in dictActivites) == True and inclure == True :
                dictActivites[IDactivite]["tarifs"].append(dictTemp)

        # Cloture de la base de données
        DB.Close()
        
        return dictActivites

    def RechercheQF(self, dictQuotientsFamiliaux=None, dictTarif=None, IDfamille=None, date=None):
        """ Pour Facturation Recherche du QF de la famille """
        # Si la famille a un QF :
        if IDfamille in dictQuotientsFamiliaux :
            listeQuotientsFamiliaux = dictQuotientsFamiliaux[IDfamille]
            for date_debut, date_fin, quotient, IDtype_quotient in listeQuotientsFamiliaux :
                if date >= date_debut and date <= date_fin and (dictTarif["IDtype_quotient"] == None or dictTarif["IDtype_quotient"] == IDtype_quotient) :
                    return quotient

        # Si la famille n'a pas de QF, on attribue le QF le plus élevé :
        listeQF = []
        for ligneCalcul in dictTarif["lignes_calcul"] :
            listeQF.append(ligneCalcul["qf_max"])
        listeQF.sort()
        if len(listeQF) > 0 :
            if listeQF[-1] != None :
                return listeQF[-1]

        return None

    def Applique_forfait(self, selectionIDcategorie_tarif=None, selectionIDtarif=None, inscription=False, selectionIDactivite=None, labelTarif=None, IDinscription=None):
        """ Recherche et applique les forfaits auto à l'inscription """
        dictUnites = self.GetDictUnites() 
        dictInscriptions = self.GetInscriptions() 
        dictComptesPayeurs = self.GetComptesPayeurs() 
        dictQuotientsFamiliaux = self.GetQuotientsFamiliaux() 
        dictAides = self.GetAides() 
        dictActivites = self.GetForfaits()
        nbre_forfaits_saisis = 0

        for IDindividu in self.listeIndividus :
            for IDactivite, dictActivite in dictActivites.items() :
                nomActivite = dictActivite["nom"]
                date_debut_activite = dictActivite["date_debut"]
                date_fin_activite = dictActivite["date_fin"]
                dictTarifs = dictActivite["tarifs"]
                
                # Récupération des informations sur l'inscription
                IDcategorie_tarif_temp = None
                if IDindividu in dictInscriptions:
                    for dictInscription in dictInscriptions[IDindividu]["inscriptions"] :
                        if dictInscription["IDactivite"] == IDactivite and (not IDinscription or dictInscription["IDinscription"] == IDinscription):
                            IDinscription = dictInscription["IDinscription"]
                            IDgroupe = dictInscription["IDgroupe"]
                            IDcategorie_tarif_temp = dictInscription["IDcategorie_tarif"]
                            break

                if IDcategorie_tarif_temp != None :

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
                                if IDgroupe in dictActivites[IDactivite]["ouvertures"] :
                                    for dateTemp, listeCombis in dictActivites[IDactivite]["ouvertures"][IDgroupe].items() :
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
                                        date_facturation = UTILS_Dates.DateEngEnDateDD(date_facturation_tarif[5:])
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

                                    # Périodes de gestion
                                    if self.gestion.Verification("consommations", listeConsommations) == False: return False

                                    if self.gestion.Verification("prestations", date_facturation, silencieux=True) == False:
                                        # Demande une nouvelle date de facturation
                                        dlg = DLG_Verrouillage(None)
                                        if dlg.ShowModal() == wx.ID_OK:
                                            date_facturation = dlg.GetDateFacturation()
                                            dlg.Destroy()
                                        else :
                                            dlg.Destroy()
                                            return False
                                    else :
                                        # Vérifie que la date de facturation n'est pas trop ancienne
                                        nbreJours = (datetime.date.today() - date_facturation).days
                                        if nbreJours > 28 :
                                            dlg = DLG_Date_facturation(None, date_facturation=date_facturation)
                                            if dlg.ShowModal() == wx.ID_OK:
                                                date_facturation = dlg.GetDateFacturation()
                                            dlg.Destroy()

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
                                        dateConso = UTILS_Dates.DateEngEnDateDD(dateConso)
                                        if {"date" : dateConso, "IDunite" : IDuniteConso} in listeConsommations :
                                            if dateConso not in listeDatesPrises :
                                                listeDatesPrises.append(dateConso)

                                    if len(listeDatesPrises) > 0 :
                                        texteDatesPrises = u""
                                        for datePrise in listeDatesPrises :
                                            texteDatesPrises += u"   > %s\n" % UTILS_Dates.DateComplete(datePrise)
                                        if labelTarif == None :
                                            label = ""
                                        else :
                                            label = labelTarif + " "
                                        dlg = wx.MessageDialog(None, _(u"Il est impossible de saisir le forfait %s! \n\nDes consommations existent déjà sur les dates suivantes :\n\n%s") % (label, texteDatesPrises), "Erreur", wx.OK | wx.ICON_ERROR)
                                        dlg.ShowModal()
                                        dlg.Destroy()
                                        return False

                                    # ------------ Recherche du montant du tarif : MONTANT UNIQUE
                                    if methode_calcul == "montant_unique" :
                                        lignes_calcul = dictTarif["lignes_calcul"]
                                        montant_tarif = lignes_calcul[0]["montant_unique"]

                                    # ------------ Recherche du montant à appliquer : QUOTIENT FAMILIAL
                                    if methode_calcul == "qf" :
                                        montant_tarif = 0.0
                                        tarifFound = False
                                        lignes_calcul = dictTarif["lignes_calcul"]
                                        for ligneCalcul in lignes_calcul :
                                            qf_min = ligneCalcul["qf_min"]
                                            qf_max = ligneCalcul["qf_max"]
                                            montant_tarif = ligneCalcul["montant_unique"]

                                            QFfamille = self.RechercheQF(dictQuotientsFamiliaux, dictTarif, self.IDfamille, date_facturation)
                                            if QFfamille != None :
                                                if QFfamille >= qf_min and QFfamille <= qf_max :
                                                    break

                                            # if dictQuotientsFamiliaux.has_key(self.IDfamille) :
                                            #     listeQuotientsFamiliaux = dictQuotientsFamiliaux[self.IDfamille]
                                            # else:
                                            #     listeQuotientsFamiliaux = []
                                            # for date_debut, date_fin, quotient in listeQuotientsFamiliaux :
                                            #     if date_facturation >= date_debut and date_facturation <= date_fin and quotient >= qf_min and quotient <= qf_max :
                                            #         tarifFound = True
                                            #     if tarifFound == True :
                                            #         break
                                            # if tarifFound == True :
                                            #     break

                                    # -------------- Recherche du montant du tarif : CHOIX (MONTANT ET LABEL SELECTIONNES PAR L'UTILISATEUR)
                                    if methode_calcul == "choix" :
                                        # Nouvelle saisie si clic sur la case
                                        lignes_calcul = dictTarif["lignes_calcul"]
                                        from Dlg import DLG_Selection_montant_prestation
                                        dlg = DLG_Selection_montant_prestation.Dialog(None, lignes_calcul=lignes_calcul, label=nom_tarif, montant=0.0, titre=labelTarif)
                                        if dlg.ShowModal() == wx.ID_OK:
                                            nom_tarif = dlg.GetLabel()
                                            montant_tarif = dlg.GetMontant()
                                            dlg.Destroy()
                                        else:
                                            dlg.Destroy()
                                            return False





                                    # ------------ Déduction d'une aide journalière --------------

                                    # Recherche si une aide est valable à cette date et pour cet individu et pour cette activité
                                    listeAidesRetenues = []
                                    for IDaide, dictAide in dictAides.items() :
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

                                            # Vérifie si date est dans jours scolaires ou de vacances
                                            date_ok = True
                                            if dictAide["jours_scolaires"] != None and dictAide["jours_scolaires"] != None:
                                                date_ok = self.VerificationPeriodes(dictAide["jours_scolaires"], dictAide["jours_vacances"], date)

                                            if date_ok == True and self.IDfamille == IDfamilleTemp and date >= dateDebutTemp and date <= dateFinTemp and IDindividu in listeBeneficiaires and IDactiviteTemp == IDactivite :
                                                # Une aide valide a été trouvée...
                                                listeCombiValides = []

                                                # On recherche si des combinaisons sont présentes sur cette ligne
                                                dictMontants = dictAide["montants"]
                                                for IDaide_montant, dictMontant in dictMontants.items() :
                                                    montant = dictMontant["montant"]
                                                    for IDaide_combi, combinaison in dictMontant["combinaisons"].items() :
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
                                                    if six.PY2:
                                                        listeCombiValides.sort(cmp=self.TriTarifs)
                                                    else:
                                                        listeCombiValides.sort(key=functools.cmp_to_key(self.TriTarifs))

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
                                        ("date_valeur", str(datetime.date.today())),
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
            if IDunite in dictUnites : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if IDunite_incompatible in dictUnites : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)
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
            if (IDindividu in dictIndividus) == False :
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
        req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient, IDtype_quotient
        FROM quotients
        WHERE IDfamille=%d
        ORDER BY date_debut
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDquotient, IDfamille, date_debut, date_fin, quotient, IDtype_quotient in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            if (IDfamille in dictQuotientsFamiliaux) == False :
                dictQuotientsFamiliaux[IDfamille] = []
            dictQuotientsFamiliaux[IDfamille].append((date_debut, date_fin, quotient, IDtype_quotient))
        DB.Close() 
        return dictQuotientsFamiliaux

    def GetAides(self):
        """ Récupère les aides journalières de la famille """
        dictAides = {}
        
        # Importation des aides
        DB = GestionDB.DB()
        req = """SELECT IDaide, IDfamille, IDactivite, aides.nom, date_debut, date_fin, caisses.IDcaisse, caisses.nom, montant_max, nbre_dates_max, jours_scolaires, jours_vacances
        FROM aides
        LEFT JOIN caisses ON caisses.IDcaisse = aides.IDcaisse
        WHERE IDfamille=%d
        ORDER BY date_debut;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeAides = DB.ResultatReq()
        if len(listeAides) == 0 : 
            DB.Close() 
            return dictAides
        listeIDaides = []
        for IDaide, IDfamille, IDactivite, nomAide, date_debut, date_fin, IDcaisse, nomCaisse, montant_max, nbre_dates_max, jours_scolaires, jours_vacances in listeAides :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            jours_scolaires = UTILS_Texte.ConvertStrToListe(jours_scolaires, siVide=None)
            jours_vacances = UTILS_Texte.ConvertStrToListe(jours_vacances, siVide=None)
            dictTemp = {
                "IDaide" : IDaide, "IDfamille" : IDfamille, "IDactivite" : IDactivite, "nomAide" : nomAide, "date_debut" : date_debut, "date_fin" : date_fin, 
                "IDcaisse" : IDcaisse, "nomCaisse" : nomCaisse, "montant_max" : montant_max, "nbre_dates_max" : nbre_dates_max, "jours_scolaires" : jours_scolaires,
                "jours_vacances" : jours_vacances, "beneficiaires" : [], "montants" : {} }
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
            if IDaide in dictAides :
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
            if IDaide in dictAides :
                # Mémorisation du montant
                if (IDaide_montant in dictAides[IDaide]["montants"]) == False :
                    dictAides[IDaide]["montants"][IDaide_montant] = {"montant":montant, "combinaisons":{}}
                # Mémorisation de la combinaison
                if (IDaide_combi in dictAides[IDaide]["montants"][IDaide_montant]["combinaisons"]) == False :
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
        self.masquerForfaitsObsoletes = True
        
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_forfait = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etiquette.png"), wx.BITMAP_TYPE_PNG))
        self.img_ok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Ok4.png'), wx.BITMAP_TYPE_PNG))
        self.img_pasok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Interdit2.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Création des colonnes
        self.AddColumn(_(u"Individu/Activité/Prestation"))
        self.SetColumnWidth(0, 330)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
        
        self.AddColumn(_(u"Période du forfait"))
        self.SetColumnWidth(1, 370)
        self.SetColumnAlignment(1, wx.ALIGN_LEFT)
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT) #  | HTL.TR_NO_HEADER

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClick)
        self.Bind(HTL.EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
        
    def OnDoubleClick(self, event):
        item = event.GetItem()
        self.CheckItem(item, not self.IsItemChecked(item))
        event.Skip() 
##        donnees = self.GetPyData(item)
##        if donnees == None : return
##        if donnees["type"] != "tarif" : return
##        IDtarif = donnees["ID"]
##        self.parent.OnBoutonOk(None)
    
    def OnCheckItem(self, event):
        item = event.GetItem()
        etat = self.IsItemChecked(item)
        if self.GetPyData(item)["type"] == "activite" :
            for index in range(0, self.GetChildrenCount(item)):
                item = self.GetNext(item) 
                self.CheckItem(item, etat)
        
    def GetCoches(self):
        """ Obtient la liste des IDtarif cochés """
        listeTarifs = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            if self.IsItemChecked(item) and self.GetPyData(item)["type"] == "tarif" :
                data = self.GetPyData(item)
                listeTarifs.append(data)
        return listeTarifs

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.Remplissage()

    def Remplissage(self):        
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        # Récupération des forfaits
        f = Forfaits(self.IDfamille, self.listeActivites, self.listeIndividus, self.saisieManuelle, self.saisieAuto)
        dictForfaits = f.GetForfaits(masquer_forfaits_obsoletes=self.masquerForfaitsObsoletes)
            
        # Récupération des données
        dictIndividus = f.GetInscriptions()
        
        # Création des branches
        for IDindividu, dictIndividu in dictIndividus.items() :
            
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
                if IDactivite in dictForfaits and len(dictForfaits[IDactivite]["tarifs"])> 0 :
                    
                    dictActivite = dictForfaits[IDactivite]
                    niveau2 = self.AppendItem(niveau1, dictActivite["nom"], ct_type=1)
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

                            # Affiche les dates extrêmes du forfait
                            if len(combinaisons) > 0 :
                                # Combinaisons perso
                                date_debut_forfait, date_fin_forfait = UTILS_Dates.DateComplete(combinaisons[0][0][0]), UTILS_Dates.DateComplete(combinaisons[-1][0][0])
                            elif options != None and "calendrier" in options :
                                # Selon le calendrier des ouvertures
                                date_debut_forfait, date_fin_forfait = "?", "?"
                                if IDgroupe in dictActivite["ouvertures"] :
                                    dates = list(dictActivite["ouvertures"][IDgroupe].keys())
                                    dates.sort()
                                    if len(dates) > 0 :
                                        date_debut_forfait, date_fin_forfait = UTILS_Dates.DateComplete(dates[0]), UTILS_Dates.DateComplete(dates[-1])
                            else :
                                date_debut_forfait, date_fin_forfait = "?", "?"
                                
                            labelDates = _(u"Du %s au %s") % (date_debut_forfait, date_fin_forfait)

                            niveau3 = self.AppendItem(niveau2, nomTarif, ct_type=1)
                            self.SetItemText(niveau3, labelDates, 1)
                            self.SetPyData(niveau3, {"type":"tarif", "ID":IDtarif, "nom":nomTarif, "dates":labelDates, "item":niveau3} )
                            
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(TR_COLUMN_LINES|wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT) # | HTL.TR_NO_HEADER
        self.ExpandAllChildren(self.root)
    
    def SetEtat(self, item=None, etat=True):
        if etat == True :
            self.SetItemImage(item, self.img_ok, which=wx.TreeItemIcon_Normal)
            self.CheckItem(item, False)
        else :
            self.SetItemImage(item, self.img_pasok, which=wx.TreeItemIcon_Normal)
            
# -----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, listeActivites=[], listeIndividus=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Appliquer_forfait", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille
        self.listeActivites = listeActivites
        self.listeIndividus = listeIndividus
        
        intro = _(u"Vous pouvez ici appliquer un ou plusieurs forfaits datés. Ceux-ci peuvent être paramétrés dans la tarification. Cochez un ou plusieurs forfaits pour l'individu et l'activité de votre choix puis cliquez sur Ok.")
        titre = _(u"Appliquer des forfaits datés")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Forfait.png")
        self.SetTitle(titre)

        self.staticbox_forfaits = wx.StaticBox(self, -1, _(u"Cochez un ou plusieurs forfaits"))
        self.ctrl_forfaits = CTRL(self, IDfamille, listeActivites, listeIndividus, saisieManuelle=True, saisieAuto=False)
        self.ctrl_forfaits.MAJ()

        self.check_masquer_obsoletes = wx.CheckBox(self, -1, _(u"Masquer les forfaits obsolètes"))
        self.check_masquer_obsoletes.SetValue(True)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Appliquer"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckObsoletes, self.check_masquer_obsoletes)

    def __set_properties(self):
        self.ctrl_forfaits.SetToolTip(wx.ToolTip(_(u"Double-cliquez sur un forfait pour l'appliquer")))
        self.check_masquer_obsoletes.SetToolTip(wx.ToolTip(_(u"Masquer les forfaits dont la date de fin de validité est inférieure à la date du jour")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((800, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        staticbox_forfaits = wx.StaticBoxSizer(self.staticbox_forfaits, wx.VERTICAL)
        staticbox_forfaits.Add(self.ctrl_forfaits, 1, wx.ALL|wx.EXPAND, 5)
        staticbox_forfaits.Add(self.check_masquer_obsoletes, 0, wx.BOTTOM|wx.ALIGN_RIGHT, 5)
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

    def OnCheckObsoletes(self, event=None):
        self.ctrl_forfaits.masquerForfaitsObsoletes = self.check_masquer_obsoletes.GetValue()
        self.ctrl_forfaits.MAJ()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Activits1")

    def OnBoutonOk(self, event): 
        listeTarifs = self.ctrl_forfaits.GetCoches() 
        if len(listeTarifs) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucun forfait à appliquer !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Application du forfait sélectionné
        f = Forfaits(IDfamille=self.IDfamille, listeActivites=self.listeActivites, listeIndividus=self.listeIndividus, saisieManuelle=True, saisieAuto=False)
        for dataItem in listeTarifs :
            IDtarif = dataItem["ID"]
            nomTarif = dataItem["nom"]
            labelDates = dataItem["dates"]
            item = dataItem["item"]
            label = u"%s (%s)" % (nomTarif, labelDates)
            resultat = f.Applique_forfait(selectionIDtarif=IDtarif, labelTarif=label) 
            
            # Affichage de la validation
            self.ctrl_forfaits.SetEtat(item=item, etat=resultat)
    
        # Fermeture de la fenêtre
##        self.EndModal(wx.ID_OK)
        


class DLG_Verrouillage(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        titre = _(u"Période verrouillée")
        self.SetTitle(titre)
        self.ctrl_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(Chemins.GetStaticPath(u"Images/48x48/Cadenas_ferme.png"), wx.BITMAP_TYPE_ANY))
        self.label_ligne_1 = wx.StaticText(self, wx.ID_ANY, titre)
        intro = _(u"La date de facturation du forfait que vous souhaitez créer se trouve dans une période de gestion verrouillée.\n\nSouhaitez-vous appliquer une autre date de facturation ?")
        self.label_ligne_2 = wx.StaticText(self, wx.ID_ANY, intro)
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())

        self.bouton_oui = CTRL_Bouton_image.CTRL(self, texte=_(u"Créer le forfait avec la date sélectionnée"), cheminImage="Images/32x32/Valider.png")
        self.bouton_non = CTRL_Bouton_image.CTRL(self, texte=_(u"Ne pas créer le forfait"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOui, self.bouton_oui)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonNon, self.bouton_non)


    def __set_properties(self):
        self.label_ligne_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_oui.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer la date de facturation sélectionnée")))
        self.bouton_non.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer et ne pas créer de forfait")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        grid_sizer_bas = wx.FlexGridSizer(1, 5, 10, 10)
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_droit = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_haut.Add(self.ctrl_image, 0, wx.ALL, 10)
        grid_sizer_droit.Add(self.label_ligne_1, 0, 0, 0)
        grid_sizer_droit.Add(self.label_ligne_2, 0, 0, 0)
        grid_sizer_droit.Add(self.ctrl_date, 0, wx.EXPAND | wx.BOTTOM, 10)
        grid_sizer_droit.AddGrowableRow(2)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_droit, 1, wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        grid_sizer_bas.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.bouton_oui, 0, 0, 0)
        grid_sizer_bas.Add(self.bouton_non, 0, 0, 0)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonNon(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOui(self, event):
        date_facturation = self.ctrl_date.GetDate()
        if self.ctrl_date.FonctionValiderDate() == False or date_facturation == None:
            dlg = wx.MessageDialog(self, _(u"La date de facturation ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False

        # Périodes de gestion
        self.gestion = UTILS_Gestion.Gestion(self)
        if self.gestion.Verification("prestations", date_facturation, silencieux=True) == False:
            dlg = wx.MessageDialog(self, _(u"La date de facturation qaue vous avez sélectionné se trouve dans une période de gestion verrouillée !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        self.EndModal(wx.ID_OK)

    def GetDateFacturation(self):
        return self.ctrl_date.GetDate()


# -----------------------------------------------------------------------------------------------------------------------------------

class DLG_Date_facturation(wx.Dialog):
    def __init__(self, parent, date_facturation=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.date_facturation = date_facturation

        self.SetTitle(_(u"Avertissement"))
        self.label_intro = wx.StaticText(self, wx.ID_ANY, _(u"La date de facturation du forfait à appliquer est ancienne. \n\nQue souhaitez-vous faire ?"))

        self.radio_conserver = wx.RadioButton(self, -1, _(u"Conserver la date (%s)") % UTILS_Dates.DateDDEnFr(self.date_facturation), style=wx.RB_GROUP)
        self.radio_modifier = wx.RadioButton(self, -1, _(u"Modifier la date :"))

        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())

        self.label_conclusion = wx.StaticText(self, wx.ID_ANY, _(u"Notez que vous pouvez modifier la date de facturation par défaut depuis le paramétrage\ndu tarif du forfait, onglet type de tarif."))
        self.label_conclusion.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDate, self.radio_conserver)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDate, self.radio_modifier)

        # Init
        self.OnRadioDate()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        grid_sizer_radio = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_radio.Add(self.radio_conserver, 1, wx.EXPAND | wx.LEFT, 10)

        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_date.Add(self.radio_modifier, 1, wx.EXPAND, 0)
        grid_sizer_date.Add(self.ctrl_date, 1, wx.EXPAND, 0)
        grid_sizer_radio.Add(grid_sizer_date, 1, wx.EXPAND | wx.LEFT, 10)

        grid_sizer_base.Add(grid_sizer_radio, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        grid_sizer_base.Add(self.label_conclusion, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnRadioDate(self, event=None):
        self.ctrl_date.Enable(self.radio_modifier.GetValue())
        if self.radio_modifier.GetValue() :
            self.ctrl_date.SetFocus()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Activits1")

    def OnBoutonOk(self, event):
        date_facturation = self.ctrl_date.GetDate()
        if self.ctrl_date.FonctionValiderDate() == False or date_facturation == None:
            dlg = wx.MessageDialog(self, _(u"La date de facturation saisie ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetDateFacturation(self):
        if self.radio_modifier.GetValue() == True :
            return self.ctrl_date.GetDate()
        else :
            return self.date_facturation





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    #dlg = Dialog(None, IDfamille=14, listeActivites=[1,], listeIndividus=[46,])
    dlg = DLG_Date_facturation(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
    
    
    
    
    
    