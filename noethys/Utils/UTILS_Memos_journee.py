#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from reportlab.lib import colors
import six

# Mapping des couleurs pour le rendu PDF (fond doux et texte d'alerte)
DICT_COULEURS_PDF = {
    "red": {"fond": colors.HexColor("#FFD9D9"), "texte": colors.HexColor("#C0392B"), "hex_fond": "#FFD9D9", "hex_texte": "#C0392B", "label": _(u"🔴 Rouge (Attention ++)")},
    "orange": {"fond": colors.HexColor("#FFE8CC"), "texte": colors.HexColor("#D35400"), "hex_fond": "#FFE8CC", "hex_texte": "#D35400", "label": _(u"🟠 Orange")},
    "yellow": {"fond": colors.HexColor("#FFF9C4"), "texte": colors.HexColor("#B7950B"), "hex_fond": "#FFF9C4", "hex_texte": "#B7950B", "label": _(u"🟡 Jaune")},
    "green": {"fond": colors.HexColor("#D5F5E3"), "texte": colors.HexColor("#27AE60"), "hex_fond": "#D5F5E3", "hex_texte": "#27AE60", "label": _(u"🟢 Vert")},
    "blue": {"fond": colors.HexColor("#D6EAF8"), "texte": colors.HexColor("#2980B9"), "hex_fond": "#D6EAF8", "hex_texte": "#2980B9", "label": _(u"🔵 Bleu")},
    "purple": {"fond": colors.HexColor("#E8DAEF"), "texte": colors.HexColor("#8E44AD"), "hex_fond": "#E8DAEF", "hex_texte": "#8E44AD", "label": _(u"🟣 Violet")},
    "pink": {"fond": colors.HexColor("#FADBD8"), "texte": colors.HexColor("#C0392B"), "hex_fond": "#FADBD8", "hex_texte": "#C0392B", "label": _(u"🌸 Rose")},
    "gray": {"fond": colors.HexColor("#EAEDED"), "texte": colors.HexColor("#7F8C8D"), "hex_fond": "#EAEDED", "hex_texte": "#7F8C8D", "label": _(u"⚪ Gris")},
    "brown": {"fond": colors.HexColor("#EDBB99"), "texte": colors.HexColor("#A04000"), "hex_fond": "#EDBB99", "hex_texte": "#A04000", "label": _(u"🟤 Marron")},
}


def GetStylesCouleurPDF(codeCouleur):
    """ Retourne le dictionnaire contenant les couleurs de fond et de texte pour le PDF, ou None si pas de surlignage """
    if not codeCouleur:
        return None
    codeCouleur = str(codeCouleur).lower().strip()
    if codeCouleur in ("none", "", "noir", "black"):
        return None
    if codeCouleur in DICT_COULEURS_PDF:
        return DICT_COULEURS_PDF[codeCouleur]
    return None


def GetPenseBeteJour(date=None, DB=None):
    """ Récupère le pense-bête d'une date (IDindividu IS NULL ou IDindividu = 0) """
    if not date:
        return None
    fermerDB = False
    if DB is None:
        DB = GestionDB.DB()
        fermerDB = True
    try:
        req = """SELECT IDmemo, texte, couleur FROM memo_journee 
                 WHERE (IDindividu IS NULL OR IDindividu = 0) AND date = '%s';""" % str(date)
        DB.ExecuterReq(req)
        res = DB.ResultatReq()
        if res and len(res) > 0:
            return {"IDmemo": res[0][0], "texte": res[0][1] or "", "couleur": res[0][2] or "yellow"}
        return None
    finally:
        if fermerDB:
            DB.Close()


def ParseActivitesPenseBete(codeCouleur):
    """ Retourne 'all' ou une liste d'IDactivite [int, ...] """
    if not codeCouleur or codeCouleur in ("all", "yellow", "None", ""):
        return "all"
    codeStr = str(codeCouleur).strip()
    if codeStr.startswith("act:"):
        try:
            return [int(x.strip()) for x in codeStr[4:].split(",") if x.strip()]
        except:
            return "all"
    return "all"


def FormatActivitesPenseBete(activites):
    """ Formate pour stockage dans le champ couleur de memo_journee ('all' ou 'act:1,2,3') """
    if not activites or activites == "all":
        return "all"
    if isinstance(activites, (list, tuple, set)):
        return "act:" + ",".join(str(int(x)) for x in activites)
    return str(activites)


def SetPenseBeteJour(date=None, texte="", couleur="all", DB=None):
    """ Enregistre, met à jour ou supprime le pense-bête pour la date """
    if not date:
        return None
    fermerDB = False
    if DB is None:
        DB = GestionDB.DB()
        fermerDB = True
    try:
        penseBete = GetPenseBeteJour(date, DB=DB)
        texte = (texte or "").strip()
        if penseBete:
            if not texte:
                DB.ReqDEL("memo_journee", "IDmemo", penseBete["IDmemo"])
            else:
                listeDonnees = [("texte", texte), ("couleur", couleur or "all")]
                DB.ReqMAJ("memo_journee", listeDonnees, "IDmemo", penseBete["IDmemo"])
        else:
            if texte:
                listeDonnees = [
                    ("IDindividu", None),
                    ("date", str(date)),
                    ("texte", texte),
                    ("couleur", couleur or "all"),
                ]
                DB.ReqInsert("memo_journee", listeDonnees)
    finally:
        if fermerDB:
            DB.Close()


def GetMemosIndividusDate(date=None, DB=None):
    """ Récupère la liste des mémos individuels pour une date """
    if not date:
        return []
    fermerDB = False
    if DB is None:
        DB = GestionDB.DB()
        fermerDB = True
    try:
        req = """SELECT memo_journee.IDmemo, memo_journee.IDindividu, memo_journee.texte, memo_journee.couleur,
                        individus.nom, individus.prenom
                 FROM memo_journee
                 JOIN individus ON individus.IDindividu = memo_journee.IDindividu
                 WHERE memo_journee.IDindividu IS NOT NULL 
                   AND memo_journee.IDindividu != 0
                   AND memo_journee.date = '%s'
                 ORDER BY individus.nom, individus.prenom;""" % str(date)
        DB.ExecuterReq(req)
        res = DB.ResultatReq()
        listeMemos = []
        for IDmemo, IDindividu, texte, couleur, nom, prenom in res:
            if not couleur or str(couleur).lower().strip() in ("none", "", "noir", "black"):
                coulClean = None
            else:
                coulClean = str(couleur).strip()
            listeMemos.append({
                "IDmemo": IDmemo,
                "IDindividu": IDindividu,
                "texte": texte or "",
                "couleur": coulClean,
                "nom": nom,
                "prenom": prenom,
            })
        return listeMemos
    finally:
        if fermerDB:
            DB.Close()


def SetMemoIndividuDate(IDindividu, date, texte="", couleur=None, DB=None):
    """ Enregistre, modifie ou supprime le mémo d'un individu pour une date """
    if not IDindividu or not date:
        return
    if not couleur or str(couleur).lower().strip() in ("none", "", "noir", "black"):
        couleur = None
    else:
        couleur = str(couleur).strip()
    fermerDB = False
    if DB is None:
        DB = GestionDB.DB()
        fermerDB = True
    try:
        req = """SELECT IDmemo FROM memo_journee WHERE IDindividu = %d AND date = '%s';""" % (int(IDindividu), str(date))
        DB.ExecuterReq(req)
        res = DB.ResultatReq()
        texte = (texte or "").strip()
        if res and len(res) > 0:
            IDmemo = res[0][0]
            if not texte:
                DB.ReqDEL("memo_journee", "IDmemo", IDmemo)
            else:
                listeDonnees = [("texte", texte), ("couleur", couleur)]
                DB.ReqMAJ("memo_journee", listeDonnees, "IDmemo", IDmemo)
        else:
            if texte:
                listeDonnees = [
                    ("IDindividu", IDindividu),
                    ("date", str(date)),
                    ("texte", texte),
                    ("couleur", couleur),
                ]
                DB.ReqInsert("memo_journee", listeDonnees)
    finally:
        if fermerDB:
            DB.Close()


def SupprimerMemo(IDmemo, DB=None):
    """ Supprime un mémo par son IDmemo """
    if not IDmemo:
        return
    fermerDB = False
    if DB is None:
        DB = GestionDB.DB()
        fermerDB = True
    try:
        DB.ReqDEL("memo_journee", "IDmemo", IDmemo)
    finally:
        if fermerDB:
            DB.Close()


class CTRL_Couleur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.couleurs = [
            {"code": None, "label": _(u"Aucun surlignage (texte normal)")},
            {"code": "red", "label": _(u"🔴 Rouge (Attention ++ / Souci)")},
            {"code": "orange", "label": _(u"🟠 Orange (Alerte modérée)")},
            {"code": "yellow", "label": _(u"🟡 Jaune (À surveiller)")},
            {"code": "green", "label": _(u"🟢 Vert")},
            {"code": "blue", "label": _(u"🔵 Bleu")},
            {"code": "purple", "label": _(u"🟣 Violet")},
            {"code": "pink", "label": _(u"🌸 Rose")},
            {"code": "gray", "label": _(u"⚪ Gris")},
            {"code": "brown", "label": _(u"🟤 Marron")},
        ]
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for dictCouleur in self.couleurs:
            self.dictDonnees[index] = {"code": dictCouleur["code"], "label": dictCouleur["label"]}
            listeItems.append(dictCouleur["label"])
            index += 1
        self.SetItems(listeItems)

    def SetCode(self, code=None):
        if not code or str(code).lower().strip() in ("none", "", "noir", "black"):
            code = None
        for index, values in self.dictDonnees.items():
            if values["code"] == code:
                self.SetSelection(index)
                return
        self.SetSelection(0)

    def GetCode(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]["code"]


class DLG_Saisie_memo(wx.Dialog):
    def __init__(self, parent, texte="", couleur=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        self.label_texte = wx.StaticText(self, wx.ID_ANY, _(u"Texte / Motif :"))
        self.ctrl_texte = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_PROCESS_ENTER)
        self.ctrl_texte.SetMinSize((300, -1))

        self.label_couleur = wx.StaticText(self, wx.ID_ANY, _(u"Couleur :"))
        self.ctrl_couleur = CTRL_Couleur(self)

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.ctrl_texte.Bind(wx.EVT_KEY_DOWN, self.OnKey)

        # Init Contrôles
        if texte:
            self.SetTitle(_(u"Modification d'un signalement / mémo"))
            self.ctrl_texte.SetValue(texte)
            self.ctrl_couleur.SetCode(couleur)
        else:
            self.SetTitle(_(u"Saisie d'un signalement / mémo"))
            if couleur:
                self.ctrl_couleur.SetCode(couleur)
        self.ctrl_texte.SetFocus()

    def __set_properties(self):
        self.ctrl_texte.SetToolTip(wx.ToolTip(_(u"Saisissez le texte du mémo ou motif de l'alerte (ex: Attention cette personne-là)")))
        self.ctrl_couleur.SetToolTip(wx.ToolTip(_(u"Sélectionnez une couleur pour surligner la personne sur la liste imprimée.")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        grid_sizer_haut = wx.FlexGridSizer(3, 2, 10, 10)

        grid_sizer_haut.Add(self.label_texte, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_texte, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_couleur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_couleur, 0, 0, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(1, 3, 10, 10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnKey(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.OnBoutonOk()
        event.Skip()

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event=None):
        self.texte = self.ctrl_texte.GetValue()
        self.couleur = self.ctrl_couleur.GetCode()
        self.EndModal(wx.ID_OK)


class DLG_Saisie_pense_bete(wx.Dialog):
    """ Dialogue de saisie du pense-bête de la journée """
    def __init__(self, parent, date=None, texte="", couleur="all"):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.date = date
        self.couleurInitiale = couleur or "all"

        from Utils import UTILS_Dates
        dateTexte = UTILS_Dates.DateComplete(date) if date else _(u"la journée")
        self.SetTitle(_(u"Alerte du jour"))

        self.label_intro = wx.StaticText(self, -1, _(u"Alerte pour le %s :") % dateTexte)
        self.label_intro.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.ctrl_texte = wx.TextCtrl(self, -1, texte or u"", style=wx.TE_MULTILINE)
        self.ctrl_texte.SetMinSize((460, 80))
        self.ctrl_texte.SetToolTip(wx.ToolTip(_(u"Cette alerte apparaîtra sur la liste imprimée de la journée.")))

        # Activités
        self.listeActivitesDispos = self.GetActivitesDisponibles()
        self.radio_toutes = wx.RadioButton(self, -1, _(u"Afficher sur toutes les activités"), style=wx.RB_GROUP)
        self.radio_certaines = wx.RadioButton(self, -1, _(u"Afficher uniquement sur les activités cochées ci-dessous :"))

        self.check_activites = wx.CheckListBox(self, -1, size=(-1, 100))
        targetAct = ParseActivitesPenseBete(self.couleurInitiale)
        for idx, (IDact, nomAct) in enumerate(self.listeActivitesDispos):
            self.check_activites.Append(nomAct)
            if targetAct == "all" or IDact in targetAct:
                self.check_activites.Check(idx, True)

        if targetAct == "all":
            self.radio_toutes.SetValue(True)
            self.check_activites.Enable(False)
        else:
            self.radio_certaines.SetValue(True)
            self.check_activites.Enable(True)

        self.bouton_cocher_tout = wx.Button(self, -1, _(u"Tout cocher"), size=(-1, 22))
        self.bouton_decocher_tout = wx.Button(self, -1, _(u"Tout décocher"), size=(-1, 22))

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Enregistrer"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_intro, 0, wx.ALL, 10)
        sizer.Add(self.ctrl_texte, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        sizer_act_header = wx.BoxSizer(wx.HORIZONTAL)
        sizer_act_header.Add(self.radio_toutes, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 15)
        sizer_act_header.Add(self.radio_certaines, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer.Add(sizer_act_header, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        sizer_act_row = wx.BoxSizer(wx.HORIZONTAL)
        sizer_act_row.Add(self.check_activites, 1, wx.EXPAND | wx.RIGHT, 5)

        sizer_act_btns = wx.BoxSizer(wx.VERTICAL)
        sizer_act_btns.Add(self.bouton_cocher_tout, 0, wx.BOTTOM | wx.EXPAND, 3)
        sizer_act_btns.Add(self.bouton_decocher_tout, 0, wx.BOTTOM | wx.EXPAND, 3)
        sizer_act_row.Add(sizer_act_btns, 0, wx.EXPAND, 0)
        sizer.Add(sizer_act_row, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        sizer_boutons = wx.BoxSizer(wx.HORIZONTAL)
        sizer_boutons.AddStretchSpacer()
        sizer_boutons.Add(self.bouton_ok, 0, wx.RIGHT, 10)
        sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        sizer.Add(sizer_boutons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(sizer)
        self.Fit()
        self.CenterOnScreen()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioToutes, self.radio_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCertaines, self.radio_certaines)
        self.Bind(wx.EVT_BUTTON, self.OnCocherTout, self.bouton_cocher_tout)
        self.Bind(wx.EVT_BUTTON, self.OnDecocherTout, self.bouton_decocher_tout)
        self.ctrl_texte.SetFocus()

    def GetActivitesDisponibles(self):
        if not self.date:
            return []
        DB = GestionDB.DB()
        req = """SELECT activites.IDactivite, activites.nom 
                 FROM activites
                 LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
                 WHERE ouvertures.date = '%s'
                 GROUP BY activites.IDactivite
                 ORDER BY activites.nom;""" % str(self.date)
        DB.ExecuterReq(req)
        res = DB.ResultatReq()
        DB.Close()
        if not res:
            DB = GestionDB.DB()
            req = """SELECT IDactivite, nom FROM activites ORDER BY nom;"""
            DB.ExecuterReq(req)
            res = DB.ResultatReq()
            DB.Close()
        return res or []

    def OnRadioToutes(self, event=None):
        self.check_activites.Enable(False)
        self.bouton_cocher_tout.Enable(False)
        self.bouton_decocher_tout.Enable(False)

    def OnRadioCertaines(self, event=None):
        self.check_activites.Enable(True)
        self.bouton_cocher_tout.Enable(True)
        self.bouton_decocher_tout.Enable(True)

    def OnCocherTout(self, event=None):
        for i in range(self.check_activites.GetCount()):
            self.check_activites.Check(i, True)

    def OnDecocherTout(self, event=None):
        for i in range(self.check_activites.GetCount()):
            self.check_activites.Check(i, False)

    def OnBoutonOk(self, event):
        self.texte = self.ctrl_texte.GetValue()
        if self.radio_toutes.GetValue() == True:
            self.couleur = "all"
        else:
            coches = []
            for i, (IDact, nom) in enumerate(self.listeActivitesDispos):
                if self.check_activites.IsChecked(i):
                    coches.append(IDact)
            if len(coches) == 0 or len(coches) == len(self.listeActivitesDispos):
                self.couleur = "all"
            else:
                self.couleur = FormatActivitesPenseBete(coches)
        self.EndModal(wx.ID_OK)
