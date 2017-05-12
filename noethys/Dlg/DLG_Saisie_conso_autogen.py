#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_heure
from Ctrl import CTRL_Etiquettes
from Utils import UTILS_Texte
import wx.lib.agw.hyperlink as Hyperlink
import GestionDB



def ConvertParametresEnDict(texte=""):
    dictDonnees = {}
    if texte in ("", None) : return dictDonnees

    listeDonnees = texte.split("##")
    for donnee in listeDonnees :
        champ, valeur = donnee.split(":=")

        if champ == "ETIQUETTES" and valeur != None :
            etiquettes = UTILS_Texte.ConvertStrToListe(valeur)
            dictDonnees["etiquettes"] = etiquettes

        if champ == "ETAT" and valeur != None :
            dictDonnees["etat"] = valeur

        if champ == "QUANTITE" and valeur != None :
            dictDonnees["quantite"] = int(valeur)

        if champ == "HEUREDEBUT" and valeur != None :
            dictDonnees["heure_debut"] = valeur

        if champ == "HEUREFIN" and valeur != None :
            dictDonnees["heure_fin"] = valeur

    return dictDonnees


# ---------------------------------------------------------------------------------------------------------------------------------
class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent

        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        listeLabels = []
        for code, label in self.parent.listeChamps :
            listeLabels.append(u"%s (%s)" % (label, code))
        dlg = wx.SingleChoiceDialog(None, _(u"Sélectionnez un champ à insérer :"), _(u"Insérer un champ"), listeLabels, wx.CHOICEDLG_STYLE)
        dlg.SetSize((580, 500))
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            champ = self.parent.listeChamps[dlg.GetSelection()][0]
            self.parent.InsertTexte(u"{%s}" % champ)
        dlg.Destroy()
        self.UpdateLink()


# ---------------------------------------------------------------------------------------------------------------------------------



class DLG_Saisie_formule(wx.Dialog):
    def __init__(self, parent, listeChamps=[], formule="", titre=_(u"Saisie d'une formule")):
        """ listeChamps = [(code, label), ...] """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.listeChamps = listeChamps
        self.SetTitle(titre)

        self.label_formule = wx.StaticText(self, -1, _(u"Saisissez une formule :"))
        self.ctrl_formule = wx.TextCtrl(self, -1, formule, style=wx.TE_MULTILINE)
        self.hyper_formule = Hyperlien(self, label=_(u"Insérer un champ"), infobulle=_(u"Cliquez ici pour insérer un champ"), URL="")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.ctrl_formule.SetToolTip(wx.ToolTip(_(u"Saisissez une formule")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((550, 350))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Formule
        grid_sizer_formule = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_formule.Add(self.label_formule, 0, 0, 0)
        grid_sizer_formule.Add(self.ctrl_formule, 0, wx.EXPAND, 0)
        grid_sizer_formule.Add(self.hyper_formule, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)
        grid_sizer_formule.AddGrowableRow(1)
        grid_sizer_formule.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_formule, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        if self.GetFormule() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune formule !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.EndModal(wx.ID_OK)

    def InsertTexte(self, texte=u""):
        positionCurseur = self.ctrl_formule.GetInsertionPoint()
        self.ctrl_formule.WriteText(texte)
        self.ctrl_formule.SetInsertionPoint(positionCurseur+len(texte))
        self.ctrl_formule.SetFocus()

    def GetFormule(self):
        return self.ctrl_formule.GetValue().strip()


# ------------------------------------------------------------------------------------

class CTRL_Conditions(wx.ListBox):
    def __init__(self, parent, IDactivite=None, IDunite=None):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.listeValeurs = []
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.Modifier)

    def SetValeur(self, valeur=""):
        self.listeValeurs = []
        if valeur != None :
            self.listeValeurs = valeur.split(";")
        self.MAJ()

    def GetValeur(self):
        if len(self.listeValeurs) > 0 :
            return ";".join(self.listeValeurs)
        else :
            return None

    def MAJ(self):
        self.listeValeurs.sort()
        self.Set(self.listeValeurs)

    def GetChamps(self):
        return self.parent.GetChamps()

    def Ajouter(self, event=None):
        dlg = DLG_Saisie_formule(self, listeChamps=self.GetChamps())
        if dlg.ShowModal() == wx.ID_OK:
            formule = dlg.GetFormule()
            self.listeValeurs.append(formule)
            self.MAJ()
        dlg.Destroy()


    def Modifier(self, event=None):
        valeur = self.GetStringSelection()
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune condition à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = DLG_Saisie_formule(self, listeChamps=self.GetChamps(), formule=valeur)
        if dlg.ShowModal() == wx.ID_OK:
            formule = dlg.GetFormule()
            self.listeValeurs[index] = formule
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self, event=None):
        valeur = self.GetStringSelection()
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune condition à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette condition ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.listeValeurs.pop(index)
            self.MAJ()
        dlg.Destroy()



# ------------------------------------------------------------------------------------

class CTRL_Choix_etat(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1))
        self.parent = parent
        self.listeEtats = [
            #(None, _(u"Ne pas modifier")),
            ("reservation", _(u"Pointage en attente")),
            ("present", _(u"Présence")),
            ("absentj", _(u"Absence justifiée")),
            ("absenti", _(u"Absence injustifiée")),
            ]
        self.MAJ()

    def MAJ(self):
        listeItems = []
        for code, label in self.listeEtats :
            listeItems.append(label)
        self.SetItems(listeItems)
        self.Select(0)

    def SetValeur(self, valeur=None):
        index = 0
        for code, label in self.listeEtats :
            if code == valeur :
                 self.SetSelection(index)
            index += 1

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]



class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, IDunite=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_conso_autogen", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDunite = IDunite

        # Importation des unités
        self.listeUnites = self.ImportationUnites()

        # Conditions
        self.staticbox_conditions_staticbox = wx.StaticBox(self, -1, _(u"Conditions d'application"))
        self.ctrl_conditions = CTRL_Conditions(self, IDactivite=IDactivite, IDunite=IDunite)

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Paramètres de la consommation
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres de la consommation"))

        self.label_heure_debut = wx.StaticText(self, -1, _(u"Heure de début :"))
        self.radio_heure_debut_fixe = wx.RadioButton(self, -1, _(u"Fixe"), style=wx.RB_GROUP)
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.radio_heure_debut_formule = wx.RadioButton(self, -1, _(u"Formule"))
        self.ctrl_heure_debut_formule = wx.TextCtrl(self, -1, u"")
        self.bouton_heure_debut_formule = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))

        self.label_heure_fin = wx.StaticText(self, -1, _(u"Heure de fin :"))
        self.radio_heure_fin_fixe = wx.RadioButton(self, -1, _(u"Fixe"), style=wx.RB_GROUP)
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)
        self.radio_heure_fin_formule = wx.RadioButton(self, -1, _(u"Formule"))
        self.ctrl_heure_fin_formule = wx.TextCtrl(self, -1, u"")
        self.ctrl_heure_fin_formule.SetMinSize((150, -1))
        self.bouton_heure_fin_formule = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))

        self.label_etat = wx.StaticText(self, -1, _(u"Etat :"))
        self.ctrl_etat = CTRL_Choix_etat(self)

        self.label_quantite = wx.StaticText(self, -1, _(u"Quantité :"))
        self.ctrl_quantite = wx.SpinCtrl(self, -1, "1", min=1, max=500, size=(80, -1))

        self.label_etiquettes = wx.StaticText(self, -1, _(u"Etiquettes :"))
        self.ctrl_etiquettes = CTRL_Etiquettes.CTRL(self, listeActivites=[self.IDactivite,], activeMenu=False)
        self.ctrl_etiquettes.MAJ()

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_conditions.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_conditions.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_conditions.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioHeureDebut, self.radio_heure_debut_fixe)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioHeureDebut, self.radio_heure_debut_formule)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioHeureFin, self.radio_heure_fin_fixe)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioHeureFin, self.radio_heure_fin_formule)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHeureDebutFormule, self.bouton_heure_debut_formule)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHeureFinFormule, self.bouton_heure_fin_formule)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôle
        self.OnRadioHeureDebut(None)
        self.OnRadioHeureFin(None)

    def __set_properties(self):
        self.SetTitle(_(u"Paramètres de l'auto-génération"))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer une nouvelle condition")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la condition sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la condition sélectionnée dans la liste")))
        self.bouton_heure_debut_formule.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la formule")))
        self.bouton_heure_fin_formule.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la formule")))
        self.ctrl_etat.SetToolTip(wx.ToolTip(_(u"Sélectionnez un état")))
        self.ctrl_quantite.SetToolTip(wx.ToolTip(_(u"Saisir une quantité (1 par défaut)")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Conditions
        staticbox_conditions = wx.StaticBoxSizer(self.staticbox_conditions_staticbox, wx.VERTICAL)
        grid_sizer_conditions = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_conditions.Add(self.ctrl_conditions, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_conditions.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)

        grid_sizer_conditions.AddGrowableRow(0)
        grid_sizer_conditions.AddGrowableCol(0)
        staticbox_conditions.Add(grid_sizer_conditions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_conditions, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Paramètres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # Heure début
        grid_sizer_parametres.Add(self.label_heure_debut, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_heure_debut = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_heure_debut.Add(self.radio_heure_debut_fixe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heure_debut.Add(self.ctrl_heure_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heure_debut.Add( (1, 1), 0, 0, 0)
        grid_sizer_heure_debut.Add(self.radio_heure_debut_formule, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heure_debut.Add(self.ctrl_heure_debut_formule, 1, wx.EXPAND, 0)
        grid_sizer_heure_debut.Add(self.bouton_heure_debut_formule, 0, 0, 0)
        grid_sizer_heure_debut.AddGrowableCol(4)

        grid_sizer_parametres.Add(grid_sizer_heure_debut, 0, wx.EXPAND, 0)

        # Heure fin
        grid_sizer_parametres.Add(self.label_heure_fin, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_heure_fin = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_heure_fin.Add(self.radio_heure_fin_fixe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heure_fin.Add(self.ctrl_heure_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heure_fin.Add( (1, 1), 0, 0, 0)
        grid_sizer_heure_fin.Add(self.radio_heure_fin_formule, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heure_fin.Add(self.ctrl_heure_fin_formule, 1, wx.EXPAND, 0)
        grid_sizer_heure_fin.Add(self.bouton_heure_fin_formule, 0, 0, 0)
        grid_sizer_heure_fin.AddGrowableCol(4)

        grid_sizer_parametres.Add(grid_sizer_heure_fin, 0, wx.EXPAND, 0)

        # Etiquettes
        grid_sizer_parametres.Add(self.label_etiquettes, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_parametres.Add(self.ctrl_etiquettes, 1, wx.EXPAND, 0)

        # Etat
        grid_sizer_parametres.Add(self.label_quantite, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_etat = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_etat.Add(self.ctrl_quantite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etat.Add( (20, 1), 0, 0, 0)
        grid_sizer_etat.Add(self.label_etat, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etat.Add(self.ctrl_etat, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_parametres.Add(grid_sizer_etat, 0, wx.EXPAND, 0)

        grid_sizer_parametres.AddGrowableCol(1)
        staticbox_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
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
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        self.SetMinSize(self.GetSize())

    def ImportationUnites(self):
        DB = GestionDB.DB()
        req = """SELECT unites.IDunite, unites.nom, unites.type
        FROM unites
        WHERE IDactivite=%d
        ;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        listeUnites = []
        for IDunite, nomUnite, typeUnite in listeTemp :
            if IDunite != self.IDunite :
                listeUnites.append({"IDunite" : IDunite, "nom" : nomUnite, "type" : typeUnite})
        return listeUnites

    def OnRadioHeureDebut(self, event):
        self.ctrl_heure_debut.Enable(self.radio_heure_debut_fixe.GetValue())
        self.ctrl_heure_debut_formule.Enable(self.radio_heure_debut_formule.GetValue())
        self.bouton_heure_debut_formule.Enable(self.radio_heure_debut_formule.GetValue())

    def OnRadioHeureFin(self, event):
        self.ctrl_heure_fin.Enable(self.radio_heure_fin_fixe.GetValue())
        self.ctrl_heure_fin_formule.Enable(self.radio_heure_fin_formule.GetValue())
        self.bouton_heure_fin_formule.Enable(self.radio_heure_fin_formule.GetValue())

    def GetChamps(self):
        """ Création de la liste des champs """
        listeCodes = [
            ("DUREE", _(u"Durée")),
            ("HEUREDEBUT", _(u"Heure de début")),
            ("HEUREFIN", _(u"Heure de fin")),
            ("QUANTITE", _(u"Quantité")),
            ("ETAT", _(u"Etat")),
        ]
        listeChamps = []
        for dictUnite in self.listeUnites :
            for code, label in listeCodes :
                codeChamp = "%s_UNITE%d" % (code, dictUnite["IDunite"])
                nomChamp = u"%s de l'unité '%s'" % (label, dictUnite["nom"])
                listeChamps.append((codeChamp, nomChamp))
        return listeChamps

    def OnBoutonHeureDebutFormule(self, event):
        formule = self.ctrl_heure_debut_formule.GetValue()
        dlg = DLG_Saisie_formule(self, listeChamps=self.GetChamps(), formule=formule)
        if dlg.ShowModal() == wx.ID_OK:
            formule = dlg.GetFormule()
            self.ctrl_heure_debut_formule.SetValue(formule)
        dlg.Destroy()

    def OnBoutonHeureFinFormule(self, event):
        formule = self.ctrl_heure_fin_formule.GetValue()
        dlg = DLG_Saisie_formule(self, listeChamps=self.GetChamps(), formule=formule)
        if dlg.ShowModal() == wx.ID_OK:
            formule = dlg.GetFormule()
            self.ctrl_heure_fin_formule.SetValue(formule)
        dlg.Destroy()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)        

    def OnBoutonOk(self, event):
        # Vérification des données
        # TODO : Vérification données saisie paramètres conso autogen à coder !!!!!!!!!!!

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        """ Récupération des données """
        conditions = self.ctrl_conditions.GetValeur()

        if self.radio_heure_debut_fixe.GetValue() == True :
            heure_debut = self.ctrl_heure_debut.GetHeure()
        else :
            heure_debut = "FORMULE:" + self.ctrl_heure_debut_formule.GetValue()

        if self.radio_heure_fin_fixe.GetValue() == True :
            heure_fin = self.ctrl_heure_fin.GetHeure()
        else :
            heure_fin = "FORMULE:" + self.ctrl_heure_fin_formule.GetValue()

        etiquettes = self.ctrl_etiquettes.GetCoches()
        etat = self.ctrl_etat.GetValeur()
        quantite = self.ctrl_quantite.GetValue()

        # Conversion en str
        etiquettesStr = "ETIQUETTES:="
        if etiquettes == [] :
            etiquettesStr += ""
        else :
            etiquettesStr += UTILS_Texte.ConvertListeToStr(etiquettes)

        quantiteStr = "QUANTITE:=%d" % quantite

        heure_debutStr = "HEUREDEBUT:="
        if heure_debut == None :
            heure_debutStr += ""
        else :
            heure_debutStr += heure_debut

        heure_finStr = "HEUREFIN:="
        if heure_fin == None :
            heure_finStr += ""
        else :
            heure_finStr += heure_fin

        etatStr = "ETAT:=%s" % etat

        listeTemp = (etiquettesStr, etatStr, quantiteStr, heure_debutStr, heure_finStr)
        parametres = "##".join(listeTemp)

        # Mémorisation
        dictDonnees = {
            "heure_debut" : heure_debut,
            "heure_fin" : heure_fin,
            "etiquettes" : etiquettes,
            "etat" : etat,
            "quantite" : quantite,
            "conditions" : conditions,
            "parametres" : parametres,
        }
        return dictDonnees

    def GetConditions(self):
        dictDonnees = self.GetDonnees()
        return dictDonnees["conditions"]

    def GetParametres(self):
        dictDonnees = self.GetDonnees()
        return dictDonnees["parametres"]

    def SetConditions(self, texte=""):
        self.ctrl_conditions.SetValeur(texte)

    def SetParametres(self, texte=""):
        if texte in ("", None) : return

        listeDonnees = texte.split("##")
        for donnee in listeDonnees :
            champ, valeur = donnee.split(":=")

            if champ == "ETIQUETTES" and valeur != None :
                etiquettes = UTILS_Texte.ConvertStrToListe(valeur)
                self.ctrl_etiquettes.SetCoches(etiquettes)

            if champ == "ETAT" and valeur != None :
                self.ctrl_etat.SetValeur(valeur)

            if champ == "QUANTITE" and valeur != None :
                self.ctrl_quantite.SetValue(int(valeur))

            if champ == "HEUREDEBUT" and valeur != None :
                heure_debut = valeur
                if "FORMULE:" in heure_debut :
                    self.radio_heure_debut_formule.SetValue(True)
                    heure_debut = heure_debut.replace("FORMULE:", "")
                    self.ctrl_heure_debut_formule.SetValue(heure_debut)
                else :
                    self.radio_heure_debut_fixe.SetValue(True)
                    if heure_debut not in (None, "") :
                        self.ctrl_heure_debut.SetHeure(heure_debut)

            if champ == "HEUREFIN" and valeur != None :
                heure_fin = valeur
                if "FORMULE:" in heure_fin :
                    self.radio_heure_fin_formule.SetValue(True)
                    heure_fin = heure_fin.replace("FORMULE:", "")
                    self.ctrl_heure_fin_formule.SetValue(heure_fin)
                else :
                    self.radio_heure_fin_fixe.SetValue(True)
                    if heure_fin not in (None, "") :
                        self.ctrl_heure_fin.SetHeure(heure_fin)

        # Init contrôles
        self.OnRadioHeureDebut(None)
        self.OnRadioHeureFin(None)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
