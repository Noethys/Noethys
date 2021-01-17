#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
import datetime
from Utils import UTILS_Titulaires
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, parent, IDfamille=None, code_compta=None):
        self.IDfamille = IDfamille
        self.code_compta = code_compta
        if not self.code_compta:
            self.code_compta = ""
        self.nomTitulaires = parent.dict_titulaires[IDfamille]["titulairesSansCivilite"]


    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.dict_parametres = {
            "liste_activites": None,
            "presents": None,
            "familles": "TOUTES",
            "label_parametres": "",
            }

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, event):
        self.Modifier()

    def InitModel(self):
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        # Conditions Activites
        if self.dict_parametres["liste_activites"] == None or self.dict_parametres["liste_activites"] == [] :
            conditionActivites = ""
        else:
            if len(self.dict_parametres["liste_activites"]) == 1 :
                conditionActivites = " AND inscriptions.IDactivite=%d" % self.dict_parametres["liste_activites"][0]
            else:
                conditionActivites = " AND inscriptions.IDactivite IN %s" % str(tuple(self.dict_parametres["liste_activites"]))

        DB = GestionDB.DB()

        # Récupération des présents
        listePresents = []
        if self.dict_parametres["presents"] != None :
            req = """SELECT IDfamille, inscriptions.IDinscription
            FROM consommations
            LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
            WHERE inscriptions.statut='ok' AND date>='%s' AND date<='%s' AND consommations.etat IN ('reservation', 'present') %s
            GROUP BY IDfamille
            ;"""  % (str(self.dict_parametres["presents"][0]), str(self.dict_parametres["presents"][1]), conditionActivites.replace("inscriptions", "consommations"))
            DB.ExecuterReq(req)
            listeIndividusPresents = DB.ResultatReq()
            for IDfamille, IDinscription in listeIndividusPresents :
                listePresents.append(IDfamille)

        # Récupération des familles
        req = """
        SELECT inscriptions.IDfamille, familles.code_comptable
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

        listeListeView = []
        for IDfamille, code_compta in listeFamilles:
            if self.dict_parametres["presents"] == None or (self.dict_parametres["presents"] != None and IDfamille in listePresents) :
                if self.dict_parametres["familles"] == "TOUTES" or (self.dict_parametres["familles"] == "AVEC" and code_compta != None) or (self.dict_parametres["familles"] == "SANS" and code_compta == None):
                    listeListeView.append(Track(self, IDfamille, code_compta))

        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), 'left', 350, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Code comptable"), "center", 200, "code_compta", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune famille"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

    def SetParametre(self, nom="", valeur=""):
        self.dict_parametres[nom] = valeur

    def MAJ(self, IDfamille=None):
        attente = wx.BusyInfo(_(u"Recherche des données..."), self)
        self.InitModel()
        self.InitObjectListView()
        del attente

        # Sélection
        for track in self.donnees:
            if track.IDfamille == IDfamille :
                self.SelectObject(track, ensureVisible=True)
                break
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 5, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=5)

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        
        menuPop.AppendSeparator()
        
        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre" : _(u"Liste des codes comptables"),
            "intro" : self.dict_parametres["label_parametres"],
            "total" : _(u"> %s familles") % len(self.donnees),
            "orientation" : wx.PORTRAIT,
            }
        return dictParametres

    def OuvrirFicheFamille(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDfamille=IDfamille)
        dlg.Destroy()

    def Modifier(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ligne à modifier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le code comptable de la famille de %s :") % track.nomTitulaires, _(u"Modifier"))
        dlg.SetValue(track.code_compta)
        if dlg.ShowModal() == wx.ID_OK:
            code_compta = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        DB = GestionDB.DB()
        DB.ReqMAJ("familles", [("code_comptable", code_compta),], "IDfamille", track.IDfamille)
        DB.Close()
        track.code_compta = code_compta
        self.RefreshObject(track)


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
        self.myOlv.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
