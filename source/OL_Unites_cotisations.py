#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import DLG_Saisie_unite_cotisation


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class Track(object):
    def __init__(self, donnees, index):
        self.index = index
        self.IDunite_cotisation = donnees["IDunite_cotisation"]
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]
        self.defaut = donnees["defaut"]
        self.nom = donnees["nom"]
        self.montant = donnees["montant"]
        self.label_prestation = donnees["label_prestation"]
        
        date_jour = datetime.date.today()
        if self.date_fin > date_jour :
            self.valide = True
        else:
            self.valide = False

        self.estActuel = False
        if date_jour >= self.date_debut and date_jour <= self.date_fin :
            self.estActuel = True

            
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDtype_cotisation = kwds.pop("IDtype_cotisation", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.listeDonnees = []
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
        listeID = None
        listeListeView = []
        index = 0
        for dictValeurs in self.listeDonnees :
            IDunite_cotisation = dictValeurs["IDunite_cotisation"]
            etat = dictValeurs["etat"]
            if etat != "SUPPR" :
                valide = True
                if listeID != None :
                    if IDunite_cotisation not in listeID :
                        valide = False
                if valide == True :
                    track = Track(dictValeurs, index)
                    dictValeurs["track"] = track
                    listeListeView.append(track)
                    if self.selectionID == IDunite_cotisation :
                        self.selectionTrack = track
            index += 1
        return listeListeView
    
    def SetListeDonnees(self, listeDonnees=[]):
        self.listeDonnees = listeDonnees
    
    def GetListeDonnees(self):
        return self.listeDonnees
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        imgDefaut = self.AddNamedImages("defaut", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageDefaut(track):
            if track.defaut == 1 : return "defaut"
            else: return None 

        def FormateDate(dateDD):
            if dateDD == None : return ""
            if dateDD == datetime.date(2999, 1, 1) : return _(u"Illimitée")
            date = str(dateDD)
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text

        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))
        
        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)


        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDunite_cotisation", typeDonnee="entier", imageGetter=GetImageDefaut),
            ColumnDefn(u"Du", 'left', 70, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Au"), 'left', 70, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Nom"), 'left', 150, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), 'right', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune unité de cotisation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDunite_cotisation
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
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
        
        # Item Par défaut
        item = wx.MenuItem(menuPop, 60, _(u"Définir comme unité par défaut"))
        if noSelection == False :
            if self.Selection()[0].defaut == 1 :
                bmp = wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.SetDefaut, id=60)
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des unités de cotisations"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des unités de cotisations"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        nomTypeCotisation = self.GetParent().ctrl_nom.GetValue()
        dlg = DLG_Saisie_unite_cotisation.Dialog(self, nomTypeCotisation=nomTypeCotisation, dictDonnees={})
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDictDonnees()
            if len(self.donnees) == 0 :
                dictDonnees["defaut"] = 1
            self.listeDonnees.append(dictDonnees)
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune unité de cotisation à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        nomTypeCotisation = self.GetParent().ctrl_nom.GetValue()
        index = self.Selection()[0].index
        dictDonnees = self.listeDonnees[index]
        dlg = DLG_Saisie_unite_cotisation.Dialog(self, nomTypeCotisation=nomTypeCotisation, dictDonnees=dictDonnees)
        if dlg.ShowModal() == wx.ID_OK:
            self.listeDonnees[index] = dlg.GetDictDonnees()
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune unité de cotisation à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite_cotisation = self.Selection()[0].IDunite_cotisation
        index = self.Selection()[0].index
        dictDonnees = self.listeDonnees[index]
        
        # Vérifie que l'unité n'est pas déjà attribuée à une cotisation
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDcotisation)
        FROM cotisations 
        WHERE IDunite_cotisation=%d
        ;""" % IDunite_cotisation
        DB.ExecuterReq(req)
        nbreCotisations = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreCotisations > 0 :
            dlg = wx.MessageDialog(self, _(u"Cette unité de cotisation a déjà été attribuée à %d cotisations(s).\n\nVous ne pouvez donc pas la supprimer !") % nbreCotisations, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette unité de cotisation ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            dictDonnees["etat"] = "SUPPR"
            # Met le défaut sur un autre item
            if dictDonnees["defaut"] == 1 :
                indexTmp = 0
                attribue = False
                for dictDonneesTemp in self.listeDonnees :
                    if attribue == False and indexTmp != index and dictDonneesTemp["etat"] != "SUPPR" :
                        dictDonneesTemp["defaut"] = 1
                        attribue = True
                    indexTmp += 1
            dictDonnees["defaut"] = 0
            self.MAJ()
        dlg.Destroy()

    def SetDefaut(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune unité de cotisation dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        trackSelection = self.Selection()[0]
        for dictDonnees in self.listeDonnees :
            if dictDonnees["track"] == trackSelection :
                dictDonnees["defaut"] = 1
                dictDonnees["etat"] = "MODIF"
            else:
                dictDonnees["defaut"] = 0
                dictDonnees["etat"] = "MODIF"
        self.MAJ()




class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, IDtype_cotisation=1, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
