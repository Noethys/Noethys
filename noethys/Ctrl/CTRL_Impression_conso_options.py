#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import GestionDB
from Ctrl import CTRL_Propertygrid
import wx.propgrid as wxpg
import copy




class CTRL(CTRL_Propertygrid.CTRL):
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)

    def Remplissage(self):

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Page")))

        # Orientation page
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Orientation de la page"), name="orientation", liste_choix=[("automatique", _(u"Automatique")), ("portrait", _(u"Portrait")), ("paysage", _(u"Paysage"))], valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'orientation de la page"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Lignes")))

        # Tri
        liste_choix = [("nom", _(u"Nom")), ("prenom", _(u"Prénom")), ("age", _(u"Âge"))]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Tri"), name="tri", liste_choix=liste_choix, valeur="nom")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez le tri"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Ordre
        liste_choix = [("croissant", _(u"Croissant")), ("decroissant", _(u"Décroissant"))]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Ordre"), name="ordre", liste_choix=liste_choix, valeur="croissant")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'ordre"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Afficher lignes vierges
        propriete = wxpg.IntProperty(label=_(u"Lignes vierges"), name="nbre_lignes_vierges", value=3)
        propriete.SetEditor("SpinCtrl")
        propriete.SetHelpString(_(u"Nombre de lignes vierges à afficher en fin de liste"))
        propriete.SetAttribute("obligatoire", True)
        propriete.SetAttribute("Min", 0)
        self.Append(propriete)

        # Afficher tous les inscrits
        propriete = wxpg.BoolProperty(label=_(u"Afficher tous les inscrits"), name="afficher_inscrits", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher tous les inscrits"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Hauteur ligne individu
        liste_choix = [("automatique", _(u"Automatique")),]
        for x in range(5, 205, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Hauteur de la ligne Individu"), name="hauteur_ligne_individu", liste_choix=liste_choix, valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la hauteur de la ligne de l'individu (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur du fond de titre
        propriete = wxpg.ColourProperty(label=_(u"Couleur ligne de titre"), name="couleur_fond_titre", value=wx.Colour(208, 208, 208) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur de fond de la ligne de titre"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur du fond d'entête de colonne
        propriete = wxpg.ColourProperty(label=_(u"Couleur ligne des entêtes"), name="couleur_fond_entetes", value=wx.Colour(240, 240, 240) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur de fond de la ligne des entêtes"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur du fond de total
        propriete = wxpg.ColourProperty(label=_(u"Couleur ligne de total"), name="couleur_fond_total", value=wx.Colour(208, 208, 208) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur de fond de la ligne de total"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Taille nom activité
        propriete = wxpg.IntProperty(label=_(u"Taille de police du nom d'activité"), name="activite_taille_nom", value=5)
        propriete.SetEditor("SpinCtrl")
        propriete.SetHelpString(_(u"Taille de police du nom d'activité"))
        propriete.SetAttribute("obligatoire", True)
        propriete.SetAttribute("Min", 0)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonne Photo")))

        # Afficher les photos
        liste_choix = [("non", _(u"Non")), ("petite", _(u"Petite taille")), ("moyenne", _(u"Moyenne taille")), ("grande", _(u"Grande taille"))]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Afficher les photos"), name="afficher_photos", liste_choix=liste_choix, valeur="non")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Afficher les photos individuelles"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonne Individu")))

        # Largeur colonne nom
        liste_choix = [("automatique", _(u"Automatique")),]
        for x in range(5, 305, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Largeur de la colonne"), name="largeur_colonne_nom", liste_choix=liste_choix, valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la largeur de la colonne Nom de l'individu (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonne Âge")))

        # Afficher l'âge des individus
        propriete = wxpg.BoolProperty(label=_(u"Afficher la colonne"), name="afficher_age", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher de la colonne de l'âge des individus"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Largeur colonne âge
        liste_choix = [("automatique", _(u"Automatique")),]
        for x in range(5, 305, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Largeur de la colonne"), name="largeur_colonne_age", liste_choix=liste_choix, valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la largeur de la colonne Âge de l'individu (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonnes des unités")))

        # Afficher les évènements
        propriete = wxpg.BoolProperty(label=_(u"Afficher les évènements"), name="afficher_evenements", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les évènements"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher les étiquettes
        propriete = wxpg.BoolProperty(label=_(u"Afficher les étiquettes"), name="afficher_etiquettes", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les étiquettes"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Masquer les consommations
        propriete = wxpg.BoolProperty(label=_(u"Masquer les consommations"), name="masquer_consommations", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour masquer les consommations"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Largeur colonne unités
        liste_choix = [("automatique", _(u"Automatique")),]
        for x in range(5, 105, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Largeur de la colonne"), name="largeur_colonne_unite", liste_choix=liste_choix, valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la largeur de chaque colonne unité (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonnes personnalisées")))

        # Largeur colonne unités
        liste_choix = []
        for x in range(5, 105, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Largeur par défaut des colonnes"), name="largeur_colonne_perso", liste_choix=liste_choix, valeur="40")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la largeur par défaut de toutes les colonnes personnalisées (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonne Informations")))

        # Afficher les informations
        propriete = wxpg.BoolProperty(label=_(u"Afficher la colonne"), name="afficher_informations", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher la colonne Informations"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Masquer les informations
        propriete = wxpg.BoolProperty(label=_(u"Masquer les informations"), name="masquer_informations", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour masquer le contenu de la colonne Informations"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher les cotisations manquantes
        propriete = wxpg.BoolProperty(label=_(u"Afficher les cotisations manquantes"), name="afficher_cotisations_manquantes", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les cotisations manquantes"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher les pièces manquantes
        propriete = wxpg.BoolProperty(label=_(u"Afficher les pièces manquantes"), name="afficher_pieces_manquantes", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les pièces manquantes"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Largeur colonne informations
        liste_choix = [("automatique", _(u"Automatique")),]
        for x in range(5, 505, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Largeur de la colonne"), name="largeur_colonne_informations", liste_choix=liste_choix, valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la largeur de la colonne Informations (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)









    def Validation(self):
        """ Validation des données saisies """
        # Vérifie que les données obligatoires ont été saisies
        for nom, valeur in self.GetPropertyValues().items():
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True:
                if valeur == "" or valeur == None:
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % self.GetPropertyLabel(nom), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        # Vérifie les tranches de QF perso
        if self.GetPropertyByName("regroupement_principal").GetValue() == "qf_perso" :
            if self.GetPropertyByName("tranches_qf_perso").GetValue() == []:
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir au moins une tranche de QF personnalisée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return True

    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        return False

    def GetParametres(self):
        return copy.deepcopy(self.GetPropertyValues())

    def SetParametres(self, dictParametres={}):
        # Réinitialisation
        if dictParametres == None :
            self.Reinitialisation(afficher_dlg=False)
            return

        # Envoi des paramètres au Ctrl
        for nom, valeur in dictParametres.items():
            try :
                propriete = self.GetPropertyByName(nom)
                propriete.SetValue(valeur)
            except :
                pass


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)        
        self.ctrl = CTRL(panel)
        self.boutonTest = wx.Button(panel, -1, _(u"Sauvegarder"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        self.ctrl.Sauvegarde()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


