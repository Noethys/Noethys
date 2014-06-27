#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import CTRL_Bandeau
import OL_Reglements
import GestionDB
import datetime
import UTILS_Dates



class CTRL_Compte(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.dictNumeros = {}
        self.SetListeDonnees() 
        self.SetID(None)
    
    def SetListeDonnees(self):
        self.listeNoms = [u"Tous"]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero
        FROM comptes_bancaires 
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        for IDcompte, nom, numero in listeDonnees :
            self.listeNoms.append(nom)
            self.listeID.append(IDcompte)
            self.dictNumeros[IDcompte] = numero
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    
    def GetNumero(self):
        IDcompte = self.GetID() 
        if IDcompte != None :
            return self.dictNumeros[IDcompte]
        else:
            return None

# ------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Modes(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.SetListeDonnees() 
        self.SetID(None)
    
    def SetListeDonnees(self):
        self.listeNoms = [u"Tous"]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDmode, label
        FROM modes_reglements 
        ORDER BY label;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        for IDmode, nom in listeDonnees :
            self.listeNoms.append(nom)
            self.listeID.append(IDmode)
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    
# ------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Annee(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.SetListeDonnees() 
    
    def SetListeDonnees(self):
        self.listeNoms = [u"Toutes"]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDreglement, date
        FROM reglements;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        dictAnnees = {}
        for IDreglement, date in listeDonnees :
            dateDD = UTILS_Dates.DateEngEnDateDD(date)
            if dateDD != None :
                if dictAnnees.has_key(dateDD.year) == False :
                    dictAnnees[dateDD.year] = 0
                dictAnnees[dateDD.year] += 1
        listeAnnees = dictAnnees.keys() 
        listeAnnees.sort() 
        for annee in listeAnnees :
            nbreReglements = dictAnnees[annee]
            self.listeNoms.append(u"%s (%d)" % (annee, nbreReglements))
            self.listeID.append(annee)
        self.SetItems(self.listeNoms)
        self.SetSelection(len(listeAnnees))
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    
# ------------------------------------------------------------------------------------------------------------------------------------------




class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = u"Vous pouvez ici consulter la liste complète des règlements saisis dans le logiciel."
        titre = u"Liste des règlements"
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Reglement.png")

        # Paramètres
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, u"Filtres")

        self.label_annee = wx.StaticText(self, -1, u"Année :")
        self.ctrl_annee = CTRL_Annee(self)
        self.ctrl_annee.SetMinSize((60, -1))
        
        self.label_compte = wx.StaticText(self, -1, u"Compte :")
        self.ctrl_compte = CTRL_Compte(self)
        self.ctrl_compte.SetMinSize((120, -1))

        self.label_mode = wx.StaticText(self, -1, u"Mode :")
        self.ctrl_mode = CTRL_Modes(self)
        self.ctrl_mode.SetMinSize((120, -1))

        self.label_tri = wx.StaticText(self, -1, u"Tri :")
        self.ctrl_tri = wx.Choice(self, -1, choices = (u"Ordre de saisie", u"Date", u"Mode de règlement", u"Emetteur", u"Numéro de pièce", u"Nom de payeur", "Montant"))
        self.ctrl_tri.Select(1) 
        
        self.label_ordre = wx.StaticText(self, -1, u"Ordre :")
        self.ctrl_ordre = wx.Choice(self, -1, choices = (u"Ascendant", u"Descendant"))
        self.ctrl_ordre.Select(0) 
        
        # Liste
        self.ctrl_reglements = OL_Reglements.ListView(self, id=-1, mode="liste", name="OL_reglements", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_recherche = OL_Reglements.BarreRecherche(self)
        
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))

        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.ctrl_reglements.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_reglements.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_reglements.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_reglements.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_reglements.ExportExcel, self.bouton_excel)

        self.Bind(wx.EVT_BUTTON, self.ctrl_reglements.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_annee)
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_compte)
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_mode)
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_tri)
        self.Bind(wx.EVT_CHOICE, self.OnParametre, self.ctrl_ordre)
        
        # Init contrôles
        self.OnParametre()
        

    def __set_properties(self):
        self.SetTitle(u"Liste des règlements")
        self.ctrl_compte.SetToolTipString(u"Sélectionnez un filtre de compte")
        self.ctrl_mode.SetToolTipString(u"Sélectionnez un filtre de mode de règlement")
        self.ctrl_tri.SetToolTipString(u"Sélectionnez le critère de tri")
        self.ctrl_ordre.SetToolTipString(u"Sélectionnez l'ordre de tri")
        self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier le règlement sélectionné dans la liste")
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer le règlement sélectionné dans la liste")
        self.bouton_apercu.SetToolTipString(u"Cliquez ici pour créer un aperçu de la liste")
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour imprimer la liste")
        self.bouton_texte.SetToolTipString(u"Cliquez ici pour exporter la liste au format Texte")
        self.bouton_excel.SetToolTipString(u"Cliquez ici pour exporter la liste au format Excel")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Paramètres
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=16, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_annee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_annee, 0, wx.EXPAND, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_compte, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_compte, 0, wx.EXPAND, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_mode, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_mode, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_tri, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_tri, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_ordre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_ordre, 0, 0, 0)
        grid_sizer_options.AddGrowableCol(1)
        staticbox_options.Add(grid_sizer_options, 0, wx.EXPAND|wx.ALL, 10)
        
        grid_sizer_base.Add(staticbox_options, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Liste
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.ctrl_reglements, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedesrglements")

    def OnParametre(self, event=None):
        listeFiltres = []
        
        # Année
        annee = self.ctrl_annee.GetID() 
        if annee != None :
            listeFiltres.append("reglements.date>='%d-01-01' and reglements.date<='%d-12-31' " % (annee, annee))
        
        # Compte
        IDcompte = self.ctrl_compte.GetID() 
        if IDcompte != None :
            listeFiltres.append("reglements.IDcompte=%d" % IDcompte)
            
        # Mode
        IDmode = self.ctrl_mode.GetID() 
        if IDmode != None :
            listeFiltres.append("reglements.IDmode=%d" % IDmode)
        
        # Tri
        tri = self.ctrl_tri.GetSelection() 
        if tri == 0 : numColonneTri = 0
        elif tri == 1 : numColonneTri = 1
        elif tri == 2 : numColonneTri = 2
        elif tri == 3 : numColonneTri = 3
        elif tri == 4 : numColonneTri = 4
        elif tri == 5 : numColonneTri = 5
        elif tri == 6 : numColonneTri = 6
        else : numColonneTri = 0
        
        # Ordre
        ordre = self.ctrl_ordre.GetSelection() 
        if ordre == 0 :
            ordreAscendant = True
        else :
            ordreAscendant = False
        
        # Envoi des paramètres au listview
        self.ctrl_reglements.numColonneTri = numColonneTri
        self.ctrl_reglements.ordreAscendant = ordreAscendant
        self.ctrl_reglements.listeFiltres = listeFiltres
        self.ctrl_reglements.MAJ() 
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
