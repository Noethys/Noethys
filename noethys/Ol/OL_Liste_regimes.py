#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
from Utils import UTILS_Titulaires
from Utils import UTILS_Utilisateurs

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def GetListe(listeActivites=None, presents=None):
    if listeActivites == None : return {} 
    
    # Récupération des données
    dictItems = {}

    # Conditions Activites
    if listeActivites == None or listeActivites == [] :
        conditionActivites = ""
    else:
        if len(listeActivites) == 1 :
            conditionActivites = " AND inscriptions.IDactivite=%d" % listeActivites[0]
        else:
            conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(listeActivites))

    # Conditions Présents
##    if presents == None :
##        conditionPresents = ""
##        jointurePresents = ""
##    else:
##        conditionPresents = " AND (consommations.date>='%s' AND consommations.date<='%s')" % (str(presents[0]), str(presents[1]))
##        jointurePresents = "LEFT JOIN consommations ON consommations.IDindividu = individus.IDindividu"

    DB = GestionDB.DB()

    # Récupération des régimes et num d'alloc pour chaque famille

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

    # Récupération des présents
    listePresents = []
    if presents != None :
        req = """SELECT IDfamille
        FROM consommations
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        WHERE inscriptions.statut='ok' AND date>='%s' AND date<='%s' AND consommations.etat IN ('reservation', 'present') %s
        GROUP BY IDfamille
        ;"""  % (str(presents[0]), str(presents[1]), conditionActivites.replace("inscriptions", "consommations"))
        DB.ExecuterReq(req)
        listeIndividusPresents = DB.ResultatReq()
        for IDfamille in listeIndividusPresents :
            listePresents.append(IDfamille)

    req = """
    SELECT 
    inscriptions.IDfamille, regimes.nom, caisses.nom, num_allocataire
    FROM inscriptions 
    LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
    LEFT JOIN familles ON familles.IDfamille = inscriptions.IDfamille
    AND inscriptions.IDfamille = familles.IDfamille
    LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
    LEFT JOIN regimes ON regimes.IDregime = caisses.IDregime
    WHERE inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') %s
    GROUP BY inscriptions.IDfamille
    ;""" % (datetime.date.today(), conditionActivites)

    DB.ExecuterReq(req)
    listeFamilles = DB.ResultatReq()
    DB.Close() 
    
    # Formatage des données
    dictFinal = {}
    titulaires = UTILS_Titulaires.GetTitulaires() 
    for IDfamille, nomRegime, nomCaisse, numAlloc in listeFamilles :
        
        if presents == None or (presents != None and IDfamille in listePresents) :
            
            if IDfamille != None :
                nomTitulaires = titulaires[IDfamille]["titulairesSansCivilite"]
            else :
                nomTitulaires = _(u"Aucun titulaire")
            dictFinal[IDfamille] = {
                "IDfamille" : IDfamille, "titulaires" : nomTitulaires, "nomRegime" : nomRegime, 
                "nomCaisse" : nomCaisse, "numAlloc" : numAlloc,
                }
    
    return dictFinal


def GetFamillesSansCaisse(listeActivites=None, date_debut=None, date_fin=None):
    """ Permet de récupérer la liste des familles n'ayant pas de caisse renseignée """
    dictDonnees = GetListe(listeActivites=listeActivites, presents=(date_debut, date_fin))
    listeFamillesSansCaisse = []
    for IDfamille, dictFamille in dictDonnees.items() :
        if dictFamille["nomCaisse"] == None :
            listeFamillesSansCaisse.append({"IDfamille" : IDfamille, "titulaires" : dictFamille["titulaires"]})
    return listeFamillesSansCaisse

# -----------------------------------------------------------------------------------------------------------------------------------------



class Track(object):
    def __init__(self, donnees):
        self.IDfamille = donnees["IDfamille"]
        self.nomTitulaires = donnees["titulaires"]
        self.nomRegime = donnees["nomRegime"]
        self.nomCaisse = donnees["nomCaisse"]
        self.numAlloc = donnees["numAlloc"]

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
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
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        dictDonnees = GetListe(self.listeActivites, self.presents)
        listeListeView = []
        for IDfamille, dictTemp in dictDonnees.items() :
            track = Track(dictTemp)
            listeListeView.append(track)
            if self.selectionID == IDfamille :
                self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), 'left', 250, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Régime"), "left", 130, "nomRegime", typeDonnee="texte"),
            ColumnDefn(_(u"Caisse"), "left", 130, "nomCaisse", typeDonnee="texte"),
            ColumnDefn(_(u"Numéro Alloc."), "left", 120, "numAlloc", typeDonnee="texte"),
            ]        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune famille"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, listeActivites=None, presents=None, labelParametres=""):
        self.listeActivites = listeActivites
        self.presents = presents
        self.labelParametres = labelParametres
        attente = wx.BusyInfo(_(u"Recherche des données..."), self)
        self.InitModel()
        self.InitObjectListView()
        del attente
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDfamille
            
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 70, _(u"Ouvrir la fiche famille correspondante"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=70)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
        
        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre" : _(u"Liste des régimes et caisses"),
            "intro" : self.labelParametres,
            "total" : _(u"> %s familles") % len(self.GetFilteredObjects()),
            "orientation" : wx.PORTRAIT,
            }
        return dictParametres

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.InitModel()
            self.InitObjectListView()
        dlg.Destroy()

# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une information..."))
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
        print(len(self.myOlv.donnees))
        print("Temps d'execution =", time.time() - t)
##        print "Nbre familles sans caisse =", GetNbreSansCaisse(listeActivites=(1, 2, 3), date_debut=datetime.date(2010, 1, 5), date_fin=datetime.date(2011, 1, 5))
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
