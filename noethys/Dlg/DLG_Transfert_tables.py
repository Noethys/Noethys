#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
from Ctrl import CTRL_Bandeau
import GestionDB
import wx.lib.filebrowsebutton as filebrowse
import time


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)

        # Bandeau
        titre = _(u"Transférer des tables")
        intro = _(u"Cette fonctionnalité permet de transférer le contenu des tables du fichier de données chargé vers un fichier de données local.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Configuration.png")
        self.SetTitle(titre)

        self.label_destination = wx.StaticText(self, -1, _(u"Fichier de destination :"))

        wildcard = _(u"Fichiers Noethys (*.dat)|*.dat|All files (*.*)|*.*")
        self.ctrl_destination = filebrowse.FileBrowseButton(self, -1, labelText=u"", buttonText=_(u"Sélectionner"), toolTip=_(u"Cliquez ici pour sélectionner un fichier de données"), dialogTitle=_(u"Sélectionner un fichier"), fileMask=wildcard)
        
        self.label_destination_copy = wx.StaticText(self, -1, _(u"Tables à transférer :"))
        
        DB = GestionDB.DB() 
        listeTablesTemp = DB.GetListeTables() 
        DB.Close() 
        listeTables = []
        for x in listeTablesTemp :
            listeTables.append(x[0])
        self.ctrl_tables = wx.CheckListBox(self, -1, (-1, -1), wx.DefaultSize, listeTables)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.ctrl_destination.SetToolTip(wx.ToolTip(_(u"Sélectionnez un fichier de destination")))
        self.ctrl_tables.SetToolTip(wx.ToolTip(_(u"Sélectionnez les tables à transférer")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer la procédure")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((800, 700))

    def __do_layout(self):
        grid_sizer_1 = wx.FlexGridSizer(5, 1, 10, 10)
        grid_sizer_3 = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_2 = wx.FlexGridSizer(3, 2, 10, 10)
        grid_sizer_1.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_2.Add(self.label_destination, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.ctrl_destination, 0, wx.EXPAND, 0)
        grid_sizer_2.Add(self.label_destination_copy, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_2.Add(self.ctrl_tables, 0, wx.EXPAND, 0)
        grid_sizer_2.AddGrowableRow(1)
        grid_sizer_2.AddGrowableCol(1)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_3.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_3.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_3.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_3.AddGrowableCol(1)
        grid_sizer_1.Add(grid_sizer_3, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # Récupération du fichier des destination
        nomFichier = self.ctrl_destination.GetValue()
        if len(nomFichier) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un fichier de données à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if os.path.isfile(nomFichier) == False :
            dlg = wx.MessageDialog(self, _(u"L'emplacement fichier que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Récupération des tables cochées
        listeTables = []
        for index in range(0, self.ctrl_tables.GetCount()):
            if self.ctrl_tables.IsChecked(index):
                nomTable = self.ctrl_tables.GetString(index)
                listeTables.append(nomTable)
                
        if len(listeTables) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une table à exporter !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment transférer %d tables ?") % len(listeTables), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Procédure de transfert
        DB = GestionDB.DB() 
        for nomTable in listeTables :
            DB.Exportation_vers_base_defaut(nomTable=nomTable, nomFichierdefault=nomFichier)
            time.sleep(1)
        DB.Close() 
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Procédure de transfert terminée !"), _(u"Fin"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        # Fermeture
        self.EndModal(wx.ID_OK)
        
        
        
        
        
        

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal() 
    dlg.Destroy() 
    app.MainLoop()
