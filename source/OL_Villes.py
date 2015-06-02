#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _

import wx
import CTRL_Bouton_image
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs


# -------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Saisie(wx.Dialog):
    def __init__(self, parent, nom=None, cp=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        self.label_nom = wx.StaticText(self, -1, _(u"Nom de la ville :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "", size=(280, -1))
        if nom != None :
            self.ctrl_nom.SetValue(nom)
            
        self.label_cp = wx.StaticText(self, -1, _(u"Code postal :"))
        self.ctrl_cp = wx.TextCtrl(self, -1, "", size=(80, -1))
        if cp !=None :
            self.ctrl_cp.SetValue(cp)
            
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if nom == None :
            self.SetTitle(_(u"Saisie d'une ville"))
        else:
            self.SetTitle(_(u"Modification d'une ville"))
        self.SetMinSize((350, -1))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_cp, 0, 0, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
    
    def GetNom(self):
        return self.ctrl_nom.GetValue()
    
    def GetCp(self):
        return self.ctrl_cp.GetValue()
        
    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        cp = self.ctrl_cp.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun nom de ville !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        if cp == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun code postal !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_cp.SetFocus()
            return

        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")


# -----------------------------------------------------------------------------------------------------------------------------------------


class Track(object):
    def __init__(self, donnees):
        self.IDville = donnees[0]
        self.nom = donnees[1]
        self.cp = donnees[2]
        self.mode = donnees[3]

    
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
        #self.GetParent().OnBoutonImporter(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        # Critères
        listeID = None
        self.criteres = ""
        # Liste de filtres
        if len(self.listeFiltres) > 0 :
            listeID, criteres = self.GetListeFiltres(self.listeFiltres)
            if criteres != "" :
                if self.criteres == "" :
                    self.criteres = "WHERE " + criteres
                else:
                    self.criteres += " AND " + criteres
        
        # Importation des villes par défaut
        DB = GestionDB.DB(nomFichier="Geographie.dat", suffixe=None)
        req = """SELECT IDville, nom, cp
        FROM villes %s ORDER BY nom; """ % self.criteres
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        # Importation des corrections de villes et codes postaux
        DB = GestionDB.DB()
        req = """SELECT IDcorrection, mode, IDville, nom, cp
        FROM corrections_villes; """ 
        DB.ExecuterReq(req)
        listeCorrections = DB.ResultatReq()
        DB.Close()
        
        # Ajout des corrections
        dictCorrections = {}
        for IDcorrection, mode, IDville, nom, cp in listeCorrections :
            dictCorrections[IDville] = {"mode":mode, "nom":nom, "cp":cp, "IDcorrection":IDcorrection}
            if mode == "ajout" :
                listeDonnees.append((100000+IDcorrection, nom, cp))

        listeListeView = []
        for IDville, nom, cp in listeDonnees :
            mode = None
            
            # Filtre de sélection
            valide = True
            if listeID != None :
                if IDville not in listeID :
                    valide = False
            
            # Traitement des corrections
            if dictCorrections.has_key(IDville) :
                mode = dictCorrections[IDville]["mode"]
                if mode == "modif" :
                    nom = dictCorrections[IDville]["nom"]
                    cp = dictCorrections[IDville]["cp"]
                    IDville = 100000 + dictCorrections[IDville]["IDcorrection"]
                if mode == "suppr" :
                    valide = False
            
            if IDville > 100000 and mode == None :
                mode = "ajout"
            
            # Création des tracks
            if valide == True :
                track = Track((IDville, nom, cp, mode))
                listeListeView.append(track)
                if self.selectionID == IDville :
                    self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDville", typeDonnee="entier"),
            ColumnDefn(_(u"Nom de la ville"), 'left', 250, "nom", typeDonnee="texte"),
            ColumnDefn("Code postal", "left", 120, "cp", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune ville"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDville=None):
        if IDville != None :
            self.selectionID = IDville
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
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Modifier
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

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        """ Ajouter une ville """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_villes", "creer") == False : return
        # Demande le nom et le code postal
        dlg = DLG_Saisie(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            cp = dlg.GetCp()
            DB = GestionDB.DB()
            IDcorrection = DB.ReqInsert("corrections_villes", [("mode", "ajout"), ("nom", nom), ("cp", cp)])
            DB.Close()
            self.MAJ(100000+IDcorrection)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_villes", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ville à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDville = self.Selection()[0].IDville
        nom = self.Selection()[0].nom
        cp = self.Selection()[0].cp
        mode = self.Selection()[0].mode
        
        dlg = DLG_Saisie(self, nom, cp)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            cp = dlg.GetCp()
            DB = GestionDB.DB()
            # Si c'est une ville par défaut
            if IDville < 100000 :
                IDcorrection = DB.ReqInsert("corrections_villes", [("mode", "modif"), ("IDville", IDville), ("nom", nom), ("cp", cp)])
                self.MAJ(100000+IDcorrection)
            else :
                # Si c'est un ajout perso
                IDcorrection = IDville-100000
                DB.ReqMAJ("corrections_villes", [("nom", nom), ("cp", cp)], "IDcorrection", IDcorrection)
                self.MAJ(IDville)
            DB.Close()
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_villes", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ville à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDville = self.Selection()[0].IDville
        nom = self.Selection()[0].nom
        cp = self.Selection()[0].cp
        mode = self.Selection()[0].mode
        
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la ville '%s (%s)' ?") % (nom, cp), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            # Si c'est une ville par défaut
            if IDville < 100000 :
                IDcorrection = DB.ReqInsert("corrections_villes", [("mode", "suppr"), ("IDville", IDville)])
            else :
                # Si la ville est un ajout ou une modif
                IDcorrection = IDville-100000
                if mode == "ajout" :
                    DB.ReqDEL("corrections_villes", "IDcorrection", IDcorrection)
                if mode == "modif" :
                    listeDonnees = [("mode", "suppr"), ("nom", None), ("cp", None)]
                    DB.ReqMAJ("corrections_villes", listeDonnees, "IDcorrection", IDcorrection)
                    
            DB.Close()
            self.MAJ()
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une ville ou un code postal..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_villes
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[1:nbreColonnes]))
        
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
        if self.rechercheEnCours == False :
            wx.CallLater(1000, self.Recherche)
            self.rechercheEnCours = True
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 
        self.rechercheEnCours = False

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
