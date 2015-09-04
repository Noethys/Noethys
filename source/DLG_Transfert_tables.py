#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import CTRL_Bandeau
import GestionDB
import wx.lib.filebrowsebutton as filebrowse
import time


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)

        # Bandeau
        titre = _(u"Transf�rer des tables")
        intro = _(u"Cette fonctionnalit� permet de transf�rer le contenu des tables du fichier de donn�es charg� vers un fichier de donn�es local.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Configuration.png")
        self.SetTitle(titre)

        self.label_destination = wx.StaticText(self, -1, _(u"Fichier de destination :"))

        wildcard = _(u"Fichiers Noethys (*.dat)|*.dat|All files (*.*)|*.*")
        self.ctrl_destination = filebrowse.FileBrowseButton(self, -1, labelText=u"", buttonText=_(u"S�lectionner"), toolTip=_(u"Cliquez ici pour s�lectionner un fichier de donn�es"), dialogTitle=_(u"S�lectionner un fichier"), fileMask=wildcard)
        
        self.label_destination_copy = wx.StaticText(self, -1, _(u"Tables � transf�rer :"))
        
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
        self.ctrl_destination.SetToolTipString(_(u"S�lectionnez un fichier de destination"))
        self.ctrl_tables.SetToolTipString(_(u"S�lectionnez les tables � transf�rer"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour lancer la proc�dure"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
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
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # R�cup�ration du fichier des destination
        nomFichier = self.ctrl_destination.GetValue()
        if len(nomFichier) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un fichier de donn�es � importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if os.path.isfile(nomFichier) == False :
            dlg = wx.MessageDialog(self, _(u"L'emplacement fichier que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # R�cup�ration des tables coch�es
        listeTables = []
        for index in range(0, self.ctrl_tables.GetCount()):
            if self.ctrl_tables.IsChecked(index):
                nomTable = self.ctrl_tables.GetString(index)
                listeTables.append(nomTable)
                
        if len(listeTables) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une table � exporter !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment transf�rer %d tables ?") % len(listeTables), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Proc�dure de transfert
        DB = GestionDB.DB() 
        for nomTable in listeTables :
            DB.Exportation_vers_base_defaut(nomTable=nomTable, nomFichierdefault=nomFichier)
            time.sleep(1)
        DB.Close() 
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Proc�dure de transfert termin�e !"), _(u"Fin"), wx.OK | wx.ICON_INFORMATION)
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
