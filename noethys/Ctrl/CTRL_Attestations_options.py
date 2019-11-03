#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import os

from Utils import UTILS_Identification
from Utils import UTILS_Config
from Utils import UTILS_Parametres

from Dlg import DLG_Filtres_factures
from Ctrl import CTRL_Propertygrid
import wx.propgrid as wxpg
import copy



TEXTE_INTRO = _(u"Je soussigné{SIGNATAIRE_GENRE} {SIGNATAIRE_NOM}, {SIGNATAIRE_FONCTION}, atteste avoir accueilli {NOMS_INDIVIDUS} sur la période du {DATE_DEBUT} au {DATE_FIN} selon le détail suivant :")


def RemplaceMotsCles(texte="", dictValeurs={}):
    for key, valeur, in dictValeurs.items() :
        if key in texte :
            texte = texte.replace(key, valeur)
    return texte


# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(CTRL_Propertygrid.CTRL) :
    def __init__(self, parent, listeActivites=[]):
        self.listeActivites = listeActivites
        self.dictDonnees = {}
        CTRL_Propertygrid.CTRL.__init__(self, parent)
        
    
    def Remplissage(self):
        listeChamps = [
            "{SIGNATAIRE_GENRE}", "{SIGNATAIRE_NOM}", "{SIGNATAIRE_FONCTION}",
            "{NUM_ATTESTATION}", "{DATE_DEBUT}", "{DATE_FIN}", "{DATE_EDITION}", "{LIEU_EDITION}", 
            "{NOMS_INDIVIDUS}", "{DESTINATAIRE_NOM}", "{DESTINATAIRE_RUE}", "{DESTINATAIRE_VILLE}", 
            "{TOTAL_PERIODE}", "{TOTAL_REGLE}", "{SOLDE_DU}", 
            "{ORGANISATEUR_NOM}", "{ORGANISATEUR_RUE}", "{ORGANISATEUR_CP}", "{ORGANISATEUR_VILLE}", "{ORGANISATEUR_TEL}", 
            "{ORGANISATEUR_FAX}", "{ORGANISATEUR_MAIL}", "{ORGANISATEUR_SITE}", "{ORGANISATEUR_AGREMENT}", "{ORGANISATEUR_SIRET}", 
            "{ORGANISATEUR_APE}", 
            ]


        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Modèle")) )

        propriete = wxpg.EnumProperty(label=_(u"Modèle de document"), name="IDmodele", value=0)
        propriete.SetHelpString(_(u"Sélectionnez le modèle de document à utiliser"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.MAJ_modeles() 

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Signataire")) )

        propriete = wxpg.EnumProperty(label=_(u"Signataire du document"), name="signataire", value=0)
        propriete.SetHelpString(_(u"Sélectionnez le signataire du document (à renseigner au préalable dans le paramétrage de l'activité)"))
        propriete.SetAttribute("obligatoire", True)
        propriete.SetAttribute("reinitialisation_interdite", True)
        self.Append(propriete)
        self.MAJ_signataires() 

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Mémorisation")) )
        
        # Mémorisation des paramètres
        propriete = wxpg.BoolProperty(label=_(u"Mémoriser les paramètres"), name="memoriser_parametres", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez mémoriser les paramètres de cette liste")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Répertoire de sauvegarde
        if 'phoenix' in wx.PlatformInfo:
            propriete = wxpg.DirProperty(name=_(u"Répertoire pour copie unique"), label="repertoire_copie", value="")
        else:
            propriete = wxpg.DirProperty(label=_(u"Répertoire pour copie unique"), name="repertoire_copie", value="")
        propriete.SetHelpString(_(u"Enregistrer une copie unique de chaque document dans le répertoire sélectionné. Sinon laissez vide ce champ.")) 
        self.Append(propriete)
        
        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Titre")) )

        # Afficher le titre
        propriete = wxpg.BoolProperty(label=_(u"Afficher le titre"), name="afficher_titre", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher le titre du le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Titre du document"), name="texte_titre", value=_(u"Attestation de présence"))
        propriete.SetHelpString(_(u"Saisissez le titre du document (Par défaut 'Attestation de présence'). Vous pouvez intégrer les mots-clés suivants : %s") % ", ".join(listeChamps)) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte du titre"), name="taille_texte_titre", value=19)
        propriete.SetHelpString(_(u"Saisissez la taille de texte du titre (29 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_titre", "SpinCtrl")
        
        propriete = wxpg.BoolProperty(label=_(u"Afficher la période de facturation"), name="afficher_periode", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher la période de facturation dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de la période"), name="taille_texte_periode", value=8)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de la période (8 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_periode", "SpinCtrl")

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Tableau des prestations")) )

        # Affichage condensé ou détaillé
        propriete = wxpg.EnumProperty(label=_(u"Affichage des prestations"), name="affichage_prestations", labels=[_(u"Détaillé"), _(u"Condensé")], values=[0, 1] , value=0)
        propriete.SetHelpString(_(u"Sélectionnez un type d'affichage")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Intitulés des prestations
        labels = [_(u"Intitulé original"), _(u"Intitulé original + état 'Absence injustifiée'"), _(u"Nom du tarif"), _(u"Nom de l'activité")]
        propriete = wxpg.EnumProperty(label=_(u"Intitulés des prestations"), name="intitules", labels=labels, values=[0, 1, 2, 3] , value=0)
        propriete.SetHelpString(_(u"Sélectionnez le type d'intitulé à afficher pour les prestations")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur 1
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 1"), name="couleur_fond_1", value=wx.Colour(204, 204, 255) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur 1")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur 2
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 2"), name="couleur_fond_2", value=wx.Colour(234, 234, 255) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur 2")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Largeur colonne Date
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Date (ou Qté)"), name="largeur_colonne_date", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Date (50 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_date", "SpinCtrl")
        
        # Largeur colonne Montant HT
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant HT"), name="largeur_colonne_montant_ht", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant HT (50 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_ht", "SpinCtrl")

        # Largeur colonne Montant TVA
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant TVA"), name="largeur_colonne_montant_tva", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant TVA (50 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_tva", "SpinCtrl")

        # Largeur colonne Montant TTC
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant TTC"), name="largeur_colonne_montant_ttc", value=70)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant TTC (70 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_ttc", "SpinCtrl")
        
        # Taille de texte du nom de l'individu
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de l'individu"), name="taille_texte_individu", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de l'individu (9 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_individu", "SpinCtrl")

        # Taille de texte du nom de l'activité
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de l'activité"), name="taille_texte_activite", value=6)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de l'activité (6 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_activite", "SpinCtrl")

        # Taille de texte des noms de colonnes
        propriete = wxpg.IntProperty(label=_(u"Taille de texte des noms de colonnes"), name="taille_texte_noms_colonnes", value=5)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des noms de colonnes (5 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_noms_colonnes", "SpinCtrl")

        # Taille de texte des prestations
        propriete = wxpg.IntProperty(label=_(u"Taille de texte des prestations"), name="taille_texte_prestation", value=7)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des prestations (7 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_prestation", "SpinCtrl")

        # Taille de texte des messages
        propriete = wxpg.IntProperty(label=_(u"Taille de texte des messages"), name="taille_texte_messages", value=7)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des messages (7 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_messages", "SpinCtrl")

        # Taille de texte des labels totaux
        propriete = wxpg.IntProperty(label=_(u"Taille de texte des labels totaux"), name="taille_texte_labels_totaux", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des labels totaux (9 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_labels_totaux", "SpinCtrl")

        # Taille de texte des totaux
        propriete = wxpg.IntProperty(label=_(u"Taille de texte des montants totaux"), name="taille_texte_montants_totaux", value=10)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des montants totaux (10 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_montants_totaux", "SpinCtrl")

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Prestations antérieures")) )

        # Taille de texte
        propriete = wxpg.IntProperty(label=_(u"Taille de texte du commentaire"), name="taille_texte_prestations_anterieures", value=5)
        propriete.SetHelpString(_(u"Saisissez la taille de texte du commentaire de bas de tableaux (5 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_prestations_anterieures", "SpinCtrl")

        # Texte d'information
        propriete = wxpg.LongStringProperty(label=_(u"Texte d'information"), name="texte_prestations_anterieures", value=_(u"Des prestations antérieures ont été reportées sur cette attestation."))
        propriete.SetHelpString(_(u"Saisissez un texte d'information pour les prestations antérieures"))
        self.Append(propriete)

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Texte d'introduction")) )

        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name="texte_introduction", value=TEXTE_INTRO)
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction. Vous pouvez intégrer les mots-clés suivants : %s") % ", ".join(listeChamps)) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte d'introduction"), name="taille_texte_introduction", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte d'introduction (9 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_introduction", "SpinCtrl")

        propriete = wxpg.EnumProperty(label=_(u"Style de texte introduction"), name="style_texte_introduction", labels=[_(u"Normal"), _(u"Italique"), "Gras", _(u"Italique + Gras")], values=[0, 1, 2, 3] , value=1)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond introduction"), name="couleur_fond_introduction", value=wx.Colour(255, 255, 255) )
        propriete.SetHelpString(_(u"Sélectionnez une couleur de fond pour le texte d'introduction")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.ColourProperty(label=_(u"Couleur de bord introduction"), name="couleur_bord_introduction", value=wx.Colour(255, 255, 255) )
        propriete.SetHelpString(_(u"Sélectionnez une couleur de bord pour le texte d'introduction")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte d'introduction"), name="alignement_texte_introduction", labels=[_(u"Gauche"), _(u"Centre"), _(u"Droite")], values=[0, 1, 2] , value=1)
        propriete.SetHelpString(_(u"Sélectionnez un type d'alignement pour le texte d'introduction")) 
        self.Append(propriete)

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Texte de conclusion")) )

        propriete = wxpg.LongStringProperty(label=_(u"Texte de conclusion"), name="texte_conclusion", value=u"")
        propriete.SetHelpString(_(u"Saisissez un texte de conclusion (Aucun par défaut). Vous pouvez intégrer les mots-clés suivants : %s") % ", ".join(listeChamps)) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte de conclusion"), name="taille_texte_conclusion", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de conclusion (9 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_conclusion", "SpinCtrl")

        propriete = wxpg.EnumProperty(label=_(u"Style de texte conclusion"), name="style_texte_conclusion", labels=[_(u"Normal"), _(u"Italique"), "Gras", _(u"Italique + Gras")], values=[0, 1, 2, 3] , value=0)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond conclusion"), name="couleur_fond_conclusion", value=wx.Colour(255, 255, 255) )
        propriete.SetHelpString(_(u"Sélectionnez une couleur de fond pour le texte de conclusion")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.ColourProperty(label=_(u"Couleur de bord conclusion"), name="couleur_bord_conclusion", value=wx.Colour(255, 255, 255) )
        propriete.SetHelpString(_(u"Sélectionnez une couleur de bord pour le texte de conclusion")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte de conclusion"), name="alignement_texte_conclusion", labels=[_(u"Gauche"), _(u"Centre"), _(u"Droite")], values=[0, 1, 2] , value=0)
        propriete.SetHelpString(_(u"Sélectionnez un type d'alignement pour le texte de conclusion")) 
        self.Append(propriete)

        # Signature 
        self.Append( wxpg.PropertyCategory(_(u"Signature")) )

        propriete = wxpg.ImageFileProperty(label=_(u"Image de signature"), name="image_signature")
        propriete.SetHelpString(_(u"Sélectionnez l'image d'une signature à insérer en fin de document")) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de l'image (en %)"), name="taille_image_signature", value=100)
        propriete.SetHelpString(_(u"Saisissez la taille de l'image en pourcentage (100 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("taille_image_signature", "SpinCtrl")

        propriete = wxpg.EnumProperty(label=_(u"Alignement de l'image"), name="alignement_image_signature", labels=[_(u"Gauche"), _(u"Centre"), _(u"Droite")], values=[0, 1, 2] , value=0)
        propriete.SetHelpString(_(u"Sélectionnez un type d'alignement pour l'image de signature")) 
        self.Append(propriete)




    def Validation(self):
        """ Validation des données saisies """
        for nom, valeur in self.GetPropertyValues().items() :
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True :
                if valeur == "" or valeur == None :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % nom, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        return True
        
    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        del dictValeurs["signataire"]
        # Recherche les paramètres mémorisés
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="impression_attestation", dictParametres=dictValeurs)
        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.items() :
            propriete = self.GetPropertyByName(nom)
            ancienneValeur = propriete.GetValue() 
            propriete.SetValue(valeur)
    
    def Sauvegarde(self, forcer=False):
        """ Mémorisation des valeurs du contrôle """
        if self.GetPropertyByName("memoriser_parametres").GetValue() == True or forcer == True :
            dictValeurs = copy.deepcopy(self.GetPropertyValues())
            del dictValeurs["signataire"]
            UTILS_Parametres.ParametresCategorie(mode="set", categorie="impression_attestation", dictParametres=dictValeurs)
        
    def GetValeurs(self) :
        return self.GetPropertyValues()

    def MAJ_modeles(self):
        categorie = "attestation"
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, largeur, hauteur, observations, defaut 
        FROM documents_modeles
        WHERE categorie='%s'
        ORDER BY nom;""" % categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        propriete = self.GetPropertyByName("IDmodele")
        self.dictDonnees["modeles"] = {}
        choix = wxpg.PGChoices()
        selectionDefaut = None
        for IDmodele, nom, largeur, hauteur, observations, defaut in listeDonnees :
            self.dictDonnees["modeles"][IDmodele] = { "nom" : nom, "largeur" : largeur, "hauteur" : hauteur, "observations" : observations, "defaut" : defaut}
            choix.Add(nom, IDmodele)
            if defaut != None : 
                selectionDefaut = IDmodele
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete) 
        if selectionDefaut != None :
            propriete.SetValue(selectionDefaut)

    def MAJ_signataires(self):
        ancienneValeur = None
        propriete = self.GetPropertyByName("signataire")
        index = propriete.GetValue()
        if index != None and index in self.dictDonnees["signataires"] :
            ancienneValeur = self.dictDonnees["signataires"][index]["ID"]
            
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        DB = GestionDB.DB()
        req = """SELECT IDresponsable, IDactivite, nom, fonction, defaut, sexe
        FROM responsables_activite
        WHERE IDactivite IN %s
        ORDER BY nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictDonnees["signataires"] = {}
        choix = wxpg.PGChoices()
        selectionDefaut = None
        index = 0
        for IDresponsable, IDactivite, nom, fonction, defaut, sexe in listeDonnees :
            self.dictDonnees["signataires"][index] = { "ID" : IDresponsable, "IDactivite" : IDactivite, "nom" : nom, "fonction" : fonction, "defaut" : defaut, "sexe" : sexe}
            choix.Add(nom, index)
            if defaut == 1 : 
                selectionDefaut = index
            index += 1
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete) 
        if selectionDefaut != None :
            propriete.SetValue(selectionDefaut)
        # Recherche le nom de l'utilisateur parmi la liste des signataires
        dictUtilisateur = UTILS_Identification.GetDictUtilisateur()
        for index, dictDonnees in self.dictDonnees["signataires"].items() :
            if ancienneValeur == dictDonnees["ID"] : 
                propriete.SetValue(index)
                break
            if dictUtilisateur != None :
                texte1 = u"%s %s" % (dictUtilisateur["prenom"], dictUtilisateur["nom"])
                texte2 = u"%s %s" % (dictUtilisateur["nom"], dictUtilisateur["prenom"])
                if dictDonnees["nom"].lower() == texte1.lower() or dictDonnees["nom"].lower() == texte2.lower() :
                    propriete.SetValue(index)
        
    def GetInfosSignataire(self):
        propriete = self.GetPropertyByName("signataire")
        index = propriete.GetValue()
        if index == None or (index in self.dictDonnees["signataires"]) == False : 
            return None
        return self.dictDonnees["signataires"][index]
        
    def OnBoutonParametres(self, propriete=None):
        ancienneValeur = propriete.GetValue()
        if propriete.GetName() == "IDmodele" :
            from Dlg import DLG_Modeles_docs
            dlg = DLG_Modeles_docs.Dialog(self, categorie="attestation")
            dlg.ShowModal() 
            dlg.Destroy()
            self.MAJ_modeles()         
        propriete.SetValue(ancienneValeur)


    def OnPropGridChange(self, event):
        propriete = event.GetProperty()
        if propriete.GetName() == "intitules" and self.GetGrandParent().GetName() == "DLG_Attestations_selection" :
            self.GetGrandParent().ctrl_attestations.typeLabel = propriete.GetValue() 
            self.GetGrandParent().ctrl_attestations.MAJ() 




# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, listeActivites=[]):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
                
        # Paramètres
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options d'impression"))
        self.ctrl_parametres = CTRL_Parametres(self, listeActivites=listeActivites)
        self.ctrl_parametres.Importation() 
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)
        self.ctrl_parametres.SetMinSize((440, 120)) 
                
        self.__do_layout()
        

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=20)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        # Paramètres
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_reinitialisation, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_sauvegarde, 0, 0, 0)

        grid_sizer_parametres.Add(grid_sizer_boutons, 0, 0, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_options.Add(grid_sizer_parametres, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(box_options, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
                                    
    def MemoriserParametres(self):
        self.ctrl_parametres.Sauvegarde() 
    
    def GetOptions(self):
        dictOptions = {} 

        # Récupération des paramètres
        if self.ctrl_parametres.Validation() == False :
            return False
        for nom, valeur in self.ctrl_parametres.GetValeurs().items()  :
            dictOptions[nom] = valeur
        
        return dictOptions


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------






class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)        
        self.ctrl = CTRL(panel, listeActivites = [1, 2, 3, 4, 5])
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        pass

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


