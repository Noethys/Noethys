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
import datetime
import os
import sys
import wx.lib.agw.customtreectrl as CT

from Ctrl import CTRL_Bandeau
import GestionDB
from Utils import UTILS_Sauvegarde
from Utils import UTILS_Fichiers
from Utils import UTILS_Cryptage_fichier
sys.modules['UTILS_Cryptage_fichier'] = UTILS_Cryptage_fichier

import DLG_Saisie_param_reseau

try: import psyco; psyco.full()
except: pass

LISTE_CATEGORIES = UTILS_Sauvegarde.LISTE_CATEGORIES


def SelectionFichier():
    """ Sélectionner le fichier à restaurer """
    # Demande l'emplacement du fichier
    wildcard = _(u"Sauvegarde Noethys (*.nod; *.noc)|*.nod; *.noc")
    standardPath = wx.StandardPaths.Get()
    rep = standardPath.GetDocumentsDir()
    dlg = wx.FileDialog(None, message=_(u"Veuillez sélectionner le fichier de sauvegarde à restaurer"), defaultDir=rep, defaultFile="", wildcard=wildcard, style=wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:
        fichier = dlg.GetPath()
    else:
        return None
    dlg.Destroy()
    
    # Décryptage du fichier
    if fichier.endswith(".noc") == True :
        dlg = wx.PasswordEntryDialog(None, _(u"Veuillez saisir le mot de passe :"), _(u"Ouverture d'une sauvegarde cryptée"))
        if dlg.ShowModal() == wx.ID_OK:
            motdepasse = dlg.GetValue()
        else:
            dlg.Destroy()
            return None
        dlg.Destroy()
        fichierTemp = UTILS_Fichiers.GetRepTemp(fichier="savedecrypte.zip")
        resultat = UTILS_Cryptage_fichier.DecrypterFichier(fichier, fichierTemp, motdepasse)
        fichier = fichierTemp
        messageErreur = _(u"Le mot de passe que vous avez saisi semble erroné !")
    else:
        messageErreur = _(u"Le fichier de sauvegarde semble corrompu !")
                
    # Vérifie que le ZIP est ok
    valide = UTILS_Sauvegarde.VerificationZip(fichier)
    if valide == False :
        dlg = wx.MessageDialog(None, messageErreur, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return None

    return fichier

    


class CTRL_Donnees(CT.CustomTreeCtrl):
    def __init__(self, parent, listeFichiers=[], id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SUNKEN_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.listeFichiers = listeFichiers
        
        self.root = self.AddRoot(_(u"Données"))
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True)

        # Fichiers locaux
        listeFichiersLocaux = self.GetListeFichiersLocaux()
        if len(listeFichiersLocaux) > 0 :
            brancheType = self.AppendItem(self.root, _(u"Fichiers locaux"), ct_type=1)
            self.SetPyData(brancheType, _(u"locaux"))
            self.SetItemBold(brancheType)
            self.CheckItem(brancheType, True)
            
            for nomFichier in listeFichiersLocaux :
                brancheNom = self.AppendItem(brancheType, nomFichier, ct_type=1)
                self.SetPyData(brancheNom, nomFichier)
                self.CheckItem(brancheNom, True)
                
                for nomCategorie, codeCategorie in LISTE_CATEGORIES :
                    fichier = u"%s_%s.dat" % (nomFichier, codeCategorie)
                    if fichier in self.listeFichiers :
                        brancheFichier = self.AppendItem(brancheNom, nomCategorie, ct_type=1)
                        self.SetPyData(brancheFichier, fichier)
                        self.CheckItem(brancheFichier, True)

        # Fichiers réseaux
        listeFichiersReseau = self.GetListeFichiersReseau()
        if len(listeFichiersReseau) > 0 :
            brancheType = self.AppendItem(self.root, _(u"Fichiers réseau"), ct_type=1)
            self.SetPyData(brancheType, _(u"reseau"))
            self.SetItemBold(brancheType)
            self.CheckItem(brancheType, True)
            
            for nomFichier in listeFichiersReseau :
                brancheNom = self.AppendItem(brancheType, nomFichier, ct_type=1)
                self.SetPyData(brancheNom, nomFichier)
                self.CheckItem(brancheNom, True)
                
                for nomCategorie, codeCategorie in LISTE_CATEGORIES :
                    fichier = u"%s_%s.sql" % (nomFichier, codeCategorie.lower())
                    if fichier in self.listeFichiers :
                        brancheFichier = self.AppendItem(brancheNom, nomCategorie, ct_type=1)
                        self.SetPyData(brancheFichier, fichier)
                        self.CheckItem(brancheFichier, True)

        self.ExpandAll() 

    def GetListeFichiersLocaux(self):
        """ Trouver les fichiers locaux présents dans le ZIP """
        listeLocaux = []
        for fichier in self.listeFichiers :
            if fichier[-9:] == "_DATA.dat" : 
                nomFichier = fichier[:-9]
                listeLocaux.append(nomFichier)
        listeLocaux.sort()
        return listeLocaux

    def GetListeFichiersReseau(self):
        """ Trouver les fichiers MySQL présents dans le ZIP """
        listeReseau = []
        for fichier in self.listeFichiers :
            if fichier[-9:] == "_data.sql" : 
                nomFichier = fichier[:-9]
                listeReseau.append(nomFichier)
        listeReseau.sort()
        return listeReseau

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

# ------------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, fichier=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.fichier = fichier
        self.listeFichiersRestaures = []
        
        # Récupération du contenu du ZIP
        self.listeFichiers = UTILS_Sauvegarde.GetListeFichiersZIP(fichier)
        
        intro = _(u"Vous pouvez ici restaurer une sauvegarde. Vous devez sélectionner dans la liste des données présentes dans la sauvegarde celles que vous souhaiter restaurer.")
        titre = _(u"Restauration")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Restaurer.png")
                
        # Données
        self.box_donnees_staticbox = wx.StaticBox(self, -1, _(u"Données à restaurer"))
        self.ctrl_donnees = CTRL_Donnees(self, listeFichiers=self.listeFichiers)
        self.ctrl_donnees.SetMinSize((250, -1))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer la restauration")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((420, 460))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        box_donnees = wx.StaticBoxSizer(self.box_donnees_staticbox, wx.VERTICAL)
        box_donnees.Add(self.ctrl_donnees, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_donnees, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        UTILS_Aide.Aide("Restaurerunesauvegarde")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):         
        # Données à sauver
        dictDonnees = self.ctrl_donnees.GetCoches() 
        if dictDonnees.has_key("locaux") :
            listeFichiersLocaux = dictDonnees["locaux"]
        else:
            listeFichiersLocaux = []
        if dictDonnees.has_key("reseau") :
            listeFichiersReseau = dictDonnees["reseau"]
        else:
            listeFichiersReseau = []
        
        if len(listeFichiersLocaux) == 0 and len(listeFichiersReseau) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un fichier à restaurer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des paramètres de connexion réseau
        dictConnexion = None
        
        if len(listeFichiersReseau) > 0 :
            # Récupère les paramètres chargés
            DB = GestionDB.DB() 
            if DB.echec != 1 :
                if DB.isNetwork == True :
                    dictConnexion = DB.GetParamConnexionReseau() 
            DB.Close() 
            
            # Demande les paramètres de connexion réseau
            if dictConnexion == None :
                
                # Demande les paramètres de connexion
                intro = _(u"Les fichiers que vos souhaitez restaurer nécessite une connexion réseau.\nVeuillez saisir vos paramètres de connexion MySQL:")
                dlg = DLG_Saisie_param_reseau.Dialog(self, intro=intro)
                if dlg.ShowModal() == wx.ID_OK:
                    dictConnexion = dlg.GetDictValeurs()
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    return
                
                # Vérifie si la connexion est bonne
                resultat = DLG_Saisie_param_reseau.TestConnexion(dictConnexion)
                if resultat == False :
                    dlg = wx.MessageDialog(self, _(u"Echec du test de connexion.\n\nLes paramètres ne semblent pas exacts !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
         
        # Sauvegarde
        resultat = UTILS_Sauvegarde.Restauration(self.parent, self.fichier, listeFichiersLocaux, listeFichiersReseau, dictConnexion)
        if resultat == False :
            return
        self.listeFichiersRestaures = resultat
        
        # Fin du processus
        dlg = wx.MessageDialog(self, _(u"Le processus de restauration est terminé."), _(u"Restauration"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        # Fermeture
        self.EndModal(wx.ID_OK)
    
    def GetFichiersRestaures(self):
        """ Récupère la liste des fichiers restaurés """
        listeTemp = []
        for fichier in self.listeFichiersRestaures :
            if fichier[-5:] in ("_DATA", "_data") : 
                nomFichier = fichier[:-5]
                listeTemp.append(nomFichier)
        return listeTemp
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    fichier = SelectionFichier()
    if fichier != None :
        dialog_1 = Dialog(None, fichier=fichier)
        app.SetTopWindow(dialog_1)
        dialog_1.ShowModal()
    app.MainLoop()
