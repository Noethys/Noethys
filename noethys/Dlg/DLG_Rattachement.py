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
import wx.html as html

from Ctrl import CTRL_Bandeau
from Ol import OL_Individus
import GestionDB

try: import psyco; psyco.full()
except: pass


from Utils import UTILS_Interface
from ObjectListView import Filter


def Formate(mot):
    """ supprime les accents du texte source """
    mot = mot.lower()
    out = ""
    for c in mot:
        if c == u'é' or c == u'è' or c == u'ê':
            c = 'e'
        elif c == u'à':
            c = 'a'
        elif c == u'ù' or c == u'û':
            c = 'u'
        elif c == u'î':
            c = 'i'
        elif c == u'ç':
            c = 'c'
        out += c
    return out


class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetPage(texte)
        couleurFond = wx.SystemSettings.GetColour(30)
        self.SetBackgroundColour(couleurFond)
    
    def OnLinkClicked(self, link):
        self.parent.CreationIDindividu()
        

class CtrlRecherche(wx.TextCtrl):
    def __init__(self, parent, numColonne):
        wx.TextCtrl.__init__(self, parent, -1, "", size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.listView = self.parent.ctrl_propositions
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[1:1]))
        
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnDoSearch(self, evt):
        self.Recherche(self.GetValue())
        
    def Recherche(self, txtSearch):
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.listView.Refresh()
        
        

class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Rattachement", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.IDfamille = IDfamille
        self.mode = None

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.nbreTitulaires = self.GetNbreTitulairesFamille() 
        
        # Bandeau
        titre = _(u"Rattachement d'un individu")
        intro = _(u"Commencez par sélectionner une catégorie de rattachement puis saisissez son nom et son prénom. Si l'individu apparait dans la liste, sélectionnez-le. Sinon créez une nouvelle fiche individuelle.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Famille.png")
        
        # Categorie
        self.staticbox_categorie_staticbox = wx.StaticBox(self, -1, _(u"1. Sélection de la catégorie de rattachement"))
        self.bouton_categorie_1 = wx.ToggleButton(self, 1, _(u"Représentant"))
        self.bouton_categorie_2 = wx.ToggleButton(self, 2, _(u"Enfant"))
        self.bouton_categorie_3 = wx.ToggleButton(self, 3, _(u"Contact"))
        self.ctrl_titulaire = wx.CheckBox(self, -1, _(u"Titulaire du dossier famille"))
        self.selection_categorie = None
        
        if self.nbreTitulaires == 0 :
            self.bouton_categorie_2.Enable(False)
            self.bouton_categorie_3.Enable(False)
        
        # Sélection individu
        self.staticbox_selection_staticbox = wx.StaticBox(self, -1, _(u"2. Saisie du nom de l'individu"))
        self.ctrl_propositions = OL_Individus.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = CtrlRecherche(self, numColonne=1)
        self.label_prenom = wx.StaticText(self, -1, _(u"Prénom :"))
        self.ctrl_prenom = wx.TextCtrl(self, -1, "") #CtrlRecherche(self, numColonne=2)
        
        # Txt remarque
        txtRemarque = u"""
        <IMG SRC="Static/Images/16x16/Attention2.png">
        <FONT SIZE=-1>
        Si l'individu à rattacher n'apparaît pas dans cette liste, 
        vous devez cliquez sur ce bouton 
        <A HREF="Saisie">Saisir un nouvel individu</A>
        pour créer une nouvelle fiche individuelle.
        </FONT>
        """
        self.ctrl_html = MyHtml(self, texte=txtRemarque, hauteur=31)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle, self.bouton_categorie_1)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle, self.bouton_categorie_2)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle, self.bouton_categorie_3)
        
        self.ActiveControles(False)
        self.ctrl_titulaire.Enable(False)
        

    def __set_properties(self):
        self.SetTitle(_(u"Rattachement d'un individu"))
        self.bouton_categorie_1.SetToolTipString(_(u"Représentants"))
        self.bouton_categorie_2.SetToolTipString(_(u"Enfants"))
        self.bouton_categorie_3.SetToolTipString(_(u"Contacts"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom de l'individu à rattacher (en majuscules et sans accents)"))
        self.ctrl_prenom.SetToolTipString(_(u"Saisissez ici le prénom de l'individu à rattacher"))
        self.ctrl_propositions.SetToolTipString(_(u"Double-cliquez sur le nom de l'individu à rattacher"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour rattacher l'individu selectionné dans la liste"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))
        self.ctrl_titulaire.SetToolTipString(_(u"Cochez cette case si l'individu doit être considéré comme titulaire du dossier"))
        self.SetMinSize((500, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_selection = wx.StaticBoxSizer(self.staticbox_selection_staticbox, wx.VERTICAL)
        grid_sizer_selection = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        staticbox_categorie = wx.StaticBoxSizer(self.staticbox_categorie_staticbox, wx.VERTICAL)
        grid_sizer_categorie = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_categorie.Add(self.bouton_categorie_1, 0, wx.EXPAND, 0)
        grid_sizer_categorie.Add(self.bouton_categorie_2, 0, wx.EXPAND, 0)
        grid_sizer_categorie.Add(self.bouton_categorie_3, 0, wx.EXPAND, 0)
        grid_sizer_categorie.AddGrowableCol(0)
        grid_sizer_categorie.AddGrowableCol(1)
        grid_sizer_categorie.AddGrowableCol(2)
        staticbox_categorie.Add(grid_sizer_categorie, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        staticbox_categorie.Add(self.ctrl_titulaire, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_categorie, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableRow(0)
        grid_sizer_nom.AddGrowableCol(1)
        grid_sizer_nom.AddGrowableCol(3)
        grid_sizer_selection.Add(grid_sizer_nom, 1, wx.EXPAND, 0)
        grid_sizer_selection.Add(self.ctrl_propositions, 0, wx.EXPAND, 0)
        grid_sizer_selection.Add(self.ctrl_html, 0, wx.EXPAND, 0)
        grid_sizer_selection.AddGrowableRow(1)
        grid_sizer_selection.AddGrowableCol(0)
        staticbox_selection.Add(grid_sizer_selection, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_selection, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnToggle(self, event):
        ID = event.GetId()
        if ID != 1 : self.bouton_categorie_1.SetValue(False)
        if ID != 2 : self.bouton_categorie_2.SetValue(False)
        if ID != 3 : self.bouton_categorie_3.SetValue(False)
        if self.selection_categorie == None :
            self.ActiveControles(True)
            self.ctrl_propositions.MAJ()
        if ID == 1 :
            # Si on choisit Représentant, on vérifie qu'un titulaire est déjà saisi dans la famille
            if self.nbreTitulaires == 0 :
                self.ctrl_titulaire.Enable(False)
            else:
                self.ctrl_titulaire.Enable(True)
            self.ctrl_titulaire.SetValue(True)
        else:
            self.ctrl_titulaire.Enable(False)
            self.ctrl_titulaire.SetValue(False)
        self.selection_categorie = ID
        self.ctrl_nom.SetFocus()
    
    def GetNbreTitulairesFamille(self):
        DB = GestionDB.DB()
        req = "SELECT IDindividu, IDfamille, IDcategorie, titulaire FROM rattachements WHERE IDfamille=%d AND titulaire=1;" % self.IDfamille
        DB.ExecuterReq(req)
        listeTitulaires = DB.ResultatReq()
        DB.Close()
        nbreTitulaires = len(listeTitulaires)
        return nbreTitulaires
            
    def ActiveControles(self, etat):
        self.ctrl_propositions.Enable(etat)
        self.bouton_ok.Enable(etat)
        self.label_nom.Enable(etat)
        self.ctrl_nom.Enable(etat)
        self.label_prenom.Enable(etat)
        self.ctrl_prenom.Enable(etat)
        self.ctrl_html.Enable(etat)
        
    def GetSelectionIDindividu(self):
        selections = self.ctrl_propositions.Selection()
        if len(selections) > 0 :
            return selections[0].IDindividu
        else:
            return None
    
    def GetData(self):
        mode = self.mode
        IDcategorie = self.selection_categorie
        titulaire = int(self.ctrl_titulaire.GetValue())
        if IDcategorie != 1 : titulaire = 0
        IDindividu = self.GetSelectionIDindividu()
        nom = self.ctrl_nom.GetValue()
        prenom = self.ctrl_prenom.GetValue()
        return mode, IDcategorie, titulaire, IDindividu, nom, prenom
    
    def CreationIDindividu(self):
        nom = self.ctrl_nom.GetValue()
        if nom  == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir le nom du nouvel individu à créer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        prenom = self.ctrl_prenom.GetValue()
        if prenom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir le prénom du nouvel individu à créer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_prenom.SetFocus()
            return
        
        # Vérifie que l'individu n'existe pas déjà dans la liste
        if self.ctrl_propositions.donnees != None :
            for individu in self.ctrl_propositions.donnees :
                if Formate(individu.nom) == Formate(nom) and Formate(individu.prenom) == Formate(prenom) :
                    dlg = wx.MessageDialog(self, _(u"Un individu portant ce nom existe déjà dans la liste ! \n\nSi vous souhaitez quand même créer un nouvel individu avec ce nom, cliquez sur OUI."), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse !=  wx.ID_YES :
                        return
        
        self.mode = "creation"
        self.EndModal(wx.ID_OK) 


    def OnBoutonOk(self, event):
        IDindividu = self.GetSelectionIDindividu()
        if IDindividu == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun élément dans la liste !\n\n(Si vous souhaitez créer un individu, cliquez sur 'Saisir un nouvel individu')"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Vérifie que la personne n'est pas déjà rattachée à cette famille
        if self.IDfamille != None :
            DB = GestionDB.DB()
            req = "SELECT IDindividu, IDfamille, IDcategorie, titulaire FROM rattachements WHERE IDindividu=%d AND IDfamille=%d;" % (IDindividu, self.IDfamille)
            DB.ExecuterReq(req)
            listeRattachements = DB.ResultatReq()
            DB.Close()
            if len(listeRattachements) > 0 :
                dlg = wx.MessageDialog(self, _(u"Rattachement Impossible : Cet individu est déjà rattaché à cette famille !"), _(u"Erreur de rattachement"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        self.mode = "rattachement"
        self.EndModal(wx.ID_OK) 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Compositiondelafamille")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=3)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
