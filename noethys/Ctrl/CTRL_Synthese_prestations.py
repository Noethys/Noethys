#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import os
import wx.lib.agw.hypertreelist as HTL
import datetime
import sys
import FonctionsPerso
import GestionDB
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils import UTILS_Organisateur
from Utils import UTILS_Dates
from Utils import UTILS_Infos_individus
from Utils import UTILS_Texte
from Utils import UTILS_Titulaires
import six


def PeriodeComplete(mois, annee):
    listeMois = (_(u"Jan"), _(u"Fév"), _(u"Mars"), _(u"Avr"), _(u"Mai"), _(u"Juin"), _(u"Juil"), _(u"Août"), _(u"Sept"), _(u"Oct"), _(u"Nov"), _(u"Déc"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete


class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.dictImpression = {}
        
        # Paramètres
        self.mode_affichage = "facture" # "facture", "regle", "nbre", "impaye"
        self.key_colonne = "mois" # "mois", "annee"
        self.key_ligne1 = "activite"
        self.key_ligne2 = "label"
        self.date_debut = None
        self.date_fin = None
        self.afficher_consommations = True
        self.afficher_cotisations = True
        self.afficher_locations = True
        self.afficher_autres = True
        self.listeActivites = []
        self.affichage_details_total = True

        self.filtreCotisations = False
        self.filtreCotisations_dateDebut = None
        self.filtreCotisations_dateFin = None
        self.filtreReglements = False
        self.filtreReglements_dateDebut = None
        self.filtreReglements_dateFin = None
        self.filtreDepots = False
        self.filtreDepots_dateDebut = None
        self.filtreDepots_dateFin = None
        
        self.labelParametres = ""

        # Importation de données
        DB = GestionDB.DB()

        req = """SELECT IDcategorie_tarif, categories_tarifs.nom, activites.nom, activites.abrege
        FROM categories_tarifs
        LEFT JOIN activites ON activites.IDactivite = categories_tarifs.IDactivite
        ORDER BY categories_tarifs.nom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictCategoriesTarifs = {}
        for IDcategorie_tarif, nomCategorie, nomActivite, abregeActivite in listeDonnees :
            self.dictCategoriesTarifs[IDcategorie_tarif] = {
                "nomCategorie" : nomCategorie,
                "nomActivite" : nomActivite,
                "abregeActivite" : abregeActivite,
                }

        req = """SELECT IDactivite, nom
        FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictActivites = {}
        for IDactivite, nom in listeDonnees :
            self.dictActivites[IDactivite] = {"nom" : nom}

        req = """SELECT IDindividu, nom, prenom
        FROM individus;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictIndividus = {}
        for IDindividu, nom, prenom in listeDonnees :
            if nom == None : nom = ""
            if prenom == None : prenom = ""
            nom_complet = u"%s %s" % (nom, prenom)
            self.dictIndividus[IDindividu] = {"nom" : nom, "prenom": prenom, "nom_complet" : nom_complet}

        DB.Close()

        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        
    def Importation_prestations(self):
        """ Importation des données """

        # Chargement des informations individuelles
        self.infosIndividus = UTILS_Infos_individus.Informations(date_reference=self.date_debut, qf=True, inscriptions=True, messages=False, infosMedicales=False, cotisationsManquantes=False, piecesManquantes=False, questionnaires=True, scolarite=True)
        self.dictInfosIndividus = self.infosIndividus.GetDictValeurs(mode="individu", ID=None, formatChamp=False)
        self.dictInfosFamilles = self.infosIndividus.GetDictValeurs(mode="famille", ID=None, formatChamp=False)

        DB = GestionDB.DB()

        # Récupèration de la ventilation des prestations de la période
        conditionDepots = ""
        if self.filtreDepots == True and self.filtreDepots_dateDebut != None and self.filtreDepots_dateFin !=None :
            conditionDepots = " AND (depots.date>='%s' and depots.date<='%s') " % (self.filtreDepots_dateDebut, self.filtreDepots_dateFin)
        
        conditionReglements = ""
        if self.filtreReglements == True and self.filtreReglements_dateDebut != None and self.filtreReglements_dateFin !=None :
            conditionReglements = " AND (reglements.date_saisie>='%s' and reglements.date_saisie<='%s') " % (self.filtreReglements_dateDebut, self.filtreReglements_dateFin)
        
        req = """SELECT 
        ventilation.IDventilation, ventilation.IDreglement, ventilation.IDprestation, ventilation.montant,
        reglements.date, reglements.date_saisie, depots.date,
        prestations.date
        FROM ventilation
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN depots ON depots.IDdepot = reglements.IDdepot
        WHERE prestations.date>='%s' AND prestations.date <='%s' %s %s
        ORDER BY prestations.date; """ % (self.date_debut, self.date_fin, conditionDepots, conditionReglements)
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()

        dictVentilation = {}
        for IDventilation, IDreglement, IDprestation, montantVentilation, dateReglement, dateSaisieReglement, dateDepotReglement, datePrestation in listeVentilation :
            if (IDprestation in dictVentilation) == False :
                dictVentilation[IDprestation] = 0.0
            dictVentilation[IDprestation] += montantVentilation
            
        # Condition Afficher Cotisations et/ou Consommations ?
        listeAffichage = []
        if self.afficher_cotisations == True : listeAffichage.append("cotisation")
        if self.afficher_locations == True: listeAffichage.append("location")
        if self.afficher_consommations == True : listeAffichage.append("consommation")
        if self.afficher_autres == True : listeAffichage.append("autre")
        
        if len(listeAffichage) == 0 : conditionAfficher = "categorie='xxxxxxx' "
        elif len(listeAffichage) == 1 : conditionAfficher = "categorie='%s'" % listeAffichage[0]
        else : conditionAfficher = "categorie IN %s" % str(tuple(listeAffichage))
                
        # Condition Activités affichées
        if len(self.listeActivites) == 0 : conditionActivites = "prestations.IDactivite=9999999"
        elif len(self.listeActivites) == 1 : conditionActivites = "prestations.IDactivite=%d" % self.listeActivites[0]
        else : conditionActivites = "prestations.IDactivite IN %s" % str(tuple(self.listeActivites))

        # Filtre Prestation facturée / non facturée
        conditionFacturee = ""
        if "facturee" in self.mode_affichage :
            conditionFacturee = " AND prestations.IDfacture IS NOT NULL"
        if "nonfacturee" in self.mode_affichage :
            conditionFacturee = " AND prestations.IDfacture IS NULL"
        
        # Récupération de toutes les prestations de la période
        req = """SELECT IDprestation, prestations.date, categorie, label, montant, prestations.IDactivite, prestations.IDcategorie_tarif, prestations.IDfamille, IDindividu, prestations.IDfacture, factures.numero
        FROM prestations
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        WHERE date>='%s' AND date <='%s'
        AND %s AND (%s OR prestations.IDactivite IS NULL)
        %s
        ORDER BY date; """ % (self.date_debut, self.date_fin, conditionAfficher, conditionActivites, conditionFacturee)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()

        # Récupération des tranches de tarifs paramétrées
        if len(self.listeActivites) == 0 :
            condition = ""
        else :
            condition = "AND %s" % conditionActivites.replace("prestations.", "")
        req = """SELECT IDligne, qf_min, qf_max
        FROM tarifs_lignes
        WHERE qf_min IS NOT NULL AND qf_max IS NOT NULL
        %s
        ;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        liste_tranches = []
        for IDligne, qf_min, qf_max in listeDonnees:
            tranche = float(qf_min), float(qf_max)
            if tranche not in liste_tranches :
                liste_tranches.append(tranche)
        liste_tranches.sort()

        DB.Close()
        
        dictPrestations = {}
        listeRegroupements = []
        dictLabelsRegroupements = {}
        for IDprestation, date, categorie, label, montant, IDactivite, IDcategorie_tarif, IDfamille, IDindividu, IDfacture, num_facture in listePrestations :
            date = UTILS_Dates.DateEngEnDateDD(date)
            annee = date.year
            mois = date.month

            if montant == None :
                montant = 0.0

            def GetKey(key_code=""):
                key = None
                key_label = ""
                key_tri = None

                if key_code == "jour":
                    key = date
                    key_tri = key
                    key_label = UTILS_Dates.DateEngFr(date)

                if key_code == "mois":
                    key = (annee, mois)
                    key_tri = key
                    key_label = PeriodeComplete(mois, annee)

                if key_code == "annee":
                    key = annee
                    key_tri = key
                    key_label = str(annee)

                if key_code == "label_prestation":
                    key = label
                    key_tri = label
                    key_label = label

                if key_code == "activite":
                    key = IDactivite
                    if IDactivite == None or (IDactivite in self.dictActivites) == False:
                        key_label = _(u"Activité inconnue")
                    else:
                        key_label = self.dictActivites[IDactivite]["nom"]
                    key_tri = key_label

                if key_code == "categorie_tarif":
                    key = IDcategorie_tarif
                    if IDcategorie_tarif == None or (IDcategorie_tarif in self.dictCategoriesTarifs) == False:
                        key_label = _(u"Sans catégorie")
                    else:
                        key_label = self.dictCategoriesTarifs[IDcategorie_tarif]["nomCategorie"]
                    key_tri = key_label

                if key_code == "famille":
                    key = IDfamille
                    if IDfamille == None or (IDfamille in self.dict_titulaires) == False:
                        key_label = _(u"Famille inconnue")
                    else:
                        key_label = self.dict_titulaires[IDfamille]["titulairesSansCivilite"]
                    key_tri = key_label

                if key_code == "individu":
                    key = IDindividu
                    if IDindividu == None or (IDindividu in self.dictIndividus) == False:
                        key_label = _(u"Individu inconnu")
                    else:
                        key_label = self.dictIndividus[IDindividu]["nom_complet"]
                    key_tri = key_label

                if key_code == "ville_residence" and IDindividu not in (0, None) :
                    key = self.dictInfosIndividus[IDindividu]["INDIVIDU_VILLE"]
                    key_label = key
                    key_tri = key

                if key_code == "secteur" and IDindividu not in (0, None) :
                    key = self.dictInfosIndividus[IDindividu]["INDIVIDU_SECTEUR"]
                    key_label = key
                    key_tri = key

                if key_code == "age" and IDindividu not in (0, None) :
                    key = self.dictInfosIndividus[IDindividu]["INDIVIDU_AGE_INT"]
                    key_label = str(key)
                    key_tri = key

                if key_code == "nom_ecole" and IDindividu not in (0, None) :
                    key = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_ECOLE"]
                    key_label = key
                    key_tri = key

                if key_code == "nom_classe" and IDindividu not in (0, None) :
                    key = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_CLASSE"]
                    key_label = key
                    key_tri = key

                if key_code == "nom_niveau_scolaire" and IDindividu not in (0, None) :
                    key = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_NIVEAU"]
                    key_label = key
                    key_tri = key

                if key_code == "regime":
                    key = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_REGIME"]
                    key_label = key
                    key_tri = key

                if key_code == "caisse":
                    key = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_CAISSE"]
                    key_label = key
                    key_tri = key

                # QF
                if key_code.startswith("qf"):
                    key = None
                    if "FAMILLE_QF_ACTUEL_INT" in self.dictInfosFamilles[IDfamille]:
                        qf = self.dictInfosFamilles[IDfamille]["FAMILLE_QF_ACTUEL_INT"]

                        # Tranches de 100
                        if key_code == "qf_100" :
                            for x in range(0, 10000, 100):
                                min, max = x, x + 99
                                if qf >= min and qf <= max:
                                    key = (min, max)
                                    key_tri = key
                                    key_label = "%s - %s" % (min, max)

                        # Tranches paramétrées
                        if key_code == "qf_tarifs" :
                            for min, max in liste_tranches :
                                if qf >= min and qf <= max:
                                    key = (min, max)
                                    key_tri = key
                                    key_label = "%s - %s" % (min, max)

                # Num facture
                if key_code == "num_facture":
                    key = num_facture
                    key_tri = num_facture
                    key_label = str(num_facture)

                # Num facture + famille
                if key_code == "num_facture_famille":
                    if IDfamille == None or (IDfamille in self.dict_titulaires) == False:
                        nom_famille = _(u"Famille inconnue")
                    else:
                        nom_famille = self.dict_titulaires[IDfamille]["titulairesSansCivilite"]
                    key = u"%s - %s" % (num_facture or u"Non facturé", nom_famille)
                    key_tri = key
                    key_label = key

                # Questionnaires
                if key_code.startswith("question_") and "famille" in key_code:
                    key = self.dictInfosFamilles[IDfamille]["QUESTION_%s" % key_code[17:]]
                    key_label = six.text_type(key)
                    key_tri = key_label

                if key_code.startswith("question_") and "individu" in key_code and IDindividu not in (0, None) :
                    key = self.dictInfosIndividus[IDindividu]["QUESTION_%s" % key_code[18:]]
                    key_label = six.text_type(key)
                    key_tri = key_label

                if key in ("", None) :
                    key = _(u"- Autre -")
                    key_label = key
                    key_tri = key_label

                return key, key_label, key_tri

            # Création des keys de regroupements
            regroupement, labelRegroupement, triRegroupement = GetKey(self.key_colonne)
            key1, key1_label, key1_tri = GetKey(self.key_ligne1)
            key2, key2_label, key2_tri = GetKey(self.key_ligne2)

            # Mémorisation du regroupement
            if regroupement not in listeRegroupements :
                listeRegroupements.append(regroupement)
                dictLabelsRegroupements[regroupement] = labelRegroupement


            # Total
            if (key1 in dictPrestations) == False :
                dictPrestations[key1] = {"label" : key1_label, "tri" : key1_tri, "nbre" : 0, "facture" : 0.0, "regle" : 0.0, "impaye" : 0.0, "regroupements" : {} }
            dictPrestations[key1]["nbre"] += 1
            dictPrestations[key1]["facture"] += montant
            
            # Détail par période
            if (regroupement in dictPrestations[key1]["regroupements"]) == False :
                dictPrestations[key1]["regroupements"][regroupement] = {"nbre" : 0, "facture" : 0.0, "regle" : 0.0, "impaye" : 0.0, "key2" : {} }
            dictPrestations[key1]["regroupements"][regroupement]["nbre"] += 1
            dictPrestations[key1]["regroupements"][regroupement]["facture"] += montant
            
            # Détail par catégorie de tarifs
            if (key2 in dictPrestations[key1]["regroupements"][regroupement]["key2"]) == False :
                dictPrestations[key1]["regroupements"][regroupement]["key2"][key2] = {"label" : key2_label, "tri" : key2_tri, "nbre" : 0, "facture" : 0.0, "regle" : 0.0, "impaye" : 0.0}
            dictPrestations[key1]["regroupements"][regroupement]["key2"][key2]["nbre"] += 1
            dictPrestations[key1]["regroupements"][regroupement]["key2"][key2]["facture"] += montant
            
            # Ajoute la ventilation
            if IDprestation in dictVentilation :
                dictPrestations[key1]["regle"] += dictVentilation[IDprestation]
                dictPrestations[key1]["regroupements"][regroupement]["regle"] += dictVentilation[IDprestation]
                dictPrestations[key1]["regroupements"][regroupement]["key2"][key2]["regle"] += dictVentilation[IDprestation]
            
            # Calcule les impayés
            dictPrestations[key1]["impaye"] = dictPrestations[key1]["regle"] - dictPrestations[key1]["facture"]
            dictPrestations[key1]["regroupements"][regroupement]["impaye"] = dictPrestations[key1]["regroupements"][regroupement]["regle"] - dictPrestations[key1]["regroupements"][regroupement]["facture"]
            dictPrestations[key1]["regroupements"][regroupement]["key2"][key2]["impaye"] = dictPrestations[key1]["regroupements"][regroupement]["key2"][key2]["regle"] - dictPrestations[key1]["regroupements"][regroupement]["key2"][key2]["facture"]

        listeRegroupements.sort()

        return dictPrestations, listeRegroupements, dictLabelsRegroupements
    
    def CreationColonnes(self, listeRegroupements=[], dictLabelsRegroupements={}):
        """ Création des colonnes """
        # Création de la première colonne
        self.AddColumn(_(u"Prestations"))
        self.SetColumnWidth(0, 250)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
        
        # Création des colonnes périodes
        numColonne = 1
        for regroupement in listeRegroupements :
            label_regroupement = dictLabelsRegroupements[regroupement]
            self.AddColumn(label_regroupement)
            self.SetColumnWidth(numColonne, 70)
            self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
            numColonne += 1
        
        # Création de la colonne Total
        self.AddColumn(_(u"Total"))
        self.SetColumnWidth(numColonne, 70)
        self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
        
    def MAJ(self):
        dlgAttente = wx.BusyInfo(_(u"Recherche des données..."), self)

        # Importation des données
        dictPrestations, listeRegroupements, dictLabelsRegroupements = self.Importation_prestations()
        self.dictImpression = { "entete" : [], "contenu" : [], "total" : [], "coloration" : [] }
        
        mode_affichage = self.mode_affichage.split("_")[0]

        # Mémorisation des colonnes
        dictColonnes = {}
        index = 1
        self.dictImpression["entete"].append(_(u"Prestations"))
        for regroupement in listeRegroupements :
            dictColonnes[regroupement] = index
            label = dictLabelsRegroupements[regroupement]
            self.dictImpression["entete"].append(label)
            index += 1
        dictColonnes["total"] = index
        self.dictImpression["entete"].append(_(u"Total"))
        
        # Initialisation du CTRL
        self.RAZ() 
        self.CreationColonnes(listeRegroupements, dictLabelsRegroupements)
        self.root = self.AddRoot(_(u"Racine"))
        
        # Création des branches
        
        # ------------------ Branches key1 -----------------
        listeKeys1 = []
        for key1, dictKey1 in dictPrestations.items() :
            listeKeys1.append((dictKey1["tri"], key1, dictKey1["label"]))
        listeKeys1.sort()
        
        for key1_tri, key1, key1_label in listeKeys1 :
            niveau1 = self.AppendItem(self.root, key1_label)
            
            regroupements = list(dictPrestations[key1]["regroupements"].keys())
            regroupements.sort()
            
            impressionLigne = [key1_label,]
            if self.key_ligne2 != "" :
                self.dictImpression["coloration"].append(len(self.dictImpression["contenu"]))
            
            # Colonnes périodes
            for regroupement in listeRegroupements :
                if regroupement in dictPrestations[key1]["regroupements"] :
                    valeur = dictPrestations[key1]["regroupements"][regroupement][mode_affichage]
                    if "nbre" in mode_affichage : 
                        texte = str(int(valeur))
                    else:
                        texte = u"%.2f %s" % (valeur, SYMBOLE)
                    self.SetItemText(niveau1, texte, dictColonnes[regroupement])
                    impressionLigne.append(texte)
                else:
                    impressionLigne.append("")
            
            # Colonne Total
            valeur = dictPrestations[key1][mode_affichage]
            if "nbre" in mode_affichage : 
                texte = str(int(valeur))
            else:
                texte = u"%.2f %s" % (valeur, SYMBOLE)
            self.SetItemText(niveau1, texte, dictColonnes["total"])
            impressionLigne.append(texte)
            
            self.dictImpression["contenu"].append(impressionLigne)
            
            # ----------------- Branches key2 -------------

            listeKeys2 = []
            for regroupement in regroupements:
                for key2, dictKey2 in dictPrestations[key1]["regroupements"][regroupement]["key2"].items():
                    key = (dictKey2["tri"], key2, dictKey2["label"])
                    if key not in listeKeys2:
                        listeKeys2.append(key)
            listeKeys2.sort()

            for key2_tri, key2, key2_label in listeKeys2 :
                if self.key_ligne2 != "" :
                    niveau2 = self.AppendItem(niveau1, key2_label)
                    self.SetItemFont(niveau2, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    self.SetItemTextColour(niveau2, wx.Colour(160, 160, 160) )
                    impressionLigne = [key2_label,]

                # Colonnes périodes
                totalLigne = 0.0
                for regroupement in listeRegroupements :
                    texte = None
                    if regroupement in dictPrestations[key1]["regroupements"] :
                        if key2 in dictPrestations[key1]["regroupements"][regroupement]["key2"] :
                            valeur = dictPrestations[key1]["regroupements"][regroupement]["key2"][key2][mode_affichage]
                            totalLigne += valeur
                            if "nbre" in mode_affichage : 
                                texte = str(int(valeur))
                            else:
                                texte = u"%.2f %s" % (valeur, SYMBOLE)
                            if self.key_ligne2 != "" :
                                self.SetItemText(niveau2, texte, dictColonnes[regroupement])
                                impressionLigne.append(texte)
                    if texte == None and self.key_ligne2 != "" : impressionLigne.append("")
                        
                # Colonne Total
                if self.key_ligne2 != "" :
                    if "nbre" in mode_affichage : 
                        texte = str(int(totalLigne))
                    else:
                        texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                    self.SetItemText(niveau2, texte, dictColonnes["total"])
                    impressionLigne.append(texte)
                    
                    self.dictImpression["contenu"].append(impressionLigne)
        
        # ------------ Ligne Total --------------
        niveauTotal = self.AppendItem(self.root, _(u"Total"))
        self.SetItemBackgroundColour(niveauTotal, wx.Colour(150, 150, 150) )
        self.SetItemTextColour(niveauTotal, wx.Colour(255, 255, 255) )
        
        impressionLigne = [_(u"Total"),]
        
        dictTotal = {}
        totalRegroupements = {}
        dictLabelsKey2 = {}
        for key1_tri, key1, key1_label in listeKeys1 :
            for regroupement, dictRegroupement in dictPrestations[key1]["regroupements"].items() :
                for key2, dictKey2 in dictRegroupement["key2"].items() :
                    dictLabelsKey2[key2] = dictKey2["label"]
                    if (key2 in dictTotal) == False :
                        dictTotal[key2] = {}
                    if (regroupement in dictTotal[key2]) == False :
                        dictTotal[key2][regroupement] = 0.0
                    dictTotal[key2][regroupement] += dictKey2[mode_affichage]
                
                    if (regroupement in totalRegroupements) == False :
                        totalRegroupements[regroupement] = 0.0
                    totalRegroupements[regroupement] += dictKey2[mode_affichage]
        
        totalLigne = 0.0
        for regroupement in listeRegroupements :
            valeur = totalRegroupements[regroupement]
            totalLigne += valeur
            if "nbre" in mode_affichage : 
                texte = str(int(valeur))
            else:
                texte = u"%.2f %s" % (valeur, SYMBOLE)
            self.SetItemText(niveauTotal, texte, dictColonnes[regroupement])
            impressionLigne.append(texte)

        if "nbre" in mode_affichage : 
            texte = str(int(totalLigne))
        else:
            texte = u"%.2f %s" % (totalLigne, SYMBOLE)
        self.SetItemText(niveauTotal, texte, dictColonnes["total"])
        impressionLigne.append(texte)
        
        self.dictImpression["total"].append(impressionLigne)
        
        if self.key_ligne2 != "" and self.affichage_details_total == True:
            
            # Tri des key2
            listeKey2 = []
            for key2 in list(dictTotal.keys()) :
                listeKey2.append((key2, dictLabelsKey2[key2]))
            listeKey2.sort()

            for key2, key2_label in listeKey2 :
                niveauCategorie = self.AppendItem(niveauTotal, key2_label)
                self.SetItemFont(niveauCategorie, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                self.SetItemTextColour(niveauCategorie, wx.Colour(120, 120, 120) )
                self.SetItemBackgroundColour(niveauCategorie, wx.Colour(210, 210, 210) )
                
                impressionLigne = [key2_label,]
                
                totalLigne = 0.0
                for regroupement in listeRegroupements :
                    texte = None
                    if key2 in dictTotal :
                        if regroupement in dictTotal[key2] :
                            valeur = dictTotal[key2][regroupement]
                            totalLigne += valeur
                            if "nbre" in mode_affichage : 
                                texte = str(int(valeur))
                            else:
                                texte = u"%.2f %s" % (valeur, SYMBOLE)
                            self.SetItemText(niveauCategorie, texte, dictColonnes[regroupement])
                            impressionLigne.append(texte)
                    if texte == None : impressionLigne.append("")
                
                if "nbre" in mode_affichage : 
                    texte = str(int(totalLigne))
                else:
                    texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                self.SetItemText(niveauCategorie, texte, dictColonnes["total"])
                impressionLigne.append(texte)
                
                self.dictImpression["total"].append(impressionLigne)
        
        self.ExpandAllChildren(self.root)

        del dlgAttente

    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
    
    def SetAffichageDetailsTotal(self, etat=True):
        self.affichage_details_total = etat

    def DevelopperTout(self):
        item = self.GetFirstChild(self.root)[0]
        for index in range(0, self.GetChildrenCount(self.root)-1) :
            self.Expand(item)
            item = self.GetNext(item)
        
    def ReduireTout(self):
        item = self.GetFirstChild(self.root)[0]
        for index in range(0, self.GetChildrenCount(self.root)-1) :
            self.Collapse(item)
            item = self.GetNext(item)
        
    def Imprimer(self):
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        hauteur_page = A4[0]
        largeur_page = A4[1]
            
        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("SYNTHESE_PRESTATIONS", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=20, leftMargin=40, rightMargin=40)
        story = []
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeur_page-175, 100) )
        dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Synthèse des prestations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        story.append(Spacer(0, 10))       
        
        # Intro
        styleA = ParagraphStyle(name="A", fontName="Helvetica", fontSize=6, spaceAfter=20)
        story.append(Paragraph(self.labelParametres, styleA))       

        # Tableau
        dataTableau = []
        largeursColonnes = [160,]
        for x in range(0, len(self.dictImpression["entete"])-1):
            largeursColonnes.append(45)
        
        # Entetes labels
        dataTableau.append(self.dictImpression["entete"])
        
        # Contenu du tableau
        listeRubriques = ("contenu", "total")
        for rubrique in listeRubriques :
            listeLignes = self.dictImpression[rubrique]
            
            for ligne in listeLignes :
                dataTableau.append(ligne)
        
        positionLigneTotal = len(self.dictImpression["contenu"]) + 1
        listeStyles = [
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
            
            ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
            ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Centre les cases
                    
##            ('ALIGN', (0,1), (-1,1), 'CENTRE'), # Ligne de labels colonne alignée au centre
##            ('FONT',(0,1),(-1,1), "Helvetica", 6), # Donne la police de caract. + taille de police des labels
##            
##            ('SPAN',(0,0),(-1,0)), # Fusionne les lignes du haut pour faire le titre du groupe
##            ('FONT',(0,0),(0,0), "Helvetica-Bold", 10), # Donne la police de caract. + taille de police du titre de groupe
            ('BACKGROUND', (0,0), (-1,0), (0.6, 0.6, 0.6) ), # Donne la couleur de fond du label
            ('BACKGROUND', (0, positionLigneTotal), (-1, positionLigneTotal), (0.6, 0.6, 0.6) ), # Donne la couleur de fond du label
            ]
            
        # Formatage des lignes "Activités"
        for indexColoration in self.dictImpression["coloration"] :
            listeStyles.append( ('FONT', (0, indexColoration+1), (-1, indexColoration+1), "Helvetica-Bold", 7) )
            listeStyles.append( ('BACKGROUND', (0, indexColoration+1), (-1, indexColoration+1), (0.8, 0.8, 0.8)) ) 
                
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
        story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
    
    def ExportExcel(self):
        """ Export Excel """
        titre = _(u"Synthèse des prestations")
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xlsx" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xlsx)|*.xlsx|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.FD_SAVE
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
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()
                
        # Export
        import xlsxwriter
        classeur = xlsxwriter.Workbook(cheminFichier)
        feuille = classeur.add_worksheet(titre)

        format_money = classeur.add_format({'num_format': '# ##0.00'})
        format_money_titre = classeur.add_format({'num_format': '# ##0.00', 'bold': True, 'bg_color': '#E7EAED'})
        format_titre = classeur.add_format({'align': 'center', 'bold': True, 'bg_color': '#E7EAED'})

        # Création des labels de colonnes
        x = 0
        y = 0
        for valeur in self.dictImpression["entete"] :
            feuille.write(x, y, valeur)
            feuille.set_column(y, y, 15)
            y += 1
        feuille.set_column(0, 0, 40)
        
        def RechercheFormat(valeur, titre):
            """ Recherche si la valeur est un nombre """
            format = None
            if valeur.endswith(SYMBOLE) :
                # Si c'est un montant en euros
                try :
                    nbre = float(valeur[:-1]) 
                    if titre == True :
                        format = format_money_titre
                    else:
                        format = format_money
                    return (nbre, format)
                except :
                    pass
                    
            else:
                # Si c'est un nombre
                try :
                    nbre = float(valeur)
                    if titre == True :
                        format = format_titre
                    return (nbre, format)
                except :
                    pass
            
            return False, None
            
            
        # Contenu
        x = 1
        y = 0
        for ligne in self.dictImpression["contenu"] :
            for valeur in ligne :
                
                # Recherche si c'est un titre
                if x-1 in self.dictImpression["coloration"] :
                    titre = True
                else:
                    titre = False
                
                # Recherche s'il y a un format de nombre ou de montant
                nbre, format = RechercheFormat(valeur, titre)
                if nbre != False : 
                    valeur = nbre
                    
                if nbre == False and titre == True and format == None :
                    format = format_titre

                # Enregistre la valeur
                if format != None :
                    feuille.write(x, y, valeur, format)
                else:
                    feuille.write(x, y, valeur)
                    
                y += 1
            x += 1
            y = 0
        
        # Total
        premiereLigne = True
        for ligne in self.dictImpression["total"] :
            for valeur in ligne :
                
                # Recherche si c'est un titre
                if premiereLigne == True :
                    titre = True
                else:
                    titre = False
                
                # Recherche s'il y a un format de nombre ou de montant
                nbre, format = RechercheFormat(valeur, titre)
                if nbre != False : 
                    valeur = nbre
                    
                if nbre == False and titre == True and format == None :
                    format = format_titre

                # Enregistre la valeur
                if format != None :
                    feuille.write(x, y, valeur, format)
                else:
                    feuille.write(x, y, valeur)

                y += 1
            premiereLigne = False
            x += 1
            y = 0
            
        # Finalisation du fichier xlsx
        classeur.close()

        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.ctrl_stats = CTRL(panel)
        
        self.ctrl_stats.date_debut = datetime.date(2011, 7, 1)
        self.ctrl_stats.date_fin = datetime.date(2011, 12, 31)
        self.ctrl_stats.afficher_consommations = True
        self.ctrl_stats.afficher_cotisations = True
        self.ctrl_stats.afficher_locations = True
        self.ctrl_stats.listeActivites = [1, 2]
        self.ctrl_stats.MAJ()
        
        self.choix = wx.Choice(panel, -1, choices=["facture", "regle", "impaye", "nbre"])
        self.choix.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.choix)

        liste_regroupements = [
            "jour", "mois", "annee", "activite", "categorie_tarif", "ville_residence", "secteur",
            "age", "nom_ecole", "nom_classe", "nom_niveau_scolaire",
            "regime", "caisse", "qf_100", "qf_tarifs",
            ]

        self.regroupement = wx.Choice(panel, -1, choices=liste_regroupements)
        self.regroupement.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.regroupement)

        self.bouton_imprimer = wx.BitmapButton(panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_stats, 1, wx.ALL|wx.EXPAND, 4)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.choix, 0, wx.ALL, 4)
        sizer_3.Add(self.regroupement, 0, wx.ALL, 4)
        sizer_3.Add(self.bouton_imprimer, 0, wx.ALL, 4)
        sizer_2.Add(sizer_3, 0, wx.ALL, 0)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
    
    def OnChoix(self, event):
        self.ctrl_stats.mode_affichage = self.choix.GetStringSelection()
        self.ctrl_stats.key_colonne = self.regroupement.GetStringSelection()
        self.ctrl_stats.MAJ() 
    
    def OnBoutonImprimer(self, event):
        self.ctrl_stats.ExportExcel() 
        

if __name__ == '__main__':    
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
