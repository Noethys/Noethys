#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB
import UTILS_Dates

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")



def GetCondition(titre="", typeDonnee="", choix="", criteres=""):
    description = u""
    
    # TEXTE
    if typeDonnee == "texte" :
        if choix == "EGAL" : description = _(u"'%s' est égal à '%s'") % (titre, criteres)
        if choix == "DIFFERENT" : description = _(u"'%s' est différent de '%s'") % (titre, criteres)
        if choix == "CONTIENT" : description = _(u"'%s' contient '%s'") % (titre, criteres)
        if choix == "CONTIENTPAS" : description = _(u"'%s' ne contient pas '%s'") % (titre, criteres)
        if choix == "VIDE" : description = _(u"'%s' est vide") % titre
        if choix == "PASVIDE" : description = _(u"'%s' n'est pas vide") % titre
    
    # ENTIER
    if typeDonnee == "entier" :
        if choix == "EGAL" : description = _(u"'%s' est égal à '%s'") % (titre, criteres)
        if choix == "DIFFERENT" : description = _(u"'%s' est différent de '%s'") % (titre, criteres)
        if choix == "SUP" : description = _(u"'%s' est supérieur à '%s'") % (titre, criteres)
        if choix == "SUPEGAL" : description = _(u"'%s' est supérieur ou égal à '%s'") % (titre, criteres)
        if choix == "INF" : description = _(u"'%s' est inférieur à '%s'") % (titre, criteres)
        if choix == "INFEGAL" : description = _(u"'%s' est inférieur ou égal à '%s'")  % (titre, criteres)
        if choix == "COMPRIS" : description = _(u"'%s' est compris entre '%s' et '%s'") % (titre, criteres.split(";")[0], criteres.split(";")[1])

    # MONTANT
    if typeDonnee == "montant" :
        if choix == "EGAL" : description = _(u"'%s' est égal à %.2f %s") % (titre, float(criteres), SYMBOLE)
        if choix == "DIFFERENT" : description = _(u"'%s' est différent de %.2f %s") % (titre, float(criteres), SYMBOLE)
        if choix == "SUP" : description = _(u"'%s' est supérieur à %.2f %s") % (titre, float(criteres), SYMBOLE)
        if choix == "SUPEGAL" : description = _(u"'%s' est supérieur ou égal à %.2f %s") % (titre, float(criteres), SYMBOLE)
        if choix == "INF" : description = _(u"'%s' est inférieur à %.2f %s") % (titre, float(criteres), SYMBOLE)
        if choix == "INFEGAL" : description = _(u"'%s' est inférieur ou égal à %.2f %s") % (titre, float(criteres), SYMBOLE)
        if choix == "COMPRIS" : description = _(u"'%s' est compris entre %.2f %s et %.2f %s") % (titre, float(criteres.split(";")[0]), SYMBOLE, float(criteres.split(";")[1]), SYMBOLE)

    # DATE
    if typeDonnee == "date" :
        if choix == "EGAL" : description = _(u"'%s' est égal au '%s'") % (titre, UTILS_Dates.DateEngFr(criteres))
        if choix == "DIFFERENT" : description = _(u"'%s' est différent du '%s'") % (titre, UTILS_Dates.DateEngFr(criteres))
        if choix == "SUP" : description = _(u"'%s' est supérieur au '%s'") % (titre, UTILS_Dates.DateEngFr(criteres))
        if choix == "SUPEGAL" : description = _(u"'%s' est supérieur ou égal au '%s'") % (titre, UTILS_Dates.DateEngFr(criteres))
        if choix == "INF" : description = _(u"'%s' est inférieur au '%s'") % (titre, UTILS_Dates.DateEngFr(criteres))
        if choix == "INFEGAL" : description = _(u"'%s' est inférieur ou égal au '%s'") % (titre, UTILS_Dates.DateEngFr(criteres))
        if choix == "COMPRIS" : description = _(u"'%s' est compris entre le '%s' et le '%s'") % (titre, UTILS_Dates.DateEngFr(criteres.split(";")[0]), UTILS_Dates.DateEngFr(criteres.split(";")[1]))

    # INSCRITS
    if typeDonnee == "inscrits" :
        if choix == "INSCRITS" : description = _(u"L'individu est inscrit sur les activités sélectionnées")
        if choix == "PRESENTS" : description = _(u"L'individu est inscrit sur les activités sélectionnées et présent entre le %s et le %s") % (UTILS_Dates.DateDDEnFr(criteres["date_debut"]), UTILS_Dates.DateDDEnFr(criteres["date_fin"]))
        
    return description




class Track(object):
    def __init__(self, parent, donnees, index):
        self.code = donnees["code"]
        self.typeDonnee = donnees["typeDonnee"]
        self.choix = donnees["choix"]
        self.criteres = donnees["criteres"]
        self.titre = donnees["titre"]
        self.index = index
        
        # Création de la description
        self.condition = GetCondition(self.titre, self.typeDonnee, self.choix, self.criteres)


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.ctrl_listview = kwds.pop("ctrl_listview", None)
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
        if self.ctrl_listview != None :
            self.listeFiltres = self.ctrl_listview.listeFiltresColonnes

    def SetDonnees(self, listeFiltres=[]):
        self.listeFiltres = listeFiltres
        self.MAJ() 
    
    def GetDonnees(self):
        listeFiltres = []
        for track in self.donnees :
            listeFiltres.append({"code":track.code, "choix":track.choix, "criteres":track.criteres, "typeDonnee":track.typeDonnee, "titre":track.titre})
        return listeFiltres

    def OnItemActivated(self,event):
        self.Modifier(None)
    
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeListeView = []
        
        # Récupération des titres des colonnes
        dictColonnes = {}
        if self.ctrl_listview != None :
            for colonne in self.ctrl_listview.listeColonnes :
                dictColonnes[colonne.valueGetter] = {"typeDonnee" : colonne.typeDonnee, "titre" : colonne.title}
            
        # Lecture de la liste des filtres
        self.dictTracks = {}
        index = 0
        for dictTemp in self.listeFiltres :
##            dictTemp["typeDonnee"] = dictColonnes[dictTemp["code"]]["typeDonnee"]
##            dictTemp["titre"] = dictColonnes[dictTemp["code"]]["titre"]
            track = Track(self, dictTemp, index)
            listeListeView.append(track)
            index += 1
        return listeListeView
    
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, ""),
            ColumnDefn(_(u"Condition"), 'left', 165, "condition", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun filtre"))
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
                
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event=None):
        # Ouverture de la fenêtre de saisie
        import DLG_Saisie_filtre_listes
        dlg = DLG_Saisie_filtre_listes.Dialog(self, ctrl_listview=self.ctrl_listview)
        if dlg.ShowModal() == wx.ID_OK:
            dictTemp = {"code":dlg.GetCode(), "typeDonnee" : dlg.GetTypeDonnee(), "choix":dlg.GetValeur()[0], "criteres":dlg.GetValeur()[1], "titre":dlg.GetTitre()}
            self.listeFiltres.append(dictTemp)
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun filtre à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        import DLG_Saisie_filtre_listes
        dlg = DLG_Saisie_filtre_listes.Dialog(self, ctrl_listview=self.ctrl_listview)
        dlg.SetCode(track.code)
        dlg.SetValeur(track.choix, track.criteres)
        if dlg.ShowModal() == wx.ID_OK:
            dictTemp = {"code":dlg.GetCode(), "typeDonnee" : dlg.GetTypeDonnee(), "choix":dlg.GetValeur()[0], "criteres":dlg.GetValeur()[1], "titre":dlg.GetTitre()}
            self.listeFiltres[track.index] = dictTemp
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun filtre à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce filtre ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.listeFiltres.pop(track.index)
            self.MAJ()
        dlg.Destroy()
    
    def ToutSupprimer(self, event):
        self.listeFiltres = []
        self.MAJ() 
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un filtre..."))
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
                
        self.myOlv = ListView(panel, ctrl_listview=None, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
