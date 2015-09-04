#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import DLG_Saisie_operation_tresorerie
import DLG_Saisie_virement
import datetime

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs
import UTILS_Dates


class Track(object):
    def __init__(self, donnees):
        self.IDvirement = donnees["IDvirement"]
        self.IDoperation_debit = donnees["IDoperation_debit"]
        self.IDoperation_credit = donnees["IDoperation_credit"]
        self.date = donnees["date"]
        self.libelle = donnees["libelle"]
        self.montant = donnees["montant"]
        self.observations = donnees["observations"]
        self.IDreleve_debit = donnees["IDreleve_debit"]
        self.IDreleve_credit = donnees["IDreleve_credit"]
        

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.IDcompte_bancaire = kwds.pop("IDcompte_bancaire", None)
        self.ctrl_soldes = None
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
    
    def SetCompteBancaire(self, IDcompte_bancaire=None):
        self.IDcompte_bancaire = IDcompte_bancaire
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        DB = GestionDB.DB()
        
        req = """SELECT IDvirement, IDoperation_debit, IDoperation_credit
        FROM compta_virements;"""
        DB.ExecuterReq(req)
        listeVirements = DB.ResultatReq()

        req = """SELECT IDoperation, date, libelle, montant, IDreleve, IDvirement, observations
        FROM compta_operations
        WHERE IDvirement IS NOT NULL;"""
        DB.ExecuterReq(req)
        listeOperations = DB.ResultatReq()

        DB.Close()
        
        dictOperations = {}
        for IDoperation, date, libelle, montant, IDreleve, IDvirement, observations in listeOperations :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictOperations[IDoperation] = {
                "IDoperation" : IDoperation, "date" : date, "libelle" : libelle, 
                "montant" : montant, "IDreleve" : IDreleve, "IDvirement" : IDvirement, "observations" : observations, 
                }
            
        listeListeView = []
        for IDvirement, IDoperation_debit, IDoperation_credit in listeVirements :
            dictOperationDebit = dictOperations[IDoperation_debit]
            dictOperationCredit = dictOperations[IDoperation_credit]
            
            dictTemp = {
                "IDvirement" : IDvirement, "IDoperation_debit" : IDoperation_debit, "IDoperation_credit" : IDoperation_credit, 
                "date" : dictOperationDebit["date"], "libelle" : dictOperationDebit["libelle"], "montant" : dictOperationDebit["montant"], 
                "observations" : dictOperationDebit["observations"], "IDreleve_debit" : dictOperationDebit["IDreleve"],
                "IDreleve_credit" : dictOperationCredit["IDreleve"],
                }
            track = Track(dictTemp)
            listeListeView.append(track)
        
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def rowFormatter(listItem, track):
            if track.date > datetime.date.today() :
                listItem.SetTextColour((180, 180, 180))

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDvirement", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 80, "date", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Libell�"), 'left', 200, "libelle", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Montant"), "right", 80, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun virement"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, track=None, IDoperation=None, IDvirement=None):
        self.Freeze()
        self.InitModel()
        self.InitObjectListView()
        # S�lection d'un item
        if track != None :
            self.SelectObject(track, deselectOthers=True, ensureVisible=True)
        if IDoperation != None :
            for trackTemp in self.donnees :
                if trackTemp.IDoperation == IDoperation :
                    self.SelectObject(trackTemp, deselectOthers=True, ensureVisible=True)
                    break
        if IDvirement != None :
            for trackTemp in self.donnees :
                if trackTemp.IDvirement == IDvirement :
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
            ID = self.Selection()[0].IDvirement
                
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un virement"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.AjouterVirement, id=10)

        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des virements"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des virements"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des virements"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des virements"))

    def AjouterVirement(self, event):
        dlg = DLG_Saisie_virement.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDvirement=dlg.GetIDvirement())
        dlg.Destroy()
        
    def Modifier(self, event):
##        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_comptables", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun virement � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie_virement.Dialog(self, track.IDvirement)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track=track)
        dlg.Destroy()

    def Supprimer(self, event):
##        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_categories_comptables", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun virement � supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        if track.IDreleve_debit != None or track.IDreleve_debit != None :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer un virement point� sur un relev� bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce virement ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("compta_operations", "IDvirement", track.IDvirement)
            DB.ReqDEL("compta_virements", "IDvirement", track.IDvirement)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    
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



### -------------------------------------------------------------------------------------------------------------------------------------------
##
##class ListviewAvecFooter(PanelAvecFooter):
##    def __init__(self, parent, kwargs={}):
##        dictColonnes = {
##            "nomTiers" : {"mode" : "nombre", "singulier" : _(u"op�ration"), "pluriel" : _(u"op�rations"), "alignement" : wx.ALIGN_CENTER},
##            "libelle" : {"mode" : "texte", "texte" : _(u"Solde du jour : 10000.00 �"), "alignement" : wx.ALIGN_CENTER},
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

        self.ctrl_virements = ListView(panel, id=-1, IDcompte_bancaire=1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_virements.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_virements, 1, wx.ALL|wx.EXPAND)
        panel.SetSizer(sizer_2)
        self.Layout()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
