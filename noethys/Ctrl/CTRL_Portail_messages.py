#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Ctrl import CTRL_Bouton_image



class ListBox_Messages(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()

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
        if self.dictDonnees.has_key(IDmessage) :
            return self.dictDonnees[IDmessage]
        else:
            return None

    def Ajouter(self):
        dlg = Saisie_Message(self)
        if dlg.ShowModal() == wx.ID_OK:
            titre = dlg.GetTitre()
            texte = dlg.GetTexte()
            DB = GestionDB.DB()
            listeDonnees = [
                ("titre", titre ),
                ("texte", texte),
                ]
            IDmessage = DB.ReqInsert("portail_messages", listeDonnees)
            DB.Close()
            self.MAJ()
        dlg.Destroy()

    def Modifier(self):
        message = self.GetSelectionMessage()
        if message == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmessage = message["IDmessage"]
        titre = message["titre"]
        texte = message["texte"]
        dlg = Saisie_Message(self, IDmessage, titre, texte)
        if dlg.ShowModal() == wx.ID_OK:
            titre = dlg.GetTitre()
            texte = dlg.GetTexte()
            DB = GestionDB.DB()
            listeDonnees = [
                ("titre", titre ),
                ("texte", texte),
                ]
            DB.ReqMAJ("portail_messages", listeDonnees, "IDmessage", IDmessage)
            DB.Close()
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self):
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

class Saisie_Message(wx.Dialog):
    def __init__(self, parent, IDmessage=None, titre=u"", texte=u""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        self.label_titre = wx.StaticText(self, -1, _(u"Titre :"))
        self.ctrl_titre = wx.TextCtrl(self, -1, titre)
        self.label_texte = wx.StaticText(self, -1, _(u"Texte :"))
        self.ctrl_texte = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        self.ctrl_titre.SetToolTipString(_(u"Saisissez ici un titre interne pour ce message. Ce titre n'apparaît pas sur le portail."))
        self.ctrl_texte.SetToolTipString(_(u"Saisissez ici le texte qui apparaîtra sur la page d'accueil du portail"))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        if IDmessage == None :
            self.SetTitle(_(u"Saisie d'un message"))
        else:
            self.SetTitle(_(u"Modification d'un message"))
        self.SetMinSize((500, 260))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_titre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_titre, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_texte, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_texte, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()
        self.CenterOnScreen()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def GetTitre(self):
        return self.ctrl_titre.GetValue()

    def GetTexte(self):
        return self.ctrl_texte.GetValue()


    def OnBoutonOk(self, event):
        if self.GetTitre() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return

        if self.GetTexte() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_texte.SetFocus()
            return

        self.EndModal(wx.ID_OK)





class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_messages = ListBox_Messages(self)

        self.bouton_ajouter_message = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_message = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_message = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnAjouterMessage, self.bouton_ajouter_message)
        self.Bind(wx.EVT_BUTTON, self.OnModifierMessage, self.bouton_modifier_message)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerMessage, self.bouton_supprimer_message)

    def __set_properties(self):
        self.ctrl_messages.SetToolTipString(_(u"Saisissez ou ou plusieurs messages qui apparaitront sur la page d'accueil du portail"))
        self.bouton_ajouter_message.SetToolTipString(_(u"Cliquez ici pour ajouter un message qui apparaîtra sur la page d'accueil du portail"))
        self.bouton_modifier_message.SetToolTipString(_(u"Cliquez ici pour modifier le message sélectionné dans la liste"))
        self.bouton_supprimer_message.SetToolTipString(_(u"Cliquez ici pour supprimer le message sélectionné dans la liste"))

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
        self.ctrl = CTRL_Messages(panel)
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