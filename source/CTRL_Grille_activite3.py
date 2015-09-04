#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB

import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED

def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))



class CTRL_archive(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.SetToolTipString(_(u"Cochez les activit�s � afficher"))
        self.listeActivites = []
        self.dictActivites = {}
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetDate(self, date=None):
        self.date = date
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeActivites, self.dictActivites = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeActivites = []
        dictActivites = {}
        if self.date == None :
            return listeActivites, dictActivites 
        # R�cup�ration des activit�s disponibles le jour s�lectionn�
        DB = GestionDB.DB()
        req = """SELECT activites.IDactivite, nom, abrege, date_debut, date_fin
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        WHERE ouvertures.date='%s'
        GROUP BY activites.IDactivite
        ORDER BY nom;""" % str(self.date)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDactivite, nom, abrege, date_debut, date_fin in listeDonnees :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            dictTemp = { "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "tarifs" : {} }
            dictActivites[IDactivite] = dictTemp
            listeActivites.append((nom, IDactivite))
        listeActivites.sort()
        return listeActivites, dictActivites

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDactivite in self.listeActivites :
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
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une s�lection d'activit�s est effectu�e... """
        listeSelections = self.GetIDcoches()
        try :
            self.parent.SetActivites(listeSelections)
        except :
            print listeSelections
    
    def GetListeActivites(self):
        return self.GetIDcoches() 
        

# --------------------------------------------------------------------------------------------------------------------



class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.date = datetime.date(2014, 01, 10) #None
        self.liste_activites = []
        self.MAJenCours = False
        self.cocherParDefaut = True
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag( HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.EnableSelectionVista(True)
        
        self.SetToolTipString(_(u"Cochez les activit�s et groupes � afficher"))
        
        # Cr�ation des colonnes
        self.AddColumn(_(u"Activit�/groupe"))
        self.SetColumnWidth(0, 185)

        # Binds
##        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu) 
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 
        
        
    def SetDate(self, date=None):
        self.date = date
        self.MAJ() 

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
##            try :
            self.parent.MAJactivites()
##            except :
##                print "Erreur dans envoi des donnees sur activites et groupes :", dictCoches
        
        
    def GetCoches(self):
        dictCoches = {}
        parent = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            parent = self.GetNext(parent) 
            # Recherche des activit�s coch�es
            if self.IsItemChecked(parent) :
                IDactivite = self.GetPyData(parent)["ID"]
                # Recherche des groupes coch�s
                listeGroupes = []
                item, cookie = self.GetFirstChild(parent)
                for index in range(0, self.GetChildrenCount(parent)):
                    if self.IsItemChecked(item) : 
                        IDgroupe = self.GetPyData(item)["ID"]
                        listeGroupes.append(IDgroupe)
                    item = self.GetNext(item) 
                if len(listeGroupes) > 0 : 
                    dictCoches[IDactivite] = listeGroupes
        return dictCoches
    
    def GetActivitesEtGroupes(self) :
        dictCoches = self.GetCoches() 
        listeActivites = []
        listeGroupes = []
        for IDactivite, listeGroupesTemp in dictCoches.iteritems() :
            listeActivites.append(IDactivite)
            for IDgroupe in listeGroupesTemp :
                listeGroupes.append(IDgroupe)
        return listeActivites, listeGroupes
    
    def SetCocherParDefaut(self, etat=True):
        self.cocherParDefaut = etat
        
    def MAJ(self):
        """ Met � jour (redessine) tout le contr�le """
        self.dictActivites = self.Importation()
##        self.Freeze()
        self.MAJenCours = True
        self.DeleteAllItems()
        # Cr�ation de la racine
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False
##        self.Thaw() 

    def Remplissage(self):
        # Tri des activit�s par nom
        listeActivites = []
        for IDactivite, dictActivite in self.dictActivites.iteritems() :
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
                niveauGroupe = self.AppendItem(niveauActivite, dictGroupe["nom"], ct_type=1)
                self.SetPyData(niveauGroupe, {"type" : "groupe", "ID" : dictGroupe["IDgroupe"], "nom" : dictGroupe["nom"]})
            
            # Coche toutes les branches enfants
            if self.cocherParDefaut == True :
                self.CheckItem(niveauActivite)
                self.CheckChilds(niveauActivite)
        
        self.ExpandAllChildren(self.root)
        
##        # Pour �viter le bus de positionnement des contr�les
##        self.GetMainWindow().CalculatePositions() 

    def Importation(self):
        dictActivites = {}
        if self.date == None :
            return dictActivites 
        # R�cup�ration des activit�s disponibles le jour s�lectionn�
        DB = GestionDB.DB()
        req = """SELECT 
        activites.IDactivite, activites.nom, activites.abrege, date_debut, date_fin,
        groupes.IDgroupe, groupes.nom
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = ouvertures.IDgroupe
        WHERE ouvertures.date='%s'
        GROUP BY groupes.IDgroupe
        ORDER BY groupes.ordre;""" % str(self.date)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDactivite, nom, abrege, date_debut, date_fin, IDgroupe, nomGroupe in listeDonnees :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            
            # M�morisation de l'activit�
            if dictActivites.has_key(IDactivite) == False :
                dictActivites[IDactivite] = { "nom":nom, "abrege":abrege, "date_debut":date_debut, "date_fin":date_fin, "groupes":[]}
            # M�morisation du groupe
            dictActivites[IDactivite]["groupes"].append({"IDgroupe":IDgroupe, "nom":nomGroupe})
        return dictActivites
    


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


