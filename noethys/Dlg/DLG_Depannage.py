#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.customtreectrl as CT
import wx.lib.agw.hyperlink as Hyperlink

import GestionDB
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Depannage


##class Hyperlien(Hyperlink.HyperLinkCtrl):
##    def __init__(self, parent, item, hypertreelist, labelCorrection, anomalie):
##        Hyperlink.HyperLinkCtrl.__init__(self, parent, id=-1, label=labelCorrection, URL="")
##        self.parent = parent
##        self.item = item
##        self.anomalie = anomalie
##        self.hypertreelist = hypertreelist
##        
##        self.SetBackgroundColour((255, 255, 255))
##        self.AutoBrowse(False)
##        self.SetColours("BLUE", "BLUE", "BLUE")
##        self.SetUnderlines(False, False, True)
##        self.SetBold(False)
##        self.EnableRollover(True)
##        self.SetToolTip(wx.ToolTip(labelCorrection))
##        self.UpdateLink()
##        self.DoPopup(False)
##        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
##        
##    def OnLeftLink(self, event):
##        DB = GestionDB.DB()
##        self.anomalie.Correction(DB)
##        DB.Close() 
##        # Modifie image
##        if self.anomalie.corrige == True :
##            self.hypertreelist.SetItemImage(self.item, self.hypertreelist.img_ok, which=wx.TreeItemIcon_Normal)
##            self.Enable(False)



def Autodetection(parent=None):
    """ Auto-détection d'anomalies """
    # Recherche d'anomalies
    d = UTILS_Depannage.Depannage(parent)
    listeResultats = d.GetResultats()
    nbreAnomalies = d.GetNbreAnomalies() 
    print("Processus d'auto-detection des anomalies : %d anomalies detectees" % nbreAnomalies)
    if nbreAnomalies == 0 :
        return None
    # Propose une correction des anomalies
    dlg = wx.MessageDialog(parent, _(u"Des anomalies ont été détectées dans ce fichier de données.\n\nSouhaitez-vous lancer maintenant le correcteur d'anomalies ?"), _(u"Anomalies"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
    reponse = dlg.ShowModal() 
    dlg.Destroy()
    if reponse == wx.ID_YES :
        dlg = Dialog(parent)
        dlg.ShowModal() 
        dlg.Destroy()
    return nbreAnomalies


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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
        if self.URL == "tout" : self.parent.ctrl_resultats.Coche(True)
        if self.URL == "rien" : self.parent.ctrl_resultats.Coche(False)
        self.UpdateLink()


class CTRL(CT.CustomTreeCtrl):
    def __init__(self, parent): 
        CT.CustomTreeCtrl.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.parent = parent

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
                        
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT | CT.TR_AUTO_CHECK_CHILD) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

    def MAJ(self):
        # Get données
        d = UTILS_Depannage.Depannage()
        listeResultats = d.GetResultats()
        nbreAnomalies = d.GetNbreAnomalies() 
            
        # RAZ ctrl
        self.DeleteAllItems()
        if nbreAnomalies == 0 : texte = _(u"Aucune anomalie détectée")
        elif nbreAnomalies == 1 : texte = _(u"1 anomalie détectée :")
        else : texte = _(u"%d anomalies détectées :") % nbreAnomalies
        self.root = self.AddRoot(texte)
        self.SetItemBold(self.root, True)
        
        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.img_ok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Ok4.png'), wx.BITMAP_TYPE_PNG))
        self.img_pasok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Interdit2.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Remplissage
        for labelAnomalie, labelCorrection, listeAnomalies in listeResultats :
            if len(listeAnomalies) > 0 :
                niveauRubrique = self.AppendItem(self.root, u"%s (%d)" % (labelAnomalie, len(listeAnomalies)), ct_type=1)
                self.SetItemBold(niveauRubrique, True)

                for anomalie in listeAnomalies :
                    if anomalie.correction_manuelle == False:
                        niveauAnomalie = self.AppendItem(niveauRubrique, anomalie.label, ct_type=1)
                        self.SetPyData(niveauAnomalie, {"type" : "anomalie", "anomalie" : anomalie})
                    else:
                        niveauAnomalie = self.AppendItem(niveauRubrique, anomalie.label)
                    if anomalie.corrige == True :
                        img = self.img_ok
                    else :
                        img = self.img_pasok
                    self.SetItemImage(niveauAnomalie, img, which=wx.TreeItemIcon_Normal)

        self.ExpandAll() 
        self.Coche(True)
            
    def Coche(self, etat=True):
        niveauRubrique = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            self.CheckItem(niveauRubrique, etat)
            niveauAnomalie = self.GetFirstChild(niveauRubrique)[0]
            for index2 in range(self.GetChildrenCount(niveauRubrique, recursively=False)) :
                self.CheckItem(niveauAnomalie, etat)
                niveauAnomalie = self.GetNextChild(niveauRubrique, index2+1)[0]
            niveauRubrique = self.GetNextChild(self.root, index1+1)[0]

    def Correction(self):
        """ Obtient la liste des éléments cochés """
        nbreCorrections = 0
        DB = GestionDB.DB()
        niveauRubrique = self.GetFirstChild(self.root)[0]
        for index1 in range(self.GetChildrenCount(self.root, recursively=False)) :
            niveauAnomalie = self.GetFirstChild(niveauRubrique)[0]
            for index2 in range(self.GetChildrenCount(niveauRubrique, recursively=False)) :
                if self.IsItemChecked(niveauAnomalie) :
                    # Correction
                    anomalie = self.GetItemPyData(niveauAnomalie)["anomalie"]
                    if anomalie.corrige == False :
                        anomalie.Correction(DB)
                        nbreCorrections += 1
                    if anomalie.corrige == True :
                        self.SetItemImage(niveauAnomalie, self.img_ok, which=wx.TreeItemIcon_Normal)
                        self.CheckItem(niveauAnomalie, False)
                        self.EnableItem(niveauAnomalie, False)

                niveauAnomalie = self.GetNextChild(niveauRubrique, index2+1)[0]
            niveauRubrique = self.GetNextChild(self.root, index1+1)[0]
        DB.Close() 

        if nbreCorrections == 0 :
            message = _(u"Aucune correction n'a été effectuée !")
        elif nbreCorrections == 1 :
            message = _(u"1 correction a bien été effectuée !")
        else :
            message = _(u"%d corrections ont bien été effectuées !") % nbreCorrections
        dlg = wx.MessageDialog(self, message, _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.sauvegardeEffectuee = False
        
        intro = _(u"Cette fonction permet de détecter et corriger automatiquement certaines anomalies qui pourraient survenir après des erreurs de manipulation ou des bugs non identifiés. Cochez les éléments à corriger puis cliquez sur le bouton Corriger.")
        titre = _(u"Correcteur d'anomalies")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Depannage.png")
        
        # Txt HTML
        self.ctrl_resultats = CTRL(self) #MyHtml(self)
        self.hyper_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout décocher"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Corriger les anomalies cochées"), cheminImage="Images/32x32/Depannage.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        # Init contrôles
        self.ctrl_resultats.MAJ() 

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour corriger les anomalies cochées")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((800, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_resultats, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=5)
        grid_sizer_options.Add( (2, 2), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_options.Add(self.label_separation, 0, 0, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, 0, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_options, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add( (1, 1), 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Correcteurdanomalies")

    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_OK)
    
    def OnBoutonOk(self, event):
        """ Lance la correction """
        if self.sauvegardeEffectuee == False :
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous sauvegarder votre fichier de données avant la correction (Recommandé) ?"), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            
            if reponse == wx.ID_YES :
                from Dlg import DLG_Sauvegarde
                dlg2 = DLG_Sauvegarde.Dialog(self)
                dlg2.ShowModal() 
                dlg2.Destroy()
                self.sauvegardeEffectuee = True
            elif reponse == wx.ID_NO :
                self.sauvegardeEffectuee = True
            elif reponse == wx.ID_CANCEL :
                return

        # Lance la correction
        self.ctrl_resultats.Correction() 
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()