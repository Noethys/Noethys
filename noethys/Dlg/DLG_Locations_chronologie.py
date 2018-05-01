#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import random
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Timeline
from Utils import UTILS_TL_db as TL
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates



class Timeline(TL.TimelinePerso):
    def __init__(self, ):
        TL.TimelinePerso.__init__(self)

    def _load_data(self):
        """ Importation des données """
        self.preferred_period = None
        self.categories = []
        self.events = []

        # Période préférée
        dateDuJour = datetime.datetime.today()
        dateDebut = dateDuJour - datetime.timedelta(6)
        dateFin = dateDuJour + datetime.timedelta(1)
        self.preferred_period = TL.TimePeriod(dateDebut, dateFin)

        # Récupération des events LOCATIONS
        DB = GestionDB.DB()
        req = """SELECT IDlocation, IDfamille, date_debut, date_fin, locations.quantite,
        produits.IDproduit, produits.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        ORDER BY locations.IDproduit;"""
        DB.ExecuterReq(req)
        listeLocations = DB.ResultatReq()
        DB.Close()

        # Préparation des données
        listeIDfamille = []
        dictProduits = {}
        for IDlocation, IDfamille, date_debut, date_fin, quantite, IDproduit, nom_produit in listeLocations:
            listeIDfamille.append(IDfamille)
            if dictProduits.has_key(IDproduit) == False :
                r = random.randint(128, 255)
                v = random.randint(128, 255)
                b = random.randint(128, 255)
                categorie = TL.Category(nom_produit, wx.Colour(r, v, b), True)
                dictProduits[IDproduit] = categorie
        dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille)

        # Création des events
        for IDlocation, IDfamille, date_debut, date_fin, quantite, IDproduit, nom_produit in listeLocations :
            date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
            if date_fin == None :
                date_fin = datetime.datetime(2999, 1, 1)

            if quantite == None :
                quantite = 1

            if dictTitulaires.has_key(IDfamille) :
                nomTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
            else :
                nomTitulaires = _(u"Famille inconnue")

            texte = nomTitulaires
            if quantite > 1 :
                texte += _(u" - Quantité : %d") % quantite
            date_debut_str = datetime.datetime.strftime(date_debut, "%d/%m/%Y-%Hh%M")
            if date_fin.year == 2999:
                date_fin_str = _(u"Illimité")
            else:
                date_fin_str = datetime.datetime.strftime(date_fin, "%d/%m/%Y-%Hh%M")

            description = _(u"Loueur : %s\nProduit : %s\nQuantité : %d\nDébut : %s\nFin : %s") % (nomTitulaires, nom_produit, quantite, date_debut_str, date_fin_str)
            icon = None

            event = TL.Event(date_debut, date_fin, texte, dictProduits[IDproduit])
            event.set_data("IDproduit", IDproduit)
            if description != None: event.set_data("description", description)
            if icon != None: event.set_data("icon", icon)
            self.events.append(event)





class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        # Bandeau
        intro = _(u"Vous pouvez ici consulter les locations sous forme chronologique. Vous pouvez déplacer le graphique vers la droite ou vers la gauche en le faisant glisser avec la souris ou en utilisant sa molette, et basculer entre un affichage annuel, mensuel ou quotidien. Conservez la touche CTRL enfoncée et utilisez la molette pour zoomer.")
        titre = _(u"Chronologie des locations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Timeline.png")
        
        # Timeline
        self.ctrl_timeline = CTRL_Timeline.CTRL(self, 
                            afficheSidebar=False, modele=Timeline(),
                            afficheToolbar=True, positionToolbar="bas",
                            lectureSeule=True,
                            )
        self.ctrl_timeline.SetPositionVerticale(20)
        self.ctrl_timeline.MAJ() 
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Timeline
        grid_sizer_base.Add(self.ctrl_timeline, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()


    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
