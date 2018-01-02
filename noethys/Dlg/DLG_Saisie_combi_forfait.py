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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB

from Ctrl import CTRL_Saisie_date

try: import psyco; psyco.full()
except: pass



class CTRL_Unites(wx.CheckListBox):
    def __init__(self, parent, listeUnites=[]):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.date = None
        self.listeUnites = listeUnites
        
        # Remplissage
        for label in self.listeUnites :
            self.Append(label)
                            
    def GetCoches(self):
        listeCoches = []
        NbreItems = len(self.listeUnites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeCoches.append(index)
        return listeCoches
    
    def SetCoches(self, listeCoches=[]):
        for index in listeCoches :
            self.Check(index)

# ------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, listeUnites=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_combi_forfait", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDactivite = IDactivite
        self.listeUnites = listeUnites
        
        # Date
        self.staticbox_date = wx.StaticBox(self, -1, _(u"Date"))
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date(self)
        self.bouton_calendrier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))

        # Unites
        self.staticbox_unites = wx.StaticBox(self, -1, _(u"Unités à combiner"))
        self.ctrl_unites = CTRL_Unites(self, self.listeUnites)
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalendrier, self.bouton_calendrier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une combinaison de forfait"))
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de la consommation")))
        self.bouton_calendrier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la date dans un calendrier")))
        self.ctrl_unites.SetToolTip(wx.ToolTip(_(u"Cochez les unités à combiner")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((350, 420))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites, wx.VERTICAL)
        staticbox_date = wx.StaticBoxSizer(self.staticbox_date, wx.VERTICAL)
        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_date.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.bouton_calendrier, 0, 0, 0)
        staticbox_date.Add(grid_sizer_date, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_date, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        staticbox_unites.Add(self.ctrl_unites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_unites, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonCalendrier(self, event): 
        import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date.SetDate(date)
        dlg.Destroy()
    
    def GetUnites(self):
        return self.ctrl_unites.GetCoches()
    
    def SetUnites(self, listeCoches=[]):
        return self.ctrl_unites.SetCoches(listeCoches)
    
    def GetDate(self):
        return self.ctrl_date.GetDate()
    
    def SetDate(self, date=None):
        if date != None :
            self.ctrl_date.SetDate(date)

    def OnBoutonOk(self, event): 
        date = self.GetDate()
        if date == None :
            dlg = wx.MessageDialog(self, _(u"La date que vous avez saisi ne semble pas valide !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return
        
        listeUnites = self.GetUnites()
        if len(listeUnites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une unité !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
                
        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()