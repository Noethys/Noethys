#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hyperlink as Hyperlink
import GestionDB


# ---------------------------------------------------------------------------------------------------------------------------------
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
        listeLabels = []
        for code, label in self.parent.listeChamps :
            listeLabels.append(u"%s (%s)" % (label, code))
        dlg = wx.SingleChoiceDialog(None, _(u"Sélectionnez un champ à insérer :"), _(u"Insérer un champ"), listeLabels, wx.CHOICEDLG_STYLE)
        dlg.SetSize((580, 700))
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            champ = self.parent.listeChamps[dlg.GetSelection()][0]
            self.parent.InsertTexte(u"{%s}" % champ)
        dlg.Destroy()
        self.UpdateLink()
        

# ---------------------------------------------------------------------------------------------------------------------------------



class Dialog(wx.Dialog):
    def __init__(self, parent, listeChamps=[], IDchamp=None, code="", nom="", formule="", titre=u""):
        """ listeChamps = [(code, label), ...] """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.listeChamps = listeChamps
        self.IDchamp = IDchamp
        
        self.label_code = wx.StaticText(self, -1, _(u"Code :"))
        self.ctrl_code = wx.TextCtrl(self, -1, code, size=(160, -1))
        self.label_code_info = wx.StaticText(self, -1, _(u"(En majuscules et sans espaces)"))
        
        self.label_nom = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, nom)

        self.label_titre = wx.StaticText(self, -1, _(u"Titre de colonne :"))
        self.ctrl_titre = wx.TextCtrl(self, -1, titre)

        self.label_formule = wx.StaticText(self, -1, _(u"Formule :"))
        self.ctrl_formule = wx.TextCtrl(self, -1, formule, style=wx.TE_MULTILINE)
        self.hyper_formule = Hyperlien(self, label=_(u"Insérer un champ"), infobulle=_(u"Cliquez ici pour insérer un champ"), URL="")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un champ personnalisé"))
        self.ctrl_code.SetToolTipString(_(u"Saisissez un code pour ce champ. Ex : 'MONCHAMP1' [OBLIGATOIRE]"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour ce champ. Ex : 'Total des présences' [OBLIGATOIRE]"))
        self.ctrl_titre.SetToolTipString(_(u"Saisissez un titre de colonne pour ce champ [OBLIGATOIRE]"))
        self.ctrl_formule.SetToolTipString(_(u"Saisissez une formule pour ce champ [OPTIONNEL]"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.label_code_info.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.SetMinSize((550, 350))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        
        # Code
        grid_sizer_contenu.Add(self.label_code, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_code = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_code.Add(self.ctrl_code, 0, 0, 0)
        grid_sizer_code.Add(self.label_code_info, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(grid_sizer_code, 1, wx.EXPAND, 0)
        
        # Nom
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        # Titre
        grid_sizer_contenu.Add(self.label_titre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_titre, 0, wx.EXPAND, 0)

        # Formule
        grid_sizer_contenu.Add(self.label_formule, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_formule = wx.FlexGridSizer(rows=3, cols=2, vgap=0, hgap=5)
        grid_sizer_formule.Add(self.ctrl_formule, 0, wx.EXPAND, 0)
        grid_sizer_formule.Add( (2, 2), 0, wx.EXPAND, 0)
        grid_sizer_formule.Add(self.hyper_formule, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)
        grid_sizer_formule.AddGrowableRow(0)
        grid_sizer_formule.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_formule, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(3)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
            
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Etatnominatif")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # Validation de la saisie
        code = self.ctrl_code.GetValue().upper()
        if code == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un code !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code.SetFocus()
            return

        if self.ctrl_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un descriptif !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        if self.ctrl_titre.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre de colonne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return

        # Vérifie que le code n'a pas déjà été attribué
        DB = GestionDB.DB()
        req = """SELECT IDchamp, code
        FROM etat_nomin_champs
        WHERE code='%s'
        ;""" % code
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        for IDchamp, code in listeDonnees :
            if self.IDchamp != IDchamp : 
                dlg = wx.MessageDialog(self, _(u"Ce code a déjà été attribué à un autre champ. Veuillez le modifier !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_code.SetFocus()
                return
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def InsertTexte(self, texte=u""):
        positionCurseur = self.ctrl_formule.GetInsertionPoint() 
        self.ctrl_formule.WriteText(texte)
        self.ctrl_formule.SetInsertionPoint(positionCurseur+len(texte)) 
        self.ctrl_formule.SetFocus()
    
    def GetCode(self):
        return self.ctrl_code.GetValue().upper().strip() 
    
    def GetNom(self):
        return self.ctrl_nom.GetValue().strip() 

    def GetFormule(self):
        return self.ctrl_formule.GetValue().strip() 
    
    def GetTitre(self):
        return self.ctrl_titre.GetValue().strip() 
    
    
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, listeChamps=[(u"CODE1", _(u"Label du champ 1")),])
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
