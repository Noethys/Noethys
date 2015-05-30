#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.aui as aui

import DLG_Remplissage
import DLG_Nbre_inscrits



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
        
    def MAJ(self):
        self.ctrl_remplissage.MAJ() 
        self.ctrl_nbre_inscrits.MAJ() 
    
    def SetPageActive(self, index=0):
        self.SetSelection(index)
    
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