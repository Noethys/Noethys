#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import os
import wx.lib.agw.customtreectrl as CT
import base64
import six
from Ctrl import CTRL_Bandeau
import GestionDB
from Utils import UTILS_Sauvegarde
from Utils import UTILS_Config
from Dlg import DLG_Saisie_param_reseau
from Utils import UTILS_Fichiers


LISTE_CATEGORIES = UTILS_Sauvegarde.LISTE_CATEGORIES




class CTRL_Donnees(CT.CustomTreeCtrl):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SUNKEN_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.root = self.AddRoot(_(u"Données"))
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True)
        
        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.OnCheck)
    
    def MAJ(self):
        cochesPrecedents = self.GetCoches() 
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Données"))
        
        # Fichiers locaux
        listeFichiersLocaux = self.GetListeFichiersLocaux()
        if len(listeFichiersLocaux) > 0 and self.parent.check_locaux.GetValue() == True :
            brancheType = self.AppendItem(self.root, _(u"Fichiers locaux"), ct_type=1)
            self.SetPyData(brancheType, _(u"locaux"))
            self.SetItemBold(brancheType)
            
            for nomFichier in listeFichiersLocaux :
                brancheNom = self.AppendItem(brancheType, nomFichier, ct_type=1)
                self.SetPyData(brancheNom, nomFichier)
                
                for nomCategorie, codeCategorie in LISTE_CATEGORIES :
                    fichier = u"%s_%s.dat" % (nomFichier, codeCategorie)
                    brancheFichier = self.AppendItem(brancheNom, nomCategorie, ct_type=1)
                    self.SetPyData(brancheFichier, fichier)
                    
                    if os.path.isfile(UTILS_Fichiers.GetRepData(fichier)) == False :
                        brancheFichier.Enable(False)

        # Fichiers réseaux
        listeFichiersReseau, listeBases = self.GetListeFichiersReseau()
        if len(listeFichiersReseau) > 0  and self.parent.check_reseau.GetValue() == True :
            brancheType = self.AppendItem(self.root, _(u"Fichiers réseau"), ct_type=1)
            self.SetPyData(brancheType, _(u"reseau"))
            self.SetItemBold(brancheType)
            
            for nomFichier in listeFichiersReseau :
                brancheNom = self.AppendItem(brancheType, nomFichier, ct_type=1)
                self.SetPyData(brancheNom, nomFichier)
                
                for nomCategorie, codeCategorie in LISTE_CATEGORIES :
                    fichier = u"%s_%s" % (nomFichier, codeCategorie.lower())
                    brancheFichier = self.AppendItem(brancheNom, nomCategorie, ct_type=1)
                    self.SetPyData(brancheFichier, fichier)
                    
                    if fichier not in listeBases :
                        brancheFichier.Enable(False)

        self.ExpandAll() 
        
        # Rétablit les coches précédents
        if len(cochesPrecedents) > 0 :
            self.SetCoches(cochesPrecedents)
            
        self.AfficheNbreElements()
        
    def GetListeFichiersLocaux(self):
        """ Trouver les fichiers présents sur le DD """
        listeFichiersTmp = os.listdir(UTILS_Fichiers.GetRepData())
        listeFichiers = []
        for fichier in listeFichiersTmp :
            if fichier[-9:] == "_DATA.dat" : 
                nomFichier = fichier[:-9]
                if nomFichier.startswith("EXEMPLE_") == False :
                    listeFichiers.append(nomFichier)
        listeFichiers.sort()
        return listeFichiers

    def GetListeFichiersReseau(self):
        """ Trouver les fichiers MySQL """
        listeFichiers = []
        if self.parent.dictConnexion == None :
            return [], []
        
##        try :
        listeBases = UTILS_Sauvegarde.GetListeFichiersReseau(self.parent.dictConnexion)
        for fichier in listeBases :
            if fichier[-5:] == "_DATA".lower() : 
                nomFichier = fichier[:-5]
                listeFichiers.append(nomFichier)
        listeFichiers.sort()
##        except : 
##            return [], []
        return listeFichiers, listeBases

    def GetCoches(self):
        """ Obtient la liste des éléments cochés """
        dictDonnees = {}
        
        brancheType = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            nomType = self.GetItemPyData(brancheType)
            dictDonnees[nomType] = []
            
            # Branche nom du fichier
            brancheNom = self.GetFirstChild(brancheType)[0]
            for index2 in range(self.GetChildrenCount(brancheType, recursively=False)) :
                nomFichier = self.GetItemPyData(brancheNom)
                
                # Branche code fichier
                brancheCode = self.GetFirstChild(brancheNom)[0]
                for index3 in range(self.GetChildrenCount(brancheNom, recursively=False)) :
                    nomFichierComplet = self.GetItemPyData(brancheCode)
                    
                    if self.IsItemChecked(brancheCode) :
                        dictDonnees[nomType].append(nomFichierComplet)
                    
                    brancheCode = self.GetNextChild(brancheNom, index3+1)[0]
                brancheNom = self.GetNextChild(brancheType, index2+1)[0]
            brancheType = self.GetNextChild(self.root, index1+1)[0]
                        
        return dictDonnees

    def SetCoches(self, listeFichiers=[], etat=True):
        brancheType = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            nomType = self.GetItemPyData(brancheType)
            
            # Branche nom du fichier
            brancheNom = self.GetFirstChild(brancheType)[0]
            for index2 in range(self.GetChildrenCount(brancheType, recursively=False)) :
                nomFichier = self.GetItemPyData(brancheNom)
                
                # Branche code fichier
                brancheCode = self.GetFirstChild(brancheNom)[0]
                nbreFichiers = self.GetChildrenCount(brancheNom, recursively=False)
                nbreFichiersCoches = 0
                for index3 in range(nbreFichiers) :
                    nomFichierComplet = self.GetItemPyData(brancheCode)
                    
                    if nomFichierComplet in listeFichiers :
                        self.CheckItem(brancheCode, etat)
                        nbreFichiersCoches += 1
                    
                    brancheCode = self.GetNextChild(brancheNom, index3+1)[0]

                if nbreFichiersCoches == nbreFichiers :
                    self.CheckItem(brancheNom, etat)

                brancheNom = self.GetNextChild(brancheType, index2+1)[0]
            brancheType = self.GetNextChild(self.root, index1+1)[0]
    
    def OnCheck(self, event):
        self.AfficheNbreElements()
        
    def AfficheNbreElements(self):
        dictDonnees = self.GetCoches() 
        if "locaux" in dictDonnees and len(dictDonnees["locaux"]) > 0 :
            listeFichiersLocaux = len(dictDonnees["locaux"])
        else:
            listeFichiersLocaux = 0
        if "reseau" in dictDonnees and len(dictDonnees["reseau"]) > 0 :
            listeFichiersReseau = len(dictDonnees["reseau"])
        else:
            listeFichiersReseau = 0
        nbreElements = listeFichiersLocaux + listeFichiersReseau
        texte = _(u"Données à sauvegarder (%d éléments cochés)") % nbreElements
        self.parent.box_donnees_staticbox.SetLabel(texte)
        

# ------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Panel) :
    def __init__(self, parent, labelControleNom=_(u"Nom")) :
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.labelControleNom = labelControleNom
        
        # Nom
        self.box_nom_staticbox = wx.StaticBox(self, -1, labelControleNom)
        self.label_nom = wx.StaticText(self, -1, u"%s :" % labelControleNom)
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Protection
        self.box_mdp_staticbox = wx.StaticBox(self, -1, _(u"Protection"))
        self.label_cryptage = wx.StaticText(self, -1, _(u"Cryptage :"))
        self.check_cryptage = wx.CheckBox(self, -1, u"")
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        self.label_confirmation = wx.StaticText(self, -1, _(u"Confirmation :"))
        self.ctrl_confirmation = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        
        # Destination
        self.box_destination_staticbox = wx.StaticBox(self, -1, _(u"Destination"))
        self.check_repertoire = wx.CheckBox(self, -1, _(u"Répertoire :"))
        self.ctrl_repertoire = wx.TextCtrl(self, -1, u"")
        self.bouton_repertoire = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Repertoire.png"), wx.BITMAP_TYPE_ANY))
        self.check_email = wx.CheckBox(self, -1, _(u"Envoi par Email :"))
        self.ctrl_email = wx.TextCtrl(self, -1, u"")
        
        # Données
        self.box_donnees_staticbox = wx.StaticBox(self, -1, _(u"Données à sauvegarder"))
        self.ctrl_donnees = CTRL_Donnees(self)
        self.ctrl_donnees.SetMinSize((300, -1))
        self.check_locaux = wx.CheckBox(self, -1, _(u"Fichiers locaux"))
        self.check_reseau = wx.CheckBox(self, -1, _(u"Fichiers réseau"))

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCryptage, self.check_cryptage)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRepertoire, self.check_repertoire)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRepertoire, self.bouton_repertoire)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckEmail, self.check_email)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckLocaux, self.check_locaux)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckReseau, self.check_reseau)

        # Init Contrôles
        self.OnCheckCryptage(None) 
        self.OnCheckRepertoire(None) 
        self.OnCheckEmail(None) 

        self.check_locaux.SetValue(True)
        # Récupération des paramètres de connexion réseau
        self.dictConnexion = None
        DB = GestionDB.DB() 
        if DB.echec != 1 :
            if DB.isNetwork == True :
                self.check_reseau.SetValue(True)
                self.dictConnexion = DB.GetParamConnexionReseau() 
        DB.Close() 
        
        self.ctrl_donnees.MAJ() 

    def __set_properties(self):
        self.check_cryptage.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour crypter le fichier de sauvegarde (utile pour un stockage en ligne)")))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le %s du fichier de sauvegarde") % self.labelControleNom.lower()))
        self.ctrl_mdp.SetToolTip(wx.ToolTip(_(u"Si vous souhaitez protéger le fichier de sauvegarde avec un mot de passe, tapez-le ici")))
        self.ctrl_confirmation.SetToolTip(wx.ToolTip(_(u"Confirmez le mot de passe")))
        self.check_repertoire.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour enregistrer le fichier de sauvegarde dans le répertoire donné")))
        self.ctrl_repertoire.SetMinSize((180, -1))
        self.ctrl_repertoire.SetToolTip(wx.ToolTip(_(u"Saisissez ici le répertoire de destination")))
        self.bouton_repertoire.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un répertoire de destination")))
        self.check_email.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour envoyer la sauvegarde par Email")))
        self.ctrl_email.SetToolTip(wx.ToolTip(_(u"Saisissez ici une ou plusieurs adresses Email (separées par des points-virgules)")))
        self.check_locaux.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les fichiers locaux")))
        self.check_reseau.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les fichiers réseau")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        box_donnees = wx.StaticBoxSizer(self.box_donnees_staticbox, wx.VERTICAL)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Nom
        box_nom = wx.StaticBoxSizer(self.box_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        box_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_nom, 1, wx.EXPAND, 0)
        
        # mdp
        box_mdp = wx.StaticBoxSizer(self.box_mdp_staticbox, wx.VERTICAL)
        grid_sizer_mdp = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_mdp.Add(self.label_cryptage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mdp.Add(self.check_cryptage, 0, wx.EXPAND, 0)
        grid_sizer_mdp.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mdp.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_mdp.Add(self.label_confirmation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mdp.Add(self.ctrl_confirmation, 0, wx.EXPAND, 0)
        grid_sizer_mdp.AddGrowableCol(1)
        box_mdp.Add(grid_sizer_mdp, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_mdp, 1, wx.EXPAND, 0)
                        
        # Destination
        box_destination = wx.StaticBoxSizer(self.box_destination_staticbox, wx.VERTICAL)
        grid_sizer_destination = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)

        # Email
        grid_sizer_email = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_email.Add(self.check_email, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_email.Add(self.ctrl_email, 0, wx.EXPAND, 0)
        grid_sizer_email.AddGrowableCol(1)
        grid_sizer_destination.Add(grid_sizer_email, 1, wx.EXPAND, 0)

        # Répertoire
        grid_sizer_repertoire = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_repertoire.Add(self.check_repertoire, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_repertoire.Add(self.ctrl_repertoire, 0, wx.EXPAND, 0)
        grid_sizer_repertoire.Add(self.bouton_repertoire, 0, 0, 0)
        grid_sizer_repertoire.AddGrowableCol(1)
        grid_sizer_destination.Add(grid_sizer_repertoire, 1, wx.EXPAND, 0)

        box_destination.Add(grid_sizer_destination, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_destination, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT, 10)
        
        box_donnees.Add(self.ctrl_donnees, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Checkbox filtres
        grid_sizer_filtres = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_filtres.Add(self.check_locaux, 0, 0, 0)
        grid_sizer_filtres.Add(self.check_reseau, 0, 0, 0)
        box_donnees.Add(grid_sizer_filtres, 0, wx.ALL, 10)
        
        grid_sizer_base.Add(box_donnees, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        self.Layout()

    
    def OnCheckCryptage(self, event):
        etat = self.check_cryptage.GetValue() 
        self.ctrl_mdp.Enable(etat)
        self.ctrl_confirmation.Enable(etat)
        
    def OnCheckRepertoire(self, event): 
        etat = self.check_repertoire.GetValue() 
        self.ctrl_repertoire.Enable(etat)
        self.bouton_repertoire.Enable(etat)
        
    def OnCheckEmail(self, event):
        etat = self.check_email.GetValue() 
        self.ctrl_email.Enable(etat)

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
    
    def OnCheckLocaux(self, event):
        self.ctrl_donnees.MAJ() 
        
    def OnCheckReseau(self, event):
        if self.dictConnexion == None :
            # Demande les paramètres de connexion
            intro = _(u"Pour accéder à la liste des fichiers réseau disponibles, un accès MySQL \nest nécessaire. Veuillez saisir vos paramètres de connexion réseau :")
            dlg = DLG_Saisie_param_reseau.Dialog(self, intro=intro)
            if dlg.ShowModal() == wx.ID_OK:
                dictValeurs = dlg.GetDictValeurs()
                dlg.Destroy()
            else:
                dlg.Destroy()
                self.check_reseau.SetValue(False)
                return
            # Vérifie si la connexion est bonne
            resultat = DLG_Saisie_param_reseau.TestConnexion(dictValeurs)
            if resultat == False :
                dlg = wx.MessageDialog(self, _(u"Echec du test de connexion.\n\nLes paramètres ne semblent pas exacts !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.check_reseau.SetValue(False)
                return
            self.dictConnexion = dictValeurs
        # MAJ de la liste des données
        self.ctrl_donnees.MAJ() 
    
    def SetDonnees(self, dictDonnees={}):
        nom = dictDonnees["sauvegarde_nom"]
        if nom != None :
            self.ctrl_nom.SetValue(nom)
        
        motdepasse = dictDonnees["sauvegarde_motdepasse"]
        if motdepasse != "" and motdepasse != None :
            try :
                motdepasse = base64.b64decode(motdepasse)
            except :
                pass
            self.check_cryptage.SetValue(True)
            self.ctrl_mdp.SetValue(motdepasse)
            self.ctrl_confirmation.SetValue(motdepasse)
            
        repertoire = dictDonnees["sauvegarde_repertoire"]
        if repertoire != "" and repertoire != None :
            self.check_repertoire.SetValue(True)
            self.ctrl_repertoire.SetValue(repertoire)
        else:
            self.check_repertoire.SetValue(True)
            standardPath = wx.StandardPaths.Get()
            destination = standardPath.GetDocumentsDir()
            self.ctrl_repertoire.SetValue(destination)
        
        emails = dictDonnees["sauvegarde_emails"]
        if emails != "" and emails != None :
            self.check_email.SetValue(True)
            self.ctrl_email.SetValue(emails)
        
        self.OnCheckCryptage(None) 
        self.OnCheckRepertoire(None) 
        self.OnCheckEmail(None) 
        
        listeFichiersLocaux = dictDonnees["sauvegarde_fichiers_locaux"]
        listeFichiersReseau = dictDonnees["sauvegarde_fichiers_reseau"]
        
        if listeFichiersReseau != None :
            self.check_reseau.SetValue(True)
            self.OnCheckReseau(None)
            liste = listeFichiersReseau.split(";")
            self.ctrl_donnees.SetCoches(liste)

        if listeFichiersLocaux != None :
            liste = listeFichiersLocaux.split(";")
            self.ctrl_donnees.SetCoches(liste)
            
        self.ctrl_donnees.AfficheNbreElements()

    def GetDonnees(self):
        # Nom
        nom = self.ctrl_nom.GetValue() 
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un %s pour cette sauvegarde !") % self.labelControleNom.lower(), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False
        
        # Mot de passe
        if self.check_cryptage.GetValue() == True :
            motdepasse = self.ctrl_mdp.GetValue() 
            confirmation = self.ctrl_confirmation.GetValue() 
            if motdepasse == "" :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun mot de passe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_mdp.SetFocus()
                return False
            if motdepasse != confirmation :
                dlg = wx.MessageDialog(self, _(u"Le mot de passe n'a pas été confirmé à l'identique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_confirmation.SetFocus()
                return False
            if six.PY3:
                motdepasse = six.binary_type(motdepasse, "utf-8")
            motdepasse = base64.b64encode(motdepasse)
        else:
            motdepasse = None
        
        # Répertoire
        if self.check_repertoire.GetValue() == True :
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
        
        # Emails
        if self.check_email.GetValue() == True :
            listeEmails = self.ctrl_email.GetValue() 
            if listeEmails == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir au moins une adresse Email !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_email.SetFocus()
                return False
        else:
            listeEmails = None
        
        # Vérifie qu'il y a une destination
        if self.check_repertoire.GetValue() == False and self.check_email.GetValue() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une destination !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Données à sauver
        dictDonnees = self.ctrl_donnees.GetCoches() 
        if "locaux" in dictDonnees and len(dictDonnees["locaux"]) > 0 :
            listeFichiersLocaux = ";".join(dictDonnees["locaux"])
        else:
            listeFichiersLocaux = None
        if "reseau" in dictDonnees and len(dictDonnees["reseau"]) > 0 :
            listeFichiersReseau = ";".join(dictDonnees["reseau"])
        else:
            listeFichiersReseau = None
        
        if listeFichiersLocaux == None and listeFichiersReseau == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un élément à sauvegarder dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Envoi des données
        dictDonnees = {
            "sauvegarde_fichiers_locaux" : listeFichiersLocaux, 
            "sauvegarde_fichiers_reseau" : listeFichiersReseau, 
            "sauvegarde_nom" : nom, 
            "sauvegarde_repertoire" : repertoire, 
            "sauvegarde_motdepasse" : motdepasse, 
            "sauvegarde_emails" : listeEmails, 
            }
        
        return dictDonnees



# ------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, dictDonnees=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)#|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.dictDonnees = dictDonnees
        self.resultat = False

        intro = _(u"Vous pouvez créer ici une sauvegarde des données afin d'en la conservation ou de les transférer sur un autre ordinateur. Il est possible de crypter le fichier de sauvegarde et de l'enregistrer sur le disque dur ou une clé USB et de l'expédier par Email.")
        titre = _(u"Sauvegarde")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Sauvegarder.png")
        
        # Panel de contenu
        self.ctrl_parametres = CTRL_Parametres(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contrôles
        if dictDonnees != None :
            self.ctrl_parametres.SetDonnees(dictDonnees) 
        else :
            self.Importation() 

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer la sauvegarde")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_base.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
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
        UTILS_Aide.Aide("Crerunesauvegarde")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)
    
    def Importation(self):
        """ Importation des données par défaut """
        dictSauvegarde = {
            "sauvegarde_nom" : _(u"Noethys_%s") % datetime.datetime.now().strftime("%Y%m%d_%H%M"),
            "sauvegarde_motdepasse" : UTILS_Config.GetParametre("sauvegarde_mdp", defaut=None),
            "sauvegarde_repertoire" : UTILS_Config.GetParametre("sauvegarde_repertoire", defaut=None),
            "sauvegarde_emails" : UTILS_Config.GetParametre("sauvegarde_emails", defaut=None),
            "sauvegarde_fichiers_locaux" : UTILS_Config.GetParametre("sauvegarde_fichiers_locaux", defaut=None),
            "sauvegarde_fichiers_reseau" : UTILS_Config.GetParametre("sauvegarde_fichiers_reseau", defaut=None),
            }
        self.ctrl_parametres.SetDonnees(dictSauvegarde) 

    def OnBoutonOk(self, event): 
        # Validation des données
        dictDonnees = self.ctrl_parametres.GetDonnees() 
        if dictDonnees == False :
            return
        
        # Récupère paramètres
        listeFichiersLocaux = dictDonnees["sauvegarde_fichiers_locaux"]
        listeFichiersReseau = dictDonnees["sauvegarde_fichiers_reseau"]
        nom = dictDonnees["sauvegarde_nom"]
        repertoire = dictDonnees["sauvegarde_repertoire"]
        motdepasse = dictDonnees["sauvegarde_motdepasse"]
        listeEmails = dictDonnees["sauvegarde_emails"]
        dictConnexion = self.ctrl_parametres.dictConnexion
        
        if listeFichiersLocaux == None :
            listeFichiersLocaux = []
        else :
            listeFichiersLocaux = listeFichiersLocaux.split(";")
        if listeFichiersReseau == None :
            listeFichiersReseau = []
        else :
            listeFichiersReseau = listeFichiersReseau.split(";")
        if listeEmails != None :
            listeEmails = listeEmails.split(";")
        
        # Sauvegarde
        self.resultat = UTILS_Sauvegarde.Sauvegarde(listeFichiersLocaux, listeFichiersReseau, nom, repertoire, motdepasse, listeEmails, dictConnexion)
        if self.resultat == False :
            return False

        # Fin du processus
        dlg = wx.MessageDialog(self, _(u"La procédure de sauvegarde est terminée."), _(u"Sauvegarde"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        # Fermeture
        self.MemoriseParametres() 
        self.EndModal(wx.ID_OK)
    
    def GetResultat(self):
        return self.resultat

    def MemoriseParametres(self):
        if self.dictDonnees == None :
            dictDonnees = self.ctrl_parametres.GetDonnees()
            UTILS_Config.SetParametre("sauvegarde_mdp", dictDonnees["sauvegarde_motdepasse"])
            UTILS_Config.SetParametre("sauvegarde_repertoire", dictDonnees["sauvegarde_repertoire"])
            UTILS_Config.SetParametre("sauvegarde_emails", dictDonnees["sauvegarde_emails"])
            UTILS_Config.SetParametre("sauvegarde_fichiers_locaux", dictDonnees["sauvegarde_fichiers_locaux"])
            UTILS_Config.SetParametre("sauvegarde_fichiers_reseau", dictDonnees["sauvegarde_fichiers_reseau"])



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
