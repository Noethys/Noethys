#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import sys
import os
import re
import cStringIO
import traceback
import copy
import datetime
import GestionDB
import CTRL_Bandeau
import wx.lib.filebrowsebutton as filebrowse
import  wx.lib.dialogs
import FonctionsPerso
import time
import UTILS_Envoi_email
import UTILS_Parametres
import UTILS_Historique
import UTILS_Dates
import CTRL_Editeur_email
import CTRL_Pieces_jointes_emails
import OL_Destinataires_emails
import OL_Pieces_jointes_emails


class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="saisie_libre", afficher_confirmation_envoi=True):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.categorie = categorie
        self.afficher_confirmation_envoi = afficher_confirmation_envoi
        self.listePiecesJointes = []
        self.listeAnomalies = []
        self.listeSucces = []

        # Bandeau
        intro = _(u"Vous pouvez ici exp�dier des Emails par lot. S�lectionnez une adresse d'exp�diteur, un objet, un ou plusieurs destinataires avant de r�diger votre texte. Les Emails sont envoy�s par lots afin de contourner les protections anti-spam des op�rateurs.")
        titre = _(u"Editeur d'Emails")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Editeur_email.png")
        
        # Destinataires
        self.box_destinataires_staticbox = wx.StaticBox(self, -1, _(u"Destinataires"))
        self.ctrl_destinataires = OL_Destinataires_emails.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_destinataires.MAJ() 
        self.bouton_modifier_dest = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Email_destinataires.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ajouter_piece_spec = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_retirer_piece_spec = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Param�tres
        self.box_param_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.label_exp = wx.StaticText(self, -1, _(u"Exp. :"))
        self.ctrl_exp = CTRL_Editeur_email.Panel_Expediteur(self)
        self.check_accuseReception = wx.CheckBox(self, -1, _(u"Accus� de r�ception"))
        
        # Pi�ces jointes
        self.box_pieces_staticbox = wx.StaticBox(self, -1, _(u"Pi�ces jointes communes"))
        self.ctrl_pieces = OL_Pieces_jointes_emails.ListView(self, id=-1, style=wx.LC_NO_HEADER|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_pieces.SetMinSize((200, 70))
        self.ctrl_pieces.MAJ() 
        
        self.bouton_ajouter_piece = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_suppr_piece = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Texte
        self.box_texte_staticbox = wx.StaticBox(self, -1, _(u"Message"))
        self.label_objet = wx.StaticText(self, -1, _(u"Objet :"))
        self.ctrl_objet = wx.TextCtrl(self, -1, u"")
        self.ctrl_objet.SetMinSize((200, -1))

        self.ctrl_editeur = CTRL_Editeur_email.CTRL(self)
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer l'Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.ctrl_destinataires.Modifier, self.bouton_modifier_dest)
        self.Bind(wx.EVT_BUTTON, self.ctrl_destinataires.AjouterPiece, self.bouton_ajouter_piece_spec)
        self.Bind(wx.EVT_BUTTON, self.ctrl_destinataires.RetirerPiece, self.bouton_retirer_piece_spec)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pieces.Ajouter, self.bouton_ajouter_piece)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pieces.Retirer, self.bouton_suppr_piece)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        
        # Init contr�les
        self.ctrl_objet.SetFocus()
        
    def __set_properties(self):
        self.ctrl_exp.SetToolTipString(_(u"S�lectionnez l'adresse d'exp�diteur"))
        self.ctrl_objet.SetToolTipString(_(u"Saisissez l'objet du message"))
        self.bouton_modifier_dest.SetToolTipString(_(u"Cliquez pour ajouter ou supprimer des destinataires"))
        self.bouton_ajouter_piece_spec.SetToolTipString(_(u"Cliquez pour ajouter une pi�ce jointe personnelle au destinataire s�lectionn� dans la liste"))
        self.bouton_retirer_piece_spec.SetToolTipString(_(u"Cliquez pour retirer une pi�ce jointe personnelle au destinataire s�lectionn� dans la liste"))
        self.bouton_ajouter_piece.SetToolTipString(_(u"Cliquez ici pour ajouter une pi�ce jointe"))
        self.bouton_suppr_piece.SetToolTipString(_(u"Cliquez ici pour retirer la pi�ce jointe s�lectionn�e dans la liste"))
        self.check_accuseReception.SetToolTipString(_(u"Cochez cette option pour demander un accus� de r�ception"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez pour obtenir de l'aide"))
        self.bouton_outils.SetToolTipString(_(u"Cliquez ici pour acc�der aux outils"))
        self.bouton_envoyer.SetToolTipString(_(u"Cliquez ici pour envoyer le mail"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((750, 680))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_haut_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Destinataires
        box_destinataires = wx.StaticBoxSizer(self.box_destinataires_staticbox, wx.VERTICAL)
        grid_sizer_destinataires = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_dest = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_destinataires.Add(self.ctrl_destinataires, 1, wx.EXPAND, 0)
        grid_sizer_boutons_dest.Add(self.bouton_modifier_dest, 0, 0, 0)
        grid_sizer_boutons_dest.Add( (10, 10), 0, 0, 0)
        grid_sizer_boutons_dest.Add(self.bouton_ajouter_piece_spec, 0, 0, 0)
        grid_sizer_boutons_dest.Add(self.bouton_retirer_piece_spec, 0, 0, 0)
        grid_sizer_destinataires.Add(grid_sizer_boutons_dest, 1, wx.EXPAND, 0) 
        grid_sizer_destinataires.AddGrowableRow(0)
        grid_sizer_destinataires.AddGrowableCol(0)

        box_destinataires.Add(grid_sizer_destinataires, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(box_destinataires, 1, wx.EXPAND, 0)
        
        # Param�tres
        box_param = wx.StaticBoxSizer(self.box_param_staticbox, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_param.Add(self.label_exp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_exp, 1, wx.EXPAND, 0)
        grid_sizer_param.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_param.Add(self.check_accuseReception, 1, wx.EXPAND, 0)
        grid_sizer_param.AddGrowableCol(1)
        box_param.Add(grid_sizer_param, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(box_param, 1, wx.EXPAND, 0)        
        
        # Pi�ces jointes
        box_pieces = wx.StaticBoxSizer(self.box_pieces_staticbox, wx.VERTICAL)
        grid_sizer_pieces = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_pieces = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_pieces.Add(self.ctrl_pieces, 0, wx.EXPAND, 0)
        grid_sizer_boutons_pieces.Add(self.bouton_ajouter_piece, 0, 0, 0)
        grid_sizer_boutons_pieces.Add(self.bouton_suppr_piece, 0, 0, 0)
        grid_sizer_pieces.Add(grid_sizer_boutons_pieces, 1, wx.EXPAND, 0)
        grid_sizer_pieces.AddGrowableRow(0)
        grid_sizer_pieces.AddGrowableCol(0)
        box_pieces.Add(grid_sizer_pieces, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(box_pieces, 1, wx.EXPAND, 0)
        grid_sizer_haut_droit.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_haut_droit, 1, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(0)
        
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Texte
        box_texte = wx.StaticBoxSizer(self.box_texte_staticbox, wx.VERTICAL)

        grid_sizer_objet = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_objet.Add(self.label_objet, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_objet.Add(self.ctrl_objet, 0, wx.EXPAND, 0)
        grid_sizer_objet.AddGrowableCol(1)
        box_texte.Add(grid_sizer_objet, 0, wx.ALL|wx.EXPAND, 5)

        box_texte.Add(self.ctrl_editeur, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_texte, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Commandes
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_commandes.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_envoyer, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_commandes.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("EditeurdEmails")

    def OnBoutonOutils(self, event):
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Ins�rer un mot-cl�
        listeMotscles = CTRL_Editeur_email.GetMotscles(self.categorie)
        sousMenuMotscles = wx.Menu()
        index = 0
        for motcle, label in listeMotscles :
            id = 10000 + index
            sousMenuMotscles.AppendItem(wx.MenuItem(menuPop, id, motcle))
            self.Bind(wx.EVT_MENU, self.InsererMotcle, id=id)
            index += 1
        menuPop.AppendMenu(10, _(u"Ins�rer un mot-cl�"), sousMenuMotscles)

        # Aper�u de la fusion
        item = wx.MenuItem(menuPop, 60, _(u"Aper�u de la fusion"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Apercu_fusion_emails.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ApercuFusion, id=60)
        
        menuPop.AppendSeparator()
        
        # Effacer le texte
        item = wx.MenuItem(menuPop, 50, _(u"Effacer le texte"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Gomme.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EffacerTexte, id=50)

        menuPop.AppendSeparator()
        
        # Mod�les d'Emails
        sousMenuModeles = wx.Menu()
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, description
        FROM modeles_emails
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDmodele, nom, description in listeDonnees :
            id = 20000 + IDmodele
            maxCaract = 80
            if len(description) > maxCaract :
                description = u"%s..." % description[:maxCaract]
            texte = u"%s (%s)" % (nom, description)
            item = wx.MenuItem(menuPop, id, texte)
            item.SetBitmap(wx.Bitmap("Images/16x16/Emails_modele.png", wx.BITMAP_TYPE_PNG))
            sousMenuModeles.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.ChargerModele, id=id)
                        
        item = menuPop.AppendMenu(20, _(u"Charger un mod�le d'Email"), sousMenuModeles)
        if len(listeDonnees) == 0 :
            item.Enable(False)
            
        # Gestion des mod�les d'Email
        item = wx.MenuItem(menuPop, 30, _(u"Gestion des mod�les"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Emails_modele.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GestionModeles, id=30)

        menuPop.AppendSeparator()
        
        # Envoyer un email de test
        item = wx.MenuItem(menuPop, 40, _(u"Envoyer un Email de test"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerTest, id=40)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def InsererMotcle(self, event):
        motcle, label = CTRL_Editeur_email.GetMotscles(self.categorie)[event.GetId() - 10000]
        self.ctrl_editeur.EcritTexte(motcle)

    def ApercuFusion(self, event):
        """ Aper�u de la fusion """
        # Pr�paration des donn�es de fusion
        donnees = self.ctrl_destinataires.GetDonneesDict()  
        if len(donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner au moins un destinataire !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(self.ctrl_editeur.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_editeur.SetFocus()
            return
        # Aper�u de la fusion
        texte_xml = self.ctrl_editeur.GetXML() 
        import DLG_Apercu_fusion_emails
        dlg = DLG_Apercu_fusion_emails.Dialog(self, donnees=donnees, texte_xml=texte_xml)
        dlg.ShowModal() 
        dlg.Destroy()
        
    def SetDonnees(self, donnees=[], modificationAutorisee=True):
        # MAJ contr�les Adresses
        self.ctrl_destinataires.SetDonneesManuelles(listeDonnees=donnees, modificationAutorisee=modificationAutorisee)
        self.bouton_modifier_dest.Enable(modificationAutorisee)
        
    def EffacerTexte(self, event):
        self.ctrl_editeur.ctrl_editeur.Clear()
        self.ctrl_editeur.SetFocus()
        
    def ChargerModele(self, event):
        """ Charger un mod�le d'Email """
        IDmodele = event.GetId() - 20000
        DB = GestionDB.DB()
        req = """SELECT objet, texte_xml, IDadresse
        FROM modeles_emails
        WHERE IDmodele=%d;""" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        objet, texte_xml, IDadresse = listeDonnees[0]
        self.ctrl_objet.SetValue(objet)
        if texte_xml != None :
            self.ctrl_editeur.SetXML(texte_xml)
        self.ctrl_exp.SetID(IDadresse)
    
    def ChargerModeleDefaut(self):
        DB = GestionDB.DB()
        req = """SELECT IDmodele, objet, texte_xml, IDadresse
        FROM modeles_emails
        WHERE categorie='%s' AND defaut=1;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 :
            return
        IDmodele, objet, texte_xml, IDadresse = listeDonnees[0]
        self.ctrl_objet.SetValue(objet)
        if texte_xml != None :
            self.ctrl_editeur.SetXML(texte_xml)
        self.ctrl_exp.SetID(IDadresse)
    
    def GestionModeles(self, event):
        import DLG_Modeles_emails
        dlg = DLG_Modeles_emails.Dialog(self, categorie=self.categorie)
        dlg.ShowModal() 
        dlg.Destroy()

    def EnvoyerTest(self, event):
        """ Envoi d'un Email de test """
        adresse = UTILS_Parametres.Parametres(mode="get", categorie="emails", nom="adresse_test", valeur=u"")      
        dlg = wx.TextEntryDialog(self, _(u"Saisissez une adresse Email et cliquez sur Ok :"), _(u"Envoi d'un Email de test"), adresse)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        adresse = dlg.GetValue()
        dlg.Destroy()
        # M�morise l'adresse saisie
        if UTILS_Envoi_email.ValidationEmail(adresse) == False :
            dlg = wx.MessageDialog(self, _(u"L'adresse saisie n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        UTILS_Parametres.Parametres(mode="set", categorie="emails", nom="adresse_test", valeur=adresse)
        # V�rifie si au moins un destintaire saisi
        listeDestinataires=self.ctrl_destinataires.GetDonnees()
        if len(listeDestinataires) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner au moins un destinataire !\n\n(En cas de fusion, les donn�es du premier destinataire seront utilis�s)"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Envoi du mail test
        self.Envoyer(listeDestinataires=[listeDestinataires[0],], adresseTest=adresse)    
        

    def OnBoutonEnvoyer(self, event):       
        self.Envoyer(listeDestinataires = self.ctrl_destinataires.GetDonnees())    
    
    
    def Envoyer(self, listeDestinataires=[], adresseTest=None):
        # Exp�diteur
        dictExp = self.ctrl_exp.GetDonnees()
        if dictExp == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune adresse d'exp�diteur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            if self.IsShown() == False : self.ShowModal()
            return
        exp = dictExp["adresse"]
        serveur = dictExp["smtp"]
        port = dictExp["port"]
        connexionssl = dictExp["ssl"]
        motdepasse = dictExp["motdepasse"]
        
        # Accus� de r�ception
        accuseReception = self.check_accuseReception.GetValue()
        
        # Objet
        sujet = self.ctrl_objet.GetValue()
        if len(sujet) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un objet pour ce message !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            if self.IsShown() == False : self.ShowModal()
            self.ctrl_objet.SetFocus()
            return
        
        # Destinataires
        if len(listeDestinataires) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner au moins un destinataire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            if self.IsShown() == False : self.ShowModal()
            return
        
        nbreAnomalies = 0
        for dest in listeDestinataires :
            if dest.adresse == None :
                nbreAnomalies += 1
        if nbreAnomalies > 0 :
            dlg = wx.MessageDialog(self, _(u"%d adresse(s) Email ne sont pas renseign�es !") % nbreAnomalies, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Texte
        if len(self.ctrl_editeur.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            if self.IsShown() == False : self.ShowModal()
            self.ctrl_editeur.SetFocus()
            return
        texteHTML, listeImages, handler = self.ctrl_editeur.GetHTML(imagesIncluses=True)
        
        # V�rifie la fusion des mots-cl�s
        if self.VerifieFusion(texteHTML, listeDestinataires) == False :
            if self.IsShown() == False : self.ShowModal()
            return
    
        # Pi�ces jointes
        listePiecesCommunes = self.ctrl_pieces.GetDonnees() 

        # Demande de confirmation
        if adresseTest == None :
            dlg = wx.MessageDialog(self, _(u"Confirmez-vous l'envoi de ce message pour %d destinataires ?\n\nAttention, l'envoi peut prendre quelques minutes...") % len(listeDestinataires), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                if self.IsShown() == False : self.ShowModal()
                return
            dlg.Destroy()

        # Envoi des mails
        dlg = wx.ProgressDialog(_(u"Envoi des mails"),
                               _(u"Veuillez patienter..."),
                               maximum = len(listeDestinataires)+1,
                               parent=self,
                                )
        dlg.SetSize((370, 140))
        dlg.CenterOnScreen() 
        
        index = 1
        self.listeAnomalies = []
        self.listeSucces = []
        for track in listeDestinataires :
            adresse = track.adresse
            if adresseTest != None :
                adresse = adresseTest
##            adresse = FonctionsPerso.Supprime_accent2(adresse)
            listePiecesPersonnelles = track.pieces
            dictChamps = track.champs      
            
            # Pi�ces Personnelles + communes
            listePieces = listePiecesPersonnelles
            listePieces.extend(listePiecesCommunes)
            
            # Traitement des champs pour la fusion
            texte = copy.deepcopy(texteHTML)
            for motcle, valeur in CTRL_Editeur_email.GetChampsStandards().iteritems() :
                texte = texte.replace(motcle, valeur)
            for motcle, valeur in dictChamps.iteritems() :
                if valeur == None : valeur = u""
                if type(valeur) == int : valeur = str(valeur)
                if type(valeur) == bool : valeur = str(valeur)
                if type(valeur) == datetime.date : valeur = UTILS_Dates.DateDDEnFr(valeur)
                texte = texte.replace(motcle, valeur)
            
            # Envoi du mail
            try :
                labelAdresse = adresse.decode("iso-8859-15")
            except :
                labelAdresse = adresse
            label = _(u"Envoi %d/%d : %s...") % (index, len(listeDestinataires), labelAdresse)
            self.EcritStatusBar(label)
            dlg.Update(index, label)
            
            try :
                etat = UTILS_Envoi_email.Envoi_mail( 
                    adresseExpediteur=exp, 
                    listeDestinataires=[adresse,], 
                    listeDestinatairesCCI=[], 
                    sujetMail=sujet, 
                    texteMail=texte, 
                    listeFichiersJoints=listePieces, 
                    serveur=serveur, 
                    port=port, 
                    ssl=connexionssl, 
                    listeImages=listeImages,
                    motdepasse=motdepasse,
                    accuseReception = accuseReception,
                    )
                self.listeSucces.append(track)
                
                # M�morisation dans l'historique
                self.MemorisationHistorique(adresse, sujet)

            except Exception, err:
                err = str(err).decode("iso-8859-15")
                self.listeAnomalies.append((track, err))
                print ("Erreur dans l'envoi d'un mail : %s...", err)
                dlgErreur = wx.MessageDialog(self, _(u"%s\n\nL'erreur suivante a �t� d�tect�e :\n%s.\n\nSouhaitez-vous quand m�me continuer le processus ?") % (label, err), _(u"Erreur"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_ERROR)
                traceback.print_exc(file=sys.stdout)
                if dlgErreur.ShowModal() != wx.ID_YES :
                    dlgErreur.Destroy()
                    # Arr�t du processus
                    dlg.Destroy() 
                    handler.DeleteTemporaryImages()
                    self.EcritStatusBar(u"")
                    return
                dlgErreur.Destroy()
            
            time.sleep(2) # 1 seconde d'attente entre chaque envoi...
            index += 1
        
        # Fin de la gauge
        dlg.Update(index, _(u"Fin de l'envoi."))
##        time.sleep(2)
        dlg.Destroy() 
        
        # Suppression des images temporaires incluses dans le message
        handler.DeleteTemporaryImages()

        # Affichage des r�sultats
        self.EcritStatusBar(_(u"Fin de l'envoi des Emails"))
        
        # Si tous les Emails envoy�s avec succ�s
        if len(self.listeAnomalies) == 0 and self.afficher_confirmation_envoi == True :
            if len(self.listeSucces) == 1 :
                message = _(u"L'Email a �t� envoy� avec succ�s !")
            else :
                message = _(u"Les %d Emails ont �t� envoy�s avec succ�s !") % len(self.listeSucces)
            dlg = wx.MessageDialog(self, message, _(u"Fin de l'envoi"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        # Si Anomalies
        if len(self.listeAnomalies) > 0 :
            
            if len(self.listeSucces) > 0 :
                message = _(u"%d Email(s) ont �t� envoy�s avec succ�s mais les %d envois suivants ont �chou� :\n\n") % (len(self.listeSucces), len(self.listeAnomalies))
            else :
                message = _(u"Tous les envois ont lamentablement �chou� :\n\n")
            
            for track, erreur in self.listeAnomalies :
                try :
                    message += u"   - %s : %s" % (track.adresse.decode("iso-8859-15"), erreur)
                except :
                    message += u"   - %s : %s" % (track.adresse, erreur)
            
            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message, _(u"Compte-rendu de l'envoi"))
            dlg.ShowModal()
                    
        self.EcritStatusBar(u"")
    
    def MemorisationHistorique(self, adresse="", sujet=""):
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, rattachements.IDfamille
        FROM individus
        LEFT JOIN rattachements ON rattachements.IDindividu = individus.IDindividu
        WHERE (mail='%s' OR travail_mail='%s'); """ % (adresse, adresse)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDindividu, IDfamille in listeDonnees :
            UTILS_Historique.InsertActions([{
                "IDindividu" : IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : 33, 
                "action" : _(u"Envoi de l'Email '%s'") % sujet,
                },])
        DB.Close()

    def EcritStatusBar(self, texte=u"") :
        try :
            wx.GetApp().GetTopWindow().SetStatusText(texte, 0)
        except : pass

    def VerifieFusion(self, texteHTML="", listeDestinataires=[]):
        """ V�rifie que tous les mots-cl�s ont �t� remplac�s """
        listeResultats = []
        for track in listeDestinataires :
            dictChamps = track.champs      
            
            # Remplacement des champs pour la fusion
            texte = copy.deepcopy(texteHTML)
            for motcle, valeur in CTRL_Editeur_email.GetChampsStandards().iteritems() :
                texte = texte.replace(motcle, valeur)
            for motcle, valeur in dictChamps.iteritems() :
                try :
                    if valeur == None : valeur = u""
                    if type(valeur) == int : valeur = str(valeur)
                    texte = texte.replace(motcle, valeur)
                except :
                    pass
            
            # V�rifie si champs non remplac�s
            regex = re.compile(r"\{[A-Za-z0-9_]*?\}") 
            listeAnomalies = regex.findall(texte)
            if len(listeAnomalies) > 0 :
                listeResultats.append((track.adresse, listeAnomalies))
        
        # Affichage des r�sultats
        if len(listeResultats) > 0 :
            message = _(u"Certains mots-cl�s semblent ne pas avoir �t� remplac�s lors de la fusion des donn�es. Est-ce normal ?\n\n")
            affichageMax = 10
            for adresse, listeAnomalies in listeResultats[:affichageMax] :
                message += u"   - %s : %s.\n" % (adresse, ", ".join(listeAnomalies))
            if len(listeResultats) > affichageMax :
                message += _(u"   - Ainsi que %d autres...\n") % (len(listeResultats) - affichageMax)
            message += _(u"\nSouhaitez-vous tout de m�me continuer l'envoi ?")
            dlgErreur = wx.MessageDialog(self, message, _(u"Anomalies"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlgErreur.ShowModal() == wx.ID_YES :
                return True
            else :
                return False
        else :
            return True


if __name__ == u"__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    listeDonnees = [
##        {"adresse" : "test@gmail.com", "pieces" : [], "champs" : {} },
        ]
    dlg.SetDonnees(listeDonnees, modificationAutorisee=True)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
    

##    app = wx.App(0)
##    try :
##        raise NameError("�t�")
##    except Exception, err :
##        err = str(err).decode("iso-8859-15")
##        dlgErreur = wx.MessageDialog(None, _(u"%s\n\nL'erreur suivante a �t� d�tect�e :\n%s.\n\nSouhaitez-vous quand m�me continuer le processus ?") % ("label", err), _(u"Erreur"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_ERROR)
##        traceback.print_exc(file=sys.stdout)
##        dlgErreur.ShowModal() 
##        dlgErreur.Destroy()
##    app.MainLoop()
##    