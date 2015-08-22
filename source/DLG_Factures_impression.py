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

import CTRL_Bandeau
import CTRL_Liste_factures
import CTRL_Factures_options
import UTILS_Facturation



class Dialog(wx.Dialog):
    def __init__(self, parent, filtres=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Cochez les factures à imprimer puis cliquez sur le bouton 'Aperçu' pour visualiser le ou les documents dans votre lecteur PDF.")
        titre = _(u"Impression de factures")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # Factures
        self.box_factures_staticbox = wx.StaticBox(self, -1, _(u"Liste des factures"))
        self.ctrl_liste_factures = CTRL_Liste_factures.CTRL(self, filtres=filtres)
        
        # Options
        self.ctrl_options = CTRL_Factures_options.CTRL(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_recap = CTRL_Bouton_image.CTRL(self, texte=_(u"Récapitulatif"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRecap, self.bouton_recap)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contrôles
        self.ctrl_liste_factures.MAJ() 
                

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_recap.SetToolTipString(_(u"Cliquez ici pour imprimer un récapitulatif des factures cochées dans la liste"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour afficher le PDF"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Factures
        box_factures = wx.StaticBoxSizer(self.box_factures_staticbox, wx.VERTICAL)
        box_factures.Add(self.ctrl_liste_factures, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_factures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        grid_sizer_base.Add(self.ctrl_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_recap, 0, 0, 0)
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
        UTILS_Aide.Aide("Imprimer")

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

        import DLG_Impression_recap_factures
        dlg = DLG_Impression_recap_factures.Dialog(self, dictOptions={}, tracks=tracks)
        dlg.ShowModal() 
        dlg.Destroy()

    def OnBoutonApercu(self, event): 
        """ Aperçu PDF des factures """
        # Validation des données saisies
        tracks = self.ctrl_liste_factures.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        listeIDfacture = []
        for track in tracks :
            # Avertissements
            if track.etat == "annulation" : 
                dlg = wx.MessageDialog(self, _(u"La facture n°%s a été annulée.\n\nVous ne pouvez pas l'imprimer !") % track.numero, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Ajout
            listeIDfacture.append(track.IDfacture) 
        
        # Récupération des options
        dictOptions = self.ctrl_options.GetOptions()
        if dictOptions == False :
            return False
        
##        for nom, valeur in dictOptions.iteritems() :
##            print (nom, valeur) 
            
        # Impression des factures sélectionnées
        facturation = UTILS_Facturation.Facturation()
        facturation.Impression(listeFactures=listeIDfacture, afficherDoc=True, dictOptions=dictOptions, repertoire=dictOptions["repertoire_copie"])
        
    





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
