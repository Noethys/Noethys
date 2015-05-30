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
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass


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


        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.inclus = kwds.pop("inclus", True)
        self.selectionPossible = kwds.pop("selectionPossible", True)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.tracks = []
        self.numColonneTri = 0
        self.ordreAscendant = True
        self.labelParametres = ""
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        if self.selectionPossible == True :
            self.Deplacer()
    
    def Deplacer(self):
        if len(self.Selection()) == 0 :
            if self.inclus == True :
                message = _(u"Vous devez d'abord sélectionner une cotisation à retirer du dépôt !")
            else:
                message = _(u"Vous devez d'abord sélectionner une cotisation disponible à ajouter au dépôt !")
            dlg = wx.MessageDialog(self, message, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        if self.inclus == True :
            track.inclus = False
        else:
            track.inclus = True
        index = self.GetIndexOf(track)
        if index == len(self.donnees)-1 :
            if len(self.donnees) > 1 :
                nextTrack = self.GetObjectAt(index-1)
            else:
                nextTrack = None
        else:
            nextTrack = self.GetObjectAt(index+1)
        self.GetParent().MAJListes(self.tracks, selectionTrack=track, nextTrack=nextTrack)
        
    def InitModel(self, tracks=None):
        if tracks != None :
            self.tracks = tracks
        listeTracks = []
        for track in self.tracks :
            if track.inclus == self.inclus :
                listeTracks.append(track)
        self.donnees = listeTracks
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        imgOk = self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        imgPasOk = self.AddNamedImages("pasok", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageCreation(track):
            if track.date_creation_carte == None : return "pasok"
            else: return "ok" 

        def GetImageDepot(track):
            if track.IDdepot_cotisation == None : return "pasok"
            else: return "ok" 
        
        def FormateDate(dateDD):
            if dateDD == None : return ""
            if dateDD == "2999-01-01" : return _(u"Illimitée")
            date = str(dateDD)
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))
        
        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDcotisation", typeDonnee="entier"),
            ColumnDefn(u"Du", 'left', 70, "date_debut", typeDonnee="date", stringConverter=FormateDate), 
            ColumnDefn(_(u"au"), 'left', 70, "date_fin", typeDonnee="date", stringConverter=FormateDate), 
            ColumnDefn(_(u"Famille"), 'left', 130, "nomTitulaires", typeDonnee="texte"), 
            ColumnDefn(_(u"Type"), 'left', 150, "typeStr", typeDonnee="texte"),
            ColumnDefn(_(u"Nom"), 'left', 270, "nomCotisation", typeDonnee="texte"),
            ColumnDefn(_(u"Numéro"), 'left', 80, "numero", typeDonnee="texte"), 
            ColumnDefn(_(u"Création carte"), 'left', 100, "date_creation_carte", typeDonnee="date", stringConverter=FormateDate, imageGetter=GetImageCreation), 
##            ColumnDefn(_(u"Dépôt carte"), 'left', 100, "depotStr", imageGetter=GetImageDepot), 
            ]
        
        self.SetColumns(liste_Colonnes)
        if self.inclus == True :
            self.SetEmptyListMsg(_(u"Aucune cotisation dans ce dépôt"))
        else:
            self.SetEmptyListMsg(_(u"Aucune cotisation disponible"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
##        self.SetSortColumn(self.columns[self.numColonneTri])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self, tracks=None, ID=None, selectionTrack=None, nextTrack=None, labelParametres=""):
        self.labelParametres = labelParametres
        self.InitModel(tracks)
        self.InitObjectListView()
        # Sélection d'un item
        if selectionTrack != None :
            self.SelectObject(selectionTrack, deselectOthers=True, ensureVisible=True)
            if self.GetSelectedObject() == None :
                self.SelectObject(nextTrack, deselectOthers=True, ensureVisible=True)
                
##        if ID == None :
##            self.DefileDernier() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDcotisation
                
        # Création du menu contextuel
        menuPop = wx.Menu()

##        # Item Modifier
##        item = wx.MenuItem(menuPop, 10, _(u"Modifier"))
##        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Modifier, id=10)
##        if noSelection == True : item.Enable(False)
##                
##        # Item Supprimer
##        item = wx.MenuItem(menuPop, 20, _(u"Supprimer"))
##        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
##        if noSelection == True : item.Enable(False)
##                
##        menuPop.AppendSeparator()
    
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
        txtIntro = self.labelParametres
        txtTotal = _(u"%d cotisations") % len(self.donnees)
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des cotisations"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
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
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des cotisations"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des cotisations"))

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDcotisation = track.IDcotisation
        import DLG_Saisie_cotisation
        dlg = DLG_Saisie_cotisation.Dialog(self, IDcompte_payeur=None, IDcotisation=IDcotisation)      
        if dlg.ShowModal() == wx.ID_OK:
            if self.GetParent().GetName() == "DLG_Saisie_depot_cotisation" :
                self.MAJ(selectionTrack=track) 
            if self.GetParent().GetName() == "DLG_Saisie_depot_cotisation_ajouter" :
                self.GetParent().MAJListes(self.tracks, selectionTrack=track)
        dlg.Destroy() 

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcotisation = self.Selection()[0].IDcotisation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette cotisation ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("cotisations", "IDcotisation", IDcotisation)
            DB.Close() 
            self.GetParent().MAJListes(self.tracks)
        dlg.Destroy()












# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une cotisation..."))
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
        self.myOlv = ListView(panel, id=-1, inclus=True, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
