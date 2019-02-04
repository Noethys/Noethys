#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
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

import GestionDB
import FonctionsPerso
from Utils import UTILS_Organisateur
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Dates

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)
            


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, listeIDconso=[]):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.listeIDconso = listeIDconso
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
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)

        # Init
        self.MAJ()

    def Importation(self):
        # Conditions Consommations
        if len(self.listeIDconso) == 0 : conditionConso = "()"
        elif len(self.listeIDconso) == 1 : conditionConso = "(%d)" % self.listeIDconso[0]
        else : conditionConso = str(tuple(self.listeIDconso))

        # Importation des consommations
        DB = GestionDB.DB()
        req = """
        SELECT IDconso, consommations.IDindividu, consommations.IDactivite, date, consommations.IDunite, consommations.IDgroupe, consommations.etat, date_saisie, quantite,
        individus.nom, individus.prenom,
        unites.nom, unites.ordre, unites.abrege,
        activites.nom, groupes.nom,
        consommations.IDcompte_payeur, comptes_payeurs.IDfamille
        FROM consommations
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = consommations.IDgroupe
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE consommations.IDconso IN %s
        ORDER BY IDconso
        ;""" % conditionConso
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        dictConso = {}
        dictActivites = {}
        dictGroupes = {}
        dictIndividus = {}
        for IDconso, IDindividu, IDactivite, date, IDunite, IDgroupe, etat, date_saisie, quantite, nomIndividu, prenomIndividu, nomUnite, ordreUnite, abregeUnite, nomActivite, nomGroupe, IDcompte_payeur, IDfamille in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            date_saisie = UTILS_Dates.DateEngEnDateDD(date_saisie)
            
            # Date
            if (date in dictConso) == False :
                dictConso[date] = {}
            # Activité
            if (IDactivite in dictConso[date]) == False :
                dictConso[date][IDactivite] = {}
            # Groupe
            if (IDgroupe in dictConso[date][IDactivite]) == False :
                dictConso[date][IDactivite][IDgroupe] = {}
            # Individu
            if (IDindividu in dictConso[date][IDactivite][IDgroupe]) == False :
                dictConso[date][IDactivite][IDgroupe][IDindividu] = []

            if quantite == None :
                quantite = 1

            dictTemp = {
                "IDconso" : IDconso, "IDindividu" : IDindividu, "IDactivite" : IDactivite, "date" : date,
                "IDunite" : IDunite, "IDgroupe" : IDgroupe, "etat" : etat, "date_saisie" : date_saisie, 
                "nomUnite" : nomUnite, "ordreUnite" : ordreUnite, "IDcompte_payeur" : IDcompte_payeur,
                "IDfamille" : IDfamille, "quantite" : quantite, "abregeUnite" : abregeUnite,
                }
            dictConso[date][IDactivite][IDgroupe][IDindividu].append(dictTemp)

            if (IDactivite in dictActivites) == False :
                dictActivites[IDactivite] = nomActivite
            if (IDgroupe in dictGroupes) == False :
                dictGroupes[IDgroupe] = nomGroupe
            if (IDindividu in dictIndividus) == False :
                dictIndividus[IDindividu] = {"nomIndividu" : u"%s %s" % (nomIndividu, prenomIndividu), "IDfamille" : IDfamille }
        
        return dictConso, dictActivites, dictGroupes, dictIndividus
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()

    def Remplissage(self):
        dictConso, dictActivites, dictGroupes, dictIndividus = self.Importation()

        # Mémorisation pour impression
        self.listeImpression = []
        
        # Branches DATE
        listeDates = list(dictConso.keys())
        listeDates.sort() 
        
        for date in listeDates :
            niveauDate = self.AppendItem(self.root, UTILS_Dates.DateComplete(date))
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

                    # Branches Individus
                    listeImpressionIndividus = []
                    listeIndividus = []
                    for IDindividu, listeConso in dictConso[date][IDactivite][IDgroupe].items() :
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
                        niveauIndividu = self.AppendItem(niveauGroupe, texteIndividu)
                        self.SetPyData(niveauIndividu, {"type" : "individu", "nomIndividu" : nomIndividu, "IDindividu" : IDindividu, "IDfamille" : IDfamille})
                        
                        # Détail pour l'individu
                        texteUnites = u""
                        dateSaisie = None
                        placeDispo = True
                        for dictUnite in dictConso[date][IDactivite][IDgroupe][IDindividu] :
                            IDunite = dictUnite["IDunite"]
                            date_saisie = dictUnite["date_saisie"]
                            texteUnites += dictUnite["abregeUnite"]
                            if dictUnite["quantite"] > 1 :
                                texteUnites += u" (%d)" % dictUnite["quantite"]
                            texteUnites += u" + "
                            if dateSaisie == None or date_saisie < dateSaisie :
                                dateSaisie = date_saisie

                        texteUnites = texteUnites[:-3]
                        texteDateSaisie = UTILS_Dates.DateComplete(dateSaisie)
                        
                        # Autres colonnes
                        self.SetItemText(niveauIndividu, texteUnites, 1)
                        self.SetItemText(niveauIndividu, texteDateSaisie, 2)

                        # Mémorisation pour impression
                        listeImpressionIndividus.append({"placeDispo" : placeDispo, "texteIndividu" : texteIndividu, "texteUnites" : texteUnites, "texteDateSaisie" : texteDateSaisie} )
                        
                        num += 1
                    
                    # Mémorisation pour impression
                    listeImpressionGroupes.append( (nomGroupe, listeImpressionIndividus) )

            # Mémorisation pour impression
            self.listeImpression.append( (UTILS_Dates.DateComplete(date), listeImpressionGroupes) )
        
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

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def OuvrirFicheFamille(self, event):
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
            
        
        
    
    def Imprimer(self, event):
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib import colors
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Initialisation du PDF
        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_CONSO", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = 520
        
        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (420, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Liste des consommations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel)
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
