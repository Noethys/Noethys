#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import wx.html as html
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Titulaires
from Utils import UTILS_Customize
import six
import requests
from xml.etree import ElementTree
from difflib import SequenceMatcher



class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte=""):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SIMPLE_BORDER | wx.html.HW_NO_SELECTION | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetPage(texte)

    def SetTexte(self, texte=""):
        self.SetPage(texte)

# -------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, dictParametres={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.dictParametres = dictParametres

        # Bandeau
        intro = _(u"La recherche est totalement automatisée mais vous pouvez effectuer une recherche manuelle en modifiant les paramètres de recherche puis en cliquant sur Rechercher.")
        titre = _(u"Contrôle des coordonnées")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Personnes.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Paramètres"))
        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.label_prenom = wx.StaticText(self, wx.ID_ANY, _(u"Prénom :"))
        self.ctrl_prenom = wx.TextCtrl(self, -1, "")
        self.label_adresse = wx.StaticText(self, wx.ID_ANY, _(u"Adresse :"))
        self.ctrl_adresse = wx.TextCtrl(self, -1, "")

        self.bouton_valider = wx.Button(self, -1, _(u"Rechercher"))

        # Résultats
        self.ctrl_resultats = MyHtml(self)
        self.ctrl_resultats.SetMinSize((450, 180))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonValider, self.bouton_valider)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Init
        self.MAJ()
        self.Rechercher()

    def __set_properties(self):
        self.bouton_valider.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider les paramètres de la recherche")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(4, 2, 10, 10)
        grid_sizer_parametres.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_prenom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_adresse, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.bouton_valider, 0, wx.EXPAND, 0)

        grid_sizer_parametres.AddGrowableCol(1)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_base.Add(box_parametres, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Résultats
        grid_sizer_base.Add(self.ctrl_resultats, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 3, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnClose(self, event):
        self.Destroy()

    def OnBoutonFermer(self, event):
        # Fermeture
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonValider(self, event=None):
        self.Rechercher()

    def MAJ(self):
        dictTitulaires = UTILS_Titulaires.GetTitulaires([self.dictParametres["IDfamille"],])
        dictInfos = dictTitulaires[self.dictParametres["IDfamille"]]

        try :
            nom = dictInfos["listeTitulaires"][0]["nom"]
            prenom = dictInfos["listeTitulaires"][0]["prenom"]
            rue = dictInfos["adresse"]["rue"]

            self.ctrl_nom.SetValue(nom)
            self.ctrl_prenom.SetValue(prenom)
            self.ctrl_adresse.SetValue(rue)

        except :
            pass

    def Rechercher(self, event=None):
        # Récupération des champs saisis
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez renseigner le nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        prenom = self.ctrl_prenom.GetValue()
        if prenom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez renseigner le prénom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        adresse = self.ctrl_adresse.GetValue()
        if adresse == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez renseigner l'adresse !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Récupération de l'URL
        url = UTILS_Customize.GetValeur("referentiel", "url", None, ajouter_si_manquant=False)
        if url == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez renseigner l'URL dans le fichier Customize !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        url = u"%s/%s* %s*" % (url, nom, prenom)

        # Requête
        try :
            reponse = requests.get(url)
        except Exception as error :
            self.ctrl_resultats.SetTexte(six.text_type(error))
            return

        # Si erreur
        if reponse.status_code != 200:
            self.ctrl_resultats.SetTexte(_(u"Accès au référentiel impossible (Erreur %s)") % reponse.status_code)
            return

        # Conversion en XML
        root = ElementTree.fromstring(reponse.content)

        # Parcours le XML

        nbreResultats = 0
        listeResultats = []
        for child in root:
            ligne = {}
            for node in child.iter():
                if "}nomOfficiel" in node.tag:
                    ligne["nom"] = node.text
                if "}prenomUsuel" in node.tag:
                    ligne["prenom"] = node.text
                if "}voieNumero" in node.tag:
                    ligne["adresse"] = node.text

            nbreResultats += 1
            listeResultats.append(ligne)

        # Analyse des résultats
        listeResultatsTraites = []
        for dictTemp in listeResultats :
            texte1 = u"%s#%s#%s" % (dictTemp["nom"], dictTemp["prenom"], dictTemp["adresse"])
            texte2 = u"%s#%s#%s" % (nom, prenom, adresse)
            pourcent = GetRatioDiffTextes(texte1, texte2)
            listeResultatsTraites.append((pourcent, dictTemp))

        # Tri en fonction du nombre de similarités
        listeResultatsTraites.sort(reverse=True)

        # Affichage des résultats
        if nbreResultats > 0 :
            texte = _(u"<FONT SIZE=5><B>%d résultats :</B><BR></FONT><BR>") % nbreResultats
        else :
            texte = _(u"<FONT SIZE=5><B>Aucun résultat</B><BR></FONT><BR>")

        for pourcent, dictTemp in listeResultatsTraites :
            if pourcent == 100 :
                couleur = "GREEN"
            elif pourcent > 90 :
                couleur = "#FF8000"
            else :
                couleur = "RED"

            texte += _(u"""
            <FONT SIZE=2 COLOR='%s'>Pertinence : %s%%</FONT> <BR>
            Nom : <B>%s</B> <BR>
            Prénom : <B>%s</B> <BR>
            Adresse : <B>%s</B> <BR>
            <BR>
            """) % (couleur, pourcent, dictTemp["nom"], dictTemp["prenom"], dictTemp["adresse"])

        # Affichage des résultats
        self.ctrl_resultats.SetTexte(texte)


def GetRatioDiffTextes(texte1="", texte2=""):
    """ Retourne un pourcentage des similarités entre deux chaînes """
    m = SequenceMatcher(None, texte1.lower(), texte2.lower())
    pourcent = int(m.ratio() * 100)
    return pourcent




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dictParametres = {"IDfamille" : 1, "IDproduit" : 1, "IDcategorie" : 1}
    dialog_1 = Dialog(None, dictParametres=dictParametres)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
