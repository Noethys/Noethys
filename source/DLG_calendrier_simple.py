#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image

##import  wx.calendar
import datetime
import CTRL_Calendrier

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Calendrier_simple", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
##        self.locale = wx.Locale(wx.LANGUAGE_FRENCH)
        
##        self.ctrl_calendrier = wx.calendar.CalendarCtrl(self, -1, wx.DateTime_Now(), 
##                             style = wx.calendar.CAL_SHOW_HOLIDAYS
##                             | wx.calendar.CAL_MONDAY_FIRST
##                             | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION
##                             )
##        self.ctrl_calendrier.Bind(wx.calendar.EVT_CALENDAR, self.OnDateSelected)
        
        self.ctrl_calendrier = CTRL_Calendrier.CTRL(self, afficheAujourdhui=False, typeCalendrier="annuel", afficheBoutonAnnuel=True, multiSelections=False)
        self.ctrl_calendrier.Bind(CTRL_Calendrier.EVT_SELECT_DATES, self.OnDateSelected)

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok.Show(False) 
        
        self.SetTitle(_(u"Cliquez sur une date pour la sélectionner..."))
        self.SetMinSize((800, 600))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.ctrl_calendrier, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add( (1, 1), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()
        self.CenterOnScreen()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Calendrier1")

    def OnDateSelected(self, event):
        self.EndModal(wx.ID_OK)
    
##    def GetDate(self):
##        dateTmp = self.ctrl_calendrier.GetDate()
##        jour = dateTmp.GetDay()
##        mois = dateTmp.GetMonth()+1
##        annee = dateTmp.GetYear()
##        date = datetime.date(annee, mois, jour)
##        return date

    def GetDate(self):
        selections = self.ctrl_calendrier.GetSelections() 
        if len(selections) > 0 :
            return selections[0]
        else:
            return None
    
    def SetDate(self, date=None):
        self.ctrl_calendrier.SelectJours([date,])

    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)
        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
