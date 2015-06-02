#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import operator
import DLG_Releve_prestations_saisie

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
        
LISTE_MOIS = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))

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
        
def PeriodeComplete(mois, annee):
    periodeComplete = u"%s %d" % (LISTE_MOIS[mois-1], annee)
    return periodeComplete




class Track(object):
    def __init__(self, periode={}, index=None):
        self.periode = periode
        self.index = index
        self.selection = periode["selection"]
        self.typeDonnees = periode["type"]
        self.dictPeriode = periode["periode"]
        self.dictOptions = periode["options"]
        
        # Type
        if self.typeDonnees == "prestations" : 
            self.label_type = _(u"Prestations")
        if self.typeDonnees == "factures" : 
            self.label_type = _(u"Factures")
        
        # Période
        self.date_debut = self.dictPeriode["date_debut"]
        self.date_fin = self.dictPeriode["date_fin"]
        self.code_periode = self.dictPeriode["code"]
        self.label_periode = self.dictPeriode["label"]

        # Options
        self.listeOptions = []
                
        if self.dictOptions.has_key("impayes") and self.dictOptions["impayes"] == True :
            self.listeOptions.append(_(u"Uniquement les impayés"))
        
        if self.dictOptions.has_key("regroupement") :
            if self.dictOptions["regroupement"] == "date" :
                self.listeOptions.append(_(u"Regroupement par date"))
            if self.dictOptions["regroupement"] == "mois" :
                self.listeOptions.append(_(u"Regroupement par mois"))
            if self.dictOptions["regroupement"] == "annee" :
                self.listeOptions.append(_(u"Regroupement par année"))
                
        if self.dictOptions.has_key("conso") and self.dictOptions["conso"] == True :
            self.listeOptions.append(_(u"Détail des consommations"))
        
        self.label_options = ", ".join(self.listeOptions)



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.listePeriodes = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)

    def InitModel(self):
        # Création des tracks
        self.donnees = []
        index = 0
        for item in self.listePeriodes :
            track = Track(item, index)
            self.donnees.append(track)
            index += 1

    def InitObjectListView(self):        
        
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(_(u"Période"), 'left', 180, "label_periode", typeDonnee="entier"),
            ColumnDefn(_(u"Type"), "left", 100, "label_type", typeDonnee="texte"),
            ColumnDefn(_(u"Options"), "left", 230, "label_options", typeDonnee="texte"),
            ColumnDefn(_(u"Date de début"), "left", 0, "date_debut", typeDonnee="date"),
            ColumnDefn(_(u"Date de fin"), "left", 0, "date_fin", typeDonnee="date"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune période"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[4])
        self.SetObjects(self.donnees)
        
        # Coche
        for track in self.donnees :
            if track.selection == True :
                self.Check(track)
                self.RefreshObject(track)
       
    def MAJ(self, listePeriodes=None):
        if listePeriodes != None :
            self.listePeriodes = listePeriodes
        self.InitModel()
        self.InitObjectListView()
    
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
            listeDonnees.append(track)
        return listeDonnees
            
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Création du menu contextuel
        menuPop = wx.Menu()

        item = wx.MenuItem(menuPop, 70, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=70)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 60, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=60)
        if len(self.Selection()) == 0 : item.Enable(False)

        item = wx.MenuItem(menuPop, 80, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=80)
        if len(self.Selection()) == 0 : item.Enable(False)

        menuPop.AppendSeparator()
        
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
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
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
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des périodes"), intro="", total="", format="A", orientation=wx.LANDSCAPE)
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
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des périodes"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des périodes"))

    def Ajouter(self, event=None):
        self.MemoriseCoches() 
        dlg = DLG_Releve_prestations_saisie.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees()
            self.listePeriodes.append(dictDonnees)
            self.MAJ() 
        dlg.Destroy()
        
    def Modifier(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune période à modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.MemoriseCoches() 
        track = self.Selection()[0]
        periode = track.periode
        
        dlg = DLG_Releve_prestations_saisie.Dialog(self)
        dlg.SetTitle(_(u"Modification d'une période"))
        dlg.SetDonnees(track.periode)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees()
            self.listePeriodes[track.index] = dictDonnees
            self.MAJ() 
        dlg.Destroy()
        
    def Supprimer(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune période à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.MemoriseCoches() 
        track = self.Selection()[0]
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette période ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.listePeriodes.pop(track.index)
            self.MAJ() 
        dlg.Destroy()
        
    def MemoriseCoches(self):
        for track in self.donnees :
            etat = self.IsChecked(track)
            track.selection = etat
            self.listePeriodes[track.index]["selection"] = etat
    
    def GetListePeriodes(self):
        self.MemoriseCoches() 
        listePeriodesTemp = sorted(self.listePeriodes, key=operator.itemgetter("date_debut"), reverse=False)
        return listePeriodesTemp


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
