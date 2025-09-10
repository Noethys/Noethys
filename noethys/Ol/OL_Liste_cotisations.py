#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
# ------------------------------------------------------------------------


from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
from Utils import UTILS_Interface
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import time
import FonctionsPerso
import GestionDB
from Utils import UTILS_Historique
from Utils import UTILS_Titulaires
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Config
from Utils import UTILS_Dates
from Utils import UTILS_Gestion
from Utils import UTILS_Infos_individus
from Utils import UTILS_Divers
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


class Track(object):
    def __init__(self, parent, donnees, dictFacturation):
        self.IDcotisation = donnees[0]
        self.IDfamille = donnees[1]
        self.IDindividu = donnees[2]
        self.IDtype_cotisation = donnees[3]
        self.IDunite_cotisation = donnees[4]
        self.date_saisie = UTILS_Dates.DateEngEnDateDD(donnees[5])
        self.IDutilisateur = donnees[6]
        self.date_creation_carte = donnees[7]
        self.numero = donnees[8]
        self.IDdepot_cotisation = donnees[9]
        self.date_debut = UTILS_Dates.DateEngEnDateDD(donnees[10])
        self.date_fin = UTILS_Dates.DateEngEnDateDD(donnees[11])
        self.IDprestation = donnees[12]
        self.nomTypeCotisation = donnees[13]
        self.typeTypeCotisation = donnees[14]
        self.typeHasCarte = donnees[15]
        self.nomUniteCotisation = donnees[16]
        self.IDcompte_payeur = donnees[17]
        self.observations = donnees[18]
        self.activites = donnees[19]
        if self.activites == None:
            self.activites = ""

        # Activites
        texte = ""
        if len(self.activites) > 0:
            listeTemp = []
            listeIDactivites = UTILS_Divers.ConvertChaineEnListe(
                self.activites)
            for IDactivite in listeIDactivites:
                if IDactivite in parent.dictActivites:
                    nomActivite = parent.dictActivites[IDactivite]["nom"]
                    listeTemp.append(nomActivite)
            if len(listeTemp) > 0:
                texte = ", ".join(listeTemp)
        self.activitesStr = texte

        # Nom cotisation
        self.nomCotisation = u"%s - %s" % (self.nomTypeCotisation,
                                           self.nomUniteCotisation)

        # Numéro de cotisation
        try:
            self.numero_int = int(self.numero)
        except:
            self.numero_int = None

        # Titulaires famille
        if self.IDfamille in parent.titulaires:
            self.nomsTitulaires = parent.titulaires[self.IDfamille]["titulairesSansCivilite"]
        else:
            self.nomsTitulaires = "nom inconnu"

        # Type
        if self.typeTypeCotisation == "famille":
            self.typeStr = _(u"Cotisation familiale")
        else:
            self.typeStr = _(u"Cotisation individuelle")

        # Validité
        dateDuJour = datetime.date.today()
        if dateDuJour >= self.date_debut and dateDuJour <= self.date_fin:
            self.valide = True
        else:
            self.valide = False

        # Dépôt
        if self.IDdepot_cotisation == None:
            self.depotStr = _(u"Non déposée")
        else:
            self.depotStr = _(u"Dépôt n°%d") % self.IDdepot_cotisation

        # Nom des titulaires de famille
        self.beneficiaires = ""
        self.rue = ""
        self.cp = ""
        self.ville = ""

        if self.IDfamille != None:
            self.beneficiaires = _(u"IDfamille n°%d") % self.IDfamille
            if parent.dictFamillesRattachees != None:
                if self.IDfamille in parent.dictFamillesRattachees:
                    self.beneficiaires = parent.dictFamillesRattachees[self.IDfamille]["nomsTitulaires"]
            else:
                if self.IDfamille in parent.titulaires:
                    self.beneficiaires = parent.titulaires[self.IDfamille]["titulairesSansCivilite"]
                    self.rue = parent.titulaires[self.IDfamille]["adresse"]["rue"]
                    self.cp = parent.titulaires[self.IDfamille]["adresse"]["cp"]
                    self.ville = parent.titulaires[self.IDfamille]["adresse"]["ville"]

        if self.IDindividu != None and self.IDindividu in parent.individus:
            self.beneficiaires = parent.individus[self.IDindividu]["nom_complet"]
            self.rue = parent.individus[self.IDindividu]["rue"]
            self.cp = parent.individus[self.IDindividu]["cp"]
            self.ville = parent.individus[self.IDindividu]["ville"]

        # Facturation
        self.montant = 0.0
        self.ventilation = 0.0
        self.dateReglement = None
        self.modeReglement = None

        if self.IDprestation in dictFacturation:
            self.montant = dictFacturation[self.IDprestation]["montant"]
            self.ventilation = dictFacturation[self.IDprestation]["ventilation"]
            self.dateReglement = dictFacturation[self.IDprestation]["dateReglement"]
            self.modeReglement = dictFacturation[self.IDprestation]["modeReglement"]

        self.solde = float(FloatToDecimal(self.montant) -
                           FloatToDecimal(self.ventilation))
        if self.solde > 0.0:
            self.solde = -self.solde
        if self.montant == None:
            self.solde = 0.0


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", None)
        self.IDfamille = kwds.pop("IDfamille", None)
        self.dictFamillesRattachees = kwds.pop("dictFamillesRattachees", None)
        self.mode = kwds.pop("mode", "liste")
        self.codesColonnes = kwds.pop("codesColonnes", [])
        self.checkColonne = kwds.pop("checkColonne", False)
        self.triColonne = kwds.pop("triColonne", "numero")
        self.filtres = None
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.labelParametres = ""
        self.titre = _(u"Liste des cotisations")

        # Périodes de gestion
        self.gestion = UTILS_Gestion.Gestion(None)

        # Importation des activités
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC;"""
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        self.dictActivites = {}
        for IDactivite, nom, abrege in listeTemp:
            dictTemp = {"IDactivite": IDactivite, "nom": nom, "abrege": abrege}
            self.dictActivites[IDactivite] = dictTemp

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def OnItemActivated(self, event):
        self.Modifier(None)

    def InitModel(self):
        self.donnees = self.GetTracks()

        # Récupération des infos de base individus et familles
        if self.mode == "liste":
            self.infosIndividus = UTILS_Infos_individus.Informations()
            for track in self.donnees:
                if track.IDindividu != None:
                    self.infosIndividus.SetAsAttributs(
                        parent=track, mode="individu", ID=track.IDindividu)
            for track in self.donnees:
                if track.IDfamille != None:
                    self.infosIndividus.SetAsAttributs(
                        parent=track, mode="famille", ID=track.IDfamille)

    def SetFiltres(self, filtres=None):
        self.filtres = filtres

    def ComparateurFiltre(self, valeur1=12.00, operateur=">=", valeur2=0.0):
        if operateur == "=":
            if valeur1 == valeur2:
                return True
        if operateur == "<>":
            if valeur1 != valeur2:
                return True
        if operateur == ">":
            if valeur1 > valeur2:
                return True
        if operateur == "<":
            if valeur1 < valeur2:
                return True
        if operateur == ">=":
            if valeur1 >= valeur2:
                return True
        if operateur == "<=":
            if valeur1 <= valeur2:
                return True
        return False

    def GetTracks(self):
        """ Récupération des données """
        self.individus = UTILS_Titulaires.GetIndividus()
        self.titulaires = UTILS_Titulaires.GetTitulaires()

        listeID = None
        DB = GestionDB.DB()

        # Conditions
        listeConditions = []
        conditions = ""

        # 1ère série de filtres
        if self.filtres != None:
            for filtre in self.filtres:

                # IDcotisation_intervalle
                if filtre["type"] == "IDcotisation_intervalle":
                    listeConditions.append("(cotisations.IDcotisation>=%d AND cotisations.IDcotisation<=%d)" % (
                        filtre["IDcotisation_min"], filtre["IDcotisation_max"]))

                # IDcotisation_liste
                if filtre["type"] == "IDcotisation_liste":
                    if len(filtre["liste"]) == 0:
                        listeTemp = "()"
                    elif len(filtre["liste"]) == 1:
                        listeTemp = "(%d)" % filtre["liste"][0]
                    else:
                        listeTemp = str(tuple(filtre["liste"]))
                    listeConditions.append(
                        "cotisations.IDcotisation IN %s" % listeTemp)

                # Type de cotisation
                if filtre["type"] == "type":
                    listeConditions.append(
                        "cotisations.IDtype_cotisation=%d" % filtre["IDtype_cotisation"])

                # Unité de cotisation
                if filtre["type"] == "unite":
                    listeConditions.append(
                        "cotisations.IDunite_cotisation=%d" % filtre["IDunite_cotisation"])

                # Carte créée
                if filtre["type"] == "carte":
                    if filtre["choix"] == True:
                        listeConditions.append(
                            "cotisations.date_creation_carte IS NOT NULL")
                    else:
                        listeConditions.append(
                            "cotisations.date_creation_carte IS NULL")

                # Carte facturée
                if filtre["type"] == "facturee":
                    if filtre["choix"] == True:
                        listeConditions.append(
                            "cotisations.IDprestation IS NOT NULL")
                    else:
                        listeConditions.append(
                            "cotisations.IDprestation IS NULL")

                # Dépôt
                if filtre["type"] == "depot":
                    listeConditions.append(
                        "cotisations.IDdepot_cotisation=%d" % filtre["IDdepot_cotisation"])

        dictFacturation = {}

        if self.mode == "liste":

            # Pour le mode LISTE
            if len(listeConditions) > 0:
                conditions = "WHERE %s" % " AND ".join(listeConditions)

            req = """SELECT prestations.IDprestation, SUM(montant)
            FROM cotisations
            LEFT JOIN prestations ON prestations.IDprestation = cotisations.IDprestation
            %s 
            GROUP BY cotisations.IDprestation;""" % conditions
            DB.ExecuterReq(req)
            listePrestations = DB.ResultatReq()
            for IDprestation, montant in listePrestations:
                dictFacturation[IDprestation] = {
                    "montant": montant, "ventilation": 0.0, "dateReglement": None, "modeReglement": None}

            # Recherche la ventilation
            req = """SELECT IDprestation, SUM(ventilation.montant), MIN(reglements.date), MIN(modes_reglements.label)
            FROM ventilation
            LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
            LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
            GROUP BY ventilation.IDprestation;"""
            DB.ExecuterReq(req)
            listeVentilations = DB.ResultatReq()
            for IDprestation, ventilation, dateReglement, modeReglement in listeVentilations:
                if IDprestation in dictFacturation:
                    dictFacturation[IDprestation]["ventilation"] = ventilation
                    dictFacturation[IDprestation]["dateReglement"] = dateReglement
                    dictFacturation[IDprestation]["modeReglement"] = modeReglement

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
            %s
            ORDER BY cotisations.date_saisie
            ;""" % conditions

        else:

            if self.IDindividu != None:
                # Pour une fiche individu
                if self.dictFamillesRattachees != None:
                    listeIDfamille = []
                    for IDfamille, dictFamille in self.dictFamillesRattachees.items():
                        if dictFamille["IDcategorie"] in (1, 2):
                            listeIDfamille.append(IDfamille)
                    if len(listeIDfamille) == 0:
                        conditionIDfamille = "()"
                    if len(listeIDfamille) == 1:
                        conditionIDfamille = "(%d)" % listeIDfamille[0]
                    else:
                        conditionIDfamille = str(tuple(listeIDfamille))
                else:
                    conditionIDfamille = "()"

                listeConditions.append("(cotisations.IDindividu=%d OR (cotisations.IDfamille IN %s AND cotisations.IDindividu IS NULL))" % (
                    self.IDindividu, conditionIDfamille))

                if len(listeConditions) > 0:
                    conditions = "WHERE %s" % " AND ".join(listeConditions)

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
                %s;
                """ % conditions
            else:
                # Pour une fiche famille
                req = """
                SELECT IDindividu, IDcategorie
                FROM rattachements 
                WHERE IDfamille=%d AND IDcategorie IN (1, 2);
                """ % self.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                listeIDindividus = []
                for IDindividu, IDcategorie in listeDonnees:
                    if IDindividu not in listeIDindividus:
                        listeIDindividus.append(IDindividu)
                if len(listeIDindividus) == 0:
                    conditionIndividus = "()"
                if len(listeIDindividus) == 1:
                    conditionIndividus = "(%d)" % listeIDindividus[0]
                else:
                    conditionIndividus = str(tuple(listeIDindividus))

                listeConditions.append("(cotisations.IDfamille=%d OR (cotisations.IDindividu IN %s AND cotisations.IDfamille IS NULL))" % (
                    self.IDfamille, conditionIndividus))

                if len(listeConditions) > 0:
                    conditions = "WHERE %s" % " AND ".join(listeConditions)

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
                %s
                """ % conditions

        DB.ExecuterReq(req)
        listeCotisations = DB.ResultatReq()

        DB.Close()

        listeListeView = []
        listeIDfamilles = []

        for item in listeCotisations:
            track = Track(self, item, dictFacturation)

            # Pour compter le nbre de familles
            IDfamille = item[1]
            if IDfamille not in listeIDfamilles and IDfamille != None:
                listeIDfamilles.append(IDfamille)

            valide = True

            # 2ème série de filtres
            if self.filtres != None:
                for filtre in self.filtres:

                    # Montant
                    if filtre["type"] == "montant":
                        montant = track.montant
                        if montant == None:
                            montant = 0.0
                        if self.ComparateurFiltre(montant, filtre["operateur"], filtre["montant"]) == False:
                            valide = False

                    # Solde actuel
                    if filtre["type"] == "solde_actuel":
                        solde = track.solde
                        if solde == None:
                            solde = 0.0
                        if self.ComparateurFiltre(solde, filtre["operateur"], filtre["montant"]) == False:
                            valide = False

                    # numero_intervalle
                    if filtre["type"] == "numero_intervalle":
                        if track.numero_int < filtre["numero_min"] or track.numero_int > filtre["numero_max"]:
                            valide = False

                    # numero_liste
                    if filtre["type"] == "numero_liste":
                        if track.numero_int not in filtre["liste"]:
                            valide = False

            if listeID != None:
                if item[0] not in listeID:
                    valide = False

            if valide == True:
                listeListeView.append(track)
                if self.selectionID == item[0]:
                    self.selectionTrack = track

        self.nbreFamilles = len(listeIDfamilles)

        return listeListeView

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur(
            "couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        # Préparation de la listeImages
        imgOk = self.AddNamedImages("ok", wx.Bitmap(
            Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        imgPasOk = self.AddNamedImages("pasok", wx.Bitmap(
            Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.imgVert = self.AddNamedImages("vert", wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG))

        def GetImageCreation(track):
            if track.date_creation_carte == None:
                return "pasok"
            else:
                return "ok"

        def GetImageDepot(track):
            if track.IDdepot_cotisation == None:
                return "pasok"
            else:
                return "ok"

        def FormateDate(dateDD):
            if dateDD == None:
                return ""
            if dateDD == "2999-01-01":
                return _(u"Illimitée")
            date = str(dateDD)
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text

        def GetImageVentilation(track):
            if track.montant == None:
                return None
            if track.montant == track.ventilation:
                return self.imgVert
            if track.ventilation == 0.0 or track.ventilation == None:
                return self.imgRouge
            if track.ventilation < track.montant:
                return self.imgOrange
            return self.imgRouge

        def FormateMontant(montant):
            if montant == None or montant == "":
                return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        def rowFormatter(listItem, track):
            if track.valide == False and self.mode != "liste":
                listItem.SetTextColour((180, 180, 180))

        dictColonnes = {
            "IDcotisation": ColumnDefn(u"", "left", 0, "IDcotisation", typeDonnee="entier"),
            "date_debut": ColumnDefn(u"Du", 'left', 80, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            "date_fin": ColumnDefn(_(u"Au"), 'left', 80, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            "date_saisie": ColumnDefn(_(u"Date saisie"), 'left', 80, "date_saisie", typeDonnee="date", stringConverter=FormateDate),
            "beneficiaires": ColumnDefn(_(u"Bénéficiaires de la cotisation"), 'left', 150, "beneficiaires", typeDonnee="texte"),
            "rue": ColumnDefn(_(u"Rue"), 'left', 120, "rue", typeDonnee="texte"),
            "cp": ColumnDefn(_(u"CP"), 'left', 70, "cp", typeDonnee="texte"),
            "ville": ColumnDefn(_(u"Ville"), 'left', 100, "ville", typeDonnee="texte"),
            "type": ColumnDefn(_(u"Type"), 'left', 110, "typeStr", typeDonnee="texte"),
            "nom": ColumnDefn(_(u"Nom de la cotisation"), 'left', 210, "nomCotisation", typeDonnee="texte"),
            "type_cotisation": ColumnDefn(_(u"Type de la cotisation"), 'left', 210, "nomTypeCotisation", typeDonnee="texte"),
            "unite_cotisation": ColumnDefn(_(u"Unité de la cotisation"), 'left', 90, "nomUniteCotisation", typeDonnee="texte"),
            "numero": ColumnDefn(_(u"Numéro de la cotisation"), 'left', 70, "numero", typeDonnee="texte"),
            "montant": ColumnDefn(_(u"Montant de la cotisation"), 'left', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            "regle": ColumnDefn(_(u"Réglé"), 'left', 70, "ventilation", typeDonnee="montant", stringConverter=FormateMontant),
            "date_reglement": ColumnDefn(_(u"Date règlement"), 'left', 80, "dateReglement", typeDonnee="date", stringConverter=FormateDate),
            "mode_reglement": ColumnDefn(_(u"Mode règlement"), 'left', 80, "modeReglement", typeDonnee="texte"),
            "solde": ColumnDefn(_(u"Solde"), 'left', 80, "solde", typeDonnee="montant", stringConverter=FormateMontant, imageGetter=GetImageVentilation),
            "date_creation_carte": ColumnDefn(_(u"Création carte"), 'left', 100, "date_creation_carte", typeDonnee="date", stringConverter=FormateDate, imageGetter=GetImageCreation),
            "depot_nom": ColumnDefn(_(u"Dépôt carte"), 'left', 100, "depotStr", typeDonnee="texte", imageGetter=GetImageDepot),
            "activites": ColumnDefn(_(u"Activités"), 'left', 150, "activitesStr", typeDonnee="texte"),
            "observations": ColumnDefn(_(u"Notes"), 'left', 150, "observations", typeDonnee="texte"),
        }

        self.rowFormatter = rowFormatter

        listeColonnes = []
        tri = None
        index = 0
        for codeColonne in self.codesColonnes:
            listeColonnes.append(dictColonnes[codeColonne])
            # Checkbox
            if codeColonne == self.triColonne:
                tri = index
            index += 1

        if self.mode == "liste":
            listeChamps = UTILS_Infos_individus.GetNomsChampsPossibles(
                mode="individu+famille")
            for titre, exemple, code in listeChamps:
                if u"n°" not in titre and "_x_" not in code:
                    typeDonnee = UTILS_Infos_individus.GetTypeChamp(code)
                    code = code.replace("{", "").replace("}", "")
                    listeColonnes.append(ColumnDefn(
                        titre, "left", 100, code, typeDonnee=typeDonnee, visible=False))
            self.SetColumns2(colonnes=listeColonnes,
                             nomListe="OL_Liste_cotisations")
        else:
            self.SetColumns(listeColonnes)

        if self.checkColonne == True:
            self.CreateCheckStateColumn(1)
        if tri != None:
            try:
                if self.checkColonne == True:
                    tri += 1
                self.SetSortColumn(self.columns[tri])
            except:
                pass

        self.SetEmptyListMsg(_(u"Aucune cotisation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetObjects(self.donnees)

    def MAJ(self, ID=None, labelParametres=""):
        self.labelParametres = labelParametres
        if ID != None:
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None:
            self.SelectObject(self.selectionTrack,
                              deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None

    def DefilePremier(self):
        if len(self.GetObjects()) > 0:
            self.EnsureCellVisible(0, 0)

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDcotisation

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        if self.mode != "liste":

            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath(
                "Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

            menuPop.AppendSeparator()

            # Item Modifier
            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            bmp = wx.Bitmap(Chemins.GetStaticPath(
                "Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
            if noSelection == True:
                item.Enable(False)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True:
            item.Enable(False)

        menuPop.AppendSeparator()

        # Item Imprimer cotisation
        item = wx.MenuItem(menuPop, 100, _(u"Imprimer la cotisation"))
        bmp = wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Reedition, id=100)
        if noSelection == True:
            item.Enable(False)

        # Item Envoyer la cotisation par Email
        item = wx.MenuItem(menuPop, 110, _(u"Envoyer la cotisation par Email"))
        bmp = wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=110)
        if noSelection == True:
            item.Enable(False)

        menuPop.AppendSeparator()

        # Item Recu Dons aux oeuvres
        item = wx.MenuItem(menuPop, 60, _(
            u"Editer un reçu Dons aux Oeuvres (PDF)"))
        bmp = wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.RecuCotisation, id=60)
        if noSelection == True:
            item.Enable(False)

        if self.mode == "liste":

            menuPop.AppendSeparator()

            # Item Ouvrir fiche famille
            item = wx.MenuItem(menuPop, 70, _(
                u"Ouvrir la fiche famille correspondante"))
            bmp = wx.Bitmap(Chemins.GetStaticPath(
                "Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=70)
            if noSelection == True:
                item.Enable(False)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(
            menuPop, dictParametres=self.GetParametresImpression())

        if self.mode == "liste":
            # Commandes standards
            self.AjouterCommandesMenuContext(menuPop)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre": _(u"Liste des cotisations"),
            "intro": self.GetTextesImpression()[0],
            "total": self.GetTextesImpression()[1],
            "orientation": wx.PORTRAIT,
        }
        return dictParametres

    def Reedition(self, event):
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation à imprimer !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcotisation = self.Selection()[0].IDcotisation
        from Utils import UTILS_Cotisations
        cotisation = UTILS_Cotisations.Cotisation()
        cotisation.Impression(listeCotisations=[IDcotisation,])

    def RecuCotisation(self, event):
        """ Imprimer dons aux oeuvres """
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation dans la liste !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcotisation = self.Selection()[0].IDcotisation
        from Dlg import DLG_Impression_don_oeuvres
        dlg = DLG_Impression_don_oeuvres.Dialog(
            self, IDcotisation=IDcotisation)
        if dlg.ShowModal() == wx.ID_OK:
            pass
        dlg.Destroy()

    def EnvoyerEmail(self, event):
        """ Envoyer la cotisation par Email """
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation à envoyer par Email !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Envoi du mail
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=track.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc(
            "COTISATION", "pdf"), categorie="cotisation")

    def CreationPDF(self, nomDoc="", afficherDoc=True):
        """ Création du PDF pour Email """
        IDcotisation = self.Selection()[0].IDcotisation
        from Utils import UTILS_Cotisations
        cotisation = UTILS_Cotisations.Cotisation()
        resultat = cotisation.Impression(
            listeCotisations=[IDcotisation,], nomDoc=nomDoc, afficherDoc=False)
        if resultat == False:
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[IDcotisation]

    def GetTextesImpression(self):
        total = _(u"%d cotisations. ") % len(self.donnees)
        if self.filtres != None:
            from Dlg.DLG_Filtres_cotisations import GetTexteFiltres
            intro = total + \
                _(u"Filtres de sélection : %s") % GetTexteFiltres(self.filtres)
        else:
            intro = None
        return intro, total

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def GetTracksTous(self):
        return self.donnees

    def Ajouter(self, event):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_cotisations", "creer") == False:
            return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_cotisations", "creer") == False:
            return

        # Vérifie que l'individu est rattaché comme REPRESENTANT ou ENFANT à une famille
        if self.dictFamillesRattachees != None:
            valide = False
            for IDfamille, dictFamille in self.dictFamillesRattachees.items():
                if dictFamille["IDcategorie"] in (1, 2):
                    valide = True
            if valide == False:
                dlg = wx.MessageDialog(self, _(u"Pour bénéficier d'une cotisation, un individu doit obligatoirement être\nrattaché comme représentant ou enfant à une fiche famille !"), _(
                    u"Création de cotisation impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Ouverture de la fenêtre de saisie d'une cotisation
        from Dlg import DLG_Saisie_cotisation
        dlg = DLG_Saisie_cotisation.Dialog(self, IDcotisation=None, IDfamille=self.IDfamille,
                                           IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)
        if dlg.ShowModal() == wx.ID_OK:
            IDcotisation = dlg.GetIDcotisation()
            self.MAJ(IDcotisation)
        dlg.Destroy()

    def Modifier(self, event):
        if self.mode == "liste":
            return

        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_cotisations", "modifier") == False:
            return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_cotisations", "modifier") == False:
            return
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation à modifier dans la liste !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        if self.gestion.Verification("cotisations", track.date_creation_carte) == False:
            return False

        from Dlg import DLG_Saisie_cotisation
        dlg = DLG_Saisie_cotisation.Dialog(self, IDcotisation=track.IDcotisation, IDfamille=self.IDfamille,
                                           IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDcotisation)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation à supprimer dans la liste !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.GetTracksCoches()) > 0:
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les %d cotisations cochées ?") % len(
                listeSelections), _(u"Suppression"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return

        else:
            # Suppression unique
            listeSelections = self.Selection()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la cotisation n°%s ?") %
                                   listeSelections[0].numero, _(u"Suppression"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return

        for track in listeSelections:
            # Vérifie les droits utilisateur
            if track.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_cotisations", "supprimer") == False:
                return
            if track.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_cotisations", "supprimer") == False:
                return
            # Vérifie les périodes gestion verrouillées
            if self.gestion.Verification("cotisations", track.date_creation_carte) == False:
                return False

        # Recherche si prestation déjà présente sur facture
        listeID = []
        for track in listeSelections:
            listeID.append(track.IDcotisation)
        if len(listeID) == 0:
            conditionIDcotisation = "()"
        if len(listeID) == 1:
            conditionIDcotisation = "(%d)" % listeID[0]
        else:
            conditionIDcotisation = str(tuple(listeID))

        DB = GestionDB.DB()
        req = """SELECT IDcotisation, prestations.date, MIN(IDfacture)
        FROM prestations
        LEFT JOIN cotisations ON cotisations.IDprestation = prestations.IDprestation
        WHERE IDcotisation IN %s
        GROUP BY cotisations.IDcotisation;""" % conditionIDcotisation
        DB.ExecuterReq(req)
        listeFactures = DB.ResultatReq()
        DB.Close()
        if len(listeFactures) > 0:
            nbreCotisations = 0
            for IDcotisation, date, IDfacture in listeFactures:
                if self.gestion.Verification("prestations", date) == False:
                    return False

                if IDfacture != None:
                    nbreCotisations += 1

            if nbreCotisations > 0:
                if nbreCotisations == 1:
                    message = _(
                        u"Cette cotisation apparaît déjà sur une facture. Il est donc impossible de la supprimer.")
                else:
                    message = _(u"%d de ces cotisations apparaissent déjà sur une ou plusieurs factures. Il est donc impossible d'effectuer la suppression.") % len(
                        listeFactures)
                dlg = wx.MessageDialog(self, message, _(
                    u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Suppression
        DB = GestionDB.DB()
        for track in listeSelections:
            DB.ReqDEL("cotisations", "IDcotisation", track.IDcotisation)
            if track.IDprestation != None:
                DB.ReqDEL("prestations", "IDprestation", track.IDprestation)

            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu": track.IDindividu,
                "IDfamille": track.IDfamille,
                "IDcategorie": 23,
                "action": _(u"Suppression de la cotisation ID%d '%s' pour la période du %s au %s") % (track.IDcotisation, track.nomCotisation, UTILS_Dates.DateEngFr(str(track.date_debut)), UTILS_Dates.DateEngFr(str(track.date_fin))),
            },])

            # Actualisation de l'affichage
            self.MAJ()

        DB.Close()
        dlg.Destroy()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False:
            return
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        IDcotisation = self.Selection()[0].IDcotisation
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDcotisation)
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, listview=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1),
                               style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False

        self.SetDescriptiveText(_(u"Rechercher une cotisation..."))
        self.ShowSearchButton(True)

        if listview != None:
            self.listView = listview
        else:
            self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(
            self.listView, self.listView.columns[0:nbreColonnes]))

        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))

        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()

    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()

    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh()


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "beneficiaires": {"mode": "nombre", "singulier": _(u"cotisation"), "pluriel": _(u"cotisations"), "alignement": wx.ALIGN_CENTER},
            "montant": {"mode": "total"},
            "ventilation": {"mode": "total"},
            "solde": {"mode": "total"},
        }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

# -------------------------------------------------------------------------------------------------------------------------------------------


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer_1)
        # mode = liste ou famille
        self.myOlv = ListView(panel, IDfamille=None, id=-1, mode="liste", triColonne="numero", checkColonne=True, codesColonnes=[
                              "IDcotisation", "beneficiaires", "date_saisie", "numero", "nom", "type_cotisation", "unite_cotisation", "montant", "solde", "activites", "observations"], name="OL_test", style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.myOlv.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL | wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()


if __name__ == '__main__':
    app = wx.App(0)
    # wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
