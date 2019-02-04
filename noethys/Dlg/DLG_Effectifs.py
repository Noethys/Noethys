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
import wx.lib.agw.aui as aui

from Dlg import DLG_Remplissage
from Dlg import DLG_Recap_evenements
from Dlg import DLG_Nbre_inscrits_2 as DLG_Nbre_inscrits
from Dlg import DLG_Tableau_bord_locations



class CTRL(aui.AuiNotebook):
    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent, agwStyle=aui.AUI_NB_BOTTOM | aui.AUI_NB_TAB_EXTERNAL_MOVE | aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE ) 
        self.parent = parent
        
        # CTRL Remplissage
        self.ctrl_remplissage = DLG_Remplissage.Panel(self)
        self.AddPage(self.ctrl_remplissage, _(u"Consommations"))
        try :
            self.SetPageTooltip(0, _(u"Affiche l'état des consommations. \nVous pouvez glisser-déposer cet onglet pour déplacer la page."))
        except :
            pass

        # CTRL Inscriptions
        self.ctrl_nbre_inscrits = DLG_Nbre_inscrits.Panel(self)
        self.AddPage(self.ctrl_nbre_inscrits, _(u"Inscriptions"))
        try :
            self.SetPageTooltip(1, _(u"Affiche l'état des inscriptions. \nVous pouvez glisser-déposer cet onglet pour déplacer la page."))
        except :
            pass

        # CTRL Evènements
        self.ctrl_evenements = DLG_Recap_evenements.Panel(self)
        self.AddPage(self.ctrl_evenements, _(u"Evènements"))
        try :
            self.SetPageTooltip(2, _(u"Affiche l'état des évènements. \nVous pouvez glisser-déposer cet onglet pour déplacer la page."))
        except :
            pass

        # CTRL Locations
        self.ctrl_locations = DLG_Tableau_bord_locations.Panel(self)
        self.AddPage(self.ctrl_locations, _(u"Locations"))
        try :
            self.SetPageTooltip(3, _(u"Affiche l'état des locations. \nVous pouvez glisser-déposer cet onglet pour déplacer la page."))
        except :
            pass

        # Bind
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        self.MAJ()

    def MAJ(self):
        if self.GetPageActive() == 0 :
            self.ctrl_remplissage.MAJ()
        if self.GetPageActive() == 1 :
            self.ctrl_nbre_inscrits.MAJ()
        if self.GetPageActive() == 2 :
            self.ctrl_evenements.MAJ()
        if self.GetPageActive() == 3 :
            self.ctrl_locations.MAJ()

    def SetPageActive(self, index=0):
        try :
            self.SetSelection(index)
        except :
            pass
    
    def GetPageActive(self):
        return self.GetSelection()
        
    def SetDictDonnees(self, dictDonnees={}):
        self.ctrl_remplissage.SetDictDonnees(dictDonnees)
        
    def OuvrirListeAttente(self):
        self.ctrl_remplissage.OuvrirListeAttente() 
        
    def OuvrirListeRefus(self):
        self.ctrl_remplissage.OuvrirListeRefus() 

        
        
        
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()    
