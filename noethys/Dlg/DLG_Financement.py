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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import FonctionsPerso
import webbrowser
import random
import datetime


def Affiche_assistance():
    try :
        topWindow = wx.GetApp().GetTopWindow()
        if topWindow.GetName() == "general":
            if topWindow.EstFichierExemple() == True:
                return False
    except :
        pass

    try:
        IDfichier = FonctionsPerso.GetIDfichier()
        anciennete = datetime.datetime.today() - datetime.datetime.strptime(IDfichier[:8], "%Y%m%d")
        if anciennete.days / 365 >= 4:
            return True
    except:
        pass

    return False




# --------------------------------------------------------------------------------------------------

class CTRL_Titre(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Titre
        self.label_titre = wx.StaticText(self, -1, _(u"Aller\nplus loin\navec\nNoethys"), style=wx.ALIGN_CENTER)

        # Propriétés
        # self.SetBackgroundColour(wx.BLACK)
        # self.label_titre.SetForegroundColour(wx.WHITE)
        self.label_titre.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))

        # Layout
        # sizer_base = wx.BoxSizer(wx.VERTICAL)
        # sizer_base.Add(self.label_titre, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER, 0)
        # self.SetSizer(sizer_base)

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_titre, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER, 0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()



# --------------------------------------------------------------------------------------------------

class Page_documentation(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Annonce_documentation.jpg"), wx.BITMAP_TYPE_ANY)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Bon de commande"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour en savoir plus sur le manuel de référence")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer le bon de commande et les conditions générales de vente")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize()
        hauteurBouton = self.bouton_imprimer.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_base.Add((largeurImage, hauteurEspaceHaut), 0, 0, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT | wx.EXPAND, 30)

        grid_sizer_base.Add((largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)

        # Calcule taille de la fenêtre
        self.SetMinSize(self.image_fond.GetSize())
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Init
        self.bouton_fermer.SetFocus()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        url = "https://www.noethys.com/index.php/presentation/2013-09-08-15-48-17/programme-de-financement"
        webbrowser.open(url)

    def OnBoutonImprimer(self, event):
        try:
            FonctionsPerso.LanceFichierExterne("https://noethys.com/public/bon_commande_documentation.pdf")
        except:
            dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas ouvrir le PDF !\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."),_(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()





# --------------------------------------------------------------------------------------------------

class Page_connecthys(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Annonce_connecthys.jpg"), wx.BITMAP_TYPE_ANY)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Bon de commande"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour en savoir plus sur Connecthys Easy")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer le bon de commande et les conditions générales de vente")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize()
        hauteurBouton = self.bouton_imprimer.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_base.Add((largeurImage, hauteurEspaceHaut), 0, 0, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT | wx.EXPAND, 30)

        grid_sizer_base.Add((largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)

        # Calcule taille de la fenêtre
        self.SetMinSize(self.image_fond.GetSize())
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Init
        self.bouton_fermer.SetFocus()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        url = "https://www.connecthys.com"
        webbrowser.open(url)

    def OnBoutonImprimer(self, event):
        try:
            FonctionsPerso.LanceFichierExterne("https://www.connecthys.com/bon_commande_connecthys.pdf")
        except:
            dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas ouvrir le PDF !\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."),_(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()




# --------------------------------------------------------------------------------------------------

class Page_noethysweb(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Annonce_nweb.jpg"), wx.BITMAP_TYPE_ANY)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Bon de commande"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour en savoir plus sur Noethysweb Easy")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer le bon de commande et les conditions générales de vente")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize()
        hauteurBouton = self.bouton_imprimer.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_base.Add((largeurImage, hauteurEspaceHaut), 0, 0, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT | wx.EXPAND, 30)

        grid_sizer_base.Add((largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)

        # Calcule taille de la fenêtre
        self.SetMinSize(self.image_fond.GetSize())
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Init
        self.bouton_fermer.SetFocus()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        url = "https://www.noethysweb.com"
        webbrowser.open(url)

    def OnBoutonImprimer(self, event):
        try:
            FonctionsPerso.LanceFichierExterne("https://www.noethysweb.com/bon_commande_noethysweb.pdf")
        except:
            dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas ouvrir le PDF !\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."),_(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()


# --------------------------------------------------------------------------------------------------

class Page_formations(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Annonce_formations.jpg"), wx.BITMAP_TYPE_ANY)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour en savoir plus sur les formations")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize()
        hauteurBouton = self.bouton_aide.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_base.Add((largeurImage, hauteurEspaceHaut), 0, 0, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT | wx.EXPAND, 30)

        grid_sizer_base.Add((largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)

        # Calcule taille de la fenêtre
        self.SetMinSize(self.image_fond.GetSize())
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Init
        self.bouton_fermer.SetFocus()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        url = "https://www.noethys.com/index.php/assistance2/2015-07-19-17-22-35/les-formations"
        webbrowser.open(url)



# --------------------------------------------------------------------------------------------------

class Page_developpement(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Annonce_developpement.jpg"), wx.BITMAP_TYPE_ANY)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour en savoir plus")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize()
        hauteurBouton = self.bouton_aide.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_base.Add((largeurImage, hauteurEspaceHaut), 0, 0, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT | wx.EXPAND, 30)

        grid_sizer_base.Add((largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)

        # Calcule taille de la fenêtre
        self.SetMinSize(self.image_fond.GetSize())
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Init
        self.bouton_fermer.SetFocus()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        dlg = wx.MessageDialog(None, _(u"Pour en savoir davantage sur les développements, consultez le concepteur de Noethys depuis le menu Aide > Envoyer un email à l'auteur."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()




# --------------------------------------------------------------------------------------------------

class Page_assistance(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Annonce_assistance.jpg"), wx.BITMAP_TYPE_ANY)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Bon de commande"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour en savoir plus")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer le bon de commande et les conditions générales de vente")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize()
        hauteurBouton = self.bouton_imprimer.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_base.Add((largeurImage, hauteurEspaceHaut), 0, 0, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT | wx.EXPAND, 30)

        grid_sizer_base.Add((largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)

        # Calcule taille de la fenêtre
        self.SetMinSize(self.image_fond.GetSize())
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Init
        self.bouton_fermer.SetFocus()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        self.OnBoutonImprimer(None)

    def OnBoutonImprimer(self, event):
        try:
            FonctionsPerso.LanceFichierExterne("https://noethys.com/public/bon_commande_assistance.pdf")
        except:
            dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas ouvrir le PDF !\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."),_(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()






# --------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, code=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.CAPTION)
        self.parent = parent
        self.SetTitle(_(u"L'offre de services de Noethys"))
        #self.ctrl_titre = CTRL_Titre(self)

        self.liste_pages = [
            {"code": "documentation", "titre" : _(u"Documentation"), "page" : Page_documentation(self), "image": 'Images/32x32/Livre.png'},
            {"code": "connecthys", "titre": _(u"Connecthys Easy"), "page": Page_connecthys(self), "image": 'Images/32x32/Connecthys.png'},
            {"code": "noethysweb", "titre": _(u"Noethysweb Easy"), "page": Page_noethysweb(self), "image": 'Images/32x32/Noethysweb.png'},
            {"code": "formations", "titre": _(u"Formations"), "page": Page_formations(self), "image": 'Images/32x32/Classe.png'},
            {"code": "developpement", "titre": _(u"Développement"), "page": Page_developpement(self), "image": 'Images/32x32/Questionnaire.png'},
        ]

        if Affiche_assistance():
            self.liste_pages.append({"code": "assistance", "titre": _(u"Assistance"), "page": Page_assistance(self), "image": 'Images/32x32/Assistance.png'})

        self.liste_boutons = []
        index = 0
        for item in self.liste_pages:
            id = 1000+index
            if index > 0:
                item["page"].Show(False)
            bouton = CTRL_Bouton_image.CTRL(self, id=id, texte=item["titre"], cheminImage=item["image"], tailleImage=(32, 32), margesImage=(40, 20, 40, 0), positionImage=wx.TOP, margesTexte=(10, 10))
            self.Bind(wx.EVT_BUTTON, self.OnBouton, bouton, id=id)
            self.liste_boutons.append(bouton)
            index += 1

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer_h = wx.BoxSizer(wx.HORIZONTAL)

        # Création des boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        #grid_sizer_boutons.Add(self.ctrl_titre, 1, wx.EXPAND, 0)
        for bouton in self.liste_boutons:
            grid_sizer_boutons.Add(bouton, 0, wx.EXPAND, 0)
        sizer_h.Add(grid_sizer_boutons, 0, wx.EXPAND | wx.ALL, 5)
        # grid_sizer_boutons.AddGrowableRow(0)

        # Création des pages
        self.sizer_pages = wx.BoxSizer(wx.VERTICAL)
        for item in self.liste_pages:
            self.sizer_pages.Add(item["page"], 0, wx.EXPAND, 0)
        sizer_h.Add(self.sizer_pages, 1, wx.EXPAND, 0)

        sizer.Add(sizer_h, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.CenterOnScreen()

        # Init
        if code != None:
            self.SetPageActive(code)
        else:
            self.SetPageAleatoire()

    def OnBouton(self, event):
        index = event.GetId() - 1000
        self.SetSelection(index)

    def SetSelection(self, selection=0):
        index = 0
        for item in self.liste_pages:
            item["page"].Show(index == selection)
            index += 1
        self.sizer_pages.Layout()
        self.liste_pages[0]["page"].SetFocus()

    def SetPageActive(self, code="documentation"):
        index = 0
        for item in self.liste_pages :
            if item["code"] == code :
                self.SetSelection(index)
            index += 1

    def SetPageAleatoire(self):
        index = random.randint(0, len(self.liste_pages)-1)
        self.SetSelection(index)



    
if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal() 
    dlg.Destroy()
    app.MainLoop()
