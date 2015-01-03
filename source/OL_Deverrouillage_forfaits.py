#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import datetime
import UTILS_Dates

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, ListCtrlPrinter


class Track(object):
    def __init__(self, donnees):
        self.IDconso = donnees["IDconso"]
        self.date = donnees["date"]
        self.IDactivite = donnees["IDactivite"]
        self.nomActivite = donnees["nomActivite"]
        self.IDunite = donnees["IDunite"]
        self.nomUnite = donnees["nomUnite"]
        self.IDindividu = donnees["IDindividu"]
        self.nomIndividu = donnees["nomIndividu"]
        self.prenomIndividu = donnees["prenomIndividu"]
        self.individu = u"%s %s" % (self.nomIndividu, self.prenomIndividu)
            
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
                        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        # Recherche si des consommations y sont attachées
        DB = GestionDB.DB()
        req = """
        SELECT IDconso, date, consommations.IDactivite, activites.nom, etat, consommations.IDunite, 
        unites.nom, consommations.IDindividu, individus.nom, individus.prenom, forfait
        FROM consommations
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        WHERE forfait=2
        ORDER BY date
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq() 
        DB.Close() 
        listeConsommations = []
        for IDconso, date, IDactivite, nomActivite, etat, IDunite, nomUnite, IDindividu, nomIndividu, prenomIndividu, forfait in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictTemp = {
            "IDconso" : IDconso, "date" : date, "IDactivite" : IDactivite, "nomActivite" : nomActivite, 
            "IDunite" : IDunite, "nomUnite" : nomUnite, 
            "IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu,
            "forfait" : forfait,
            }
            listeConsommations.append(dictTemp)
        listeListeView = []
        for item in listeConsommations :
            track = Track(item)
            listeListeView.append(track)
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(dateDD):
            return UTILS_Dates.DateComplete(dateDD)

        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 50, "IDconso"),
            ColumnDefn(u"Date", 'left', 150, "date", stringConverter=FormateDate),
            ColumnDefn(u"Individu", "left", 180, "individu"),
            ColumnDefn(u"Activité", "left", 160, "nomActivite"),
            ColumnDefn(u"Unité", "left", 160, "nomUnite"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(u"Aucune consommation")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
           
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
    
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
    
    def Deverrouillage(self):
        nbreCoches = len(self.GetTracksCoches())
        if nbreCoches == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez coché aucune consommation à déverrouiller !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment déverrouiller les %d consommations cochées ?" % nbreCoches, u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        dlg.Destroy()

        # Déverrouillage
        DB = GestionDB.DB()
        for track in self.GetTracksCoches() :
            DB.ReqMAJ("consommations", [("forfait", 1),], "IDconso", track.IDconso)
        DB.Close()
        self.MAJ() 
                
# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher une information...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)
    
    def OnEnter(self, event):
        listeObjets = self.listView.GetFilteredObjects()
        if len(listeObjets) == 0 : return
        track = listeObjets[0]
        self.listView.SelectObject(track)
        if self.GetParent().GetName() == "DLG_medecin" :
            self.GetParent().OnBouton_ok(None)
        
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

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
