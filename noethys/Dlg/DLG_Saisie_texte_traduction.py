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
import wx.html as html
from Dlg import DLG_Messagebox



class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25, couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.couleurFond = couleurFond
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetTexte(texte)
    
    def SetTexte(self, texte=u""):
        self.SetPage(texte)
        self.SetBackgroundColour(self.couleurFond)

class CTRL_Avertissement(wx.Panel):
    def __init__(self, parent, texte=u"", couleurFond=wx.Colour(255, 147, 132)):
        wx.Panel.__init__(self, parent, -1, style=wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(couleurFond)

        texte = _(u"""
            <FONT SIZE=-1>
            Lorsque vous traduisez un texte, veillez à conserver le même formatage du texte : Notamment les caractères spéciaux, espaces et balises.
            Leur suppression pourrait entraîner un dysfonctionnement du logiciel.
            Exemples : %s %d %.2f \\n <para> <font>... 
            </FONT>
            """)

        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Attention.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_html = MyHtml(self, texte=texte, couleurFond=couleurFond, hauteur=25)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.ctrl_image, 0, wx.ALL, 10)
        sizer.Add(self.ctrl_html, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def SetTexte(self, texte=u""):
        self.ctrl_html.SetTexte(texte)





class Dialog(wx.Dialog):
    def __init__(self, parent, texte="", traduction=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        
        self.ctrl_avertissement = CTRL_Avertissement(self) 
        
        self.label_texte = wx.StaticText(self, wx.ID_ANY, _(u"Texte original :"))
        self.ctrl_texte = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.ctrl_texte.SetBackgroundColour((245, 245, 245)) 
        
        self.label_traduction = wx.StaticText(self, wx.ID_ANY, _(u"Traduction :"))
        self.ctrl_traduction = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
                
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        self.ctrl_texte.SetValue(texte)
        self.ctrl_traduction.SetValue(traduction)
        wx.CallAfter(self.ctrl_traduction.SetFocus)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une traduction"))
        self.ctrl_texte.SetToolTip(wx.ToolTip(_(u"Texte original")))
        self.ctrl_traduction.SetToolTip(wx.ToolTip(_(u"Saisissez une traduction")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((670, 400))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(4, 2, 10, 10)
        
        grid_sizer_base.Add(self.ctrl_avertissement, 0, wx.EXPAND, 0)
        
        grid_sizer_haut.Add(self.label_texte, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_haut.Add(self.ctrl_texte, 0, wx.EXPAND, 0)
        grid_sizer_haut.Add(self.label_traduction, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_haut.Add(self.ctrl_traduction, 0, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableRow(1)
        grid_sizer_haut.AddGrowableCol(1)
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
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Traduirelelogiciel")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetTraduction(self):
        return self.ctrl_traduction.GetValue() 
        
    def OnBoutonOk(self, event): 
        # Vérification de la traduction
        balises = [u"\n", u"%s", "%d", "%.2f", ]
        differences = []
        for balise in balises :
            nbreOriginal = self.ctrl_texte.GetValue().count(balise)
            nbreTraduction = self.ctrl_traduction.GetValue().count(balise)
            
            if nbreOriginal != nbreTraduction :
                balise = balise.replace("\n", "\\n")
                detail = u"%d fois dans le texte original et %d fois dans le texte traduit" % (nbreOriginal, nbreTraduction)
                differences.append(u"%s  -> %s" % (balise, detail))
                
        if len(differences) > 0 :
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Avertissement"), introduction=_(u"Attention, les éléments suivants du texte original n'apparaissent pas\ndans la traduction : "), detail="\n".join(differences), conclusion=_(u"Il est très fortement conseillé de les insérer dans la traduction !"), icone=wx.ICON_EXCLAMATION, boutons=[_(u"Valider quand même"), _(u"Annuler")])
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            if reponse == 1 :
                return False
            
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
        
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    texte = u"Ceci est un texte\nmultiligne. Le %s est là ainsi que le %s..."
    dialog_1 = Dialog(None, texte=texte)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
