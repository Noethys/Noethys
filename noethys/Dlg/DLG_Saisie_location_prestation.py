#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Utils import UTILS_Dates
from Utils import UTILS_Interface
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES
from Dlg.DLG_Ouvertures import Track_tarif




class OL_Tarifs(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.dictInfosLocation = kwds.pop("dictInfosLocation", {})
        self.donnees = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)

    def InitModel(self):
        """ Récupération des données """
        if self.dictInfosLocation["IDproduit"] == None :
            return

        liste_tarifs = []

        DB = GestionDB.DB()

        # Importation du tarif fixe du produit
        req = """SELECT nom, montant
        FROM produits 
        WHERE IDproduit=%d;""" % self.dictInfosLocation["IDproduit"]
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            nom_produit, montant_produit = listeDonnees[0]
            if montant_produit != None :
                track = Track_tarif({"IDtarif": None})
                track.label = nom_produit
                track.montant = montant_produit
                liste_tarifs.append(track)

        # Importation des tarifs
        req = """SELECT IDtarif, IDactivite, date_debut, date_fin, methode, type, categories_tarifs, groupes, etiquettes, cotisations, 
        caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, 
        IDtype_quotient, label_prestation, IDproduit
        FROM tarifs WHERE IDproduit=%d;""" % self.dictInfosLocation["IDproduit"]
        DB.ExecuterReq(req)
        listeDonneesTarifs = DB.ResultatReq()
        listeIDtarif = []
        for temp in listeDonneesTarifs:
            listeIDtarif.append(temp[0])

        if len(listeIDtarif) == 0:
            condition = "()"
        elif len(listeIDtarif) == 1:
            condition = "(%d)" % listeIDtarif[0]
        else:
            condition = str(tuple(listeIDtarif))

        # Importation des lignes de tarifs
        req = """SELECT %s FROM tarifs_lignes WHERE IDtarif IN %s ORDER BY num_ligne;""" % (", ".join(CHAMPS_TABLE_LIGNES), condition)
        DB.ExecuterReq(req)
        listeDonneesLignes = DB.ResultatReq()
        dictLignes = {}
        for ligne in listeDonneesLignes:
            index = 0
            dictLigne = {}
            for valeur in ligne:
                dictLigne[CHAMPS_TABLE_LIGNES[index]] = valeur
                index += 1
            if dictLignes.has_key(dictLigne["IDtarif"]) == False:
                dictLignes[dictLigne["IDtarif"]] = []
            dictLignes[dictLigne["IDtarif"]].append(dictLigne)

        # Mémorisation des tarifs
        for IDtarif, IDactivite, date_debut, date_fin, methode, type, categories_tarifs, groupes, etiquettes, cotisations, caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, IDtype_quotient, label_prestation, IDproduit in listeDonneesTarifs:

            # Récupération des lignes du tarif
            if dictLignes.has_key(IDtarif):
                liste_lignes = dictLignes[IDtarif]
            else:
                liste_lignes = []

            dictTarif = {
                "IDtarif": IDtarif, "IDactivite": IDactivite, "date_debut": date_debut, "date_fin": date_fin, "methode": methode, "type": type, "categories_tarifs": categories_tarifs,
                "groupes": groupes, "etiquettes": etiquettes, "cotisations": cotisations, "caisses": caisses, "description": description,
                "jours_scolaires": jours_scolaires, "jours_vacances": jours_vacances, "observations": observations, "tva": tva,
                "code_compta": code_compta, "IDtype_quotient": IDtype_quotient, "label_prestation": label_prestation, "IDproduit": IDproduit,
                "filtres": [], "lignes": liste_lignes,
            }
            track = Track_tarif(dictTarif)

            # Ajustement du label de la prestation
            if label_prestation == "description_tarif" :
                track.label = description
            else :
                track.label = nom_produit

            # Calcul du montant
            track.montant = 0.0

            # ------------ Recherche du montant du tarif : MONTANT UNIQUE
            if methode == "produit_montant_unique":
                track.montant = liste_lignes[0]["montant_unique"]

            # ------------ Recherche du montant du tarif : MONTANT PROPORTIONNEL A LA QUANTITE
            if methode == "produit_proportionnel_quantite":
                if self.dictInfosLocation.has_key("quantite") :
                    quantite = self.dictInfosLocation["quantite"]
                    track.montant = quantite * liste_lignes[0]["montant_unique"]

            # Mémorisation du tarif
            liste_tarifs.append(track)

        DB.Close()

        # Envoi des données au OL
        self.donnees = liste_tarifs

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDtarif", typeDonnee="entier"),
            ColumnDefn(_(u"Du"), 'left', 80, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"au"), 'left', 80, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Label"), "left", 220, "label", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), "right", 80, "montant", typeDonnee="montant", stringConverter=FormateMontant),
        ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun tarif"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

    def MAJ(self, track=None):
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if track != None:
            self.SelectObject(track, deselectOthers=True, ensureVisible=True)

    def Selection(self):
        return self.GetSelectedObjects()[0]



# -------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, track=None, dictInfosLocation={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.dictInfosLocation = dictInfosLocation
        self.track = track

        # Tarifs
        self.box_tarifs_staticbox = wx.StaticBox(self, -1, _(u"Tarifs disponibles"))
        self.label_tarifs = wx.StaticText(self, -1, _(u"Cliquez sur un tarif pour le sélectionner ou double-cliquez pour le sélectionner et le valider directement."))
        self.label_tarifs.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.ctrl_tarifs = OL_Tarifs(self, id=-1, dictInfosLocation=dictInfosLocation, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_tarifs.SetMinSize((50, 50))
        self.ctrl_tarifs.MAJ()

        # Prestation
        self.box_prestation_staticbox = wx.StaticBox(self, -1, _(u"Prestation"))

        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, "")

        self.label_date_prestation = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date_prestation = CTRL_Saisie_date.Date2(self, activeCallback=False)
        
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.ctrl_tarifs.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnClick)
        self.ctrl_tarifs.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDoubleClick)

        # Importation du track
        self.SetTrack(self.track)


    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une prestation"))
        self.ctrl_tarifs.SetToolTip(wx.ToolTip(_(u"Sélectionnez un tarif à appliquer")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((560, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Tarifs
        box_tarifs = wx.StaticBoxSizer(self.box_tarifs_staticbox, wx.VERTICAL)
        box_tarifs.Add(self.label_tarifs, 0, wx.ALL|wx.EXPAND, 10)
        box_tarifs.Add(self.ctrl_tarifs, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_base.Add(box_tarifs, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Prestation
        box_prestation = wx.StaticBoxSizer(self.box_prestation_staticbox, wx.VERTICAL)
        grid_sizer_prestation = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_prestation.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        
        grid_sizer_prestation.Add(self.label_date_prestation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_prestation_2 = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_prestation_2.Add(self.ctrl_date_prestation, 0, 0, 0)
        grid_sizer_prestation_2.Add( (40, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation_2.Add(self.label_montant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation_2.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_prestation.Add(grid_sizer_prestation_2, 1, wx.EXPAND, 0)

        grid_sizer_prestation.AddGrowableCol(1)
        box_prestation.Add(grid_sizer_prestation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_prestation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnClick(self, event=None):
        track = self.ctrl_tarifs.Selection()
        self.ctrl_date_prestation.SetDate(datetime.date.today())
        self.ctrl_label.SetValue(track.label)
        self.ctrl_montant.SetMontant(track.montant)

    def OnDoubleClick(self, event=None):
        self.OnBoutonOk()
        
    def OnBoutonAide(self, event=None):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event=None):
        # Validation label prestation
        if len(self.ctrl_label.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un label pour cette prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return False

        if self.ctrl_date_prestation.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date pour cette prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_prestation.SetFocus()
            return False

        if self.ctrl_montant.GetMontant() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un montant pour cette prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        # Ferme la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event=None): 
        self.EndModal(wx.ID_CANCEL)

    def GetTrack(self):
        self.track.label = self.ctrl_label.GetValue()
        self.track.date = self.ctrl_date_prestation.GetDate()
        self.track.montant = self.ctrl_montant.GetMontant()
        return self.track

    def SetTrack(self, track=None):
        if track != None :
            self.ctrl_label.SetValue(track.label)
            self.ctrl_date_prestation.SetDate(track.date)
            self.ctrl_montant.SetMontant(track.montant)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
