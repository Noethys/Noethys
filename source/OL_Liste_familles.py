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
import UTILS_Utilisateurs
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Infos_individus


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def GetListe(listeActivites=None, presents=None):
    if listeActivites == None : return {} 
    
    # R�cup�ration des donn�es
    dictItems = {}

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

### Ancienne version lente :
##    req = """
##    SELECT 
##    familles.IDfamille, regimes.nom, caisses.nom, num_allocataire
##    FROM familles 
##    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
##    LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu
##    LEFT JOIN inscriptions ON inscriptions.IDactivite = consommations.IDactivite 
##    AND inscriptions.IDfamille = familles.IDfamille
##    LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
##    LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
##    WHERE inscriptions.parti=0 %s %s
##    GROUP BY familles.IDfamille
##    ;""" % (conditionActivites, conditionPresents)

    # R�cup�ration des pr�sents
    listePresents = []
    if presents != None :
        req = """SELECT IDfamille, inscriptions.IDinscription
        FROM consommations
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        WHERE date>='%s' AND date<='%s' %s
        GROUP BY IDfamille
        ;"""  % (str(presents[0]), str(presents[1]), conditionActivites.replace("inscriptions", "consommations"))
        DB.ExecuterReq(req)
        listeIndividusPresents = DB.ResultatReq()
        for IDfamille, IDinscription in listeIndividusPresents :
            listePresents.append(IDfamille)
    
    # R�cup�ration des r�gimes et num d'alloc pour chaque famille
    req = """
    SELECT 
    inscriptions.IDfamille, regimes.nom, caisses.nom, num_allocataire
    FROM inscriptions 
    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
    LEFT JOIN familles ON familles.IDfamille = inscriptions.IDfamille
    AND inscriptions.IDfamille = familles.IDfamille
    LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
    LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
    WHERE inscriptions.parti=0 %s
    GROUP BY familles.IDfamille
    ;""" % conditionActivites

    DB.ExecuterReq(req)
    listeFamilles = DB.ResultatReq()
    DB.Close() 
    
    # Formatage des donn�es
    dictFinal = {}
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, nomRegime, nomCaisse, numAlloc in listeFamilles :
        
        if presents == None or (presents != None and IDfamille in listePresents) :
            
            if IDfamille != None and titulaires.has_key(IDfamille) :
                nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
                rue = titulaires[IDfamille]["adresse"]["rue"]
                cp = titulaires[IDfamille]["adresse"]["cp"]
                ville = titulaires[IDfamille]["adresse"]["ville"]
                secteur = titulaires[IDfamille]["adresse"]["nomSecteur"]
            else :
                nomTitulaires = _(u"Aucun titulaire")
                rue = u""
                cp = u""
                ville = u""
                secteur = u""
            dictFinal[IDfamille] = {
                "IDfamille" : IDfamille, "titulaires" : nomTitulaires, "nomRegime" : nomRegime, 
                "nomCaisse" : nomCaisse, "numAlloc" : numAlloc,
                "rue" : rue, "cp" : cp, "ville" : ville, "secteur" : secteur,
                }
    
    return dictFinal


# -----------------------------------------------------------------------------------------------------------------------------------------



class Track(object):
    def __init__(self, donnees):
        self.IDfamille = donnees["IDfamille"]
        self.nomTitulaires = donnees["titulaires"]
        self.rue = donnees["rue"]
        self.cp = donnees["cp"]
        self.ville = donnees["ville"]
        self.secteur = donnees["secteur"]
        self.regime = donnees["nomRegime"]
        self.caisse = donnees["nomCaisse"]
        self.numAlloc = donnees["numAlloc"]

    
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
            self.infosIndividus.SetAsAttributs(parent=track, mode="famille", ID=track.IDfamille)

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        dictDonnees = GetListe(self.listeActivites, self.presents)
        listeListeView = []
        for IDfamille, dictTemp in dictDonnees.iteritems() :
            track = Track(dictTemp)
            listeListeView.append(track)
            if self.selectionID == IDfamille :
                self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), 'left', 250, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Rue"), "left", 160, "rue", typeDonnee="texte"),
            ColumnDefn(_(u"C.P."), "left", 45, "cp", typeDonnee="texte"),
            ColumnDefn(_(u"Ville"), "left", 120, "ville", typeDonnee="texte"),
            ColumnDefn(_(u"Secteur"), "left", 100, "secteur", typeDonnee="texte"),
            ColumnDefn(_(u"R�gime"), "left", 130, "regime", typeDonnee="texte"),
            ColumnDefn(_(u"Caisse"), "left", 130, "caisse", typeDonnee="texte"),
            ColumnDefn(_(u"Num�ro Alloc."), "left", 120, "numAlloc", typeDonnee="texte"),
            ]        

        # Insertion des champs infos de base individus
        listeChamps = self.infosIndividus.GetNomsChampsPresents(mode="famille")
        for nomChamp in listeChamps :
            typeDonnee = UTILS_Infos_individus.GetTypeChamp(nomChamp)
            liste_Colonnes.append(ColumnDefn(nomChamp, "left", 100, nomChamp, typeDonnee=typeDonnee, visible=False))

        self.SetColumns2(colonnes=liste_Colonnes, nomListe="OL_Liste_familles")
        self.SetEmptyListMsg(_(u"Aucune famille"))
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
            ID = self.Selection()[0].IDfamille
            
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()
        
        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 70, _(u"Ouvrir la fiche famille correspondante"))
        bmp = wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=70)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
        
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

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune fiche famille � ouvrir !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.InitModel()
            self.InitObjectListView()
        dlg.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donn�e � imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        intro = self.labelParametres
        total = _(u"> %d famillles") % len(self.donnees)
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des familles"), intro=intro, total=total, format="A", orientation=wx.PORTRAIT)
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
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des familles"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des familles"))


# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une famille..."))
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

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
