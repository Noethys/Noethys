#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.hyperlink as Hyperlink
from Ol import OL_Locations
from Utils import UTILS_Utilisateurs




class CTRL(wx.Panel):
    def __init__(self, parent, filtres=[]):
        wx.Panel.__init__(self, parent, id=-1, name="CTRL_Liste_locations", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Liste des locations
        self.listviewAvecFooter = OL_Locations.ListviewAvecFooter(self, kwargs={"checkColonne" : True})
        self.ctrl_locations = self.listviewAvecFooter.GetListview()

        # Commandes de liste
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_email = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_liste_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_liste_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_liste_export_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_liste_export_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        
        # Options de liste
        self.ctrl_recherche = OL_Locations.CTRL_Outils(self, listview=self.ctrl_locations, afficherCocher=True)

        self.check_locations_actives = wx.CheckBox(self, -1, _(u"Afficher uniquement les locations en cours"))
        self.check_locations_actives.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        self.check_locations_actives.SetValue(True)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckActives, self.check_locations_actives)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonListeApercu, self.bouton_liste_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonListeImprimer, self.bouton_liste_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonListeExportTexte, self.bouton_liste_export_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonListeExportExcel, self.bouton_liste_export_excel)

        # Init contrôles
        self.ctrl_locations.afficher_uniquement_actives = self.check_locations_actives.GetValue()

    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu de la location sélectionnée")))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Cliquez ici envoyer la location sélectionnée par Email")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la location sélectionnée ou les locations cochées")))
        self.bouton_liste_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de cette liste")))
        self.bouton_liste_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer cette liste")))
        self.bouton_liste_export_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter cette liste au format Texte")))
        self.bouton_liste_export_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter cette liste au format Excel")))
        self.check_locations_actives.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher uniquement les locations actives")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)

        grid_sizer_liste = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_liste.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        
        # Commandes de liste
        grid_sizer_commandes = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)

        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)

        grid_sizer_commandes.Add(self.bouton_liste_apercu, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_liste_imprimer, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)
        
        grid_sizer_commandes.Add(self.bouton_liste_export_texte, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_liste_export_excel, 0, 0, 0)
        grid_sizer_liste.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_outils = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=30)
        grid_sizer_outils.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_outils.Add(self.check_locations_actives, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_outils.AddGrowableCol(0)
        grid_sizer_liste.Add(grid_sizer_outils, 1, wx.EXPAND, 0)
        
        grid_sizer_liste.AddGrowableRow(0)
        grid_sizer_liste.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_liste, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def OnCheckActives(self, event):
        self.ctrl_locations.afficher_uniquement_actives = self.check_locations_actives.GetValue()
        self.ctrl_locations.MAJ()

    def OnBoutonApercu(self, event): 
        self.ctrl_locations.Reedition(None)

    def OnBoutonEmail(self, event): 
        self.ctrl_locations.EnvoyerEmail(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_locations.Supprimer(None)

    def OnBoutonListeApercu(self, event): 
        self.ctrl_locations.Apercu(None)

    def OnBoutonListeImprimer(self, event): 
        self.ctrl_locations.Imprimer(None)

    def OnBoutonListeExportTexte(self, event): 
        self.ctrl_locations.ExportTexte(None)

    def OnBoutonListeExportExcel(self, event): 
        self.ctrl_locations.ExportExcel(None)
    
    def GetTracksCoches(self):
        return self.ctrl_locations.GetTracksCoches()

    def GetTracksTous(self):
        return self.ctrl_locations.GetTracksTous()

    def MAJ(self):
        self.ctrl_locations.MAJ()
        
    def SetFiltres(self, filtres=[]):
        self.ctrl_locations.SetFiltres(filtres)






class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)        
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ() 
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        pass

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


