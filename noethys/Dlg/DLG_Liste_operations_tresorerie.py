#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Operations_tresorerie
from Ctrl import CTRL_Saisie_compte
import GestionDB


ID_AJOUTER_DEBIT = wx.NewId()
ID_AJOUTER_CREDIT = wx.NewId()
ID_AJOUTER_VIREMENT = wx.NewId()




class Dialog(wx.Dialog):
    def __init__(self, parent, IDcompte_bancaire=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez consulter ici la liste des opérations d'un compte bancaire. Sélectionnez un compte dans la liste déroulante et ajoutez rapidement des opérations grâce aux boutons raccourcis situés au-dessus de la liste.")
        titre = _(u"Liste des opérations de trésorerie")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Operations.png")
        
        # Barre d'outils
        self.barreOutils = UTILS_Adaptations.ToolBar(self, -1, style =
            wx.TB_HORIZONTAL 
            | wx.NO_BORDER
            | wx.TB_FLAT
            | wx.TB_TEXT
            | wx.TB_HORZ_LAYOUT
            | wx.TB_NODIVIDER
            )
        self.barreOutils.AddLabelTool(ID_AJOUTER_DEBIT, label=_(u"Ajouter un débit"), bitmap=wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Addition.png"), wx.BITMAP_TYPE_PNG), shortHelp=_(u"Ajouter une opération au débit"), longHelp=_(u"Ajouter une opération au débit"))
        self.barreOutils.AddLabelTool(ID_AJOUTER_CREDIT, label=_(u"Ajouter un crédit"), bitmap=wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Addition.png"), wx.BITMAP_TYPE_PNG), shortHelp=_(u"Ajouter une opération au crédit"), longHelp=_(u"Ajouter une opération au crédit"))
        self.barreOutils.AddLabelTool(ID_AJOUTER_VIREMENT, label=_(u"Ajouter un virement"), bitmap=wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Addition.png"), wx.BITMAP_TYPE_PNG), shortHelp=_(u"Ajouter un virement"), longHelp=_(u"Ajouter un virement"))
        try :
            self.barreOutils.AddStretchableSpace()
        except :
            self.barreOutils.AddSeparator()
        self.ctrl_comptes = CTRL_Saisie_compte.CTRL(self.barreOutils, IDcompte_bancaire=IDcompte_bancaire, size=(400, -1))
        self.barreOutils.AddControl(self.ctrl_comptes)
        self.barreOutils.Realize()

        # Liste des opérations
        self.ctrl_operations = OL_Operations_tresorerie.ListView(self, id=-1, IDcompte_bancaire=self.ctrl_comptes.GetID(), style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_soldes = OL_Operations_tresorerie.BarreSoldes(self, listview=self.ctrl_operations)
        self.ctrl_operations.ctrl_soldes = self.ctrl_soldes
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_tresorerie = CTRL_Bouton_image.CTRL(self, texte=_(u"Trésorerie"), cheminImage="Images/32x32/Tresorerie.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixCompte, self.ctrl_comptes)
        
        self.Bind(wx.EVT_TOOL, self.ctrl_operations.AjouterDebit, id=ID_AJOUTER_DEBIT)
        self.Bind(wx.EVT_TOOL, self.ctrl_operations.AjouterCredit, id=ID_AJOUTER_CREDIT)
        self.Bind(wx.EVT_TOOL, self.ctrl_operations.AjouterVirement, id=ID_AJOUTER_VIREMENT)
        self.Bind(wx.EVT_BUTTON, self.ctrl_operations.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_operations.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_operations.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_operations.ExportExcel, self.bouton_excel)

        self.Bind(wx.EVT_BUTTON, self.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_operations.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_operations.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTresorerie, self.bouton_tresorerie)

        # Init contrôles
        self.ctrl_operations.MAJ()
        

    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une opération")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'opération sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'opération sélectionné dans la liste")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_tresorerie.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir le suivi de la trésorerie")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((980, 750))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.barreOutils, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_gauche.Add(self.ctrl_operations, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_soldes, 0, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
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
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_tresorerie, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesoperationsdetresorerie")
    
    def OnBoutonTresorerie(self, event):
        from Dlg import DLG_Tresorerie
        dlg = DLG_Tresorerie.Dialog(self, IDcompte_bancaire=self.ctrl_comptes.GetID())
        dlg.ShowModal() 
        dlg.Destroy()
        
    def OnChoixCompte(self, event):
        IDcompte = self.ctrl_comptes.GetID() 
        self.ctrl_operations.SetCompteBancaire(IDcompte)
        self.ctrl_operations.MAJ() 
        
    def Ajouter(self, event=None):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter une opération au débit"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Addition.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_operations.AjouterDebit, id=10)

        item = wx.MenuItem(menuPop, 20, _(u"Ajouter une opération au crédit"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Addition.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_operations.AjouterCredit, id=20)

        item = wx.MenuItem(menuPop, 30, _(u"Ajouter un virement"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Addition.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_operations.AjouterVirement, id=30)

        self.PopupMenu(menuPop)
        menuPop.Destroy()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcompte_bancaire=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
