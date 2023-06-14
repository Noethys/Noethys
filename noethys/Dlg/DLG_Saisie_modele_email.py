#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import FonctionsPerso
import GestionDB

from Ctrl import CTRL_Editeur_email







class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="", IDmodele=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.categorie = categorie
        self.IDmodele = IDmodele     
        self.defaut = 0   
        
        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_description = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_description = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Mots-clés
        self.listeMotsCles = []
        listeMotscles = CTRL_Editeur_email.GetMotscles(self.categorie)
        for motCle, code in listeMotscles :
            self.listeMotsCles.append(motCle)

        self.staticbox_motscles_staticbox = wx.StaticBox(self, -1, _(u"Mots-clés disponibles"))
        self.ctrl_motscles = wx.ListBox(self, -1, choices=self.listeMotsCles, style=wx.SIMPLE_BORDER)
        self.ctrl_motscles.SetBackgroundColour("#F0FBED")
        
        # Expéditeur
        self.label_exp = wx.StaticText(self, -1, _(u"Expéditeur :"))
        self.ctrl_exp = CTRL_Editeur_email.Panel_Expediteur(self)
        
        # Objet
        self.label_objet = wx.StaticText(self, -1, _(u"Objet :"))
        self.ctrl_objet = wx.TextCtrl(self, -1, u"")
        
        # texte
        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, _(u"Message"))
        self.ctrl_editeur = CTRL_Editeur_email.CTRL(self)
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()


        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnInsertMotcle, self.ctrl_motscles)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDmodele != None :
            self.SetTitle(_(u"Modification d'un modèle d'Email"))
            self.Importation()
        else:
            self.SetTitle(_(u"Saisie d'un modèle d'Email"))
        

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom pour ce modèle")))
        self.ctrl_description.SetToolTip(wx.ToolTip(_(u"Saisissez une description pour ce modèle [Optionnel]")))
        self.ctrl_objet.SetToolTip(wx.ToolTip(_(u"Saisissez l'objet du message")))
        self.ctrl_motscles.SetToolTip(wx.ToolTip(_(u"Double-cliquez sur un mot-clé pour l'insérer dans le texte\nou recopiez-le directement (avec ses accolades).")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((700, 580))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_description, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_description, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Mots-clés
        staticbox_motscles = wx.StaticBoxSizer(self.staticbox_motscles_staticbox, wx.VERTICAL)
        staticbox_motscles.Add(self.ctrl_motscles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_motscles, 1, wx.EXPAND, 0)
        
        # Message
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        grid_sizer_texte = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_objet = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_objet.Add(self.label_exp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_objet.Add(self.ctrl_exp, 0, wx.EXPAND, 0)
        grid_sizer_objet.Add(self.label_objet, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_objet.Add(self.ctrl_objet, 0, wx.EXPAND, 0)
        grid_sizer_objet.AddGrowableCol(1)
        grid_sizer_texte.Add(grid_sizer_objet, 1, wx.EXPAND|wx.BOTTOM, 10)
        
        grid_sizer_texte.Add(self.ctrl_editeur, 0, wx.EXPAND, 0) 
        grid_sizer_texte.AddGrowableRow(1)
        grid_sizer_texte.AddGrowableCol(0)

        staticbox_texte.Add(grid_sizer_texte, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_texte, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
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
        
    def OnInsertMotcle(self, event):
        index = event.GetSelection()
        motcle = self.listeMotsCles[index]
        self.ctrl_editeur.EcritTexte(motcle)
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("ModlesdEmails")

    def OnBoutonOk(self, event):     
        # Vérification des données
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce modèle !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return        
        
        # Description
        description = self.ctrl_description.GetValue()

        # Adresse Exp
        IDadresse = self.ctrl_exp.GetID()
        if IDadresse == None :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir sélectionner d'adresse d'expéditeur pour ce modèle ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                return
            dlg.Destroy()

        # Objet
        objet = self.ctrl_objet.GetValue()
        if objet == "" :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir saisir d'objet de message pour ce modèle ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                return
            dlg.Destroy()
        
        # Récupération du texte
        texteStr = self.ctrl_editeur.GetValue() 
        texteXML = self.ctrl_editeur.GetXML()
        if len(texteStr) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_editeur.SetFocus()
            return     

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("categorie", self.categorie),
                ("nom", nom),
                ("description", description),
                ("objet", objet),
                ("texte_xml", texteXML),
                ("IDadresse", IDadresse),
                ("defaut", self.defaut),
                ]
        if self.IDmodele == None :
            self.IDmodele = DB.ReqInsert("modeles_emails", listeDonnees)
        else:
            DB.ReqMAJ("modeles_emails", listeDonnees, "IDmodele", self.IDmodele)
        DB.Close()

        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDmodele(self):
        return self.IDmodele

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT categorie, nom, description, objet, texte_xml, IDadresse, defaut
        FROM modeles_emails
        WHERE IDmodele=%d;
        """ % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        categorie, nom, description, objet, texte_xml, IDadresse, defaut = listeDonnees[0]
        # Importation des valeurs
        self.ctrl_nom.SetValue(nom)
        self.ctrl_description.SetValue(description)
        self.ctrl_objet.SetValue(objet)
        if texte_xml != None :
            self.ctrl_editeur.SetXML(texte_xml)
        self.ctrl_exp.SetID(IDadresse)
        self.defaut = defaut


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, categorie="releve_prestations", IDmodele=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
