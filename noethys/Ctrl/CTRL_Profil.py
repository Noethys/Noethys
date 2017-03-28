#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
import wx
import GestionDB
from Utils.UTILS_Traduction import _


class CTRL_Choix_profil(wx.Choice):
    def __init__(self, parent, categorie=""):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.categorie = categorie
        self.MAJ()
        if len(self.dictDonnees) > 0:
            self.Select(0)

    def MAJ(self):
        selectionActuelle = self.GetID()
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0:
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        # Re-sélection après MAJ
        self.SetID(selectionActuelle)

    def GetListeDonnees(self):
        listeItems = [_(u"Aucun")]
        self.dictDonnees = {0 : None}
        DB = GestionDB.DB()
        req = """SELECT IDprofil, label
        FROM profils
        WHERE categorie='%s'
        ORDER BY label;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDprofil, label in listeDonnees:
            listeItems.append(label)
            self.dictDonnees[index] = IDprofil
            index += 1
        return listeItems

    def SetID(self, ID=None):
        for index, IDprofil in self.dictDonnees.iteritems():
            if IDprofil != None and IDprofil == ID:
                self.SetSelection(index)
                return
        self.SetSelection(0)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]


# -------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    """ Contrôle sélection d'un profil avec boutons d'actions """
    def __init__(self, parent, categorie=""):
        wx.Panel.__init__(self, parent, id=-1, name="ctrl_profil", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie

        self.ctrl_choix_profil = CTRL_Choix_profil(self, categorie=categorie)
        self.bouton_gestion = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_enregistrer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Sauvegarder.png"), wx.BITMAP_TYPE_ANY))

        self.Bind(wx.EVT_CHOICE, self.OnChoixProfil, self.ctrl_choix_profil)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGestion, self.bouton_gestion)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnregistrer, self.bouton_enregistrer)

        self.ctrl_choix_profil.SetToolTipString(_(u"Sélectionnez un profil de configuration"))
        self.bouton_gestion.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des profils"))
        self.bouton_enregistrer.SetToolTipString(_(u"Cliquez ici pour enregistrer le profil sélectionné"))

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_choix_profil, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.bouton_gestion, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.bouton_enregistrer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def OnBoutonGestion(self, event=None):
        from Dlg import DLG_Profils_parametres
        dlg = DLG_Profils_parametres.Dialog(self, categorie=self.categorie)
        dlg.ShowModal()
        dernierProfilCree = dlg.GetDernierProfilCree()
        dlg.Destroy()
        self.ctrl_choix_profil.MAJ()
        if dernierProfilCree != None :
            self.ctrl_choix_profil.SetID(dernierProfilCree)

    def OnBoutonEnregistrer(self, event=None):
        self.Recevoir_parametres()

    def GetIDprofil(self):
        return self.ctrl_choix_profil.GetID()

    def OnChoixProfil(self, event=None):
        """ Lors du choix du profil """
        IDprofil = self.GetIDprofil()
        if IDprofil == None :
            dictParametres = None
        else :
            dictParametres = GetParametres(IDprofil=IDprofil)
        self.Envoyer_parametres(dictParametres)

    def Enregistrer(self, dictParametres={}):
        """ Enregistrer les paramètres du profil """
        IDprofil = self.GetIDprofil()

        # Si aucun profil sélectionné, on propose d'en créer tout de suite
        if IDprofil == None :
            IDprofil = self.Proposer_creation_profil()
            if IDprofil in (None, False) :
                return False

        # Sauvegarde des paramètres du profil dans la base
        SetParametres(categorie="profil_%s" % self.categorie, dictParametres=dictParametres, IDprofil=IDprofil)

    def Proposer_creation_profil(self):
        """ On propose de créer un nouveau profil """
        dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun profil pour enregistrer votre configuration.\n\nSouhaitez-vous créer un nouveau profil maintenant ?"), _(u"Créer un profil de configuration"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Création d'un nouveau profil
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du nouveau profil de configuration :"), _(u"Saisie d'un profil"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetValue()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return False
        if label == "":
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        else:
            DB = GestionDB.DB()
            listeDonnees = [("label", label), ("categorie", self.categorie)]
            IDprofil = DB.ReqInsert("profils", listeDonnees)
            DB.Close()
            self.ctrl_choix_profil.MAJ()
            self.ctrl_choix_profil.SetID(IDprofil)
            return IDprofil


    def Envoyer_parametres(self, dictParametres={}):
        """ A SURCHARGER : Envoi des paramètres du profil sélectionné à la fenêtre """
        pass

    def Recevoir_parametres(self):
        """ A SURCHARGER : Récupération des paramètres pour la sauvegarde du profil """
        # Utiliser avec self.Enregistrer(dictParametres)
        pass






def SetParametres(categorie="", dictParametres={}, IDprofil=None):
    # Ouverture de la DB
    DB = GestionDB.DB()
    if DB.echec == 1:
        return False

    # Lecture des valeurs existantes dans la DB
    req = """SELECT IDparametre, nom, parametre, type_donnee FROM profils_parametres WHERE IDprofil=%d;""" % IDprofil
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictDonnees = {}
    for IDparametre, nom, parametre, type_donnee in listeDonnees:
        dictDonnees[nom] = parametre

    # On boucle sur chaque valeur
    listeAjouts = []
    listeModifications = []
    for nom, valeur in dictParametres.iteritems():
        type_donnee = type(valeur)
        if type_donnee in (str, unicode) :
            type_donnee = "texte"
            valeur = valeur
        else :
            type_donnee = "autre"
            valeur = unicode(valeur)

        if dictDonnees.has_key(nom):
            # Si valeur existe déjà dans DB
            if dictDonnees[nom] != valeur :
                listeModifications.append((valeur, type_donnee, nom, IDprofil))

        else:
            # Le parametre n'existe pas, on le créé :
            listeAjouts.append((nom, valeur, type_donnee, IDprofil))

    # Sauvegarde des modifications
    if len(listeModifications) > 0:
        DB.Executermany("UPDATE profils_parametres SET parametre=?, type_donnee=? WHERE nom=? and IDprofil=?", listeModifications, commit=False)

    # Sauvegarde des ajouts
    if len(listeAjouts) > 0:
        DB.Executermany("INSERT INTO profils_parametres (nom, parametre, type_donnee, IDprofil) VALUES (?, ?, ?, ?)", listeAjouts, commit=False)

    # Commit et fermeture de la DB
    if len(listeModifications) > 0 or len(listeAjouts) > 0:
        DB.Commit()

    DB.Close()


def GetParametres(IDprofil=None):
    # Ouverture de la DB
    DB = GestionDB.DB()
    if DB.echec == 1:
        return {}

    # Lecture des valeurs dans la DB
    req = """SELECT IDparametre, nom, parametre, type_donnee FROM profils_parametres WHERE IDprofil=%d;""" % IDprofil
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()

    # On boucle sur chaque valeur
    dictResultats = {}
    for IDparametre, nom, parametre, type_donnee in listeDonnees:
        if type_donnee == "texte":
            parametre = parametre
        else :
            exec("parametre = " + parametre)
        dictResultats[nom] = parametre

    return dictResultats








class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="panel_test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
