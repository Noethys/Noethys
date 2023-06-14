#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Ctrl import CTRL_Bouton_image



class ListBox_Messages(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.Modifier)

    def MAJ(self):
        self.dictDonnees = {}
        self.listeMessages = []
        self.Clear()
        DB = GestionDB.DB()
        req = """SELECT IDmessage, titre, texte
        FROM portail_messages
        ORDER BY titre;"""
        DB.ExecuterReq(req)
        listeMessages = DB.ResultatReq()
        DB.Close()
        if len(listeMessages) == 0 : return None
        listeDonnees = []
        self.dictDonnees = {}
        self.listeMessages = []
        for IDmessage, titre, texte in listeMessages :
            self.Insert(titre, self.GetCount(), IDmessage)
            self.dictDonnees[IDmessage] = {"IDmessage" : IDmessage, "titre" : titre, "texte" : texte}
            self.listeMessages.append((titre, texte))
        return listeDonnees

    def GetSelectionMessage(self):
        index = self.GetSelection()
        if index == -1 : return None
        IDmessage = self.GetClientData(index)
        if IDmessage in self.dictDonnees :
            return self.dictDonnees[IDmessage]
        else:
            return None

    def Ajouter(self, event=None):
        from Dlg import DLG_Saisie_portail_message
        dlg = DLG_Saisie_portail_message.Dialog(self, IDmessage=None)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, event=None):
        message = self.GetSelectionMessage()
        if message == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmessage = message["IDmessage"]
        from Dlg import DLG_Saisie_portail_message
        dlg = DLG_Saisie_portail_message.Dialog(self, IDmessage=IDmessage)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self, event=None):
        message = self.GetSelectionMessage()
        if message == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce message ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDmessage = message["IDmessage"]
            DB = GestionDB.DB()
            DB.ReqDEL("portail_messages", "IDmessage", IDmessage)
            DB.Close()
            self.MAJ()
        dlg.Destroy()


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_messages = ListBox_Messages(self)
        self.ctrl_messages.SetMinSize((50, 50))

        self.bouton_ajouter_message = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_message = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_message = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnAjouterMessage, self.bouton_ajouter_message)
        self.Bind(wx.EVT_BUTTON, self.OnModifierMessage, self.bouton_modifier_message)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerMessage, self.bouton_supprimer_message)

    def __set_properties(self):
        self.ctrl_messages.SetToolTip(wx.ToolTip(_(u"Saisissez ou ou plusieurs messages qui apparaitront sur la page d'accueil du portail")))
        self.bouton_ajouter_message.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un message qui apparaîtra sur la page d'accueil du portail")))
        self.bouton_modifier_message.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le message sélectionné dans la liste")))
        self.bouton_supprimer_message.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le message sélectionné dans la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_messages, 0, wx.EXPAND, 0)

        grid_sizer_boutons_message = wx.FlexGridSizer(rows=3, cols=1, vgap=1, hgap=2)
        grid_sizer_boutons_message.Add(self.bouton_ajouter_message, 0, 0, 0)
        grid_sizer_boutons_message.Add(self.bouton_modifier_message, 0, 0, 0)
        grid_sizer_boutons_message.Add(self.bouton_supprimer_message, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons_message, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnAjouterMessage(self, event):
        self.ctrl_messages.Ajouter()

    def OnModifierMessage(self, event):
        self.ctrl_messages.Modifier()

    def OnSupprimerMessage(self, event):
        self.ctrl_messages.Supprimer()


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





# ----------------------------------------------------------------------------------------------------------------------        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
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