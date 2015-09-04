#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import locale
import UTILS_Titulaires

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

import UTILS_Utilisateurs


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


# ---------------------------------------- LISTVIEW DATES -----------------------------------------------------------------------

class Track(object):
    def __init__(self, parent, donnees):
        self.IDattestation = donnees["IDattestation"]
        self.numero = donnees["numero"]
        self.IDfamille = donnees["IDfamille"]
        self.date_edition = donnees["date_edition"]
        self.IDutilisateur = donnees["IDutilisateur"]
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]
        self.total = donnees["total"]
        self.regle = donnees["regle"]
        self.solde = donnees["solde"]
        self.nomsTitulaires =  parent.titulaires[self.IDfamille]["titulairesSansCivilite"]


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.IDfamille = kwds.pop("IDfamille", None)
        self.selectionID = None
        self.selectionTrack = None
##        locale.setlocale(locale.LC_ALL, 'FR')
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
        IDattestation, numero, IDfamille, 
        date_edition, IDutilisateur,
        date_debut, date_fin, total, regle, solde
        FROM attestations
        %s
        ORDER BY date_edition
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        listeAttestations = []
        for IDattestation, numero, IDfamille, date_edition, IDutilisateur, date_debut, date_fin, total, regle, solde in listeDonnees :
            date_edition = DateEngEnDateDD(date_edition) 
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            dictTemp = {
                "IDattestation" : IDattestation, "numero" : numero, "IDfamille" : IDfamille, "date_edition" : date_edition,
                "IDutilisateur" : IDutilisateur, "date_debut" : date_debut, "date_fin" : date_fin, "total" : total, "regle" : regle, "solde" : solde, 
                }
            listeAttestations.append(dictTemp)
            
        return listeAttestations


    def GetTracks(self):
        # R�cup�ration des donn�es
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
                if self.selectionID == item["IDattestation"] :
                    self.selectionTrack = track
        return listeListeView


    def InitObjectListView(self):
        
        # ImageList
        self.imgVert = self.AddNamedImages("vert", wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG))

##        def GetImageSoldeActuel(track):
##            if track.soldeActuel == 0.0 :
##                return self.imgVert
##            if track.soldeActuel < 0.0 and track.soldeActuel != -track.total :
##                return self.imgOrange
##            return self.imgRouge
        
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
        self.oddRowsBackColor = wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
        self.evenRowsBackColor = "#F0FBED" # Vert

        # Param�tres ListView
        self.useExpansionColumn = True
        
        # Version pour liste factures g�n�rale
        self.SetColumns([
            ColumnDefn(u"", "left", 0, "IDfacture", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), "left", 70, "date_edition", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Num�ro"), "centre", 60, "numero", typeDonnee="entier", stringConverter=FormateNumero), 
            ColumnDefn(_(u"Famille"), "left", 180, "nomsTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Date d�but"), "centre", 75, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Date fin"), "centre", 75, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Total"), "right", 65, "total", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"R�gl�"), "right", 65, "regle", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Solde"), "right", 65, "solde", typeDonnee="montant", stringConverter=FormateMontant),
        ])
        self.SetSortColumn(self.columns[1])
        self.SetEmptyListMsg(_(u"Aucune attestation de pr�sence"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
        # S�lection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        if ID == None :
            self.DefileDernier() 
        # MAJ du total du panel
        try :
            if self.GetParent().GetName() == "panel_prestations" :
                self.GetParent().MAJtotal()
        except :
            pass
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) > 0 :
            ID = self.Selection()[0].IDattestation
        
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
##        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
##
##        # Item Modifier
##        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
##        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
##        if len(self.Selection()) == 0 : item.Enable(False)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if len(self.Selection()) == 0 : item.Enable(False)
        
        menuPop.AppendSeparator()
    
##        # Item R��diter la facture
##        item = wx.MenuItem(menuPop, 60, _(u"R��diter la facture (PDF)"))
##        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Reedition, id=60)
##        
##        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
    
##    def Reedition(self, event):
##        if len(self.Selection()) == 0 :
##            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune facture � r��diter !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
##        IDfacture = self.Selection()[0].IDfacture
##        import CTRL_Facturation_factures
##        CTRL_Facturation_factures.Reedition(IDfacture)

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des attestations de pr�sence"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des attestations de pr�sence"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des attestations de pr�sence"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des attestations de pr�sence"))

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_attestations", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune attestation � supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDattestation = self.Selection()[0].IDattestation
        numero = self.Selection()[0].numero
                
        # Demande la confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer l'attestation n�%d ?") % numero, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        
        # Suppression de la facture
        DB = GestionDB.DB()
        DB.ReqDEL("attestations", "IDattestation", IDattestation)
        DB.Close()         
        
        # MAJ du listeView
        self.MAJ() 
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Attestation supprim�e !"), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune fiche famille � ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        IDattestation = self.Selection()[0].IDattestation
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDattestation)
        dlg.Destroy()

# -------------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une attestation de pr�sence..."))
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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomsTitulaires" : {"mode" : "nombre", "singulier" : "attestation", "pluriel" : "attestations", "alignement" : wx.ALIGN_CENTER},
            "total" : {"mode" : "total"},
            "regle" : {"mode" : "total"},
            "solde" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


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
