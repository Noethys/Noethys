#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import os
import wx.lib.agw.hypertreelist as HTL
import datetime
import copy
import sys
import FonctionsPerso

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import UTILS_Organisateur
import GestionDB

try: import psyco; psyco.full()
except: pass



def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
def PeriodeComplete(mois, annee):
    listeMois = (u"Jan", u"Fév", u"Mars", u"Avr", u"Mai", u"Juin", u"Juil", u"Août", u"Sept", u"Oct", u"Nov", u"Déc")
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
        self.mode_affichage = "facture" # "facture", "regle", "nbre", "impaye"
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
                
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | wx.TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        
    def Importation_categories(self):
        """ Récupération des noms des catégories de tarifs """
        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, categories_tarifs.nom, activites.nom, activites.abrege
        FROM categories_tarifs
        LEFT JOIN activites ON activites.IDactivite = categories_tarifs.IDactivite
        ORDER BY categories_tarifs.nom; """
        DB.ExecuterReq(req)
        listeCategoriesTarifs = DB.ResultatReq()
        DB.Close()
        dictCategoriesTarifs = {}
        for IDcategorie_tarif, nomCategorie, nomActivite, abregeActivite in listeCategoriesTarifs :
            dictCategoriesTarifs[IDcategorie_tarif] = {
                "nomCategorie" : nomCategorie,
                "nomActivite" : nomActivite,
                "abregeActivite" : abregeActivite,
                }
        return dictCategoriesTarifs

    def Importation_prestations(self):
        """ Importation des données """
        DB = GestionDB.DB()

##        self.filtreCotisations = False
##        self.filtreCotisations_dateDebut = None
##        self.filtreCotisations_dateFin = None
        
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
        req = """SELECT IDprestation, date, categorie, label, montant, IDactivite, IDcategorie_tarif
        FROM prestations 
        WHERE date>='%s' AND date <='%s'
        AND %s AND (%s OR prestations.IDactivite IS NULL)
        ORDER BY date; """ % (self.date_debut, self.date_fin, conditionAfficher, conditionActivites)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        DB.Close()
        
        dictPrestations = {}
        listePeriodes = []
        for IDprestation, date, categorie, label, montant, IDactivite, IDcategorie_tarif in listePrestations :
            date = DateEngEnDateDD(date)
            annee = date.year
            mois = date.month
            periode = (annee, mois)
            
            if periode not in listePeriodes :
                listePeriodes.append(periode)
                
            # Total
            if dictPrestations.has_key(label) == False :
                dictPrestations[label] = {"nbre" : 0, "facture" : 0.0, "regle" : 0.0, "impaye" : 0.0, "periodes" : {} }
            dictPrestations[label]["nbre"] += 1
            dictPrestations[label]["facture"] += montant
            
            # Détail par période
            if dictPrestations[label]["periodes"].has_key(periode) == False :
                dictPrestations[label]["periodes"][periode] = {"nbre" : 0, "facture" : 0.0, "regle" : 0.0, "impaye" : 0.0, "categories" : {} }
            dictPrestations[label]["periodes"][periode]["nbre"] += 1
            dictPrestations[label]["periodes"][periode]["facture"] += montant
            
            # Détail par catégorie de tarifs
            if dictPrestations[label]["periodes"][periode]["categories"].has_key(IDcategorie_tarif) == False :
                dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif] = {"nbre" : 0, "facture" : 0.0, "regle" : 0.0, "impaye" : 0.0}
            dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif]["nbre"] += 1
            dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif]["facture"] += montant
            
            # Ajoute la ventilation
            if dictVentilation.has_key(IDprestation) :
                dictPrestations[label]["regle"] += dictVentilation[IDprestation]
                dictPrestations[label]["periodes"][periode]["regle"] += dictVentilation[IDprestation]
                dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif]["regle"] += dictVentilation[IDprestation]
            
            # Calcule les impayés
            dictPrestations[label]["impaye"] = dictPrestations[label]["regle"] - dictPrestations[label]["facture"]
            dictPrestations[label]["periodes"][periode]["impaye"] = dictPrestations[label]["periodes"][periode]["regle"] - dictPrestations[label]["periodes"][periode]["facture"]
            dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif]["impaye"] = dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif]["regle"] - dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif]["facture"]
            
        return dictPrestations, listePeriodes
    
    def CreationColonnes(self, listePeriodes=[]):
        """ Création des colonnes """
        # Création de la première colonne
        self.AddColumn(u"Prestations")
        self.SetColumnWidth(0, 250)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
        
        # Création des colonnes périodes
        numColonne = 1
        for annee, mois in listePeriodes :
            self.AddColumn(PeriodeComplete(mois, annee))
            self.SetColumnWidth(numColonne, 65)
            self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
            numColonne += 1
        
        # Création de la colonne Total
        self.AddColumn(u"Total")
        self.SetColumnWidth(numColonne, 65)
        self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
        
    def MAJ(self):        
        # Importation des données
        dictCategoriesTarifs = self.Importation_categories() 
        dictPrestations, listePeriodes = self.Importation_prestations() 
        self.dictImpression = { "entete" : [], "contenu" : [], "total" : [], "coloration" : [] }
        
        # Mémorisation des colonnes
        dictColonnes = {}
        index = 1
        self.dictImpression["entete"].append(u"Prestations")
        for periode in listePeriodes :
            dictColonnes[periode] = index
            self.dictImpression["entete"].append(PeriodeComplete(periode[1], periode[0]))
            index += 1
        dictColonnes["total"] = index
        self.dictImpression["entete"].append(u"Total")
        
        # Initialisation du CTRL
        self.RAZ() 
        self.CreationColonnes(listePeriodes) 
        self.root = self.AddRoot(u"Racine")
        
        # Création des branches
        
        # ------------------ Branches prestations -----------------
        listeLabels = []
        for label, dictLabel in dictPrestations.iteritems() :
            listeLabels.append(label)
        listeLabels.sort()
        
        for label in listeLabels :
            niveauPrestation = self.AppendItem(self.root, label)
            
            periodes = dictPrestations[label]["periodes"].keys()
            periodes.sort()
            
            impressionLigne = [label,] 
            if self.affichage_details == True :
                self.dictImpression["coloration"].append(len(self.dictImpression["contenu"]))
            
            # Colonnes périodes
            for periode in listePeriodes :
                if dictPrestations[label]["periodes"].has_key(periode) :
                    valeur = dictPrestations[label]["periodes"][periode][self.mode_affichage]
                    if self.mode_affichage == "nbre" : 
                        texte = str(int(valeur))
                    else:
                        texte = u"%.2f %s" % (valeur, SYMBOLE)
                    self.SetItemText(niveauPrestation, texte, dictColonnes[periode])
                    impressionLigne.append(texte)
                else:
                    impressionLigne.append("")
            
            # Colonne Total
            valeur = dictPrestations[label][self.mode_affichage]
            if self.mode_affichage == "nbre" : 
                texte = str(int(valeur))
            else:
                texte = u"%.2f %s" % (valeur, SYMBOLE)
            self.SetItemText(niveauPrestation, texte, dictColonnes["total"])
            impressionLigne.append(texte)
            
            self.dictImpression["contenu"].append(impressionLigne)
            
            # ----------------- Branches catégories -------------
            listeCategories = []
            for periode in periodes :
                for IDcategorie_tarif in dictPrestations[label]["periodes"][periode]["categories"].keys() :
                    if IDcategorie_tarif == None : 
                        nomCategorie = u"Sans catégorie"
                    else: 
                        nomCategorie = u"%s - %s" % (dictCategoriesTarifs[IDcategorie_tarif]["nomActivite"], dictCategoriesTarifs[IDcategorie_tarif]["nomCategorie"])
                    if (nomCategorie, IDcategorie_tarif) not in listeCategories :
                        listeCategories.append((nomCategorie, IDcategorie_tarif))
            listeCategories.sort()

            for nomCategorie, IDcategorie_tarif in listeCategories :
                if self.affichage_details == True :
                    niveauCategorie = self.AppendItem(niveauPrestation, nomCategorie)
                    self.SetItemFont(niveauCategorie, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    self.SetItemTextColour(niveauCategorie, wx.Colour(160, 160, 160) )
                    impressionLigne = [nomCategorie,] 
                
                # Colonnes périodes
                totalLigne = 0.0
                for periode in listePeriodes :
                    texte = None
                    if dictPrestations[label]["periodes"].has_key(periode) :
                        if dictPrestations[label]["periodes"][periode]["categories"].has_key(IDcategorie_tarif) :
                            valeur = dictPrestations[label]["periodes"][periode]["categories"][IDcategorie_tarif][self.mode_affichage]
                            totalLigne += valeur
                            if self.mode_affichage == "nbre" : 
                                texte = str(int(valeur))
                            else:
                                texte = u"%.2f %s" % (valeur, SYMBOLE)
                            if self.affichage_details == True :
                                self.SetItemText(niveauCategorie, texte, dictColonnes[periode])
                                impressionLigne.append(texte)
                    if texte == None and self.affichage_details == True : impressionLigne.append("")
                        
                # Colonne Total
                if self.affichage_details == True :
                    if self.mode_affichage == "nbre" : 
                        texte = str(int(totalLigne))
                    else:
                        texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                    self.SetItemText(niveauCategorie, texte, dictColonnes["total"])
                    impressionLigne.append(texte)
                    
                    self.dictImpression["contenu"].append(impressionLigne)
        
        # ------------ Ligne Total --------------
        niveauTotal = self.AppendItem(self.root, u"Total")
        self.SetItemBackgroundColour(niveauTotal, (150, 150, 150) )
        self.SetItemTextColour(niveauTotal, wx.Colour(255, 255, 255) )
        
        impressionLigne = [u"Total",]
        
        dictTotal = {}
        totalPeriodes = {}
        for label in listeLabels :
            for periode, dictPeriode in dictPrestations[label]["periodes"].iteritems() :
                for IDcategorie_tarif, dictCategories in dictPeriode["categories"].iteritems() :
                    if dictTotal.has_key(IDcategorie_tarif) == False :
                        dictTotal[IDcategorie_tarif] = {}
                    if dictTotal[IDcategorie_tarif].has_key(periode) == False :
                        dictTotal[IDcategorie_tarif][periode] = 0.0
                    dictTotal[IDcategorie_tarif][periode] += dictCategories[self.mode_affichage]
                
                    if totalPeriodes.has_key(periode) == False :
                        totalPeriodes[periode] = 0.0
                    totalPeriodes[periode] += dictCategories[self.mode_affichage]
        
        totalLigne = 0.0
        for periode in listePeriodes :
##        for periode, valeur in totalPeriodes.iteritems() :
            valeur = totalPeriodes[periode]
            totalLigne += valeur
            if self.mode_affichage == "nbre" : 
                texte = str(int(valeur))
            else:
                texte = u"%.2f %s" % (valeur, SYMBOLE)
            self.SetItemText(niveauTotal, texte, dictColonnes[periode])
            impressionLigne.append(texte)

        if self.mode_affichage == "nbre" : 
            texte = str(int(totalLigne))
        else:
            texte = u"%.2f %s" % (totalLigne, SYMBOLE)
        self.SetItemText(niveauTotal, texte, dictColonnes["total"])
        impressionLigne.append(texte)
        
        self.dictImpression["total"].append(impressionLigne)
        
        if self.affichage_details == True :
            
            # Tri des catégories
            listeCategories = []
            for IDcategorie_tarif in dictTotal.keys() :
                if IDcategorie_tarif == None : 
                    nomCategorie = u"Sans catégorie"
                else: 
                    nomCategorie = u"%s - %s" % (dictCategoriesTarifs[IDcategorie_tarif]["nomActivite"], dictCategoriesTarifs[IDcategorie_tarif]["nomCategorie"])
                listeCategories.append((nomCategorie, IDcategorie_tarif))
            listeCategories.sort()
            
            for nomCategorie, IDcategorie_tarif in listeCategories :
                niveauCategorie = self.AppendItem(niveauTotal, nomCategorie)
                self.SetItemFont(niveauCategorie, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                self.SetItemTextColour(niveauCategorie, wx.Colour(120, 120, 120) )
                self.SetItemBackgroundColour(niveauCategorie, (210, 210, 210) )
                
                impressionLigne = [nomCategorie,]
                
                totalLigne = 0.0
                for periode in listePeriodes :
                    texte = None
                    if dictTotal.has_key(IDcategorie_tarif) :
                        if dictTotal[IDcategorie_tarif].has_key(periode) :
                            valeur = dictTotal[IDcategorie_tarif][periode]
                            totalLigne += valeur
                            if self.mode_affichage == "nbre" : 
                                texte = str(int(valeur))
                            else:
                                texte = u"%.2f %s" % (valeur, SYMBOLE)
                            self.SetItemText(niveauCategorie, texte, dictColonnes[periode])
                            impressionLigne.append(texte)
                    if texte == None : impressionLigne.append("")
                
                if self.mode_affichage == "nbre" : 
                    texte = str(int(totalLigne))
                else:
                    texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                self.SetItemText(niveauCategorie, texte, dictColonnes["total"])
                impressionLigne.append(texte)
                
                self.dictImpression["total"].append(impressionLigne)
        
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
        nomDoc = "Temp/Synthese_prestations_%s.pdf" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=20, leftMargin=40, rightMargin=40)
        story = []
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeur_page-175, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (u"Situation financière", u"%s\nEdité le %s" % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        titre = u"Synthèse des prestations"
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xls" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xls)|*.xls|" \
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
        txtMessage = u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?"
        dlgConfirm = wx.MessageDialog(None, txtMessage, u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
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
        
        self.ctrl_stats.date_debut = datetime.date(2011, 3, 1)
        self.ctrl_stats.date_fin = datetime.date(2011, 7, 31)
        self.ctrl_stats.afficher_consommations = True
        self.ctrl_stats.afficher_cotisations = True
        self.ctrl_stats.listeActivites = [1, 2]
        self.ctrl_stats.mode_affichage = "facture"
        self.ctrl_stats.MAJ() 
        
        self.choix = wx.Choice(panel, -1, choices = ["facture", "regle", "impaye", "nbre"])
        self.choix.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.choix)
        
        self.bouton_imprimer = wx.BitmapButton(panel, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_stats, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.choix, 0, wx.ALL, 4)
        sizer_2.Add(self.bouton_imprimer, 0, wx.ALL, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
    
    def OnChoix(self, event):
        valeur = self.choix.GetStringSelection()
        self.ctrl_stats.mode_affichage = valeur
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
