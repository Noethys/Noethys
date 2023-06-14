#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import GestionDB
import datetime
import calendar
from Ctrl import CTRL_Saisie_date



class Page_Semaines(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Semaine
        self.label_semaine = wx.StaticText(self, -1, _(u"Semaine :"))
        self.ctrl_semaine = wx.SpinCtrl(self, -1, "", min=1, max=52)
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", min=1977, max=2999)
        self.bouton_aujourdhui = wx.Button(self, -1, _(u"Aujourd'hui"))

        # Properties
        self.ctrl_semaine.SetMinSize((70, -1))
        self.ctrl_semaine.SetToolTip(wx.ToolTip(_(u"Sélectionnez une semaine")))
        self.ctrl_annee.SetMinSize((70, -1))
        self.ctrl_annee.SetToolTip(wx.ToolTip(_(u"Sélectionnez une année")))
        self.bouton_aujourdhui.SetToolTip(wx.ToolTip(_(u"Sélectionnez la semaine en cours")))

        # Binds
        self.Bind(wx.EVT_SPINCTRL, self.parent.CallBack, self.ctrl_semaine)
        self.Bind(wx.EVT_SPINCTRL, self.parent.CallBack, self.ctrl_annee)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAujourdhui, self.bouton_aujourdhui)

        # Layout
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)

        # Période
        grid_sizer_semaines = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_semaines.Add(self.label_semaine, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_semaines.Add(self.ctrl_semaine, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_semaines.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_semaines.Add(self.ctrl_annee, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_semaines.Add(self.bouton_aujourdhui, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
        sizer_base.Add(grid_sizer_semaines, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.SelectAujourdhui()

    def SelectAujourdhui(self):
        dateDuJour = datetime.date.today()
        self.ctrl_annee.SetValue(dateDuJour.year)
        self.ctrl_semaine.SetValue(dateDuJour.isocalendar()[1])

    def OnBoutonAujourdhui(self, event=None):
        self.SelectAujourdhui()
        self.parent.CallBack()

    def GetDateDebut(self):
        annee = int(self.ctrl_annee.GetValue())
        num_semaine = int(self.ctrl_semaine.GetValue())
        date_debut = datetime.datetime.strptime("%d-W%d-1" % (annee, num_semaine), "%Y-W%W-%w").date()
        return date_debut

    def GetDateFin(self):
        annee = int(self.ctrl_annee.GetValue())
        num_semaine = int(self.ctrl_semaine.GetValue())
        date_fin = datetime.datetime.strptime("%d-W%d-0" % (annee, num_semaine), "%Y-W%W-%w").date()
        return date_fin



class Page_Mois(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Mois
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.ctrl_mois = wx.Choice(self, -1, choices=[_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")])
        self.spin_mois = wx.SpinButton(self, -1, size=(18, 24),  style=wx.SP_VERTICAL)
        self.spin_mois.SetRange(-1, 1)
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", min=1977, max=2999)
        self.bouton_aujourdhui = wx.Button(self, -1, _(u"Aujourd'hui"))

        # Properties
        self.ctrl_mois.SetToolTip(wx.ToolTip(_(u"Sélectionnez un mois")))
        self.ctrl_annee.SetMinSize((70, -1))
        self.ctrl_annee.SetToolTip(wx.ToolTip(_(u"Sélectionnez une année")))
        self.bouton_aujourdhui.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'année en cours")))

        # Binds
        self.Bind(wx.EVT_SPIN, self.OnSpinMois, self.spin_mois)
        self.Bind(wx.EVT_CHOICE, self.parent.CallBack, self.ctrl_mois)
        self.Bind(wx.EVT_SPINCTRL, self.parent.CallBack, self.ctrl_annee)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAujourdhui, self.bouton_aujourdhui)

        # Layout
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)

        # Période
        grid_sizer_mois = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_mois.Add(self.label_mois, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mois.Add(self.ctrl_mois, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_mois.Add(self.spin_mois, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mois.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_mois.Add(self.ctrl_annee, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_mois.Add(self.bouton_aujourdhui, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
        sizer_base.Add(grid_sizer_mois, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.SelectAujourdhui()

    def SelectAujourdhui(self):
        dateDuJour = datetime.date.today()
        self.ctrl_annee.SetValue(dateDuJour.year)
        self.ctrl_mois.SetSelection(dateDuJour.month-1)

    def OnBoutonAujourdhui(self, event=None):
        self.SelectAujourdhui()
        self.parent.CallBack()

    def OnSpinMois(self, event):
        x = event.GetPosition()
        mois = self.ctrl_mois.GetSelection()+x
        if mois != -1 and mois < 12 :
            self.ctrl_mois.SetSelection(mois)
            self.parent.CallBack()
        self.spin_mois.SetValue(0)

    def GetDateDebut(self):
        annee = int(self.ctrl_annee.GetValue())
        mois = self.ctrl_mois.GetSelection()+1
        return datetime.date(annee, mois, 1)

    def GetDateFin(self):
        annee = int(self.ctrl_annee.GetValue())
        mois = self.ctrl_mois.GetSelection()+1
        tmp, nbreJours = calendar.monthrange(annee, mois)
        return datetime.date(annee, mois, nbreJours)



class Page_Vacances(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Vacances
        self.label_vacances = wx.StaticText(self, -1, _(u"Période :"))
        self.ctrl_vacances = wx.Choice(self, -1, choices=[])
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", min=1977, max=2999)

        # Properties
        self.ctrl_vacances.SetMinSize((90, -1))
        self.ctrl_vacances.SetToolTip(wx.ToolTip(_(u"Sélectionnez une période de vacances")))
        self.ctrl_annee.SetMinSize((70, -1))
        self.ctrl_annee.SetToolTip(wx.ToolTip(_(u"Sélectionnez une année")))

        # Binds
        self.Bind(wx.EVT_CHOICE, self.parent.CallBack, self.ctrl_vacances)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixAnnee, self.ctrl_annee)

        # Layout
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)

        # Période
        grid_sizer_semaines = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_semaines.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_semaines.Add(self.ctrl_vacances, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_semaines.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_semaines.Add(self.ctrl_annee, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        sizer_base.Add(grid_sizer_semaines, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.SelectAujourdhui()

    def SelectAujourdhui(self):
        dateDuJour = datetime.date.today()
        self.ctrl_annee.SetValue(dateDuJour.year)
        self.MAJVacances()

    def OnChoixAnnee(self, event=None):
        self.MAJVacances()
        self.parent.CallBack()

    def MAJVacances(self):
        DB = GestionDB.DB()
        req = """SELECT nom, date_debut, date_fin
        FROM vacances 
        WHERE annee=%d
        ORDER BY date_debut
        ;""" % self.ctrl_annee.GetValue()
        DB.ExecuterReq(req)
        listeVacances = DB.ResultatReq()
        DB.Close()
        listeChoix = []
        self.dictVacances = {}
        index = 0
        for nom, date_debut, date_fin in listeVacances :
            date_debut = datetime.date(year=int(date_debut[:4]), month=int(date_debut[5:7]), day=int(date_debut[8:10]))
            date_fin = datetime.date(year=int(date_fin[:4]), month=int(date_fin[5:7]), day=int(date_fin[8:10]))
            listeChoix.append(nom)
            self.dictVacances[index] = (date_debut, date_fin)
            index += 1
        self.ctrl_vacances.Set(listeChoix)
        if len(listeChoix) > 0 :
            self.ctrl_vacances.Select(0)
            self.ctrl_vacances.Enable(True)
        else :
            self.ctrl_vacances.Enable(False)

    def GetDatesVacances(self):
        index = self.ctrl_vacances.GetSelection()
        if index != -1 :
            return self.dictVacances[index]
        return None, None

    def GetDateDebut(self):
        date_debut, date_fin = self.GetDatesVacances()
        return date_debut

    def GetDateFin(self):
        date_debut, date_fin = self.GetDatesVacances()
        return date_fin


class Page_Dates(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Période
        self.label_periode = wx.StaticText(self, wx.ID_ANY, _(u"Du"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.bouton_appliquer_dates = wx.Button(self, -1, _(u"Appliquer"))

        # Properties
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de la période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de la période")))
        self.bouton_appliquer_dates.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la période saisie")))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.parent.CallBack, self.bouton_appliquer_dates)

        # Layout
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)

        # Période
        grid_sizer_periode = wx.FlexGridSizer(1, 6, 5, 5)
        grid_sizer_periode.Add(self.label_periode, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.bouton_appliquer_dates, 0, wx.EXPAND, 0)
        sizer_base.Add(grid_sizer_periode, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.ctrl_date_debut.SetDate(datetime.date.today() - datetime.timedelta(days=3))
        self.ctrl_date_fin.SetDate(datetime.date.today() + datetime.timedelta(days=30))

    def OnChoixDate(self):
        self.parent.CallBack()

    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate()

    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate()


class Page_Jour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Jour
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.bouton_appliquer_dates = wx.Button(self, -1, _(u"Appliquer"))
        self.bouton_aujourdhui = wx.Button(self, -1, _(u"Aujourd'hui"))

        # Properties
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez une date")))
        self.bouton_appliquer_dates.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la date saisie")))
        self.bouton_aujourdhui.SetToolTip(wx.ToolTip(_(u"Sélectionnez la date du jour")))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.parent.CallBack, self.bouton_appliquer_dates)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAujourdhui, self.bouton_aujourdhui)

        # Layout
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)

        # Période
        grid_sizer_periode = wx.FlexGridSizer(1, 4, 5, 5)
        grid_sizer_periode.Add(self.ctrl_date, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.bouton_appliquer_dates, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.bouton_aujourdhui, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_base.Add(grid_sizer_periode, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        self.SelectAujourdhui()

    def SelectAujourdhui(self):
        self.ctrl_date.SetDate(datetime.date.today())

    def OnBoutonAujourdhui(self, event=None):
        self.SelectAujourdhui()
        self.parent.CallBack()

    def OnChoixDate(self):
        self.parent.CallBack()

    def GetDateDebut(self):
        return self.ctrl_date.GetDate()

    def GetDateFin(self):
        return self.ctrl_date.GetDate()



class CTRL(wx.Notebook):
    def __init__(self, parent, callback=None):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.parent = parent
        self.callback = callback
        self.dictPages = {}
        self.callback_actif = True

        self.listePages = [
            {"code": "mois", "ctrl": Page_Mois(self), "label": _(u"Mois"), "image": "Calendrier_mois.png"},
            {"code": "semaine", "ctrl": Page_Semaines(self), "label": _(u"Semaine"), "image": "Calendrier3jours.png"},
            {"code": "vacances", "ctrl": Page_Vacances(self), "label": _(u"Vacances"), "image": "Calendrier3jours.png"},
            {"code": "periode", "ctrl": Page_Dates(self), "label": _(u"Période"), "image": "Calendrier_jour.png"},
            {"code": "date", "ctrl": Page_Jour(self), "label": _(u"Jour"), "image": "Calendrier_jour.png"},
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages:
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Création des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def CallBack(self, event=None):
        if self.callback != None and self.callback_actif == True :
            self.callback()

    def GetPageActive(self):
        index = self.GetSelection()
        return self.listePages[index]["ctrl"]

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]

    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == codePage:
                self.SetSelection(index)
            index += 1

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        self.CallBack()

    def GetDateDebut(self):
        return self.GetPageActive().GetDateDebut()

    def GetDateFin(self):
        return self.GetPageActive().GetDateFin()

    def SetModePeriode(self, code=""):
        self.callback_actif = False
        self.AffichePage(code)
        self.callback_actif = True

    def GetModePeriode(self):
        index = self.GetSelection()
        return self.listePages[index]["code"]




            
            
            
        


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
        self.SetMinSize((300, 600))
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBouton, bouton_test) 
        
    def OnBouton(self, event):
        print("test")
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()