#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import decimal
import GestionDB
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Dates


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

                
  
class Track(object):
    def __init__(self, parent, dictValeurs, index):
        self.index = index
        self.parent = parent
        self.dictValeurs = dictValeurs
        self.IDconso = dictValeurs["IDconso"]
        self.date = dictValeurs["date"]
        self.IDunite = dictValeurs["IDunite"]
        self.heure_debut = dictValeurs["heure_debut"]
        self.heure_fin = dictValeurs["heure_fin"]
        self.quantite = dictValeurs["quantite"]
        self.etat = dictValeurs["etat"]
        
        self.nomUnite = parent.dictUnites[self.IDunite]["nom"]
        
        self.texteDetail = ""
        if self.heure_debut != None and self.heure_fin != None :
            self.texteDetail = "%s-%s" % (self.heure_debut, self.heure_fin)
        if self.quantite != None :
            self.texteDetail += _(u" Qté=%d") % self.quantite
        
        if self.etat == "reservation" : 
            self.texteEtat = _(u"Réservation")
        elif self.etat == "present" : 
            self.texteEtat = _(u"Présent")
        elif self.etat == "attente" : 
            self.texteEtat = _(u"Attente")
        elif self.etat == "absenti" : 
            self.texteEtat = _(u"Absence injustifiée")
        elif self.etat == "absentj" : 
            self.texteEtat = _(u"Absence justifiée")
        elif self.etat == "refus" : 
            self.texteEtat = _(u"Refus")
        else :
            self.texteEtat = ""
            
# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDactivite = kwds.pop("IDactivite", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.listeDonnees = []
        self.dictUnites = self.Importation_unites() 
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.donnees = []
        self.InitObjectListView()

    def Importation_unites(self):
        # Récupération des unités
        DB = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        dictUnites = {}
        for IDunite, nom, abrege, type, heure_debut, heure_fin in listeDonnees :
            dictUnites[IDunite] = {"nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "unites_incompatibles" : []}

        # Récupère les incompatibilités entre unités
        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
        FROM unites_incompat;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
            if dictUnites.has_key(IDunite) : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if dictUnites.has_key(IDunite_incompatible) : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)

        return dictUnites

    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = []
        index = 0
        for dictPeriode in self.listeDonnees :
            track = Track(self, dictPeriode, index)
            self.donnees.append(track)
            index += 1
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        liste_Colonnes = [
            ColumnDefn(_(u"IDconso"), "left", 0, "IDconso", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'centre', 75, "date", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Unité"), 'left', 70, "nomUnite", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Etat"), 'left', 50, "texteEtat", typeDonnee="texte"),
            ColumnDefn(_(u"Détail"), 'left', 100, "texteDetail", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune consommation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(2)
        
    def MAJ(self):
        self.InitModel()
        self.SetObjects(self.donnees)
        self._ResizeSpaceFillingColumns() 

    def SetDonnees(self, listeDonnees={}):
        self.listeDonnees = listeDonnees
        self.MAJ() 
    
    def GetDonnees(self):
        return self.listeDonnees
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

##        # Item Assistant
##        item = wx.MenuItem(menuPop, 100, _(u"Générer automatiquement des consommations"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Magique.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Generer, id=100)
##                
##        menuPop.AppendSeparator()
##
##        # Item Modifier
##        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
##
##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
##        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()

        # Item Tout cocher
        item = wx.MenuItem(menuPop, 70, _(u"Tout cocher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=70)

        # Item Tout décocher
        item = wx.MenuItem(menuPop, 80, _(u"Tout décocher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Decocher.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=80)

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des consommations"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des consommations"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des consommations"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des consommations"), autoriseSelections=False)

    def Generer(self, event):  
        pass
##        date_debut = self.GetGrandParent().ctrl_date_debut.GetDate()
##        date_fin = self.GetGrandParent().ctrl_date_fin.GetDate()
##        listePeriodes = self.GetDonnees() 
##        from Dlg import DLG_Saisie_contrat_conso
##        dlg = DLG_Saisie_contrat_conso.Dialog(self, IDactivite=self.IDactivite, date_debut=date_debut, date_fin=date_fin, listePeriodes=listePeriodes)
##        if dlg.ShowModal() == wx.ID_OK:
##            listePeriodes = dlg.GetListePeriodes()
##            self.SetDonnees(listePeriodes)
##        dlg.Destroy()

    def Ajouter(self, event):  
        pass
##        from Dlg import DLG_Saisie_contrat_periode
##        dlg = DLG_Saisie_contrat_periode.Dialog(self, IDactivite=self.IDactivite, listeTracks=self.donnees)
##        if dlg.ShowModal() == wx.ID_OK:
##            dictDonnees = dlg.GetDonnees() 
##            self.listeDonnees.append(dictDonnees)
##            self.MAJ() 
##        dlg.Destroy()
        
    def Modifier(self, event):  
        pass
##        if len(self.Selection()) == 0 :
##            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune période à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
##        track = self.Selection()[0]
##        from Dlg import DLG_Saisie_contrat_periode
##        dlg = DLG_Saisie_contrat_periode.Dialog(self, IDactivite=self.IDactivite, track=track, listeTracks=self.donnees)
##        if dlg.ShowModal() == wx.ID_OK:
##            self.listeDonnees[track.index] = dlg.GetDonnees() 
##            self.MAJ() 
##        dlg.Destroy()

    def Supprimer(self, event):  
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune consommation à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les consommations cochées ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()        
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la consommation sélectionnée ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Suppression
        listeSuppressions = []
        for track in listeSelections :
            if track.etat in ("present", "absenti", "absentj") :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la consommation '%s' du %s car elle est déjà pointée !") % (track.nomUnite, UTILS_Dates.DateDDEnFr(track.date)) , _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

            listeSuppressions.append(track.index)
            
            if track.IDconso != None :
                self.GetGrandParent().GetGrandParent().GetParent().listeSuppressionConso.append(track.IDconso)
        
        nouvelleListe = []
        index = 0
        for dictConso in self.listeDonnees :
            if index not in listeSuppressions :
                nouvelleListe.append(dictConso)
            index += 1
        self.listeDonnees = nouvelleListe
        self.MAJ() 

    def CocheTout(self, event=None):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_soldes
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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomUnite" : {"mode" : "nombre", "singulier" : _(u"consommation"), "pluriel" : _(u"consommations"), "alignement" : wx.ALIGN_LEFT},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        ctrl = ListviewAvecFooter(panel, kwargs={"IDactivite" : 1}) 
        listview = ctrl.GetListview()
        listview.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(ctrl, 1, wx.ALL|wx.EXPAND, 10)
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
