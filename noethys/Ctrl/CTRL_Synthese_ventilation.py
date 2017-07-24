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
from Utils import UTILS_Organisateur
from Utils import UTILS_Divers
from Utils import UTILS_Dates
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import GestionDB

from Dlg import DLG_Options_impression_pdf
import wx.propgrid as wxpg


def PeriodeComplete(mois, annee):
    listeMois = (_(u"Jan"), _(u"Fév"), _(u"Mars"), _(u"Avr"), _(u"Mai"), _(u"Juin"), _(u"Juil"), _(u"Août"), _(u"Sept"), _(u"Oct"), _(u"Nov"), _(u"Déc"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete





class CTRL_Parametres(DLG_Options_impression_pdf.CTRL_Parametres):
    def __init__(self, parent):
        DLG_Options_impression_pdf.CTRL_Parametres.__init__(self, parent)

    def Remplissage(self):
        # --------------------------- COULEURS DE FOND ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Couleurs de fond")) )

        # Couleur 3
        propriete = wxpg.ColourProperty(label=_(u"Fond ligne entêtes"), name="couleur_fond_entetes", value=wx.Colour(204, 204, 255))
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur 1
        propriete = wxpg.ColourProperty(label=_(u"Fond ligne dépôt"), name="couleur_fond_depot", value=wx.Colour(230, 230, 255))
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur 2
        propriete = wxpg.ColourProperty(label=_(u"Fond ligne total"), name="couleur_fond_total", value=wx.Colour(204, 204, 255))
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- TEXTE ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Texte")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte", "SpinCtrl")

        # --------------------------- COLONNES ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Colonnes")) )

        # Largeur colonne labels
        propriete = wxpg.IntProperty(label=_(u"Largeur colonne label"), name="largeur_colonne_labels", value=170)
        propriete.SetHelpString(_(u"Saisissez la largeur pour la colonne label (170 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_labels", "SpinCtrl")

        # Largeur colonne valeurs
        propriete = wxpg.IntProperty(label=_(u"Largeur colonne valeur"), name="largeur_colonne_valeurs", value=45)
        propriete.SetHelpString(_(u"Saisissez la largeur pour la colonne valeur (45 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_valeurs", "SpinCtrl")



class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.dictImpression = {}
        
        # Paramètres
        self.mode_affichage = "mois" # "mois", "annee"
        self.affichage_details = True
        self.type = "depots"
        self.date_debut = None
        self.date_fin = None
        self.listeActivites = []
        self.listeDepots = []
        
##        # Création de l'ImageList
##        il = wx.ImageList(16, 16)
##        self.img_ok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Ok.png'), wx.BITMAP_TYPE_PNG))
##        self.img_pasok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Interdit.png'), wx.BITMAP_TYPE_PNG))
##        self.AssignImageList(il)
        
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
    
    def SetModeAffichage(self, mode="depots"):
        self.mode_affichage = mode
    
    def SetAffichageDetails(self, etat=True):
        self.affichage_details = etat
        
    def SetTypeDepots(self, listeDepots=[]):
        self.type = "depots"
        self.listeDepots = listeDepots
        
    def SetTypePrestations(self, date_debut=None, date_fin=None, listeActivites=[]):
        self.type = "prestations"
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.listeActivites = listeActivites

    def SetTypeVide(self):
        self.type = "vide"

    def Importation_depots(self):
        """ Importation des données """
        DB = GestionDB.DB()
        
        if len(self.listeDepots) == 0 : conditionDepots = "()"
        elif len(self.listeDepots) == 1 : conditionDepots = "(%d)" % self.listeDepots[0]
        else : conditionDepots = str(tuple(self.listeDepots))
        
        req = """SELECT depots.IDdepot, depots.date, nom, verrouillage, depots.IDcompte,
        SUM(reglements.montant)
        FROM depots
        LEFT JOIN reglements ON reglements.IDdepot = depots.IDdepot
        WHERE depots.IDdepot IN %s
        GROUP BY depots.IDdepot
        ORDER BY depots.date
        ;""" % conditionDepots
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDepots = {}
        for IDdepot, date, nom, verrouillage, IDcompte, montantTotal in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if montantTotal == None : montantTotal = 0.0
            dictDepots[IDdepot] = {"date":date, "nom":nom, "verrouillage":verrouillage, "IDcompte":IDcompte, "montantTotal":montantTotal}
        
        DB.Close() 
        return dictDepots

    def Importation_ventilation(self):
        """ Importation des données """
        DB = GestionDB.DB()
        
        if self.type == "depots" :
            # Type Dépôts
            if len(self.listeDepots) == 0 : condition = "depots.IDdepot IN ()"
            elif len(self.listeDepots) == 1 : condition = "depots.IDdepot IN (%d)" % self.listeDepots[0]
            else : condition = "depots.IDdepot IN %s" % str(tuple(self.listeDepots))
        else:
            # Type Prestations
            if len(self.listeActivites) == 0 : conditionActivites = ""
            elif len(self.listeActivites) == 1 : conditionActivites = "AND prestations.IDactivite=%d" % self.listeActivites[0]
            else : conditionActivites = "AND prestations.IDactivite IN %s" % str(tuple(self.listeActivites))
            condition = "prestations.date>='%s' AND prestations.date<='%s' %s" % (self.date_debut, self.date_fin, conditionActivites)
                            
        # Récupèration de la ventilation des prestations des dépôts
        req = """SELECT 
        ventilation.IDventilation, ventilation.IDreglement, ventilation.IDprestation, ventilation.montant,
        reglements.date, reglements.date_saisie, depots.IDdepot, depots.date,
        prestations.date, prestations.label, prestations.IDactivite, activites.nom, activites.abrege
        FROM ventilation
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN depots ON depots.IDdepot = reglements.IDdepot
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        WHERE %s
        ORDER BY prestations.date; """ % condition
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()
        dictVentilation = {}
        listePeriodes = []
        dictIDreglements = {}
        for IDventilation, IDreglement, IDprestation, montantVentilation, dateReglement, dateSaisieReglement, IDdepot, dateDepotReglement, datePrestation, labelPrestation, IDactivite, nomActivite, abregeActivite in listeVentilation :
            dateReglement = UTILS_Dates.DateEngEnDateDD(dateReglement)
            dateSaisieReglement = UTILS_Dates.DateEngEnDateDD(dateSaisieReglement)
            dateDepotReglement = UTILS_Dates.DateEngEnDateDD(dateDepotReglement)
            datePrestation = UTILS_Dates.DateEngEnDateDD(datePrestation)
            
            # Compte le nombre de règlements dans chaque dépôt
            if dictIDreglements.has_key(IDdepot) == False :
                dictIDreglements[IDdepot] = []
            if IDreglement not in dictIDreglements[IDdepot] :
                dictIDreglements[IDdepot].append(IDreglement)
            
            # Rajoute le nom de l'activité dans le label de la prestation
            if nomActivite != None :
                labelPrestation = u"%s - %s" % (nomActivite, labelPrestation)
            
            # Retient la période de ventilation
            if datePrestation != None :
                annee = datePrestation.year
                mois = datePrestation.month
                if self.mode_affichage == "mois" :
                    periode = (annee, mois)
                else:
                    periode = annee
                
                if periode not in listePeriodes :
                    listePeriodes.append(periode)
                    
                if dictVentilation.has_key(IDdepot) == False :
                    dictVentilation[IDdepot] = {}
                if dictVentilation[IDdepot].has_key(periode) == False :
                    dictVentilation[IDdepot][periode] = {}
                if dictVentilation[IDdepot][periode].has_key(labelPrestation) == False :
                    dictVentilation[IDdepot][periode][labelPrestation] = 0.0
                dictVentilation[IDdepot][periode][labelPrestation] += montantVentilation
        
        DB.Close() 
        listePeriodes.sort()
        
        return dictVentilation, listePeriodes, dictIDreglements
    
    def CreationColonnes(self, listePeriodes=[]):
        """ Création des colonnes """
        # Création de la première colonne
        self.AddColumn(_(u"Dépôts"))
        self.SetColumnWidth(0, 270)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
        
        # Création des colonnes périodes
        numColonne = 1
        if self.mode_affichage == "mois" :
            # Mode affichage MOIS
            for annee, mois in listePeriodes :
                self.AddColumn(PeriodeComplete(mois, annee))
                self.SetColumnWidth(numColonne, 65)
                self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
                numColonne += 1
        else:
            # Mode affichage ANNEE
            for annee in listePeriodes :
                self.AddColumn(str(annee))
                self.SetColumnWidth(numColonne, 65)
                self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
                numColonne += 1

        # Création de la colonne Non Ventilé
        if self.type == "depots" :
            self.AddColumn(_(u"Non ventilé"))
            self.SetColumnWidth(numColonne, 65)
            self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
            numColonne += 1

        # Création de la colonne Total
        self.AddColumn(_(u"Total"))
        self.SetColumnWidth(numColonne, 75)
        self.SetColumnAlignment(numColonne, wx.ALIGN_CENTRE)
        
    def MAJ(self):        
        """ Remplissage du ctrl """
        if self.type == "vide" :
            self.RAZ()
            return

        # Importation des données
        dictVentilation, listePeriodes, dictIDreglements = self.Importation_ventilation() 
        if self.type == "prestations" :
            self.listeDepots = dictVentilation.keys()
            if None in self.listeDepots : self.listeDepots.remove(None)
        dictDepots = self.Importation_depots()
        
        # Si on est en type PRESTATIONS, on crée un dépôt virtuel pour les règlements non déposées
        if self.type == "prestations" and dictVentilation.has_key(None) :
            dictDepots[None] = {"date":datetime.date(1977, 1, 1), "nom":_(u"----- %d règlements non déposés -----") % len(dictIDreglements[None]), "verrouillage":False, "IDcompte":None, "montantTotal":0.0}
        
        self.dictImpression = { "entete" : [], "contenu" : [], "total" : [], "coloration" : [] }
        
        # Mémorisation des colonnes
        dictColonnes = {}
        index = 1
        self.dictImpression["entete"].append(_(u"Dépôts"))
        for periode in listePeriodes :
            dictColonnes[periode] = index
            if self.mode_affichage == "mois" :
                label = PeriodeComplete(periode[1], periode[0])
            else:
                label = str(periode)
            self.dictImpression["entete"].append(label)
            index += 1
        if self.type == "depots" :
            dictColonnes["sansVentilation"] = index
            self.dictImpression["entete"].append(_(u"Non ventilé"))
            index += 1
        dictColonnes["total"] = index
        self.dictImpression["entete"].append(_(u"Total"))
        
        # Initialisation du CTRL
        self.RAZ() 
        self.CreationColonnes(listePeriodes) 
        self.root = self.AddRoot(_(u"Racine"))
    
        # Création des branches
        
        # ------------------ Branches DEPOTS -----------------
        
        # Tri des dépôts par date de dépôt
        listeDepotsTemp = []
        for IDdepot, dictDepot in dictDepots.iteritems() :
            if dictDepot["date"] == None :
                dateDepot = datetime.date(1977, 1, 1)
            else:
                dateDepot = dictDepot["date"] 
            listeDepotsTemp.append( (dateDepot, IDdepot, dictDepot) )
        listeDepotsTemp.sort()
        
        dictLigneTotal = {}
        totalSansVentilation = 0.0
        
        for dateDepot, IDdepot, dictDepot in listeDepotsTemp :
            if dateDepot == datetime.date(1977, 1, 1) : 
                dateStr = _(u"Sans date de dépôt")
            else:
                dateStr = u"%02d/%02d/%04d" % (dateDepot.day, dateDepot.month, dateDepot.year)
            label = u"%s (%s - %.2f %s)" % (dictDepot["nom"], dateStr, dictDepot["montantTotal"], SYMBOLE)
            if IDdepot == None : label = dictDepot["nom"]
            niveauDepot = self.AppendItem(self.root, label)
                        
            impressionLigne = [label,] 
            if self.affichage_details == True :
                self.dictImpression["coloration"].append(len(self.dictImpression["contenu"]))
                        
            # Colonnes périodes
            totalLigne = 0.0
            for periode in listePeriodes :
                if dictVentilation.has_key(IDdepot) and dictVentilation[IDdepot].has_key(periode) :
                    valeur = 0.0
                    for labelPrestation, montantVentilation in dictVentilation[IDdepot][periode].iteritems() : 
                        valeur += montantVentilation
                    totalLigne += valeur
                    texte = u"%.2f %s" % (valeur, SYMBOLE)
                    self.SetItemText(niveauDepot, texte, dictColonnes[periode])
                    impressionLigne.append(texte)
                else:
                    impressionLigne.append("")
                           
            # Colonne NON VENTILE
            if self.type == "depots" :
                totalDepot = dictDepots[IDdepot]["montantTotal"]
                sansVentilation = totalDepot - totalLigne
                if sansVentilation != 0.0 :
                    totalLigne += sansVentilation
                    totalSansVentilation += sansVentilation
                    texte = u"%.2f %s" % (sansVentilation, SYMBOLE)
                    self.SetItemText(niveauDepot, texte, dictColonnes["sansVentilation"])
                    impressionLigne.append(texte)
                else:
                    impressionLigne.append(u"")

            # Colonne Total
            texte = u"%.2f %s" % (totalLigne, SYMBOLE)
            self.SetItemText(niveauDepot, texte, dictColonnes["total"])
            impressionLigne.append(texte)
            
            self.dictImpression["contenu"].append(impressionLigne)
            
            # ----------------- Branches LABELS DE PRESTATIONS -------------
                
            listeLabelsPrestations = []
            for periode in listePeriodes :
                if dictVentilation.has_key(IDdepot) :
                    if dictVentilation[IDdepot].has_key(periode) :
                        for labelPrestation, montantVentilation in dictVentilation[IDdepot][periode].iteritems() : 
                            if labelPrestation not in listeLabelsPrestations :
                                listeLabelsPrestations.append(labelPrestation)
            listeLabelsPrestations.sort()

            for labelPrestation in listeLabelsPrestations :
                if self.affichage_details == True :
                    niveauPrestation = self.AppendItem(niveauDepot, labelPrestation)
                    self.SetItemFont(niveauPrestation, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    self.SetItemTextColour(niveauPrestation, wx.Colour(160, 160, 160) )
                    impressionLigne = [labelPrestation,] 
                
                # Colonnes périodes
                totalLigne = 0.0
                for periode in listePeriodes :
                    texte = None
                    if dictVentilation.has_key(IDdepot) :
                        if dictVentilation[IDdepot].has_key(periode) :
                            if dictVentilation[IDdepot][periode].has_key(labelPrestation) :
                                valeur = dictVentilation[IDdepot][periode][labelPrestation]
                                totalLigne += valeur
                                if dictLigneTotal.has_key(labelPrestation) == False :
                                    dictLigneTotal[labelPrestation] = {}
                                if dictLigneTotal[labelPrestation].has_key(periode) == False :
                                    dictLigneTotal[labelPrestation][periode] = 0.0
                                dictLigneTotal[labelPrestation][periode] += valeur
                                if self.affichage_details == True :
                                    texte = u"%.2f %s" % (valeur, SYMBOLE)
                                    self.SetItemText(niveauPrestation, texte, dictColonnes[periode])
                                    impressionLigne.append(texte)
                    if texte == None and self.affichage_details == True : impressionLigne.append("")
                
                # Colonne Non ventilé
                if self.type == "depots" and self.affichage_details == True :
                    impressionLigne.append(u"")
                
                # Colonne Total
                if self.affichage_details == True :
                    texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                    self.SetItemText(niveauPrestation, texte, dictColonnes["total"])
                    impressionLigne.append(texte)
                
                    self.dictImpression["contenu"].append(impressionLigne)
        
        # ------------ Ligne Total --------------
        niveauTotal = self.AppendItem(self.root, _(u"Total"))
        self.SetItemBackgroundColour(niveauTotal, wx.Colour(150, 150, 150) )
        self.SetItemTextColour(niveauTotal, wx.Colour(255, 255, 255) )
        
        impressionLigne = [_(u"Total"),]
        
        listeLabels = dictLigneTotal.keys()
        listeLabels.sort()
        
        # Ligne de TOTAL pour chaque PERIODE
        totalLigne = 0.0
        for periode in listePeriodes :
            totalColonne = 0.0
            for dateDepot, IDdepot, dictDepot in listeDepotsTemp :
                for label in listeLabels :
                    if dictVentilation.has_key(IDdepot) :
                        if dictVentilation[IDdepot].has_key(periode):
                            if dictVentilation[IDdepot][periode].has_key(label):
                                valeur = dictVentilation[IDdepot][periode][label]
                                totalColonne += valeur
            texte = u"%.2f %s" % (totalColonne, SYMBOLE)
            totalLigne += totalColonne
            self.SetItemText(niveauTotal, texte, dictColonnes[periode])
            impressionLigne.append(texte)
        
        # Total SANS VENTILATION
        if self.type == "depots" :
            texte = u"%.2f %s" % (totalSansVentilation, SYMBOLE)
            totalLigne += totalSansVentilation
            self.SetItemText(niveauTotal, texte, dictColonnes["sansVentilation"])
            impressionLigne.append(texte)
        
        # Total de la ligne de Total
        texte = u"%.2f %s" % (totalLigne, SYMBOLE)
        self.SetItemText(niveauTotal, texte, dictColonnes["total"])
        impressionLigne.append(texte)
        
        self.dictImpression["total"].append(impressionLigne)
        
        # Total des colonnes par label de prestation
        if self.affichage_details == True :
        
            for label in listeLabels :
                niveauPrestation = self.AppendItem(niveauTotal, label)
                self.SetItemFont(niveauPrestation, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                self.SetItemTextColour(niveauPrestation, wx.Colour(120, 120, 120) )
                self.SetItemBackgroundColour(niveauPrestation, wx.Colour(210, 210, 210) )
                
                impressionLigne = [label,]
                
                totalLigne = 0.0
                for periode in listePeriodes :
                    texte = None
                    if dictLigneTotal.has_key(label):
                        if dictLigneTotal[label].has_key(periode) :
                            valeur = dictLigneTotal[label][periode]
                            totalLigne += valeur
                            texte = u"%.2f %s" % (valeur, SYMBOLE)
                            self.SetItemText(niveauPrestation, texte, dictColonnes[periode])
                            impressionLigne.append(texte)
                    if texte == None : impressionLigne.append(u"")
                
                # Colonne None ventilé
                if self.type == "depots" :
                    impressionLigne.append(u"")
                
                # Colonne Total
                texte = u"%.2f %s" % (totalLigne, SYMBOLE)
                self.SetItemText(niveauPrestation, texte, dictColonnes["total"])
                impressionLigne.append(texte)
                
                self.dictImpression["total"].append(impressionLigne)
        
        self.ExpandAllChildren(self.root)   
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
    
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
        dlg = DLG_Options_impression_pdf.Dialog(self, categorie="synthese_ventilation", ctrl=CTRL_Parametres)
        if dlg.ShowModal() == wx.ID_OK:
            dictOptions = dlg.GetOptions()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return

        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        
        hauteur_page = A4[0]
        largeur_page = A4[1]
            
        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("STATS_VENTILATION", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30)
        story = []
        
        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (largeur_page-175, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Analyse croisée ventilation/dépôts"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
            story.append(Spacer(0,20))       
        
        # Insère un header
        Header() 
        
        # Tableau
        dataTableau = []
        largeursColonnes = [dictOptions["largeur_colonne_labels"],]
        for x in range(0, len(self.dictImpression["entete"])-1):
            largeursColonnes.append(dictOptions["largeur_colonne_valeurs"])
        
        # Entetes labels
        dataTableau.append(self.dictImpression["entete"])

        paraNormal = ParagraphStyle(name="normal", fontName="Helvetica", fontSize=dictOptions["taille_texte"], spaceAfter=0, leading=dictOptions["taille_texte"]+1, spaceBefore=0)
        paraTitre = ParagraphStyle(name="titre", fontName="Helvetica-Bold", fontSize=dictOptions["taille_texte"], spaceAfter=0, leading=dictOptions["taille_texte"]+1, spaceBefore=0)

        # Contenu du tableau
        listeRubriques = ("contenu", "total")
        for rubrique in listeRubriques :
            listeLignes = self.dictImpression[rubrique]

            indexLigne = 0
            for ligne in listeLignes :
                ligneTemp = []
                indexColonne = 0
                for texte in ligne :

                    # Aligne à droite les montants
                    if indexColonne > 0 :
                        texte = _(u"<para align='right'>%s</para>") % texte

                    case = Paragraph(texte, paraNormal)

                    # Ligne de titre
                    if rubrique == "contenu" and indexLigne in self.dictImpression["coloration"] :
                        case = Paragraph(texte, paraTitre)

                    ligneTemp.append(case)
                    indexColonne += 1

                dataTableau.append(ligneTemp)
                indexLigne += 1
        
        positionLigneTotal = len(self.dictImpression["contenu"]) + 1
        listeStyles = [
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
            ('FONT',(0,0),(-1,-1), "Helvetica", dictOptions["taille_texte"]), # Donne la police de caract. + taille de police
            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
            ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Centre les cases
            ('BACKGROUND', (0,0), (-1,0), UTILS_Divers.ConvertCouleurWXpourPDF(dictOptions["couleur_fond_entetes"]) ), # Donne la couleur de fond du label
            ('BACKGROUND', (0, positionLigneTotal), (-1, positionLigneTotal), UTILS_Divers.ConvertCouleurWXpourPDF(dictOptions["couleur_fond_total"]) ), # Donne la couleur de fond du label
            ]

        # Formatage des lignes "Activités"
        for indexColoration in self.dictImpression["coloration"] :
            listeStyles.append( ('BACKGROUND', (0, indexColoration+1), (-1, indexColoration+1), UTILS_Divers.ConvertCouleurWXpourPDF(dictOptions["couleur_fond_depot"])))
                
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
                    return (nbre, None)
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.ctrl_stats = CTRL(panel)
        
        # Choix du mode d'affichage
        self.ctrl_stats.SetModeAffichage("mois")
        
##        # Type dépôts
##        self.ctrl_stats.SetTypeDepots(listeDepots=[1, 2, 3, 4, 5])
        
        # Type Prestations
        self.ctrl_stats.SetTypePrestations(date_debut=datetime.date(2011, 7, 1), date_fin=datetime.date(2011, 7, 31))
        
        # MAJ du ctrl
        self.ctrl_stats.MAJ() 
        
        self.choix = wx.Choice(panel, -1, choices = ["mois", "annee"])
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
        self.ctrl_stats.SetModeAffichage(self.choix.GetStringSelection())
        self.ctrl_stats.MAJ() 
    
    def OnBoutonImprimer(self, event):
##        self.ctrl_stats.ExportExcel() 
        self.ctrl_stats.Imprimer()

if __name__ == '__main__':    
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
