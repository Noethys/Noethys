#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Data import DATA_Serveurs_fai


class Dialog(wx.Dialog):
    def __init__(self, parent, IDadresse=None):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Saisie d'une adresse Email"))
        self.IDadresse = IDadresse
        self.defaut = False
        
        # Récupération des serveurs prédéfinis
        self.listeServeurs = DATA_Serveurs_fai.LISTE_SERVEURS_FAI
        listeServeursChoices = []
        for fai, smtp, port, auth, startTLS in self.listeServeurs :
            listeServeursChoices.append(fai)
        
        self.static_sizer_adresse_staticbox = wx.StaticBox(self, -1, _(u"Adresse de messagerie"))
        self.static_sizer_serveur_staticbox = wx.StaticBox(self, -1, _(u"Serveur de messagerie"))
        self.label_intro = wx.StaticText(self, -1, _(u"Choisissez le serveur de messagerie dans la liste qui correspond à votre\nadresse de messagerie."))
        self.radio_predefini = wx.RadioButton(self, -1, "")
        self.label_predefini = wx.StaticText(self, -1, _(u"Serveur prédéfini :"))
        self.ctrl_predefinis = wx.Choice(self, -1, choices=listeServeursChoices)
        self.radio_personnalise = wx.RadioButton(self, -1, "")
        self.label_personnalise = wx.StaticText(self, -1, _(u"Serveur personnalisé :"))
        self.label_smtp = wx.StaticText(self, -1, _(u"Serveur SMTP :"))
        self.ctrl_smtp = wx.TextCtrl(self, -1, "")
        self.label_port = wx.StaticText(self, -1, _(u"Numéro de port :"))
        self.ctrl_port = wx.TextCtrl(self, -1, "")
        self.label_authentification  = wx.StaticText(self, -1, _(u"Connexion authentifiée :"))
        self.ctrl_authentification  = wx.CheckBox(self, -1, "")
        self.label_startTLS  = wx.StaticText(self, -1, _(u"startTLS :"))
        self.ctrl_startTLS   = wx.CheckBox(self, -1, "")
        self.label_adresse = wx.StaticText(self, -1, _(u"Adresse d'envoi :"))
        self.ctrl_adresse = wx.TextCtrl(self, -1, "")
        self.label_nom_adresse = wx.StaticText(self, -1, _(u"Nom affiché pour l'adresse d'envoi :"))
        self.ctrl_nom_adresse = wx.TextCtrl(self, -1, "")
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Nom d'utilisateur :"))
        self.ctrl_utilisateur = wx.TextCtrl(self, -1, "")
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.ctrl_mdp.Enable(False)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioServeur, self.radio_predefini )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioServeur, self.radio_personnalise )
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAuthentification, self.ctrl_authentification)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceServeur, self.ctrl_predefinis)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDadresse != None :
            self.Importation() 
        
        self.OnRadioServeur(None) 
        

    def __set_properties(self):
        self.radio_predefini.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un serveur prédéfini dans la liste")))
        self.ctrl_predefinis.SetMinSize((200, -1))
        self.radio_personnalise.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir manuellement les caractéristiques du serveur de messagerie")))
        self.ctrl_smtp.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom du serveur SMPT (exemple : smtp.orange.fr)")))
        self.ctrl_port.SetMinSize((60, -1))
        self.ctrl_port.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numero de port (laissez la case vide pour utiliser le numéro de port par défaut)")))
        self.ctrl_authentification.SetToolTip(wx.ToolTip(_(u"Cliquez ici sur le serveur de messagerie nécessite une authentification")))
        self.ctrl_adresse.SetToolTip(wx.ToolTip(_(u"Saisissez ici votre adresse mail d'envoi")))
        self.ctrl_nom_adresse.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom qui sera affiché pour l'adrese mail d'envoi")))
        self.ctrl_utilisateur.SetToolTip(wx.ToolTip(_(u"Saisissez ici votre nom d'utilisateur (il s'agit parfois de l'adresse d'envoi)")))
        self.ctrl_mdp.SetToolTip(wx.ToolTip(_(u"Saisissez ici le mot de passe s'il s'agit d'une connexion SSL")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALL, 10)

        static_sizer_serveur = wx.StaticBoxSizer(self.static_sizer_serveur_staticbox, wx.VERTICAL)
        grid_sizer_serveur = wx.FlexGridSizer(rows=6, cols=2, vgap=15, hgap=0)
        grid_sizer_serveur.Add(self.radio_predefini, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # Serveur prédéfini
        grid_sizer_predefini = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_predefini.Add(self.label_predefini, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_predefini.Add(self.ctrl_predefinis, 0, wx.EXPAND, 0)
        grid_sizer_predefini.AddGrowableCol(1)
        grid_sizer_serveur.Add(grid_sizer_predefini, 1, wx.EXPAND, 0)

        grid_sizer_serveur.Add(self.radio_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_serveur.Add(self.label_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_serveur.Add((20, 20), 0, wx.EXPAND, 0)

        # Personnalisé
        grid_sizer_personnalise = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_personnalise.Add(self.label_smtp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise.Add(self.ctrl_smtp, 0, wx.EXPAND, 0)
        grid_sizer_personnalise.Add(self.label_port, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise.Add(self.ctrl_port, 0, 0, 0)
        grid_sizer_personnalise.Add(self.label_authentification, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise.Add(self.ctrl_authentification, 0, 0, 0)
        grid_sizer_personnalise.Add(self.label_startTLS, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_personnalise.Add(self.ctrl_startTLS, 0, 0, 0)
        grid_sizer_personnalise.AddGrowableCol(1)
        grid_sizer_serveur.Add(grid_sizer_personnalise, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_serveur.AddGrowableCol(1)
        static_sizer_serveur.Add(grid_sizer_serveur, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer_serveur, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Saisie adresse
        grid_sizer_adresse = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_adresse.Add(self.label_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_nom_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_nom_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_utilisateur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_utilisateur, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)

        static_sizer_adresse = wx.StaticBoxSizer(self.static_sizer_adresse_staticbox, wx.VERTICAL)
        static_sizer_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
    
    def OnRadioServeur(self, event):
        if self.radio_predefini.GetValue() == True :
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
        etatAuth  = False
        if self.radio_predefini.GetValue() == True :
            # Si serveur prédéfini
            selection = self.ctrl_predefinis.GetSelection()
            if selection != -1 :
                etatAuth = self.listeServeurs[selection][3]
                self.ctrl_authentification.SetValue(etatAuth)
                self.ctrl_startTLS.SetValue(self.listeServeurs[selection][4])
        else:
            # Si serveur personnalisé
            etatAuth = self.ctrl_authentification.GetValue()
        self.ctrl_utilisateur.Enable(etatAuth)
        self.ctrl_mdp.Enable(etatAuth)

    def Importation(self):
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur
        FROM adresses_mail WHERE IDadresse=%d; """ % self.IDadresse
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, auth, startTLS, utilisateur = listeDonnees[0]
        
        self.defaut = bool(defaut)
        
        self.ctrl_adresse.SetValue(adresse)
        if nom_adresse != None :
            self.ctrl_nom_adresse.SetValue(nom_adresse)
        if motdepasse != None :
            self.ctrl_mdp.SetValue(motdepasse)

        if utilisateur != None :
            self.ctrl_utilisateur.SetValue(utilisateur)

        # Recherche si les paramètres correspondent à un serveur prédéfini
        index = 0
        indexPredefini = None
        for fai, smtpTmp, portTmp, authTmp, startTLSTmp in self.listeServeurs :
            if smtpTmp == smtp and portTmp == port and authTmp == auth and startTLSTmp == startTLS :
                indexPredefini = index
            index += 1
        
        if indexPredefini != None :
            # Prédéfini :
            self.ctrl_predefinis.SetSelection(indexPredefini)
            self.radio_predefini.SetValue(True)
        else:
            # Serveur personnalisé :
            if smtp != None :
                self.ctrl_smtp.SetValue(smtp)
            if port != None :
                self.ctrl_port.SetValue(str(port))
            if auth != None :
                self.ctrl_authentification.SetValue(auth)
            if startTLS != None :
                self.ctrl_startTLS.SetValue(startTLS)
            self.radio_personnalise.SetValue(True)
        
        self.ActiveCtrlMdp()
        
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
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        if self.radio_predefini.GetValue() == True :
        
            # Validation du serveur prédéfini
            if self.ctrl_predefinis.GetSelection() == -1 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun serveur de messagerie dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Validation du serveur prédéfini
            if self.ctrl_adresse.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une adresse de messagerie."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Validation du mot de passe
            if self.listeServeurs[self.ctrl_predefinis.GetSelection()][3] == True :
                if self.ctrl_mdp.GetValue() == "" :
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le mot de passe de votre messagerie"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

                if self.ctrl_utilisateur.GetValue() == "" :
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le nom d'utilisateur de votre messagerie"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

        else:
            
            if self.ctrl_smtp.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le nom du serveur SMTP"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            if self.ctrl_port.GetValue() != "" :
                try :
                    test = int(self.ctrl_port.GetValue())
                except :
                    dlg = wx.MessageDialog(self, _(u"Le numéro de port que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            
            # Validation du mot de passe
            if self.ctrl_authentification.GetValue() == True :
                if self.ctrl_mdp.GetValue() == "" :
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le mot de passe de votre messagerie"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

                if self.ctrl_utilisateur.GetValue() == "" :
                    dlg = wx.MessageDialog(self, _(u"Vous avez omis de saisir le nom d'utilisateur de votre messagerie"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

        # Sauvegarde
        self.Sauvegarde()
                
        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK)  

    def Sauvegarde(self):
        """ Sauvegarde des données """
        # Récupération des valeurs saisies
        if self.radio_predefini.GetValue() == True :
            
            adresse = self.ctrl_adresse.GetValue()
            if self.ctrl_nom_adresse.GetValue() == "" :
                nom_adresse = None
            else:
                nom_adresse = self.ctrl_nom_adresse.GetValue()
            selection = self.ctrl_predefinis.GetSelection()
            smtp = self.listeServeurs[selection][1]
            port = self.listeServeurs[selection][2]
            auth = self.listeServeurs[selection][3]
            startTLS = self.listeServeurs[selection][4]
            if auth == True :
                motdepasse = self.ctrl_mdp.GetValue()
                utilisateur = self.ctrl_utilisateur.GetValue()
            else:
                motdepasse = None
                utilisateur = None
        
        else:
            
            adresse = self.ctrl_adresse.GetValue()
            if self.ctrl_nom_adresse.GetValue() == "" :
                nom_adresse = None
            else:
                nom_adresse = self.ctrl_nom_adresse.GetValue()
            if self.ctrl_mdp.GetValue() == "" :
                motdepasse = None
                utilisateur = None
            else:
                motdepasse = self.ctrl_mdp.GetValue()
                utilisateur = self.ctrl_utilisateur.GetValue()
            if self.ctrl_smtp.GetValue() == "" :
                smtp = None
            else:
                smtp = self.ctrl_smtp.GetValue()
            if self.ctrl_port.GetValue() == "" :
                port = None
            else:
                port = int(self.ctrl_port.GetValue())
            if self.ctrl_authentification.GetValue() == True :
                auth = 1
            else:
                auth = 0
            if self.ctrl_startTLS.GetValue() == True :
                startTLS = 1
            else :
                startTLS = 0
        
        # Si c'est la première adresse saisie, on la met comme defaut
        nbreAdresses = self.GetNbreAdresses() 
        if nbreAdresses == 0 :
            defaut = True
        else:
            defaut = self.defaut
            
        # Enregistrement des données
        DB = GestionDB.DB()
        listeDonnees = [    ("adresse",   adresse),  
                                    ("nom_adresse",    nom_adresse),
                                    ("motdepasse",    motdepasse),
                                    ("smtp",    smtp),
                                    ("port",    port), 
                                    ("connexionAuthentifiee", auth),
                                    ("startTLS", startTLS),
                                    ("defaut",    defaut),
                                    ("utilisateur", utilisateur),
                                    ]
        if self.IDadresse == None :
            # Enregistrement
            newID = DB.ReqInsert("adresses_mail", listeDonnees)
            ID = newID
        else:
            # Modification
            DB.ReqMAJ("adresses_mail", listeDonnees, "IDadresse", self.IDadresse)
            ID = self.IDadresse
        DB.Commit()
        DB.Close()
        
        return ID
            




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDadresse=None)
    dialog_1.ShowModal()
    app.MainLoop()
