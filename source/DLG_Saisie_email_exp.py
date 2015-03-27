#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import DATA_Serveurs_fai


class Dialog(wx.Dialog):
    def __init__(self, parent, IDadresse=None):
        wx.Dialog.__init__(self, parent, -1, title=u"Saisie d'une adresse Email")
        self.IDadresse = IDadresse
        self.defaut = False
        
        # R�cup�ration des serveurs pr�d�finis
        self.listeServeurs = DATA_Serveurs_fai.LISTE_SERVEURS_FAI
        listeServeursChoices = []
        for fai, smtp, port, ssl in self.listeServeurs :
            listeServeursChoices.append(fai)
        
        self.static_sizer_adresse_staticbox = wx.StaticBox(self, -1, u"Adresse de messagerie")
        self.static_sizer_serveur_staticbox = wx.StaticBox(self, -1, u"Serveur de messagerie")
        self.label_intro = wx.StaticText(self, -1, u"Choisissez le serveur de messagerie dans la liste qui correspond � votre\nadresse de messagerie.")
        self.radio_predefini = wx.RadioButton(self, -1, "")
        self.label_predefini = wx.StaticText(self, -1, u"Serveur pr�d�fini :")
        self.ctrl_predefinis = wx.Choice(self, -1, choices=listeServeursChoices)
        self.radio_personnalise = wx.RadioButton(self, -1, "")
        self.label_personnalise = wx.StaticText(self, -1, u"Serveur personnalis� :")
        self.label_smtp = wx.StaticText(self, -1, u"Serveur SMTP :")
        self.ctrl_smtp = wx.TextCtrl(self, -1, "")
        self.label_port = wx.StaticText(self, -1, u"Num�ro de port :")
        self.ctrl_port = wx.TextCtrl(self, -1, "")
        self.label_authentification = wx.StaticText(self, -1, u"Connexion authentifiee :")
        self.ctrl_authentification = wx.CheckBox(self, -1, "")
        self.label_startTLS = wx.StaticText(self, -1, u"startTLS :")
        self.ctrl_startTLS = wx.CheckBox(self, -1, "")
        self.label_adresse = wx.StaticText(self, -1, u"Adresse :")
        self.ctrl_adresse = wx.TextCtrl(self, -1, "")
        self.label_mdp = wx.StaticText(self, -1, u"Mot de passe :")
        self.ctrl_mdp = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.ctrl_mdp.Enable(False)
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioServeur, self.radio_predefini )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioServeur, self.radio_personnalise )
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAuthentification, self.ctrl_authentification)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAuthentification, self.ctrl_authentification)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceServeur, self.ctrl_predefinis)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDadresse != None :
            self.Importation() 
        
        self.OnRadioServeur(None) 
        

    def __set_properties(self):
        self.radio_predefini.SetToolTipString(u"Cliquez ici pour s�lectionner un serveur pr�d�fini dans la liste")
        self.ctrl_predefinis.SetMinSize((200, -1))
        self.radio_personnalise.SetToolTipString(u"Cliquez ici pour saisir manuellement les caract�ristiques du serveur de messagerie")
        self.ctrl_smtp.SetToolTipString(u"Saisissez ici le nom du serveur SMPT (exemple : smtp.orange.fr)")
        self.ctrl_port.SetMinSize((60, -1))
        self.ctrl_port.SetToolTipString(u"Saisissez ici le numero de port (laissez la case vide pour utiliser le num�ro de port par d�faut)")
        self.ctrl_authentification.SetToolTipString(u"Cliquez ici sur le serveur de messagerie n�cessite une authentification")
        self.ctrl_adresse.SetToolTipString(u"Saisissez ici votre adresse mail")
        self.ctrl_mdp.SetToolTipString(u"Saisissez ici le mot de passe s'il s'agit d'une connexion SSL")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour acc�der � l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler la saisie")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        static_sizer_adresse = wx.StaticBoxSizer(self.static_sizer_adresse_staticbox, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        static_sizer_serveur = wx.StaticBoxSizer(self.static_sizer_serveur_staticbox, wx.VERTICAL)
        grid_sizer_serveur = wx.FlexGridSizer(rows=6, cols=2, vgap=15, hgap=0)
        grid_sizer_personnalise = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_predefini = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALL, 10)
        grid_sizer_serveur.Add(self.radio_predefini, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_predefini.Add(self.label_predefini, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_predefini.Add(self.ctrl_predefinis, 0, wx.EXPAND, 0)
        grid_sizer_predefini.AddGrowableCol(1)
        grid_sizer_serveur.Add(grid_sizer_predefini, 1, wx.EXPAND, 0)
        grid_sizer_serveur.Add(self.radio_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_serveur.Add(self.label_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_serveur.Add((20, 20), 0, wx.EXPAND, 0)
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
        grid_sizer_adresse.Add(self.label_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)
        static_sizer_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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
        etat = False
        if self.radio_predefini.GetValue() == True :
            # Si serveur pr�d�fini
            selection = self.ctrl_predefinis.GetSelection()
            if selection != -1 :
                ssl = self.listeServeurs[selection][3]
                if ssl == True :
                    etat = True
        else:
            # Si serveur personnalis�
            if self.ctrl_authentification.GetValue() == True :
                etat = True
        self.ctrl_mdp.Enable(etat)

    def Importation(self):
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS
        FROM adresses_mail WHERE IDadresse=%d; """ % self.IDadresse
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDadresse, adresse, motdepasse, smtp, port, defaut, auth, startTLS = listeDonnees[0]
        
        self.defaut = bool(defaut)
        
        self.ctrl_adresse.SetValue(adresse)
        if motdepasse != None :
            self.ctrl_mdp.SetValue(motdepasse)
        
        # Recherche si les param�tres correspondent � un serveur pr�d�fini
        index = 0
        indexPredefini = None
        for fai, smtpTmp, portTmp, sslTmp in self.listeServeurs :
            if smtpTmp == smtp and portTmp == port and sslTmp == auth :
                indexPredefini = index
            index += 1
        
        if indexPredefini != None :
            # Pr�d�fini :
            self.ctrl_predefinis.SetSelection(indexPredefini)
            self.radio_predefini.SetValue(True)
        else:
            # Serveur personnalis� :
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
        """ R�cup�re le nbre d'adresses d�j� saisies """
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, motdepasse, smtp, port, defaut, connexionssl
        FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        return len(listeDonnees)
    
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Adressesdexpditiondemails")
        
    def OnBoutonOk(self, event):
        """ Validation des donn�es saisies """
        if self.radio_predefini.GetValue() == True :
        
            # Validation du serveur pr�d�fini
            if self.ctrl_predefinis.GetSelection() == -1 :
                dlg = wx.MessageDialog(self, u"Vous n'avez s�lectionn� aucun serveur de messagerie dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Validation du serveur pr�d�fini
            if self.ctrl_adresse.GetValue() == "" :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une adresse de messagerie.", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Validation du mot de passe
            if self.listeServeurs[self.ctrl_predefinis.GetSelection()][3] == True :
                if self.ctrl_mdp.GetValue() == "" :
                    dlg = wx.MessageDialog(self, u"Vous n'avez omis de saisir le mot de passe de votre messagerie", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
        
        else:
            
            if self.ctrl_smtp.GetValue() == "" :
                dlg = wx.MessageDialog(self, u"Vous n'avez omis de saisir le nom du serveur SMTP", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            if self.ctrl_port.GetValue() != "" :
                try :
                    test = int(self.ctrl_port.GetValue())
                except :
                    dlg = wx.MessageDialog(self, u"Le num�ro de port que vous avez saisi n'est pas valide.", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            
            # Validation du mot de passe
            if self.ctrl_authentification.GetValue() == True :
                if self.ctrl_mdp.GetValue() == "" :
                    dlg = wx.MessageDialog(self, u"Vous n'avez omis de saisir le mot de passe de votre messagerie", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
        
        # Sauvegarde
        self.Sauvegarde()
                
        # Ferme la bo�te de dialogue
        self.EndModal(wx.ID_OK)  

    def Sauvegarde(self):
        """ Sauvegarde des donn�es """
        # R�cup�ration des valeurs saisies
        if self.radio_predefini.GetValue() == True :
            
            adresse = self.ctrl_adresse.GetValue()
            selection = self.ctrl_predefinis.GetSelection()
            smtp = self.listeServeurs[selection][1]
            port = self.listeServeurs[selection][2]
            auth = self.listeServeurs[selection][3]
            if auth == True :
                motdepasse = self.ctrl_mdp.GetValue()
            else:
                motdepasse = None
        
        else:
            
            adresse = self.ctrl_adresse.GetValue()
            if self.ctrl_mdp.GetValue() == "" :
                motdepasse = None
            else:
                motdepasse = self.ctrl_mdp.GetValue()
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
            else:
                startTLS = 0

        # Si c'est la premi�re adresse saisie, on la met comme defaut
        nbreAdresses = self.GetNbreAdresses() 
        if nbreAdresses == 0 :
            defaut = True
        else:
            defaut = self.defaut
            
        # Enregistrement des donn�es
        DB = GestionDB.DB()
        listeDonnees = [    ("adresse",   adresse),  
                                    ("motdepasse",    motdepasse),
                                    ("smtp",    smtp),
                                    ("port",    port), 
                                    ("connexionssl",    auth),
                                    ("defaut",    defaut),
                                    ("connexionAuthentifiee", auth),
                                    ("startTLS", startTLS)
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
