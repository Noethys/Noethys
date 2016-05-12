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
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Dates
import datetime
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

LISTE_MOIS= (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))

  
class Track(object):
    def __init__(self, dictValeurs={}):
        self.dictValeurs = dictValeurs
        self.MAJ()

    def MAJ(self):
        self.IDprestation = self.dictValeurs["IDprestation"]
        self.date_facturation = self.dictValeurs["date_facturation"]
        self.forfait_date_debut = self.dictValeurs["forfait_date_debut"]
        self.forfait_date_fin = self.dictValeurs["forfait_date_fin"]
        self.taux = self.dictValeurs["taux"]
        self.tarif_base = self.dictValeurs["tarif_base"]
        self.tarif_depassement = self.dictValeurs["tarif_depassement"]

        # Prévisions
        self.heures_prevues = self.dictValeurs["heures_prevues"]
        self.montant_prevu = self.dictValeurs["montant_prevu"]

        # Facturé
        self.IDfacture = self.dictValeurs["IDfacture"]
        self.num_facture = self.dictValeurs["num_facture"]
        self.heures_facturees = self.dictValeurs["heures_facturees"]
        self.montant_facture = self.dictValeurs["montant_facture"]

        self.mois = self.date_facturation.month
        self.annee = self.date_facturation.year
        self.annee_mois = (self.annee, self.mois)

        self.label_prestation = u"%s %s" % (LISTE_MOIS[self.mois-1], self.annee)


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
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.donnees = []
        self.listeDonnees = []
        self.InitObjectListView()


    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateDDEnFr(dateDD)

        def FormateMontant(montant):
            if montant in ("", None, FloatToDecimal(0.0)) :
                return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateMontant2(montant):
            if montant == None or montant == "" : return ""
            return u"%.5f %s" % (montant, SYMBOLE)

        def FormateDuree(duree):
            if duree in (None, "", datetime.timedelta(seconds=0)):
                return ""
            else :
                return UTILS_Dates.DeltaEnStr(duree, separateur="h")

        def FormateMois(donnee):
            if donnee in ("", None):
                return ""
            else :
                annee, mois = donnee
                return u"%s %s" % (LISTE_MOIS[mois-1], annee)

        liste_Colonnes = [
            ColumnDefn(_(u"IDprestation"), "left", 0, "IDprestation", typeDonnee="entier"),
            ColumnDefn(_(u"Mois"), 'left', 110, "annee_mois", typeDonnee="texte", stringConverter=FormateMois),
            ColumnDefn(_(u"Heures prév."), 'center', 80, "heures_prevues", typeDonnee="duree", stringConverter=FormateDuree),
            ColumnDefn(_(u"Montant prév."), 'center', 90, "montant_prevu", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Date fact."), 'center', 80, "date_facturation", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Heures fact."), 'center', 80, "heures_facturees", typeDonnee="duree", stringConverter=FormateDuree),
            ColumnDefn(_(u"Montant fact."), 'center', 90, "montant_facture", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"N° Facture"), 'center', 70, "num_facture", typeDonnee="entier"),
            ColumnDefn(_(u"Taux"), 'center', 80, "taux", typeDonnee="montant", stringConverter=FormateMontant2),
            ColumnDefn(_(u"Tarif de base"), 'center', 80, "tarif_base", typeDonnee="montant", stringConverter=FormateMontant2),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune mensualité"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(1)
        
    def MAJ(self):
        self.SetObjects(self.donnees)
        self._ResizeSpaceFillingColumns() 

    def GetTracks(self):
        return self.GetObjects()

    def SetTracks(self, tracks=[]):
        self.donnees = tracks
        self.MAJ()

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = wx.Menu()

        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Création du menu contextuel
        menuPop = wx.Menu()

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualités"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualités"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des mensualités"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des mensualités"), autoriseSelections=False)


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "annee_mois" : {"mode" : "nombre", "singulier" : _(u"mensualité"), "pluriel" : _(u"mensualités"), "alignement" : wx.ALIGN_CENTER},
            "heures_prevues" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_prevu" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},
            "heures_facturees" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_facture" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},
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
