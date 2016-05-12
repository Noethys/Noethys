#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import wx.lib.agw.flatnotebook as FNB
import copy

import GestionDB
from Ol import OL_Filtres_questionnaire
import CTRL_Etiquettes
from Utils import UTILS_Texte


class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetMinSize((-1, 80))
        self.IDactivite = IDactivite
        self.data = []
        self.Importation() 
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeValeurs = []
        for IDgroupe, nom in listeDonnees :
            listeValeurs.append((IDgroupe, nom, False)) 
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

class CTRL_Cotisations(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.Importation() 
    
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDtype_cotisation, nom, type, carte, defaut 
        FROM types_cotisations ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeValeurs = []
        for IDtype_cotisation, nom, type, carte, defaut  in listeDonnees :
            listeValeurs.append((IDtype_cotisation, nom, False)) 
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

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Caisses(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeCaisses = []
        self.dictCaisses = {}
        self.MAJ() 

    def MAJ(self):
        self.listeCaisses, self.dictCaisses = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeCaisses = [(_(u"Caisse non spécifiée"), 0),]
        dictCaisses = {"nom":_(u"Caisse non spécifiée"), "IDcaisse":0}

        DB = GestionDB.DB()
        req = """SELECT IDcaisse, nom
        FROM caisses
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDcaisse, nom in listeDonnees :
            dictTemp = { "nom" : nom, "IDcaisse" : IDcaisse}
            dictCaisses[IDcaisse] = dictTemp
            listeCaisses.append((nom, IDcaisse))
        listeCaisses.sort()
        return listeCaisses, dictCaisses

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 1
        for nom, IDcaisse in self.listeCaisses :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeCaisses)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeCaisses[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeCaisses)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeCaisses)):
            ID = self.listeCaisses[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetListeCaisses(self):
        return self.GetIDcoches() 
    
    def GetDictCaisses(self):
        return self.dictCaisses

    def GetTexteCoches(self):
        listeIDcoches = []
        listeTemp = self.GetIDcoches() 
        if len(listeTemp) == 0 : return None
        for ID in listeTemp :
            listeIDcoches.append(str(ID))
        texte = ";".join(listeIDcoches)
        return texte

# -------------------------------------------------------------------------------------------------------------------

class CTRL_Periodes(wx.Panel):
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
            
        
# ---------------------------------------------------------------------------------------------------------------------------------------

class Page_Groupes(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif

        # Groupes
        self.check_groupes = wx.CheckBox(self, -1, _(u"Uniquement pour les groupes cochés :"))
        self.ctrl_groupes = CTRL_Groupes(self, IDactivite)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckGroupes, self.check_groupes)

        # Init
        self.OnCheckGroupes(None)

    def __set_properties(self):
        self.check_groupes.SetToolTipString(_(u"Cochez cette case si vous souhaitez appliquer un filtre de groupe"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_groupes, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl_groupes, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheckGroupes(self, event):
        self.ctrl_groupes.Enable(self.check_groupes.GetValue())
        self.parent.SurbrillanceLabel("groupes", self.check_groupes.GetValue())
                
    def SetGroupes(self, groupes):
        if groupes != None :
            listeGroupes = []
            listeTemp = groupes.split(";")
            for IDgroupe in listeTemp :
                listeGroupes.append(int(IDgroupe))
            self.ctrl_groupes.SetIDcoches(listeGroupes)
            self.check_groupes.SetValue(True)
        else:
            self.check_groupes.SetValue(False)
        self.OnCheckGroupes(None)

    def GetGroupes(self):
        if self.check_groupes.GetValue() == True :
            texteGroupes = self.ctrl_groupes.GetTexteCoches()
        else:
            texteGroupes = None
        return texteGroupes

    def Validation(self):
        # Vérifie les groupes
        if self.check_groupes.GetValue() == True :
            if len(self.ctrl_groupes.GetIDcoches()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucun groupe !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True


# ---------------------------------------------------------------------------------------------------------------------------------------

class Page_Etiquettes(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif

        # Etiquettes
        self.check_etiquettes = wx.CheckBox(self, -1, _(u"Uniquement pour les étiquettes cochées :"))
        self.ctrl_etiquettes = CTRL_Etiquettes.CTRL(self, listeActivites=[self.IDactivite,], nomActivite=u"Activité", activeMenu=False)
        self.ctrl_etiquettes.MAJ() 
        
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEtiquettes, self.check_etiquettes)

        # Init
        self.OnCheckEtiquettes(None)

    def __set_properties(self):
        self.check_etiquettes.SetToolTipString(_(u"Cochez cette case si vous souhaitez appliquer un filtre sur les étiquettes"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_etiquettes, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl_etiquettes, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheckEtiquettes(self, event):
        self.ctrl_etiquettes.Activation(self.check_etiquettes.GetValue())
        self.parent.SurbrillanceLabel("etiquettes", self.check_etiquettes.GetValue())
                
    def SetEtiquettes(self, etiquettes=None):
        if etiquettes not in (None, "") :
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
            self.ctrl_etiquettes.SetCoches(etiquettes)
            self.check_etiquettes.SetValue(True)
        else:
            self.check_etiquettes.SetValue(False)
        self.OnCheckEtiquettes(None)

    def GetEtiquettes(self):
        if self.check_etiquettes.GetValue() == True :
            texteEtiquettes = UTILS_Texte.ConvertListeToStr(self.ctrl_etiquettes.GetCoches())
        else:
            texteEtiquettes = None
        return texteEtiquettes

    def Validation(self):
        # Vérifie les étiquettes
        if self.check_etiquettes.GetValue() == True :
            if len(self.ctrl_etiquettes.GetCoches()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune étiquette !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True



# ---------------------------------------------------------------------------------------------------------------------------------------

class Page_Cotisations(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif

        # Cotisations
        self.check_cotisations = wx.CheckBox(self, -1, _(u"Uniquement si au moins une des cotisations cochées est à jour :"))
        self.ctrl_cotisations = CTRL_Cotisations(self)
        self.ctrl_cotisations.SetMinSize((150, 50))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCotisations, self.check_cotisations)

        # Init
        self.OnCheckCotisations(None)

    def __set_properties(self):
        self.check_cotisations.SetToolTipString(_(u"Cochez cette case pour appliquer ce tarif uniquement lorsque une des cotisations cochées est à jour"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_cotisations, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl_cotisations, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheckCotisations(self, event):
        if self.check_cotisations.GetValue() == True :
            self.ctrl_cotisations.Enable(True)
        else:
            self.ctrl_cotisations.Enable(False)
        self.parent.SurbrillanceLabel("cotisations", self.check_cotisations.GetValue())
        
    def SetCotisations(self, cotisations):
        if cotisations != None :
            listeCotisations = []
            listeTemp = cotisations.split(";")
            for IDtype_cotisation in listeTemp :
                listeCotisations.append(int(IDtype_cotisation))
            self.ctrl_cotisations.SetIDcoches(listeCotisations)
            self.check_cotisations.SetValue(True)
        else:
            self.check_cotisations.SetValue(False)
        self.OnCheckCotisations(None)
        
    def GetCotisations(self):
        if self.check_cotisations.GetValue() == True :
            texteCotisations = self.ctrl_cotisations.GetTexteCoches()
        else:
            texteCotisations = None
        return texteCotisations

    def Validation(self):
        return True




class Page_Questionnaires(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.listeInitialeFiltres = [] 
        
        # Cotisations
        self.check_filtres = wx.CheckBox(self, -1, _(u"Uniquement selon les filtres suivants :"))
        self.ctrl_filtres = OL_Filtres_questionnaire.ListView(self, listeDonnees=[], id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_filtres.SetMinSize((150, 50))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

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
        self.check_filtres.SetToolTipString(_(u"Cochez cette case pour appliquer des filtres sur les questionnaires individuels ou familiaux"))
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
        self.parent.SurbrillanceLabel("questionnaires", self.check_filtres.GetValue())

    def OnAjouter(self, event): 
        self.ctrl_filtres.Ajouter(None)

    def OnModifier(self, event): 
        self.ctrl_filtres.Modifier(None) 

    def OnSupprimer(self, event):
        self.ctrl_filtres.Supprimer(None) 

    def SetFiltres(self, listeFiltres):
        if len(listeFiltres) > 0 :
            self.check_filtres.SetValue(True)
        listeDonnees = []
        for IDfiltre, IDquestion, choix, criteres in listeFiltres :
            listeDonnees.append( {"IDfiltre":IDfiltre, "IDquestion":IDquestion, "choix":choix, "criteres":criteres} )
        self.ctrl_filtres.SetDonnees(listeDonnees)
        self.listeInitialeFiltres = copy.deepcopy(listeDonnees)
        self.OnCheckFiltres(None)
    
    def GetListeInitialeFiltres(self):
        return self.listeInitialeFiltres
    
    def GetFiltres(self):
        if self.check_filtres.GetValue() == True :
            listeDonnees = self.ctrl_filtres.GetDonnees()
        else:
            listeDonnees = []
        return listeDonnees

    def Validation(self):
        # Vérifie les filtres
        if self.check_filtres.GetValue() == True and len(self.GetFiltres()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez coché la condition 'Filtres de questionnaire' mais sans saisir de filtre !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_Caisses(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Caisses
        self.check_caisses = wx.CheckBox(self, -1, _(u"Uniquement pour les caisses cochées :"))
        self.ctrl_caisses = CTRL_Caisses(self)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCaisses, self.check_caisses)

        # Init
        self.OnCheckCaisses(None)

    def __set_properties(self):
        self.check_caisses.SetToolTipString(_(u"Cochez cette case si vous souhaitez appliquer un filtre de caisses"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_caisses, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl_caisses, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheckCaisses(self, event):
        self.ctrl_caisses.Enable(self.check_caisses.GetValue())
        self.parent.SurbrillanceLabel("caisses", self.check_caisses.GetValue())
                
    def SetCaisses(self, caisses):
        if caisses != None :
            listeCaisses = []
            listeTemp = caisses.split(";")
            for IDcaisse in listeTemp :
                listeCaisses.append(int(IDcaisse))
            self.ctrl_caisses.SetIDcoches(listeCaisses)
            self.check_caisses.SetValue(True)
        else:
            self.check_caisses.SetValue(False)
        self.OnCheckCaisses(None)

    def GetCaisses(self):
        if self.check_caisses.GetValue() == True :
            texteCaisses = self.ctrl_caisses.GetTexteCoches()
        else:
            texteCaisses = None
        return texteCaisses

    def Validation(self):
        # Vérifie les caisses
        if self.check_caisses.GetValue() == True :
            if len(self.ctrl_caisses.GetIDcoches()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune caisse !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_Periodes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Caisses
        self.check_periodes = wx.CheckBox(self, -1, _(u"Uniquement sur les jours cochés :"))
        self.ctrl_periodes = CTRL_Periodes(self)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckPeriodes, self.check_periodes)

        # Init
        self.OnCheckPeriodes(None)

    def __set_properties(self):
        self.check_periodes.SetToolTipString(_(u"Cochez cette case si vous souhaitez appliquer un filtre de périodes"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_periodes, 0, wx.ALL, 5)
        grid_sizer_base.Add(self.ctrl_periodes, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnCheckPeriodes(self, event):
        self.ctrl_periodes.Enable(self.check_periodes.GetValue())
        self.parent.SurbrillanceLabel("periodes", self.check_periodes.GetValue())
                
    def SetPeriodes(self, jours_scolaires=None, jours_vacances=None):
        if jours_scolaires == None and jours_vacances == None :
            self.check_periodes.SetValue(False)
        else :
            self.ctrl_periodes.SetJours("scolaire", jours_scolaires)
            self.ctrl_periodes.SetJours("vacances", jours_vacances)
            self.check_periodes.SetValue(True)
        self.OnCheckPeriodes(None)

    def GetPeriodes(self):
        if self.check_periodes.GetValue() == True :
            jours_scolaires = self.ctrl_periodes.GetJours("scolaire")
            jours_vacances = self.ctrl_periodes.GetJours("vacances")
        else:
            jours_scolaires = None
            jours_vacances = None
        return jours_scolaires, jours_vacances

    def Validation(self):
        # Vérifie les périodes
        if self.check_periodes.GetValue() == True :
            jours_scolaires, jours_vacances = self.GetPeriodes()
            if jours_scolaires == None and jours_vacances == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucun jour !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True


class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.listePages = [] 

        # Validité
        self.notebook = FNB.FlatNotebook(self, -1, agwStyle= FNB.FNB_NO_TAB_FOCUS | FNB.FNB_NO_X_BUTTON)

        if self.GetParent().GetName() == "notebook" :
            couleur = self.GetParent().GetThemeBackgroundColour()
            self.SetBackgroundColour(couleur)
            self.notebook.SetBackgroundColour(couleur)
            self.notebook.SetTabAreaColour(couleur)

        # Binds
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.notebook, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        
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
            {"index" : 0, "code" : "groupes", "ctrl" : Page_Groupes(self, self.IDactivite, self.IDtarif), "label" : _(u"Groupes")},
            {"index" : 1, "code" : "etiquettes", "ctrl" : Page_Etiquettes(self, self.IDactivite, self.IDtarif), "label" : _(u"Etiquettes")},
            {"index" : 2, "code" : "cotisations", "ctrl" : Page_Cotisations(self, self.IDactivite, self.IDtarif), "label" : _(u"Cotisations")},
            {"index" : 3, "code" : "questionnaires", "ctrl" : Page_Questionnaires(self, self.IDactivite, self.IDtarif), "label" : _(u"Questionnaires")},
            {"index" : 4, "code" : "caisses", "ctrl" : Page_Caisses(self,), "label" : _(u"Caisses")},
            {"index" : 5, "code" : "periodes", "ctrl" : Page_Periodes(self,), "label" : _(u"Périodes")},
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

    def Sauvegarde(self):
        pass

    def SetGroupes(self, groupes):
        self.dictPages["groupes"].SetGroupes(groupes)

    def GetGroupes(self):
        return self.dictPages["groupes"].GetGroupes()

    def SetEtiquettes(self, etiquettes):
        self.dictPages["etiquettes"].SetEtiquettes(etiquettes)

    def GetEtiquettes(self):
        return self.dictPages["etiquettes"].GetEtiquettes()

    def SetCotisations(self, cotisations):
        self.dictPages["cotisations"].SetCotisations(cotisations)

    def GetCotisations(self):
        return self.dictPages["cotisations"].GetCotisations()

    def SetFiltres(self, listeFiltres):
        self.dictPages["questionnaires"].SetFiltres(listeFiltres)

    def GetFiltres(self):
        return self.dictPages["questionnaires"].GetFiltres()
    
    def GetListeInitialeFiltres(self):
        return self.dictPages["questionnaires"].GetListeInitialeFiltres()

    def SetCaisses(self, caisses):
        self.dictPages["caisses"].SetCaisses(caisses)

    def GetCaisses(self):
        return self.dictPages["caisses"].GetCaisses()

    def SetPeriodes(self, jours_scolaires, jours_vacances):
        self.dictPages["periodes"].SetPeriodes(jours_scolaires, jours_vacances)

    def GetPeriodes(self):
        return self.dictPages["periodes"].GetPeriodes()


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=1, IDtarif=1)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()