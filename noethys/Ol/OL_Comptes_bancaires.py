#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import GestionDB
from Dlg import DLG_Saisie_compte


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs


class Track(object):
    def __init__(self, donnees):
        self.IDcompte = donnees[0]
        self.nom = donnees[1]
        self.numero = donnees[2]
        self.defaut = donnees[3]
        self.raison = donnees[4]
        self.code_etab = donnees[5]
        self.code_guichet = donnees[6]
        self.code_nne = donnees[7]

    
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
        self.nom_fichier_liste = __file__
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
        req = """SELECT IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne
        FROM comptes_bancaires 
        ORDER BY nom; """
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
        
        # Préparation de la listeImages
        imgDefaut = self.AddNamedImages("defaut", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        
        def GetImageDefaut(track):
            if track.defaut == 1 : return "defaut"
            else: return None 

        liste_Colonnes = [
            ColumnDefn(u"", "left", 21, "IDcompte", typeDonnee="entier", imageGetter=GetImageDefaut),
            ColumnDefn(_(u"Intitulé"), 'left', 200, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Numéro"), "left", 100, "numero", typeDonnee="texte"),
            ColumnDefn(_(u"Raison sociale"), "left", 170, "raison", typeDonnee="texte"),
            ColumnDefn(_(u"Code Etab."), "left", 80, "code_etab", typeDonnee="texte"),
            ColumnDefn(_(u"Code Guichet"), "left", 90, "code_guichet", typeDonnee="texte"),
            ColumnDefn(_(u"N° NNE"), "left", 80, "code_nne", typeDonnee="texte"),
            ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun compte bancaire"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
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
            ID = self.Selection()[0].IDcompte
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Par défaut
        item = wx.MenuItem(menuPop, 60, _(u"Définir comme compte par défaut"))
        if noSelection == False :
            if self.Selection()[0].defaut == 1 :
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.SetDefaut, id=60)
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des comptes bancaires"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des comptes bancaires"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_comptes_bancaires", "creer") == False : return
        if len(self.donnees) == 0 :
            defaut = 1 
        else:
            defaut = 0
        dlg = DLG_Saisie_compte.Dialog(self, IDcompte=None, defaut=defaut)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDcompte() )
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_comptes_bancaires", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun compte à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie_compte.Dialog(self, IDcompte=track.IDcompte, defaut=track.defaut)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDcompte() )
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_comptes_bancaires", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun compte à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcompte = self.Selection()[0].IDcompte
        
        # Vérifie que ce compte n'a pas déjà été attribué à un règlement
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDreglement)
        FROM reglements 
        WHERE IDcompte=%d
        ;""" % IDcompte
        DB.ExecuterReq(req)
        nbre = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbre > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce compte a déjà été attribué à %d règlement(s).\n\nVous ne pouvez donc pas le supprimer !") % nbre, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que ce compte n'a pas déjà été attribué à un dépôt
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDdepot)
        FROM depots 
        WHERE IDcompte=%d
        ;""" % IDcompte
        DB.ExecuterReq(req)
        nbre = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbre > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce compte a déjà été attribué à %d dépôt(s) de règlements.\n\nVous ne pouvez donc pas le supprimer !") % nbre, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que ce compte n'a pas déjà été attribué à une opération comptable
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDoperation)
        FROM compta_operations 
        WHERE IDcompte_bancaire=%d
        ;""" % IDcompte
        DB.ExecuterReq(req)
        nbre = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbre > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce compte a déjà été attribué à %d opérations comptables.\n\nVous ne pouvez donc pas le supprimer !") % nbre, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que ce compte n'a pas déjà été attribué à un relevé de compte
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDreleve)
        FROM compta_releves 
        WHERE IDcompte_bancaire=%d
        ;""" % IDcompte
        DB.ExecuterReq(req)
        nbre = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbre > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce compte a déjà été attribué à %d relevés de compte.\n\nVous ne pouvez donc pas le supprimer !") % nbre, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce compte bancaire ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            # Suppression de l'identité
            DB.ReqDEL("comptes_bancaires", "IDcompte", IDcompte)
            # Attribue le Défaut à un autre compte
            if self.Selection()[0].defaut == 1 :
                req = """SELECT IDcompte, defaut
                FROM comptes_bancaires
                ORDER BY nom
                ; """
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) > 0 :
                    DB.ReqMAJ("comptes_bancaires", [("defaut", 1 ),], "IDcompte", listeDonnees[0][0])
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    def SetDefaut(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_comptes_bancaires", "modifier") == False : return
        if self.Selection():
            IDcompteDefaut = self.Selection()[0].IDcompte
            DB = GestionDB.DB()
            req = """SELECT IDcompte, defaut
            FROM comptes_bancaires
            ; """
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            for IDcompte, defaut in listeDonnees :
                if IDcompte == IDcompteDefaut :
                    DB.ReqMAJ("comptes_bancaires", [("defaut", 1 ),], "IDcompte", IDcompte)
                else:
                    DB.ReqMAJ("comptes_bancaires", [("defaut", 0 ),], "IDcompte", IDcompte)
            DB.Close()
            self.MAJ()


# -------------------------------------------------------------------------------------------------------------------------------------------

class Saisie(wx.Dialog):
    def __init__(self, parent, nom=None, numero=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        self.label_nom = wx.StaticText(self, -1, _(u"Intitulé du compte :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        if nom != None :
            self.ctrl_nom.SetValue(nom)
        self.label_numero = wx.StaticText(self, -1, _(u"Numéro de compte :"))
        self.ctrl_numero = wx.TextCtrl(self, -1, "")
        if numero !=None :
            self.ctrl_numero.SetValue(numero)
            
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if nom == None :
            self.SetTitle(_(u"Saisie d'un compte"))
        else:
            self.SetTitle(_(u"Modification d'un compte"))
        self.SetMinSize((450, -1))
        
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici l'intitulé du compte")))
        self.ctrl_numero.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numéro du compte")))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_numero, 0, wx.EXPAND, 0)
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
    
    def GetNumero(self):
        return self.ctrl_numero.GetValue()
        
    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        numero = self.ctrl_numero.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de compte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        if numero == "" :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas saisir de numéro de compte ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Comptesbancaires")


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un compte bancaire..."))
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
