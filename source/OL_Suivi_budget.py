#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import DLG_Saisie_categorie_budget
import datetime

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import GroupListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter




class Analyse():
    def __init__(self, dictBudget={}):
        self.dictBudget = dictBudget
        
    def GetValeurs(self):
        self.dictChamps = {}
        
        DB = GestionDB.DB() 
        
        # Récupération des consommations
        req = """SELECT IDunite, COUNT(IDconso)
        FROM consommations
        WHERE date >='%s' AND date <='%s'
        GROUP BY IDunite
        ;""" % (self.dictBudget["date_debut"], self.dictBudget["date_fin"])
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDunite, nbreConso in listeDonnees :
            nomChamp = "{NBRE_UNITE_%d}" % IDunite
            self.dictChamps[nomChamp] = nbreConso
        
        # Condition analytiques
        if len(self.dictBudget["analytiques"]) == 0 : conditionAnalytiques = ""
        elif len(self.dictBudget["analytiques"]) == 1 : conditionAnalytiques = "(%d)" % self.dictBudget["analytiques"][0]
        else : conditionAnalytiques = str(tuple(self.dictBudget["analytiques"]))
        
        listeCategoriesUtilisees = []
        
        # Récupération des opérations de trésorerie
        req = """SELECT IDcategorie, SUM(montant)
        FROM compta_ventilation
        WHERE date_budget>='%s' AND date_budget<='%s' AND IDanalytique IN %s
        GROUP BY IDcategorie
        ;""" % (self.dictBudget["date_debut"], self.dictBudget["date_fin"], conditionAnalytiques)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictOperationsTresorerie = {}
        for IDcategorie, montant in listeDonnees :
            dictOperationsTresorerie[IDcategorie] = montant       
            if IDcategorie not in listeCategoriesUtilisees :
                listeCategoriesUtilisees.append(IDcategorie) 

        # Récupération des opérations budgétaires
        req = """SELECT IDcategorie, SUM(montant)
        FROM compta_operations_budgetaires
        WHERE date_budget>='%s' AND date_budget<='%s' AND IDanalytique IN %s
        GROUP BY IDcategorie
        ;""" % (self.dictBudget["date_debut"], self.dictBudget["date_fin"], conditionAnalytiques)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictOperationsBudgetaires = {}
        for IDcategorie, montant in listeDonnees :
            dictOperationsBudgetaires[IDcategorie] = montant        
            if IDcategorie not in listeCategoriesUtilisees :
                listeCategoriesUtilisees.append(IDcategorie) 

        # Récupéraion des infos sur les catégories
        req = """SELECT IDcategorie, type, nom, abrege
        FROM compta_categories;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictInfosCategories = {}
        for IDcategorie, typeCategorie, nom, abrege in listeDonnees :
            dictInfosCategories[IDcategorie] = {"typeCategorie" : typeCategorie, "nom" : nom, "abrege" : abrege}        
        
        # Récupération des catégories budgétaires
        req = """SELECT IDcategorie_budget, type, IDcategorie, valeur
        FROM compta_categories_budget
        WHERE IDbudget=%d
        ORDER BY type
        ;""" % self.dictBudget["IDbudget"]
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        listeCategories = []
        listeIDcategories = []
        totalPlafond = 0.0
        totalRealise = 0.0
        totalSolde = 0.0
        for IDcategorie_budget, typeCategorie, IDcategorie, valeur in listeDonnees :
            plafond = self.CalculePlafond(valeur)
            
            realise = 0.0
            if dictOperationsTresorerie.has_key(IDcategorie) :
                realise += dictOperationsTresorerie[IDcategorie]
            if dictOperationsBudgetaires.has_key(IDcategorie) :
                realise += dictOperationsBudgetaires[IDcategorie]
                
            if typeCategorie == "debit" : 
                solde = plafond - realise
                totalPlafond -= plafond
                totalRealise -= realise
            else :
                solde = realise - plafond
                totalPlafond += plafond
                totalRealise += realise
            
            try :
                pourcentage = 100.0 * realise / plafond
            except :
                pourcentage = 0.0
            
            totalSolde += solde 
            
            listeIDcategories.append(IDcategorie)
            listeCategories.append({
                "IDcategorie_budget" : IDcategorie_budget, "typeCategorie" : typeCategorie, 
                "IDcategorie" : IDcategorie, "valeur" : valeur, "nomCategorie" : dictInfosCategories[IDcategorie]["nom"],
                "plafond" : plafond, "realise" : realise, "solde" : solde, "pourcentage" : pourcentage,
                })

        DB.Close() 
        
        # Catégories non budgétées
        if self.dictBudget["inclure_toutes_categories"] == True :
            
            for IDcategorie in listeCategoriesUtilisees :
                if IDcategorie not in listeIDcategories :
                    typeCategorie = dictInfosCategories[IDcategorie]["typeCategorie"]
                    
                    realise = 0.0
                    if dictOperationsBudgetaires.has_key(IDcategorie) :
                        realise += dictOperationsBudgetaires[IDcategorie]
                    if dictOperationsTresorerie.has_key(IDcategorie) :
                        realise += dictOperationsTresorerie[IDcategorie]

                    if typeCategorie == "debit" : 
                        solde = - realise
                        totalRealise -= realise
                    else :
                        solde = realise
                        totalRealise += realise
                    totalSolde += solde 
                    
                    listeCategories.append({
                        "IDcategorie_budget" : None, "typeCategorie" : typeCategorie, 
                        "IDcategorie" : IDcategorie, "valeur" : 0.0, "nomCategorie" : dictInfosCategories[IDcategorie]["nom"],
                        "plafond" : 0.0, "realise" : realise, "solde" : solde, "pourcentage" : None,
                        })
        
        # Total
        try :
            pourcentage = 100.0 * totalRealise / totalPlafond
        except :
            pourcentage = None
            
        listeCategories.append({
            "IDcategorie_budget" : None, "typeCategorie" : "total", 
            "IDcategorie" : None, "valeur" : None, "nomCategorie" : _(u"Total"),
            "plafond" : totalPlafond, "realise" : totalRealise, "solde" : totalSolde,
            "pourcentage" : pourcentage,
            })

        return listeCategories
        
    def CalculePlafond(self, valeur=""):
        """ Calcule du montant plafond de la catégorie """
        # Remplacement des champs
        for nomChamp, valChamp in self.dictChamps.iteritems() :
            valeur = valeur.replace(nomChamp, str(valChamp))
        # Calcul et formatage de la valeur
        try :
            exec("""resultat = float(%s)""" % valeur)
        except Exception, err :
            resultat = 0.0
            print "Erreur dans categorie budgetaire : ", err
        return resultat
        
        


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Track(object):
    def __init__(self, donnees):
        self.IDcategorie_budget = donnees["IDcategorie_budget"]
        self.typeCategorie = donnees["typeCategorie"]
        self.IDcategorie = donnees["IDcategorie"]
        self.valeur = donnees["valeur"]
        self.nomCategorie = donnees["nomCategorie"]
        self.plafond = donnees["plafond"]
        self.realise = donnees["realise"]
        self.solde = donnees["solde"]
        self.pourcentage = donnees["pourcentage"]
        
        

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListView(GroupListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.listeTracks = []
        self.dictBudget = None
        # Initialisation du listCtrl
        GroupListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
    
    def SetDictBudget(self, dictBudget=None):
        self.dictBudget = dictBudget
        
    def InitModel(self):
        self.donnees = []
        
        # Importation des catégories
        if self.dictBudget == None :
            return
        analyse = Analyse(self.dictBudget)
        listeCategories = analyse.GetValeurs() 

        listeTracks = []
        for dictCategorie in listeCategories :
            listeTracks.append(Track(dictCategorie))
        self.donnees = listeTracks

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateMontant(valeur):
            if valeur == None : return u""
            try :
                montant = float(valeur)
                return u"%.2f %s" % (float(valeur), SYMBOLE)
            except :
                return valeur
        
        def FormateEcart(valeur):
            if valeur == None : return u""
            if valeur > 0.0 :
                return u"+%.2f %s" % (float(valeur), SYMBOLE)
            else :
                return u"%.2f %s" % (float(valeur), SYMBOLE)

        def FormatePourcentage(valeur):
            if valeur == None : return u""
            return u"%.1f %%" % float(valeur)

        def FormateType(valeur):
            if valeur == "credit" : return _(u"Crédit")
            if valeur == "debit" : return _(u"Débit")
            if valeur == "total" : return _(u"Total")
            
            
        liste_Colonnes = [
##            ColumnDefn(u"", "left", 0, "IDcategorie_budget"),
            ColumnDefn(_(u"Catégorie budgétaire"), "left", 200, "nomCategorie", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Type"), "left", 50, "typeCategorie", typeDonnee="texte", stringConverter=FormateType),
            ColumnDefn(_(u"Réel"), "right", 80, "realise", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Budgété"), "right", 80, "plafond", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Pourcent."), "right", 80, "pourcentage", stringConverter=FormatePourcentage),
            ColumnDefn(_(u"Ecart"), "right", 80, "solde", typeDonnee="montant", stringConverter=FormateEcart),
            ]
        self.SetColumns(liste_Colonnes)
        
        # Regroupement
        self.SetAlwaysGroupByColumn(2)
        self.SetShowGroups(True)
        self.useExpansionColumn = True
        self.SetShowItemCounts(False)

        self.SetEmptyListMsg(_(u"Aucune catégorie budgétaire"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

    def MAJ(self, ID=None):
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = wx.Menu()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)

        menuPop.AppendSeparator()

        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des catégories budgétaires"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des catégories budgétaires"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des catégories budgétaires"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des catégories budgétaires"))


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 

# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "realise" : {"mode" : "total"},
            "plafond" : {"mode" : "total"},
            "solde" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        
        self.listviewAvecFooter = ListviewAvecFooter(panel) 
        self.ctrl = self.listviewAvecFooter.GetListview()
        
        dictBudget = {
            "IDbudget" : 1,
            "inclure_toutes_categories" : True,
            "date_debut" : datetime.date(2015, 1, 1),
            "date_fin" : datetime.date(2015, 12, 31),
            "analytiques" : (1, 2),
            }
        self.ctrl.SetDictBudget(dictBudget)
        self.ctrl.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.listviewAvecFooter, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
