#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import CTRL_Saisie_date


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        self.SetTitle(u"Saisie d'un agrément")  
        
        self.sizer_agrement_staticbox = wx.StaticBox(self, -1, u"Numéro d'agrément")
        self.label_agrement = wx.StaticText(self, -1, u"Agrément :")
        self.ctrl_agrement = wx.TextCtrl(self, -1, "")
        
        self.sizer_duree_staticbox = wx.StaticBox(self, -1, u"Dates de validité")
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, u"au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.ctrl_agrement.SetToolTipString(u"Saisissez ici un numéro d'agrément Par exemple : '098GHJ25542'")
        self.ctrl_date_debut.SetToolTipString(u"Saisissez ici la date de début de validité")
        self.ctrl_date_fin.SetToolTipString(u"Saisissez ici la date de fin de validité")
        self.SetMinSize((340, 200))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Nom
        sizer_nom = wx.StaticBoxSizer(self.sizer_agrement_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_agrement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_agrement, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        sizer_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Validité
        sizer_duree = wx.StaticBoxSizer(self.sizer_duree_staticbox, wx.VERTICAL)
        grid_sizer_validite = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_validite.Add((40,-1), 0, 0, 0)
        grid_sizer_validite.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer_validite.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_fin, 0, wx.EXPAND, 0)
        sizer_duree.Add(grid_sizer_validite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_duree, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
            
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Agrments")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_agrement.GetValue() == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement donner un numéro d'agrément !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_agrement.SetFocus()
            return
        if self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement donner une date de début de validité !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        if self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement donner une date de fin de validité !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return
                    
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetAgrement(self):
        return self.ctrl_agrement.GetValue()

    def SetAgrement(self, agrement=""):
        self.ctrl_agrement.SetValue(agrement)
        
    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate() 

    def SetDateDebut(self, date_debut=None):
        self.ctrl_date_debut.SetDate(date_debut)
    
    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate() 

    def SetDateFin(self, date_fin=None):
        self.ctrl_date_fin.SetDate(date_fin)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
