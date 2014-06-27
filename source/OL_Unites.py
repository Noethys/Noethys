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
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter

try: import psyco; psyco.full()
except: pass


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text



class Track(object):
    def __init__(self, donnees):
        self.IDunite = donnees[0]
        self.nom = donnees[1]
        self.abrege = donnees[2]
        self.type = donnees[3]
        
        if self.type == "Unitaire" : self.type = u"Standard"
        if self.type == "Quantite" : self.type = u"Quantité"
        
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.ordre = donnees[6]
        
        if self.date_debut == "1977-01-01" and self.date_fin == "2999-01-01" :
            self.periode_validite = u"Illimitée"
        else:
            self.periode_validite = u"Du %s au %s" % (DateEngFr(self.date_debut), DateEngFr(self.date_fin))
        
        
    
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
        listeID = None
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, date_debut, date_fin, ordre
        FROM unites 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
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
        
        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 0, "IDunite"),
            ColumnDefn(u"Ordre", "left", 70, "ordre"),
            ColumnDefn(u"Nom", 'left', 200, "nom"),
            ColumnDefn(u"Abrégé", "left", 60, "abrege"), 
            ColumnDefn(u"Type", "left", 60, "type"), 
            ColumnDefn(u"Période de validité", "left", 200, "periode_validite"), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucune unité de consommation")
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
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDunite
                
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
        
        # Item Deplacer vers le haut
        item = wx.MenuItem(menuPop, 40, u"Déplacer vers le haut")
        bmp = wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)

        # Item Déplacer vers le bas
        item = wx.MenuItem(menuPop, 50, u"Déplacer vers le bas")
        bmp = wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        
                
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 60, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=60)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 70, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=70)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des unités", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des unités", format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        import DLG_Saisie_unite
        dlg = DLG_Saisie_unite.Dialog(self, IDactivite=self.IDactivite, IDunite=None)
        if dlg.ShowModal() == wx.ID_OK:
            IDunite = dlg.GetIDunite()
            self.MAJ(IDunite)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune unité à modifier dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite = self.Selection()[0].IDunite
        import DLG_Saisie_unite
        dlg = DLG_Saisie_unite.Dialog(self, IDactivite=self.IDactivite, IDunite=IDunite)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDunite)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune unité à supprimer dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite = self.Selection()[0].IDunite
        
        # Vérifie que l'unité n'est pas déjà attribuée à une unité de remplissage
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDunite_remplissage)
        FROM unites_remplissage_unites 
        WHERE IDunite=%d
        ;""" % IDunite
        DB.ExecuterReq(req)
        nbreUnites = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreUnites > 0 :
            dlg = wx.MessageDialog(self, u"Cette unité de consommation a déjà été attribuée à %d unité(s) de remplissage.\n\nVous ne pouvez donc pas la supprimer !" % nbreUnites, u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que l'unité n'est pas déjà attribuée à une ouverture
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDouverture)
        FROM ouvertures 
        WHERE IDunite=%d
        ;""" % IDunite
        DB.ExecuterReq(req)
        nbreOuvertures = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreOuvertures > 0 :
            dlg = wx.MessageDialog(self, u"Cette unité de consommation a déjà été attribuée à %d ouverture(s).\n\nVous ne pouvez donc pas la supprimer !" % nbreOuvertures, u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que l'unité n'est pas déjà attribuée à un tarif
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDcombi_tarif)
        FROM combi_tarifs_unites 
        WHERE IDunite=%d
        ;""" % IDunite
        DB.ExecuterReq(req)
        nbreCombiTarifs = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreCombiTarifs > 0 :
            dlg = wx.MessageDialog(self, u"Cette unité de consommation a déjà été attribuée à une ou plusieurs combinaisons de tarifs.\n\nVous ne pouvez donc pas la supprimer !", u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que l'unité n'est pas déjà attribuée à une aide
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDaide_combi_unite)
        FROM aides_combi_unites 
        WHERE IDunite=%d
        ;""" % IDunite
        DB.ExecuterReq(req)
        nbreCombiAides = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreCombiAides > 0 :
            dlg = wx.MessageDialog(self, u"Cette unité de consommation a déjà été attribuée à une ou plusieurs combinaisons d'aides journalières.\n\nVous ne pouvez donc pas la supprimer !", u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Confirmation de suppression
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer cette unité ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("unites", "IDunite", IDunite)
            DB.ReqDEL("unites_groupes", "IDunite", IDunite)
            DB.ReqDEL("unites_incompat", "IDunite", IDunite)
            DB.Close() 
            self.MAJordre(IDunite)
            self.MAJ()
        dlg.Destroy()
    
    def MAJordre(self, IDunite=None):
        DB = GestionDB.DB()
        ordre = 1
        for index in range(0, len(self.donnees)) :
            objet = self.GetObjectAt(index)
            if objet.IDunite != IDunite :
                DB.ReqMAJ("unites", [("ordre", ordre),], "IDunite", objet.IDunite)
                ordre += 1
        DB.Close()

    def Monter(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune unité dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite = self.Selection()[0].IDunite
        ordre = self.Selection()[0].ordre
        if ordre == 1 : return
        DB = GestionDB.DB()
        # Modifie unite actuelle
        DB.ReqMAJ("unites", [("ordre", ordre-1),], "IDunite", IDunite)
        self.Selection()[0].ordre = ordre-1
        # Modifie unite a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        unite2 = self.GetObjectAt(index-1)
        IDunite2 = unite2.IDunite
        DB.ReqMAJ("unites", [("ordre", ordre),], "IDunite", IDunite2)
        DB.Close()
        self.MAJ(IDunite)
    
    def Descendre(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune unité dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite = self.Selection()[0].IDunite
        ordre = self.Selection()[0].ordre
        if ordre == len(self.donnees) : return
        DB = GestionDB.DB()
        # Modifie unite actuelle
        DB.ReqMAJ("unites", [("ordre", ordre+1),], "IDunite", IDunite)
        self.Selection()[0].ordre = ordre+1
        # Modifie unite a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        unite2 = self.GetObjectAt(index+1)
        IDunite2 = unite2.IDunite
        DB.ReqMAJ("unites", [("ordre", ordre),], "IDunite", IDunite2)
        DB.Close()
        self.MAJ(IDunite)











# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher une unité")
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
        self.myOlv = ListView(panel, IDactivite=1, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
