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
import UTILS_Historique
import UTILS_Utilisateurs

from CTRL_Saisie_transport import DICT_CATEGORIES

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


DICT_ARRETS = {}
DICT_LIEUX = {}
DICT_ACTIVITES = {}
DICT_ECOLES = {}

        
class Track(object):
    def __init__(self, donnees):
        self.IDtransport = donnees[0]
        self.IDindividu = donnees[1]
        self.categorie = donnees[2]
        
        self.depart_heure = donnees[3]
        self.depart_IDarret = donnees[4]
        self.depart_IDlieu = donnees[5]
        self.depart_localisation = donnees[6]
        
        self.arrivee_heure = donnees[7]
        self.arrivee_IDarret = donnees[8]
        self.arrivee_IDlieu = donnees[9]
        self.arrivee_localisation = donnees[10]
        
        self.date_debut = DateEngEnDateDD(donnees[11])
        self.date_fin = DateEngEnDateDD(donnees[12])
        self.actif = donnees[13]
        
        # Analyse du départ
        self.depart_nom = u""
        if self.depart_IDarret != None and DICT_ARRETS.has_key(self.depart_IDarret) :
            self.depart_nom = DICT_ARRETS[self.depart_IDarret]
        if self.depart_IDlieu != None and DICT_LIEUX.has_key(self.depart_IDlieu) :
            self.depart_nom = DICT_LIEUX[self.depart_IDlieu]
        if self.depart_localisation != None :
            self.depart_nom = self.AnalyseLocalisation(self.depart_localisation)

        # Analyse de l'arrivée
        self.arrivee_nom = u""
        if self.arrivee_IDarret != None and DICT_ARRETS.has_key(self.arrivee_IDarret) :
            self.arrivee_nom = DICT_ARRETS[self.arrivee_IDarret]
        if self.arrivee_IDlieu != None and DICT_LIEUX.has_key(self.arrivee_IDlieu) :
            self.arrivee_nom = DICT_LIEUX[self.arrivee_IDlieu]
        if self.arrivee_localisation != None :
            self.arrivee_nom = self.AnalyseLocalisation(self.arrivee_localisation)

    def AnalyseLocalisation(self, texte=""):
        code = texte.split(";")[0]
        if code == "DOMI" :
            return u"Domicile"
        if code == "ECOL" :
            IDecole = int(texte.split(";")[1])
            if DICT_ECOLES.has_key(IDecole):
                return DICT_ECOLES[IDecole]
        if code == "ACTI" :
            IDactivite = int(texte.split(";")[1])
            if DICT_ACTIVITES.has_key(IDactivite):
                return DICT_ACTIVITES[IDactivite]
        if code == "AUTR" :
            code, nom, rue, cp, ville = texte.split(";")
            return u"%s %s %s %s" % (nom, rue, cp, ville)
        return u""


    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", "IDindividu")
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
        self.GetAutresDonnees() 
        self.donnees = self.GetTracks()

    def GetAutresDonnees(self):
        global DICT_ARRETS, DICT_LIEUX, DICT_ACTIVITES, DICT_ECOLES
        DB = GestionDB.DB()
        
        # Arrêts
        req = """SELECT IDarret, nom FROM transports_arrets;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DICT_ARRETS = {}
        for IDarret, nom in listeDonnees :
            DICT_ARRETS[IDarret] = nom
            
        # Lieux
        req = """SELECT IDlieu, nom FROM transports_lieux;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DICT_LIEUX = {}
        for IDlieu, nom in listeDonnees :
            DICT_LIEUX[IDlieu] = nom
        
        # Activités
        req = """SELECT IDactivite, nom FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DICT_ACTIVITES = {}
        for IDactivite, nom in listeDonnees :
            DICT_ACTIVITES[IDactivite] = nom

        # Ecoles
        req = """SELECT IDecole, nom FROM ecoles;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DICT_ECOLES = {}
        for IDecole, nom in listeDonnees :
            DICT_ECOLES[IDecole] = nom

        DB.Close()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        DB = GestionDB.DB()
        req = """SELECT IDtransport, IDindividu, categorie, 
        depart_heure, depart_IDarret, depart_IDlieu, depart_localisation,
        arrivee_heure, arrivee_IDarret, arrivee_IDlieu, arrivee_localisation,
        date_debut, date_fin, actif
        FROM transports
        WHERE mode='PROG' AND IDindividu=%d
        ;""" % self.IDindividu
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
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Image list
        for code, valeurs in DICT_CATEGORIES.iteritems() :
            img = self.AddNamedImages(code, wx.Bitmap("Images/16x16/%s.png" % valeurs["image"], wx.BITMAP_TYPE_PNG))

        def rowFormatter(listItem, track):
            if track.actif == 0 or (track.date_debut >= datetime.date.today() and track.date_fin <= datetime.date.today()) :
                listItem.SetTextColour((180, 180, 180))

        def GetImageCategorie(track):
            return track.categorie

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        def FormateHeure(heure):
            if heure == "00:00" or heure == None : return ""
            return heure.replace(":", "h")

        def FormateCategorie(categorie):
            return DICT_CATEGORIES[categorie]["label"]

        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 0, "IDtransport", typeDonnee="entier"), 
            ColumnDefn(u"Transport", "left", 70, "categorie", typeDonnee="texte", stringConverter=FormateCategorie,  imageGetter=GetImageCategorie),
            ColumnDefn(u"Du", 'left', 80, "date_debut", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(u"Au", 'left', 80, "date_fin", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(u"Départ", 'center', 50, "depart_heure", typeDonnee="texte", stringConverter=FormateHeure),
            ColumnDefn(u"Origine", 'left', 110, "depart_nom", typeDonnee="texte"),
            ColumnDefn(u"Arrivée", 'center', 50, "arrivee_heure", typeDonnee="texte", stringConverter=FormateHeure),
            ColumnDefn(u"Destination", 'left', 110, "arrivee_nom", typeDonnee="texte"),
            ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun transport programmé")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
        self.Refresh()
        
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

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, u"Il n'y a aucune donnée à imprimer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des transports programmés", format="A", orientation=wx.PORTRAIT)
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
        UTILS_Export.ExportTexte(self, titre=u"Liste des transports programmés")
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des transports programmés")

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_prog_transports", "creer") == False : return
        import DLG_Saisie_transport
        dlg = DLG_Saisie_transport.Dialog_prog(self, IDindividu=self.IDindividu) 
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_prog_transports", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun transport à modifier dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDtransport = self.Selection()[0].IDtransport
        import DLG_Saisie_transport
        dlg = DLG_Saisie_transport.Dialog_prog(self, IDtransport=IDtransport, IDindividu=self.IDindividu)      
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDtransport)
        dlg.Destroy() 

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_prog_transports", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun transport à supprimer dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDtransport = self.Selection()[0].IDtransport
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer ce transport programmé ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("transports", "IDtransport", IDtransport)
            DB.Close()
            self.MAJ()
        dlg.Destroy()

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un transport...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_reglements
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
        self.myOlv = ListView(panel, id=-1, IDindividu=46, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
