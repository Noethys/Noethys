#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED
import wx.lib.platebtn as platebtn
import FonctionsPerso
import sys
import operator
import os
import six

from Ctrl import CTRL_Calendrier
from Ctrl import CTRL_Photo
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Impression_conso_unites
from Ctrl import CTRL_Impression_conso_options
from Ctrl import CTRL_Profil

from Ol import OL_Impression_conso_colonnes

import GestionDB
from Utils import UTILS_Config
from Utils import UTILS_Organisateur
from Utils import UTILS_Cotisations_manquantes
from Utils import UTILS_Pieces_manquantes
from Data import DATA_Civilites as Civilites
from Ctrl import CTRL_Etiquettes
from Ctrl import CTRL_Evenements
from Utils import UTILS_Texte
from Utils import UTILS_Fichiers
from Utils import UTILS_Dates
from Utils import UTILS_Divers
from Utils import UTILS_Infos_individus

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import ParagraphAndImage, Image
from reportlab.rl_config import defaultPageSize
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import code39

COULEUR_FOND_TITRE = (204, 204, 255) # version PDF : (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)

DICT_CIVILITES = Civilites.GetDictCivilites()


def FormateCondition(listeDonnees=[]):
    if len(listeDonnees) == 0:
        condition = "()"
    elif len(listeDonnees) == 1:
        condition = "(%d)" % listeDonnees[0]
    else:
        condition = str(tuple(listeDonnees))
    return condition


class CTRL_profil_perso(CTRL_Profil.CTRL):
    def __init__(self, parent, categorie="", dlg=None):
        CTRL_Profil.CTRL.__init__(self, parent, categorie=categorie)
        self.dlg = dlg

    def Envoyer_parametres(self, dictParametres={}):
        """ Envoi des param�tres du profil s�lectionn� � la fen�tre """
        self.dlg.SetParametres(dictParametres)

    def Recevoir_parametres(self):
        """ R�cup�ration des param�tres pour la sauvegarde du profil """
        dictParametres = self.dlg.GetParametres()
        self.Enregistrer(dictParametres)




class CTRL_Cocher(platebtn.PlateButton):
    def __init__(self, parent, ctrl_liste=None):
        platebtn.PlateButton.__init__(self, parent, -1, u" Cocher", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_ANY))
        self.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour cocher ou d�cocher rapidement tous les �l�ments de cette liste")))
        self.ctrl_liste = ctrl_liste
        self.SetBackgroundColour(wx.WHITE)

        menu = UTILS_Adaptations.Menu()
        item = wx.MenuItem(menu, 10, u"Tout cocher", u"Cliquez ici pour cocher tous les �l�ments de la liste")
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_ANY))
        menu.AppendItem(item)
        item = wx.MenuItem(menu, 20, u"Tout d�cocher", u"Cliquez ici pour d�cocher tous les �l�ments de la liste")
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Decocher.png"), wx.BITMAP_TYPE_ANY))
        menu.AppendItem(item)
        self.SetMenu(menu)

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCocher, self)
        self.Bind(wx.EVT_MENU, self.OnMenu)

    def OnBoutonCocher(self, event):
        self.ShowMenu()

    def OnMenu(self, event):
        ID = event.GetId()
        # Tout cocher
        if ID == 10 :
            self.ctrl_liste.CocheListeTout()
        # Tout d�cocher
        if ID == 20:
            self.ctrl_liste.CocheListeRien()

















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
        
        self.SetToolTip(wx.ToolTip(_(u"Cochez les activit�s et groupes � afficher")))
        
        # Cr�ation des colonnes
        self.AddColumn(_(u"Activit�/groupe"))
        self.SetColumnWidth(0, 220)

        # Binds
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
        
    def Cocher(self, etat=True):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            self.CheckItem(item, etat)
        self.MAJenCours = False

    def CocheListeTout(self):
        self.Cocher(True)

    def CocheListeRien(self):
        self.Cocher(False)

    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            # Active ou non les branches enfants
            if self.GetPyData(item)["type"] == "activite" :
                if self.IsItemChecked(item) :
                    self.EnableChildren(item, True)
                else:
                    self.EnableChildren(item, False)
            # Envoie les donn�es aux contr�le parent
            listeActivites = self.GetListeActivites()
            self.GetGrandParent().GetParent().SetUnites(listeActivites)

    def SetDates(self, listeDates=[]):
        self.listeDates = listeDates
        self.MAJ() 

    def MAJ(self):
        """ Met � jour (redessine) tout le contr�le """
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

        # R�cup�ration des activit�s disponibles le jour s�lectionn�
        DB = GestionDB.DB()
        req = """SELECT 
        activites.IDactivite, activites.nom, activites.abrege, date_debut, date_fin,
        groupes.IDgroupe, groupes.nom, groupes.ordre
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = ouvertures.IDgroupe
        WHERE ouvertures.date IN %s
        GROUP BY groupes.IDgroupe, activites.IDactivite
        ORDER BY groupes.ordre;""" % conditionDates
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDactivite, nom, abrege, date_debut, date_fin, IDgroupe, nomGroupe, ordreGroupe in listeDonnees :
            if date_debut != None : date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            
            # M�morisation de l'activit� et du groupe
            if (IDactivite in dictActivites) == False :
                dictActivites[IDactivite] = { "nom":nom, "abrege":abrege, "date_debut":date_debut, "date_fin":date_fin, "groupes":[]}
            
            if (IDgroupe in dictGroupes) == False :
                dictGroupes[IDgroupe] = {"nom" : nomGroupe, "IDactivite" : IDactivite, "ordre":ordreGroupe}
                
            dictActivites[IDactivite]["groupes"].append({"IDgroupe":IDgroupe, "nom":nomGroupe, "ordre":ordreGroupe})
            
        return dictActivites, dictGroupes

    def Remplissage(self):
        # Tri des activit�s par nom
        listeActivites = []
        for IDactivite, dictActivite in self.dictActivites.items() :
            listeActivites.append((dictActivite["nom"], IDactivite))
        listeActivites.sort() 
        
        # Remplissage
        for nomActivite, IDactivite in listeActivites :
            dictActivite = self.dictActivites[IDactivite]
            
            # Niveau Activit�
            niveauActivite = self.AppendItem(self.root, nomActivite, ct_type=1)
            self.SetPyData(niveauActivite, {"type" : "activite", "ID" : IDactivite, "nom" : nomActivite})
            self.SetItemBold(niveauActivite, True)
            
            # Niveau Groupes
            for dictGroupe in dictActivite["groupes"] :
                if dictGroupe["IDgroupe"] != None :
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
        self.regroupement = None
        self.MAJenCours = False
        self.dictNiveaux = self.ImportationNiveaux() 
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.EnableSelectionVista(True)
        
        self.SetToolTip(wx.ToolTip(_(u"Cochez les �coles et classes � afficher")))
        
        # Cr�ation des colonnes
        self.AddColumn(_(u"Ecole/classe"))
        self.SetColumnWidth(0, 420)

        # Binds
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 

    def Cocher(self, etat=True):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            self.CheckItem(item, etat)
        self.MAJenCours = False

    def CocheListeTout(self):
        self.Cocher(True)

    def CocheListeRien(self):
        self.Cocher(False)

    def Activation(self, etat=True):
        """ Active ou d�sactive le contr�le """
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

    def SetRegroupement(self, regroupement=None):
        self.regroupement = regroupement
        self.MAJ()

    def MAJ(self):
        """ Met � jour (redessine) tout le contr�le """
        self.dictEcoles, self.dictClasses = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False


    def Importation(self):
        # R�cup�re les dates s�lectionn�es
        dictEcoles = {}
        dictClasses = {}
        if self.regroupement == None or self.listeDates == None or len(self.listeDates) == 0 :
            return dictEcoles, dictClasses

        self.listeDates.sort()
        date_min = min(self.listeDates)
        date_max = max(self.listeDates)

        # R�cup�ration des �l�ves
        DB = GestionDB.DB()
        req = """SELECT scolarite.IDindividu, ecoles.IDecole, ecoles.nom,
        classes.IDclasse, classes.nom, classes.date_debut, classes.date_fin, classes.niveaux
        FROM scolarite 
        LEFT JOIN ecoles ON ecoles.IDecole = scolarite.IDecole
        LEFT JOIN classes ON classes.IDclasse = scolarite.IDclasse
        WHERE scolarite.date_debut<='%s' AND scolarite.date_fin>='%s'
        ;""" % (date_max, date_min)
        DB.ExecuterReq(req)
        listeEtapes = DB.ResultatReq()
        DB.Close()
        for IDindividu, IDecole, ecole_nom, IDclasse, classe_nom, classe_debut, classe_fin, niveaux in listeEtapes :
            if classe_debut != None : classe_debut = UTILS_Dates.DateEngEnDateDD(classe_debut)
            if classe_fin != None : classe_fin = UTILS_Dates.DateEngEnDateDD(classe_fin)

            # Formatage des niveaux
            listeNiveaux = []
            listeOrdresNiveaux = []
            txtNiveaux = u""
            if niveaux != None and niveaux != "" and niveaux != " " :
                listeTemp = niveaux.split(";")
                txtTemp = []
                for niveau in listeTemp :
                    IDniveau = int(niveau)
                    if IDniveau in self.dictNiveaux :
                        nomNiveau = self.dictNiveaux[IDniveau]["abrege"]
                        ordreNiveau = self.dictNiveaux[IDniveau]["ordre"]
                        listeNiveaux.append(IDniveau)
                        txtTemp.append(nomNiveau)
                        listeOrdresNiveaux.append(ordreNiveau)
                txtNiveaux = ", ".join(txtTemp)

            # M�morisation de l'�cole
            if (IDecole in dictEcoles) == False:
                dictEcoles[IDecole] = {"nom": ecole_nom, "classes": []}

            if IDclasse != None and self.regroupement == "classe" :

                # M�morisation de la classe dans le dictEcoles
                donnees = (listeOrdresNiveaux, classe_nom, txtNiveaux, IDclasse, classe_debut, classe_fin)
                if donnees not in dictEcoles[IDecole]["classes"] :
                    dictEcoles[IDecole]["classes"].append(donnees)

                # M�morisation dans le dictClasses
                if (IDclasse in dictClasses) == False:
                    dictClasses[IDclasse] = {"nom": classe_nom, "IDecole": IDecole, "date_debut": classe_debut, "date_fin": classe_fin, "txtNiveaux": txtNiveaux}

        return dictEcoles, dictClasses


    def Remplissage(self):
        # Tri des �coles par nom
        listeEcoles = []
        for IDecole, dictEcole in self.dictEcoles.items() :
            listeEcoles.append((dictEcole["nom"], IDecole))
        listeEcoles.sort() 
        
        # Remplissage
        for nomEcole, IDecole in listeEcoles :
            dictEcole = self.dictEcoles[IDecole]

            if self.regroupement == "ecole" or (self.regroupement == "classe" and len(dictEcole["classes"]) > 0) :

                # Niveau Ecole
                niveauEcole = self.AppendItem(self.root, nomEcole, ct_type=1)
                self.SetPyData(niveauEcole, {"type" : "ecole", "ID" : IDecole, "nom" : nomEcole})
                self.SetItemBold(niveauEcole, True)
                self.CheckItem(niveauEcole)

                # Niveau Classes
                listeClasses = dictEcole["classes"]
                if len(listeClasses) > 0 :
                    listeClasses.sort()
                    for listeOrdresNiveaux, nomClasse, txtNiveaux, IDclasse, date_debut, date_fin in listeClasses :
                        nomSaison = _(u"Du %s au %s") % (UTILS_Dates.DateEngFr(str(date_debut)), UTILS_Dates.DateEngFr(str(date_fin)) )
                        labelClasse = u"%s (%s)" % (nomClasse, nomSaison)
                        niveauClasse = self.AppendItem(niveauEcole, labelClasse, ct_type=1)
                        self.SetPyData(niveauClasse, {"type" : "classe", "ID" : IDclasse, "nom" : nomClasse})

                    # Coche toutes les branches enfants
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
        self.checkbox_saut_activites = wx.CheckBox(self, -1, _(u"Apr�s l'activit�"))
        self.checkbox_saut_groupes = wx.CheckBox(self, -1, _(u"Apr�s le groupe"))
        
        # Propri�t�s
        self.checkbox_saut_activites.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour ins�rer un saut de page apr�s chaque activit�")))
        self.checkbox_saut_groupes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour ins�rer un saut de page apr�s chaque groupe")))
        self.ctrl_cocher = CTRL_Cocher(self, ctrl_liste=self.ctrl_activites)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_activites, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=2, hgap=5)
        grid_sizer_options.Add(self.label_saut_activites, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_activites, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_groupes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_cocher, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        dictParametres = {}
        dictParametres["saut_activites"] = int(self.checkbox_saut_activites.GetValue())
        dictParametres["saut_groupes"] = int(self.checkbox_saut_groupes.GetValue())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        if dictParametres == None :
            self.checkbox_saut_activites.SetValue(True)
            self.checkbox_saut_groupes.SetValue(True)
        else :
            if "saut_activites" in dictParametres : self.checkbox_saut_activites.SetValue(dictParametres["saut_activites"])
            if "saut_groupes" in dictParametres : self.checkbox_saut_groupes.SetValue(dictParametres["saut_groupes"])

# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Scolarite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.label_regroupement = wx.StaticText(self, -1, _(u"Regrouper par :"))
        self.checkbox_ecoles = wx.CheckBox(self, -1, _(u"Ecole"))
        self.checkbox_classes = wx.CheckBox(self, -1, _(u"Classe"))
        self.checkbox_inconnus = wx.CheckBox(self, -1, _(u"Afficher scolarit� inconnue"))
        self.ctrl_ecoles = CTRL_Ecoles(self)
        self.ctrl_ecoles.SetMinSize((380, 50))

        self.label_saut_ecoles = wx.StaticText(self, -1, _(u"Sauts de page :"))
        self.checkbox_saut_ecoles = wx.CheckBox(self, -1, _(u"Apr�s l'�cole"))
        self.checkbox_saut_classes = wx.CheckBox(self, -1, _(u"Apr�s la classe"))
        self.ctrl_cocher = CTRL_Cocher(self, ctrl_liste=self.ctrl_ecoles)

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEcoles, self.checkbox_ecoles)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckClasses, self.checkbox_classes)

        # Propri�t�s
        self.checkbox_ecoles.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour regrouper les individus par �cole ")))
        self.checkbox_classes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour regrouper les individus par classe")))
        self.checkbox_inconnus.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les individus dont la scolarit� est inconnue")))
        self.checkbox_saut_ecoles.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour ins�rer un saut de page apr�s chaque �cole")))
        self.checkbox_saut_classes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour ins�rer un saut de page apr�s chaque classe")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=10)

        grid_sizer_regroupement = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=5)
        grid_sizer_regroupement.Add(self.label_regroupement, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_regroupement.Add(self.checkbox_ecoles, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_regroupement.Add(self.checkbox_classes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_regroupement.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_regroupement.Add(self.checkbox_inconnus, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_regroupement.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_regroupement, 0, wx.EXPAND, 0)

        grid_sizer_base.Add(self.ctrl_ecoles, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=2, hgap=5)
        grid_sizer_options.Add(self.label_saut_ecoles, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_ecoles, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_classes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add((5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_cocher, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer_base)
        self.Layout()
        
        self.OnCheckEcoles(None)

    def GetRegroupement(self):
        return self.ctrl_ecoles.regroupement

    def GetAfficherInconnus(self):
        return self.checkbox_inconnus.GetValue()

    def OnCheckEcoles(self, event=None):
        self.OnCheck(self.checkbox_ecoles.GetValue(), "ecole")

    def OnCheckClasses(self, event=None):
        self.OnCheck(self.checkbox_classes.GetValue(), "classe")

    def OnCheck(self, etat=False, case=None):
        if case == "ecole" :
            self.checkbox_classes.SetValue(False)
            self.checkbox_classes.Enable(not etat)
            self.checkbox_saut_classes.Enable(False)
        elif case == "classe" :
            self.checkbox_ecoles.SetValue(False)
            self.checkbox_ecoles.Enable(not etat)
            self.checkbox_saut_classes.Enable(etat)
        else :
            self.checkbox_classes.Enable(not etat)
            self.checkbox_ecoles.Enable(not etat)
            self.checkbox_saut_classes.Enable(etat)
        self.ctrl_ecoles.Activation(etat)
        self.label_saut_ecoles.Enable(etat)
        self.checkbox_saut_ecoles.Enable(etat)
        self.ctrl_cocher.Enable(etat)
        if etat == True :
            self.ctrl_ecoles.SetRegroupement(case)
        else :
            self.ctrl_ecoles.SetRegroupement(None)

    def GetParametres(self):
        dictParametres = {}
        if self.checkbox_ecoles.GetValue() == True :
            dictParametres["regroupement_ecoles"] = "ecole"
        elif self.checkbox_classes.GetValue() == True :
            dictParametres["regroupement_ecoles"] = "classe"
        else :
            dictParametres["regroupement_ecoles"] = None
        dictParametres["scolarite_inconnue"] = int(self.checkbox_inconnus.GetValue())
        dictParametres["saut_ecoles"] = int(self.checkbox_saut_ecoles.GetValue())
        dictParametres["saut_classes"] = int(self.checkbox_saut_classes.GetValue())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        self.checkbox_ecoles.SetValue(False)
        self.checkbox_classes.SetValue(False)
        self.OnCheck(False)

        if dictParametres == None :
            self.checkbox_saut_ecoles.SetValue(True)
            self.checkbox_saut_classes.SetValue(True)
            self.checkbox_inconnus.SetValue(False)
        else :
            if "regroupement_ecoles" in dictParametres :
                if dictParametres["regroupement_ecoles"] in (1, "classe") :
                    self.checkbox_classes.SetValue(True)
                    self.OnCheck(True, "classe")
                if dictParametres["regroupement_ecoles"] == "ecole" :
                    self.checkbox_ecoles.SetValue(True)
                    self.OnCheck(True, "ecole")

            if "scolarite_inconnue" in dictParametres :
                self.checkbox_inconnus.SetValue(dictParametres["scolarite_inconnue"])
            else :
                self.checkbox_inconnus.SetValue(False)
            if "saut_ecoles" in dictParametres : self.checkbox_saut_ecoles.SetValue(dictParametres["saut_ecoles"])
            if "saut_classes" in dictParametres : self.checkbox_saut_classes.SetValue(dictParametres["saut_classes"])

# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Evenements(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.checkbox_evenements = wx.CheckBox(self, -1, _(u"Regrouper par �v�nement"))
        self.ctrl_evenements = CTRL_Evenements.CTRL(self, activeMenu=False, activeCheck=True, onCheck=None)
        self.ctrl_evenements.SetMinSize((250, 50))
        self.label_saut_evenements = wx.StaticText(self, -1, _(u"Sauts de page :"))
        self.checkbox_saut_evenements = wx.CheckBox(self, -1, _(u"Apr�s l'�v�nement"))
        self.ctrl_cocher = CTRL_Cocher(self, ctrl_liste=self.ctrl_evenements)

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEvenements, self.checkbox_evenements)

        # Propri�t�s
        self.checkbox_evenements.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour regrouper les consommations par �v�nement")))
        self.checkbox_saut_evenements.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour ins�rer un saut de page apr�s chaque �v�nement")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=10)

        grid_sizer_base.Add(self.checkbox_evenements, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_evenements, 1, wx.EXPAND, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=5)
        grid_sizer_options.Add(self.label_saut_evenements, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_evenements, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add((5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_cocher, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer_base)
        self.Layout()

        self.OnCheckEvenements(None)

    def OnCheckEvenements(self, event=None):
        if self.checkbox_evenements.GetValue() == True:
            etat = True
        else:
            etat = False
        self.ctrl_evenements.Activation(etat)
        self.label_saut_evenements.Enable(etat)
        self.checkbox_saut_evenements.Enable(etat)
        self.ctrl_cocher.Enable(etat)

    def GetParametres(self):
        dictParametres = {}
        dictParametres["regroupement_evenements"] = int(self.checkbox_evenements.GetValue())
        dictParametres["saut_evenements"] = int(self.checkbox_saut_evenements.GetValue())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        if dictParametres == None:
            self.checkbox_evenements.SetValue(False)
            self.checkbox_saut_evenements.SetValue(True)
        else:
            if "regroupement_evenements" in dictParametres: self.checkbox_evenements.SetValue(dictParametres["regroupement_evenements"])
            if "saut_evenements" in dictParametres: self.checkbox_saut_evenements.SetValue(dictParametres["saut_evenements"])
        self.OnCheckEvenements()

        # -----------------------------------------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Etiquettes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.checkbox_etiquettes = wx.CheckBox(self, -1, _(u"Regrouper par �tiquette"))
        self.ctrl_etiquettes = CTRL_Etiquettes.CTRL(self, activeMenu=False, onCheck=None)
        self.ctrl_etiquettes.SetMinSize((250, 50))
        self.label_saut_etiquettes = wx.StaticText(self, -1, _(u"Sauts de page :"))
        self.checkbox_saut_etiquettes = wx.CheckBox(self, -1, _(u"Apr�s l'�tiquette"))
        self.ctrl_cocher = CTRL_Cocher(self, ctrl_liste=self.ctrl_etiquettes)

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEtiquettes, self.checkbox_etiquettes)
        
        # Propri�t�s
        self.checkbox_etiquettes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour regrouper les consommations par �tiquette")))
        self.checkbox_saut_etiquettes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour ins�rer un saut de page apr�s chaque �tiquette")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=10)
        
        grid_sizer_base.Add(self.checkbox_etiquettes, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_etiquettes, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=5)
        grid_sizer_options.Add(self.label_saut_etiquettes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.checkbox_saut_etiquettes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add((5, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_cocher, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer_base)
        self.Layout()
        
        self.OnCheckEtiquettes(None) 
        
    def OnCheckEtiquettes(self, event=None):
        if self.checkbox_etiquettes.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_etiquettes.Activation(etat)
        self.label_saut_etiquettes.Enable(etat)
        self.checkbox_saut_etiquettes.Enable(etat)
        self.ctrl_cocher.Enable(etat)

    def GetParametres(self):
        dictParametres = {}
        dictParametres["regroupement_etiquettes"] = int(self.checkbox_etiquettes.GetValue())
        dictParametres["saut_etiquettes"] = int(self.checkbox_saut_etiquettes.GetValue())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        if dictParametres == None :
            self.checkbox_etiquettes.SetValue(False)
            self.checkbox_saut_etiquettes.SetValue(True)
        else :
            if "regroupement_etiquettes" in dictParametres : self.checkbox_etiquettes.SetValue(dictParametres["regroupement_etiquettes"])
            if "saut_etiquettes" in dictParametres : self.checkbox_saut_etiquettes.SetValue(dictParametres["saut_etiquettes"])
        self.OnCheckEtiquettes()

# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Unites(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_unites = CTRL_Impression_conso_unites.CTRL(self)
        self.ctrl_unites.SetMinSize((250, 50))
        self.ctrl_unites.MAJ() 

        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Descendre, self.bouton_descendre)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Reinit, self.bouton_reinit)
        
        # Propri�t�s
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter l'unit� s�lectionn�e dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre l'unit� s�lectionn�e dans la liste")))
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour r�initialiser la liste compl�te des unit�s")))

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
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        dictParametres = {}
        dictParametres["unites"] = self.ctrl_unites.GetParametres()
        return dictParametres

    def SetParametres(self, dictParametres={}):
        self.ctrl_unites.SetParametres(dictParametres)

# -----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Colonnes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_colonnes = OL_Impression_conso_colonnes.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_colonnes.SetMinSize((50, 50))
        self.ctrl_colonnes.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Descendre, self.bouton_descendre)

        # Propri�t�s
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une colonne personnalis�e")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la colonne s�lectionn�e dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la colonne s�lectionn�e dans la liste")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter la colonne s�lectionn�e dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre la colonne s�lectionn�e dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_colonnes, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        return self.ctrl_colonnes.GetParametres()

    def SetParametres(self, dictParametres={}):
        self.ctrl_colonnes.SetParametres(dictParametres)


# ----------------------------------------------------------------------------------------------------------------------------------------------

class Page_Options(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_options = CTRL_Impression_conso_options.CTRL(self)
        self.ctrl_options.SetMinSize((100, 50))

        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.Reinitialisation, self.bouton_reinit)

        # Propri�t�s
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour r�initialiser les options")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_options, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_reinit, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer_base)
        self.Layout()

    def Reinitialisation(self, event=None):
        self.ctrl_options.Reinitialisation()

    def GetParametres(self):
        return self.ctrl_options.GetParametres()

    def SetParametres(self, dictParametres={}):
        self.ctrl_options.SetParametres(dictParametres)



# ----------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style= wx.BK_DEFAULT | wx.NB_MULTILINE) 
        self.dictPages = {}

        self.listePages = [
            {"code" : "activites", "ctrl" : Page_Activites(self), "label" : _(u"Activit�s"), "image" : "Activite.png"},
            {"code" : "scolarite", "ctrl" : Page_Scolarite(self), "label" : _(u"Scolarit�"), "image" : "Classe.png"},
            {"code" : "evenements", "ctrl": Page_Evenements(self), "label": _(u"Ev�nements"), "image": "Evenement.png"},
            {"code" : "etiquettes", "ctrl" : Page_Etiquettes(self), "label" : _(u"Etiquettes"), "image" : "Etiquette.png"},
            {"code" : "unites", "ctrl" : Page_Unites(self), "label" : _(u"Unit�s"), "image" : "Tableau_colonne.png"},
            {"code" : "colonnes", "ctrl": Page_Colonnes(self), "label": _(u"Colonnes perso."), "image": "Tableau_colonne.png"},
            {"code" : "options", "ctrl" : Page_Options(self), "label" : _(u"Options"), "image" : "Options.png"},
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages :
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Cr�ation des pages
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
        """ Quand une page du notebook est s�lectionn�e """
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
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_conso", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.date = date
        
        intro = _(u"Vous pouvez ici imprimer une liste des consommations au format PDF. Pour une liste journali�re, s�lectionnez 'journali�re' puis une date dans le calendrier. Pour la liste d'une p�riode de dates continues ou non, s�lectionnez 'p�riodique' puis plusieurs dates (en appuyant sur les touches CTRL ou SHIFT) dans le calendrier.")
        titre = _(u"Impression d'une liste de consommations")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # Type de calendrier
        self.staticbox_type_staticbox = wx.StaticBox(self, -1, _(u"Type de liste"))
        self.radio_journ = wx.RadioButton(self, -1, _(u"Journali�re"), style=wx.RB_GROUP)
        self.radio_period = wx.RadioButton(self, -1, _(u"P�riodique"))
        
        # Calendrier
        self.staticbox_date_staticbox = wx.StaticBox(self, -1, _(u"Date"))
        self.ctrl_calendrier = PANEL_Calendrier(self)
        self.ctrl_calendrier.SetMinSize((250, 80)) 
                
        # Profil de configuration
        self.staticbox_profil_staticbox = wx.StaticBox(self, -1, _(u"Profil de configuration"))
        self.ctrl_profil = CTRL_profil_perso(self, categorie="impression_conso", dlg=self)

        # Param�tres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.ctrl_parametres = CTRL_Parametres(self) 

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_export = CTRL_Bouton_image.CTRL(self, texte=_(u"Export sous Excel"), cheminImage="Images/32x32/Excel.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aper�u"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioJourn, self.radio_journ)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriod, self.radio_period)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExport, self.bouton_export)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Active le mode du calendrier
        if self.radio_journ.GetValue() == True : self.OnRadioJourn(None)
        if self.radio_period.GetValue() == True : self.OnRadioPeriod(None)
        
        # S�lectionne la date par d�faut
        if self.date == None :
            self.SetDateDefaut(datetime.date.today())
        else:
            self.SetDateDefaut(self.date)

        # Init Contr�les
        self.bouton_ok.SetFocus()
        self.ctrl_profil.SetOnDefaut()
        
        self.__do_layout()

        wx.CallLater(1, self.ctrl_parametres.Refresh)

    def __set_properties(self):
        self.SetTitle(_(u"Impression d'une liste de consommations"))
        self.radio_journ.SetToolTip(wx.ToolTip(_(u"Cochez ici pour s�lectionner une liste journali�re")))
        self.radio_period.SetToolTip(wx.ToolTip(_(u"Cochez ici pour s�lectionner une liste p�riodique")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_export.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter les donn�es vers Excel")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((880, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Profil
        staticbox_profil = wx.StaticBoxSizer(self.staticbox_profil_staticbox, wx.VERTICAL)
        staticbox_profil.Add(self.ctrl_profil, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_gauche.Add(staticbox_profil, 1, wx.EXPAND, 0)

        # Calendrier
        staticbox_date = wx.StaticBoxSizer(self.staticbox_date_staticbox, wx.VERTICAL)
        staticbox_date.Add(self.ctrl_calendrier, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_date, 1, wx.EXPAND, 0)

        # Type
        staticbox_type = wx.StaticBoxSizer(self.staticbox_type_staticbox, wx.HORIZONTAL)
        staticbox_type.Add(self.radio_journ, 0, wx.ALL|wx.EXPAND, 5)
        staticbox_type.Add(self.radio_period, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_type, 1, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Param�tres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.HORIZONTAL)
        staticbox_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND | wx.ALL, 5)
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
        self.GetPage("unites").ctrl_unites.MAJ()
        self.staticbox_date_staticbox.SetLabel(_(u"Date"))
        
    def OnRadioPeriod(self, event):
        self.ctrl_calendrier.SetMultiSelection(True)
        self.GetPage("unites").ctrl_unites.MAJ()
        self.staticbox_date_staticbox.SetLabel(_(u"P�riode"))

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesconsommations")
    
    def SetDateDefaut(self, date=None):
        self.ctrl_calendrier.SetDates([date,])
        self.SetDates([date,]) 
        
    def SetDates(self, listeDates=[]):
        if listeDates == None : listeDates = []
        self.GetPage("activites").ctrl_activites.SetDates(listeDates)
        self.SetUnites(self.GetPage("activites").ctrl_activites.GetListeActivites())
        self.GetPage("scolarite").ctrl_ecoles.SetDates(listeDates)
        self.GetPage("evenements").ctrl_evenements.SetDates(listeDates=listeDates)
        self.GetPage("evenements").ctrl_evenements.SetCoches(tout=True)

    def SetUnites(self, listeActivites=[]):
        self.GetPage("unites").ctrl_unites.SetActivites(listeActivites)
        self.GetPage("etiquettes").ctrl_etiquettes.SetActivites(listeActivites)
        self.GetPage("etiquettes").ctrl_etiquettes.SetCoches(tout=True)
        self.GetPage("evenements").ctrl_evenements.SetActivites(listeActivites)
        self.GetPage("evenements").ctrl_evenements.SetCoches(tout=True)

    def GetAge(self, date_naiss=None):
        if date_naiss == None : return None
        datedujour = datetime.date.today()
        age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
        return age

    def OnClose(self, event):
        self.OnBoutonAnnuler(None)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonOk(self, event):
        self.Impression() 
    
    def OnBoutonExport(self, event=None):
        typeListe = self.GetTypeListe()
##        if typeListe != "journ" :
##            dlg = wx.MessageDialog(self, _(u"L'export sous Excel n'est disponible que pour le mode journalier !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
        
        donnees = self.Impression(modeExport=True) 
        if donnees == False :
            return
        listeExport, largeursColonnes = donnees
        
        # Demande � l'utilisateur le nom de fichier et le r�pertoire de destination
        nomFichier = "ExportExcel_%s.xlsx" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xlsx)|*.xlsx|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez s�lectionner le r�pertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.FD_SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe d�j� :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        import xlsxwriter
        classeur = xlsxwriter.Workbook(cheminFichier)

        numFeuille = 1
        for dictFeuille in listeExport :
            activite = dictFeuille["activite"]
            groupe = dictFeuille["groupe"]
            ecole = dictFeuille["ecole"]
            classe = dictFeuille["classe"]
            evenement = dictFeuille["evenement"]
            etiquette = dictFeuille["etiquette"]
            lignes = dictFeuille["lignes"]
            
            # Nom de la feuille
            titre = _(u"Page %d") % numFeuille
            feuille = classeur.add_worksheet(titre)
            
            # Titre de la page
            listeLabels = []
            if activite != None : listeLabels.append(activite)
            if groupe != None : listeLabels.append(groupe)
            if ecole != None : listeLabels.append(ecole)
            if classe != None : listeLabels.append(classe)
            if evenement != None : listeLabels.append(evenement)
            if etiquette != None: listeLabels.append(etiquette)
            titre = " - ".join(listeLabels)
            feuille.write(0, 0, titre)
            
            numLigne = 2
            for ligne in lignes :
                
                numColonne = 0
                for valeur in ligne :
                    # Si c'est un Paragraph
                    if isinstance(valeur, Paragraph) :
                        valeur = valeur.text
                    # Largeur colonne
                    if type(valeur) == six.text_type and (_(u"Nom - ") in valeur or valeur == "Informations") :
                        feuille.set_column(numColonne, numColonne, 50)
                    # Valeur case
                    if type(valeur) in (str, six.text_type, int) :
                        # Formatage des heures
                        if type(valeur) == six.text_type and len(valeur) == 11 and valeur[2] == "h" and valeur[8] == "h" :
                            valeur = valeur.replace(u"\n", u"-")
                        feuille.write(numLigne, numColonne, valeur)
                    # Si c'est une liste
                    if type(valeur) == list :
                        listeInfos = []
                        for element in valeur :
                            try :
                                valeur = element.text
                            except :
                                valeur = element.P.text
                            if valeur == "X":
                                valeur = "1"
                            listeInfos.append(valeur)
                        if len(listeInfos) == 1 and listeInfos[0] == "1" :
                            texte = int(valeur)
                        else :
                            texte = " - ".join(listeInfos)
                        feuille.write(numLigne, numColonne, texte)
                    
                    numColonne += 1
                numLigne += 1
            numFeuille += 1
            
        # Finalisation du fichier xlsx
        classeur.close()
        
        # Confirmation de cr�ation du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a �t� cr�� avec succ�s. Souhaitez-vous l'ouvrir d�s maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)


    def Impression(self, modeExport=False):
        # R�cup�ration des param�tres
        dictParametres = self.GetParametres()

        # V�rification des donn�es
        listeDates = self.ctrl_calendrier.GetDates()
        if listeDates == None : listeDates = []
        if len(listeDates) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner au moins une date !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        listeActivites = self.GetPage("activites").ctrl_activites.GetListeActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        listeGroupes = self.GetPage("activites").ctrl_activites.GetListeGroupes()
        if len(listeGroupes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un groupe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.GetPage("scolarite").GetRegroupement() in ("ecole", "classe") :

            listeEcoles = self.GetPage("scolarite").ctrl_ecoles.GetListeEcoles()
            if len(listeEcoles) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une �cole !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            listeClasses = self.GetPage("scolarite").ctrl_ecoles.GetListeClasses()
            if len(listeClasses) == 0 and self.GetPage("scolarite").GetRegroupement() == "classe" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une classe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        if self.GetPage("evenements").checkbox_evenements.GetValue() == True :
            listeEvenements = self.GetPage("evenements").ctrl_evenements.GetCoches()
            if len(listeEvenements) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un �v�nement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        if self.GetPage("etiquettes").checkbox_etiquettes.GetValue() == True :
            listeEtiquettes = self.GetPage("etiquettes").ctrl_etiquettes.GetCoches()
            if len(listeEtiquettes) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une �tiquette !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        dictChoixUnites = self.GetPage("unites").ctrl_unites.GetDonnees()
        if len(dictChoixUnites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner au moins une unit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        for IDactivite in listeActivites :
            valide = False
            listeUnitesTemp = dictChoixUnites[IDactivite]
            for typeTemp, IDunite, affichage in listeUnitesTemp :
                if affichage != "jamais" : valide = True
            if valide == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement avoir au moins une unit� � afficher pour chaque activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        typeListe = self.GetTypeListe()

        # Affiche la DLG d'attente
        DlgAttente = wx.BusyInfo(_(u"Recherche des donn�es..."), self)

        # Recherche des infos individuelles et familiales pour les colonnes perso
        if len(dictParametres["colonnes"]) >0 :
            infosIndividus = UTILS_Infos_individus.Informations(date_reference=listeDates[0], qf=True, inscriptions=True, messages=False, infosMedicales=False, cotisationsManquantes=False, piecesManquantes=False, questionnaires=True, scolarite=True)
            dictInfosIndividus = infosIndividus.GetDictValeurs(mode="individu", ID=None, formatChamp=False)
            dictInfosFamilles = infosIndividus.GetDictValeurs(mode="famille", ID=None, formatChamp=False)


        # R�cup�ration des autres donn�es dans la base
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

        # if self.GetPage("scolarite").checkbox_ecoles.GetValue() == True :
        #     if len(listeClasses) == 0 : conditionTemp = "()"
        #     elif len(listeClasses) == 1 : conditionTemp = "(%d)" % listeClasses[0]
        #     else : conditionTemp = str(tuple(listeClasses))
        #     conditionsScolarite = "AND (scolarite.IDclasse IN %s OR scolarite.IDclasse IS NULL)" % conditionTemp
        # else:
        #     conditionsScolarite = ""

        if self.GetPage("scolarite").GetRegroupement() == "ecole" :
            conditionsScolarite = "AND (scolarite.IDecole IN %s OR scolarite.IDecole IS NULL)" % FormateCondition(listeEcoles)
        elif self.GetPage("scolarite").GetRegroupement() == "classe" :
            conditionsScolarite = "AND (scolarite.IDclasse IN %s OR scolarite.IDclasse IS NULL)" % FormateCondition(listeClasses)
        else:
            conditionsScolarite = ""

        if self.GetPage("evenements").checkbox_evenements.GetValue() == True :
            conditionsEvenements = " AND consommations.IDevenement IN %s" % FormateCondition(listeEvenements)
        else :
            conditionsEvenements = ""

        # R�cup�ration de la liste des unit�s ouvertes ce jour
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
            date = UTILS_Dates.DateEngEnDateDD(date)
            if (IDactivite in dictOuvertures) == False : dictOuvertures[IDactivite] = {}
            if (IDgroupe in dictOuvertures[IDactivite]) == False : dictOuvertures[IDactivite][IDgroupe] = {}
            if (date in dictOuvertures[IDactivite][IDgroupe]) == False : dictOuvertures[IDactivite][IDgroupe][date] = []
            dictOuvertures[IDactivite][IDgroupe][date].append(IDunite)

##            if dictOuvertures.has_key(IDactivite) == False : dictOuvertures[IDactivite] = {}
##            if dictOuvertures[IDactivite].has_key(IDgroupe) == False : dictOuvertures[IDactivite][IDgroupe] = []
##            dictOuvertures[IDactivite][IDgroupe].append(IDunite)

        # R�cup�ration des infos sur les unit�s
        req = """SELECT IDunite, IDactivite, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin, ordre
        FROM unites;"""
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        dictUnites = {}
        for IDunite, IDactivite, nom, abrege, typeTemp, heure_debut, heure_fin, date_debut, date_fin, ordre in listeUnites :
            dictUnites[IDunite] = {"IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "type" : typeTemp, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre}

        req = """SELECT
        unites_remplissage.IDunite_remplissage, nom, abrege, etiquettes, heure_min, heure_max,
        unites_remplissage_unites.IDunite_remplissage_unite,
        unites_remplissage_unites.IDunite
        FROM unites_remplissage
        LEFT JOIN unites_remplissage_unites ON unites_remplissage.IDunite_remplissage = unites_remplissage_unites.IDunite_remplissage
        ;"""
        DB.ExecuterReq(req)
        listeUnitesRemplissage = DB.ResultatReq()
        dictUnitesRemplissage = {}
        for IDunite_remplissage, nom, abrege, etiquettes, heure_min, heure_max, IDunite_remplissage_unite, IDunite in listeUnitesRemplissage :
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
            if (IDunite_remplissage in dictUnitesRemplissage) == False :
                dictUnitesRemplissage[IDunite_remplissage] = {"nom" : nom, "abrege" : abrege, "etiquettes" : etiquettes, "heure_min" : heure_min, "heure_max" : heure_max, "unites" : [] }
            dictUnitesRemplissage[IDunite_remplissage]["unites"].append(IDunite)

        # R�cup�ration des noms des groupes
        dictGroupes = self.GetPage("activites").ctrl_activites.GetDictGroupes()

        # R�cup�ration des noms d'activit�s
        dictActivites = self.GetPage("activites").ctrl_activites.GetDictActivites()

        # R�cup�ration des noms des �coles
        dictEcoles = self.GetPage("scolarite").ctrl_ecoles.GetDictEcoles()

        # R�cup�ration des noms des classes
        dictClasses = self.GetPage("scolarite").ctrl_ecoles.GetDictClasses()

        # R�cup�ration des �v�nements
        dictEvenements = self.GetPage("evenements").ctrl_evenements.GetDictEvenements()

        # R�cup�ration des �tiquettes
        dictEtiquettes = self.GetPage("etiquettes").ctrl_etiquettes.GetDictEtiquettes()

        # R�cup�ration des consommations
        req = """SELECT IDconso, consommations.IDindividu, IDcivilite, consommations.IDactivite, IDunite, consommations.IDgroupe, heure_debut, heure_fin, consommations.etat, quantite, etiquettes, IDevenement,
        IDcivilite, individus.nom, prenom, date_naiss, types_sieste.nom, inscriptions.IDfamille, consommations.date, scolarite.IDecole, scolarite.IDclasse
        FROM consommations 
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN types_sieste ON types_sieste.IDtype_sieste = individus.IDtype_sieste
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        LEFT JOIN scolarite ON scolarite.IDindividu = consommations.IDindividu AND scolarite.date_debut <= consommations.date AND scolarite.date_fin >= consommations.date
        WHERE consommations.etat IN ("reservation", "present")
        AND inscriptions.statut='ok'
        AND consommations.IDactivite IN %s AND consommations.date IN %s %s %s
        ORDER BY consommations.date, consommations.heure_debut
        ;""" % (conditionActivites, conditionDates, conditionsScolarite, conditionsEvenements)
        DB.ExecuterReq(req)
        listeConso = DB.ResultatReq()
        dictConso = {}
        dictIndividus = {}
        listeIDindividus = []
        for IDconso, IDindividu, IDcivilite, IDactivite, IDunite, IDgroupe, heure_debut, heure_fin, etat, quantite, etiquettes, IDevenement, IDcivilite, nom, prenom, date_naiss, nomSieste, IDfamille, date, IDecole, IDclasse in listeConso :
            date = UTILS_Dates.DateEngEnDateDD(date)
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
            conso_IDevenement = IDevenement

            # Calcul de l'�ge
            if date_naiss != None : date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
            age = self.GetAge(date_naiss)

            # M�morisation de l'activit�
            if (IDactivite in dictConso) == False :
                dictConso[IDactivite] = {}

            # M�morisation du groupe
            if (IDgroupe in dictConso[IDactivite]) == False :
                dictConso[IDactivite][IDgroupe] = {}

            # M�morisation du regroupement de scolarit�
            regroupement_scolarite = self.GetPage("scolarite").GetRegroupement()
            if regroupement_scolarite == "ecole" :
                scolarite = IDecole
            elif regroupement_scolarite == "classe" :
                scolarite = IDclasse
            else :
                scolarite = None

            if (scolarite in dictConso[IDactivite][IDgroupe]) == False :
                dictConso[IDactivite][IDgroupe][scolarite] = {}

            # M�morisation de l'�v�nement
            if self.GetPage("evenements").checkbox_evenements.GetValue() == False :
                IDevenement = None

            if (IDevenement in dictConso[IDactivite][IDgroupe][scolarite]) == False :
                dictConso[IDactivite][IDgroupe][scolarite][IDevenement] = {}

            # M�morisation de l'�tiquette
            if self.GetPage("etiquettes").checkbox_etiquettes.GetValue() == False :
                listeEtiquettes = [None,]
            else :
                listeEtiquettes = etiquettes

            for IDetiquette in listeEtiquettes :

                if (IDetiquette in dictConso[IDactivite][IDgroupe][scolarite][IDevenement]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette] = {}

                # M�morisation de l'individu
                if (IDindividu in dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu] = { "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss, "age" : age, "nomSieste" : nomSieste, "listeConso" : {} }

                # M�morisation de la date
                if (date in dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu]["listeConso"]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu]["listeConso"][date] = {}

                # M�morisation de la consommation
                if (IDunite in dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu]["listeConso"][date]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu]["listeConso"][date][IDunite] = []

                dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu]["listeConso"][date][IDunite].append( { "heure_debut" : heure_debut, "heure_fin" : heure_fin, "etat" : etat, "quantite" : quantite, "IDfamille" : IDfamille, "IDevenement" : conso_IDevenement, "etiquettes" : etiquettes } )

                # M�morisation du IDindividu
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu)

                # Dict Individu
                dictIndividus[IDindividu] = { "IDcivilite" : IDcivilite, "IDfamille" : IDfamille }

        # Int�gration de tous les inscrits
        if dictParametres["afficher_inscrits"] == True :

            req = """SELECT individus.IDindividu, IDcivilite, individus.nom, prenom, date_naiss, types_sieste.nom, 
            inscriptions.IDactivite, inscriptions.IDgroupe, inscriptions.IDfamille, scolarite.IDecole, scolarite.IDclasse
            FROM individus 
            LEFT JOIN types_sieste ON types_sieste.IDtype_sieste = individus.IDtype_sieste
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            LEFT JOIN scolarite ON scolarite.IDindividu = individus.IDindividu AND scolarite.date_debut <= '%s' AND scolarite.date_fin >= '%s'
            WHERE inscriptions.statut='ok' AND inscriptions.IDactivite IN %s and (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s')
            ; """ % (min(listeDates), max(listeDates), conditionActivites, max(listeDates))
            DB.ExecuterReq(req)
            listeTousInscrits = DB.ResultatReq()
            for IDindividu, IDcivilite, nom, prenom, date_naiss, nomSieste, IDactivite, IDgroupe, IDfamille, IDecole, IDclasse in listeTousInscrits :

                # Calcul de l'�ge
                if date_naiss != None : date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
                age = self.GetAge(date_naiss)

                # M�morisation de l'activit�
                if (IDactivite in dictConso) == False :
                    dictConso[IDactivite] = {}

                # M�morisation du groupe
                if (IDgroupe in dictConso[IDactivite]) == False :
                    dictConso[IDactivite][IDgroupe] = {}

                # M�morisation du regroupement de scolarit�
                regroupement_scolarite = self.GetPage("scolarite").GetRegroupement()
                if regroupement_scolarite == "ecole":
                    scolarite = IDecole
                elif regroupement_scolarite == "classe":
                    scolarite = IDclasse
                else:
                    scolarite = None

                if (scolarite in dictConso[IDactivite][IDgroupe]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite] = {}

                IDevenement = None
                if (IDevenement in dictConso[IDactivite][IDgroupe][scolarite]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite][IDevenement] = {}

                IDetiquette = None
                if (IDetiquette in dictConso[IDactivite][IDgroupe][scolarite][IDevenement]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette] = {}

                # M�morisation de l'individu
                if (IDindividu in dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette]) == False :
                    dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu] = { "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss, "age" : age, "nomSieste" : nomSieste, "listeConso" : {} }

                # M�morisation du IDindividu
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu)

                # Dict Individu
                dictIndividus[IDindividu] = { "IDcivilite" : IDcivilite, "IDfamille" : IDfamille }

        # R�cup�ration des m�mo-journ�es
        req = """SELECT IDmemo, IDindividu, date, texte, couleur
        FROM memo_journee
        WHERE date IN %s
        ORDER BY date
        ; """ % conditionDates
        DB.ExecuterReq(req)
        listeMemos = DB.ResultatReq()
        dictMemos = {}
        for IDmemo, IDindividu, date, texte, couleur in listeMemos :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if (IDindividu in dictMemos) == False :
                dictMemos[IDindividu] = {}
            dictMemos[IDindividu][date] = {"texte": texte, "couleur": couleur}

        # R�cup�ration des photos individuelles
        dictPhotos = {}
        taillePhoto = 128
        if dictParametres["afficher_photos"] == "petite" : tailleImageFinal = 16
        if dictParametres["afficher_photos"] == "moyenne" : tailleImageFinal = 32
        if dictParametres["afficher_photos"] == "grande" : tailleImageFinal = 64
        if dictParametres["afficher_photos"] != "non" :
            for IDindividu in listeIDindividus :
                IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                nomFichier = Chemins.GetStaticPath("Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"])
                IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)

                # Cr�ation de la photo dans le r�pertoire Temp
                nomFichier = UTILS_Fichiers.GetRepTemp(fichier="photoTmp%d.jpg" % IDindividu)
                bmp.SaveFile(nomFichier, type=wx.BITMAP_TYPE_JPEG)
                img = Image(nomFichier, width=tailleImageFinal, height=tailleImageFinal)
                dictPhotos[IDindividu] = img

        # R�cup�ration des messages
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
            if IDindividu != None and (IDindividu in dictMessagesIndividus) == False : dictMessagesIndividus[IDindividu] = []
            if IDindividu != None : dictMessagesIndividus[IDindividu].append(dictTemp)
            # Si c'est un message individuel
            if IDfamille != None and (IDfamille in dictMessagesFamilles) == False : dictMessagesFamilles[IDfamille] = []
            if IDfamille != None : dictMessagesFamilles[IDfamille].append(dictTemp)

        # R�cup�ration de la liste des cotisations manquantes
        dictCotisations = UTILS_Cotisations_manquantes.GetListeCotisationsManquantes(dateReference=datetime.date.today(), listeActivites=listeActivites, presents=(min(listeDates), max(listeDates)), concernes=True)

        # R�cup�ration de la liste des pi�ces manquantes
        dictPieces = UTILS_Pieces_manquantes.GetListePiecesManquantes(dateReference=datetime.date.today(), listeActivites=listeActivites, presents=(min(listeDates), max(listeDates)), concernes=True)

        # R�cup�ration des informations m�dicales
        req = """SELECT IDprobleme, IDindividu, IDtype, intitule, description, traitement_medical, description_traitement, date_debut_traitement, date_fin_traitement
        FROM problemes_sante
        WHERE diffusion_listing_conso = 1
        AND date_debut <= '%s' AND date_fin >= '%s';""" % (min(listeDates), max(listeDates))
        DB.ExecuterReq(req)
        listeInfosMedicales = DB.ResultatReq()
        dictInfosMedicales = {}
        for IDprobleme, IDindividu, IDtype, intitule, description, traitement_medical, description_traitement, date_debut_traitement, date_fin_traitement in listeInfosMedicales :
            if (IDindividu in dictInfosMedicales) == False : dictInfosMedicales[IDindividu] = []
            dictTemp = {"IDtype":IDtype, "intitule":intitule, "description":description, "traitement_medical":traitement_medical, "description_traitement":description_traitement, "date_debut_traitement":date_debut_traitement, "date_fin_traitement":date_fin_traitement}
            dictInfosMedicales[IDindividu].append(dictTemp)

        DB.Close()

        # ---------------- Cr�ation du PDF -------------------

        couleur_fond_titre = UTILS_Divers.ConvertCouleurWXpourPDF(dictParametres["couleur_fond_titre"])
        couleur_fond_entetes = UTILS_Divers.ConvertCouleurWXpourPDF(dictParametres["couleur_fond_entetes"])
        couleur_fond_total = UTILS_Divers.ConvertCouleurWXpourPDF(dictParametres["couleur_fond_total"])

        # Orientation de la page
        if dictParametres["orientation"] == "automatique" :
            if typeListe == "journ" :
                orientation = "portrait"
            else:
                orientation = "paysage"
        else :
            orientation = dictParametres["orientation"]

        if orientation == "portrait" :
            hauteur_page = A4[1]
            largeur_page = A4[0]
        else:
            hauteur_page = A4[0]
            largeur_page = A4[1]

        margeG, margeD = 30, 30

        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_CONSO", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30)
        story = []

        largeurContenu = largeur_page - margeG - margeD

        # Font normale
        styleNormal = ParagraphStyle(name="normal", fontName="Helvetica", alignment=1, fontSize=7, leading=8)
        styleEntetes = ParagraphStyle(name="entetes", fontName="Helvetica", alignment=1, fontSize=6, leading=7)

        # Cr�ation du header du document
        def CreationTitreDocument():
            dataTableau = []
            largeursColonnes = ( (largeurContenu-100, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            if typeListe == "journ" :
                titre = _(u"Consommations du %s") % UTILS_Dates.DateComplete(min(listeDates))
            else:
                titre = _(u"Consommations")
            dataTableau.append((titre, _(u"%s\nEdit� le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)))
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

        # Cr�ation du titre des tableaux
        def CreationTitreTableau(nomActivite="", nomGroupe="", nomEcole="", nomClasse="", couleurFond=couleur_fond_titre, couleurTexte=colors.black, tailleGroupe=14):
            dataTableau = []
            largeursColonnes = ( (largeurContenu * 1.0 / 3, largeurContenu * 2.0 / 3) )

            styleActivite = ParagraphStyle(name="activite", fontName="Helvetica", fontSize=dictParametres["activite_taille_nom"], leading=dictParametres["activite_taille_nom"], spaceAfter=0, textColor=couleurTexte)
            styleGroupe = ParagraphStyle(name="groupe", fontName="Helvetica-Bold", fontSize=tailleGroupe, leading=tailleGroupe+2, spaceBefore=0, spaceAfter=2, textColor=couleurTexte)
            styleEcole = ParagraphStyle(name="ecole", fontName="Helvetica", alignment=2, fontSize=5, leading=3, spaceAfter=0, textColor=couleurTexte)
            styleClasse = ParagraphStyle(name="classe", fontName="Helvetica-Bold", alignment=2, fontSize=14, leading=16, spaceBefore=0, spaceAfter=2, textColor=couleurTexte)

            ligne = [ (Paragraph(nomActivite, styleActivite), Paragraph(nomGroupe, styleGroupe)), None]

            if self.GetPage("scolarite").GetRegroupement() == "ecole" :
                if nomEcole == None : nomEcole = _(u"Ecole inconnue")
                ligne[1] = (Paragraph(nomEcole, styleClasse))

            if self.GetPage("scolarite").GetRegroupement() == "classe":
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

        # Pr�pare liste pour Export Excel
        listeExport = []

        # Ins�re un header
        CreationTitreDocument()

        # Activit�s
        nbreActivites = len(listeActivites)
        indexActivite = 1
        for IDactivite in listeActivites :
            nomActivite = dictActivites[IDactivite]["nom"]

            # Groupes
            if IDactivite in dictOuvertures :
                nbreGroupes = len(dictOuvertures[IDactivite])

                # tri des groupes par ordre
                listeGroupesTemp = self.TriGroupes(list(dictOuvertures[IDactivite].keys()), dictGroupes)

                indexGroupe = 1
                for IDgroupe in listeGroupesTemp :
                    dictDatesUnites = dictOuvertures[IDactivite][IDgroupe]

                    nomGroupe = dictGroupes[IDgroupe]["nom"]

                    # Classes
                    listeScolarite = []
                    if IDactivite in dictConso :
                        if IDgroupe in dictConso[IDactivite] :
                            listeScolarite = list(dictConso[IDactivite][IDgroupe].keys())

                    # tri des classes
                    listeInfosScolarite = self.TriClasses(listeScolarite, dictEcoles)

                    # Si aucun enfant scolaris�
                    if len(listeInfosScolarite) == 0 or self.GetPage("scolarite").GetRegroupement() == None :
                        listeInfosScolarite = [None,]

                    nbreClasses = len(listeInfosScolarite)
                    indexClasse = 1
                    for dictClasse in listeInfosScolarite :

                        # R�cup�ration des infos sur �cole et classe
                        if dictClasse != None :
                            IDecole = dictClasse["IDecole"]
                            nomEcole = dictClasse["nomEcole"]
                            IDclasse = dictClasse["IDclasse"]
                            nomClasse = dictClasse["nomClasse"]
                        else :
                            IDecole = None
                            nomEcole = None
                            IDclasse = None
                            nomClasse = None

                        # M�morisation du regroupement de scolarit�
                        regroupement_scolarite = self.GetPage("scolarite").GetRegroupement()
                        if regroupement_scolarite == "ecole":
                            scolarite = IDecole
                        elif regroupement_scolarite == "classe":
                            scolarite = IDclasse
                        else:
                            scolarite = None

                        # Recherche des �v�nements
                        listeEvenements = []
                        if IDactivite in dictConso:
                            if IDgroupe in dictConso[IDactivite]:
                                if scolarite in dictConso[IDactivite][IDgroupe]:
                                    listeEvenements = list(dictConso[IDactivite][IDgroupe][scolarite].keys())

                        # tri des �v�nements
                        #listeInfosScolarite = self.TriClasses(listeScolarite, dictEcoles) #todo ?

                        # Si regroupement par �v�nement
                        if self.GetPage("evenements").checkbox_evenements.GetValue() == False :
                            listeEvenements = [None, ]

                        for IDevenement in listeEvenements :

                            # # Recherche nom �v�nement
                            # if dictEvenements.has_key(IDevenement) :
                            #     nomEvenement = dictEvenements[IDevenement]
                            # else :
                            #     nomEvenement = None

                            # Parcours les �tiquettes
                            listeIDetiquette = []
                            if IDactivite in dictConso :
                                if IDgroupe in dictConso[IDactivite] :
                                    if scolarite in dictConso[IDactivite][IDgroupe] :
                                        if IDevenement in dictConso[IDactivite][IDgroupe][scolarite]:
                                            for IDetiquette, temp in dictConso[IDactivite][IDgroupe][scolarite][IDevenement].items() :
                                                listeIDetiquette.append(IDetiquette)
                            if len(listeIDetiquette) == 0 :
                                listeIDetiquette = [None,]

                            for IDetiquette in listeIDetiquette :

                                # Initialisation du tableau
                                dataTableau = []
                                largeursColonnes = []
                                labelsColonnes = []

                                # Recherche des ent�tes de colonnes :
                                if dictParametres["afficher_photos"] != "non" :
                                    labelsColonnes.append(Paragraph(_(u"Photo"), styleEntetes))
                                    largeursColonnes.append(tailleImageFinal+6)

                                labelsColonnes.append(Paragraph(_(u"Nom - pr�nom"), styleEntetes))
                                if dictParametres["largeur_colonne_nom"] == "automatique" :
                                    largeurColonneNom = 120
                                else :
                                    largeurColonneNom = int(dictParametres["largeur_colonne_nom"])
                                largeursColonnes.append(largeurColonneNom)

                                if dictParametres["afficher_age"] == True :
                                    labelsColonnes.append(Paragraph(_(u"Age"), styleEntetes))
                                    if dictParametres["largeur_colonne_age"] == "automatique":
                                        largeurColonneAge = 20
                                    else:
                                        largeurColonneAge = int(dictParametres["largeur_colonne_age"])
                                    largeursColonnes.append(largeurColonneAge)

                                # Recherche des entetes de colonnes UNITES
                                if dictParametres["largeur_colonne_unite"] == "automatique" :
                                    largeurColonneUnite = 30
                                else :
                                    largeurColonneUnite = int(dictParametres["largeur_colonne_unite"])

                                listePositionsDates = []
                                positionCol1 = len(labelsColonnes)
                                indexCol = len(labelsColonnes)
                                for date in listeDates :
                                    if date in dictDatesUnites :
                                        listeUnites = dictDatesUnites[date]
                                        positionG = indexCol
                                        for typeTemp, IDunite, affichage in dictChoixUnites[IDactivite] :
                                            if (affichage == "utilise" and IDunite in listeUnites) or affichage == "toujours" :
                                                if typeTemp == "conso" :
                                                    abregeUnite = dictUnites[IDunite]["abrege"]
                                                else:
                                                    if IDunite in dictUnitesRemplissage :
                                                        abregeUnite = dictUnitesRemplissage[IDunite]["abrege"]
                                                    else :
                                                        abregeUnite = "?"
                                                labelsColonnes.append(Paragraph(abregeUnite, styleEntetes))
                                                largeur = largeurColonneUnite

                                                # Agrandit si unit� de type multihoraires
                                                if typeTemp == "conso" and dictUnites[IDunite]["type"] == "Multihoraires" and dictParametres["largeur_colonne_unite"] == "automatique" :
                                                    largeur = 55

                                                # Agrandit si �v�nements � afficher
                                                if dictParametres["afficher_evenements"] == True and dictParametres["largeur_colonne_unite"] == "automatique" :
                                                    largeur += 30

                                                # Agrandit si �tiquettes � afficher
                                                if dictParametres["afficher_etiquettes"] == True and dictParametres["largeur_colonne_unite"] == "automatique" :
                                                    largeur += 10

                                                largeursColonnes.append(largeur)
                                                indexCol += 1
                                        positionD = indexCol-1
                                        listePositionsDates.append((date, positionG, positionD))

                                # Colonnes personnalis�es
                                for dictColonnePerso in dictParametres["colonnes"]:
                                    labelsColonnes.append(Paragraph(dictColonnePerso["nom"], styleEntetes))
                                    if dictColonnePerso["largeur"] == "automatique" :
                                        largeurColonnePerso = int(dictParametres["largeur_colonne_perso"])
                                        if dictColonnePerso["donnee_code"].startswith("codebarres"):
                                            largeurColonnePerso = 85
                                    else :
                                        largeurColonnePerso = int(dictColonnePerso["largeur"])
                                    largeursColonnes.append(largeurColonnePerso)

                                # Colonne Informations
                                if dictParametres["afficher_informations"] == True :
                                    labelsColonnes.append(Paragraph(_(u"Informations"), styleEntetes))
                                    if dictParametres["largeur_colonne_informations"] == "automatique" :
                                        largeurColonneInformations = largeurContenu - sum(largeursColonnes)
                                    else :
                                        largeurColonneInformations = int(dictParametres["largeur_colonne_informations"])
                                    largeursColonnes.append(largeurColonneInformations)

                                # ------ Cr�ation de l'entete de groupe ------
                                CreationTitreTableau(nomActivite, nomGroupe, nomEcole, nomClasse)

                                if IDevenement != None :
                                    nomEvenement = dictEvenements[IDevenement]["nom"]
                                    CreationTitreTableau(nomGroupe=nomEvenement, couleurTexte=colors.black, tailleGroupe=10)
                                else :
                                    nomEvenement = None

                                if IDetiquette != None :
                                    nomEtiquette = dictEtiquettes[IDetiquette]["label"]
                                    couleurEtiquette = colors.grey #ConvertCouleurWXpourPDF(dictEtiquettes[IDetiquette]["couleurRVB"])
                                    CreationTitreTableau(nomGroupe=nomEtiquette, couleurTexte=couleurEtiquette, tailleGroupe=10)
                                else :
                                    nomEtiquette = None

                                listeLignesExport = []

                                # Cr�ation de l'entete des DATES
                                if typeListe == "period" :
                                    ligneTempExport = []
                                    styleDate = ParagraphStyle(name="date", fontName="Helvetica-Bold", fontSize=8, spaceAfter=0, leading=9)
                                    ligne = []
                                    for index in range(0, len(labelsColonnes)-1):
                                        ligne.append("")
                                        ligneTempExport.append("")

                                    index = 0
                                    for date, positionG, positionD in listePositionsDates :
                                        listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
                                        listeJoursAbrege = (_(u"Lun."), _(u"Mar."), _(u"Mer."), _(u"Jeu."), _(u"Ven."), _(u"Sam."), _(u"Dim."))
                                        listeMoisAbrege = (_(u"janv."), _(u"f�v."), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juil."), _(u"ao�t"), _(u"sept."), _(u"oct"), _(u"nov."), _(u"d�c."))
                                        try :
                                            if (positionD-positionG) < 1 :
                                                jourStr = listeJoursAbrege[date.weekday()]
                                                ligne[positionG] = u"%s\n%d\n%s\n%d" % (jourStr, date.day, listeMoisAbrege[date.month-1], date.year)
                                            else:
                                                jourStr = listeJours[date.weekday()]
                                                dateStr = u"<para align='center'>%s %d %s %d</para>" % (jourStr, date.day, listeMoisAbrege[date.month-1], date.year)
                                                ligne[positionG] = Paragraph(dateStr, styleDate)
                                            ligneTempExport[positionG] = UTILS_Dates.DateEngFr(str(date))
                                        except:
                                            pass
                                        index += 1
                                    dataTableau.append(ligne)
                                    listeLignesExport.append(ligneTempExport)

                                # Cr�ation des ent�tes
                                ligne = []
                                for label in labelsColonnes :
                                    ligne.append(label)
                                dataTableau.append(ligne)
                                listeLignesExport.append(ligne)

                                # --------- Cr�ation des lignes -----------

                                # Cr�ation d'une liste temporaire pour le tri
                                listeIndividus = []
                                if IDactivite in dictConso :
                                    if IDgroupe in dictConso[IDactivite] :
                                        if scolarite in dictConso[IDactivite][IDgroupe] :
                                            if IDevenement in dictConso[IDactivite][IDgroupe][scolarite] :
                                                if IDetiquette in dictConso[IDactivite][IDgroupe][scolarite][IDevenement]:
                                                    for IDindividu, dictIndividu in dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette].items() :
                                                        valeursTri = (IDindividu, dictIndividu["nom"], dictIndividu["prenom"], dictIndividu["age"])
                                                        listeIndividus.append(valeursTri)

                                if dictParametres["tri"] == "nom" : paramTri = 1 # Nom
                                if dictParametres["tri"] == "prenom" : paramTri = 2 # Pr�nom
                                if dictParametres["tri"] == "age" : paramTri = 3 # Age
                                if dictParametres["ordre"] == "croissant" :
                                    ordreDecroissant = False
                                else:
                                    ordreDecroissant = True
                                listeIndividus = sorted(listeIndividus, key=operator.itemgetter(paramTri), reverse=ordreDecroissant)

                                # R�cup�ration des lignes individus
                                dictTotauxColonnes = {}
                                indexLigne = 0
                                for IDindividu, nom, prenom, age in listeIndividus :

                                    dictIndividu = dictConso[IDactivite][IDgroupe][scolarite][IDevenement][IDetiquette][IDindividu]
                                    ligne = []
                                    indexColonne = 0
                                    ligneVide = True

                                    # Photo
                                    if dictParametres["afficher_photos"] != "non" and IDindividu in dictPhotos :
                                        img = dictPhotos[IDindividu]
                                        ligne.append(img)
                                        indexColonne += 1

                                    # Nom
                                    ligne.append(Paragraph(u"%s %s" % (nom, prenom), styleNormal))
                                    indexColonne += 1

                                    # Age
                                    if dictParametres["afficher_age"] == True :
                                        if age != None :
                                            ligne.append(Paragraph(str(age), styleNormal))
                                        else:
                                            ligne.append("")
                                        indexColonne += 1

                                    # Unites
                                    for date in listeDates :
                                        if date in dictDatesUnites :
                                            listeUnites = dictDatesUnites[date]

                                            for typeTemp, IDunite, affichage in dictChoixUnites[IDactivite] :
                                                if (affichage == "utilise" and IDunite in listeUnites) or affichage == "toujours" :
                                                    listeLabels = []
                                                    quantite = None

                                                    styleConso = ParagraphStyle(name="label_conso", fontName="Helvetica", alignment=1, fontSize=6, leading=6, spaceBefore=0, spaceAfter=0, textColor=colors.black)
                                                    styleEvenement = ParagraphStyle(name="label_evenement", fontName="Helvetica", alignment=1, fontSize=5, leading=5, spaceBefore=2, spaceAfter=0, textColor=colors.black)
                                                    styleEtiquette = ParagraphStyle(name="label_etiquette", fontName="Helvetica", alignment=1, fontSize=5, leading=5, spaceBefore=2, spaceAfter=0, textColor=colors.grey)

                                                    if typeTemp == "conso" :
                                                        # Unit� de Conso
                                                        if date in dictIndividu["listeConso"] :
                                                            if IDunite in dictIndividu["listeConso"][date] :
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
                                                                        #if len(label) > 0 : label += "\n"
                                                                        label = u"%s > %s" % (heure_debut, heure_fin)
                                                                    if typeUnite == "Evenement" :
                                                                         label = u"X"
                                                                    if typeUnite == "Quantite" :
                                                                         label = str(quantite)

                                                                    if dictParametres["masquer_consommations"] == True :
                                                                        label = ""

                                                                    listeLabels.append(Paragraph(label, styleConso))

                                                                    # Affichage de l'�v�nement
                                                                    if dictParametres["afficher_evenements"] == True and dictConsoTemp["IDevenement"] != None :
                                                                        texteEvenement = dictEvenements[dictConsoTemp["IDevenement"]]["nom"]
                                                                        listeLabels.append(Paragraph(texteEvenement, styleEvenement))

                                                                    # Affichage de l'�tiquette
                                                                    if dictParametres["afficher_etiquettes"] == True and len(etiquettes) > 0 :
                                                                        texteEtiquette = []
                                                                        for IDetiquetteTemp in etiquettes :
                                                                            texteEtiquette.append(dictEtiquettes[IDetiquetteTemp]["label"])
                                                                        etiquette = "\n\n" + ", ".join(texteEtiquette)
                                                                        listeLabels.append(Paragraph(etiquette, styleEtiquette))

                                                    else:
                                                        # Unit� de Remplissage
                                                        if IDunite in dictUnitesRemplissage :
                                                            unitesLiees = dictUnitesRemplissage[IDunite]["unites"]
                                                            etiquettesUnitesRemplissage = dictUnitesRemplissage[IDunite]["etiquettes"]
                                                        else :
                                                            unitesLiees = []
                                                            etiquettesUnitesRemplissage = []

                                                        for IDuniteLiee in unitesLiees :
                                                            if date in dictIndividu["listeConso"] :
                                                                if IDuniteLiee in dictIndividu["listeConso"][date] :
                                                                    typeUnite = dictUnites[IDuniteLiee]["type"]

                                                                    for dictConsoTemp in dictIndividu["listeConso"][date][IDuniteLiee] :
                                                                        etat = dictConsoTemp["etat"]
                                                                        quantite = dictConsoTemp["quantite"]
                                                                        etiquettes = dictConsoTemp["etiquettes"]
                                                                        heure_debut = dictConsoTemp["heure_debut"]
                                                                        heure_fin = dictConsoTemp["heure_fin"]

                                                                        valide = True

                                                                        # Validation de la condition �tiquettes
                                                                        if len(etiquettesUnitesRemplissage) > 0 :
                                                                            valide = False
                                                                            for IDetiquetteTemp in etiquettesUnitesRemplissage :
                                                                                if IDetiquetteTemp in etiquettes :
                                                                                    valide = True

                                                                        # Validation de la condition tranche horaire
                                                                        try:
                                                                            heure_min = dictUnitesRemplissage[IDunite]["heure_min"]
                                                                            heure_max = dictUnitesRemplissage[IDunite]["heure_max"]
                                                                            if heure_min != None and heure_max != None and heure_debut != None and heure_fin != None:
                                                                                heure_min_TM = UTILS_Dates.HeureStrEnTime(heure_min)
                                                                                heure_max_TM = UTILS_Dates.HeureStrEnTime(heure_max)
                                                                                heure_debut_TM = UTILS_Dates.HeureStrEnTime(heure_debut)
                                                                                heure_fin_TM = UTILS_Dates.HeureStrEnTime(heure_fin)

                                                                                if heure_debut_TM <= heure_max_TM and heure_fin_TM >= heure_min_TM:
                                                                                    valide = True
                                                                                else:
                                                                                    valide = False
                                                                        except:
                                                                            pass

                                                                        if valide == True :

                                                                            if quantite != None :
                                                                                label = str(quantite)
                                                                            else :
                                                                                label = u"X"

                                                                            if dictParametres["masquer_consommations"] == True :
                                                                                label = ""

                                                                            listeLabels.append(Paragraph(label, styleConso))

                                                                            # Affichage de l'�v�nement
                                                                            if dictParametres["afficher_evenements"] == True and dictConsoTemp["IDevenement"] != None:
                                                                                texteEvenement = dictEvenements[dictConsoTemp["IDevenement"]]["nom"]
                                                                                listeLabels.append(Paragraph(texteEvenement, styleEvenement))

                                                                            # Affichage de l'�tiquette
                                                                            if dictParametres["afficher_etiquettes"] == True and len(etiquettes) > 0 :
                                                                                texteEtiquette = []
                                                                                for IDetiquetteTemp in etiquettes :
                                                                                    texteEtiquette.append(dictEtiquettes[IDetiquetteTemp]["label"])
                                                                                    etiquette = "\n\n" + ", ".join(texteEtiquette)
                                                                                listeLabels.append(Paragraph(etiquette, styleEtiquette))


                                                    if quantite == None :
                                                        quantite = 1

                                                    if len(listeLabels) > 0 :
                                                        ligneVide = False
                                                        if (indexColonne in dictTotauxColonnes) == True :
                                                            dictTotauxColonnes[indexColonne] += quantite
                                                        else:
                                                            dictTotauxColonnes[indexColonne] = quantite
                                                    ligne.append(listeLabels)
                                                    indexColonne += 1

                                    # Colonnes personnalis�es
                                    for dictColonnePerso in dictParametres["colonnes"]:
                                        IDfamille = dictIndividus[IDindividu]["IDfamille"]
                                        type_donnee = "unicode"
                                        if dictColonnePerso["donnee_code"] == None :
                                            donnee = ""
                                        else :
                                            try :
                                                if dictColonnePerso["donnee_code"] == "aucun": donnee = ""
                                                if dictColonnePerso["donnee_code"] == "ville_residence": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_VILLE"]
                                                if dictColonnePerso["donnee_code"] == "secteur": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_SECTEUR"]
                                                if dictColonnePerso["donnee_code"] == "genre": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_SEXE"]
                                                if dictColonnePerso["donnee_code"] == "ville_naissance": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_VILLE_NAISS"]
                                                if dictColonnePerso["donnee_code"] == "nom_ecole": donnee = dictInfosIndividus[IDindividu]["SCOLARITE_NOM_ECOLE"]
                                                if dictColonnePerso["donnee_code"] == "nom_classe": donnee = dictInfosIndividus[IDindividu]["SCOLARITE_NOM_CLASSE"]
                                                if dictColonnePerso["donnee_code"] == "nom_niveau_scolaire": donnee = dictInfosIndividus[IDindividu]["SCOLARITE_NOM_NIVEAU"]
                                                if dictColonnePerso["donnee_code"] == "famille": donnee = dictInfosFamilles[IDfamille]["FAMILLE_NOM"]
                                                if dictColonnePerso["donnee_code"] == "regime": donnee = dictInfosFamilles[IDfamille]["FAMILLE_NOM_REGIME"]
                                                if dictColonnePerso["donnee_code"] == "caisse": donnee = dictInfosFamilles[IDfamille]["FAMILLE_NOM_CAISSE"]
                                                if dictColonnePerso["donnee_code"] == "quotient_familial": donnee = dictInfosFamilles[IDfamille]["FAMILLE_QF_ACTUEL"]
                                                if dictColonnePerso["donnee_code"] == "date_naiss": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_DATE_NAISS"]
                                                if dictColonnePerso["donnee_code"] == "medecin_nom": donnee = dictInfosIndividus[IDindividu]["MEDECIN_NOM"]
                                                if dictColonnePerso["donnee_code"] == "tel_mobile": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_TEL_MOBILE"]
                                                if dictColonnePerso["donnee_code"] == "tel_domicile": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_TEL_DOMICILE"]
                                                if dictColonnePerso["donnee_code"] == "mail": donnee = dictInfosIndividus[IDindividu]["INDIVIDU_MAIL"]

                                                if dictColonnePerso["donnee_code"] == "adresse_residence":
                                                    rue = dictInfosIndividus[IDindividu]["INDIVIDU_RUE"]
                                                    if rue == None : rue = ""
                                                    cp = dictInfosIndividus[IDindividu]["INDIVIDU_CP"]
                                                    if cp == None : cp = ""
                                                    ville = dictInfosIndividus[IDindividu]["INDIVIDU_VILLE"]
                                                    if ville == None : ville = ""
                                                    donnee = u"%s %s %s" % (rue, cp, ville)

                                                # Questionnaires
                                                if dictColonnePerso["donnee_code"].startswith("question_") and "famille" in \
                                                        dictColonnePerso["donnee_code"]:
                                                    donnee = dictInfosFamilles[IDfamille][
                                                        "QUESTION_%s" % dictColonnePerso["donnee_code"][17:]]
                                                if dictColonnePerso["donnee_code"].startswith("question_") and "individu" in \
                                                        dictColonnePerso["donnee_code"]:
                                                    donnee = dictInfosIndividus[IDindividu][
                                                        "QUESTION_%s" % dictColonnePerso["donnee_code"][18:]]

                                                # Code-barre individu
                                                if dictColonnePerso["donnee_code"] == "codebarres_individu":
                                                    type_donnee = "code-barres"
                                                    donnee = code39.Extended39("I%06d" % IDindividu, humanReadable=False)

                                            except :
                                                donnee = ""

                                        if type_donnee == "unicode" :
                                            ligne.append(Paragraph(six.text_type(donnee), styleNormal))
                                        else :
                                            ligne.append(donnee)


                                    # Infos m�dicales
                                    texteInfos = u""
                                    listeInfos = []
                                    paraStyle = ParagraphStyle(name="infos", fontName="Helvetica", fontSize=7, leading=8, spaceAfter=2,)

                                    # M�mo-journ�e
                                    if IDindividu in dictMemos :
                                        for date in listeDates :
                                            if date in dictMemos[IDindividu] :
                                                memo_texte = dictMemos[IDindividu][date]["texte"]
                                                memo_couleur = dictMemos[IDindividu][date]["couleur"]
                                                if typeListe == "period" :
                                                    memo_texte = u"%02d/%02d/%04d : %s" % (date.day, date.month, date.year, memo_texte)
                                                if len(memo_texte) > 0 and memo_texte[-1] != "." : memo_texte += u"."
                                                listeInfos.append(ParagraphAndImage(Paragraph("<FONT color='%s'>%s</FONT>" % (memo_couleur or "black", memo_texte), paraStyle), Image(Chemins.GetStaticPath("Images/16x16/Information.png"),width=8, height=8), xpad=1, ypad=0, side="left"))

                                    # Messages individuels
                                    if IDindividu in dictMessagesIndividus:
                                        for dictMessage in dictMessagesIndividus[IDindividu] :
                                            texteMessage = dictMessage["texte"]
                                            listeInfos.append(ParagraphAndImage(Paragraph(texteMessage, paraStyle), Image(Chemins.GetStaticPath("Images/16x16/Mail.png"),width=8, height=8), xpad=1, ypad=0, side="left"))

                                    # R�cup�re la liste des familles rattach�es � cet individu
                                    listeIDfamille = []
                                    for date, dictUnitesTemps in dictIndividu["listeConso"].items() :
                                        for temp, listeConso in dictUnitesTemps.items() :
                                            for dictConsoTemp in listeConso :
                                                if dictConsoTemp["IDfamille"] not in listeIDfamille :
                                                    listeIDfamille.append(dictConsoTemp["IDfamille"])

                                    # Messages familiaux
                                    for IDfamille in listeIDfamille :
                                        if IDfamille in dictMessagesFamilles:
                                            for dictMessage in dictMessagesFamilles[IDfamille] :
                                                texteMessage = dictMessage["texte"]
                                                listeInfos.append(ParagraphAndImage(Paragraph(texteMessage, paraStyle), Image(Chemins.GetStaticPath("Images/16x16/Mail.png"),width=8, height=8), xpad=1, ypad=0, side="left"))

                                    # Cotisations manquantes
                                    if dictParametres["afficher_cotisations_manquantes"] == True :
                                        for IDfamille in listeIDfamille :
                                            if IDfamille in dictCotisations:
                                                if dictCotisations[IDfamille]["nbre"] == 1 :
                                                    texteCotisation = _(u"1 cotisation manquante : %s") % dictCotisations[IDfamille]["cotisations"]
                                                else:
                                                    texteCotisation = _(u"%d cotisations manquantes : %s") % (dictCotisations[IDfamille]["nbre"], dictCotisations[IDfamille]["cotisations"])
                                                listeInfos.append(ParagraphAndImage(Paragraph(texteCotisation, paraStyle), Image(Chemins.GetStaticPath("Images/16x16/Cotisation.png"),width=8, height=8), xpad=1, ypad=0, side="left"))

                                    # Pi�ces manquantes
                                    if dictParametres["afficher_pieces_manquantes"] == True :
                                        for IDfamille in listeIDfamille :
                                            if IDfamille in dictPieces:
                                                if dictPieces[IDfamille]["nbre"] == 1 :
                                                    textePiece = _(u"1 pi�ce manquante : %s") % dictPieces[IDfamille]["pieces"]
                                                else:
                                                    textePiece = _(u"%d pi�ces manquantes : %s") % (dictPieces[IDfamille]["nbre"], dictPieces[IDfamille]["pieces"])
                                                listeInfos.append(ParagraphAndImage(Paragraph(textePiece, paraStyle), Image(Chemins.GetStaticPath("Images/16x16/Piece.png"),width=8, height=8), xpad=1, ypad=0, side="left"))

                                    # Sieste
                                    texte_sieste = dictIndividu["nomSieste"]
                                    if texte_sieste != None and texte_sieste != "" :
                                        if len(texte_sieste) > 0 and texte_sieste[-1] != "." : texte_sieste += u"."
                                        listeInfos.append(ParagraphAndImage(Paragraph(texte_sieste, paraStyle), Image(Chemins.GetStaticPath("Images/16x16/Reveil.png"),width=8, height=8), xpad=1, ypad=0, side="left"))

                                    # Informations m�dicales
                                    if IDindividu in dictInfosMedicales :
                                        for infoMedicale in dictInfosMedicales[IDindividu] :
                                            intitule = infoMedicale["intitule"]
                                            description = infoMedicale["description"]
                                            traitement = infoMedicale["traitement_medical"]
                                            description_traitement = infoMedicale["description_traitement"]
                                            date_debut_traitement = infoMedicale["date_debut_traitement"]
                                            date_fin_traitement = infoMedicale["date_fin_traitement"]
                                            IDtype = infoMedicale["IDtype"]
                                            # Intitul� et description
                                            if description != None and description != "" :
                                                texte = u"<b>%s</b> : %s" % (intitule, description) # >
                                            else:
                                                texte = u"%s" % intitule # >
                                            if len(texte) > 0 and texte[-1] != "." : texte += u"."
                                            # Traitement m�dical
                                            if traitement == 1 and description_traitement != None and description_traitement != "" :
                                                texteDatesTraitement = u""
                                                if date_debut_traitement != None and date_fin_traitement != None :
                                                    texteDatesTraitement = _(u" du %s au %s") % (UTILS_Dates.DateEngFr(date_debut_traitement), UTILS_Dates.DateEngFr(date_fin_traitement))
                                                if date_debut_traitement != None and date_fin_traitement == None :
                                                    texteDatesTraitement = _(u" � partir du %s") % UTILS_Dates.DateEngFr(date_debut_traitement)
                                                if date_debut_traitement == None and date_fin_traitement != None :
                                                    texteDatesTraitement = _(u" jusqu'au %s") % UTILS_Dates.DateEngFr(date_fin_traitement)
                                                texte += _(u"Traitement%s : %s.") % (texteDatesTraitement, description_traitement)

                                            listeInfos.append(ParagraphAndImage(Paragraph(texte, paraStyle), Image(Chemins.GetStaticPath("Images/16x16/Medical.png"),width=8, height=8), xpad=1, ypad=0, side="left"))

                                    if dictParametres["afficher_informations"] == True:
                                        if dictParametres["masquer_informations"] == False :
                                            ligne.append(listeInfos)
                                        else:
                                            ligne.append(u"")

                                    if not ligneVide or dictParametres["afficher_inscrits"] == True :
                                        # Ajout de la ligne individuelle dans le tableau
                                        dataTableau.append(ligne)
                                        # M�morise les lignes pour export Excel
                                        listeLignesExport.append(ligne)
                                        indexLigne += 1

                                # Cr�ation des lignes vierges
                                for x in range(0, dictParametres["nbre_lignes_vierges"]):
                                    ligne = []
                                    for col in labelsColonnes :
                                        ligne.append("")
                                    dataTableau.append(ligne)

                                # Style du tableau
                                colPremiereUnite = 1
                                if dictParametres["afficher_photos"] != "non" :
                                    colPremiereUnite += 1
                                if dictParametres["afficher_age"] == True :
                                    colPremiereUnite += 1


                                style = [
                                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                                        ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police
                                        ('ALIGN', (0,0), (-2,-1), 'CENTRE'), # Centre les cases
                                        ('ALIGN', (0,0), (-1,0), 'CENTRE'), # Ligne de labels colonne align�e au centre
                                        ('FONT',(0,0),(-1,0), "Helvetica", 6), # Donne la police de caract. + taille de police des labels
                                        ('LEFTPADDING', (0, 0), (-1, 0), 0), # Entetes de colonnes
                                        ('RIGHTPADDING', (0, 0), (-1, 0), 0), # Entetes de colonnes
                                        ('LEFTPADDING', (1, 1), (-2, -1), 1), # Colonnes unit�s et perso uniquement
                                        ('RIGHTPADDING', (1, 1), (-2, -1), 1), # Colonnes unit�s et perso uniquement
                                        # Donne la police de caract. + taille de police des labels
                                        ]

                                # Formatage de la ligne DATES
                                if typeListe == "period" :
                                    style.append( ('BACKGROUND', (0, 0), (-1, 0), couleur_fond_titre) )
                                    style.append( ('BACKGROUND', (0, 1), (-1, 1), couleur_fond_entetes) )
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
                                    style.append(('BACKGROUND', (0, 0), (-1, 0), couleur_fond_entetes))

                                # V�rifie si la largeur du tableau est inf�rieure � la largeur de la page
                                if modeExport == False :
                                    largeurTableau = 0
                                    for largeur in largeursColonnes :
                                        if largeur < 0 :
                                            dlg = wx.MessageDialog(self, _(u"Il y a trop de colonnes dans le tableau ! \n\nVeuillez s�lectionner moins de jours dans le calendrier..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                                            dlg.ShowModal()
                                            dlg.Destroy()
                                            DlgAttente.Destroy()
                                            return False

                                # Cr�ation du tableau
                                if typeListe == "period" :
                                    repeatRows = 2
                                else :
                                    repeatRows = 1

                                # Hauteur de ligne individus
                                if dictParametres["hauteur_ligne_individu"] == "automatique":
                                    hauteursLignes = None
                                else :
                                    hauteursLignes = [int(dictParametres["hauteur_ligne_individu"]) for x in range(len(dataTableau))]
                                    hauteursLignes[0] = 12
                                    hauteursLignes[-1] = 10

                                tableau = Table(dataTableau, largeursColonnes, rowHeights=hauteursLignes, repeatRows=repeatRows)
                                tableau.setStyle(TableStyle(style))
                                story.append(tableau)

                                # Cr�ation du tableau des totaux
                                if dictParametres["afficher_photos"] != "non" :
                                    colNomsIndividus = 1
                                else:
                                    colNomsIndividus = 0

                                ligne = []
                                indexCol = 0
                                for indexCol in range(0, len(labelsColonnes)) :
                                    if indexCol in dictTotauxColonnes :
                                        valeur = dictTotauxColonnes[indexCol]
                                    else:
                                        valeur = ""
                                    if indexCol == colNomsIndividus :
                                        if indexLigne == 1 :
                                            valeur = _(u"1 individu")
                                        else:
                                            valeur = _(u"%d individus") % indexLigne
                                    ligne.append(valeur)
                                listeLignesExport.append(ligne)

                                if dictParametres["afficher_informations"] == True :
                                    colDerniereUnite = -2
                                else :
                                    colDerniereUnite = -1

                                style = [
                                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                                        ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police
                                        ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Centre les cases
                                        ('GRID', (colPremiereUnite,-1), (colDerniereUnite,-1), 0.25, colors.black),
                                        ('BACKGROUND', (colPremiereUnite, -1), (colDerniereUnite, -1), couleur_fond_total)
                                        ]

                                if typeListe == "period" :
                                    for date, positionG, positionD in listePositionsDates :
                                        style.append( ('BOX', (positionG, 0), (positionD, 0), 1, colors.black) ) # Entoure toutes les colonnes Dates

                                tableau = Table([ligne,], largeursColonnes)
                                tableau.setStyle(TableStyle(style))
                                story.append(tableau)

                                story.append(Spacer(0,20))

                                # Export
                                listeExport.append({"activite":nomActivite, "groupe":nomGroupe, "ecole":nomEcole, "classe":nomClasse, "evenement":nomEvenement, "etiquette":nomEtiquette, "lignes":listeLignesExport})

                                # Saut de page apr�s une �tiquette
                                if self.GetPage("etiquettes").checkbox_etiquettes.GetValue() == True and self.GetPage("etiquettes").checkbox_saut_etiquettes.GetValue() == True :
                                    CreationSautPage()

                            # Saut de page apr�s un �v�nement
                            if self.GetPage("evenements").checkbox_evenements.GetValue() == True and self.GetPage("evenements").checkbox_saut_evenements.GetValue() == True :
                                CreationSautPage()

                        # Saut de page apr�s une classe
                        if self.GetPage("scolarite").GetRegroupement() == "classe" and self.GetPage("scolarite").checkbox_saut_classes.GetValue() == True and indexClasse <= nbreClasses :
                            CreationSautPage()

                        # Saut de page apr�s une �cole
                        if self.GetPage("scolarite").GetRegroupement() == "classe" and self.GetPage("scolarite").checkbox_saut_ecoles.GetValue() == True :
                            IDecoleActuelle = None
                            IDecoleSuivante = None
                            if IDclasse in dictClasses :
                                IDecoleActuelle = dictClasses[IDclasse]["IDecole"]
                                if indexClasse < nbreClasses :
                                    IDclasseSuivante = listeInfosScolarite[indexClasse]["IDclasse"]
                                    if IDclasseSuivante in dictClasses :
                                        IDecoleSuivante = dictClasses[IDclasseSuivante]["IDecole"]
                            if IDecoleActuelle != IDecoleSuivante :
                                CreationSautPage()

                        # Saut de page apr�s une �cole
                        if self.GetPage("scolarite").GetRegroupement() == "ecole" and self.GetPage("scolarite").checkbox_saut_ecoles.GetValue() == True :
                            IDecoleActuelle = scolarite
                            IDecoleSuivante = None
                            if indexClasse < nbreClasses :
                                IDecoleSuivante = listeInfosScolarite[indexClasse]["IDecole"]
                            if IDecoleActuelle != IDecoleSuivante :
                                CreationSautPage()


                        indexClasse += 1


                    # Saut de page apr�s un groupe
                    if self.GetPage("activites").checkbox_saut_groupes.GetValue() == True and indexGroupe < nbreGroupes :
                        CreationSautPage()
                    indexGroupe += 1

            # Saut de page apr�s une activit�
            if self.GetPage("activites").checkbox_saut_activites.GetValue() == True and indexActivite < nbreActivites :
                CreationSautPage()
            indexActivite += 1

        # Suppression de la derni�re page si elle est vide
        try :
            element = str(story[-3])
            if element == "PageBreak()" :
                story.pop(-1)
                story.pop(-1)
                story.pop(-1)
        except :
            pass

        # Suppression du dernier spacer s'il y en a un
        try :
            element = str(story[-1])
            if element == "Spacer(0, 20)" :
                story.pop(-1)
        except :
            pass

        # Destruction de la DlgAttente
        del DlgAttente

        # Si mode export Excel
        if modeExport == True :
            return listeExport, largeursColonnes

        # Enregistrement et ouverture du PDF
        doc.build(story)
        FonctionsPerso.LanceFichierExterne(nomDoc)

    def TriClasses(self, listeScolarite=[], dictEcoles={}):
        """ Tri des classes par nom d'�cole, par nom de classe et par niveau """
        listeResultats = []

        # Insertion des �coles et classes inconnues
        if self.GetPage("scolarite").GetAfficherInconnus() == True :
            if self.GetPage("scolarite").GetRegroupement() == "ecole" and None in listeScolarite :
                listeResultats.append({"IDecole": None, "nomEcole": _(u"Ecole inconnue"), "nomClasse": None, "IDclasse": None})
            if self.GetPage("scolarite").GetRegroupement() == "classe" and None in listeScolarite :
                listeResultats.append({"IDecole": None, "nomEcole": _(u"Ecole inconnue"), "nomClasse": _(u"Classe inconnue"), "IDclasse": None})

        # Insertion des �coles
        listeEcoles = []
        for IDecole, dictEcole in dictEcoles.items() :
            listeEcoles.append((dictEcole["nom"], IDecole))
        listeEcoles.sort()

        # Insertion des classes
        for nomEcole, IDecole in listeEcoles :

            if self.GetPage("scolarite").GetRegroupement() == "ecole" :
                if IDecole in listeScolarite:
                    listeResultats.append({"IDecole": IDecole, "nomEcole": nomEcole, "nomClasse":None, "IDclasse":None})

            if self.GetPage("scolarite").GetRegroupement() == "classe":
                listeClassesTemp = dictEcoles[IDecole]["classes"]
                listeClassesTemp.sort()
                for listeOrdresNiveaux, nomClasse, txtNiveaux, IDclasse, date_debut, date_fin in listeClassesTemp :
                    if IDclasse in listeScolarite :
                        listeResultats.append({"IDecole" : IDecole, "nomEcole":nomEcole, "nomClasse":nomClasse, "IDclasse":IDclasse, "date_debut":date_debut, "date_fin":date_fin})
        
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
        

    def GetTypeListe(self):
        if self.radio_journ.GetValue() == True :
            return "journ"
        else :
            return "period"

    def SetTypeListe(self, type_liste="journ"):
        if type_liste == "journ" :
            self.radio_journ.SetValue(True)
            self.OnRadioJourn(None)
        else :
            self.radio_period.SetValue(True)
            self.OnRadioPeriod(None)

    def GetParametres(self):
        """ R�cup�ration des param�tres """
        dictParametres = {}
        dictParametres["type_liste"] = self.GetTypeListe()
        dictParametres.update(self.GetPage("activites").GetParametres())
        dictParametres.update(self.GetPage("scolarite").GetParametres())
        dictParametres.update(self.GetPage("etiquettes").GetParametres())
        dictParametres.update(self.GetPage("evenements").GetParametres())
        dictParametres.update(self.GetPage("unites").GetParametres())
        dictParametres.update(self.GetPage("colonnes").GetParametres())
        dictParametres.update(self.GetPage("options").GetParametres())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        """ Importation des param�tres """
        # Type de liste
        if dictParametres == None :
            self.SetTypeListe("journ")
        else :
            if "type_liste" in dictParametres :
                self.SetTypeListe(dictParametres["type_liste"])

        # Autres pages
        self.GetPage("activites").SetParametres(dictParametres)
        self.GetPage("scolarite").SetParametres(dictParametres)
        self.GetPage("etiquettes").SetParametres(dictParametres)
        self.GetPage("evenements").SetParametres(dictParametres)
        self.GetPage("unites").SetParametres(dictParametres)
        self.GetPage("colonnes").SetParametres(dictParametres)
        self.GetPage("options").SetParametres(dictParametres)






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, date=datetime.date(2018, 2, 12))
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
