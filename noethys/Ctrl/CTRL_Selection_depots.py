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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB

import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.MAJenCours = False
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT | HTL.TR_AUTO_CHECK_CHILD | HTL.TR_AUTO_CHECK_PARENT)
        self.EnableSelectionVista(True)
        
        self.SetToolTip(wx.ToolTip(_(u"Cochez les dépôts à afficher")))
        
        # Création des colonnes
        self.AddColumn(_(u"Dépôts"))
        self.SetColumnWidth(0, 400)

        # Binds
        #self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem)

    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            # Active ou non les branches enfants

            if self.GetPyData(item)["type"] == "annee" :
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
            annee = self.GetPyData(parent)["ID"]
            # Recherche des dépôts cochés
            listeDepots = []
            item, cookie = self.GetFirstChild(parent)
            for index in range(0, self.GetChildrenCount(parent)):
                if self.IsItemChecked(item) :
                    IDdepot = self.GetPyData(item)["ID"]
                    listeDepots.append(IDdepot)
                item = self.GetNext(item)
            if len(listeDepots) > 0 :
                dictCoches[annee] = listeDepots
        return dictCoches
    
    def GetDepots(self) :
        dictCoches = self.GetCoches() 
        listeDepots = []
        for annee, listeDepotsTemp in dictCoches.iteritems() :
            for IDdepot in listeDepotsTemp :
                listeDepots.append(IDdepot)
        return listeDepots
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.listeDepots = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Remplissage(self):
        # Tri des dépôts par année
        dictDepots = {} 
        for dictDepot in self.listeDepots :
            date = dictDepot["date"]
            if date == None :
                annee = None
            else:
                annee = date.year
            if dictDepots.has_key(annee) == False :
                dictDepots[annee] = []
            dictDepots[annee].append(dictDepot)
        
        listeAnnees = dictDepots.keys() 
        listeAnnees.sort()
        
        # Remplissage
        for annee in listeAnnees :
            
            # Niveau Année
            if annee == None :
                label = _(u"Sans date de dépôt")
            else :
                label = str(annee)
            niveauAnnee = self.AppendItem(self.root, label, ct_type=1)
            self.SetPyData(niveauAnnee, {"type" : "annee", "ID" : annee, "label" : label})
            self.SetItemBold(niveauAnnee, True)
            
            # Niveau Dépôts
            for dictDepot in dictDepots[annee] :
                if dictDepot["date"] == None :
                    dateStr = u""
                else:
                    dateStr = u"(%02d/%02d/%04d)" % (dictDepot["date"].day, dictDepot["date"].month, dictDepot["date"].year)
                label = u"%s %s" % (dictDepot["nom"], dateStr)
                niveauDepot = self.AppendItem(niveauAnnee, label, ct_type=1)
                self.SetPyData(niveauDepot, {"type" : "depot", "ID" : dictDepot["IDdepot"], "label" : label})
            
            # Coche toutes les branches enfants
            #self.EnableChildren(niveauAnnee, False)
            
            if annee == datetime.date.today().year :
                self.Expand(niveauAnnee)
                

    def Importation(self):
        listeDepots = []
        DB = GestionDB.DB()
        req = """SELECT IDdepot, date, nom, verrouillage, IDcompte
        FROM depots
        ORDER BY date;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDdepot, date, nom, verrouillage, IDcompte in listeDonnees :
            if date != None : date = DateEngEnDateDD(date)
            dictTemp = {"IDdepot":IDdepot, "date":date, "nom":nom, "verrouillage":verrouillage, "IDcompte":IDcompte}
            listeDepots.append(dictTemp)
        return listeDepots
    


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
    

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


