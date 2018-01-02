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
import wx.animate
import time

from Ctrl import CTRL_Bandeau

import smartcard


def CheckLecteurs():
    try :
        if len(smartcard.System.readers()) == 0 :
            return False
        else :
            return True
    except :
        return False


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.IDbadge = None
        self.timer = wx.Timer(self, -1)

        # Bandeau
        titre = _(u"Scanner un badge RFID")
        intro = _(u"Veuillez scanner un badge dans votre lecteur RFID.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Rfid.png")
        
        self.panel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        self.ctrl_image = wx.animate.AnimationCtrl(self.panel, -1, wx.animate.Animation(Chemins.GetStaticPath("Images/Special/Attente.gif")))
        self.ctrl_image.SetUseWindowBackgroundColour()
        self.ctrl_image.Play()
            
        self.ctrl_label = wx.StaticText(self.panel, -1, _(u"Veuillez scanner un badge"))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
        # Init contrôle
        wx.CallAfter(self.InitialisationLecteur)
        self.Start()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((420, 320))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_1 = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_1.Add((20, 20), 0, 0, 0)
        grid_sizer_1.Add(self.ctrl_image, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_1.Add(self.ctrl_label, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_1.Add((20, 20), 0, 0, 0)
        self.panel.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableRow(3)
        grid_sizer_1.AddGrowableCol(0)
        grid_sizer_base.Add(self.panel, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Questionnaires")

    def OnBoutonAnnuler(self, event): 
        self.Stop() 
        self.EndModal(wx.ID_CANCEL)        
    
    def OnClose(self, event):
        self.Stop() 
        self.EndModal(wx.ID_CANCEL)        

    def Stop(self):
        self.timer.Stop()
        
    def Start(self):
        if not self.timer.IsRunning():
            self.timer.Start(500)
    
    def InitialisationLecteur(self):
        self.lecteurs = smartcard.System.readers()
        self.lecteur = self.lecteurs[0]
        #print self.lecteur.name
        self.connexion = self.lecteur.createConnection()
        
    def OnTimer(self, event):
        try :
            self.connexion.connect()
            apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = self.connexion.transmit(apdu)
            if sw1 == 144 :
                self.IDbadge = self.ListToHex(data)
                self.Stop()
                self.EndModal(wx.ID_OK)        
        except Exception, err :
            #print Exception, err
            pass

    def ListToHex(self, data):
        string= ''
        for d in data:
            string += '%02X' % d
        return string

    def GetIDbadge(self):
        return self.IDbadge
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
