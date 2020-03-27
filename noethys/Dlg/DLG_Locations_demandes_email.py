#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import traceback
import GestionDB

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Liste_locations_demandes
from Ctrl import CTRL_Locations_demandes_options
from Utils import UTILS_Locations_demandes
from Utils import UTILS_Envoi_email


class Dialog(wx.Dialog):
    def __init__(self, parent, filtres=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Cochez les demandes de locations à envoyer par Email puis cliquez sur le bouton 'Transférer vers l'éditeur d'Emails'.")
        titre = _(u"Envoi de demandes de locations par Email")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Emails_piece.png")
        
        # Locations
        self.box_locations_staticbox = wx.StaticBox(self, -1, _(u"Liste des locations"))
        self.ctrl_liste_demandes = CTRL_Liste_locations_demandes.CTRL(self, filtres=filtres)
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options des locations"))
        self.ctrl_options = CTRL_Locations_demandes_options.CTRL(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Transférer vers l'éditeur d'Emails"), cheminImage="Images/32x32/Emails_piece.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contrôles
        self.ctrl_liste_demandes.MAJ()
                

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour transférer les demandes vers l'éditeur d'Emails")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Factures
        box_locations = wx.StaticBoxSizer(self.box_locations_staticbox, wx.VERTICAL)
        box_locations.Add(self.ctrl_liste_demandes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_locations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        box_options.Add(self.ctrl_options, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("TransmettredesdemandesparEmail")

    def OnBoutonAnnuler(self, event): 
        self.ctrl_options.MemoriserParametres() 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        """ Aperçu PDF des locations """
        # Validation des données saisies
        tracks = self.ctrl_liste_demandes.GetTracksCoches()
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune demande à envoyer par Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Création des demandes sélectionnées
        listeIDdemande = []
        for track in tracks :
            listeIDdemande.append(track.IDdemande)
        demande = UTILS_Locations_demandes.Demande()
        dictOptions = self.ctrl_options.GetOptions()
        if dictOptions == False :
            return

        resultat = demande.Impression(listeDemandes=listeIDdemande, nomDoc=None, afficherDoc=False, dictOptions=dictOptions, repertoire=dictOptions["repertoire"], repertoireTemp=True)
        if resultat == False : 
            return
        dictChampsFusion, dictPieces = resultat
        
        def SupprimerFichiersTemp():
            for IDdemande, fichier in dictPieces.items():
                if os.path.isfile(fichier):
                    os.remove(fichier)

        # Récupération des adresses Emails
        dict_adresses = UTILS_Envoi_email.GetAdressesFamilles([track.IDfamille for track in tracks])
        if dict_adresses == False:
            return False

        liste_donnees = []
        for track in tracks:
            if track.IDdemande in dictPieces:
                for adresse in dict_adresses.get(track.IDfamille, []):
                    fichier = dictPieces[track.IDdemande]
                    champs = dictChampsFusion[track.IDdemande]
                    liste_donnees.append({"adresse" : adresse, "pieces" : [fichier,], "champs" : champs})

        # Transfert des données vers DLG Mailer
        from Dlg import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self, categorie="location_demande")
        dlg.SetDonnees(liste_donnees, modificationAutorisee=False)
        dlg.ChargerModeleDefaut()
        dlg.ShowModal() 
        dlg.Destroy()

        # Suppression des PDF temporaires
        SupprimerFichiersTemp()




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
