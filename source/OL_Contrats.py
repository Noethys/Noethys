#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
##import cStringIO
import datetime
import GestionDB
import UTILS_Historique
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, ListCtrlPrinter, PanelAvecFooter

import UTILS_Utilisateurs


class Track(object):
    def __init__(self, parent, donnees):
        self.IDcontrat = donnees[0]
        self.IDinscription = donnees[1]
        self.date_debut = donnees[2]
        self.date_fin = donnees[3]
        self.IDindividu = donnees[4]
        self.IDfamille = donnees[5]
        self.nom_activite = donnees[6]
        self.montant = donnees[7]

        # Nom de l'individu
        self.nomIndividu = donnees[8]
        self.prenomIndividu = donnees[9]
        if self.prenomIndividu == None :
            self.prenomIndividu = ""
        self.nomCompletIndividu = u"%s %s" % (self.nomIndividu, self.prenomIndividu)

        # Type de contrat
        self.type_contrat = donnees[10]
        if self.type_contrat in (None, "classique") :
            self.type_contrat_str = _(u"Classique")
        if self.type_contrat == "psu" :
            self.type_contrat_str = _(u"P.S.U.")

        # Validité
        if str(datetime.date.today()) <= self.date_fin :
            self.valide = True
        else:
            self.valide = False
            

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", None)
        self.dictFamillesRattachees = kwds.pop("dictFamillesRattachees", {} )
        self.activeDoubleclick = kwds.pop("activeDoubleclick", True)
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
        listeConditions = []
        if self.IDindividu != None :
            listeConditions.append("contrats.IDindividu=%d" % self.IDindividu)
        for filtre in self.listeFiltres :
            listeConditions.append(filtre)
        if len(listeConditions) > 0 :
            conditions = "WHERE " + " AND ".join(listeConditions)
        else :
            conditions = ""
            
        listeID = None
        DB = GestionDB.DB()
        req = """SELECT contrats.IDcontrat, contrats.IDinscription, contrats.date_debut, contrats.date_fin,
        inscriptions.IDindividu, inscriptions.IDfamille, activites.nom, 
        SUM(prestations.montant) as total, 
        individus.nom, individus.prenom,
        contrats.type
        FROM contrats 
        LEFT JOIN inscriptions ON inscriptions.IDinscription=contrats.IDinscription
        LEFT JOIN activites ON activites.IDactivite=inscriptions.IDactivite
        LEFT JOIN prestations ON prestations.IDcontrat = contrats.IDcontrat
        LEFT JOIN individus ON individus.IDindividu = contrats.IDindividu
        %s
        GROUP BY contrats.IDcontrat
        ORDER BY contrats.date_debut; """ % conditions
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
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def DateEngFr(textDate):
            if textDate != None :
                text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
            else:
                text = ""
            return text

        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(_(u"IDcontrat"), "left", 0, "IDcontrat", typeDonnee="entier"),
            ColumnDefn(_(u"Du"), 'center', 70, "date_debut", typeDonnee="date", stringConverter=DateEngFr),
            ColumnDefn(_(u"Au"), 'center', 70, "date_fin", typeDonnee="date", stringConverter=DateEngFr),
            ColumnDefn(_(u"Type"), 'center', 70, "type_contrat_str", typeDonnee="texte"),
            ColumnDefn(_(u"Nom de l'activité"), 'left', 110, "nom_activite", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Montant"), 'right', 80, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ]
        
        if self.IDindividu == None :
            liste_Colonnes.insert(4, ColumnDefn(_(u"Individu"), 'left', 200, "nomCompletIndividu", typeDonnee="texte"))
            
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun contrat"))
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
        self._ResizeSpaceFillingColumns() 
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDcontrat
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        if self.IDindividu != None :
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

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des contrats"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des contrats"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des contrats"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des contrats"))

    def Ajouter(self, event):
        # Sélection de l'activité
        import DLG_Saisie_contrat_intro
        dlg = DLG_Saisie_contrat_intro.Dialog(self, IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)
        if dlg.ShowModal() == wx.ID_OK:
            type_contrat = dlg.GetTypeContrat()
            IDinscription = dlg.GetInscription() 
            dictOptions = dlg.GetOptions() 
            dlg.Destroy()
        else :
            dlg.Destroy()
            return
        
        copie = False
        IDmodele = None
        
        if dictOptions != None :
            # Utilisation d'un modèle
            if dictOptions["type"] == "modele" :
                IDmodele = dictOptions["IDmodele"]

            # Copie d'un contrat
            if dictOptions["type"] == "contrat" :
                copie = dictOptions["IDcontrat"]
            
        # Création du contrat de type Classique
        if type_contrat == "classique" :
            import DLG_Saisie_contrat
            dlg = DLG_Saisie_contrat.Dialog(self, IDindividu=self.IDindividu, IDinscription=IDinscription, IDcontrat=None, IDmodele=IDmodele, copie=copie)
            if dlg.ShowModal() == wx.ID_OK:
                IDcontrat = dlg.GetIDcontrat()
                self.MAJ(IDcontrat)
            dlg.Destroy()

        # Création du contrat de type PSU
        if type_contrat == "psu" :
            import DLG_Saisie_contratpsu
            dlg = DLG_Saisie_contratpsu.Assistant(self, IDinscription=IDinscription)
            if dlg.ShowModal() == wx.ID_OK:
                IDcontrat = dlg.GetIDcontrat()
                self.MAJ(IDcontrat)
            dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun contrat à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        if track.type_contrat in (None, "classique") :
            import DLG_Saisie_contrat
            dlg = DLG_Saisie_contrat.Dialog(self, IDindividu=track.IDindividu, IDinscription=track.IDinscription, IDcontrat=track.IDcontrat)
            if dlg.ShowModal() == wx.ID_OK:
                IDcontrat = dlg.GetIDcontrat()
                self.MAJ(IDcontrat)
            dlg.Destroy()

        if track.type_contrat == "psu" :
            import DLG_Saisie_contratpsu
            dlg = DLG_Saisie_contratpsu.Dialog(self, IDcontrat=track.IDcontrat)
            if dlg.ShowModal() == wx.ID_OK:
                IDcontrat = dlg.GetIDcontrat()
                self.MAJ(IDcontrat)
            dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun contrat à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        
##        # Verrouillage utilisateurs
##        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_inscriptions", "supprimer", IDactivite=IDactivite) == False : 
##            return

        DB = GestionDB.DB()
        
        # Recherche si des consommations existent
        req = """SELECT IDprestation, IDfacture
        FROM prestations
        WHERE IDcontrat=%d;""" % track.IDcontrat
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()     
        listePrestationsFacturees = []
        listeIDprestations = []
        for IDprestation, IDfacture in listePrestations :
            listeIDprestations.append(IDprestation)
            if IDfacture != None :
                listePrestationsFacturees.append(IDprestation)
        if len(listePrestationsFacturees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Il est impossible de supprimer ce contrat directement car %d prestations associées apparaissent déjà sur une facture !") % len(listePrestationsFacturees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close() 
            return
        
        # Recherche si des consommations sont pointées
        req = """SELECT IDconso, etat
        FROM consommations
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        WHERE prestations.IDcontrat=%d;""" % track.IDcontrat
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()  
        DB.Close()    
        listeConsoPointees = []
        for IDconso, etat in listeConsommations :
            if etat in ("present", "absenti", "absentj"):
                listeConsoPointees.append(IDconso)
        if len(listeConsoPointees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Il est impossible de supprimer ce contrat directement car %d consommations associées sont déjà pointées !") % len(listeConsoPointees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce contrat ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("contrats", "IDcontrat", track.IDcontrat)
            DB.ReqDEL("contrats_tarifs", "IDcontrat", track.IDcontrat)
            DB.ReqDEL("prestations", "IDcontrat", track.IDcontrat)
            # Suppression des consommations associées
            for IDprestation in listeIDprestations :
                DB.ReqDEL("consommations", "IDprestation", IDprestation)
            DB.Close() 
            
##            # Mémorise l'action dans l'historique
##            UTILS_Historique.InsertActions([{
##                "IDindividu" : self.IDindividu,
##                "IDfamille" : IDfamille,
##                "IDcategorie" : 19, 
##                "action" : _(u"Suppression de l'inscription à l'activité '%s'") % nomActivite
##                },])
                
            # Actualise l'affichage
            self.MAJ()
        dlg.Destroy()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, track.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDcontrat)
        dlg.Destroy()

        
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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date_fin" : {"mode" : "nombre", "singulier" : _(u"contrat"), "pluriel" : _(u"contrats"), "alignement" : wx.ALIGN_LEFT},
            "montant" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, IDindividu=None, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
