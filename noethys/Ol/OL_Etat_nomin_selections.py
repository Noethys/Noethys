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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
import OL_Etat_nomin_champs



class Track(object):
    def __init__(self, donnees):
        self.IDselection = donnees["IDselection"]
        self.IDprofil = donnees["IDprofil"]
        self.code = donnees["code"]
        self.ordre = donnees["ordre"]
        self.label = donnees["label"]
        self.titre = donnees["titre"]
        self.type = donnees["type"]
        self.categorie = donnees["categorie"]
        self.formule = donnees["formule"]
        
        # Largeur de colonne
        if donnees.has_key("largeur") :
            self.largeur = donnees["largeur"]
        else :
            self.largeur = 100


# ----------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.IDprofil = None
        self.dateMin = None
        self.dateMax = None
        self.listeActivites = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
    
    def SetParametres(self, IDprofil=None, dateMin=None, dateMax=None, listeActivites=[]):
        self.IDprofil = IDprofil
        self.dateMin = dateMin
        self.dateMax = dateMax
        self.listeActivites = listeActivites
    
    def OnItemActivated(self,event):
        self.Modifier(None)

    def InitModel(self):
        self.donnees = self.GetTracks()
        
    def GetTracks(self):
        # Récupération des champs disponibles
        champs = OL_Etat_nomin_champs.Champs(listeActivites=self.listeActivites, dateMin=self.dateMin, dateMax=self.dateMax)
        self.dictChamps = champs.GetDictChamps() 
        self.listeChampsDispo = champs.GetChamps() 

        # Récupération des champs sélectionnés du profil
        DB = GestionDB.DB()
        req = """SELECT IDselection, IDprofil, code, ordre
        FROM etat_nomin_selections
        WHERE IDprofil=%d
        ORDER BY ordre
        ;""" % self.IDprofil
        DB.ExecuterReq(req)
        listeSelectionChamps = DB.ResultatReq()     
        DB.Close() 
        
        listeListeView = []
        for IDselection, IDprofil, code, ordre in listeSelectionChamps :
            if self.dictChamps.has_key(code) :
                # Champ disponible
                trackInfo = self.dictChamps[code]
                dictTemp = {"IDselection":IDselection, "IDprofil":IDprofil, "code":code, "ordre":ordre, "label":trackInfo.label, "type":trackInfo.type, "categorie":trackInfo.categorie, "formule":trackInfo.formule, "titre":trackInfo.titre, "largeur":trackInfo.largeur}
            else :
                # Champ indisponible
                dictTemp = {"IDselection":IDselection, "IDprofil":IDprofil, "code":code, "ordre":ordre, "label":_(u"Non disponible"), "type":None, "categorie":None, "titre":None, "formule":None}
            listeListeView.append(Track(dictTemp))

        return listeListeView

    def InitObjectListView(self):           
        # ImageList 
        self.AddNamedImages("individu", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Personnes.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("famille", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("unite", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etiquette.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("perso", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("euro", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("formule", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Formule.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("temps", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Horloge3.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("indisponible", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit2.png"), wx.BITMAP_TYPE_PNG))
        
        def GetImageCode(track):
            if track.categorie == _(u"Individu") : return "individu"
            if track.categorie == _(u"Famille") : return "famille"
            if track.type == _(u"NBRE_UNITE") : return "unite"
            if track.type == _(u"TEMPS_UNITE") : return "temps"
            if track.type == _(u"MONTANT_PRESTATION") : return "euro"
            if track.type == _(u"NBRE_AIDES") : return "unite"
            if track.type == _(u"MONTANT_AIDES") : return "euro"
            if track.type == _(u"PERSO") : return "perso"
            if track.type == None : return "indisponible"
            return None

        def GetImageFormule(track):
            if len(track.formule) > 0 :
                return "formule"
            else :
                return None

        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDselection"),
            ColumnDefn(_(u"Ordre"), "left", 0, "ordre"),
            ColumnDefn(_(u"Code"), "left", 200, "code", imageGetter=GetImageCode), 
            ColumnDefn(_(u"Description"), 'left', 250, "label", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun champ"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if ID != None :
            for track in self.donnees :
                if track.IDselection == ID :
                    self.SelectObject(track, deselectOthers=True, ensureVisible=True)
        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier la liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        
        menuPop.AppendSeparator()
        
        # Item Deplacer vers le haut
        item = wx.MenuItem(menuPop, 60, _(u"Déplacer vers le haut"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=60)
        if noSelection == True : item.Enable(False)
        
        # Item Déplacer vers le bas
        item = wx.MenuItem(menuPop, 70, _(u"Déplacer vers le bas"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=70)
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des champs"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des champs"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des champs"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des champs"))
    
    def GetTracksSelections(self):
        """ Retourne la liste tracks sélectionnés """
        listeTracks = []
        for track in self.donnees :
            listeTracks.append(track)
        return listeTracks
    
    def GetListeChampsDispo(self):
        return self.listeChampsDispo
    
    def Modifier(self, event):
        listeTracksSelections = self.GetTracksSelections() 
        listeCodesSelections = []
        for track in listeTracksSelections :
            listeCodesSelections.append(track.code)
        from Dlg import DLG_Etat_nomin_champs
        dlg = DLG_Etat_nomin_champs.Dialog(self, listeActivites=self.listeActivites, dateMin=self.dateMin, dateMax=self.dateMax, listeSelections=listeCodesSelections)
        if dlg.ShowModal() == wx.ID_OK:
            listeNewSelections = dlg.GetCodesChamps() 
            DB = GestionDB.DB()
            # Ajout de champs
            ordre = len(self.donnees)
            for code in listeNewSelections :
                if code not in listeCodesSelections :
                    ordre = len(listeCodesSelections) + 1
                    IDselection = DB.ReqInsert("etat_nomin_selections", [ ("IDprofil", self.IDprofil), ("code", code), ("ordre", ordre)])
                    listeCodesSelections.append(code)
            # Suppression de champ
            for track in listeTracksSelections :
                if track.code not in listeNewSelections :
                    DB.ReqDEL("etat_nomin_selections", "IDselection", track.IDselection)
            DB.Close()
            # MAJ de l'affichage
            self.MAJ()
            self.MAJordre() 
            self.MAJ()
        dlg.Destroy()
        
        

    def MAJordre(self, IDselection=None):
        DB = GestionDB.DB()
        ordre = 1
        for index in range(0, len(self.donnees)) :
            objet = self.GetObjectAt(index)
            if objet.IDselection != IDselection :
                DB.ReqMAJ("etat_nomin_selections", [("ordre", ordre),], "IDselection", objet.IDselection)
                ordre += 1
        DB.Close()

    def Monter(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun champ dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        ordre = track.ordre
        if ordre == 1 : return
        DB = GestionDB.DB()
        # Modifie champ actuel
        DB.ReqMAJ("etat_nomin_selections", [("ordre", ordre-1),], "IDselection", track.IDselection)
        track.ordre = ordre-1
        # Modifie champ a remplacer
        index = self.GetIndexOf(track)
        track2 = self.GetObjectAt(index-1)
        IDselection2 = track2.IDselection
        DB.ReqMAJ("etat_nomin_selections", [("ordre", ordre),], "IDselection", IDselection2)
        DB.Close()
        self.MAJ(track.IDselection)
    
    def Descendre(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun champ dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        ordre = track.ordre
        if ordre == len(self.donnees) : return
        DB = GestionDB.DB()
        # Modifie champ actuel
        DB.ReqMAJ("etat_nomin_selections", [("ordre", ordre+1),], "IDselection", track.IDselection)
        track.ordre = ordre+1
        # Modifie champ a remplacer
        index = self.GetIndexOf(track)
        track2 = self.GetObjectAt(index+1)
        IDselection2 = track2.IDselection
        DB.ReqMAJ("etat_nomin_selections", [("ordre", ordre),], "IDselection", IDselection2)
        DB.Close()
        self.MAJ(track.IDselection)
    
            
        

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un champ..."))
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((600, 600))
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.SetParametres(IDprofil=3, dateMin=datetime.date(2012, 01, 01), dateMax=datetime.date(2012, 12, 31), listeActivites=[1, 2, 3, 4])
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
