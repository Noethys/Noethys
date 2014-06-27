#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import UTILS_Dates
import UTILS_Titulaires

from ObjectListView import FastObjectListView, ColumnDefn, Filter


class Track(object):
    def __init__(self, donnees, dictTitulaires):
        self.IDpiece = donnees[0]
        self.date_debut = donnees[1]
        self.date_fin = donnees[2]
        self.public = donnees[3]
        self.nomPiece = donnees[4]
        self.IDindividu = donnees[5]
        self.IDfamille = donnees[6]
        self.individu_nom = donnees[7]
        self.individu_prenom = donnees[8]
        
        # Nom Individu si pièce individuelle
        if self.individu_prenom == None :
            self.individu_nom_complet = self.individu_nom
        else :
            self.individu_nom_complet = u"%s %s" % (self.individu_nom, self.individu_prenom)
        
        # Nom Famille si pièce familiale
        if self.IDfamille != None :
            self.nom_titulaires = dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.nom_titulaires = ""
            
        # Type de pièce        
        if self.public == "famille" : 
            self.nomPublic = u"Familiale"
        else :
            self.nomPublic = u"Individuelle"
            
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDtype_piece = None
        self.date_reference = None
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
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        if self.IDtype_piece == None :
            return [] 
        
        if self.date_reference != None :
            conditionDate = "AND pieces.date_debut <= '%s' AND pieces.date_fin >= '%s'" % (self.date_reference, self.date_reference)
        else :
            conditionDate = ""
            
        listeID = None
        db = GestionDB.DB()
        req = """SELECT pieces.IDpiece, pieces.date_debut, pieces.date_fin,
        types_pieces.public, types_pieces.nom, 
        individus.IDindividu, pieces.IDfamille, individus.nom, individus.prenom
        FROM pieces 
        LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        LEFT JOIN individus ON individus.IDindividu = pieces.IDindividu
        WHERE pieces.IDtype_piece = %d %s
        ORDER BY individus.nom; """ % (self.IDtype_piece, conditionDate)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item, dictTitulaires)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            if dateDD == "2999-01-01" :
                return u"Illimitée"
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        liste_Colonnes = [
            ColumnDefn(u"IDPiece", "left", 0, "IDpiece"),
            ColumnDefn(u"Individu", 'left', 170, "individu_nom_complet"),
            ColumnDefn(u"Famille", 'left', 220, "nom_titulaires"),
            ColumnDefn(u"Du", "left", 80, "date_debut", stringConverter=FormateDateCourt),
            ColumnDefn(u"Au", "left", 80, "date_fin", stringConverter=FormateDateCourt),
            ColumnDefn(u"Type de pièce", "left", 100, "nomPublic"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucune pièce")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        if len(self.donnees) > 0 :
            if self.donnees[0].public == "famille" :
                self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None, IDtype_piece=None, date_reference=None):
        self.IDtype_piece = IDtype_piece
        self.date_reference = date_reference
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
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDpiece
                
        # Création du menu contextuel
        menuPop = wx.Menu()
    
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
        import UTILS_Printer
        if len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, u"Il n'y a aucune donnée dans la liste !", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        txtIntro = u"Pièce sélectionnée : %s" % self.donnees[0].nomPiece
        txtTotal = u"Un total de %d pièces" % len(self.donnees)
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des pièces fournies", intro=txtIntro, total=txtTotal, format="A", orientation=wx.PORTRAIT)
        if mode == "preview" :
            prt.Preview()
        else :
            prt.Print()

    def Apercu(self, event=None):
        self.Impression("preview")

    def Imprimer(self, event=None):
        self.Impression("print")

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des pièces fournies")
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des pièces fournies")


# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher une pièce...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_donnees
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
        self.myOlv.MAJ() 
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
