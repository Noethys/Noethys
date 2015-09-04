#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Saisie_date

import GestionDB



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        
        # Dates
        self.staticbox_dates_staticbox = wx.StaticBox(self, -1, _(u"Dates de validit�"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au :"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Param�tres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.label_quotient = wx.StaticText(self, -1, _(u"Quotient familial :"))
        self.ctrl_quotient = wx.TextCtrl(self, -1, u"")
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez ici la date de d�but de validit�"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez ici la date de fin de validit�"))
        self.ctrl_quotient.SetToolTipString(_(u"Saisissez ici le quotient familial"))
        self.ctrl_observations.SetToolTipString(_(u"[Optionnel] Saisissez ici des commentaires sur ce quotient"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        staticbox_dates = wx.StaticBoxSizer(self.staticbox_dates_staticbox, wx.VERTICAL)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_dates.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        staticbox_dates.Add(grid_sizer_dates, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_dates, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_parametres.Add(self.label_quotient, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_quotient, 0, 0, 0)
        grid_sizer_parametres.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableRow(1)
        grid_sizer_parametres.AddGrowableCol(1)
        staticbox_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
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
        import UTILS_Aide
        UTILS_Aide.Aide("Quotientsfamiliaux")
    
    def SetDateDebut(self, date=None):
        self.ctrl_date_debut.SetDate(date)

    def SetDateFin(self, date=None):
        self.ctrl_date_fin.SetDate(date)
    
    def SetQuotient(self, quotient=None):
        if quotient != None :
            self.ctrl_quotient.SetValue(str(quotient))
    
    def SetObservations(self, observations=None):
        if observations != None :
            self.ctrl_observations.SetValue(observations)
    
    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate() 

    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate() 

    def GetQuotient(self):
        return int(self.ctrl_quotient.GetValue())
    
    def GetObservations(self):
        return self.ctrl_observations.GetValue()

    def OnBoutonOk(self, event): 
        if self.ctrl_date_debut.FonctionValiderDate() == False or self.GetDateDebut() == None :
            dlg = wx.MessageDialog(self, _(u"La date de d�but de validit� n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        if self.ctrl_date_fin.FonctionValiderDate() == False or self.GetDateFin() == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de validit� n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return
        quotient = self.ctrl_quotient.GetValue()
        try :
            test = int(quotient)
        except :
            dlg = wx.MessageDialog(self, _(u"Le quotient familial que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_quotient.SetFocus()
            return

        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
