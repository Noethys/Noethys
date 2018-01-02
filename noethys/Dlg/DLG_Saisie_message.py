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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

import GestionDB

from Utils import UTILS_Historique
from Utils import UTILS_Identification
from Ctrl import CTRL_Saisie_date
from Utils import UTILS_Titulaires

def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))




class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeDonnees = self.GetListeDonnees()
        self.SetItems(listeDonnees)
        self.Select(0)

    def GetListeDonnees(self):
        listeItems = [_(u"Aucune"),]
        self.dictDonnees = {0 : {"ID" : None}}
        DB = GestionDB.DB()
        req = """
        SELECT IDcategorie, nom, priorite, afficher_accueil, afficher_liste
        FROM messages_categories
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDcategorie, nom, priorite, afficher_accueil, afficher_liste in listeDonnees :
            self.dictDonnees[index] = { 
                "ID" : IDcategorie, 
                "nom" : nom, 
                "priorite" : priorite, 
                "afficher_accueil" : afficher_accueil, 
                "afficher_liste" : afficher_liste, 
                }
            listeItems.append(nom)
            index += 1
        return listeItems
    
    def GetDetailDonnees(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index in (-1, 0) : return None
        return self.dictDonnees[index]["ID"]
            

# -------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDmessage=None, IDfamille=None, IDindividu=None, mode="accueil"):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent      
        self.IDmessage = IDmessage
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        self.mode = mode
        self.date_saisie = datetime.date.today()
        self.nom = None
        
        # Catégorie
        self.staticbox_categorie_staticbox = wx.StaticBox(self, -1, _(u"Catégorie"))
        self.ctrl_categorie = CTRL_Categorie(self)
        self.bouton_categorie = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # Texte
        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, _(u"Texte"))
        self.ctrl_texte = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        
        self.ctrl_afficher_accueil = wx.CheckBox(self, -1, _(u"Afficher sur la page d'accueil"))
        self.ctrl_afficher_liste = wx.CheckBox(self, -1, _(u"Afficher sur la liste des consommations"))
        self.ctrl_afficher_factures = wx.CheckBox(self, -1, _(u"Afficher sur les factures"))

        self.ctrl_rappel_famille = wx.CheckBox(self, -1, _(u"Rappel à l'ouverture de la fiche famille"))
        self.ctrl_rappel_accueil = wx.CheckBox(self, -1, _(u"Rappel à l'ouverture du fichier"))

        self.label_parution = wx.StaticText(self, -1, _(u"Date de parution :"))
        self.ctrl_parution = CTRL_Saisie_date.Date(self)
        self.ctrl_parution.SetDate(datetime.date.today())
        
        self.label_priorite = wx.StaticText(self, -1, _(u"Priorité :"))
        self.ctrl_priorite = wx.Choice(self, -1, choices=[_(u"Normale"), _(u"Haute")])
        self.ctrl_priorite.SetSelection(0)
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategorie, self.bouton_categorie)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDmessage == None :
            self.SetTitle(_(u"Saisie d'un message"))
        else:
            self.Importation()
            self.SetTitle(_(u"Modification d'un message"))

        if self.mode != "famille" :
            self.ctrl_afficher_factures.Show(False)
            self.ctrl_rappel_famille.Show(False)
        if self.mode == "accueil" :
            self.ctrl_afficher_accueil.SetValue(True)
            self.ctrl_afficher_accueil.Show(False)
            self.ctrl_afficher_liste.Show(False)

        wx.CallLater(0, self.ctrl_texte.SetFocus)

    def __set_properties(self):
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez une catégorie")))
        self.bouton_categorie.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des catégories de messages")))
        self.ctrl_afficher_accueil.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher ce message sur la page d'accueil")))
        self.ctrl_afficher_factures.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher ce message sur les futures factures de la famille")))
        self.ctrl_parution.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de parution du message")))
        self.ctrl_afficher_liste.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher ce message sur la liste des consommations")))
        self.ctrl_priorite.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la priorité du message")))
        self.ctrl_rappel_accueil.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher un rappel du message à l'ouverture du logiciel")))
        self.ctrl_rappel_famille.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher un rappel du message à l'ouverture de la fiche famille")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((550, 440))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Catégorie
        staticbox_categorie = wx.StaticBoxSizer(self.staticbox_categorie_staticbox, wx.VERTICAL)
        grid_sizer_categorie = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_categorie.Add(self.ctrl_categorie, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_categorie.Add(self.bouton_categorie, 0, 0, 0)
        grid_sizer_categorie.AddGrowableCol(0)
        staticbox_categorie.Add(grid_sizer_categorie, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_categorie, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Texte
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        staticbox_texte.Add(self.ctrl_texte, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_texte, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        grid_sizer_options_gauche = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_options_gauche.Add(self.ctrl_afficher_accueil, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_gauche.Add(self.ctrl_afficher_liste, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_gauche.Add(self.ctrl_afficher_factures, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_gauche.Add(self.ctrl_rappel_famille, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_gauche.Add(self.ctrl_rappel_accueil, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(grid_sizer_options_gauche, 0, wx.EXPAND, 0)
        
        grid_sizer_options_droit = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_options_droit.Add(self.label_parution, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_droit.Add(self.ctrl_parution, 0, wx.EXPAND, 0)
        grid_sizer_options_droit.Add(self.label_priorite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_droit.Add(self.ctrl_priorite, 0, 0, 0)
        grid_sizer_options.Add(grid_sizer_options_droit, 0, wx.EXPAND, 0)
        
        grid_sizer_options.AddGrowableCol(0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        
        wx.CallLater(0, self.Layout) # Contre pb d'affichage du wx.Choice

    def OnBoutonCategorie(self, event): 
        IDcategorie = self.ctrl_categorie.GetID()
        import DLG_Categories_messages
        dlg = DLG_Categories_messages.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_categorie.MAJ() 
        self.ctrl_categorie.SetID(IDcategorie)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lesmessages")

    def OnBoutonOk(self, event): 
        # Vérification des données
        if len(self.ctrl_texte.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_texte.SetFocus()
            return
        
        if self.ctrl_parution.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de parution !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_parution.SetFocus()
            return
        
        # Sauvegarde
        self.Sauvegarde()
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDmessage(self):
        return self.IDmessage

    def Importation(self):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT type, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite,
        afficher_accueil, afficher_liste, IDfamille, IDindividu, texte, nom, rappel, afficher_facture, rappel_famille
        FROM messages 
        WHERE IDmessage=%d;""" % self.IDmessage
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        type, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite, afficher_accueil, afficher_liste, IDfamille, IDindividu, texte, nom, rappel_accueil, afficher_facture, rappel_famille = listeDonnees[0]
        
        self.type = type
        self.date_saisie = DateEngEnDateDD(date_saisie)
        self.IDutilisateur = IDutilisateur
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        self.nom = nom
        
        self.ctrl_categorie.SetID(IDcategorie)
        self.ctrl_parution.SetDate(date_parution)
        if priorite == "HAUTE" : self.ctrl_priorite.Select(1)
        self.ctrl_afficher_accueil.SetValue(afficher_accueil)
        self.ctrl_afficher_liste.SetValue(afficher_liste)
        if afficher_facture != None :
            self.ctrl_afficher_factures.SetValue(afficher_facture)
        self.ctrl_rappel_accueil.SetValue(rappel_accueil)
        if rappel_famille != None :
            self.ctrl_rappel_famille.SetValue(rappel_famille)
        self.ctrl_texte.SetValue(texte)

    def Sauvegarde(self):
        """ Sauvegarde """
        # Récupération des données
        IDcategorie = self.ctrl_categorie.GetID()
        texte = self.ctrl_texte.GetValue()
        if self.ctrl_priorite.GetSelection() == 1 :
            priorite = "HAUTE"
        else:
            priorite = "NORMALE"
        afficher_accueil = int(self.ctrl_afficher_accueil.GetValue())
        afficher_liste = int(self.ctrl_afficher_liste.GetValue())
        afficher_factures = int(self.ctrl_afficher_factures.GetValue())
        rappel_accueil = int(self.ctrl_rappel_accueil.GetValue())
        rappel_famille = int(self.ctrl_rappel_famille.GetValue())
        date_parution = self.ctrl_parution.GetDate() 
        
        if self.mode == "famille" and self.nom == None : self.nom = self.GetNomFamille() 
        if self.mode == "individu" and self.nom == None : self.nom = self.GetNomIndividu() 
        
        IDutilisateur = UTILS_Identification.GetIDutilisateur()
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("type", "INSTANTANE"),
                ("IDcategorie", IDcategorie),
                ("date_saisie", self.date_saisie),
                ("IDutilisateur", IDutilisateur),
                ("date_parution", date_parution),
                ("priorite", priorite),
                ("afficher_accueil", afficher_accueil),
                ("afficher_liste", afficher_liste),
                ("rappel", rappel_accueil),
                ("rappel_famille", rappel_famille),
                ("IDfamille", self.IDfamille),
                ("IDindividu", self.IDindividu),
                ("nom", self.nom),
                ("texte", texte),
                ("afficher_facture", afficher_factures),
            ]
        if self.IDmessage == None :
            nouveauMessage = True
            self.IDmessage = DB.ReqInsert("messages", listeDonnees)
        else:
            nouveauMessage = False
            DB.ReqMAJ("messages", listeDonnees, "IDmessage", self.IDmessage)
        DB.Close()
        
        # Mémorise l'action dans l'historique
        if nouveauMessage == True :
            type = _(u"Saisie")
            IDcategorie = 24
        else:
            type = _(u"Modification")
            IDcategorie = 25
        if len(texte) > 450 : texte = texte[450:] + u"..."
        UTILS_Historique.InsertActions([{
            "IDindividu" : self.IDindividu,
            "IDfamille" : self.IDfamille,
            "IDcategorie" : IDcategorie, 
            "action" : _(u"%s du message ID%d : '%s'") % (type, self.IDmessage, texte)
            },])

    
    def GetNomIndividu(self):
        if self.GetGrandParent().GetName() == "notebook_individu" :
            ongletIdentite = self.GetGrandParent().GetPageAvecCode("identite")
            nom = ongletIdentite.ctrl_nom.GetValue() 
            prenom = ongletIdentite.ctrl_prenom.GetValue() 
            return u"%s %s" % (nom, prenom)
        else:
            return None
    
    def GetNomFamille(self):
        try :
            dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille=[self.IDfamille,])
            nomTitulaires = dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        except :
            nomTitulaires = u""
        return nomTitulaires
                


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmessage=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
