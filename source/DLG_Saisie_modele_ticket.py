#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import wx.gizmos as gizmos

import FonctionsPerso
import GestionDB


CATEGORIES = [
    {"code" : "badgeage_enregistrer", "label" : u"Badgeage - Enregistrement d'une consommation", "motscles" : ["{ID_INDIVIDU}",  "{NOM_INDIVIDU}", "{NOM_ACTIVITE}", "{NOM_UNITE}", "{NOM_GROUPE}", "{DATE}",  "{HEURE}", "{ACTION}"] },
    ] # Code, label, mots-clés




class CTRL_Imprimante(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        import UTILS_Ticket
        listeItems = [u"Imprimante par défaut",]
        try :
            listeImprimantes = UTILS_Ticket.GetListeImprimantes()
            for nom in listeImprimantes :
                listeItems.append(nom)
        except :
            pass
        self.SetItems(listeItems)
                                        
    def SetImprimante(self, nom=None):
        if nom == None :
            self.SetSelection(0)
        else :
            self.SetStringSelection(nom)

    def GetImprimante(self):
        if self.GetSelection() == 0 :
            return None
        else :
            return self.GetStringSelection()



class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="", IDmodele=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.categorie = categorie
        self.IDmodele = IDmodele     
        self.defaut = 0   
        
        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, u"Généralités")
        self.label_nom = wx.StaticText(self, -1, u"Nom :")
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_description = wx.StaticText(self, -1, u"Description :")
        self.ctrl_description = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, u"Options")
        self.label_taille = wx.StaticText(self, -1, u"Taille de police :")
        self.ctrl_taille = wx.SpinCtrl(self, -1, "", size=(60, -1))
        self.ctrl_taille.SetRange(1, 200)
        self.ctrl_taille.SetValue(15)
        self.label_interligne = wx.StaticText(self, -1, u"Interligne :")
        self.ctrl_interligne = wx.SpinCtrl(self, -1, "", size=(60, -1))
        self.ctrl_interligne.SetRange(1, 200)
        self.ctrl_interligne.SetValue(5)
        self.label_imprimante = wx.StaticText(self, -1, u"Imprimante :")
        self.ctrl_imprimante = CTRL_Imprimante(self)

        # Mots-clés
        self.listeMotsCles = []
        for dictCategorie in CATEGORIES :
            if dictCategorie["code"] == self.categorie : 
                self.listeMotsCles = dictCategorie["motscles"]

        self.staticbox_motscles_staticbox = wx.StaticBox(self, -1, u"Mots-clés disponibles")
        self.ctrl_motscles = wx.ListBox(self, -1, choices=self.listeMotsCles, style=wx.SIMPLE_BORDER)
        self.ctrl_motscles.SetBackgroundColour("#F0FBED")
                
        # texte
        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, u"Ticket")
        self.ctrl_editeur = gizmos.EditableListBox(self, -1, u"Saisissez ci-dessous les lignes à imprimer sur le ticket")
        self.ctrl_editeur.GetDelButton().SetToolTipString(u"Supprimer la ligne sélectionnée")
        self.ctrl_editeur.GetDownButton().SetToolTipString(u"Descendre la ligne sélectionnée")
        self.ctrl_editeur.GetUpButton().SetToolTipString(u"Monter la ligne sélectionnée")
        self.ctrl_editeur.GetEditButton().SetToolTipString(u"Editer la ligne sélectionnée")
        self.ctrl_editeur.GetNewButton().SetToolTipString(u"Insérer une nouvelle ligne")
        
        # Commandes
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu= wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Imprimer_ticket_test.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()


##        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnInsertMotcle, self.ctrl_motscles)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDmodele != None :
            self.SetTitle(u"Modification d'un modèle de ticket")
            self.Importation()
        else:
            self.SetTitle(u"Saisie d'un modèle de ticket")
        

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(u"Saisissez un nom pour ce modèle")
        self.ctrl_description.SetToolTipString(u"Saisissez une description pour ce modèle")
        self.ctrl_taille.SetToolTipString(u"Sélectionnez une taille de police")
        self.ctrl_interligne.SetToolTipString(u"Sélectionnez la hauteur d'interligne")
        self.ctrl_imprimante.SetToolTipString(u"Sélectionnez l'imprimante à utiliser")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_apercu.SetToolTipString(u"Cliquez ici pour imprimer une page de test")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((700, 580))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
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

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=12, vgap=5, hgap=5)
        
        grid_sizer_options.Add(self.label_taille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_taille, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_interligne, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_interligne, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_imprimante, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_imprimante, 0, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(7)
        
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Mots-clés
        staticbox_motscles = wx.StaticBoxSizer(self.staticbox_motscles_staticbox, wx.VERTICAL)
        staticbox_motscles.Add(self.ctrl_motscles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_motscles, 1, wx.EXPAND, 0)
        
        # Message
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        grid_sizer_texte = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        grid_sizer_texte.Add(self.ctrl_editeur, 0, wx.EXPAND, 0) 
        grid_sizer_texte.AddGrowableRow(0)
        grid_sizer_texte.AddGrowableCol(0)

        staticbox_texte.Add(grid_sizer_texte, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_texte, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        
##    def OnInsertMotcle(self, event):
##        index = event.GetSelection()
##        motcle = self.listeMotsCles[index]
##        self.ctrl_editeur.EcritTexte(motcle)
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Modlesdetickets")

    def OnBoutonOk(self, event):     
        # Vérification des données
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom pour ce modèle !", "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return        
        
        # Description
        description = self.ctrl_description.GetValue()
        if description == "" :
            dlg = wx.MessageDialog(self, u"Etes-vous sûr de ne pas vouloir saisir de description pour ce modèle ?", u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                return
            dlg.Destroy()
        
        # Récupération du texte
        listeLignes = self.ctrl_editeur.GetStrings() 
        if len(listeLignes) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une ligne !", "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_editeur.SetFocus()
            return     
        
        lignes = u"@@@".join(listeLignes)

        taillePolice = self.ctrl_taille.GetValue() 
        interligne = self.ctrl_interligne.GetValue() 
        imprimante = self.ctrl_imprimante.GetImprimante()
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("categorie", self.categorie),
                ("nom", nom),
                ("description", description),
                ("lignes", lignes),
                ("defaut", self.defaut),
                ("taille", taillePolice),
                ("interligne", interligne),
                ("imprimante", imprimante),
                ]
        if self.IDmodele == None :
            self.IDmodele = DB.ReqInsert("modeles_tickets", listeDonnees)
        else:
            DB.ReqMAJ("modeles_tickets", listeDonnees, "IDmodele", self.IDmodele)
        DB.Close()

        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDmodele(self):
        return self.IDmodele

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT categorie, nom, description, lignes, defaut, taille, interligne, imprimante
        FROM modeles_tickets
        WHERE IDmodele=%d;
        """ % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        categorie, nom, description, lignes, defaut, taille, interligne, imprimante = listeDonnees[0]
        # Importation des valeurs
        self.ctrl_nom.SetValue(nom)
        self.ctrl_description.SetValue(description)
        if taille != None : self.ctrl_taille.SetValue(taille)
        if interligne != None : self.ctrl_interligne.SetValue(interligne)
        listeLignes = lignes.split("@@@")
        self.ctrl_editeur.SetStrings(listeLignes)
        self.defaut = defaut
        self.ctrl_imprimante.SetImprimante(imprimante)
    
    def OnBoutonApercu(self, event=None):
        """ Impression d'un ticket test """
        listeLignes = self.ctrl_editeur.GetStrings() 
        if len(listeLignes) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir une ligne !", "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_editeur.SetFocus()
            return     
        
        taillePolice = self.ctrl_taille.GetValue() 
        interligne = self.ctrl_interligne.GetValue() 
        imprimante = self.ctrl_imprimante.GetImprimante()
        
        try :
            import UTILS_Ticket
            UTILS_Ticket.Impression(lignes=listeLignes, imprimante=imprimante, titre=u"Ticket", nomPolice="Arial", taillePolice=taillePolice, interligne=interligne)
        except Exception, erreur :
            print Exception, erreur
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, categorie="badgeage_enregistrer", IDmodele=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
