#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import datetime
import locale
from Utils import UTILS_Titulaires
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


# ---------------------------------------- LISTVIEW DATES -----------------------------------------------------------------------

class Track(object):
    def __init__(self, parent, donnees):
        self.IDrecu = donnees["IDrecu"]
        self.numero = donnees["numero"]
        self.IDfamille = donnees["IDfamille"]
        self.date_edition = donnees["date_edition"]
        self.IDutilisateur = donnees["IDutilisateur"]
        self.IDreglement = donnees["IDreglement"]
        if self.IDfamille in parent.titulaires :
            self.nomsTitulaires =  parent.titulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.nomsTitulaires = _(u"Famille inconnue")


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.IDfamille = kwds.pop("IDfamille", None)
        self.selectionID = None
        self.selectionTrack = None
##        locale.setlocale(locale.LC_ALL, 'FR')
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnActivated(self,event):
        self.Modifier(None)

    def InitModel(self):
        self.titulaires = UTILS_Titulaires.GetTitulaires() 
        self.donnees = self.GetTracks()
        
    def GetListeAttestations(self):
        DB = GestionDB.DB()
        if self.IDfamille != None :
            conditions = "WHERE IDfamille = %d" % self.IDfamille
        else:
            conditions = ""
        req = """
        SELECT 
        IDrecu, numero, IDfamille, 
        date_edition, IDutilisateur,
        IDreglement
        FROM recus
        %s
        ORDER BY date_edition
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        listeRecus = []
        for IDrecu, numero, IDfamille, date_edition, IDutilisateur, IDreglement in listeDonnees :
            date_edition = DateEngEnDateDD(date_edition) 
            dictTemp = {
                "IDrecu" : IDrecu, "numero" : numero, "IDfamille" : IDfamille, "date_edition" : date_edition,
                "IDutilisateur" : IDutilisateur, "IDreglement" : IDreglement, 
                }
            listeRecus.append(dictTemp)
        return listeRecus


    def GetTracks(self):
        # Récupération des données
        listeID = None
        listeDonnees = self.GetListeAttestations() 
    
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item["IDrecu"] :
                    self.selectionTrack = track
        return listeListeView


    def InitObjectListView(self):
        
        def FormateNumero(numero):
            return "%06d" % numero

        def FormateDate(dateDD):
            if dateDD == None : return u""
            return DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)
                   
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour(wx.Colour(150, 150, 150))
                
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = "#FFFFFF" # Vert

        # Paramètres ListView
        self.useExpansionColumn = True

        # Version pour liste reçus
        self.SetColumns([
            ColumnDefn(u"", "left", 0, "IDrecu", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), "left", 70, "date_edition", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Numéro"), "centre", 60, "numero", typeDonnee="entier", stringConverter=FormateNumero), 
            ColumnDefn(_(u"Famille"), "left", 180, "nomsTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"IDreglement"), "centre", 75, "IDreglement", typeDonnee="entier"),
        ])
        self.SetSortColumn(self.columns[1])
        self.SetEmptyListMsg(_(u"Aucun reçu de règlement"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
##        self.rowFormatter = rowFormatter
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
##        # MAJ du total du panel
##        try :
##            if self.GetParent().GetName() == "panel_prestations" :
##                self.GetParent().MAJtotal()
##        except :
##            pass
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) > 0 :
            ID = self.Selection()[0].IDrecu
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
##
##        # Item Modifier
##        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
##        if len(self.Selection()) == 0 : item.Enable(False)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if len(self.Selection()) == 0 : item.Enable(False)
        
        menuPop.AppendSeparator()
    
##        # Item Rééditer la facture
##        item = wx.MenuItem(menuPop, 60, _(u"Rééditer la facture (PDF)"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Reedition, id=60)
##        
##        menuPop.AppendSeparator()
    
        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des reçus de règlements"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
##    def Reedition(self, event):
##        if len(self.Selection()) == 0 :
##            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à rééditer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
##        IDfacture = self.Selection()[0].IDfacture
##        from Ctrl import CTRL_Facturation_factures
##        CTRL_Facturation_factures.Reedition(IDfacture)

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune reçu à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDrecu = self.Selection()[0].IDrecu
        numero = self.Selection()[0].numero
                
        # Demande la confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer le reçu n°%d ?") % numero, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        
        # Suppression du reçu
        DB = GestionDB.DB()
        DB.ReqDEL("recus", "IDrecu", IDrecu)
        DB.Close()         
        
        # MAJ du listeView
        self.MAJ() 
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Reçu supprimé !"), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        IDrecu = self.Selection()[0].IDrecu
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDrecu)
        dlg.Destroy()

# -------------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un reçu de règlement..."))
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




# ----------------- FRAME DE TEST ----------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((800, 400))
        self.Layout()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "GroupListView")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
