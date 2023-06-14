#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHING

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")



def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


#-----------INDIVIDUS-----------

class Track(object):
    def __init__(self, donnees):
        self.label = donnees[0]
        self.IDactivite = donnees[1]
        self.nomActivite = donnees[2]
        self.nombre = donnees[3]
        self.montant = donnees[4]
        self.commentaire = u""


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Variables
        self.date_debut = None
        self.date_fin = None
        self.dateNaiss = None
        self.listeActivites = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """

        # Récupération des conditions
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        
        if self.dateNaiss != None :
            conditionDateNaiss = "AND individus.date_naiss >= '%s' " % self.dateNaiss
        else:
            conditionDateNaiss = ""
            
        DB = GestionDB.DB()
        # Recherche des prestations
        req = """SELECT prestations.label, prestations.IDactivite, activites.nom, COUNT(prestations.IDprestation), SUM(prestations.montant)
        FROM prestations
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE prestations.IDactivite IN %s
        AND (prestations.date>='%s' AND prestations.date<='%s')
        AND prestations.categorie='consommation'
        %s
        GROUP BY prestations.label, prestations.IDactivite
        ;""" % (conditionActivites, self.date_debut, self.date_fin, conditionDateNaiss)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()  
        DB.Close() 
        listeListeView = []
        for item in listePrestations :
            track = Track(item)
            listeListeView.append(track)
        return listeListeView

    def InitObjectListView(self):

        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(_(u"Prestation"), 'left', 250, "label", typeDonnee="texte", isSpaceFilling=True, isEditable=False),
            ColumnDefn(_(u"Commentaire"), "left", 150, "commentaire", typeDonnee="texte", isEditable=True), 
            ColumnDefn(_(u"Activité"), "left", 120, "nomActivite", typeDonnee="texte", isEditable=False), 
            ColumnDefn(_(u"Qté"), "left", 50, "nombre", typeDonnee="entier", isEditable=False), 
            ColumnDefn(_(u"Total"), "left", 90, "montant", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),
            ]
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)

        self.SetEmptyListMsg(_(u"Aucune prestation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

        self.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK # ObjectListView.CELLEDIT_DOUBLECLICK
       
    def MAJ(self, date_debut=None, date_fin=None, dateNaiss=None, listeActivites=[]):
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.dateNaiss = dateNaiss
        self.listeActivites = listeActivites
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 
        self.CocheTout()

    def Selection(self):
        return self.GetSelectedObjects()
    
    def CocheTout(self, event=None):
        for track in self.donnees :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def GetInfosCoches(self):
        listeDonnees = []
        for track in self.GetTracksCoches() :
            dictTemp = track.GetDict()
            for code, valeur in self.dictOrganisme.items() :
                dictTemp[code] = valeur
            listeDonnees.append(dictTemp)
        return listeDonnees
    
    def GetDonnees(self):
        listeDonnees = []
        for track in self.GetTracksCoches() :
            listeDonnees.append({"label":track.label, "IDactivite":track.IDactivite, "commentaire":track.commentaire})
        return listeDonnees
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
                
        # Tout sélectionner
        item = wx.MenuItem(menuPop, 20, _(u"Tout sélectionner"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=20)

        # Tout dé-sélectionner
        item = wx.MenuItem(menuPop, 30, _(u"Tout dé-sélectionner"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=30)
        
        menuPop.AppendSeparator()
        
        # Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des prestations"), intro="", total="", format="A", orientation=wx.LANDSCAPE)
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
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des prestations"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des prestations"))


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
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(
            date_debut = datetime.date(2012, 1, 1),
            date_fin = datetime.date(2012, 12, 31),
            dateNaiss=None,#datetime.date(2006, 1, 1),
            listeActivites=[1, 2, 4, 5, 6, 7, 8],
            )
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
