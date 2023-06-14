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
from Ctrl import CTRL_Selection_activites
from Ctrl import CTRL_Grille_periode
from Utils import UTILS_Dates


def GetSQLdates(listePeriodes=[]):
    texteSQL = ""
    for date_debut, date_fin in listePeriodes :
        texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
    if len(texteSQL) > 0 :
        texteSQL = "(" + texteSQL[:-4] + ")"
    else:
        texteSQL = "date=0"
    return texteSQL



class CTRL_Activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.listePeriodes = []
        self.SetToolTip(wx.ToolTip(_(u"Cochez les activités à afficher")))
        self.listeActivites = []
        self.dictActivites = {}
        self.SetMinSize((-1, 100))
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)

    def SetPeriodes(self, listePeriodes=[]):
        self.listePeriodes = listePeriodes
        self.MAJ()
        self.CocheTout()

    def MAJ(self):
        self.listeActivites, self.dictActivites = self.Importation()
        self.SetListeChoix()

    def Importation(self):
        listeActivites = []
        dictActivites = {}
        if len(self.listePeriodes) == 0:
            return listeActivites, dictActivites
            # Condition Périodes
        conditionsPeriodes = GetSQLdates(self.listePeriodes)

        # Récupération des activités disponibles la période sélectionnée
        DB = GestionDB.DB()
        req = """SELECT activites.IDactivite, nom, abrege, date_debut, date_fin
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        WHERE %s
        GROUP BY activites.IDactivite
        ORDER BY date_fin DESC;""" % conditionsPeriodes
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDactivite, nom, abrege, date_debut, date_fin in listeDonnees:
            if date_debut != None: date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            if date_fin != None: date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            dictTemp = {"nom": nom, "abrege": abrege, "date_debut": date_debut, "date_fin": date_fin, "tarifs": {}}
            dictActivites[IDactivite] = dictTemp
            listeActivites.append((nom, IDactivite))
        listeActivites.sort()
        return listeActivites, dictActivites

    def SetListeChoix(self):
        self.Clear()
        index = 0
        for nom, IDactivite in self.listeActivites:
            self.Append(nom)
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeActivites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeActivites[index][1])
        return listeIDcoches

    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeActivites)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeActivites)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches:
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une sélection d'activités est effectuée... """
        self.parent.OnCheckActivites()

    def GetListeActivites(self):
        return self.GetIDcoches()

    def GetDictActivites(self):
        return self.dictActivites




# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.SetToolTip(wx.ToolTip(_(u"Cochez les groupes à afficher")))
        self.listeGroupes = []
        self.dictGroupes = {}
        self.SetMinSize((-1, 100))

    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
        self.MAJ()
        self.CocheTout()

    def MAJ(self):
        self.listeGroupes, self.dictGroupes = self.Importation()
        self.SetListeChoix()

    def Importation(self):
        listeGroupes = []
        dictGroupes = {}
        if len(self.listeActivites) == 0:
            return listeGroupes, dictGroupes
            # Récupération des groupes des activités sélectionnées
        if len(self.listeActivites) == 0:
            conditionActivites = "()"
        elif len(self.listeActivites) == 1:
            conditionActivites = "(%d)" % self.listeActivites[0]
        else:
            conditionActivites = str(tuple(self.listeActivites))
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, groupes.IDactivite, groupes.nom, activites.nom
        FROM groupes
        LEFT JOIN activites ON activites.IDactivite = groupes.IDactivite
        WHERE groupes.IDactivite IN %s
        ORDER BY groupes.nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDgroupe, IDactivite, nom, nomActivite in listeDonnees:
            dictTemp = {"nom": nom, "IDactivite": IDactivite, "nomActivite": nomActivite}
            dictGroupes[IDgroupe] = dictTemp
            listeGroupes.append((nom, IDgroupe, nomActivite))
        listeGroupes.sort()
        return listeGroupes, dictGroupes

    def SetListeChoix(self):
        self.Clear()
        index = 0
        for nom, IDgroupe, nomActivite in self.listeGroupes:
            nom = u"%s (%s)" % (nom, nomActivite)
            self.Append(nom)
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeGroupes)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeGroupes[index][1])
        return listeIDcoches

    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            ID = self.listeGroupes[index][1]
            if ID in listeIDcoches:
                self.Check(index)
            index += 1

    def GetListeGroupes(self):
        return self.GetIDcoches()

    def GetDictGroupes(self):
        return self.dictGroupes


# -------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Mode
        self.staticbox_mode_staticbox = wx.StaticBox(self, -1, _(u"Mode de sélection"))
        self.radio_inscrits = wx.RadioButton(self, -1, _(u"Inscrits"), style=wx.RB_GROUP)
        self.radio_presents = wx.RadioButton(self, -1, _(u"Présents sur une période"))

        # Calendrier
        self.staticbox_date_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.ctrl_calendrier = CTRL_Grille_periode.CTRL(self)
        self.ctrl_calendrier.SetMinSize((230, 150))

        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites_presents = CTRL_Activites(self)
        self.ctrl_activites_inscrits = CTRL_Selection_activites.CTRL(self)
        self.ctrl_activites_presents.SetMinSize((10, 10))
        self.ctrl_activites_inscrits.SetMinSize((10, 10))

        # Groupes
        self.staticbox_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((10, 100))

        # Propriétés
        self.radio_inscrits.SetToolTip(wx.ToolTip(_(u"Sélectionnez le mode de sélection des individus")))
        self.radio_presents.SetToolTip(wx.ToolTip(_(u"Sélectionnez le mode de sélection des individus")))

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_inscrits)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_presents)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Sizer GAUCHE
        grid_sizer_gauche = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Mode
        staticbox_mode = wx.StaticBoxSizer(self.staticbox_mode_staticbox, wx.VERTICAL)
        grid_sizer_mode = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=10)
        grid_sizer_mode.Add(self.radio_inscrits, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mode.Add(self.radio_presents, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_mode.Add(grid_sizer_mode, 0, wx.ALL | wx.EXPAND, 10)
        grid_sizer_gauche.Add(staticbox_mode, 1, wx.EXPAND, 0)

        # Période
        staticbox_date = wx.StaticBoxSizer(self.staticbox_date_staticbox, wx.VERTICAL)
        staticbox_date.Add(self.ctrl_calendrier, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_gauche.Add(staticbox_date, 1, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, 10)

        # Sizer DROIT
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)

        staticbox_activites.Add(self.ctrl_activites_presents, 1, wx.ALL | wx.EXPAND, 10)
        staticbox_activites.Add(self.ctrl_activites_inscrits, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_droit.Add(staticbox_activites, 1, wx.EXPAND, 0)

        # Groupes
        staticbox_groupes = wx.StaticBoxSizer(self.staticbox_groupes_staticbox, wx.VERTICAL)
        staticbox_groupes.Add(self.ctrl_groupes, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_droit.Add(staticbox_groupes, 1, wx.EXPAND, 0)

        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM, 10)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        self.Layout()
        self.grid_sizer_base = grid_sizer_base

        # Init
        self.ctrl_calendrier.SetVisibleSelection()
        self.SetListesPeriodes(self.ctrl_calendrier.GetDatesSelections())
        self.OnRadioMode()

    def OnRadioMode(self, event=None):
        self.ctrl_activites_inscrits.Show(self.radio_inscrits.GetValue())
        self.ctrl_activites_presents.Show(self.radio_presents.GetValue())
        self.staticbox_date_staticbox.Enable(self.radio_presents.GetValue())
        self.ctrl_calendrier.Enable(self.radio_presents.GetValue())
        self.grid_sizer_base.Layout()
        self.OnCheckActivites()

    def OnCheckActivites(self):
        if self.radio_inscrits.GetValue() == True:
            listeSelections = self.ctrl_activites_inscrits.GetActivites()
            self.SetGroupes(listeSelections)
        if self.radio_presents.GetValue() == True:
            listeSelections = self.ctrl_activites_presents.GetIDcoches()
            self.SetGroupes(listeSelections)

    def SetListesPeriodes(self, listePeriodes=[]):
        self.ctrl_activites_presents.SetPeriodes(listePeriodes)
        self.SetGroupes(self.ctrl_activites_presents.GetListeActivites())

    def SetGroupes(self, listeActivites=[]):
        self.ctrl_groupes.SetActivites(listeActivites)

    def SetModePresents(self, etat=True):
        self.radio_presents.SetValue(etat)
        self.OnRadioMode()

    def GetParametres(self):
        dictParametres = {}

        dictParametres["liste_periodes"] = self.ctrl_calendrier.GetDatesSelections()
        dictParametres["impression_infos_med_mode_presents"] = self.radio_presents.GetValue()

        if self.radio_inscrits.GetValue() == True:
            dictParametres["mode"] = "inscrits"
            dictParametres["liste_activites"] = self.ctrl_activites_inscrits.GetActivites()
            dictParametres["dict_activites"] = self.ctrl_activites_inscrits.GetDictActivites()

        if self.radio_presents.GetValue() == True:
            dictParametres["mode"] = "presents"
            dictParametres["liste_activites"] = self.ctrl_activites_presents.GetListeActivites()
            dictParametres["dict_activites"] = self.ctrl_activites_presents.GetDictActivites()

        dictParametres["liste_groupes"] = self.ctrl_groupes.GetListeGroupes()
        dictParametres["dict_groupes"] = self.ctrl_groupes.GetDictGroupes()

        return dictParametres

    def SetParametres(self, dictParametres={}):
        pass


# ----------------------------------------------------------------------------------------------

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
        self.SetMinSize((600, 500))
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBouton, bouton_test) 
        
    def OnBouton(self, event):
        print("ok")
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(600, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()