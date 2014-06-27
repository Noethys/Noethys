#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import CTRL_Bandeau
import textwrap


class Dialog(wx.Dialog):
    def __init__(self, parent, listeBoutons=[], titre=u"Quel type de prélèvement souhaitez-vous créer ?", intro=u"Cliquez sur la norme souhaitée...", minSize=(500, 400)):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.minSize = minSize
                
        # Bandeau
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage=None)
        
        # Activation
        self.listeControles = []
        index = 0
        for label, description in listeBoutons :
            ctrl = wx.CommandLinkButton(self, index, label, textwrap.fill(description, 80))
            self.listeControles.append(ctrl)
            self.Bind(wx.EVT_BUTTON, self.OnBouton, ctrl)
            index += 1

        # Boutons
        self.bouton_fermer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

    def __set_properties(self):
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize(self.minSize)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        for ctrl in self.listeControles :
            grid_sizer_base.Add(ctrl, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_base.Add((5, 5), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, wx.EXPAND, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(len(self.listeControles)+1)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBouton(self, event):
        ID = event.GetId() 
        self.EndModal(ID)
        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    listeBoutons = [
        (u"Label 1", u"Description 1"),
        (u"Label 2", u"Description 2"),
        ]
    dialog_1 = Dialog(None, listeBoutons=listeBoutons)
    app.SetTopWindow(dialog_1)
    print dialog_1.ShowModal()
    app.MainLoop()
