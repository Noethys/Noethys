#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.colourselect as csel
import wx.richtext as rt
import sys
import cStringIO
import re

import FonctionsPerso
import GestionDB


def FormateCouleur(texte):
    pos1 = texte.index(",")
    pos2 = texte.index(",", pos1+1)
    r = int(texte[1:pos1])
    v = int(texte[pos1+2:pos2])
    b = int(texte[pos2+2:-1])
    return (r, v, b)


ID_GRAS = wx.NewId()
ID_ITALIQUE = wx.NewId()
ID_SOULIGNE = wx.NewId()
ID_COULEUR_POLICE = wx.NewId()
ID_ALIGNER_GAUCHE = wx.NewId()
ID_ALIGNER_CENTRE = wx.NewId()
ID_ALIGNER_DROIT = wx.NewId()
ID_RETRAIT_GAUCHE = wx.NewId()
ID_RETRAIT_DROIT = wx.NewId()

MOTSCLES = [
    ( "{ID_FAMILLE}", "IDfamille" ),
    ( "{NOM_AVEC_CIVILITE}", "{FAMILLE_NOM}" ),
    ( "{NOM_SANS_CIVILITE}", "nomSansCivilite" ),
    ( "{ADRESSE_RUE}", "{FAMILLE_RUE}" ),
    ( "{ADRESSE_CP}", "{FAMILLE_CP}" ),
    ( "{ADRESSE_VILLE}", "{FAMILLE_VILLE}" ),
    ( "{SOLDE_CHIFFRES}", "solde" ),
    ( "{SOLDE_LETTRES}", "solde_lettres" ),
    ( "{DATE_MIN}", "date_min" ),
    ( "{DATE_MAX}", "date_max" ),
    ( "{NUM_DOCUMENT}", "num_rappel" ),
    ]

class BarreOutils(wx.ToolBar):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TB_FLAT
        wx.ToolBar.__init__(self, *args, **kwds)
        self.parent = self.GetParent() 
        
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
                
        # Boutons
        doBind( self.AddTool(ID_ALIGNER_GAUCHE, wx.Bitmap("Images/Teamword/aligner_gauche.png", wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Aligner à gauche")), self.parent.OnAlignLeft, self.parent.OnUpdateAlignLeft)
        doBind( self.AddTool(ID_ALIGNER_CENTRE, wx.Bitmap("Images/Teamword/aligner_centre.png", wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Centrer")), self.parent.OnAlignCenter, self.parent.OnUpdateAlignCenter)
        doBind( self.AddTool(ID_ALIGNER_DROIT, wx.Bitmap("Images/Teamword/aligner_droit.png", wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Aligner à droite")), self.parent.OnAlignRight, self.parent.OnUpdateAlignRight)
        self.AddSeparator()
        doBind( self.AddTool(ID_GRAS, wx.Bitmap("Images/Teamword/gras.png", wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Gras")), self.parent.OnBold, self.parent.OnUpdateBold)
        doBind( self.AddTool(ID_ITALIQUE, wx.Bitmap("Images/Teamword/italique.png", wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Italique")), self.parent.OnItalic, self.parent.OnUpdateItalic)
        doBind( self.AddTool(ID_SOULIGNE, wx.Bitmap("Images/Teamword/souligne.png", wx.BITMAP_TYPE_ANY), isToggle=True, shortHelpString=_(u"Souligné")), self.parent.OnUnderline, self.parent.OnUpdateUnderline)
        self.AddSeparator()
##        doBind( self.AddTool(ID_COULEUR_POLICE, wx.Bitmap("Images/Teamword/police_couleur.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Couleur de la police")), self.parent.OnColour)
##        self.AddSeparator()
        doBind( self.AddTool(wx.ID_UNDO, wx.Bitmap("Images/Teamword/annuler.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Annuler")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        doBind( self.AddTool(wx.ID_REDO, wx.Bitmap("Images/Teamword/repeter.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Répéter")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        self.AddSeparator()
        doBind( self.AddTool(wx.ID_CUT, wx.Bitmap("Images/Teamword/couper.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Couper")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        doBind( self.AddTool(wx.ID_COPY, wx.Bitmap("Images/Teamword/copier.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Copier")), self.parent.ForwardEvent, self.parent.ForwardEvent)
        doBind( self.AddTool(wx.ID_PASTE, wx.Bitmap("Images/Teamword/coller.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Coller")), self.parent.ForwardEvent, self.parent.ForwardEvent)
##        self.AddSeparator()
##        doBind( self.AddTool(ID_RETRAIT_GAUCHE, wx.Bitmap("Images/Teamword/retrait_gauche.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Diminuer le retrait")), self.parent.OnIndentLess)
##        doBind( self.AddTool(ID_RETRAIT_DROIT, wx.Bitmap("Images/Teamword/retrait_droit.png", wx.BITMAP_TYPE_ANY), shortHelpString=_(u"Augmenter le retrait")), self.parent.OnIndentMore)


        self.SetToolBitmapSize((16, 16))
        self.Realize()
    


class MyRichTextCtrl(rt.RichTextCtrl):
    def __init__(self, parent, id=-1, style=wx.VSCROLL|wx.HSCROLL|wx.WANTS_CHARS ):
        rt.RichTextCtrl.__init__(self, parent, id=id, style=style)


class Dialog(wx.Dialog):
    def __init__(self, parent, IDtexte=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.IDtexte = IDtexte
        self.couleur = (255, 255, 255)
        
        self.listeMotsCles = []
        for motCle, code in MOTSCLES :
            self.listeMotsCles.append(motCle)
        
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralites"))
        
        # Nom
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Couleur
        self.label_couleur = wx.StaticText(self, -1, _(u"Couleur :"))
        self.ctrl_couleur = csel.ColourSelect(self, -1, "", self.couleur, size = (40, 22))
        
        # Attribution
        self.ctrl_attribution = wx.CheckBox(self, -1, u"")
        self.label_attribution_1 = wx.StaticText(self, -1, _(u"Attribuer par défaut lorsque le nombre de jours de retard est entre"))
        self.ctrl_retard_min = wx.SpinCtrl(self, -1, u"", min=0, max=9000)
        self.label_attribution_2 = wx.StaticText(self, -1, _(u"et"))
        self.ctrl_retard_max = wx.SpinCtrl(self, -1, u"", min=0, max=9000)
        
        # Mots-clés
        self.staticbox_motscles_staticbox = wx.StaticBox(self, -1, _(u"Mots-clés disponibles"))
        self.ctrl_motscles = wx.ListBox(self, -1, choices=self.listeMotsCles, style=wx.SIMPLE_BORDER)
        self.ctrl_motscles.SetBackgroundColour("#F0FBED")
        
        # Titre
        self.label_titre = wx.StaticText(self, -1, _(u"Titre :"))
        self.ctrl_titre = wx.TextCtrl(self, -1, u"")
        
        # texte
        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, _(u"Texte"))
        self.barre_outils = BarreOutils(self)
        self.AddRTCHandlers()
        self.ctrl_texte = MyRichTextCtrl(self)
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()


        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnInsertMotcle, self.ctrl_motscles)
        self.ctrl_couleur.Bind(csel.EVT_COLOURSELECT, self.OnSelectColour)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAttribution, self.ctrl_attribution)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDtexte != None :
            self.Importation()
            self.SetTitle(_(u"Modification d'un texte de rappel"))
        else:
            self.SetTitle(_(u"Saisie d'un texte de rappel"))
        
        # Init contrôles
        self.OnCheckAttribution(None)

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour ce texte"))
        self.ctrl_titre.SetToolTipString(_(u"Saisissez le titre qui apparaîtra en entête du document"))
        self.ctrl_couleur.SetToolTipString(_(u"Sélectionnez une couleur"))
        self.ctrl_attribution.SetToolTipString(_(u"Cochez cette case pour que ce texte soit automatiquement attribué en fonction du nombre de jours de retard du paiement"))
        self.ctrl_retard_min.SetMinSize((60, -1))
        self.ctrl_retard_max.SetMinSize((60, -1))
        self.ctrl_motscles.SetToolTipString(_(u"Double-cliquez sur un mot-clé pour l'insérer dans le texte\nou recopiez-le directement (avec ses accolades)."))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((580, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        grid_sizer_texte = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        staticbox_motscles = wx.StaticBoxSizer(self.staticbox_motscles_staticbox, wx.VERTICAL)
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=5)
        grid_sizer_attribution = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_nom.Add(self.label_couleur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_couleur, 0, 0, 0)
        grid_sizer_nom.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_nom, 1, wx.EXPAND, 0)
        grid_sizer_generalites.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_attribution.Add(self.ctrl_attribution, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_attribution.Add(self.label_attribution_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_attribution.Add(self.ctrl_retard_min, 0, 0, 0)
        grid_sizer_attribution.Add(self.label_attribution_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_attribution.Add(self.ctrl_retard_max, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_attribution, 1, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        staticbox_motscles.Add(self.ctrl_motscles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_motscles, 1, wx.EXPAND, 0)
        
        grid_sizer_titre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_titre.Add(self.label_titre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_titre.Add(self.ctrl_titre, 0, wx.EXPAND, 0)
        grid_sizer_titre.AddGrowableCol(1)
        grid_sizer_texte.Add(grid_sizer_titre, 1, wx.EXPAND|wx.BOTTOM, 10)
        
        grid_sizer_texte.Add(self.barre_outils, 0, wx.EXPAND, 0)
        grid_sizer_texte.Add(self.ctrl_texte, 0, wx.EXPAND, 0)
        grid_sizer_texte.AddGrowableRow(2)
        grid_sizer_texte.AddGrowableCol(0)
        
        staticbox_texte.Add(grid_sizer_texte, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_texte, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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
        
    def OnInsertMotcle(self, event):
        index = event.GetSelection()
        motcle = self.listeMotsCles[index]
        self.ctrl_texte.WriteText(motcle)

    def OnCheckAttribution(self, event):
        if self.ctrl_attribution.GetValue() == True :
            self.ctrl_retard_min.Enable(True) 
            self.ctrl_retard_max.Enable(True) 
        else:
            self.ctrl_retard_min.Enable(False) 
            self.ctrl_retard_max.Enable(False) 
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Gnration1")

    def OnSelectColour(self, event):
        reponse = event.GetValue()
        self.couleur = (reponse[0], reponse[1], reponse[2])

    def OnBold(self, evt):
        self.ctrl_texte.ApplyBoldToSelection()
        
    def OnItalic(self, evt): 
        self.ctrl_texte.ApplyItalicToSelection()
        
    def OnUnderline(self, evt):
        self.ctrl_texte.ApplyUnderlineToSelection()
        
    def OnAlignLeft(self, evt):
        self.ctrl_texte.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_LEFT)
        
    def OnAlignRight(self, evt):
        self.ctrl_texte.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_RIGHT)
        
    def OnAlignCenter(self, evt):
        self.ctrl_texte.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_CENTRE)
        
    def OnIndentMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.ctrl_texte.GetInsertionPoint()
        if self.ctrl_texte.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_texte.HasSelection():
                r = self.ctrl_texte.GetSelectionRange()

            attr.SetLeftIndent(attr.GetLeftIndent() + 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.ctrl_texte.SetStyle(r, attr)
       
        
    def OnIndentLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.ctrl_texte.GetInsertionPoint()
        if self.ctrl_texte.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_texte.HasSelection():
                r = self.ctrl_texte.GetSelectionRange()

        if attr.GetLeftIndent() >= 100:
            attr.SetLeftIndent(attr.GetLeftIndent() - 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.ctrl_texte.SetStyle(r, attr)

        
    def OnParagraphSpacingMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.ctrl_texte.GetInsertionPoint()
        if self.ctrl_texte.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_texte.HasSelection():
                r = self.ctrl_texte.GetSelectionRange()

            attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
            attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
            self.ctrl_texte.SetStyle(r, attr)

        
    def OnParagraphSpacingLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.ctrl_texte.GetInsertionPoint()
        if self.ctrl_texte.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_texte.HasSelection():
                r = self.ctrl_texte.GetSelectionRange()

            if attr.GetParagraphSpacingAfter() >= 20:
                attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
                attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
                self.ctrl_texte.SetStyle(r, attr)

        
    def OnLineSpacingSingle(self, evt): 
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.ctrl_texte.GetInsertionPoint()
        if self.ctrl_texte.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_texte.HasSelection():
                r = self.ctrl_texte.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(10)
            self.ctrl_texte.SetStyle(r, attr)
 
                
    def OnLineSpacingHalf(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.ctrl_texte.GetInsertionPoint()
        if self.ctrl_texte.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_texte.HasSelection():
                r = self.ctrl_texte.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(15)
            self.ctrl_texte.SetStyle(r, attr)

        
    def OnLineSpacingDouble(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.ctrl_texte.GetInsertionPoint()
        if self.ctrl_texte.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.ctrl_texte.HasSelection():
                r = self.ctrl_texte.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(20)
            self.ctrl_texte.SetStyle(r, attr)


    def OnFont(self, evt):
        if not self.ctrl_texte.HasSelection():
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un texte."), _(u"Police"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        r = self.ctrl_texte.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_FONT)
        if self.ctrl_texte.GetStyle(self.ctrl_texte.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(wx.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.ctrl_texte.SetStyle(r, attr)
        dlg.Destroy()


    def OnColour(self, evt):
        colourData = wx.ColourData()
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        if self.ctrl_texte.GetStyle(self.ctrl_texte.GetInsertionPoint(), attr):
            colourData.SetColour(attr.GetTextColour())

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colourData = dlg.GetColourData()
            colour = colourData.GetColour()
            if colour:
                if not self.ctrl_texte.HasSelection():
                    self.ctrl_texte.BeginTextColour(colour)
                else:
                    r = self.ctrl_texte.GetSelectionRange()
                    attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
                    attr.SetTextColour(colour)
                    self.ctrl_texte.SetStyle(r, attr)
        dlg.Destroy()

    def OnUpdateBold(self, evt):
        if self.ctrl_texte == None : return
        evt.Check(self.ctrl_texte.IsSelectionBold())
    
    def OnUpdateItalic(self, evt):
        if self.ctrl_texte == None : return
        evt.Check(self.ctrl_texte.IsSelectionItalics())
    
    def OnUpdateUnderline(self, evt): 
        if self.ctrl_texte == None : return
        evt.Check(self.ctrl_texte.IsSelectionUnderlined())
    
    def OnUpdateAlignLeft(self, evt):
        if self.ctrl_texte == None : return
        evt.Check(self.ctrl_texte.IsSelectionAligned(wx.TEXT_ALIGNMENT_LEFT))
        
    def OnUpdateAlignCenter(self, evt):
        if self.ctrl_texte == None : return
        evt.Check(self.ctrl_texte.IsSelectionAligned(wx.TEXT_ALIGNMENT_CENTRE))
        
    def OnUpdateAlignRight(self, evt):
        if self.ctrl_texte == None : return
        evt.Check(self.ctrl_texte.IsSelectionAligned(wx.TEXT_ALIGNMENT_RIGHT))
    
    def ForwardEvent(self, evt):
        if self.ctrl_texte == None : return
        self.ctrl_texte.ProcessEvent(evt)

    def AddRTCHandlers(self):
        # make sure we haven't already added them.
        if rt.RichTextBuffer.FindHandlerByType(rt.RICHTEXT_TYPE_HTML) is not None:
            return
        # This would normally go in your app's OnInit method.  I'm
        # not sure why these file handlers are not loaded by
        # default by the C++ richtext code, I guess it's so you
        # can change the name or extension if you wanted...
        rt.RichTextBuffer.AddHandler(rt.RichTextHTMLHandler())
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler())
        # ...like this
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler(name="Teamword", ext="twd", type=99))
        # This is needed for the view as HTML option since we tell it
        # to store the images in the memory file system.
        wx.FileSystem.AddHandler(wx.MemoryFSHandler())

    def GetHtmlText(self, imagesIncluses=False):
        # Récupération de la source HTML
        handler = rt.RichTextHTMLHandler()
        if imagesIncluses == True : 
            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)
        else:
            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])
        import cStringIO
        stream = cStringIO.StringIO()
        if self.ctrl_texte == None and self.nb.GetPageCount()>0 :
            self.ctrl_texte = self.nb.GetPage(self.nb.GetSelection())
        if not handler.SaveStream(self.ctrl_texte.GetBuffer(), stream):
            return False
        source = stream.getvalue() 
##        source = source.replace("<head></head>", head)
        source = source.decode("utf-8")
        return source
    
    def SaveTexte(self):
        out = cStringIO.StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.ctrl_texte.GetBuffer()
        handler.SaveStream(buffer, out)
        out.seek(0)
        content = out.read()
        return content
    
    def LoadTexte(self, texteXml=""):
        out = cStringIO.StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.ctrl_texte.GetBuffer()
        buffer.AddHandler(handler)
        out.write(texteXml)
        out.seek(0)
        handler.LoadStream(buffer, out)
        self.ctrl_texte.Refresh()
            
    def HtmlEnReportlab(self, source="") :
        # Supprimer l'entete
##        source = source.replace("<html><head></head><body>", "")
##        source = source.replace('<font face="MS Shell Dlg 2" size="2" color="#000000" >', "")
##        source = source.replace("</font></body></html>", "")

        source = source.replace("<html><head></head><body>", "")
        source = source.replace("</body></html>", "")

        # Change la balise <p> en <para>
        source = source.replace("<p", "<para")
        source = source.replace("</p>", "</para>")
        # Supprime des sauts à la ligne
        source = source.replace("<br>", "")
        source = source.replace("\r\n", "")
        # Pour faire des sauts de ligne
        source = source.replace("></para>", "> </para>")
        
        source = re.sub(r'<font.*?>', "", source)
        source = re.sub(r'</font>', "", source)
##        source = re.sub(r'face=".*?"', "", source)
        return source

    def OnBoutonOk(self, event):     
        # Vérification des données
        label = self.ctrl_nom.GetValue()
        if label == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return        
        
        if self.couleur == (255, 255, 255):
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une couleur en cliquant sur le bouton couleur !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_couleur.SetFocus()
            return
        
        attribution = self.ctrl_attribution.GetValue()
        if attribution == True :
            retard_min = self.ctrl_retard_min.GetValue()
            retard_max = self.ctrl_retard_max.GetValue()
            if retard_min >= retard_max :
                dlg = wx.MessageDialog(self, _(u"Les conditions d'attribution par défaut semblent erronées !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return   
        else:
            retard_min = 0
            retard_max = 0
        
        titre = self.ctrl_titre.GetValue()
        if titre == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return        
        
        # Récupération du texte
        texteStr = self.ctrl_texte.GetValue() 
        texteXML = self.SaveTexte()
        textePDF = self.HtmlEnReportlab(self.GetHtmlText())
        if len(texteStr) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_texte.SetFocus()
            return     
        
        # Pour éviter bug de la police segoe UI
        texteXML = texteXML.replace("Segoe UI", "Arial")
        textePDF = textePDF.replace("Segoe UI", "Arial")
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("label", label),
                ("couleur", str(self.couleur)),
                ("retard_min", retard_min),
                ("retard_max", retard_max),
                ("titre", titre),
                ("texte_xml", texteXML),
                ("texte_pdf", textePDF),
                ]
        if self.IDtexte == None :
            self.IDtexte = DB.ReqInsert("textes_rappels", listeDonnees)
        else:
            DB.ReqMAJ("textes_rappels", listeDonnees, "IDtexte", self.IDtexte)
        DB.Close()

        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDtexte(self):
        return self.IDtexte

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT label, couleur, retard_min, retard_max, titre, texte_xml
        FROM textes_rappels
        WHERE IDtexte=%d;
        """ % self.IDtexte
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        label, couleur, retard_min, retard_max, titre, texte_xml = listeDonnees[0]
        
        self.ctrl_nom.SetValue(label)
        self.ctrl_titre.SetValue(titre)
        self.couleur = FormateCouleur(couleur)
        self.ctrl_couleur.SetColour(self.couleur)
        if retard_min != 0 or retard_max != 0 :
            self.ctrl_attribution.SetValue(True)
            self.ctrl_retard_min.SetValue(retard_min)
            self.ctrl_retard_max.SetValue(retard_max)
        self.LoadTexte(texte_xml)
        
    def ImpressionTEST(self):
        texte = self.HtmlEnReportlab(self.GetHtmlText())
        
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Initialisation du PDF
        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        nomDoc = "Temp/test_texte_rappel_%s.pdf" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30)
        story = []
        
        # Test texte
        paraStyle = ParagraphStyle(name="test",
                              fontName="Helvetica",
                              fontSize=9,
                              #leading=7,
                              spaceBefore=0,
                              spaceafter=0,
                            )
        
        listeParagraphes = texte.split("</para>")
        for paragraphe in listeParagraphes :
            textePara = Paragraph(u"%s</para>" % paragraphe, paraStyle)
            story.append(textePara)
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDtexte=1)
    app.SetTopWindow(dlg)
    if dlg.ShowModal() == wx.ID_OK :
        texteXML = dlg.SaveTexte()
        textePDF = dlg.HtmlEnReportlab(dlg.GetHtmlText())
        
        print "texteXML=", texteXML
        print "texteHTML=", dlg.GetHtmlText()
        print "textePDF=", textePDF
        
        dlg.ImpressionTEST() 

    dlg.Destroy() 
    app.MainLoop()
