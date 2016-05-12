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
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import wx.lib.agw.hypertreelist as HTL
import datetime
import copy
import sys
import FonctionsPerso

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Utils import UTILS_Titulaires
import GestionDB
from Utils import UTILS_Organisateur
from Utils import UTILS_Utilisateurs

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal



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
        
def PeriodeComplete(mois, annee):
    listeMois = (_(u"Jan"), _(u"Fév"), _(u"Mars"), _(u"Avr"), _(u"Mai"), _(u"Juin"), _(u"Juil"), _(u"Août"), _(u"Sept"), _(u"Oct"), _(u"Nov"), _(u"Déc"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete

def ConvertStrToListe(texte=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None :
        return None
    listeResultats = []
    temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats




            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.dictImpression = {}
        
        # Paramètres
        self.mode_regroupement = "activites"      # "activite", "famille"
        self.mode_periode = "mois"                  # "mois", "annee"
        self.date_debut = None
        self.date_fin = None
        self.afficher_consommations = True
        self.afficher_cotisations = True
        self.afficher_autres = True
        self.listeActivites = []
        self.affichage_details = True

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
        
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | wx.TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
##        self.EnableSelectionVista(True)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)

        
    def Importation_activites(self):
        """ Récupération des noms des activités """
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()
        DB.Close()
        dictActivites = {}
        for IDactivite, nom, abrege in listeActivites :
            dictActivites[IDactivite] = {"nom" : nom, "abrege" : abrege}
        return dictActivites

    def Importation_prestations(self):
        """ Importation des données """
        DB = GestionDB.DB()

##        self.filtreCotisations = False
##        self.filtreCotisations_dateDebut = None
##        self.filtreCotisations_dateFin = None
        
        # Récupèration de la ventilation des prestations de la période
        conditionDepots = ""
        if self.filtreDepots == True and self.filtreDepots_dateDebut != None and self.filtreDepots_dateFin !=None :
            conditionDepots = " AND (depots.date>='%s' AND depots.date<='%s') " % (self.filtreDepots_dateDebut, self.filtreDepots_dateFin)
        
        conditionReglements = ""
        if self.filtreReglements == True and self.filtreReglements_dateDebut != None and self.filtreReglements_dateFin !=None :
            conditionReglements = " AND (reglements.date>='%s' AND reglements.date<='%s') " % (self.filtreReglements_dateDebut, self.filtreReglements_dateFin)
        
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
            if dictVentilation.has_key(IDprestation) == False :
                dictVentilation[IDprestation] = 0.0
            dictVentilation[IDprestation] += montantVentilation
            
        # Condition Afficher Cotisations et/ou Consommations ?
        listeAffichage = []
        if self.afficher_cotisations == True : listeAffichage.append("cotisation")
        if self.afficher_consommations == True : listeAffichage.append("consommation")
        if self.afficher_autres == True : listeAffichage.append("autre")
        
        if len(listeAffichage) == 0 : conditionAfficher = "categorie='xxxxxxx' "
        elif len(listeAffichage) == 1 : conditionAfficher = "categorie='%s'" % listeAffichage[0]
        else : conditionAfficher = "categorie IN %s" % str(tuple(listeAffichage))
                
        # Condition Activités affichées
        if len(self.listeActivites) == 0 : conditionActivites = "prestations.IDactivite=9999999"
        elif len(self.listeActivites) == 1 : conditionActivites = "prestations.IDactivite=%d" % self.listeActivites[0]
        else : conditionActivites = "prestations.IDactivite IN %s" % str(tuple(self.listeActivites))
        
        # Récupération de toutes les prestations de la période
        req = """SELECT IDprestation, date, categorie, label, montant, IDactivite, IDcategorie_tarif, IDcompte_payeur, IDfamille
        FROM prestations 
        WHERE date>='%s' AND date <='%s'
        AND %s AND (%s OR prestations.IDactivite IS NULL)
        ORDER BY date; """ % (self.date_debut, self.date_fin, conditionAfficher, conditionActivites)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        DB.Close()
        
        dictResultats = {"familles" : {}, "activites" : {} } # Stocke la version ACTIVITES et la version FAMILLES
        listePeriodes = []
        for IDprestation, date, categorie, label, montant, IDactivite, IDcategorie_tarif, IDcompte_payeur, IDfamille in listePrestations :
            date = DateEngEnDateDD(date)
            annee = date.year
            mois = date.month
            
            if self.mode_periode == "mois" :
                periode = (annee, mois)
            else :
                periode = annee
            
            if periode not in listePeriodes :
                listePeriodes.append(periode)
            
            if categorie == "cotisation" : 
                IDactivite = 888888
            if IDactivite == None : 
                IDactivite = 999999
            
            if dictVentilation.has_key(IDprestation) :
                solde = float(FloatToDecimal(montant) - FloatToDecimal(dictVentilation[IDprestation]))
            else :
                solde = montant

            # Regroupement par activités
            if dictResultats["activites"].has_key(IDactivite) == False :
                dictResultats["activites"][IDactivite] = {"total":0, "periodes":{}}
            if dictResultats["activites"][IDactivite]["periodes"].has_key(periode) == False :
                dictResultats["activites"][IDactivite]["periodes"][periode] = {"total":0, "familles":{}}
            if dictResultats["activites"][IDactivite]["periodes"][periode]["familles"].has_key(IDfamille) == False :
                dictResultats["activites"][IDactivite]["periodes"][periode]["familles"][IDfamille] = 0
            
            dictResultats["activites"][IDactivite]["total"] += solde
            dictResultats["activites"][IDactivite]["periodes"][periode]["total"] += solde
            dictResultats["activites"][IDactivite]["periodes"][periode]["familles"][IDfamille] += solde
            
            # Regroupement par familles
            if dictResultats["familles"].has_key(IDfamille) == False :
                dictResultats["familles"][IDfamille] = {"total":0, "periodes":{}}
            if dictResultats["familles"][IDfamille]["periodes"].has_key(periode) == False :
                dictResultats["familles"][IDfamille]["periodes"][periode] = {"total":0, "activites":{}}
            if dictResultats["familles"][IDfamille]["periodes"][periode]["activites"].has_key(IDactivite) == False :
                dictResultats["familles"][IDfamille]["periodes"][periode]["activites"][IDactivite] = 0
            
            dictResultats["familles"][IDfamille]["total"] += solde
            dictResultats["familles"][IDfamille]["periodes"][periode]["total"] += solde
            dictResultats["familles"][IDfamille]["periodes"][periode]["activites"][IDactivite] += solde
        
        return dictResultats, listePeriodes
    
    def CreationColonnes(self, listePeriodes=[]):
        """ Création des colonnes """
        # Création de la première colonne
        if self.mode_regroupement == "activites" :
            label = _(u"Activités")
        else :
            label = _(u"Familles")
        self.AddColumn(label)
        self.SetColumnWidth(0, 250)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
        
        # Création des colonnes périodes
        numColonne = 1
        for periode in listePeriodes :
            if self.mode_periode == "mois" :
                self.AddColumn(PeriodeComplete(periode[1], periode[0]))
            else :
                self.AddColumn(str(periode))
            self.SetColumnWidth(numColonne, 65)
            self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
            numColonne += 1
        
        # Création de la colonne Total
        self.AddColumn(_(u"Total"))
        self.SetColumnWidth(numColonne, 65)
        self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
        
    def MAJ(self):        
        # Importation des données
        dictActivites = self.Importation_activites() 
        dictResultats, listePeriodes = self.Importation_prestations() 
        
        self.dictImpression = { "entete" : [], "contenu" : [], "total" : [], "coloration" : [] }
        
        # Mémorisation des colonnes
        dictColonnes = {}
        index = 1
        if self.mode_regroupement == "activites" :
            label = _(u"Activités")
        else:
            label = _(u"Familles")
        self.dictImpression["entete"].append(label)
        for periode in listePeriodes :
            dictColonnes[periode] = index
            if self.mode_periode == "mois" :
                label = PeriodeComplete(periode[1], periode[0])
            else :
                label = str(periode)
            self.dictImpression["entete"].append(label)
            index += 1
        dictColonnes["total"] = index
        self.dictImpression["entete"].append(_(u"Total"))
        
        # Initialisation du CTRL
        self.RAZ() 
        self.CreationColonnes(listePeriodes) 
        self.root = self.AddRoot(_(u"Racine"))
    
        # Création des branches
        def GetNomActivite(IDactivite=None):
            if dictActivites.has_key(IDactivite) : return dictActivites[IDactivite]["nom"]
            if IDactivite == 888888 : return _(u"Cotisations")
            if IDactivite == 999999 : return _(u"Autres")
            return _(u"Activité inconnue")
        
        def GetNomFamille(IDfamille=None):
            if self.dictTitulaires.has_key(IDfamille) :
                return self.dictTitulaires[IDfamille]["titulairesSansCivilite"]
            else :
                return _(u"Famille ID%d") % IDfamille
        
        def GetLabels(mode="activites"):
            listeLabels = []
            if mode == "activites" :
                for IDactivite, dictActivite in dictResultats["activites"].iteritems() :
                    label = GetNomActivite(IDactivite)
                    if dictActivite["total"] != 0.0 :
                        listeLabels.append((label, IDactivite))
            else :
                for IDfamille, dictFamille in dictResultats["familles"].iteritems() :
                    label = GetNomFamille(IDfamille)
                    if dictFamille["total"] != 0.0 :
                        listeLabels.append((label, IDfamille))
            listeLabels.sort()
            return listeLabels
        
        
        # Branches de niveau 1
        listeLabels1 = GetLabels(self.mode_regroupement)
        for label1, ID1 in listeLabels1 :
            niveau1 = self.AppendItem(self.root, label1)
            if self.mode_regroupement == "familles" :
                self.SetPyData(niveau1, {"type" : "famille", "IDfamille" : ID1, "nom": label1})
            
            impressionLigne = [label1,] 
            if self.affichage_details == True :
                self.dictImpression["coloration"].append(len(self.dictImpression["contenu"]))
            
            # Colonnes périodes
            for periode in listePeriodes :
                if dictResultats[self.mode_regroupement][ID1]["periodes"].has_key(periode) :
                    valeur = dictResultats[self.mode_regroupement][ID1]["periodes"][periode]["total"]
                    if valeur == 0 :
                        texte = ""
                    else:
                        texte = u"%.2f %s" % (valeur, SYMBOLE)
                    self.SetItemText(niveau1, texte, dictColonnes[periode])
                    impressionLigne.append(texte)
                else:
                    impressionLigne.append("")
            
            # Colonne Total
            valeur = dictResultats[self.mode_regroupement][ID1]["total"]
            texte = u"%.2f %s" % (valeur, SYMBOLE)
            self.SetItemText(niveau1, texte, dictColonnes["total"])
            impressionLigne.append(texte)
            
            self.dictImpression["contenu"].append(impressionLigne)
            
            
            # ----------------- Branches de niveau 2 -------------
            if self.mode_regroupement == "activites" :
                mode2 = "familles"
            else :
                mode2 = "activites"

            listeLabels2 = []
            if self.mode_regroupement == "activites" :
                for periode, dictPeriode in dictResultats["activites"][ID1]["periodes"].iteritems() :
                    for IDfamille, impayes in dictPeriode["familles"].iteritems() :
                        if impayes > 0 :
                            label = GetNomFamille(IDfamille)
                            if (label, IDfamille) not in listeLabels2 :
                                listeLabels2.append((label, IDfamille))
            else :
                for periode, dictPeriode in dictResultats["familles"][ID1]["periodes"].iteritems() :
                    for IDactivite, impayes in dictPeriode["activites"].iteritems() :
                        if impayes > 0 :
                            label = GetNomActivite(IDactivite)
                            if (label, IDactivite) not in listeLabels2 :
                                listeLabels2.append((label, IDactivite))
            listeLabels2.sort()
                    
            for label2, ID2 in listeLabels2 :
                if self.affichage_details == True :
                    niveau2 = self.AppendItem(niveau1, label2)
                    if self.mode_regroupement == "activites" :
                        self.SetPyData(niveau2, {"type" : "famille", "IDfamille" : ID2, "nom": label2})
                    self.SetItemFont(niveau2, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    self.SetItemTextColour(niveau2, wx.Colour(160, 160, 160) )
                    impressionLigne = [label2,] 
                
                # Colonnes périodes
                totalLigne = 0.0
                for periode in listePeriodes :
                    texte = None
                    if dictResultats[self.mode_regroupement][ID1]["periodes"].has_key(periode) :
                        if dictResultats[self.mode_regroupement][ID1]["periodes"][periode][mode2].has_key(ID2) :
                            valeur = dictResultats[self.mode_regroupement][ID1]["periodes"][periode][mode2][ID2]
                            totalLigne += valeur
                            if valeur == 0 :
                                texte = ""
                            else:
                                texte = u"%.2f %s" % (valeur, SYMBOLE)
                            if self.affichage_details == True :
                                self.SetItemText(niveau2, texte, dictColonnes[periode])
                                impressionLigne.append(texte)
                    if texte == None and self.affichage_details == True : impressionLigne.append("")
                        
                # Colonne Total
                if self.affichage_details == True :
                    texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                    self.SetItemText(niveau2, texte, dictColonnes["total"])
                    impressionLigne.append(texte)
                    self.dictImpression["contenu"].append(impressionLigne)
        
        
        
        
        
        
        # ------------ Ligne Total --------------
        niveauTotal = self.AppendItem(self.root, _(u"Total"))
        self.SetItemBackgroundColour(niveauTotal, (150, 150, 150) )
        self.SetItemTextColour(niveauTotal, wx.Colour(255, 255, 255) )
        
        impressionLigne = [_(u"Total"),]
        
        dictTotal = {}
        totalPeriodes = {}
        
        if self.mode_regroupement == "activites" :
            for IDactivite, dictActivite in dictResultats["activites"].iteritems() :
                for periode, dictPeriode in dictActivite["periodes"].iteritems() :
                    if totalPeriodes.has_key(periode) == False :
                        totalPeriodes[periode] = 0.0
                    totalPeriodes[periode] += dictPeriode["total"]
        else :
            for IDfamille, dictFamille in dictResultats["familles"].iteritems() :
                for periode, dictPeriode in dictFamille["periodes"].iteritems() :
                    if totalPeriodes.has_key(periode) == False :
                        totalPeriodes[periode] = 0.0
                    totalPeriodes[periode] += dictPeriode["total"]
        
        totalLigne = 0.0
        for periode in listePeriodes :
            valeur = totalPeriodes[periode]
            totalLigne += valeur
            texte = u"%.2f %s" % (valeur, SYMBOLE)
            self.SetItemText(niveauTotal, texte, dictColonnes[periode])
            impressionLigne.append(texte)

        texte = u"%.2f %s" % (totalLigne, SYMBOLE)
        self.SetItemText(niveauTotal, texte, dictColonnes["total"])
        impressionLigne.append(texte)
        
        self.dictImpression["total"].append(impressionLigne)
        
##        if self.affichage_details == True :
##            
##            # Tri des catégories
##            listeCategories = []
##            for IDcategorie_tarif in dictTotal.keys() :
##                if IDcategorie_tarif == None : 
##                    nomCategorie = _(u"Sans catégorie")
##                else: 
##                    nomCategorie = u"%s - %s" % (dictCategoriesTarifs[IDcategorie_tarif]["nomActivite"], dictCategoriesTarifs[IDcategorie_tarif]["nomCategorie"])
##                listeCategories.append((nomCategorie, IDcategorie_tarif))
##            listeCategories.sort()
##            
##            for nomCategorie, IDcategorie_tarif in listeCategories :
##                niveauCategorie = self.AppendItem(niveauTotal, nomCategorie)
##                self.SetItemFont(niveauCategorie, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
##                self.SetItemTextColour(niveauCategorie, wx.Colour(120, 120, 120) )
##                self.SetItemBackgroundColour(niveauCategorie, (210, 210, 210) )
##                
##                impressionLigne = [nomCategorie,]
##                
##                totalLigne = 0.0
##                for periode in listePeriodes :
##                    texte = None
##                    if dictTotal.has_key(IDcategorie_tarif) :
##                        if dictTotal[IDcategorie_tarif].has_key(periode) :
##                            valeur = dictTotal[IDcategorie_tarif][periode]
##                            totalLigne += valeur
##                            if self.mode_affichage == "nbre" : 
##                                texte = str(int(valeur))
##                            else:
##                                texte = u"%.2f %s" % (valeur, SYMBOLE)
##                            self.SetItemText(niveauCategorie, texte, dictColonnes[periode])
##                            impressionLigne.append(texte)
##                    if texte == None : impressionLigne.append("")
##                
##                if self.mode_affichage == "nbre" : 
##                    texte = str(int(totalLigne))
##                else:
##                    texte = u"%.2f %s" % (totalLigne, SYMBOLE)
##                self.SetItemText(niveauCategorie, texte, dictColonnes["total"])
##                impressionLigne.append(texte)
##                
##                self.dictImpression["total"].append(impressionLigne)
        
        self.ExpandAllChildren(self.root)   
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
    
    def SetAffichageDetails(self, etat=True):
        self.affichage_details = etat

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
        nomDoc = FonctionsPerso.GenerationNomDoc("SYNTHESE_IMPAYES", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30, leftMargin=40, rightMargin=40)
        story = []
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeur_page-175, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Synthèse des impayés"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        titre = _(u"Synthèse des impayés")
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xls" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xls)|*.xls|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
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
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()
                
        # Export
        import pyExcelerator
        # Création d'un classeur
        wb = pyExcelerator.Workbook()
        # Création d'une feuille
        ws1 = wb.add_sheet(titre)
        # Remplissage de la feuille
        
        fntLabel = pyExcelerator.Font()
        fntLabel.name = 'Verdana'
        fntLabel.bold = True
        
        al = pyExcelerator.Alignment()
        al.horz = pyExcelerator.Alignment.HORZ_LEFT
        al.vert = pyExcelerator.Alignment.VERT_CENTER
        
        ar = pyExcelerator.Alignment()
        ar.horz = pyExcelerator.Alignment.HORZ_RIGHT
        ar.vert = pyExcelerator.Alignment.VERT_CENTER

        pat = pyExcelerator.Pattern()
        pat.pattern = pyExcelerator.Pattern.SOLID_PATTERN
        pat.pattern_fore_colour = 0x01F
        
        styleLabel = pyExcelerator.XFStyle()
        styleLabel.alignment = al
        styleLabel.pattern = pat
        
        styleTotal = pyExcelerator.XFStyle()
        styleTotal.alignment = al
        styleTotal.pattern = pat
        styleTotal.font.bold = True

        styleTotalNbre = pyExcelerator.XFStyle()
        styleTotalNbre.alignment = ar
        styleTotalNbre.pattern = pat
        styleTotalNbre.font.bold = True
        
##        styleEuros = pyExcelerator.XFStyle()
##        styleEuros.num_format_str = "#,##0.00 €"
##    
##        # Création des labels de colonnes
##        x = 0
##        y = 0
##        for valeur in self.dictImpression["entete"] :
##            ws1.write(x, y, valeur)
##            ws1.col(y).width = 3000
##            y += 1
##        ws1.col(0).width = 10000
##        
##        # Contenu
##        x = 1
##        y = 0
##        for ligne in self.dictImpression["contenu"] :
##            for valeur in ligne :
##                if x-1 in self.dictImpression["coloration"] :
##                    ws1.write(x, y, valeur, styleTotal)
##                else:
##                    ws1.write(x, y, valeur)
##                y += 1
##            x += 1
##            y = 0
##        
##        # Total
##        premiereLigne = True
##        for ligne in self.dictImpression["total"] :
##            for valeur in ligne :
##                if premiereLigne == True :
##                    ws1.write(x, y, valeur, styleTotal)
##                else:
##                    ws1.write(x, y, valeur)
##                y += 1
##            premiereLigne = False
##            x += 1
##            y = 0
##            
##        # Finalisation du fichier xls
##        wb.save(cheminFichier)

        styleEuros = pyExcelerator.XFStyle()
        styleEuros.num_format_str = '"$"#,##0.00_);("$"#,##'
        styleEuros.alignment = ar
        
        styleTotalEuros = pyExcelerator.XFStyle()
        styleTotalEuros.num_format_str = '"$"#,##0.00_);("$"#,##'
        styleTotalEuros.alignment = ar
        styleTotalEuros.pattern = pat
        styleTotalEuros.font.bold = True

        # Création des labels de colonnes
        x = 0
        y = 0
        for valeur in self.dictImpression["entete"] :
            ws1.write(x, y, valeur)
            ws1.col(y).width = 3000
            y += 1
        ws1.col(0).width = 10000
        
        def RechercheFormat(valeur, titre):
            """ Recherche si la valeur est un nombre """
            format = None
            if valeur.endswith(SYMBOLE) :
                # Si c'est un montant en euros
                try :
                    nbre = float(valeur[:-1]) 
                    if titre == True :
                        format = styleTotalEuros
                    else:
                        format = styleEuros
                    return (nbre, format)
                except :
                    pass
                    
            else:
                # Si c'est un nombre
                try :
                    nbre = float(valeur)
                    if titre == True :
                        format = styleTotalNbre
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
                    format = styleTotal

                # Enregistre la valeur
                if format != None :
                    ws1.write(x, y, valeur, format)
                else:
                    ws1.write(x, y, valeur)
                    
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
                    format = styleTotal

                # Enregistre la valeur
                if format != None :
                    ws1.write(x, y, valeur, format)
                else:
                    ws1.write(x, y, valeur)

                y += 1
            premiereLigne = False
            x += 1
            y = 0
            
        # Finalisation du fichier xls
        wb.save(cheminFichier)

        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None : return
        type = dictItem["type"]
        if type != "famille" : return
        nomFamille = dictItem["nom"]
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille de %s") % nomFamille)
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        type = dictItem["type"]
        if type != "famille" : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDfamille = dictItem["IDfamille"]
        
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ() 


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.ctrl_stats = CTRL(panel)
        
        self.ctrl_stats.date_debut = datetime.date(2013, 8, 1)
        self.ctrl_stats.date_fin = datetime.date(2013, 8, 31)
        self.ctrl_stats.afficher_consommations = True
        self.ctrl_stats.afficher_cotisations = True
        self.ctrl_stats.afficher_autres = True
        self.ctrl_stats.listeActivites = [1, 2, 3]
        self.ctrl_stats.mode_regroupement = "activites"
        self.ctrl_stats.mode_periode = "mois"
        self.ctrl_stats.MAJ() 
        
        self.choix1 = wx.Choice(panel, -1, choices = ["activites", "familles"])
        self.choix1.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix1, self.choix1)

        self.choix2 = wx.Choice(panel, -1, choices = ["mois", "annee"])
        self.choix2.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix2, self.choix2)

        self.bouton_imprimer = wx.BitmapButton(panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_stats, 1, wx.ALL|wx.EXPAND, 4)
        
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.choix1, 0, wx.ALL, 4)
        sizer_3.Add(self.choix2, 0, wx.ALL, 4)
        sizer_3.Add(self.bouton_imprimer, 0, wx.ALL, 4)
        
        sizer_2.Add(sizer_3, 0, wx.ALL, 0)
        
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
    
    def OnChoix1(self, event):
        self.ctrl_stats.mode_regroupement = self.choix1.GetStringSelection()
        self.ctrl_stats.MAJ() 

    def OnChoix2(self, event):
        self.ctrl_stats.mode_periode = self.choix2.GetStringSelection()
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
