#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB

LISTE_SUFFIXES = ("data", "photos", "documents")


class Dialog(wx.Dialog):
    def __init__(self, parent,  nomUtilisateur="", nomHote="", nomBase=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      

        self.nomUtilisateur = nomUtilisateur
        self.nomHote = nomHote
        self.nomBase = nomBase
        
        # Nom Utilisateur
        self.sizer_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de l'utilisateur"))
        self.label_nom = wx.StaticText(self, -1, "Nom :")
        self.ctrl_nom = wx.TextCtrl(self, -1, self.nomUtilisateur)
        
        # Mot de passe
        self.sizer_mdp_staticbox = wx.StaticBox(self, -1, _(u"Mot de passe"))
        self.label_mdp_1 = wx.StaticText(self, -1, "Mot de passe :")
        self.ctrl_mdp_1 = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.label_mdp_2 = wx.StaticText(self, -1, "Confirmation :")
        self.ctrl_mdp_2 = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        
        # Hotes utilisateur
        self.sizer_hotes_staticbox = wx.StaticBox(self, -1, _(u"Hôtes de connexion"))
        self.radio_1 = wx.RadioButton(self, -1, _(u"Connexion depuis n'importe quel hôte (recommandé)"), style=wx.RB_GROUP)
        self.radio_2 = wx.RadioButton(self, -1, _(u"Connexion uniquement depuis le serveur principal"))
        self.radio_3 = wx.RadioButton(self, -1, _(u"Connexion uniquement depuis l'hôte suivant :"))
        self.ctrl_hote = wx.TextCtrl(self, -1, "")
        
        # Autorisation d'accès au fichier
        self.sizer_autorisation_staticbox = wx.StaticBox(self, -1, _(u"Autorisation d'accès au fichier '%s'") % self.nomBase)
        self.ctrl_autorisation = wx.CheckBox(self, -1, _(u"Cet utilisateur est autorisé à se connecter au fichier"))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioHotes, self.radio_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioHotes, self.radio_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioHotes, self.radio_3)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Si Modification -> importation des données
        if self.nomUtilisateur == "" :
            self.mode = "creation"
            self.SetTitle(_(u"Création d'un utilisateur réseau"))
        else:
            self.mode = "modification"
            self.SetTitle(_(u"Modification d'un utilisateur réseau"))
        
        # Importation
        if self.nomHote == "%" or self.nomHote == "" : 
            self.radio_1.SetValue(True)
            self.ctrl_hote.Enable(False)
        elif self.nomHote == "localhost" : 
            self.radio_2.SetValue(True)
            self.ctrl_hote.Enable(False)
        else : 
            self.radio_3.SetValue(True)
            self.ctrl_hote.SetValue(self.nomHote)
        
        # Recherche l'autorisation d'accès au fichier
        self.ctrl_autorisation.SetValue(self.RechercheAutorisation())


    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici un nom pour l'utilisateur. \nIl est fortement conseillé de n'inclure aucun caractères spéciaux (accents, symboles...)"))
        self.radio_1.SetToolTipString(_(u"L'utilisateur ne peut se connecter à la base de données\n qu'à partir du serveur sur lequel se trouve la base de données."))
        self.radio_2.SetToolTipString(_(u"L'utilisateur ne peut se connecter à la base de données\n qu'à partir des ordinateurs dont les adresses locales ou\n distantes sont cochées dans la liste suivante."))
        self.radio_3.SetToolTipString(_(u"L'utilisateur ne peut se connecter à la base de données\n qu'à partir des ordinateurs dont les adresses locales ou\n distantes sont cochées dans la liste suivante."))
        self.ctrl_mdp_1.SetToolTipString(_(u"Saisissez un mot de passe pour cet utilisateur"))
        self.ctrl_mdp_2.SetToolTipString(_(u"Confirmez le mot de passe en le tapant une seconde fois..."))
        self.ctrl_autorisation.SetToolTipString(_(u"Cochez cette case pour autoriser l'utilisateur à se connecter \nau fichier à partir de l'hôte indiqué ci-dessus."))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Nom Utilisateur
        sizer_nom = wx.StaticBoxSizer(self.sizer_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        sizer_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_nom, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Mots de passe
        sizer_mdp = wx.StaticBoxSizer(self.sizer_mdp_staticbox, wx.VERTICAL)
        grid_sizer_mdp = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_mdp.Add(self.label_mdp_1, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mdp.Add(self.ctrl_mdp_1, 0, wx.EXPAND, 0)
        grid_sizer_mdp.Add(self.label_mdp_2, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mdp.Add(self.ctrl_mdp_2, 0, wx.EXPAND, 0)
        grid_sizer_mdp.AddGrowableCol(1)
        sizer_mdp.Add(grid_sizer_mdp, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_mdp, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Hotes de l'utilisateur
        sizer_hotes = wx.StaticBoxSizer(self.sizer_hotes_staticbox, wx.VERTICAL)
        grid_sizer_hotes = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=5)
        grid_sizer_hotes.Add(self.radio_1, 0, 0, 0)
        grid_sizer_hotes.Add( (5, 5), 0, 0, 0)
        grid_sizer_hotes.Add(self.radio_2, 0, 0, 0)
        grid_sizer_hotes.Add( (5, 5), 0, 0, 0)
        grid_sizer_hotes.Add(self.radio_3, 0, 0, 0)
        grid_sizer_hotes.Add( (5, 5), 0, 0, 0)
        grid_sizer_hotes.Add(self.ctrl_hote, 1, wx.LEFT|wx.EXPAND, 20)
        
        grid_sizer_hotes.AddGrowableRow(2)
        grid_sizer_hotes.AddGrowableCol(0)
        sizer_hotes.Add(grid_sizer_hotes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_hotes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Autorisations
        sizer_autorisation = wx.StaticBoxSizer(self.sizer_autorisation_staticbox, wx.VERTICAL)
        grid_sizer_autorisation = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_autorisation.Add(self.ctrl_autorisation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_autorisation.Add(grid_sizer_autorisation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_autorisation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons de commande
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        # Finalisation
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()


    def RechercheAutorisation(self):
        # Recherche l'autorisation d'accès au fichier
        if self.radio_1.GetValue() == True : hote = "%"
        if self.radio_2.GetValue() == True : hote = "localhost"
        if self.radio_3.GetValue() == True : hote = self.ctrl_hote.GetValue()
        DB = GestionDB.DB()
        DB.ExecuterReq("USE mysql;")
        req = "SELECT host, db, user FROM db WHERE user='%s' and db='%s' and host='%s';" % (self.nomUtilisateur, u"%s_data" % self.nomBase, hote)
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        if len(donnees) > 0 :
            return True
        else:
            return False
        
    def OnRadioHotes(self, event):
        if self.radio_1.GetValue() == True or self.radio_2.GetValue() == True :
            self.ctrl_hote.Enable(False)
        else:
            self.ctrl_hote.Enable(True)
        # Fixe l'autorisation
        self.ctrl_autorisation.SetValue(self.RechercheAutorisation())

    def Importation_hotes(self):
        """ Importation des hotes de la base """       
        DB = GestionDB.DB()
        
        # Recherche des autorisations pour la base en cours
        req = "SELECT Host FROM `mysql`.`db` WHERE Db='%s' AND User='%s';" % (u"%s_data" % self.nomBase, self.nomUtilisateur)
        DB.ExecuterReq(req)
        listeAutorisations = DB.ResultatReq()

        # Recherche des Hotes
        req = "SELECT Host, User, Password FROM `mysql`.`user` WHERE User='%s' ORDER BY Host;" % self.nomUtilisateur
        DB.ExecuterReq(req)
        listeHotesTmp = DB.ResultatReq()
        DB.Close()
        
        listeHotesLabels = []
        listeHotesData = []
        for host, user, password in listeHotesTmp :
            # Recherche s'il y a une autorisation pour la base en cours
            if (host,) in listeAutorisations :
                autorisation = True
            else:
                autorisation = False
            listeHotesData.append((host, autorisation))
            listeHotesLabels.append(host)

        return listeHotesLabels, listeHotesData

    def RemplissageCtrlHotes(self):
        self.ctrl_hote.Set(self.listeHotesLabels)
        index = 0
        for hote, autorisation in self.listeHotesData:
            if autorisation == True :
                self.ctrl_hote.Check(index)
            index += 1
        
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Accsrseau")

    def OnBoutonOk(self, event):

        # Vérification des données saisies
        textNom = self.ctrl_nom.GetValue()
        if textNom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement donner un nom pour cet utilisateur !"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        # Vérification des caractères spéciaux du nom
        erreur = False
        for caract in textNom :
            if caract in u"ïîôûëê~&é(-è_çà)=~#{[|`\^@]}" :
                erreur = True
        if erreur == True :
            dlg = wx.MessageDialog(self, _(u"Le nom d'utilisateur ne devrait pas inclure de caractères spéciaux (accents, symboles...)"), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        # Vérification du mot de passe
        mdp1 = self.ctrl_mdp_1.GetValue()
        mdp2 = self.ctrl_mdp_2.GetValue()
        if mdp1 != mdp2 :
            dlg = wx.MessageDialog(self, _(u"Le mot de passe ne correspond pas à la confirmation."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Si pas de mot de passe
        if mdp1 == "" :
            txtMessage = unicode(_(u"Attention, vous n'avez saisi aucun mot de passe pour cet utilisateur.\nCela peut être risqué pour la sécurité des données.\n\nVoulez-vous quand même valider la création de cet utilisateur sans mot de passe ?\n\n(Cliquez sur Non ou sur Annuler pour saisir un mot de de passe)"))
            dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL :
                return
        
        # Vérification qu'un hôte spécifique a été saisi
        textHote = self.ctrl_hote.GetValue()
        if textHote == "" and self.radio_3.GetValue() == True :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un hote spécifique"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_hote.SetFocus()
            return
        
        # Procédure d'enregistrement des données
        resultat = self.Sauvegarde()
        if resultat == False:
            return
        
        # MàJ du listCtrl du panel de configuration
        self.parent.listCtrl.MAJListeCtrl()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

            
            
    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """ 
        DB = GestionDB.DB()
        DB.ExecuterReq("USE mysql;")
        
        nom = self.ctrl_nom.GetValue()
        motdepasse = self.ctrl_mdp_1.GetValue()
        if self.radio_1.GetValue() == True : hote = "%"
        if self.radio_2.GetValue() == True : hote = "localhost"
        if self.radio_3.GetValue() == True : hote = self.ctrl_hote.GetValue()
                
        # Création de l'hôte :
        req = "SELECT host, user, password FROM user WHERE user='%s' and host='%s';" % (nom, hote)
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        if len(donnees) == 0 :
            req = u"CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (nom, hote, motdepasse)
            DB.ExecuterReq(req)
            print "L'utilisateur a ete cree."
        else:
            print "L'utilisateur existe deja."
            DB.Close()
            dlg = wx.MessageDialog(self, _(u"Cet utilisateur avec cet hôte existe déjà !"), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Création de l'autorisation à la base en cours
        if self.ctrl_autorisation.GetValue() == True :
            for suffixe in LISTE_SUFFIXES :
                req = u"""GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER,EXECUTE ON %s.* TO '%s'@'%s' ;
                """ % (u"%s_%s" % (self.nomBase, suffixe), nom, hote)
                DB.ExecuterReq(req)
        else:
            # Si l'autorisation existe déjà mais est décochée : on efface cette autorisation
            for suffixe in LISTE_SUFFIXES :
                req = "SELECT host, db, user FROM db WHERE user='%s' and db='%s' and host='%s';" % (nom, u"%s_%s" % (self.nomBase, suffixe), hote)
                DB.ExecuterReq(req)
                donnees = DB.ResultatReq()
                if len(donnees) > 0 :
                    req = u"""REVOKE ALL ON %s.* FROM '%s'@'%s';
                    """ % (self.nomBase, nom, hote)
                    DB.ExecuterReq(req)

        DB.ExecuterReq(u"FLUSH PRIVILEGES;")
        DB.Close()
        
        return True
        
        
        
            
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, nomUtilisateur=_(u"Bernard"), nomHote="%", nomBase="test1")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
