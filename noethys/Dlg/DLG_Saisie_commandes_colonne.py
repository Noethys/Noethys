#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Utils import UTILS_Dates
from Ctrl import CTRL_Bouton_image
import GestionDB
import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED
import six


DICT_LABELS_CATEGORIES = {
    "numerique_avec_suggestion" : _(u"Numérique (Avec suggestion)"),
    "numerique_sans_suggestion" : _(u"Numérique (Libre)"),
    "numerique_total" : _(u"Numérique (Total)"),
    "texte_infos" : _(u"Texte (Informations)"),
    "texte_libre" : _(u"Texte (Libre)"),
}


class CTRL_Unites(HTL.HyperTreeList):
    def __init__(self, parent):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.MAJenCours = False

        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT)
        self.EnableSelectionVista(True)

        # Création des colonnes
        self.AddColumn(_(u"Activité/Unité/Groupe"))
        self.SetColumnWidth(0, 370)

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.dictActivites, self.dictUnites = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Importation(self):
        dictActivites = {}
        dictUnites = {}

        # Conditions
        conditions = []
        if self.parent.check_repas.GetValue() == True :
            conditions.append("AND unites.repas=1")

        # Récupération des activités et des unités
        DB = GestionDB.DB()
        req = """SELECT 
        activites.IDactivite, activites.nom, activites.abrege, activites.date_debut, activites.date_fin,
        groupes.IDgroupe, groupes.nom,
        unites.IDunite, unites.nom, unites.ordre
        FROM activites
        LEFT JOIN groupes ON groupes.IDactivite = activites.IDactivite
        LEFT JOIN unites ON unites.IDactivite = activites.IDactivite
        WHERE unites.IDunite IS NOT NULL %s
        GROUP BY groupes.IDgroupe, unites.IDunite
        ORDER BY activites.date_fin, groupes.ordre, unites.ordre;""" % " ".join(conditions)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDactivite, nom, abrege, date_debut, date_fin, IDgroupe, nomGroupe, IDunite, nomUnite, ordreUnite in listeDonnees:
            if date_debut != None: date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            if date_fin != None: date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)

            # Mémorisation de l'activité, du groupe et de l'unité
            if (IDactivite in dictActivites) == False:
                dictActivites[IDactivite] = {"nom": nom, "abrege": abrege, "date_debut": date_debut, "date_fin": date_fin, "groupes": {}}

            if (IDgroupe in dictActivites[IDactivite]["groupes"]) == False:
                dictActivites[IDactivite]["groupes"][IDgroupe] = {"IDgroupe" : IDgroupe, "nom": nomGroupe, "unites": []}

            dictActivites[IDactivite]["groupes"][IDgroupe]["unites"].append({"IDunite": IDunite, "nom": nomUnite, "ordre": ordreUnite})

        return dictActivites, dictUnites

    def Remplissage(self):
        # Tri des activités par nom
        listeActivites = []
        for IDactivite, dictActivite in self.dictActivites.items():
            listeActivites.append((dictActivite["nom"], IDactivite))
        #listeActivites.sort()

        # Remplissage
        for nomActivite, IDactivite in listeActivites:
            dictActivite = self.dictActivites[IDactivite]

            # Niveau Activité
            niveauActivite = self.AppendItem(self.root, nomActivite)
            self.SetPyData(niveauActivite, {"type": "activite", "ID": IDactivite, "nom": nomActivite})
            self.SetItemBold(niveauActivite, True)

            # Niveau Groupes
            for IDgroupe, dictGroupe in dictActivite["groupes"].items():
                niveauGroupe = self.AppendItem(niveauActivite, dictGroupe["nom"])
                self.SetPyData(niveauGroupe, {"type": "groupe", "ID": dictGroupe["IDgroupe"], "nom": dictGroupe["nom"]})

                # Niveau Unités
                for dictUnite in dictGroupe["unites"]:
                    niveauUnite = self.AppendItem(niveauGroupe, dictUnite["nom"], ct_type=1)
                    self.SetPyData(niveauUnite, {"type": "unite", "IDunite": dictUnite["IDunite"], "IDgroupe": dictGroupe["IDgroupe"], "nom": dictUnite["nom"]})

        self.ExpandAllChildren(self.root)

    def GetCoches(self, typeTemp="unite"):
        listeCoches = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            if self.IsItemChecked(item) and self.IsItemEnabled(item):
                IDgroupe = self.GetPyData(item)["IDgroupe"]
                IDunite = self.GetPyData(item)["IDunite"]
                if self.GetPyData(item)["type"] == typeTemp:
                    listeCoches.append((IDgroupe, IDunite))
        return listeCoches

    def SetCoches(self, listeID=[], typeTemp="unite"):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            if self.IsItemEnabled(item) and self.GetPyData(item)["type"] == typeTemp :
                IDgroupe = self.GetPyData(item)["IDgroupe"]
                IDunite = self.GetPyData(item)["IDunite"]
                if (IDgroupe, IDunite) in listeID:
                    self.CheckItem(item, True)
        self.MAJenCours = False

    def GetListeUnites(self):
        return self.GetCoches(typeTemp="unite")

    def GetDictUnites(self):
        return self.dictUnites


# ------------------------------------------------------------------------------------------------------------



class CTRL_Groupes(HTL.HyperTreeList):
    def __init__(self, parent):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.MAJenCours = False

        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT)
        self.EnableSelectionVista(True)

        # Création des colonnes
        self.AddColumn(_(u"Activité/Groupe"))
        self.SetColumnWidth(0, 370)

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.dictActivites = self.Importation()
        self.MAJenCours = True
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.MAJenCours = False

    def Importation(self):
        dictActivites = {}

        # Récupération des activités et des groupes
        DB = GestionDB.DB()
        req = """SELECT 
        activites.IDactivite, activites.nom, activites.abrege, activites.date_debut, activites.date_fin,
        groupes.IDgroupe, groupes.nom
        FROM activites
        LEFT JOIN groupes ON groupes.IDactivite = activites.IDactivite
        GROUP BY groupes.IDgroupe
        ORDER BY activites.date_fin, groupes.ordre;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDactivite, nom, abrege, date_debut, date_fin, IDgroupe, nomGroupe in listeDonnees:
            if date_debut != None: date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            if date_fin != None: date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)

            # Mémorisation de l'activité, du groupe et de l'unité
            if (IDactivite in dictActivites) == False:
                dictActivites[IDactivite] = {"nom": nom, "abrege": abrege, "date_debut": date_debut, "date_fin": date_fin, "groupes": []}

            dictActivites[IDactivite]["groupes"].append({"IDgroupe" : IDgroupe, "nom": nomGroupe})

        return dictActivites

    def Remplissage(self):
        # Tri des activités par nom
        listeActivites = []
        for IDactivite, dictActivite in self.dictActivites.items():
            listeActivites.append((dictActivite["nom"], IDactivite))
        #listeActivites.sort()

        # Remplissage
        for nomActivite, IDactivite in listeActivites:
            dictActivite = self.dictActivites[IDactivite]

            # Niveau Activité
            niveauActivite = self.AppendItem(self.root, nomActivite)
            self.SetPyData(niveauActivite, {"type": "activite", "IDactivite": IDactivite, "nom": nomActivite})
            self.SetItemBold(niveauActivite, True)

            # Niveau Groupes
            for dictGroupe in dictActivite["groupes"]:
                niveauGroupe = self.AppendItem(niveauActivite, dictGroupe["nom"], ct_type=1)
                self.SetPyData(niveauGroupe, {"type": "groupe", "IDgroupe": dictGroupe["IDgroupe"], "nom": dictGroupe["nom"]})

        self.ExpandAllChildren(self.root)

    def GetCoches(self, typeTemp="groupe"):
        listeCoches = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            if self.IsItemChecked(item) and self.IsItemEnabled(item):
                IDgroupe = self.GetPyData(item)["IDgroupe"]
                if self.GetPyData(item)["type"] == typeTemp:
                    listeCoches.append(IDgroupe)
        return listeCoches

    def SetCoches(self, listeID=[], typeTemp="groupe"):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            if self.IsItemEnabled(item) and self.GetPyData(item)["type"] == typeTemp :
                IDgroupe = self.GetPyData(item)["IDgroupe"]
                if IDgroupe in listeID:
                    self.CheckItem(item, True)
        self.MAJenCours = False



# ------------------------------------------------------------------------------------------------------------

class CTRL_Colonnes_numeriques(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent

    def MAJ(self):
        # Importation des colonnes numériques
        try :
            tracks_colonnes = self.GetGrandParent().GetGrandParent().donnees
        except :
            tracks_colonnes = []
        listeDonnees = []
        for track in tracks_colonnes :
            if track.categorie.startswith("numerique") and "total" not in track.categorie :
                listeDonnees.append((track.IDcolonne, track.nom))
        # Remplissage
        self.Clear()
        self.dictIndex = {}
        index = 0
        for IDcolonne, nom in listeDonnees:
            self.Append(nom)
            self.dictIndex[index] = IDcolonne
            index += 1

    def GetCoches(self):
        listeIDcoches = []
        NbreItems = len(self.dictIndex)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                IDcolonne = self.dictIndex[index]
                listeIDcoches.append(IDcolonne)
        return listeIDcoches

    def SetCoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.dictIndex)):
            ID = self.dictIndex[index]
            if ID in listeIDcoches:
                self.Check(index)
            index += 1



# -------------------------------------------------------------------------------------------------------------

class PAGE_Unites(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.label_intro = wx.StaticText(self, -1, _(u"Cochez les unités à additionner :"))
        self.ctrl_unites = CTRL_Unites(self)
        self.ctrl_unites.SetMinSize((100, 50))
        self.check_repas = wx.CheckBox(self, -1, _(u"Afficher uniquement les unités avec repas inclus"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_unites, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.Add(self.check_repas, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

        # Bind
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRepas, self.check_repas)

        # Init
        self.ctrl_unites.MAJ()

    def OnCheckRepas(self, event):
        self.ctrl_unites.MAJ()

    def Validation(self):
        if len(self.ctrl_unites.GetCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une unité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

    def GetParametres(self):
        listeUnites = self.ctrl_unites.GetCoches()
        return {"unites" : listeUnites}

    def SetParametres(self, dictParametres={}):
        if type(dictParametres) in (six.text_type, str) :
            dictParametres = eval(dictParametres)
        self.ctrl_unites.SetCoches(dictParametres["unites"])



# ------------------------------------------------------------------------------------------------------------

class PAGE_Informations(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.label_intro = wx.StaticText(self, -1, _(u"Cochez les informations à afficher :"))
        self.check_infos_medicales = wx.CheckBox(self, -1, _(u"Afficher les informations médicales"))
        self.check_messages = wx.CheckBox(self, -1, _(u"Afficher les messages individuels"))

        self.label_groupes = wx.StaticText(self, -1, _(u"Cochez les groupes concernés :"))
        self.radio_groupes_tous = wx.RadioButton(self, -1, _(u"Tous les groupes"), style=wx.RB_GROUP)
        self.radio_groupes_choix = wx.RadioButton(self, -1, _(u"Uniquement les groupes suivants :"))
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((100, 50))

        self.check_infos_medicales.SetToolTip(wx.ToolTip(_(u"Affiche les informations médicales. Attention, la case 'Afficher sur la commande des repas' doit avoir été cochée dans la fenêtre de saisie de l'information médicale.")))
        self.check_messages.SetToolTip(wx.ToolTip(_(u"Affiche les messages individuels. Attention, la case 'Afficher sur la commande des repas' doit avoir été cochée dans la fenêtre de saisie du message.")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.Add(self.check_infos_medicales, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.Add(self.check_messages, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)

        grid_sizer_base.Add(self.label_groupes, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.Add(self.radio_groupes_tous, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_groupes_choix, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_groupes, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(6)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioGroupes, self.radio_groupes_tous)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioGroupes, self.radio_groupes_choix)

        # Init
        self.ctrl_groupes.MAJ()
        self.OnRadioGroupes()

    def OnRadioGroupes(self, event=None):
        self.ctrl_groupes.Enable(self.radio_groupes_choix.GetValue())

    def Validation(self):
        if self.check_infos_medicales.GetValue() == False and self.check_messages.GetValue() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un élément !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if self.radio_groupes_choix.GetValue() == True :
            if len(self.ctrl_groupes.GetCoches()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un groupe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

    def GetParametres(self):
        dictParametres = {}
        if self.check_infos_medicales.GetValue() == True :
            dictParametres["infos_medicales"] = True
        if self.check_messages.GetValue() == True :
            dictParametres["messages_individuels"] = True
        if self.radio_groupes_choix.GetValue() == True :
            dictParametres["groupes"] = self.ctrl_groupes.GetCoches()
        return dictParametres

    def SetParametres(self, dictParametres={}):
        if type(dictParametres) in (six.text_type, str) :
            dictParametres = eval(dictParametres)
        if ("infos_medicales" in dictParametres) == True :
            self.check_infos_medicales.SetValue(True)
        if ("messages_individuels" in dictParametres) == True :
            self.check_messages.SetValue(True)
        if ("groupes" in dictParametres) == True :
            self.radio_groupes_choix.SetValue(True)
            self.ctrl_groupes.SetCoches(dictParametres["groupes"])
        self.OnRadioGroupes()

# ------------------------------------------------------------------------------------------------------------

class PAGE_Total(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.label_intro = wx.StaticText(self, -1, _(u"Précisez les données à totaliser :"))
        self.radio_colonnes_toutes = wx.RadioButton(self, -1, _(u"Toutes les colonnes numériques"), style=wx.RB_GROUP)
        self.radio_colonnes_choix = wx.RadioButton(self, -1, _(u"Uniquement les colonnes suivantes :"))
        self.ctrl_colonnes = CTRL_Colonnes_numeriques(self)
        self.ctrl_colonnes.SetMinSize((100, 50))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.Add(self.radio_colonnes_toutes, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_colonnes_choix, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_colonnes, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(3)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioColonnes, self.radio_colonnes_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioColonnes, self.radio_colonnes_choix)

        # Init
        self.ctrl_colonnes.MAJ()
        self.OnRadioColonnes()

    def OnRadioColonnes(self, event=None):
        self.ctrl_colonnes.Enable(self.radio_colonnes_choix.GetValue())

    def Validation(self):
        return True

    def GetParametres(self):
        dictParametres = {}
        if self.radio_colonnes_choix.GetValue() == True :
            dictParametres["colonnes"] = self.ctrl_colonnes.GetCoches()
        return dictParametres

    def SetParametres(self, dictParametres={}):
        if type(dictParametres) in (six.text_type, str) :
            dictParametres = eval(dictParametres)
        if ("colonnes" in dictParametres) == True :
            self.radio_colonnes_choix.SetValue(True)
            self.ctrl_colonnes.SetCoches(dictParametres["colonnes"])
        self.OnRadioColonnes()

# ------------------------------------------------------------------------------------------------------------

class PAGE_Vide(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Contrôles
        self.label_intro = wx.StaticText(self, -1, _(u"Aucun paramètre à renseigner."))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def Validation(self):
        return True

    def GetParametres(self):
        return {}

    def SetParametres(self, dictParametres={}):
        pass




# ----------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent, id=-1)
        self.parent = parent

        self.listePanels = [
            ("numerique_avec_suggestion", PAGE_Unites(self)),
            ("numerique_sans_suggestion", PAGE_Vide(self)),
            ("numerique_total", PAGE_Total(self)),
            ("texte_infos", PAGE_Informations(self)),
            ("texte_libre", PAGE_Vide(self)),
        ]

        for code, ctrl in self.listePanels:
            label = DICT_LABELS_CATEGORIES[code]
            self.AddPage(ctrl, label)

        # Sélection par défaut
        self.SetSelection(0)

    def GetPageByCode(self, code=""):
        index = 0
        for codeTemp, ctrl in self.listePanels:
            if code == codeTemp:
                return ctrl
            index += 1
        return None

    def SetPageByCode(self, code=""):
        index = 0
        for codeTemp, ctrl in self.listePanels:
            if code == codeTemp:
                self.SetSelection(index)
            index += 1

    def GetPageActive(self):
        return self.listePanels[self.GetSelection()][1]

    def GetCodePageActive(self):
        return self.listePanels[self.GetSelection()][0]

    def Validation(self):
        return self.GetPageActive().Validation()

    def GetParametres(self):
        dictParametres = self.GetPageActive().GetParametres()
        dictParametres["categorie"] = self.GetCodePageActive()
        return dictParametres

    def SetParametres(self, dictParametres={}):
        self.GetPageActive().SetParametres(dictParametres)



# -----------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDcolonne = None
        self.dictDonnees = {}

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))

        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")

        self.label_largeur = wx.StaticText(self, -1, _(u"Largeur :"))
        self.ctrl_largeur = wx.SpinCtrl(self, -1, "", min=10, max=200)
        self.ctrl_largeur.SetValue(80)

        # Paramètres
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.SetMinSize((400, 250))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Init
        self.ctrl_nom.SetFocus()


    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une colonne"))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de la colonne (Ex : 'Enfants', 'Adultes'...)")))
        self.ctrl_largeur.SetToolTip(wx.ToolTip(_(u"Saisissez ici la largeur de la colonne")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)

        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_largeur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_largeur, 0, 0, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Paramètres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        staticbox_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Modelesdecommandesderepas")

    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette colonne !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        # Validation des paramètres
        if self.ctrl_parametres.Validation() == False :
            return False

        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        self.dictDonnees["IDcolonne"] = self.IDcolonne
        self.dictDonnees["nom"] = self.ctrl_nom.GetValue()
        self.dictDonnees["largeur"] = self.ctrl_largeur.GetValue()
        self.dictDonnees["categorie"] = self.ctrl_parametres.GetCodePageActive()
        self.dictDonnees["parametres"] = self.ctrl_parametres.GetParametres()
        if type(self.dictDonnees["parametres"]) in (six.text_type, str):
            self.dictDonnees['parametres'] = eval(self.dictDonnees["parametres"])
        return self.dictDonnees

    def SetDonnees(self, dictDonnees={}):
        self.dictDonnees = dictDonnees
        self.SetTitle(_(u"Modification d'une colonne"))
        if "IDcolonne" in self.dictDonnees :
            self.IDcolonne = self.dictDonnees["IDcolonne"]
        if "nom" in self.dictDonnees :
            self.ctrl_nom.SetValue(self.dictDonnees["nom"])
        if "largeur" in self.dictDonnees :
            self.ctrl_largeur.SetValue(self.dictDonnees["largeur"])
        if "categorie" in self.dictDonnees :
            self.ctrl_largeur.SetValue(self.dictDonnees["largeur"])
        if "parametres" in self.dictDonnees :
            self.ctrl_parametres.SetPageByCode(self.dictDonnees["categorie"])
            if type(self.dictDonnees["parametres"]) in (str, six.text_type) :
                self.dictDonnees['parametres'] = eval(self.dictDonnees["parametres"])
            self.ctrl_parametres.SetParametres(self.dictDonnees["parametres"])





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    print(dlg.GetDonnees())
    app.MainLoop()
