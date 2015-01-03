#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import datetime
import UTILS_Titulaires
import DATA_Civilites as Civilites
import UTILS_Historique

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


def GetListe(IDclasse=None, IDindividu=None):
    if IDclasse == None and IDindividu == None: 
        return []
    
    # Conditions
    if IDindividu == None :
        condition = "scolarite.IDclasse=%d" % IDclasse
    else:
        condition = "scolarite.IDindividu=%d" % IDindividu
        
    # Récupération des individus
    DB = GestionDB.DB()
    req = """
    SELECT IDscolarite, scolarite.date_debut, scolarite.date_fin, scolarite.IDindividu, scolarite.IDniveau,
    individus.IDcivilite, individus.nom, individus.prenom, individus.date_naiss,
    niveaux_scolaires.abrege, scolarite.IDecole, ecoles.nom, scolarite.IDclasse, classes.nom
    FROM scolarite 
    LEFT JOIN individus ON individus.IDindividu = scolarite.IDindividu
    LEFT JOIN ecoles ON ecoles.IDecole = scolarite.IDecole
    LEFT JOIN classes ON classes.IDclasse = scolarite.IDclasse
    LEFT JOIN niveaux_scolaires ON niveaux_scolaires.IDniveau = scolarite.IDniveau
    WHERE %s
    ORDER BY individus.nom, individus.prenom
    ;""" % condition
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    
    # Récupération des civilités
    dictCivilites = Civilites.GetDictCivilites()
    
    listeListeView = []
    for valeurs in listeDonnees :
        dictTemp = {}
        dictTemp["IDscolarite"] = valeurs[0]
        dictTemp["date_debut"] = valeurs[1]
        dictTemp["date_fin"] = valeurs[2]
        dictTemp["IDindividu"] = valeurs[3]
        dictTemp["IDniveau"] = valeurs[4]
        dictTemp["IDcivilite"] = valeurs[5]
        dictTemp["nomIndividu"] = valeurs[6]
        dictTemp["prenomIndividu"] = valeurs[7]
        dictTemp["date_naiss"] = valeurs[8]
        dictTemp["abregeNiveau"] = valeurs[9]
        dictTemp["IDecole"] = valeurs[10]
        dictTemp["nomEcole"] = valeurs[11]
        dictTemp["IDclasse"] = valeurs[12]
        dictTemp["nomClasse"] = valeurs[13]
        
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
                    
        # Formatage sous forme de TRACK
        track = Track(dictTemp)
        listeListeView.append(track)
        
    return listeListeView


# -----------------------------------------------------------------------------------------------------------------------------------------



class Track(object):
    def __init__(self, donnees):
        self.IDscolarite = donnees["IDscolarite"]
        self.IDindividu = donnees["IDindividu"]
        self.IDcivilite = donnees["IDcivilite"]
        self.nom = donnees["nomIndividu"]
        self.prenom = donnees["prenomIndividu"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        
        self.genre = donnees["genre"]
        self.categorieCivilite = donnees["categorieCivilite"]
        self.civiliteLong = donnees["civiliteLong"]
        self.civiliteAbrege = donnees["civiliteAbrege"]
        self.nomImage = donnees["nomImage"]
        
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]
        self.dateDebutDD = DateEngEnDateDD(self.date_debut)
        self.dateFinDD = DateEngEnDateDD(self.date_fin)

        self.IDecole = donnees["IDecole"]
        self.nomEcole = donnees["nomEcole"]
        if self.nomEcole == None :
            self.nomEcole = u""
        
        self.IDclasse = donnees["IDclasse"]
        self.nomClasse = donnees["nomClasse"]
        if self.nomClasse == None :
            self.nomClasse = u""
            
        self.IDniveau = donnees["IDniveau"]
        self.abregeNiveau = donnees["abregeNiveau"]
        if self.abregeNiveau == None :
            self.abregeNiveau = u""
                    



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.IDclasse = None
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self,event):
        self.Modifier(None)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeListeView = GetListe(IDclasse=self.IDclasse)
        return listeListeView
    
    def GetScolariteIndividu(self, IDindividu=None):
        return GetListe(IDindividu=IDindividu)
        
    def MAJlabelBoxInscrits(self):
        nbre = len(self.donnees)
        try :
            self.GetParent().SetLabelBoxInscrits(nbre)
        except :
            pass
        
    def InitObjectListView(self):
        # Création du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap("Images/16x16/%s" % nomImage, wx.BITMAP_TYPE_PNG))
        
        def GetImageCivilite(track):
            return track.nomImage

        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def FormateAge(age):
            if age == None : return ""
            return u"%d ans" % age
        
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDindividu", typeDonnee="entier", imageGetter=GetImageCivilite),
            ColumnDefn(u"Nom", 'left', 100, "nom", typeDonnee="texte"),
            ColumnDefn(u"Prénom", "left", 100, "prenom", typeDonnee="texte"),
            ColumnDefn(u"Date naiss.", "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(u"Age", "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
            ColumnDefn(u"Niveau", "left", 60, "abregeNiveau", typeDonnee="texte"),
            ColumnDefn(u"Du", "left", 72, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(u"Au", "left", 72, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun inscrit")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDclasse=None):
        self.IDclasse = IDclasse
        self.InitModel()
        self.InitObjectListView()
        self.MAJlabelBoxInscrits() 
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDscolarite
            
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
    
        menuPop.AppendSeparator()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, u"Exporter au format Texte")
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, u"Exporter au format Excel")
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, u"Il n'y a aucune donnée à imprimer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        import UTILS_Printer
        dictInfosClasse = self.GetInfosClasse(self.IDclasse) 
        titre = dictInfosClasse["nom"]
        intro = u"> %s - %d inscrits" % (dictInfosClasse["periode"], len(self.donnees))
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=titre, intro=intro, total="", format="A", orientation=wx.PORTRAIT)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event=None):
        self.Impression("preview")

    def Imprimer(self, event=None):
        self.Impression("print")

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des inscrits")
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des inscrits")
    
    def GetInfosClasse(self, IDclasse=None):
        # Recherche les caractéristiques de la classe
        DB = GestionDB.DB()
        req = """SELECT IDecole, nom, date_debut, date_fin, niveaux
        FROM classes WHERE IDclasse=%d
        ;""" % IDclasse
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        
        IDecole = listeDonnees[0][0]
        nom = listeDonnees[0][1]
        date_debut = listeDonnees[0][2]
        date_fin = listeDonnees[0][3]
        niveaux = listeDonnees[0][4]
        listeNiveaux = []
        if niveaux != None and niveaux != "" :
            listeTemp = niveaux.split(";")
            for IDniveau in listeTemp :
                listeNiveaux.append(int(IDniveau))
        periode = u"Du %s au %s" % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)))
        nomComplet = u"%s (%s)" % (nom, periode)
        
        dictInfos = {"IDecole":IDecole, "nom":nom, "nomComplet":nomComplet, "date_debut":date_debut, "date_fin":date_fin, "periode":periode, "listeNiveaux":listeNiveaux}
        return dictInfos
    
    def Ajouter(self, event=None):
        dictInfosClasse = self.GetInfosClasse(self.IDclasse) 
        IDecole = dictInfosClasse["IDecole"]
        nom = dictInfosClasse["nom"]
        date_debut = dictInfosClasse["date_debut"]
        date_fin = dictInfosClasse["date_fin"]
        listeNiveaux = dictInfosClasse["listeNiveaux"]

        # Ouverture le fenêtre de saisie
        import DLG_Saisie_inscriptions_scolaires
        dlg = DLG_Saisie_inscriptions_scolaires.Dialog(self, IDecole=IDecole, IDclasse=self.IDclasse) 
        dlg.SetNomClasse(nom)
        dlg.SetDateDebut(date_debut)
        dlg.SetDateFin(date_fin)
        dlg.SetListeNiveaux(listeNiveaux)
        if len(listeNiveaux) == 1 :
            dlg.SetNiveau(listeNiveaux[0])
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDclasse=self.IDclasse)
        dlg.Destroy()

    def Modifier(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune inscription à modifier dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        IDscolarite = self.Selection()[0].IDscolarite
        IDindividu = self.Selection()[0].IDindividu
        date_debut = self.Selection()[0].dateDebutDD
        date_fin = self.Selection()[0].dateFinDD
        IDecole = self.Selection()[0].IDecole
        IDclasse = self.Selection()[0].IDclasse
        IDniveau = self.Selection()[0].IDniveau
        nom = self.Selection()[0].nom
        prenom = self.Selection()[0].prenom
        
        # Récupération de toute la scolarité de l'individu
        listeDonneesIndividu = GetListe(IDindividu=IDindividu)
        
        import DLG_Saisie_scolarite
        dlg = DLG_Saisie_scolarite.Dialog(self, IDscolarite=IDscolarite, donneesScolarite=listeDonneesIndividu)
        dlg.SetTitle(u"Modification d'une étape de la scolarité de %s %s" % (prenom, nom))
        dlg.SetDateDebut(date_debut)
        dlg.SetDateFin(date_fin)
        dlg.SetEcole(IDecole)
        dlg.SetClasse(IDclasse)
        dlg.SetNiveau(IDniveau)
        if dlg.ShowModal() == wx.ID_OK:
            date_debut = dlg.GetDateDebut()
            date_fin = dlg.GetDateFin()
            IDecole = dlg.GetEcole()
            IDclasse = dlg.GetClasse()
            IDniveau = dlg.GetNiveau()
            nomEcole = dlg.GetNomEcole()
            nomClasse = dlg.GetNomClasse()
            nomNiveau = dlg.GetNomNiveau()

            # Sauvegarde
            DB = GestionDB.DB()
            listeDonnees = [
                ("date_debut", date_debut ),
                ("date_fin", date_fin ),
                ("IDecole", IDecole),
                ("IDclasse", IDclasse),
                ("IDniveau", IDniveau),
                ]
            DB.ReqMAJ("scolarite", listeDonnees, "IDscolarite", IDscolarite)
            DB.Close()
            
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : IDindividu,
                "IDfamille" : None,
                "IDcategorie" : 31, 
                "action" : u"Inscription scolaire du %s au %s. Ecole : '%s'. Classe : '%s'. Niveau : '%s'" % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nomEcole, nomClasse, nomNiveau)
                },])

            # Actualise l'affichage
            self.MAJ(IDclasse=self.IDclasse)
        dlg.Destroy()


    def Supprimer(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune inscription à supprimer dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDscolarite = self.Selection()[0].IDscolarite
        IDindividu = self.Selection()[0].IDindividu
        nom = self.Selection()[0].nom
        prenom = self.Selection()[0].prenom
        date_debut = self.Selection()[0].dateDebutDD
        date_fin = self.Selection()[0].dateFinDD
        nomEcole = self.Selection()[0].nomEcole
        nomClasse = self.Selection()[0].nomClasse
        abregeNiveau = self.Selection()[0].abregeNiveau
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer l'inscription scolaire de %s %s dans cette classe ?" % (prenom, nom), u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("scolarite", "IDscolarite", IDscolarite)
            DB.Close() 

            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : IDindividu,
                "IDfamille" : None,
                "IDcategorie" : 32, 
                "action" : u"Inscription scolaire du %s au %s. Ecole : '%s'. Classe : '%s'. Niveau : '%s'" % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nomEcole, nomClasse, abregeNiveau)
                },])

            self.MAJ(IDclasse=self.IDclasse)
        dlg.Destroy()



# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un individu...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_inscrits
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

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(IDclasse=6) 
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
