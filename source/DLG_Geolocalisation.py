#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import GestionDB
import UTILS_Gps
import CTRL_Saisie_adresse


class Dialog(wx.Dialog):
    def __init__(self, parent, titre=_(u"Géolocalisation GPS")):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        
        # Bandeau
        intro = _(u"Cette fonctionnalité vous permet d'obtenir les coordonnées GPS d'un lieu. Saisissez une adresse complète ou une ville avant de cliquer sur Rechercher.")
        titre = _(u"Géolocalisation GPS")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Carte.png")
        
        # Recherche
        self.box_recherche_staticbox = wx.StaticBox(self, -1, _(u"Recherche"))
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_ville = wx.StaticText(self, -1, _(u"CP :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)
        self.bouton_rechercher = CTRL_Bouton_image.CTRL(self, texte=_(u"Rechercher"), cheminImage="Images/32x32/Loupe.png")
        
        # Résultats
        self.box_resultats_staticbox = wx.StaticBox(self, -1, _(u"Résultats"))
        self.ctrl_resultats = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonRechercher, self.bouton_rechercher)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_ok)

    def __set_properties(self):
        self.ctrl_rue.SetToolTipString(_(u"Saisissez un nom de rue [Optionnel]"))
        self.bouton_rechercher.SetToolTipString(_(u"Cliquez ici pour lancer la recherche"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((520, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        
        box_recherche = wx.StaticBoxSizer(self.box_recherche_staticbox, wx.VERTICAL)
        grid_sizer_recherche = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_recherche.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_recherche.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add(self.label_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_recherche.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add(self.bouton_rechercher, 0, wx.EXPAND, 0)

        grid_sizer_recherche.AddGrowableCol(1)
        box_recherche.Add(grid_sizer_recherche, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_recherche, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        box_resultats = wx.StaticBoxSizer(self.box_resultats_staticbox, wx.VERTICAL)
        box_resultats.Add(self.ctrl_resultats, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_resultats, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonRechercher(self, event): 
        # Vérification de la saisie
        rue = self.ctrl_rue.GetValue()
        cp = self.ctrl_ville.GetValueCP()
        ville = self.ctrl_ville.GetValueVille()
        if ville == None or ville == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement un nom de ville !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Recherche
        resultats = UTILS_Gps.GPS(rue=rue, cp=cp, ville=ville, pays="France")
        
        # Affichage des résultats
        if resultats == None :
            texte = _(u"Aucun résultat \n")
        else :
            texte = _(u"Lat : %s  Long : %s \n") % (str(resultats["lat"]), str(resultats["long"]))
        self.ctrl_resultats.write(texte)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("GolocalisationGPS")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)



        
        



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
