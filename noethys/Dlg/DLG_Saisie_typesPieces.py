#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Vignettes_documents


class Dialog(wx.Dialog):
    def __init__(self, parent, IDtype_piece=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent      
        self.SetTitle(_(u"Saisie d'un type de pièce"))
        self.IDtype_piece = IDtype_piece
        
        self.sizer_nom_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.label_public = wx.StaticText(self, -1, _(u"Public :"))
        self.ctrl_public = wx.Choice(self, -1, (100, -1), choices = ("Individu", "Famille"))
        self.ctrl_rattachement = wx.CheckBox(self, -1, u"")
        self.label_rattachement = wx.StaticText(self, -1, _(u"Cochez cette case si, lorsqu'un individu est rattaché à plusieurs \nfamilles, cette pièce est valable pour toutes les familles rattachées."))
        
        self.sizer_duree_staticbox = wx.StaticBox(self, -1, _(u"Validité par défaut"))
        
        self.radio_duree_1 = wx.RadioButton(self, -1, _(u"Validité illimitée"), style=wx.RB_GROUP)
        
        self.radio_duree_2 = wx.RadioButton(self, -1, _(u"La durée suivante : "))
        self.label_jours = wx.StaticText(self, -1, _(u"Jours :"))
        self.spin_jours = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.spin_mois = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_annees = wx.StaticText(self, -1, _(u"Années :"))
        self.spin_annees = wx.SpinCtrl(self, -1, "", min=0, max=100)
        
        self.radio_duree_3 = wx.RadioButton(self, -1, _(u"La date suivante : "))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)

        # Pages capturées
        self.sizer_pages_staticbox = wx.StaticBox(self, -1, _(u"Documents associés"))
        self.ctrl_pages = CTRL_Vignettes_documents.CTRL(self, type_donnee="type_piece", IDtype_piece=self.IDtype_piece, style=wx.BORDER_SUNKEN)
        self.ctrl_pages.SetMinSize((160, 280))
        self.bouton_ajouter_page = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_page = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser_page = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_zoom_plus = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_plus.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_zoom_moins = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_moins.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoice_public, self.ctrl_public)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_3)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.AjouterPage, self.bouton_ajouter_page)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.SupprimerPage, self.bouton_supprimer_page)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.VisualiserPage, self.bouton_visualiser_page)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.ZoomPlus, self.bouton_zoom_plus)
        self.Bind(wx.EVT_BUTTON, self.ctrl_pages.ZoomMoins, self.bouton_zoom_moins)

        self.OnChoice_public(None)
        self.OnRadioDuree(None)

        # Importation
        if self.IDtype_piece != None :
            self.Importation()


    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici un nom de pièce. Par exemple : 'Fiche sanitaire'")))
        self.ctrl_public.SetToolTip(wx.ToolTip(_(u"Sélectionnez le public auquel cette pièce s'adresse")))
        self.radio_duree_1.SetToolTip(wx.ToolTip(_(u"Sélectionnez 'Illimitée' si la pièce est valable à vie")))
        self.radio_duree_2.SetToolTip(wx.ToolTip(_(u"Sélectionnez 'Durée' si vous souhaitez définir une durée de validité pour cette pièce")))
        self.radio_duree_3.SetToolTip(wx.ToolTip(_(u"Sélectionnez 'Date' si la pièce n'est valable que jusqu'à une date précise")))
        self.spin_jours.SetMinSize((60, -1))
        self.spin_mois.SetMinSize((60, -1))
        self.spin_annees.SetMinSize((60, -1))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        sizer_nom = wx.StaticBoxSizer(self.sizer_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(self.label_public, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_public, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add((10, 10), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_rattachement = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_rattachement.Add(self.ctrl_rattachement, 0, wx.EXPAND, 0)
        grid_sizer_rattachement.Add(self.label_rattachement, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(grid_sizer_rattachement, 0, wx.EXPAND, 0)
        
        grid_sizer_nom.AddGrowableCol(1)
        sizer_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(sizer_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 0)
        
        sizer_duree = wx.StaticBoxSizer(self.sizer_duree_staticbox, wx.VERTICAL)
        
        # Illimitée
        grid_sizer_duree1 = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_duree1.Add(self.radio_duree_1, 0, 0, 0)
                
        # Durée
        grid_sizer_duree2 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree2.Add(self.radio_duree_2, 0, 0, 0)
        grid_sizer_duree1.Add(grid_sizer_duree2, 1, wx.EXPAND, 0)

        grid_sizer_duree3 = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_duree3.Add(self.label_jours, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree3.Add(self.spin_jours, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_mois, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_mois, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_annees, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_annees, 0, 0, 0)
        
        grid_sizer_duree2.Add(grid_sizer_duree3, 1, wx.LEFT|wx.EXPAND, 20)
        
        # Date
        grid_sizer_duree4 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree4.Add(self.radio_duree_3, 0, 0, 0)
        grid_sizer_duree1.Add(grid_sizer_duree4, 1, wx.EXPAND, 0)
        
        grid_sizer_duree4.Add(self.ctrl_date, 1, wx.LEFT|wx.EXPAND, 20)
        
        sizer_duree.Add(grid_sizer_duree1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(sizer_duree, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)


        # Pages
        sizer_pages = wx.StaticBoxSizer(self.sizer_pages_staticbox, wx.VERTICAL)

        grid_sizer_pages = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_pages.Add(self.ctrl_pages, 0, wx.EXPAND, 0)
        grid_sizer_pages.AddGrowableRow(0)
        grid_sizer_pages.AddGrowableCol(0)

        grid_sizer_commandes_pages = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes_pages.Add(self.bouton_ajouter_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_supprimer_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add( (10, 10), 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_visualiser_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add( (10, 10), 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_zoom_plus, 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_zoom_moins, 0, 0, 0)
        grid_sizer_pages.Add(grid_sizer_commandes_pages, 1, wx.EXPAND, 0)

        sizer_pages.Add(grid_sizer_pages, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_contenu.Add(sizer_pages, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)

        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
        self.SetMinSize(self.GetSize())
    
    def OnChoice_public(self, event):
        if self.ctrl_public.GetSelection() == 0 :
            self.ctrl_rattachement.Enable(True)
            self.label_rattachement.Enable(True)
        else:
            self.ctrl_rattachement.Enable(False)
            self.label_rattachement.Enable(False)
        
    def OnRadioDuree(self, event):
        self.label_jours.Enable(self.radio_duree_2.GetValue())
        self.spin_jours.Enable(self.radio_duree_2.GetValue())
        self.label_mois.Enable(self.radio_duree_2.GetValue())
        self.spin_mois.Enable(self.radio_duree_2.GetValue())
        self.label_annees.Enable(self.radio_duree_2.GetValue())
        self.spin_annees.Enable(self.radio_duree_2.GetValue())
        self.ctrl_date.Enable(self.radio_duree_3.GetValue())
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Typesdepices")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement donner un nom à cette pièce !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        if self.ctrl_public.GetSelection() == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner le public !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_public.SetFocus()
            return

        jours = int(self.spin_jours.GetValue())
        mois = int(self.spin_mois.GetValue())
        annees = int(self.spin_annees.GetValue())
        date = self.ctrl_date.GetDate() 

        if jours == 0 and mois == 0 and annees == 0 and self.radio_duree_2.GetValue() == True:
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné une durée de pièce limitée. \nVous devez donc saisir un nombre de jours et/ou de mois et/ou d'années."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.spin_jours.SetFocus()
            return

        if date == None and self.radio_duree_3.GetValue() == True:
            dlg = wx.MessageDialog(self, _(u"La date de fin de validité n'est pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return

        # Sauvegarde
        public = self.GetPublic()
        rattachement = self.GetRattachement()
        validite = self.GetValidite()

        DB = GestionDB.DB()
        listeDonnees = [("nom", nom ), ("public", public ), ("valide_rattachement", rattachement ), ("duree_validite", validite),]
        if self.IDtype_piece == None :
            self.IDtype_piece = DB.ReqInsert("types_pieces", listeDonnees)
        else :
            DB.ReqMAJ("types_pieces", listeDonnees, "IDtype_piece", self.IDtype_piece)
        DB.Close()

        # Sauvegarde des pages scannées
        self.ctrl_pages.Sauvegarde(self.IDtype_piece)

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT nom, public, duree_validite, valide_rattachement
        FROM types_pieces WHERE IDtype_piece=%d; """ % self.IDtype_piece
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        nom, public, duree_validite, valide_rattachement = listeDonnees[0]

        self.ctrl_nom.SetValue(nom)
        self.SetPublic(public)
        self.SetValidite(duree_validite)
        self.SetRattachement(valide_rattachement)


    def GetValidite(self):
        if self.radio_duree_1.GetValue() == True:
            return None
        if self.radio_duree_2.GetValue() == True:
            return "j%d-m%d-a%d" % (int(self.spin_jours.GetValue()), int(self.spin_mois.GetValue()), int(self.spin_annees.GetValue()),)
        if self.radio_duree_3.GetValue() == True:
            return "d%s" % str(self.ctrl_date.GetDate())

    def SetValidite(self, validite=None):
        if validite == None or validite == "j0-m0-a0" :
            self.radio_duree_1.SetValue(True)

        elif validite != None and validite.startswith("j") :
            posM = validite.find("m")
            posA = validite.find("a")
            self.spin_jours.SetValue(int(validite[1:posM-1]))
            self.spin_mois.SetValue(int(validite[posM+1:posA-1]))
            self.spin_annees.SetValue(int(validite[posA+1:]))
            self.radio_duree_2.SetValue(True)

        elif validite != None and validite.startswith("d") :
            self.ctrl_date.SetDate(validite[1:])
            self.radio_duree_3.SetValue(True)

        self.OnRadioDuree(None)
    
    def GetPublic(self):
        if self.ctrl_public.GetSelection() == 0 : return "individu"
        if self.ctrl_public.GetSelection() == 1 : return "famille"
        return None

    def SetPublic(self, public):
        if public == "individu" : self.ctrl_public.SetSelection(0)
        if public == "famille" : self.ctrl_public.SetSelection(1)
        self.OnChoice_public(None)
    
    def GetRattachement(self):
        if self.GetPublic() == "individu" :
            return int(self.ctrl_rattachement.GetValue())
        else:
            return None

    def SetRattachement(self, valeur):
        if valeur == 1 :
            self.ctrl_rattachement.SetValue(True)

    def GetIDtype_piece(self):
        return self.IDtype_piece



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDtype_piece=3)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
