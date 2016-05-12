#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import os
import sys
import traceback
import GestionDB
from Ctrl import CTRL_Choix_modele
from Ol import OL_Attestations_fiscales_selection

from Utils import UTILS_Identification
from Utils import UTILS_Historique
from Utils import UTILS_Attestations_fiscales
from Utils import UTILS_Envoi_email

import wx.lib.agw.hyperlink as Hyperlink
import wx.lib.agw.pybusyinfo as PBI


TEXTE_INTRO = _(u"Veuillez trouver ci-dessous le montant réglé à notre organisme sur la période du {DATE_DEBUT} au {DATE_FIN} pour la garde de votre ou vos enfants de moins de 7 ans :")


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def GetTexteNoms(listeNoms=[]):
    """ Récupère les noms sous la forme David DUPOND et Maxime DURAND... """
    texteNoms = u""
    nbreIndividus = len(listeNoms)
    if nbreIndividus == 0 : texteNoms = u""
    if nbreIndividus == 1 : texteNoms = listeNoms[0]
    if nbreIndividus == 2 : texteNoms = _(u"%s et %s") % (listeNoms[0], listeNoms[1])
    if nbreIndividus > 2 :
        for texteNom in listeNoms[:-2] :
            texteNoms += u"%s, " % texteNom
        texteNoms += _(u"%s et %s") % (listeNoms[-2], listeNoms[-1])
    return texteNoms

def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte


# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Signataires(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self, listeActivites=[] ):
        listeItems, indexDefaut = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        if indexDefaut != None :
            self.Select(indexDefaut)
        
        # Recherche le nom de l'utilisateur parmi la liste des signataires
        dictUtilisateur = UTILS_Identification.GetDictUtilisateur()
        for index, dictDonnees in self.dictDonnees.iteritems() :
            if dictUtilisateur != None :
                texte1 = u"%s %s" % (dictUtilisateur["prenom"], dictUtilisateur["nom"])
                texte2 = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
                if dictDonnees["nom"].lower() == texte1.lower() or dictDonnees["nom"].lower() == texte2.lower() :
                    self.SetSelection(index)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDresponsable, IDactivite, nom, fonction, defaut, sexe
        FROM responsables_activite
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        indexDefaut = None
        index = 0
        for IDresponsable, IDactivite, nom, fonction, defaut, sexe in listeDonnees :
            if nom not in listeItems :
                if indexDefaut == None and defaut == 1 : indexDefaut = index
                self.dictDonnees[index] = { 
                    "ID" : IDresponsable, "IDactivite" : IDactivite,
                    "nom" : nom, "fonction" : fonction,
                    "defaut" : defaut, "sexe" : sexe, 
                    }
                listeItems.append(nom)
                index += 1
        return listeItems, indexDefaut

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfos(self):
        """ Récupère les infos sur le signataire sélectionné """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]


##class CTRL_Signataires(wx.Choice):
##    def __init__(self, parent):
##        wx.Choice.__init__(self, parent, -1) 
##        self.parent = parent
##        self.listeActivites = []
##        self.MAJ() 
##        if len(self.dictDonnees) > 0 :
##            self.SetSelection(0)
##    
##    def MAJ(self, listeActivites=[] ):
##        self.listeActivites = listeActivites
##        listeItems, indexDefaut = self.GetListeDonnees()
##        if len(listeItems) == 0 :
##            self.Enable(False)
##        else:
##            self.Enable(True)
##        self.SetItems(listeItems)
##        if indexDefaut != None :
##            self.Select(indexDefaut)
##                                        
##    def GetListeDonnees(self):
##        if len(self.listeActivites) == 0 : conditionActivites = "()"
##        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
##        else : conditionActivites = str(tuple(self.listeActivites))
##        db = GestionDB.DB()
##        req = """SELECT IDresponsable, IDactivite, nom, fonction, defaut, sexe
##        FROM responsables_activite
##        WHERE IDactivite IN %s
##        ORDER BY nom;""" % conditionActivites
##        db.ExecuterReq(req)
##        listeDonnees = db.ResultatReq()
##        db.Close()
##        listeItems = []
##        self.dictDonnees = {}
##        indexDefaut = None
##        index = 0
##        for IDresponsable, IDactivite, nom, fonction, defaut, sexe in listeDonnees :
##            if indexDefaut == None and defaut == 1 : indexDefaut = index
##            self.dictDonnees[index] = { 
##                "ID" : IDresponsable, "IDactivite" : IDactivite,
##                "nom" : nom, "fonction" : fonction,
##                "defaut" : defaut, "sexe" : sexe, 
##                }
##            listeItems.append(nom)
##            index += 1
##        return listeItems, indexDefaut
##
##    def SetID(self, ID=0):
##        for index, values in self.dictDonnees.iteritems():
##            if values["ID"] == ID :
##                 self.SetSelection(index)
##
##    def GetID(self):
##        index = self.GetSelection()
##        if index == -1 : return None
##        return self.dictDonnees[index]["ID"]
##    
##    def GetInfos(self):
##        """ Récupère les infos sur le signataire sélectionné """
##        index = self.GetSelection()
##        if index == -1 : return None
##        return self.dictDonnees[index]
        

# -----------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        if self.URL == "payes" : self.parent.CochePayes() 
        if self.URL == "tout" : self.parent.CocheTout() 
        if self.URL == "rien" : self.parent.DecocheTout() 
        self.UpdateLink()
    













class CTRL_Options(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele = CTRL_Choix_modele.CTRL_Choice(self, categorie="attestation_fiscale")
        self.ctrl_modele.Select(0)
        self.bouton_gestion_modeles = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        self.label_signataire = wx.StaticText(self, -1, _(u"Signataire :"))
        self.ctrl_signataire = CTRL_Signataires(self)
        
        self.label_intro = wx.StaticText(self, -1, _(u"Intro :"))
        self.ctrl_intro = wx.CheckBox(self, -1, u"")
        self.ctrl_intro.SetValue(True)
        self.ctrl_texte_intro = wx.TextCtrl(self, -1, TEXTE_INTRO)

##        self.label_affichage = wx.StaticText(self, -1, _(u"Affichage :"))
##        self.radio_condense = wx.RadioButton(self, -1, _(u"Condensé"), style=wx.RB_GROUP)
##        self.radio_detaille = wx.RadioButton(self, -1, _(u"Détaillé"))

        # Répertoire
        self.label_repertoire = wx.StaticText(self, -1, _(u"Copie :"))
        self.checkbox_repertoire = wx.CheckBox(self, -1, _(u"Enregistrer une copie unique dans le répertoire :"))
        self.ctrl_repertoire = wx.TextCtrl(self, -1, u"")
        self.bouton_repertoire = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Repertoire.png"), wx.BITMAP_TYPE_ANY))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeles, self.bouton_gestion_modeles)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckIntro, self.ctrl_intro)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRepertoire, self.checkbox_repertoire)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRepertoire, self.bouton_repertoire)


        self.__set_properties()
        self.__do_layout()

        # Init contrôles
        self.OnCheckIntro(None) 
        self.OnCheckRepertoire(None)

    def __set_properties(self):
        self.ctrl_modele.SetToolTipString(_(u"Sélectionnez un modèle de documents"))
        self.ctrl_signataire.SetToolTipString(_(u"Sélectionnez ici le signataire du document"))
        self.ctrl_intro.SetToolTipString(_(u"Cochez cette case pour inclure le texte d'introduction : 'Je soussigné... atteste...' "))
        self.ctrl_texte_intro.SetToolTipString(_(u"Vous pouvez modifier ici le texte d'introduction. \n\nUtilisez les mots-clés {GENRE}, {NOM}, {FONCTION}, {ENFANTS}, \n{DATE_DEBUT} et {DATE_FIN} pour inclure dynamiquement les \nvaleurs correspondantes."))
        self.checkbox_repertoire.SetToolTipString(_(u"Cochez cette case pour enregistrer un exemplaire de chaque attestation de rappel au format PDF dans le répertoire indiqué"))
        self.bouton_repertoire.SetToolTipString(_(u"Cliquez ici pour sélectionner un répertoire de destination"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Options
        grid_sizer_options = wx.FlexGridSizer(rows=6, cols=2, vgap=5, hgap=10)
        
        # Modèle
        grid_sizer_options.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele.Add(self.bouton_gestion_modeles, 0, 0, 0)
        grid_sizer_modele.AddGrowableCol(0)
        grid_sizer_options.Add(grid_sizer_modele, 1, wx.EXPAND, 0)
        
        # Signataire
        grid_sizer_options.Add(self.label_signataire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_signataire, 1, wx.EXPAND, 0)
        
        # Intro
        grid_sizer_options.Add(self.label_intro, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_intro.Add(self.ctrl_intro, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.Add(self.ctrl_texte_intro, 1,wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_intro.AddGrowableCol(1)
        grid_sizer_options.Add(grid_sizer_intro, 1, wx.EXPAND, 0)

        # Affichage
##        grid_sizer_options.Add(self.label_affichage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_affichage = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
##        grid_sizer_affichage.Add(self.radio_condense, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_affichage.Add(self.radio_detaille, 0,wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_options.Add(grid_sizer_affichage, 1, wx.EXPAND, 0)

        # Répertoire
        grid_sizer_options.Add(self.label_repertoire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_repertoire = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_repertoire.Add(self.checkbox_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.ctrl_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.bouton_repertoire, 0, 0, 0)
        grid_sizer_repertoire.AddGrowableCol(1)
        grid_sizer_options.Add(grid_sizer_repertoire, 1, wx.EXPAND, 0)

        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 0)
                        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()

    def OnCheckIntro(self, event):
        self.ctrl_texte_intro.Enable(self.ctrl_intro.GetValue())

    def OnBoutonModeles(self, event): 
        import DLG_Modeles_docs
        dlg = DLG_Modeles_docs.Dialog(self, categorie="attestation_fiscale")
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_modele.MAJ() 

    def OnCheckRepertoire(self, event):
        etat = self.checkbox_repertoire.GetValue()
        self.ctrl_repertoire.Enable(etat)
        self.bouton_repertoire.Enable(etat)

    def OnBoutonRepertoire(self, event): 
        if self.ctrl_repertoire.GetValue != "" : 
            cheminDefaut = self.ctrl_repertoire.GetValue()
            if os.path.isdir(cheminDefaut) == False :
                cheminDefaut = ""
        else:
            cheminDefaut = ""
        dlg = wx.DirDialog(self, _(u"Veuillez sélectionner un répertoire de destination :"), defaultPath=cheminDefaut, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_repertoire.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnChoixIntitules(self, event=None):
        typeLabel = self.ctrl_intitules.GetID()
        self.ctrl_attestations.typeLabel = typeLabel
        self.ctrl_attestations.MAJ() 

    def GetOptions(self):
        dictOptions = {} 

        # Signataire
        infosSignataire = self.ctrl_signataire.GetInfos()
        if infosSignataire == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun signataire !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        nomSignataire = infosSignataire["nom"]
        fonctionSignataire = infosSignataire["fonction"]
        sexeSignataire = infosSignataire["sexe"]
        if sexeSignataire == "H" :
            genreSignataire = u""
        else:
            genreSignataire = u"e"
        
        dictOptions["signataire"] = {
            "nom" : nomSignataire,
            "fonction" : fonctionSignataire,
            "sexe" : sexeSignataire,
            "genre" : genreSignataire,
            }
        
        # Répertoire
        if self.checkbox_repertoire.GetValue() == True :
            repertoire = self.ctrl_repertoire.GetValue() 
            # Vérifie qu'un répertoire a été saisie
            if repertoire == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un répertoire de destination !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_repertoire.SetFocus()
                return False
            # Vérifie que le répertoire existe
            if os.path.isdir(repertoire) == False :
                dlg = wx.MessageDialog(self, _(u"Le répertoire de destination que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_repertoire.SetFocus()
                return False
        else:
            repertoire = None
                
        # Récupération du modèle
        IDmodele = self.ctrl_modele.GetID() 
        if IDmodele == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Intro
        if self.ctrl_intro.GetValue() == True :
             intro = self.ctrl_texte_intro.GetValue() 
        else :
            intro = None

        # Constitution du dictOptions
        dictOptions["IDmodele"] = IDmodele
        dictOptions["repertoire"] = repertoire
        dictOptions["intro"] = intro
        
        return dictOptions



# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Attestations_fiscales_selection", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.impressionEffectuee = False
        self.donnees = {}
        
        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options d'impression"))
        self.ctrl_options = CTRL_Options(self)
        
        # Attestations
        self.staticbox_attestations_staticbox = wx.StaticBox(self, -1, _(u"Attestations à générer"))
        self.ctrl_attestations = OL_Attestations_fiscales_selection.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.bouton_apercu_liste = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer_liste = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        self.hyper_payes = Hyperlien(self, label=_(u"Sélectionner uniquement les payés"), infobulle=_(u"Cliquez ici pour sélectionner uniquement les payés"), URL="payes")
        self.label_separation_1 = wx.StaticText(self, -1, u"|")
        self.hyper_tout = Hyperlien(self, label=_(u"Tout sélectionner"), infobulle=_(u"Cliquez ici pour tout sélectionner"), URL="tout")
        self.label_separation_2 = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout désélectionner"), infobulle=_(u"Cliquez ici pour tout désélectionner"), URL="rien")
        
        # Actions
        self.staticbox_actions_staticbox = wx.StaticBox(self, -1, _(u"Actions"))
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Transmettre\npar Email"), tailleImage=(32, 32), margesImage=(4, 4, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), tailleImage=(32, 32), margesImage=(4, 0, 0, 0), margesTexte=(-5, 1), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_email.SetMinSize((200, -1))
        self.bouton_imprimer.SetMinSize((200, -1))
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_attestations.Apercu, self.bouton_apercu_liste)
        self.Bind(wx.EVT_BUTTON, self.ctrl_attestations.Imprimer, self.bouton_imprimer_liste)
        self.Bind(wx.EVT_BUTTON, self.ctrl_attestations.ExportTexte, self.bouton_export_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_attestations.ExportExcel, self.bouton_export_excel)
        self.Bind(wx.EVT_BUTTON, self.EnvoiEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_imprimer)


    def __set_properties(self):
        self.bouton_apercu_liste.SetToolTipString(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste"))
        self.bouton_imprimer_liste.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_export_texte.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format texte"))
        self.bouton_export_excel.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Excel"))
        self.bouton_email.SetToolTipString(_(u"Cliquez ici pour accéder à l'envoi des attestations fiscales par Email"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer les attestations fiscales générées"))

    def __do_layout(self):
##        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
##        
##        # Options
##        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
##        staticbox_options.Add(self.ctrl_options, 1, wx.ALL|wx.EXPAND, 5)
##        grid_sizer_base.Add(staticbox_options, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 0)
##        
##        # Attestations
##        staticbox_attestations = wx.StaticBoxSizer(self.staticbox_attestations_staticbox, wx.VERTICAL)
##        grid_sizer_attestations = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
##        grid_sizer_attestations.Add(self.ctrl_attestations, 1, wx.EXPAND, 0)
##
##        grid_sizer_commandes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
##        grid_sizer_commandes.Add(self.bouton_apercu_liste, 0, 0, 0)
##        grid_sizer_commandes.Add(self.bouton_imprimer_liste, 0, 0, 0)
##        grid_sizer_commandes.Add(self.bouton_export_texte, 0, 0, 0)
##        grid_sizer_commandes.Add(self.bouton_export_excel, 0, 0, 0)
##        grid_sizer_attestations.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
##
##        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=9, vgap=5, hgap=5)
##        grid_sizer_commandes.Add(self.hyper_payes, 0, 0, 0)
##        grid_sizer_commandes.Add(self.label_separation_1, 0, 0, 0)
##        grid_sizer_commandes.Add(self.hyper_tout, 0, 0, 0)
##        grid_sizer_commandes.Add(self.label_separation_2, 0, 0, 0)
##        grid_sizer_commandes.Add(self.hyper_rien, 0, 0, 0)
##        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
##        grid_sizer_commandes.Add(self.bouton_email, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_commandes.Add(self.bouton_imprimer, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        
##        grid_sizer_commandes.AddGrowableCol(5)
##        
##        grid_sizer_attestations.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
##        grid_sizer_attestations.AddGrowableCol(0)
##        grid_sizer_attestations.AddGrowableRow(0)
##        
##        staticbox_attestations.Add(grid_sizer_attestations, 1, wx.ALL|wx.EXPAND, 5)
##        grid_sizer_base.Add(staticbox_attestations, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)        
##                
##        self.SetSizer(grid_sizer_base)
##        grid_sizer_base.Fit(self)
##        grid_sizer_base.AddGrowableRow(1)
##        grid_sizer_base.AddGrowableCol(0)
##        self.Layout()


        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
                
        # Attestations
        staticbox_attestations = wx.StaticBoxSizer(self.staticbox_attestations_staticbox, wx.VERTICAL)
        grid_sizer_attestations = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_attestations.Add(self.ctrl_attestations, 1, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu_liste, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_imprimer_liste, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_export_texte, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_export_excel, 0, 0, 0)
        grid_sizer_attestations.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=9, vgap=5, hgap=5)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.hyper_payes, 0, 0, 0)
        grid_sizer_commandes.Add(self.label_separation_1, 0, 0, 0)
        grid_sizer_commandes.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_commandes.Add(self.label_separation_2, 0, 0, 0)
        grid_sizer_commandes.Add(self.hyper_rien, 0, 0, 0)

        grid_sizer_commandes.AddGrowableCol(0)
        
        grid_sizer_attestations.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_attestations.AddGrowableCol(0)
        grid_sizer_attestations.AddGrowableRow(0)
        
        staticbox_attestations.Add(grid_sizer_attestations, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_attestations, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)        
        
        # Gridsizer bas
        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_bas.AddGrowableRow(0)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        staticbox_options.Add(self.ctrl_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_bas.Add(staticbox_options, 1, wx.EXPAND, 0)
        
        # Boutons d'actions
        staticbox_actions = wx.StaticBoxSizer(self.staticbox_actions_staticbox, wx.VERTICAL)
        staticbox_actions.Add(self.bouton_email, 1, wx.EXPAND|wx.ALL, 5) 
        staticbox_actions.Add(self.bouton_imprimer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        grid_sizer_bas.Add(staticbox_actions, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()



    def CochePayes(self):
        self.ctrl_attestations.CocherPayes() 
        
    def CocheTout(self):
        self.ctrl_attestations.CocherTout()

    def DecocheTout(self):
        self.ctrl_attestations.CocherRien()
    
    def Validation(self):
        pass

    def MAJ(self):
        listeActivites = self.GetParent().page1.GetActivites() 
        self.ctrl_options.ctrl_signataire.MAJ(listeActivites)

        dlgAttente = PBI.PyBusyInfo(_(u"Recherche des données..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        try :
            listePrestations = self.GetParent().page1.GetPrestations() 
            self.ctrl_attestations.MAJ(listePrestations) 
            del dlgAttente
        except Exception, err :
            print err
            del dlgAttente


    def EcritStatusbar(self, texte=u""):
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass

    def Sauvegarder(self):
        """ Sauvegarde des attestations """
        # Demande la confirmation de sauvegarde
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous mémoriser les attestations ?\n\n(Cliquez NON si c'était juste un test sinon cliquez OUI)"), _(u"Sauvegarde"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        dlgAttente = PBI.PyBusyInfo(_(u"Sauvegarde des attestations en cours..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 

        DB = GestionDB.DB()
        
        try :
            for IDcompte_payeur, dictCompte in self.donnees.iteritems() :
                if dictCompte["select"] == True :
                    numero = dictCompte["num_attestation"]
                    IDfamille = dictCompte["IDfamille"] 
                    listePrestations = dictCompte["listePrestations"] 
                    total = dictCompte["total"] 
                    regle = dictCompte["ventilation"] 
                    solde = total - regle

                    # Liste des activités
                    texteActivites = ""
                    for IDactivite in self.listeActivites :
                        texteActivites += "%d;" % IDactivite
                    if len(self.listeActivites) > 0 :
                        texteActivites = texteActivites[:-1]
                    # Liste des individus
                    texteIndividus = ""
                    for IDindividu in dictCompte["individus"].keys() :
                        texteIndividus += "%d;" % IDindividu
                    if len(dictCompte["individus"].keys()) > 0 :
                        texteIndividus = texteIndividus[:-1]
                    
                    IDutilisateur = UTILS_Identification.GetIDutilisateur()
                    
                    # Sauvegarde de la facture
                    listeDonnees = [ 
                        ("numero", numero), 
                        ("IDfamille", IDfamille), 
                        ("date_edition", str(datetime.date.today())), 
                        ("activites", texteActivites), 
                        ("individus", texteIndividus), 
                        ("IDutilisateur", IDutilisateur), 
                        ("date_debut", str(self.date_debut)), 
                        ("date_fin", str(self.date_fin)), 
                        ("total", float(total)), 
                        ("regle", float(regle)), 
                        ("solde", float(solde)), 
                        ]

                    IDattestation = DB.ReqInsert("attestations", listeDonnees)
                                        
                    # Mémorisation de l'action dans l'historique
                    UTILS_Historique.InsertActions([{
                            "IDfamille" : IDfamille,
                            "IDcategorie" : 27, 
                            "action" : _(u"Edition d'une attestation de présence pour la période du %s au %s pour un total de %.02f € et un solde de %.02f €") % (DateEngFr(str(self.date_debut)), DateEngFr(str(self.date_fin)), total, solde),
                            },])

            DB.Close() 
            del dlgAttente

        except Exception, err:
            DB.Close() 
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la sauvegarde des attestations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
    
    def GetOptions(self):
        dictOptions = self.ctrl_options.GetOptions()
        if dictOptions == False :
            return False
        
        dictOptions["date_debut"], dictOptions["date_fin"] = self.GetParent().page1.GetPeriode()
        dictOptions["titre"] = _(u"Attestation fiscale")
        return dictOptions
        
    def Apercu(self, event=None): 
        """ Aperçu PDF des attestations """
        # Validation des données saisies
        tracks = self.ctrl_attestations.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune attestation à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des options
        dictOptions = self.GetOptions() 
        if dictOptions == False :
            return False
        
        # Impression des cotisations sélectionnées
        x = UTILS_Attestations_fiscales.Attestations_fiscales()
        x.Impression(tracks=tracks, afficherDoc=True, dictOptions=dictOptions, repertoire=dictOptions["repertoire"])

    
    def EnvoiEmail(self, event=None): 
        """ Envoi par Email des attestations fiscales """
        # Validation des données saisies
        tracks = self.ctrl_attestations.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune attestation à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Création des cotisations sélectionnées
        dictOptions = self.GetOptions() 
        if dictOptions == False :
            return False

        x = UTILS_Attestations_fiscales.Attestations_fiscales()
        resultat = x.Impression(tracks=tracks, nomDoc=None, afficherDoc=False, dictOptions=dictOptions, repertoire=dictOptions["repertoire"], repertoireTemp=True)
        if resultat == False : 
            return False
        dictChampsFusion, dictPieces = resultat
        
        def SupprimerFichiersTemp():
            for IDcompte_payeur, fichier in dictPieces.iteritems() :
                os.remove(fichier)  

        # Récupération de toutes les adresses Emails
        DB = GestionDB.DB()
        req = """SELECT IDindividu, mail, travail_mail
        FROM individus;"""
        DB.ExecuterReq(req)
        listeAdressesIndividus = DB.ResultatReq()
        DB.Close() 
        dictAdressesIndividus = {}
        for IDindividu, mail, travail_mail in listeAdressesIndividus :
            dictAdressesIndividus[IDindividu] = {"perso" : mail, "travail" : travail_mail}
                
        # Récupération des données adresse + champs + pièces
        listeDonnees = []
        listeAnomalies = []
        listeEnvoiNonDemande = []
        for track in tracks :
            adresse = UTILS_Envoi_email.GetAdresseFamille(track.IDfamille, choixMultiple=False, muet=True, nomTitulaires=track.nomsTitulaires)
            
            # Mémorisation des données
            if adresse not in (None, "", []) : 
                if dictPieces.has_key(track.IDcompte_payeur) :
                    fichier = dictPieces[track.IDcompte_payeur]
                    champs = dictChampsFusion[track.IDcompte_payeur]
                    listeDonnees.append({"adresse" : adresse, "pieces" : [fichier,], "champs" : champs})
            else :
                listeAnomalies.append(track.nomsTitulaires)
        
        # Annonce les anomalies trouvées
        if len(listeAnomalies) > 0 :
            texte = _(u"%d des familles sélectionnées n'ont pas d'adresse Email.\n\n") % len(listeAnomalies)
            texte += _(u"Souhaitez-vous quand même continuer avec les %d autres familles ?") % len(listeDonnees)
            dlg = wx.MessageDialog(self, texte, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                SupprimerFichiersTemp()
                return        
        
        # Dernière vérification avant transfert
        if len(listeDonnees) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Il ne reste finalement aucune attestation fiscale à envoyer par Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            SupprimerFichiersTemp()
            return

        # Transfert des données vers DLG Mailer
        import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self, categorie="attestation_fiscale")
        dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
        dlg.ChargerModeleDefaut()
        dlg.ShowModal() 
        dlg.Destroy()

        # Suppression des PDF temporaires
        SupprimerFichiersTemp()







# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.panel = panel
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        self.ctrl.Validation()
        print self.panel.dictParametres

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

##    import DLG_Attestations_fiscales_generation
##    dlg = DLG_Attestations_fiscales_generation.Dialog(None)
##    dlg.ShowModal()
##    dlg.Destroy()

