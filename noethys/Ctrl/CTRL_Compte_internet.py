#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import wx.html as html
from Utils import UTILS_Internet



class CTRL(html.HtmlWindow):
    def __init__(self, parent, IDfamille=None, IDutilisateur=None, couleurFond=None):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.BORDER_THEME | wx.html.HW_NO_SELECTION | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDutilisateur = IDutilisateur
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        if couleurFond == None :
            self.couleurFond = wx.SystemSettings.GetColour(30)
        else :
            self.couleurFond = couleurFond
        self.SetMinSize((200, 130))
        self.SetBorders(4)
        self.dictDonnees = {}

    def SetDonnees(self, dictDonnees={}):
        self.dictDonnees = dictDonnees
        self.MAJ()

    def GetDonnees(self):
        return self.dictDonnees

    def MAJ(self):
        if self.dictDonnees["internet_actif"] == 1 :
            activation = _(u"Compte internet activé")
            image = "Ok4"
        else :
            activation = _(u"Compte internet désactivé")
            image = "Interdit2"
        identifiant = self.dictDonnees["internet_identifiant"]
        if identifiant == None :
            identifiant = ""
        mdp = self.dictDonnees["internet_mdp"]
        if mdp == None :
            mdp = ""
        if mdp.startswith("#@#"):
            mdp = UTILS_Internet.DecrypteMDP(mdp)

        if mdp.startswith("custom"):
            mdp = _(u"********<BR><FONT SIZE=1>(Mot de passe personnalisé)</FONT>")
        self.SetPage(u"""
        <FONT SIZE=2>
        <BR><BR>
        <CENTER><IMG SRC="%s"><BR>%s
        <BR><BR>
        <B>Identifiant</B> : %s
        <BR>
        <B>Mot de passe</B> : %s
        </CENTER>
        </FONT>
        """ % (Chemins.GetStaticPath(u"Images/16x16/%s.png" % image), activation, identifiant, mdp))
        self.SetBackgroundColour(self.couleurFond)

    def GetIdentifiant(self):
        return self.dictDonnees["internet_identifiant"]

    def GetMdp(self):
        internet_mdp = self.dictDonnees["internet_mdp"]
        if internet_mdp.startswith("custom"):
            internet_mdp = "********"
        if internet_mdp.startswith("#@#"):
            internet_mdp = UTILS_Internet.DecrypteMDP(internet_mdp)
        return internet_mdp

    def Modifier(self, event):
        from Dlg import DLG_Compte_internet
        dlg = DLG_Compte_internet.Dialog(self, IDfamille=self.IDfamille, IDutilisateur=self.IDutilisateur)
        if self.IDutilisateur != None :
            dlg.SetDonnees(self.dictDonnees)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetDonnees(dlg.GetDonnees())
        dlg.Destroy()

    def Envoyer_pressepapiers(self, event):
        # Mémorisation des codes dans le presse-papiers
        codes = _(u"Identifiant : %s / Mot de passe : %s") % (self.GetIdentifiant(), self.GetMdp())
        clipdata = wx.TextDataObject()
        clipdata.SetText(codes)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        dlg = wx.MessageDialog(self, _(u"Les codes ont été copiés dans le presse-papiers."), u"Presse-papiers", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()








# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, IDfamille=14)
        self.ctrl.SetDonnees({"internet_actif": 1, "internet_identifiant": "test1", "internet_mdp": "test2"})
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
