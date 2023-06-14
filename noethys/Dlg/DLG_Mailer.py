#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
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
import six
import re
import traceback
import copy
import datetime
import GestionDB
from Ctrl import CTRL_Bandeau
import  wx.lib.dialogs
from Dlg import DLG_Messagebox
from Utils import UTILS_Envoi_email
from Utils import UTILS_Parametres
from Utils import UTILS_Historique
from Utils import UTILS_Dates
from Ctrl import CTRL_Editeur_email
from Ol import OL_Destinataires_emails
from Ol import OL_Pieces_jointes_emails


class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="saisie_libre", afficher_confirmation_envoi=True):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
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
        self.bouton_modifier_dest = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Email_destinataires.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_ajouter_piece_spec = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_retirer_piece_spec = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Param�tres
        self.box_param_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.label_exp = wx.StaticText(self, -1, _(u"Exp. :"))
        self.ctrl_exp = CTRL_Editeur_email.Panel_Expediteur(self)

        # Pi�ces jointes
        self.box_pieces_staticbox = wx.StaticBox(self, -1, _(u"Pi�ces jointes communes"))
        self.ctrl_pieces = OL_Pieces_jointes_emails.ListView(self, id=-1, style=wx.LC_NO_HEADER|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_pieces.SetMinSize((250, 70))
        self.ctrl_pieces.MAJ() 
        
        self.bouton_ajouter_piece = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_suppr_piece = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

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
        self.ctrl_exp.SetToolTip(wx.ToolTip(_(u"S�lectionnez l'adresse d'exp�diteur")))
        self.ctrl_objet.SetToolTip(wx.ToolTip(_(u"Saisissez l'objet du message")))
        self.bouton_modifier_dest.SetToolTip(wx.ToolTip(_(u"Cliquez pour ajouter ou supprimer des destinataires")))
        self.bouton_ajouter_piece_spec.SetToolTip(wx.ToolTip(_(u"Cliquez pour ajouter une pi�ce jointe personnelle au destinataire s�lectionn� dans la liste")))
        self.bouton_retirer_piece_spec.SetToolTip(wx.ToolTip(_(u"Cliquez pour retirer une pi�ce jointe personnelle au destinataire s�lectionn� dans la liste")))
        self.bouton_ajouter_piece.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une pi�ce jointe")))
        self.bouton_suppr_piece.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour retirer la pi�ce jointe s�lectionn�e dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez pour obtenir de l'aide")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour acc�der aux outils")))
        self.bouton_envoyer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer le mail")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((800, 680))

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

        grid_sizer_haut_droit.AddGrowableRow(1)
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
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("EditeurdEmails")

    def OnBoutonOutils(self, event):
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Ins�rer un mot-cl�
        listeMotscles = CTRL_Editeur_email.GetMotscles(self.categorie)
        sousMenuMotscles = UTILS_Adaptations.Menu()
        index = 0
        for motcle, label in listeMotscles :
            id = 10000 + index
            sousMenuMotscles.AppendItem(wx.MenuItem(menuPop, id, motcle))
            self.Bind(wx.EVT_MENU, self.InsererMotcle, id=id)
            index += 1
        menuPop.AppendMenu(10, _(u"Ins�rer un mot-cl�"), sousMenuMotscles)

        # Aper�u de la fusion
        item = wx.MenuItem(menuPop, 60, _(u"Aper�u de la fusion"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu_fusion_emails.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ApercuFusion, id=60)
        
        menuPop.AppendSeparator()
        
        # Effacer le texte
        item = wx.MenuItem(menuPop, 50, _(u"Effacer le texte"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EffacerTexte, id=50)

        menuPop.AppendSeparator()
        
        # Mod�les d'Emails
        sousMenuModeles = UTILS_Adaptations.Menu()
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
            item = wx.MenuItem(menuPop, id, nom)
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_modele.png"), wx.BITMAP_TYPE_PNG))
            sousMenuModeles.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.ChargerModeleMenu, id=id)
                        
        item = menuPop.AppendMenu(20, _(u"Charger un mod�le d'Email"), sousMenuModeles)
        if len(listeDonnees) == 0 :
            if item != None :
                item.Enable(False)
            
        # Gestion des mod�les d'Email
        item = wx.MenuItem(menuPop, 30, _(u"Gestion des mod�les"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_modele.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GestionModeles, id=30)

        menuPop.AppendSeparator()
        
        # Envoyer un email de test
        item = wx.MenuItem(menuPop, 40, _(u"Envoyer un Email de test"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG))
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
        from Dlg import DLG_Apercu_fusion_emails
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
        
    def ChargerModeleMenu(self, event):
        """ Charger un mod�le d'Email """
        IDmodele = event.GetId() - 20000
        self.ChargerModele(IDmodele)

    def ChargerModele(self, IDmodele=None):
        DB = GestionDB.DB()
        req = """SELECT objet, texte_xml, IDadresse
        FROM modeles_emails
        WHERE IDmodele=%d;""" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if listeDonnees:
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
        from Dlg import DLG_Modeles_emails
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
        if adresseTest == None and self.afficher_confirmation_envoi == True :
            dlg = wx.MessageDialog(self, _(u"Confirmez-vous l'envoi de ce message pour %d destinataires ?\n\nAttention, l'envoi peut prendre quelques minutes...") % len(listeDestinataires), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                if self.IsShown() == False : self.ShowModal()
                return
            dlg.Destroy()

        # Pr�paration des messages
        liste_messages = []
        for track in listeDestinataires:
            adresse = track.adresse
            if adresseTest != None:
                adresse = adresseTest
            listePiecesPersonnelles = track.pieces
            dictChamps = track.champs

            # Pi�ces Personnelles + communes
            listePieces = listePiecesPersonnelles
            listePieces.extend(listePiecesCommunes)

            # Traitement des champs pour la fusion
            texte = copy.deepcopy(texteHTML)
            for motcle, valeur in CTRL_Editeur_email.GetChampsStandards().items():
                texte = texte.replace(motcle, valeur)
            for motcle, valeur in dictChamps.items():
                if valeur == None: valeur = u""
                if type(valeur) == int: valeur = str(valeur)
                if type(valeur) == bool: valeur = str(valeur)
                if type(valeur) == datetime.date: valeur = UTILS_Dates.DateDDEnFr(valeur)
                texte = texte.replace(motcle, valeur)

            # M�morisation du message
            message = UTILS_Envoi_email.Message(
                destinataires=[adresse,],
                sujet=sujet,
                texte_html=texte,
                fichiers=listePieces,
                images=listeImages,
                champs=dictChamps,
            )
            liste_messages.append(message)

        # Connexion messagerie
        dlg_progress = wx.ProgressDialog(_(u"Envoi des mails"), _(u"Connexion au serveur de messagerie..."), maximum=len(liste_messages)+1, parent=None)
        dlg_progress.SetSize((450, 140))
        dlg_progress.CenterOnScreen()

        try :
            messagerie = UTILS_Envoi_email.Messagerie(backend=dictExp["moteur"], hote=dictExp["smtp"], port=dictExp["port"], utilisateur=dictExp["utilisateur"], motdepasse=dictExp["motdepasse"],
                                                    email_exp=dictExp["adresse"], nom_exp=dictExp["nom_adresse"], timeout=20, use_tls=dictExp["startTLS"], parametres=dictExp["parametres"])
            messagerie.Connecter()
        except Exception as err:
            dlg_progress.Destroy()
            err = str(err).decode("iso-8859-15")
            intro = _(u"La connexion au serveur de messagerie est impossible :")
            conclusion = _(u"V�rifiez votre connexion internet ou les param�tres de votre adresse d'exp�dition.")
            dlgErreur = DLG_Messagebox.Dialog(self, titre=_(u"Erreur"), introduction=intro, detail=err, conclusion=conclusion, icone=wx.ICON_ERROR, boutons=[_(u"Ok"),])
            dlgErreur.ShowModal()
            dlgErreur.Destroy()
            return False

        # Envoi des messages
        self.listeSucces = messagerie.Envoyer_lot(messages=liste_messages, dlg_progress=dlg_progress, afficher_confirmation_envoi=self.afficher_confirmation_envoi)

        # Fermeture messagerie
        try :
            messagerie.Fermer()
        except:
            pass

        # Fermeture dlg_progress si besoin
        if dlg_progress != None:
            try :
                dlg_progress.Destroy()
            except:
                pass

        # Suppression des images temporaires incluses dans le message
        handler.DeleteTemporaryImages()

        # M�morisation dans l'historique
        if self.listeSucces != False:
            for message in self.listeSucces :
                self.MemorisationHistorique(message.GetLabelDestinataires(), message.sujet)

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

    def VerifieFusion(self, texteHTML="", listeDestinataires=[]):
        """ V�rifie que tous les mots-cl�s ont �t� remplac�s """
        listeResultats = []
        for track in listeDestinataires :
            dictChamps = track.champs      
            
            # Remplacement des champs pour la fusion
            texte = copy.deepcopy(texteHTML)
            for motcle, valeur in CTRL_Editeur_email.GetChampsStandards().items():
                texte = texte.replace(motcle, valeur)
            for motcle, valeur in dictChamps.items() :
                try :
                    if valeur == None : valeur = u""
                    if type(valeur) == int : valeur = str(valeur)
                    texte = texte.replace(motcle, valeur)
                except :
                    pass
            
            # V�rifie si champs non remplac�s
            x = r"\{[A-Za-z0-9_]*?\}"
            regex = re.compile(x)
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

    def SetPiecesJointes(self, listeFichiers=[]):
        self.ctrl_pieces.SetFichiers(listeFichiers)





if __name__ == u"__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    listeDonnees = [
        {"adresse" : "test@gmail.com", "pieces" : [], "champs" : {} },
        ]
    dlg.SetDonnees(listeDonnees, modificationAutorisee=True)
    dlg.ctrl_editeur.EcritTexte(u"Ceci est un texte de test.")
    dlg.ctrl_objet.SetValue(u"Test")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
