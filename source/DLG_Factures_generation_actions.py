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
import datetime
import GestionDB
import OL_Factures
import UTILS_Utilisateurs


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Factures_generation_actions", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Liste de factures
        self.box_factures_staticbox = wx.StaticBox(self, -1, _(u"Factures"))

        codesColonnes = ["IDfacture", "date", "numero", "famille", "prelevement", "email", "total", "solde", "solde_actuel", "date_echeance", "nom_lot"]
        checkColonne = False
        triColonne = "numero"
        self.ctrl_factures = OL_Factures.ListView(self, id=-1, codesColonnes=codesColonnes, checkColonne=checkColonne, triColonne=triColonne, 
                                                                    style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)

        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email_facture = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu_liste = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer_liste = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        
        # Actions
        self.box_actions_staticbox = wx.StaticBox(self, -1, _(u"Autres actions possibles"))
        
        self.image_fleche1 = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Fleche_droite.png", wx.BITMAP_TYPE_ANY))
        self.image_fleche2 = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Fleche_droite.png", wx.BITMAP_TYPE_ANY))
        self.image_fleche3 = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Fleche_droite.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_helios = CTRL_Bouton_image.CTRL(self, texte=_(u"Exporter\nvers Hélios"), tailleImage=(32, 32), margesImage=(4, 0, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Helios.png")
        self.bouton_prelevements = CTRL_Bouton_image.CTRL(self, texte=_(u"Prélèvement\nautomatique"), tailleImage=(32, 32), margesImage=(4, 0, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Prelevement.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Transmettre\npar Email"), tailleImage=(32, 32), margesImage=(4, 4, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), tailleImage=(32, 32), margesImage=(4, 0, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Imprimante.png")
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmailFacture, self.bouton_email_facture)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercuListe, self.bouton_apercu_liste)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerListe, self.bouton_imprimer_liste)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportTexte, self.bouton_export_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportExcel, self.bouton_export_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonPrelevements, self.bouton_prelevements)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHelios, self.bouton_helios)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)

    def __set_properties(self):
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour afficher un aperçu de la facture sélectionnée"))
        self.bouton_email_facture.SetToolTipString(_(u"Cliquez ici envoyer la facture sélectionnée par Email"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la facture sélectionnée ou les factures cochées"))
        self.bouton_apercu_liste.SetToolTipString(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste"))
        self.bouton_imprimer_liste.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_export_texte.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format texte"))
        self.bouton_export_excel.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Excel"))
        self.bouton_prelevements.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des prélèvements automatiques"))
        self.bouton_email.SetToolTipString(_(u"Cliquez ici pour accéder à l'envoi des factures par Email"))
        self.bouton_helios.SetToolTipString(_(u"Cliquez ici pour accéder à l'export HELIOS des factures"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer les factures générées"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        box_factures = wx.StaticBoxSizer(self.box_factures_staticbox, wx.VERTICAL)
        grid_sizer_factures = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_factures.Add(self.ctrl_factures, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_email_facture, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)

        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)

        grid_sizer_commandes.Add(self.bouton_apercu_liste, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_imprimer_liste, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)
        
        grid_sizer_commandes.Add(self.bouton_export_texte, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_export_excel, 0, 0, 0)
        grid_sizer_factures.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_factures.AddGrowableRow(0)
        grid_sizer_factures.AddGrowableCol(0)
        box_factures.Add(grid_sizer_factures, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_factures, 1, wx.EXPAND, 0)
        
        # Actions
        box_actions = wx.StaticBoxSizer(self.box_actions_staticbox, wx.VERTICAL)
        
        grid_sizer_actions = wx.FlexGridSizer(rows=1, cols=10, vgap=5, hgap=5)
        grid_sizer_actions.Add(self.bouton_helios, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.image_fleche1, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.bouton_prelevements, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.image_fleche2, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.bouton_email, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.image_fleche3, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.bouton_imprimer, 0, wx.EXPAND, 0)
        
        box_actions.Add(grid_sizer_actions, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_actions.AddGrowableCol(0)
        grid_sizer_actions.AddGrowableCol(2)
        grid_sizer_actions.AddGrowableCol(4)
        grid_sizer_actions.AddGrowableCol(6)
        
        grid_sizer_base.Add(box_actions, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonApercu(self, event): 
        self.ctrl_factures.Reedition(None)

    def OnBoutonEmailFacture(self, event): 
        self.ctrl_factures.EnvoyerEmail(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_factures.Supprimer(None)

    def OnBoutonApercuListe(self, event): 
        self.ctrl_factures.Apercu()

    def OnBoutonImprimerListe(self, event): 
        self.ctrl_factures.Imprimer()

    def OnBoutonExportTexte(self, event): 
        self.ctrl_factures.ExportTexte()

    def OnBoutonExportExcel(self, event): 
        self.ctrl_factures.ExportExcel()

    def GetFiltreNumerosFactures(self):
        """ Retourn un filtre par numéro de factures générées """
        listeNumeros = []
        for track in self.ctrl_factures.GetTracksTous() :
            listeNumeros.append(track.numero)
        return {"type" : "numero_intervalle", "numero_min" : min(listeNumeros), "numero_max" : max(listeNumeros)}
        
    def OnBoutonPrelevements(self, event): 
        """ Gestion des prélèvements """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_prelevements", "consulter") == False : return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_prelevements", "creer") == False : return
        
        # Demande d'application automatique de filtres
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous utiliser l'assistant de préparation des lots de prélèvements automatiques (Conseillé) ?\n\nSinon, le gestionnaire des prélèvements sera simplement ouvert."), _(u"Prélèvement automatique"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse == wx.ID_CANCEL :
            return
        # Ouverture DLG
        import DLG_Lots_prelevements
        dlg = DLG_Lots_prelevements.Dialog(self)
        if reponse == wx.ID_YES :
            filtres = [
                self.GetFiltreNumerosFactures(),
                {"type" : "solde_actuel", "operateur" : "<", "montant" : 0.0},
                {"type" : "prelevement", "choix" : True},
                ]
            dlg.Assistant(filtres=filtres, nomLot=self.parent.dictParametres["nomLot"])
        dlg.ShowModal() 
        dlg.Destroy()

    def OnBoutonHelios(self, event):
        """ Export vers Helios """ 
        import UTILS_Pes
        choix = UTILS_Pes.DemanderChoix(self)
        
        if choix == "rolmre" :
            
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "creer") == False : return
            import DLG_Export_helios
            filtres = [
                self.GetFiltreNumerosFactures(),
                ]
            dlg = DLG_Export_helios.Dialog(self, filtres=filtres)
            dlg.ShowModal() 
            dlg.Destroy()

        if choix == "pes" :
            
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "consulter") == False : return
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "creer") == False : return
            
            # Demande d'application automatique de filtres
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous utiliser l'assistant de préparation des bordereaux PES (Conseillé) ?\n\nSinon, le gestionnaire des bordereaux PES sera simplement ouvert."), _(u"Hélios"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse == wx.ID_CANCEL :
                return
            # Ouverture DLG
            import DLG_Lots_pes
            dlg = DLG_Lots_pes.Dialog(self)
            if reponse == wx.ID_YES :
                filtres = [
                    self.GetFiltreNumerosFactures(),
                    ]
                dlg.Assistant(filtres=filtres, nomLot=self.parent.dictParametres["nomLot"])
            dlg.ShowModal() 
            dlg.Destroy()


    def OnBoutonEmail(self, event): 
        """ Envoi par Email des factures """
        filtres = [self.GetFiltreNumerosFactures(),]
        # Demande d'application automatique de filtres
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous que Noethys sélectionne automatiquement les factures dont les familles souhaitent recevoir leurs factures par Email ?\n\n(Si non, notez que vous pouvez toujours effectuer cette sélection ultérieurement avec les filtres de sélection)"), _(u"Application automatique de filtres"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse == wx.ID_CANCEL :
            return
        if reponse == wx.ID_YES :
            filtres.append({"type" : "email", "choix" : True})
        # Ouverture DLG
        import DLG_Factures_email
        dlg = DLG_Factures_email.Dialog(self, filtres=filtres)
        dlg.ShowModal() 
        dlg.Destroy()

    def OnBoutonImprimer(self, event): 
        """ Impression des factures """
        filtres = [self.GetFiltreNumerosFactures(),]
        # Demande d'application automatique de filtres
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous que Noethys sélectionne automatiquement les factures dont les familles ne souhaitent pas recevoir leurs factures par Email ?\n\n(Si non, notez que vous pouvez toujours effectuer cette sélection ultérieurement avec les filtres de sélection)"), _(u"Application automatique de filtres"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse == wx.ID_CANCEL :
            return
        if reponse == wx.ID_YES :
            filtres.append({"type" : "email", "choix" : False})
        # Ouverture DLG
        import DLG_Factures_impression
        dlg = DLG_Factures_impression.Dialog(self, filtres=filtres)
        dlg.ShowModal() 
        dlg.Destroy()

    def MAJ(self):
        if len(self.parent.listeFacturesGenerees) > 0 :
            IDfacture_min = min(self.parent.listeFacturesGenerees)
            IDfacture_max = max(self.parent.listeFacturesGenerees)
            self.ctrl_factures.SetFiltres([{"type" : "IDfacture_intervalle", "IDfacture_min" : IDfacture_min, "IDfacture_max" : IDfacture_max},])
            self.box_factures_staticbox.SetLabel(_(u"%d factures générées") % len(self.parent.listeFacturesGenerees))
        self.ctrl_factures.MAJ() 
        self.ctrl_factures.DefilePremier()
        
    def Validation(self):
        return True





class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        panel.listeFacturesGenerees = range(2800, 2910)
        
        self.ctrl = Panel(panel)
        self.ctrl.MAJ() 
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        print "Validation =", self.ctrl.Validation()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
