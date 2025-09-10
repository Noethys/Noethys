#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
# -----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB
from Utils import UTILS_Config
import copy


COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)

LARGEUR_COLONNE_AFFICHAGE = 135


class Track(object):
    def __init__(self, donnees, type="conso"):
        self.type = type
        if type == "conso":
            self.texteType = "Consommation"
        else:
            self.texteType = "Remplissage"
        self.IDunite = donnees[0]
        self.IDactivite = donnees[1]
        self.nomUnite = donnees[2]
        self.abrege = donnees[3]
        self.ordre = donnees[4]
        self.nomActivite = donnees[5]
        self.affichage = None
        self.position = 0

        # Items HyperTreeList
        self.item = None
        self.itemParent = None

        # Contrôles
        self.ctrl_affichage = None

    def ReinitAffichage(self):
        self.affichage = None
        self.ctrl_affichage.SetDefaut()


# --------------------------------------------------------------------------------------------------------------------------------

class CTRL_Affichage(wx.Choice):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Type d'affichage """
        wx.Choice.__init__(self, parent, id=id, size=(
            LARGEUR_COLONNE_AFFICHAGE-7, -1))
        self.parent = parent
        self.item = item
        self.track = track
        if self.track.type == "conso" :
            self.SetItems([_(u"Toujours afficher"), _(u"Ne jamais afficher"), _(u"Afficher si ouvert"), _(u"Afficher si conso")])
        else:
            self.SetItems([_(u"Toujours afficher"), _(u"Ne jamais afficher")])
        self.SetToolTip(wx.ToolTip(
            _(u"Sélectionnez un type d'affichage pour cette unité")))
        # Defaut
        self.SetDefaut()
        # Bind
        self.Bind(wx.EVT_CHOICE, self.OnChoice)

    def SetDefaut(self):
        if self.track.affichage == None:
            if self.track.type == "conso":
                self.SetSelection(2)
                self.track.affichage = "utilise"
            if self.track.type == "remplissage":
                self.SetSelection(1)
                self.track.affichage = "jamais"
        else:
            if self.track.affichage == "toujours" : self.SetSelection(0)
            if self.track.affichage == "jamais" : self.SetSelection(1)
            if self.track.affichage == "utilise" : self.SetSelection(2)
            if self.track.affichage == "conso": self.SetSelection(3)

    def OnChoice(self, event):
        if self.GetSelection() == 0 : self.track.affichage = "toujours"
        if self.GetSelection() == 1 : self.track.affichage = "jamais"
        if self.GetSelection() == 2 : self.track.affichage = "utilise"
        if self.GetSelection() == 3: self.track.affichage = "conso"

# -------------------------------------------------------------------------------------------------------------------


class CTRL(HTL.HyperTreeList):
    def __init__(self, parent):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.dictParametres = {}
        self.listeActivites = []

        # Importation des données
        self.Importation()

        # Création des colonnes
        listeColonnes = [
            (_(u"Activité / Unité"), 180, wx.ALIGN_LEFT),
            (_(u"Abrégé"), 50, wx.ALIGN_LEFT),
            (_(u"Type"), 100, wx.ALIGN_LEFT),
            (_(u"Affichage"), LARGEUR_COLONNE_AFFICHAGE, wx.ALIGN_LEFT),
            # ( _(u"Ordre"), 40, wx.ALIGN_CENTER),
        ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes:
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1

        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)

        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else:
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_ROW_LINES | TR_COLUMN_LINES | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
                                   wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT)  # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

    def Importation(self):
        """ Importation des unités de conso et de remplissage """
        DB = GestionDB.DB()

        # Importation des unités de consommations
        type = "conso"
        req = """SELECT 
        unites.IDunite, unites.IDactivite, unites.nom, unites.abrege, unites.ordre,
        activites.nom
        FROM unites
        LEFT JOIN activites ON activites.IDactivite = unites.IDactivite
        ORDER BY unites.IDactivite, ordre
        ;"""
        DB.ExecuterReq(req)
        listeUnitesConso = DB.ResultatReq()
        self.listeTracks = []
        self.dictActivites = {}
        for item in listeUnitesConso:
            track = Track(item, type)
            self.listeTracks.append(track)
            self.dictActivites[track.IDactivite] = track.nomActivite

        # Importation des unités de remplissage
        type = "remplissage"
        req = """SELECT 
        unites_remplissage.IDunite_remplissage, unites_remplissage.IDactivite, 
        unites_remplissage.nom, unites_remplissage.abrege, unites_remplissage.ordre, activites.nom
        FROM unites_remplissage
        LEFT JOIN activites ON activites.IDactivite = unites_remplissage.IDactivite
        ORDER BY unites_remplissage.IDactivite, ordre
        ;"""
        DB.ExecuterReq(req)
        listeUnitesRemplissage = DB.ResultatReq()
        for item in listeUnitesRemplissage:
            track = Track(item, type)
            self.listeTracks.append(track)
            self.dictActivites[track.IDactivite] = track.nomActivite

        DB.Close()

        # Met les tracks de la base de données dans un dict
        self.dictTracksInitial = {}
        for track in self.listeTracks:
            if (track.IDactivite in self.dictTracksInitial) == False:
                self.dictTracksInitial[track.IDactivite] = []
            self.dictTracksInitial[track.IDactivite].append(track)

        self.dictTracksFinal = copy.deepcopy(self.dictTracksInitial)

    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
        self.MAJ()

    def MAJ(self, selectionItem=None):
        """ Met à jour (redessine) tout le contrôle """
        self.Freeze()
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage(selectionItem)
        self.Thaw()

    def Remplissage(self, selectionItem=None):
        # Regroupement
        listeKeys = []
        for IDactivite, nomActivite in self.dictActivites.items():
            key = (nomActivite, IDactivite)
            if key not in listeKeys:
                listeKeys.append(key)
        listeKeys.sort()

        # Création des branches
        for nomActivite, IDactivite in listeKeys:

            if IDactivite in self.listeActivites:

                # Niveau Nom de l'activité
                brancheActivite = self.AppendItem(self.root, nomActivite)
                self.SetPyData(brancheActivite, IDactivite)
                self.SetItemBold(brancheActivite, True)
                self.SetItemBackgroundColour(
                    brancheActivite, COULEUR_FOND_REGROUPEMENT)

                # Niveau Unités de consommation ou de remplissage
                index = 0
                for track in self.dictTracksFinal[IDactivite]:

                    if track.IDactivite == IDactivite:

                        brancheUnite = self.AppendItem(
                            brancheActivite, track.nomUnite)
                        self.SetPyData(brancheUnite, track)  # track.IDunite

                        # Mémorisation des items dans le track
                        track.item = brancheUnite
                        track.itemParent = brancheActivite

                        # Colonnes textes
                        self.SetItemText(brancheUnite, track.abrege, 1)
                        self.SetItemText(brancheUnite, track.texteType, 2)

                        # CTRL de l'affichage
                        ctrl_affichage = CTRL_Affichage(
                            self.GetMainWindow(), item=brancheUnite, track=track)
                        self.SetItemWindow(brancheUnite, ctrl_affichage, 3)
                        track.ctrl_affichage = ctrl_affichage

                        # Colonnes textes

                        # TODO : check this comment that cause crash
                        # self.SetItemText(brancheUnite, str(index+1), 4)
                        track.position = index
                        index += 1

                        # Sélection d'un item
                        if selectionItem == track:
                            self.SelectItem(brancheUnite, True)
                            self.ScrollTo(brancheUnite)

        self.ExpandAllChildren(self.root)

        # Pour éviter le bus de positionnement des contrôles
        self.GetMainWindow().CalculatePositions()

    def GetDonnees(self):
        """ Récupère les résultats des données saisies """
        dictDonnees = {}
        for IDactivite, listeTracks in self.dictTracksFinal.items():
            for track in listeTracks:
                if track.affichage != None:
                    if (IDactivite in dictDonnees) == False:
                        dictDonnees[IDactivite] = []
                    dictDonnees[IDactivite].append(
                        (track.type, track.IDunite, track.affichage))
        return dictDonnees

    def GetParametres(self):
        return self.GetDonnees()

    def SetParametres(self, dictParametres={}):
        if dictParametres == None:
            return False
        if "unites" in dictParametres:
            self.dictParametres = dictParametres["unites"]

        # Recherche les paramètres dans le profil de config
        self.dictTracksFinal = {}
        listeTracksTemp = self.listeTracks[:]
        for IDactivite, listeUnites in self.dictParametres.items():
            if (IDactivite in self.dictTracksFinal) == False:
                self.dictTracksFinal[IDactivite] = []
            for type, IDunite, affichage in listeUnites:
                if IDactivite in self.dictTracksInitial:
                    # Recherche si le track existe dans la liste initiale. Si oui, le récupère et le copie dans la liste finale
                    for track in self.dictTracksInitial[IDactivite]:
                        if track.type == type and track.IDunite == IDunite:
                            track.affichage = affichage
                            self.dictTracksFinal[IDactivite].append(
                                copy.deepcopy(track))
                            listeTracksTemp.remove(track)

        # Rajoute les tracks n'apparaissant pas dans le dict des paramètres
        for track in listeTracksTemp:
            IDactivite = track.IDactivite
            if (IDactivite in self.dictTracksFinal) == False:
                self.dictTracksFinal[IDactivite] = []
            self.dictTracksFinal[IDactivite].append(copy.deepcopy(track))

        # MAJ du remplissage
        self.MAJ()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Monter
        item = wx.MenuItem(menuPop, 10, _(u"Monter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=10)

        # Item Descendre
        item = wx.MenuItem(menuPop, 20, _(u"Descendre"))
        bmp = wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=20)

        menuPop.AppendSeparator()

        # Item Descendre
        item = wx.MenuItem(menuPop, 30, _(u"Réinitialiser"))
        bmp = wx.Bitmap(Chemins.GetStaticPath(
            "Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Reinit, id=30)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()

# def RechercherTrack(self, trackSelection=None):
# for IDactivite, listeTracks in self.dictTracks.iteritems() :
# index = 0
# for track in listeTracks :
# if track == trackSelection :
# return track, position
# index += 1

    def Monter(self, event):
        item = self.GetSelection()
        track = self.GetMainWindow().GetItemPyData(item)
        if track == None or type(track) == int:
            dlg = wx.MessageDialog(self, _(u"Nous n'avez sélectionné aucune unité à déplacer !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if track.position == 0:
            dlg = wx.MessageDialog(self, _(u"Cette unité est déjà en première position !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        listeTemp = self.dictTracksFinal[track.IDactivite]
        listeTemp.remove(track)
        track.position -= 1
        listeTemp.insert(track.position, track)
        self.MAJ(track)

    def Descendre(self, event):
        item = self.GetSelection()
        track = self.GetMainWindow().GetItemPyData(item)
        if track == None or type(track) == int:
            dlg = wx.MessageDialog(self, _(u"Nous n'avez sélectionné aucune unité à déplacer !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if track.position == len(self.dictTracksFinal[track.IDactivite])-1:
            dlg = wx.MessageDialog(self, _(u"Cette unité est déjà en dernière position !"), _(
                u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        listeTemp = self.dictTracksFinal[track.IDactivite]
        listeTemp.remove(track)
        track.position += 1
        listeTemp.insert(track.position, track)
        self.MAJ(track)

    def Reinit(self, event):
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment réinitialiser la liste des unités ?"), _(
            u"Réinitialisation"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.dictTracksFinal = copy.deepcopy(self.dictTracksInitial)
            self.MAJ()
        dlg.Destroy()

# -------------------------------------------------------------------------------------------------------------------------------------------


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.listeActivites = [1, 3]
        self.ctrl.MAJ()
        self.boutonTest = wx.Button(panel, -1, _(u"Test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL | wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL | wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)

    def OnBoutonTest(self, event):
        print(self.ctrl.GetDonnees())


if __name__ == '__main__':
    app = wx.App(0)
    # wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
