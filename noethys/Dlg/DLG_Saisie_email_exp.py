#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
from Data import DATA_Serveurs_fai
from Dlg import DLG_Messagebox
from Utils import UTILS_Parametres
from Utils import UTILS_Envoi_email
import wx.lib.agw.labelbook as LB
import wx.html as html



class CTRL_Infos(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=32, couleurFond=(255, 255, 255), style=0):
        html.HtmlWindow.__init__(self, parent, -1, style=style)  # , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetLabel(texte)

    def SetLabel(self, texte=""):
        self.SetPage(u"""<BODY><FONT SIZE=2 COLOR='#000000'>%s</FONT></BODY>""" % texte)
        couleurFond = wx.SystemSettings.GetColour(30)
        self.SetBackgroundColour(couleurFond)


class Page_SMTP(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Récupération des serveurs prédéfinis
        self.listeServeurs = DATA_Serveurs_fai.LISTE_SERVEURS_FAI
        listeServeursChoices = []
        for fai, smtp, port, auth, startTLS in self.listeServeurs:
            listeServeursChoices.append(fai)

        self.static_sizer_adresse_staticbox = wx.StaticBox(self, -1, _(u"Adresse de messagerie"))
        self.static_sizer_serveur_staticbox = wx.StaticBox(self, -1, _(u"Serveur de messagerie"))
        self.radio_predefini = wx.RadioButton(self, -1, "")
        self.label_predefini = wx.StaticText(self, -1, _(u"Serveur prédéfini :"))
        self.ctrl_predefinis = wx.Choice(self, -1, choices=listeServeursChoices)
        self.radio_personnalise = wx.RadioButton(self, -1, "")
        self.label_personnalise = wx.StaticText(self, -1, _(u"Serveur personnalisé :"))
        self.label_smtp = wx.StaticText(self, -1, _(u"Serveur SMTP :"))
        self.ctrl_smtp = wx.TextCtrl(self, -1, "")
        self.label_port = wx.StaticText(self, -1, _(u"Numéro de port :"))
        self.ctrl_port = wx.TextCtrl(self, -1, "")
        self.label_authentification = wx.StaticText(self, -1, _(u"Authentification :"))
        self.ctrl_authentification = wx.CheckBox(self, -1, "")
        self.label_startTLS = wx.StaticText(self, -1, _(u"TLS :"))
        self.ctrl_startTLS = wx.CheckBox(self, -1, "")
        self.label_adresse = wx.StaticText(self, -1, _(u"Adresse d'envoi :"))
        self.ctrl_adresse = wx.TextCtrl(self, -1, "")
        self.label_nom_adresse = wx.StaticText(self, -1, _(u"Nom affiché :"))
        self.ctrl_nom_adresse = wx.TextCtrl(self, -1, "")
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Utilisateur :"))
        self.ctrl_utilisateur = wx.TextCtrl(self, -1, "")
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.ctrl_mdp.Enable(False)

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioServeur, self.radio_predefini )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioServeur, self.radio_personnalise )
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAuthentification, self.ctrl_authentification)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceServeur, self.ctrl_predefinis)

        # Properties
        self.radio_predefini.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un serveur prédéfini dans la liste")))
        self.ctrl_predefinis.SetMinSize((350, -1))
        self.radio_personnalise.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir manuellement les caractéristiques du serveur de messagerie")))
        self.ctrl_smtp.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom du serveur SMPT (exemple : smtp.orange.fr)")))
        self.ctrl_port.SetMinSize((60, -1))
        self.ctrl_port.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numéro de port (laissez la case vide pour utiliser le numéro de port par défaut)")))
        self.ctrl_authentification.SetToolTip(wx.ToolTip(_(u"Cliquez ici si le serveur de messagerie nécessite une authentification")))
        self.ctrl_adresse.SetToolTip(wx.ToolTip(_(u"Saisissez ici votre adresse mail d'envoi")))
        self.ctrl_nom_adresse.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom qui sera affiché pour l'adresse mail d'envoi")))
        self.ctrl_utilisateur.SetToolTip(wx.ToolTip(_(u"Saisissez ici votre nom d'utilisateur (il s'agit souvent de l'adresse d'envoi)")))
        self.ctrl_mdp.SetToolTip(wx.ToolTip(_(u"Saisissez ici le mot de passe s'il s'agit d'une connexion authentifiée")))
        self.ctrl_startTLS.SetToolTip(wx.ToolTip(_(u"Cochez cette case si votre messagerie utilise le protocole TLS")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        static_sizer_serveur = wx.StaticBoxSizer(self.static_sizer_serveur_staticbox, wx.VERTICAL)
        grid_sizer_serveur = wx.FlexGridSizer(rows=6, cols=2, vgap=15, hgap=0)
        grid_sizer_serveur.Add(self.radio_predefini, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # Serveur prédéfini
        grid_sizer_predefini = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_predefini.Add(self.label_predefini, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_predefini.Add(self.ctrl_predefinis, 0, wx.EXPAND, 0)
        grid_sizer_predefini.AddGrowableCol(1)
        grid_sizer_serveur.Add(grid_sizer_predefini, 1, wx.EXPAND, 0)

        grid_sizer_serveur.Add(self.radio_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_serveur.Add(self.label_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_serveur.Add((5, 5), 0, wx.EXPAND, 0)

        # Personnalisé
        grid_sizer_personnalise = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_personnalise.Add(self.label_smtp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise.Add(self.ctrl_smtp, 0, wx.EXPAND, 0)
        grid_sizer_personnalise.Add(self.label_port, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_personnalise_2 = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_personnalise_2.Add(self.ctrl_port, 0, 0, 0)
        grid_sizer_personnalise_2.Add((5, 5), 0, 0, 0)
        grid_sizer_personnalise_2.Add(self.label_authentification, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise_2.Add(self.ctrl_authentification, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise_2.Add((5, 5), 0, 0, 0)
        grid_sizer_personnalise_2.Add(self.label_startTLS, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise_2.Add(self.ctrl_startTLS, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise.Add(grid_sizer_personnalise_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_personnalise.AddGrowableCol(1)
        grid_sizer_serveur.Add(grid_sizer_personnalise, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_serveur.AddGrowableCol(1)
        static_sizer_serveur.Add(grid_sizer_serveur, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer_serveur, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Saisie adresse
        grid_sizer_adresse = wx.FlexGridSizer(rows=2, cols=5, vgap=5, hgap=5)
        grid_sizer_adresse.Add(self.label_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_utilisateur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_utilisateur, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_nom_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_nom_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)
        grid_sizer_adresse.AddGrowableCol(4)

        static_sizer_adresse = wx.StaticBoxSizer(self.static_sizer_adresse_staticbox, wx.VERTICAL)
        static_sizer_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()

        # Init controles
        self.radio_predefini.SetValue(True)
        self.OnRadioServeur(None)

    def OnRadioServeur(self, event):
        if self.radio_predefini.GetValue() == True:
            self.ctrl_predefinis.Enable(True)
            self.label_smtp.Enable(False)
            self.label_port.Enable(False)
            self.label_authentification.Enable(False)
            self.label_startTLS.Enable(False)
            self.ctrl_smtp.Enable(False)
            self.ctrl_port.Enable(False)
            self.ctrl_authentification.Enable(False)
            self.ctrl_startTLS.Enable(False)
        else:
            self.ctrl_predefinis.Enable(False)
            self.label_smtp.Enable(True)
            self.label_port.Enable(True)
            self.label_authentification.Enable(True)
            self.label_startTLS.Enable(True)
            self.ctrl_smtp.Enable(True)
            self.ctrl_port.Enable(True)
            self.ctrl_authentification.Enable(True)
            self.ctrl_startTLS.Enable(True)
        self.ActiveCtrlMdp()

    def OnChoiceServeur(self, event):
        self.ActiveCtrlMdp()

    def OnCheckAuthentification(self, event):
        self.ActiveCtrlMdp()

    def ActiveCtrlMdp(self):
        etatAuth = False
        if self.radio_predefini.GetValue() == True:
            # Si serveur prédéfini
            selection = self.ctrl_predefinis.GetSelection()
            if selection != -1:
                etatAuth = self.listeServeurs[selection][3]
                self.ctrl_authentification.SetValue(etatAuth)
                self.ctrl_startTLS.SetValue(self.listeServeurs[selection][4])
        else:
            # Si serveur personnalisé
            etatAuth = self.ctrl_authentification.GetValue()
        self.ctrl_utilisateur.Enable(etatAuth)
        self.ctrl_mdp.Enable(etatAuth)

    def GetDonnees(self):
        # Récupération des valeurs saisies
        if self.radio_predefini.GetValue() == True:

            adresse = self.ctrl_adresse.GetValue()
            if self.ctrl_nom_adresse.GetValue() == "":
                nom_adresse = None
            else:
                nom_adresse = self.ctrl_nom_adresse.GetValue()
            selection = self.ctrl_predefinis.GetSelection()
            smtp = self.listeServeurs[selection][1]
            port = self.listeServeurs[selection][2]
            auth = self.listeServeurs[selection][3]
            startTLS = self.listeServeurs[selection][4]
            if auth == True:
                motdepasse = self.ctrl_mdp.GetValue()
                utilisateur = self.ctrl_utilisateur.GetValue()
            else:
                motdepasse = None
                utilisateur = None

        else:

            adresse = self.ctrl_adresse.GetValue()
            if self.ctrl_nom_adresse.GetValue() == "":
                nom_adresse = None
            else:
                nom_adresse = self.ctrl_nom_adresse.GetValue()
            if self.ctrl_smtp.GetValue() == "":
                smtp = None
            else:
                smtp = self.ctrl_smtp.GetValue()
            if self.ctrl_port.GetValue() == "":
                port = None
            else:
                port = int(self.ctrl_port.GetValue())
            if self.ctrl_authentification.GetValue() == True:
                auth = 1
                motdepasse = self.ctrl_mdp.GetValue()
                utilisateur = self.ctrl_utilisateur.GetValue()
            else:
                auth = 0
                motdepasse = None
                utilisateur = None
            if self.ctrl_startTLS.GetValue() == True:
                startTLS = 1
            else:
                startTLS = 0

        # Renvoie un dict des données
        dict_donnees = {
            "moteur": "smtp", "adresse": adresse, "nom_adresse": nom_adresse, "motdepasse": motdepasse, "smtp": smtp, "port": port,
            "auth": auth, "startTLS": startTLS, "utilisateur": utilisateur, "parametres":None}
        return dict_donnees

    def SetDonnees(self, dictDonnees={}):
        self.ctrl_adresse.SetValue(dictDonnees["adresse"])
        if dictDonnees["nom_adresse"] != None:
            self.ctrl_nom_adresse.SetValue(dictDonnees["nom_adresse"])
        if dictDonnees["motdepasse"] != None:
            self.ctrl_mdp.SetValue(dictDonnees["motdepasse"])

        if dictDonnees["utilisateur"] != None:
            self.ctrl_utilisateur.SetValue(dictDonnees["utilisateur"])

        # Recherche si les paramètres correspondent à un serveur prédéfini
        index = 0
        indexPredefini = None
        for fai, smtpTmp, portTmp, authTmp, startTLSTmp in self.listeServeurs:
            if smtpTmp == dictDonnees["smtp"] and portTmp == dictDonnees["port"] and authTmp == dictDonnees["auth"] and startTLSTmp == dictDonnees["startTLS"]:
                indexPredefini = index
            index += 1

        if indexPredefini != None:
            # Prédéfini :
            self.ctrl_predefinis.SetSelection(indexPredefini)
            self.radio_predefini.SetValue(True)
        else:
            # Serveur personnalisé :
            if dictDonnees["smtp"] != None:
                self.ctrl_smtp.SetValue(dictDonnees["smtp"])
            if dictDonnees["port"] != None:
                self.ctrl_port.SetValue(str(dictDonnees["port"]))
            if dictDonnees["auth"] != None:
                self.ctrl_authentification.SetValue(dictDonnees["auth"])
            if dictDonnees["startTLS"] != None:
                self.ctrl_startTLS.SetValue(dictDonnees["startTLS"])
            self.radio_personnalise.SetValue(True)

        self.OnRadioServeur(None)
        self.ActiveCtrlMdp()

    def Validation(self):
        if self.radio_predefini.GetValue() == True:

            # Validation du serveur prédéfini
            if self.ctrl_predefinis.GetSelection() == -1:
                dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun serveur de messagerie dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Validation du serveur prédéfini
            if self.ctrl_adresse.GetValue() == "":
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une adresse de messagerie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Validation du mot de passe
            if self.listeServeurs[self.ctrl_predefinis.GetSelection()][3] == True:
                if self.ctrl_mdp.GetValue() == "":
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le mot de passe de votre messagerie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

                if self.ctrl_utilisateur.GetValue() == "":
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le nom d'utilisateur de votre messagerie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        else:

            if self.ctrl_smtp.GetValue() == "":
                dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le nom du serveur SMTP !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if self.ctrl_port.GetValue() != "":
                try:
                    test = int(self.ctrl_port.GetValue())
                except:
                    dlg = wx.MessageDialog(self, _(u"Le numéro de port que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

            # Validation du mot de passe
            if self.ctrl_authentification.GetValue() == True:
                if self.ctrl_mdp.GetValue() == "":
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le mot de passe de votre messagerie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

                if self.ctrl_utilisateur.GetValue() == "":
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le nom d'utilisateur de votre messagerie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        return True

# -------------------------------------------------------------------------------------------------

class Page_MAILJET(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.static_sizer_adresse_staticbox = wx.StaticBox(self, -1, _(u"Paramètres Mailjet"))
        self.label_adresse = wx.StaticText(self, -1, _(u"Adresse d'envoi :"))
        self.ctrl_adresse = wx.TextCtrl(self, -1, "")
        self.label_nom_adresse = wx.StaticText(self, -1, _(u"Nom affiché :"))
        self.ctrl_nom_adresse = wx.TextCtrl(self, -1, "")
        self.label_api_key = wx.StaticText(self, -1, _(u"Clé API :"))
        self.ctrl_api_key = wx.TextCtrl(self, -1, "")
        self.label_api_secret = wx.StaticText(self, -1, _(u"Clé secrète :"))
        self.ctrl_api_secret = wx.TextCtrl(self, -1, "")

        self.static_sizer_infos_staticbox = wx.StaticBox(self, -1, _(u"Informations"))
        self.ctrl_infos = CTRL_Infos(self)

        self.ctrl_infos.SetLabel(u"""<FONT SIZE=2><IMG SRC="%s">
        Mailjet est un service d'envoi d'emails que vous pouvez découvrir sur https://fr.mailjet.com.
        Vous pouvez récupérer votre clé API et votre clé secrète sur la page 'Paramètres SMTP' de votre compte Mailjet.
        N'oubliez pas de saisir sur la page 'Domaines et adresses d'expéditeur' de votre compte l'adresse d'expédition que vous renseignez ici.
        """ % Chemins.GetStaticPath(u"Images/16x16/Astuce.png"))

        # Properties
        self.ctrl_adresse.SetToolTip(wx.ToolTip(_(u"Saisissez ici votre adresse mail d'envoi")))
        self.ctrl_nom_adresse.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom qui sera affiché dans le client de messagerie de votre destinataire")))
        self.ctrl_api_key.SetToolTip(wx.ToolTip(_(u"Saisissez ici votre clé API Mailjet")))
        self.ctrl_api_secret.SetToolTip(wx.ToolTip(_(u"Saisissez ici votre clé secrète Mailjet")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        grid_sizer_adresse = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_adresse.Add(self.label_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_nom_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_nom_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_api_key, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_api_key, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_api_secret, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_api_secret, 0, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)

        static_sizer_adresse = wx.StaticBoxSizer(self.static_sizer_adresse_staticbox, wx.VERTICAL)
        static_sizer_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        static_sizer_infos = wx.StaticBoxSizer(self.static_sizer_infos_staticbox, wx.VERTICAL)
        static_sizer_infos.Add(self.ctrl_infos, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer_infos, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()

    def GetDonnees(self):
        # Renvoie un dict des données
        adresse = self.ctrl_adresse.GetValue()
        nom_adresse = self.ctrl_nom_adresse.GetValue()
        api_key = self.ctrl_api_key.GetValue()
        api_secret = self.ctrl_api_secret.GetValue()
        parametres = "api_key==%s##api_secret==%s" % (api_key, api_secret)

        dict_donnees = {
            "moteur": "mailjet", "adresse": adresse, "nom_adresse": nom_adresse, "motdepasse": None, "smtp": None, "port": None,
            "auth": None, "startTLS": None, "utilisateur": None, "parametres":parametres}
        return dict_donnees

    def SetDonnees(self, dictDonnees={}):
        adresse = self.ctrl_adresse.SetValue(dictDonnees.get("adresse", ""))
        nom_adresse = self.ctrl_nom_adresse.SetValue(dictDonnees.get("nom_adresse", ""))
        parametres = dictDonnees.get("parametres", None)
        dict_parametres = {}
        if parametres not in ("", None):
            liste_parametres = parametres.split("##")
            for texte in liste_parametres:
                nom, valeur = texte.split("==")
                dict_parametres[nom] = valeur
        self.ctrl_api_key.SetValue(dict_parametres.get("api_key", ""))
        self.ctrl_api_secret.SetValue(dict_parametres.get("api_secret", ""))

    def Validation(self):
        adresse = self.ctrl_adresse.GetValue()
        nom_adresse = self.ctrl_nom_adresse.GetValue()
        api_key = self.ctrl_api_key.GetValue()
        api_secret = self.ctrl_api_secret.GetValue()

        if adresse == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir l'adresse d'expédition !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if nom_adresse == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir le nom à afficher !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if api_key == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir votre clé API Mailjet !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if api_secret == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir votre clé secrète Mailjet !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        return True

# -------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDadresse=None):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Saisie d'une adresse Email"))
        self.IDadresse = IDadresse
        self.defaut = False

        # Intro
        self.label_intro = wx.StaticText(self, -1, _(u"Sélectionnez un moteur d'envoi (SMTP par défaut) puis renseignez les paramètres obligatoires."))

        # Book
        self.ctrl_labelbook = LB.FlatImageBook(self, -1, agwStyle=LB.INB_LEFT)
        self.InitLabelbook()

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_tester = CTRL_Bouton_image.CTRL(self, texte=_(u"Tester"), cheminImage="Images/32x32/Connexion.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTester, self.bouton_tester)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDadresse != None :
            self.Importation()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à l'aide")))
        self.bouton_tester.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réaliser un test d'envoi d'email")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Intro
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)

        # Book
        grid_sizer_base.Add(self.ctrl_labelbook, 0, wx.ALL|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_tester, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CentreOnScreen()

    def InitLabelbook(self):
        self.listePages = [
            ("smtp", _(u"SMTP"), Page_SMTP(self), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Smtp.png'), wx.BITMAP_TYPE_PNG)),
            ("mailjet", _(u"Mailjet"), Page_MAILJET(self), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Mailjet.png'), wx.BITMAP_TYPE_PNG)),
        ]

        il = wx.ImageList(32, 32)
        index = 0
        for code, label, ctrl, image in self.listePages:
            il.Add(image)
            index += 1
        self.ctrl_labelbook.AssignImageList(il)

        index = 0
        for code, label, ctrl, image in self.listePages:
            self.ctrl_labelbook.AddPage(ctrl, label, imageId=index)
            index += 1

    def GetPage(self, moteur="smtp"):
        for code, label, ctrl, image in self.listePages:
            if code == moteur :
                return ctrl
        return None

    def GetPageActive(self):
        index = self.ctrl_labelbook.GetSelection()
        return self.listePages[index][2]

    def SetPageActive(self, moteur="smtp"):
        index = 0
        for code, label, ctrl, image in self.listePages:
            if code == moteur :
                self.ctrl_labelbook.SetSelection(index)
            index += 1

    def Importation(self):
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, moteur, adresse, nom_adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur, parametres
        FROM adresses_mail WHERE IDadresse=%d; """ % self.IDadresse
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDadresse, moteur, adresse, nom_adresse, motdepasse, smtp, port, defaut, auth, startTLS, utilisateur, parametres = listeDonnees[0]

        if moteur in (None, ""):
            moteur = "smtp"

        dictDonnees = {
            "IDadresse": IDadresse, "moteur": moteur, "adresse": adresse,
            "nom_adresse": nom_adresse, "motdepasse": motdepasse, "smtp": smtp,
            "port": port, "defaut": defaut, "auth": auth,
            "startTLS": startTLS, "utilisateur": utilisateur, "parametres": parametres,
            }

        self.defaut = bool(defaut)

        # Envoie les données vers la page du book
        self.GetPage(moteur=moteur).SetDonnees(dictDonnees=dictDonnees)
        wx.CallAfter(self.SetPageActive, moteur)

        return listeDonnees
    
    def GetNbreAdresses(self):
        """ Récupère le nbre d'adresses déjà saisies """
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur
        FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        return len(listeDonnees)
    
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Adressesdexpditiondemails")

    def OnBoutonTester(self, event):
        if self.GetPageActive().Validation() == False :
            return False

        # Récupération des paramètres
        dict_donnees = self.GetPageActive().GetDonnees()

        # Demande une adresse de destination
        adresse = UTILS_Parametres.Parametres(mode="get", categorie="emails", nom="adresse_test", valeur=u"")
        dlg = wx.TextEntryDialog(self, _(u"Saisissez une adresse Email de destination et cliquez sur Ok :"), _(u"Envoi d'un Email de test"), adresse)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        adresse = dlg.GetValue()
        dlg.Destroy()
        # Mémorise l'adresse saisie
        if UTILS_Envoi_email.ValidationEmail(adresse) == False :
            dlg = wx.MessageDialog(self, _(u"L'adresse saisie n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        UTILS_Parametres.Parametres(mode="set", categorie="emails", nom="adresse_test", valeur=adresse)

        # Création du message de test
        message = UTILS_Envoi_email.Message(
            destinataires=[adresse, ],
            sujet=u"Test de messagerie",
            texte_html=u"<p>Ceci est un <b>test de messagerie</b> envoyé à %s.</p>" % datetime.datetime.now().strftime("%H:%M:%S"),
        )

        try :
            messagerie = UTILS_Envoi_email.Messagerie(
                backend=dict_donnees["moteur"],
                hote=dict_donnees["smtp"],
                port=dict_donnees["port"],
                utilisateur=dict_donnees["utilisateur"],
                motdepasse=dict_donnees["motdepasse"],
                email_exp=dict_donnees["adresse"],
                nom_exp=dict_donnees["nom_adresse"],
                timeout=10,
                use_tls=dict_donnees["startTLS"],
                parametres=dict_donnees["parametres"],
            )
            messagerie.Connecter()
            messagerie.Envoyer(message)
            messagerie.Fermer()
        except Exception, err:
            err = str(err).decode("iso-8859-15")
            intro = _(u"L'envoi de l'email de test est impossible :")
            conclusion = _(u"Vérifiez votre connexion internet ou les paramètres de votre adresse d'expédition.")
            dlgErreur = DLG_Messagebox.Dialog(self, titre=_(u"Erreur"), introduction=intro, detail=err, conclusion=conclusion, icone=wx.ICON_ERROR, boutons=[_(u"Ok"),])
            dlgErreur.ShowModal()
            dlgErreur.Destroy()
            return False

        dlg = wx.MessageDialog(self, _(u"L'email de test a été envoyé avec succès."), _(u"Test de connexion"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        if self.GetPageActive().Validation() == False :
            return False

        # Sauvegarde
        self.Sauvegarde()
                
        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK)  

    def Sauvegarde(self):
        """ Sauvegarde des données """
        # Récupération des données
        dict_donnees = self.GetPageActive().GetDonnees()

        # Si c'est la première adresse saisie, on la met comme defaut
        nbreAdresses = self.GetNbreAdresses()
        if nbreAdresses == 0 :
            defaut = True
        else:
            defaut = self.defaut

        # Enregistrement des données
        DB = GestionDB.DB()
        listeDonnees = [
            ("adresse", dict_donnees["adresse"]),
            ("nom_adresse", dict_donnees["nom_adresse"]),
            ("motdepasse", dict_donnees["motdepasse"]),
            ("smtp", dict_donnees["smtp"]),
            ("port", dict_donnees["port"]),
            ("connexionAuthentifiee", dict_donnees["auth"]),
            ("startTLS", dict_donnees["startTLS"]),
            ("utilisateur", dict_donnees["utilisateur"]),
            ("moteur", dict_donnees["moteur"]),
            ("parametres", dict_donnees["parametres"]),
            ("defaut", defaut),
        ]
        if self.IDadresse == None :
            # Enregistrement
            self.IDadresse = DB.ReqInsert("adresses_mail", listeDonnees)
        else:
            # Modification
            DB.ReqMAJ("adresses_mail", listeDonnees, "IDadresse", self.IDadresse)
        DB.Commit()
        DB.Close()

    def GetIDadresse(self):
        return self.IDadresse



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDadresse=None)
    dialog_1.ShowModal()
    app.MainLoop()
