#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import wx.lib.colourselect as csel

def ConvertCouleur(couleur=None):
    if couleur == None or len(couleur) == 0 : return None
    couleur = couleur[1:-1].split(",")
    couleur = (int(couleur[0]), int(couleur[1]), int(couleur[2]) )
    return couleur


class Dialog(wx.Dialog):
    def __init__(self, parent, type="individu", IDcategorie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent      
        self.type = type
        self.IDcategorie = IDcategorie
        
        self.box_contenu_staticbox = wx.StaticBox(self, -1, u"")
        
        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.ctrl_label.SetMinSize((300, -1)) 
        
        self.label_visible = wx.StaticText(self, -1, _(u"Visible :"))
        self.ctrl_visible = wx.CheckBox(self, -1, u"")
        self.ctrl_visible.SetValue(True) 
        
        self.label_couleur = wx.StaticText(self, -1, _(u"Couleur :"))
        couleur_defaut = (174, 255, 174)
        self.ctrl_couleur = csel.ColourSelect(self, -1, u"", couleur_defaut, size=(60, 20))

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Importation
        if self.IDcategorie != None :
            self.Importation()

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une catégorie"))
        self.ctrl_label.SetToolTipString(_(u"Saisissez ici un label"))
        self.ctrl_couleur.SetToolTipString(_(u"Cliquez ici pour sélectionner la couleur de cette catégorie"))
        self.ctrl_visible.SetToolTipString(_(u"Cochez cette case pour afficher cette catégorie"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        box_contenu = wx.StaticBoxSizer(self.box_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_ligne = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_visible, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ligne.Add(self.ctrl_visible, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ligne.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_ligne.Add(self.label_couleur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ligne.Add(self.ctrl_couleur, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ligne.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_ligne, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        box_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT ordre, visible, type, couleur, label
        FROM questionnaire_categories
        WHERE IDcategorie=%d;
        """ % self.IDcategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        ordre, visible, type, couleur, label = listeDonnees[0]
        self.ctrl_label.SetValue(label) 
        self.ctrl_couleur.SetColour(ConvertCouleur(couleur))
        self.ctrl_visible.SetValue(visible)


    def OnBoutonOk(self, event): 
        label = self.ctrl_label.GetValue() 
        couleur = str(self.ctrl_couleur.GetColour())
        visible = self.ctrl_visible.GetValue() 

        if label == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un label !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Sauvegarde des données
        DB = GestionDB.DB()
        if self.IDcategorie == None :
            # Recherche de l'ordre de la catégorie
            req = """SELECT max(ordre)
            FROM questionnaire_categories;"""
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            ordre = listeTemp[0][0]
            if ordre == None :
                ordre = 0
            listeDonnees = [    
                ("ordre", ordre),
                ("visible", visible),
                ("type", self.type),
                ("couleur", couleur),
                ("label", label),
                ]
            self.IDcategorie = DB.ReqInsert("questionnaire_categories", listeDonnees)
        else:
            listeDonnees = [    
                ("visible", visible),
                ("couleur", couleur),
                ("label", label),
                ]
            DB.ReqMAJ("questionnaire_categories", listeDonnees, "IDcategorie", self.IDcategorie)
        DB.Close()
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetIDcategorie(self):
        return self.IDcategorie
    
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
