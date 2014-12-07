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

from ObjectListView import FastObjectListView, ColumnDefn, Filter, PanelAvecFooter

import UTILS_Utilisateurs


DICT_DETAILS_DEPOTS = {}


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    if dateDD == None : return u""
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

        
class Track(object):
    def __init__(self, donnees):
        self.IDdepot_cotisation = donnees[0]
        self.date = donnees[1]
        if self.date != None :
            self.date = DateEngEnDateDD(self.date)
        self.nom = donnees[2]
        self.verrouillage = donnees[3]
        self.observations = donnees[4]
        
        self.nbre = donnees[5]
        if self.nbre == None or self.nbre == 0 :
            self.detail = u"Aucune cotisation"
        else:
            self.detail = u"%d cotisations" % self.nbre
   
##        # Détails
##        if DICT_DETAILS_DEPOTS.has_key(self.IDdepot_cotisation) :
##            dictDetails = DICT_DETAILS_DEPOTS[self.IDdepot_cotisation]
##            # Totaux du dépôt
##            self.nbre = dictDetails["nbre"]
##            self.total = dictDetails["montant"]
##            # Création du texte du détail
##            texte = u""
##            for IDmode, dictDetail in dictDetails.iteritems() :
##                if IDmode != "nbre" and IDmode != "montant" :
##                    texteDetail = u"%d %s (%.2f €), " % (dictDetail["nbre"], dictDetail["nom"], dictDetail["montant"])
##                    texte += texteDetail
##            if len(dictDetails) > 2 :
##                texte = texte[:-2]
##            self.detail = texte
##        else:
##            self.nbre = 0
##            self.total = 0.0
##            self.detail = u"Aucune cotisation"

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
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
##        self.GetDetailsDepots()
        self.donnees = self.GetTracks()
    
##    def GetDetailsDepots(self):
##        global DICT_DETAILS_DEPOTS
##        DICT_DETAILS_DEPOTS = {}
##        DB = GestionDB.DB()
##        req = """SELECT 
##        depots_cotisations.IDdepot, reglements.IDmode, modes_reglements.label,
##        SUM(reglements.montant), COUNT(reglements.IDreglement)
##        FROM depots
##        LEFT JOIN reglements ON reglements.IDdepot = depots.IDdepot
##        LEFT JOIN modes_reglements ON modes_reglements.IDmode = reglements.IDmode
##        GROUP BY depots.IDdepot, reglements.IDmode
##        """
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        
##        for IDdepot, IDmode, nom_mode, montant, nbre in listeDonnees :
##            if IDmode != None :
##                if DICT_DETAILS_DEPOTS.has_key(IDdepot) == False :
##                    DICT_DETAILS_DEPOTS[IDdepot] = {"nbre" : 0, "montant" : 0.0} 
##                if DICT_DETAILS_DEPOTS[IDdepot].has_key(IDmode) == False :
##                    DICT_DETAILS_DEPOTS[IDdepot][IDmode] = {"nom" : nom_mode, "nbre" : 0, "montant" : 0.0} 
##                DICT_DETAILS_DEPOTS[IDdepot][IDmode]["nbre"] += nbre
##                DICT_DETAILS_DEPOTS[IDdepot][IDmode]["montant"] += montant
##                DICT_DETAILS_DEPOTS[IDdepot]["nbre"] += nbre
##                DICT_DETAILS_DEPOTS[IDdepot]["montant"] += montant
                
    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        req = """SELECT 
        depots_cotisations.IDdepot_cotisation, depots_cotisations.date, depots_cotisations.nom, 
        depots_cotisations.verrouillage, depots_cotisations.observations,
        COUNT(IDcotisation) AS nbre_cotisations
        FROM depots_cotisations
        LEFT JOIN cotisations ON cotisations.IDdepot_cotisation = depots_cotisations.IDdepot_cotisation
        GROUP BY depots_cotisations.IDdepot_cotisation
        ORDER BY depots_cotisations.date;
        """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        
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
        self.imgVerrouillage = self.AddNamedImages("verrouillage", wx.Bitmap("Images/16x16/Cadenas_ferme.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageVerrouillage(track):
            if track.verrouillage == 1 :
                return self.imgVerrouillage
            else:
                return None
                    
        def FormateDateLong(dateDD):
            return DateComplete(dateDD)

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f €" % montant

        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 42, "IDdepot_cotisation", imageGetter=GetImageVerrouillage),
            ColumnDefn(u"Date", 'left', 160, "date", stringConverter=FormateDateLong),
            ColumnDefn(u"Nom", 'left', 250, "nom"),
            ColumnDefn(u"Observations", 'left', 250, "observations"),
            ColumnDefn(u"Nbre cotisations", 'centre', 100, "nbre"),
##            ColumnDefn(u"Total", 'right', 65, "total", stringConverter=FormateMontant),
##            ColumnDefn(u"Détail", 'left', 210, "detail"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun dépôt de cotisations")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDdepot_cotisation
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
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

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des dépôts de cotisations", format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des dépôts de cotisations", format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des dépôts de cotisations")
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des dépôts de cotisations")

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("cotisations_depots", "creer") == False : return
        import DLG_Saisie_depot_cotisation
        dlg = DLG_Saisie_depot_cotisation.Dialog(self, IDdepot_cotisation=None) 
        if dlg.ShowModal() == wx.ID_OK:
            IDdepot_cotisation = dlg.GetIDdepotCotisation()
            self.MAJ(IDdepot_cotisation)
            self.GetGrandParent().MAJcotisations()
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("cotisations_depots", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun dépôt de cotisations à modifier dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdepot_cotisation = self.Selection()[0].IDdepot_cotisation
        import DLG_Saisie_depot_cotisation
        dlg = DLG_Saisie_depot_cotisation.Dialog(self, IDdepot_cotisation=IDdepot_cotisation)      
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDdepot_cotisation)
            self.GetGrandParent().MAJcotisations()
        dlg.Destroy() 

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("cotisations_depots", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun dépôt de cotisations à supprimer dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdepot_cotisation = self.Selection()[0].IDdepot_cotisation
        nbre_cotisations = self.Selection()[0].nbre
        if nbre_cotisations > 0 :
            dlg = wx.MessageDialog(self, u"Des cotisations sont déjà associées à ce dépôt. Vous ne pouvez donc pas le supprimer !", u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer ce dépôt de cotisations ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("depots_cotisations", "IDdepot_cotisation", IDdepot_cotisation)
            DB.Close() 
            self.MAJ()
            self.GetGrandParent().MAJcotisations()
        dlg.Destroy()











# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un dépôt de cotisations...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_depots
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
        self.listView.Refresh() 


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nom" : {"mode" : "nombre", "singulier" : u"dépôt", "pluriel" : u"dépôts", "alignement" : wx.ALIGN_CENTER},
            "nbre" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

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
        self.SetSize((890, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
