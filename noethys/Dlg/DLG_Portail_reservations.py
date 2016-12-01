#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import wx.html as html
import GestionDB
import datetime
from Utils import UTILS_Dialogs
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Grille_facturation
from Dlg import DLG_Badgeage_grille
from Dlg.DLG_Portail_demandes import CTRL_Log


class CTRL_Html(html.HtmlWindow):
    def __init__(self, parent, texte="", couleurFond=(255, 255, 255), style=wx.SIMPLE_BORDER):
        html.HtmlWindow.__init__(self, parent, -1, style=style)  # , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(3)
        self.couleurFond = couleurFond
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetTexte(texte)

    def SetTexte(self, texte=""):
        self.SetPage(u"""<BODY><FONT SIZE=3 COLOR='#000000'>%s</FONT></BODY>""" % texte)
        self.SetBackgroundColour(self.couleurFond)



class Dialog(wx.Dialog):
    def __init__(self, parent, track=None):
        if parent == None :
            dlgparent = None
        else :
            dlgparent = parent.parent
        wx.Dialog.__init__(self, dlgparent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.track = track
        self.reponse = ""

        # Bandeau
        intro = _(u"Vous pouvez gérer ici la demande de façon manuelle. Commencez par cliquer sur le bouton 'Appliquer la demande' pour voir apparaître les modifications demandées dans la grille des conso. Vous pouvez alors effectuer manuellement d'éventuelles modifications avant de valider.")
        titre = _(u"Traitement manuel des réservations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier_modifier.png")

        # Facturation
        self.box_facturation_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Facturation"))
        self.ctrl_facturation = CTRL_Grille_facturation.CTRL(self)
        self.ctrl_facturation.SetMinSize((275, 100))

        # Détail demande
        self.box_demande_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Détail de la demande"))
        self.ctrl_demande = CTRL_Html(self, couleurFond=self.GetBackgroundColour())
        self.ctrl_demande.SetMinSize((275, 100))

        # Grille
        self.box_grille_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Grille des consommations"))
        self.ctrl_grille = DLG_Badgeage_grille.CTRL(self, panel_facturation=self.ctrl_facturation)

        # Journal
        self.box_journal_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Journal d'évènements"))
        self.ctrl_log = CTRL_Log(self)
        self.ctrl_log.SetMinSize((100, 80))
        self.bouton_traiter = CTRL_Bouton_image.CTRL(self, texte=_(u"Appliquer la demande"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_reinit = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler les modifications"), cheminImage="Images/32x32/Actualiser.png")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonTraiter, self.bouton_traiter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)

        # Init
        if self.parent != None :
            self.parent.Init_grille(ctrl_grille=self.ctrl_grille)
            self.ctrl_demande.SetTexte(self.parent.parent.ctrl_description.GetTexte())

    def __set_properties(self):
        self.bouton_traiter.SetToolTipString(_(u"Cliquez ici pour appliquer la demande"))
        self.bouton_reinit.SetToolTipString(_(u"Cliquez ici pour annuler les modifications"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_outils.SetToolTipString(_(u"Cliquez ici pour accéder au menu des outils"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour commencer le traitement des demandes"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1,wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(2, 1, 10, 10)

        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)

        # Grille
        box_grille = wx.StaticBoxSizer(self.box_grille_staticbox, wx.VERTICAL)
        box_grille.Add(self.ctrl_grille, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_haut.Add(box_grille, 1, wx.EXPAND, 10)

        grid_sizer_droit = wx.FlexGridSizer(2, 1, 10, 10)

        # Facturation
        box_facturation = wx.StaticBoxSizer(self.box_facturation_staticbox, wx.VERTICAL)
        box_facturation.Add(self.ctrl_facturation, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_droit.Add(box_facturation, 1, wx.EXPAND, 10)

        # Demande
        box_demande = wx.StaticBoxSizer(self.box_demande_staticbox, wx.VERTICAL)
        box_demande.Add(self.ctrl_demande, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_droit.Add(box_demande, 1, wx.EXPAND, 10)

        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableRow(1)
        grid_sizer_droit.AddGrowableCol(0)

        grid_sizer_haut.Add(grid_sizer_droit, 1, wx.EXPAND, 10)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(0)

        grid_sizer_contenu.Add(grid_sizer_haut, 1, wx.EXPAND, 10)

        # Journal
        box_journal = wx.StaticBoxSizer(self.box_journal_staticbox, wx.VERTICAL)
        grid_sizer_journal = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_journal.Add(self.ctrl_log, 0, wx.EXPAND, 0)

        sizer_boutons = wx.BoxSizer(wx.VERTICAL)
        sizer_boutons.Add(self.bouton_traiter, 1, wx.EXPAND, 0)
        sizer_boutons.Add(self.bouton_reinit, 1, wx.EXPAND | wx.TOP, 5)
        grid_sizer_journal.Add(sizer_boutons, 1, wx.EXPAND, 0)
        
        grid_sizer_journal.AddGrowableRow(0)
        grid_sizer_journal.AddGrowableCol(0)
        box_journal.Add(grid_sizer_journal, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_contenu.Add(box_journal, 1, wx.EXPAND, 10)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 5, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOutils(self, event):
        # Création du menu Outils
        menuPop = wx.Menu()

        item = wx.MenuItem(menuPop, 10, _(u"Recalculer toutes les prestations"), _(u"Recalculer toutes les prestations"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_grille.RecalculerToutesPrestations, id=10)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 20, _(u"Imprimer la liste des réservations"), _(u"Imprimer la liste des réservations affichées"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_grille.grille.Imprimer, id=20)

        item = wx.MenuItem(menuPop, 30, _(u"Envoyer la liste des réservations par Email"), _(u"Envoyer la liste des réservations affichées par Email"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_grille.grille.EnvoyerEmail, id=30)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnBoutonTraiter(self, event):
        self.reponse = self.parent.Appliquer_reservations(ctrl_grille=self.ctrl_grille, log_jumeau=self.ctrl_log)

    def OnBoutonReinit(self, event):
        self.parent.Init_grille(ctrl_grille=self.ctrl_grille)

    def OnBoutonOk(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_OK)

    def GetReponse(self):
        return self.reponse



        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()