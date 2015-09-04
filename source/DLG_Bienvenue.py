#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.html as html
import FonctionsPerso
import CTRL_Liste_fichiers



VERSION_LOGICIEL = FonctionsPerso.GetVersionLogiciel()

TEXTE_ACCUEIL = u"""
<BR>
<B><FONT SIZE=10>Bienvenue !</B></FONT><BR>
<BR><BR>
<FONT SIZE=3>
Bienvenue dans Noethys, le logiciel libre et gratuit de gestion multi-activit�s pour les accueils de 
loisirs, cr�ches, cantines, garderies p�riscolaires, secteurs jeunes, activit�s sportives et culturelles, etc...
Pour d�couvrir toutes les fonctionnalit�s du logiciel, suivre l'�volution du projet, 
ou �changer sur le forum d'entraide, consultez le site d�di� <A HREF="Saisie">www.noethys.com</A>.
<BR><BR>
Si vous utilisez Noethys pour la premi�re fois, il vous est recommand� de charger 
d�s � pr�sent un des fichiers exemples propos�s ci-dessous dont les donn�es fictives vous permettront
d'appr�hender rapidement les principales fonctionnalit�s du logiciel.
(Notez que vous pourrez toujours le faire plus tard depuis le menu Fichier > Ouvrir un fichier)
</FONT>
""" 



class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetPage(texte)
        couleurFond = wx.SystemSettings.GetColour(30)
        self.SetBackgroundColour(couleurFond)
    
    def OnLinkClicked(self, link):
        FonctionsPerso.LanceFichierExterne(_(u"http://www.noethys.com"))
        

class MargeGauche(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="marge_gauche", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.SetBackgroundColour("#548410")
        
        # Image de gauche
        self.image = wx.StaticBitmap(self, -1, wx.Bitmap("Images/Special/LogoMargeGauche.png", wx.BITMAP_TYPE_ANY))


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        
        # Marge gauche
        self.margeGauche = MargeGauche(self)
        
        # Txt HTML
        self.ctrl_html = MyHtml(self, texte=TEXTE_ACCUEIL, hauteur=230)
        
        # Liste Fichiers exemples
        self.label_fichiers = wx.StaticText(self, -1, _(u"S�lectionnez un fichier exemple puis cliquez sur Ok :"))
        self.label_fichiers.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.ctrl_fichiers = CTRL_Liste_fichiers.CTRL(self, prefixe="EXEMPLE_", details=False, mode="local")
        self.ctrl_fichiers.SetMinSize((-1, 100))
        
        # Boutons de commande
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnBoutonOk, self.ctrl_fichiers)


    def __set_properties(self):
        self.SetTitle(_(u"Bienvenue"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour ouvrir le fichier s�lectionn� dans la liste"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour fermer cette fen�tre"))
        self.SetMinSize((800, 640))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        
        # Marge gauche
        grid_sizer_base.Add(self.margeGauche, 1, wx.EXPAND, 0)
        
        # Grid sizer droit
        grid_sizer_droit = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_droit.Add(self.ctrl_html, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_droit.Add(self.label_fichiers, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_droit.Add(self.ctrl_fichiers, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_droit.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_droit.AddGrowableRow(2)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        index = self.ctrl_fichiers.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun fichier dans la liste !\n\nSi vous ne souhaitez pas ouvrir de fichier maintenant, cliquez sur le bouton Fermer. Vous pourrez le faire ult�rieurement depuis le menu Fichier > Ouvrir un fichier."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 
        self.EndModal(wx.ID_OK)
    
    def GetNomFichier(self):
        index = self.ctrl_fichiers.GetFirstSelected()
        dictItem = self.ctrl_fichiers.GetItemPyData(index)
        nomFichier = dictItem["titre"]
        nomFichier = nomFichier.decode("iso-8859-15")
        return nomFichier





if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    if dlg.ShowModal() == wx.ID_OK :
        print dlg.GetNomFichier() 
    dlg.Destroy() 
    app.MainLoop()
