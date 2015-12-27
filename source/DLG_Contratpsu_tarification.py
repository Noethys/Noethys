#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import OL_Contratspsu_tarifs
import CTRL_Saisie_duree


class Panel(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_tarification", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        # Tarifs
        self.staticbox_tarifs_staticbox = wx.StaticBox(self, -1, _(u"Tarifs"))
        self.listviewAvecFooter = OL_Contratspsu_tarifs.ListviewAvecFooter(self, kwargs={"clsbase" : clsbase})
        self.ctrl_tarifs = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Contratspsu_tarifs.CTRL_Outils(self, listview=self.ctrl_tarifs, afficherCocher=False)
        if self.parent.GetName() == "notebook" :
            self.ctrl_recherche.SetBackgroundColour(self.parent.GetThemeBackgroundColour())

        self.bouton_tarifs_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_tarifs_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_tarifs_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_tarifs_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_tarifs_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_regularisation = wx.StaticText(self, -1, _(u"Heures de régularisation :"))
        self.ctrl_regularisation = CTRL_Saisie_duree.CTRL(self)

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Ajouter, self.bouton_tarifs_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Modifier, self.bouton_tarifs_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Supprimer, self.bouton_tarifs_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Apercu, self.bouton_tarifs_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Imprimer, self.bouton_tarifs_imprimer)

    def __set_properties(self):
        self.bouton_tarifs_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un tarif"))
        self.bouton_tarifs_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le tarif sélectionné"))
        self.bouton_tarifs_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le tarif sélectionné"))
        self.bouton_tarifs_apercu.SetToolTipString(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste"))
        self.bouton_tarifs_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.ctrl_regularisation.SetToolTipString(_(u"Saisissez ici le nombre d'heure de régularisation (en positif ou négatif)"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Tarifs
        staticbox_tarifs = wx.StaticBoxSizer(self.staticbox_tarifs_staticbox, wx.VERTICAL)
        grid_sizer_tarifs = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        grid_sizer_tarifs.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)

        grid_sizer_boutons_tarifs = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_tarifs.Add(self.bouton_tarifs_ajouter, 0, 0, 0)
        grid_sizer_boutons_tarifs.Add(self.bouton_tarifs_modifier, 0, 0, 0)
        grid_sizer_boutons_tarifs.Add(self.bouton_tarifs_supprimer, 0, 0, 0)
        grid_sizer_boutons_tarifs.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons_tarifs.Add(self.bouton_tarifs_apercu, 0, 0, 0)
        grid_sizer_boutons_tarifs.Add(self.bouton_tarifs_imprimer, 0, 0, 0)
        grid_sizer_tarifs.Add(grid_sizer_boutons_tarifs, 1, wx.EXPAND, 0)

        grid_sizer_tarifs.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)

        grid_sizer_tarifs.AddGrowableRow(0)
        grid_sizer_tarifs.AddGrowableCol(0)
        staticbox_tarifs.Add(grid_sizer_tarifs, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_tarifs, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=8, vgap=10, hgap=10)
        grid_sizer_options.Add(self.label_regularisation, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_regularisation, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def Validation(self):
        if len(self.ctrl_tarifs.GetTracks()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement au moins un tarif !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.clsbase.Calculer(mode_test=True) == False :
            return False

        return True

    def Sauvegarde(self):
        self.clsbase.SetValeur("tracks_tarifs", self.ctrl_tarifs.GetTracks())
        self.clsbase.SetValeur("duree_heures_regularisation", self.ctrl_regularisation.GetValue())

    def MAJ(self):
        self.clsbase.Calculer()

        if self.MAJ_effectuee == False :
            # Liste des tarifs
            tracks_tarifs = self.clsbase.GetValeur("tracks_tarifs", [])
            self.ctrl_tarifs.SetTracks(tracks_tarifs)

            # Heures de régularisation
            duree_heures_regularisation = self.clsbase.GetValeur("duree_heures_regularisation", datetime.timedelta(0))
            if duree_heures_regularisation != None :
                self.ctrl_regularisation.SetValue(duree_heures_regularisation)

        self.MAJ_effectuee = True


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()