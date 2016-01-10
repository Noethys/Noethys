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
import GestionDB
import UTILS_Dates
import UTILS_Utilisateurs


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



def FormatDuree(validite):
    # Illimitée
    if validite == None or validite == "j0-m0-a0" :
        return _(u"Illimitée")
    
    # Durée
    if validite != None and validite.startswith("j") :
        posM = validite.find("m")
        posA = validite.find("a")
        jours = int(validite[1:posM-1])
        mois = int(validite[posM+1:posA-1])
        annees = int(validite[posA+1:])

        listItems = []
        if jours == 1:
            textJours = _(u"%d jour") % jours
            listItems.append(textJours)
        if jours > 1:
            textJours = _(u"%d jours") % jours
            listItems.append(textJours)
        if mois > 0:
            textMois = _(u"%d mois") % mois
            listItems.append(textMois)
        if annees == 1:
            textAnnees = _(u"%d année") % annees
            listItems.append(textAnnees)
        if annees > 1:
            textAnnees = _(u"%d années") % annees
            listItems.append(textAnnees)

        nbreItems = len(listItems)
        if nbreItems == 1:
            return listItems[0]
        if nbreItems == 2:
            return listItems[0] + " et " + listItems[1]
        if nbreItems == 3:
            return listItems[0] + ", " + listItems[1] + " et " + listItems[2]

    # Date
    if validite != None and validite.startswith("d") :
        return _(u"Jusqu'au %s") % UTILS_Dates.DateEngFr(validite[1:])



class Track(object):
    def __init__(self, donnees):
        self.IDtype_piece = donnees[0]
        self.nom = donnees[1]
        self.public = donnees[2]
        self.txt_public = self.public.capitalize()
        self.duree_validite = donnees[3]
        self.txt_duree_validite = FormatDuree(self.duree_validite)
        self.valide_rattachement = donnees[4]
        if self.valide_rattachement == 1 :
            self.txt_rattachement = _(u"Oui")
        else:
            self.txt_rattachement = ""
        
        
    
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
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        req = """SELECT IDtype_piece, nom, public, duree_validite, valide_rattachement
        FROM types_pieces ORDER BY nom; """ 
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
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDtype_piece", typeDonnee="entier"),
            ColumnDefn(_(u"Nom de la pièce"), 'left', 220, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Public"), "left", 70, "txt_public", typeDonnee="texte"), 
            ColumnDefn(_(u"Validité"), "left", 140, "txt_duree_validite", typeDonnee="texte"), 
            ColumnDefn(_(u"Rattachement valide"), "left", 120, "txt_rattachement", typeDonnee="texte"), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun type de pièce"))
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
            ID = self.Selection()[0].IDtype_piece
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()
    
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des types de pièces"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des types de pièces"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_types_pieces", "creer") == False : return
        import DLG_Saisie_typesPieces
        dlg = DLG_Saisie_typesPieces.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            public = dlg.GetPublic()
            rattachement = dlg.GetRattachement()
            validite = dlg.GetValidite()
            # Sauvegarde vaccin
            DB = GestionDB.DB()
            listeDonnees = [("nom", nom ), ("public", public ), ("valide_rattachement", rattachement ), ("duree_validite", validite),]
            IDtype_piece = DB.ReqInsert("types_pieces", listeDonnees)
            DB.Close()
            self.MAJ(IDtype_piece)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_types_pieces", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun type de pièce dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDtype_piece = self.Selection()[0].IDtype_piece
        nom = self.Selection()[0].nom
        public = self.Selection()[0].public
        validite = self.Selection()[0].duree_validite
        rattachement = self.Selection()[0].valide_rattachement
        import DLG_Saisie_typesPieces
        dlg = DLG_Saisie_typesPieces.Dialog(self)      
        dlg.SetNom(nom)
        dlg.SetPublic(public)
        dlg.SetValidite(validite)
        dlg.SetRattachement(rattachement)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            public = dlg.GetPublic()
            rattachement = dlg.GetRattachement()
            validite = dlg.GetValidite()
            # Sauvegarde vaccin
            DB = GestionDB.DB()
            listeDonnees = [("nom", nom ), ("public", public ), ("valide_rattachement", rattachement ), ("duree_validite", validite),]
            DB.ReqMAJ("types_pieces", listeDonnees, "IDtype_piece", IDtype_piece)
            DB.Close()
            self.MAJ(IDtype_piece)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_types_pieces", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun type de pièce dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDtype_piece = self.Selection()[0].IDtype_piece
        
        # Vérifie que ce type de pièce n'est pas déjà attribué à un individu
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDpiece)
        FROM pieces 
        WHERE IDtype_piece=%d
        ;""" % IDtype_piece
        DB.ExecuterReq(req)
        nbrePieces = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbrePieces > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce type de pièce a déjà été attribué à %d pièce(s).\n\nVous ne pouvez donc pas le supprimer !") % nbrePieces, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que ce type de pièce n'est pas déjà attribué comme pièce obligatoire pour une activité
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDpiece_activite)
        FROM pieces_activites 
        WHERE IDtype_piece=%d
        ;""" % IDtype_piece
        DB.ExecuterReq(req)
        nbreActivites = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreActivites > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce type de pièce a déjà été attribué comme pièce obligatoire à %d activité(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreActivites, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce type de pièce ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("types_pieces", "IDtype_piece", IDtype_piece)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()





# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un type de pièce..."))
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
