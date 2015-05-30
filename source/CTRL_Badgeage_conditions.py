#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import wx.lib.agw.flatnotebook as FNB
import copy

import GestionDB

import CTRL_Saisie_heure
import OL_Filtres_questionnaire


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))



class CTRL_Activite(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetMinSize((-1, 100))
        self.data = []
        self.Importation() 
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeValeurs = []
        for IDactivite, nom, abrege in listeDonnees :
            listeValeurs.append((IDactivite, nom, False)) 
        self.SetData(listeValeurs)
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
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
    
    def GetTexteCoches(self):
        listeIDcoches = []
        listeTemp = self.GetIDcoches() 
        if len(listeTemp) == 0 : return None
        for ID in listeTemp :
            listeIDcoches.append(str(ID))
        texte = ";".join(listeIDcoches)
        return texte

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

# --------------------------------------------------------------------------------------------------------


class CTRL_Heure(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL | wx.SIMPLE_BORDER) 
        self.SetBackgroundColour((255, 255, 255))
        self.radio_egal = wx.RadioButton(self, -1, _(u"Est égal à"), style=wx.RB_GROUP)
        self.ctrl_egal = CTRL_Saisie_heure.Heure(self)
        self.radio_different = wx.RadioButton(self, -1, _(u"Est différent de"))
        self.ctrl_different = CTRL_Saisie_heure.Heure(self)
        self.radio_sup = wx.RadioButton(self, -1, _(u"Est supérieur à"))
        self.ctrl_sup = CTRL_Saisie_heure.Heure(self)
        self.radio_supegal = wx.RadioButton(self, -1, _(u"Est supérieur ou égal à"))
        self.ctrl_supegal = CTRL_Saisie_heure.Heure(self)
        self.radio_inf = wx.RadioButton(self, -1, _(u"Est inférieur à"))
        self.ctrl_inf = CTRL_Saisie_heure.Heure(self)
        self.radio_infegal = wx.RadioButton(self, -1, _(u"Est inférieur ou égal à"))
        self.ctrl_infegal = CTRL_Saisie_heure.Heure(self)
        self.radio_compris = wx.RadioButton(self, -1, _(u"Est compris entre"))
        self.ctrl_min = CTRL_Saisie_heure.Heure(self)
        self.label_et = wx.StaticText(self, -1, _(u"et"))
        self.ctrl_max = CTRL_Saisie_heure.Heure(self)

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
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_sup.Add(self.radio_sup, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_sup.Add(self.ctrl_sup, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_sup, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_supegal.Add(self.radio_supegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_supegal.Add(self.ctrl_supegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_supegal, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_inf.Add(self.radio_inf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_inf.Add(self.ctrl_inf, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_inf, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_infegal.Add(self.radio_infegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infegal.Add(self.ctrl_infegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_infegal, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_compris.Add(self.radio_compris, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_min, 0, 0, 0)
        grid_sizer_compris.Add(self.label_et, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_compris, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
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
            self.ctrl_egal.SetHeure(criteres)
        if choix == "DIFFERENT" : 
            self.radio_diff.SetValue(True)
            self.ctrl_diff.SetHeure(criteres)
        if choix == "SUP" : 
            self.radio_sup.SetValue(True)
            self.ctrl_sup.SetHeure(criteres)
        if choix == "SUPEGAL" : 
            self.radio_supegal.SetValue(True)
            self.ctrl_supegal.SetHeure(criteres)
        if choix == "INF" : 
            self.radio_inf.SetValue(True)
            self.ctrl_inf.SetHeure(criteres)
        if choix == "INFEGAL" : 
            self.radio_infegal.SetValue(True)
            self.ctrl_infegal.SetHeure(criteres)
        if choix == "COMPRIS" : 
            self.radio_compris.SetValue(True)
            min, max = criteres.split("-")
            self.ctrl_min.SetHeure(min)
            self.ctrl_max.SetHeure(max)
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = (self.ctrl_egal.GetHeure())
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = str(self.ctrl_different.GetHeure())
        if self.radio_sup.GetValue() == True :
            choix = "SUP"
            criteres = str(self.ctrl_sup.GetHeure())
        if self.radio_supegal.GetValue() == True :
            choix = "SUPEGAL"
            criteres = str(self.ctrl_supegal.GetHeure())
        if self.radio_inf.GetValue() == True :
            choix = "INF"
            criteres = str(self.ctrl_inf.GetHeure())
        if self.radio_infegal.GetValue() == True :
            choix = "INFEGAL"
            criteres = str(self.ctrl_infegal.GetHeure())
        if self.radio_compris.GetValue() == True :
            choix = "COMPRIS"
            criteres = "%s-%s" % (self.ctrl_min.GetHeure(), self.ctrl_max.GetHeure())
        return choix, criteres

    def Validation(self):
        choix, criteres = self.GetValeur() 
        if criteres == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Periode(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL | wx.SIMPLE_BORDER)
        self.parent = parent
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        self.SetBackgroundColour((255, 255, 255))
        
        # Périodes scolaires
        self.label_periodes_scolaires = wx.StaticText(self, -1,_(u"> Périodes scolaires :"))
        self.CreationCaseJours("scolaire")
        
        # Périodes de vacances
        self.label_periodes_vacances = wx.StaticText(self, -1,_(u"> Périodes de vacances :"))
        self.CreationCaseJours("vacances")
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
                
        # Périodes scolaires
        grid_sizer_base.Add(self.label_periodes_scolaires, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)

        grid_sizer_scolaire = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        for jour in self.liste_jours :
            exec("grid_sizer_scolaire.Add(self.check_scolaire_%s, 0, 0, 0)" % jour)
        grid_sizer_base.Add(grid_sizer_scolaire, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Périodes de vacances
        grid_sizer_base.Add(self.label_periodes_vacances, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        grid_sizer_vacances = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        for jour in self.liste_jours :
            exec("grid_sizer_vacances.Add(self.check_vacances_%s, 0, 0, 0)" % jour)
        grid_sizer_base.Add(grid_sizer_vacances, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
                
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
    
    def CreationCaseJours(self, periode="scolaire"):
        for jour in self.liste_jours :
            exec("self.check_%s_%s = wx.CheckBox(self, -1,u'%s')" % (periode, jour, jour[0].upper()) )
            exec("self.check_%s_%s.SetToolTipString(u'%s')" % (periode, jour, jour.capitalize()) )

    def GetJours(self, periode="scolaire"):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            exec("etat = self.check_%s_%s.GetValue()" % (periode, jour))
            if etat == True :
                listeTemp.append(str(index))
            index += 1
        texte = ";".join(listeTemp)
        if len(texte) == 0 :
            texte = None
        return texte
    
    def SetJours(self, periode="scolaire", texteJours=""):
        if texteJours == None or len(texteJours) == 0 :
            return
        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = "True"
            else :
                etat = "False"
            exec("self.check_%s_%s.SetValue(%s)" % (periode, jour, etat))
            index += 1
            

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Poste(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.listeValeurs = []
    
    def SetValeur(self, valeur=""):
        self.listeValeurs = []
        if valeur != None :
            self.listeValeurs = valeur.split(";")
        self.MAJ() 
        
    def GetValeur(self):
        if len(self.listeValeurs) > 0 :
            return ";".join(self.listeValeurs)
        else :
            return None
    
    def MAJ(self):
        self.listeValeurs.sort()
        self.Set(self.listeValeurs)
    
    def Ajouter(self):
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du poste réseau :"), _(u"Saisie"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                self.listeValeurs.append(nom)
                self.MAJ()
        dlg.Destroy()
        
    def Modifier(self):
        valeur = self.GetStringSelection()
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun poste à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.TextEntryDialog(self, _(u"Modifiez le nom du poste réseau :"), _(u"Modification"), valeur)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                self.listeValeurs[index] = nom
                self.MAJ()
        dlg.Destroy()

    def Supprimer(self):
        valeur = self.GetStringSelection()
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun poste à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce poste ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
                self.listeValeurs.pop(index)
                self.MAJ()
        dlg.Destroy()

        
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_Activite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Groupes
        self.check = wx.CheckBox(self, -1, _(u"Uniquement si l'individu est inscrit à l'une des activités cochées :"))
        self.ctrl = CTRL_Activite(self)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check)

        # Init
        self.OnCheck(None)

    def __set_properties(self):
        self.check.SetToolTipString(_(u"Cochez cette case si vous souhaitez appliquer un filtre sur les activités"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheck(self, event):
        self.ctrl.Enable(self.check.GetValue())
        self.parent.SurbrillanceLabel("activite", self.check.GetValue())
                
    def SetValeur(self, valeur=""):
        if valeur == None :
            self.check.SetValue(False)
        else :
            listeActivites = []
            listeTemp = valeur.split(";")
            for IDactivite in listeTemp :
                listeActivites.append(int(IDactivite))
            self.ctrl.SetIDcoches(listeActivites)
            self.check.SetValue(True)
        self.OnCheck(None)

    def GetValeur(self):
        if self.check.GetValue() == True :
            valeur = self.ctrl.GetTexteCoches()
        else:
            valeur = None
        return valeur

    def Validation(self):
        # Vérifie la saisie
        if self.check.GetValue() == True :
            if self.GetValeur() == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune activité !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_Heure(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.check = wx.CheckBox(self, -1, _(u"Uniquement si l'heure de badgeage..."))
        self.ctrl_heure = CTRL_Heure(self)

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check)

        self.OnCheck(None)

    def __set_properties(self):
        self.check.SetToolTipString(_(u"Cochez cette case si vous souhaitez appliquer un filtre sur l'heure de badgeage"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl_heure, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheck(self, event):
        self.ctrl_heure.Enable(self.check.GetValue())
        self.parent.SurbrillanceLabel("heure", self.check.GetValue())
                
    def SetValeur(self, valeur=""):
        # Exemple de valeur : "EGAL;10:45"
        if valeur == None :
            self.check.SetValue(False)
        else :
            choix, criteres = valeur.split(";")
            self.ctrl_heure.SetValeur(choix, criteres)
            self.check.SetValue(True)
        self.OnCheck(None)

    def GetValeur(self):
        if self.check.GetValue() == True :
            choix, criteres = self.ctrl_heure.GetValeur()
            valeur = u"%s;%s" % (choix, criteres)
        else:
            valeur = None
        return valeur

    def Validation(self):
        # Vérifie les données saisies
        if self.check.GetValue() == True :
            return self.ctrl_heure.Validation()
        return True


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_Periode(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Caisses
        self.check = wx.CheckBox(self, -1, _(u"Uniquement sur les jours cochés :"))
        self.ctrl_periode = CTRL_Periode(self)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check)

        # Init
        self.OnCheck(None)

    def __set_properties(self):
        self.check.SetToolTipString(_(u"Cochez cette case si vous souhaitez appliquer un filtre de périodes"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl_periode, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheck(self, event):
        self.ctrl_periode.Enable(self.check.GetValue())
        self.parent.SurbrillanceLabel("periode", self.check.GetValue())
                
    def SetValeur(self, valeur=None):
        if valeur == None :
            self.check.SetValue(False)
        else :
            jours_scolaires, jours_vacances = valeur.split("-")
            if jours_scolaires == "None" : jours_scolaires = None
            if jours_vacances == "None" : jours_vacances = None
            self.ctrl_periode.SetJours("scolaire", jours_scolaires)
            self.ctrl_periode.SetJours("vacances", jours_vacances)
            self.check.SetValue(True)
        self.OnCheck(None)

    def GetValeur(self):
        if self.check.GetValue() == True :
            jours_scolaires = self.ctrl_periode.GetJours("scolaire")
            jours_vacances = self.ctrl_periode.GetJours("vacances")
            valeur = u"%s-%s" % (jours_scolaires, jours_vacances)
        else:
            valeur = None
        return valeur

    def Validation(self):
        # Vérifie la saisie
        if self.check.GetValue() == True :
            valeur = self.GetValeur()
            if valeur == "None-None" :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucun jour !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_Poste(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listeInitiale = [] 
        
        self.check = wx.CheckBox(self, -1, _(u"Uniquement sur les postes réseau suivants :"))
        self.ctrl = CTRL_Poste(self)
        self.ctrl.SetMinSize((150, 50))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check)
        self.Bind(wx.EVT_BUTTON, self.OnAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimer, self.bouton_supprimer)

        # Init
        self.OnCheck(None)

    def __set_properties(self):
        self.check.SetToolTipString(_(u"Cochez cette case pour appliquer un filtre sur les noms de postes réseau"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un nom de poste"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le nom de poste sélectionné dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le nom de poste sélectionné dans la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check, 0, wx.ALL, 5)
        grid_sizer_base.Add( (2, 2), 0, 0, 0)
        grid_sizer_base.Add(self.ctrl, 1, wx.BOTTOM|wx.LEFT|wx.EXPAND, 5)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheck(self, event):
        self.ctrl.Enable(self.check.GetValue())
        self.bouton_ajouter.Enable(self.check.GetValue())
        self.bouton_modifier.Enable(self.check.GetValue())
        self.bouton_supprimer.Enable(self.check.GetValue())
        self.parent.SurbrillanceLabel("poste", self.check.GetValue())

    def OnAjouter(self, event): 
        self.ctrl.Ajouter()

    def OnModifier(self, event): 
        self.ctrl.Modifier() 

    def OnSupprimer(self, event):
        self.ctrl.Supprimer() 

    def SetValeur(self, valeur=None):
        if valeur == None :
            self.check.SetValue(False)
        else :
            self.ctrl.SetValeur(valeur)
            self.listeInitiale = copy.deepcopy(valeur)
            self.check.SetValue(True)
        self.OnCheck(None)
    
    def GetListeInitiale(self):
        return self.listeInitiale
    
    def GetValeur(self):
        if self.check.GetValue() == True :
            listeDonnees = self.ctrl.GetValeur()
        else :
            listeDonnees = None
        return listeDonnees

    def Validation(self):
        # Vérifie la saisie
        if self.check.GetValue() == True and self.GetValeur() == None :
            dlg = wx.MessageDialog(self, _(u"Vous avez coché la condition 'Poste' mais sans saisir de noms de poste !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_Questionnaire(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listeInitialeFiltres = [] 
        
        # Cotisations
        self.check_filtres = wx.CheckBox(self, -1, _(u"Uniquement selon les filtres questionnaires suivants :"))
        self.ctrl_filtres = OL_Filtres_questionnaire.ListView(self, listeDonnees=[], listeTypes=["individu",], id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_filtres.SetMinSize((150, 50))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.check_filtres)
        self.Bind(wx.EVT_BUTTON, self.OnAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimer, self.bouton_supprimer)

        # Init
        self.OnCheckFiltres(None)

    def __set_properties(self):
        self.check_filtres.SetToolTipString(_(u"Cochez cette case pour appliquer des filtres sur les questionnaires individuels "))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un filtre"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le filtre sélectionné dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le filtre sélectionné dans la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_filtres, 0, wx.ALL, 5)
        grid_sizer_base.Add( (2, 2), 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_filtres, 1, wx.BOTTOM|wx.LEFT|wx.EXPAND, 5)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheckFiltres(self, event):
        self.ctrl_filtres.Enable(self.check_filtres.GetValue())
        self.bouton_ajouter.Enable(self.check_filtres.GetValue())
        self.bouton_modifier.Enable(self.check_filtres.GetValue())
        self.bouton_supprimer.Enable(self.check_filtres.GetValue())
        self.parent.SurbrillanceLabel("questionnaire", self.check_filtres.GetValue())

    def OnAjouter(self, event): 
        self.ctrl_filtres.Ajouter(None)

    def OnModifier(self, event): 
        self.ctrl_filtres.Modifier(None) 

    def OnSupprimer(self, event):
        self.ctrl_filtres.Supprimer(None) 

    def SetValeur(self, valeur=""):
        if valeur == None :
            self.check_filtres.SetValue(False)
        else :
            listeDonnees = []
            for donnees in valeur.split("##") :
                IDquestion, choix, criteres = donnees.split(";;")
                listeDonnees.append( {"IDfiltre":None, "IDquestion":int(IDquestion), "choix":choix, "criteres":criteres} )
            self.ctrl_filtres.SetDonnees(listeDonnees)
            self.listeInitialeFiltres = copy.deepcopy(listeDonnees)
            self.check_filtres.SetValue(True)
        self.OnCheckFiltres(None)
    
    def GetListeInitialeFiltres(self):
        return self.listeInitialeFiltres
    
    def GetValeur(self):
        if self.check_filtres.GetValue() == False :
            return None
        else :
            listeDonnees = self.ctrl_filtres.GetDonnees()
            listeTemp = []
            for dictTemp in listeDonnees :
                listeTemp.append(u"%d;;%s;;%s" % (dictTemp["IDquestion"], dictTemp["choix"],dictTemp["criteres"]) )
            valeur = "##".join(listeTemp)
            return valeur

    def Validation(self):
        # Vérifie les filtres
        if self.check_filtres.GetValue() == True and len(self.ctrl_filtres.GetDonnees()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez coché la condition 'Filtres de questionnaire' mais sans saisir de filtre !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True







# ---------------------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listePages = [] 
        
        self.notebook = FNB.FlatNotebook(self, -1, agwStyle= FNB.FNB_NO_TAB_FOCUS | FNB.FNB_NO_X_BUTTON)
        
        # Binds
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.notebook, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 0)
        self.SetSizer(box)
        box.Fit(self)
        
        # Init contrôles
        self.CreationPages() 
    
    def SurbrillanceLabel(self, codePage, etat=False):
        """ change la couleur du tab du notebook """
        index = self.GetIndexPage(codePage)
        if index == None : return
        if etat == True :
            couleur = wx.Colour(255, 0, 0)
        else:
            couleur = None
        self.notebook.SetPageTextColour(index, couleur)
    
    def GetIndexPage(self, code=""):
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                return dictPage["index"]
        return None
        
    def CreationPages(self):
        """ Création des pages du notebook """
        self.listePages = [
            {"index" : 0, "code" : "activite", "ctrl" : Page_Activite(self), "label" : _(u"Activité")},
            {"index" : 1, "code" : "heure", "ctrl" : Page_Heure(self), "label" : _(u"Heure")},
            {"index" : 2, "code" : "periode", "ctrl" : Page_Periode(self), "label" : _(u"Période")},
            {"index" : 3, "code" : "poste", "ctrl" : Page_Poste(self), "label" : _(u"Poste")},
            {"index" : 4, "code" : "questionnaire", "ctrl" : Page_Questionnaire(self), "label" : _(u"Questionnaire")},
            ]
        
        self.dictPages = {}
        for dictPage in self.listePages :
            self.notebook.AddPage(dictPage["ctrl"], dictPage["label"])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]

    def Validation(self):
        for dictPage in self.listePages :
            if dictPage["ctrl"].Validation() == False :
                return False
        return True
    
    def SetValeur(self, codePage="", valeur=None):
        self.dictPages[codePage].SetValeur(valeur)
        
    def GetValeur(self, codePage=""):
        return self.dictPages[codePage].GetValeur()
    
    def GetDonnees(self):
        dictDonnees = {}
        for dictPage in self.listePages :
            code = dictPage["code"]
            dictDonnees["condition_%s" % code] = self.GetValeur(code)
        return dictDonnees
    
    def SetDonnees(self, dictDonnees={}):
        for code, valeur in dictDonnees.iteritems() :
            self.SetValeur(code, valeur)
            
    
    

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

        # Test ACTIVITES
        self.ctrl.SetValeur("activite", "1;2")
        print "Activite =", self.ctrl.GetValeur("activite")

        # Test HEURE
        self.ctrl.SetValeur("heure", "COMPRIS;10:45-11:50")
        print "Heure =", self.ctrl.GetValeur("heure")
        
        # Test PERIODE
        self.ctrl.SetValeur("periode", "1-2")
        print "Periode =", self.ctrl.GetValeur("periode")
        
        # Test POSTE
        self.ctrl.SetValeur("poste", "poste1;poste2;poste3")
        print "Poste =", self.ctrl.GetValeur("poste")

        # Test QUESTIONNAIRE
        self.ctrl.SetValeur("questionnaire", "1;;EGAL;;bonjour##4;;SUPEGAL;;2")
        print "Questionnaire =", self.ctrl.GetValeur("questionnaire")



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()