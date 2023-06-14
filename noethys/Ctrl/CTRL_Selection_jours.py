#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import wx.lib.agw.hyperlink as Hyperlink
from dateutil import rrule
import datetime
import GestionDB
from Utils import UTILS_Dates


def ConvertNumEnDateutil(jours=[]):
    listeReference = [rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]
    listeJours = []

    if type(jours) != list:
        listeJoursTemp = jours.split(";")
        listeJours = []
        for jour in listeJoursTemp:
            if len(jour) > 0:
                listeJours.append(int(jour))

    for numJour in jours :
        listeJours.append(listeReference[numJour])
    return listeJours

def IsVacances(listeVacances=[], date=None):
    isVacances = False
    for date_debut, date_fin in listeVacances :
        if date >= date_debut and date <= date_fin :
            isVacances = True
    return isVacances

def GetDates(jours={}, date_min=None, date_max=None):
    # Importation des vacances
    DB = GestionDB.DB()
    req = """SELECT date_debut, date_fin
    FROM vacances 
    WHERE date_debut<='%s' AND date_fin>='%s'
    ORDER BY date_debut;""" % (date_max, date_min)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeVacances = []
    for date_debut, date_fin in listeDonnees:
        date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
        date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
        listeVacances.append((date_debut, date_fin))

    listeDates = []
    for periode in ("scolaires", "vacances"):
        liste_jours = ConvertNumEnDateutil(jours[periode])
        if len(liste_jours) > 0 :
            listeDatesTemp = list(rrule.rrule(rrule.WEEKLY, wkst=rrule.MO, byweekday=liste_jours, dtstart=date_min, until=date_max))
            for date in listeDatesTemp :
                date = date.date()
                isVacances = IsVacances(listeVacances, date)
                if periode == "scolaires" and isVacances == False : listeDates.append(date)
                if periode == "vacances" and isVacances == True : listeDates.append(date)
    listeDates.sort()
    return listeDates





class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent

        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        if self.URL == "tout": self.parent.CocherTout()
        if self.URL == "rien": self.parent.CocherRien()
        self.UpdateLink()


class CTRL_Jours(wx.Panel):
    def __init__(self, parent, periode="scolaire"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.periode = periode
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")

        for jour in self.liste_jours:
            setattr(self, "check_%s" % jour, wx.CheckBox(self, -1, jour[0].upper()))
            getattr(self, "check_%s" % jour).SetToolTip(wx.ToolTip(jour.capitalize()))

        self.hyper_tout = Hyperlien(self, label=_(u"Tout"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Rien"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=10, vgap=0, hgap=0)
        for jour in self.liste_jours:
            grid_sizer_base.Add(getattr(self, "check_%s" % jour), 0, 0, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=3)
        grid_sizer_options.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_options, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def GetJours(self):
        listeTemp = []
        index = 0
        for jour in self.liste_jours:
            etat = getattr(self, "check_%s" % jour).GetValue()
            if etat == True:
                listeTemp.append(index)
            index += 1
        return listeTemp

    def SetJours(self, jours=""):
        if jours == None:
            return

        if type(jours) == list :
            listeJours = jours
        else :
            listeJoursTemp = jours.split(";")
            listeJours = []
            for jour in listeJoursTemp:
                if len(jour) > 0:
                    listeJours.append(int(jour))

        index = 0
        for jour in self.liste_jours:
            if index in listeJours:
                etat = True
            else:
                etat = False
            getattr(self, "check_%s" % jour).SetValue(etat)
            index += 1

    def CocherTout(self):
        self.SetJours("0;1;2;3;4;5;6")

    def CocherRien(self):
        self.SetJours("")


class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.label_scolaires = wx.StaticText(self, -1, _(u"Jours scolaires :"))
        self.ctrl_scolaires = CTRL_Jours(self, "scolaire")
        self.label_vacances = wx.StaticText(self, -1, _(u"Jours de vacances :"))
        self.ctrl_vacances = CTRL_Jours(self, "vacances")

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_scolaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_scolaires, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_vacances, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def GetDonnees(self):
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        return {"vacances" : jours_vacances, "scolaires" : jours_scolaires}

    def SetDonnees(self, donnees=None):
        if "vacances" in donnees:
            self.ctrl_vacances.SetJours(donnees["vacances"])
        if "scolaires" in donnees:
            self.ctrl_scolaires.SetJours(donnees["scolaires"])
            
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        bouton_test = wx.Button(panel, -1, u"Test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBouton, bouton_test) 
        
    def OnBouton(self, event):
        self.ctrl.SetDonnees({"vacances" : [0, 1], "scolaires" : "5;6"})
        donnees = self.ctrl.GetDonnees()
        print(donnees)
        print(ConvertNumEnDateutil(donnees["vacances"]))
        print(GetDates(jours=donnees, date_min=datetime.date(2018, 1, 1), date_max=datetime.date(2018, 12, 31)))
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(400, 200))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()