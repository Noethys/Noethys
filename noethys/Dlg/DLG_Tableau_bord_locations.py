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
import sys
from Dlg import DLG_Categories_produits_images
from Dlg import DLG_Produits_liste
from Dlg import DLG_Locations
from Dlg import DLG_Locations_demandes

from Utils import UTILS_Utilisateurs
import wx.lib.agw.labelbook as LB



class Page_locations(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_locations = OL_Locations.ListView(self, id=-1, name="OL_locations", style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.ctrl_locations.SetMinSize((50, 50))
        self.ctrl_recherche = OL_Produits.CTRL_Outils(self, listview=self.ctrl_locations)

        self.check_locations_actives = wx.CheckBox(self, -1, _(u"Afficher uniquement les locations en cours"))
        self.check_locations_actives.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        self.check_locations_actives.SetValue(True)

        self.bouton_ajouter_location = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_location = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_location = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckActives, self.check_locations_actives)
        self.Bind(wx.EVT_BUTTON, self.ctrl_locations.Ajouter, self.bouton_ajouter_location)
        self.Bind(wx.EVT_BUTTON, self.ctrl_locations.Modifier, self.bouton_modifier_location)
        self.Bind(wx.EVT_BUTTON, self.ctrl_locations.Supprimer, self.bouton_supprimer_location)

        # Propriétés
        self.bouton_ajouter_location.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une location")))
        self.bouton_modifier_location.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la location sélectionnée")))
        self.bouton_supprimer_location.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la location sélectionnée")))
        self.check_locations_actives.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher uniquement les locations actives")))

        # --- Layout ---
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)

        # Locations
        grid_sizer_locations = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_locations.Add(self.ctrl_locations, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter_location, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier_location, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer_location, 0, wx.ALL, 0)
        grid_sizer_locations.Add(grid_sizer_boutons, 1, wx.ALL, 0)

        grid_sizer_outils = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=30)
        grid_sizer_outils.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_outils.Add(self.check_locations_actives, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_outils.AddGrowableCol(0)
        grid_sizer_locations.Add(grid_sizer_outils, 1, wx.EXPAND, 0)

        grid_sizer_locations.AddGrowableCol(0)
        grid_sizer_locations.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_locations, 1, wx.EXPAND | wx.LEFT, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()

        # Init contrôles
        self.ctrl_locations.afficher_uniquement_actives = self.check_locations_actives.GetValue()

    def OnCheckActives(self, event):
        self.ctrl_locations.afficher_uniquement_actives = self.check_locations_actives.GetValue()
        self.ctrl_locations.MAJ()

    def MAJ(self):
        self.ctrl_locations.MAJ()


class Page_demandes(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille

        # Filtres
        self.check_attente_avec_possibilites = wx.CheckBox(self, -1, _(u"Demandes avec disponibilités"))
        self.check_attente_sans_possibilites = wx.CheckBox(self, -1, _(u"Demandes sans disponibilités"))
        self.check_attente_refusees = wx.CheckBox(self, -1, _(u"Demandes refusées"))
        self.check_attente_attribuees = wx.CheckBox(self, -1, _(u"Demandes attribuées"))

        self.ctrl_demandes = OL_Locations_demandes.ListView(self, IDfamille=IDfamille, id=-1, name="OL_Demandes_locations", style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.ctrl_demandes.SetMinSize((50, 50))

        self.bouton_ajouter_demande = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_demande = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_demande = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.Ajouter, self.bouton_ajouter_demande)
        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.Modifier, self.bouton_modifier_demande)
        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.Supprimer, self.bouton_supprimer_demande)

        # Propriétés
        self.bouton_ajouter_demande.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une demande de location")))
        self.bouton_modifier_demande.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la demande de location sélectionnée")))
        self.bouton_supprimer_demande.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la demande de location sélectionnée")))

        # --- Layout ---
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)

        # Demandes
        grid_sizer_demandes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_demandes.Add(self.ctrl_demandes, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter_demande, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier_demande, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer_demande, 0, wx.ALL, 0)
        grid_sizer_demandes.Add(grid_sizer_boutons, 1, wx.ALL, 0)

        grid_sizer_demandes.AddGrowableCol(0)
        grid_sizer_demandes.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_demandes, 1, wx.EXPAND | wx.LEFT, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()

    def MAJ(self):
        self.ctrl_demandes.MAJ()



class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Tableau_bord_locations", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille

        self.ctrl_labelbook = wx.Toolbook(self, -1, style=wx.BK_TOP) # LB.FlatImageBook(self, -1, agwStyle=LB.INB_TOP)
        self.InitLabelbook()

        # --- Layout ---
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_labelbook, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

    def InitLabelbook(self):
        bordure = 5

        self.listePages = [
            (_("images"), _(u"Images"), DLG_Categories_produits_images.Panel(self.ctrl_labelbook, bordure=bordure), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Image_interactive.png'), wx.BITMAP_TYPE_PNG)),
            (_("produits"), _(u"Produits"), DLG_Produits_liste.Panel(self.ctrl_labelbook, bordure=bordure), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Produit.png'), wx.BITMAP_TYPE_PNG)),
            (_("locations"), _(u"Locations"), DLG_Locations.Panel(self.ctrl_labelbook, bordure=bordure), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Location.png'), wx.BITMAP_TYPE_PNG)),
            (_("demandes"), _(u"Demandes"), DLG_Locations_demandes.Panel(self.ctrl_labelbook, bordure=bordure), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Location_demande.png'), wx.BITMAP_TYPE_PNG)),
            ]

        il = wx.ImageList(32, 32)
        index = 0
        for code, label, ctrl, image in self.listePages:
            il.Add(image)
            index += 1
        self.ctrl_labelbook.AssignImageList(il)

        # Binds
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.OnPageChanged, self.ctrl_labelbook)

        index = 0
        for code, label, ctrl, image in self.listePages:
            self.ctrl_labelbook.AddPage(ctrl, label, imageId=index)
            index += 1

    def OnPageChanged(self, event):
        """ Quand une page du tookbook est sélectionnée """
        index = event.GetSelection()
        self.MAJpage(index)
        event.Skip()

    def MAJpage(self, index=0):
        page = self.listePages[index][2]
        page.MAJ()

    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_locations", "consulter", afficheMessage=False) == False :
            return False
        return True

    def MAJ(self):
        """ MAJ de la page """
        index = self.ctrl_labelbook.GetSelection()
        self.MAJpage(index)
        self.Refresh()

        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel, IDfamille=3)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()