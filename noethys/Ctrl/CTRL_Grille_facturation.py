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
##import wx.gizmos as gizmos
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


DICT_LABELS_CATEGORIES = {
    "consommation" : (_(u"Consommation"), _(u"Consommations")),
    "cotisation" : (_(u"Cotisation"), _(u"Cotisations")),
    "location" : (_(u"Location"), _(u"Locations")),
    "autre" : (_(u"Autre"), _(u"Autres")),
    } # Code : (Singulier, Pluriel)
            
            

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
    
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, listePrestations=[]): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(TR_COLUMN_LINES | HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.parent = parent
        
        self.SetBackgroundColour(wx.WHITE)
        
        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
        
        self.Initialisation() 
        
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_vert = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG))
        self.img_orange = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG))
        self.img_rouge = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
##        self.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnContextMenu)
    
    def Initialisation(self):               
        # Création des colonnes
        self.AddColumn(_(u"Prestations"))
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 195)
        self.AddColumn(u"")
        self.SetColumnWidth(1, 55)
        self.SetColumnAlignment(1, wx.ALIGN_RIGHT)
        
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        self.dictBranches = {}
        self.dictBranchesPrestations = {}

    
    def SaisiePrestation(self, dictPrestations, dictDeductions, listeNouvellesPrestations, listeAnciennesPrestations, selectionIndividus, listeActivites, listePeriodes):        
        # Affichage des nouvelles prestations
        for IDprestation in listeNouvellesPrestations :
            dictPrestation = dictPrestations[IDprestation]
            categorie = dictPrestation["categorie"]
            if categorie in DICT_LABELS_CATEGORIES :
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
            if montant == None :
                montant = 0.0
            IDactivite = dictPrestation["IDactivite"]
            if "montantVentilation" in dictPrestation :
                montantVentilation = dictPrestation["montantVentilation"]
            else:
                montantVentilation = 0.0
            
            if IDprestation in dictDeductions :
                if len(dictDeductions[IDprestation]) > 0 :
                    label += u"*"
            
            # Critères d'affichage
            affichePrestation = True
            # Affiche uniquement les individus sélectionnés
            if IDindividu not in selectionIndividus and IDindividu != 0 :
                affichePrestation = False
            # Affiche uniquement les activités sélectionnées
            if IDactivite not in listeActivites and IDactivite != None :
                affichePrestation = False
            # Affiche uniquement les périodes sélectionnées
            afficheTemp = False
            for date_debut, date_fin in listePeriodes :
                if date >= date_debut and date <= date_fin :
                    afficheTemp = True
            if afficheTemp == False :
                affichePrestation = False
            
            if affichePrestation == True :
            
                # Recherche de la branche Catégorie
                brancheCategorie = self.RechercheBranche(categorie)
                if brancheCategorie == None :
                    brancheCategorie = self.AppendItem(self.root, labelCategorie)
                    self.SetPyData(brancheCategorie, labelCategorie)
                    self.SetItemBackgroundColour(brancheCategorie, wx.Colour(200, 200, 200) )
                    self.SetItemTextColour(brancheCategorie, wx.Colour(120, 120, 120) )
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
                    # Coloration si prestation payée
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
            if IDprestation in self.dictBranchesPrestations :
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
                
                # Suppression des branches catégories inutiles
                if len(self.dictBranches[categorie]) == 2 :
                    self.Delete(self.dictBranches[categorie]["branche"])
                    del self.dictBranches[categorie]
        
        # Calcul du total par catégorie
        totalCategorie = 0.0
        dictTotaux = {}
        for IDprestation, dictValeurs in self.dictBranchesPrestations.items() :
            categorie = dictValeurs["categorie"]
            if categorie in dictTotaux :
                dictTotaux[categorie] += dictValeurs["montant"]
            else:
                dictTotaux[categorie] = dictValeurs["montant"]
        for categorie, total in dictTotaux.items() :
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
##        # Si cet item doit être premier
##        if listeDates[0] == date and len(listeDates) > 1 : 
##            brancheDate = self.InsertItemBefore(brancheCategorie, 0, DateComplete(date))
##            return brancheDate
##        # Si cet item doit être dernier
##        if listeDates[-1] == date : 
##            brancheDate = self.AppendItem(brancheCategorie, DateComplete(date))
##            return brancheDate
##        # Si l'item est à une autre position
##        index = 0
##        for dateTmp in listeDates :
##            if date == dateTmp :
##                previousItem = self.dictBranches[categorie][listeDates[index-1]]["branche"]
##                brancheDate = self.InsertItem(brancheCategorie, previousItem, DateComplete(date))
##                return brancheDate
##            index += 1
            
    def RechercheBranche(self, type=None, date=None, IDindividu=None, IDprestation=None):
        if type in self.dictBranches :
            # Renvoie la branche du type
            if date == None : return self.dictBranches[type]["branche"]
            if date in self.dictBranches[type] :
                # Renvoie la branche de la date
                if IDindividu == None : return self.dictBranches[type][date]["branche"]
                if IDindividu in self.dictBranches[type][date] :
                    # Renvoie la branche de l'individu
                    if IDprestation == None : return self.dictBranches[type][date][IDindividu]["branche"]
                    # Renvoie la branche de la prestation
                    if IDprestation in self.dictBranches[type][date][IDindividu] :
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
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Créer une prestation"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        item = self.GetSelection()
        IDprestation = self.RechercherIDprestation(item)
        
        if col != -1 and IDprestation != None :
            
            menuPop.AppendSeparator()

            # Item Ajouter
            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
            
            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
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
        for IDprestation, dictValeurs in self.dictBranchesPrestations.items() :
            if dictValeurs["branche"] == item :
                return IDprestation
        return None
    
    def ModifiePrestation(self, date, IDindividu, IDprestation, montantVentilation=0.0, nouveauMontant=0.0, nouveauLabel=None):
        """ Fontion qui sert au tarif basé sur le nbre d'individus de la famille présents """
        # Modifie le montant
        if IDprestation in self.dictBranchesPrestations :
            self.dictBranchesPrestations[IDprestation]["montant"] = nouveauMontant
        # Recherche de la branche Prestation
        branchePrestation = self.RechercheBranche("consommation", date, IDindividu, IDprestation)
        if branchePrestation != None :
            self.SetItemText(branchePrestation, u"%.2f %s " % (nouveauMontant, SYMBOLE), 1)
            # Coloration si prestation payée
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
    from Dlg import DLG_Grille2 as DLG_Grille
    frame_1 = DLG_Grille.Dialog(None, IDfamille=14, selectionIndividus=[46,])
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
