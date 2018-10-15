#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB



class CTRL(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeDonnees = []
        self.dictDonnees = {}

    def SetDonnees(self, listeDonnees=[], trier=False, cocher=False):
        self.listeDonnees = listeDonnees
        listeLabels = []
        for dictTemp in listeDonnees :
            listeLabels.append((dictTemp["label"], dictTemp))

        # Tri par ordre alphabétique si demandé
        if trier == True :
            listeLabels.sort()

        # Remplissage
        self.dictDonnees = {}
        self.Clear()
        index = 0
        for label, dictTemp in listeLabels :
            self.Append(label)
            if cocher == True :
                self.Check(index)
            self.dictDonnees[index] = dictTemp
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        for index, dictItem in self.dictDonnees.iteritems() :
            if self.IsChecked(index):
                listeIDcoches.append(dictItem["ID"])
        return listeIDcoches

    def CocherTout(self):
        for index, dictItem in self.dictDonnees.iteritems() :
            self.Check(index)

    def CocherRien(self):
        for index, dictItem in self.dictDonnees.iteritems() :
            self.Check(index, False)

    def SetIDcoches(self, listeIDcoches=[]):
        for index, dictItem in self.dictDonnees.iteritems() :
            if dictItem["ID"] in listeIDcoches :
                self.Check(index)

    def GetLabelsCoches(self):
        """ Renvoie un texte de type 'label1, label2, label3, ...' """
        listeLabels = []
        listeID = self.GetIDcoches()
        for index, dictItem in self.dictDonnees.iteritems() :
            if dictItem["ID"] in listeID :
                listeLabels.append(dictItem["label"])
        return ", ".join(listeLabels)





class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Liste à cocher
        self.ctrl_liste = CTRL(self)

        # Boutons
        self.bouton_cocher_tout = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Cocher.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_cocher_rien = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Decocher.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCocherTout, self.bouton_cocher_tout)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCocherRien, self.bouton_cocher_rien)

        # Associe les fonctions du ctrl au panel
        listeFonctions = ["SetDonnees", "GetIDcoches", "CocherTout", "CocherRien", "SetIDcoches", "GetLabelsCoches"]
        for nomFonction in listeFonctions :
            fonction = getattr(self.ctrl_liste, nomFonction)
            setattr(self, nomFonction, fonction)


    def __set_properties(self):
        self.bouton_cocher_tout.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour tout cocher")))
        self.bouton_cocher_rien.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour tout décocher")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_liste, 1, wx.EXPAND, 0)

        grid_sizer_boutons_colonnes = wx.FlexGridSizer(rows=2, cols=1, vgap= 5, hgap=5)
        grid_sizer_boutons_colonnes.Add(self.bouton_cocher_tout, 0, 0, 0)
        grid_sizer_boutons_colonnes.Add(self.bouton_cocher_rien, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons_colonnes, 0, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnBoutonCocherTout(self, event=None):
        self.ctrl_liste.CocherTout()

    def OnBoutonCocherRien(self, event=None):
        self.ctrl_liste.CocherRien()


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        boutonTest = wx.Button(panel, -1, _(u"Test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, boutonTest)

        self.MAJ()
        self.ctrl.CocherTout()


    def MAJ(self, IDactivite=1):
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, IDactivite, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % IDactivite
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        DB.Close()

        # Formatage des données
        listeDonnees = []
        for IDgroupe, IDactivite, nom in listeGroupes:
            dictTemp = {"ID": IDgroupe, "label": nom, "IDactivite": IDactivite}
            listeDonnees.append(dictTemp)

        # Envoi des données à la liste
        self.ctrl.SetDonnees(listeDonnees)

    def OnBoutonTest(self, event):
        print self.ctrl.GetLabelsCoches()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
