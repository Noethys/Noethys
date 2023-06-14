#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
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
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
import GestionDB
from Utils import UTILS_Internet
from Utils import UTILS_Parametres



class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, IDutilisateur=None, mode_virtuel=False):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDutilisateur = IDutilisateur
        self.mode_virtuel = mode_virtuel
        self.dictDonneesInitiales = {}

        # Bandeau
        intro = _(u"Sélectionnez les paramètres du compte internet.")
        titre = _(u"Paramètres du compte internet")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Connecthys.png")
        
        # Activation
        self.box_activation_staticbox = wx.StaticBox(self, -1, _(u"Activation"))
        self.label_activation = wx.StaticText(self, -1, _(u"Compte activé :"))
        self.radio_activation_oui = wx.RadioButton(self, -1, _(u"Oui"), style=wx.RB_GROUP)
        self.radio_activation_non = wx.RadioButton(self, -1, _(u"Non"))
                
        # Codes
        self.box_codes_staticbox = wx.StaticBox(self, -1, _(u"Codes d'accès"))

        self.label_identifiant = wx.StaticText(self, -1, _(u"Identifiant :"))
        self.ctrl_identifiant = wx.TextCtrl(self, -1, "")
        self.bouton_identifiant_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_identifiant_regenerer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_ANY))

        self.ctrl_identifiant.SetMinSize((200, -1))
        self.ctrl_identifiant.Enable(False)

        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, "")
        self.bouton_mdp_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_mdp_regenerer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_mdp.Enable(False)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.ActiveIdentifiant, self.bouton_identifiant_modifier)
        self.Bind(wx.EVT_BUTTON, self.ActiveMdp, self.bouton_mdp_modifier)
        self.Bind(wx.EVT_BUTTON, self.RegenererIdentifiant, self.bouton_identifiant_regenerer)
        self.Bind(wx.EVT_BUTTON, self.RegenererMdp, self.bouton_mdp_regenerer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.radio_activation_non.SetValue(True)
        if self.mode_virtuel == False :
            self.Importation()

    def __set_properties(self):
        self.radio_activation_oui.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour activer le compte internet")))
        self.radio_activation_non.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour désactiver le compte internet")))
        self.bouton_identifiant_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour autoriser la modification manuelle de l'identifiant")))
        self.bouton_mdp_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour autoriser la modification manuelle du mot de passe")))
        self.bouton_identifiant_regenerer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour régénérer automatiquement un nouvel identifiant")))
        self.bouton_mdp_regenerer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour régénérer automatiquement un nouveau mot de passe")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Activation
        box_activation = wx.StaticBoxSizer(self.box_activation_staticbox, wx.VERTICAL)
        grid_sizer_activation = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_activation.Add(self.label_activation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_activation.Add(self.radio_activation_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_activation.Add(self.radio_activation_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_activation.Add(grid_sizer_activation, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_activation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
                
        # Codes
        box_codes = wx.StaticBoxSizer(self.box_codes_staticbox, wx.VERTICAL)
        grid_sizer_codes = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)

        grid_sizer_codes.Add(self.label_identifiant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identifiant = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_identifiant.Add(self.ctrl_identifiant, 0,wx.EXPAND, 0)
        grid_sizer_identifiant.Add(self.bouton_identifiant_modifier, 0,wx.EXPAND, 0)
        grid_sizer_identifiant.Add(self.bouton_identifiant_regenerer, 0,wx.EXPAND, 0)
        grid_sizer_identifiant.AddGrowableCol(0)
        grid_sizer_codes.Add(grid_sizer_identifiant, 0,wx.EXPAND, 0)

        grid_sizer_codes.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mdp = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_mdp.Add(self.ctrl_mdp, 0,wx.EXPAND, 0)
        grid_sizer_mdp.Add(self.bouton_mdp_modifier, 0,wx.EXPAND, 0)
        grid_sizer_mdp.Add(self.bouton_mdp_regenerer, 0,wx.EXPAND, 0)
        grid_sizer_mdp.AddGrowableCol(0)
        grid_sizer_codes.Add(grid_sizer_mdp, 0,wx.EXPAND, 0)

        grid_sizer_codes.AddGrowableCol(1)
        box_codes.Add(grid_sizer_codes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_codes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Factures1")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def ActiveIdentifiant(self, event):
        self.ctrl_identifiant.Enable(True)
        self.ctrl_identifiant.SetFocus()

    def ActiveMdp(self, event):
        if "********" in self.ctrl_mdp.GetValue():
            dlg = wx.MessageDialog(self, _(u"Attention, ce mot de passe a déjà été personnalisé par l'usager ! \n\nSouhaitez-vous vraiment modifier ce mot de passe ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

            self.ctrl_mdp.SetValue("")

        self.ctrl_mdp.Enable(True)
        self.ctrl_mdp.SetFocus()

    def RegenererIdentifiant(self, event):
        dlg = wx.MessageDialog(self, _(u"Vous êtes vraiment sûr de vouloir générer un nouvel identifiant ?"), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES:
            return False

        internet_identifiant = UTILS_Internet.CreationIdentifiant(IDfamille=self.IDfamille, IDutilisateur=self.IDutilisateur)
        self.ctrl_identifiant.SetValue(internet_identifiant)

    def RegenererMdp(self, event):
        if "********" in self.ctrl_mdp.GetValue():
            dlg = wx.MessageDialog(self, _(u"Attention, ce mot de passe a déjà été personnalisé par l'usager ! \n\nSouhaitez-vous vraiment modifier ce mot de passe ?"), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return False

        dlg = wx.MessageDialog(self, _(u"Vous êtes vraiment sûr de vouloir générer un nouveau mot de passe ?"), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES:
            return False

        taille = UTILS_Parametres.Parametres(mode="get", categorie="comptes_internet", nom="taille_passwords", valeur=8)
        internet_mdp = UTILS_Internet.CreationMDP(nbreCaract=taille, cryptage=False)
        self.ctrl_mdp.SetValue(internet_mdp)

    def Importation(self):
        """ Importation des données """
        if self.IDfamille == None and self.IDutilisateur == None :
            return

        DB = GestionDB.DB()
        if self.IDfamille != None :
            req = """SELECT internet_actif, internet_identifiant, internet_mdp
            FROM familles
            WHERE IDfamille=%d;""" % self.IDfamille
        if self.IDutilisateur != None :
            req = """SELECT internet_actif, internet_identifiant, internet_mdp
            FROM utilisateurs
            WHERE IDutilisateur=%d;""" % self.IDutilisateur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        internet_actif, internet_identifiant, internet_mdp = listeDonnees[0]
        self.dictDonneesInitiales = {"internet_actif" : internet_actif, "internet_identifiant" : internet_identifiant, "internet_mdp" : internet_mdp}
        self.MAJ()

    def MAJ(self):
        if self.dictDonneesInitiales["internet_actif"] == 1:
            self.radio_activation_oui.SetValue(True)
        if self.dictDonneesInitiales["internet_identifiant"] != None :
            self.ctrl_identifiant.SetValue(self.dictDonneesInitiales["internet_identifiant"])
        if self.dictDonneesInitiales["internet_mdp"] != None :
            internet_mdp = self.dictDonneesInitiales["internet_mdp"]
            if internet_mdp.startswith("custom"):
                internet_mdp = "********"
            if internet_mdp.startswith("#@#"):
                internet_mdp = UTILS_Internet.DecrypteMDP(internet_mdp)
            self.ctrl_mdp.SetValue(internet_mdp)

    def OnBoutonOk(self, event):
        dictDonnees = self.GetDonnees()

        # Validation
        if len(dictDonnees["internet_identifiant"]) < 7 and dictDonnees["internet_identifiant"] != "demo" :
            dlg = wx.MessageDialog(self, _(u"L'identifiant est vraiment court.\n\nSouhaitez-vous tout de même le valider ?"), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return False

        if len(dictDonnees["internet_mdp"]) < 7 and dictDonnees["internet_mdp"] != "demo" :
            dlg = wx.MessageDialog(self, _(u"Le mot de passe est vraiment court.\n\nSouhaitez-vous tout de même le valider ?"), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return False

        # Vérifie que l'identifiant n'a pas déjà été attribué à un autre utilisateur ou une autre famille
        DB = GestionDB.DB()
        if self.IDfamille != None :
            req = u"""SELECT IDfamille, internet_identifiant
            FROM familles
            WHERE internet_identifiant='%s' AND IDfamille<>%d;""" % (dictDonnees["internet_identifiant"], self.IDfamille)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Cet identifiant a déjà été attribué à %d famille(s) !") % len(listeDonnees), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        if self.IDutilisateur != None :
            req = u"""SELECT IDutilisateur, internet_identifiant
            FROM utilisateurs
            WHERE internet_identifiant='%s' AND IDutilisateur<>%d;""" % (dictDonnees["internet_identifiant"], self.IDutilisateur)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Cet identifiant a déjà été attribué à %d utilisateur(s) !") % len(listeDonnees), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Cryptage du mot de passe
        internet_mdp = dictDonnees["internet_mdp"]
        # if not internet_mdp.startswith("custom") and not internet_mdp.startswith("#@#"):
        #     internet_mdp = UTILS_Internet.CrypteMDP(internet_mdp)

        # Sauvegarde
        if self.mode_virtuel == False :
            DB = GestionDB.DB()
            listeDonnees = [
                ("internet_actif", dictDonnees["internet_actif"]),
                ("internet_identifiant", dictDonnees["internet_identifiant"]),
                ("internet_mdp", internet_mdp),
            ]

            if self.IDfamille != None :
                DB.ReqMAJ("familles", listeDonnees, "IDfamille", self.IDfamille)
            if self.IDutilisateur != None :
                DB.ReqMAJ("utilisateurs", listeDonnees, "IDutilisateur", self.IDutilisateur)
            DB.Close()

        # Fermeture
        self.EndModal(wx.ID_OK)

    def SetDonnees(self, dictDonnees={}):
        self.dictDonneesInitiales = dictDonnees
        self.MAJ()

    def GetDonnees(self):
        dictDonnees = {}
        if self.radio_activation_oui.GetValue() == True :
            dictDonnees["internet_actif"] = 1
        else :
            dictDonnees["internet_actif"] = 0
        dictDonnees["internet_identifiant"] = self.ctrl_identifiant.GetValue()
        if self.ctrl_mdp.GetValue() == "********" :
            dictDonnees["internet_mdp"] = self.dictDonneesInitiales["internet_mdp"]
        else :
            dictDonnees["internet_mdp"] = self.ctrl_mdp.GetValue()
        return dictDonnees



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=1, IDutilisateur=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
