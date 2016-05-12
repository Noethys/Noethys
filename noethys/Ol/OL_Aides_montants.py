#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass

DICT_UNITES = {}


class Track(object):
    def __init__(self, donnees):
        self.IDaide_montant = donnees[0]
        self.montant = donnees[1]
        self.listeCombinaisons = donnees[2]
        self.dictMontant = donnees[3]
        self.index = donnees[4]
        
        self.texteCombinaisons = u""
        for dictCombi in self.listeCombinaisons :
            IDaide_combi = dictCombi["IDaide_combi"]
            listeUnites = dictCombi["listeUnites"]
            texteCombi = u""
            for dictUnite in listeUnites :
                IDaide_combi_unite = dictUnite["IDaide_combi_unite"]
                IDunite = dictUnite["IDunite"]
                nomUnite = DICT_UNITES[IDunite]["nom"]
                texteCombi += nomUnite + " + "
            if len(listeUnites) > 0 :
                texteCombi = texteCombi[:-3]
            self.texteCombinaisons += texteCombi + " OU "
        if len(self.listeCombinaisons) > 0 :
            self.texteCombinaisons = self.texteCombinaisons[:-4]
                
                ##    DONNEES_TEST = {
##    "IDaide_tarif" : None,
##    "montant" : 20.0,
##    "combinaisons" : [
##            { "IDaide_combi" : None, "listeUnites" : 
##                [
##                {"IDaide_combi_unite" : None, "IDunite" : 35}, # Après-midi
##                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
##                ],
##            },
##            { "IDaide_combi" : None, "listeUnites" : 
##                [
##                {"IDaide_combi_unite" : None, "IDunite" : 34}, # Matinée
##                {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
##                ],
##            },
##        ],
##    }

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        global DICT_UNITES
        DICT_UNITES = self.ImportationUnites() 
        self.listeMontants = []
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.IDactivite = None
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
    
    def SetIDactivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.donnees = []
        self.InitObjectListView()
    
    def SetListeMontants(self, listeMontants={}):
        self.listeMontants = listeMontants
        self.MAJ() 
    
    def GetListeMontants(self):
        return self.listeMontants
        
    def InitModel(self):
        self.donnees = self.GetTracks()
    
    def ImportationUnites(self):
        # Recherche des unités disponibles de l'activité
        db = GestionDB.DB()
        req = """SELECT IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin
        FROM unites
        ORDER BY ordre;"""
        db.ExecuterReq(req)
        listeUnites = db.ResultatReq()
        db.Close()
        dictUnites = {}
        for IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin in listeUnites :
            dictUnites[IDunite] = {"ordre":ordre, "nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "date_debut":date_debut, "date_fin":date_fin}
        return dictUnites


    def GetTracks(self):
        """ Récupération des données """
        listeDonnees = []
        index = 0
        for dictMontant in self.listeMontants :
            IDaide_montant = dictMontant["IDaide_montant"]
            montant = dictMontant["montant"]
            listeCombinaisons = dictMontant["combinaisons"]
            listeDonnees.append((IDaide_montant, montant, listeCombinaisons, dictMontant, index))
            index += 1
        
        listeListeView = []
        for item in listeDonnees :
            track = Track(item)
            listeListeView.append(track)
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateMontant(montant):
            if montant == None : return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDaide_montant"),
            ColumnDefn(_(u"Montant"), 'centre', 90, "montant", stringConverter=FormateMontant), 
            ColumnDefn(_(u"Combinaisons d'unités"), 'left', 285, "texteCombinaisons", isSpaceFilling=True), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun montant"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDaide_montant
                
        # Création du menu contextuel
        menuPop = wx.Menu()

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des montants de l'aide"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des montants de l'aide"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        from Dlg import DLG_Saisie_montant_aide
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = DLG_Saisie_montant_aide.Dialog(self, IDactivite=self.IDactivite, dictMontant=None)
        if dlg.ShowModal() == wx.ID_OK:
            dictMontant = dlg.GetDictMontant()
            self.listeMontants.append(dictMontant)
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun montant dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dictMontant = self.Selection()[0].dictMontant
        index = self.Selection()[0].index
        
        from Dlg import DLG_Saisie_montant_aide
        dlg = DLG_Saisie_montant_aide.Dialog(self, IDactivite=self.IDactivite, dictMontant=dictMontant)
        if dlg.ShowModal() == wx.ID_OK:
            dictMontant = dlg.GetDictMontant()
            self.listeMontants[index] = dictMontant
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun montant dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce montant ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            index = self.Selection()[0].index
            self.listeMontants.pop(index)
            self.MAJ()
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une caisse..."))
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

LISTE_TEST = [

    {
        "IDaide_montant" : 1,
        "montant" : 20.0,
        "combinaisons" : [
                { "IDaide_combi" : None, "listeUnites" : 
                    [
                    {"IDaide_combi_unite" : None, "IDunite" : 35}, # Après-midi
                    {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
                    ],
                },
                { "IDaide_combi" : None, "listeUnites" : 
                    [
                    {"IDaide_combi_unite" : None, "IDunite" : 34}, # Matinée
                    {"IDaide_combi_unite" : None, "IDunite" : 33}, # Repas
                    ],
                },
            ],
        },
    ]


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
        
        self.myOlv.SetListeMontants(LISTE_TEST)

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
