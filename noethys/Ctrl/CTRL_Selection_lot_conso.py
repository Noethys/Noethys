#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

import GestionDB
from Ctrl import CTRL_Grille_periode



class CTRL_Individus(wx.CheckListBox):
    def __init__(self, parent, IDfamille=None, selectionIndividus=[]):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.IDfamille = IDfamille
        self.selectionIndividus = selectionIndividus
        self.data = []
        self.MAJ() 

    def MAJ(self):
        db = GestionDB.DB()
        req = """SELECT rattachements.IDindividu, individus.nom, individus.prenom
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        LEFT JOIN inscriptions ON inscriptions.IDindividu = rattachements.IDindividu
        WHERE rattachements.IDfamille=%d AND IDcategorie IN (1, 2)
        AND inscriptions.statut='ok' AND inscriptions.IDactivite IS NOT NULL
        GROUP BY individus.IDindividu
        ORDER BY individus.nom, individus.prenom;""" % self.IDfamille
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeValeurs = []
        for IDindividu, nom, prenom in listeDonnees :
            if prenom == None : prenom = u""
            checked = False
            if IDindividu in self.selectionIndividus : checked = True
            listeValeurs.append((IDindividu, u"%s %s" % (nom, prenom), checked))
        self.SetData(listeValeurs)

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
# -----------------------------------------------------------------------------------------------------------------

class CTRL_Activite(wx.Choice):
    def __init__(self, parent, selectionIndividus=[], selectionActivite=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.selectionIndividus = selectionIndividus
        self.selectionActivite = selectionActivite
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True) 
        self.SetItems(listeItems)
        if self.selectionActivite != None :
            self.SetID(self.selectionActivite)
        else:
            if len(listeItems) == 1 :
                self.SetStringSelection(listeItems[0])
                                        
    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        if len(self.selectionIndividus) == 0 : return listeItems
        elif  len(self.selectionIndividus) == 1 : criteresIndividus = "inscriptions.IDindividu = %d" % self.selectionIndividus[0]
        else: criteresIndividus = "inscriptions.IDindividu IN %s" % str(tuple(self.selectionIndividus))
        
        db = GestionDB.DB()
        req = """SELECT inscriptions.IDactivite, activites.nom
        FROM inscriptions
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        WHERE %s
        GROUP BY inscriptions.IDactivite
        ORDER BY activites.nom;""" % criteresIndividus
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        index = 0
        for IDactivite, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDactivite, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
            

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent, selectionActivite=None):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.selectionActivite = selectionActivite
        self.data = []
        self.MAJ() 

    def MAJ(self):
        if self.selectionActivite == None or self.selectionActivite == [] :
            self.Clear() 
            self.Enable(False)
            return
        else:
            self.Enable(True)
        db = GestionDB.DB()
        req = """SELECT groupes.IDactivite, groupes.nom
        FROM groupes
        WHERE groupes.IDactivite=%d
        ORDER BY groupes.nom;""" % self.selectionActivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeValeurs = []
        for IDgroupe, nom in listeDonnees :
            checked = True
            listeValeurs.append((IDgroupe, nom, checked))
        self.SetData(listeValeurs)

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
# -----------------------------------------------------------------------------------------------------------------

class CTRL_Unites(wx.CheckListBox):
    def __init__(self, parent, selectionActivite=None):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.selectionActivite = selectionActivite
        self.data = []
        self.MAJ() 

    def MAJ(self):
        if self.selectionActivite == None :
            self.Clear() 
            self.Enable(False)
            return
        else:
            self.Enable(True)
        db = GestionDB.DB()
        req = """SELECT IDunite, nom
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.selectionActivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeValeurs = []
        for IDunite, nom in listeDonnees :
            checked = True
            listeValeurs.append((IDunite, nom, checked))
        self.SetData(listeValeurs)

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
# -----------------------------------------------------------------------------------------------------------------

class CTRL_Modes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.data = []
        self.MAJ() 
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCoche)

    def MAJ(self):
        listeDonnees = [
            ("reservation", _(u"Réservation")),
            ("attente", _(u"Attente")),
            ("refus", _(u"Refus")),
        ]
        listeValeurs = []
        for code, nom in listeDonnees :
            if self.parent.mode == "modification" :
                checked = True
            else:
                checked = False
            listeValeurs.append((code, nom, checked))
        self.SetData(listeValeurs)

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
        for code, label, checked in listeValeurs:
            self.data.append((code, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def OnCoche(self, event):
        if self.parent.mode == "ajout" :
            if 'phoenix' in wx.PlatformInfo:
                self.SetCheckedItems([])
            else:
                self.SetChecked([])
            index = event.GetSelection()
            self.Check(index)

# -----------------------------------------------------------------------------------------------------------------

class CTRL_Etats(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 60))
        self.parent = parent
        self.data = []
        self.MAJ() 
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCoche)

    def MAJ(self):
        listeDonnees = [
            ("reservation", _(u"Pointage en attente")),
            ("present", _(u"Présent")),
            ("absentj", _(u"Absence justifiée")),
            ("absenti", _(u"Absence injustifiée")),            
        ]
        listeValeurs = []
        for code, nom in listeDonnees :
            if self.parent.mode == "modification" :
                checked = True
            else:
                checked = False
            listeValeurs.append((code, nom, checked))
        self.SetData(listeValeurs)

    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        self.Clear() 
        for code, label, checked in listeValeurs:
            self.data.append((code, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def OnCoche(self, event):
        if self.parent.mode == "ajout" :
            if 'phoenix' in wx.PlatformInfo:
                self.SetCheckedItems([])
            else:
                self.SetChecked([])
            index = event.GetSelection()
            self.Check(index)

# -----------------------------------------------------------------------------------------------------------------


class CTRL(wx.Panel):
    def __init__(self, parent, IDfamille=None, mode="ajout", listeDates=[], selectionIndividus=[], selectionActivite=None):
        wx.Panel.__init__(self, parent, id=-1, name="CTRL_Selection_lot_conso", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.IDfamille = IDfamille
        self.mode = mode
        self.listeDates = listeDates
        self.selectionIndividus = selectionIndividus
        self.selectionActivite = selectionActivite
        
        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.radio_periode_1 = wx.RadioButton(self, -1, u"")
        self.label_periode = wx.StaticText(self, -1, _(u"La période affichée dans la grille"))
        self.radio_periode_2 = wx.RadioButton(self, -1, u"")
        self.radio_periode_2.Enable(False) # <<<<<<<<<<<<<<<< PROVISOIRE
        self.ctrl_periode = CTRL_Grille_periode.CTRL(self)
        self.ctrl_periode.SetMinSize((60, 110))
        
        # Individus
        self.staticbox_individus_staticbox = wx.StaticBox(self, -1, _(u"Individus"))
        self.ctrl_individus = CTRL_Individus(self, self.IDfamille, self.selectionIndividus)
        
        # Activité
        self.staticbox_activite_staticbox = wx.StaticBox(self, -1, _(u"Activité"))
        self.ctrl_activite = CTRL_Activite(self, self.selectionIndividus, self.selectionActivite)
        
        # Groupes
        self.staticbox_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_Groupes(self, self.selectionActivite)
        
        # Unités
        self.staticbox_unites_staticbox = wx.StaticBox(self, -1, _(u"Unités"))
        self.ctrl_unites = CTRL_Unites(self, self.selectionActivite)
        
        # Modes
        self.staticbox_modes_staticbox = wx.StaticBox(self, -1, _(u"Modes"))
        self.ctrl_modes = CTRL_Modes(self)
        self.ctrl_modes.SetMinSize((60, 40))
        
        # Etats
        self.staticbox_etats_staticbox = wx.StaticBox(self, -1, _(u"Etats"))
        self.ctrl_etats = CTRL_Etats(self)
        self.ctrl_etats.SetMinSize((60, 40))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_periode_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_periode_2)
        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCocheIndividus, self.ctrl_individus)
        
        # Init Contrôles
        self.radio_periode_1.SetValue(True)
        self.OnRadioPeriode(None)

    def __set_properties(self):
        self.radio_periode_1.SetToolTip(wx.ToolTip(_(u"Cochez ici pour sélectionner la période affichée dans la grille des consommations")))
        self.radio_periode_2.SetToolTip(wx.ToolTip(_(u"Cochez ici pour sélectionner une autre période")))
        self.ctrl_individus.SetToolTip(wx.ToolTip(_(u"Cochez les individus souhaités")))
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Selectionnez l'activité souhaitée")))
        self.ctrl_groupes.SetToolTip(wx.ToolTip(_(u"Cochez les groupes souhaités")))
        self.ctrl_unites.SetToolTip(wx.ToolTip(_(u"Cochez les unités de consommations souhaitées")))
        self.ctrl_modes.SetToolTip(wx.ToolTip(_(u"Cochez les modes souhaités")))
        self.ctrl_etats.SetToolTip(wx.ToolTip(_(u"Cochez les etats souhaités")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Grid sizer HAUT
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=5)
        grid_sizer_periode.Add(self.radio_periode_1, 0, 0, 0)
        grid_sizer_periode.Add(self.label_periode, 0, 0, 0)
        grid_sizer_periode.Add(self.radio_periode_2, 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_periode, 0, wx.EXPAND, 0)
        grid_sizer_periode.AddGrowableRow(1)
        grid_sizer_periode.AddGrowableCol(1)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticbox_periode, 1, wx.EXPAND, 0)
        
        grid_sizer_haut_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        staticbox_individus = wx.StaticBoxSizer(self.staticbox_individus_staticbox, wx.VERTICAL)
        grid_sizer_individus = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0)
        grid_sizer_individus.Add(self.ctrl_individus, 0, wx.EXPAND, 0)
        grid_sizer_individus.AddGrowableRow(0)
        grid_sizer_individus.AddGrowableCol(0)
        staticbox_individus.Add(grid_sizer_individus, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(staticbox_individus, 1, wx.EXPAND, 0)
        
        staticbox_activite = wx.StaticBoxSizer(self.staticbox_activite_staticbox, wx.VERTICAL)
        staticbox_activite.Add(self.ctrl_activite, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(staticbox_activite, 1, wx.EXPAND, 0)
        
        grid_sizer_haut_droit.AddGrowableRow(0)
        grid_sizer_haut_droit.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_haut_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        
        # Grid sizer MILIEU
        grid_sizer_milieu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        staticbox_groupes = wx.StaticBoxSizer(self.staticbox_groupes_staticbox, wx.VERTICAL)
        grid_sizer_groupes = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0)
        grid_sizer_groupes.Add(self.ctrl_groupes, 0, wx.EXPAND, 0)
        grid_sizer_groupes.AddGrowableRow(0)
        grid_sizer_groupes.AddGrowableCol(0)
        staticbox_groupes.Add(grid_sizer_groupes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_milieu.Add(staticbox_groupes, 1, wx.EXPAND, 0)
        
        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites_staticbox, wx.VERTICAL)
        grid_sizer_unites = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0)
        grid_sizer_unites.Add(self.ctrl_unites, 0, wx.EXPAND, 0)
        grid_sizer_unites.AddGrowableRow(0)
        grid_sizer_unites.AddGrowableCol(0)
        staticbox_unites.Add(grid_sizer_unites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_milieu.Add(staticbox_unites, 1, wx.EXPAND, 0)
        
        grid_sizer_milieu.AddGrowableRow(0)
        grid_sizer_milieu.AddGrowableCol(0)
        grid_sizer_milieu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_milieu, 1, wx.EXPAND, 0)
        
        # Grid sizer BAS
        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        staticbox_modes = wx.StaticBoxSizer(self.staticbox_modes_staticbox, wx.VERTICAL)
        grid_sizer_modes = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0)
        grid_sizer_modes.Add(self.ctrl_modes, 0, wx.EXPAND, 0)
        grid_sizer_modes.AddGrowableRow(0)
        grid_sizer_modes.AddGrowableCol(0)
        staticbox_modes.Add(grid_sizer_modes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_bas.Add(staticbox_modes, 1, wx.EXPAND, 0)

        staticbox_etats = wx.StaticBoxSizer(self.staticbox_etats_staticbox, wx.VERTICAL)
        grid_sizer_etats = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0)
        grid_sizer_etats.Add(self.ctrl_etats, 0, wx.EXPAND, 0)
        grid_sizer_etats.AddGrowableRow(0)
        grid_sizer_etats.AddGrowableCol(0)
        staticbox_etats.Add(grid_sizer_etats, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_bas.Add(staticbox_etats, 1, wx.EXPAND, 0)
        
        grid_sizer_bas.AddGrowableRow(0)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_bas.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.EXPAND, 0)
        
        # Layout
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadioPeriode(self, event): 
        if self.radio_periode_1.GetValue() == True :
            self.ctrl_periode.Enable(False)
        else:
            self.ctrl_periode.Enable(True)
    
    def OnCocheIndividus(self, event):
        self.ctrl_activite.selectionIndividus = self.ctrl_individus.GetIDcoches()
        self.ctrl_activite.MAJ() 
        self.OnChoixActivite(None)

    def OnChoixActivite(self, event): 
        IDactivite = self.ctrl_activite.GetID() 
        # MAJ Groupes
        self.ctrl_groupes.selectionActivite = IDactivite
        self.ctrl_groupes.MAJ() 
        # MAJ Unités
        self.ctrl_unites.selectionActivite = IDactivite
        self.ctrl_unites.MAJ() 
        # MAJ Panel Modifications
        if self.parent.GetName() == "DLG_Modification_lot_conso" :
            self.parent.SetActivite(IDactivite)
    
    def GetPeriodes(self):
        # Recup Période
        if self.radio_periode_1.GetValue() == True :
            return self.listeDates
        else:
            return self.ctrl_periode.GetDatesSelections()
    
    def GetIndividus(self):
        # Recup Individus
        return self.ctrl_individus.GetIDcoches() 
        
    def GetActivite(self):
        # Recup Activite
        return self.ctrl_activite.GetID() 
        
    def GetGroupes(self):
        # Recup Groupes
        return self.ctrl_groupes.GetIDcoches()
        
    def GetUnites(self):
        # Recup Unités
        return self.ctrl_unites.GetIDcoches()
        
    def GetModes(self):
        # Recup Modes
        return self.ctrl_modes.GetIDcoches()
        
    def GetEtats(self):
        # Recup Etats
        return self.ctrl_etats.GetIDcoches()
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, IDfamille=7, mode="modification")
        self.bouton_ok = CTRL_Bouton_image.CTRL(panel, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.EXPAND|wx.ALL, 10)
        sizer_2.Add(self.bouton_ok, 0, wx.EXPAND|wx.ALL, 10)
        panel.SetSizer(sizer_2)
        self.SetSize((550, 550))
        self.Layout()
        self.CenterOnScreen() 
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
    def OnBoutonOk(self, event):
        self.ctrl.Test()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", name="test")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
