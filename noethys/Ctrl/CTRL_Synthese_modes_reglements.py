#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import os
import wx.lib.agw.hypertreelist as HTL
import datetime
import copy
import sys
import FonctionsPerso

from Utils import UTILS_Organisateur
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import GestionDB




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
        
        # Importation des valeurs invariables
        self.dictActivites = self.ImportationActivites()
        self.dictModes = self.ImportationModes()

        # Paramètres
        self.mode = "saisis" # "saisis", "deposes"
        self.date_debut = None
        self.date_fin = None
        self.listeActivites = "toutes"
        self.filtres = []
        self.listeAnneesVentilation = [] 
        self.ventilation = None
        self.affichage_details = True
        self.labelParametres = ""
        
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
    
    def ImportationActivites(self):
        """ Importation des noms d'activités """
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        dictActivites = {}
        for IDactivite, nom, abrege in listeDonnees :
            dictActivites[IDactivite] = {"nom":nom, "abrege":abrege}
        return dictActivites
    
    def ImportationModes(self):
        """ Importation des noms des modes de règlements """
        DB = GestionDB.DB()
        req = """SELECT IDmode, label
        FROM modes_reglements;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        dictModes = {}
        for IDmode, label in listeDonnees :
            dictModes[IDmode] = {"nom":label}
        return dictModes
        
    def Importation(self):
        """ Importation des données """
        dictResultats = {}
        listeModes = []
        self.listeAnneesVentilation = [] 
        
        if len(self.filtres) == 0 :
            return dictResultats, listeModes
        
        DB = GestionDB.DB()
        
        # Conditions Règlements
        if self.mode == "saisis" :
            condition = " (reglements.date>='%s' and reglements.date<='%s') " % (self.date_debut, self.date_fin)
        if self.mode == "deposes" :
            condition = " (depots.date>='%s' and depots.date<='%s') " % (self.date_debut, self.date_fin)
        if self.mode == "nondeposes" :
            condition = " (depots.IDdepot IS NULL)"

        # Conditions Activités
        if self.listeActivites == "toutes" or self.listeActivites == None :
            conditionActivites = ""
        else :
            if len(self.listeActivites) == 0 : conditionActivites = "AND prestations.IDactivite IN ()"
            elif len(self.listeActivites) == 1 : conditionActivites = "AND prestations.IDactivite IN (%d)" % self.listeActivites[0]
            else : conditionActivites = "AND prestations.IDactivite IN %s" % str(tuple(self.listeActivites))
        
        # Filtres
        listeFiltres = []
        texteFiltres = ""
        if "consommation" in self.filtres : 
            listeFiltres.append("(prestations.categorie='consommation' %s)" % conditionActivites)
        if "cotisation" in self.filtres : 
            listeFiltres.append("(prestations.categorie='cotisation')")
        if "location" in self.filtres :
            listeFiltres.append("(prestations.categorie='location')")
        if "autre" in self.filtres : 
            listeFiltres.append("(prestations.categorie='autre')")
        if len(listeFiltres) > 0 :
            texteFiltres = "AND (%s)" % " OR ".join(listeFiltres)
        else :
            texteFiltres = " AND reglements.IDreglement=0"

        req = """SELECT 
        ventilation.IDventilation, ventilation.IDreglement, ventilation.IDprestation, ventilation.montant,
        reglements.date, reglements.date_saisie, reglements.IDmode, depots.date,
        prestations.date, prestations.label, prestations.IDactivite, prestations.categorie
        FROM ventilation
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN depots ON depots.IDdepot = reglements.IDdepot
        WHERE %s %s
        ORDER BY prestations.date; """ % (condition, texteFiltres)
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()
        
        self.listeAnneesVentilation = []
        for IDventilation, IDreglement, IDprestation, montantVentilation, dateReglement, dateSaisieReglement, IDmode, dateDepotReglement, datePrestation, labelPrestation, IDactivite, categoriePrestation in listeVentilation :
            datePrestation = DateEngEnDateDD(datePrestation)
            anneePrestation = datePrestation.year
            if anneePrestation not in self.listeAnneesVentilation :
                self.listeAnneesVentilation.append(anneePrestation)
            
            # Filtre ventilation
            valide = False
            if self.ventilation == None :
                valide = True
            elif self.ventilation == 0 :
                valide = False
            else :
                if type(self.ventilation) == list :
                    ventilation_debut, ventilation_fin = self.ventilation
                    if ventilation_debut != None and ventilation_fin != None :
                        if datePrestation >= ventilation_debut and datePrestation <= ventilation_fin :
                            valide = True
                else :
                    annee = self.ventilation
                    if anneePrestation == annee :
                        valide = True
            
            # Mémorisation
            if valide == True :
            
                if categoriePrestation == "cotisation" :
                    IDactivite = 99999
                
                if (IDactivite in dictResultats) == False :
                    dictResultats[IDactivite] = {}
                if (labelPrestation in dictResultats[IDactivite]) == False :
                    dictResultats[IDactivite][labelPrestation] = {}
                if (IDmode in dictResultats[IDactivite][labelPrestation]) == False :
                    dictResultats[IDactivite][labelPrestation][IDmode] = 0.0
                dictResultats[IDactivite][labelPrestation][IDmode] += montantVentilation
                
                if IDmode not in listeModes :
                    listeModes.append(IDmode) 
            
        
        # Recherche des règlements non ventilés
        if "avoir" in self.filtres and (self.ventilation == None or self.ventilation == 0) :
            
            req = """SELECT IDmode, SUM(montant)
            FROM reglements
            LEFT JOIN depots ON depots.IDdepot = reglements.IDdepot
            WHERE %s
            GROUP BY IDmode
            ; """ % condition
            DB.ExecuterReq(req)
            listeReglements = DB.ResultatReq()
            
            req = """SELECT IDmode, SUM(ventilation.montant)
            FROM ventilation
            LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
            LEFT JOIN depots ON depots.IDdepot = reglements.IDdepot
            WHERE %s
            GROUP BY IDmode
            ; """ % condition
            DB.ExecuterReq(req)
            listeVentiles = DB.ResultatReq()
            dictTemp = {}
            for IDmode, montant in listeVentiles :
                dictTemp[IDmode] = montant

            # Synthèse des non ventilés
            for IDmode, montant in listeReglements :
                
                if IDmode in dictTemp :
                    montantAvoir = montant - dictTemp[IDmode]
                else :
                    montantAvoir = montant
                
                if montantAvoir > 0.0 :
                    if (88888 in dictResultats) == False :
                        dictResultats[88888] = {"Avoirs" : {} }
                    if (IDmode in dictResultats[88888]["Avoirs"]) == False :
                        dictResultats[88888]["Avoirs"][IDmode] = 0.0
                    dictResultats[88888]["Avoirs"][IDmode] += montantAvoir

                    if IDmode not in listeModes :
                        listeModes.append(IDmode) 

        DB.Close() 
        return dictResultats, listeModes
    
    def GetVentilation(self):
        return self.listeAnneesVentilation
    
    def SetVentilation(self, ventilation=None):
        self.ventilation = ventilation
##        self.MAJ(mode=self.mode, date_debut=self.date_debut, date_fin=self.date_fin, listeActivites=self.listeActivites, filtres=self.filtres, ventilation=ventilation)
    
    def CreationColonnes(self, listeModes=[]):
        """ Création des colonnes """
        # Création de la première colonne
        self.AddColumn(_(u"Activités/Prestations"))
        self.SetColumnWidth(0, 250)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
        self.dictImpression["entete"].append(_(u"Activités/Prestations"))
        
        dictColonnes = {}
        numColonne = 1
        for label, IDmode in listeModes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, 95)
            self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
            dictColonnes[IDmode] = numColonne
            self.dictImpression["entete"].append(label)
            numColonne += 1
        
        # Création de la colonne Total
        self.AddColumn(_(u"Total"))
        self.SetColumnWidth(numColonne, 95)
        self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
        dictColonnes["total"] = numColonne
        self.dictImpression["entete"].append(_(u"Total"))
        
        return dictColonnes
        
    def MAJ(self, mode="saisis", date_debut=None, date_fin=None, listeActivites=[], filtres=[]):     
        self.mode = mode
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.listeActivites = listeActivites
        self.filtres = filtres
        
        # Affiche d'une fenêtre d'attente
        message = _(u"Calcul des données en cours... Veuillez patienter...")
        dlgAttente = wx.BusyInfo(message, None)
        if 'phoenix' not in wx.PlatformInfo:
            wx.Yield()

        # Importation des données
        dictResultats, listeModes = self.Importation()
        self.dictImpression = { "entete" : [], "contenu" : [], "total" : [], "coloration" : [] }

        # Tri des modes par ordre alphabétique
        listeModesAlpha = []
        for IDmode in listeModes :
            if IDmode in self.dictModes :
                label = self.dictModes[IDmode]["nom"]
            else :
                label = _(u"Mode inconnu")
            listeModesAlpha.append((label, IDmode))
        listeModesAlpha.sort() 

        # Initialisation du CTRL
        self.RAZ() 
        dictColonnes = self.CreationColonnes(listeModesAlpha) 
        self.root = self.AddRoot(_(u"Racine"))
        
        # Branches Activités
        listeLabels = []
        for IDactivite, dictActivite in dictResultats.items() :
            if IDactivite in self.dictActivites :
                nomActivite = self.dictActivites[IDactivite]["nom"]
            else :
                if IDactivite == 99999 :
                    nomActivite = _(u"Cotisations")
                elif IDactivite == 88888 :
                    nomActivite = _(u"Avoirs")
                else :
                    nomActivite = _(u"Activité inconnue")
            listeLabels.append((nomActivite, IDactivite, dictActivite))
        listeLabels.sort()
        
        for nomActivite, IDactivite, dictActivite in listeLabels :
            niveauActivite = self.AppendItem(self.root, nomActivite)
            #self.SetItemBold(niveauActivite)
            impressionLigne = [nomActivite,] 
            
            # Total par mode
            dictTotal = {}
            for labelPrestation, dictPrestation in dictActivite.items() :
                for IDmode, montant in dictPrestation.items() :
                    if (IDmode in dictTotal) == False :
                        dictTotal[IDmode] = 0.0
                    dictTotal[IDmode] += montant
            
            totalLigne = 0.0
            for labelMode, IDmode in listeModesAlpha :
                if IDmode in dictTotal :
                    montant = dictTotal[IDmode]
                    texte = u"%.2f %s" % (montant, SYMBOLE)
                    self.SetItemText(niveauActivite, texte, dictColonnes[IDmode])
                    totalLigne += montant
                    impressionLigne.append(texte)
                else :
                    impressionLigne.append("")
            
            # Total Ligne Activité
            texte = u"%.2f %s" % (totalLigne, SYMBOLE)
            self.SetItemText(niveauActivite, texte, dictColonnes["total"])
            impressionLigne.append(texte)
            
            self.dictImpression["contenu"].append(impressionLigne)
            
            # Branches Prestations
            listePrestations = []
            for labelPrestation, dictPrestation in dictActivite.items() :
                listePrestations.append((labelPrestation, dictPrestation))
            listePrestations.sort()
            
            if self.affichage_details == True :
                self.dictImpression["coloration"].append(len(self.dictImpression["contenu"])-1)
                
                for labelPrestation, dictPrestation in listePrestations :
                    niveauPrestation = self.AppendItem(niveauActivite, labelPrestation)
                    self.SetItemFont(niveauPrestation, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    self.SetItemTextColour(niveauPrestation, wx.Colour(160, 160, 160) )

                    impressionLigne = [labelPrestation,] 
                    
                    # Colonnes Modes
                    totalLigne = 0.0
                    for labelMode, IDmode in listeModesAlpha :
                        if IDmode in dictPrestation :
                            montant = dictPrestation[IDmode]
                            texte = u"%.2f %s" % (montant, SYMBOLE)
                            self.SetItemText(niveauPrestation, texte, dictColonnes[IDmode])
                            totalLigne += montant
                            impressionLigne.append(texte)
                        else :
                            impressionLigne.append("")
                            
                    # Total ligne Prestation
                    texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                    self.SetItemText(niveauPrestation, texte, dictColonnes["total"])
                    impressionLigne.append(texte)
                    
                    self.dictImpression["contenu"].append(impressionLigne)
                
        # ------------ Ligne Total --------------
        niveauTotal = self.AppendItem(self.root, _(u"Total"))
        self.SetItemBackgroundColour(niveauTotal, wx.Colour(150, 150, 150) )
        self.SetItemTextColour(niveauTotal, wx.Colour(255, 255, 255) )
        impressionLigne = [_(u"Total"),]
        
        totauxColonnes = {}
        for IDactivite, dictActivite in dictResultats.items() :
            for labelPrestation, dictPrestation in dictActivite.items() :
                for IDmode, montant in dictPrestation.items() :
                    if (IDmode in totauxColonnes) == False :
                        totauxColonnes[IDmode] = 0.0 
                    totauxColonnes[IDmode] += montant

        totalLigne = 0.0
        for labelMode, IDmode in listeModesAlpha :
            if IDmode in totauxColonnes :
                montant = totauxColonnes[IDmode]
                texte = u"%.2f %s" % (montant, SYMBOLE)
                self.SetItemText(niveauTotal, texte, dictColonnes[IDmode])
                totalLigne += montant
                impressionLigne.append(texte)
            else :
                impressionLigne.append("")
                
        # Total ligne Prestation
        texte = u"%.2f %s" % (totalLigne, SYMBOLE)
        self.SetItemText(niveauTotal, texte, dictColonnes["total"])
        impressionLigne.append(texte)
        
        self.dictImpression["total"].append(impressionLigne)
        self.ExpandAllChildren(self.root)   
        
        del dlgAttente
        
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
        nomDoc = FonctionsPerso.GenerationNomDoc("synthese_modes_reglements", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30, leftMargin=40, rightMargin=40)
        story = []
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeur_page-175, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Synthèse des modes de règlements"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        titre = _(u"Synthèse des modes de règlements")
        
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
        feuille = classeur.add_worksheet()
        
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
        self.ctrl_stats.MAJ(mode="saisis", date_debut = datetime.date(2011, 3, 1), date_fin = datetime.date(2012, 7, 31), listeActivites = "toutes", filtres=["cotisation", "consommation", "autre", "avoir"]) 
        
        self.choix = wx.Choice(panel, -1, choices = ["facture", "regle", "impaye", "nbre"])
        self.choix.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.choix)
        
        self.bouton_imprimer = wx.BitmapButton(panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
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
##        self.ctrl_stats.Imprimer() 
        self.ctrl_stats.ExportExcel() 
        

if __name__ == '__main__':    
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
