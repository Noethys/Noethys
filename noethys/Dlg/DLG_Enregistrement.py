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
from Utils.UTILS_Traduction import _
import wx
import sys
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
import wx.lib.masked as masked
import wx.html as html
import urllib2
import traceback
import datetime
from Utils import UTILS_Config
from Utils import UTILS_Utilisateurs
import wx.lib.agw.pybusyinfo as PBI


##TEXTE = u"""
##<IMG SRC="Images/80x80/Logo.png">
##<BR>
##<FONT SIZE=2>
##<B>Ceci est un exemple de Titre</B><BR>
##<BR><BR>
##Ceci est un paragaphe
##<BR><BR>
##Et ceci est le deuxième paragraphe
##<BR>
##<A HREF="http://www.noethys.com">Cliquez ici pour accéder au lien</A>.
##</FONT>
##"""

TEXTE = u"""
<FONT SIZE=2>
<P>Noethys est un logiciel totalement libre et gratuit mais son développement représente des milliers d'heures de travail.</P>
<P>Alors si vous jugez que Noethys vous apporte un soutien appréciable au quotidien et 
que vous souhaitez contribuer à son développement, offrez à votre structure un abonnement Classic ou Premium et bénéficiez en échange de la version complète du manuel de l'utilisateur.</P>
<P>
    <SPAN><U>Caractéristiques des abonnements :</U></SPAN>
    <UL>
    <LI>Vous soutenez le développement du logiciel</LI>
    <LI>Vous bénéficiez d'un accès complet au manuel de l'utilisateur</LI>
    <LI>Vous choisissez le montant de votre contribution</LI>
    <LI>Paiement par chèque ou virement</LI>
    <LI>Envoi d'une facture</LI>
    </UL>
</P>
<P>Pour en savoir davantage, <A HREF="publicite">cliquez ici</A>.</P>
</FONT>
"""

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


def GetValidite(identifiant="", code=""):
    try :
        url = "http://www.noethys.com/aide/html/testcode.php?identifiant=%s&code=%s" % (identifiant, code)
        h = urllib2.urlopen(url, timeout=5)
        html = h.read()
        h.close()
    except :
        return False
    
    # Analyse l'état
    if html.startswith("codeok") :
        try :
            date = DateEngEnDateDD(html[7:])
        except :
            date = None
    else :
        date = None
    
    # Affiche l'état
    if date == None :
        return False
    else :
        nbreJoursRestants =  (date - datetime.date.today()).days
        return date, nbreJoursRestants


class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(5)
        self.SetMinSize((-1, hauteur))
        self.SetPage(texte)
        self.SetBackgroundColour(wx.Colour(240, 251, 237))
    
    def OnLinkClicked(self, link):
        from Utils import UTILS_Financement
        dlg = UTILS_Financement.DLG_Financement(None)
        dlg.ShowModal() 
        dlg.Destroy()



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Enregistrement", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.derniereValidation = (None, None)

        # Bandeau
        titre = _(u"Enregistrement")
        intro = _(u"Vous pouvez saisir ici votre code d'enregistrement personnel afin d'activer votre abonnement Classic ou Premium. Effectuez ce paramétrage sur chacun de vos postes.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Cle.png")
        
        # Saisie code
        self.staticbox_code_staticbox = wx.StaticBox(self, -1, _(u"Code d'enregistrement"))
        self.label_identifiant = wx.StaticText(self, -1, _(u"Identifiant :"))
        self.ctrl_identifiant = wx.TextCtrl(self, -1, "")
        self.label_code = wx.StaticText(self, -1, _(u"Code :"))
        self.ctrl_code = masked.TextCtrl(self, -1, "", mask="AAAA-AAAA-AAAA-AAAA-AAAA", formatcodes="F!")
        self.ctrl_code.SetMinSize((190, -1))
        self.bouton_validite = wx.Button(self, -1, _(u"Vérifier la validité"))
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/absenti.png"), wx.BITMAP_TYPE_ANY))
        self.label_validite = wx.StaticText(self, -1, _(u"Veuillez saisir un code."))
        
        # HTML
        self.ctrl_html = MyHtml(self, texte=TEXTE, hauteur=30)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonValidite, self.bouton_validite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Init contrôles
        identifiant = UTILS_Config.GetParametre("enregistrement_identifiant", defaut=None)
        code = UTILS_Config.GetParametre("enregistrement_code", defaut=None)
        if identifiant != None and code != None :
            self.ctrl_identifiant.SetValue(identifiant)
            self.ctrl_code.SetValue(code)
            
        self.VerifieEtat(identifiant, code)
        
        # Vérifie droits utilisateurs
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_enregistrement", "modifier", afficheMessage=False) == False : 
            self.ctrl_identifiant.Enable(False)
            self.ctrl_code.Enable(False)
            self.bouton_validite.Enable(False)
            
            

    def __set_properties(self):
        self.ctrl_identifiant.SetToolTipString(_(u"Saisissez votre identifiant"))
        self.ctrl_code.SetToolTipString(_(u"Saisissez votre code d'enregistrement"))
        self.bouton_validite.SetToolTipString(_(u"Cliquez ici pour vérifier la validité de votre code d'enregistrement"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((460, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        staticbox_code = wx.StaticBoxSizer(self.staticbox_code_staticbox, wx.VERTICAL)
        grid_sizer_code = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        
        grid_sizer_code.Add(self.label_identifiant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_code.Add(self.ctrl_identifiant, 0, wx.EXPAND, 0)
        grid_sizer_code.Add(self.label_code, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_code2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_code2.Add(self.ctrl_code, 0, wx.EXPAND, 0)
        grid_sizer_code2.Add(self.bouton_validite, 0, wx.EXPAND, 0)
        grid_sizer_code2.AddGrowableCol(1)
        grid_sizer_code.Add(grid_sizer_code2, 0, wx.EXPAND, 0)

        grid_sizer_code.Add((5, 5), 0, wx.EXPAND, 0)
        
        grid_sizer_validite = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=3)
        grid_sizer_validite.Add(self.ctrl_image, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.label_validite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.AddGrowableCol(1)
        grid_sizer_code.Add(grid_sizer_validite, 1, wx.EXPAND, 0)
        grid_sizer_code.AddGrowableCol(1)
        staticbox_code.Add(grid_sizer_code, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_code, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_base.Add(self.ctrl_html, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonValidite(self, event): 
        # Vérifie la saisie
        identifiant = self.ctrl_identifiant.GetValue()
        if len(identifiant) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun identifiant !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_identifiant.SetFocus()
            return
        if " " in identifiant :
            dlg = wx.MessageDialog(self, _(u"L'identifiant saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_identifiant.SetFocus()
            return

        code = self.ctrl_code.GetValue()
        if " " in code :
            dlg = wx.MessageDialog(self, _(u"Le code saisi n'est pas complet !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code.SetFocus()
            return
        
        # Vérifie validité en ligne
        self.VerifieEtat(identifiant, code)
        
    
    def VerifieEtat(self, identifiant="", code=""):
        """ Vérifie la validité du code en ligne """
        dlgAttente = PBI.PyBusyInfo(_(u"Vérification du code en cours..."), parent=None, title=_(u"Veuillez patienter"), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        try :
            url = "http://www.noethys.com/aide/html/testcode.php?identifiant=%s&code=%s" % (identifiant, code)
            h = urllib2.urlopen(url, timeout=5)
            html = h.read()
            h.close()
        except Exception, err:
            self.AfficheEtatValidite(texte=u"Vérification impossible. Vérifiez votre connexion internet !", image="attention")
            del dlgAttente
            print "pb dans verification code enregistrement."
            traceback.print_exc(file=sys.stdout)
            return False
        
        # Analyse l'état
        if html.startswith("codeok") :
            try :
                date = DateEngEnDateDD(html[7:])
            except :
                date = None
        else :
            date = None
        
        # Affiche l'état
        if date == None :
            texte = _(u"Vous n'avez saisi aucun code valide")
            image = "pasok"
        else :
            nbreJoursRestants =  (date - datetime.date.today()).days
            if nbreJoursRestants < 0 :
                texte = _(u"Votre licence est périmée depuis le %s") % DateEngFr(str(date))
                image = "pasok"
            elif nbreJoursRestants <= 30 :
                texte = _(u"Votre licence est valide jusqu'au %s (%d jours restants)") % (DateEngFr(str(date)), nbreJoursRestants)
                image = "attention"
            else :
                texte = _(u"Votre licence est valide jusqu'au %s") % DateEngFr(str(date))
                image = "ok"
            
        self.AfficheEtatValidite(texte, image)
        self.derniereValidation = (identifiant, code)
        del dlgAttente

    def AfficheEtatValidite(self, texte=u"", image=""):
        # Image = "ok" "attention", "pasok"
        self.label_validite.SetLabel(texte)
        if image == "ok" : 
            bmp = "Ok4.png"
        elif image == "attention" : 
            bmp = "Attention.png"
        else :
            bmp = "Interdit2.png"
        self.ctrl_image.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % bmp), wx.BITMAP_TYPE_ANY))

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Enregistrement")

    def OnBoutonFermer(self, event): 
        """ Fermeture """
        identifiant = self.ctrl_identifiant.GetValue()
        code = self.ctrl_code.GetValue()
        if len(identifiant) == 0 :
            identifiant = None
        if " " in code :
            code = None
        
        # Vérification des codes
        if identifiant != None and code != None and self.derniereValidation != (identifiant, code) and "impossible" not in self.label_validite.GetLabel() :
            dlg = wx.MessageDialog(self, _(u"Vous avez modifié votre saisie depuis la dernière vérification.\n\nVeuillez vérifier maintenant la validité du code en cliquant sur le bouton 'Vérifier la validité' !"), _(u"Validation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Mémorisation des codes
        UTILS_Config.SetParametre("enregistrement_identifiant", identifiant)
        UTILS_Config.SetParametre("enregistrement_code", code)

        self.EndModal(wx.ID_OK)   
    
    def OnClose(self, event):
        self.OnBoutonFermer(None)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
