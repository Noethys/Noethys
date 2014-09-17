#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import CTRL_Bandeau
import OL_Soldes
import CTRL_Saisie_date



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = u"Vous pouvez ici consulter la liste des comptes des familles. Double-cliquez sur une ligne pour ouvrir la fiche famille correspondante. Utilisez le champ Date pour connaître la situation des comptes à une date précise."
        titre = u"Soldes des comptes"
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, u"Paramètres")
        self.label_date = wx.StaticText(self, -1, u"Date de la situation :")
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.label_filtres = wx.StaticText(self, -1, u"Filtres des soldes :")
        self.check_debit = wx.CheckBox(self, -1, u"Débiteurs")
        self.check_credit = wx.CheckBox(self, -1, u"Créditeurs")
        self.check_nul = wx.CheckBox(self, -1, u"Nuls")
        self.bouton_actualiser = wx.Button(self, -1, u"Actualiser")
        
        # Liste
##        self.ctrl_soldes = OL_Soldes.ListView(self, id=-1, name="OL_soldes", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.listviewAvecFooter = OL_Soldes.ListviewAvecFooter(self) 
        self.ctrl_soldes = self.listviewAvecFooter.GetListview()

        self.ctrl_recherche = OL_Soldes.BarreRecherche(self)
        
        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_CHECKBOX, self.OnFiltres, self.check_debit)
        self.Bind(wx.EVT_CHECKBOX, self.OnFiltres, self.check_credit)
        self.Bind(wx.EVT_CHECKBOX, self.OnFiltres, self.check_nul)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        
        # Init contrôles
        self.ctrl_date.SetDate(datetime.date.today()) 
        self.check_debit.SetValue(True)
        self.check_credit.SetValue(True)
        self.check_nul.SetValue(True)
        self.Actualiser() 

    def __set_properties(self):
        self.SetTitle(u"Soldes des comptes")
        self.bouton_ouvrir_fiche.SetToolTipString(u"Cliquez ici pour ouvrir la fiche de la famille sélectionnée dans la liste")
        self.bouton_apercu.SetToolTipString(u"Cliquez ici pour créer un aperçu de la liste")
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour imprimer la liste")
        self.bouton_texte.SetToolTipString(u"Cliquez ici pour exporter la liste au format Texte")
        self.bouton_excel.SetToolTipString(u"Cliquez ici pour exporter la liste au format Excel")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.ctrl_date.SetToolTipString(u"Veuillez saisir une date de situation")
        self.check_debit.SetToolTipString(u"Afficher les soldes débiteurs")
        self.check_credit.SetToolTipString(u"Afficher les soldes créditeurs")
        self.check_nul.SetToolTipString(u"Afficher les soldes nuls")
        self.SetMinSize((780, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Parametres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=9, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.label_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add( (5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.label_filtres, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.check_debit, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.check_credit, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.check_nul, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add( (5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.bouton_actualiser, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.AddGrowableCol(7)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Liste
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
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
    
    def OnChoixDate(self):
        self.Actualiser() 
        
    def OnFiltres(self, event=None):
        self.Actualiser() 
    
    def OnBoutonActualiser(self, event=None):
        self.Actualiser() 
        
    def Actualiser(self):
        date = self.ctrl_date.GetDate() 
        afficherDebit = self.check_debit.GetValue() 
        afficherCredit = self.check_credit.GetValue() 
        afficherNul = self.check_nul.GetValue() 
        self.ctrl_soldes.MAJ(date, afficherDebit, afficherCredit, afficherNul)
        
    def OuvrirFiche(self, event):
        self.ctrl_soldes.OuvrirFicheFamille(None)

    def Apercu(self, event):
        self.ctrl_soldes.Apercu(None)
        
    def Imprimer(self, event):
        self.ctrl_soldes.Imprimer(None)

    def ExportTexte(self, event):
        self.ctrl_soldes.ExportTexte(None)

    def ExportExcel(self, event):
        self.ctrl_soldes.ExportExcel(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedessoldes")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
