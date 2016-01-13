#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import wx.calendar

import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED
import wx.lib.colourselect as csel

import FonctionsPerso
import sys
import operator
import os

import CTRL_Calendrier
import CTRL_Photo
import CTRL_Bandeau
import CTRL_Unites_impression_conso

import GestionDB
import UTILS_Config
import UTILS_Organisateur
import UTILS_Cotisations_manquantes
import UTILS_Pieces_manquantes
import DATA_Civilites as Civilites
import CTRL_Etiquettes
import UTILS_Texte

from DLG_Saisie_pb_sante import LISTE_TYPES

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import ParagraphAndImage, Image
from reportlab.rl_config import defaultPageSize
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


COULEUR_FOND_TITRE = (204, 204, 255) # version PDF : (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)

DICT_TYPES_INFOS = {}
for IDtype, nom, img in LISTE_TYPES :
    DICT_TYPES_INFOS[IDtype] = { "nom" : nom, "img" : img }



DICT_CIVILITES = Civilites.GetDictCivilites()


def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def ConvertCouleurWXpourPDF(couleurwx=(0, 0, 0)):
    return (couleurwx[0]/255.0, couleurwx[1]/255.0, couleurwx[2]/255.0)

def ConvertCouleurPDFpourWX(couleurpdf=(0, 0, 0)):
    return (couleurpdf[0]*255.0, couleurpdf[1]*255.0, couleurpdf[2]*255.0)



class PANEL_Calendrier(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        self.ctrl_calendrier = CTRL_Calendrier.CTRL(self, afficheBoutonAnnuel=False, multiSelections=False)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_calendrier, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

        self.ctrl_calendrier.Bind(CTRL_Calendrier.EVT_SELECT_DATES, self.OnDateSelected)
        
    def OnDateSelected(self, event):
        self.GetParent().SetDates(self.GetDates())
    
    def GetDates(self):
        selections = self.ctrl_calendrier.GetSelections() 
        if len(selections) > 0 :
            return selections
        else:
            return None
    
    def SetDates(self, listeDates=[]):
        self.ctrl_calendrier.SelectJours(listeDates)

    def SetMultiSelection(self, etat=False):
        self.ctrl_calendrier.SetMultiSelection(etat)


#------------------------------------------------------------------------------------------------------------------------------------



class CTRL_Activites(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.listeDates = []
        self.dictActivites = {}
        self.dictGroupes = {}
        self.MAJenCours = False
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.EnableSelectionVista(True)
        
        self.SetToolTipString(_(u"Cochez les activités et groupes à afficher"))
        
        # Création des colonnes
        self.AddColumn(_(u"Activité/groupe"))
        self.SetColumnWidth(0, 220)

        # Binds
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
        

    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            # Active ou non les branches enfants
            if self.GetPyData(item)["type"] == "activite" :
                if self.IsItemChecked(item) :
                    self.EnableChildren(item, True)
                else:
                    self.EnableChildren(item, False)
            # Envoie les données aux contrôle parent
            listeActivites = self.GetListeActivites()
            self.GetGrandParent().GetParent().SetUnites(listeActivites)

    def SetDates(self, listeDates=[]):
        self.listeDates = listeDates
        self.MAJ() 

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.dictActivites, self.dictGroupes = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Importation(self):
        dictActivites = {}
        dictGroupes = {}
        if len(self.listeDates) == 0 :
            return dictActivites, dictGroupes
        
        if len(self.listeDates) == 0 : conditionDates = "()"
        elif len(self.listeDates) == 1 : conditionDates = "('%s')" % self.listeDates[0]
        else : 
            listeTmp = []
            for dateTmp in self.listeDates :
                listeTmp.append(str(dateTmp))
            conditionDates = str(tuple(listeTmp))

        # Récupération des activités disponibles le jour sélectionné
        DB = GestionDB.DB()
        req = """SELECT 
        activites.IDactivite, activites.nom, activites.abrege, date_debut, date_fin,
        groupes.IDgroupe, groupes.nom, groupes.ordre
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = ouvertures.IDgroupe
        WHERE ouvertures.date IN %s
        GROUP BY groupes.IDgroupe
        ORDER BY groupes.ordre;""" % conditionDates
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDactivite, nom, abrege, date_debut, date_fin, IDgroupe, nomGroupe, ordreGroupe in listeDonnees :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            
            # Mémorisation de l'activité et du groupe
            if dictActivites.has_key(IDactivite) == False :
                dictActivites[IDactivite] = { "nom":nom, "abrege":abrege, "date_debut":date_debut, "date_fin":date_fin, "groupes":[]}
            
            if dictGroupes.has_key(IDgroupe) == False :
                dictGroupes[IDgroupe] = {"nom" : nomGroupe, "IDactivite" : IDactivite, "ordre":ordreGroupe}
                
            dictActivites[IDactivite]["groupes"].append({"IDgroupe":IDgroupe, "nom":nomGroupe, "ordre":ordreGroupe})
            
        return dictActivites, dictGroupes

    def Remplissage(self):
        # Tri des activités par nom
        listeActivites = []
        for IDactivite, dictActivite in self.dictActivites.iteritems() :
            listeActivites.append((dictActivite["nom"], IDactivite))
        listeActivites.sort() 
        
        # Remplissage
        for nomActivite, IDactivite in listeActivites :
            dictActivite = self.dictActivites[IDactivite]
            
            # Niveau Activité
            niveauActivite = self.AppendItem(self.root, nomActivite, ct_type=1)
            self.SetPyData(niveauActivite, {"type" : "activite", "ID" : IDactivite, "nom" : nomActivite})
            self.SetItemBold(niveauActivite, True)
            
            # Niveau Groupes
            for dictGroupe in dictActivite["groupes"] :
                niveauGroupe = self.AppendItem(niveauActivite, dictGroupe["nom"], ct_type=1)
                self.SetPyData(niveauGroupe, {"type" : "groupe", "ID" : dictGroupe["IDgroupe"], "nom" : dictGroupe["nom"]})
            
            # Coche toutes les branches enfants
            self.CheckItem(niveauActivite)
            self.CheckChilds(niveauActivite)
        
        self.ExpandAllChildren(self.root)
        
    def GetCoches(self, typeTemp="activite"):
        listeCoches = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            if self.IsItemChecked(item) and self.IsItemEnabled(item):
                ID = self.GetPyData(item)["ID"]
                if self.GetPyData(item)["type"] == typeTemp :
                    listeCoches.append(ID)
        return listeCoches
    
    def GetListeActivites(self):
        return self.GetCoches(typeTemp="activite")

    def GetListeGroupes(self):
        return self.GetCoches(typeTemp="groupe")
    
    def GetDictActivites(self):
        return self.dictActivites
    
    def GetDictGroupes(self):
        return self.dictGroupes

# ------------------------------------------------------------------------------------------------------------

class CTRL_Ecoles(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.activation = True
        self.data = []
        self.listeDates = []
        self.dictEcoles = {}
        self.dictClasses = {}
        self.MAJenCours = False
        self.dictNiveaux = self.ImportationNiveaux() 
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.EnableSelectionVista(True)
        
        self.SetToolTipString(_(u"Cochez les écoles et classes à afficher"))
        
        # Création des colonnes
        self.AddColumn(_(u"Ecole/classe"))
        self.SetColumnWidth(0, 420)

        # Binds
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
    
    def Activation(self, etat=True):
        """ Active ou désactive le contrôle """
        self.activation = etat
        self.MAJ() 
        
    def ImportationNiveaux(self):
        dictNiveaux = {}
        DB = GestionDB.DB()
        req = """SELECT IDniveau, ordre, nom, abrege
        FROM niveaux_scolaires
        ORDER BY ordre; """ 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDniveau, ordre, nom, abrege in listeDonnees :
            dictNiveaux[IDniveau] = {"nom" : nom, "abrege" : abrege, "ordre" : ordre}
        return dictNiveaux

    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            # Active ou non les branches enfants
            if self.GetPyData(item)["type"] == "ecole" :
                if self.IsItemChecked(item) :
                    self.EnableChildren(item, True)
                else:
                    self.EnableChildren(item, False)

    def SetDates(self, listeDates=[]):
        self.listeDates = listeDates
        self.MAJ() 

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.dictEcoles, self.dictClasses = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Importation(self):
        dictEcoles = {}
        dictClasses = {}
        if len(self.listeDates) == 0 :
            return dictEcoles, dictClasses
        
        if len(self.listeDates) == 0 : conditionDates = ""
        elif len(self.listeDates) == 1 : conditionDates = "WHERE classes.date_debut<='%s' AND classes.date_fin>='%s' " % (self.listeDates[0], self.listeDates[0])
        else : 
            listeTmp = []
            for dateTemp in self.listeDates :
                listeTmp.append("(classes.date_debut<='%s' AND classes.date_fin>='%s')" % (dateTemp, dateTemp))
            conditionDates = "WHERE %s" % " OR ".join(listeTmp)
        
        # Récupération des activités disponibles le jour sélectionné
        DB = GestionDB.DB()
        req = """SELECT 
        ecoles.IDecole, ecoles.nom, 
        classes.IDclasse, classes.nom, classes.date_debut, classes.date_fin, classes.niveaux
        FROM ecoles
        LEFT JOIN classes ON classes.IDecole = ecoles.IDecole
        %s
        GROUP BY classes.IDclasse
        ORDER BY classes.IDclasse;""" % conditionDates
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDecole, nomEcole, IDclasse, nomClasse, date_debut, date_fin, niveaux in listeDonnees :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)

            # Formatage des niveaux
            listeNiveaux = []
            listeOrdresNiveaux = []
            txtNiveaux = u""
            if niveaux != None and niveaux != "" and niveaux != " " :
                listeTemp = niveaux.split(";")
                txtTemp = []
                for niveau in listeTemp :
                    IDniveau = int(niveau)
                    if self.dictNiveaux.has_key(IDniveau) :
                        nomNiveau = self.dictNiveaux[IDniveau]["abrege"]
                        ordreNiveau = self.dictNiveaux[IDniveau]["ordre"]
                        listeNiveaux.append(IDniveau)
                        txtTemp.append(nomNiveau)
                        listeOrdresNiveaux.append(ordreNiveau)
                txtNiveaux = ", ".join(txtTemp)

            # Mémorisation de l'école
            if dictEcoles.has_key(IDecole) == False :
                dictEcoles[IDecole] = { "nom":nomEcole, "classes":[]}
            
            # Mémorisation dans le dictClasses
            if dictClasses.has_key(IDclasse) == False :
                dictClasses[IDclasse] = { "nom" : nomClasse, "IDecole":IDecole, "date_debut": date_debut, "date_fin" : date_fin, "txtNiveaux" : txtNiveaux}
            
            # Mémorisation de la classe dans le dictEcoles
            donnees = (listeOrdresNiveaux, nomClasse, txtNiveaux, IDclasse, date_debut, date_fin) 
            dictEcoles[IDecole]["classes"].append(donnees)
            
        return dictEcoles, dictClasses

    def Remplissage(self):
        # Tri des écoles par nom
        listeEcoles = []
        for IDecole, dictEcole in self.dictEcoles.iteritems() :
            listeEcoles.append((dictEcole["nom"], IDecole))
        listeEcoles.sort() 
        
        # Remplissage
        for nomEcole, IDecole in listeEcoles :
            dictEcole = self.dictEcoles[IDecole]
            
            # Niveau Ecole
            niveauEcole = self.AppendItem(self.root, nomEcole, ct_type=1)
            self.SetPyData(niveauEcole, {"type" : "ecole", "ID" : IDecole, "nom" : nomEcole})
            self.SetItemBold(niveauEcole, True)                
                
            # Niveau Classes
            listeClasses = dictEcole["classes"]
            listeClasses.sort() 
            for listeOrdresNiveaux, nomClasse, txtNiveaux, IDclasse, date_debut, date_fin in listeClasses :
                nomSaison = _(u"Du %s au %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)) )
                labelClasse = u"%s (%s)" % (nomClasse, nomSaison)
                niveauClasse = self.AppendItem(niveauEcole, labelClasse, ct_type=1)
                self.SetPyData(niveauClasse, {"type" : "classe", "ID" : IDclasse, "nom" : nomClasse})
            
            # Coche toutes les branches enfants
            self.CheckItem(niveauEcole)
            self.CheckChilds(niveauEcole)
        
        self.ExpandAllChildren(self.root)

        if self.activation == False :
            self.EnableChildren(self.root, False)
        
    def GetCoches(self, typeTemp="ecole"):
        listeCoches = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            if self.IsItemChecked(item) and self.IsItemEnabled(item):
                ID = self.GetPyData(item)["ID"]
                if self.GetPyData(item)["type"] == typeTemp :
                    listeCoches.append(ID)
        return listeCoches
    
    def GetListeEcoles(self):
        return self.GetCoches(typeTemp="ecole")

    def GetListeClasses(self):
        return self.GetCoches(typeTemp="classe")

    def GetDictEcoles(self):
        return self.dictEcoles
    
    def GetDictClasses(self):
        return self.dictClasses
    
    
    
# -------------------------------------------------------------------------------------------------------------------------------------

class Page_Activites(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((250, 50))

        self.label_saut_activites = wx.StaticText(self, -1, _(u"Sauts de page :"))
        self.checkbox_saut_activites = wx.CheckBox(self, -1, _(u"Après l'activité"))
        self.checkbox_saut_groupes = wx.CheckBox(self, -1, _(u"Après le groupe"))
        
        # Propriétés
        self.checkbox_saut_activites.SetToolTipString(_(u"Cochez cette case pour insérer un saut de page après chaque activité"))
        self.checkbox_saut_groupes.SetToolTipString(_(u"Cochez cette case pour insérer un saut de page après chaque groupe"))
        
        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_activites, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=5)
        grid_sizer_options.Add(self.label_saut_activites, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_activites, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_groupes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()
                
# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Scolarite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.checkbox_ecoles = wx.CheckBox(self, -1, _(u"Regrouper par école et par classe"))
        self.ctrl_ecoles = CTRL_Ecoles(self)
        self.ctrl_ecoles.SetMinSize((380, 50))

        self.label_saut_ecoles = wx.StaticText(self, -1, _(u"Sauts de page :"))
        self.checkbox_saut_ecoles = wx.CheckBox(self, -1, _(u"Après l'école"))
        self.checkbox_saut_classes = wx.CheckBox(self, -1, _(u"Après la classe"))
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEcoles, self.checkbox_ecoles)
        
        # Propriétés
        self.checkbox_ecoles.SetToolTipString(_(u"Cochez cette case pour regrouper les individus par école et par classe"))
        self.checkbox_saut_ecoles.SetToolTipString(_(u"Cochez cette case pour insérer un saut de page après chaque école"))
        self.checkbox_saut_classes.SetToolTipString(_(u"Cochez cette case pour insérer un saut de page après chaque classe"))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.checkbox_ecoles, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_ecoles, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=5)
        grid_sizer_options.Add(self.label_saut_ecoles, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_ecoles, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_classes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()
        
        self.OnCheckEcoles(None)
        
    def OnCheckEcoles(self, event): 
        if self.checkbox_ecoles.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_ecoles.Activation(etat)
        self.label_saut_ecoles.Enable(etat)
        self.checkbox_saut_ecoles.Enable(etat)
        self.checkbox_saut_classes.Enable(etat)
        
# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Etiquettes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.checkbox_etiquettes = wx.CheckBox(self, -1, _(u"Regrouper par étiquette"))
        self.ctrl_etiquettes = CTRL_Etiquettes.CTRL(self, activeMenu=False, onCheck=None)
        self.ctrl_etiquettes.SetMinSize((250, 50))
        self.label_saut_etiquettes = wx.StaticText(self, -1, _(u"Sauts de page :"))
        self.checkbox_saut_etiquettes = wx.CheckBox(self, -1, _(u"Après l'étiquette"))
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEtiquettes, self.checkbox_etiquettes)
        
        # Propriétés
        self.checkbox_etiquettes.SetToolTipString(_(u"Cochez cette case pour regrouper les consommations par étiquette"))
        self.checkbox_saut_etiquettes.SetToolTipString(_(u"Cochez cette case pour insérer un saut de page après chaque étiquette"))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.checkbox_etiquettes, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_etiquettes, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=5)
        grid_sizer_options.Add(self.label_saut_etiquettes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_etiquettes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()
        
        self.OnCheckEtiquettes(None) 
        
    def OnCheckEtiquettes(self, event): 
        if self.checkbox_etiquettes.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_etiquettes.Activation(etat)
        self.label_saut_etiquettes.Enable(etat)
        self.checkbox_saut_etiquettes.Enable(etat)

# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Unites(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_unites = CTRL_Unites_impression_conso.CTRL(self)
        self.ctrl_unites.SetMinSize((250, 50))
        self.ctrl_unites.MAJ() 

        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Actualiser.png", wx.BITMAP_TYPE_ANY))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Descendre, self.bouton_descendre)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Reinit, self.bouton_reinit)
        
        # Propriétés
        self.bouton_monter.SetToolTipString(_(u"Cliquez ici pour monter l'unité sélectionnée dans la liste"))
        self.bouton_descendre.SetToolTipString(_(u"Cliquez ici pour descendre l'unité sélectionnée dans la liste"))
        self.bouton_reinit.SetToolTipString(_(u"Cliquez ici pour réinitialiser la liste complète des unités"))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_base.Add(self.ctrl_unites, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_reinit, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()


# ----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Options(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele = wx.Choice(self, -1, choices=[_(u"Modèle par défaut"),])
        self.ctrl_modele.Select(0)
        self.label_tri = wx.StaticText(self, -1, _(u"Tri :"))
        self.ctrl_tri = wx.Choice(self, -1, choices=["Nom", _(u"Prénom"), _(u"Age")])
        self.ctrl_tri.Select(0)
        self.ctrl_ordre = wx.Choice(self, -1, choices=["Croissant", _(u"Décroissant")])
        self.ctrl_ordre.Select(0)
        
        self.checkbox_couleur = wx.CheckBox(self, -1, _(u"Couleur de fond du titre :"))
        self.ctrl_couleur = csel.ColourSelect(self, -1, u"", COULEUR_FOND_TITRE, size=(60, 18))
        self.checkbox_lignes_vierges = wx.CheckBox(self, -1, _(u"Afficher des lignes vierges :"))
        self.checkbox_lignes_vierges.SetValue(True)
        self.ctrl_nbre_lignes = wx.Choice(self, -1, choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])
        self.ctrl_nbre_lignes.Select(2)
        self.checkbox_age = wx.CheckBox(self, -1, _(u"Afficher l'âge des individus"))
        self.checkbox_age.SetValue(True)
        self.checkbox_infos = wx.CheckBox(self, -1, _(u"Afficher les informations"))
        self.checkbox_infos.SetValue(True)
        self.checkbox_etiquettes = wx.CheckBox(self, -1, _(u"Afficher les étiquettes"))
        self.checkbox_cotisations_manquantes = wx.CheckBox(self, -1, _(u"Afficher les cotisations manquantes"))
        self.checkbox_cotisations_manquantes.SetValue(True)
        self.checkbox_pieces_manquantes = wx.CheckBox(self, -1, _(u"Afficher les pièces manquantes"))
        self.checkbox_pieces_manquantes.SetValue(True)
        self.checkbox_tous_inscrits = wx.CheckBox(self, -1, _(u"Afficher tous les inscrits"))
        self.checkbox_photos = wx.CheckBox(self, -1, _(u"Afficher les photos :"))
        self.checkbox_photos.SetValue(False)
        self.ctrl_taille_photos = wx.Choice(self, -1, choices=[_(u"Petite taille"), _(u"Moyenne taille"), _(u"Grande taille")])
        self.ctrl_taille_photos.SetSelection(1)
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckLignesVierges, self.checkbox_lignes_vierges)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckPhotos, self.checkbox_photos)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCouleur, self.checkbox_couleur)
        
        # Propriétés
        self.checkbox_couleur.SetToolTipString(_(u"Cochez cette case pour afficher le fond des titres en couleur"))
        self.ctrl_couleur.SetToolTipString(_(u"Cliquez ici pour sélectionner une couleur de fond de titre"))
        self.checkbox_lignes_vierges.SetToolTipString(_(u"Cochez cette case pour afficher des lignes vierges à la fin de la liste"))
        self.checkbox_age.SetToolTipString(_(u"Cochez cette case pour afficher l'âge des individus dans la liste"))
        self.checkbox_infos.SetToolTipString(_(u"Cochez cette case pour afficher les informations individuelles"))
        self.checkbox_etiquettes.SetToolTipString(_(u"Cochez cette case pour afficher le détail des étiquettes pour chaque consommation"))
        self.checkbox_cotisations_manquantes.SetToolTipString(_(u"Cochez cette case pour afficher les cotisations manquantes"))
        self.checkbox_pieces_manquantes.SetToolTipString(_(u"Cochez cette case pour afficher les pièces manquantes"))
        self.checkbox_tous_inscrits.SetToolTipString(_(u"Cochez cette case pour inclure tous les inscrits dans la liste"))
        self.checkbox_photos.SetToolTipString(_(u"Cochez cette case pour afficher les photos des individus"))
        self.ctrl_nbre_lignes.SetToolTipString(_(u"Sélectionnez le nombre de lignes à afficher"))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=10, cols=1, vgap=8, hgap=10)
        
        grid_sizer_options_grille = wx.FlexGridSizer(rows=8, cols=2, vgap=5, hgap=10)
        grid_sizer_options_grille.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_grille.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
        grid_sizer_options_grille.Add(self.label_tri, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Tri
        grid_sizer_tri = wx.FlexGridSizer(rows=1, cols=2, vgap=12, hgap=10)
        grid_sizer_tri.Add(self.ctrl_tri, 0, wx.EXPAND, 0)
        grid_sizer_tri.Add(self.ctrl_ordre, 0, wx.EXPAND, 0)
        grid_sizer_options_grille.Add(grid_sizer_tri, 0, wx.EXPAND, 0)
        
        grid_sizer_options_grille.Add( (10, 10), 0, wx.EXPAND, 0)
        
        grid_sizer_options_grille.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_options_grille, 1, wx.EXPAND, 0)
        
        grid_sizer_couleur = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_couleur.Add(self.checkbox_couleur, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_couleur.Add(self.ctrl_couleur, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_couleur, 1, wx.EXPAND, 0)
        
        grid_sizer_lignes_vierges = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_lignes_vierges.Add(self.checkbox_lignes_vierges, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lignes_vierges.Add(self.ctrl_nbre_lignes, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_lignes_vierges, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.checkbox_age, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.checkbox_infos, 0, wx.ALIGN_CENTER_VERTICAL, 0) 
        grid_sizer_base.Add(self.checkbox_etiquettes, 0, wx.ALIGN_CENTER_VERTICAL, 0) 
        grid_sizer_base.Add(self.checkbox_cotisations_manquantes, 0, wx.ALIGN_CENTER_VERTICAL, 0) 
        grid_sizer_base.Add(self.checkbox_pieces_manquantes, 0, wx.ALIGN_CENTER_VERTICAL, 0) 
        grid_sizer_base.Add(self.checkbox_tous_inscrits, 0, wx.ALIGN_CENTER_VERTICAL, 0) 
        
        grid_sizer_photos = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_photos.Add(self.checkbox_photos, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_photos.Add(self.ctrl_taille_photos, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_photos, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()
        
        # Init
        self.OnCheckLignesVierges(None)
        self.OnCheckPhotos(None) 
        self.OnCheckCouleur(None) 

    def OnCheckLignesVierges(self, event): 
        if self.checkbox_lignes_vierges.GetValue() == True :
            self.ctrl_nbre_lignes.Enable(True)
        else:
            self.ctrl_nbre_lignes.Enable(False)

    def OnCheckPhotos(self, event): 
        if self.checkbox_photos.GetValue() == True :
            self.ctrl_taille_photos.Enable(True)
        else:
            self.ctrl_taille_photos.Enable(False)

    def OnCheckCouleur(self, event): 
        if self.checkbox_couleur.GetValue() == True :
            self.ctrl_couleur.Enable(True)
        else:
            self.ctrl_couleur.Enable(False)


# ----------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style= wx.BK_DEFAULT | wx.NB_MULTILINE) 
        self.dictPages = {}

        self.listePages = [
            {"code" : "activites", "ctrl" : Page_Activites(self), "label" : _(u"Activités"), "image" : "Activite.png"},
            {"code" : "scolarite", "ctrl" : Page_Scolarite(self), "label" : _(u"Scolarité"), "image" : "Classe.png"},
            {"code" : "etiquettes", "ctrl" : Page_Etiquettes(self), "label" : _(u"Etiquettes"), "image" : "Etiquette.png"},
            {"code" : "unites", "ctrl" : Page_Unites(self), "label" : _(u"Unités"), "image" : "Tableau_colonne.png"},
            {"code" : "options", "ctrl" : Page_Options(self), "label" : _(u"Options"), "image" : "Options.png"},
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages :
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap("Images/16x16/%s" % dictPage["image"], wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Création des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages :
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]
    
    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages :
            if dictPage["code"] == codePage :
                self.SetSelection(index)
            index += 1

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        if event.GetOldSelection()==-1: return
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        self.Freeze()
        wx.CallLater(1, page.Refresh)
        self.Thaw()
        event.Skip()



# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, date=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_conso", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.date = date
        
        intro = _(u"Vous pouvez ici imprimer une liste des consommations au format PDF. Pour une liste journalière, sélectionnez 'journalière' puis une date dans le calendrier. Pour la liste d'une période de dates continues ou non, sélectionnez 'périodique' puis plusieurs dates (en appuyant sur les touches CTRL ou SHIFT) dans le calendrier.")
        titre = _(u"Impression d'une liste de consommations")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # Type de calendrier
        self.staticbox_type_staticbox = wx.StaticBox(self, -1, _(u"Type de liste"))
        self.radio_journ = wx.RadioButton(self, -1, _(u"Journalière"), style=wx.RB_GROUP)
        self.radio_period = wx.RadioButton(self, -1, _(u"Périodique"))
        
        # Calendrier
        self.staticbox_date_staticbox = wx.StaticBox(self, -1, _(u"Date"))
        self.ctrl_calendrier = PANEL_Calendrier(self)
        self.ctrl_calendrier.SetMinSize((250, 80)) 
                
        # Mémorisation des paramètres
        self.staticbox_memoriser_staticbox = wx.StaticBox(self, -1, _(u"Mémoriser"))
        self.ctrl_memoriser = wx.CheckBox(self, -1, _(u"Mémoriser les paramètres"))
        self.ctrl_memoriser.SetValue(True) 
        
        # Paramètres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self) 

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_export = CTRL_Bouton_image.CTRL(self, texte=_(u"Export sous Excel"), cheminImage="Images/32x32/Excel.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioJourn, self.radio_journ)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriod, self.radio_period)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExport, self.bouton_export)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Récupération des paramètres dans le CONFIG
        self.ImporterParametres() 
        
        # Active le mode du calendrier
        if self.radio_journ.GetValue() == True : self.OnRadioJourn(None)
        if self.radio_period.GetValue() == True : self.OnRadioPeriod(None)
        
        # Sélectionne la date par défaut
        if self.date == None :
            self.SetDateDefaut(datetime.date.today())
        else:
            self.SetDateDefaut(self.date)

        # Init Contrôles
        self.bouton_ok.SetFocus() 
        
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle(_(u"Impression d'une liste de consommations"))
        self.radio_journ.SetToolTipString(_(u"Cochez ici pour sélectionner une liste journalière"))
        self.radio_period.SetToolTipString(_(u"Cochez ici pour sélectionner une liste périodique"))
        self.ctrl_memoriser.SetToolTipString(_(u"Cochez cette case pour mémoriser les paramètres pour la prochaine édition"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_export.SetToolTipString(_(u"Cliquez ici pour exporter les données vers Excel"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((880, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Type
        staticbox_type = wx.StaticBoxSizer(self.staticbox_type_staticbox, wx.HORIZONTAL)
        staticbox_type.Add(self.radio_journ, 0, wx.ALL|wx.EXPAND, 10)
        staticbox_type.Add(self.radio_period, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(staticbox_type, 1, wx.EXPAND, 0)

        # Calendrier
        staticbox_date = wx.StaticBoxSizer(self.staticbox_date_staticbox, wx.VERTICAL)
        staticbox_date.Add(self.ctrl_calendrier, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(staticbox_date, 1, wx.EXPAND, 0)

        # Mémoriser
        staticbox_memoriser = wx.StaticBoxSizer(self.staticbox_memoriser_staticbox, wx.VERTICAL)
        staticbox_memoriser.Add(self.ctrl_memoriser, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_gauche.Add(staticbox_memoriser, 1, wx.EXPAND, 0)
        
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Paramètres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.HORIZONTAL)
        staticbox_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_contenu.Add(staticbox_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)

        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)     
                                        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_export, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetSize(self.GetMinSize())
        self.CenterOnScreen() 
    
    def GetPage(self, code=""):
        """ Retourne le ctrl page du notebook selon le code page """
        return self.ctrl_parametres.GetPageAvecCode(code)

    def OnRadioJourn(self, event):
        self.ctrl_calendrier.SetMultiSelection(False)
        self.GetPage("unites").ctrl_unites.SetTypeListe("journ")
        self.GetPage("unites").ctrl_unites.MAJ()
        self.staticbox_date_staticbox.SetLabel(_(u"Date"))
        
    def OnRadioPeriod(self, event):
        self.ctrl_calendrier.SetMultiSelection(True)
        self.GetPage("unites").ctrl_unites.SetTypeListe("period")
        self.GetPage("unites").ctrl_unites.MAJ()
        self.staticbox_date_staticbox.SetLabel(_(u"Période"))

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedesconsommations")
    
    def SetDateDefaut(self, date=None):
        self.ctrl_calendrier.SetDates([date,])
        self.SetDates([date,]) 
        
    def SetDates(self, listeDates=[]):
        if listeDates == None : listeDates = []
        self.GetPage("activites").ctrl_activites.SetDates(listeDates)
        self.SetUnites(self.GetPage("activites").ctrl_activites.GetListeActivites())
        self.GetPage("scolarite").ctrl_ecoles.SetDates(listeDates)

    def SetUnites(self, listeActivites=[]):
        self.GetPage("unites").ctrl_unites.SetActivites(listeActivites)
        self.GetPage("etiquettes").ctrl_etiquettes.SetActivites(listeActivites)
        self.GetPage("etiquettes").ctrl_etiquettes.SetCoches(tout=True)
        
    def GetAge(self, date_naiss=None):
        if date_naiss == None : return None
        datedujour = datetime.date.today()
        age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
        return age

    def OnClose(self, event):
        self.OnBoutonAnnuler(None)

    def OnBoutonAnnuler(self, event):
        self.MemoriserParametres() 
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonOk(self, event):
        self.Impression() 
    
    def OnBoutonExport(self, event=None):
        typeListe = self.GetPage("unites").ctrl_unites.typeListe
##        if typeListe != "journ" :
##            dlg = wx.MessageDialog(self, _(u"L'export sous Excel n'est disponible que pour le mode journalier !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
        
        donnees = self.Impression(modeExport=True) 
        if donnees == False :
            return
        listeExport, largeursColonnes = donnees
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xls" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xls)|*.xls|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        import pyExcelerator
        classeur = pyExcelerator.Workbook()

        al = pyExcelerator.Alignment()
        al.horz = pyExcelerator.Alignment.HORZ_LEFT
        al.vert = pyExcelerator.Alignment.VERT_CENTER
        
        ar = pyExcelerator.Alignment()
        ar.horz = pyExcelerator.Alignment.HORZ_RIGHT
        ar.vert = pyExcelerator.Alignment.VERT_CENTER

        ac = pyExcelerator.Alignment()
        ac.horz = pyExcelerator.Alignment.HORZ_CENTER
        ac.vert = pyExcelerator.Alignment.VERT_CENTER

        styleDefaut = pyExcelerator.XFStyle()
        styleDefaut.alignment = ac

        styleDate = pyExcelerator.XFStyle()
        styleDate.num_format_str = 'DD/MM/YYYY'
        styleDate.alignment = ar

        styleHeure = pyExcelerator.XFStyle()
        styleHeure.num_format_str = "[hh]:mm"
        styleHeure.alignment = ar
        
        numFeuille = 1
        for dictFeuille in listeExport :
            activite = dictFeuille["activite"]
            groupe = dictFeuille["groupe"]
            ecole = dictFeuille["ecole"]
            classe = dictFeuille["classe"]
            etiquette = dictFeuille["etiquette"]
            lignes = dictFeuille["lignes"]
            
            # Nom de la feuille
            titre = _(u"Page %d") % numFeuille
            feuille = classeur.add_sheet(titre)
            
            # Titre de la page
            listeLabels = []
            if activite != None : listeLabels.append(activite)
            if groupe != None : listeLabels.append(groupe)
            if ecole != None : listeLabels.append(ecole)
            if classe != None : listeLabels.append(classe)
            if etiquette != None : listeLabels.append(etiquette)
            titre = " - ".join(listeLabels)
            feuille.write(0, 0, titre)
            
            numLigne = 2
            for ligne in lignes :
                
                numColonne = 0
                for valeur in ligne :
                    # Largeur colonne
                    if type(valeur) == unicode and (_(u"Nom - ") in valeur or valeur == "Informations") :
                        feuille.col(numColonne).width = 10000
                    # Valeur case
                    if type(valeur) in (str, unicode, int) :
                        # Formatage des heures
                        if type(valeur) == unicode and len(valeur) == 11 and valeur[2] == "h" and valeur[8] == "h" :
                            valeur = valeur.replace(u"\n", u"-")
                        feuille.write(numLigne, numColonne, valeur, styleDefaut)
                    # Si c'est une liste
                    if type(valeur) == list :
                        listeInfos = []
                        for element in valeur :
                            try :
                                listeInfos.append(element.text)
                            except :
                                listeInfos.append(element.P.text) 
                        feuille.write(numLigne, numColonne, " - ".join(listeInfos), styleDefaut)
                    
                    numColonne += 1
                numLigne += 1
            numFeuille += 1
            
        # Finalisation du fichier xls
        classeur.save(cheminFichier)
        
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

    
    def Impression(self, modeExport=False):
        # Récupération et vérification des données
        listeDates = self.ctrl_calendrier.GetDates() 
        if listeDates == None : listeDates = []
        if len(listeDates) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une date !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        listeActivites = self.GetPage("activites").ctrl_activites.GetListeActivites() 
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        listeGroupes = self.GetPage("activites").ctrl_activites.GetListeGroupes() 
        if len(listeGroupes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un groupe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        if self.GetPage("scolarite").checkbox_ecoles.GetValue() == True :
            
            listeEcoles = self.GetPage("scolarite").ctrl_ecoles.GetListeEcoles() 
            if len(listeEcoles) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une école !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            listeClasses = self.GetPage("scolarite").ctrl_ecoles.GetListeClasses() 
            if len(listeClasses) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une classe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        if self.GetPage("etiquettes").checkbox_etiquettes.GetValue() == True :
            
            listeEtiquettes = self.GetPage("etiquettes").ctrl_etiquettes.GetCoches() 
            if len(listeEtiquettes) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une étiquette !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
        dictChoixUnites = self.GetPage("unites").ctrl_unites.GetDonnees() 
        if len(dictChoixUnites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner au moins une unité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        for IDactivite in listeActivites :
            valide = False
            listeUnitesTemp = dictChoixUnites[IDactivite]
            for typeTemp, IDunite, affichage in listeUnitesTemp :
                if affichage != "jamais" : valide = True
            if valide == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement avoir au moins une unité à afficher pour chaque activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        typeListe = self.GetPage("unites").ctrl_unites.typeListe
        
        # Récupération des autres données dans la base
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        if len(listeGroupes) == 0 : conditionGroupes = "()"
        elif len(listeGroupes) == 1 : conditionGroupes = "(%d)" % listeGroupes[0]
        else : conditionGroupes = str(tuple(listeGroupes))
        
        if len(listeDates) == 0 : conditionDates = "()"
        elif len(listeDates) == 1 : conditionDates = "('%s')" % listeDates[0]
        else : 
            listeTmp = []
            for dateTmp in listeDates :
                listeTmp.append(str(dateTmp))
            conditionDates = str(tuple(listeTmp))
        
        if self.GetPage("scolarite").checkbox_ecoles.GetValue() == True :
            if len(listeClasses) == 0 : conditionTemp = "()"
            elif len(listeClasses) == 1 : conditionTemp = "(%d)" % listeClasses[0]
            else : conditionTemp = str(tuple(listeClasses))
            conditionsClasses = "AND (scolarite.IDclasse IN %s OR scolarite.IDclasse IS NULL)" % conditionTemp
        else:
            conditionsClasses = ""
            
            
        # Récupération de la liste des unités ouvertes ce jour
        DB = GestionDB.DB()
        req = """SELECT IDouverture, ouvertures.IDactivite, ouvertures.IDunite, IDgroupe, date
        FROM ouvertures 
        LEFT JOIN unites ON unites.IDunite = ouvertures.IDunite
        WHERE ouvertures.IDactivite IN %s AND date IN %s
        AND IDgroupe IN %s
        ORDER BY ordre; """ % (conditionActivites, conditionDates, conditionGroupes)
        DB.ExecuterReq(req)
        listeOuvertures = DB.ResultatReq()
        dictOuvertures = {}
        for IDouverture, IDactivite, IDunite, IDgroupe, date in listeOuvertures :
            date = DateEngEnDateDD(date)
            if dictOuvertures.has_key(IDactivite) == False : dictOuvertures[IDactivite] = {}
            if dictOuvertures[IDactivite].has_key(IDgroupe) == False : dictOuvertures[IDactivite][IDgroupe] = {}
            if dictOuvertures[IDactivite][IDgroupe].has_key(date) == False : dictOuvertures[IDactivite][IDgroupe][date] = []
            dictOuvertures[IDactivite][IDgroupe][date].append(IDunite)
            
##            if dictOuvertures.has_key(IDactivite) == False : dictOuvertures[IDactivite] = {}
##            if dictOuvertures[IDactivite].has_key(IDgroupe) == False : dictOuvertures[IDactivite][IDgroupe] = []
##            dictOuvertures[IDactivite][IDgroupe].append(IDunite)

        # Récupération des infos sur les unités
        req = """SELECT IDunite, IDactivite, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin, ordre
        FROM unites;"""
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        dictUnites = {}
        for IDunite, IDactivite, nom, abrege, typeTemp, heure_debut, heure_fin, date_debut, date_fin, ordre in listeUnites :
            dictUnites[IDunite] = {"IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "type" : typeTemp, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre}
        
        # Récupération des infos sur les unités de remplissage
        req = """SELECT 
        unites_remplissage_unites.IDunite_remplissage_unite, 
        unites_remplissage_unites.IDunite_remplissage, 
        unites_remplissage_unites.IDunite,
        nom, abrege, etiquettes
        FROM unites_remplissage_unites
        LEFT JOIN unites_remplissage ON unites_remplissage.IDunite_remplissage = unites_remplissage_unites.IDunite_remplissage
        ;"""
        DB.ExecuterReq(req)
        listeUnitesRemplissage = DB.ResultatReq()
        dictUnitesRemplissage = {}
        for IDunite_remplissage_unite, IDunite_remplissage, IDunite, nom, abrege, etiquettes in listeUnitesRemplissage :
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
            if dictUnitesRemplissage.has_key(IDunite_remplissage) == False :
                dictUnitesRemplissage[IDunite_remplissage] = {"nom" : nom, "abrege" : abrege, "etiquettes" : etiquettes, "unites" : [] }
            dictUnitesRemplissage[IDunite_remplissage]["unites"].append(IDunite)
        
        # Récupération des noms des groupes
        dictGroupes = self.GetPage("activites").ctrl_activites.GetDictGroupes()
        
        # Récupération des noms d'activités
        dictActivites = self.GetPage("activites").ctrl_activites.GetDictActivites()

        # Récupération des noms des écoles
        dictEcoles = self.GetPage("scolarite").ctrl_ecoles.GetDictEcoles()
        
        # Récupération des noms des classes
        dictClasses = self.GetPage("scolarite").ctrl_ecoles.GetDictClasses()
        
        # Récupération des étiquettes
        dictEtiquettes = self.GetPage("etiquettes").ctrl_etiquettes.GetDictEtiquettes()

        # Récupération des consommations
        req = """SELECT IDconso, consommations.IDindividu, IDcivilite, consommations.IDactivite, IDunite, consommations.IDgroupe, heure_debut, heure_fin, etat, quantite, etiquettes,
        IDcivilite, individus.nom, prenom, date_naiss, types_sieste.nom, inscriptions.IDfamille, consommations.date, scolarite.IDclasse
        FROM consommations 
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN types_sieste ON types_sieste.IDtype_sieste = individus.IDtype_sieste
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        LEFT JOIN scolarite ON scolarite.IDindividu = consommations.IDindividu AND scolarite.date_debut <= consommations.date AND scolarite.date_fin >= consommations.date
        WHERE etat IN ("reservation", "present")
        AND consommations.IDactivite IN %s AND consommations.date IN %s %s
        ; """ % (conditionActivites, conditionDates, conditionsClasses)
        DB.ExecuterReq(req)
        listeConso = DB.ResultatReq()
        dictConso = {}
        dictIndividus = {}
        listeIDindividus = []
        for IDconso, IDindividu, IDcivilite, IDactivite, IDunite, IDgroupe, heure_debut, heure_fin, etat, quantite, etiquettes, IDcivilite, nom, prenom, date_naiss, nomSieste, IDfamille, date, IDclasse in listeConso :
            date = DateEngEnDateDD(date)
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes) 
            
            # Calcul de l'âge
            if date_naiss != None : date_naiss = DateEngEnDateDD(date_naiss)
            age = self.GetAge(date_naiss)
            
            # Mémorisation de l'activité
            if dictConso.has_key(IDactivite) == False :
                dictConso[IDactivite] = {}
                
            # Mémorisation du groupe
            if dictConso[IDactivite].has_key(IDgroupe) == False :
                dictConso[IDactivite][IDgroupe] = {}

            # Mémorisation de la classe
            if self.GetPage("scolarite").checkbox_ecoles.GetValue() == False :
                IDclasse = None
            
            if dictConso[IDactivite][IDgroupe].has_key(IDclasse) == False :
                dictConso[IDactivite][IDgroupe][IDclasse] = {}

            # Mémorisation de l'étiquette
            if self.GetPage("etiquettes").checkbox_etiquettes.GetValue() == False :
                listeEtiquettes = [None,]
            else :
                listeEtiquettes = etiquettes
            
            for IDetiquette in listeEtiquettes :
                
                if dictConso[IDactivite][IDgroupe][IDclasse].has_key(IDetiquette) == False :
                    dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette] = {}

                # Mémorisation de l'individu
                if dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette].has_key(IDindividu) == False :
                    dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu] = { "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss, "age" : age, "nomSieste" : nomSieste, "listeConso" : {} }

                # Mémorisation de la date
                if dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu]["listeConso"].has_key(date) == False :
                    dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu]["listeConso"][date] = {}
                
                # Mémorisation de la consommation
                if dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu]["listeConso"][date].has_key(IDunite) == False :
                    dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu]["listeConso"][date][IDunite] = []
                    
                dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu]["listeConso"][date][IDunite].append( { "heure_debut" : heure_debut, "heure_fin" : heure_fin, "etat" : etat, "quantite" : quantite, "IDfamille" : IDfamille, "etiquettes" : etiquettes } )
                
                # Mémorisation du IDindividu
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu) 
                    
                # Dict Individu
                dictIndividus[IDindividu] = { "IDcivilite" : IDcivilite }


        # Intégration de tous les inscrits
        if self.GetPage("options").checkbox_tous_inscrits.GetValue() == True :
            
            req = """SELECT individus.IDindividu, IDcivilite, individus.nom, prenom, date_naiss, types_sieste.nom, 
            inscriptions.IDactivite, inscriptions.IDgroupe, inscriptions.IDfamille, scolarite.IDclasse
            FROM individus 
            LEFT JOIN types_sieste ON types_sieste.IDtype_sieste = individus.IDtype_sieste
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            LEFT JOIN scolarite ON scolarite.IDindividu = individus.IDindividu AND scolarite.date_debut <= '%s' AND scolarite.date_fin >= '%s'
            WHERE inscriptions.IDactivite IN %s and inscriptions.parti=0
            ; """ % (min(listeDates), max(listeDates), conditionActivites)
            DB.ExecuterReq(req)
            listeTousInscrits = DB.ResultatReq()
            for IDindividu, IDcivilite, nom, prenom, date_naiss, nomSieste, IDactivite, IDgroupe, IDfamille, IDclasse in listeTousInscrits :
                
                # Calcul de l'âge
                if date_naiss != None : date_naiss = DateEngEnDateDD(date_naiss)
                age = self.GetAge(date_naiss)
                            
                # Mémorisation de l'activité
                if dictConso.has_key(IDactivite) == False :
                    dictConso[IDactivite] = {}
                    
                # Mémorisation du groupe
                if dictConso[IDactivite].has_key(IDgroupe) == False :
                    dictConso[IDactivite][IDgroupe] = {}

                # Mémorisation de la classe
                if self.GetPage("scolarite").checkbox_ecoles.GetValue() == False :
                    IDclasse = None
                
                if dictConso[IDactivite][IDgroupe].has_key(IDclasse) == False :
                    dictConso[IDactivite][IDgroupe][IDclasse] = {}
                
                IDetiquette = None
                if dictConso[IDactivite][IDgroupe][IDclasse].has_key(IDetiquette) == False :
                    dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette] = {}
                
                # Mémorisation de l'individu
                if dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette].has_key(IDindividu) == False :
                    dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu] = { "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss, "age" : age, "nomSieste" : nomSieste, "listeConso" : {} }
                
                # Mémorisation du IDindividu
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu) 
                    
                # Dict Individu
                dictIndividus[IDindividu] = { "IDcivilite" : IDcivilite }

        # Récupération des mémo-journées
        req = """SELECT IDmemo, IDindividu, date, texte
        FROM memo_journee
        WHERE date IN %s
        ORDER BY date
        ; """ % conditionDates
        DB.ExecuterReq(req)
        listeMemos = DB.ResultatReq()
        dictMemos = {}
        for IDmemo, IDindividu, date, texte in listeMemos :
            date = DateEngEnDateDD(date)
            if dictMemos.has_key(IDindividu) == False :
                dictMemos[IDindividu] = {} 
            dictMemos[IDindividu][date] = texte
        
        # Récupération des photos individuelles
        dictPhotos = {}
        taillePhoto = 128
        if self.GetPage("options").ctrl_taille_photos.GetSelection() == 0 : tailleImageFinal = 16
        if self.GetPage("options").ctrl_taille_photos.GetSelection() == 1 : tailleImageFinal = 32
        if self.GetPage("options").ctrl_taille_photos.GetSelection() == 2 : tailleImageFinal = 64
        if self.GetPage("options").checkbox_photos.GetValue() == True :
            for IDindividu in listeIDindividus :
                IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                nomFichier = "Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"]
                IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)
                
                # Création de la photo dans le répertoire Temp
                nomFichier = "Temp/photoTmp" + str(IDindividu) + ".jpg"
                bmp.SaveFile(nomFichier, type=wx.BITMAP_TYPE_JPEG)
                img = Image(nomFichier, width=tailleImageFinal, height=tailleImageFinal)
                dictPhotos[IDindividu] = img
                
        # Récupération des messages
        req = """SELECT IDmessage, type, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite,
        afficher_accueil, afficher_liste, IDfamille, IDindividu, texte, nom
        FROM messages
        WHERE afficher_liste=1
        ;"""
        DB.ExecuterReq(req)
        listeMessages = DB.ResultatReq()
        dictMessagesFamilles = {}
        dictMessagesIndividus = {}
        for IDmessage, typeTemp, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite, afficher_accueil, afficher_liste, IDfamille, IDindividu, texte, nom in listeMessages :
            dictTemp = {
                "IDmessage":IDmessage, "type":typeTemp, "IDcategorie":IDcategorie, "date_saisie":date_saisie, 
                "IDutilisateur":IDutilisateur, "date_parution":date_parution, "priorite":priorite, 
                "afficher_accueil":afficher_accueil, "afficher_liste":afficher_liste, "texte":texte, "nom":nom,
                }
            # Si c'est un message familial
            if IDindividu != None and dictMessagesIndividus.has_key(IDindividu) == False : dictMessagesIndividus[IDindividu] = []
            if IDindividu != None : dictMessagesIndividus[IDindividu].append(dictTemp)
            # Si c'est un message individuel
            if IDfamille != None and dictMessagesFamilles.has_key(IDfamille) == False : dictMessagesFamilles[IDfamille] = []
            if IDfamille != None : dictMessagesFamilles[IDfamille].append(dictTemp)
        
        # Récupération de la liste des cotisations manquantes
        dictCotisations = UTILS_Cotisations_manquantes.GetListeCotisationsManquantes(dateReference=datetime.date.today(), listeActivites=listeActivites, presents=(min(listeDates), max(listeDates)), concernes=True)

        # Récupération de la liste des pièces manquantes
        dictPieces = UTILS_Pieces_manquantes.GetListePiecesManquantes(dateReference=datetime.date.today(), listeActivites=listeActivites, presents=(min(listeDates), max(listeDates)), concernes=True)
        
        # Récupération des informations médicales
        req = """SELECT IDprobleme, IDindividu, IDtype, intitule, description, traitement_medical, description_traitement, date_debut_traitement, date_fin_traitement
        FROM problemes_sante
        WHERE diffusion_listing_conso = 1
        AND date_debut <= '%s' AND date_fin >= '%s';""" % (min(listeDates), max(listeDates))
        DB.ExecuterReq(req)
        listeInfosMedicales = DB.ResultatReq()
        dictInfosMedicales = {}
        for IDprobleme, IDindividu, IDtype, intitule, description, traitement_medical, description_traitement, date_debut_traitement, date_fin_traitement in listeInfosMedicales :
            if dictInfosMedicales.has_key(IDindividu) == False : dictInfosMedicales[IDindividu] = []
            dictTemp = {"IDtype":IDtype, "intitule":intitule, "description":description, "traitement_medical":traitement_medical, "description_traitement":description_traitement, "date_debut_traitement":date_debut_traitement, "date_fin_traitement":date_fin_traitement}
            dictInfosMedicales[IDindividu].append(dictTemp)

        DB.Close()
            
        # ---------------- Création du PDF -------------------
        
        if self.GetPage("options").checkbox_couleur.GetValue() == True :
            couleur_fond_titre = ConvertCouleurWXpourPDF(self.GetPage("options").ctrl_couleur.GetColour())
        else:
            couleur_fond_titre = ConvertCouleurWXpourPDF((255, 255, 255))
        
        # Orientation de la page
        if typeListe == "journ" :
            orientation = "portrait"
        else:
            orientation = "paysage"
        margeG, margeD = 30, 30
        
        if orientation == "portrait" :
            hauteur_page = A4[1]
            largeur_page = A4[0]
        else:
            hauteur_page = A4[0]
            largeur_page = A4[1]

        # Initialisation du PDF
        nomDoc = "Temp/liste_consommations_%s.pdf" % FonctionsPerso.GenerationIDdoc() 
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = largeur_page - margeG - margeD
        
        # Création du header du document
        def CreationTitreDocument():
            dataTableau = []
            largeursColonnes = ( (largeurContenu-100, 100) )
            dateDuJour = DateEngFr(str(datetime.date.today()))
            if typeListe == "journ" :
                titre = _(u"Consommations du %s") % DateComplete(min(listeDates))
            else:
                titre = _(u"Consommations")
            dataTableau.append((titre, _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)))
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                    ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                    ('ALIGN', (0,0), (0,0), 'LEFT'), 
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                    ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                    ('FONT',(1,0),(1,0), "Helvetica", 6), 
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0,20))       

        # Création du titre des tableaux
        def CreationTitreTableau(nomActivite="", nomGroupe="", nomEcole="", nomClasse="", couleurFond=couleur_fond_titre, couleurTexte=colors.black):
            dataTableau = []
            largeursColonnes = ( (largeurContenu * 1.0 / 3, largeurContenu * 2.0 / 3) )
            
            styleActivite = ParagraphStyle(name="activite", fontName="Helvetica", fontSize=5, leading=3, spaceAfter=0, textColor=couleurTexte)
            styleGroupe = ParagraphStyle(name="groupe", fontName="Helvetica-Bold", fontSize=14, leading=16, spaceBefore=0, spaceAfter=2, textColor=couleurTexte)
            styleEcole = ParagraphStyle(name="ecole", fontName="Helvetica", alignment=2, fontSize=5, leading=3, spaceAfter=0, textColor=couleurTexte)
            styleClasse = ParagraphStyle(name="classe", fontName="Helvetica-Bold", alignment=2, fontSize=14, leading=16, spaceBefore=0, spaceAfter=2, textColor=couleurTexte)

            ligne = [ (Paragraph(nomActivite, styleActivite), Paragraph(nomGroupe, styleGroupe)), None]
            if self.GetPage("scolarite").checkbox_ecoles.GetValue() == True :
                if nomEcole == None : nomEcole = _(u"Ecole inconnue")
                if nomClasse == None : nomClasse = _(u"Classe inconnue")
                ligne[1] = (Paragraph(nomEcole, styleEcole), Paragraph(nomClasse, styleClasse))
            dataTableau.append(ligne)

            if typeListe == "period" :
                style = TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                        ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                        ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                        ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black), # Box du titre
                        ('LINEBEFORE', (0, 0), (0, 0), 0.25, colors.black), # Box du titre
                        ('LINEAFTER', (-1, 0), (-1, 0), 0.25, colors.black), # Box du titre
                        ])
            else:
                style = TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                        ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                        ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                        ('BOX', (0, 0), (-1, 0), 0.25, colors.black), # Box du titre
                        ])            
            
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
        
        def CreationSautPage():
            try :
                element = str(story[-3])
                if element != "PageBreak()" :
                    story.append(PageBreak())
                    CreationTitreDocument() 
            except :
                pass
                
        # Prépare liste pour Export Excel
        listeExport = []

        # Insère un header
        CreationTitreDocument() 
        
        # Activités
        nbreActivites = len(listeActivites)
        indexActivite = 1
        for IDactivite in listeActivites :
            nomActivite = dictActivites[IDactivite]["nom"]
            
            # Groupes
            if dictOuvertures.has_key(IDactivite) :
                nbreGroupes = len(dictOuvertures[IDactivite])
                
                # tri des groupes par ordre
                listeGroupesTemp = self.TriGroupes(dictOuvertures[IDactivite].keys(), dictGroupes)
                
                indexGroupe = 1
                for IDgroupe in listeGroupesTemp :
                    dictDatesUnites = dictOuvertures[IDactivite][IDgroupe]
                    
                    nomGroupe = dictGroupes[IDgroupe]["nom"]
                    
                    # Classes
                    listeClasses = []
                    if dictConso.has_key(IDactivite) :
                        if dictConso[IDactivite].has_key(IDgroupe) :
                            listeClasses = dictConso[IDactivite][IDgroupe].keys() 

                    # tri des classes
                    listeInfosClasses = self.TriClasses(listeClasses, dictEcoles)
                    
                    # Si aucun enfant scolarisé
                    if len(listeInfosClasses) == 0 or self.GetPage("scolarite").checkbox_ecoles.GetValue() == False :
                        listeInfosClasses = [None,]
                    
                    nbreClasses = len(listeInfosClasses)
                    indexClasse = 1
                    for dictClasse in listeInfosClasses :
                        
                        # Récupération des infos sur école et classe
                        if dictClasse != None :
                            IDclasse = dictClasse["IDclasse"]
                            nomEcole = dictClasse["nomEcole"]
                            nomClasse = dictClasse["nomClasse"]
                        else :
                            IDclasse = None
                            nomEcole = None
                            nomClasse = None
                        
                        
                        # -------------------------------------------------------------------------------
                        listeIDetiquette = []
                        if dictConso.has_key(IDactivite) :
                            if dictConso[IDactivite].has_key(IDgroupe) :
                                if dictConso[IDactivite][IDgroupe].has_key(IDclasse) :
                                    for IDetiquette, temp in dictConso[IDactivite][IDgroupe][IDclasse].iteritems() :
                                        listeIDetiquette.append(IDetiquette)
                        if len(listeIDetiquette) == 0 :
                            listeIDetiquette = [None,]
                            
                        for IDetiquette in listeIDetiquette :
                            
                            # Initialisation du tableau
                            dataTableau = []
                            largeursColonnes = []
                            labelsColonnes = []
                                                
                            # Recherche des entêtes de colonnes :
                            if self.GetPage("options").checkbox_photos.GetValue() == True :
                                labelsColonnes.append(_(u"Photo"))
                                largeursColonnes.append(tailleImageFinal+6)
                                
                            labelsColonnes.append(_(u"Nom - prénom"))
                            largeursColonnes.append(120)
                            
                            if self.GetPage("options").checkbox_age.GetValue() == True :
                                labelsColonnes.append(_(u"Âge"))
                                largeursColonnes.append(20)
                            
                            # Recherche des entetes de colonnes UNITES
                            if typeListe == "journ" :
                                largeurColonneUnite = 30
                            else:
                                largeurColonneUnite = 30
                            
                            listePositionsDates = []
                            positionCol1 = len(labelsColonnes)
                            indexCol = len(labelsColonnes)
                            for date in listeDates :
                                if dictDatesUnites.has_key(date) :
                                    listeUnites = dictDatesUnites[date]
                                    positionG = indexCol
                                    for typeTemp, IDunite, affichage in dictChoixUnites[IDactivite] :
                                        if (affichage == "utilise" and IDunite in listeUnites) or affichage == "toujours" :
                                            if typeTemp == "conso" :
                                                abregeUnite = dictUnites[IDunite]["abrege"]
                                            else:
                                                if dictUnitesRemplissage.has_key(IDunite) :
                                                    abregeUnite = dictUnitesRemplissage[IDunite]["abrege"]
                                                else :
                                                    abregeUnite = "?"
                                            labelsColonnes.append(abregeUnite)
                                            largeur = largeurColonneUnite
                                            
                                            # Agrandit si unité de type multihoraires
                                            if typeTemp == "conso" and dictUnites[IDunite]["type"] == "Multihoraires" :
                                                largeur = 55
                                            
                                            # Agrandit si étiquettes à afficher
                                            if self.GetPage("options").checkbox_etiquettes.GetValue() == True :
                                                largeur += 10
                                                
                                            largeursColonnes.append(largeur)
                                            indexCol += 1
                                    positionD = indexCol-1
                                    listePositionsDates.append((date, positionG, positionD))
                            
                            labelsColonnes.append(_(u"Informations"))
                            largeursColonnes.append(largeurContenu - sum(largeursColonnes))
                            
                            # ------ Création de l'entete de groupe ------
                            CreationTitreTableau(nomActivite, nomGroupe, nomEcole, nomClasse)
                            
                            if IDetiquette != None :
                                nomEtiquette = dictEtiquettes[IDetiquette]["label"]
                                couleurEtiquette = colors.grey #ConvertCouleurWXpourPDF(dictEtiquettes[IDetiquette]["couleurRVB"])
                                CreationTitreTableau(nomGroupe=nomEtiquette, couleurTexte=couleurEtiquette)
                            else :
                                nomEtiquette = None

                            listeLignesExport = []

                            # Création de l'entete des DATES
                            if typeListe == "period" :
                                ligneTempExport = []
                                styleDate = ParagraphStyle(name="date",
                                          fontName="Helvetica-Bold",
                                          fontSize=8,
                                         spaceAfter=0,
                                         leading=9,
                                         #spaceBefore=0,,
                                        )
                                ligne = []
                                for index in range(0, len(labelsColonnes)-1):
                                    ligne.append("")
                                    ligneTempExport.append("")
                                    
                                index = 0
                                for date, positionG, positionD in listePositionsDates :
                                    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
                                    listeJoursAbrege = (_(u"Lun."), _(u"Mar."), _(u"Mer."), _(u"Jeu."), _(u"Ven."), _(u"Sam."), _(u"Dim."))
                                    listeMoisAbrege = (_(u"janv."), _(u"fév."), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juil."), _(u"août"), _(u"sept."), _(u"oct"), _(u"nov."), _(u"déc."))
                                    if (positionD-positionG) < 1 :
                                        jourStr = listeJoursAbrege[date.weekday()]
                                        ligne[positionG] = u"%s\n%d\n%s\n%d" % (jourStr, date.day, listeMoisAbrege[date.month-1], date.year)
                                    else:
                                        jourStr = listeJours[date.weekday()]
                                        dateStr = u"<para align='center'>%s %d %s %d</para>" % (jourStr, date.day, listeMoisAbrege[date.month-1], date.year)
                                        ligne[positionG] = Paragraph(dateStr, styleDate)
                                    ligneTempExport[positionG] = DateEngFr(str(date))
                                    index += 1
                                dataTableau.append(ligne)
                                listeLignesExport.append(ligneTempExport) 
                                
                            # Création des entêtes
                            ligne = []
                            for label in labelsColonnes :
                                ligne.append(label)
                            dataTableau.append(ligne)
                            listeLignesExport.append(ligne) 
                            
                            # --------- Création des lignes -----------
                                
                            # Création d'une liste temporaire pour le tri
                            listeIndividus = []
                            if dictConso.has_key(IDactivite) :
                                if dictConso[IDactivite].has_key(IDgroupe) :
                                    if dictConso[IDactivite][IDgroupe].has_key(IDclasse) :
                                        if dictConso[IDactivite][IDgroupe][IDclasse].has_key(IDetiquette) :
                                            for IDindividu, dictIndividu in dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette].iteritems() :
                                                valeursTri = (IDindividu, dictIndividu["nom"], dictIndividu["prenom"], dictIndividu["age"])
                                                listeIndividus.append(valeursTri)
                            
                            if self.GetPage("options").ctrl_tri.GetSelection() == 0 : paramTri = 1 # Nom
                            if self.GetPage("options").ctrl_tri.GetSelection() == 1 : paramTri = 2 # Prénom
                            if self.GetPage("options").ctrl_tri.GetSelection() == 2 : paramTri = 3 # Age
                            if self.GetPage("options").ctrl_ordre.GetSelection() == 0 :
                                ordreDecroissant = False
                            else:
                                ordreDecroissant = True
                            listeIndividus = sorted(listeIndividus, key=operator.itemgetter(paramTri), reverse=ordreDecroissant)
                            
                            # Récupération des lignes individus
                            dictTotauxColonnes = {}
                            for IDindividu, nom, prenom, age in listeIndividus :
                                
                                dictIndividu = dictConso[IDactivite][IDgroupe][IDclasse][IDetiquette][IDindividu]
                                ligne = []
                                indexColonne = 0
                                
                                # Photo
                                if self.GetPage("options").checkbox_photos.GetValue() == True and IDindividu in dictPhotos :
                                    img = dictPhotos[IDindividu]
                                    ligne.append(img)
                                    indexColonne += 1
                                
                                # Nom
                                ligne.append(u"%s %s" % (nom, prenom))
                                indexColonne += 1
                                
                                # Age
                                if self.GetPage("options").checkbox_age.GetValue() == True :
                                    if age != None :
                                        ligne.append(age)
                                    else:
                                        ligne.append("")
                                    indexColonne += 1
                                
                                # Unites
                                for date in listeDates :
                                    if dictDatesUnites.has_key(date) : 
                                        listeUnites = dictDatesUnites[date]
                                    
                                        for typeTemp, IDunite, affichage in dictChoixUnites[IDactivite] :
                                            if (affichage == "utilise" and IDunite in listeUnites) or affichage == "toujours" :
                                                listeLabels = []
                                                quantite = None
                                                
                                                styleConso = ParagraphStyle(name="label_conso", fontName="Helvetica", alignment=1, fontSize=6, leading=6, spaceBefore=0, spaceAfter=0, textColor=colors.black)
                                                styleEtiquette = ParagraphStyle(name="label_etiquette", fontName="Helvetica", alignment=1, fontSize=5, leading=5, spaceBefore=2, spaceAfter=0, textColor=colors.grey)    
                                                
                                                if typeTemp == "conso" :
                                                    # Unité de Conso
                                                    if dictIndividu["listeConso"].has_key(date) :
                                                        if dictIndividu["listeConso"][date].has_key(IDunite) :
                                                            typeUnite = dictUnites[IDunite]["type"]
                                                            
                                                            label = u""
                                                            for dictConsoTemp in dictIndividu["listeConso"][date][IDunite] :
                                                            
                                                                etat = dictConsoTemp["etat"]
                                                                heure_debut = dictConsoTemp["heure_debut"]
                                                                heure_fin = dictConsoTemp["heure_fin"]
                                                                quantite = dictConsoTemp["quantite"]
                                                                etiquettes = dictConsoTemp["etiquettes"]
                                                                
                                                                if typeUnite == "Unitaire" :
                                                                     label = u"X"
                                                                if typeUnite == "Horaire" :
                                                                    if heure_debut == None : heure_debut = "?"
                                                                    if heure_fin == None : heure_fin = "?"
                                                                    heure_debut = heure_debut.replace(":", "h")
                                                                    heure_fin = heure_fin.replace(":", "h")
                                                                    label = u"%s\n%s" % (heure_debut, heure_fin)
                                                                if typeUnite == "Multihoraires" :
                                                                    if heure_debut == None : heure_debut = "?"
                                                                    if heure_fin == None : heure_fin = "?"
                                                                    heure_debut = heure_debut.replace(":", "h")
                                                                    heure_fin = heure_fin.replace(":", "h")
                                                                    if len(label) > 0 : label += "\n"
                                                                    label += u"%s > %s" % (heure_debut, heure_fin)
                                                                if typeUnite == "Quantite" :
                                                                     label = str(quantite)
                                                
                                                                listeLabels.append(Paragraph(label, styleConso))
                                                
                                                                # Affichage de l'étiquette
                                                                if self.GetPage("options").checkbox_etiquettes.GetValue() == True and len(etiquettes) > 0 :
                                                                    texteEtiquette = []
                                                                    for IDetiquetteTemp in etiquettes :
                                                                        texteEtiquette.append(dictEtiquettes[IDetiquetteTemp]["label"])
                                                                    etiquette = "\n\n" + ", ".join(texteEtiquette)
                                                                    listeLabels.append(Paragraph(etiquette, styleEtiquette))
                                                    
                                                else:
                                                    # Unité de Remplissage
                                                    unitesLiees = dictUnitesRemplissage[IDunite]["unites"]
                                                    etiquettesUnitesRemplissage = dictUnitesRemplissage[IDunite]["etiquettes"]
                                                    for IDuniteLiee in unitesLiees :
                                                        if dictIndividu["listeConso"].has_key(date) :
                                                            if dictIndividu["listeConso"][date].has_key(IDuniteLiee) :
                                                                typeUnite = dictUnites[IDuniteLiee]["type"]
                                                                
                                                                for dictConsoTemp in dictIndividu["listeConso"][date][IDuniteLiee] :
                                                                    etat = dictConsoTemp["etat"]
                                                                    quantite = dictConsoTemp["quantite"]
                                                                    etiquettes = dictConsoTemp["etiquettes"]
                                                                    
                                                                    valide = True
                                                                    if len(etiquettesUnitesRemplissage) > 0 :
                                                                        valide = False
                                                                        for IDetiquetteTemp in etiquettesUnitesRemplissage :
                                                                            if IDetiquetteTemp in etiquettes :
                                                                                valide = True
                                                                                
                                                                    if valide == True :
                                                                        
                                                                        if quantite != None :
                                                                            label = str(quantite)
                                                                        else :
                                                                            label = u"X"

                                                                        listeLabels.append(Paragraph(label, styleConso))
                                                                
                                                                        # Affichage de l'étiquette
                                                                        if self.GetPage("options").checkbox_etiquettes.GetValue() == True and len(etiquettes) > 0 :
                                                                            texteEtiquette = []
                                                                            for IDetiquetteTemp in etiquettes :
                                                                                texteEtiquette.append(dictEtiquettes[IDetiquetteTemp]["label"])
                                                                                etiquette = "\n\n" + ", ".join(texteEtiquette)
                                                                            listeLabels.append(Paragraph(etiquette, styleEtiquette))
                                                

                                                if quantite == None :
                                                    quantite = 1
                                                    
                                                if len(listeLabels) > 0 :
                                                    if dictTotauxColonnes.has_key(indexColonne) == True :
                                                        dictTotauxColonnes[indexColonne] += quantite
                                                    else:
                                                        dictTotauxColonnes[indexColonne] = quantite
                                                ligne.append(listeLabels)
                                                indexColonne += 1
                                            
                                # Infos médicales
                                texteInfos = u""
                                listeInfos = []
                                paraStyle = ParagraphStyle(name="infos",
                                          fontName="Helvetica",
                                          fontSize=7,
                                          leading=8,
                                          spaceAfter=2,)
                                
                                # Mémo-journée
                                if dictMemos.has_key(IDindividu) :
                                    for date in listeDates :
                                        if dictMemos[IDindividu].has_key(date) :
                                            memo_journee = dictMemos[IDindividu][date]
                                            if typeListe == "period" : 
                                                memo_journee = u"%02d/%02d/%04d : %s" % (date.day, date.month, date.year, memo_journee)
                                            if len(memo_journee) > 0 and memo_journee[-1] != "." : memo_journee += u"."
                                            listeInfos.append(ParagraphAndImage(Paragraph(memo_journee, paraStyle), Image("Images/16x16/Information.png",width=8, height=8), xpad=1, ypad=0, side="left"))
                                
                                # Messages individuels
                                if dictMessagesIndividus.has_key(IDindividu):
                                    for dictMessage in dictMessagesIndividus[IDindividu] :
                                        texteMessage = dictMessage["texte"]
                                        listeInfos.append(ParagraphAndImage(Paragraph(texteMessage, paraStyle), Image("Images/16x16/Mail.png",width=8, height=8), xpad=1, ypad=0, side="left"))

                                # Récupère la liste des familles rattachées à cet individu
                                listeIDfamille = []
                                for date, dictUnitesTemps in dictIndividu["listeConso"].iteritems() :
                                    for temp, listeConso in dictUnitesTemps.iteritems() :
                                        for dictConsoTemp in listeConso :
                                            if dictConsoTemp["IDfamille"] not in listeIDfamille : 
                                                listeIDfamille.append(dictConsoTemp["IDfamille"])
                                
                                # Messages familiaux
                                for IDfamille in listeIDfamille :
                                    if dictMessagesFamilles.has_key(IDfamille):
                                        for dictMessage in dictMessagesFamilles[IDfamille] :
                                            texteMessage = dictMessage["texte"]
                                            listeInfos.append(ParagraphAndImage(Paragraph(texteMessage, paraStyle), Image("Images/16x16/Mail.png",width=8, height=8), xpad=1, ypad=0, side="left"))

                                # Cotisations manquantes
                                if self.GetPage("options").checkbox_cotisations_manquantes.GetValue() == True :
                                    for IDfamille in listeIDfamille :
                                        if dictCotisations.has_key(IDfamille):
                                            if dictCotisations[IDfamille]["nbre"] == 1 :
                                                texteCotisation = _(u"1 cotisation manquante : %s") % dictCotisations[IDfamille]["cotisations"]
                                            else:
                                                texteCotisation = _(u"%d cotisations manquantes : %s") % (dictCotisations[IDfamille]["nbre"], dictCotisations[IDfamille]["cotisations"])
                                            listeInfos.append(ParagraphAndImage(Paragraph(texteCotisation, paraStyle), Image("Images/16x16/Cotisation.png",width=8, height=8), xpad=1, ypad=0, side="left"))

                                # Pièces manquantes
                                if self.GetPage("options").checkbox_pieces_manquantes.GetValue() == True :
                                    for IDfamille in listeIDfamille :
                                        if dictPieces.has_key(IDfamille):
                                            if dictPieces[IDfamille]["nbre"] == 1 :
                                                textePiece = _(u"1 pièce manquante : %s") % dictPieces[IDfamille]["pieces"]
                                            else:
                                                textePiece = _(u"%d pièces manquantes : %s") % (dictPieces[IDfamille]["nbre"], dictPieces[IDfamille]["pieces"])
                                            listeInfos.append(ParagraphAndImage(Paragraph(textePiece, paraStyle), Image("Images/16x16/Piece.png",width=8, height=8), xpad=1, ypad=0, side="left"))
                                    
                                # Sieste
                                texte_sieste = dictIndividu["nomSieste"]
                                if texte_sieste != None and texte_sieste != "" : 
                                    if len(texte_sieste) > 0 and texte_sieste[-1] != "." : texte_sieste += u"."
                                    listeInfos.append(ParagraphAndImage(Paragraph(texte_sieste, paraStyle), Image("Images/16x16/Reveil.png",width=8, height=8), xpad=1, ypad=0, side="left"))
                                        
                                # Informations médicales
                                if dictInfosMedicales.has_key(IDindividu) :
                                    for infoMedicale in dictInfosMedicales[IDindividu] :
                                        intitule = infoMedicale["intitule"]
                                        description = infoMedicale["description"]
                                        traitement = infoMedicale["traitement_medical"]
                                        description_traitement = infoMedicale["description_traitement"]
                                        date_debut_traitement = infoMedicale["date_debut_traitement"]
                                        date_fin_traitement = infoMedicale["date_fin_traitement"]
                                        IDtype = infoMedicale["IDtype"]
                                        # Intitulé et description
                                        if description != None and description != "" :
                                            texte = u"<b>%s</b> : %s" % (intitule, description) # >
                                        else:
                                            texte = u"%s" % intitule # >
                                        if len(texte) > 0 and texte[-1] != "." : texte += u"."
                                        # Traitement médical
                                        if traitement == 1 and description_traitement != None and description_traitement != "" :
                                            texteDatesTraitement = u""
                                            if date_debut_traitement != None and date_fin_traitement != None : 
                                                texteDatesTraitement = _(u" du %s au %s") % (DateEngFr(date_debut_traitement), DateEngFr(date_fin_traitement))
                                            if date_debut_traitement != None and date_fin_traitement == None : 
                                                texteDatesTraitement = _(u" à partir du %s") % DateEngFr(date_debut_traitement)
                                            if date_debut_traitement == None and date_fin_traitement != None : 
                                                texteDatesTraitement = _(u" jusqu'au %s") % DateEngFr(date_fin_traitement)
                                            texte += _(u"Traitement%s : %s.") % (texteDatesTraitement, description_traitement)
                                        
                                        img = DICT_TYPES_INFOS[IDtype]["img"]
                                        listeInfos.append(ParagraphAndImage(Paragraph(texte, paraStyle), Image("Images/16x16/%s" % img,width=8, height=8), xpad=1, ypad=0, side="left"))
                                        
                                if self.GetPage("options").checkbox_infos.GetValue() == True :
                                    ligne.append(listeInfos)
                                else:
                                    ligne.append(u"")
                                
                                # Ajout de la ligne individuelle dans le tableau
                                dataTableau.append(ligne)
                                
                                # Mémorise les lignes pour export Excel
                                listeLignesExport.append(ligne)
                                
                            # Création des lignes vierges
                            if self.GetPage("options").checkbox_lignes_vierges.GetValue() == True :
                                for x in range(0, self.GetPage("options").ctrl_nbre_lignes.GetSelection()+1):
                                    ligne = []
                                    for col in labelsColonnes :
                                        ligne.append("") 
                                    dataTableau.append(ligne)
                                                    
                            # Style du tableau
                            colPremiereUnite = 1
                            if self.GetPage("options").checkbox_photos.GetValue() == True :
                                colPremiereUnite += 1
                            if self.GetPage("options").checkbox_age.GetValue() == True :
                                colPremiereUnite += 1
                            
                            style = [
                                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                                    ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                                    ('ALIGN', (0,0), (-2,-1), 'CENTRE'), # Centre les cases
                                    ('ALIGN', (0,0), (-1,0), 'CENTRE'), # Ligne de labels colonne alignée au centre
                                    ('FONT',(0,0),(-1,0), "Helvetica", 6), # Donne la police de caract. + taille de police des labels
                                    ]
                            
                            # Formatage de la ligne DATES
                            if typeListe == "period" :
                                style.append( ('BACKGROUND', (0, 0), (-1, 0), couleur_fond_titre) )
                                style.append( ('GRID', (0, 1), (-1,-1), 0.25, colors.black) )
                                style.append( ('LINEBEFORE', (0,0), (0,0), 0.25, colors.black) )
                                style.append( ('LINEAFTER', (-1,0), (-1,0), 0.25, colors.black) )
                                style.append( ('ALIGN', (0, 1), (-1, 1), 'CENTRE') )
                                style.append( ('FONT',(0,0),(-1,0), "Helvetica-Bold", 8) )
                                for date, positionG, positionD in listePositionsDates :
                                    style.append( ('SPAN', (positionG, 0), (positionD, 0) ) )
                                    style.append( ('BACKGROUND', (positionG, 0), (positionD, 0), (1, 1, 1)) )
                                    style.append( ('BOX', (positionG, 0), (positionD, -1), 1, colors.black) ) # Entoure toutes les colonnes Dates
                            else:
                                style.append( ('GRID', (0,0), (-1,-1), 0.25, colors.black) )
                            
                            # Vérifie si la largeur du tableau est inférieure à la largeur de la page
                            if modeExport == False :
                                largeurTableau = 0
                                for largeur in largeursColonnes :
                                    if largeur < 0 :
                                        dlg = wx.MessageDialog(self, _(u"Il y a trop de colonnes dans le tableau ! \n\nVeuillez sélectionner moins de jours dans le calendrier..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                                        dlg.ShowModal()
                                        dlg.Destroy()
                                        return False
                            
                            # Création du tableau
                            if typeListe == "period" :
                                repeatRows = 2
                            else :
                                repeatRows = 1
                            tableau = Table(dataTableau, largeursColonnes, repeatRows=repeatRows)
                            tableau.setStyle(TableStyle(style))
                            story.append(tableau)
                            
                            # Création du tableau des totaux
                            if self.GetPage("options").checkbox_photos.GetValue() == True :
                                colNomsIndividus = 1
                            else:
                                colNomsIndividus = 0
                                
                            ligne = []
                            indexCol = 0
                            for indexCol in range(0, len(labelsColonnes)) :
                                if dictTotauxColonnes.has_key(indexCol) :
                                    valeur = dictTotauxColonnes[indexCol]
                                else:
                                    valeur = ""
                                if indexCol == colNomsIndividus : 
                                    if len(listeIndividus) == 1 :
                                        valeur = _(u"1 individu")
                                    else:
                                        valeur = _(u"%d individus") % len(listeIndividus)
                                ligne.append(valeur)     
                            listeLignesExport.append(ligne)               
                            
                            style = [
                                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                                    ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                                    ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Centre les cases
                                    ('GRID', (colPremiereUnite,-1), (-2,-1), 0.25, colors.black),
                                    ('BACKGROUND', (colPremiereUnite,-1), (-2,-1), couleur_fond_titre), 
                                    ]
                                    
                            if typeListe == "period" :
                                for date, positionG, positionD in listePositionsDates :
                                    style.append( ('BOX', (positionG, 0), (positionD, 0), 1, colors.black) ) # Entoure toutes les colonnes Dates

                            tableau = Table([ligne,], largeursColonnes)
                            tableau.setStyle(TableStyle(style))
                            story.append(tableau)
                            
                            story.append(Spacer(0,20))
                            
                            # Export
                            listeExport.append({"activite":nomActivite, "groupe":nomGroupe, "ecole":nomEcole, "classe":nomClasse, "etiquette":nomEtiquette, "lignes":listeLignesExport})

                            # Saut de page après une étiquette
                            if self.GetPage("etiquettes").checkbox_etiquettes.GetValue() == True and self.GetPage("etiquettes").checkbox_saut_etiquettes.GetValue() == True :
                                CreationSautPage()
                            
                            
                        # Saut de page après une classe
                        if self.GetPage("scolarite").checkbox_ecoles.GetValue() == True and self.GetPage("scolarite").checkbox_saut_classes.GetValue() == True and indexClasse <= nbreClasses :
                            CreationSautPage()
                            
                        # Saut de page après une école
                        if self.GetPage("scolarite").checkbox_ecoles.GetValue() == True and self.GetPage("scolarite").checkbox_saut_ecoles.GetValue() == True :
                            IDecoleActuelle = None
                            IDecoleSuivante = None
                            if dictClasses.has_key(IDclasse) :
                                IDecoleActuelle = dictClasses[IDclasse]["IDecole"]
                                if indexClasse < nbreClasses :
                                    IDclasseSuivante = listeInfosClasses[indexClasse]["IDclasse"]
                                    if dictClasses.has_key(IDclasseSuivante) :
                                        IDecoleSuivante = dictClasses[IDclasseSuivante]["IDecole"]
                            if IDecoleActuelle != IDecoleSuivante :
                                CreationSautPage()
                            
                        indexClasse += 1


                    # Saut de page après un groupe
                    if self.GetPage("activites").checkbox_saut_groupes.GetValue() == True and indexGroupe < nbreGroupes :
                        CreationSautPage()
                    indexGroupe += 1
                    
            # Saut de page après une activité
            if self.GetPage("activites").checkbox_saut_activites.GetValue() == True and indexActivite < nbreActivites :
                CreationSautPage()
            indexActivite += 1

        # Suppression de la dernière page si elle est vide
        element = str(story[-3])
        if element == "PageBreak()" :
            story.pop(-1)
            story.pop(-1)
            story.pop(-1)
        
        # Suppression du dernier spacer s'il y en a un
        element = str(story[-1])
        if element == "Spacer(0, 20)" :
            story.pop(-1)
        
        if modeExport == True :
            return listeExport, largeursColonnes
        
        # Enregistrement et ouverture du PDF
        doc.build(story)
        FonctionsPerso.LanceFichierExterne(nomDoc)

    def TriClasses(self, listeClasses=[], dictEcoles={}):
        """ Tri des classes par nom d'école, par nom de classe et par niveau """
        listeResultats = []
        
        listeEcoles = []
        for IDecole, dictEcole in dictEcoles.iteritems() :
            listeEcoles.append((dictEcole["nom"], IDecole))
        listeEcoles.sort() 
        
        # Remplissage
        for nomEcole, IDecole in listeEcoles :
            listeClassesTemp = dictEcoles[IDecole]["classes"]
            listeClassesTemp.sort() 
            
            for listeOrdresNiveaux, nomClasse, txtNiveaux, IDclasse, date_debut, date_fin in listeClassesTemp :
                if IDclasse in listeClasses :
                    dictTemp = {"nomEcole":nomEcole, "nomClasse":nomClasse, "IDclasse":IDclasse, "date_debut":date_debut, "date_fin":date_fin}
                    listeResultats.append(dictTemp)
        
        return listeResultats

    def TriGroupes(self, listeGroupes=[], dictGroupes={}):
        """ Tri des groupes par ordre """
        listeTemp = []
        for IDgroupe in listeGroupes :
            ordre = dictGroupes[IDgroupe]["ordre"]
            listeTemp.append((ordre, IDgroupe))
        listeTemp.sort()
        listeResultat = []
        for ordre, IDgroupe in listeTemp :
            listeResultat.append(IDgroupe)
        return listeResultat
        
    def ImporterParametres(self):
        param_type = UTILS_Config.GetParametre("impression_conso_type_liste", defaut="journ")
        self.GetPage("unites").ctrl_unites.SetTypeListe(param_type)
        if param_type == "period" :
            self.radio_period.SetValue(True)
        
        param_tri = UTILS_Config.GetParametre("impression_conso_journ_tri", defaut=0)
        self.GetPage("options").ctrl_tri.Select(param_tri)
        
        param_ordre = UTILS_Config.GetParametre("impression_conso_journ_ordre", defaut=0)
        self.GetPage("options").ctrl_ordre.Select(param_ordre)
        
        param_lignes_vierges = UTILS_Config.GetParametre("impression_conso_journ_lignes_vierges", defaut=1)
        self.GetPage("options").checkbox_lignes_vierges.SetValue(param_lignes_vierges)
        
        if param_lignes_vierges == 1 :
            param_nbre_lignes_vierges = UTILS_Config.GetParametre("impression_conso_journ_nbre_lignes_vierges", defaut=2)
            self.GetPage("options").ctrl_nbre_lignes.Select(param_nbre_lignes_vierges)
            self.GetPage("options").OnCheckLignesVierges(None)
        
        param_age = UTILS_Config.GetParametre("impression_conso_journ_age", defaut=1)
        self.GetPage("options").checkbox_age.SetValue(param_age)
        
        param_infos = UTILS_Config.GetParametre("impression_conso_journ_infos", defaut=1)
        self.GetPage("options").checkbox_infos.SetValue(param_infos)

        param_etiquettes = UTILS_Config.GetParametre("impression_conso_journ_afficher_etiquettes", defaut=0)
        self.GetPage("options").checkbox_etiquettes.SetValue(param_etiquettes)
        
        param_cotisations = UTILS_Config.GetParametre("impression_conso_journ_cotisations", defaut=0)
        self.GetPage("options").checkbox_cotisations_manquantes.SetValue(param_cotisations)
        
        param_pieces = UTILS_Config.GetParametre("impression_conso_journ_pieces", defaut=0)
        self.GetPage("options").checkbox_pieces_manquantes.SetValue(param_pieces)

        param_tous_inscrits = UTILS_Config.GetParametre("impression_conso_journ_tous_inscrits", defaut=0)
        self.GetPage("options").checkbox_tous_inscrits.SetValue(param_tous_inscrits)
        
        param_photos = UTILS_Config.GetParametre("impression_conso_journ_photos", defaut=0)
        self.GetPage("options").checkbox_photos.SetValue(param_photos)
        
        param_taille_photos = UTILS_Config.GetParametre("impression_conso_journ_taille_photos", defaut=1)
        self.GetPage("options").ctrl_taille_photos.SetSelection(param_taille_photos)
        self.GetPage("options").OnCheckPhotos(None) 
        
        param_memoriser = UTILS_Config.GetParametre("impression_conso_journ_memoriser", defaut=1)
        self.ctrl_memoriser.SetValue(param_memoriser)
        
        active_couleur = UTILS_Config.GetParametre("impression_conso_journ_active_couleur", defaut=1)
        self.GetPage("options").checkbox_couleur.SetValue(active_couleur)
        if active_couleur == 1 :
            param_couleur = UTILS_Config.GetParametre("impression_conso_journ_couleur", defaut=COULEUR_FOND_TITRE)
            self.GetPage("options").ctrl_couleur.SetColour(param_couleur)
            self.GetPage("options").OnCheckCouleur(None) 
        
        self.GetPage("scolarite").checkbox_ecoles.SetValue(UTILS_Config.GetParametre("impression_conso_journ_ecoles", defaut=0))
        self.GetPage("etiquettes").checkbox_etiquettes.SetValue(UTILS_Config.GetParametre("impression_conso_journ_etiquettes", defaut=0))
        
        # Sauts de page
        self.GetPage("activites").checkbox_saut_activites.SetValue(UTILS_Config.GetParametre("impression_conso_journ_saut_activites", defaut=1))
        self.GetPage("activites").checkbox_saut_groupes.SetValue(UTILS_Config.GetParametre("impression_conso_journ_saut_groupes", defaut=1))
        self.GetPage("scolarite").checkbox_saut_ecoles.SetValue(UTILS_Config.GetParametre("impression_conso_journ_saut_ecoles", defaut=1))
        self.GetPage("scolarite").checkbox_saut_classes.SetValue(UTILS_Config.GetParametre("impression_conso_journ_saut_classes", defaut=1))
        self.GetPage("etiquettes").checkbox_saut_etiquettes.SetValue(UTILS_Config.GetParametre("impression_conso_journ_saut_etiquettes", defaut=1))
        
        self.GetPage("scolarite").OnCheckEcoles(None)
        self.GetPage("etiquettes").OnCheckEtiquettes(None)

    def MemoriserParametres(self):
        if self.ctrl_memoriser.GetValue() == True :
            UTILS_Config.SetParametre("impression_conso_type_liste", self.GetPage("unites").ctrl_unites.typeListe)
            UTILS_Config.SetParametre("impression_conso_journ_tri", self.GetPage("options").ctrl_tri.GetSelection())
            UTILS_Config.SetParametre("impression_conso_journ_ordre", self.GetPage("options").ctrl_ordre.GetSelection())
            UTILS_Config.SetParametre("impression_conso_journ_lignes_vierges", int(self.GetPage("options").checkbox_lignes_vierges.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_nbre_lignes_vierges", self.GetPage("options").ctrl_nbre_lignes.GetSelection())
            UTILS_Config.SetParametre("impression_conso_journ_age", int(self.GetPage("options").checkbox_age.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_infos", int(self.GetPage("options").checkbox_infos.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_afficher_etiquettes", int(self.GetPage("options").checkbox_etiquettes.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_cotisations", int(self.GetPage("options").checkbox_cotisations_manquantes.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_tous_inscrits", int(self.GetPage("options").checkbox_tous_inscrits.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_pieces", int(self.GetPage("options").checkbox_pieces_manquantes.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_photos", int(self.GetPage("options").checkbox_photos.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_taille_photos", int(self.GetPage("options").ctrl_taille_photos.GetSelection())) 
            UTILS_Config.SetParametre("impression_conso_journ_ecoles", int(self.GetPage("scolarite").checkbox_ecoles.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_saut_activites", int(self.GetPage("activites").checkbox_saut_activites.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_saut_groupes", int(self.GetPage("activites").checkbox_saut_groupes.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_saut_ecoles", int(self.GetPage("scolarite").checkbox_saut_ecoles.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_saut_classes", int(self.GetPage("scolarite").checkbox_saut_classes.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_etiquettes", int(self.GetPage("etiquettes").checkbox_etiquettes.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_saut_etiquettes", int(self.GetPage("etiquettes").checkbox_saut_etiquettes.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_active_couleur", int(self.GetPage("options").checkbox_couleur.GetValue()))
            UTILS_Config.SetParametre("impression_conso_journ_couleur", self.GetPage("options").ctrl_couleur.GetColour())
            self.GetPage("unites").ctrl_unites.MemoriseParametres()
        
        UTILS_Config.SetParametre("impression_conso_journ_memoriser", int(self.ctrl_memoriser.GetValue()))
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, date=datetime.date(2015, 10, 5))
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
