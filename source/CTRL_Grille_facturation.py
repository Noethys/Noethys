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
##import wx.gizmos as gizmos
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

try: import psyco; psyco.full()
except: pass

DICT_LABELS_CATEGORIES = {
    "consommation" : (_(u"Consommation"), _(u"Consommations")),
    "cotisation" : (_(u"Cotisation"), _(u"Cotisations")),
    "autre" : (_(u"Autre"), _(u"Autres")),
    } # Code : (Singulier, Pluriel)
            
            

def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
    
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, listePrestations=[]): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.SetAGWWindowStyleFlag(wx.TR_COLUMN_LINES | HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.parent = parent
        
        self.SetBackgroundColour(wx.WHITE)
        
        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
        
        self.Initialisation() 
        
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_vert = il.Add(wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG))
        self.img_orange = il.Add(wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG))
        self.img_rouge = il.Add(wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
##        self.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnContextMenu)
    
    def Initialisation(self):               
        # Cr�ation des colonnes
        self.AddColumn(_(u"Prestations"))
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 195)
        self.AddColumn(u"")
        self.SetColumnWidth(1, 55)
        self.SetColumnAlignment(1, wx.ALIGN_RIGHT)
        
        # Cr�ation de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        self.dictBranches = {}
        self.dictBranchesPrestations = {}

    
    def SaisiePrestation(self, dictPrestations, dictDeductions, listeNouvellesPrestations, listeAnciennesPrestations, selectionIndividus, listeActivites, listePeriodes):        
        # Affichage des nouvelles prestations
        for IDprestation in listeNouvellesPrestations :
            dictPrestation = dictPrestations[IDprestation]
            categorie = dictPrestation["categorie"]
            if DICT_LABELS_CATEGORIES.has_key(categorie) :
                labelCategorie = DICT_LABELS_CATEGORIES[categorie][1]
            else:
                labelCategorie = categorie # TEMPORAIRE ICI !!!!!!!!!!!!
            date = dictPrestation["date"]
            IDfamille = dictPrestation["IDfamille"]
            IDindividu = dictPrestation["IDindividu"]
            if IDindividu != None :
                nomIndividu = dictPrestation["nomIndividu"]
            else:
                nomIndividu = u""
            if IDindividu == None :
                IDindividu = 0
            label = dictPrestation["label"]
            montant = dictPrestation["montant"]
            IDactivite = dictPrestation["IDactivite"]
            if dictPrestation.has_key("montantVentilation") :
                montantVentilation = dictPrestation["montantVentilation"]
            else:
                montantVentilation = 0.0
            
            if dictDeductions.has_key(IDprestation) :
                if len(dictDeductions[IDprestation]) > 0 :
                    label += u"*"
            
            # Crit�res d'affichage
            affichePrestation = True
            # Affiche uniquement les individus s�lectionn�s
            if IDindividu not in selectionIndividus and IDindividu != 0 :
                affichePrestation = False
            # Affiche uniquement les activit�s s�lectionn�es
            if IDactivite not in listeActivites and IDactivite != None :
                affichePrestation = False
            # Affiche uniquement les p�riodes s�lectionn�es
            afficheTemp = False
            for date_debut, date_fin in listePeriodes :
                if date >= date_debut and date <= date_fin :
                    afficheTemp = True
            if afficheTemp == False :
                affichePrestation = False
            
            if affichePrestation == True :
            
                # Recherche de la branche Cat�gorie
                brancheCategorie = self.RechercheBranche(categorie)
                if brancheCategorie == None :
                    brancheCategorie = self.AppendItem(self.root, labelCategorie)
                    self.SetPyData(brancheCategorie, labelCategorie)
                    self.SetItemBackgroundColour(brancheCategorie, (200, 200, 200) )
                    self.SetItemTextColour(brancheCategorie, (120, 120, 120) )
                    self.dictBranches[categorie] = {"branche" : brancheCategorie, "donnee" : labelCategorie}
                
                    self.SortChildren(self.root)
                
                # Recherche de la branche date
                brancheDate = self.RechercheBranche(categorie, date)
                if brancheDate == None :
                    brancheDate = self.AppendItem(brancheCategorie, DateComplete(date))
                    self.SetPyData(brancheDate, date)
                    self.SetItemBold(brancheDate, True)
                    self.dictBranches[categorie][date] = {"branche" : brancheDate, "donnee" : date}
                
                    self.SortChildren(brancheCategorie)
                
                # Recherche de la branche Individu
                brancheIndividu = self.RechercheBranche(categorie, date, IDindividu)
                if brancheIndividu == None :
                    if len(selectionIndividus) > 1 and IDindividu != 0 : 
                        brancheIndividu = self.AppendItem(brancheDate, nomIndividu)
                        self.SetPyData(brancheIndividu, nomIndividu)
                    else:
                        brancheIndividu = brancheDate
                    self.dictBranches[categorie][date][IDindividu] = {"branche" : brancheIndividu, "donnee" : nomIndividu}
                
                    self.SortChildren(brancheDate)
                
                # Recherche de la branche Prestation
                branchePrestation = self.RechercheBranche(categorie, date, IDindividu, IDprestation)
                if branchePrestation == None :
                    branchePrestation = self.AppendItem(brancheIndividu, label)
                    self.SetPyData(branchePrestation, label)
                    self.SetItemText(branchePrestation, u"%.2f %s " % (montant, SYMBOLE), 1)
                    self.dictBranches[categorie][date][IDindividu][IDprestation] = {"branche" : branchePrestation, "donnee" : label}
                    self.dictBranchesPrestations[IDprestation] = {
                        "categorie" : categorie,
                        "branche" : branchePrestation,
                        "date" : date,
                        "IDindividu" : IDindividu,
                        "montant" : montant,
                        }
                    # Coloration si prestation pay�e
                    if montantVentilation > 0.0 :
                        if montant == montantVentilation :
                            self.SetItemImage(branchePrestation, self.img_vert, which=wx.TreeItemIcon_Normal)
                        else:
                            self.SetItemImage(branchePrestation, self.img_orange, which=wx.TreeItemIcon_Normal)
                    else:
                        self.SetItemImage(branchePrestation, self.img_rouge, which=wx.TreeItemIcon_Normal) 
                    
                    self.SortChildren(brancheIndividu)
                    
        # Suppression des anciennes prestations
        for IDprestation, categorie in listeAnciennesPrestations :
            if self.dictBranchesPrestations.has_key(IDprestation) :
                branchePrestation = self.dictBranchesPrestations[IDprestation]["branche"]
                date = self.dictBranchesPrestations[IDprestation]["date"]
                IDindividu = self.dictBranchesPrestations[IDprestation]["IDindividu"]
                self.Delete(branchePrestation)
                del self.dictBranches[categorie][date][IDindividu][IDprestation]
                del self.dictBranchesPrestations[IDprestation]
            
                # Suppression des branches individus inutiles
                if len(self.dictBranches[categorie][date][IDindividu]) == 2 :
                    if len(selectionIndividus) > 1 : 
                        self.Delete(self.dictBranches[categorie][date][IDindividu]["branche"])
                    del self.dictBranches[categorie][date][IDindividu]
                
                # Suppression des branches dates inutiles
                if len(self.dictBranches[categorie][date]) == 2 :
                    self.Delete(self.dictBranches[categorie][date]["branche"])
                    del self.dictBranches[categorie][date]
                
                # Suppression des branches cat�gories inutiles
                if len(self.dictBranches[categorie]) == 2 :
                    self.Delete(self.dictBranches[categorie]["branche"])
                    del self.dictBranches[categorie]
        
        # Calcul du total par cat�gorie
        totalCategorie = 0.0
        dictTotaux = {}
        for IDprestation, dictValeurs in self.dictBranchesPrestations.iteritems() :
            categorie = dictValeurs["categorie"]
            if dictTotaux.has_key(categorie) :
                dictTotaux[categorie] += dictValeurs["montant"]
            else:
                dictTotaux[categorie] = dictValeurs["montant"]
        for categorie, total in dictTotaux.iteritems() :
            self.SetItemText(self.dictBranches[categorie]["branche"], u"%.2f %s " % (total, SYMBOLE), 1)
        
        self.ExpandAllChildren(self.root)
    
    def OnCompareItems(self, item1, item2):
        if self.GetPyData(item1) > self.GetPyData(item2) :
            return 1
        elif self.GetPyData(item1) < self.GetPyData(item2) :
            return -1
        else:
            return 0
            
##    def CreationBrancheDate(self, categorie, date):
##        listeDates = []
##        for key in self.dictBranches[categorie].keys() :
##            if key not in ("branche", "donnee") :
##                listeDates.append(key)
##        listeDates.append(date)
##        listeDates.sort()
##        brancheCategorie = self.dictBranches[categorie]["branche"]
##        # Si cet item doit �tre premier
##        if listeDates[0] == date and len(listeDates) > 1 : 
##            brancheDate = self.InsertItemBefore(brancheCategorie, 0, DateComplete(date))
##            return brancheDate
##        # Si cet item doit �tre dernier
##        if listeDates[-1] == date : 
##            brancheDate = self.AppendItem(brancheCategorie, DateComplete(date))
##            return brancheDate
##        # Si l'item est � une autre position
##        index = 0
##        for dateTmp in listeDates :
##            if date == dateTmp :
##                previousItem = self.dictBranches[categorie][listeDates[index-1]]["branche"]
##                brancheDate = self.InsertItem(brancheCategorie, previousItem, DateComplete(date))
##                return brancheDate
##            index += 1
            
    def RechercheBranche(self, type=None, date=None, IDindividu=None, IDprestation=None):
        if self.dictBranches.has_key(type) :
            # Renvoie la branche du type
            if date == None : return self.dictBranches[type]["branche"]
            if self.dictBranches[type].has_key(date) :
                # Renvoie la branche de la date
                if IDindividu == None : return self.dictBranches[type][date]["branche"]
                if self.dictBranches[type][date].has_key(IDindividu) :
                    # Renvoie la branche de l'individu
                    if IDprestation == None : return self.dictBranches[type][date][IDindividu]["branche"]
                    # Renvoie la branche de la prestation
                    if self.dictBranches[type][date][IDindividu].has_key(IDprestation) :
                        return self.dictBranches[type][date][IDindividu][IDprestation]["branche"]
        return None
        
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
            
    def OnContextMenu(self, event):
        pos = event.GetPosition()
        item, flags, col = self.HitTest(pos)
        
        if col != -1 :
            self.SelectItem(item)
        
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Cr�er une prestation"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        item = self.GetSelection()
        IDprestation = self.RechercherIDprestation(item)
        
        if col != -1 and IDprestation != None :
            
            menuPop.AppendSeparator()

            # Item Ajouter
            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
            
            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
                
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        self.parent.panel_grille.grille.AjouterPrestation()
        
    def Modifier(self, event):
        item = self.GetSelection()
        IDprestation = self.RechercherIDprestation(item)
        self.parent.panel_grille.grille.ModifierPrestation(IDprestation)

    def Supprimer(self, event):
        item = self.GetSelection()
        IDprestation = self.RechercherIDprestation(item)
        categorie = self.dictBranchesPrestations[IDprestation]["categorie"]
        self.parent.panel_grille.grille.SupprimerPrestation(IDprestation, categorie)
    
    def RechercherIDprestation(self, item):
        for IDprestation, dictValeurs in self.dictBranchesPrestations.iteritems() :
            if dictValeurs["branche"] == item :
                return IDprestation
        return None
    
    def ModifiePrestation(self, date, IDindividu, IDprestation, montantVentilation=0.0, nouveauMontant=0.0, nouveauLabel=None):
        """ Fontion qui sert au tarif bas� sur le nbre d'individus de la famille pr�sents """
        # Modifie le montant
        if self.dictBranchesPrestations.has_key(IDprestation) :
            self.dictBranchesPrestations[IDprestation]["montant"] = nouveauMontant
        # Recherche de la branche Prestation
        branchePrestation = self.RechercheBranche("consommation", date, IDindividu, IDprestation)
        if branchePrestation != None :
            self.SetItemText(branchePrestation, u"%.2f %s " % (nouveauMontant, SYMBOLE), 1)
            # Coloration si prestation pay�e
            if montantVentilation > 0.0 :
                if nouveauMontant == montantVentilation :
                    self.SetItemImage(branchePrestation, self.img_vert, which=wx.TreeItemIcon_Normal)
                else:
                    self.SetItemImage(branchePrestation, self.img_orange, which=wx.TreeItemIcon_Normal)
            else:
                self.SetItemImage(branchePrestation, self.img_rouge, which=wx.TreeItemIcon_Normal) 
            # Modifie label 
            if nouveauLabel != None :
                self.SetItemText(branchePrestation, nouveauLabel, 0)

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel)
        self.myOlv.Initialisation() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

##if __name__ == '__main__':
##    app = wx.App(0)
##    #wx.InitAllImageHandlers()
##    frame_1 = MyFrame(None, -1, "OL TEST")
##    app.SetTopWindow(frame_1)
##    frame_1.Show()
##    app.MainLoop()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import DLG_Grille2 as DLG_Grille
    frame_1 = DLG_Grille.Dialog(None, IDfamille=14, selectionIndividus=[46,])
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
