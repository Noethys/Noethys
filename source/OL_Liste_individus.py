#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import UTILS_Titulaires
import DATA_Civilites as Civilites
import UTILS_Infos_individus

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass

DICT_INFOS_INDIVIDUS = {}


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def GetDictInfosIndividus():
    global DICT_INFOS_INDIVIDUS
    dictInfos = {}
    db = GestionDB.DB()
    req = """SELECT IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid FROM individus;"""
    db.ExecuterReq(req)
    listeDonnees = db.ResultatReq()
    db.Close()
    for IDindividu, nom, prenom, rue_resid, cp_resid, ville_resid in listeDonnees :
        dictInfos[IDindividu] = { "nom" : nom, "prenom" : prenom, "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid}
    DICT_INFOS_INDIVIDUS = dictInfos

def GetListe(listeActivites=None, presents=None):
    if listeActivites == None : return []

    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND inscriptions.IDactivite=%d" % listeActivites[0]
        else:
            conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(listeActivites))

    # Conditions Pr�sents
##    if presents == None :
##        conditionPresents = ""
##        jointurePresents = ""
##    else:
##        conditionPresents = " AND consommations.date>='%s' AND consommations.date<='%s' AND consommations.etat IN ('reservation', 'present')" % (str(presents[0]), str(presents[1]))
##        jointurePresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"
    
    DB = GestionDB.DB()
    
    # R�cup�ration des pr�sents
    listePresents = []
    if presents != None :
        req = """SELECT IDindividu, IDinscription
        FROM consommations
        WHERE date>='%s' AND date<='%s' %s
        GROUP BY IDindividu
        ;"""  % (str(presents[0]), str(presents[1]), conditionActivites.replace("inscriptions", "consommations"))
        DB.ExecuterReq(req)
        listeIndividusPresents = DB.ResultatReq()
        for IDindividu, IDinscription in listeIndividusPresents :
            listePresents.append(IDindividu)

    # R�cup�ration des individus
    listeChamps = (
        "individus.IDindividu", "IDcivilite", "nom", "prenom", "num_secu","IDnationalite", 
        "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
        "adresse_auto", "rue_resid", "cp_resid", "ville_resid", 
        "IDcategorie_travail", "profession", "employeur", "travail_tel", "travail_fax", "travail_mail", 
        "tel_domicile", "tel_mobile", "tel_fax", "mail"
        )
    
    req = """
    SELECT %s
    FROM inscriptions 
    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
    WHERE inscriptions.parti=0 %s
    GROUP BY individus.IDindividu
    ;""" % (",".join(listeChamps), conditionActivites)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    
    # R�cup�ration des civilit�s
    dictCivilites = Civilites.GetDictCivilites()
    
    # R�cup�ration des adresses auto
    GetDictInfosIndividus()

    listeListeView = []
    for valeurs in listeDonnees :
        IDindividu = valeurs[0]
        
        if presents == None or (presents != None and IDindividu in listePresents) :
            
            dictTemp = {}
            dictTemp["IDindividu"] = valeurs[0]
            # Infos de la table Individus
            for index in range(0, len(listeChamps)) :
                nomChamp = listeChamps[index]
                dictTemp[nomChamp] = valeurs[index]
            # Infos sur la civilit�
            if dictTemp["IDcivilite"] != None and dictTemp["IDcivilite"] != "" : 
                IDcivilite = dictTemp["IDcivilite"]
            else :
                IDcivilite = 1
            dictTemp["genre"] = dictCivilites[IDcivilite]["sexe"]
            dictTemp["categorieCivilite"] = dictCivilites[IDcivilite]["categorie"]
            dictTemp["civiliteLong"]  = dictCivilites[IDcivilite]["civiliteLong"]
            dictTemp["civiliteAbrege"] = dictCivilites[IDcivilite]["civiliteAbrege"] 
            dictTemp["nomImage"] = dictCivilites[IDcivilite]["nomImage"] 
            
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
        self.IDindividu = donnees["IDindividu"]
        self.IDcivilite = donnees["IDcivilite"]
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        self.IDnationalite = donnees["IDnationalite"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        self.IDpays_naiss = donnees["IDpays_naiss"]
        self.cp_naiss = donnees["cp_naiss"]
        self.ville_naiss = donnees["ville_naiss"]
        self.adresse_auto = donnees["adresse_auto"]
        
        # Adresse auto ou manuelle
        if self.adresse_auto != None and DICT_INFOS_INDIVIDUS.has_key(self.adresse_auto) :
            self.rue_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["rue_resid"]
            self.cp_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["cp_resid"]
            self.ville_resid = DICT_INFOS_INDIVIDUS[self.adresse_auto]["ville_resid"]
        else:
            self.rue_resid = donnees["rue_resid"]
            self.cp_resid = donnees["cp_resid"]
            self.ville_resid = donnees["ville_resid"]
        
        self.profession = donnees["profession"]
        self.employeur = donnees["employeur"]
        self.travail_tel = donnees["travail_tel"]
        self.travail_fax = donnees["travail_fax"]
        self.travail_mail = donnees["travail_mail"]
        self.tel_domicile = donnees["tel_domicile"]
        self.tel_mobile = donnees["tel_mobile"]
        self.tel_fax = donnees["tel_fax"]
        self.mail = donnees["mail"]
        self.tel_fax = donnees["tel_fax"]
        self.genre = donnees["genre"]
        self.categorieCivilite = donnees["categorieCivilite"]
        self.civiliteLong = donnees["civiliteLong"]
        self.civiliteAbrege = donnees["civiliteAbrege"]
        self.nomImage = donnees["nomImage"]
        
            
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.dateReference = None
        self.listeActivites = None
        self.presents = None
        self.concernes = False
        self.labelParametres = ""
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        self.donnees = self.GetTracks()
        # R�cup�ration des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations() 
        for track in self.donnees :
            self.infosIndividus.SetAsAttributs(parent=track, mode="individu", ID=track.IDindividu)

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        listeListeView = GetListe(self.listeActivites, self.presents)
##        listeListeView = []
##        for IDfamille, dictTemp in dictDonnees.iteritems() :
##            track = Track(dictTemp)
##            listeListeView.append(track)
##            if self.selectionID == IDfamille :
##                self.selectionTrack = track
        return listeListeView

    def InitObjectListView(self):
        # Cr�ation du imageList
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
            return _(u"%d ans") % age
        
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDindividu", typeDonnee="entier", imageGetter=GetImageCivilite),
            ColumnDefn(_(u"Nom"), 'left', 100, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Pr�nom"), "left", 100, "prenom", typeDonnee="texte"),
            ColumnDefn(_(u"Date naiss."), "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Genre"), "left", 50, "genre", typeDonnee="texte"),
            ColumnDefn(_(u"Age"), "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
            ColumnDefn(_(u"Rue"), "left", 150, "rue_resid", typeDonnee="texte"),
            ColumnDefn(_(u"C.P."), "left", 50, "cp_resid", typeDonnee="texte"),
            ColumnDefn(_(u"Ville"), "left", 120, "ville_resid", typeDonnee="texte"),
            ColumnDefn(_(u"T�l. domicile"), "left", 100, "tel_domicile", typeDonnee="texte"),
            ColumnDefn(_(u"T�l. mobile"), "left", 100, "tel_mobile", typeDonnee="texte"),
            ColumnDefn(_(u"Email"), "left", 150, "mail", typeDonnee="texte"),
            ]
        
        # Insertion des champs infos de base individus
        listeChamps = self.infosIndividus.GetNomsChampsPresents(mode="individu")
        for nomChamp in listeChamps :
            typeDonnee = UTILS_Infos_individus.GetTypeChamp(nomChamp)
            liste_Colonnes.append(ColumnDefn(nomChamp, "left", 100, nomChamp, typeDonnee=typeDonnee, visible=False))


        self.SetColumns2(colonnes=liste_Colonnes, nomListe="OL_Liste_individus")
        
        self.SetEmptyListMsg(_(u"Aucun individu"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        if len(self.columns) > 0 :
            self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, listeActivites=None, presents=None, labelParametres=""):
        self.listeActivites = listeActivites
        self.presents = presents
        self.labelParametres = labelParametres
        attente = wx.BusyInfo(_(u"Recherche des donn�es..."), self)
        self.InitModel()
        self.InitObjectListView()
        attente.Destroy()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDindividu
            
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()
                
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)
        
        # Commandes standards
        self.AjouterCommandesMenuContext(menuPop)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donn�e � imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        intro = self.labelParametres
        total = _(u"> %d individus") % len(self.donnees)
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des individus"), intro=intro, total=total, format="A", orientation=wx.LANDSCAPE)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des individus"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des individus"))


# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un individu..."))
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
        import time
        t = time.time()
        self.myOlv.MAJ(listeActivites=(1, 2, 3), presents=(datetime.date(2015, 1, 1), datetime.date(2015, 12, 31)))
        print len(self.myOlv.donnees)
        print "Temps d'execution =", time.time() - t
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((1200, 600))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
