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
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import GestionDB
from Dlg import DLG_Saisie_utilisateur_reseau
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Utilisateurs
import six


LISTE_SUFFIXES = ("data", "photos", "documents")


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1, nomBase="" ):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        self.nomBase = nomBase
        self.parent = parent

        # Recherche de la base MySQL en cours
        if self.nomBase == "" :
            self.nomBase = self.RechercheBaseEnCours()
        
        self.listCtrl = ListCtrl(self, nomBase=self.nomBase)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un utilisateur réseau")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'utilisateur réseau sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'utilisateur réseau sélectionné dans la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.listCtrl, 1, wx.EXPAND, 0)
        
        # Commandes
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=10)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def MAJpanel(self):
        self.nomBase = self.RechercheBaseEnCours()
        self.active = self.ActiveAffichage()
        self.listCtrl.MAJListeCtrl() 
        if self.active == True :
            self.Enable(True)
        else:
            self.Enable(False)
        
    def OnBoutonAjouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs_reseau", "creer") == False : return
        from Dlg import DLG_Saisie_utilisateur_reseau
        dlg = DLG_Saisie_utilisateur_reseau.Dialog(self, nomUtilisateur="", nomHote="", nomBase=self.nomBase)
        dlg.ShowModal() 
        dlg.Destroy()
        self.listCtrl.MAJListeCtrl()

    def OnBoutonModifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs_reseau", "modifier") == False : return
        dlg = wx.MessageDialog(self, _(u"Actuellement, il n'est pas encore possible de modifier un utilisateur. \nVous devez donc supprimer l'utilisateur et le re-créer."), "Information", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()      
        
    def OnBoutonSupprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs_reseau", "supprimer") == False : return
        index = self.listCtrl.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un utilisateur à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        nom = self.listCtrl.listeDonnees[index][0]
        hote = self.listCtrl.listeDonnees[index][1]
        
        # Vérifie que ce n'est pas ROOT
        if nom == "root" :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer le compte administrateur"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande de confirmation
        txtMessage = unicode((_(u"Voulez-vous vraiment supprimer cet utilisateur ? \n\n> %s@%s") % (nom, hote)))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression
        DB = GestionDB.DB()
        DB.ExecuterReq("USE mysql;")

        # Suppression de l'autorisation à la base en cours
        for suffixe in LISTE_SUFFIXES :
            req = "SELECT host, db, user FROM db WHERE user='%s' and db='%s' and host='%s';" % (nom, u"%s_%s" % (self.nomBase, suffixe), hote)
            DB.ExecuterReq(req)
            donnees = DB.ResultatReq()
            if len(donnees) > 0 :
                req = u"""REVOKE ALL ON %s.* FROM '%s'@'%s';
                """ % (u"%s_%s" % (self.nomBase, suffixe), nom, hote)
                DB.ExecuterReq(req)

        # Suppression de l'hôte :
        req = "DELETE FROM user WHERE user='%s' and host='%s';" % (nom, hote)
        DB.ExecuterReq(req)

        req = u"FLUSH PRIVILEGES;"
        DB.ExecuterReq(req)
        DB.Close()

        # MàJ du ListCtrl
        self.listCtrl.MAJListeCtrl()
                
    def RechercheBaseEnCours(self):
        nomFichier = ""
        try :
            topWindow = wx.GetApp().GetTopWindow()
            nomWindow = topWindow.GetName()
        except :
            nomWindow = None
        if nomWindow == "general" : 
            # Si la frame 'General' est chargée, on y récupère le dict de config
            nomFichier = topWindow.userConfig["nomFichier"]
        else:
            # Récupération du nom de la DB directement dans le fichier de config sur le disque dur
            from Utils import UTILS_Config
            cfg = UTILS_Config.FichierConfig()
            nomFichier = cfg.GetItemConfig("nomFichier")
        if "[RESEAU]" in nomFichier :
            nomFichier = nomFichier[nomFichier.index("[RESEAU]") + 8:]
        return nomFichier


class ListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, nomBase = ""):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        self.nomBase = nomBase
        self.Remplissage()

    def Remplissage(self, select=None):
        self.listeDonnees = self.Importation()

        # Création des colonnes
        self.InsertColumn(0, _(u"Accès"))
        self.SetColumnWidth(0, 55)
        self.InsertColumn(1, _(u"Nom de l'utilisateur"))
        self.SetColumnWidth(1, 200)
        self.InsertColumn(2, _(u"Hôte de connexion"))
        self.SetColumnWidth(2, 300)

        # Remplissage avec les valeurs
        self.remplissage = True
        indexListe = 0
        for user, host, autorisation in self.listeDonnees :
            if user == "root" : 
                autorisation = True
                
            if autorisation == True :
                autorisationStr = "Oui"
            else:
                autorisationStr = "Non"
            index = self.InsertStringItem(six.MAXSIZE, autorisationStr)
            
            if user == "root" :
                user = _(u"root (Administrateur)")
            self.SetStringItem(index, 1, user)

            if host == "%" : host = _(u"Connexion depuis n'importe quel hôte")
            elif host == "localhost" : host = _(u"Connexion uniquement depuis le serveur principal")
            else : host = _(u"Connexion uniquement depuis l'hôte %s") % host
            self.SetStringItem(index, 2, host)

            self.SetItemData(index, indexListe)
                
            # Check
            if autorisation == True :
                self.CheckItem(index) 
            
            indexListe += 1
        
        self.remplissage = False

    def MAJListeCtrl(self, select=None):
        self.ClearAll()
        self.Remplissage(select)

    def OnCheckItem(self, index, flag):
        """ Ne fait rien si c'est le remplissage qui coche la case ! """
        if self.remplissage == False :
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_utilisateurs_reseau", "modifier") == False : return
            nom, hote = self.listeDonnees[index][0], self.listeDonnees[index][1]
            
            # Vérifie que ce n'est pas ROOT
            if nom == "root" :
                self.remplissage = True
                self.CheckItem(index) 
                self.remplissage = False
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas modifier le compte administrateur"), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
            # Enregistre le changement d'autorisation
            if self.IsChecked(index) == False :
                self.SetAutorisation(False, nom, hote)
                self.listeDonnees[index][2] = False
                self.SetStringItem(index, 0, "Non")
            else:
                etat = self.SetAutorisation(True, nom, hote)
                self.listeDonnees[index][2] = True
                self.SetStringItem(index, 0, "Oui")

        else:
            pass

    def SetAutorisation(self, etat=True, nom="", hote=""):
        # Création de l'autorisation à la base en cours
        DB = GestionDB.DB()
        DB.ExecuterReq("USE mysql;")
        
        if etat == True :
            for suffixe in LISTE_SUFFIXES :
                req = u"""GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER,EXECUTE ON %s.* TO '%s'@'%s' ;
                """ % (u"%s_%s" % (self.nomBase, suffixe), nom, hote)
                DB.ExecuterReq(req)
        else:
            # Si l'autorisation existe déjà mais est décochée : on efface cette autorisation
            for suffixe in LISTE_SUFFIXES :
                req = u"SELECT host, db, user FROM db WHERE user='%s' and db='%s' and host='%s';" % (nom, u"%s_%s" % (self.nomBase, suffixe), hote)
                DB.ExecuterReq(req)
                donnees = DB.ResultatReq()
                if len(donnees) > 0 :
                    req = u"""REVOKE ALL ON %s.* FROM '%s'@'%s';
                    """ % (u"%s_%s" % (self.nomBase, suffixe), nom, hote)
                    DB.ExecuterReq(req)            
        req = u"FLUSH PRIVILEGES;"
        DB.ExecuterReq(req)
        DB.Close()
        

    def Importation(self):
        # Importation des données de la liste
        DB = GestionDB.DB()
        
        # Recherche des utilisateurs MySQL
        req = """SELECT Host, User 
        FROM `mysql`.`user` 
        WHERE User NOT LIKE 'mysql%'
        ORDER BY User, Host;"""
        DB.ExecuterReq(req)
        listeUtilisateurs = DB.ResultatReq()

        # Recherche des autorisations pour la base en cours
        req = "SELECT host, user FROM `mysql`.`db` WHERE Db='%s';" % u"%s_data" % self.nomBase
        DB.ExecuterReq(req)
        listeAutorisations = DB.ResultatReq()
        DB.Close()
        
        # Création de la liste de données
        listeDonnees = []
        for host, user in listeUtilisateurs :
            # Recherche s'il y a une autorisation pour la base en cours
            autorisation = False
            for hostTmp, userTmp in listeAutorisations :
                if host == hostTmp and user == userTmp :
                    autorisation = True

            if six.PY2:
                host = host.decode("utf8")
            listeDonnees.append([user, host, autorisation])
        return listeDonnees


        

class Dialog(wx.Dialog):
    def __init__(self, parent, title="", nomBase="" ):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent      
        
        # Bandeau
        intro = _(u"Quand vous créez un fichier réseau pour Noethys, il n'y a que vous, l'administrateur, qui avez le droit d'accéder au fichier. Vous devez donc créer des utilisateurs ou accorder une autorisation d'accès aux utilisateurs existants. Vous devez indiquer également les postes (hôtes) depuis lesquels ces utilisateurs sont autorisés à se connecter. Cochez les utilisateurs autorisés à se connecter au fichier réseau chargé. Cliquez sur le bouton 'Aide' pour en savoir plus...")
        titre = _(u"Gestion des accès réseau")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=54, nomImage="Images/32x32/Utilisateur_reseau.png")
        self.SetTitle(titre)

        self.panel_contenu = Panel(self, nomBase=nomBase)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        
    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
        self.SetMinSize((660, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(self.panel_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Accsrseau")
                            
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
