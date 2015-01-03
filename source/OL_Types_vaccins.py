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

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs


DICT_MALADIES = {}
DICT_LIENS_MALADIES = {}



def FormatDuree(duree):
    posM = duree.find("m")
    posA = duree.find("a")
    jours = int(duree[1:posM-1])
    mois = int(duree[posM+1:posA-1])
    annees = int(duree[posA+1:])
    
    listItems = []
    if jours == 1:
        textJours = u"%d jour" % jours
        listItems.append(textJours)
    if jours > 1:
        textJours = u"%d jours" % jours
        listItems.append(textJours)
    if mois > 0:
        textMois = u"%d mois" % mois
        listItems.append(textMois)
    if annees == 1:
        textAnnees = u"%d année" % annees
        listItems.append(textAnnees)
    if annees > 1:
        textAnnees = u"%d années" % annees
        listItems.append(textAnnees)

    nbreItems = len(listItems)
    if nbreItems == 0:
        resultat = u"Validité illimitée"
    else:
        if nbreItems == 1:
            resultat = listItems[0]
        if nbreItems == 2:
            resultat = listItems[0] + " et " + listItems[1]
        if nbreItems == 3:
            resultat = listItems[0] + ", " + listItems[1] + " et " + listItems[2]

    return resultat



class Track(object):
    def __init__(self, donnees):
        self.IDtype_vaccin = donnees[0]
        self.nom = donnees[1]
        # Durée de validité
        self.duree_validite = donnees[2]
        self.txt_duree_validite = FormatDuree(self.duree_validite)
        # Maladies associées
        self.txt_maladies_associees = ""
        if DICT_LIENS_MALADIES.has_key(self.IDtype_vaccin) :
            self.listeMaladiesAssociees = DICT_LIENS_MALADIES[self.IDtype_vaccin]
            for IDtype_maladie in self.listeMaladiesAssociees :
                self.txt_maladies_associees += DICT_MALADIES[IDtype_maladie]["nom"] + ", "
            self.txt_maladies_associees = self.txt_maladies_associees[:-2]
        else:
            self.listeMaladiesAssociees = []
            
        
        
    
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
        self.SetDictMaladies() 
        self.SetDictLiens() 
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        req = """SELECT IDtype_vaccin, nom, duree_validite
        FROM types_vaccins ORDER BY nom; """ 
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
    
    def SetDictMaladies(self):
        global DICT_MALADIES
        db = GestionDB.DB()
        req = """SELECT IDtype_maladie, nom, vaccin_obligatoire
        FROM types_maladies ORDER BY nom; """ 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictMaladies = {}
        for IDtype_maladie, nom, vaccin_obligatoire in listeDonnees :
            dictMaladies[IDtype_maladie] = { "nom" : nom, "vaccin_obligatoire" : vaccin_obligatoire }
        DICT_MALADIES = dictMaladies

    def SetDictLiens(self):
        global DICT_LIENS_MALADIES
        db = GestionDB.DB()
        req = """SELECT IDvaccins_maladies, IDtype_vaccin, IDtype_maladie
        FROM vaccins_maladies; """ 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictLiensMaladies = {}
        for IDvaccins_maladies, IDtype_vaccin, IDtype_maladie in listeDonnees :
            if dictLiensMaladies.has_key(IDtype_vaccin) == False :
                dictLiensMaladies[IDtype_vaccin] = [IDtype_maladie,]
            else:
                dictLiensMaladies[IDtype_vaccin].append(IDtype_maladie)
        DICT_LIENS_MALADIES = dictLiensMaladies        
        
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 0, "IDtype_vaccin", typeDonnee="entier"),
            ColumnDefn(u"Nom du vaccin", 'left', 200, "nom", typeDonnee="texte"),
            ColumnDefn(u"Durée de validité", "left", 140, "txt_duree_validite", typeDonnee="texte"), 
            ColumnDefn(u"Maladies associées", "left", 220, "txt_maladies_associees", typeDonnee="texte"), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun vaccin")
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
            ID = self.Selection()[0].IDtype_vaccin
                
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des types de vaccins", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des types de vaccins", format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vaccins", "creer") == False : return
        import DLG_Saisie_typesVaccins
        dlg = DLG_Saisie_typesVaccins.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            validite = dlg.GetValidite()
            listeIDmaladies = dlg.GetMaladiesAssociees()
            # Sauvegarde vaccin
            DB = GestionDB.DB()
            listeDonnees = [("nom", nom ), ("duree_validite", validite),]
            IDtype_vaccin = DB.ReqInsert("types_vaccins", listeDonnees)
            # Sauvegarde Maladies associées
            for IDtype_maladie in listeIDmaladies :
                listeDonnees = [("IDtype_vaccin", IDtype_vaccin), ("IDtype_maladie", IDtype_maladie),]
                IDvaccins_maladies = DB.ReqInsert("vaccins_maladies", listeDonnees)
            DB.Close()
            self.MAJ(IDtype_vaccin)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vaccins", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun vaccin dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDtype_vaccin = self.Selection()[0].IDtype_vaccin
        nom = self.Selection()[0].nom
        validite = self.Selection()[0].duree_validite
        ancienneListeMaladies = self.Selection()[0].listeMaladiesAssociees
        import DLG_Saisie_typesVaccins
        dlg = DLG_Saisie_typesVaccins.Dialog(self)      
        dlg.SetNom(nom)
        dlg.SetValidite(validite)
        dlg.SetMaladiesAssociees(ancienneListeMaladies)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            validite = dlg.GetValidite()
            nouvelleListeMaladies= dlg.GetMaladiesAssociees()
            # Sauvegarde vaccin
            DB = GestionDB.DB()
            listeDonnees = [("nom", nom ), ("duree_validite", validite),]
            DB.ReqMAJ("types_vaccins", listeDonnees, "IDtype_vaccin", IDtype_vaccin)
            # Sauvegarde NOUVELLES Maladies associées
            for IDtype_maladie in nouvelleListeMaladies :
                if IDtype_maladie not in ancienneListeMaladies :
                    listeDonnees = [("IDtype_vaccin", IDtype_vaccin), ("IDtype_maladie", IDtype_maladie),]
                    IDvaccins_maladies = DB.ReqInsert("vaccins_maladies", listeDonnees)
            # Effacement des anciennes maladies plus associées
            for IDtype_maladie in ancienneListeMaladies :
                if IDtype_maladie not in nouvelleListeMaladies :
                    req = "DELETE FROM vaccins_maladies WHERE IDtype_maladie=%d AND IDtype_vaccin=%d" % (IDtype_maladie, IDtype_vaccin)
                    DB.ExecuterReq(req)
                    DB.Commit()
            DB.Close()
            self.MAJ(IDtype_vaccin)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vaccins", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun vaccin dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDtype_vaccin = self.Selection()[0].IDtype_vaccin
        
        # Vérifie que ce type de vaccin n'a pas déjà été attribué à un individu
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDvaccin)
        FROM vaccins 
        WHERE IDtype_vaccin=%d
        ;""" % IDtype_vaccin
        DB.ExecuterReq(req)
        nbreVaccins = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreVaccins > 0 :
            dlg = wx.MessageDialog(self, u"Ce vaccin a déjà été attribué %d fois.\n\nVous ne pouvez donc pas le supprimer !" % nbreVaccins, u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer ce vaccin ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("types_vaccins", "IDtype_vaccin", IDtype_vaccin)
            DB.ReqDEL("vaccins_maladies", "IDtype_vaccin", IDtype_vaccin)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()













# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un vaccin...")
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
