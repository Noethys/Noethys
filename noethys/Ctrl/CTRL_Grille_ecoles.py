#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteurs:         Ivan LUCAS, Cliss XXI
# Copyright:       (c) 2010-11 Ivan LUCAS
#                  (c) 2017 Cliss XXI
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import datetime

import wx
import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import (
    EVT_TREE_ITEM_CHECKED, EVT_TREE_ITEM_RIGHT_CLICK
)

import Chemins # noqa
import GestionDB
from Utils import UTILS_Dates
from Utils.UTILS_Traduction import _

ID_COCHER_TOUTES = wx.NewId()
ID_COCHER_AUCUNE = wx.NewId()


class CTRL(HTL.HyperTreeList):
    def __init__(self, parent):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.date = None
        self.dictEcoles = {}
        self.MAJenCours = False
        self.cocherParDefaut = True
        self.cocheInconnue = True
        self.cochesActives = {}
        self.cochesEcolesActives = set()

        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(
            HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
            wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT
        )
        self.EnableSelectionVista(True)

        self.SetToolTipString(_(u"Cochez les écoles et classes à afficher"))

        # Création des colonnes
        self.AddColumn(_(u"Ecole/classe"))
        self.SetColumnWidth(0, 420)

        # Binds
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem)
        self.Bind(EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)

    def SetDate(self, date=None):
        self.date = date
        self.MAJ()

    def SetCocherParDefaut(self, etat=True):
        self.cocherParDefaut = etat

    def OnCheckItem(self, event):
        if self.MAJenCours is False:
            item = event.GetItem()
            data = self.GetPyData(item)
            # Active ou non les branches enfants
            if data["type"] == "ecole":
                if self.IsItemChecked(item):
                    self.EnableChildren(item, True)
                    self.cochesEcolesActives.add(data["ID"])
                else:
                    self.EnableChildren(item, False)
                    self.cochesEcolesActives.discard(data["ID"])
            elif data["type"] == "classe":
                cochesGroupes = self.cochesActives[data["IDecole"]]
                if self.IsItemChecked(item):
                    cochesGroupes.add(data["ID"])
                else:
                    cochesGroupes.discard(data["ID"])
            else:
                self.cocheInconnue = self.IsItemChecked(item)
            # Envoie les données aux contrôle parent
            if hasattr(self.parent, "MAJecoles"):
                self.parent.MAJecoles()

    def OnContextMenu(self, event):
        menu = wx.Menu()

        # Ajouter les éléments au menu
        item = wx.MenuItem(
            menu, ID_COCHER_TOUTES, u"Tout cocher",
            u"Cocher toutes les écoles et classes",
        )
        item.SetBitmap(wx.Bitmap(
            Chemins.GetStaticPath("Images/16x16/Cocher.png"),
            wx.BITMAP_TYPE_ANY,
        ))
        menu.AppendItem(item)
        item = wx.MenuItem(
            menu, ID_COCHER_AUCUNE, u"Tout décocher",
            u"Décocher toutes les écoles et classes",
        )
        item.SetBitmap(wx.Bitmap(
            Chemins.GetStaticPath("Images/16x16/Decocher.png"),
            wx.BITMAP_TYPE_ANY,
        ))
        menu.AppendItem(item)

        # Attache les événements
        wx.EVT_MENU(menu, ID_COCHER_TOUTES, self.OnCocher)
        wx.EVT_MENU(menu, ID_COCHER_AUCUNE, self.OnCocher)

        # Affiche le menu
        self.PopupMenu(menu, event.GetPoint())
        menu.Destroy()

    def OnCocher(self, event):
        ID = event.GetId()
        if ID == ID_COCHER_TOUTES:
            self.CocheListeTout()
        elif ID == ID_COCHER_AUCUNE:
            self.CocheListeRien()
        else:
            return

        if hasattr(self.parent, "MAJecoles"):
            self.parent.MAJecoles()

    def Cocher(self, etat=True):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            self.CheckItem(item, etat)
        if etat:
            self.EnableChildren(self.root, True)
        self.MAJenCours = False

    def CocheListeTout(self):
        self.Cocher(True)

        # Mets à jour l'état des coches
        self.cocheInconnue = True
        self.cochesEcolesActives = set(self.dictEcoles.keys())
        self.cochesActives = {
            ID: set([
                d["IDclasse"] for d in self.dictEcoles[ID]["classes"]
            ]) for ID in self.cochesEcolesActives
        }

    def CocheListeRien(self):
        self.Cocher(False)

        # Mets à jour l'état des coches
        self.cocheInconnue = False
        self.cochesEcolesActives.clear()
        self.cochesActives = {
            ID: set() for ID in self.dictEcoles.keys()
        }

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.dictEcoles = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Importation(self):
        dictEcoles = {}
        if not self.date:
            return dictEcoles

        # Récupération des écoles disponibles le jour sélectionné
        DB = GestionDB.DB()
        req = """SELECT ecoles.IDecole, ecoles.nom,
        classes.IDclasse, classes.nom, classes.niveaux,
        classes.date_debut, classes.date_fin
        FROM scolarite
        LEFT JOIN ecoles ON ecoles.IDecole = scolarite.IDecole
        LEFT JOIN classes ON classes.IDclasse = scolarite.IDclasse
        WHERE scolarite.IDclasse IS NOT NULL
              AND scolarite.date_debut<='{0}' AND scolarite.date_fin>='{0}'
        GROUP BY scolarite.IDclasse;""".format(self.date)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        for (IDecole, nomEcole, IDclasse, nomClasse, niveaux,
             date_debut, date_fin) in listeDonnees:
            if date_debut is not None:
                date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            if date_fin is not None:
                date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)

            # Mémorisation de l'école
            if IDecole not in dictEcoles:
                dictEcoles[IDecole] = {"nom": nomEcole, "classes": []}

            # Mémorisation de la classe
            dictEcoles[IDecole]["classes"].append({
                "IDclasse": IDclasse,
                "nom": nomClasse,
                "date_debut": date_debut,
                "date_fin": date_fin
            })

        return dictEcoles

    def Remplissage(self):
        # Tri des écoles par nom
        listeEcoles = []
        for IDecole, dictEcole in self.dictEcoles.iteritems():
            listeEcoles.append((dictEcole["nom"], IDecole))
        listeEcoles.sort()

        # Remplissage
        for nomEcole, IDecole in listeEcoles:
            dictEcole = self.dictEcoles[IDecole]

            # Initialise l'état des coches pour l'école
            if IDecole not in self.cochesActives:
                if self.cocherParDefaut is True:
                    self.cochesEcolesActives.add(IDecole)
                    self.cochesActives[IDecole] = set([
                        d["IDclasse"] for d in dictEcole["classes"]
                    ])
                else:
                    self.cochesActives[IDecole] = set()

            # Niveau Ecole
            niveauEcole = self.AppendItem(self.root, nomEcole, ct_type=1)
            self.SetPyData(niveauEcole, {
                "type": "ecole",
                "ID": IDecole,
                "nom": nomEcole
            })
            self.SetItemBold(niveauEcole, True)

            # Niveau Classes
            for dictClasse in dictEcole["classes"]:
                IDclasse = dictClasse["IDclasse"]
                nomClasse = dictClasse["nom"]
                label = u"{0} (du {1} au {2})".format(
                    nomClasse,
                    UTILS_Dates.DateEngFr(dictClasse["date_debut"]),
                    UTILS_Dates.DateEngFr(dictClasse["date_fin"]),
                )
                niveauClasse = self.AppendItem(niveauEcole, label, ct_type=1)
                self.SetPyData(niveauClasse, {
                    "type": "classe",
                    "ID": IDclasse,
                    "nom": nomClasse,
                    "IDecole": IDecole,
                })

                if IDclasse in self.cochesActives[IDecole]:
                    self.CheckItem(niveauClasse)

            # Coche l'école et active ses classes
            if IDecole in self.cochesEcolesActives:
                self.CheckItem(niveauEcole)
                self.EnableChildren(niveauEcole, True)
            else:
                self.EnableChildren(niveauEcole, False)

        # Ajoute une entrée pour les enfants dont la scolarité est inconnue
        item = self.AppendItem(self.root, u"Scolarité inconnue", ct_type=1)
        self.SetPyData(item, {"type": "inconnu"})
        if self.cocheInconnue:
            self.CheckItem(item)

        self.ExpandAllChildren(self.root)

    def GetCoches(self, typeTemp="ecole"):
        listeCoches = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            if self.IsItemChecked(item) and self.IsItemEnabled(item):
                data = self.GetPyData(item)
                if data["type"] == typeTemp:
                    listeCoches.append(data["ID"])
        return listeCoches

    def GetListeEcoles(self):
        return self.GetCoches(typeTemp="ecole")

    def GetListeClasses(self):
        return self.GetCoches(typeTemp="classe")

    def GetScolariteInconnue(self):
        item = self.GetLastChild(self.root)
        return self.IsItemChecked(item) and self.IsItemEnabled(item)

    def GetDictEcoles(self):
        return self.dictEcoles


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
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    frame_1.ctrl.SetDate(datetime.datetime.now())
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
