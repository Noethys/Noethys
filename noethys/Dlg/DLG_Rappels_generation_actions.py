#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Ol import OL_Rappels


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Rappels_generation_actions", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Liste de rappels
        self.box_rappels_staticbox = wx.StaticBox(self, -1, _(u"Lettres de rappel"))

        codesColonnes = ["IDrappel", "date_edition", "date_reference", "numero", "famille", "date_min", "date_max", "retard", "email", "solde", "nom_lot", "labelTexte"]
        checkColonne = False
        triColonne = "numero"
        self.ctrl_rappels = OL_Rappels.ListView(self, id=-1, codesColonnes=codesColonnes, checkColonne=checkColonne, triColonne=triColonne, 
                                                                    style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)

        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_email = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu_liste = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer_liste = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        
        # Actions
        self.box_actions_staticbox = wx.StaticBox(self, -1, _(u"Autres actions possibles"))
        
        self.image_fleche1 = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_droite.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_email_lot = CTRL_Bouton_image.CTRL(self, texte=_(u"Transmettre\npar Email"), tailleImage=(32, 32), margesImage=(4, 4, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_imprimer_lot = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), tailleImage=(32, 32), margesImage=(4, 0, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Imprimante.png")
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercuListe, self.bouton_apercu_liste)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerListe, self.bouton_imprimer_liste)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportTexte, self.bouton_export_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportExcel, self.bouton_export_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmailLot, self.bouton_email_lot)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerLot, self.bouton_imprimer_lot)

    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu de la lettre de rappel sélectionnée")))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Cliquez ici envoyer la lettre de rappel sélectionnée par Email")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la lettre de rappel sélectionnée ou les lettres de rappel cochées")))
        self.bouton_apercu_liste.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste")))
        self.bouton_imprimer_liste.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_export_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format texte")))
        self.bouton_export_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_email_lot.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à l'envoi des rappels par Email")))
        self.bouton_imprimer_lot.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer les lettres de rappel générées")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        box_rappels = wx.StaticBoxSizer(self.box_rappels_staticbox, wx.VERTICAL)
        grid_sizer_rappels = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_rappels.Add(self.ctrl_rappels, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)

        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)

        grid_sizer_commandes.Add(self.bouton_apercu_liste, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_imprimer_liste, 0, 0, 0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND, 0)
        
        grid_sizer_commandes.Add(self.bouton_export_texte, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_export_excel, 0, 0, 0)
        grid_sizer_rappels.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_rappels.AddGrowableRow(0)
        grid_sizer_rappels.AddGrowableCol(0)
        box_rappels.Add(grid_sizer_rappels, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_rappels, 1, wx.EXPAND, 0)
        
        # Actions
        box_actions = wx.StaticBoxSizer(self.box_actions_staticbox, wx.VERTICAL)
        
        grid_sizer_actions = wx.FlexGridSizer(rows=1, cols=10, vgap=5, hgap=5)
        grid_sizer_actions.Add(self.bouton_email_lot, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.image_fleche1, 0, wx.EXPAND, 0)
        grid_sizer_actions.Add(self.bouton_imprimer_lot, 0, wx.EXPAND, 0)
        
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
        self.ctrl_rappels.Reedition(None)

    def OnBoutonEmail(self, event): 
        self.ctrl_rappels.EnvoyerEmail(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_rappels.Supprimer(None)

    def OnBoutonApercuListe(self, event): 
        self.ctrl_rappels.Apercu()

    def OnBoutonImprimerListe(self, event): 
        self.ctrl_rappels.Imprimer()

    def OnBoutonExportTexte(self, event): 
        self.ctrl_rappels.ExportTexte()

    def OnBoutonExportExcel(self, event): 
        self.ctrl_rappels.ExportExcel()

    def GetFiltreNumerosRappels(self):
        """ Retourn un filtre par numéro de lettres générées """
        listeNumeros = []
        for track in self.ctrl_rappels.GetTracksTous() :
            listeNumeros.append(track.numero)
        return {"type" : "numero_intervalle", "numero_min" : min(listeNumeros), "numero_max" : max(listeNumeros)}
        
    
    def OnBoutonEmailLot(self, event): 
        """ Envoi par Email des lettres de rappel """
        filtres = [self.GetFiltreNumerosRappels(),]
        # Demande d'application automatique de filtres
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous que Noethys sélectionne automatiquement les lettres de rappels dont les familles souhaitent recevoir leurs factures par Email ?\n\n(Si non, notez que vous pouvez toujours effectuer cette sélection ultérieurement avec les filtres de sélection)"), _(u"Application automatique de filtres"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse == wx.ID_CANCEL :
            return
        if reponse == wx.ID_YES :
            filtres.append({"type" : "email", "choix" : True})
        # Ouverture DLG
        import DLG_Rappels_email
        dlg = DLG_Rappels_email.Dialog(self, filtres=filtres)
        dlg.ShowModal() 
        dlg.Destroy()

    def OnBoutonImprimerLot(self, event): 
        """ Impression des lettres de rappel """
        filtres = [self.GetFiltreNumerosRappels(),]
        # Demande d'application automatique de filtres
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous que Noethys sélectionne automatiquement les lettres de rappel dont les familles ne souhaitent pas recevoir leurs factures par Email ?\n\n(Si non, notez que vous pouvez toujours effectuer cette sélection ultérieurement avec les filtres de sélection)"), _(u"Application automatique de filtres"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse == wx.ID_CANCEL :
            return
        if reponse == wx.ID_YES :
            filtres.append({"type" : "email", "choix" : False})
        # Ouverture DLG
        import DLG_Rappels_impression
        dlg = DLG_Rappels_impression.Dialog(self, filtres=filtres)
        dlg.ShowModal() 
        dlg.Destroy()

    def MAJ(self):
        if len(self.parent.listeRappelsGenerees) > 0 :
            IDrappel_min = min(self.parent.listeRappelsGenerees)
            IDrappel_max = max(self.parent.listeRappelsGenerees)
            self.ctrl_rappels.SetFiltres([{"type" : "IDrappel_intervalle", "IDrappel_min" : IDrappel_min, "IDrappel_max" : IDrappel_max},])
            self.box_rappels_staticbox.SetLabel(_(u"%d lettres de rappel générées") % len(self.parent.listeRappelsGenerees))
        self.ctrl_rappels.MAJ() 
        self.ctrl_rappels.DefilePremier()
        
    def Validation(self):
        return True





class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        panel.listeRappelsGenerees = [96, 97, 98]
        
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
