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

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs




class Track(object):
    def __init__(self, donnees, dictModeles):
        self.IDutilisateur = donnees[0]
        self.sexe = donnees[1]
        self.nom = donnees[2]
        self.prenom = donnees[3]
        self.mdp = donnees[4]
        self.profil = donnees[5]
        self.actif = donnees[6]
        if self.actif == 1 :
            self.texteActif = "Oui"
        else :
            self.texteActif = "Non"
        self.nomImage = donnees[7]
        
        # Droits
        if self.profil.startswith("modele:") :
            IDmodele = int(self.profil.replace("modele:", ""))
            if dictModeles.has_key(IDmodele) :
                self.texteDroits = dictModeles[IDmodele]
            else :
                self.texteDroits = u"Modèle de droits inconnu"

        elif self.profil == "perso" :
            self.texteDroits = u"Droits personnalisés"
        
        else :
            self.texteDroits = u"Administrateur"
        
        # Image
        if self.nomImage == None or self.nomImage == "Automatique" :
            if self.sexe == "M" : 
                self.image = wx.Bitmap("Images/Avatars/16x16/Homme.png", wx.BITMAP_TYPE_PNG)
            else:
                self.image = wx.Bitmap("Images/Avatars/16x16/Femme.png", wx.BITMAP_TYPE_PNG)
        else :
            self.image = wx.Bitmap("Images/Avatars/16x16/%s.png" % self.nomImage, wx.BITMAP_TYPE_PNG)
        
        
    
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
        DB = GestionDB.DB()
        
        # Liste des modèles
        req = """SELECT IDmodele, nom
        FROM modeles_droits;"""
        DB.ExecuterReq(req)
        listeModeles = DB.ResultatReq()
        dictModeles = {}
        for IDmodele, nom in listeModeles :
            dictModeles[IDmodele] = nom
        
        # Liste des utilisateurs
        req = """SELECT IDutilisateur, sexe, nom, prenom, mdp, profil, actif, image
        FROM utilisateurs;"""
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
                track = Track(item, dictModeles)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        imgActif = self.AddNamedImages("actif", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        imgInactif = self.AddNamedImages("inactif", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        
        for track in self.donnees :
            self.AddNamedImages(str(track.IDutilisateur), track.image)
        
        # Formatage des données
        def GetImageActif(track):
            if track.actif == 1 : return "actif"
            else: return "inactif"
            
        def GetImageAvatar(track):
            return str(track.IDutilisateur)

        liste_Colonnes = [
            
            ColumnDefn(u"", 'left', 22, "IDutilisateur", typeDonnee="entier", imageGetter=GetImageAvatar),
            ColumnDefn(u"Nom", 'left', 150, "nom", typeDonnee="texte"),
            ColumnDefn(u"Prénom", 'left', 150, "prenom", typeDonnee="texte"),
            ColumnDefn(u"Actif", "left", 60, "texteActif", typeDonnee="texte", imageGetter=GetImageActif),
            ColumnDefn(u"Droits", 'left', 200, "texteDroits", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun utilisateur")
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
            ID = self.Selection()[0].IDutilisateur
                
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
        
        # Item Historique
        item = wx.MenuItem(menuPop, 60, u"Historique")
        bmp = wx.Bitmap("Images/16x16/Horloge3.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Historique, id=60)
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des utilisateurs", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des utilisateurs", format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs", "creer") == False : return
        import DLG_Saisie_utilisateur
        dlg = DLG_Saisie_utilisateur.Dialog(self, IDutilisateur=None)
        if dlg.ShowModal() == wx.ID_OK:
            IDutilisateur = dlg.GetIDutilisateur()
            self.MAJ(IDutilisateur)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun utilisateur à modifier dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs", "modifier") == False : return
        IDutilisateur = self.Selection()[0].IDutilisateur
        import DLG_Saisie_utilisateur
        dlg = DLG_Saisie_utilisateur.Dialog(self, IDutilisateur=IDutilisateur)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDutilisateur)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun utilisateur à supprimer dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs", "supprimer") == False : return
        IDutilisateur = self.Selection()[0].IDutilisateur
        profil = self.Selection()[0].profil
        # Vérifie que cet utilisateur n'est pas déjà attribué à d'autres tables de données
        
        # Table Consommations
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDconso)
        FROM consommations 
        WHERE IDutilisateur=%d
        ;""" % IDutilisateur
        DB.ExecuterReq(req)
        nbreConso = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreConso > 0 :
            dlg = wx.MessageDialog(self, u"Cet utilisateur a déjà été attribué à %d consommation(s).\n\nVous ne pouvez donc pas le supprimer !" % nbreConso, u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Table Règlements
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDreglement)
        FROM reglements 
        WHERE IDutilisateur=%d
        ;""" % IDutilisateur
        DB.ExecuterReq(req)
        nbreReglements = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreReglements > 0 :
            dlg = wx.MessageDialog(self, u"Cet utilisateur a déjà été attribué à %d règlement(s).\n\nVous ne pouvez donc pas le supprimer !" % nbreReglements, u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie qu'il reste au moins un administrateur
        if profil == "administrateur" :
            nbreAdmin = 0
            for track in self.donnees :
                if track.profil == "administrateur" and track.IDutilisateur != IDutilisateur : 
                    nbreAdmin += 1
            if nbreAdmin == 0 :
                dlg = wx.MessageDialog(self, u"Vous ne pouvez pas supprimer le seul administrateur !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
        # Suppression
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer cet utilisateur ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("utilisateurs", "IDutilisateur", IDutilisateur)
            DB.ReqDEL("droits", "IDutilisateur", IDutilisateur)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()

    def Historique(self, event):
        """ Affiche l'historique de l'utilisateur """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun utilisateur dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDutilisateur = self.Selection()[0].IDutilisateur
        import DLG_Historique
        dlg = DLG_Historique.Dialog(self, IDutilisateur=IDutilisateur)
        dlg.ShowModal() 
        dlg.Destroy()
        

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un utilisateur...")
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
