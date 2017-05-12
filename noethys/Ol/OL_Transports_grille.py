#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Utils import UTILS_Historique
from Utils import UTILS_Transports

from Ctrl.CTRL_Saisie_transport import DICT_CATEGORIES


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))



        
class Track(object):
    def __init__(self, donnees, modLocalisation):
        self.dictDonnees = donnees
        
        self.IDtransport = donnees["IDtransport"]
        self.IDindividu = donnees["IDindividu"]
        self.categorie = donnees["categorie"]
        
        self.depart_dateDD = donnees["depart_date"]
##        self.depart_dateDD = DateEngEnDateDD(self.depart_date)
        self.depart_heure = donnees["depart_heure"]
        if self.depart_heure != None :
            hr, mn = self.depart_heure.split(":")
        else :
            hr, mn = 0, 0
        self.depart_dateHeure = datetime.datetime(self.depart_dateDD.year, self.depart_dateDD.month, self.depart_dateDD.day, int(hr), int(mn))
        self.depart_IDarret = donnees["depart_IDarret"]
        self.depart_IDlieu = donnees["depart_IDlieu"]
        self.depart_localisation = donnees["depart_localisation"]
        
        self.arrivee_dateDD = donnees["arrivee_date"]
##        self.arrivee_dateDD = DateEngEnDateDD(self.arrivee_date)
        self.arrivee_heure = donnees["arrivee_heure"]
        if self.arrivee_heure != None :
            hr, mn = self.arrivee_heure.split(":")
        else :
            hr, mn = 0, 0
        self.arrivee_dateHeure = datetime.datetime(self.arrivee_dateDD.year, self.arrivee_dateDD.month, self.arrivee_dateDD.day, int(hr), int(mn))
        self.arrivee_IDarret = donnees["arrivee_IDarret"]
        self.arrivee_IDlieu = donnees["arrivee_IDlieu"]
        self.arrivee_localisation = donnees["arrivee_localisation"]
        
        # Analyse des localisations
        self.depart_nom = modLocalisation.Analyse(self.depart_IDarret, self.depart_IDlieu, self.depart_localisation)
        self.arrivee_nom = modLocalisation.Analyse(self.arrivee_IDarret, self.arrivee_IDlieu, self.arrivee_localisation)

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.grid = kwds.pop("grid", None)
        self.IDindividu = kwds.pop("IDindividu", None)
        self.date = kwds.pop("date", None)
        self.dictTransports = kwds.pop("dictTransports", {})
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
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
        modLocalisation = UTILS_Transports.AnalyseLocalisation() 
        
        listeListeView = []
        for IDtransport, item in self.dictTransports.iteritems() :
            track = Track(item, modLocalisation)
            listeListeView.append(track)
            if self.selectionID == IDtransport :
                self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Image list
        for code, valeurs in DICT_CATEGORIES.iteritems() :
            img = self.AddNamedImages(code, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s.png" % valeurs["image"]), wx.BITMAP_TYPE_PNG))
        
        def GetImageCategorie(track):
            return track.categorie

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        def FormateDateHeure(dateDT):
            date = FormateDateCourt(datetime.date(dateDT.year, dateDT.month, dateDT.day))
            heure = U"%dh%02d" % (dateDT.hour, dateDT.minute)
            if heure == "0h00" : heure = u""
            return u"%s %s" % (date, heure)

        def FormateCategorie(categorie):
            return DICT_CATEGORIES[categorie]["label"]

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDtransport", typeDonnee="entier"), 
            ColumnDefn(_(u"Transport"), "left", 80, "categorie", typeDonnee="texte", stringConverter=FormateCategorie,  imageGetter=GetImageCategorie),
            ColumnDefn(_(u"Départ"), 'left', 130, "depart_dateHeure", typeDonnee="texte", stringConverter=FormateDateHeure),
            ColumnDefn(_(u"Origine"), 'left', 120, "depart_nom", typeDonnee="texte"),
            ColumnDefn(_(u"Arrivée"), 'left', 130, "arrivee_dateHeure", typeDonnee="texte", stringConverter=FormateDateHeure),
            ColumnDefn(_(u"Destination"), 'left', 120, "arrivee_nom", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun transport"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
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
            ID = self.Selection()[0].IDtransport
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
            
        menuPop.AppendSeparator()

        # Item Modifier
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

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donnée à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des transports"), format="A", orientation=wx.PORTRAIT)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des transports"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des transports"))

    def Ajouter(self, event):
        from Dlg import DLG_Saisie_transport
        dlg = DLG_Saisie_transport.Dialog(self, IDindividu=self.IDindividu, modeVirtuel=True, verrouilleBoutons=True) 
        dlg.SetDateObligatoire(self.date) 
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDictDonnees()
            IDtransport = self.grid.RechercheProchainIDtransport()
            dictDonnees["IDtransport"] = IDtransport
            dictDonnees["mode"] = "TRANSP"
            self.dictTransports[IDtransport] = dictDonnees
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun transport à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dictDonnees = track.dictDonnees
        IDtransport = dictDonnees["IDtransport"]
        from Dlg import DLG_Saisie_transport
        dlg = DLG_Saisie_transport.Dialog(self, IDtransport=IDtransport, IDindividu=self.IDindividu, modeVirtuel=True, dictDonnees=dictDonnees, verrouilleBoutons=True)    
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDictDonnees()
            dictDonnees["etat"] = "MODIF"
            dictDonnees["mode"] = "TRANSP"
            self.dictTransports[IDtransport] = dictDonnees
            self.MAJ(IDtransport)
        dlg.Destroy() 

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun transport à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDtransport = self.Selection()[0].IDtransport
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce transport ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            del self.dictTransports[IDtransport]
            self.MAJ() 
        dlg.Destroy()

    def GetDictTransports(self):
        return self.dictTransports
    
    
# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un transport..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_reglements
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
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
        self.myOlv = ListView(panel, id=-1, IDindividu=46, date=datetime.date(2011, 4, 13), name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
