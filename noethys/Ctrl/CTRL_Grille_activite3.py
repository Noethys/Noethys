#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB

import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED


def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (
        _(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"),
        _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"),
    )
    listeMois = (
        _(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"),
        _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"),
        _(u"octobre"), _(u"novembre"), _(u"décembre"),
    )
    dateComplete = u"{0} {1} {2} {3}".format(
        listeJours[dateDD.weekday()], str(dateDD.day),
        listeMois[dateDD.month-1], str(dateDD.year),
    )
    return dateComplete


def DateEngEnDateDD(dateEng):
    return datetime.date(
        int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]),
    )


class CTRL_archive(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.SetToolTip(wx.ToolTip(_(u"Cochez les activités à afficher")))
        self.listeActivites = []
        self.dictActivites = {}
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)

    def SetDate(self, date=None):
        self.date = date
        self.MAJ()
        self.CocheTout()

    def MAJ(self):
        self.listeActivites, self.dictActivites = self.Importation()
        self.SetListeChoix()

    def Importation(self):
        listeActivites = []
        dictActivites = {}
        if self.date is None:
            return listeActivites, dictActivites
        # Récupération des activités disponibles le jour sélectionné
        DB = GestionDB.DB()
        req = """SELECT activites.IDactivite, nom, abrege, date_debut, date_fin
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        WHERE ouvertures.date='%s'
        GROUP BY activites.IDactivite
        ORDER BY nom;""" % str(self.date)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDactivite, nom, abrege, date_debut, date_fin in listeDonnees:
            if date_debut is not None:
                date_debut = DateEngEnDateDD(date_debut)
            if date_fin is not None:
                date_fin = DateEngEnDateDD(date_fin)
            dictTemp = {
                "nom": nom, "abrege": abrege,
                "date_debut": date_debut, "date_fin": date_fin,
                "tarifs": {},
            }
            dictActivites[IDactivite] = dictTemp
            listeActivites.append((nom, IDactivite))
        listeActivites.sort()
        return listeActivites, dictActivites

    def SetListeChoix(self):
        self.Clear()
        index = 0
        for nom, IDactivite in self.listeActivites:
            self.Append(nom)
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeActivites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeActivites[index][1])
        return listeIDcoches

    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeActivites)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeActivites)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches:
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une sélection d'activités est effectuée... """
        listeSelections = self.GetIDcoches()
        try:
            self.parent.SetActivites(listeSelections)
        except:
            print(listeSelections)

    def GetListeActivites(self):
        return self.GetIDcoches()


# --------------------------------------------------------------------------------------------------------------------

class CTRL(HTL.HyperTreeList):
    def __init__(self, parent):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.date = datetime.date(2014, 1, 10)  # None
        self.liste_activites = []
        self.MAJenCours = False
        self.cocherParDefaut = True
        self.cochesActives = {}
        self.cochesActivitesActives = set()

        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(
            HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
            wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT
        )
        self.EnableSelectionVista(True)

        self.SetToolTip(wx.ToolTip(
            _(u"Cochez les activités et groupes à afficher"))
        )

        # Création des colonnes
        self.AddColumn(_(u"Activité/groupe"))
        self.SetColumnWidth(0, 185)

        # Binds
#        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem)

    def SetDate(self, date=None):
        self.date = date
        self.MAJ()

    def OnCheckItem(self, event):
        if self.MAJenCours is False:
            item = event.GetItem()
            data = self.GetPyData(item)
            # Active ou non les branches enfants
            if data["type"] == "activite":
                if self.IsItemChecked(item):
                    self.EnableChildren(item, True)
                    self.cochesActivitesActives.add(data["ID"])
                else:
                    self.EnableChildren(item, False)
                    self.cochesActivitesActives.discard(data["ID"])
            else:
                cochesGroupes = self.cochesActives[data["IDactivite"]]
                if self.IsItemChecked(item):
                    cochesGroupes.add(data["ID"])
                else:
                    cochesGroupes.discard(data["ID"])
            # Envoie les données aux contrôle parent
            self.parent.MAJactivites()

    def GetCoches(self):
        dictCoches = {}
        parent = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            parent = self.GetNext(parent)
            # Recherche des activités cochées
            if self.IsItemChecked(parent):
                IDactivite = self.GetPyData(parent)["ID"]
                # Recherche des groupes cochés
                listeGroupes = []
                item, cookie = self.GetFirstChild(parent)
                for index in range(0, self.GetChildrenCount(parent)):
                    if self.IsItemChecked(item):
                        IDgroupe = self.GetPyData(item)["ID"]
                        listeGroupes.append(IDgroupe)
                    item = self.GetNext(item)
                if len(listeGroupes) > 0:
                    dictCoches[IDactivite] = listeGroupes
        return dictCoches

    def GetActivitesEtGroupes(self):
        dictCoches = self.GetCoches()
        listeActivites = []
        listeGroupes = []
        for IDactivite, listeGroupesTemp in dictCoches.items():
            listeActivites.append(IDactivite)
            for IDgroupe in listeGroupesTemp:
                listeGroupes.append(IDgroupe)
        return listeActivites, listeGroupes

    def SetCocherParDefaut(self, etat=True):
        self.cocherParDefaut = etat

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.dictActivites = self.Importation()
#        self.Freeze()
        self.MAJenCours = True
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False
#        self.Thaw()

    def Remplissage(self):
        # Tri des activités par nom
        listeActivites = []
        for IDactivite, dictActivite in self.dictActivites.items():
            listeActivites.append((dictActivite["nom"], IDactivite))
        listeActivites.sort()

        # Remplissage
        for nomActivite, IDactivite in listeActivites:
            dictActivite = self.dictActivites[IDactivite]

            # Initialise l'état des coches pour l'activité
            if IDactivite not in self.cochesActives:
                if self.cocherParDefaut is True:
                    self.cochesActivitesActives.add(IDactivite)
                    self.cochesActives[IDactivite] = set([
                        d["IDgroupe"] for d in dictActivite["groupes"]
                    ])
                else:
                    self.cochesActives[IDactivite] = set()

            # Niveau Activité
            niveauActivite = self.AppendItem(self.root, nomActivite, ct_type=1)
            self.SetPyData(niveauActivite, {
                "type": "activite",
                "ID": IDactivite,
                "nom": nomActivite,
            })
            self.SetItemBold(niveauActivite, True)

            # Niveau Groupes
            for dictGroupe in dictActivite["groupes"]:
                IDgroupe = dictGroupe["IDgroupe"]
                niveauGroupe = self.AppendItem(niveauActivite, dictGroupe["nom"], ct_type=1)
                self.SetPyData(niveauGroupe, {
                    "type": "groupe",
                    "ID": IDgroupe,
                    "nom": dictGroupe["nom"],
                    "IDactivite": IDactivite,
                })

                if IDgroupe in self.cochesActives[IDactivite]:
                    self.CheckItem(niveauGroupe)

            # Coche l'activité et active ses groupes
            if IDactivite in self.cochesActivitesActives:
                self.CheckItem(niveauActivite)
                self.EnableChildren(niveauActivite, True)
            else:
                self.EnableChildren(niveauActivite, False)

        self.ExpandAllChildren(self.root)

#        # Pour éviter le bus de positionnement des contrôles
#        self.GetMainWindow().CalculatePositions()

    def Importation(self):
        dictActivites = {}
        if self.date is None:
            return dictActivites
        # Récupération des activités disponibles le jour sélectionné
        DB = GestionDB.DB()
        req = """SELECT
        activites.IDactivite, activites.nom, activites.abrege,
        date_debut, date_fin,
        groupes.IDgroupe, groupes.nom
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = ouvertures.IDgroupe
        WHERE ouvertures.date='%s'
        GROUP BY groupes.IDgroupe
        ORDER BY groupes.ordre;""" % str(self.date)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDactivite, nom, abrege, date_debut, date_fin, IDgroupe, nomGroupe in listeDonnees:

            if IDgroupe != None :

                if date_debut is not None:
                    date_debut = DateEngEnDateDD(date_debut)
                if date_fin is not None:
                    date_fin = DateEngEnDateDD(date_fin)

                # Mémorisation de l'activité
                if IDactivite not in dictActivites:
                    dictActivites[IDactivite] = {
                        "nom": nom, "abrege": abrege,
                        "date_debut": date_debut, "date_fin": date_fin,
                        "groupes": [],
                    }
                # Mémorisation du groupe
                dictActivites[IDactivite]["groupes"].append({
                    "IDgroupe": IDgroupe, "nom": nomGroupe,
                })

        return dictActivites


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL | wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    # wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
