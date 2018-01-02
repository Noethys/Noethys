#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_euros

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils




class Track(object):
    def __init__(self, donnees):
        self.ordre = donnees[0]
        self.label = donnees[1]
        self.montant = donnees[2]

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.lignes_calcul = kwds.pop("lignes_calcul", [])
        self.donnees = []
        FastObjectListView.__init__(self, *args, **kwds)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

    def OnItemActivated(self,event):
        self.Selection(valider=True)
    
    def OnItemSelected(self, event):
        self.Selection()

    def Selection(self, valider=False):
        track = self.GetSelectedObjects()[0]
        self.GetParent().SetSelection(label=track.label, montant=track.montant, valider=valider)

    def InitModel(self):
        self.donnees = []
        index = 0
        for ligneCalcul in self.lignes_calcul :
            montant = ligneCalcul["montant_unique"]
            label = ligneCalcul["label"]
            self.donnees.append(Track((index, label, montant)))
            index += 1
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        imgImportant = self.AddNamedImages("attention", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        
        # Formatage des données
        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "index", typeDonnee="entier"),
            ColumnDefn(_(u"Label"), 'left', 100, "label", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Montant"), 'right', 90, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun tarif"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[0])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 



# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, lignes_calcul=[], label=u"", montant=0.0, titre=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici sélectionner dans la liste un montant et un label pour la prestation qui va être créée. Vous pouvez également double-cliquer dans la liste pour valider aussitôt.")
        titreDefaut = _(u"Tarif au choix")
        if titre == None :
            titre = titreDefaut
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titreDefaut, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")

        # Liste de choix
        self.ctrl_choix = ListView(self, -1, lignes_calcul=lignes_calcul, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_choix.MAJ() 
        
        # Détail prestation
        self.box_prestation_staticbox = wx.StaticBox(self, -1, _(u"Détail de la prestation"))
        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, label)
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self, font=wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD, 0, u""), style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
        self.ctrl_montant.SetMontant(montant)
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterMontant, self.ctrl_montant)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        # Init
        self.ctrl_choix.SetFocus() 

    def __set_properties(self):
        self.ctrl_label.SetToolTip(wx.ToolTip(_(u"Vous pouvez modifier ici un label personnalisé pour la prestation")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez ici le montant de la prestation et tapez sur la touche Entrée pour valider rapidement")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.ctrl_choix, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        box_prestation = wx.StaticBoxSizer(self.box_prestation_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        box_prestation.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(box_prestation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
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
        self.SetMinSize((450, 550))
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
    
    def SetSelection(self, label="", montant=0.0, valider=False):
        if label == None : label = ""
        self.ctrl_label.SetValue(label)
        self.ctrl_montant.SetMontant(montant)
        if valider == True :
            self.OnBoutonOk(None)
        
    def OnBoutonOk(self, event): 
        # Validation du montant
        validation, message = self.ctrl_montant.Validation() 
        if validation == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant valide pour cette prestation !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return
        # Validation du label
        if self.ctrl_label.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un label pour cette prestation !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetMontant(self):
        return self.ctrl_montant.GetMontant() 
    
    def GetLabel(self):
        return self.ctrl_label.GetValue()

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def OnEnterMontant(self, event):
        self.OnBoutonOk(None)
        
        



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    lignes_calcul = [
        {"label" : u"Tarif 1", "montant_unique" : 1.0},
        {"label" : u"Tarif 2", "montant_unique" : 2.0},
        {"label" : u"Tarif 3", "montant_unique" : 3.0},
        ]
    frame_1 = Dialog(None, lignes_calcul=lignes_calcul, label=u"Test", montant=0.0)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
