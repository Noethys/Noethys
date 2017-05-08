#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _

import wx
from Ctrl import CTRL_Bouton_image
import datetime
import decimal
import time
import copy
import sys
import traceback
import wx.lib.agw.pybusyinfo as PBI

import GestionDB
from Utils import UTILS_Dates
import FonctionsPerso
from Utils import UTILS_Impression_facture
from Dlg import DLG_Apercu_facture
from Utils import UTILS_Facturation
from Utils import UTILS_Titulaires

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter



class Track(object):
    def __init__(self, IDcompte_payeur, dictCompte):
        self.IDcompte_payeur = IDcompte_payeur
        self.dictCompte = dictCompte
        self.IDfamille = dictCompte["IDfamille"]
        self.total = dictCompte["total"]
        self.ventilation = dictCompte["ventilation"]
        self.du_periode = self.total - self.ventilation
        self.total_reports = dictCompte["total_reports"]
        self.du_total = self.total - self.ventilation + self.total_reports
        self.nomSansCivilite = dictCompte["nomSansCivilite"]

        
                                
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.dictParametres = {}
        self.dictComptes = {}
        FastObjectListView.__init__(self, *args, **kwds)
        # DictTitulaires
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnActivated(self,event):
        self.AfficherApercu(None)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        # Récupération des données
        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des prestations à facturer en cours..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        try :
            facturation = UTILS_Facturation.Facturation()
            self.dictComptes = facturation.GetDonnees(  liste_activites=self.dictParametres["listeActivites"],
                                                        date_debut=self.dictParametres["date_debut"],
                                                        date_fin=self.dictParametres["date_fin"],
                                                        date_edition=self.dictParametres["date_emission"],
                                                        date_echeance=self.dictParametres["date_echeance"],
                                                        prestations=self.dictParametres["prestations"],
                                                        date_anterieure=self.dictParametres["date_anterieure"],
                                                        )
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la recherche de factures : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Condition famille unique
        if self.dictParametres["IDcompte_payeur"] != None :
            IDcompte_payeur = self.dictParametres["IDcompte_payeur"]
            if self.dictComptes.has_key(IDcompte_payeur) :
                self.dictComptes = { IDcompte_payeur : self.dictComptes[IDcompte_payeur],}
            else :
                self.dictComptes = {}
            
        # Branches COMPTE
        listeListeView = []
        for IDcompte_payeur, dictCompte in self.dictComptes.iteritems() :
            track = Track(IDcompte_payeur, dictCompte)
            listeListeView.append(track)
        return listeListeView

    def InitObjectListView(self):
        # ImageList
        self.imgVert = self.AddNamedImages("vert", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG))

        def GetImageDuPeriode(track):
            if track.total == track.ventilation :
                return self.imgVert
            if track.ventilation == 0.0 or track.ventilation == None :
                return self.imgRouge
            if track.ventilation < track.total :
                return self.imgOrange
            return self.imgRouge

        def GetImageDuTotal(track):
            if track.du_total == 0.0 or track.du_total == None :
                return self.imgVert
            return self.imgRouge

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
        self.SetColumns([
            ColumnDefn(_(u"IDfamille"), "left", 0, "IDfamille", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), "left", 195, "nomSansCivilite", typeDonnee="texte"),#, isSpaceFilling=True),
            ColumnDefn(_(u"Total période"), "right", 85, "total", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Déjà réglé"), "right", 85, "ventilation", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Dû période"), "right", 85, "du_periode", typeDonnee="montant", stringConverter=FormateMontant, imageGetter=GetImageDuPeriode),
            ColumnDefn(_(u"Rep. impayés"), "right", 90, "total_reports", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Dû total"), "right", 85, "du_total", typeDonnee="montant", stringConverter=FormateMontant, imageGetter=GetImageDuTotal),
        ])
        self.CreateCheckStateColumn(0)
        self.SetSortColumn(self.columns[2])
        self.SetEmptyListMsg(_(u"Aucune facture à générer"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetObjects(self.donnees)
    
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
        #self._ResizeSpaceFillingColumns()
        self.CocheListeTout()
        self.Refresh()
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        ID = None
        if len(self.Selection()) > 0 :
            ID = self.Selection()[0].IDcompte_payeur
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 5, _(u"Afficher un aperçu PDF"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.AfficherApercu, id=5)
        if ID == None : item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Tout cocher
        item = wx.MenuItem(menuPop, 70, _(u"Tout cocher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeTout, id=70)

        # Item Tout décocher
        item = wx.MenuItem(menuPop, 80, _(u"Tout décocher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Decocher.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheListeRien, id=80)

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des factures à générer"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des factures à générer"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des factures à générer"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des factures à générer"))
        
    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def SetParametres(self, dictParametres={}):
        self.dictParametres = dictParametres
        self.MAJ() 

    def AfficheNbreComptes(self, nbreComptes=0):
        grandParent = self.GetGrandParent()
        if grandParent.GetName() == "DLG_Factures_generation_selection" :
            if nbreComptes == 0 : label = _(u"Aucune facture sélectionnée")
            elif nbreComptes == 1 : label = _(u"1 facture sélectionnée")
            else: label = _(u"%d factures sélectionnées") % nbreComptes
            grandParent.box_factures_staticbox.SetLabel(label)

    def OnCheck(self, track=None):
        self.AfficheNbreComptes(len(self.GetTracksCoches()))

    def CocherMontant(self, montant=0.0):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            if track.du_periode >= montant :
                self.Check(track)
            else :
                self.Uncheck(track)
            #self.RefreshObject(track)
        self.Refresh()
        self.OnCheck()

    def AfficherApercu(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDfamille = track.IDfamille
        IDcompte_payeur = track.IDcompte_payeur
        
        # Récupération des données
        dictCompte = self.dictComptes[IDcompte_payeur]

        # Récupération des paramètres d'affichage
        dlg = DLG_Apercu_facture.Dialog(self, provisoire=True)
        if dlg.ShowModal() == wx.ID_OK:
            dictOptions = dlg.GetParametres()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return False
                   
        # Fabrication du PDF
        dlgAttente = PBI.PyBusyInfo(_(u"Création de l'aperçu au format PDF..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        try :
            UTILS_Impression_facture.Impression({IDcompte_payeur : dictCompte}, dictOptions, IDmodele=dictOptions["IDmodele"])
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la création de l'aperçu de la facture : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def GetListeComptes(self):
        return self.dictComptes.keys() 



# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomSansCivilite" : {"mode" : "nombre", "singulier" : _(u"facture"), "pluriel" : _(u"factures"), "alignement" : wx.ALIGN_CENTER},
            "total" : {"mode" : "total"},
            "ventilation" : {"mode" : "total"},
            "du_periode" : {"mode" : "total"},
            "total_reports" : {"mode" : "total"},
            "du_total" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


# -----------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        # Données pour les tests
        date_debut = datetime.date(2010, 10, 4)
        date_fin = datetime.date(2012, 11, 30)
        liste_activites = [1, 3]
        
        self.listviewAvecFooter = ListviewAvecFooter(panel) 
        self.ctrl = self.listviewAvecFooter.GetListview()
        
        dictParametres = {
            "date_debut" : datetime.date(2015, 7, 1),
            "date_fin" : datetime.date(2015, 7, 31),
            "date_emission" : datetime.date.today(),
            "date_echeance" : None,
            "prestations" : ["consommation", "cotisation", "autre"],
            "IDcompte_payeur" : None,
            "listeActivites" : [1, 2, 3],
            }
            
        import time
        h = time.time()
        self.ctrl.SetParametres(dictParametres) 
        print time.time() - h
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.listviewAvecFooter, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
