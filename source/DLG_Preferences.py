#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import shelve
import CTRL_Bandeau

import GestionDB
import UTILS_Config
import UTILS_Utilisateurs




# ---------------------------------------------------------------------------------------------------------------------------

class Langue(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.listeLangues = [u"Français (par défaut)",]
        self.listeCodes = [None,]
        
        # Recherche des langues disponibles
        listeFichiers = os.listdir("Lang/") 
        for nomFichier in listeFichiers :
            if nomFichier.endswith("lang") :
                code, extension = nomFichier.split(".")
                fichier = shelve.open("Lang/" + nomFichier, "r")
                dictInfos = fichier["###INFOS###"]
                nom = dictInfos["nom_langue"]
                code = dictInfos["code_langue"]
                fichier.close()
                
                if code not in self.listeCodes :
                    self.listeCodes.append(code)
                    self.listeLangues.append(nom)
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Langue interface*"))
        self.label_langue = wx.StaticText(self, -1, _(u"Langue :"))
        self.ctrl_langue = wx.Choice(self, -1, choices=self.listeLangues)

        self.__set_properties()
        self.__do_layout()
        
        self.ctrl_langue.SetSelection(0)
        self.Importation() 

    def __set_properties(self):
        self.ctrl_langue.SetToolTipString(_(u"Sélectionnez la langue de l'interface parmi les langues disponibles dans la liste. Redémarrez le logiciel pour appliquer la modification."))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_langue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_langue, 1, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(1)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        code = UTILS_Config.GetParametre("langue_interface", None)
        index = 0
        for codeTemp in self.listeCodes :
            if codeTemp == code :
                self.ctrl_langue.SetSelection(index)
            index += 1
            
    def Validation(self):
        return True
    
    def Sauvegarde(self):
        code = self.listeCodes[self.ctrl_langue.GetSelection()]
        UTILS_Config.SetParametre("langue_interface", code)



# ------------------------------------------------------------------------------------------------------------------------

class Monnaie(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Monnaie*"))
        self.label_singulier = wx.StaticText(self, -1, _(u"Nom (singulier) :"))
        self.ctrl_singulier = wx.TextCtrl(self, -1, "")
        self.label_division = wx.StaticText(self, -1, _(u"Unité divisionnaire :"))
        self.ctrl_division = wx.TextCtrl(self, -1, "")
        self.label_pluriel = wx.StaticText(self, -1, _(u"Nom (pluriel) :"))
        self.ctrl_pluriel = wx.TextCtrl(self, -1, "")
        self.label_symbole = wx.StaticText(self, -1, _(u"Symbole :"))
        self.ctrl_symbole = wx.TextCtrl(self, -1, "")

        self.__set_properties()
        self.__do_layout()
        
        self.Importation() 

    def __set_properties(self):
        self.ctrl_singulier.SetToolTipString(_(u"'Euro' par défaut (au singulier)"))
        self.ctrl_division.SetToolTipString(_(u"'Centime' par défaut (au singulier)"))
        self.ctrl_pluriel.SetToolTipString(_(u"'Euros' par défaut (au pluriel)"))
        self.ctrl_symbole.SetMinSize((60, -1))
        self.ctrl_symbole.SetToolTipString(u"'€' par défaut")

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_singulier, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_singulier, 0, wx.EXPAND, 0)
        grid_sizer_base.Add((20, 20), 0, 0, 0)
        grid_sizer_base.Add(self.label_division, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_division, 0, 0, 0)
        grid_sizer_base.Add(self.label_pluriel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_pluriel, 0, wx.EXPAND, 0)
        grid_sizer_base.Add((20, 20), 0, 0, 0)
        grid_sizer_base.Add(self.label_symbole, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_symbole, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(1)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        self.ctrl_singulier.SetValue(UTILS_Config.GetParametre("monnaie_singulier", _(u"Euro")))
        self.ctrl_pluriel.SetValue(UTILS_Config.GetParametre("monnaie_pluriel", _(u"Euros")))
        self.ctrl_division.SetValue(UTILS_Config.GetParametre("monnaie_division", _(u"Centime")))
        self.ctrl_symbole.SetValue(UTILS_Config.GetParametre("monnaie_symbole", u"€"))
    
    def Validation(self):
        singulier = self.ctrl_singulier.GetValue() 
        if len(singulier) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une monnaie (singulier) !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_singulier.SetFocus()
            return False
        
        pluriel = self.ctrl_pluriel.GetValue() 
        if len(pluriel) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une monnaie (pluriel) !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_pluriel.SetFocus()
            return False

        division = self.ctrl_division.GetValue() 
        if len(division) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une monnaie (division) !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_division.SetFocus()
            return False

        symbole = self.ctrl_symbole.GetValue() 
        if len(symbole) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un symbole pour la monnaie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_symbole.SetFocus()
            return False
        
        return True
    
    def Sauvegarde(self):
        singulier = self.ctrl_singulier.GetValue() 
        pluriel = self.ctrl_pluriel.GetValue() 
        division = self.ctrl_division.GetValue() 
        symbole = self.ctrl_symbole.GetValue() 
        
        UTILS_Config.SetParametre("monnaie_singulier", singulier)
        UTILS_Config.SetParametre("monnaie_pluriel", pluriel)
        UTILS_Config.SetParametre("monnaie_division", division)
        UTILS_Config.SetParametre("monnaie_symbole", symbole)


# ------------------------------------------------------------------------------------------------------------------------

class Telephones(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)

        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Numéros de téléphone"))
        self.radio_france = wx.RadioButton(self, -1, _(u"Format français"), style = wx.RB_GROUP)
        self.radio_libre = wx.RadioButton(self, -1, _(u"Format libre"))

        self.__set_properties()
        self.__do_layout()
        
        self.Importation() 

    def __set_properties(self):
        self.radio_france.SetToolTipString(_(u"Format français"))
        self.radio_libre.SetToolTipString(_(u"Format libre"))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.radio_france, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.radio_libre, 0, wx.EXPAND, 0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        mask = UTILS_Config.GetParametre("mask_telephone", "##.##.##.##.##.")
        if mask == "" :
            self.radio_libre.SetValue(True)
        else:
            self.radio_france.SetValue(True)
    
    def Validation(self):
        return True
    
    def Sauvegarde(self):
        if self.radio_france.GetValue() == True :
            mask = "##.##.##.##.##."
        else:
            mask = u""
        UTILS_Config.SetParametre("mask_telephone", mask)

# ------------------------------------------------------------------------------------------------------------------------

class Codes_postaux(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)

        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Codes postaux"))
        self.radio_france = wx.RadioButton(self, -1, _(u"Format français"), style = wx.RB_GROUP)
        self.radio_libre = wx.RadioButton(self, -1, _(u"Format libre"))

        self.__set_properties()
        self.__do_layout()
        
        self.Importation() 

    def __set_properties(self):
        self.radio_france.SetToolTipString(_(u"Format français"))
        self.radio_libre.SetToolTipString(_(u"Format libre"))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.radio_france, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.radio_libre, 0, wx.EXPAND, 0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        mask = UTILS_Config.GetParametre("mask_cp", "#####")
        if mask == "" :
            self.radio_libre.SetValue(True)
        else:
            self.radio_france.SetValue(True)
    
    def Validation(self):
        return True
    
    def Sauvegarde(self):
        if self.radio_france.GetValue() == True :
            mask = "#####"
        else:
            mask = u""
        UTILS_Config.SetParametre("mask_cp", mask)

# ---------------------------------------------------------------------------------------------------------------------------

class Adresses(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)

        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Adresses"))
        self.check_autoComplete = wx.CheckBox(self, -1, _(u"Auto-complétion des villes et codes postaux"))

        self.__set_properties()
        self.__do_layout()
        
        self.Importation() 

    def __set_properties(self):
        self.check_autoComplete.SetToolTipString(_(u"Activation de l'auto-complétion"))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.check_autoComplete, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        autoComplete = UTILS_Config.GetParametre("adresse_autocomplete", True)
        self.check_autoComplete.SetValue(autoComplete)
    
    def Validation(self):
        return True
    
    def Sauvegarde(self):
        UTILS_Config.SetParametre("adresse_autocomplete", self.check_autoComplete.GetValue())

# ---------------------------------------------------------------------------------------------------------------------------

class Rapport_bugs(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)

        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Rapports de bugs"))
        self.check = wx.CheckBox(self, -1, _(u"Affichage du rapport de bugs lorsqu'une erreur est rencontrée"))

        self.__set_properties()
        self.__do_layout()
        
        self.Importation() 

    def __set_properties(self):
        self.check.SetToolTipString(_(u"Affichage du rapport de bugs lorsqu'une erreur est rencontrée"))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.check, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        valeur = UTILS_Config.GetParametre("rapports_bugs", True)
        self.check.SetValue(valeur)
    
    def Validation(self):
        return True
    
    def Sauvegarde(self):
        UTILS_Config.SetParametre("rapports_bugs", self.check.GetValue())

# ---------------------------------------------------------------------------------------------------------------------------

class Propose_maj(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)

        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Mises à jour internet"))
        self.check = wx.CheckBox(self, -1, _(u"Propose le téléchargement des mises à jour à l'ouverture du logiciel"))

        self.__set_properties()
        self.__do_layout()
        
        self.Importation() 

    def __set_properties(self):
        self.check.SetToolTipString(_(u"Propose le téléchargement des mises à jour à l'ouverture du logiciel"))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.check, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        valeur = UTILS_Config.GetParametre("propose_maj", True)
        self.check.SetValue(valeur)
    
    def Validation(self):
        return True
    
    def Sauvegarde(self):
        UTILS_Config.SetParametre("propose_maj", self.check.GetValue())

# ---------------------------------------------------------------------------------------------------------------------------

class DerniersFichiers(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)

        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Liste des derniers fichiers ouverts"))
        self.label_nbre = wx.StaticText(self, -1, _(u"Nombre de fichiers affichés :"))
        self.ctrl_nbre = wx.SpinCtrl(self, -1)
        self.ctrl_nbre.SetRange(1, 20)
        self.bouton_purge = wx.Button(self, -1, _(u"Purger la liste"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonPurge, self.bouton_purge)
        
        self.Importation() 

    def __set_properties(self):
        self.ctrl_nbre.SetToolTipString(_(u"Saisissez ici le nombre de fichiers à afficher dans la liste des fichiers ouverts"))
        self.bouton_purge.SetToolTipString(_(u"Cliquez ici pour purger la liste des derniers fichiers ouverts"))

    def __do_layout(self):
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_nbre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_nbre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_purge, 0, wx.EXPAND, 0)
        staticbox.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(staticbox)
        staticbox.Fit(self)
    
    def Importation(self):
        nbre = UTILS_Config.GetParametre("nbre_derniers_fichiers", 10)
        self.ctrl_nbre.SetValue(nbre)
        
    def Validation(self):
        return True
    
    def Sauvegarde(self):
        nbre = self.ctrl_nbre.GetValue()
        UTILS_Config.SetParametre("nbre_derniers_fichiers", nbre)
        topWindow = wx.GetApp().GetTopWindow()
        try :
            topWindow.PurgeListeDerniersFichiers(nbre)
        except :
            pass

    def OnBoutonPurge(self, event):
        topWindow = wx.GetApp().GetTopWindow()
        topWindow.PurgeListeDerniersFichiers(1) 





















# ------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        intro = _(u"Vous pouvez modifier ici les paramètres de base du logiciel. Ces paramètres seront mémorisés uniquement sur cet ordinateur. ")
        titre = _(u"Préférences")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Configuration2.png")
        
        # Contenu
        self.ctrl_langue = Langue(self)
        self.ctrl_monnaie = Monnaie(self)
        self.ctrl_telephones = Telephones(self)
        self.ctrl_codesPostaux = Codes_postaux(self)
        self.ctrl_adresses = Adresses(self)
        self.ctrl_rapport_bugs = Rapport_bugs(self)
        self.ctrl_propose_maj = Propose_maj(self)
        self.ctrl_derniers_fichiers = DerniersFichiers(self)

        # Redémarrage
        self.label_redemarrage = wx.StaticText(self, -1, _(u"* Le changement sera effectif au redémarrage du logiciel"))
        self.label_redemarrage.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
                
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        
    def __set_properties(self):
        self.SetTitle(_(u"Préférences"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider la saisie"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=12, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_langue, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_monnaie, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_telephones, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_codesPostaux, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_adresses, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_rapport_bugs, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_propose_maj, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_derniers_fichiers, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Ligne vide pour agrandir la fenêtre
##        grid_sizer_base.Add( (20, 20), 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        
        grid_sizer_base.Add(self.label_redemarrage, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
##        self.SetMinSize((400, 300))
        
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Prfrences")
    
    def OnBoutonOk(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_preferences", "modifier") == False : return
        
        # Validation des données
        if self.ctrl_langue.Validation() == False : return
        if self.ctrl_monnaie.Validation() == False : return
        if self.ctrl_telephones.Validation() == False : return
        if self.ctrl_codesPostaux.Validation() == False : return
        if self.ctrl_adresses.Validation() == False : return
        if self.ctrl_rapport_bugs.Validation() == False : return
        if self.ctrl_propose_maj.Validation() == False : return
        if self.ctrl_derniers_fichiers.Validation() == False : return
        
        # Sauvegarde
        self.ctrl_langue.Sauvegarde()
        self.ctrl_monnaie.Sauvegarde()
        self.ctrl_telephones.Sauvegarde()
        self.ctrl_codesPostaux.Sauvegarde()
        self.ctrl_adresses.Sauvegarde()
        self.ctrl_rapport_bugs.Sauvegarde()
        self.ctrl_propose_maj.Sauvegarde()
        self.ctrl_derniers_fichiers.Sauvegarde()
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
        
    
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


