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
import datetime
from Data import DATA_Civilites as Civilites


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))



class Track(object):
    def __init__(self, donnees):
        self.IDindividu = donnees["IDindividu"]
        self.nom = donnees["nomIndividu"]
        self.prenom = donnees["prenomIndividu"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        
        self.IDcivilite = donnees["IDcivilite"]
        self.genre = donnees["genre"]
        self.categorieCivilite = donnees["categorieCivilite"]
        self.civiliteLong = donnees["civiliteLong"]
        self.civiliteAbrege = donnees["civiliteAbrege"]
        self.nomImage = donnees["nomImage"]
        
        self.abregeNiveau = donnees["abregeNiveau"]
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.IDecole = None
        self.IDclasse = None
        self.IDniveau = None
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        # Conditions
        conditions = []
        if self.IDecole != None :
            conditions.append("scolarite.IDecole=%d " % self.IDecole)
        if self.IDclasse != None :
            conditions.append("scolarite.IDclasse=%d " % self.IDclasse)
        if self.IDniveau != None :
            conditions.append("scolarite.IDniveau=%d " % self.IDniveau)
        if len(conditions) > 0 :
            txtConditions = "WHERE %s" % " AND ".join(conditions)
        else :
            txtConditions = ""
        
        # Récupération des individus
        DB = GestionDB.DB()
        req = """
        SELECT individus.IDindividu, individus.IDcivilite, individus.nom, individus.prenom, individus.date_naiss,
        IDscolarite, MIN(date_debut), MAX(date_fin), scolarite.IDniveau, niveaux_scolaires.abrege
        FROM individus 
        LEFT JOIN scolarite ON scolarite.IDindividu = individus.IDindividu
        LEFT JOIN niveaux_scolaires ON niveaux_scolaires.IDniveau = scolarite.IDniveau
        %s
        GROUP BY individus.IDindividu
        ORDER BY individus.nom, individus.prenom, scolarite.IDniveau
        ;""" % txtConditions

        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        
        # Récupération des civilités
        dictCivilites = Civilites.GetDictCivilites()
        
        listeListeView = []
        for valeurs in listeDonnees :
            dictTemp = {}
            dictTemp["IDindividu"] = valeurs[0]
            dictTemp["IDcivilite"] = valeurs[1]
            dictTemp["nomIndividu"] = valeurs[2]
            dictTemp["prenomIndividu"] = valeurs[3]
            dictTemp["date_naiss"] = valeurs[4]
            dictTemp["IDscolarite"] = valeurs[5]
            dictTemp["date_debut"] = valeurs[6]
            dictTemp["date_fin"] = valeurs[7]
            dictTemp["IDniveau"] = valeurs[8]
            dictTemp["abregeNiveau"] = valeurs[9]
            
            # Infos sur la civilité
            dictTemp["genre"] = dictCivilites[dictTemp["IDcivilite"]]["sexe"]
            dictTemp["categorieCivilite"] = dictCivilites[dictTemp["IDcivilite"]]["categorie"]
            dictTemp["civiliteLong"]  = dictCivilites[dictTemp["IDcivilite"]]["civiliteLong"]
            dictTemp["civiliteAbrege"] = dictCivilites[dictTemp["IDcivilite"]]["civiliteAbrege"] 
            dictTemp["nomImage"] = dictCivilites[dictTemp["IDcivilite"]]["nomImage"] 
            
            if dictTemp["date_naiss"] == None :
                dictTemp["age"] = None
            else:
                datenaissDD = datetime.date(year=int(dictTemp["date_naiss"][:4]), month=int(dictTemp["date_naiss"][5:7]), day=int(dictTemp["date_naiss"][8:10]))
                datedujour = datetime.date.today()
                age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
                dictTemp["age"] = age
            
            # Spécial
            if self.IDclasse == None :
                dictTemp["IDniveau"] = None
                dictTemp["abregeNiveau"] = u""
                
            # Formatage sous forme de TRACK
            track = Track(dictTemp)
            listeListeView.append(track)
            
        return listeListeView
        
    def InitObjectListView(self):
        # Création du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % nomImage), wx.BITMAP_TYPE_PNG))
        
        def GetImageCivilite(track):
            return track.nomImage

        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def FormateAge(age):
            if age == None : return ""
            return _(u"%d ans") % age
        
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDindividu", typeDonnee="entier", imageGetter=GetImageCivilite),
            ColumnDefn(_(u"Nom"), 'left', 100, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Prénom"), "left", 100, "prenom", typeDonnee="texte"),
            ColumnDefn(_(u"Date naiss."), "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Age"), "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
            ColumnDefn(_(u"Niveau"), "left", 60, "abregeNiveau", typeDonnee="texte"),
            ColumnDefn(u"Du", "left", 72, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Au"), "left", 72, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucun individu"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDecole=None, IDclasse=None, IDniveau=None, forceMAJ=False):
        if forceMAJ == False and self.IDecole == IDecole and self.IDclasse == IDclasse and self.IDniveau == IDniveau :
            return 
        self.IDecole = IDecole
        self.IDclasse = IDclasse
        self.IDniveau = IDniveau
        self.InitModel()
        self.InitObjectListView()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def CocheTout(self, event=None):
        for track in self.donnees :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def GetCoches(self):
        listeDonnees = []
        for track in self.GetTracksCoches() :
            listeDonnees.append(track.IDindividu)
        return listeDonnees

# -------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un individu..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_individus
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
        self.myOlv.MAJ(IDecole=2, IDclasse=6) 
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
