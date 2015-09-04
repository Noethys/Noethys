#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import CTRL_Bandeau
import UTILS_Historique
import CTRL_Saisie_date
import wx.lib.agw.hyperlink as Hyperlink

try: import psyco; psyco.full()
except: pass



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
        if self.URL == "tout" :
            self.parent.CocheTout() 
        if self.URL == "rien" :
            self.parent.DecocheTout() 
        self.UpdateLink()
        


class Dialog(wx.Dialog):
    def __init__(self, parent, IDutilisateur=None, IDfamille=None, IDindividu=None, IDcategorie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici purger tout ou une partie de l'historique de Noethys. Cette fonction peut vous permettre d'all�ger la base de donn�es au bout de quelques ann�es d'utilisation.")
        titre = _(u"Purge de l'historique")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Horloge3.png")
        
        # Liste cat�gories
        self.label_categories = wx.StaticText(self, -1, _(u"Cat�gories :"))
        self.listeCategories = []
        self.dictCategories = {}
        index = 0
        for IDcategorie, label in UTILS_Historique.CATEGORIES.iteritems() :
            self.listeCategories.append(label)
            self.dictCategories[index] = IDcategorie
            index += 1
        self.ctrl_categories = wx.CheckListBox(self, -1, choices=self.listeCategories)
        self.hyper_tout = Hyperlien(self, label=_(u"Tout s�lectionner"), infobulle=_(u"Cliquez ici pour tout s�lectionner"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout d�s�lectionner"), infobulle=_(u"Cliquez ici pour tout d�s�lectionner"), URL="rien")
        
        # Date limite
        self.label_date = wx.StaticText(self, -1, _(u"Date limite :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.SetTitle(_(u"Historique"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour lancer la purge"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.ctrl_date.SetToolTipString(_(u"Saisissez ici la date limite jusqu'� laquelle les actions seront supprim�es"))
        self.SetMinSize((450, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Contenu
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=2, vgap=0, hgap=10)
        grid_sizer_contenu.Add(self.label_categories, 0, 0, 10)
        grid_sizer_contenu.Add(self.ctrl_categories, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_selection = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_selection.Add( (5, 5), 0, 0, 0)
        grid_sizer_selection.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_selection.Add(self.label_separation, 0, 0, 0)
        grid_sizer_selection.Add(self.hyper_rien, 0, 0, 0)
        grid_sizer_selection.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_selection, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu.Add(self.label_date, 0, wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_contenu.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        grid_sizer_base.Add( (5, 5), 0, 0, 0)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def OnBoutonOk(self, event):
        # R�cup�re les cat�gories
        listeCategories = self.GetIDcoches() 
        if len(listeCategories) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner un moins une cat�gorie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # R�cup�re la date limite
        date = self.ctrl_date.GetDate() 
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date limite jusqu'� laquelle les actions seront effac�es !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return
        
        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Etes-vous s�r de vouloir purger l'historique ?"), _(u"Demande de confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        
        # Suppression
        if len(listeCategories) == 1 : conditionCategories = "IDcategorie=%d" % listeCategories[0]
        else: conditionCategories = "IDcategorie IN %s" % str(tuple(listeCategories))
        DB = GestionDB.DB()
        req = """DELETE FROM historique 
        WHERE %s AND date<='%s'
        ;""" % (conditionCategories, str(date))
        DB.ExecuterReq(req)
        DB.Commit() 
        DB.Close()
        
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def GetIDcoches(self):
        listeIDcoches = []
        for index in range(0, self.ctrl_categories.GetCount() ):
            if self.ctrl_categories.IsChecked(index):
                listeIDcoches.append(self.dictCategories[index])
        return listeIDcoches

    def CocheTout(self):
        index = 0
        for index in range(0, self.ctrl_categories.GetCount() ):
            self.ctrl_categories.Check(index)
            index += 1

    def DecocheTout(self):
        index = 0
        for index in range(0, self.ctrl_categories.GetCount() ):
            self.ctrl_categories.Check(index, False)
            index += 1

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Purger")





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
