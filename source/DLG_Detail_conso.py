#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.html as html

import CTRL_Bandeau
import CTRL_Saisie_heure

import GestionDB

try: import psyco; psyco.full()
except: pass



class Groupe(wx.Choice):
    def __init__(self, parent, IDactivite=0):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDactivite = IDactivite
        self.MAJlisteDonnees() 
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDrestaurateur, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDrestaurateur }
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# ----------------------------------------------------------------------------------------------------------------------------

class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SIMPLE_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(3)
        self.SetMinSize((-1, hauteur))
        self.SetPage(u"<FONT SIZE=-2>%s</FONT>""" % texte)

# -------------------------------------------------------------------------------------------------------------------------------------------




class Dialog(wx.Dialog):
    def __init__(self, parent, dictConso={}, texteInfoBulle=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.dictInfoConso = dictConso
        self.texteInfoBulle = texteInfoBulle
        
        intro = _(u"Prenez connaissance des informations détaillées concernant cette consommation et modifier certains de ses paramètres.")
        titre = _(u"Détail d'une consommation")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier_zoom.png")

        # Informations
        texteInfos = self.GetTexteInfos()
        self.staticbox_infos = wx.StaticBox(self, -1, _(u"Informations"))
        self.ctrl_infos = wx.TextCtrl(self, -1, texteInfos, style=wx.TE_MULTILINE) #MyHtml(self, texteInfos)
        
        # Paramètres
        self.staticbox_param = wx.StaticBox(self, -1, _(u"Paramètres"))
        
        self.label_groupe = wx.StaticText(self, -1, _(u"Groupe :"))
        self.ctrl_groupe = Groupe(self, IDactivite=self.dictInfoConso.IDactivite)
        self.ctrl_groupe.SetID(self.dictInfoConso.IDgroupe)
        
        self.label_heure_debut = wx.StaticText(self, -1, _(u"Heure de début :"))
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.ctrl_heure_debut.SetHeure(self.dictInfoConso.heure_debut)
        
        self.label_heure_fin = wx.StaticText(self, -1, _(u"Heure de fin :"))
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)
        self.ctrl_heure_fin.SetHeure(self.dictInfoConso.heure_fin)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)


    def __set_properties(self):
        self.SetTitle(_(u"Détail d'une consommation"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((400, 510))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Infos
        staticbox_infos = wx.StaticBoxSizer(self.staticbox_infos, wx.VERTICAL)
        staticbox_infos.Add(self.ctrl_infos, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_infos, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Param
        staticbox_param = wx.StaticBoxSizer(self.staticbox_param, wx.VERTICAL)
        
        grid_sizer_param = wx.FlexGridSizer(rows=5, cols=2, vgap=5, hgap=5)
        
        grid_sizer_param.Add(self.label_groupe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_groupe, 0, wx.ALL|wx.EXPAND, 0)
        
        grid_sizer_param.Add(self.label_heure_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_heure_debut, 0, wx.ALL, 0)
        
        grid_sizer_param.Add(self.label_heure_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_heure_fin, 0, wx.ALL, 0)
        
        staticbox_param.Add(grid_sizer_param, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_param, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
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
        import UTILS_Aide
        UTILS_Aide.Aide("Lagrilledesconsommations")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_heure_debut.Validation() == False or self.ctrl_heure_debut.GetHeure() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de début !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_heure_fin.Validation() == False or self.ctrl_heure_fin.GetHeure() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
                    
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDgroupe(self):
        return self.ctrl_groupe.GetID()
    
    def GetHeureDebut(self):
        return self.ctrl_heure_debut.GetHeure()

    def GetHeureFin(self):
        return self.ctrl_heure_fin.GetHeure()

    def GetTexteInfos(self):
        texte = ""
        if self.dictInfoConso == None :
            return texte

        texte += self.texteInfoBulle["titre"].upper()
        texte +="----------------------------------------------------\n"
        texte += self.texteInfoBulle["texte"]
        texte +="\n----------------------------------------------------\n"
        
        if self.dictInfoConso.IDconso == None :
            texte += _(u"IDconso : Consommation non enregistrée\n")
        else:
            texte += _(u"IDconso : %d\n") % self.dictInfoConso.IDconso
        
        texte += _(u"IDfamille : %d") % self.dictInfoConso.IDfamille
        
        return texte


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
