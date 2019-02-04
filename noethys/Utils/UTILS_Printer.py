#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import copy

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import ReportFormat
from Outils import ListCtrlPrinter
import GestionDB
from Dlg import DLG_Options_impression_listes
from Utils import UTILS_Dates




class PreviewControlBar(wx.PyPreviewControlBar):
    def __init__(self, preview, buttons, parent):
        wx.PyPreviewControlBar.__init__(self, preview, buttons, parent)
        self.preview = preview
        self.parent = parent
        zoomDefaut = 100
        self.preview.SetZoom(zoomDefaut)
        
        # Impression
        self.staticbox_impression_staticbox = wx.StaticBox(self, -1, _(u"Impression"))
        self.bouton_imprimer = wx.BitmapButton(self, wx.ID_PREVIEW_PRINT, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Imprimante.png"), wx.BITMAP_TYPE_ANY), size=(80, -1))
        
        # Impression rapide
        self.staticbox_rapide_staticbox = wx.StaticBox(self, -1, _(u"Impression rapide"))
        self.bouton_rapide_x1 = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Imprimer-x1.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_rapide_x2 = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Imprimer-x2.png"), wx.BITMAP_TYPE_ANY))

        # Navigation
        self.staticbox_navigation_staticbox = wx.StaticBox(self, -1, _(u"Navigation"))
        self.bouton_premier = wx.BitmapButton(self, wx.ID_PREVIEW_FIRST, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Premier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_precedent = wx.BitmapButton(self, wx.ID_PREVIEW_PREVIOUS, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Precedent.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_suivant = wx.BitmapButton(self, wx.ID_PREVIEW_NEXT, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Suivant.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_dernier = wx.BitmapButton(self, wx.ID_PREVIEW_LAST, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Dernier.png"), wx.BITMAP_TYPE_ANY))

        # Zoom
        self.staticbox_zoom_staticbox = wx.StaticBox(self, -1, _(u"Zoom"))
        self.bouton_zoom_moins = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_moins.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_zoom = wx.Slider(self, -1, zoomDefaut, 1, 200, style=wx.SL_HORIZONTAL)
        self.ctrl_zoom.SetTickFreq(5, 1)
        self.bouton_zoom_plus = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_plus.png"), wx.BITMAP_TYPE_ANY))

        # Fermer
        self.staticbox_fermer_staticbox = wx.StaticBox(self, -1, _(u"Fermer"))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_PREVIEW_CLOSE, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Fermer.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnImpressionRapideX1, self.bouton_rapide_x1)
        self.Bind(wx.EVT_BUTTON, self.OnImpressionRapideX2, self.bouton_rapide_x2)
        self.Bind(wx.EVT_SCROLL, self.OnZoom, self.ctrl_zoom)
        self.Bind(wx.EVT_BUTTON, self.OnZoomMoins, self.bouton_zoom_moins)
        self.Bind(wx.EVT_BUTTON, self.OnZoomPlus, self.bouton_zoom_plus)

    def __set_properties(self):
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher l'impression")))
        self.bouton_rapide_x1.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer une impression rapide en 1 exemplaire")))
        self.bouton_rapide_x2.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer une impression rapide en 2 exemplaires")))
        self.bouton_premier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la première page")))
        self.bouton_precedent.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la page précédente")))
        self.bouton_suivant.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la page suivante")))
        self.bouton_dernier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la dernière page")))
        self.bouton_zoom_moins.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour faire un zoom arrière")))
        self.ctrl_zoom.SetToolTip(wx.ToolTip(_(u"Déplacez la règlette pour zoomer")))
        self.bouton_zoom_plus.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour faire un zoom avant")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer l'aperçu")))

    def __do_layout(self):
        grid_sizer_base = wx.GridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=10, vgap=10, hgap=10)
        staticbox_fermer = wx.StaticBoxSizer(self.staticbox_fermer_staticbox, wx.VERTICAL)
        staticbox_zoom = wx.StaticBoxSizer(self.staticbox_zoom_staticbox, wx.VERTICAL)
        grid_sizer_zoom = wx.FlexGridSizer(rows=1, cols=4, vgap=0, hgap=5)
        staticbox_navigation = wx.StaticBoxSizer(self.staticbox_navigation_staticbox, wx.VERTICAL)
        grid_sizer_navigation = wx.FlexGridSizer(rows=1, cols=4, vgap=0, hgap=0)
        staticbox_rapide = wx.StaticBoxSizer(self.staticbox_rapide_staticbox, wx.VERTICAL)
        grid_sizer_rapide = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        staticbox_impression = wx.StaticBoxSizer(self.staticbox_impression_staticbox, wx.VERTICAL)
        grid_sizer_impression = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_impression.Add(self.bouton_imprimer, 0, 0, 0)
        staticbox_impression.Add(grid_sizer_impression, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_impression, 1, wx.EXPAND, 0)
        grid_sizer_rapide.Add(self.bouton_rapide_x1, 0, 0, 0)
        grid_sizer_rapide.Add(self.bouton_rapide_x2, 0, 0, 0)
        staticbox_rapide.Add(grid_sizer_rapide, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_rapide, 1, wx.EXPAND, 0)
        grid_sizer_navigation.Add(self.bouton_premier, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_precedent, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_suivant, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_dernier, 0, 0, 0)
        staticbox_navigation.Add(grid_sizer_navigation, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_navigation, 1, wx.EXPAND, 0)
        grid_sizer_zoom.Add(self.bouton_zoom_moins, 0, 0, 0)
        grid_sizer_zoom.Add(self.ctrl_zoom, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_zoom.Add(self.bouton_zoom_plus, 0, 0, 0)
        staticbox_zoom.Add(grid_sizer_zoom, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_zoom, 1, wx.EXPAND, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        staticbox_fermer.Add(self.bouton_fermer, 0, wx.ALL, 5)
        grid_sizer_commandes.Add(staticbox_fermer, 1, wx.EXPAND, 0)
        grid_sizer_commandes.AddGrowableCol(4)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(grid_sizer_base)
        self.Layout() 
        #grid_sizer_base.Fit(self)
    
    def OnImpressionRapideX1(self, event):
        self.ImpressionRapide(nbreExemplaires=1)
    
    def OnImpressionRapideX2(self, event):
        self.ImpressionRapide(nbreExemplaires=2)
    
    def ImpressionRapide(self, nbreExemplaires=1):
        pd = wx.PrintData()
        pd.SetPrinterName('')
        pd.SetOrientation(self.GetParent().orientation)
        pd.SetPaperId(wx.PAPER_A4)
        pd.SetQuality(wx.PRINT_QUALITY_DRAFT)
        pd.SetColour(True)
        pd.SetNoCopies(nbreExemplaires)
        pd.SetCollate(True)
        
        pdd = wx.PrintDialogData()
        pdd.SetPrintData(pd)
        
        printer = wx.Printer(pdd)
        printer.Print(self.parent, self.preview.GetPrintoutForPrinting(), False)
        
    def OnZoom(self, event): 
        zoom = self.ctrl_zoom.GetValue()
        self.preview.SetZoom(zoom)

    def OnZoomMoins(self, event):
        zoomActuel = self.ctrl_zoom.GetValue()
        zoom = zoomActuel - 10
        if zoom >= 1 :
            self.ctrl_zoom.SetValue(zoom)
            self.preview.SetZoom(zoom)

    def OnZoomPlus(self, event):
        zoomActuel = self.ctrl_zoom.GetValue()
        zoom = zoomActuel + 10
        if zoom <= 200 :
            self.ctrl_zoom.SetValue(zoom)
            self.preview.SetZoom(zoom)


        
    
class PreviewFrame(wx.PyPreviewFrame):
    def __init__(self, preview, parent, title=_(u"Aperçu avant impression"), orientation=wx.PORTRAIT):
        wx.PyPreviewFrame.__init__(self, preview, parent, title)
        self.preview = preview
        self.orientation = orientation

        self.SetMinSize((650, 500))
        
        self.controlBar = PreviewControlBar(self.preview, wx.PREVIEW_DEFAULT, self)
        self.SetControlBar(self.controlBar)
        
        previewCanvas = wx.PreviewCanvas(self.preview, self, style=wx.SUNKEN_BORDER)
        self.SetPreviewCanvas(previewCanvas)
                
        self.SetSize((900, 700))
        self.CenterOnScreen() 

    def doClose(self, event):
         self.Close()
    
    def CreateControlBar(self):
        return PreviewControlBar(self.preview, wx.PREVIEW_DEFAULT, self)
        

class ObjectListViewPrinter():
    def __init__(self, listview, titre=u"", intro=u"", total=u"", format="A", orientation=wx.PORTRAIT):
        self.listview = listview
        self.titre = titre
        self.intro = intro
        self.total = total
        self.orientation = orientation
    
    def InitParametres(self):
        """ Récupération des paramètres d'impression """
        # DLG des paramètres d'impression
        dictOptions = {
            "titre" : self.titre,
            "introduction" : self.intro,
            "conclusion" : self.total,
            "orientation" : self.orientation,
            }
        dlg = DLG_Options_impression_listes.Dialog(None, dictOptions=dictOptions)
        if dlg.ShowModal() == wx.ID_OK:
            dictOptions = dlg.GetOptions()
            dlg.Destroy() 
        else :
            dlg.Destroy() 
            return False
        
        # Remplacement des mots-clés
        listeChamps = ["pied_page_texte_gauche", "pied_page_texte_milieu", "pied_page_texte_droite"]
        nomOrganisateur = self.GetNomOrganisateur()
        for key, valeur in dictOptions.items() :
            if key in listeChamps :
                valeur = valeur.replace("{DATE_JOUR}", UTILS_Dates.DateDDEnFr(datetime.date.today()))
                valeur = valeur.replace("{TITRE_DOCUMENT}", self.titre)
                valeur = valeur.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
                valeur = valeur.replace("{NUM_PAGE}", "%(currentPage)d")
                valeur = valeur.replace("{NBRE_PAGES}", "%(totalPages)d")
                dictOptions[key] = valeur
                
        # Préparation du printout
        self.printer = ListCtrlPrinter.ListCtrlPrinter(self.listview, dictOptions["titre"])
        self.printer.printout.margins = (wx.Point(int(dictOptions["marge_gauche"]), int(dictOptions["marge_haut"])), wx.Point(int(dictOptions["marge_droite"]), int(dictOptions["marge_bas"])))
        self.printer.printout.printData.SetOrientation(dictOptions["orientation"])
        self.printer.printout.printData.SetQuality(int(dictOptions["qualite_impression"]))
        self.printer.PageFooter = (dictOptions["pied_page_texte_gauche"], dictOptions["pied_page_texte_milieu"], dictOptions["pied_page_texte_droite"])
        ListCtrlPrinter.LISTINTRO = dictOptions["introduction"]
        ListCtrlPrinter.LISTFOOTER = dictOptions["conclusion"]
        
        # Préparation du format
        fmt = ReportFormat()
        
        # Entête de page
    ##        fmt.PageHeader.Font = wx.FFont(10, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
    ##        fmt.PageHeader.TextColor = wx.WHITE
    ##        fmt.PageHeader.Background(wx.GREEN, wx.RED, space=(16, 4, 0, 4))
    ##        fmt.PageHeader.Padding = (0, 0, 0, 12)
        
        # Titre de liste
        fmt.ListHeader.Font = wx.Font(int(dictOptions["titre_taille_texte"]), wx.SWISS, wx.NORMAL, int(dictOptions["titre_style"]), faceName="Arial")
        fmt.ListHeader.TextColor = dictOptions["titre_couleur"]
        fmt.ListHeader.Padding = (0, 12, 0, 10)
        fmt.ListHeader.TextAlignment = dictOptions["titre_alignement"]
        fmt.ListHeader.Frame(wx.Pen(wx.BLACK, 0.25, wx.SOLID), space=10)
        
        # Intro
        fmt.ListIntro.Font = wx.Font(int(dictOptions["intro_taille_texte"]), wx.SWISS, wx.NORMAL, int(dictOptions["intro_style"]), faceName="Arial")
        fmt.ListIntro.TextColor = dictOptions["intro_couleur"]
        fmt.ListIntro.Padding = (12, 2, 12, 2)
        fmt.ListIntro.TextAlignment = dictOptions["intro_alignement"]
        fmt.ListIntro.CanWrap = True
        
        # Titre de colonne
        fmt.ColumnHeader.Font = wx.Font(int(dictOptions["titre_colonne_taille_texte"]), wx.SWISS, wx.NORMAL, int(dictOptions["titre_colonne_style"]), faceName="Arial")
        fmt.ColumnHeader.TextColor = dictOptions["titre_colonne_couleur"]
        fmt.ColumnHeader.Padding = (0, 15, 0, 0)
        fmt.ColumnHeader.Background(dictOptions["titre_colonne_couleur_fond"])
        fmt.ColumnHeader.CellPadding = 5
        fmt.ColumnHeader.TextAlignment = dictOptions["titre_colonne_alignement"]
        fmt.ColumnHeader.GridPen = wx.Pen(dictOptions["grille_trait_couleur"], dictOptions["grille_trait_epaisseur"], wx.SOLID)
        fmt.ColumnHeader.SetAlwaysCenter(True)
        
        # Titre d'un groupe
        fmt.GroupTitle.Font = wx.FFont(10, wx.FONTFAMILY_SWISS, wx.FONTFLAG_BOLD, faceName="Arial")
        fmt.GroupTitle.Padding = (2, 10, 2, 2)
        fmt.GroupTitle.CellPadding = 12
        fmt.GroupTitle.GridPen = wx.Pen(dictOptions["grille_trait_couleur"], dictOptions["grille_trait_epaisseur"], wx.SOLID)
        
##        fmt.GroupTitle.TextColor = wx.BLUE
##        fmt.GroupTitle.Padding = (0, 12, 0, 12)
##        fmt.GroupTitle.Line(wx.BOTTOM, wx.GREEN, 4, toColor=wx.WHITE, space=0)

        # Ligne
        fmt.Row.Font = wx.Font(int(dictOptions["ligne_taille_texte"]), wx.SWISS, wx.NORMAL, int(dictOptions["ligne_style"]), faceName="Arial")
        fmt.Row.TextColor = dictOptions["ligne_couleur"]
        fmt.Row.CellPadding = 5
        fmt.Row.GridPen = wx.Pen(dictOptions["grille_trait_couleur"], dictOptions["grille_trait_epaisseur"], wx.SOLID)
        fmt.Row.CanWrap = dictOptions["ligne_multilignes"]
        
        # Pied de page
        fmt.PageFooter.Font = wx.Font(int(dictOptions["pied_page_taille_texte"]), wx.SWISS, wx.NORMAL, int(dictOptions["pied_page_style"]), faceName="Arial")
        fmt.PageFooter.TextColor = dictOptions["pied_page_couleur"]
        fmt.PageFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.PageFooter.Padding = (0, 16, 0, 0)

        # Pied de colonne
        fmt.ColumnFooter.Font = wx.Font(int(dictOptions["pied_colonne_taille_texte"]), wx.SWISS, wx.NORMAL, int(dictOptions["pied_colonne_style"]), faceName="Arial")
        fmt.ColumnFooter.TextColor = dictOptions["pied_colonne_couleur"]
        fmt.ColumnFooter.Padding = (0, 0, 0, 0)
        fmt.ColumnFooter.Background(dictOptions["pied_colonne_couleur_fond"])
        fmt.ColumnFooter.CellPadding = 5
        fmt.ColumnFooter.TextAlignment = dictOptions["pied_colonne_alignement"]
        fmt.ColumnFooter.GridPen = wx.Pen(dictOptions["grille_trait_couleur"], dictOptions["grille_trait_epaisseur"], wx.SOLID)
##        fmt.ColumnFooter.SetAlwaysCenter(True)

        # Conclusion
        fmt.ListFooter.Font = wx.Font(int(dictOptions["conclusion_taille_texte"]), wx.SWISS, wx.NORMAL, int(dictOptions["conclusion_style"]), faceName="Arial")
        fmt.ListFooter.TextColor = dictOptions["conclusion_couleur"]
        fmt.ListFooter.Padding = (12, 12, 0, 0)
        fmt.ListFooter.CellPadding = 5
##        fmt.ListFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.ListFooter.TextAlignment = dictOptions["conclusion_alignement"]
        fmt.ListFooter.CanWrap = True
        
        # Divers paramètres
        fmt.IsShrinkToFit = True
        fmt.IncludeImages = dictOptions["inclure_images"]
        fmt.IsColumnHeadingsOnEachPage = dictOptions["entetes_toutes_pages"]
        fmt.UseListCtrlTextFormat = True

        self.printer.ReportFormat = fmt
        return True

##        self.printer = ListCtrlPrinter.ListCtrlPrinter(self.listview, self.titre)
##        self.printer.printout.margins = (wx.Point(5, 5), wx.Point(5, 5))
##        self.printer.printout.printData.SetOrientation(orientation)
##        self.printer.printout.printData.SetQuality(wx.PRINT_QUALITY_MEDIUM)
##        dateJour = DateEngFr(str(datetime.date.today()))
##        self.printer.PageFooter = (dateJour, u"%s - %s" % (self.titre, self.GetNomOrganisateur()), "%(currentPage)d / %(totalPages)d")
##        ListCtrlPrinter.LISTINTRO = self.intro
##        ListCtrlPrinter.LISTFOOTER = self.total
##        if format == "A" : self.printer.ReportFormat = self.GetFormatA()
        
    def PreviewStandard(self):
        if self.InitParametres() == False :
            return
        self.printer.PrintPreview()
    
    def Print(self):
        if self.InitParametres() == False :
            return
        self.printer.Print() 
    
    def Preview(self):
        if self.InitParametres() == False :
            return
        printPreview = self.printer.printout.GetPrintPreview()
        printPreview.SetZoom(100)

        frm = MyPreviewFrame(printPreview, None, _(u"Aperçu avant impression"))
        frm.Show(True)



    def GetFormatA(self):        
        """ Paramètres du format personnalisé pour objectlistview """
        fmt = ReportFormat()
        
        headerFontName="Arial"
        rowFontName="Arial"
        
        # Entête de page
    ##        fmt.PageHeader.Font = wx.FFont(10, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
    ##        fmt.PageHeader.TextColor = wx.WHITE
    ##        fmt.PageHeader.Background(wx.GREEN, wx.RED, space=(16, 4, 0, 4))
    ##        fmt.PageHeader.Padding = (0, 0, 0, 12)
        
        # Titre de liste
        fmt.ListHeader.Font = wx.FFont(16, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ListHeader.TextColor = wx.BLACK
        fmt.ListHeader.Padding = (0, 12, 0, 10)
        fmt.ListHeader.TextAlignment = wx.ALIGN_LEFT
        fmt.ListHeader.Frame(wx.Pen(wx.BLACK, 0.25, wx.SOLID), space=10)
        
        # Intro
        fmt.ListIntro.Font = wx.FFont(7, wx.FONTFAMILY_DECORATIVE, face=headerFontName)
        fmt.ListIntro.TextColor = wx.BLACK
        fmt.ListIntro.Padding = (12, 2, 12, 2)
        fmt.ListIntro.TextAlignment = wx.ALIGN_LEFT
        fmt.ListIntro.CanWrap = True
        
        # Titre de colonne
        fmt.ColumnHeader.Font = wx.FFont(8, wx.FONTFAMILY_SWISS, face=headerFontName)
        fmt.ColumnHeader.Padding = (0, 15, 0, 0)
        fmt.ColumnHeader.Background(wx.Colour(240, 240, 240))
        fmt.ColumnHeader.CellPadding = 5
        fmt.ColumnHeader.TextAlignment = wx.ALIGN_CENTER
        fmt.ColumnHeader.GridPen = wx.Pen(wx.BLACK, 0.25, wx.SOLID)
        fmt.ColumnHeader.SetAlwaysCenter(True)
        
        # Titre d'un groupe
        fmt.GroupTitle.Font = wx.FFont(9, wx.FONTFAMILY_SWISS, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.GroupTitle.Padding = (2, 10, 2, 2)
        fmt.GroupTitle.CellPadding = 12
        fmt.GroupTitle.GridPen = wx.Pen(wx.BLACK, 0.25, wx.SOLID)
        
##        fmt.GroupTitle.TextColor = wx.BLUE
##        fmt.GroupTitle.Padding = (0, 12, 0, 12)
##        fmt.GroupTitle.Line(wx.BOTTOM, wx.GREEN, 4, toColor=wx.WHITE, space=0)

        # Ligne
        fmt.Row.Font = wx.FFont(8, wx.FONTFAMILY_SWISS, face=rowFontName)
        fmt.Row.CellPadding = 5
        fmt.Row.GridPen = wx.Pen(wx.BLACK, 0.25, wx.SOLID)
        fmt.Row.CanWrap = True
        
        # Pied de page
        fmt.PageFooter.Font = wx.FFont(7, wx.FONTFAMILY_DECORATIVE, face=headerFontName)
        fmt.PageFooter.TextColor = wx.BLACK
        fmt.PageFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.PageFooter.Padding = (0, 16, 0, 0)

        # Pied de colonne
        fmt.ColumnFooter.Font = wx.FFont(8, wx.FONTFAMILY_SWISS, face=headerFontName)
        fmt.ColumnFooter.Padding = (0, 0, 0, 0)
        fmt.ColumnFooter.Background(wx.Colour(240, 240, 240))
        fmt.ColumnFooter.CellPadding = 5
        fmt.ColumnFooter.TextAlignment = wx.ALIGN_CENTER
        fmt.ColumnFooter.GridPen = wx.Pen(wx.BLACK, 0.25, wx.SOLID)
        fmt.ColumnFooter.SetAlwaysCenter(True)

        # Pied de Liste
        fmt.ListFooter.Font = wx.FFont(7, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ListFooter.Padding = (12, 12, 0, 0)
        fmt.ListFooter.CellPadding = 5
##        fmt.ListFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.ListFooter.TextAlignment = wx.ALIGN_LEFT
        fmt.ListFooter.CanWrap = True
        
        # Divers paramètres
        fmt.IsShrinkToFit = True
        fmt.IncludeImages = True
        fmt.IsColumnHeadingsOnEachPage = True
        fmt.UseListCtrlTextFormat = True

        return fmt

    def GetNomOrganisateur(self):
        DB = GestionDB.DB()
        req = """SELECT nom, rue, cp, ville
        FROM organisateur WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return ""
        nom = listeDonnees[0][0]
        if nom == None :
            nom = ""
        return nom


class MyPreviewFrame(wx.PreviewFrame):
    def __init__(self, *args, **kwargs):
        wx.PreviewFrame.__init__(self, *args, **kwargs)
        self.Initialize()

        # Récupération de la bar de contrôle
        controlBar = self.GetControlBar()
        liste_controles = controlBar.GetChildren()

        # Traduction des contrôles en français
        liste_controles[0].SetToolTip(wx.ToolTip(_(u"Imprimer")))
        liste_controles[1].SetToolTip(wx.ToolTip(_(u"Aller à la première page")))
        liste_controles[2].SetToolTip(wx.ToolTip(_(u"Aller à la page précédente")))
        liste_controles[5].SetToolTip(wx.ToolTip(_(u"Aller à la page suivante")))
        liste_controles[6].SetToolTip(wx.ToolTip(_(u"Aller à la dernière page")))
        liste_controles[7].SetToolTip(wx.ToolTip(_(u"Zoom arrière")))
        liste_controles[9].SetToolTip(wx.ToolTip(_(u"Zoom avant")))
        liste_controles[10].SetToolTip(wx.ToolTip(_(u"Fermer")))
        liste_controles[10].SetLabel(_(u"Fermer"))

        # Ajustement taille et position de la fenêtre
        if 'phoenix' not in wx.PlatformInfo:
            self.MakeModal(False)

        frame = wx.GetApp().GetTopWindow()
        self.SetPosition(frame.GetPosition())
        self.SetSize(frame.GetSize())




        


class FramePreview(wx.Frame):
    def __init__(self, parent, title="", printPreview=None):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.printPreview = printPreview
        
        self.panel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        
        # Commandes
        self.bouton_premier = wx.BitmapButton(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Premier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_precedent = wx.BitmapButton(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Precedent.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_suivant = wx.BitmapButton(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Suivant.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_dernier = wx.BitmapButton(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Dernier.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_fermer = wx.BitmapButton(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Fermer.png"), wx.BITMAP_TYPE_ANY))
        
        self.ctrl_zoom = wx.Slider(self.panel, -1, 100, 1, 200, size=(200, -1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.ctrl_zoom.SetTickFreq(5, 1)

        # Canvas preview
        self.previewCanvas = wx.PreviewCanvas(self.printPreview, self.panel, style=wx.SUNKEN_BORDER)
        self.printPreview.SetCanvas(self.previewCanvas)
        
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnPremierePage, self.bouton_premier)
        self.Bind(wx.EVT_BUTTON, self.OnPagePrecedente, self.bouton_precedent)
        self.Bind(wx.EVT_BUTTON, self.OnPageSuivante, self.bouton_suivant)
        self.Bind(wx.EVT_BUTTON, self.OnDernierePage, self.bouton_dernier)
        self.Bind(wx.EVT_BUTTON, self.OnFermer, self.bouton_fermer)
        self.Bind(wx.EVT_SCROLL, self.OnZoom, self.ctrl_zoom)
        
    def __set_properties(self):
##        _icon = wx.EmptyIcon()
##        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
##        self.SetIcon(_icon)
        self.SetMinSize((200, 200))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # Commandes
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=10, vgap=10, hgap=10)
        grid_sizer_commandes.Add(self.bouton_premier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_precedent, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_suivant, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_dernier, 0, 0, 0)
        grid_sizer_commandes.Add(self.ctrl_zoom, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_fermer, 0, 0, 0)
        
        grid_sizer_commandes.AddGrowableCol(5)
        grid_sizer_base.Add(grid_sizer_commandes, 0, wx.EXPAND | wx.ALL, 10)
        
        # Canvas
        grid_sizer_base.Add(self.previewCanvas, 0, wx.EXPAND, 0)
        
        self.panel.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        
        # Initialisation des contrôles
        self.OnZoom(None)


    def OnPageSetup(self, event): 
        self.listCtrlPrinter.PageSetup()
        self.RefreshPreview()

    def OnPrint(self, event): 
        self.listCtrlPrinter.Print()

    def OnPremierePage(self, event): # wxGlade: MyFrame.<event_handler>
        self.printPreview.SetCurrentPage(self.printPreview.GetMinPage())

    def OnPagePrecedente(self, event): # wxGlade: MyFrame.<event_handler>
        if self.printPreview.GetCurrentPage() > self.printPreview.GetMinPage():
            self.printPreview.SetCurrentPage(self.printPreview.GetCurrentPage() - 1)

    def OnPageSuivante(self, event): # wxGlade: MyFrame.<event_handler>
        if self.printPreview.GetCurrentPage() < self.printPreview.GetMaxPage():
            self.printPreview.SetCurrentPage(self.printPreview.GetCurrentPage() + 1)

    def OnDernierePage(self, event): # wxGlade: MyFrame.<event_handler>
        self.printPreview.SetCurrentPage(self.printPreview.GetMaxPage())

    def OnZoom(self, event): 
        zoom = self.ctrl_zoom.GetValue()
        self.printPreview.SetZoom(zoom)

    def RefreshPreview(self):
        self.printPreview.RenderPage(min(self.printPreview.GetCurrentPage(), self.printPreview.GetMaxPage()))
        self.previewCanvas.Refresh()
    
    def OnFermer(self, event):
        self.Destroy() 


