#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import GestionDB

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass


        
class Track(object):
    def __init__(self, donnees):
        self.IDdeduction = donnees["IDdeduction"]
        self.IDprestation = donnees["IDprestation"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.date = donnees["date"]
        self.montant = donnees["montant"]
        self.label = donnees["label"]
        self.IDaide = donnees["IDaide"]
        self.etat = donnees["etat"]
                        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDcompte_payeur = kwds.pop("IDcompte_payeur", None)
        self.IDprestation = kwds.pop("IDprestation", None)
        self.modificationsVirtuelles = kwds.pop("modificationsVirtuelles", True)
        self.dictDeductions = self.Importation_deductions() 
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.prochainIDdeduction = -1
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        # Modification 
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()
    
    def Importation_deductions(self):
        dictDeductions = {}
        criteres = ""
        
        if self.IDcompte_payeur != None and self.IDprestation != None :
            criteres = "WHERE IDcompte_payeur=%d AND IDprestation=%d" % (self.IDcompte_payeur, self.IDprestation)
        if self.IDcompte_payeur == None and self.IDprestation != None :
            criteres = "WHERE IDprestation=%d" % self.IDprestation
        if self.IDcompte_payeur != None and self.IDprestation == None :
            criteres = "WHERE IDcompte_payeur=%d" % self.IDcompte_payeur
            
        db = GestionDB.DB()
        req = """SELECT 
        IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide
        FROM deductions
        %s
        """ % criteres
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close() 
        for IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide in listeDonnees :
            dictTemp = {
                "IDdeduction" : IDdeduction, "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, 
                "date" : date, "montant" : montant, "label" : label, "IDaide" : IDaide, "etat" : None,
                }
            dictDeductions[IDdeduction] = dictTemp
        return dictDeductions

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        listeListeView = []
        for IDdeduction, item in self.dictDeductions.iteritems() :
            valide = True
            
            if item["etat"] == "SUPPR" : valide = False
            
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == IDdeduction :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                    
        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)
        
        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 0, "IDdeduction", typeDonnee="entier"),
            ColumnDefn(u"Montant", 'centre', 90, "montant", typeDonnee="montant", stringConverter=FormateMontant), 
            ColumnDefn(u"Label", 'left', 300, "label", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucune déduction")
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
        if ID == None :
            self.DefileDernier() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDdeduction
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
            
        menuPop.AppendSeparator()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, u"Exporter au format Texte")
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, u"Exporter au format Excel")
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des déductions", format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des déductions", format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des déductions")
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des déductions")

    def Ajouter(self, event):
        import DLG_Saisie_deduction
        dlg = DLG_Saisie_deduction.Dialog(self, IDdeduction=None)
        if dlg.ShowModal() == wx.ID_OK:
            newLabel = dlg.GetLabel()
            newMontant = dlg.GetMontant()
            if self.modificationsVirtuelles == False :
                # Ajout direct dans la base de données
                DB = GestionDB.DB()
                listeDonnees = [    
                    ("IDprestation", self.IDprestation),
                    ("IDcompte_payeur", self.IDcompte_payeur),
                    ("date", str(datetime.date.today()) ),
                    ("label", newLabel),
                    ("montant", newMontant),
                    ("IDaide", None),
                    ]
                IDdeduction = DB.ReqInsert("deductions", listeDonnees)
                DB.Close()
            else:
                # Modifications virtuelles
                IDdeduction = self.prochainIDdeduction
                self.dictDeductions[IDdeduction] = { "IDdeduction" : IDdeduction }
                self.dictDeductions[IDdeduction]["IDprestation"] = self.IDprestation
                self.dictDeductions[IDdeduction]["IDcompte_payeur"] = self.IDcompte_payeur
                self.dictDeductions[IDdeduction]["date"] = str(datetime.date.today()) 
                self.dictDeductions[IDdeduction]["label"] = newLabel
                self.dictDeductions[IDdeduction]["montant"] = newMontant
                self.dictDeductions[IDdeduction]["IDaide"] = None
                self.dictDeductions[IDdeduction]["etat"] = "AJOUT"
                self.prochainIDdeduction -= 1
        
            # MAJ du contrôle
            self.MAJ(IDdeduction)
            
            # MAJ du montant de la prestation
            self.MAJ_montant_prestation(-newMontant)

        dlg.Destroy() 
        

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune déduction à modifier dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdeduction = self.Selection()[0].IDdeduction
        label = self.Selection()[0].label
        montant = self.Selection()[0].montant
        import DLG_Saisie_deduction
        dlg = DLG_Saisie_deduction.Dialog(self, IDdeduction=IDdeduction)
        dlg.SetLabel(label)
        dlg.SetMontant(montant)
        if dlg.ShowModal() == wx.ID_OK:
            newLabel = dlg.GetLabel()
            newMontant = dlg.GetMontant()
            if self.modificationsVirtuelles == False :
                # Modification directes dans la base de données
                DB = GestionDB.DB()
                listeDonnees = [    
                    ("label", newLabel),
                    ("montant", newMontant),
                    ]
                DB.ReqMAJ("deductions", listeDonnees, "IDdeduction", IDdeduction)
                DB.Close()
            else:
                # Modifications virtuelles
                self.dictDeductions[IDdeduction]["label"] = newLabel
                self.dictDeductions[IDdeduction]["montant"] = newMontant
                self.dictDeductions[IDdeduction]["etat"] = "MODIF"
            
            # MAJ du montant de la prestation
            self.MAJ_montant_prestation(montant-newMontant)
            
        dlg.Destroy() 
        
        # MAJ du contrôle
        self.MAJ(IDdeduction)

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune déduction à supprimer dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdeduction = self.Selection()[0].IDdeduction
        montant = self.Selection()[0].montant
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer cette déduction ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            if self.modificationsVirtuelles == False :
                # Suppression dans la base de données
                DB = GestionDB.DB()
                DB.ReqDEL("deductions", "IDdeduction", IDdeduction)
                DB.Close() 
            else:
                # Suppression virtuelle
                self.dictDeductions[IDdeduction]["etat"] = "SUPPR"
            self.MAJ()
            # MAJ du montant de la prestation
            self.MAJ_montant_prestation(montant)
        dlg.Destroy()
    
    def MAJ_montant_prestation(self, montantDiff=0.0):
        """ Modification du montant dans la DLG_Saisie_prestation """
        if self.GetParent().GetName() == "DLG_Saisie_prestation" :
##            # Ancienne version
##            ctrl_montant = self.GetParent().ctrl_montant
##            montantPrestation = ctrl_montant.GetMontant() 
##            montantPrestation += montantDiff
##            ctrl_montant.SetMontant(montantPrestation)
            
            self.GetParent().OnTextMontant(None)
            
##            # Nouvelle version
##            DB = GestionDB.DB()
##            req = """SELECT IDdeduction, montant
##            FROM deductions
##            WHERE IDprestation=%d
##            """ % self.IDprestation
##            DB.ExecuterReq(req)
##            listeDonnees = DB.ResultatReq()
##            DB.Close() 
##            totalDeductions = 0.0 
##            for IDdeduction, montant in listeDonnees :
##                totalDeductions += montant
##            ctrl_montant = self.GetParent().ctrl_montant
##            montantPrestation = ctrl_montant.GetMontant() 
##            ctrl_montant.SetMontant(montantPrestation - totalDeductions)
##            print montantPrestation, totalDeductions
    
    def GetTotalDeductions(self):
        """ Est utilisée par la DLG_Saisie_prestation pour connaître le montant total des déductions """
        total = 0.0
        for IDdeduction, dictDeduction in self.dictDeductions.iteritems() :
            if dictDeduction["etat"] != "SUPPR" :
                total += dictDeduction["montant"]
        return total
        
    
    def Sauvegarde(self, IDprestation=None):
        """ Effectue une sauvegarde des données SI on est en mode MODIFICATIONS VIRTUELLES """
        DB = GestionDB.DB()
        
        for IDdeduction, dictDeduction in self.dictDeductions.iteritems() :
            IDcompte_payeur = dictDeduction["IDcompte_payeur"]
            date = dictDeduction["date"]
            label = dictDeduction["label"]
            montant = dictDeduction["montant"]
            IDaide = dictDeduction["IDaide"]
            
            listeDonnees = [    
                    ("IDprestation", IDprestation),
                    ("IDcompte_payeur", IDcompte_payeur),
                    ("date", date ),
                    ("label", label),
                    ("montant", montant),
                    ("IDaide", IDaide),
                    ]
                    
            # Ajout
            if dictDeduction["etat"] == "AJOUT" :
                IDdeduction = DB.ReqInsert("deductions", listeDonnees)
            
            # Modification
            if dictDeduction["etat"] == "MODIF" :
                DB.ReqMAJ("deductions", listeDonnees, "IDdeduction", IDdeduction)
            
            # Suppression
            if dictDeduction["etat"] == "SUPPR" :
                DB.ReqDEL("deductions", "IDdeduction", IDdeduction)
        
        DB.Close()


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher une déduction...")
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

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, IDprestation=None, IDcompte_payeur=14, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
