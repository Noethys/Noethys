#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Dates
import datetime
import wx.lib.dialogs as dialogs

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

                
  
class Track(object):
    def __init__(self, clsbase=None, dictValeurs={}):
        self.clsbase = clsbase
        self.dictValeurs = dictValeurs
        self.MAJ()

    def MAJ(self):
        self.IDconso = self.dictValeurs["IDconso"]
        self.date = self.dictValeurs["date"]
        self.IDunite = self.dictValeurs["IDunite"]
        self.heure_debut = self.dictValeurs["heure_debut"]
        self.heure_fin = self.dictValeurs["heure_fin"]
        self.quantite = self.dictValeurs["quantite"]
        self.etat = self.dictValeurs["etat"]
        self.etiquettes = self.dictValeurs["etiquettes"]
        
        self.nomUnite = "TEST"#self.parent.dictUnites[self.IDunite]["nom"]
        
        self.texteDetail = ""
        if self.heure_debut != None and self.heure_fin != None :
            self.texteDetail = "%s - %s" % (self.heure_debut.replace(":", "h"), self.heure_fin.replace(":", "h"))
        if self.quantite != None :
            self.texteDetail += _(u" Qté=%d") % self.quantite
        
        if self.etat == "reservation" : 
            self.texteEtat = _(u"Réservation")
        elif self.etat == "present" : 
            self.texteEtat = _(u"Présent")
        elif self.etat == "attente" : 
            self.texteEtat = _(u"Attente")
        elif self.etat == "absenti" : 
            self.texteEtat = _(u"Absence injustifiée")
        elif self.etat == "absentj" : 
            self.texteEtat = _(u"Absence justifiée")
        elif self.etat == "refus" : 
            self.texteEtat = _(u"Refus")
        else :
            self.texteEtat = ""

        # Calcule des horaires
        self.heure_debut_time = UTILS_Dates.HeureStrEnTime(self.heure_debut)
        self.heure_fin_time = UTILS_Dates.HeureStrEnTime(self.heure_fin)

        # Calcule la durée réelle
        self.duree_reelle = UTILS_Dates.SoustractionHeures(self.heure_fin_time, self.heure_debut_time)
        self.duree_reelle_str = UTILS_Dates.DeltaEnStr(self.duree_reelle, separateur="h")

        # Calcule la durée arrondie
        arrondi_type = self.clsbase.GetValeur("arrondi_type", None)
        arrondi_delta = self.clsbase.GetValeur("arrondi_delta", 15)
        self.duree_arrondie = UTILS_Dates.CalculerArrondi(arrondi_type=arrondi_type, arrondi_delta=arrondi_delta, heure_debut=self.heure_debut_time, heure_fin=self.heure_fin_time)
        self.duree_arrondie_str = UTILS_Dates.DeltaEnStr(self.duree_arrondie, separateur="h")

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.clsbase = kwds.pop("clsbase", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []

        # Init autres données
        self.dictUnites = self.Importation_unites()
        self.dictOuvertures = self.GetOuverturesUnites()

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)

        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.donnees = []
        self.InitObjectListView()

    def Importation_unites(self):
        self.dictUnites = {}
        if self.clsbase == None :
            return

        # Récupération des unités
        DB = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.clsbase.GetValeur("IDactivite", 0)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        self.dictUnites = {}
        for IDunite, nom, abrege, type, heure_debut, heure_fin in listeDonnees :
            self.dictUnites[IDunite] = {"nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "unites_incompatibles" : []}

        # Récupère les incompatibilités entre unités
        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
        FROM unites_incompat;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
            if IDunite in self.dictUnites : self.dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if IDunite_incompatible in self.dictUnites : self.dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)

    def OnItemActivated(self,event):
        self.Modifier(None)

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateComplete(dateDD)

        def FormateDuree(duree):
            if duree in (None, ""):
                return ""
            else :
                return UTILS_Dates.DeltaEnStr(duree, separateur="h")

        liste_Colonnes = [
            ColumnDefn(_(u"IDconso"), "left", 0, "IDconso", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 190, "date", typeDonnee="date", stringConverter=FormateDate),
            #ColumnDefn(_(u"Unité"), 'left', 70, "nomUnite", typeDonnee="texte", isSpaceFilling=True),
            #ColumnDefn(_(u"Etat"), 'left', 50, "texteEtat", typeDonnee="texte"),
            ColumnDefn(_(u"Détail"), 'left', 100, "texteDetail", typeDonnee="texte"),
            ColumnDefn(_(u"Durée réelle"), 'center', 90, "duree_reelle", typeDonnee="texte", stringConverter=FormateDuree),
            ColumnDefn(_(u"Durée retenue"), 'center', 90, "duree_arrondie", typeDonnee="texte", stringConverter=FormateDuree),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune consommation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(2)
        
    def MAJ(self):
        self.SetObjects(self.donnees)
        self._ResizeSpaceFillingColumns()
        self.MAJ_label_page()

    def SetDonnees(self, listeDonnees=[]):
        self.donnees = []
        for dictConso in listeDonnees :
            self.donnees.append(Track(self, dictConso))

    def SetTracks(self, listeTracks=[]):
        self.donnees = listeTracks
        self.MAJ()

    def MAJtracks(self):
        for track in self.donnees :
            track.MAJ()
        self.RefreshObjects(self.donnees)
        self.MAJ_label_page()

    def MAJ_label_page(self):
        """ Envoie un label de la page du notebook qui contient cette liste """
        nbreConso = len(self.GetTracks())
        if nbreConso == 0 :
            label = _(u"Consommations")
        else :
            label = _(u"Consommations (%d)") % nbreConso
        try :
            self.GetGrandParent().GetParent().SetLabelPage(1, label)
        except :
            pass

    def GetTracks(self):
        return self.GetObjects()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Modifier
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
            
    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des prévisions"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des prévisions"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des prévisions"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des prévisions"), autoriseSelections=False)


    def Ajouter(self, event):
        from Dlg import DLG_Saisie_contratpsu_conso
        dlg = DLG_Saisie_contratpsu_conso.Dialog(self, clsbase=self.clsbase)
        if dlg.ShowModal() == wx.ID_OK:
            listeConso = dlg.GetListeConso()
            listeTracks = []
            for dictConso in listeConso :
                listeTracks.append(Track(self.clsbase, dictConso))
            self.AddObjects(listeTracks)
            self.MAJ_label_page()
        dlg.Destroy()
        
    def Modifier(self, event):  
        if len(self.Selection()) == 0 :
           dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune consommation à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
           dlg.ShowModal()
           dlg.Destroy()
           return
        track = self.Selection()[0]
        from Dlg import DLG_Saisie_contratpsu_conso
        dlg = DLG_Saisie_contratpsu_conso.Dialog(self, clsbase=self.clsbase)
        dlg.SetConso(track)
        if dlg.ShowModal() == wx.ID_OK:
            track.dictValeurs = dlg.GetListeConso()[0]
            track.MAJ()
            self.RefreshObject(track)
            self.MAJ_label_page()
        dlg.Destroy()

    def Supprimer(self, event):  
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune consommation à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les consommations cochées ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()        
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la consommation sélectionnée ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Suppression
        listeSuppressions = []
        for track in listeSelections :
            if track.etat in ("present", "absenti", "absentj") :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la consommation '%s' du %s car elle est déjà pointée !") % (track.nomUnite, UTILS_Dates.DateDDEnFr(track.date)) , _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

            listeSuppressions.append(track)

        # Suppression de la liste
        self.RemoveObjects(listeSuppressions)
        self.MAJ_label_page()

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






    def Importation_unites(self):
        # Récupération des unités
        DB = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.clsbase.GetValeur("IDactivite")
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictUnites = {}
        for IDunite, nom, abrege, type, heure_debut, heure_fin in listeDonnees :
            dictUnites[IDunite] = {"nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "unites_incompatibles" : []}

        # Récupère les incompatibilités entre unités
        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
        FROM unites_incompat;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
            if IDunite in dictUnites : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if IDunite_incompatible in dictUnites : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)

        return dictUnites

    def GetOuverturesUnites(self):
        DB = GestionDB.DB()
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures
        WHERE IDactivite=%d
        ORDER BY date; """ % self.clsbase.GetValeur("IDactivite")
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictOuvertures = {}
        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictOuvertures[(date, IDunite, IDgroupe)] = IDouverture
        return dictOuvertures

    def VerifieCompatibilitesUnites(self, IDunite1=None, IDunite2=None):
        listeIncompatibilites = self.dictUnites[IDunite1]["unites_incompatibles"]
        if IDunite2 in listeIncompatibilites :
            return False
        return True

    def Generation(self, listeConso=[], IDconso=None):

        # Vérification de la validité des dates
        listeAnomalies = []
        nbreConsoValides = 0
        listeConsoFinale = []

        for dictConso in listeConso :

            index = 0
            dateFr = UTILS_Dates.DateDDEnFr(dictConso["date"])
            valide = True

            # Recherche si pas d'incompatibilités avec les conso déjà saisies
            for track in self.GetTracks() :
                if dictConso["date"] == track.date :
                    nomUnite1 = self.dictUnites[dictConso["IDunite"]]["nom"]
                    nomUnite2 = self.dictUnites[track.IDunite]["nom"]

                    if self.VerifieCompatibilitesUnites(track.IDunite, dictConso["IDunite"]) == False :
                        listeAnomalies.append(_(u"%s : Unité %s incompatible avec unité %s déjà présente") % (dateFr, nomUnite1, nomUnite2))
                        valide = False

                    if dictConso["IDunite"] == track.IDunite :
                        if self.dictUnites[dictConso["IDunite"]]["type"] == "Multihoraire" :
                            if dictConso["heure_fin"] > track.heure_debut and dictConso["heure_debut"] < track.heure_fin :
                                listeAnomalies.append(_(u"%s : L'unité multihoraires %s chevauche une consommation d'une unité identique") % (dateFr, nomUnite1))
                                valide = False
                        else :
                            listeAnomalies.append(_(u"%s : Unité %s déjà présente") % (dateFr, nomUnite1))
                            valide = False

            # Vérifie si unité ouverte
            IDgroupe = self.clsbase.GetValeur("IDgroupe")
            if IDgroupe != None and ((dictConso["date"], dictConso["IDunite"], IDgroupe) in self.dictOuvertures) == False :
                listeAnomalies.append(_(u"%s : Unité %s fermée") % (dateFr, self.dictUnites[dictConso["IDunite"]]["nom"]))
                valide = False

            # IDconso pour les modifications
            if IDconso != None :
                dictConso["IDconso"] = IDconso

            # Insertion de la conso validée
            if valide == True :
                listeConsoFinale.append(dictConso)
                nbreConsoValides += 1

                index += 1

        # Signalement des anomalies
        if len(listeAnomalies) :
            message1 = _(u"Les %d anomalies suivantes ont été trouvées.\n\nSouhaitez-vous tout de même générer les %d autres consommations ?") % (len(listeAnomalies), nbreConsoValides)
            message2 = u"\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, message1, caption = _(u"Génération"), msg2=message2, style = wx.ICON_EXCLAMATION | wx.YES|wx.CANCEL|wx.YES_DEFAULT, btnLabels={wx.ID_YES : _(u"Oui"), wx.ID_CANCEL : _(u"Annuler")})
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        if nbreConsoValides == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune consommation à générer !"), _(u"Génération"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Demande de confirmation
        if IDconso == None :
            dlg = wx.MessageDialog(self, _(u"Confirmez-vous la génération de %d consommations ?") % nbreConsoValides, _(u"Génération"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        return listeConsoFinale

    def GenerationSelonPlanning(self, listeConso=[]):
        """ Génération des consommations selon le planning général """
        # Recherche des conso à générer
        listeConso = self.Generation(listeConso=listeConso)
        if listeConso == False :
            return

        # Création des tracks
        listeTracks = []
        for dictConso in listeConso :
            listeTracks.append(Track(self.clsbase, dictConso))
        self.AddObjects(listeTracks)
        self.MAJ_label_page()



# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_soldes
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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date" : {"mode" : "nombre", "singulier" : _(u"consommation"), "pluriel" : _(u"consommations"), "alignement" : wx.ALIGN_CENTER},
            "duree_reelle" : {"mode" : "total", "format" : "temps", "alignement" : wx.ALIGN_CENTER},
            "duree_arrondie" : {"mode" : "total", "format" : "temps", "alignement" : wx.ALIGN_CENTER},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        ctrl = ListviewAvecFooter(panel, kwargs={})
        listview = ctrl.GetListview()
        listview.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(ctrl, 1, wx.ALL|wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
