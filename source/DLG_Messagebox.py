#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB



class Dialog(wx.Dialog):
    def __init__(self, parent, titre=None, introduction=None, detail=None, conclusion=None, icone=None, boutons=[], defaut=None):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP | wx.DIALOG_NO_PARENT)
        self.parent = parent   

        self.largeur_max = 550
        self.hauteur_max= 350
        self.taille_icone = (32, 32)
        
        # Titre
        if titre :
            self.SetTitle(titre)
        
        # Image
        if icone :
            if not isinstance(icone, wx.Bitmap) :
                if icone == wx.ICON_ERROR : artid = wx.ART_ERROR
                if icone == wx.ICON_EXCLAMATION : artid = wx.ART_WARNING
                if icone == wx.ICON_QUESTION : artid = wx.ART_QUESTION
                if icone == wx.ICON_INFORMATION : artid = wx.ART_INFORMATION
                icone = wx.ArtProvider.GetBitmap(artid, wx.ART_MESSAGE_BOX, self.taille_icone)
            image = wx.StaticBitmap(self, -1, icone)
        else:
            image = self.taille_icone

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(image, 0, wx.TOP|wx.LEFT, 12)
        sizer.Add( (10,10) )
        
        messageSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Introduction
        if introduction :
            t = wx.StaticText(self, -1, introduction)
            t.Wrap(self.largeur_max)
            messageSizer.Add(t, 0, wx.BOTTOM, 10)
            t.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        # Détail
        if detail :
            t = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH|wx.TE_DONTWRAP)
            t.SetValue(detail)

            dc = wx.ClientDC(t)
            dc.SetFont(t.GetFont())
            w,h,lh = dc.GetMultiLineTextExtent(detail)
            w = min(self.largeur_max, 10 + w + wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X))
            h = min(self.hauteur_max, 10 + h) + 20
            t.SetMinSize((w,h))
            messageSizer.Add(t, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        # Conclusion
        if conclusion :
            t = wx.StaticText(self, -1, conclusion)
            t.Wrap(self.largeur_max)
            messageSizer.Add(t, 0, wx.BOTTOM, 10)

        # Boutons
        boutonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        id = 100
        for label in boutons :
            bouton = wx.Button(self, id=id, label=label)
            self.Bind(wx.EVT_BUTTON, self.OnBouton, bouton)
            boutonsSizer.Add(bouton, 0, wx.LEFT, 10)
            id += 1
        
        messageSizer.Add(boutonsSizer, 0, wx.TOP | wx.ALIGN_RIGHT, 5)
        
        # Finalisation
        sizer.Add(messageSizer, 0, wx.ALL, 12)
        self.SetSizer(sizer)
        self.Fit()
        if parent:
            self.CenterOnParent()
        else:
            self.CenterOnScreen()
        
        if defaut == None :
            defaut = 0
        bouton = self.FindWindowById(defaut+100)
        bouton.SetFocus() 
            

    def OnBouton(self, evt):
        if self.IsModal():
            self.EndModal(evt.EventObject.Id-100)
        else:
            self.Close()
        






if __name__ == u"__main__":
    app = wx.App(0)
    
##    icone = wx.Bitmap(u"Images/32x32/Absenti.png", wx.BITMAP_TYPE_ANY)
    icone = wx.ICON_INFORMATION
    dlg = Dialog(None, titre=_(u"Avertissement"), introduction=_(u"Introduction ici !"), detail="detail", conclusion=_(u"Conclusion ici"), icone=icone, boutons=[_(u"Oui"), _(u"Oui pour tout"), _(u"Non"), _(u"Annuler")])
    reponse = dlg.ShowModal() 
    dlg.Destroy() 
    print reponse
    app.MainLoop()
