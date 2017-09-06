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
from Utils.UTILS_Traduction import _
import wx
import wx.html as html
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Titulaires
from Utils import UTILS_Questionnaires
from Utils import UTILS_Distances_villes
from Utils import UTILS_Parametres


class CTRL_Lieu(wx.Choice):
    def __init__(self, parent, dictParametres={}):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.dictParametres = dictParametres
        self.MAJ() 
        if len(self.dictDonnees) > 0 :
            self.Select(0)
    
    def MAJ(self):
        liste_champs = []

        # Recherche adresse du loueur
        if self.dictParametres.has_key("IDfamille") and self.dictParametres["IDfamille"] != None :
            IDfamille = self.dictParametres["IDfamille"]
            dict_titulaires = UTILS_Titulaires.GetTitulaires([IDfamille,])
            rue = dict_titulaires[IDfamille]["adresse"]["rue"]
            cp = dict_titulaires[IDfamille]["adresse"]["cp"]
            ville = dict_titulaires[IDfamille]["adresse"]["ville"]
            liste_champs.append({"code" : "adresse_famille", "label" : _(u"Lieu de résidence du loueur"), "adresse" : "%s %s %s" % (rue, cp, ville)})

        # Questionnaire produits
        if self.dictParametres.has_key("IDproduit") and self.dictParametres["IDproduit"] != None :
            IDproduit = self.dictParametres["IDproduit"]
            questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="produit")
            for dictQuestion in questionnaires.GetDonnees(ID=IDproduit):
                liste_champs.append({"code" : dictQuestion["champ"], "label" : _(u"%s (produit)") % dictQuestion["label"], "adresse" : dictQuestion["reponse"]})

        # Questionnaire catégories de produits
        if self.dictParametres.has_key("IDcategorie") and self.dictParametres["IDcategorie"] != None:
            IDcategorie = self.dictParametres["IDcategorie"]
            questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="categorie_produit")
            for dictQuestion in questionnaires.GetDonnees(ID=IDcategorie):
                liste_champs.append({"code": dictQuestion["champ"], "label": _(u"%s (catégorie de produits)") % dictQuestion["label"], "adresse": dictQuestion["reponse"]})

        # Remplissage du ctrl
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for dictValeurs in liste_champs :
            self.dictDonnees[index] = dictValeurs
            listeItems.append(dictValeurs["label"])
            index += 1

        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)

    def SetCode(self, code=None):
        if code == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["code"] == code :
                 self.SetSelection(index)

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["code"]

    def GetValeurs(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]



# -------------------------------------------------------------------------------------------------------------------------------

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

        # Bandeau
        intro = _(u"Vous pouvez ici mesurer la distance entre deux lieux. Sélectionnez l'origine et la destination du trajet à mesurer. Ces paramètres sont mémorisés pour une utilisation ultérieure.")
        titre = _(u"Mesurer une distance")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Transport.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Paramètres"))
        self.label_origine = wx.StaticText(self, wx.ID_ANY, _(u"Origine :"))
        self.ctrl_origine = CTRL_Lieu(self, dictParametres=dictParametres)
        self.label_destination = wx.StaticText(self, wx.ID_ANY, _(u"Destination :"))
        self.ctrl_destination = CTRL_Lieu(self, dictParametres=dictParametres)
        self.label_moyen = wx.StaticText(self, wx.ID_ANY, _(u"Véhicule :"))
        self.radio_voiture = wx.RadioButton(self, -1, _(u"En voiture"), style=wx.RB_GROUP)
        self.radio_marche = wx.RadioButton(self, -1, _(u"A pied"))
        self.radio_velo = wx.RadioButton(self, -1, _(u"A vélo"))

        # Résultats
        self.ctrl_resultats = MyHtml(self)
        self.ctrl_resultats.SetMinSize((450, 180))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_origine)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_destination)
        self.Bind(wx.EVT_RADIOBUTTON, self.MAJ, self.radio_voiture)
        self.Bind(wx.EVT_RADIOBUTTON, self.MAJ, self.radio_marche)
        self.Bind(wx.EVT_RADIOBUTTON, self.MAJ, self.radio_velo)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Récupération des paramètres mémorisés
        dictParametres = {"origine" : None, "destination" : None, "moyen" : None}
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="locations_mesure_distance", dictParametres=dictParametres)
        if dictParametres.has_key("origine") :
            self.ctrl_origine.SetCode(dictParametres["origine"])
        if dictParametres.has_key("destination") :
            self.ctrl_destination.SetCode(dictParametres["destination"])
        if dictParametres.has_key("moyen") :
            self.SetMoyen(dictParametres["moyen"])

        # Calcule les résultats
        self.MAJ()
        

    def __set_properties(self):
        self.ctrl_origine.SetToolTip(wx.ToolTip(_(u"Sélectionnez une origine dans la liste")))
        self.ctrl_destination.SetToolTip(wx.ToolTip(_(u"Sélectionnez une destination dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.HORIZONTAL)
        grid_sizer_parametres = wx.FlexGridSizer(3, 2, 10, 10)
        grid_sizer_parametres.Add(self.label_origine, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_origine, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_destination, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_destination, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_moyen, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_moyen = wx.FlexGridSizer(1, 3, 10, 10)
        grid_sizer_moyen.Add(self.radio_voiture, 0, 0, 0)
        grid_sizer_moyen.Add(self.radio_marche, 0, 0, 0)
        grid_sizer_moyen.Add(self.radio_velo, 0, 0, 0)
        grid_sizer_parametres.Add(grid_sizer_moyen, 0, wx.ALIGN_CENTER_VERTICAL, 0)

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

    def MemorisationParametres(self):
        # Mémorisation des paramètres
        if self.ctrl_origine.GetCode() != self.ctrl_destination.GetCode() :
            dictValeurs = {
                "origine" : self.ctrl_origine.GetCode(),
                "destination": self.ctrl_destination.GetCode(),
                "moyen": self.GetMoyen(),
                }
            UTILS_Parametres.ParametresCategorie(mode="set", categorie="locations_mesure_distance", dictParametres=dictValeurs)

    def OnClose(self, event):
        self.MemorisationParametres()
        self.Destroy()

    def OnBoutonFermer(self, event):
        self.MemorisationParametres()
        # Fermeture
        self.EndModal(wx.ID_CANCEL)

    def GetMoyen(self):
        if self.radio_marche.GetValue() == True :
            moyen = "marche"
        elif self.radio_velo.GetValue() == True :
            moyen = "velo"
        else :
            moyen = "voiture"
        return moyen

    def SetMoyen(self, moyen=""):
        if moyen == "marche" :
            self.radio_marche.SetValue(True)
        elif moyen == "velo" :
            self.radio_velo.SetValue(True)
        else :
            self.radio_voiture.SetValue(True)

    def MAJ(self, event=None):
        # Récupération de l'origine
        dictValeursOrigine = self.ctrl_origine.GetValeurs()
        if dictValeursOrigine == None or dictValeursOrigine["adresse"] in (None, ""):
            self.ctrl_resultats.SetTexte(_(u"Le lieu d'origine n'est pas valide."))
            return False
        origine_adresse = dictValeursOrigine["adresse"]

        # Récupération de la destination
        dictValeursDestination = self.ctrl_destination.GetValeurs()
        if dictValeursDestination == None or dictValeursDestination["adresse"] in (None, ""):
            self.ctrl_resultats.SetTexte(_(u"Le lieu de destination n'est pas valide."))
            return False
        origine_destination = dictValeursDestination["adresse"]

        # Récupération du moyen
        moyen = self.GetMoyen()

        # Calcul de la distance
        dictResultats = UTILS_Distances_villes.GetDistances(origine=origine_adresse, destinations=origine_destination, moyen=moyen)
        if dictResultats == {} :
            self.ctrl_resultats.SetTexte(_(u"Aucun résultat avec ces paramètres."))
            return False

        # Affichage des résultats
        dictResultats = dictResultats[origine_destination]
        texte = _(u"""
        <FONT SIZE=5><B>Résultats :</B><BR></FONT>
        <BR>
        <FONT SIZE=2>
            Origine : <I>%s</I> <BR>
            Destination : <I>%s</I> <BR>
        </FONT>
        <BR>
        <FONT SIZE=4>
            Distance : <FONT COLOR='RED'><B>%s</B></FONT> <BR>
            Temps : <FONT COLOR='RED'><B>%s</B></FONT> <BR>
        </FONT>
        """) % (origine_adresse, origine_destination, dictResultats["distance_texte"], dictResultats["temps_texte"])
        self.ctrl_resultats.SetTexte(texte)







if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dictParametres = {"IDfamille" : 1, "IDproduit" : 1, "IDcategorie" : 1}
    dialog_1 = Dialog(None, dictParametres=dictParametres)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
