#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ol import OL_Prestations
from Utils import UTILS_Dates
import datetime


class CTRL_Annee(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.SetListeDonnees() 
    
    def SetListeDonnees(self):
        self.listeNoms = [_(u"Toutes")]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDprestation, date
        FROM prestations;"""
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
            #self.listeNoms.append(u"%s (%d)" % (annee, nbreReglements))
            self.listeNoms.append(str(annee))
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

class CTRL_Activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.SetListeDonnees() 
    
    def SetListeDonnees(self):
        self.listeLabels = [_(u"Toutes")]
        self.listeID = [None,]
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        dictActivites = {}
        for IDactivite, nom, abrege in listeDonnees :
            self.listeLabels.append(nom)
            self.listeID.append(IDactivite)
        self.SetItems(self.listeLabels)
        self.SetSelection(0)
    
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
        
        intro = _(u"Vous pouvez ici consulter la liste complète des prestations créées dans le logiciel. Les commandes proposées vous permettent de modifier, supprimer ou imprimer des prestations. Pour supprimer un lot de prestations, cochez-les et utilisez le bouton Supprimer.")
        titre = _(u"Liste des prestations")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")

        # Paramètres
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Filtres"))

        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = CTRL_Annee(self)
        self.ctrl_annee.SetMinSize((60, -1))

        self.label_activite = wx.StaticText(self, -1, _(u"Activité :"))
        self.ctrl_activite = CTRL_Activite(self)
        self.ctrl_activite.SetMinSize((200, -1))

        self.label_facture = wx.StaticText(self, -1, _(u"Facturée :"))
        self.ctrl_facture = wx.Choice(self, -1, choices = (_(u"Toutes"), _(u"Oui"), _(u"Non")))
        self.ctrl_facture.Select(0) 
                
        # Liste
        self.listviewAvecFooter = OL_Prestations.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_listview = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Prestations.CTRL_Outils(self, listview=self.ctrl_listview)

        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_annee)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_activite)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_facture)
        
        # Init contrôles
        wx.CallAfter(self.MAJ)

    def __set_properties(self):
        self.SetTitle(_(u"Liste des prestations"))
        self.bouton_ouvrir_fiche.SetToolTipString(_(u"Cliquez ici pour ouvrir la fiche famille de la prestation sélectionnée dans la liste"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour créer un aperçu avant impression de la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer directement la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la prestation sélectionnée dans la liste"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la prestation sélectionnée dans la liste"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((1000, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Paramètres
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=16, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_annee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_annee, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_activite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_activite, 0, 0, 0)
        grid_sizer_options.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_facture, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_facture, 0, 0, 0)
##        grid_sizer_options.AddGrowableCol(4)
        staticbox_options.Add(grid_sizer_options, 0, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(staticbox_options, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Contenu
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
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
    
    def MAJ(self, event=None):
        # Filtre Année
        annee = self.ctrl_annee.GetID() 
        if annee != None :
            self.ctrl_listview.listePeriodes = [(datetime.date(annee, 1, 1), datetime.date(annee, 12, 31)),]
        else :
            self.ctrl_listview.listePeriodes = []
            
        # Filtre Activité
        IDactivite = self.ctrl_activite.GetID() 
        if IDactivite != None :
            self.ctrl_listview.dictFiltres["prestations.IDactivite"] = IDactivite
        else :
            if self.ctrl_listview.dictFiltres.has_key("prestations.IDactivite") :
                del self.ctrl_listview.dictFiltres["prestations.IDactivite"]

        # Filtre Facturé
        facture = self.ctrl_facture.GetSelection() 
        if facture == 0 :
            self.ctrl_listview.dictFiltres["FACTURE_COMPLEXE"] = None
        if facture == 1 :
            self.ctrl_listview.dictFiltres["FACTURE_COMPLEXE"] = "prestations.IDfacture IS NOT NULL"
        if facture == 2 :
            self.ctrl_listview.dictFiltres["FACTURE_COMPLEXE"] = "prestations.IDfacture IS NULL"

        # MAJ de la liste
        attente = wx.BusyInfo(_(u"Recherche des données..."), self)
        self.ctrl_listview.MAJ() 
        attente.Destroy()
        
    def OuvrirFiche(self, event):
        self.ctrl_listview.OuvrirFicheFamille(None)

    def Imprimer(self, event):
        self.ctrl_listview.Imprimer(None)

    def Modifier(self, event):
        self.ctrl_listview.Modifier(None)
        
    def Supprimer(self, event):
        self.ctrl_listview.Supprimer(None)
        
    def Apercu(self, event):
        self.ctrl_listview.Apercu(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesprestations")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
