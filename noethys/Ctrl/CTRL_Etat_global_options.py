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
import GestionDB
from Utils import UTILS_Parametres
from Utils import UTILS_Questionnaires
from Ctrl import CTRL_Propertygrid
import wx.propgrid as wxpg
import copy





class CTRL(CTRL_Propertygrid.CTRL):
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)

    def Remplissage(self):
        # Regroupement
        self.Append(wxpg.PropertyCategory(_(u"Regroupement")))

        # Regroupement principal
        liste_regroupements = [
            ("aucun", _(u"Aucun")),
            ("jour", _(u"Jour")),
            ("mois", _(u"Mois")),
            ("annee", _(u"Année")),
            ("activite", _(u"Activité")),
            ("groupe", _(u"Groupe")),
            ("evenement", _(u"Evènement")),
            ("evenement_date", _(u"Evènement (avec date)")),
            ("etiquette", _(u"Etiquette")),
            ("unite_conso", _(u"Unité de consommation")),
            ("categorie_tarif", _(u"Catégorie de tarif")),
            ("ville_residence", _(u"Ville de résidence")),
            ("secteur", _(u"Secteur géographique")),
            ("genre", _(u"Genre (M/F)")),
            ("age", _(u"Age")),
            ("ville_naissance", _(u"Ville de naissance")),
            ("nom_ecole", _(u"Ecole")),
            ("nom_classe", _(u"Classe")),
            ("nom_niveau_scolaire", _(u"Niveau scolaire")),
            ("individu", _(u"Individu")),
            ("famille", _(u"Famille")),
            ("regime", _(u"Régime social")),
            ("caisse", _(u"Caisse d'allocations")),
            ("qf_perso", _(u"Quotient familial (tranches personnalisées)")),
            ("qf_tarifs", _(u"Quotient familial (tranches paramétrées)")),
            ("qf_100", _(u"Quotient familial (tranches de 100)")),
            ("categorie_travail", _(u"Catégorie de travail")),
            ("categorie_travail_pere", _(u"Catégorie de travail du père")),
            ("categorie_travail_mere", _(u"Catégorie de travail de la mère")),
            ]

        # Intégration des questionnaires
        q = UTILS_Questionnaires.Questionnaires()
        for public in ("famille", "individu") :
            for dictTemp in q.GetQuestions(public) :
                label = _(u"Question %s. : %s") % (public[:3], dictTemp["label"])
                code = "question_%s_%d" % (public, dictTemp["IDquestion"])
                liste_regroupements.append((code, label))

        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Regroupement principal"), name="regroupement_principal", liste_choix=liste_regroupements, valeur="aucun")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez un niveau de regroupement principal"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Tranches d'âge
        propriete = CTRL_Propertygrid.Propriete_liste(label=_(u"Regroupement par tranches d'âge"), name="regroupement_age", liste_selections=[])
        propriete.SetHelpString(_(u"Saisissez les tranches d'âge souhaitées séparées par des virgules. Exemple : '3, 6, 12'"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Tranches de QF perso
        propriete = CTRL_Propertygrid.Propriete_liste(label=_(u"Regroupement par tranches de QF"), name="tranches_qf_perso", liste_selections=[])
        propriete.SetHelpString(_(u"Attention, à utiliser avec le regroupement principal 'Quotient familial (tranches personnalisées)'. Saisissez les tranches de QF souhaitées séparées par des virgules. Exemple : '650, 800, 1200'"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Afficher les périodes détaillées
        propriete = wxpg.BoolProperty(label=_(u"Regroupement par périodes détaillées"), name="periodes_detaillees", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les périodes détaillées"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Données
        self.Append(wxpg.PropertyCategory(_(u"Données")))

        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Format des données"), name="format_donnees", liste_choix=[("horaire", _(u"Horaire")), ("decimal", _(u"Décimal"))], valeur="horaire")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez le format d'affichage des données"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Afficher l'avertissement 'familles sans régime'
        propriete = wxpg.BoolProperty(label=_(u"Avertissement si régime famille inconnu"), name="afficher_regime_inconnu", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher un avertissement si le régime d'une ou plusieurs familles est inconnu"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Associer régime inconnu
        DB = GestionDB.DB()
        req = """SELECT IDregime, nom FROM regimes ORDER BY nom;"""
        DB.ExecuterReq(req)
        liste_regimes = DB.ResultatReq()
        DB.Close()
        liste_regimes.insert(0, ("non", _(u"Non")))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Associer régime inconnu à un régime"), name="associer_regime_inconnu", liste_choix=liste_regimes, valeur="non")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez le régime dans lequel vous souhaitez inclure les familles au régime inconnu"))
        propriete.SetAttribute("obligatoire", False)
        self.Append(propriete)

        # Filtres
        self.Append(wxpg.PropertyCategory(_(u"Filtres")))

        # Jours hors vacances
        liste_jours = [(0, _(u"Lundi")), (1, _(u"Mardi")), (2, _(u"Mercredi")), (3, _(u"Jeudi")), (4, _(u"Vendredi")), (5, _(u"Samedi")), (6, _(u"Dimanche"))]
        propriete = CTRL_Propertygrid.Propriete_multichoix(label=_(u"Jours hors vacances"), name="jours_hors_vacances", liste_choix=liste_jours, liste_selections=[0, 1, 2, 3, 4, 5, 6])
        propriete.SetHelpString(_(u"Sélectionnez les jours hors vacances à inclure dans les calculs. Cliquez sur le bouton à droite du champ de saisie pour accéder à la fenêtre de sélection."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Jours de vacances
        propriete = CTRL_Propertygrid.Propriete_multichoix(label=_(u"Jours de vacances"), name="jours_vacances", liste_choix=liste_jours, liste_selections=[0, 1, 2, 3, 4, 5, 6])
        propriete.SetHelpString(_(u"Sélectionnez les jours de vacances à inclure dans les calculs. Cliquez sur le bouton à droite du champ de saisie pour accéder à la fenêtre de sélection."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Etat des consommations
        liste_etats = [("reservation", _(u"Pointage en attente")), ("present", _(u"Présent")), ("absentj", _(u"Absence justifiée")), ("absenti", _(u"Absence injustifiée"))]
        propriete = CTRL_Propertygrid.Propriete_multichoix(label=_(u"Etat des consommations"), name="etat_consommations", liste_choix=liste_etats, liste_selections=["reservation", "present", "absentj", "absenti"])
        propriete.SetHelpString(_(u"Sélectionnez les états de consommations à inclure dans les calculs. Cliquez sur le bouton à droite du champ de saisie pour accéder à la fenêtre de sélection."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Affichage
        self.Append(wxpg.PropertyCategory(_(u"Affichage")))

        # Orientation page
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Orientation de la page"), name="orientation", liste_choix=[("portrait", _(u"Portrait")), ("paysage", _(u"Paysage"))], valeur="portrait")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'orientation de la page"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur Ligne tranche d'âge
        propriete = wxpg.ColourProperty(label=_(u"Couleur de la ligne tranche d'âge"), name="couleur_ligne_age", value=wx.Colour(192,192,192) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur de la ligne tranche d'âge"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur Ligne total
        propriete = wxpg.ColourProperty(label=_(u"Couleur de la ligne total"), name="couleur_ligne_total", value=wx.Colour(234,234,234) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur de la ligne total"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur case regroupement principal
        propriete = wxpg.ColourProperty(label=_(u"Couleur de la case regroupement principal"), name="couleur_case_regroupement", value=wx.Colour(0, 0, 0) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur de la case regroupement principal"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur texte regroupement principal
        propriete = wxpg.ColourProperty(label=_(u"Couleur du texte regroupement principal"), name="couleur_texte_regroupement", value=wx.Colour(255, 255, 255) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur du texte regroupement principal"))
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


