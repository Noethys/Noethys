#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import wx.lib.agw.aui as aui
from Dlg.DLG_Noedoc import Panel_canvas
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Dialogs



class Track(object):
    def __init__(self, parent=None, donnees=None):
        self.parent = parent
        self.IDproduit = donnees[0]
        self.nom = donnees[1]
        self.observations = donnees[2]
        self.nomCategorie = donnees[3]
        self.quantite = donnees[4]
        if self.quantite == None :
            self.quantite = 1
        self.disponible = int(self.quantite)

        # Recherche si le produit est en cours de location
        # if parent.afficher_locations == True :
        #     if parent.dictLocations.has_key(self.IDproduit):
        #         self.statut = "indisponible"
        #         dictLocation = parent.dictLocations[self.IDproduit]
        #         self.IDfamille = dictLocation["IDfamille"]
        #         self.nomTitulaires = parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        #         self.date_debut = dictLocation["date_debut"]
        #         self.date_fin = dictLocation["date_fin"]
        #     else :
        #         self.statut = "disponible"

        # Recherche si le produit est en cours de location
        if self.IDproduit in parent.dictLocations:
            self.liste_locations = parent.dictLocations[self.IDproduit]
            for dictLocation in self.liste_locations:
                self.disponible -= dictLocation["quantite"]

        # Récupération des réponses des questionnaires
        for dictQuestion in parent.liste_questions :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], parent.GetReponse(dictQuestion["IDquestion"], self.IDproduit))

    def GetTexteInfoBulle(self):
        # Génération du texte de l'infobulle
        texte = u""

        # Location en cours
        if self.disponible > 0 :
            texte += u"Produit disponible (Stock : %d)\n" % self.disponible
        else :
            if len(self.liste_locations) == 1 :
                texte_location = _(u"1 location")
            else :
                texte_location = _(u"%d locations") % len(self.liste_locations)
            texte += u"%s en cours (Quantité louée : %d / Stock : %d) :\n\n" % (texte_location, self.quantite-self.disponible, self.quantite)

            for dictLocation in self.liste_locations:
                IDfamille = dictLocation["IDfamille"]
                if IDfamille in self.parent.dict_titulaires:
                    nomTitulaires = self.parent.dict_titulaires[IDfamille]["titulairesSansCivilite"]
                else :
                    nomTitulaires = _("Titulaires inconnus")
                date_debut = dictLocation["date_debut"]
                date_fin = dictLocation["date_fin"]
                quantite = dictLocation["quantite"]
                if quantite == None :
                    quantite = 1
                date_debut_str = datetime.datetime.strftime(date_debut, "%d/%m/%Y-%Hh%M")
                if date_fin == None:
                    date_fin_str = u"[Illimité]"
                else:
                    date_fin_str = datetime.datetime.strftime(date_fin, "%d/%m/%Y-%Hh%M")

                texte += u"- %s (Du %s au %s, quantité : %d)\n" % (nomTitulaires, date_debut_str, date_fin_str, quantite)

        texte += "\n"

        # Autres informations
        if self.observations not in ("", None) :
            texte += u"Notes : %s\n" % self.observations
        else :
            texte += u"Notes : Aucune\n"

        # Questionnaires
        for dictQuestion in self.parent.liste_questions:
            question = dictQuestion["label"]
            reponse = self.parent.GetReponse(dictQuestion["IDquestion"], self.IDproduit)
            texte += u"%s : %s\n" % (question, reponse)

        dictDonnees = {
            "titre" : u"%s (%s)" % (self.nom, self.nomCategorie),
            "texte" : texte,
            "pied" : u"Double-cliquez pour accéder au détail",
            }
        return dictDonnees

    def GetCouleur(self):
        if self.disponible > 0 :
            return wx.Colour(211, 255, 136)
        else :
            return wx.Colour(255, 135, 125)

    def GetLabel(self):
        return self.nom

    def OnDClickObjet(self, event=None):
        from Dlg import DLG_Fiche_produit
        dlg = DLG_Fiche_produit.Dialog(None, IDproduit=self.IDproduit)
        dlg.ShowModal()
        dirty = dlg.IsDirty()
        dlg.Destroy()
        return dirty




class Data():
    def __init__(self, IDmodele=None):
        self.afficher_locations = True
        self.IDmodele = IDmodele
        if IDmodele != None :
            self.MAJ()

    def GetReponse(self, IDquestion=None, ID=None):
        if IDquestion in self.dict_questionnaires :
            if ID in self.dict_questionnaires[IDquestion] :
                return self.dict_questionnaires[IDquestion][ID]
        return u""

    def MAJ(self):
        import GestionDB
        from Utils import UTILS_Questionnaires
        from Utils import UTILS_Locations
        from Utils import UTILS_Titulaires

        # Importation des titulaires
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Initialisation des questionnaires
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type="produit")
        self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type="produit")

        DB = GestionDB.DB()

        # Importation des locations en cours
        self.dictLocations = UTILS_Locations.GetProduitsLoues(DB=DB)

        # Importation des caractéristiques du modèle
        req = """SELECT categorie, IDdonnee
        FROM documents_modeles
        WHERE IDmodele=%d;""" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.categorie, self.IDdonnee = listeDonnees[0]

        # Importation des produits
        req = """SELECT IDproduit, produits.nom, produits.observations, produits_categories.nom, produits.quantite
        FROM produits
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE produits.IDcategorie=%d;""" % self.IDdonnee
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictTracks = {}
        for item in listeDonnees:
            track = Track(parent=self, donnees=item)
            self.dictTracks[track.IDproduit] = track

        return self.dictTracks

    def GetTrack(self, IDproduit=None):
        if IDproduit in self.dictTracks:
            return self.dictTracks[IDproduit]
        else :
            return None

    def GetTexteInfoBulle(self, IDdonnee=None):
        track = self.GetTrack(IDdonnee)
        if track == None :
            return None
        else :
            return track.GetTexteInfoBulle()


    def GetCouleur(self, IDdonnee=None):
        track = self.GetTrack(IDdonnee)
        if track == None :
            return None
        else :
            return track.GetCouleur()




class CTRL(wx.Panel):
    def __init__(self, parent, IDmodele=None):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.IDmodele = IDmodele

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        # Propriétés
        self.SetMinSize((920, 740))

        # Importation des données
        # interactive_data = Data(IDmodele=IDmodele)
        # categorie = interactive_data.categorie

        # Création des widgets
        couleur_zone_travail = wx.Colour(255, 255, 255)
        self.ctrl_canvas = Panel_canvas(self, IDmodele=self.IDmodele, categorie="", couleur_zone_travail=couleur_zone_travail,
                                        mode="visualisation")#, interactive_data=interactive_data)

        # Barres d'outils
        self.toolbar1 = self.MakeToolBar1()
        self.toolbar2 = self.MakeToolBar2()

        # Création du panel central
        self._mgr.AddPane(self.ctrl_canvas, aui.AuiPaneInfo().Name("canvas").CenterPane())

        # Création des barres d'outils
        self._mgr.AddPane(self.toolbar1, aui.AuiPaneInfo().
                          Name("barreOutil_modes").Caption("Modes").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(True))

        self._mgr.AddPane(self.toolbar2, aui.AuiPaneInfo().
                          Name("barreOutil_outils").Caption("Modes").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(True))

        self._mgr.Update()

        # Init Canvas
        self.ctrl_canvas.Init_canvas()
        self.SendSizeEvent()


    def MAJ(self, IDmodele=False):
        if IDmodele != False :
            self.IDmodele = IDmodele

        if self.IDmodele != None :
            interactive_data = Data(IDmodele=self.IDmodele)
            categorie = interactive_data.categorie

            self.ctrl_canvas.IDmodele = self.IDmodele
            self.ctrl_canvas.interactive_data = interactive_data
            self.ctrl_canvas.categorie = categorie

        # Importation
        if self.IDmodele != None:
            self.ctrl_canvas.Importation(self.IDmodele)

        self.ctrl_canvas.OnOutil_ajuster(None)


    def MakeToolBar1(self):
        tbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbar.SetToolBitmapSize(wx.Size(32, 32))

        ID_OUTIL_CURSEUR = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_CURSEUR, _(u"Curseur"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Curseur.png"), wx.BITMAP_TYPE_ANY), _(u"Curseur"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_curseur, id=ID_OUTIL_CURSEUR)
        tbar.ToggleTool(ID_OUTIL_CURSEUR, True)

        ID_OUTIL_DEPLACER = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_DEPLACER, _(u"Déplacer"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Main.png"), wx.BITMAP_TYPE_ANY), _(u"Déplacer"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_deplacer, id=ID_OUTIL_DEPLACER)

        ID_OUTIL_ZOOM_OUT = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_OUT, _(u"Zoom arrière"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_moins.png"), wx.BITMAP_TYPE_ANY), _(u"Zoom arrière"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_zoom_moins, id=ID_OUTIL_ZOOM_OUT)

        ID_OUTIL_ZOOM_IN = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_IN, _(u"Zoom avant"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_plus.png"), wx.BITMAP_TYPE_ANY), _(u"Zoom avant"), aui.ITEM_RADIO)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_zoom_plus, id=ID_OUTIL_ZOOM_IN)

        tbar.AddSeparator()

        ID_OUTIL_ZOOM_AJUSTER = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_ZOOM_AJUSTER, _(u"Ajuster et centrer l'affichage"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Ajuster.png"), wx.BITMAP_TYPE_ANY), _(u"Ajuster et centrer l'affichage"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnOutil_ajuster, id=ID_OUTIL_ZOOM_AJUSTER)

        tbar.AddSeparator()

        ID_OUTIL_AFFICHAGE_APERCU = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_APERCU, _(u"Afficher un aperçu PDF"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Pdf.png"), wx.BITMAP_TYPE_ANY), _(u"Afficher un aperçu PDF"))
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnAffichage_apercu, id=ID_OUTIL_AFFICHAGE_APERCU)

        tbar.Realize()
        return tbar

    def MakeToolBar2(self):
        tbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tbar.SetToolBitmapSize(wx.Size(32, 32))

        ID_OUTIL_AFFICHAGE_LABELS = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_LABELS, _(u"Afficher les labels associés aux données"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calque_label.png"), wx.BITMAP_TYPE_ANY), _(u"Afficher les labels associés aux données"), aui.ITEM_CHECK)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnAffichage_labels, id=ID_OUTIL_AFFICHAGE_LABELS)
        tbar.ToggleTool(ID_OUTIL_AFFICHAGE_LABELS, True)

        ID_OUTIL_AFFICHAGE_REMPLISSAGE = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_REMPLISSAGE, _(u"Afficher le remplissage des objets associés aux données"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calque_fond.png"), wx.BITMAP_TYPE_ANY), _(u"Afficher le remplissage des objets associés aux données"), aui.ITEM_CHECK)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnAffichage_remplissage, id=ID_OUTIL_AFFICHAGE_REMPLISSAGE)
        tbar.ToggleTool(ID_OUTIL_AFFICHAGE_REMPLISSAGE, True)

        ID_OUTIL_AFFICHAGE_COULEURS = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_COULEURS, _(u"Synchroniser les couleurs du remplissage avec les données"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calque_couleurs.png"), wx.BITMAP_TYPE_ANY), _(u"Synchroniser les couleurs du remplissage avec les données"), aui.ITEM_CHECK)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnAffichage_couleurs, id=ID_OUTIL_AFFICHAGE_COULEURS)
        tbar.ToggleTool(ID_OUTIL_AFFICHAGE_COULEURS, True)

        ID_OUTIL_AFFICHAGE_BORDS = wx.Window.NewControlId()
        tbar.AddSimpleTool(ID_OUTIL_AFFICHAGE_BORDS, _(u"Afficher les bords des objets associés aux données"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calque_bords.png"), wx.BITMAP_TYPE_ANY), _(u"Afficher les bords des objets associés aux données"), aui.ITEM_CHECK)
        self.Bind(wx.EVT_TOOL, self.ctrl_canvas.OnAffichage_bords, id=ID_OUTIL_AFFICHAGE_BORDS)
        tbar.ToggleTool(ID_OUTIL_AFFICHAGE_BORDS, True)

        tbar.Realize()
        return tbar


# -----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDmodele = IDmodele

        dlgAttente = wx.BusyInfo(_(u"Veuillez patienter..."), self.parent)

        self.ctrl_image = CTRL(self, IDmodele=IDmodele)
        self.ctrl_image.SetMinSize((700, 600))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Binds
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Logo
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Image_interactive.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle(u"Visualiseur d'images interactives")

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_image, 1, wx.EXPAND, 0)

        # Layout
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        sizer_base.Add(grid_sizer_boutons, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

        # Init
        self.ctrl_image.MAJ()
        del dlgAttente

    def OnBoutonAnnuler(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Imagesinteractives1")






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmodele=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
