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
from Ctrl import CTRL_Bouton_image
import wx.html as html
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Vocal
from Ol import OL_Corrections_phoniques
import FonctionsPerso
from Utils import UTILS_Utilisateurs



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
        
    def OnLinkClicked(self, link):
        texte = u"""
        <FONT SIZE=-1>
        <CENTER>
            <IMG SRC="Images/32x32/Telecharger.png">
            <BR><BR>
            <B>Téléchargement de la voix française</B>
            <BR><BR>
            Vous pouvez télécharger gratuitement la voix française "Virginie" en cliquant sur le lien suivant :
            <BR>
            <A HREF="http://www.ac-limoges.fr/ia87/spip.php?article315">Page de téléchargement</A>.
            <BR><BR>
            <I>(Le fichier à télécharger "Virginie-2.zip" se trouve en bas de la page dans le chapitre "Documents joints").</I>
        </CENTER>
        <BR><BR>
        Pour installer le fichier :
        <UL>
        <LI>Dézippez ce fichier</LI>
        <LI>Lancez l'installation en cliquant sur "Virginie.exe"</LI>
        <LI>Utilisez la procédure d'installation standard.</LI>
        </UL>
        <BR><BR>
        Vous pouvez maintenant revenir dans le paramétrage de la synthèse vocale de Noethys pour définir la voix Virginie comme voix par défaut.       
        
        </FONT>
        """
        import DLG_Message_html
        dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Télécharger la voix française"), size=(360, 500))
        dlg.ShowModal()
        dlg.Destroy()
        
        self.GetGrandParent().ctrl_voix.MAJ() 
        self.GetGrandParent().MAJAvertissement() 


class CTRL_Avertissement(wx.Panel):
    def __init__(self, parent, texte=u"", couleurFond=wx.Colour(255, 147, 132)):
        wx.Panel.__init__(self, parent, -1, style=wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(couleurFond)
        
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/48x48/Attention.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_html = MyHtml(self, texte=texte, couleurFond=couleurFond, hauteur=25)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.ctrl_image, 0, wx.ALL, 10)
        sizer.Add(self.ctrl_html, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def SetTexte(self, texte=u""):
        self.ctrl_html.SetTexte(texte)

# ----------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Voix(wx.Choice):
    def __init__(self, parent, vocal):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.vocal = vocal
        self.MAJ() 
        
    def MAJ(self):
        # Récupération de la liste des voix
        listeVoix = self.vocal.GetListeVoix()
        # Remplissage
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for voix in listeVoix :
            listeItems.append(voix.name)
            self.dictDonnees[index] = voix.id
            index += 1
        self.SetItems(listeItems)
        # Sélectionne la voix par défaut
        voixActuelle = self.vocal.GetVoixActuelle()
        if voixActuelle in self.dictDonnees.values() :
            self.SetID(voixActuelle)
        else :
            self.Select(0)
            self.parent.MemoriseVoix(self.dictDonnees[0])

    def SetID(self, id=""):
        for index, idTemp in self.dictDonnees.iteritems():
            if idTemp == id :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

# -----------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Init moteur vocal
        self.vocal = UTILS_Vocal.Vocal() 
        
        # Bandeau
        intro = _(u"Vous pouvez paramétrer et tester ici la synthèse vocale utilisée par Noethys. Attention, si ce n'est pas déjà fait, téléchargez dès à présent la voix française ci-dessous !")
        titre = _(u"Synthèse vocale")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Vocal.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres de la voix"))
        self.label_voix = wx.StaticText(self, -1, _(u"Voix actuelle :"))
        self.ctrl_voix = CTRL_Voix(self, vocal=self.vocal)
        
        # Avertissement
        self.ctrl_avertissement = CTRL_Avertissement(self)
        self.MAJAvertissement() 
        
        # Corrections
        self.box_corrections_staticbox = wx.StaticBox(self, -1, _(u"Corrections phoniques"))
        self.ctrl_corrections = OL_Corrections_phoniques.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_corrections.MAJ() 
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Test
        self.box_test_staticbox = wx.StaticBox(self, -1, _(u"Test"))
        self.ctrl_test = wx.TextCtrl(self, -1, u"")

        # Boutons
        self.bouton_test = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Vocal.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixVoix, self.ctrl_voix)
        self.Bind(wx.EVT_BUTTON, self.OnAjouterCorrection, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnModifierCorrection, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerCorrection, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vocal", "modifier", afficheMessage=False) == False : 
            self.ctrl_voix.Enable(False)
            self.bouton_ajouter.Enable(False)
            self.bouton_modifier.Enable(False)
            self.bouton_supprimer.Enable(False)
            

    def __set_properties(self):
        self.ctrl_voix.SetToolTipString(_(u"Sélectionnez une voix dans la liste"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter une correction phonique. Exemple : Créez une correction 'Kévin'->'Kévine' pour que le moteur vocal lise correctement le son 'in'."))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la correction sélectionnée"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la correction sélectionnée"))
        self.ctrl_test.SetToolTipString(_(u"Tapez un texte à lire"))
        self.bouton_test.SetToolTipString(_(u"Cliquez ici pour lire le texte saisi"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((550, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.label_voix, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_voix, 0, wx.EXPAND, 0)
        
        grid_sizer_parametres.Add( (0, 0), 0, 0, 0)
        grid_sizer_parametres.Add(self.ctrl_avertissement, 0, wx.EXPAND, 0)
        
        grid_sizer_parametres.AddGrowableCol(1)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Corrections
        box_corrections = wx.StaticBoxSizer(self.box_corrections_staticbox, wx.VERTICAL)
        grid_sizer_corrections = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_corrections.Add(self.ctrl_corrections, 0, wx.EXPAND, 0)
        grid_sizer_commandes = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_corrections.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_corrections.AddGrowableRow(0)
        grid_sizer_corrections.AddGrowableCol(0)
        box_corrections.Add(grid_sizer_corrections, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_corrections, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Test
        box_test = wx.StaticBoxSizer(self.box_test_staticbox, wx.VERTICAL)
        grid_sizer_test = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_test.Add(self.ctrl_test, 0, wx.EXPAND, 0)
        grid_sizer_test.Add(self.bouton_test, 0, 0, 0)
        grid_sizer_test.AddGrowableCol(0)
        box_test.Add(grid_sizer_test, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_test, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)        
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
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

    def OnChoixVoix(self, event): 
        id = self.ctrl_voix.GetID() 
        self.MemoriseVoix(id)
    
    def MAJAvertissement(self):
        # Affiche ou cache le cadre d'avertissement
        afficher = False
        if self.vocal.VerifieSiVirginieInstallee() == False :
            texte = u"""
            <FONT SIZE=-1>
            Aucune voix française n'est installée sur votre ordinateur. 
            <A HREF="x">Cliquez ici pour télécharger</A> et installer la voix française "Virginie" sur votre ordinateur.
            </FONT>
            """
            self.ctrl_avertissement.SetTexte(texte)
            afficher = True
        else :
            if self.vocal.VerifieSiVirginieDefaut() == False :
                texte = u"""
                <FONT SIZE=-1>
                La voix française Virginie est bien installée sur votre ordinateur. Veuillez maintenant la sélectionner ci-dessus pour l'activer dans Noethys !
                </FONT>
                """
                self.ctrl_avertissement.SetTexte(texte)
                afficher = True
        self.ctrl_avertissement.Show(afficher)
        self.Layout()

    def MemoriseVoix(self, id=None):
        self.vocal.SetVoixActuelle(id)
        self.MAJAvertissement() 

    def OnAjouterCorrection(self, event): 
        self.ctrl_corrections.Ajouter()

    def OnModifierCorrection(self, event): 
        self.ctrl_corrections.Modifier()

    def OnSupprimerCorrection(self, event): 
        self.ctrl_corrections.Supprimer()
    
    def InitCorrections(self):
        self.vocal.InitCorrections() 

    def OnBoutonTest(self, event): 
        """ Test vocal """
        texte = self.ctrl_test.GetValue()
        if len(texte) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun texte à lire !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_test.SetFocus() 
                return
        # Lecture
        self.vocal.Parle(texte)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Synthsevocale")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
