#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED
import datetime

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Calendrier
from Ctrl import CTRL_Saisie_transport
from Ctrl import CTRL_Saisie_date
import GestionDB


def MelangeDictionnaires(d1={}, d2={}):
    for key, value in d2.items() :
        d1[key] = value
    return d1
    
    
def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class CTRL_Choix_unites(HTL.HyperTreeList):
    def __init__(self, parent, IDindividu=None): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.IDindividu = IDindividu
        self.MAJenCours = False
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.EnableSelectionVista(True)
        
        self.SetToolTip(wx.ToolTip(_(u"Cochez les unités conditionnelles")))
        
        # Création des colonnes
        self.AddColumn(_(u"Unités"))
        self.SetColumnWidth(0, 220)

        # Binds
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
        
        self.MAJ()

    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            # Active ou non les branches enfants
            if self.GetPyData(item)["type"] == "activite" :
                if self.IsItemChecked(item) :
                    self.EnableChildren(item, True)
                    self.CheckChilds(item)
                else:
                    self.CheckChilds(item, False)
                    self.EnableChildren(item, False)
                            
    def GetCoches(self):
        dictCoches = {}
        parent = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            parent = self.GetNext(parent) 
            # Recherche des activités cochées
            if self.IsItemChecked(parent) :
                IDactivite = self.GetPyData(parent)["ID"]
                # Recherche des unités cochées
                listeUnites = []
                item, cookie = self.GetFirstChild(parent)
                for index in range(0, self.GetChildrenCount(parent)):
                    if self.IsItemChecked(item) : 
                        IDunite = self.GetPyData(item)["ID"]
                        listeUnites.append(IDunite)
                    item = self.GetNext(item) 
                if len(listeUnites) > 0 : 
                    dictCoches[IDactivite] = listeUnites
        return dictCoches
    
    def GetUnites(self) :
        dictCoches = self.GetCoches() 
        listeUnites = []
        for IDactivite, listeUnitesTemp in dictCoches.items() :
            for IDunite in listeUnitesTemp :
                listeUnites.append(IDunite)
        return listeUnites
    
    def SetUnites(self, texteUnites=""):
        listeCoches = []
        listeTemp = texteUnites.split(";")
        for IDunite in listeTemp :
            listeCoches.append(int(IDunite))
        self.MAJ(listeCoches)
    
    def GetTexteUnites(self):
        """ Retourne une chaine texte des ID cochés """
        listeUnites = self.GetUnites() 
        listeTemp = []
        for IDunite in listeUnites :
            listeTemp.append(str(IDunite))
        texte = ";".join(listeTemp)
        return texte
    
    def MAJ(self, listeCoches=[]):
        """ Met à jour (redessine) tout le contrôle """
        self.dictUnites = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage(listeCoches)
        self.MAJenCours = False

    def Remplissage(self, listeCoches=[]):
        # Tri des activités par date de fin de validité
        listeActivites = []
        for IDactivite, dictActivite in self.dictUnites.items() :
            listeActivites.append((dictActivite["date_fin"], IDactivite))
        listeActivites.sort(reverse=True) 
        
        # Remplissage
        for date_fin, IDactivite in listeActivites :
            
            # Niveau Activité
            label = self.dictUnites[IDactivite]["nom"]
            niveauActivite = self.AppendItem(self.root, label, ct_type=1)
            self.SetPyData(niveauActivite, {"type" : "activite", "ID" : IDactivite, "label" : label})
            self.SetItemBold(niveauActivite, True)
            
            # Niveau Unité
            for ordre, IDunite, nomUnite in self.dictUnites[IDactivite]["unites"] :
                label = nomUnite
                niveauUnite = self.AppendItem(niveauActivite, label, ct_type=1)
                self.SetPyData(niveauUnite, {"type" : "depot", "ID" : IDunite, "label" : label})
                if IDunite in listeCoches :
                    self.CheckItem(niveauUnite)
                    self.CheckItem(niveauActivite)
            
            # Coche toutes les branches enfants
            if self.IsItemChecked(niveauActivite) == False : 
                self.EnableChildren(niveauActivite, False)
            self.Expand(niveauActivite)

    def Importation(self):
        dictUnites = {}
        DB = GestionDB.DB()
        req = """SELECT IDunite, unites.nom, ordre, unites.IDactivite, activites.nom, activites.date_debut, activites.date_fin
        FROM unites
        LEFT JOIN activites ON activites.IDactivite = unites.IDactivite
        LEFT JOIN inscriptions ON inscriptions.IDactivite = activites.IDactivite
        WHERE inscriptions.statut='ok' AND IDindividu=%d
        ORDER BY unites.IDactivite, ordre;""" % self.IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDunite, nomUnite, ordre, IDactivite, nomActivite, date_debut, date_fin in listeDonnees :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            
            if (IDactivite in dictUnites) == False :
                dictUnites[IDactivite] = {"nom" : nomActivite, "date_debut" : date_debut, "date_fin" : date_fin, "unites" : []}
            dictUnites[IDactivite]["unites"].append((ordre, IDunite, nomUnite))
                
        return dictUnites




class CTRL_Saisie_prog(wx.Panel):
    def __init__(self, parent, IDtransport=None, IDindividu=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDtransport = IDtransport
        self.IDindividu = IDindividu
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        # Validité
        self.box_validite_staticbox = wx.StaticBox(self, -1, _(u"Validité"))
        self.label_date_debut = wx.StaticText(self, -1,u"Du :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1,_(u"Au :"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.label_actif = wx.StaticText(self, -1,_(u"Actif :"))
        self.ctrl_actif = wx.CheckBox(self, -1, u"") 
        self.ctrl_actif.SetValue(True) 
        
        # Conditions
        self.box_conditions_staticbox = wx.StaticBox(self, -1, _(u"Conditions"))

        # Périodes scolaires
        self.label_periodes_scolaires = wx.StaticText(self, -1,_(u"Périodes scolaires :"))
        self.check_scolaire_lundi = wx.CheckBox(self, -1,u"L")
        self.check_scolaire_mardi = wx.CheckBox(self, -1,u"M")
        self.check_scolaire_mercredi = wx.CheckBox(self, -1,u"M")
        self.check_scolaire_jeudi = wx.CheckBox(self, -1,u"J")
        self.check_scolaire_vendredi = wx.CheckBox(self, -1,u"V")
        self.check_scolaire_samedi = wx.CheckBox(self, -1,u"S")
        self.check_scolaire_dimanche = wx.CheckBox(self, -1,u"D")
        self.CheckJours("scolaire")
        
        # Périodes de vacances
        self.label_periodes_vacances = wx.StaticText(self, -1,_(u"Périodes de vacances :"))
        self.check_vacances_lundi = wx.CheckBox(self, -1,u"L")
        self.check_vacances_mardi = wx.CheckBox(self, -1,u"M")
        self.check_vacances_mercredi = wx.CheckBox(self, -1,u"M")
        self.check_vacances_jeudi = wx.CheckBox(self, -1,u"J")
        self.check_vacances_vendredi = wx.CheckBox(self, -1,u"V")
        self.check_vacances_samedi = wx.CheckBox(self, -1,u"S")
        self.check_vacances_dimanche = wx.CheckBox(self, -1,u"D")
        self.CheckJours("vacances")
        
        # Unités
        self.label_unites = wx.StaticText(self, -1,_(u"Unités de consommation :"))
        self.ctrl_unites = CTRL_Choix_unites(self, IDindividu=self.IDindividu)
        
        self.__set_properties()
        self.__do_layout()
        
        # Importation
        if self.IDtransport != None :
            self.Importation() 

    def __set_properties(self):
        self.check_scolaire_lundi.SetToolTip(wx.ToolTip(_(u"Lundi")))
        self.check_scolaire_mardi.SetToolTip(wx.ToolTip(_(u"Mardi")))
        self.check_scolaire_mercredi.SetToolTip(wx.ToolTip(_(u"Mercredi")))
        self.check_scolaire_jeudi.SetToolTip(wx.ToolTip(_(u"Jeudi")))
        self.check_scolaire_vendredi.SetToolTip(wx.ToolTip(_(u"Vendredi")))
        self.check_scolaire_samedi.SetToolTip(wx.ToolTip(_(u"Samedi")))
        self.check_scolaire_dimanche.SetToolTip(wx.ToolTip(_(u"Dimanche")))
        self.check_vacances_lundi.SetToolTip(wx.ToolTip(_(u"Lundi")))
        self.check_vacances_mardi.SetToolTip(wx.ToolTip(_(u"Mardi")))
        self.check_vacances_mercredi.SetToolTip(wx.ToolTip(_(u"Mercredi")))
        self.check_vacances_jeudi.SetToolTip(wx.ToolTip(_(u"Jeudi")))
        self.check_vacances_vendredi.SetToolTip(wx.ToolTip(_(u"Vendredi")))
        self.check_vacances_samedi.SetToolTip(wx.ToolTip(_(u"Samedi")))
        self.check_vacances_dimanche.SetToolTip(wx.ToolTip(_(u"Dimanche")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Validité
        box_validite = wx.StaticBoxSizer(self.box_validite_staticbox, wx.VERTICAL)
        grid_sizer_validite = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_validite.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_validite.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_validite.Add(self.label_actif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_actif, 0, 0, 0)
        box_validite.Add(grid_sizer_validite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_validite, 1, wx.EXPAND, 0)
        
        # Conditions
        box_conditions = wx.StaticBoxSizer(self.box_conditions_staticbox, wx.VERTICAL)
        grid_sizer_conditions = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        # Périodes scolaires
        grid_sizer_conditions.Add(self.label_periodes_scolaires, 0, 0, 0)

        grid_sizer_scolaire = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_scolaire.Add(self.check_scolaire_lundi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_mardi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_mercredi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_jeudi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_vendredi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_samedi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_dimanche, 0, 0, 0)
        grid_sizer_conditions.Add(grid_sizer_scolaire, 1, wx.EXPAND, 0)
        
        # Périodes de vacances
        grid_sizer_conditions.Add(self.label_periodes_vacances, 0, wx.TOP, 10)
        
        grid_sizer_vacances = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_vacances.Add(self.check_vacances_lundi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_mardi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_mercredi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_jeudi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_vendredi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_samedi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_dimanche, 0, 0, 0)
        grid_sizer_conditions.Add(grid_sizer_vacances, 1, wx.EXPAND, 0)
        
        # Unités
        grid_sizer_conditions.Add(self.label_unites, 0, wx.TOP, 10)
        grid_sizer_conditions.Add(self.ctrl_unites, 1, wx.EXPAND, 0)

        grid_sizer_conditions.AddGrowableCol(0)
        grid_sizer_conditions.AddGrowableRow(5)
        
        box_conditions.Add(grid_sizer_conditions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_conditions, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def CheckJours(self, periode="scolaire"):
        for jour in self.liste_jours[:5] :
            getattr(self, "check_%s_%s" % (periode, jour)).SetValue(True)

    def GetJours(self, periode="scolaire"):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            etat = getattr(self, "check_%s_%s" % (periode, jour)).GetValue()
            if etat == True :
                listeTemp.append(str(index))
            index += 1
        texte = ";".join(listeTemp)
        return texte
    
    def SetJours(self, periode="scolaire", texteJours=""):
        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            if jour != "" :
                listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = True
            else :
                etat = False
            getattr(self, "check_%s_%s" % (periode, jour)).SetValue(etat)
            index += 1

    def GetData(self):
        dictData = {}
        # Période
        dictData["date_debut"] = self.ctrl_date_debut.GetDate()
        dictData["date_fin"] = self.ctrl_date_fin.GetDate()
        # Actif
        dictData["actif"] = int(self.ctrl_actif.GetValue())
        # Périodes scolaires
        dictData["jours_scolaires"] = self.GetJours("scolaire")
        # Périodes vacances
        dictData["jours_vacances"] = self.GetJours("vacances")
        # Unités
        dictData["unites"] = self.ctrl_unites.GetTexteUnites()
        return dictData
    
    def Validation(self):
        dictData = self.GetData() 
        if dictData["date_debut"] == None or self.ctrl_date_debut.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_debut.SetFocus()
                return False
        date_fin = self.ctrl_date_fin.GetDate()
        if dictData["date_fin"] == None or self.ctrl_date_fin.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
        if len(dictData["jours_scolaires"]) == 0 and len(dictData["jours_vacances"]) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un jour de la semaine !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        if len(dictData["unites"]) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une unité de consommation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

    def Importation(self):
        """ Importation des données """
        # Importation
        DB = GestionDB.DB()
        req = """SELECT date_debut, date_fin, actif, jours_scolaires, jours_vacances, unites
        FROM transports 
        WHERE IDtransport=%d;""" % self.IDtransport
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        DB.Close()
        if len(listeValeurs) == 0 : return
        date_debut, date_fin, actif, jours_scolaires, jours_vacances, unites = listeValeurs[0]

        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        self.ctrl_actif.SetValue(actif) 
        self.SetJours("scolaire", jours_scolaires)
        self.SetJours("vacances", jours_vacances)
        self.ctrl_unites.SetUnites(unites)
        

# -----------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Planning(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        # Période
        self.label_date_debut = wx.StaticText(self, -1,u"Du :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1,_(u"Au :"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Périodes scolaires
        self.label_periodes_scolaires = wx.StaticText(self, -1,_(u"Périodes scolaires :"))
        self.check_scolaire_lundi = wx.CheckBox(self, -1,u"L")
        self.check_scolaire_mardi = wx.CheckBox(self, -1,u"M")
        self.check_scolaire_mercredi = wx.CheckBox(self, -1,u"M")
        self.check_scolaire_jeudi = wx.CheckBox(self, -1,u"J")
        self.check_scolaire_vendredi = wx.CheckBox(self, -1,u"V")
        self.check_scolaire_samedi = wx.CheckBox(self, -1,u"S")
        self.check_scolaire_dimanche = wx.CheckBox(self, -1,u"D")
        self.CheckJours("scolaire")
        
        # Périodes de vacances
        self.label_periodes_vacances = wx.StaticText(self, -1,_(u"Périodes de vacances :"))
        self.check_vacances_lundi = wx.CheckBox(self, -1,u"L")
        self.check_vacances_mardi = wx.CheckBox(self, -1,u"M")
        self.check_vacances_mercredi = wx.CheckBox(self, -1,u"M")
        self.check_vacances_jeudi = wx.CheckBox(self, -1,u"J")
        self.check_vacances_vendredi = wx.CheckBox(self, -1,u"V")
        self.check_vacances_samedi = wx.CheckBox(self, -1,u"S")
        self.check_vacances_dimanche = wx.CheckBox(self, -1,u"D")
        self.CheckJours("vacances")
        
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.check_scolaire_lundi.SetToolTip(wx.ToolTip(_(u"Lundi")))
        self.check_scolaire_mardi.SetToolTip(wx.ToolTip(_(u"Mardi")))
        self.check_scolaire_mercredi.SetToolTip(wx.ToolTip(_(u"Mercredi")))
        self.check_scolaire_jeudi.SetToolTip(wx.ToolTip(_(u"Jeudi")))
        self.check_scolaire_vendredi.SetToolTip(wx.ToolTip(_(u"Vendredi")))
        self.check_scolaire_samedi.SetToolTip(wx.ToolTip(_(u"Samedi")))
        self.check_scolaire_dimanche.SetToolTip(wx.ToolTip(_(u"Dimanche")))
        self.check_vacances_lundi.SetToolTip(wx.ToolTip(_(u"Lundi")))
        self.check_vacances_mardi.SetToolTip(wx.ToolTip(_(u"Mardi")))
        self.check_vacances_mercredi.SetToolTip(wx.ToolTip(_(u"Mercredi")))
        self.check_vacances_jeudi.SetToolTip(wx.ToolTip(_(u"Jeudi")))
        self.check_vacances_vendredi.SetToolTip(wx.ToolTip(_(u"Vendredi")))
        self.check_vacances_samedi.SetToolTip(wx.ToolTip(_(u"Samedi")))
        self.check_vacances_dimanche.SetToolTip(wx.ToolTip(_(u"Dimanche")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=8, hgap=8)
        grid_sizer_base.Add( (5, 5), 1, wx.EXPAND, 0)
        
        # Période
        grid_sizer_date_debut = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_date_debut.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_debut.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_date_debut, 1, wx.EXPAND, 0)

        grid_sizer_date_fin = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_date_fin.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_fin.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_date_fin, 1, wx.EXPAND, 0)
        
        # Périodes scolaires
        grid_sizer_base.Add(self.label_periodes_scolaires, 0, wx.TOP, 10)

        grid_sizer_scolaire = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_scolaire.Add(self.check_scolaire_lundi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_mardi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_mercredi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_jeudi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_vendredi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_samedi, 0, 0, 0)
        grid_sizer_scolaire.Add(self.check_scolaire_dimanche, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_scolaire, 1, wx.EXPAND, 0)
        
        # Périodes de vacances
        grid_sizer_base.Add(self.label_periodes_vacances, 0, wx.TOP, 10)
        
        grid_sizer_vacances = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_vacances.Add(self.check_vacances_lundi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_mardi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_mercredi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_jeudi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_vendredi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_samedi, 0, 0, 0)
        grid_sizer_vacances.Add(self.check_vacances_dimanche, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_vacances, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
    
    def CheckJours(self, periode="scolaire"):
        for jour in self.liste_jours[:5] :
            getattr(self, "check_%s_%s" % (periode, jour)).SetValue(True)
        
    def GetJours(self, periode="scolaire"):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            etat = getattr(self, "check_%s_%s" % (periode, jour)).GetValue()
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp
        
    def GetData(self):
        dictData = {}
        # Période
        dictData["date_debut"] = self.ctrl_date_debut.GetDate()
        dictData["date_fin"] = self.ctrl_date_fin.GetDate()
        # Périodes scolaires
        dictData["jours_scolaires"] = self.GetJours("scolaire")
        # Périodes vacances
        dictData["jours_vacances"] = self.GetJours("vacances")
        return dictData
        
    def Validation(self):
        dictData = self.GetData() 
        if dictData["date_debut"] == None or self.ctrl_date_debut.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_debut.SetFocus()
                return False
        date_fin = self.ctrl_date_fin.GetDate()
        if dictData["date_fin"] == None or self.ctrl_date_fin.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
        if len(dictData["jours_scolaires"]) == 0 and len(dictData["jours_vacances"]) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un jour de la semaine !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True
    

class CTRL_Mode_multiple(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent, id=-1)
        self.parent = parent
        #self.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une localisation")))
        
        self.listePanels = [
            ("CALENDRIER", _(u"Selon les dates sélectionnées"), CTRL_Calendrier.CTRL(self, afficheBoutonAnnuel=False) ),
            ("PLANNING", _(u"Selon le planning suivant"), CTRL_Planning(self) ),
            ]
        
        for code, label, ctrl in self.listePanels :
            self.AddPage(ctrl, label)
            
        # Sélection par défaut
        self.SetSelection(0)
    
    def GetData(self):
        dictData = {}
        if self.GetSelection() == 0 :
            # Mode Calendrier
            dictData["mode"] = "CALENDRIER"
            ctrl = self.listePanels[self.GetSelection()][2]
            listeDates = ctrl.GetSelections()
            dictData["dates"] = listeDates
        else :
            # Mode Planning
            dictData["mode"] = "PLANNING"
            ctrl = self.listePanels[self.GetSelection()][2]
            dictData = MelangeDictionnaires(dictData, ctrl.GetData())
        return dictData
    
    def Validation(self):
        dictData = self.GetData() 
        if dictData["mode"] == "CALENDRIER" :
            if dictData["dates"] == None or len(dictData["dates"]) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune date dans le calendrier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        if dictData["mode"] == "PLANNING" :
            ctrl = self.listePanels[self.GetSelection()][2]
            if ctrl.Validation() == False :
                return False
        return True
    
#------------------------------------------------------------------------------------------------------


class CTRL_Choix_activite(wx.Choice):
    def __init__(self, parent, IDindividu=None):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.IDindividu = IDindividu
        self.MAJ() 
        self.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une activité")))
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
            self.Select(0)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT activites.IDactivite, activites.nom
        FROM activites
        LEFT JOIN inscriptions ON inscriptions.IDactivite = activites.IDactivite
        WHERE inscriptions.statut='ok' AND IDindividu=%d
        ORDER BY activites.date_fin DESC;""" % self.IDindividu
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDactivite, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDactivite, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


class CTRL_Saisie_multiple(wx.Panel):
    def __init__(self, parent, IDindividu=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        
        # Mode
        self.box_mode_staticbox = wx.StaticBox(self, -1, _(u"Mode de saisie"))
        self.radio_unique = wx.RadioButton(self, -1, _(u"Saisie unique"), style=wx.RB_GROUP)
        self.radio_multiple = wx.RadioButton(self, -1, _(u"Saisie multiple"))
        
        # Saisie multiple
        self.box_multiple_staticbox = wx.StaticBox(self, -1, _(u"Saisie multiple"))
        self.ctrl_multiple = CTRL_Mode_multiple(self)
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.check_feries = wx.CheckBox(self, -1, _(u"Inclure les jours fériés"))
        self.check_activite = wx.CheckBox(self, -1, _(u"Uniquement si individu inscrit sur l'activité :"))
        self.ctrl_activite = CTRL_Choix_activite(self, IDindividu=self.IDindividu)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMode, self.radio_unique)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMode, self.radio_multiple)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckActivite, self.check_activite)
        
        # Init contrôles
        self.OnChoixMode(None)

    def __set_properties(self):
        self.radio_unique.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour saisir un seul transport")))
        self.radio_multiple.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour saisir plusieurs transports à la fois")))
        self.check_feries.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour saisir également des transports sur les jours fériés")))
        self.check_activite.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour saisir ce transport uniquement les jours sur lesquels l'individu est inscrit sur une activité donnée")))
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Sélectionnez une activité")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Mode de saisie
        box_mode = wx.StaticBoxSizer(self.box_mode_staticbox, wx.VERTICAL)
        grid_sizer_mode = wx.FlexGridSizer(rows=2, cols=2, vgap=20, hgap=20)
        grid_sizer_mode.Add(self.radio_unique, 0, 0, 0)
        grid_sizer_mode.Add(self.radio_multiple, 0, 0, 0)
        box_mode.Add(grid_sizer_mode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_mode, 1, wx.EXPAND, 0)
        
        # Saisie multiple
        box_multiple = wx.StaticBoxSizer(self.box_multiple_staticbox, wx.VERTICAL)
        box_multiple.Add(self.ctrl_multiple, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_multiple, 1, wx.EXPAND, 0)
        
        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_options.Add(self.check_feries, 0, 0, 0)
        grid_sizer_options.Add(self.check_activite, 0, 0, 0)
        grid_sizer_options.Add(self.ctrl_activite, 0, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_options.AddGrowableCol(0)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_options, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def OnChoixMode(self, event): 
        etat =  self.radio_multiple.GetValue()
        self.ctrl_multiple.Enable(etat) 
        self.check_feries.Enable(etat) 
        self.check_activite.Enable(etat) 
        self.OnCheckActivite(None) 
        # Affiche ou non les dates de saisie 
        self.parent.AffichageDates(not etat)
    
    def OnCheckActivite(self, event): 
        if self.radio_multiple.GetValue() == True and self.check_activite.GetValue() == True :
            self.ctrl_activite.Enable(True)
        else :
            self.ctrl_activite.Enable(False)
    
    def GetData(self):
        dictData = None
        if self.radio_multiple.GetValue() == True :
            dictData = {}
            
            # Récupération paramètres multiples
            dictData = self.ctrl_multiple.GetData()
            
            # Récupération paramètres Options
            dictData["feries"] = self.check_feries.GetValue()
            dictData["activite"] = None
            if self.check_activite.GetValue() == True :
                dictData["activite"] = self.ctrl_activite.GetID() 
        
        return dictData
            
    
    def Validation(self):
        if self.radio_multiple.GetValue() == True :
            # Validation Paramètres multiples
            if self.ctrl_multiple.Validation() == False :
                return False
            # Validation Options
            if self.check_activite.GetValue() == True and self.ctrl_activite.GetID() == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_activite.SetFocus() 
                return False
        return True
        




class Dialog_prog(wx.Dialog):
    def __init__(self, parent, IDtransport=None, IDindividu=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.IDtransport = IDtransport
        self.IDindividu = IDindividu

        # Bandeau
        titre = _(u"Programmation d'un transport")
        intro = _(u"Vous pouvez ici programmer un transport. Celui-ci sera ainsi créé automatiquement par Noethys à chaque fois qu'une consommation sera saisie pour cet individu en fonction des paramètres que vous aurez précisé ci-dessous.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Transport.png")
        
        # Contenu
        self.ctrl_saisie = CTRL_Saisie_transport.CTRL(self, IDtransport=IDtransport, IDindividu=IDindividu)
        self.ctrl_saisie_prog = CTRL_Saisie_prog(self, IDtransport=IDtransport, IDindividu=IDindividu)
        
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        # Init contrôles
        self.AffichageDates(False)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((800, 660))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=20, hgap=20)
        grid_sizer_contenu.Add(self.ctrl_saisie_prog, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_saisie, 1, wx.EXPAND|wx.TOP, 10)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Transports1")

    def OnBoutonOk(self, event):
        # Validation des données
        if self.Validation() == False : 
            return False
        
        # Sauvegardes des données
        parametres = self.GetData() 
        
        # Sauvegarde
        resultat = self.ctrl_saisie.Sauvegarde(mode="prog", parametres=parametres)
        if resultat == True :
            self.EndModal(wx.ID_OK)
    
    def GetListeDictDonnees(self):
        listedictDonnees = self.ctrl_saisie.listeDonneesSauvegardees
        return listedictDonnees
    
    def GetData(self):
        dictData = {}
        dictData = self.ctrl_saisie_prog.GetData() 
        return dictData
    
    def Validation(self):
        if self.ctrl_saisie_prog.Validation() == False : 
            return False
        if self.ctrl_saisie.Validation() == False : 
            return False
        return True

    def AffichageDates(self, etat=True):
        self.ctrl_saisie.AffichageDates(etat)




class Dialog_multiple(wx.Dialog):
    def __init__(self, parent, IDindividu=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.IDindividu = IDindividu

        # Bandeau
        titre = _(u"Saisie d'un ou plusieurs transports")
        intro = _(u"Vous pouvez ici sélectionner toutes les caractéristiques du ou des transports à créer. Pour saisir un lot de transports identiques sur un ensemble de dates, sélectionnez le mode Saisie multiple.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Transport.png")
        
        # Contenu
        self.ctrl_saisie = CTRL_Saisie_transport.CTRL(self, IDtransport=None, IDindividu=IDindividu)
        self.ctrl_saisie_multiple = CTRL_Saisie_multiple(self, IDindividu=IDindividu)
        
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((800, 660))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=20, hgap=20)
        grid_sizer_contenu.Add(self.ctrl_saisie_multiple, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_saisie, 1, wx.EXPAND|wx.TOP, 10)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Transports1")

    def OnBoutonOk(self, event):
        # Validation des données
        if self.Validation() == False : 
            return False
        
        # Sauvegardes des données
        parametres = self.GetData() 
        if parametres == None :
            mode = "unique"
        else :
            mode = "multiple"
            
        # Sauvegarde
        resultat = self.ctrl_saisie.Sauvegarde(mode=mode, parametres=parametres)
        if resultat == True :
            self.EndModal(wx.ID_OK)
    
    def GetListeDictDonnees(self):
        listedictDonnees = self.ctrl_saisie.listeDonneesSauvegardees
        return listedictDonnees
    
    def GetData(self):
        dictData = {}
        dictData = self.ctrl_saisie_multiple.GetData() 
        return dictData
    
    def Validation(self):
        if self.ctrl_saisie_multiple.Validation() == False : 
            return False
        if self.ctrl_saisie.Validation() == False : 
            return False
        return True

    def AffichageDates(self, etat=True):
        self.ctrl_saisie.AffichageDates(etat)



class Dialog(wx.Dialog):
    def __init__(self, parent, IDtransport=None, IDindividu=None, modeVirtuel=False, dictDonnees={}, verrouilleBoutons=False):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.IDindividu = IDindividu
        self.IDtransport = IDtransport
        self.modeVirtuel = modeVirtuel
        self.dictDonnees = dictDonnees # Pour le mode virtuel
        
        # Bandeau
        if IDtransport == None :
            titre = _(u"Saisie d'un transport")
        else:
            titre = _(u"Modification d'un transport")
        intro = _(u"Vous pouvez ici sélectionner toutes les caractéristiques du transport.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Transport.png")
        
        # Contenu
        self.ctrl_saisie = CTRL_Saisie_transport.CTRL(self, IDtransport=IDtransport, IDindividu=IDindividu, dictDonnees=self.dictDonnees, verrouilleBoutons=verrouilleBoutons)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((450, 660))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_saisie, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Transports1")

    def OnBoutonOk(self, event):
        # Validation des données
        if self.Validation() == False : 
            return False

        # Fermeture sans sauvegarde
        if self.modeVirtuel == True :
            self.EndModal(wx.ID_OK)
            return
        
        # Sauvegarde
        resultat = self.ctrl_saisie.Sauvegarde(mode="unique", )
        if resultat == True :
            self.EndModal(wx.ID_OK)
    
    def GetDictDonnees(self):
        dictDonnees = self.ctrl_saisie.GetDictDonnees() 
        dictDonnees["IDtransport"] = self.GetIDtransport() 
        return dictDonnees
    
    def GetIDtransport(self):
        return self.ctrl_saisie.GetIDtransport()
    
    def SetDateHeure(self, datedt=None):
        # Règle la date et l'heure de départ
        ctrl_date_heure = self.ctrl_saisie.GetControle("date_heure", "depart")
        ctrl_date_heure.SetDateTime(datedt)
        # Règle la date et l'heure d'arrivée
        ctrl_date_heure = self.ctrl_saisie.GetControle("date_heure", "arrivee")
        ctrl_date_heure.SetDateTime(datedt)
    
    def SetDateObligatoire(self, date=None):
        ctrl_date_heure = self.ctrl_saisie.GetControle("date_heure", "depart")
        ctrl_date_heure.SetDate(date)
        ctrl_date_heure.ctrl_date.Enable(False)
        ctrl_date_heure = self.ctrl_saisie.GetControle("date_heure", "arrivee")
        ctrl_date_heure.SetDate(date)
        ctrl_date_heure.ctrl_date.Enable(False)
    
    def VerrouilleBoutonsGestion(self):
        """ Verrouille l'accès aux boutons de gestion """
        self.ctrl_saisie.VerrouilleBoutonsGestion()
        
    def Validation(self):
        # Validation de la saisie
        resultat = self.ctrl_saisie.Validation() 
        return resultat
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog_prog(None, IDtransport=1, IDindividu=46) # Pour une saisie multiple
    # dialog_1 = Dialog_multiple(None, IDindividu=46) # Pour une saisie multiple
    # dialog_1 = Dialog(None, IDtransport=None, IDindividu=46) # Pour une saisie unique
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
