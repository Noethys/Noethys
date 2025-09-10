#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ctrl import CTRL_Saisie_heure
from Ctrl import CTRL_Saisie_date
import sys
import datetime
import wx.propgrid as wxpg
import six
import GestionDB
from Utils import UTILS_Dates
from Utils import UTILS_Parametres
import copy

if 'phoenix' in wx.PlatformInfo:
    from wx.propgrid import PG_LABEL as NAME
    from wx.propgrid import PGChoiceEditor as ChoiceEditor
    from wx.propgrid import PGEditor as Editor
    from wx.propgrid import PGProperty as Property
    from wx.propgrid import ArrayStringProperty as ArrayStringProperty
else:
    from wx.propgrid import LABEL_AS_NAME as NAME
    from wx.propgrid import PyChoiceEditor as ChoiceEditor
    from wx.propgrid import PyEditor as Editor
    from wx.propgrid import PyProperty as Property
    from wx.propgrid import PyArrayStringProperty as ArrayStringProperty



class Propriete_date(wxpg.PyProperty):
    def __init__(self, label, name=NAME, value=None):
        wxpg.PyProperty.__init__(self, label, name)
        self.SetValue(value)

    def GetClassName(self):
        return self.__class__.__name__

    def GetEditor(self):
        return "TextCtrl"

    def ValueToString(self, value, flags):
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            return value.strftime("%d/%m/%Y")
        return ""

    def StringToValue(self, s, flags):
        if not s:
            return (True, None)
        try:
            date = datetime.datetime.strptime(s, "%d/%m/%Y")
        except:
            return (False, None)
        return (True, date)


class EditeurChoix(ChoiceEditor):
    def __init__(self):
        ChoiceEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, size):
        if 'phoenix' in wx.PlatformInfo:
            ctrl = super(EditeurChoix, self).CreateControls(propGrid, property, pos, size)
            try:
                ctrl = ctrl.GetPrimary()
            except:
                ctrl = ctrl.m_primary
            self.SetControlIntValue(property, ctrl, 0)
            return wxpg.PGWindowList(ctrl)
        else :
            ctrl = self.CallSuperMethod("CreateControls", propGrid, property, pos, size)
            self.SetControlIntValue(property, ctrl, 0)
            return ctrl

    def UpdateControl(self, property, ctrl):
        self.SetControlStringValue(property, ctrl, property.GetDisplayedString())



class Propriete_choix(Property):
    """ Simple liste de choix """
    def __init__(self, label, name=NAME, liste_choix=[], valeur=None):
        self.liste_choix = liste_choix
        Property.__init__(self, label, name)
        if 'phoenix' in wx.PlatformInfo:
            choix = wxpg.PGChoices([x[1] for x in self.liste_choix])
        else :
            choix = [x[1] for x in self.liste_choix]
        self.SetChoices(choix)
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

class Propriete_multichoix(ArrayStringProperty):
    """ Propriété Multichoix """
    def __init__(self, label, name = NAME, liste_choix=[], liste_selections=[]):
        self.liste_choix = liste_choix
        self.liste_selections = liste_selections

        # Initialisation
        ArrayStringProperty.__init__(self, label, name)

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
        if 'phoenix' in wx.PlatformInfo:
            retval = super(Propriete_multichoix, self).DoSetAttribute(name, value)
        else:
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
            if 'phoenix' in wx.PlatformInfo:
                return super(Propriete_multichoix, self).StringToValue(text, 0)
            else:
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
            dlg = wx.MultiChoiceDialog(propgrid, _(u"Cochez les éléments à sélectionner :"), _(u"sélection"), [x[1] for x in self.liste_choix])
            liste_index = []
            index = 0
            for id, valeur in self.liste_choix :
                if id in (self.m_value or []):
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

class Propriete_liste(ArrayStringProperty):
    """ Propriété Multichoix """
    def __init__(self, label, name = NAME, type_donnees=int, liste_selections=[]):
        self.type_donnees = type_donnees
        self.liste_selections = liste_selections

        # Initialisation
        ArrayStringProperty.__init__(self, label, name)

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
        if 'phoenix' in wx.PlatformInfo:
            return False

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

        ls = [six.text_type(x) for x in self.GetValue()]
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

class EditeurComboBoxAvecBoutons(ChoiceEditor):
    def __init__(self):
        ChoiceEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        # Create and populate buttons-subwindow
        buttons = wxpg.PGMultiButton(propGrid, sz)

        # Add two regular buttons
        buttons.AddBitmapButton(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        buttons.GetButton(0).SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des paramêtres")))
        
        # Create the 'primary' editor control (textctrl in this case)
        if 'phoenix' in wx.PlatformInfo:
            wnd = super(EditeurComboBoxAvecBoutons, self).CreateControls(propGrid, property, pos, buttons.GetPrimarySize())
            try:
                wnd = wnd.GetPrimary()
            except:
                wnd = wnd.m_primary
            buttons.Finalize(propGrid, pos)
            self.buttons = buttons
            return wxpg.PGWindowList(wnd, buttons)
        else :
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

        if 'phoenix' in wx.PlatformInfo:
            return super(EditeurComboBoxAvecBoutons, self).OnEvent(propGrid, prop, ctrl, event)
        else :
            return self.CallSuperMethod("OnEvent", propGrid, prop, ctrl, event)

# ------------------------------------------------------------------------------------------------------

class EditeurHeure(Editor):
    def __init__(self):
        Editor.__init__(self)

    def CreateControls(self, propgrid, property, pos, size):
        try:
            ctrl = CTRL_Saisie_heure.Heure(propgrid.GetPanel(), id=wxpg.PG_SUBID1, pos=pos, size=size, style=wx.TE_PROCESS_ENTER)
            ctrl.SetHeure(property.GetDisplayedString())
            if 'phoenix' in wx.PlatformInfo:
                return wxpg.PGWindowList(ctrl)
            else :
                return ctrl
        except:
            import traceback
            print((traceback.print_exc()))

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
        ctrl.SetSelection(-1, -1)
        ctrl.SetFocus()




# ------------------------------------------------------------------------------------------------------

class EditeurDate(Editor):
    def __init__(self):
        Editor.__init__(self)

    def CreateControls(self, propgrid, property, pos, size):
        try:
            ctrl = CTRL_Saisie_date.Date2(propgrid.GetPanel(), pos=pos, size=(-1, 25))
            ctrl.SetDate(property.GetDisplayedString())
            if 'phoenix' in wx.PlatformInfo:
                return wxpg.PGWindowList(ctrl)
            else :
                return ctrl
        except:
            import traceback
            print((traceback.print_exc()))

    def UpdateControl(self, property, ctrl):
        ctrl.SetDate(property.GetDisplayedString())

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
        valeur = ctrl.GetDate()
        if ctrl.Validation() == False :
            valeur = ""

        if property.UsesAutoUnspecified() and not valeur:
            return (True, None)

        #res, value = property.StringToValue(valeur, wxpg.PG_EDITABLE_VALUE)
        res, value = True, valeur
        if not res and value is None:
            res = True

        return (res, value)

    def SetValueToUnspecified(self, property, ctrl):
        ctrl.Remove(0, len(ctrl.GetDate()))

    def SetControlStringValue(self, property, ctrl, text):
        ctrl.SetDate(text)

    def OnFocus(self, property, ctrl):
        ctrl.SetSelection(-1, -1)
        ctrl.SetFocus()


# ----------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wxpg.PropertyGrid) :
    def __init__(self, parent, style=wxpg.PG_SPLITTER_AUTO_CENTER):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=style)
        self.parent = parent
        
        # définition des éditeurs personnalisés
        if not getattr(sys, '_PropGridEditorsRegistered', False):
            self.RegisterEditor(EditeurComboBoxAvecBoutons)
            self.RegisterEditor(EditeurHeure)
            self.RegisterEditor(EditeurDate)
            self.RegisterEditor(EditeurChoix)
            # ensure we only do it once
            sys._PropGridEditorsRegistered = True
        
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        
        couleurFond = "#e5ecf3"
        self.SetCaptionBackgroundColour(couleurFond)
        self.SetMarginColour(couleurFond)

        self.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange )
        
        # Remplissage du contrôle
        self.Remplissage() 
        
        # mémorisation des valeurs par défaut
        self.dictValeursDefaut = self.GetPropertyValues()
        
        # Importation des valeurs
        self.Importation() 
        

    def OnPropGridChange(self, event):
        event.Skip() 

    def Reinitialisation(self, afficher_dlg=True):
        # Demande confirmation
        if afficher_dlg == True :
            dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment réinitialiser tous les paramêtres ?"), _(u"Paramêtres par défaut"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        # Réinitialisation
        for nom, valeur in self.dictValeursDefaut.items() :
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "reinitialisation_interdite") != True :
                propriete.SetValue(valeur)

    def GetParametres(self):
        return copy.deepcopy(self.GetPropertyValues())




# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Bouton_reinitialisation(wx.BitmapButton):
    def __init__(self, parent, ctrl_parametres=None):
        wx.BitmapButton.__init__(self, parent, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_parametres = ctrl_parametres
        self.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réinitialiser tous les paramêtres")))
        self.Bind(wx.EVT_BUTTON, self.OnBouton)
    
    def OnBouton(self, event):
        self.ctrl_parametres.Reinitialisation() 

class Bouton_sauvegarde(wx.BitmapButton):
    def __init__(self, parent, ctrl_parametres=None):
        wx.BitmapButton.__init__(self, parent, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Sauvegarder.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_parametres = ctrl_parametres
        self.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour mémoriser tous les paramêtres")))
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
        propriete.SetHelpString(_(u"sélectionnez une heure"))
        propriete.SetEditor("EditeurHeure")
        self.Append(propriete)

        # CTRL Date
        propriete = wxpg.StringProperty(label=_(u"Date"), name="date", value=UTILS_Dates.DateDDEnFr(datetime.date.today()))
        propriete.SetHelpString(_(u"sélectionnez une date"))
        propriete.SetEditor("EditeurDate")
        self.Append(propriete)

        # Catégorie 
        self.Append( wxpg.PropertyCategory(_(u"mémorisation")) )
        
        # mémorisation des paramêtres
        propriete = wxpg.EnumProperty(label=_(u"mémoriser les paramêtres"), name="memoriser_parametres", labels=[_(u"Non"), _(u"Uniquement sur cet ordinateur"), _(u"Pour tous les ordinateurs")], values=[0, 1, 3] , value=3)
        propriete.SetHelpString(_(u"mémoriser les paramêtres")) 
        self.Append(propriete)

        # Répertoire de sauvegarde
        if 'phoenix' in wx.PlatformInfo:
            propriete = wxpg.DirProperty(name=_(u"Répertoire pour copie unique"), label="repertoire_copie", value="")
        else:
            propriete = wxpg.DirProperty(label=_(u"Répertoire pour copie unique"), name="repertoire_copie", value="")
        propriete.SetHelpString(_(u"Enregistrer une copie unique de chaque document dans le Répertoire sélectionné")) 
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

        # Affichage condensé ou Détaillné
        propriete = wxpg.EnumProperty(label=_(u"Affichage des prestations"), name="affichage_prestations", labels=[_(u"Détaillné"), _(u"Condensé")], values=[0, 1] , value=0)
        propriete.SetHelpString(_(u"sélectionnez un type d'affichage")) 
        self.Append(propriete)

        # intitulés des prestations
        labels = [_(u"intitulé original"), _(u"intitulé original + état 'Absence injustifinée'"), _(u"Nom du tarif"), _(u"Nom de l'activité")]
        propriete = wxpg.EnumProperty(label=_(u"intitulés des prestations"), name="intitules", labels=labels, values=[0, 1, 2, 3] , value=0)
        propriete.SetHelpString(_(u"sélectionnez le type d'intitulé à afficher pour les prestations")) 
        self.Append(propriete)
        
        # Couleur 1
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 1"), name="couleur_fond_1", value=wx.Colour(255, 0, 0) )
        propriete.SetHelpString(_(u"sélectionnez la couleur 1")) 
        self.Append(propriete)
        
        # Couleur 2
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 2"), name="couleur_fond_2", value=wx.Colour(255, 0, 0) )
        propriete.SetHelpString(_(u"sélectionnez la couleur 2")) 
        self.Append(propriete)
        
        # Largeur colonne Date
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Date (ou Qtné)"), name="largeur_colonne_date", value=50)
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
        # Recherche les paramêtres mémorisés
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="impression_facture", dictParametres=dictValeurs)
        # Envoie les paramêtres dans le contrôle
        for nom, valeur in dictParametres.items() :
            propriete = self.GetPropertyByName(nom)
            # propriete
            ancienneValeur = propriete.GetValue() 
            propriete.SetValue(valeur)
    
    def Sauvegarde(self):
        """ mémorisation des valeurs du contrôle """
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

