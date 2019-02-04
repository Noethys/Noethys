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
import wx.lib.agw.hypertreelist as HTL
import datetime
import copy
import sys
import os

import GestionDB
from Ctrl import CTRL_Saisie_euros
import FonctionsPerso
from Utils import UTILS_Organisateur
from Utils import UTILS_Utilisateurs

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)
            
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
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, dictDonnees={}, dictEtatPlaces={}, dictUnitesRemplissage={}, mode="attente"):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.mode = mode

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.dictDonnees = dictDonnees
        self.dictEtatPlaces = dictEtatPlaces # copy.deepcopy(dictEtatPlaces)
        self.dictUnitesRemplissage = dictUnitesRemplissage
        self.listeTracks = []
        self.listePeriodes = []
        self.listeActivites = []
        self.listeImpression = []
                
        # Création des colonnes
        listeColonnes = [
            ( _(u"Date/Groupe/Individu"), 250, wx.ALIGN_LEFT),
            ( _(u"Consommations réservées"), 240, wx.ALIGN_LEFT),
            ( _(u"Date de la réservation"), 200, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.img_ok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Ok.png'), wx.BITMAP_TYPE_PNG))
        self.img_pasok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Interdit.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        
        if len(dictDonnees) > 0 :
            self.SetDictDonnees(dictDonnees)


    def SetDictDonnees(self, dictDonnees=None):
        self.dictDonnees = dictDonnees
        self.listeActivites = self.dictDonnees["listeActivites"]
        self.listePeriodes = self.dictDonnees["listePeriodes"]
        self.MAJ() 
        
    def GetSQLdates(self, listePeriodes=[]):
        texteSQL = ""
        for date_debut, date_fin in listePeriodes :
            texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
        if len(texteSQL) > 0 :
            texteSQL = "(" + texteSQL[:-4] + ")"
        else:
            texteSQL = "date='3000-01-01'"
        return texteSQL

    def Importation(self):
        # Conditions Périodes
        conditionsDates = self.GetSQLdates(self.listePeriodes)
        conditionsDates = conditionsDates.replace("date", "consommations.date")

        # Conditions Activités
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        
        # Importation des consommations en attente
        DB = GestionDB.DB()
        req = """
        SELECT IDconso, consommations.IDindividu, consommations.IDactivite, consommations.date, consommations.IDunite, consommations.IDgroupe, consommations.IDevenement, consommations.etat, date_saisie,
        evenements.nom,
        individus.nom, individus.prenom,
        unites.nom, unites.ordre,
        activites.nom, groupes.nom,
        consommations.IDcompte_payeur, comptes_payeurs.IDfamille
        FROM consommations
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        LEFT JOIN evenements ON evenements.IDevenement = consommations.IDevenement
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = consommations.IDgroupe
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE consommations.etat = '%s' AND consommations.IDactivite IN %s AND %s
        ORDER BY IDconso
        ;""" % (self.mode, conditionActivites, conditionsDates)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        dictConso = {}
        dictActivites = {}
        dictGroupes = {}
        dictIndividus = {}
        dictEvenements = {}
        for IDconso, IDindividu, IDactivite, date, IDunite, IDgroupe, IDevenement, etat, date_saisie, nomEvenement, nomIndividu, prenomIndividu, nomUnite, ordreUnite, nomActivite, nomGroupe, IDcompte_payeur, IDfamille in listeDonnees :
            date = DateEngEnDateDD(date)
            date_saisie = DateEngEnDateDD(date_saisie)
            
            # Date
            if (date in dictConso) == False :
                dictConso[date] = {}
            # Activité
            if (IDactivite in dictConso[date]) == False :
                dictConso[date][IDactivite] = {}
            # Groupe
            if (IDgroupe in dictConso[date][IDactivite]) == False :
                dictConso[date][IDactivite][IDgroupe] = {}
            # Evènement
            if (IDevenement in dictConso[date][IDactivite][IDgroupe]) == False :
                dictConso[date][IDactivite][IDgroupe][IDevenement] = {}
            # Individu
            if (IDindividu in dictConso[date][IDactivite][IDgroupe][IDevenement]) == False :
                dictConso[date][IDactivite][IDgroupe][IDevenement][IDindividu] = []
                
            dictTemp = {
                "IDconso" : IDconso, "IDindividu" : IDindividu, "IDactivite" : IDactivite, "date" : date,
                "IDunite" : IDunite, "IDgroupe" : IDgroupe, "etat" : etat, "date_saisie" : date_saisie, 
                "nomUnite" : nomUnite, "ordreUnite" : ordreUnite, "IDcompte_payeur" : IDcompte_payeur,
                "IDfamille" : IDfamille, "IDevenement" : IDevenement, "nomEvenement" : nomEvenement,
                }
            dictConso[date][IDactivite][IDgroupe][IDevenement][IDindividu].append(dictTemp)
            
            if (IDactivite in dictActivites) == False :
                dictActivites[IDactivite] = nomActivite
            if (IDgroupe in dictGroupes) == False :
                dictGroupes[IDgroupe] = nomGroupe
            if (IDindividu in dictIndividus) == False :
                dictIndividus[IDindividu] = {"nomIndividu" : u"%s %s" % (nomIndividu, prenomIndividu), "IDfamille" : IDfamille }

            if (IDevenement in dictEvenements) == False and IDevenement != None :
                dictEvenements[IDevenement] = nomEvenement

        return dictConso, dictActivites, dictGroupes, dictIndividus, dictEvenements
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
##        self.Freeze()
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
##        self.Thaw() 

    def Remplissage(self):
        dictConso, dictActivites, dictGroupes, dictIndividus, dictEvenements = self.Importation()

        dictPlacesRestantes = {}
        
        # Mémorisation pour impression
        self.listeImpression = []
        
        # Branches DATE
        listeDates = list(dictConso.keys())
        listeDates.sort() 
        
        for date in listeDates :
            niveauDate = self.AppendItem(self.root, DateComplete(date))
            self.SetPyData(niveauDate, {"type" : "date", "valeur" : date})
            self.SetItemBold(niveauDate, True)
            self.SetItemBackgroundColour(niveauDate, wx.Colour(*COULEUR_FOND_REGROUPEMENT))
            
            # Branches Activités
            listeActivites = list(dictConso[date].keys())
            listeActivites.sort() 
            
            for IDactivite in listeActivites :
                
                if len(listeActivites) > 1 :
                    niveauActivite = self.AppendItem(niveauDate, dictActivites[IDactivite])
                    self.SetPyData(niveauActivite, IDactivite)
                    self.SetItemBold(niveauActivite, True)
                else:
                    niveauActivite = niveauDate
                
                # Branches Groupe
                listeImpressionGroupes = []
                listeGroupes = list(dictConso[date][IDactivite].keys())
                listeGroupes.sort() 
                
                for IDgroupe in listeGroupes :
                    nomGroupe = dictGroupes[IDgroupe]
                    niveauGroupe = self.AppendItem(niveauActivite, nomGroupe)
                    self.SetPyData(niveauGroupe, {"type" : "groupe", "valeur" : IDgroupe})
                    self.SetItemBold(niveauGroupe, True)

                    # Parcourt les évènements
                    for IDevenement, dictTemp in dictConso[date][IDactivite][IDgroupe].items() :

                        if IDevenement != None :
                            parent = self.AppendItem(niveauGroupe, dictEvenements[IDevenement])
                            self.SetPyData(parent, {"type": "groupe", "valeur": IDgroupe})
                            # self.SetItemBold(parent, True)
                        else :
                            parent = niveauGroupe

                        # Branches Individus
                        listeImpressionIndividus = []
                        listeIndividus = []
                        for IDindividu, listeConso in dictTemp.items() :
                            listeIDconso = []
                            for dictConsoIndividu in listeConso :
                                listeIDconso.append(dictConsoIndividu["IDconso"])
                            IDconsoMin = min(listeIDconso)
                            listeIndividus.append((IDconsoMin, IDindividu))
                        listeIndividus.sort()

                        num = 1
                        for ordreIndividu, IDindividu in listeIndividus :
                            nomIndividu = dictIndividus[IDindividu]["nomIndividu"]
                            texteIndividu = u"%d. %s" % (num, nomIndividu)
                            IDfamille = dictIndividus[IDindividu]["IDfamille"]
                            niveauIndividu = self.AppendItem(parent, texteIndividu)
                            self.SetPyData(niveauIndividu, {"type" : "individu", "nomIndividu" : nomIndividu, "IDindividu" : IDindividu, "IDfamille" : IDfamille})

                            # Détail pour l'individu
                            texteUnites = u""
                            dateSaisie = None
                            placeDispo = True
                            listePlaces = []
                            for dictUnite in dictConso[date][IDactivite][IDgroupe][IDevenement][IDindividu] :

                                IDunite = dictUnite["IDunite"]
                                date_saisie = dictUnite["date_saisie"]
                                nomUnite = dictUnite["nomUnite"]
                                if IDevenement != None :
                                    nomUnite += u" (%s)" % dictEvenements[IDevenement]
                                texteUnites += nomUnite + " + "
                                if dateSaisie == None or date_saisie < dateSaisie :
                                    dateSaisie = date_saisie

                                # Etat des places
                                if IDunite in self.dictUnitesRemplissage :
                                    listePlacesRestantes = []
                                    for IDuniteRemplissage in self.dictUnitesRemplissage[IDunite] :
                                        key = (date, IDactivite, IDgroupe, IDuniteRemplissage, IDevenement)
                                        if key in dictPlacesRestantes :
                                            nbrePlacesRestantes = dictPlacesRestantes[key]
                                        elif key in self.dictEtatPlaces :
                                            if IDevenement == None :
                                                nbrePlacesRestantes = self.dictEtatPlaces[key]["remplissage"]["nbrePlacesRestantes"]
                                            else :
                                                nbrePlacesRestantes = self.dictEtatPlaces[key]["evenement"].GetPlacesEvenement()["nbrePlacesRestantes"]
                                            if nbrePlacesRestantes == None :
                                                nbrePlacesRestantes = 99999
                                            dictPlacesRestantes[key] = nbrePlacesRestantes
                                        else :
                                            nbrePlacesRestantes = 0
                                        listePlacesRestantes.append(nbrePlacesRestantes)
                                    nbrePlacesRestantes = min(listePlacesRestantes)
                                    if nbrePlacesRestantes <= 0 :
                                        placeDispo = False

                            # S'il reste finalement une place dispo, on change le nbre de places restantes
                            if placeDispo == True :
                                for dictUnite in dictConso[date][IDactivite][IDgroupe][IDevenement][IDindividu] :
                                    IDunite = dictUnite["IDunite"]
                                    if IDunite in self.dictUnitesRemplissage :
                                        for IDuniteRemplissage in self.dictUnitesRemplissage[IDunite] :
                                            key = (date, IDactivite, IDgroupe, IDuniteRemplissage, IDevenement)
                                            #self.dictEtatPlaces[key]["remplissage"]["nbrePlacesRestantes"] -= 1
                                            dictPlacesRestantes[key] -= 1

                            texteUnites = texteUnites[:-3]
                            texteDateSaisie = DateComplete(dateSaisie)

                            # Autres colonnes
                            self.SetItemText(niveauIndividu, texteUnites, 1)
                            self.SetItemText(niveauIndividu, texteDateSaisie, 2)

                            # Image
                            if placeDispo == True :
                                img = self.img_ok
                            else :
                                img = self.img_pasok
                            self.SetItemImage(niveauIndividu, img, which=wx.TreeItemIcon_Normal)

                            # Mémorisation pour impression
                            listeImpressionIndividus.append({"placeDispo" : placeDispo, "nomIndividu" : nomIndividu, "num" : num, "texteIndividu" : texteIndividu, "texteUnites" : texteUnites, "texteDateSaisie" : texteDateSaisie} )

                            num += 1
                    
                    # Mémorisation pour impression
                    listeImpressionGroupes.append( (nomGroupe, listeImpressionIndividus) )

            # Mémorisation pour impression
            self.listeImpression.append( (DateComplete(date), listeImpressionGroupes) )
        
        self.ExpandAllChildren(self.root)
    
    
    def OnCompareItems(self, item1, item2):
        if self.GetPyData(item1) > self.GetPyData(item2) :
            return 1
        elif self.GetPyData(item1) < self.GetPyData(item2) :
            return -1
        else:
            return 0
                        
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        if type != "individu" : return
        nomIndividu = dictItem["nomIndividu"]
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille de %s") % nomIndividu)
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 20, _(u"Imprimer (PDF)"), _(u"Imprimer (PDF)"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=20)

        item = wx.MenuItem(menuPop, 30, _(u"Exporter au format Excel"), _(u"Exporter au format Excel"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=30)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def OuvrirFicheFamille(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        type = dictItem["type"]
        if type != "individu" : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDindividu = dictItem["IDindividu"]
        IDfamille = dictItem["IDfamille"]
        
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        
        if self.GetGrandParent().GetName() == "panel_remplissage" :
            panel_remplissage = self.GetGrandParent()
            # Mise à jour des chiffres du remplissage
            panel_remplissage.MAJ() 
            # Récupération des nouveau chiffres
            self.dictEtatPlaces = panel_remplissage.ctrl_remplissage.GetEtatPlaces() # copy.deepcopy(panel_remplissage.ctrl_remplissage.GetEtatPlaces())
            # MAJ du contrôle liste d'attente
            self.MAJ() 
            
        
        
    
    def Imprimer(self, event=None):
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Initialisation du PDF
        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_ATTENTE", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = 520
        
        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (420, 100) )
            dateDuJour = DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Liste d'attente"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
                                
        # Un tableau par date
        for date, listeGroupes in self.listeImpression :
            
            dataTableau = []
            largeursColonnes = [180, 180, 160]
            
            dataTableau.append( (date, "", "") )
            
            # Groupes
            listeIndexGroupes = []
            indexLigne = 0
            for nomGroupe, listeIndividus in listeGroupes :
                indexLigne += 1
                listeIndexGroupes.append(indexLigne)
                
                dataTableau.append( (nomGroupe, "", "") )
                
                # Individus
                for dictIndividu in listeIndividus :
                    placeDispo = dictIndividu["placeDispo"]
                    texteIndividu = dictIndividu["texteIndividu"]
                    texteUnites = dictIndividu["texteUnites"]
                    texteDateSaisie = _(u"Saisie le %s") % dictIndividu["texteDateSaisie"]
                    dataTableau.append( (texteIndividu, texteUnites, texteDateSaisie) ) # Paragraph(memo_journee, paraStyle)
                    indexLigne += 1
                    
            couleurFond = (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)
            
            listeStyles = [
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                    
                    ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                    ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                    ('ALIGN', (0,1), (-1,-1), 'CENTRE'), # Centre les cases
                    
                    ('ALIGN', (0,1), (-1,1), 'CENTRE'), # Ligne de labels colonne alignée au centre
                    ('FONT',(0,1),(-1,1), "Helvetica", 6), # Donne la police de caract. + taille de police des labels
                    
                    ('SPAN',(0,0),(-1,0)), # Fusionne les lignes du haut pour faire le titre du groupe
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 10), # Donne la police de caract. + taille de police du titre de groupe
                    ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                    
                    ]
            
            # Formatage des lignes "Activités"
            for indexGroupe in listeIndexGroupes :
                listeStyles.append( ('SPAN', (0, indexGroupe), (-1, indexGroupe)) )
                listeStyles.append( ('FONT', (0, indexGroupe), (-1, indexGroupe), "Helvetica-Bold", 7) )
                listeStyles.append( ('ALIGN', (0, indexGroupe), (-1, indexGroupe), 'LEFT') ) 
                
            # Création du tableau
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)
            story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


    def ExportExcel(self, event=None):
        """ Export Excel """
        titre = _(u"Liste d'attente")

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
        import pyExcelerator
        # Création d'un classeur
        wb = pyExcelerator.Workbook()
        # Création d'une feuille
        ws1 = wb.add_sheet(titre)

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

        styleDate = pyExcelerator.XFStyle()
        styleDate.alignment = al
        styleDate.font.bold = True

        # Entetes et largeurs des colonnes
        colonnes = [
            (_(u"Date"), 8000), (_(u"Groupe"), 8000), (_(u"Dispo"), 2000), (_(u"N°"), 2000),
            (_(u"Individu"), 10000), (_(u"Unités"), 10000), (_(u"Date de saisie"), 10000),
            ]
        index = 0
        for label, largeur in colonnes :
            ws1.col(index).width = largeur
            ws1.write(0, index, label)
            index += 1

        # Contenu
        x = 1
        for date, listeGroupes in self.listeImpression :
            for nomGroupe, listeIndividus in listeGroupes :
                for dictIndividu in listeIndividus :
                    placeDispo = dictIndividu["placeDispo"]
                    if placeDispo == True :
                        placeDispoTxt = _(u"Oui")
                    else :
                        placeDispo = ""

                    ws1.write(x, 0, date, styleDate)
                    ws1.write(x, 1, nomGroupe)
                    ws1.write(x, 2, placeDispo)
                    ws1.write(x, 3, dictIndividu["num"])
                    ws1.write(x, 4, dictIndividu["nomIndividu"])
                    ws1.write(x, 5, dictIndividu["texteUnites"])
                    ws1.write(x, 6, dictIndividu["texteDateSaisie"])

                    x += 1

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
        
        dictDonnees = {
            "page" : 0,
            "listeSelections" : [2, 3, 5],
            "annee" : 2009,
            "dateDebut" : None,
            "dateFin" : None,
            "listePeriodes" : [ (datetime.date(2010, 1, 1), datetime.date(2010, 12, 31)), ],
            "listeActivites" : [1,],
            }

        
        self.myOlv = CTRL(panel, dictDonnees={})
        self.myOlv.SetDictDonnees(dictDonnees) 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
