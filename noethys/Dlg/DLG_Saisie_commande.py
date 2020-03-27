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
import wx.html as html
from Ctrl import CTRL_Bouton_image
import datetime
import FonctionsPerso
import sys
import six
import GestionDB
from Utils import UTILS_Organisateur
from Utils import UTILS_Divers
from Utils import UTILS_Dates
from Utils import UTILS_Dialogs
from Utils import UTILS_Images
from Data import DATA_Civilites as Civilites
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Commande_repas
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Dlg import DLG_Options_impression_pdf
from Ctrl import CTRL_Propertygrid
import wx.propgrid as wxpg

DICT_CIVILITES = Civilites.GetDictCivilites()

DICT_INFOS_IMPRESSION = {}



# -------------------------------------------------------------------------------------

class Track_total(object):
    def __init__(self, donnees):
        self.IDcolonne = donnees["IDcolonne"]
        self.nom_colonne = donnees["nom_colonne"]
        self.valeur = donnees["valeur"]
        self.isTotal = donnees["isTotal"]


class OL_Totaux(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        self.SendSizeEvent()

    def SetColonnes(self, listeDonnees = []):
        self.listeDonnees = listeDonnees
        self.MAJ()

    def SetValeurs(self, dictValeurs={}):
        listeTracksModifies = []
        for track in self.donnees :
            if track.IDcolonne in dictValeurs:
                if track.valeur != dictValeurs[track.IDcolonne]:
                    track.valeur = dictValeurs[track.IDcolonne]
                    listeTracksModifies.append(listeTracksModifies)
                    self.RefreshObject(track)

    def InitModel(self):
        self.donnees = []
        for dictDonnee in self.listeDonnees :
            self.donnees.append(Track_total(dictDonnee))

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = wx.Colour(255, 255, 255)
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def rowFormatter(listItem, track):
            if track.isTotal == True :
                listItem.SetBackgroundColour(wx.Colour(240, 240, 240))
                font = listItem.GetFont()
                font.SetWeight(wx.FONTWEIGHT_BOLD)
                font.SetPointSize(9)
                listItem.SetFont(font)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "", typeDonnee="texte"),
            ColumnDefn(_(u"Nom"), "left", 170, "nom_colonne", typeDonnee="texte"),
            ColumnDefn(_(u"valeur"), "center", 50, "valeur", typeDonnee="texte"),
        ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune donnée"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetObjects(self.donnees)

    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()





class CTRL_Infos(html.HtmlWindow):
    def __init__(self, parent):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SUNKEN_BORDER|wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((200, -1))

    def MAJ(self):
        listeTemp = []

        if ("restaurateur_nom" in self.parent.dictDonnees) == True :
            restaurateur_nom = self.parent.dictDonnees["restaurateur_nom"]
            restaurateur_tel = self.parent.dictDonnees["restaurateur_tel"]
            restaurateur_mail = self.parent.dictDonnees["restaurateur_mail"]

            if restaurateur_nom not in (None, "") :
                listeTemp.append(u"<B>%s</B>" % restaurateur_nom)
            else :
                listeTemp.append(_(u"<B>Restaurateur<BR>non renseigné</B>"))
            if restaurateur_tel not in (None, "") :
                listeTemp.append(restaurateur_tel)
        else :
            listeTemp.append(u"<B>Restaurateur<BR>non renseigné</B>")

        texte = u"""
        <CENTER>
        <BR><BR>
        <IMG SRC="%s"><BR>
        <FONT SIZE=2>
        %s
        </FONT> 
        </CENTER>
        """ % (Chemins.GetStaticPath("Images/32x32/Restaurateur.png"), "<BR>".join(listeTemp))
        self.SetPage(texte)


class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=None, IDcommande=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_commande", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDmodele = IDmodele
        self.IDcommande = IDcommande
        self.dictDonnees = {}
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.label_periode = wx.StaticText(self, wx.ID_ANY, _(u"Période :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.label_observations = wx.StaticText(self, wx.ID_ANY, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        self.ctrl_observations.SetMinSize((270, -1))

        # Infos
        self.box_infos_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Restaurateur"))
        self.ctrl_infos = CTRL_Infos(self)

        # Totaux
        self.box_totaux_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Totaux"))
        self.ctrl_totaux = OL_Totaux(self, id=-1, style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.ctrl_totaux.SetMinSize((250, 50))

        # Repas
        self.box_repas_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Données"))
        self.ctrl_repas = CTRL_Commande_repas.CTRL(self, IDmodele=IDmodele, IDcommande=IDcommande)
        self.ctrl_repas.SetMinSize((100, 380))

        # Légende
        self.listeLegende = [
            {"label": _(u"Cases modifiables"), "couleur": CTRL_Commande_repas.COULEUR_CASES_OUVERTES, "ctrl_label": None, "ctrl_img": None},
            {"label": _(u"Cases non modifiables"), "couleur": CTRL_Commande_repas.COULEUR_CASES_FERMEES, "ctrl_label": None, "ctrl_img": None},
            ]
        index = 0
        for dictTemp in self.listeLegende :
            img = wx.StaticBitmap(self, -1, UTILS_Images.CreationCarreCouleur(12, 12, dictTemp["couleur"], contour=True))
            label = wx.StaticText(self, -1, dictTemp["label"])
            label.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.listeLegende[index]["ctrl_img"] = img
            self.listeLegende[index]["ctrl_label"] = label
            index += 1

        self.image_info = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Astuce.png"), wx.BITMAP_TYPE_ANY))
        self.label_info = wx.StaticText(self, -1, _(u"Double-cliquez pour modifier ou faites un clic droit pour ouvrir le menu contextuel ou utilisez le copier-coller (Ctrl+C puis Ctrl+V)"))
        self.label_info.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Init
        if self.IDcommande == None :
            self.SetTitle(_(u"Saisie d'une commande de repas"))
        else :
            self.SetTitle(_(u"Modification d'une commande de repas"))

        self.Importation()
        self.ctrl_infos.MAJ()
        self.MAJ()

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom pour cette commande (Ex : 'Vacances de Pâques 2018')")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de la période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de la période")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez des observations")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux outils")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la commande au format PDF")))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer la commande par Email")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        #self.SetMinSize((650, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_haut = wx.FlexGridSizer(1, 3, 10, 10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(5, 2, 10, 10)

        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_periode, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_periode = wx.FlexGridSizer(1, 4, 5, 5)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(grid_sizer_periode, 1, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_generalites, 1, wx.EXPAND, 0)

        # Infos
        box_infos = wx.StaticBoxSizer(self.box_infos_staticbox, wx.VERTICAL)
        box_infos.Add(self.ctrl_infos, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_infos, 1, wx.EXPAND, 0)

        # Totaux
        box_totaux = wx.StaticBoxSizer(self.box_totaux_staticbox, wx.VERTICAL)
        box_totaux.Add(self.ctrl_totaux, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_totaux, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(0)

        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)

        # Repas
        box_repas = wx.StaticBoxSizer(self.box_repas_staticbox, wx.VERTICAL)
        grid_sizer_repas = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_repas.Add(self.ctrl_repas, 1, wx.EXPAND, 0)

        # Légende
        grid_sizer_legende = wx.FlexGridSizer(rows=1, cols=len(self.listeLegende)*3 + 3, vgap=4, hgap=4)

        grid_sizer_legende.Add(self.image_info, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_legende.Add(self.label_info, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        for dictTemp in self.listeLegende :
            grid_sizer_legende.Add((5, 5), 0, 0, 0)
            grid_sizer_legende.Add(dictTemp["ctrl_img"], 0, wx.ALIGN_CENTER_VERTICAL, 0)
            grid_sizer_legende.Add(dictTemp["ctrl_label"], 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_legende.AddGrowableCol(2)
        grid_sizer_repas.Add(grid_sizer_legende, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)

        grid_sizer_repas.AddGrowableRow(0)
        grid_sizer_repas.AddGrowableCol(0)
        box_repas.Add(grid_sizer_repas, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_repas, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=7, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(4)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def OnChoixDate(self):
        self.MAJ()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Commandesdesrepas")

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Importer les suggestions
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menuPop, id, _(u"Convertir les suggestions"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Magique.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_repas.Importer_suggestions, id=id)

        menuPop.AppendSeparator()

        # RAZ
        id = wx.Window.NewControlId()
        item = wx.MenuItem(menuPop, id, _(u"Vider les données"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_repas.RAZ, id=id)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def MAJ(self):
        self.ctrl_repas.MAJ(date_debut=self.ctrl_date_debut.GetDate(), date_fin=self.ctrl_date_fin.GetDate())

    def Importation(self):
        """ Importation des données """
        if self.IDmodele == None :
            IDmodele = 0
        else :
            IDmodele = self.IDmodele

        DB = GestionDB.DB()

        # Commande
        if self.IDcommande != None :

            req = """SELECT IDmodele, nom, date_debut, date_fin, observations
            FROM commandes 
            WHERE IDcommande=%d;""" % self.IDcommande
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0:
                IDmodele, nom, date_debut, date_fin, observations = listeDonnees[0]
                self.IDmodele = IDmodele
                self.ctrl_nom.SetValue(nom)
                date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
                date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
                self.ctrl_date_debut.SetDate(date_debut)
                self.ctrl_date_fin.SetDate(date_fin)
                self.ctrl_observations.SetValue(observations)

        # Modèle
        req = """SELECT modeles_commandes.nom, modeles_commandes.IDrestaurateur, parametres,
        restaurateurs.nom, restaurateurs.tel, restaurateurs.mail
        FROM modeles_commandes 
        LEFT JOIN restaurateurs ON restaurateurs.IDrestaurateur = modeles_commandes.IDrestaurateur
        WHERE IDmodele=%d;""" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0:
            nom_modele, IDrestaurateur, parametres, restaurateur_nom, restaurateur_tel, restaurateur_mail = listeDonnees[0]
            if type(parametres) in (str, six.text_type) :
                parametres = eval(parametres)

            self.dictDonnees["modele_nom"] = nom_modele
            self.dictDonnees["modele_parametres"] = parametres
            self.dictDonnees["IDrestaurateur"] = IDrestaurateur
            self.dictDonnees["restaurateur_nom"] = restaurateur_nom
            self.dictDonnees["restaurateur_tel"] = restaurateur_tel
            self.dictDonnees["restaurateur_mail"] = restaurateur_mail

        # Colonnes
        req = """SELECT IDcolonne, ordre, nom, largeur, categorie, parametres
        FROM modeles_commandes_colonnes 
        WHERE IDmodele=%d
        ORDER BY ordre;""" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeColonnes = []
        if len(listeDonnees) > 0:
            for IDcolonne, ordre, nom, largeur, categorie, parametres in listeDonnees :
                if type(parametres) in (str, six.text_type):
                    parametres = eval(parametres)
                listeColonnes.append({"IDcolonne" : IDcolonne, "ordre" : ordre, "nom" : nom, "largeur" : largeur, "categorie" : categorie, "parametres" : parametres})
        self.dictDonnees["colonnes"] = listeColonnes

        DB.Close()

    def OnClose(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        event.Skip()

    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        # Validation de la saisie
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette commande !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        # validation des dates
        date_debut = self.ctrl_date_debut.GetDate()
        if self.ctrl_date_debut.Validation() == False or date_debut == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        date_fin = self.ctrl_date_fin.GetDate()
        if self.ctrl_date_fin.Validation() == False or date_fin == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas saisir une date de début supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        observations = self.ctrl_observations.GetValue()

        # Sauvegarde de la commande
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDmodele", self.IDmodele),
            ("nom", nom),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("observations", observations),
            ]
        if self.IDcommande == None :
            self.IDcommande = DB.ReqInsert("commandes", listeDonnees)
        else:
            DB.ReqMAJ("commandes", listeDonnees, "IDcommande", self.IDcommande)

        # Sauvegarde des repas
        self.ctrl_repas.Sauvegarde(IDcommande=self.IDcommande)

        # Clôture de la base
        DB.Close()

        # Fermeture de la fenêtre
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_OK)

    def GetIDcommande(self):
        return self.IDcommande

    def OnBoutonEmail(self, event):
        restaurateur_mail = self.ctrl_repas.GetDonnees()["restaurateur_mail"]
        if restaurateur_mail in ("", None) :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord renseigner l'adresse mail du restaurateur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, nomDoc=FonctionsPerso.GenerationNomDoc("COMMANDE_REPAS", "pdf"), categorie="commande_repas", listeAdresses=[restaurateur_mail,])

    def Imprimer(self, event=None):
        self.CreationPDF()

    def CreationPDF(self, nomDoc=FonctionsPerso.GenerationNomDoc("COMMANDE_REPAS", "pdf"), afficherDoc=True):
        dictChampsFusion = {}

        # Récupération des données
        nom_commande = self.ctrl_nom.GetValue()
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        observations = self.ctrl_observations.GetValue()
        dictDonnees = self.ctrl_repas.GetDonnees()

        # Récupération des options d'impression
        global DICT_INFOS_IMPRESSION
        DICT_INFOS_IMPRESSION = {"date_debut" : date_debut, "date_fin" : date_fin}
        dlg = DLG_Options_impression_pdf.Dialog(self, categorie="commande_repas", ctrl=CTRL_Options_impression)
        if dlg.ShowModal() == wx.ID_OK:
            dictOptions = dlg.GetOptions()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return False

        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle

        if dictOptions["orientation"] == "portrait" :
            largeur_page, hauteur_page = A4
        else:
            hauteur_page, largeur_page = A4

        # Initialisation du PDF
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30)
        story = []

        largeurContenu = largeur_page - 75

        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (largeurContenu-100, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Commande des repas"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 16),
                    ('ALIGN', (1,0), (1,0), 'RIGHT'),
                    ('FONT',(1,0),(1,0), "Helvetica", 6),
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0, 10))

        # Insère un header
        Header()

        # Insère le nom et la période de la commande
        style_titre_commande = ParagraphStyle(name="1", alignment=1, fontName="Helvetica-Bold", fontSize=dictOptions["taille_texte_titre"], leading=8, spaceAfter=14)
        story.append(Paragraph(_(u"<para>%s - Du %s au %s</para>") % (nom_commande, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin)), style_titre_commande))

        # Styles
        style_entete = ParagraphStyle(name="1", alignment=1, fontName="Helvetica-Bold", fontSize=dictOptions["taille_texte"], leading=8, spaceAfter=2)
        style_numerique = ParagraphStyle(name="2", alignment=2, fontName="Helvetica", fontSize=dictOptions["taille_texte"], leading=8, spaceAfter=2)
        style_total = ParagraphStyle(name="3", alignment=2, fontName="Helvetica-Bold", fontSize=dictOptions["taille_texte"], leading=8, spaceAfter=2)
        style_texte = ParagraphStyle(name="4", alignment=0, fontName="Helvetica", fontSize=dictOptions["taille_texte"], leading=8, spaceAfter=2)

        # Calcule des largeurs de colonne
        largeur_colonne_date = dictOptions["largeur_colonne_date"]

        largeur_colonnes = largeurContenu - largeur_colonne_date
        dictLargeurs = {}

        if dictOptions["largeur_colonnes_auto"] == True :
            total_largeurs_colonnes = 0
            for dictColonne in dictDonnees["liste_colonnes"] :
                total_largeurs_colonnes += dictColonne["largeur"]
            for dictColonne in dictDonnees["liste_colonnes"] :
                dictLargeurs[dictColonne["IDcolonne"]] = 1.0 * dictColonne["largeur"] / total_largeurs_colonnes * largeur_colonnes

        # Dessin du tableau de données
        dataTableau = []
        largeursColonnes = [largeur_colonne_date,]

        # Dessin des noms de colonnes
        ligne = [Paragraph(_(u"Date"), style_entete),]
        for dictColonne in dictDonnees["liste_colonnes"] :
            valeur = dictColonne["nom_colonne"]
            ligne.append(Paragraph(valeur, style_entete))
            if dictColonne["IDcolonne"] in dictLargeurs:
                largeur = dictLargeurs[dictColonne["IDcolonne"]]
            else :
                largeur = dictColonne["largeur"] / 1.5
            largeursColonnes.append(largeur)
        dataTableau.append(ligne)

        # Dessin des lignes
        dict_totaux_colonnes = {}
        for numLigne in range(0, len(dictDonnees["liste_dates"])):
            ligne = []

            # Ajout de la date à la ligne
            date = dictDonnees["liste_dates"][numLigne]

            afficher_ligne = True
            if dictOptions["masquer_dates_anciennes"] == True and type(date) == datetime.date and date < datetime.date.today():
                afficher_ligne = False

            if afficher_ligne == True :

                if type(date) == datetime.date :
                    valeur = UTILS_Dates.DateComplete(date)
                else :
                    valeur = date
                ligne.append(Paragraph(valeur, style_entete))

                # Ajout des cases à la ligne
                numColonne = 0
                for dictColonne in dictDonnees["liste_colonnes"]:

                    # Recherche la valeur
                    valeur = ""
                    if (numLigne, numColonne) in dictDonnees["cases"]:
                        case = dictDonnees["cases"][(numLigne, numColonne)]
                        valeur = case.GetValeur()

                        # Recherche le style à appliquer
                        if "numerique" in case.categorieColonne:
                            style = style_numerique

                            # Définit le style de la case total
                            if "total" in case.categorieColonne or numLigne == len(dictDonnees["liste_dates"])-1 :
                                style = style_total

                            if numLigne == len(dictDonnees["liste_dates"]) - 1:
                                # Récupère la valeur total de la colonne
                                valeur = dict_totaux_colonnes.get(numColonne, 0)
                            else :
                                # Mémorise total de la colonne numérique
                                if (numColonne in dict_totaux_colonnes) == False:
                                    dict_totaux_colonnes[numColonne] = 0
                                dict_totaux_colonnes[numColonne] += valeur

                        else :
                            style = style_texte
                            valeur = valeur.replace("\n", "<br/>")
                    ligne.append(Paragraph(six.text_type(valeur), style))
                    numColonne += 1

                # Ajout de la ligne au tableau
                dataTableau.append(ligne)

        # Style du tableau
        couleur_fond_entetes = UTILS_Divers.ConvertCouleurWXpourPDF(dictOptions["couleur_fond_entetes"])
        couleur_fond_total = UTILS_Divers.ConvertCouleurWXpourPDF(dictOptions["couleur_fond_total"])

        listeStyles = [
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONT',(0,0),(-1,-1), "Helvetica", dictOptions["taille_texte"]),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (0,1), (-2,-1), 'RIGHT'), # Centre les cases
                ('FONT', (0, 0), (0, -1), "Helvetica-Bold", dictOptions["taille_texte"]),
                ('FONT', (0, 0), (-1, 0), "Helvetica-Bold", dictOptions["taille_texte"]),
                ('BACKGROUND', (0, 0), (-1, 0), couleur_fond_entetes),
                ('BACKGROUND', (0, 0), (0, -1), couleur_fond_entetes),
                ('BACKGROUND', (0, -1), (-1, -1), couleur_fond_entetes),
                ]

        # Colorisation des colonnes TOTAL
        numColonne = 1
        for dictColonne in dictDonnees["liste_colonnes"]:
            if "total" in dictColonne["categorie"]:
                listeStyles.insert(0, ('BACKGROUND', (numColonne, 1), (numColonne, -1), couleur_fond_total))
            numColonne += 1

        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes, repeatRows=1)
        style = TableStyle(listeStyles)
        tableau.setStyle(style)
        story.append(tableau)

        # Observations
        if dictOptions["afficher_observations"] == True and len(observations) > 0:
            style_observations = ParagraphStyle(name="2", alignment=1, fontName="Helvetica", fontSize=dictOptions["taille_texte"], leading=8, spaceBefore=10)
            story.append(Paragraph(observations, style=style_observations))

        # Enregistrement du PDF
        doc.build(story)

        # Affichage du PDF
        if afficherDoc == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)

        # Mémorisation des champs de fusion
        dictChampsFusion["{NOM_COMMANDE}"] = nom_commande
        dictChampsFusion["{DATE_DEBUT}"] = UTILS_Dates.DateDDEnFr(date_debut)
        dictChampsFusion["{DATE_FIN}"] = UTILS_Dates.DateDDEnFr(date_fin)

        return dictChampsFusion


class CTRL_Options_impression(DLG_Options_impression_pdf.CTRL_Parametres):
    def __init__(self, parent):
        DLG_Options_impression_pdf.CTRL_Parametres.__init__(self, parent)

    def Remplissage(self):
        # Affichage
        self.Append(wxpg.PropertyCategory(_(u"Affichage")))

        # Période à afficher
        # date_debut = DICT_INFOS_IMPRESSION["date_debut"]
        # date_fin = DICT_INFOS_IMPRESSION["date_fin"]
        # if date_debut != None and date_fin != None :
        #
        #     propriete = wxpg.StringProperty(label=_(u"Date de début"), name="date_debut", value=UTILS_Dates.DateDDEnFr(date_debut))
        #     propriete.SetEditor("EditeurDate")
        #     self.Append(propriete)
        #
        #     propriete = wxpg.StringProperty(label=_(u"Date de fin"), name="date_fin", value=UTILS_Dates.DateDDEnFr(date_fin))
        #     propriete.SetEditor("EditeurDate")
        #     self.Append(propriete)

        # Masquer dates anciennes
        propriete = wxpg.BoolProperty(label=_(u"Masquer les anciennes dates"), name="masquer_dates_anciennes", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour masquer les dates passées"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher observations
        propriete = wxpg.BoolProperty(label=_(u"Afficher les observations"), name="afficher_observations", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les observations"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Page
        self.Append(wxpg.PropertyCategory(_(u"Page")))

        # Orientation page
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Orientation de la page"), name="orientation", liste_choix=[("portrait", _(u"Portrait")), ("paysage", _(u"Paysage"))], valeur="portrait")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'orientation de la page"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        self.Append( wxpg.PropertyCategory(_(u"Couleurs de fond")) )

        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Fond entêtes"), name="couleur_fond_entetes", value=wx.Colour(230, 230, 230))
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Fond colonne total"), name="couleur_fond_total", value=wx.Colour(245, 245, 245))
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        self.Append( wxpg.PropertyCategory(_(u"Texte")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte", "SpinCtrl")

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte du titre"), name="taille_texte_titre", value=9)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (9 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte", "SpinCtrl")

        self.Append( wxpg.PropertyCategory(_(u"Colonnes")) )

        # Largeur automatique
        propriete = wxpg.BoolProperty(label=_(u"Largeur auto ajustée"), name="largeur_colonnes_auto", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour laisser Noethys ajuster la largeur des colonnes automatiquement"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Largeur colonne labels
        propriete = wxpg.IntProperty(label=_(u"Largeur colonne date"), name="largeur_colonne_date", value=110)
        propriete.SetHelpString(_(u"Saisissez la largeur pour la colonne date (110 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_date", "SpinCtrl")





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmodele=1, IDcommande=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
