#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import time
import GestionDB
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Dates
from Utils import UTILS_Titulaires


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils.UTILS_Mandats import LISTE_SEQUENCES



class Track(object):
    def __init__(self, donnees, dictTitulaires):
        self.IDfamille = donnees[0]
        self.iban = donnees[1]
        self.bic = donnees[2]
        self.IDindividu = donnees[4]
        self.individu_nom = donnees[5]
        self.individu_rue = donnees[6]
        self.individu_cp = donnees[7]
        self.individu_ville = donnees[8]
        
        self.rum = donnees[9]
        self.date = donnees[10]
        if self.date != None :
            self.date = UTILS_Dates.DateEngEnDateDD(self.date)
        self.memo = donnees[11]
        self.IDmandat = donnees[12]
                
        # Titulaire du compte
        if self.IDindividu != None :
            self.individu_nom = donnees[13]
            self.individu_prenom = donnees[14]
            self.individu_nom_complet = u""
            if self.individu_nom != None : self.individu_nom_complet += self.individu_nom + u" "
            if self.individu_prenom != None : self.individu_nom_complet += self.individu_prenom
        else :
            self.individu_nom_complet = self.individu_nom
        
        # NomFamille
        if dictTitulaires != None :
            self.titulairesFamille = dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.titulairesFamille = u""
        
        # Analyse
        informationsManquantes = []
        if self.iban == None or self.iban == "" : informationsManquantes.append(_(u"IBAN"))
        if self.bic == None or self.bic == "" : informationsManquantes.append(_(u"BIC"))
        if self.individu_nom_complet == None or self.individu_nom_complet == "" : informationsManquantes.append(_(u"nom du titulaire"))
        if self.rum == None or self.rum == "" : informationsManquantes.append(_(u"RUM"))
        if self.date == None or self.date == "" : informationsManquantes.append(_(u"date du mandat"))
        
        if self.IDmandat != None :
            self.analyse = _(u"Mandat déjà créé")
            self.valide = False
        elif len(informationsManquantes) > 0 :
            self.analyse = _(u"Infos manquantes : %s") % ", ".join(informationsManquantes)
            self.valide = False
        else :
            self.analyse = _(u"Prêt pour transfert")
            self.valide = True
        
        
    
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
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        dictTitulaires = UTILS_Titulaires.GetTitulaires()
        listeID = None

        # Récupération des RIB
        DB = GestionDB.DB()
        req = """SELECT familles.IDfamille, prelevement_iban, prelevement_bic, prelevement_banque,
        prelevement_individu, prelevement_nom, prelevement_rue, prelevement_cp, prelevement_ville,
        prelevement_reference_mandat, prelevement_date_mandat, prelevement_memo,
        mandats.IDmandat, individus.nom, individus.prenom,
        banques.nom
        FROM familles 
        LEFT JOIN mandats ON mandats.rum = familles.prelevement_reference_mandat
        LEFT JOIN individus ON individus.IDindividu = familles.prelevement_individu
        LEFT JOIN banques ON banques.IDbanque = familles.prelevement_banque
        GROUP BY familles.IDfamille
        ;""" 
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
                track = Track(item, dictTitulaires)
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
        imgOk = self.AddNamedImages("ok", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        imgPasOk = self.AddNamedImages("pasok", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))

        def GetImageAnalyse(track):
            if track.valide == False : 
                return "pasok"
            else: 
                return "ok" 

        def rowFormatter(listItem, track):
            valide = True
            if valide == False :
                listItem.SetTextColour((180, 180, 180))

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDfamille"),
            ColumnDefn(_(u"Analyse"), 'left', 250, "analyse", imageGetter=GetImageAnalyse),
            ColumnDefn(_(u"Famille"), 'left', 200, "titulairesFamille"),
            ColumnDefn(_(u"IBAN"), 'left', 180, "iban"),
            ColumnDefn(_(u"BIC"), 'left', 100, "bic"),
            ColumnDefn(_(u"RUM"), 'left', 60, "rum"),
            ColumnDefn(_(u"Date sign."), 'left', 75, "date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Titulaire"), 'left', 110, "individu_nom_complet"),
            ColumnDefn(_(u"Observations"), 'left', 120, "memo"),
            ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune donnée"))
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
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Cocher les valides
        item = wx.MenuItem(menuPop, 60, _(u"Cocher uniquement les transferts valides"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheValides, id=60)
        
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

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donnée à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mandats"), format="A", orientation=wx.LANDSCAPE)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des RIB"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des RIB"))

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
    
    def CocheValides(self, event=None) :
        """ Coche uniquement des tracks valides """
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            if track.valide == True :
                self.Check(track)
            else :
                self.Uncheck(track)
            self.RefreshObject(track)
        
    def Conversion(self):
        tracks = self.GetTracksCoches() 
        
        # Vérifie si ligne valide
        for track in tracks :
            if track.valide == False :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez sélectionner que les lignes valides !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la création de %d mandats ?\n\nCette opération peut prendre quelques minutes...") % len(tracks), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False
        
        # Lancement de la conversion
        DB = GestionDB.DB()
        
        index = 0
        for track in tracks :
            self.EcritStatusbar(_(u"Veuillez patienter...  Création du mandat %d / %d") % (index, len(tracks)))
            listeDonnees = [    
                    ("IDfamille", track.IDfamille),
                    ("rum", track.rum),
                    ("type", "recurrent"),
                    ("date", str(track.date)),
                    ("IDbanque", None),
                    ("IDindividu", track.IDindividu),
                    ("individu_nom", track.individu_nom),
                    ("individu_rue", track.individu_rue),
                    ("individu_cp", track.individu_cp),
                    ("individu_ville", track.individu_ville),
                    ("iban", track.iban),
                    ("bic", track.bic),
                    ("memo", track.memo),
                    ("sequence", "auto"),
                    ("actif", 1),
                ]
            DB.ReqInsert("mandats", listeDonnees)
            time.sleep(0.5)
            index += 1
            
        DB.Close()
        self.EcritStatusbar(u"") 
        
        dlg = wx.MessageDialog(self, _(u"%d mandats ont été créés avec succès.") % len(tracks), _(u"Fin"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True

        
    def EcritStatusbar(self, texte=""):
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass



# -------------------------------------------------------------------------------------------------------------------------------------------

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
        self.SetSize((800, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
