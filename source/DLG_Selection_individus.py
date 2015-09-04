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
import datetime
import GestionDB
import CTRL_Saisie_date
import CTRL_Selection_activites



class Dialog(wx.Dialog):
    def __init__(self, parent, afficherPresents=True):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        self.radio_tous = wx.RadioButton(self, -1, _(u"Tous les individus"))
        self.radio_inscrits = wx.RadioButton(self, -1, _(u"Uniquement les inscrits aux activit�s suivantes :"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        
        self.check_presents = wx.CheckBox(self, -1, _(u"Et pr�sents du"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        if afficherPresents == False :
            self.check_presents.Show(False)
            self.ctrl_date_debut.Show(False)
            self.label_au.Show(False)
            self.ctrl_date_fin.Show(False)
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_tous)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inscrits)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckPresents, self.check_presents)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contr�les
        self.OnRadio(None)

    def __set_properties(self):
        self.SetTitle(_(u"S�lection d'individus"))
        self.radio_tous.SetToolTipString(_(u"Cochez ici pour s�lectionner tous les individus"))
        self.radio_inscrits.SetToolTipString(_(u"Cochez ici pour s�lectionner des inscrits"))
        self.check_presents.SetToolTipString(_(u"Cochez cette case pour saisir une p�riode de pr�sence"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de d�but de p�riode"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez ici la date de fin de p�riode"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((430, 460))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_activites = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_presents = wx.FlexGridSizer(rows=1, cols=9, vgap=2, hgap=2)
        grid_sizer_base.Add(self.radio_tous, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_base.Add(self.radio_inscrits, 0, wx.LEFT|wx.RIGHT, 10)
        grid_sizer_activites.Add(self.ctrl_activites, 0, wx.LEFT|wx.EXPAND, 16)
        grid_sizer_presents.Add(self.check_presents, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 16)
        grid_sizer_presents.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_presents.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        grid_sizer_presents.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_activites.Add(grid_sizer_presents, 1, wx.EXPAND, 0)
        grid_sizer_activites.AddGrowableRow(0)
        grid_sizer_activites.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_activites, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadio(self, event): 
        if self.radio_tous.GetValue() == True :
            self.ctrl_activites.Enable(False)
            self.check_presents.Enable(False)
            self.label_au.Enable(False)
            self.ctrl_date_debut.Enable(False)
            self.ctrl_date_fin.Enable(False)
        else:
            self.ctrl_activites.Enable(True)
            self.check_presents.Enable(True)
            self.label_au.Enable(True)
            self.OnCheckPresents(None)

    def OnCheckPresents(self, event): 
        etat = self.check_presents.GetValue() 
        self.ctrl_date_debut.Enable(etat)
        self.ctrl_date_fin.Enable(etat)

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnCheckActivites(self):
        pass
            
    def GetActivites(self):
        if self.radio_tous.GetValue() == True :
            return None
        else :
            return self.ctrl_activites.GetActivites() 
    
    def GetMode(self):
        if self.radio_tous.GetValue() == True :
            return "tous"
        else :
            return "inscrits"
        
    def GetPeriodePresents(self):
        if self.check_presents.GetValue()  == True :
            date_debut = self.ctrl_date_debut.GetDate() 
            date_fin = self.ctrl_date_fin.GetDate() 
            return date_debut, date_fin
        else :
            return None
    
    def OnBoutonOk(self, event): 
        """ Validation """
        # Tous les individus
        if self.radio_tous.GetValue() == True :
            self.EndModal(wx.ID_OK)
            return
        
        # Uniquement les inscrits
        if self.ctrl_activites.Validation() == False :
            return
        
        # Les pr�sents
        if self.check_presents.GetValue() == True :
            if self.ctrl_date_debut.GetDate() == None or self.ctrl_date_debut.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune date de d�but de p�riode !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            if self.ctrl_date_fin.GetDate() == None or self.ctrl_date_fin.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune date de fin de p�riode !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

            if self.ctrl_date_debut.GetDate() > self.ctrl_date_fin.GetDate() :
                dlg = wx.MessageDialog(self, _(u"La date de d�but est sup�rieure � la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)
            


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, afficherPresents=False)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
