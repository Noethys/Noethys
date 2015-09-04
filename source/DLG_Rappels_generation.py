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
import CTRL_Bandeau

from DLG_Rappels_generation_parametres import Panel as Page1
from DLG_Rappels_generation_selection import Panel as Page2
from DLG_Rappels_generation_actions import Panel as Page3


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Rappels", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici générer des lettres de rappel. Page 1 : Sélectionnez des paramètres puis cliquez sur Suite pour afficher les rappels disponibles. Page 2 : Cochez les rappels à générer puis cliquez sur Suite. Page 3 : Vous pouvez effectuer d'autres actions sur les lettres de rappel générées.")
        titre = _(u"Génération de lettres de rappel")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Generation.png")
        
        self.listePages = ("Page1", "Page2", "Page3")
        
        self.static_line = wx.StaticLine(self, -1)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_retour = CTRL_Bouton_image.CTRL(self, texte=_(u"Retour"), cheminImage="Images/32x32/Fleche_gauche.png")
        self.bouton_suite = CTRL_Bouton_image.CTRL(self, texte=_(u"Suite"), cheminImage="Images/32x32/Fleche_droite.png", margesImage=(0, 0, 4, 0), positionImage=wx.RIGHT)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        
        self.bouton_retour.Enable(False)
        self.nbrePages = len(self.listePages)    
        self.pageVisible = 1
                        
        # Création des pages
        self.Creation_Pages()        
        
            
    def Creation_Pages(self):
        """ Creation des pages """
        for numPage in range(1, self.nbrePages+1) :
            exec( "self.page" + str(numPage) + " = " + self.listePages[numPage-1] + "(self)" )
            exec( "self.sizer_pages.Add(self.page" + str(numPage) + ", 1, wx.EXPAND, 0)" )
            self.sizer_pages.Layout()
            exec( "self.page" + str(numPage) + ".Show(False)" )
        self.page1.Show(True)
        self.sizer_pages.Layout()

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_retour.SetToolTipString(_(u"Cliquez ici pour revenir à la page précédente"))
        self.bouton_suite.SetToolTipString(_(u"Cliquez ici pour passer à l'étape suivante"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler"))
        self.SetMinSize((750, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Contenu
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        
        self.sizer_pages = sizer_pages
    
    def Onbouton_aide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Gnration1")

    def Onbouton_retour(self, event):
        # rend invisible la page affichée
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible -= 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on quitte l'avant-dernière page, on active le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage("Images/32x32/Fermer.png")
        else:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage("Images/32x32/Fleche_droite.png")
        # Si on revient à la première page, on désactive le bouton Retour
        if self.pageVisible == 1 :
            self.bouton_retour.Enable(False)
        # On active le bouton annuler
        self.bouton_annuler.Enable(True)

    def Onbouton_suite(self, event):
        # Vérifie que les données de la page en cours sont valides
        validation = self.ValidationPages()
        if validation == False : return
        # Si on est déjà sur la dernière page : on termine
        if self.pageVisible == self.nbrePages :
            self.Terminer()
            return
        # Rend invisible la page affichée
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible += 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.MAJ() 
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on arrive à la dernière page, on désactive le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.SetImage("Images/32x32/Fermer.png")
            self.bouton_suite.SetTexte(_(u"Fermer"))
            self.bouton_annuler.Enable(False)
        # Si on quitte la première page, on active le bouton Retour
        if self.pageVisible > 1 :
            self.bouton_retour.Enable(True)
        
        # Désactivation du bouton Retour si dernière page > SPECIAL FACTURATION !!!
        if self.pageVisible == self.nbrePages :            
            self.bouton_retour.Enable(False)

    def ValidationPages(self) :
        """ Validation des données avant changement de pages """
        exec( "validation = self.page" + str(self.pageVisible) + ".Validation()" )
        return validation
    
    def Terminer(self):
        # Fermeture
        self.EndModal(wx.ID_OK)
        
    def SetFamille(self, IDfamille=None):
        self.page1.SetFamille(IDfamille)
        
        
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    IDactivite = 1
    frame_1 = Dialog(None) 
    # TESTS
    frame_1.page1.ctrl_date_reference.SetDate(datetime.date.today())
    
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
