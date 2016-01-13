#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os

import GestionDB

import CTRL_Bandeau
import CTRL_Liste_cotisations
import CTRL_Cotisations_options
import UTILS_Cotisations
import UTILS_Envoi_email


class Dialog(wx.Dialog):
    def __init__(self, parent, filtres=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Cochez les cotisations à envoyer par Email puis cliquez sur le bouton 'Transférer vers l'éditeur d'Emails'.")
        titre = _(u"Envoi de cotisations par Email")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Emails_piece.png")
        
        # Cotisations
        self.box_cotisations_staticbox = wx.StaticBox(self, -1, _(u"Liste des cotisations"))
        self.ctrl_liste_cotisations = CTRL_Liste_cotisations.CTRL(self, filtres=filtres)
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options des cotisations"))
        self.ctrl_options = CTRL_Cotisations_options.CTRL(self)
        
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
        self.ctrl_liste_cotisations.MAJ() 
                

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour transférer les cotisations vers l'éditeur d'Emails"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Factures
        box_cotisations = wx.StaticBoxSizer(self.box_cotisations_staticbox, wx.VERTICAL)
        box_cotisations.Add(self.ctrl_liste_cotisations, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_cotisations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        import UTILS_Aide
        UTILS_Aide.Aide("Transmettredescotisationsparemai")

    def OnBoutonAnnuler(self, event): 
        self.ctrl_options.MemoriserParametres() 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        """ Aperçu PDF des cotisations """
        # Validation des données saisies
        tracks = self.ctrl_liste_cotisations.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune cotisation à envoyer par Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Création des cotisations sélectionnées
        listeIDcotisation = []
        for track in tracks :
            listeIDcotisation.append(track.IDcotisation) 
        cotisation = UTILS_Cotisations.Cotisation()
        dictOptions = self.ctrl_options.GetOptions()
        if dictOptions == False :
            return

        resultat = cotisation.Impression(listeCotisations=listeIDcotisation, nomDoc=None, afficherDoc=False, dictOptions=dictOptions, repertoire=dictOptions["repertoire"], repertoireTemp=True)
        if resultat == False : 
            return
        dictChampsFusion, dictPieces = resultat
        
        def SupprimerFichiersTemp():
            for IDcotisation, fichier in dictPieces.iteritems() :
                os.remove(fichier)  

        # Récupération de toutes les adresses Emails
        DB = GestionDB.DB()
        req = """SELECT IDindividu, mail, travail_mail
        FROM individus;"""
        DB.ExecuterReq(req)
        listeAdressesIndividus = DB.ResultatReq()
        DB.Close() 
        dictAdressesIndividus = {}
        for IDindividu, mail, travail_mail in listeAdressesIndividus :
            dictAdressesIndividus[IDindividu] = {"perso" : mail, "travail" : travail_mail}
                
        # Récupération des données adresse + champs + pièces
        listeDonnees = []
        listeAnomalies = []
        listeEnvoiNonDemande = []
        for track in tracks :
            adresse = UTILS_Envoi_email.GetAdresseFamille(track.IDfamille, choixMultiple=False, muet=True, nomTitulaires=track.nomsTitulaires)
            
            # Mémorisation des données
            if adresse not in (None, "", []) : 
                if dictPieces.has_key(track.IDcotisation) :
                    fichier = dictPieces[track.IDcotisation]
                    champs = dictChampsFusion[track.IDcotisation]
                    listeDonnees.append({"adresse" : adresse, "pieces" : [fichier,], "champs" : champs})
            else :
                listeAnomalies.append(track.nomsTitulaires)
        
        # Annonce les anomalies trouvées
        if len(listeAnomalies) > 0 :
            texte = _(u"%d des familles sélectionnées n'ont pas d'adresse Email.\n\n") % len(listeAnomalies)
            texte += _(u"Souhaitez-vous quand même continuer avec les %d autres familles ?") % len(listeDonnees)
            dlg = wx.MessageDialog(self, texte, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                SupprimerFichiersTemp()
                return        
        
        # Dernière vérification avant transfert
        if len(listeDonnees) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Il ne reste finalement aucune cotisation à envoyer par Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            SupprimerFichiersTemp()
            return

        # Transfert des données vers DLG Mailer
        import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self, categorie="cotisation")
        dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
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
