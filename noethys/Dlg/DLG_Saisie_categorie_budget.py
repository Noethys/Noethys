#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import wx.lib.agw.hyperlink as Hyperlink
from Ctrl import CTRL_Saisie_euros



class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
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
        # Récupération des consommations
        DB = GestionDB.DB() 
        req = """SELECT IDunite, unites.nom, activites.nom
        FROM unites
        LEFT JOIN activites ON activites.IDactivite = unites.IDactivite
        ORDER BY activites.date_fin DESC, activites.nom, unites.nom
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeLabels = []
        listeChamps = []
        for IDunite, nomUnite, nomActivite in listeDonnees :
            nomChamp = u"{NBRE_UNITE_%d}" % IDunite
            listeLabels.append(_(u"%s : Quantité de '%s' %s") % (nomActivite, nomUnite, nomChamp))
            listeChamps.append(nomChamp)
        DB.Close() 
        
        dlg = wx.SingleChoiceDialog(None, _(u"Sélectionnez un champ à insérer :"), _(u"Insérer un champ"), listeLabels, wx.CHOICEDLG_STYLE)
        dlg.SetSize((600, 500))
        if dlg.ShowModal() == wx.ID_OK:
            champ = listeChamps[dlg.GetSelection()]
            self.parent.InsertTexte(champ)
        dlg.Destroy()
        self.UpdateLink()
        

# ---------------------------------------------------------------------------------------------------------------------------------

class CTRL_Categorie(wx.Choice):
    def __init__(self, parent, typeCategorie="debit"):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.typeCategorie = typeCategorie
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [u"",]
        self.dictDonnees = { 0 : {"ID":None}, }
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, type, nom, abrege, journal, IDcompte
        FROM compta_categories
        WHERE type='%s'
        ORDER BY nom; """ % self.typeCategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDcategorie, typeCategorie, nom, abrege, journal, IDcompte in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcategorie }
            label = nom
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, typeCategorie="credit", track=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent   
        self.track = track
        self.typeCategorie = typeCategorie
        self.IDcategorie_budget = None

        self.label_categorie = wx.StaticText(self, wx.ID_ANY, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self, typeCategorie=typeCategorie)
        self.bouton_categories = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.label_valeur = wx.StaticText(self, wx.ID_ANY, _(u"Plafond :"))
        
        self.radio_montant = wx.RadioButton(self, -1, _(u"Montant :"), style=wx.RB_GROUP)
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        self.radio_formule = wx.RadioButton(self, -1, _(u"Formule de calcul :"))
        self.ctrl_formule = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        self.ctrl_formule.SetMinSize((400, 100)) 
        
        self.hyper_champ = Hyperlien(self, label=_(u"Insérer un champ"), infobulle=_(u"Cliquez ici pour insérer un champ"), URL="")
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValeur, self.radio_montant)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValeur, self.radio_formule)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        if self.track != None :
            titre = _(u"Modification d'une catégorie budgétaire")
            self.Importation()
        else :
            titre = _(u"Saisie d'une catégorie budgétaire")
        if self.typeCategorie == "credit" : titre += _(u" au crédit")
        if self.typeCategorie == "debit" : titre += _(u" au débit")
        self.SetTitle(titre)
        self.OnRadioValeur(None)

    def __set_properties(self):
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez la catégorie comptable à associer")))
        self.bouton_categories.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des catégories comptables")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez un montant plafonf (Ex : 200.00)")))
        self.ctrl_formule.SetToolTip(wx.ToolTip(_(u"Saisissez une formule de calcul du plafond (Ex : {NBRE_UNITE_1}*3.00)")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((600, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(5, 2, 5, 10)

        grid_sizer_haut.Add(self.label_categorie, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, 10)

        grid_sizer_categorie = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_categorie.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_categorie.Add(self.bouton_categories, 0, 0, 0)
        grid_sizer_categorie.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_categorie, 1, wx.EXPAND | wx.BOTTOM, 10)

        grid_sizer_haut.Add(self.label_valeur, 0, wx.ALIGN_RIGHT | wx.TOP, 5)
        
        grid_sizer_valeur = wx.FlexGridSizer(4, 1, 5, 5)
        grid_sizer_valeur.Add(self.radio_montant, 0, wx.EXPAND, 0)
        grid_sizer_valeur.Add(self.ctrl_montant, 0, wx.EXPAND | wx.LEFT, 16)
        grid_sizer_valeur.Add(self.radio_formule, 0, wx.EXPAND, 0)
        grid_sizer_valeur.Add(self.ctrl_formule, 0, wx.EXPAND | wx.LEFT, 16)
        grid_sizer_valeur.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_valeur, 1, wx.EXPAND | wx.TOP, 5)
        
        grid_sizer_haut.Add( (2, 2), 0, 0, 0)
        grid_sizer_haut.Add(self.hyper_champ, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_haut.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnRadioValeur(self, event):
        self.ctrl_montant.Enable(self.radio_montant.GetValue())
        self.ctrl_formule.Enable(self.radio_formule.GetValue())
        self.hyper_champ.Enable(self.radio_formule.GetValue())
        if self.radio_montant.GetValue() == True :
            self.ctrl_montant.SetFocus() 
        else :
            self.ctrl_formule.SetFocus() 
        
    def OnBoutonCategories(self, event):  
        IDcategorie = self.ctrl_categorie.GetID()
        from Dlg import DLG_Categories_operations
        dlg = DLG_Categories_operations.Dialog(self)
        dlg.SetType(self.typeCategorie, verrouillage=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_categorie.MAJ()
        self.ctrl_categorie.SetID(IDcategorie)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Budgets")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def InsertTexte(self, texte=u""):
        positionCurseur = self.ctrl_formule.GetInsertionPoint() 
        self.ctrl_formule.WriteText(texte)
        self.ctrl_formule.SetInsertionPoint(positionCurseur+len(texte)) 
        self.ctrl_formule.SetFocus()

    def OnBoutonOk(self, event): 
        IDcategorie = self.ctrl_categorie.GetID()
        if IDcategorie == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_categorie.SetFocus()
            return False

        if self.radio_montant.GetValue() == True :
            valeur = self.ctrl_montant.GetMontant() 
            if valeur == "" or valeur == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_montant.SetFocus()
                return False

        else :
            valeur = self.ctrl_formule.GetValue()
            if valeur == "" or valeur == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une formule de calcul !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_formule.SetFocus()
                return False

        self.EndModal(wx.ID_OK)
    
    def Importation(self):
        """ Importation depuis un track """
        # Catégorie
        self.IDcategorie_budget = self.track.IDcategorie_budget
        self.ctrl_categorie.SetID(self.track.IDcategorie)
        
        # Valeur
        try :
            montant = float(self.track.valeur)
            self.ctrl_montant.SetMontant(montant)
            self.radio_montant.SetValue(True)
        except :
            self.ctrl_formule.SetValue(self.track.valeur)
            self.radio_formule.SetValue(True)
    
    def GetDictDonnees(self):
        if self.radio_montant.GetValue() == True :
            valeur = self.ctrl_montant.GetMontant() 
        else :
            valeur = self.ctrl_formule.GetValue()
        dictDonnees = {
            "IDcategorie_budget" : self.IDcategorie_budget, 
            "IDcategorie" : self.ctrl_categorie.GetID(),
            "typeCategorie" : self.typeCategorie,
            "valeur" : valeur,
            }
        return dictDonnees



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, typeCategorie="debit", track=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
