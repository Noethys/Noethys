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
import decimal
import GestionDB
import UTILS_Dates

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import UTILS_Titulaires
import UTILS_Utilisateurs
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter


class Track(object):
    def __init__(self, parent, donnees):
        self.IDfamille = donnees["IDfamille"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]    
        if self.IDfamille != None :
            self.titulaires = parent.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.titulaires = _(u"Aucun titulaire")
        self.listeTitulaires = parent.dictTitulaires[self.IDfamille]["listeTitulaires"]
        self.total = donnees["total"]
        self.paye = donnees["paye"]
        self.impaye = donnees["impaye"]
        self.quantite = donnees["quantite"]
        self.listePrestations = donnees["prestations"]

        
                                
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.date_debut = None
        self.date_fin = None
        self.selectionID = None
        self.selectionTrack = None
        FastObjectListView.__init__(self, *args, **kwds)
        # DictTitulaires
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnActivated(self,event):
        self.Modifier(None)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        # Récupération des données
        listeID = None
        
        DB = GestionDB.DB()
        
        req = """
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, prestations.date, prestations.label, prestations.montant, IDfamille, IDfacture
        FROM prestations
        WHERE date>='%s' AND date<='%s'
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % (self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq() 
        
        req = """
        SELECT ventilation.IDprestation, SUM(ventilation.montant) AS montant_ventilation
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        WHERE prestations.date>='%s' AND prestations.date<='%s'
        GROUP BY ventilation.IDprestation
        ;""" % (self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq() 
        dictVentilation = {}
        for IDprestation, montantVentilation in listeVentilation :
            dictVentilation[IDprestation] = montantVentilation
                
        DB.Close() 
        
        dictResultats = {}
        for IDprestation, IDcompte_payeur, date, label, montant, IDfamille, IDfacture in listePrestations :
            date = UTILS_Dates.DateEngEnDateDD(date)  
            
            montant = decimal.Decimal(montant)
            if dictVentilation.has_key(IDprestation) :
                montant_ventilation = decimal.Decimal(dictVentilation[IDprestation])
            else :
                montant_ventilation = decimal.Decimal(0.0)
            paye = montant_ventilation
            impaye = montant - montant_ventilation
            
            if dictResultats.has_key(IDfamille) == False :
                dictResultats[IDfamille] = {"IDfamille" : IDfamille, "IDcompte_payeur" : IDcompte_payeur, "prestations" : [], "quantite" : 0, "total" : decimal.Decimal(0.0), "paye" : decimal.Decimal(0.0), "impaye" : decimal.Decimal(0.0) }            
            
            dictResultats[IDfamille]["prestations"].append({"IDprestation" : IDprestation, "label" : label, "montant" : montant, "paye" : paye, "impaye" : impaye, "IDfamille" : IDfamille, "IDcompte_payeur" : IDcompte_payeur, "IDfacture" : IDfacture})
            dictResultats[IDfamille]["quantite"] += 1
            dictResultats[IDfamille]["total"] += montant
            dictResultats[IDfamille]["paye"] += paye
            dictResultats[IDfamille]["impaye"] += impaye
            
    
        listeListeView = []
        for IDfamille, dictTemp in dictResultats.iteritems() :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, dictTemp)
                listeListeView.append(track)
                if self.selectionID == IDfamille :
                    self.selectionTrack = track
        return listeListeView


    def InitObjectListView(self):
        # ImageList
        self.imgVert = self.AddNamedImages("vert", wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG))

        def GetImageVentilation(track):
            if track.montant == track.montant_ventilation :
                return self.imgVert
            if track.montant_ventilation == 0.0 or track.montant_ventilation == None :
                return self.imgRouge
            if track.montant_ventilation < track.montant :
                return self.imgOrange
            return self.imgRouge

        def FormateDate(dateDD):
            return UTILS_Dates.DateComplete(dateDD)

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)
                   
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour(wx.Colour(150, 150, 150))
                
        # Couleur en alternance des lignes
        self.oddRowsBackColor = wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
        self.evenRowsBackColor = "#F0FBED" # Vert
        
        # Paramètres ListView
        self.useExpansionColumn = True
        self.SetColumns([
            ColumnDefn(u"", "left", 0, "IDfamille", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), "left", 250, "titulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Nbre Prest."), "center", 80, "quantite", typeDonnee="entier"),
            ColumnDefn(_(u"Total"), "right", 80, "total", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Payé"), "right", 80, "paye", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Impayés"), "right", 80, "impaye", typeDonnee="montant", stringConverter=FormateMontant),
        ])
        self.CreateCheckStateColumn(0)
        self.SetSortColumn(self.columns[2])
        self.SetEmptyListMsg(_(u"Aucune prestation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetObjects(self.donnees)
    
    def GetListeIndividus(self):
        return self.listeIndividus
    
    def GetListeActivites(self):
        return self.listeActivites
    
    def GetListeFactures(self):
        return self.listeFactures
    
    def GetTotal(self):
        return self.total 
    
    def SetPeriode(self, date_debut=None, date_fin=None):
        self.date_debut = date_debut
        self.date_fin = date_fin
            
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
        self.Refresh()
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        ID = None
        if len(self.Selection()) > 0 :
            ID = self.Selection()[0].IDfamille
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        if ID == None : item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Tout cocher
        item = wx.MenuItem(menuPop, 70, _(u"Tout cocher"))
        bmp = wx.Bitmap("Images/16x16/Cocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=70)

        # Item Tout décocher
        item = wx.MenuItem(menuPop, 80, _(u"Tout décocher"))
        bmp = wx.Bitmap("Images/16x16/Decocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=80)

        menuPop.AppendSeparator()

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des prestations"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des prestations"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des prestations"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des prestations"))
        
    def CocheTout(self, event=None):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def GetListePrestations(self):
        listePrestations = []
        for track in self.GetTracksCoches() :
            for dictPrestation in track.listePrestations :
                if dictPrestation not in listePrestations :
                    listePrestations.append(dictPrestation)
        return listePrestations
        
    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, track.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ(track.IDfamille)

# -------------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_prestations
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
            "titulaires" : {"mode" : "nombre", "singulier" : _(u"famille"), "pluriel" : _(u"familles"), "alignement" : wx.ALIGN_CENTER},
            "quantite" : {"mode" : "total"},
            "total" : {"mode" : "total"},
            "paye" : {"mode" : "total"},
            "impaye" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


# ----------------- FRAME DE TEST ----------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.myOlv.SetPeriode(date_debut=datetime.date(2013, 1, 1), date_fin=datetime.date(2013, 12, 31))
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((800, 400))
        self.Layout()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "GroupListView")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
