#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import datetime
import GestionDB
import CTRL_Saisie_date
import CTRL_Saisie_euros

from CTRL_Questionnaire import LISTE_CONTROLES




class CTRL_Choix(wx.CheckListBox):
    def __init__(self, parent, IDquestion=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.IDquestion = IDquestion
        self.parent = parent
        self.dictDonnees = {}
        self.dictIndex = {}
        self.listeDonnees = self.Importation()
        if self.listeDonnees == None : 
            self.listeDonnees = []
        self.MAJ() 
        
    def MAJ(self):
        self.listeDonnees = self.Importation()
        self.Clear()
        self.dictIndex = {}
        if self.listeDonnees == None : return
        index = 0
        for IDchoix, label in self.listeDonnees :
            self.Append(label) 
            self.dictIndex[index] = IDchoix
            index += 1

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDchoix, label
        FROM questionnaire_choix
        WHERE IDquestion=%d AND visible=1
        ORDER BY ordre;""" % self.IDquestion
        DB.ExecuterReq(req)
        listeChoix = DB.ResultatReq()
        DB.Close()
        return listeChoix
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                IDchoix = self.dictIndex[index]
                listeIDcoches.append(IDchoix)
        listeIDcoches.sort() 
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            ID = self.dictIndex[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1


class CTRL_Page_choix(wx.Panel):
    def __init__(self, parent, IDquestion=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.IDquestion = IDquestion
        self.label_intro = wx.StaticText(self, -1, u"L'un des choix suivants est sélectionné :")
        self.ctrl_choix = CTRL_Choix(self, IDquestion=IDquestion)
        self.__do_layout()
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_choix, 1, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
    
    def SetValeur(self, choix=None, criteres=None):
        if len(criteres) > 0 :
            listeChoix = criteres.split(";")
            listeID = []
            for choix in listeChoix :
                listeID.append(int(choix))
            self.ctrl_choix.SetIDcoches(listeID)
    
    def GetValeur(self):
        choix, criteres = "", ""
        listeChoix = self.ctrl_choix.GetIDcoches() 
        if len(listeChoix) > 0 :
            listeStr = []
            for ID in listeChoix :
                listeStr.append(str(ID))
            criteres = ";".join(listeStr)
        return choix, criteres

    def Validation(self):
        choix, criteres = self.GetValeur() 
        if criteres == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement cocher au moins un item !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True


# -------------------------------------------------------------------------------------------------------------------------------

class CTRL_Page_coche(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_coche = wx.RadioButton(self, -1, u"Est coché", style=wx.RB_GROUP)
        self.radio_decoche = wx.RadioButton(self, -1, u"Est décoché")
        self.__do_layout()
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.radio_coche, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.radio_decoche, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "COCHE" : self.radio_coche.SetValue(True)
        if choix == "DECOCHE" : self.radio_decoche.SetValue(True)
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_coche.GetValue() == True : choix = "COCHE"
        if self.radio_decoche.GetValue() == True : choix = "DECOCHE"
        return choix, criteres

    def Validation(self):
        return True

# -------------------------------------------------------------------------------------------------------------------------------


class CTRL_Page_texte(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_egal = wx.RadioButton(self, -1, u"Est égal à", style=wx.RB_GROUP)
        self.ctrl_egal = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_different = wx.RadioButton(self, -1, u"Est différent de")
        self.ctrl_different = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_contient = wx.RadioButton(self, -1, u"Contient")
        self.ctrl_contient = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_contientpas = wx.RadioButton(self, -1, u"Ne contient pas")
        self.ctrl_contientpas = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_vide = wx.RadioButton(self, -1, u"Est vide")
        self.radio_pasvide = wx.RadioButton(self, -1, u"N'est pas vide")
        
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_contient)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_contientpas)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_vide)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_pasvide)
        
        self.OnRadio(None) 
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_contient = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_contient.Add(self.radio_contient, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contient.Add(self.ctrl_contient, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_contient, 1, wx.EXPAND, 0)
        grid_sizer_contientpas = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_contientpas.Add(self.radio_contientpas, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contientpas.Add(self.ctrl_contientpas, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_contientpas, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_vide, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_pasvide, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_contient.Enable(self.radio_contient.GetValue())
        self.ctrl_contientpas.Enable(self.radio_contientpas.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetValue(criteres)
        if choix == "DIFFERENT" : 
            self.radio_different.SetValue(True)
            self.ctrl_different.SetValue(criteres)
        if choix == "CONTIENT" : 
            self.radio_contient.SetValue(True)
            self.ctrl_contient.SetValue(criteres)
        if choix == "CONTIENTPAS" : 
            self.radio_contientpas.SetValue(True)
            self.ctrl_contientpas.SetValue(criteres)
        if choix == "VIDE" : 
            self.radio_vide.SetValue(True)
        if choix == "PASVIDE" : 
            self.radio_pasvide.SetValue(True)
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = self.ctrl_egal.GetValue()
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = self.ctrl_different.GetValue()
        if self.radio_contient.GetValue() == True :
            choix = "CONTIENT"
            criteres = self.ctrl_contient.GetValue()
        if self.radio_contientpas.GetValue() == True :
            choix = "CONTIENTPAS"
            criteres = self.ctrl_contientpas.GetValue()
        if self.radio_vide.GetValue() == True :
            choix = "VIDE"
        if self.radio_pasvide.GetValue() == True :
            choix = "PASVIDE"
        return choix, criteres

    def Validation(self):
        choix, criteres = self.GetValeur() 
        if choix not in ("VIDE", "PASVIDE") and criteres == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un texte !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

# -------------------------------------------------------------------------------------------------------------------------------



class CTRL_Page_entier(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_egal = wx.RadioButton(self, -1, u"Est égal à", style=wx.RB_GROUP)
        self.ctrl_egal = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.radio_different = wx.RadioButton(self, -1, u"Est différent de")
        self.ctrl_different = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.radio_sup = wx.RadioButton(self, -1, u"Est supérieur à")
        self.ctrl_sup = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.radio_supegal = wx.RadioButton(self, -1, u"Est supérieur ou égal à")
        self.ctrl_supegal = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.radio_inf = wx.RadioButton(self, -1, u"Est inférieur à")
        self.ctrl_inf = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.radio_infegal = wx.RadioButton(self, -1, u"Est inférieur ou égal à")
        self.ctrl_infegal = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.radio_compris = wx.RadioButton(self, -1, u"Est compris entre")
        self.ctrl_min = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_et = wx.StaticText(self, -1, u"et")
        self.ctrl_max = wx.SpinCtrl(self, -1, "", min=0, max=100)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_sup)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_supegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inf)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_infegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_compris)
        
        self.OnRadio(None) 
        
    def __set_properties(self):
        self.ctrl_egal.SetMinSize((80, -1))
        self.ctrl_different.SetMinSize((80, -1))
        self.ctrl_sup.SetMinSize((80, -1))
        self.ctrl_supegal.SetMinSize((80, -1))
        self.ctrl_inf.SetMinSize((80, -1))
        self.ctrl_infegal.SetMinSize((80, -1))
        self.ctrl_min.SetMinSize((80, -1))
        self.ctrl_max.SetMinSize((80, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_compris = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_infegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_inf = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_supegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_sup = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_sup.Add(self.radio_sup, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_sup.Add(self.ctrl_sup, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_sup, 1, wx.EXPAND, 0)
        grid_sizer_supegal.Add(self.radio_supegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_supegal.Add(self.ctrl_supegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_supegal, 1, wx.EXPAND, 0)
        grid_sizer_inf.Add(self.radio_inf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_inf.Add(self.ctrl_inf, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_inf, 1, wx.EXPAND, 0)
        grid_sizer_infegal.Add(self.radio_infegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infegal.Add(self.ctrl_infegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_infegal, 1, wx.EXPAND, 0)
        grid_sizer_compris.Add(self.radio_compris, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_min, 0, 0, 0)
        grid_sizer_compris.Add(self.label_et, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_compris, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_sup.Enable(self.radio_sup.GetValue())
        self.ctrl_supegal.Enable(self.radio_supegal.GetValue())
        self.ctrl_inf.Enable(self.radio_inf.GetValue())
        self.ctrl_infegal.Enable(self.radio_infegal.GetValue())
        self.ctrl_min.Enable(self.radio_compris.GetValue())
        self.ctrl_max.Enable(self.radio_compris.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetValue(int(criteres))
        if choix == "DIFFERENT" : 
            self.radio_diff.SetValue(True)
            self.ctrl_diff.SetValue(int(criteres))
        if choix == "SUP" : 
            self.radio_sup.SetValue(True)
            self.ctrl_sup.SetValue(int(criteres))
        if choix == "SUPEGAL" : 
            self.radio_supegal.SetValue(True)
            self.ctrl_supegal.SetValue(int(criteres))
        if choix == "INF" : 
            self.radio_inf.SetValue(True)
            self.ctrl_inf.SetValue(int(criteres))
        if choix == "INFEGAL" : 
            self.radio_infegal.SetValue(True)
            self.ctrl_infegal.SetValue(int(criteres))
        if choix == "COMPRIS" : 
            self.radio_compris.SetValue(True)
            min, max = criteres.split(";")
            self.ctrl_min.SetValue(int(min))
            self.ctrl_max.SetValue(int(max))
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = str(self.ctrl_egal.GetValue())
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = str(self.ctrl_different.GetValue())
        if self.radio_sup.GetValue() == True :
            choix = "SUP"
            criteres = str(self.ctrl_sup.GetValue())
        if self.radio_supegal.GetValue() == True :
            choix = "SUPEGAL"
            criteres = str(self.ctrl_supegal.GetValue())
        if self.radio_inf.GetValue() == True :
            choix = "INF"
            criteres = str(self.ctrl_inf.GetValue())
        if self.radio_infegal.GetValue() == True :
            choix = "INFEGAL"
            criteres = str(self.ctrl_infegal.GetValue())
        if self.radio_compris.GetValue() == True :
            choix = "COMPRIS"
            criteres = "%d;%d" % (self.ctrl_min.GetValue(), self.ctrl_max.GetValue())
        return choix, criteres

    def Validation(self):
        return True

# -------------------------------------------------------------------------------------------------------------------------------

class CTRL_Page_montant(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_egal = wx.RadioButton(self, -1, u"Est égal à", style=wx.RB_GROUP)
        self.ctrl_egal = CTRL_Saisie_euros.CTRL(self)
        self.radio_different = wx.RadioButton(self, -1, u"Est différent de")
        self.ctrl_different = CTRL_Saisie_euros.CTRL(self)
        self.radio_sup = wx.RadioButton(self, -1, u"Est supérieur à")
        self.ctrl_sup = CTRL_Saisie_euros.CTRL(self)
        self.radio_supegal = wx.RadioButton(self, -1, u"Est supérieur ou égal à")
        self.ctrl_supegal = CTRL_Saisie_euros.CTRL(self)
        self.radio_inf = wx.RadioButton(self, -1, u"Est inférieur à")
        self.ctrl_inf = CTRL_Saisie_euros.CTRL(self)
        self.radio_infegal = wx.RadioButton(self, -1, u"Est inférieur ou égal à")
        self.ctrl_infegal = CTRL_Saisie_euros.CTRL(self)
        self.radio_compris = wx.RadioButton(self, -1, u"Est compris entre")
        self.ctrl_min = CTRL_Saisie_euros.CTRL(self)
        self.label_et = wx.StaticText(self, -1, u"et")
        self.ctrl_max = CTRL_Saisie_euros.CTRL(self)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_sup)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_supegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inf)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_infegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_compris)
        
        self.OnRadio(None) 
        
    def __set_properties(self):
        self.ctrl_egal.SetMinSize((80, -1))
        self.ctrl_different.SetMinSize((80, -1))
        self.ctrl_sup.SetMinSize((80, -1))
        self.ctrl_supegal.SetMinSize((80, -1))
        self.ctrl_inf.SetMinSize((80, -1))
        self.ctrl_infegal.SetMinSize((80, -1))
        self.ctrl_min.SetMinSize((80, -1))
        self.ctrl_max.SetMinSize((80, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_compris = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_infegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_inf = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_supegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_sup = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_sup.Add(self.radio_sup, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_sup.Add(self.ctrl_sup, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_sup, 1, wx.EXPAND, 0)
        grid_sizer_supegal.Add(self.radio_supegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_supegal.Add(self.ctrl_supegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_supegal, 1, wx.EXPAND, 0)
        grid_sizer_inf.Add(self.radio_inf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_inf.Add(self.ctrl_inf, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_inf, 1, wx.EXPAND, 0)
        grid_sizer_infegal.Add(self.radio_infegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infegal.Add(self.ctrl_infegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_infegal, 1, wx.EXPAND, 0)
        grid_sizer_compris.Add(self.radio_compris, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_min, 0, 0, 0)
        grid_sizer_compris.Add(self.label_et, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_compris, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_sup.Enable(self.radio_sup.GetValue())
        self.ctrl_supegal.Enable(self.radio_supegal.GetValue())
        self.ctrl_inf.Enable(self.radio_inf.GetValue())
        self.ctrl_infegal.Enable(self.radio_infegal.GetValue())
        self.ctrl_min.Enable(self.radio_compris.GetValue())
        self.ctrl_max.Enable(self.radio_compris.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetMontant(float(criteres))
        if choix == "DIFFERENT" : 
            self.radio_diff.SetValue(True)
            self.ctrl_diff.SetMontant(float(criteres))
        if choix == "SUP" : 
            self.radio_sup.SetValue(True)
            self.ctrl_sup.SetMontant(float(criteres))
        if choix == "SUPEGAL" : 
            self.radio_supegal.SetValue(True)
            self.ctrl_supegal.SetMontant(float(criteres))
        if choix == "INF" : 
            self.radio_inf.SetValue(True)
            self.ctrl_inf.SetMontant(float(criteres))
        if choix == "INFEGAL" : 
            self.radio_infegal.SetValue(True)
            self.ctrl_infegal.SetMontant(float(criteres))
        if choix == "COMPRIS" : 
            self.radio_compris.SetValue(True)
            min, max = criteres.split(";")
            self.ctrl_min.SetMontant(float(min))
            self.ctrl_max.SetMontant(float(max))
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = str(self.ctrl_egal.GetMontant())
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = str(self.ctrl_different.GetMontant())
        if self.radio_sup.GetValue() == True :
            choix = "SUP"
            criteres = str(self.ctrl_sup.GetMontant())
        if self.radio_supegal.GetValue() == True :
            choix = "SUPEGAL"
            criteres = str(self.ctrl_supegal.GetMontant())
        if self.radio_inf.GetValue() == True :
            choix = "INF"
            criteres = str(self.ctrl_inf.GetMontant())
        if self.radio_infegal.GetValue() == True :
            choix = "INFEGAL"
            criteres = str(self.ctrl_infegal.GetMontant())
        if self.radio_compris.GetValue() == True :
            choix = "COMPRIS"
            criteres = "%d;%d" % (self.ctrl_min.GetMontant(), self.ctrl_max.GetMontant())
        return choix, criteres

    def Validation(self):
        return True

# -------------------------------------------------------------------------------------------------------------------------------


class CTRL_Page_date(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_egal = wx.RadioButton(self, -1, u"Est égal à", style=wx.RB_GROUP)
        self.ctrl_egal = CTRL_Saisie_date.Date2(self)
        self.radio_different = wx.RadioButton(self, -1, u"Est différent de")
        self.ctrl_different = CTRL_Saisie_date.Date2(self)
        self.radio_sup = wx.RadioButton(self, -1, u"Est supérieur à")
        self.ctrl_sup = CTRL_Saisie_date.Date2(self)
        self.radio_supegal = wx.RadioButton(self, -1, u"Est supérieur ou égal à")
        self.ctrl_supegal = CTRL_Saisie_date.Date2(self)
        self.radio_inf = wx.RadioButton(self, -1, u"Est inférieur à")
        self.ctrl_inf = CTRL_Saisie_date.Date2(self)
        self.radio_infegal = wx.RadioButton(self, -1, u"Est inférieur ou égal à")
        self.ctrl_infegal = CTRL_Saisie_date.Date2(self)
        self.radio_compris = wx.RadioButton(self, -1, u"Est compris entre")
        self.ctrl_min = CTRL_Saisie_date.Date2(self)
        self.label_et = wx.StaticText(self, -1, u"et")
        self.ctrl_max = CTRL_Saisie_date.Date2(self)

        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_sup)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_supegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inf)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_infegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_compris)
        
        self.OnRadio(None)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_compris = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_infegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_inf = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_supegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_sup = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_sup.Add(self.radio_sup, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_sup.Add(self.ctrl_sup, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_sup, 1, wx.EXPAND, 0)
        grid_sizer_supegal.Add(self.radio_supegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_supegal.Add(self.ctrl_supegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_supegal, 1, wx.EXPAND, 0)
        grid_sizer_inf.Add(self.radio_inf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_inf.Add(self.ctrl_inf, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_inf, 1, wx.EXPAND, 0)
        grid_sizer_infegal.Add(self.radio_infegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infegal.Add(self.ctrl_infegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_infegal, 1, wx.EXPAND, 0)
        grid_sizer_compris.Add(self.radio_compris, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_min, 0, 0, 0)
        grid_sizer_compris.Add(self.label_et, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_compris, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_sup.Enable(self.radio_sup.GetValue())
        self.ctrl_supegal.Enable(self.radio_supegal.GetValue())
        self.ctrl_inf.Enable(self.radio_inf.GetValue())
        self.ctrl_infegal.Enable(self.radio_infegal.GetValue())
        self.ctrl_min.Enable(self.radio_compris.GetValue())
        self.ctrl_max.Enable(self.radio_compris.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetDate(criteres)
        if choix == "DIFFERENT" : 
            self.radio_diff.SetValue(True)
            self.ctrl_diff.SetDate(criteres)
        if choix == "SUP" : 
            self.radio_sup.SetValue(True)
            self.ctrl_sup.SetDate(criteres)
        if choix == "SUPEGAL" : 
            self.radio_supegal.SetValue(True)
            self.ctrl_supegal.SetDate(criteres)
        if choix == "INF" : 
            self.radio_inf.SetValue(True)
            self.ctrl_inf.SetDate(criteres)
        if choix == "INFEGAL" : 
            self.radio_infegal.SetValue(True)
            self.ctrl_infegal.SetDate(criteres)
        if choix == "COMPRIS" : 
            self.radio_compris.SetValue(True)
            min, max = criteres.split(";")
            self.ctrl_min.SetDate(min)
            self.ctrl_max.SetDate(max)
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = (self.ctrl_egal.GetDate())
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = str(self.ctrl_different.GetDate())
        if self.radio_sup.GetValue() == True :
            choix = "SUP"
            criteres = str(self.ctrl_sup.GetDate())
        if self.radio_supegal.GetValue() == True :
            choix = "SUPEGAL"
            criteres = str(self.ctrl_supegal.GetDate())
        if self.radio_inf.GetValue() == True :
            choix = "INF"
            criteres = str(self.ctrl_inf.GetDate())
        if self.radio_infegal.GetValue() == True :
            choix = "INFEGAL"
            criteres = str(self.ctrl_infegal.GetDate())
        if self.radio_compris.GetValue() == True :
            choix = "COMPRIS"
            criteres = "%s;%s" % (self.ctrl_min.GetDate(), self.ctrl_max.GetDate())
        return choix, criteres

    def Validation(self):
        choix, criteres = self.GetValeur() 
        if criteres == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une date !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

# -------------------------------------------------------------------------------------------------------------------------------

class CTRL_Page_vide(wx.Panel):
    def __init__(self, parent, texte=u""):
        wx.Panel.__init__(self, parent, id=-1) 
        self.label_titre = wx.StaticText(self, -1, texte)
        grid_sizer = wx.FlexGridSizer(rows=1, cols=1, vgap=5, hgap=5)
        grid_sizer.Add(self.label_titre, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)

    def GetValeur(self):
        return None

    def Validation(self):
        dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune question !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return False


class CTRL_Titre(wx.Panel):
    def __init__(self, parent, titre=u"", image=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.SIMPLE_BORDER) 
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap("Images/32x32/%s" % image, wx.BITMAP_TYPE_ANY))
        if len(titre) > 40 :
            titre = titre[:40] + "..."
        self.label_titre = wx.StaticText(self, -1, titre)
        self.label_titre.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_image, 0, wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        grid_sizer.Add(self.label_titre, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer.AddGrowableCol(1)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)


class CTRL_Page(wx.Panel):
    def __init__(self, parent, IDquestion=None, titre=u"", image=None, filtre=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.SIMPLE_BORDER) 
        self.ctrl_titre = CTRL_Titre(self, titre, image)
        self.IDquestion = IDquestion
        self.filtre = filtre
        
        if filtre == "texte" : 
            self.ctrl_contenu = CTRL_Page_texte(self)
        elif filtre == "entier" : 
            self.ctrl_contenu = CTRL_Page_entier(self)
        elif filtre == "montant" : 
            self.ctrl_contenu = CTRL_Page_montant(self)
        elif filtre == "coche" : 
            self.ctrl_contenu = CTRL_Page_coche(self)
        elif filtre == "choix" : 
            self.ctrl_contenu = CTRL_Page_choix(self, IDquestion=IDquestion)
        elif filtre == "date" : 
            self.ctrl_contenu = CTRL_Page_date(self)
        else :
            self.ctrl_contenu = CTRL_Page_vide(self, texte=u"Aucun filtre disponible pour cette question !")

        grid_sizer = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_titre, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer.Add(self.ctrl_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer.AddGrowableCol(0)
        grid_sizer.AddGrowableRow(1)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
    
    def SetValeur(self, choix="", criteres=""):
        self.ctrl_contenu.SetValeur(choix, criteres)
    
    def GetValeur(self):
        return self.ctrl_contenu.GetValeur() 
    
    def Validation(self):
        return self.ctrl_contenu.Validation() 
    
    def GetFiltre(self):
        return self.filtre
    
    def GetIDquestion(self):
        return self.IDquestion 
    
    
class CTRL_Filtres(wx.Treebook):
    def __init__(self, parent, id=wx.ID_ANY, listeTypes=("famille", "individu"), pos=wx.DefaultPosition, size=wx.DefaultSize, style= wx.BK_DEFAULT):
        wx.Treebook.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.listeTypes = listeTypes
        
        self.dictControles = self.GetDictControles() 
        
        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Création de l'ImageList
        self.dictImages = {}
        self.il = wx.ImageList(32, 32)
        for controle in LISTE_CONTROLES :
            self.dictImages[controle["code"]] = {"ID":self.il.Add(wx.Bitmap("Images/32x32/%s" % controle["image"], wx.BITMAP_TYPE_ANY)), "nom":controle["image"]}
        self.dictImages["famille"] = {"ID":self.il.Add(wx.Bitmap("Images/32x32/Famille.png", wx.BITMAP_TYPE_ANY)), "nom":"Famille.png"}
        self.dictImages["individu"] = {"ID":self.il.Add(wx.Bitmap("Images/32x32/Personnes.png", wx.BITMAP_TYPE_ANY)), "nom":"Personnes.png"}
        self.AssignImageList(self.il)
        
        # Binds
        self.Bind(wx.EVT_TREEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
        self.MAJ() 
    
    def GetDictControles(self):
        dictControles = {}
        for controle in LISTE_CONTROLES :
            dictControles[controle["code"]] = controle
        return dictControles

    def MAJ(self):
        self.dictQuestions = self.Importation() 
        self.dictItems = {}
        
        # Remplissage
        index = 0
        for type in self.listeTypes :
            if len(self.dictQuestions[type]) > 0 :
                
                # Création de la page TYPE (famille ou individu)
                panel = CTRL_Page_vide(self, texte=u"Veuillez sélectionner une question dans la liste !")
                if type == "famille" :
                    label = u"Questions familiales"
                else :
                    label = u"Questions individuelles"
                self.AddPage(panel, label, imageId=self.dictImages[type]["ID"])
                indexType = int(index)
                index += 1
                
                # Création des pages QUESTIONS
                for dictQuestion in self.dictQuestions[type] :
                    IDquestion = dictQuestion["IDquestion"]
                    titre = dictQuestion["label"]
                    image = self.dictImages[dictQuestion["controle"]]["nom"]
                    filtre = self.dictControles[dictQuestion["controle"]]["filtre"]
                    panel = CTRL_Page(self, IDquestion=IDquestion, titre=titre, image=image, filtre=filtre)
                    self.AddSubPage(panel, dictQuestion["label"], imageId=self.dictImages[dictQuestion["controle"]]["ID"])
                    self.dictItems[dictQuestion["IDquestion"]] = index
                    index += 1
                    
                self.ExpandNode(indexType) 
        
    def Importation(self):
        # Importation des questions existantes
        DB = GestionDB.DB()
        req = """SELECT IDquestion, questionnaire_questions.IDcategorie, 
        questionnaire_categories.type, questionnaire_questions.visible, 
        questionnaire_questions.label, questionnaire_questions.controle
        FROM questionnaire_questions
        LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
        ORDER BY questionnaire_questions.ordre
        ;"""
        DB.ExecuterReq(req)
        listeQuestions = DB.ResultatReq()     
        DB.Close() 
        
        dictQuestions = { "famille" : [], "individu" : []}
        for IDquestion, IDcategorie, type, visible, label, controle in listeQuestions :
            dictTemp = {"IDquestion":IDquestion, "IDcategorie":IDcategorie, "type":type, "visible":visible, "label":label, "controle":controle}
            dictQuestions[type].append(dictTemp)
            
        return dictQuestions
        
    def GetQuestion(self):
        indexSelection = self.GetSelection() 
        for IDquestion, index in self.dictItems.iteritems() :
            if index == indexSelection :
                return IDquestion
        return None
    
    def SetQuestion(self, IDquestion=None):
        if self.dictItems.has_key(IDquestion) :
            self.SetSelection(self.dictItems[IDquestion])

    def OnPageChanged(self, event):
        #print self.GetQuestion() 
        pass
    
    def SetValeur(self, choix="", criteres=""):
        page = self.GetCurrentPage()
        page.SetValeur(choix, criteres)
    
    def GetValeur(self):
        page = self.GetCurrentPage()
        return page.GetValeur() 
    
    def GetFiltre(self):
        page = self.GetCurrentPage()
        return page.GetFiltre() 
        
    def Validation(self):
        page = self.GetCurrentPage()
        return page.Validation() 

# -------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, listeTypes=("famille", "individu")):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        self.listeTypes = listeTypes
        self.SetTitle(u"Saisie d'un filtre")  
        
        self.ctrl_filtres = CTRL_Filtres(self, listeTypes=listeTypes)
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetMinSize((760, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_filtres, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
            
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_filtres.Validation() == False :
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetValeur(self):
        # Récupération des valeurs
        return self.ctrl_filtres.GetValeur() 
    
    def SetValeur(self, choix="", criteres=""):
        self.ctrl_filtres.SetValeur(choix, criteres)
        
    def GetQuestion(self):
        return self.ctrl_filtres.GetQuestion() 
    
    def GetFiltre(self):
        return self.ctrl_filtres.GetFiltre() 
    
    def SetQuestion(self, IDquestion=None):
        self.SetTitle(u"Modification d'un filtre")  
        self.ctrl_filtres.SetQuestion(IDquestion) 
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    # Test d'importation
    dialog_1.SetQuestion(2)
    dialog_1.SetValeur("CONTIENT", u"Ceci est un test  !")
    
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
