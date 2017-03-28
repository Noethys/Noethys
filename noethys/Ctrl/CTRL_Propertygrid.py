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
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_heure
import sys
import datetime
import wx.propgrid as wxpg

import GestionDB
from Utils import UTILS_Dates
from Utils import UTILS_Parametres
import copy






class EditeurChoix(wxpg.PyChoiceEditor):
    def __init__(self):
        wxpg.PyChoiceEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, size):
        ctrl = self.CallSuperMethod("CreateControls", propGrid, property, pos, size)
        self.SetControlIntValue(property, ctrl, 0)
        return ctrl

    def UpdateControl(self, property, ctrl):
        self.SetControlStringValue(property, ctrl, property.GetDisplayedString())



class Propriete_choix(wxpg.PyProperty):
    """ Simple liste de choix """
    def __init__(self, label, name=wxpg.LABEL_AS_NAME, liste_choix=[], valeur=None):
        self.liste_choix = liste_choix
        wxpg.PyProperty.__init__(self, label, name)
        self.SetChoices([x[1] for x in self.liste_choix])
        if valeur != None:
            self.SetValue(valeur)

    def GetClassName(self):
        return "Propriete_choix"

    def GetEditor(self):
        return "Choice"

    def ValueToString(self, value, flags):
        for id, label in self.liste_choix:
            if id == value:
                return label
        return ""

    def IntToValue(self, index, flags):
        try:
            valeur = self.liste_choix[index][0]
            return (True, valeur)
        except:
            return False


# ---------------------------------------------------------------------------------------------------------------

class Propriete_multichoix(wxpg.PyArrayStringProperty):
    """ Propriété Multichoix """
    def __init__(self, label, name = wxpg.LABEL_AS_NAME, liste_choix=[], liste_selections=[]):
        self.liste_choix = liste_choix
        self.liste_selections = liste_selections

        # Initialisation
        wxpg.PyArrayStringProperty.__init__(self, label, name)

        # Set default delimiter
        self.SetAttribute("Delimiter", ',')

        # Importation des sélections
        self.SetValue(self.liste_selections)

    def GetEditor(self):
        return "TextCtrlAndButton"

    def ValueToString(self, value, flags):
        return self.m_display

    def OnSetValue(self):
        self.GenerateValueAsString()

    def DoSetAttribute(self, name, value):
        # Proper way to call same method from super class
        retval = self.CallSuperMethod("DoSetAttribute", name, value)

        # Must re-generate cached string when delimiter changes
        if name == "Delimiter":
            self.GenerateValueAsString(delim=value)

        return retval

    def GenerateValueAsString(self, delim=None):
        """ This function creates a cached version of displayed text (self.m_display). """
        if not delim:
            delim = self.GetAttribute("Delimiter")
            if not delim:
                delim = ','

        selections = self.GetValue()
        ls = [x[1] for x in self.liste_choix if x[0] in selections]
        if delim == '"' or delim == "'":
            text = ' '.join(['%s%s%s'%(delim,a,delim) for a in ls])
        else:
            text = ', '.join(ls)
        self.m_display = text

    def StringToValue(self, text, argFlags):
        """ If failed, return False or (False, None). If success, return tuple (True, newValue) """
        delim = self.GetAttribute("Delimiter")
        if delim == '"' or delim == "'":
            # Proper way to call same method from super class
            return self.CallSuperMethod("StringToValue", text, 0)
        valeurs_saisies = [a.strip() for a in text.split(delim)]
        liste_id = []
        for valeur in valeurs_saisies :
            found = False
            for id, label in self.liste_choix :
                if valeur.lower() == label.lower() :
                    liste_id.append(id)
                    found = True
            if not found :
                liste_id = self.m_value
                break
        return (True, liste_id)

    def OnEvent(self, propgrid, primaryEditor, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            dlg = wx.MultiChoiceDialog(propgrid, _(u"Cochez les éléments à sélectionner :"), _(u"Sélection"), [x[1] for x in self.liste_choix])
            liste_index = []
            index = 0
            for id, valeur in self.liste_choix :
                if id in self.m_value :
                    liste_index.append(index)
                index += 1
            dlg.SetSelections(liste_index)
            if dlg.ShowModal() == wx.ID_OK:
                liste_id = []
                for index in dlg.GetSelections() :
                    liste_id.append(self.liste_choix[index][0])
                self.SetValueInEvent(liste_id)
                retval = True
            else:
                retval = False
            dlg.Destroy()
            return retval
        return False



# -------------------------------------------------------------------------------------------------

class Propriete_liste(wxpg.PyArrayStringProperty):
    """ Propriété Multichoix """
    def __init__(self, label, name = wxpg.LABEL_AS_NAME, type_donnees=int, liste_selections=[]):
        self.type_donnees = type_donnees
        self.liste_selections = liste_selections

        # Initialisation
        wxpg.PyArrayStringProperty.__init__(self, label, name)

        # Set default delimiter
        self.SetAttribute("Delimiter", ',')

        # Importation des sélections
        self.SetValue(self.liste_selections)

    def GetEditor(self):
        return "TextCtrl"

    def ValueToString(self, value, flags):
        return self.m_display

    def OnSetValue(self):
        self.GenerateValueAsString()

    def DoSetAttribute(self, name, value):
        # Proper way to call same method from super class
        retval = self.CallSuperMethod("DoSetAttribute", name, value)

        # Must re-generate cached string when delimiter changes
        if name == "Delimiter":
            self.GenerateValueAsString(delim=value)

        return retval

    def GenerateValueAsString(self, delim=None):
        """ This function creates a cached version of displayed text (self.m_display). """
        if not delim:
            delim = self.GetAttribute("Delimiter")
            if not delim:
                delim = ','

        ls = [unicode(x) for x in self.GetValue()]
        if delim == '"' or delim == "'":
            text = ' '.join(['%s%s%s'%(delim,a,delim) for a in ls])
        else:
            text = ', '.join(ls)
        self.m_display = text

    def StringToValue(self, text, argFlags):
        """ If failed, return False or (False, None). If success, return tuple (True, newValue) """
        delim = self.GetAttribute("Delimiter")
        if delim == '"' or delim == "'":
            # Proper way to call same method from super class
            return self.CallSuperMethod("StringToValue", text, 0)
        valeurs_saisies = [a.strip() for a in text.split(delim)]
        liste_id = []
        if valeurs_saisies != ["",] :
            for valeur in valeurs_saisies :
                try :
                    liste_id.append(self.type_donnees(valeur))
                except :
                    liste_id = self.m_value
                    break
        return (True, liste_id)




# -------------------------------------------------------------------------------------------------

class EditeurComboBoxAvecBoutons(wxpg.PyChoiceEditor):
    def __init__(self):
        wxpg.PyChoiceEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        # Create and populate buttons-subwindow
        buttons = wxpg.PGMultiButton(propGrid, sz)

        # Add two regular buttons
        buttons.AddBitmapButton(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        buttons.GetButton(0).SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des paramètres"))
        
        # Create the 'primary' editor control (textctrl in this case)
        wnd = self.CallSuperMethod("CreateControls", propGrid, property, pos, buttons.GetPrimarySize())
        buttons.Finalize(propGrid, pos);
        self.buttons = buttons
        return (wnd, buttons)

    def OnEvent(self, propGrid, prop, ctrl, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            buttons = self.buttons
            evtId = event.GetId()
            if evtId == buttons.GetButtonId(0):
                propGrid.GetPanel().OnBoutonParametres(prop)

        return self.CallSuperMethod("OnEvent", propGrid, prop, ctrl, event)


# ------------------------------------------------------------------------------------------------------

class EditeurHeure(wxpg.PyEditor):
    def __init__(self):
        wxpg.PyEditor.__init__(self)

    def CreateControls(self, propgrid, property, pos, size):
        try:
            ctrl = CTRL_Saisie_heure.Heure(propgrid.GetPanel(), id=wxpg.PG_SUBID1, pos=pos, size=size, style=wx.TE_PROCESS_ENTER)
            ctrl.SetHeure(property.GetDisplayedString())
            return ctrl
        except:
            import traceback
            print(traceback.print_exc())

    def UpdateControl(self, property, ctrl):
        ctrl.SetHeure(property.GetDisplayedString())

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            dc.DrawText(property.GetDisplayedString(), rect.x+5, rect.y)

    def OnEvent(self, propgrid, property, ctrl, event):
        if not ctrl:
            return False

        evtType = event.GetEventType()

        if evtType == wx.wxEVT_COMMAND_TEXT_ENTER:
            if propgrid.IsEditorsValueModified():
                return True
        elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
            event.Skip()
            event.SetId(propgrid.GetId())
            propgrid.EditorsValueWasModified()
            return False

        return False

    def GetValueFromControl(self, property, ctrl):
        valeur = ctrl.GetHeure()
        if ctrl.Validation() == False :
            valeur = ""

        if property.UsesAutoUnspecified() and not valeur:
            return (True, None)

        res, value = property.StringToValue(valeur, wxpg.PG_EDITABLE_VALUE)

        if not res and value is None:
            res = True

        return (res, value)

    def SetValueToUnspecified(self, property, ctrl):
        ctrl.Remove(0, len(ctrl.GetHeure()))

    def SetControlStringValue(self, property, ctrl, text):
        ctrl.SetHeure(text)

    def OnFocus(self, property, ctrl):
        ctrl.SetSelection(-1,-1)
        ctrl.SetFocus()





# ----------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wxpg.PropertyGrid) :
    def __init__(self, parent, style=wxpg.PG_SPLITTER_AUTO_CENTER):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=style)
        self.parent = parent
        
        # Définition des éditeurs personnalisés
        if not getattr(sys, '_PropGridEditorsRegistered', False):
            self.RegisterEditor(EditeurComboBoxAvecBoutons)
            self.RegisterEditor(EditeurHeure)
            self.RegisterEditor(EditeurChoix)
            # ensure we only do it once
            sys._PropGridEditorsRegistered = True
        
        # Remplissage des valeurs               
##        for nom, listeProprietes in self.listeDonnees :
##            self.Append( wxpg.PropertyCategory(nom) )
##        
##            for dictTemp in listeProprietes :
##                propriete = wxpg.IntProperty(label=dictTemp["label"], name=dictTemp["code"], value=dictTemp["valeur"])
##                self.Append(propriete)
##                self.SetPropertyAttribute(propriete, "Min", 0)
##                self.SetPropertyAttribute(propriete, "Max", 800)
##                self.SetPropertyEditor(propriete, "EditeurAvecBoutons")
        
##        self.SetVerticalSpacing(3) 
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        
        couleurFond = "#e5ecf3"
        self.SetCaptionBackgroundColour(couleurFond)
        self.SetMarginColour(couleurFond)

        self.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange )
        
        # Remplissage du contrôle
        self.Remplissage() 
        
        # Mémorisation des valeurs par défaut
        self.dictValeursDefaut = self.GetPropertyValues()
        
        # Importation des valeurs
        self.Importation() 
        
##        # Bordereau
##        self.Append( wxpg.PropertyCategory(_(u"Bordereau")) )
##        
##        propriete = wxpg.IntProperty(label=_(u"Exercice"), name="exercice", value=datetime.date.today().year)
##        propriete.SetHelpString(_(u"Saisissez l'année de l'exercice")) 
##        self.Append(propriete)
##        self.SetPropertyEditor("exercice", "SpinCtrl")
##        
##        listeMois = [_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]
##        propriete = wxpg.EnumProperty(label=_(u"Mois"), name="mois", labels=listeMois, values=range(1, 13) , value=datetime.date.today().month)
##        propriete.SetHelpString(_(u"Sélectionnez le mois")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Objet"), name="objet_dette", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'objet du bordereau (Ex : 'Centre de Loisirs')")) 
##        self.Append(propriete)
##
##        # Dates
##        self.Append( wxpg.PropertyCategory(_(u"Dates")) )
##        
##        propriete = wxpg.DateProperty(label=_(u"Date d'émission"), name="date_emission", value=wx.DateTime_Now())
##        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
##        self.Append(propriete)
##        
##        propriete = wxpg.DateProperty(label=_(u"Date du prélèvement"), name="date_prelevement", value=wx.DateTime_Now())
##        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
##        self.Append(propriete)
##        
##        propriete = wxpg.DateProperty(label=_(u"Avis d'envoi"), name="date_envoi", value=wx.DateTime_Now())
##        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
##        self.Append(propriete)
##
##        # Collectivité
##        self.Append( wxpg.PropertyCategory(_(u"Identification")) )
##        
##        propriete = wxpg.StringProperty(label=_(u"ID Bordereau"), name="id_bordereau", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'ID du bordereau")) 
##        self.Append(propriete)
####        propriete.SetAttribute("Hint", _(u"Coucou !"))
####        self.SetPropertyCell("id_bordereau", 0, bitmap = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
##        
##        propriete = wxpg.StringProperty(label=_(u"ID Poste"), name="id_poste", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'ID du bordereau")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"ID Collectivité"), name="id_collectivite", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'ID de la collectivité")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Code Collectivité"), name="code_collectivite", value=u"")
##        propriete.SetHelpString(_(u"Saisissez le code Collectivité")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Code Budget"), name="code_budget", value=u"")
##        propriete.SetHelpString(_(u"Saisissez le code Budget")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Code Produit Local"), name="code_prodloc", value=u"")
##        propriete.SetHelpString(_(u"Saisissez le code Produit Local")) 
##        self.Append(propriete)
##
##        # Libellés
##        self.Append( wxpg.PropertyCategory(_(u"Libellés")) )
##
##        propriete = wxpg.StringProperty(label=_(u"Objet de la pièce"), name="objet_piece", value=_(u"FACTURE_NUM{NUM_FACTURE}_{MOIS_LETTRES}_{ANNEE}"))
##        propriete.SetHelpString(_(u"Saisissez l'objet de la pièce (en majuscules et sans accents). Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
##        self.Append(propriete)
##
##        propriete = wxpg.StringProperty(label=_(u"Libellé du prélèvement"), name="prelevement_libelle", value=u"{NOM_ORGANISATEUR} - {OBJET_PIECE}")
##        propriete.SetHelpString(_(u"Saisissez le libellé du prélèvement qui apparaîtra sur le relevé de compte de la famille. Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {OBJET_PIECE} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
##        self.Append(propriete)
##
##        # Règlement automatique
##        self.Append( wxpg.PropertyCategory(_(u"Règlement automatique")) )
##        
##        propriete = wxpg.BoolProperty(label=_(u"Régler automatiquement"), name="reglement_auto", value=False)
##        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys créé un règlement automatiquement pour les prélèvements")) 
##        propriete.SetAttribute("UseCheckbox", True)
##        self.Append(propriete)
##        
##        propriete = wxpg.EnumProperty(label=_(u"Compte à créditer"), name="IDcompte")
##        propriete.SetHelpString(_(u"Sélectionnez le compte bancaire à créditer dans le cadre du règlement automatique"))
##        propriete.SetEditor("EditeurComboBoxAvecBoutons")
##        self.Append(propriete)
##        self.MAJ_comptes() 
##
##        propriete = wxpg.EnumProperty(label=_(u"Mode de règlement"), name="IDmode")
##        propriete.SetHelpString(_(u"Sélectionnez le mode de règlement à utiliser dans le cadre du règlement automatique"))
##        propriete.SetEditor("EditeurComboBoxAvecBoutons")
##        self.Append(propriete)
####        self.MAJ_modes() 
##                            
##                            
##    def MAJ_comptes(self):
##        DB = GestionDB.DB()
##        req = """SELECT IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics
##        FROM comptes_bancaires
##        ORDER BY nom;"""
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        self.dictComptes = {}
##        choix = wxpg.PGChoices()
##        for IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics in listeDonnees :
##            self.dictComptes[IDcompte] = { 
##                "nom" : nom, "numero" : numero, "defaut" : defaut,
##                "raison" : raison, "code_etab" : code_etab, "code_guichet" : code_guichet, 
##                "code_nne" : code_nne, "cle_rib" : cle_rib, "cle_iban" : cle_iban,
##                "iban" : iban, "bic" : bic, "code_ics" : code_ics,
##                }
##            choix.Add(nom, IDcompte)
##        propriete = self.GetPropertyByName("IDcompte")
##        propriete.SetChoices(choix)
##
##    def MAJ_modes(self):
##        DB = GestionDB.DB()
##        req = """SELECT IDmode, label, numero_piece, nbre_chiffres, 
##        frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, image
##        FROM modes_reglements
##        ORDER BY label;"""
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        self.dictModes = {}
##        choix = wxpg.PGChoices()
##        for IDmode, label, numero_piece, nbre_chiffres, frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, image in listeDonnees :
##            self.dictModes[IDmode] = { 
##                "label" : label, "numero_piece" : numero_piece, "nbre_chiffres" : nbre_chiffres,
##                "frais_gestion" : frais_gestion, "frais_montant" : frais_montant, "frais_pourcentage" : frais_pourcentage, 
##                "frais_arrondi" : frais_arrondi, "frais_label" : frais_label, "image" : image,
##                }
##            bmp = OL_Modes_reglements.GetImage(image)
##            choix.Add(label, bmp, IDmode)
##        propriete = self.GetPropertyByName("IDmode")
##        propriete.SetChoices(choix)
##
##
##    def OnBoutonParametres(self, propriete=None):
##        ancienneValeur = propriete.GetValue() 
##        if propriete.GetName() == "compte" :
##            from Dlg import DLG_Comptes_bancaires
##            dlg = DLG_Comptes_bancaires.Dialog(self)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.MAJ_comptes() 
##        if propriete.GetName() == "mode" :
##            from Dlg import DLG_Modes_reglements
##            dlg = DLG_Modes_reglements.Dialog(self)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.MAJ_modes() 
##        
##        propriete.SetValue(ancienneValeur)

    def OnPropGridChange(self, event):
        event.Skip() 
##        propriete = event.GetProperty()
##        if propriete.GetName() == "reglement_auto" :
##            self.parent.ctrl_pieces.reglement_auto = propriete.GetValue()
    
    def Reinitialisation(self, afficher_dlg=True):
        # Demande confirmation
        if afficher_dlg == True :
            dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment réinitialiser tous les paramètres ?"), _(u"Paramètres par défaut"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Réinitialisation
        for nom, valeur in self.dictValeursDefaut.iteritems() :
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "reinitialisation_interdite") != True :
                propriete.SetValue(valeur)



##    def Sauvegarde(self):
##        # Récupération des noms et valeurs par défaut du contrôle
##        dictValeurs = copy.deepcopy(self.GetPropertyValues())
##        # Sauvegarde des valeurs
##        UTILS_Parametres.ParametresCategorie(mode="set", categorie="impression_facture", dictParametres=dictValeurs)



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Bouton_reinitialisation(wx.BitmapButton):
    def __init__(self, parent, ctrl_parametres=None):
        wx.BitmapButton.__init__(self, parent, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_parametres = ctrl_parametres
        self.SetToolTipString(_(u"Cliquez ici pour réinitialiser tous les paramètres"))
        self.Bind(wx.EVT_BUTTON, self.OnBouton)
    
    def OnBouton(self, event):
        self.ctrl_parametres.Reinitialisation() 

class Bouton_sauvegarde(wx.BitmapButton):
    def __init__(self, parent, ctrl_parametres=None):
        wx.BitmapButton.__init__(self, parent, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Sauvegarder.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_parametres = ctrl_parametres
        self.SetToolTipString(_(u"Cliquez ici pour mémoriser tous les paramètres"))
        self.Bind(wx.EVT_BUTTON, self.OnBouton)
    
    def OnBouton(self, event):
        self.ctrl_parametres.Sauvegarde(forcer=True) 


# --------------------------------------- TESTS ----------------------------------------------------------------------------------------


class CTRL_TEST(CTRL) :
    def __init__(self, parent):
        CTRL.__init__(self, parent)
    
    def Remplissage(self):

        # Catégorie
        self.Append( wxpg.PropertyCategory(_(u"Tests")) )

        # CTRL Heure
        propriete = wxpg.StringProperty(label=_(u"Heure"), name="heure")
        propriete.SetHelpString(_(u"Sélectionnez une heure"))
        propriete.SetEditor("EditeurHeure")
        self.Append(propriete)

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Mémorisation")) )
        
        # Mémorisation des paramètres
        propriete = wxpg.EnumProperty(label=_(u"Mémoriser les paramètres"), name="memoriser_parametres", labels=[_(u"Non"), _(u"Uniquement sur cet ordinateur"), _(u"Pour tous les ordinateurs")], values=[0, 1, 3] , value=3)
        propriete.SetHelpString(_(u"Mémoriser les paramètres")) 
        self.Append(propriete)

        # Répertoire de sauvegarde
        propriete = wxpg.DirProperty(label=_(u"Répertoire pour copie unique"), name="repertoire_copie", value="")
        propriete.SetHelpString(_(u"Enregistrer une copie unique de chaque document dans le répertoire sélectionné")) 
        self.Append(propriete)

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Eléments à afficher")) )
        
        # Afficher les coupons-réponse
        propriete = wxpg.BoolProperty(label=_(u"Afficher le coupon-réponse"), name="coupon_reponse", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher un coupon-réponse dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        # Afficher les messages
        propriete = wxpg.BoolProperty(label=_(u"Afficher les messages"), name="messages", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher les messages dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher le rappel des impayés
        propriete = wxpg.BoolProperty(label=_(u"Afficher le rappel des impayés"), name="impayes", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher le rappel des impayés dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher les codes-barres
        propriete = wxpg.BoolProperty(label=_(u"Afficher les codes-barres"), name="codes_barres", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher les codes-barres dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        # Afficher les avis de prélèvements
        propriete = wxpg.BoolProperty(label=_(u"Afficher les avis de prélèvements"), name="avis_prelevements", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher les avis de prélèvements dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Titre")) )

        # Afficher le titre
        propriete = wxpg.BoolProperty(label=_(u"Afficher le titre"), name="afficher_titre", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher le titre du le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Titre du document"), name="titre_document", value=_(u"Facture"))
        propriete.SetHelpString(_(u"Saisissez le titre du document (Par défaut 'Facture')")) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte du titre"), name="taille_texte_titre", value=19)
        propriete.SetHelpString(_(u"Saisissez la taille de texte du titre (29 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_titre", "SpinCtrl")
        
        propriete = wxpg.BoolProperty(label=_(u"Afficher la période de facturation"), name="afficher_periode", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher la période de facturation dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de la période"), name="taille_texte_periode", value=8)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de la période (8 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_periode", "SpinCtrl")

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Tableau des prestations")) )

        # Affichage condensé ou détaillé
        propriete = wxpg.EnumProperty(label=_(u"Affichage des prestations"), name="affichage_prestations", labels=[_(u"Détaillé"), _(u"Condensé")], values=[0, 1] , value=0)
        propriete.SetHelpString(_(u"Sélectionnez un type d'affichage")) 
        self.Append(propriete)

        # Intitulés des prestations
        labels = [_(u"Intitulé original"), _(u"Intitulé original + état 'Absence injustifiée'"), _(u"Nom du tarif"), _(u"Nom de l'activité")]
        propriete = wxpg.EnumProperty(label=_(u"Intitulés des prestations"), name="intitules", labels=labels, values=[0, 1, 2, 3] , value=0)
        propriete.SetHelpString(_(u"Sélectionnez le type d'intitulé à afficher pour les prestations")) 
        self.Append(propriete)
        
        # Couleur 1
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 1"), name="couleur_fond_1", value=wx.Colour(255, 0, 0) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur 1")) 
        self.Append(propriete)
        
        # Couleur 2
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 2"), name="couleur_fond_2", value=wx.Colour(255, 0, 0) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur 2")) 
        self.Append(propriete)
        
        # Largeur colonne Date
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Date (ou Qté)"), name="largeur_colonne_date", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Date (50 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_date", "SpinCtrl")
        
        # Largeur colonne Montant HT
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant HT"), name="largeur_colonne_montant_ht", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant HT (50 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_ht", "SpinCtrl")

        # Largeur colonne Montant TVA
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant TVA"), name="largeur_colonne_montant_tva", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant TVA (50 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_tva", "SpinCtrl")

        # Largeur colonne Montant TTC
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant TTC"), name="largeur_colonne_montant_ttc", value=70)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant TTC (70 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_ttc", "SpinCtrl")
        
        # Taille de texte du nom de l'individu
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de l'individu"), name="taille_texte_individu", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de l'individu (9 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_individu", "SpinCtrl")

        # Taille de texte du nom de l'activité
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de l'activité"), name="taille_texte_activite", value=6)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de l'activité (6 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_activite", "SpinCtrl")

        # Taille de texte des noms de colonnes
        propriete = wxpg.IntProperty(label=_(u"Taille de texte des noms de colonnes"), name="taille_texte_noms_colonnes", value=5)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des noms de colonnes (5 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_noms_colonnes", "SpinCtrl")

        # Taille de texte des prestations
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de des prestations"), name="taille_texte_prestation", value=7)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des prestations (7 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_prestation", "SpinCtrl")
        
        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"Autres textes")) )

        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name="texte_introduction", value=u"")
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction (Aucun par défaut)")) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte d'introduction"), name="taille_texte_introduction", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte d'introduction (9 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_introduction", "SpinCtrl")

        propriete = wxpg.LongStringProperty(label=_(u"Texte de conclusion"), name="texte_conclusion", value=u"")
        propriete.SetHelpString(_(u"Saisissez un texte de conclusion (Aucun par défaut)")) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte de conclusion"), name="taille_texte_conclusion", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de conclusion (9 par défaut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_conclusion", "SpinCtrl")
        
    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
##        for nom, valeur in dictValeurs.iteritems() :
##            print (nom, valeur, str(type(valeur)))
        # Recherche les paramètres mémorisés
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="impression_facture", dictParametres=dictValeurs)
        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.iteritems() :
            propriete = self.GetPropertyByName(nom)
            print propriete
            ancienneValeur = propriete.GetValue() 
            propriete.SetValue(valeur)
    
    def Sauvegarde(self):
        """ Mémorisation des valeurs du contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        # Sauvegarde des valeurs
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="impression_facture", dictParametres=dictValeurs)
        
        
        
        
        
    def GetDictValeurs(self) :
        return self.GetPropertyValues()
        

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL_TEST(panel)
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        self.bouton_reinit = Bouton_reinitialisation(panel, self.ctrl)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_reinit, 0, wx.ALL|wx.EXPAND, 4)
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
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 600))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

