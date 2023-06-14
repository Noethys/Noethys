#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ol import OL_Badgeage_consommations



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez consulter ici la liste des consommations badgées sur une période choisie. Commencez par sélectionner une période de référence puis actualisez l'affichage de la liste.")
        titre = _(u"Consommations badgées")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Badgeage.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.label_date_debut = wx.StaticText(self, -1, _(u"Période :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_date_debut.SetDate(datetime.date.today())
        self.ctrl_date_fin.SetDate(datetime.date.today())
        self.bouton_actualiser = wx.Button(self, -1, _(u"Actualiser"))
        
        # Log
        self.box_log_staticbox = wx.StaticBox(self, -1, _(u"Consommations"))

        self.ctrl_listview = OL_Badgeage_consommations.ListView(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((100, 100))
        self.ctrl_recherche = OL_Badgeage_consommations.CTRL_Outils(self, listview=self.ctrl_listview)
        
        self.bouton_log_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_log_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_log_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_log_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Texte.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Apercu, self.bouton_log_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Imprimer, self.bouton_log_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportExcel, self.bouton_log_excel)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportTexte, self.bouton_log_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        
        # Init contrôles
        self.Actualiser() 
        
    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date")))
        self.bouton_log_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un apercu avant impression")))
        self.bouton_log_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer")))
        self.bouton_log_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_log_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((870, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=6, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add( (5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.bouton_actualiser, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        
        grid_sizer_parametres.AddGrowableCol(1)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Log
        box_log = wx.StaticBoxSizer(self.box_log_staticbox, wx.VERTICAL)
        grid_sizer_log = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_log.Add(self.ctrl_listview, 1, wx.EXPAND, 0)
        
        # Commandes
        grid_sizer_log_commandes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_log_commandes.Add(self.bouton_log_apercu, 0, 0, 0)
        grid_sizer_log_commandes.Add(self.bouton_log_imprimer, 0, 0, 0)
        grid_sizer_log_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_log_commandes.Add(self.bouton_log_excel, 0, 0, 0)
        grid_sizer_log_commandes.Add(self.bouton_log_texte, 0, 0, 0)
        grid_sizer_log.Add(grid_sizer_log_commandes, 1, wx.EXPAND, 0)
        grid_sizer_log.AddGrowableRow(0)
        grid_sizer_log.AddGrowableCol(0)
        box_log.Add(grid_sizer_log, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_log.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)

        grid_sizer_base.Add(box_log, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()  

    def OnBoutonActualiser(self, event=None):
        self.Actualiser() 
        
    def Actualiser(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        self.ctrl_listview.SetPeriode(date_debut, date_fin)
        self.ctrl_listview.MAJ()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Badgeage")
        
    def OnBoutonFermer(self, event): 
        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()