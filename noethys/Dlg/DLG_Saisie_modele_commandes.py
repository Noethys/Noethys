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
from Ctrl import CTRL_Bouton_image
import six
import GestionDB
from Data import DATA_Civilites as Civilites
from Ol import OL_Commandes_colonnes

DICT_CIVILITES = Civilites.GetDictCivilites()



class CTRL_Restaurateur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJlisteDonnees()

    def MAJlisteDonnees(self):
        self.SetItems(self.GetListeDonnees())
        self.Select(0)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDrestaurateur, nom
        FROM restaurateurs
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [_(u"Aucun"), ]
        self.dictDonnees = {0: {"ID": None}}
        index = 1
        for IDrestaurateur, nom in listeDonnees:
            self.dictDonnees[index] = {"ID": IDrestaurateur}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]["ID"]


# --------------------------------------------------------------------------------------------------

class Page_Colonnes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_colonnes = OL_Commandes_colonnes.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_colonnes.SetMinSize((150, 100))
        self.ctrl_colonnes.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Descendre, self.bouton_descendre)

        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une colonne")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la colonne sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la colonne sélectionnée dans la liste")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter la colonne sélectionnée dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre la colonne sélectionnée dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_colonnes, 1, wx.EXPAND, 0)

        grid_sizer_droit = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetColonnes(self):
        return self.ctrl_colonnes.GetParametres()

    def GetParametres(self):
        return {"colonnes" : self.ctrl_colonnes.GetParametres()}

    def SetParametres(self, dictParametres={}):
        if type(dictParametres) in (six.text_type, str):
            dictParametres = eval(dictParametres)
        self.ctrl_colonnes.SetParametres(dictParametres)

    def Validation(self):
        if len(self.GetColonnes()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez créer au moins une colonne pour ce modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True


# ----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=None, premierModele=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Modele_commandes", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDmodele = IDmodele
        self.premierModele = premierModele
        self.listeIDcolonnesImportees = []

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom du modèle :"))
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.label_restaurateur = wx.StaticText(self, -1, _(u"Restaurateur :"))
        self.ctrl_restaurateur = CTRL_Restaurateur(self)
        self.bouton_restaurateur = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # Colonnes
        self.box_colonnes_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Colonnes"))
        self.ctrl_colonnes = Page_Colonnes(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRestaurateur, self.bouton_restaurateur)

        # Init Contrôles
        if self.IDmodele == None :
            self.SetTitle(_(u"Saisie d'un modèle de commandes de repas"))
        else :
            self.SetTitle(_(u"Modification d'un modèle de commandes de repas"))
            self.Importation()

        self.ctrl_nom.SetFocus()

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom pour ce modèle")))
        self.ctrl_restaurateur.SetToolTip(wx.ToolTip(_(u"Selectionnez un restaurateur")))
        self.bouton_restaurateur.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des restaurateurs")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((650, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(5, 2, 10, 10)

        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_restaurateur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_restaurateur = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_restaurateur.Add(self.ctrl_restaurateur, 0, wx.EXPAND, 0)
        grid_sizer_restaurateur.Add(self.bouton_restaurateur, 0, 0, 0)
        grid_sizer_restaurateur.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_restaurateur, 1, wx.EXPAND, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)

        # Colonnes
        box_colonnes = wx.StaticBoxSizer(self.box_colonnes_staticbox, wx.VERTICAL)
        box_colonnes.Add(self.ctrl_colonnes, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_colonnes, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

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

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Modelesdecommandesderepas")

    def OnBoutonRestaurateur(self, event):
        IDrestaurateur = self.ctrl_restaurateur.GetID()
        from Dlg import DLG_Restaurateurs
        dlg = DLG_Restaurateurs.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_restaurateur.MAJlisteDonnees()
        self.ctrl_restaurateur.SetID(IDrestaurateur)

    def GetDonnees(self):
        dictDonnees = {}
        dictDonnees["nom"] = self.ctrl_nom.GetValue()
        dictDonnees["IDrestaurateur"] = self.ctrl_restaurateur.GetID()
        dictDonnees.update(self.ctrl_colonnes.GetParametres())
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        self.SetTitle(_(u"Modification d'une colonne"))
        if "nom" in dictDonnees :
            self.ctrl_nom.SetValue(dictDonnees["nom"])
        if "IDrestaurateur" in dictDonnees :
            self.ctrl_restaurateur.SetID(dictDonnees["IDrestaurateur"])
        self.ctrl_colonnes.SetParametres(dictDonnees)

    def Importation(self):
        """ Importation des données """
        DB = GestionDB.DB()

        # Modèle
        req = """SELECT nom, IDrestaurateur, parametres
        FROM modeles_commandes WHERE IDmodele=%d;""" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0:
            nom, IDrestaurateur, parametres = listeDonnees[0]
            self.ctrl_nom.SetValue(nom)
            self.ctrl_restaurateur.SetID(IDrestaurateur)

        # Colonnes
        req = """SELECT modeles_commandes_colonnes.IDcolonne, ordre, nom, largeur, categorie, parametres,
        COUNT(commandes_valeurs.IDvaleur)
        FROM modeles_commandes_colonnes
        LEFT JOIN commandes_valeurs ON commandes_valeurs.IDcolonne = modeles_commandes_colonnes.IDcolonne
        WHERE IDmodele=%d
        GROUP BY modeles_commandes_colonnes.IDcolonne
        ORDER BY ordre;""" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeColonnes = []
        if len(listeDonnees) > 0:
            for IDcolonne, ordre, nom, largeur, categorie, parametres, nbre_valeurs in listeDonnees :
                if type(parametres) in (str, six.text_type):
                    parametres = eval(parametres)
                if nbre_valeurs == None :
                    nbre_valeurs = 0
                listeColonnes.append({"IDcolonne" : IDcolonne, "ordre" : ordre, "nom" : nom, "largeur" : largeur, "categorie" : categorie, "parametres" : parametres, "nbre_valeurs" : nbre_valeurs})
                self.listeIDcolonnesImportees.append(IDcolonne)
        self.ctrl_colonnes.SetParametres(listeColonnes)

        DB.Close()

    def OnBoutonOk(self, event):
        # Validation
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        IDrestaurateur = self.ctrl_restaurateur.GetID()
        if IDrestaurateur == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun restaurateur.\n\nEtes-vous sûr de vouloir continuer ?"), _(u"Information"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        if self.ctrl_colonnes.Validation() == False :
            return False
        colonnes = self.ctrl_colonnes.GetColonnes()

        # Récupération des données
        dictDonnees = self.GetDonnees()

        # Sauvegarde
        DB = GestionDB.DB()

        # Sauvegarde du modèle
        listeDonnees = [
            ("nom", nom),
            ("IDrestaurateur", IDrestaurateur),
            ("parametres", None),
            ]
        if self.premierModele == True :
            listeDonnees.append(("defaut", 1))

        if self.IDmodele == None :
            self.IDmodele = DB.ReqInsert("modeles_commandes", listeDonnees)
        else:
            DB.ReqMAJ("modeles_commandes", listeDonnees, "IDmodele", self.IDmodele)

        # Sauvegarde des colonnes
        index = 0
        listeIDcolonne = []
        dictCorrespondancesID = {}
        for dictColonne in colonnes :
            IDcolonne = dictColonne["IDcolonne"]
            listeDonnees = [
                ("IDmodele", self.IDmodele),
                ("ordre", index),
                ("nom", dictColonne["nom"]),
                ("largeur", dictColonne["largeur"]),
                ("categorie", dictColonne["categorie"]),
                ("parametres", six.text_type(dictColonne["parametres"])),
                ]
            if IDcolonne == None or IDcolonne < 0 :
                newIDcolonne = DB.ReqInsert("modeles_commandes_colonnes", listeDonnees)
                dictCorrespondancesID[IDcolonne] = int(newIDcolonne) # Convertit l'IDnégatif en IDpositif
                dictColonne["IDcolonne"] = newIDcolonne
            else:
                DB.ReqMAJ("modeles_commandes_colonnes", listeDonnees, "IDcolonne", IDcolonne)
            listeIDcolonne.append(IDcolonne)
            index += 1

        # Echange l'IDnégatif contre IDpositif dans les paramètres des colonnes de total
        if len(dictCorrespondancesID) > 0 :
            for dictColonne in colonnes:
                if dictColonne["categorie"] == "numerique_total" and ("colonnes" in dictColonne["parametres"]) == True :
                    listeID = dictColonne["parametres"]["colonnes"]
                    listeNewID = []
                    for IDcolonne in listeID:
                        if IDcolonne < 0 :
                            IDcolonne = dictCorrespondancesID[IDcolonne]
                        listeNewID.append(IDcolonne)
                    if listeID != listeNewID :
                        dictColonne["parametres"]["colonnes"] = listeNewID
                        listeDonnees = [("parametres", six.text_type(dictColonne["parametres"])),]
                        DB.ReqMAJ("modeles_commandes_colonnes", listeDonnees, "IDcolonne", dictColonne["IDcolonne"])

        # Suppression des colonnes obsolètes
        for IDcolonne in self.listeIDcolonnesImportees :
            if IDcolonne not in listeIDcolonne :
                DB.ReqDEL("modeles_commandes_colonnes", "IDcolonne", IDcolonne)
                DB.ReqDEL("commandes_valeurs", "IDcolonne", IDcolonne)

        # Clôture de la base
        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDmodele(self):
        return self.IDmodele






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmodele=4)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
