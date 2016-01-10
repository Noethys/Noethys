#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import UTILS_Utilisateurs
import UTILS_Dates


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



class Track(object):
    def __init__(self, donnees):
        self.IDindividu = donnees["IDindividu"]
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        if self.prenom == None : 
            self.prenom = u""
        self.nomComplet = u"%s %s" % (self.nom, self.prenom)
        self.consommations = donnees["consommations"]
        
        # Création du label des consommations
        dictDates = {}
        for dictTemp in self.consommations :
            
            # Tri des consommations par date
            date = dictTemp["date"]
            if dictDates.has_key(date) == False :
                dictDates[date] = []
            dictDates[date].append(dictTemp["abregeUnite"])
        
        listeDates = dictDates.keys()
        listeDates.sort() 
        self.nbreDates = len(listeDates)
        
        self.listeLabels = []
        for date in listeDates :
            self.listeLabels.append(u"%s (%s)" % (UTILS_Dates.DateDDEnFr(date), "+".join(dictDates[date])))
        
        self.labelConsommations = ", ".join(self.listeLabels)
            
    
    
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.periode = None
        self.listeActivites = None
        self.affichage = None
        self.concernes = False
        self.labelParametres = ""
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        if self.periode == None : return []
        
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        
        DB = GestionDB.DB()
        req = """SELECT 
        consommations.IDconso, consommations.date, consommations.IDunite,
        individus.IDindividu, individus.nom, individus.prenom,
        unites.nom, unites.abrege
        FROM consommations 
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        WHERE date>='%s' AND date<='%s' AND consommations.IDactivite IN %s AND consommations.etat='%s'
        ORDER BY consommations.IDindividu, consommations.date, unites.ordre
        ;""" % (self.periode[0], self.periode[1], conditionActivites, self.affichage)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        
        dictIndividus = {}
        for IDconso, date, IDunite, IDindividu, nom, prenom, nomUnite, abregeUnite in listeDonnees :
            if dictIndividus.has_key(IDindividu) == False :
                dictIndividus[IDindividu] = {"IDindividu" : IDindividu, "nom" : nom, "prenom" : prenom, "consommations" : [] }
            dictIndividus[IDindividu]["consommations"].append(({"IDconso" : IDconso, "date" : UTILS_Dates.DateEngEnDateDD(date), "IDunite" : IDunite, "nomUnite" : nomUnite, "abregeUnite" : abregeUnite}))
        
        listeListeView = []
        for IDindividu, dictTemp in dictIndividus.iteritems() :
            track = Track(dictTemp)
            listeListeView.append(track)
            if self.selectionID == IDindividu :
                self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDindividu", typeDonnee="entier"),
            ColumnDefn(_(u"Individu"), 'left', 200, "nomComplet", typeDonnee="texte"),
            ColumnDefn(_(u"Nbre"), 'center', 70, "nbreDates", typeDonnee="entier"),
            ColumnDefn(_(u"Absences"), "left", 450, "labelConsommations", typeDonnee="texte"),
            ]        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune absence"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SortBy(2, False)
        self.SetObjects(self.donnees)
       
    def MAJ(self, periode=None, listeActivites=None, affichage=None, labelParametres=""):
        self.periode = periode
        self.listeActivites = listeActivites
        self.affichage = affichage
        self.labelParametres = labelParametres
        self.InitModel()
        self.InitObjectListView()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDindividu
            
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

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donnée à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        intro = self.labelParametres
        total = _(u"> %d individus") % len(self.donnees)
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des absences"), intro=intro, total=total, format="A", orientation=wx.PORTRAIT)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des absences"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des absences"))


# -------------------------------------------------------------------------------------------------------------------------------------


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

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(periode=(datetime.date(2011, 1, 5), datetime.date(2014, 1, 5)), listeActivites=(1, 2, 3), affichage="absenti")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
