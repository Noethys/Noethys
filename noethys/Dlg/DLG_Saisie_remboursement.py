#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import datetime
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Saisie_euros
from Utils import UTILS_Identification
from Ctrl import CTRL_Bandeau
import wx.lib.agw.hyperlink as Hyperlink
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Ol.OL_Verification_ventilation import VentilationAuto
from DLG_Saisie_reglement import CTRL_Mode, CTRL_Compte

from Utils import UTILS_Texte
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


def GetSolde(IDcompte_payeur):
    """ Récupère le solde de la famille """
    # Ventilation automatique
    VentilationAuto(IDcompte_payeur)

    DB = GestionDB.DB()

    # Récupère les prestations
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_prestations
    FROM prestations
    WHERE IDcompte_payeur=%d
    GROUP BY IDcompte_payeur;""" % IDcompte_payeur
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    if len(listePrestations) > 0 :
        total_prestations = listePrestations[0][1]
    else :
        total_prestations = 0.0

    # Récupère les règlements
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_reglements
    FROM reglements
    WHERE IDcompte_payeur=%d
    GROUP BY IDcompte_payeur;""" % IDcompte_payeur
    DB.ExecuterReq(req)
    listeReglements = DB.ResultatReq()
    if len(listeReglements) > 0 :
        total_reglements = listeReglements[0][1]
    else :
        total_reglements = 0.0

    DB.Close()

    # Calcule le solde du compte
    solde = total_prestations - total_reglements
    return solde




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
        self.parent.CreerMode()




class CTRL_Payeurs(wx.Choice):
    def __init__(self, parent, IDcompte_payeur=None):
        wx.Choice.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.IDcompte_payeur = IDcompte_payeur
        self.MAJ()

    def MAJ(self):
        self.listeDonnees = []
        self.Importation()
        listeItems = []
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["nom"]
                listeItems.append(label)
        self.Set(listeItems)
        if len(listeItems) > 0 :
            self.Select(0)

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDpayeur, nom
        FROM payeurs
        WHERE IDcompte_payeur=%d
        ORDER BY nom; """ % self.IDcompte_payeur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDpayeur, nom in listeDonnees :
            valeurs = {"ID" : IDpayeur, "nom" : nom}
            self.listeDonnees.append(valeurs)

    def SetID(self, ID=None):
        index = 0
        for dictValeurs in self.listeDonnees :
            if ID == dictValeurs["ID"] :
                self.SetSelection(index)
                return
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        ID = self.listeDonnees[index]["ID"]
        return ID



class Dialog(wx.Dialog):
    def __init__(self, parent, IDcompte_payeur=None, solde=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDcompte_payeur = IDcompte_payeur
        self.solde = solde

        titre = _(u"Saisir un remboursement")
        intro = _(u"Cette fonctionnalité permet de rembourser un avoir. Deux prestations et un règlement fictif seront générés automatiquement afin de régulariser le compte.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Remboursement.png")

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))

        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)

        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))

        self.label_compte = wx.StaticText(self, -1, _(u"Compte bancaire :"))
        self.ctrl_compte = CTRL_Compte(self)

        self.label_payeur = wx.StaticText(self, -1, _(u"Nom du payeur :"))
        self.ctrl_payeur = CTRL_Payeurs(self, self.IDcompte_payeur)
        self.bouton_payeurs = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.label_mode = wx.StaticText(self, -1, _(u"Mode de règlement :"))
        self.ctrl_mode = CTRL_Mode(self)
        self.ctrl_mode.SetMinSize((200, -1))
        self.bouton_modes = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.hyper_creer_mode = Hyperlien(self, label=_(u"Créer un mode 'Remboursement'"), infobulle=_(u"Si vous n'avez pas de mode 'Remboursement' dans la liste des modes, cliquez ici pour en créer automatiquement."), URL="creer_mode")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModes, self.bouton_modes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonPayeurs, self.bouton_payeurs)

        # Init
        self.SelectModeRemboursement()

        if solde != None :
            self.ctrl_montant.SetMontant(solde)

        wx.CallLater(1, self.SendSizeEvent)


    def __set_properties(self):
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez ici le montant du remboursement")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations [Optionnel]. Vous pouvez par exemple saisir le numéro de chèque qui a été utilisé pour le remboursement, etc...")))
        self.ctrl_payeur.SetToolTip(wx.ToolTip(_(u"Sélectionnez le payeur qui sera utilisé dans l'enregistrement du règlement fictif")))
        self.bouton_payeurs.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer un payeur")))
        self.ctrl_mode.SetToolTip(wx.ToolTip(_(u"Sélectionnez le mode de règlement qui sera utilisé. Si un mode 'Remboursement' n'existe pas, créez-le.")))
        self.bouton_modes.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer un mode de règlement")))
        self.ctrl_compte.SetToolTip(wx.ToolTip(_(u"Sélectionnez le compte bancaire qui sera utilisé pour le remboursement")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)

        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_montant, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        grid_sizer_options.Add(self.label_compte, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_compte, 0, wx.EXPAND, 0)

        grid_sizer_options.Add(self.label_payeur, 0, wx.ALIGN_RIGHT|wx.TOP, 4)

        grid_sizer_mode = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_mode.Add(self.ctrl_payeur, 0, wx.EXPAND, 0)
        grid_sizer_mode.Add(self.bouton_payeurs, 0, wx.EXPAND, 0)
        grid_sizer_mode.AddGrowableCol(0)
        grid_sizer_options.Add(grid_sizer_mode, 0, wx.EXPAND, 0)

        grid_sizer_options.Add(self.label_mode, 0, wx.ALIGN_RIGHT|wx.TOP, 4)

        grid_sizer_mode = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_mode.Add(self.ctrl_mode, 0, wx.EXPAND, 0)
        grid_sizer_mode.Add(self.bouton_modes, 0, wx.EXPAND, 0)
        grid_sizer_mode.Add(self.hyper_creer_mode, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mode.AddGrowableCol(0)
        grid_sizer_options.Add(grid_sizer_mode, 0, wx.EXPAND, 0)

        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def SelectModeRemboursement(self):
        for index, dictTemp in self.ctrl_mode.dictDonnees.iteritems() :
            if "remboursement" in UTILS_Texte.Supprime_accent(dictTemp["label"].lower()) :
                self.ctrl_mode.SetID(dictTemp["ID"])

    def CreerMode(self):
        """ Créer un mode 'Remboursement' """
        # Vérifie si un mode Remboursement n'existe pas déjà
        DB = GestionDB.DB()
        req = """SELECT IDmode, label FROM modes_reglements;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        present = False
        for IDmode, label in listeDonnees :
            if "remboursement" in UTILS_Texte.Supprime_accent(label.lower()) :
                present = True

        if present == True :
            dlg = wx.MessageDialog(self, _(u"Il semblerait qu'un mode 'Remboursement' soit déjà présent.\n\nSouhaitez-vous quand même créer un nouveau mode ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la création d'un mode de règlement 'Remboursement' ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
                ("label", _(u"Remboursement")),
            ]
        IDmode = DB.ReqInsert("modes_reglements", listeDonnees)

        DB.Close()

        # MAJ Contrôle Modes
        self.ctrl_mode.MAJ()
        self.SelectModeRemboursement()

    def OnBoutonModes(self, event):
        IDmode = self.ctrl_mode.GetID()
        import DLG_Modes_reglements
        dlg = DLG_Modes_reglements.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_mode.MAJ()
        self.ctrl_mode.SetID(IDmode)

    def OnBoutonPayeurs(self, event):
        IDpayeur = self.ctrl_payeur.GetID()
        import DLG_Payeurs
        dlg = DLG_Payeurs.Dialog(self, self.IDcompte_payeur)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_payeur.MAJ()
        self.ctrl_payeur.SetID(IDpayeur)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        montant = self.ctrl_montant.GetMontant()
        if montant == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return

        if montant < 0.0 :
            dlg = wx.MessageDialog(self, _(u"Le montant doit obligatoirement être positif !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return

        if self.solde != None and FloatToDecimal(montant) > FloatToDecimal(self.solde) :
            dlg = wx.MessageDialog(self, _(u"Le montant du remboursement ne doit pas être supérieur au solde du compte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return

        IDcompte = self.ctrl_compte.GetID()
        if IDcompte == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_compte.SetFocus()

        IDpayeur = self.ctrl_payeur.GetID()
        if IDpayeur == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un payeur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_payeur.SetFocus()

        IDmode = self.ctrl_mode.GetID()
        if IDmode == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un mode de règlement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_mode.SetFocus()
            return


        observations = self.ctrl_observations.GetValue()

        DB = GestionDB.DB()

        # Récupère IDfamille
        req = """SELECT IDfamille
        FROM comptes_payeurs
        WHERE IDcompte_payeur=%d
        """ % self.IDcompte_payeur
        DB.ExecuterReq(req)
        IDfamille = DB.ResultatReq()[0][0]

        # Enregistrement de la prestation positive
        listeDonnees = [
            ("IDcompte_payeur", self.IDcompte_payeur),
            ("date", str(datetime.date.today())),
            ("categorie", "autre"),
            ("label", _(u"Remboursement")),
            ("montant_initial", montant),
            ("montant", montant),
            ("IDfamille", IDfamille),
            ("date_valeur", str(datetime.date.today())),
            ]
        IDprestation_positive = DB.ReqInsert("prestations", listeDonnees)

        # Ventiler la prestation positive avec l'avoir
        VentilationAuto(self.IDcompte_payeur)


        # Enregistrement de la prestation négative
        listeDonnees = [
            ("IDcompte_payeur", self.IDcompte_payeur),
            ("date", str(datetime.date.today())),
            ("categorie", "autre"),
            ("label", _(u"Remboursement")),
            ("montant_initial", -montant),
            ("montant", -montant),
            ("IDfamille", IDfamille),
            ("date_valeur", str(datetime.date.today())),
            ]
        IDprestation_negative = DB.ReqInsert("prestations", listeDonnees)

        # Enregistrement du règlement négatif
        listeDonnees = [
            ("IDcompte_payeur", self.IDcompte_payeur),
            ("date", str(datetime.date.today())),
            ("IDmode", IDmode),
            ("montant", -montant),
            ("IDpayeur", IDpayeur),
            ("observations", observations),
            ("IDcompte", IDcompte),
            ("date_saisie", str(datetime.date.today())),
            ("IDutilisateur", UTILS_Identification.GetIDutilisateur()),
            ]
        IDreglement = DB.ReqInsert("reglements", listeDonnees)

        # Ventilation de la prestation négative sur le règlement
        listeDonnees = [
            ("IDreglement", IDreglement),
            ("IDcompte_payeur", self.IDcompte_payeur),
            ("IDprestation", IDprestation_negative),
            ("montant", -montant),
            ]
        IDventilation = DB.ReqInsert("ventilation", listeDonnees)

        DB.Close()

        # Fermeture
        self.EndModal(wx.ID_OK)





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcompte_payeur=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
