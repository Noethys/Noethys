#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import wx.lib.agw.aui as aui
from Dlg.DLG_Noedoc import Panel_canvas, Panel_infos, Panel_commandes, Panel_proprietes_objet, Panel_proprietes_image_interactive
from Utils import UTILS_Dialogs



class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=None, nom="", observations="", categorie="categorie_produits", IDdonnee=None, champs_interactifs={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDmodele = IDmodele
        self.IDdonnee = IDdonnee

        # DLG Attente
        dlgAttente = wx.BusyInfo(_(u"Veuillez patienter..."), self.parent)

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        # Propriétés
        self.SetMinSize((920, 740))

        # Création des widgets
        couleur_zone_travail = wx.Colour(255, 255, 255)
        self.ctrl_canvas = Panel_canvas(self, IDmodele=IDmodele, categorie=categorie, couleur_zone_travail=couleur_zone_travail, IDdonnee=IDdonnee, champs_interactifs=champs_interactifs)

        # Barres d'outils
        self.toolbar1 = self.MakeToolBar1()
        self.toolbar2 = self.MakeToolBar2()

        # Création des panels détachables
        self.ctrl_infos = Panel_infos(self)
        self.ctrl_commandes = Panel_commandes(self)
        self.ctrl_proprietes_doc = Panel_proprietes_image_interactive(self, self.ctrl_canvas, categorie=categorie)
        self.ctrl_proprietes_objet = Panel_proprietes_objet(self, self.ctrl_canvas)
        self.ctrl_canvas.ctrl_proprietes = self.ctrl_proprietes_objet

        # Saisit le nom de l'image
        self.ctrl_proprietes_doc.SetNom(nom)
        self.ctrl_proprietes_doc.SetObservations(observations)

        # Création des panels amovibles
        self._mgr.AddPane(self.ctrl_infos, aui.AuiPaneInfo().
                          Name("infos").Caption(_(u"Infos")).
                          Bottom().Layer(0).Position(1).CaptionVisible(False).CloseButton(False).MaximizeButton(False).MinSize((-1, 18)))

        self._mgr.AddPane(self.ctrl_commandes, aui.AuiPaneInfo().
                          Name("commandes").Caption(_(u"Commandes")).
                          Bottom().Layer(1).Position(2).CaptionVisible(False).CloseButton(False).MaximizeButton(False).MinSize((-1, 50)))

        self._mgr.AddPane(self.ctrl_proprietes_doc, aui.AuiPaneInfo().
                          Name("proprietes_doc").Caption(_(u"Propriétés de l'image")).
                          Right().Layer(1).Position(1).Fixed().CloseButton(False).MaximizeButton(False))

        self._mgr.AddPane(self.ctrl_proprietes_objet, aui.AuiPaneInfo().
                          Name("proprietes_objet").Caption(_(u"Propriétés de l'objet")).
                          Right().Layer(1).Position(2).CloseButton(False).MaximizeButton(False).MinSize((160, -1)))

        # Création du panel central
        self._mgr.AddPane(self.ctrl_canvas, aui.AuiPaneInfo().Name("canvas").CenterPane())

        # Création des barres d'outils
        self._mgr.AddPane(self.toolbar1, aui.AuiPaneInfo().
                          Name("barreOutil_modes").Caption("Modes").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(True))

        self._mgr.AddPane(self.toolbar2, aui.AuiPaneInfo().
                          Name("barreOutils_objets").Caption("Objets").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(True))

        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)

        # Logo
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle(u"Editeur d'images interactives")

        # Init Canvas
        self.CenterOnScreen()
        self.ctrl_canvas.Init_canvas()

        del dlgAttente

        # Importation
        if self.IDmodele != None:
            self.ctrl_canvas.Importation(self.IDmodele)

        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()
        self.ctrl_canvas.OnOutil_ajuster(None)


    def MakeToolBar1(self):
        tbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbar.SetToolBitmapSize(wx.Size(32, 32))

        ID_OUTIL_CURSEUR = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_CURSEUR, _(u"Curseur"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Curseur.png"), wx.BITMAP_TYPE_ANY), _(u"Curseur"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_curseur, id=ID_OUTIL_CURSEUR)
        tbar.ToggleTool(ID_OUTIL_CURSEUR, True)

        ID_OUTIL_DEPLACER = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_DEPLACER, _(u"Déplacer"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Main.png"), wx.BITMAP_TYPE_ANY), _(u"Déplacer"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_deplacer, id=ID_OUTIL_DEPLACER)

        ID_OUTIL_ZOOM_OUT = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_OUT, _(u"Zoom arrière"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_moins.png"), wx.BITMAP_TYPE_ANY), _(u"Zoom arrière"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_zoom_moins, id=ID_OUTIL_ZOOM_OUT)

        ID_OUTIL_ZOOM_IN = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_IN, _(u"Zoom avant"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_plus.png"), wx.BITMAP_TYPE_ANY), _(u"Zoom avant"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_zoom_plus, id=ID_OUTIL_ZOOM_IN)

        tbar.AddSeparator()

        ID_OUTIL_ZOOM_AJUSTER = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_AJUSTER, _(u"Ajuster et centrer l'affichage"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Ajuster.png"), wx.BITMAP_TYPE_ANY), _(u"Ajuster et centrer l'affichage"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_ajuster, id=ID_OUTIL_ZOOM_AJUSTER)

        tbar.AddSeparator()

        ID_OUTIL_AFFICHAGE_APERCU = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_APERCU, _(u"Afficher un aperçu PDF"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Pdf.png"), wx.BITMAP_TYPE_ANY), _(u"Afficher un aperçu PDF"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnAffichage_apercu, id=ID_OUTIL_AFFICHAGE_APERCU)

        tbar.Realize()
        return tbar

    def MakeToolBar2(self):
        tbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbar.SetToolBitmapSize(wx.Size(32, 32))

        ID_OUTIL_OBJET_TEXTE_BLOC = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_OBJET_TEXTE_BLOC, _(u"Insérer un bloc de texte multi-lignes"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Texte_ligne.png"), wx.BITMAP_TYPE_ANY), _(u"Insérer un bloc de texte multi-lignes"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_texteBloc, id=ID_OUTIL_OBJET_TEXTE_BLOC)

        ID_OUTIL_OBJET_RECTANGLE = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_OBJET_RECTANGLE, _(u"Insérer un rectangle"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Rectangle.png"), wx.BITMAP_TYPE_ANY), _(u"Insérer un rectangle"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_rectangle, id=ID_OUTIL_OBJET_RECTANGLE)

        ID_OUTIL_OBJET_LIGNE = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_OBJET_LIGNE, _(u"Insérer une ligne"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Ligne.png"), wx.BITMAP_TYPE_ANY), _(u"Insérer une ligne"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_ligne, id=ID_OUTIL_OBJET_LIGNE)

        ID_OUTIL_OBJET_CERCLE = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_OBJET_CERCLE, _(u"Insérer une ellipse"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Cercle.png"), wx.BITMAP_TYPE_ANY), _(u"Insérer une ellipse"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_cercle, id=ID_OUTIL_OBJET_CERCLE)

        ID_OUTIL_OBJET_POLYGONE = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_OBJET_POLYGONE, _(u"Insérer un polygone"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Polygone.png"), wx.BITMAP_TYPE_ANY), _(u"Insérer un polygone"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_polygone, id=ID_OUTIL_OBJET_POLYGONE)

        ID_OUTIL_OBJET_POLYLINE = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_OBJET_POLYLINE, _(u"Dessiner un polygone à main levée"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Polyline.png"), wx.BITMAP_TYPE_ANY), _(u"Dessiner un polygone à main levée"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_polyline, id=ID_OUTIL_OBJET_POLYLINE)

        ID_OUTIL_OBJET_IMAGE_DROPDOWN = wx.Window.NewControlId()
        ID_OUTIL_OBJET_IMAGE = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_OBJET_IMAGE_DROPDOWN, _(u"Insérer une image"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Image.png"), wx.BITMAP_TYPE_ANY), _(u"Insérer une image"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_image, id=ID_OUTIL_OBJET_IMAGE)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.ctrl_canvas.OnDropDownImage, id=ID_OUTIL_OBJET_IMAGE_DROPDOWN)
        tbar.SetToolDropDown(ID_OUTIL_OBJET_IMAGE_DROPDOWN, True)

        tbar.Realize()
        return tbar

    def OnBoutonOk(self, event=None):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event=None):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def Quitter(self, enregistrer=True):
        # Quitter
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()

    def GetIDmodele(self, IDmodele=None):
        return self.ctrl_canvas.IDmodele






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    champs_interactifs = {
        1: u"Produit 1",
        2: u"Produit 2",
        3: u"Produit 3",
        4: u"Produit 4",
    }

    dialog_1 = Dialog(None, IDmodele=1, categorie="categorie_produits", champs_interactifs=champs_interactifs)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
