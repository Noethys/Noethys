#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Saisie_date


class Panel(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_generalites", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Dates du contrat"))
        self.label_date_debut = wx.StaticText(self, -1, _(u"Du"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Paramètres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Autres paramètres"))
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début du contrat")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin du contrat")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez d'éventuelles observations")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Période
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        x = self.label_observations.GetSize()[0] - self.label_date_debut.GetSize()[0] - 10
        grid_sizer_periode.Add( (x, 5), 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_debut, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 1, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_fin, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 1, wx.EXPAND, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_periode, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Paramètres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_parametres.Add(self.label_observations, 1, wx.ALIGN_RIGHT, 0)
        grid_sizer_parametres.Add(self.ctrl_observations, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(1)
        staticbox_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def Validation(self):
        if self.ctrl_date_debut.Validation() == False or self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de contrat valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        if self.ctrl_date_fin.Validation() == False or self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de contrat valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        if self.ctrl_date_debut.GetDate() > self.ctrl_date_fin.GetDate() :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas avoir une date de début de contrat supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        # Tests
        dict_valeurs = {
            "date_debut" : self.ctrl_date_debut.GetDate(),
            "date_fin" : self.ctrl_date_fin.GetDate(),
            }
        if self.clsbase.Calculer(mode_test=True, dict_valeurs=dict_valeurs) == False :
            return False

        return True

    def Sauvegarde(self):
        dictValeurs = {
            "date_debut" : self.ctrl_date_debut.GetDate(),
            "date_fin" : self.ctrl_date_fin.GetDate(),
            "observations" : self.ctrl_observations.GetValue(),
        }
        self.clsbase.SetValeurs(dictValeurs)

    def MAJ(self):
        self.clsbase.Calculer()

        if self.MAJ_effectuee == False :
            date_debut = self.clsbase.GetValeur("date_debut")
            date_fin = self.clsbase.GetValeur("date_fin")
            observations = self.clsbase.GetValeur("observations")

            self.ctrl_date_debut.SetDate(date_debut)
            self.ctrl_date_fin.SetDate(date_fin)
            if observations != None :
                self.ctrl_observations.SetValue(observations)

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