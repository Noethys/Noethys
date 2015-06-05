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
import CTRL_Saisie_date
import OL_Pieces_fournies



class CTRL_Piece(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        if len(self.dictDonnees) > 0 :
            self.Select(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDtype_piece, nom
        FROM types_pieces
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDtype_piece, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDtype_piece, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDlot=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Pieces_fournies", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent  

        # Bandeau
        intro = _(u"Vous pouvez ici afficher la liste des pièces fournies. Commencez par sélectionner le type de pièce à afficher puis cochez la case 'valide' si vous souhaitez afficher uniquement les pièces valides à une date précise.")
        titre = _(u"Liste des pièces fournies")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Piece.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Paramètres"))
        self.label_piece = wx.StaticText(self, wx.ID_ANY, _(u"Pièce :"))
        self.ctrl_piece = CTRL_Piece(self)
        self.ctrl_valide = wx.CheckBox(self, wx.ID_ANY, _(u"Uniquement si valide au :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())
        self.bouton_actualiser = wx.Button(self, wx.ID_ANY, _(u"Actualiser la liste"))
        
        # Liste
        self.ctrl_donnees = OL_Pieces_fournies.ListView(self, id=-1, name="OL_pieces_fournies", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_donnees.MAJ() 
        
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_recherche = OL_Pieces_fournies.CTRL_Outils(self, listview=self.ctrl_donnees)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixPiece, self.ctrl_piece)
        self.Bind(wx.EVT_CHECKBOX, self.OnPieceValide, self.ctrl_valide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init
        self.ctrl_valide.SetValue(True) 
        self.OnPieceValide(None)

    def __set_properties(self):
        self.ctrl_piece.SetToolTipString(_(u"Sélectionnez une pièce dans la liste"))
        self.ctrl_valide.SetToolTipString(_(u"Cochez cette case pour afficher uniquement les pièces valides à la date choisie"))
        self.ctrl_date.SetToolTipString(_(u"Choisissez la date à laquelle les pièces doivent être valides"))
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser la liste en fonction des paramètres sélectionnés"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_excel.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Excel"))
        self.bouton_texte.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Texte"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((750, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        self.box_parametres_staticbox.Lower()
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.HORIZONTAL)

        grid_sizer_parametres = wx.FlexGridSizer(1, 7, 5, 5)
        grid_sizer_parametres.Add(self.label_piece, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_piece, 0, 0, 0)
        grid_sizer_parametres.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.ctrl_valide, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_parametres.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.bouton_actualiser, 0, 0, 0)
        grid_sizer_parametres.AddGrowableCol(5)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        grid_sizer_contenu = wx.FlexGridSizer(2, 2, 5, 5)
        grid_sizer_contenu.Add(self.ctrl_donnees, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(6, 1, 5, 5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 3, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnChoixPiece(self, event): 
        self.MAJ() 

    def OnPieceValide(self, event): 
        self.ctrl_date.Enable(self.ctrl_valide.GetValue())
        self.MAJ() 

    def OnBoutonActualiser(self, event): 
        self.MAJ() 
        
    def MAJ(self):
        IDtype_piece = self.ctrl_piece.GetID() 
        date_reference = None
        if self.ctrl_valide.GetValue() == True :
            date_reference = self.ctrl_date.GetDate() 
            if date_reference == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez renseigner une date de référence !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date.SetFocus() 
                return
        self.ctrl_donnees.MAJ(IDtype_piece=IDtype_piece, date_reference=date_reference)

    def OnBoutonApercu(self, event):  
        self.ctrl_donnees.Apercu()

    def OnBoutonImprimer(self, event):  
        self.ctrl_donnees.Imprimer()

    def OnBoutonExcel(self, event):  
        self.ctrl_donnees.ExportExcel()

    def OnBoutonTexte(self, event): 
        self.ctrl_donnees.ExportTexte()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
