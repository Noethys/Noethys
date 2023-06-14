#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Fichiers
import os
import sys
import importlib
import shutil
import codecs



class CTRL_Extensions(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.MAJ()
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.Executer)

    def MAJ(self, IDactivite=None):
        # Recherche d'extensions dans le répertoire
        ext = "py"
        fichiers = os.listdir(UTILS_Fichiers.GetRepExtensions())
        fichiers.sort()
        listeExtensions = []
        for fichier in fichiers:
            if fichier.endswith(ext):
                nomFichier = os.path.split(fichier)[1]
                titre = nomFichier[:-(len(ext) + 1)]
                listeExtensions.append(titre)

        listeItems = []
        self.Clear()
        if len(listeExtensions) > 0:
            self.Set(listeExtensions)
            self.Select(0)

    def Importer(self, event=None):
        # Ouverture de la fenêtre de dialogue
        wildcard = _(u"Module python (*.py)|*.py|Tous les fichiers (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une extension à importer"),
            defaultDir=sp.GetDocumentsDir(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Cherche si le fichier
        fichier = codecs.open(nomFichierLong, encoding='utf8', mode='r')
        texte = "\n".join(fichier.readlines())
        fichier.close()
        if "def Extension(" not in texte:
            dlg = wx.MessageDialog(self, _(u"Cette extension ne semble pas valide.\n\nUne extension est un module Python qui doit obligatoirement contenir une fonction Extension()."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Copie le fichier vers le répertoire Extensions
        shutil.copyfile(nomFichierLong, UTILS_Fichiers.GetRepExtensions(nomFichierCourt))
        self.MAJ()

    def Supprimer(self, event=None):
        if self.GetSelection() == -1:
            dlg = wx.MessageDialog(self, _(u"Aucune extension n'a été sélectionnée dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        nom_fichier = self.GetStringSelection()
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer l'extension '%s' ?") % nom_fichier, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False
        os.remove(UTILS_Fichiers.GetRepExtensions(nom_fichier + ".py"))
        self.MAJ()

    def Executer(self, event=None):
        if self.GetSelection() == -1:
            dlg = wx.MessageDialog(self, _(u"Aucune extension n'a été sélectionnée dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Exécution de l'extension
        nom_fichier = self.GetStringSelection()
        sys.path.append(UTILS_Fichiers.GetRepExtensions())
        module = importlib.import_module(nom_fichier)
        module.Extension()


# -------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Extensions", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici exécuter, importer ou supprimer des extensions. Une extension est un module Python qui apporte des fonctionnalités supplémentaires. Une extension doit contenir une fonction Extension().")
        titre = _(u"Extensions")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Terminal.png")
        self.ctrl_extensions = CTRL_Extensions(self)
        self.ctrl_extensions.MAJ()

        self.bouton_executer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Avancer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_importer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_import.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
            
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_extensions.Executer, self.bouton_executer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_extensions.Importer, self.bouton_importer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_extensions.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)


    def __set_properties(self):
        self.bouton_importer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour importer une extension")))
        self.bouton_executer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exécuter l'extension sélectionnée dans la liste ou double-cliquez sur la ligne correspondante dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'extension sélectionnée dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((550, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_droit = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_extensions, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_droit.Add(self.bouton_executer, 0, 0, 0)
        grid_sizer_droit.Add((10, 10), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_importer, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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
        UTILS_Aide.Aide("Extensions")




if __name__ == "__main__":
    app = wx.App(0)
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
