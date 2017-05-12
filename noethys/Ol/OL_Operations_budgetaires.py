#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Dlg import DLG_Saisie_operation_budgetaire
import datetime

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs
from Utils import UTILS_Dates


class Track(object):
    def __init__(self, donnees):
        self.IDoperation_budgetaire = donnees["IDoperation_budgetaire"]
        self.typeOperation = donnees["typeOperation"]
        self.date_budget = donnees["date_budget"]
        self.IDcategorie = donnees["IDcategorie"]
        self.IDanalytique = donnees["IDanalytique"]
        self.libelle = donnees["libelle"]
        self.montant = donnees["montant"]
        self.label_categorie = donnees["label_categorie"]
        self.label_analytique = donnees["label_analytique"]
        
        if self.typeOperation == "debit" :
            self.debit = self.montant
            self.credit = None
        else :
            self.debit = None
            self.credit = self.montant
            




class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
            
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        db = GestionDB.DB()
        req = """SELECT 
        IDoperation_budgetaire, compta_operations_budgetaires.type, date_budget, compta_operations_budgetaires.IDcategorie, compta_operations_budgetaires.IDanalytique, libelle, montant,
        compta_categories.nom, compta_analytiques.nom
        FROM compta_operations_budgetaires 
        LEFT JOIN compta_categories ON compta_categories.IDcategorie = compta_operations_budgetaires.IDcategorie
        LEFT JOIN compta_analytiques ON compta_analytiques.IDanalytique = compta_operations_budgetaires.IDanalytique
        ORDER BY date_budget, IDoperation_budgetaire
        ;""" 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeListeView = []
        for IDoperation_budgetaire, typeOperation, date_budget, IDcategorie, IDanalytique, libelle, montant, label_categorie, label_analytique in listeDonnees :
            date_budget = UTILS_Dates.DateEngEnDateDD(date_budget)
            dictTemp = {
                "IDoperation_budgetaire" : IDoperation_budgetaire, "typeOperation" : typeOperation, "date_budget" : date_budget, "IDcategorie" : IDcategorie, 
                "IDanalytique" : IDanalytique, "libelle" : libelle, "montant" : montant, "label_categorie" : label_categorie, "label_analytique" : label_analytique, 
                }
            track = Track(dictTemp)
            listeListeView.append(track)
        
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def rowFormatter(listItem, track):
            if track.date_budget > datetime.date.today() :
                listItem.SetTextColour((180, 180, 180))

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDoperation_budgetaire", typeDonnee="entier"),
            ColumnDefn(_(u"Date Budget"), 'left', 120, "date_budget", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Analytique"), "left", 160, "label_analytique", typeDonnee="texte"),
            ColumnDefn(_(u"Catégorie"), "left", 160, "label_categorie", typeDonnee="texte"),
            ColumnDefn(_(u"Libellé"), "left", 120, "libelle", typeDonnee="texte", isSpaceFilling=True),
            #ColumnDefn(_(u"Montant"), "right", 100, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Débit"), "right", 80, "debit", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Crédit"), "right", 80, "credit", typeDonnee="montant", stringConverter=FormateMontant),
            ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune opération budgétaire"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDoperation_budgetaire=None):
        self.Freeze()
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if IDoperation_budgetaire != None :
            for trackTemp in self.donnees :
                if trackTemp.IDoperation_budgetaire == IDoperation_budgetaire :
                    self.SelectObject(trackTemp, deselectOthers=True, ensureVisible=True)
                    break
        # MAJ listctrl
        self._ResizeSpaceFillingColumns() 
        self.Thaw() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDoperation_budgetaire
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter une opération au débit"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Addition.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.AjouterDebit, id=10)

        item = wx.MenuItem(menuPop, 11, _(u"Ajouter une opération au crédit"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Addition.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.AjouterCredit, id=11)

        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)

        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des opérations budgétaires"), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des opérations budgétaires"), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des opérations budgétaires"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des opérations budgétaires"))

    def AjouterDebit(self, event):
        self.Ajouter("debit")

    def AjouterCredit(self, event):
        self.Ajouter("credit")

    def Ajouter(self, typeOperation="credit"):
        dlg = DLG_Saisie_operation_budgetaire.Dialog(self, typeOperation=typeOperation)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDoperation_budgetaire=dlg.GetIDoperation_budgetaire())
        dlg.Destroy()

    def Modifier(self, event):
##        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_comptables", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune opération budgétaire à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie_operation_budgetaire.Dialog(self, typeOperation=track.typeOperation, IDoperation_budgetaire=track.IDoperation_budgetaire)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDoperation_budgetaire=dlg.GetIDoperation_budgetaire())
        dlg.Destroy()

    def Supprimer(self, event):
##        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_comptables", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune opération budgétaire à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]            
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette opération budgétaire ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("compta_operations_budgetaires", "IDoperation_budgetaire", track.IDoperation_budgetaire)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    

### -------------------------------------------------------------------------------------------------------------------------------------------
##
##class ListviewAvecFooter(PanelAvecFooter):
##    def __init__(self, parent, kwargs={}):
##        dictColonnes = {
##            "nomTiers" : {"mode" : "nombre", "singulier" : _(u"opération"), "pluriel" : _(u"opérations"), "alignement" : wx.ALIGN_CENTER},
##            "libelle" : {"mode" : "texte", "texte" : _(u"Solde du jour : 10000.00 €"), "alignement" : wx.ALIGN_CENTER},
##            "solde" : {"mode" : "total"},
##            }
##        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)
##
### -------------------------------------------------------------------------------------------------------------------------------------------


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        self.ctrl_operations = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)        
        self.ctrl_operations.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_operations, 1, wx.ALL|wx.EXPAND)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 500))
        


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
