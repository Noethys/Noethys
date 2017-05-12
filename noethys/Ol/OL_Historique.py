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
from Utils import UTILS_Titulaires


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
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

        
class Track(object):
    def __init__(self, parent, donnees):
        self.IDaction = donnees[0]
        # Date
        self.date = donnees[1]
        self.heure = donnees[2]
        self.dateHeure = "%s|%s" % (self.date, self.heure)
        # Utilisateur
        self.IDutilisateur = donnees[3]
        self.nom_utilisateur = donnees[8]
        if self.nom_utilisateur == None : 
            self.nom_utilisateur = u""
        self.prenom_utilisateur = donnees[9]
        if self.prenom_utilisateur == None : 
            self.prenom_utilisateur = u""
        self.nomComplet_utilisateur = u"%s %s" % (self.nom_utilisateur, self.prenom_utilisateur)
        # Famille
        self.IDfamille = donnees[4]
        if self.IDfamille != None :
            if parent.titulaires.has_key(self.IDfamille) :
                self.nomTitulaires = parent.titulaires[self.IDfamille]["titulairesSansCivilite"]
            else:
                self.nomTitulaires = _(u"Aucun titulaire")
        else:
            self.nomTitulaires = u""
        # Individu
        self.IDindividu = donnees[5]
        self.nom_individu = donnees[10]
        if self.nom_individu == None : 
            self.nom_individu = u""
        self.prenom_individu = donnees[11]
        if self.prenom_individu == None : 
            self.prenom_individu = u""
        if self.IDindividu != None :
            self.nomComplet_individu = u"%s %s" % (self.nom_individu, self.prenom_individu)
        else:
            self.nomComplet_individu = u""
        # Catégorie
        self.IDcategorie = donnees[6]
        if UTILS_Historique.CATEGORIES.has_key(self.IDcategorie) :
            self.nomCategorie = UTILS_Historique.CATEGORIES[self.IDcategorie]
        else :
            self.nomCategorie = u""
        # Texte de l'action
        self.action = donnees[7]
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.IDindividu = kwds.pop("IDindividu", None)
        self.IDutilisateur = kwds.pop("IDutilisateur", None)
        self.IDcategorie = kwds.pop("IDcategorie", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
##        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.titulaires = UTILS_Titulaires.GetTitulaires() 
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        listeCriteres = []
        if self.IDfamille != None : listeCriteres.append("historique.IDfamille=%d" % self.IDfamille)
        if self.IDindividu != None : listeCriteres.append("historique.IDindividu=%d" % self.IDindividu)
        if self.IDutilisateur != None : listeCriteres.append("historique.IDutilisateur=%d" % self.IDutilisateur)
        if self.IDcategorie != None : listeCriteres.append("historique.IDcategorie=%d" % self.IDcategorie)
        if len(listeCriteres) == 0 :
            criteres = ""
        elif len(listeCriteres) == 1 :
            criteres = "WHERE %s" % listeCriteres[0]
        else:
            criteres = "WHERE %s" % " AND ".join(listeCriteres)
        DB = GestionDB.DB()
        req = """SELECT 
        historique.IDaction, historique.date, historique.heure, historique.IDutilisateur, 
        historique.IDfamille, historique.IDindividu, historique.IDcategorie, historique.action,
        utilisateurs.nom, utilisateurs.prenom,
        individus.nom, individus.prenom
        FROM historique
        LEFT JOIN utilisateurs ON utilisateurs.IDutilisateur = historique.IDutilisateur
        LEFT JOIN individus ON individus.IDindividu = historique.IDindividu
        %s
        ORDER BY historique.date, historique.heure""" % criteres
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                    
        def FormateDate(dateHeureStr):
            dateStr, heure = dateHeureStr.split("|")
            return DateEngFr(dateStr)
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDaction", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'center', 70, "dateHeure", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Heure"), 'center', 60, "heure", typeDonnee="texte"),
            ColumnDefn(_(u"Utilisateur"), 'left', 130, "nomComplet_utilisateur", typeDonnee="texte"),
            ColumnDefn(_(u"Famille"), 'left', 120, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Individu"), 'left', 120, "nomComplet_individu", typeDonnee="texte"),
            ColumnDefn(_(u"Catégorie"), 'left', 150, "nomCategorie", typeDonnee="texte"),
            ColumnDefn(_(u"Action"), 'left', 700, "action", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun historique"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
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
        
        # Envoie des données au Timeline
        try :
            self.GetParent().MAJ_timeline(self.donnees)
        except : 
            pass

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = wx.Menu()
    
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Historique"), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Historique"), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Historique"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Historique"))

    def SetUtilisateur(self, IDutilisateur=None):
        self.IDutilisateur = IDutilisateur
        self.MAJ() 

    def SetCategorie(self, IDcategorie=None):
        self.IDcategorie = IDcategorie
        self.MAJ() 

    def SetFamille(self, IDfamille=None):
        self.IDfamille = IDfamille
        self.MAJ() 

    def SetIndividu(self, IDindividu=None):
        self.IDindividu = IDindividu
        self.MAJ() 


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une action..."))
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
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
