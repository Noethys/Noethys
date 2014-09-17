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
import CTRL_Bandeau
import OL_Verification_ventilation
import wx.lib.agw.hyperlink as Hyperlink



class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        if self.URL == "tout" :
            self.parent.ctrl_reglements.CocheTout() 
        if self.URL == "rien" :
            self.parent.ctrl_reglements.CocheRien() 
        self.UpdateLink()



def Verification(IDcompte_payeur=None):
    """ Recherche s'il y a des soucis de ventilation """
    tracks = OL_Verification_ventilation.Importation(onlyNonVentiles=True, IDcompte_payeur=IDcompte_payeur)
    return tracks


class Dialog(wx.Dialog):
    def __init__(self, parent, tracks=None, IDcompte_payeur=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = u"Vous pouvez ici consulter la liste des familles pour lesquelles il est possible de ventiler un ou plusieurs règlements. Cette opération est nécessaire avant l'édition de documents tels que les factures ou les attestations de présence. Double-cliquez sur une ligne pour ouvrir la fiche famille correspondante."
        titre = u"Vérification de la ventilation"
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Repartition.png")
        
        self.listviewAvecFooter = OL_Verification_ventilation.ListviewAvecFooter(self, kwargs={"tracks" : tracks, "IDcompte_payeur" : IDcompte_payeur, "onlyNonVentiles" : True}) 
        self.ctrl_reglements = self.listviewAvecFooter.GetListview()
        self.ctrl_reglements.MAJ() 
        
##        self.ctrl_reglements = OL_Verification_ventilation.ListView(self, id=-1, tracks=tracks, IDcompte_payeur=IDcompte_payeur, onlyNonVentiles=True, name="OL_reglements", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
##        self.ctrl_reglements.MAJ() 
        self.ctrl_recherche = OL_Verification_ventilation.BarreRecherche(self)

        self.hyper_tout = Hyperlien(self, label=u"Tout cocher", infobulle=u"Cliquez ici pour tout cocher", URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=u"Tout décocher", infobulle=u"Cliquez ici pour tout décocher", URL="rien")

        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ventilation = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ventilation_automatique.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonVentilation, self.bouton_ventilation)

    def __set_properties(self):
        self.SetTitle(u"Vérification de la ventilation")
        self.bouton_ouvrir_fiche.SetToolTipString(u"Cliquez ici pour ouvrir la fiche famille sélectionnée dans la liste")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize((780, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_options.Add((10, 10), 0, 0, 0)
        grid_sizer_options.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_gauche.Add(grid_sizer_options, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ventilation, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OuvrirFiche(self, event):
        self.ctrl_reglements.OuvrirFicheFamille(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Vrifierlaventilation")

    def OnBoutonVentilation(self, event):
        """ Ventilation automatique """    
        if len(self.ctrl_reglements.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

        # Création du menu contextuel
        menuPop = wx.Menu()
        
        item = wx.MenuItem(menuPop, 201, u"Uniquement la ligne sélectionnée")
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_reglements.VentilationAuto, id=201)
        if noSelection == True : item.Enable(False)
        
        item = wx.MenuItem(menuPop, 202, u"Uniquement les lignes cochées")
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_reglements.VentilationAuto, id=202)
        if len(self.ctrl_reglements.GetTracksCoches()) == 0 : item.Enable(False)

        item = wx.MenuItem(menuPop, 203, u"Toutes les lignes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_reglements.VentilationAuto, id=203)

        self.PopupMenu(menuPop)
        menuPop.Destroy()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
