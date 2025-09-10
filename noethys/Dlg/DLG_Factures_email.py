#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os

import GestionDB
from Dlg import DLG_Messagebox
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Liste_factures
from Ctrl import CTRL_Factures_options
from Utils import UTILS_Facturation
from Utils import UTILS_Envoi_email


class Dialog(wx.Dialog):
    def __init__(self, parent, filtres=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Cochez les factures à envoyer par Email puis cliquez sur le bouton 'Transférer vers l'éditeur d'Emails'.")
        titre = _(u"Envoi de factures par Email")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Emails_piece.png")
        
        # Factures
        self.box_factures_staticbox = wx.StaticBox(self, -1, _(u"Liste des factures"))
        self.ctrl_liste_factures = CTRL_Liste_factures.CTRL(self, filtres=filtres)
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options des factures"))
        self.ctrl_options = CTRL_Factures_options.CTRL(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_recap = CTRL_Bouton_image.CTRL(self, texte=_(u"Récapitulatif"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Transférer vers l'éditeur d'Emails"), cheminImage="Images/32x32/Emails_piece.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRecap, self.bouton_recap)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contrôles
        self.ctrl_liste_factures.MAJ() 
                

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_recap.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer un récapitulatif des factures cochées dans la liste")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour transférer les factures vers l'éditeur d'Emails")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Factures
        box_factures = wx.StaticBoxSizer(self.box_factures_staticbox, wx.VERTICAL)
        box_factures.Add(self.ctrl_liste_factures, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_factures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        box_options.Add(self.ctrl_options, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_recap, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("TransmettreparEmail")

    def OnBoutonAnnuler(self, event): 
        self.ctrl_options.MemoriserParametres() 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonRecap(self, event): 
        """ Aperçu PDF du récapitulatif des factures """
        tracks = self.ctrl_liste_factures.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une facture dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        from Dlg import DLG_Impression_recap_factures
        dlg = DLG_Impression_recap_factures.Dialog(self, dictOptions={}, tracks=tracks)
        dlg.ShowModal() 
        dlg.Destroy()

    def OnBoutonOk(self, event): 
        """ Aperçu PDF des factures """
        # Validation des données saisies
        tracks = self.ctrl_liste_factures.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à envoyer par Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Création des factures sélectionnées
        listeIDfacture = []
        for track in tracks :
            # Avertissements
            if track.etat == "annulation" : 
                dlg = wx.MessageDialog(self, _(u"La facture n°%s a été annulée.\n\nVous ne pouvez pas l'envoyer par Email !") % track.numero, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Ajout
            listeIDfacture.append(track.IDfacture) 
            
        facturation = UTILS_Facturation.Facturation()
        dictOptions = self.ctrl_options.GetOptions()
        if dictOptions == False :
            return

        resultat = facturation.Impression(listeFactures=listeIDfacture, nomDoc=None, afficherDoc=False, dictOptions=dictOptions, repertoire=dictOptions["repertoire_copie"], repertoireTemp=True)
        if resultat == False : 
            return
        dictChampsFusion, dictPieces = resultat
        
        def SupprimerFichiersTemp():
            for IDfacture, fichier in dictPieces.items() :
                try :
                    os.remove(fichier)  
                except :
                    pass

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
            liste_adresses = []

            if track.email == True :
                # Si Famille inscrite à l'envoi par Email :
                for valeur in track.email_factures.split("##"):
                    IDindividu, categorie, adresse = valeur.split(";")
                    if IDindividu != "" :
                        if int(IDindividu) in dictAdressesIndividus :
                            adresse = dictAdressesIndividus[int(IDindividu)][categorie]
                            liste_adresses.append(adresse)
                    else :
                        liste_adresses.append(adresse)

            else :
                # Si famille non inscrite à l'envoi par Email
                adresse = UTILS_Envoi_email.GetAdresseFamille(track.IDfamille, choixMultiple=False, muet=True, nomTitulaires=track.nomsTitulaires)
                if adresse == False:
                    return False
                liste_adresses.append(adresse)

            # Mémorisation des données
            for adresse in liste_adresses :
                if adresse not in (None, "", []) :
                    if track.IDfacture in dictPieces :
                        fichier = dictPieces[track.IDfacture]
                        champs = dictChampsFusion[track.IDfacture]
                        listeDonnees.append({"adresse" : adresse, "pieces" : [fichier,], "champs" : champs})
                        if track.email == False :
                            if track.nomsTitulaires not in listeEnvoiNonDemande :
                                listeEnvoiNonDemande.append(track.nomsTitulaires)
                else :
                    listeAnomalies.append(track.nomsTitulaires)

        
        # Annonce les anomalies trouvées
        if len(listeAnomalies) > 0 :
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Avertissement"), introduction=u"%d des familles sélectionnées n'ont pas d'adresse Email :" % len(listeAnomalies),
                                        detail=u"".join([u"- %s\n" % nom for nom in listeAnomalies]), conclusion=u"Souhaitez-vous quand même continuer avec les %d autres familles ?" % len(listeDonnees),
                                        icone=wx.ICON_WARNING, boutons=[_(u"Oui"), _(u"Non"), _(u"Annuler")])
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != 0:
                SupprimerFichiersTemp()
                return False

        # Annonce les envois non demandés
        if len(listeEnvoiNonDemande) > 0 :
            texte = _(u"%d des familles sélectionnées n'ont pas demandé d'envoi par Email de leur facture :\n\n") % len(listeEnvoiNonDemande)
            texte += _(u"Souhaitez-vous quand même leur envoyer une facture ?")
            dlg = wx.MessageDialog(self, texte, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                SupprimerFichiersTemp()
                return        
        
        # Dernière vérification avant transfert
        if len(listeDonnees) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Il ne reste finalement aucune facture à envoyer par Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            SupprimerFichiersTemp()
            return

        # Transfert des données vers DLG Mailer
        from Dlg import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self, categorie="facture")
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
