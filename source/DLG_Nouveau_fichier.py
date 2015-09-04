#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image

import GestionDB
import DATA_Tables as Tables
import CTRL_Bandeau

import FonctionsPerso
import wx.lib.hyperlink as hl
import sys


class PanelReseau(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.label_port = wx.StaticText(self, -1, _(u"Port :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_port = wx.TextCtrl(self, -1, "3306", size=(45, -1))
        
        self.label_hote = wx.StaticText(self, -1, _(u"H�te :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_hote = wx.TextCtrl(self, -1, "", size=(-1, -1))
        
        self.label_user = wx.StaticText(self, -1, _(u"Utilisateur :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_user = wx.TextCtrl(self, -1, "", size=(-1, -1))
        
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_mdp = wx.TextCtrl(self, -1, "", size=(-1, -1), style=wx.TE_PASSWORD)
        
        self.__do_layout()

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=2, vgap=5, hgap=5)
        
        # Port
        grid_sizer_base.Add(self.label_port, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_port, 0, wx.ALL, 0)
        
        # Hote
        grid_sizer_base.Add(self.label_hote, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_hote, 1, wx.EXPAND | wx.ALL, 0)
        
        # User
        grid_sizer_base.Add(self.label_user, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_user, 1, wx.EXPAND | wx.ALL, 0)
        
        # Mot de passe
        grid_sizer_base.Add(self.label_mdp, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_mdp, 1, wx.EXPAND | wx.ALL, 0)
                
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        
        self.ctrl_port.SetToolTipString(_(u"Le num�ro de port est 3306 par d�faut."))
        self.ctrl_hote.SetToolTipString(_(u"Indiquez ici le nom du serveur h�te."))
        self.ctrl_user.SetToolTipString(_(u"Indiquez ici le nom de l'utilisateur. Ce nom doit avoir �t� valid� par le cr�ateur du fichier."))
        self.ctrl_mdp.SetToolTipString(_(u"Indiquez ici le mot de passe n�cessaire � la connexion � MySQL"))


class MyDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Cr�ation d'un fichier"))       
        self.parent = parent
        
        self.listeTablesImportation = Tables.TABLES_IMPORTATION_OPTIONNELLES

        # Bandeau
        titre = _(u"Cr�er un nouveau fichier")
        intro = _(u"S�lectionnez le type de fichier � cr�er puis renseignez les param�tres demand�s : le nom du fichier et l'identit� de l'administrateur du fichier. Pour un fichier r�seau, saisissez les codes MySQL.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Fichier_nouveau.png")
        self.SetTitle(titre)
        
        # Radio Local/R�seau
        self.sizer_type_staticbox = wx.StaticBox(self, -1, _(u"Type de fichier"))
        self.radio_local = wx.RadioButton(self, -1, _(u"Local"), style = wx.RB_GROUP )
        self.radio_reseau = wx.RadioButton(self, -1, _(u"R�seau") )
        self.radio_internet = wx.RadioButton(self, -1, _(u"Serveur internet") )
        
        # Nom Fichier
        self.sizer_contenu_staticbox = wx.StaticBox(self, -1, _(u"Nom du fichier"))
        self.label_nomFichier = wx.StaticText(self, -1, _(u"Nom de fichier :"))
        self.text_nomFichier = wx.TextCtrl(self, -1, "")
        self.text_nomFichier.SetMinSize((350, -1)) 
        
        # Identit� Administrateur
        self.staticbox_identite_staticbox = wx.StaticBox(self, -1, _(u"Identit� administrateur"))
        self.label_sexe = wx.StaticText(self, -1, _(u"Sexe :"))
        self.ctrl_sexe = wx.Choice(self, -1, choices=[_(u"Homme"), _(u"Femme")])
        self.ctrl_sexe.Select(0)
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_prenom = wx.StaticText(self, -1, _(u"Pr�nom :"))
        self.ctrl_prenom = wx.TextCtrl(self, -1, u"")
        self.label_code = wx.StaticText(self, -1, _(u"Code :"))
        self.ctrl_code = wx.TextCtrl(self, -1, u"")
        
        # S�lection des tables � importer
        self.checkbox_details = wx.CheckBox(self, -1, _(u"Importer les donn�es par d�faut"))
        self.checkbox_details.SetValue(True)
        self.hyperlink_details = self.Build_Hyperlink()
        
        # Panel Fichier RESEAU
        self.sizer_reseau_staticbox = wx.StaticBox(self, -1, _(u"Connexion au r�seau"))
        self.panelReseau = PanelReseau(self)
        self.panelReseau.Enable(False)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLocal, self.radio_local)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioReseau, self.radio_reseau)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioReseau, self.radio_internet)

    def __set_properties(self):
        self.checkbox_details.SetToolTipString(_(u"Il est recommand� de conserver cette case\n coch�e afin d'importer les donn�es par d�faut"))
        self.text_nomFichier.SetToolTipString(_(u"Saisissez ici le nom de votre nouveau fichier.\nExemples : 'CLSH Lannilis', 'Colo Auvergne' ou 'Mon fichier � moi'..."))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie"))
        self.radio_local.SetToolTipString(_(u"Le mode local est utilis� pour une utilisation mono-poste"))
        self.radio_reseau.SetToolTipString(_(u"Le mode r�seau est utilisateur pour une utilisation multipostes. \nMySQL doit �tre obligatoirement install� et configur� avant utilisation."))
        self.radio_internet.SetToolTipString(_(u"Le mode Serveur internet permet d'installer le fichier sur un serveur internet distant"))
        self.ctrl_sexe.SetToolTipString(_(u"S�lectionnez le sexe de l'utilisateur"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom de famille de l'utilisateur"))
        self.ctrl_prenom.SetToolTipString(_(u"Saisissez ici le prenom de l'utilisateur"))
        self.ctrl_code.SetToolTipString(_(u"Saisissez ici le code d'acc�s personnel de l'individu"))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Radios Local/r�seau
        sizer_type = wx.StaticBoxSizer(self.sizer_type_staticbox, wx.VERTICAL)
        grid_sizer_radio = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_radio.Add(self.radio_local, 1, wx.EXPAND | wx.TOP|wx.BOTTOM, 5)
        grid_sizer_radio.Add(self.radio_reseau, 1, wx.EXPAND | wx.TOP|wx.BOTTOM, 5)
        grid_sizer_radio.Add(self.radio_internet, 1, wx.EXPAND | wx.TOP|wx.BOTTOM, 5)
        sizer_type.Add(grid_sizer_radio, 1, wx.LEFT|wx.RIGHT, 10)
        grid_sizer_base.Add(sizer_type, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
                
        grid_sizer_contenu.Add(self.label_nomFichier, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_nomFichier, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add((5, 5), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        sizer_details = wx.BoxSizer(wx.HORIZONTAL)
        sizer_details.Add(self.checkbox_details, 0, 0, 0)
        sizer_details.Add(self.hyperlink_details, 0, 0, 0)
        grid_sizer_contenu.Add(sizer_details, 1, wx.ALL|wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        # Identit� Administrateur
        staticbox_identite = wx.StaticBoxSizer(self.staticbox_identite_staticbox, wx.VERTICAL)
        grid_sizer_identite = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        
        grid_sizer_identite.Add(self.label_sexe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_sexe, 0, 0, 0)
        
        grid_sizer_identite.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        
        grid_sizer_identite.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        
        grid_sizer_identite.Add(self.label_code, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_code, 0, 0, 0)
        
        grid_sizer_identite.AddGrowableCol(1)
        staticbox_identite.Add(grid_sizer_identite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_identite, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        # R�seau
        sizer_reseau = wx.StaticBoxSizer(self.sizer_reseau_staticbox, wx.VERTICAL)
        sizer_reseau.Add(self.panelReseau, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_reseau, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)
        
        # Boutons de commande
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        #grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
        self.grid_sizer_base = grid_sizer_base

    def OnRadioLocal(self, event):
        self.panelReseau.Enable(False)

    def OnRadioReseau(self, event):
        self.panelReseau.Enable(True)
        
    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"(D�tails)"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour s�lectionner les donn�es � importer")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
    
    def OnLeftLink(self, event):
        """ S�lectionner les donn�es � importer """
        # Pr�paration de la liste des donn�es
        listeDonnees = []
        listePreSelections = []
        index = 0
        for nomCategorie, tables, selection in self.listeTablesImportation :
            listeDonnees.append(nomCategorie)
            if selection == True :
                listePreSelections.append(index)
            index += 1
                                          
        # Bo�te de dialogue s�lections multiples
        titre = _(u"Importation des donn�es")
        message = _(u"S�lectionnez les donn�es que vous souhaitez importer :")
        dlg = wx.MultiChoiceDialog(self, message, titre, listeDonnees, wx.CHOICEDLG_STYLE)
        # Coche ceux qui doivent �tre d�j� s�lectionn�s dans la liste
        dlg.SetSelections(listePreSelections)
        
        # R�sultats
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            index = 0
            for categorie in self.listeTablesImportation :
                if index in listeSelections :
                    self.listeTablesImportation[index][2] = True
                else:
                    self.listeTablesImportation[index][2] = False
                index += 1
            
            if len(listeSelections) == 0 :
                self.checkbox_details.SetValue(False)
            dlg.Destroy()
        else:
            dlg.Destroy()

    
    def DesactiveIdentite(self):
        self.label_sexe.Enable(False)
        self.ctrl_sexe.Enable(False)
        self.label_nom.Enable(False)
        self.ctrl_nom.Enable(False)
        self.label_prenom.Enable(False)
        self.ctrl_prenom.Enable(False)
        self.label_code.Enable(False)
        self.ctrl_code.Enable(False)
                
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Crerunfichier")

    def OnBoutonOk(self, event):
        """ Validation des donn�es saisies """
        
        # Validation du nom saisi
        nomFichier = self.text_nomFichier.GetValue()
        if nomFichier == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom de fichier valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nomFichier.SetFocus()
            return
        
        if (self.radio_reseau.GetValue() == True or self.radio_internet.GetValue() == True) and " " in nomFichier :
            dlg = wx.MessageDialog(self, _(u"Il est interdit d'utiliser des espaces dans les noms des fichiers r�seau !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nomFichier.SetFocus()
            return
        
        for caract in nomFichier :
            if caract in u"�������������'&%*,;!:?./�@�" :
                dlg = wx.MessageDialog(self, _(u"Il est interdit d'utiliser des accents ou autres caract�res sp�ciaux dans le nom de fichier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.text_nomFichier.SetFocus()
                return
                    
        # Traitement du checkbox
        if self.checkbox_details.GetValue() == False :
            
            # Demande de confirmation pour le refus d'importer les donn�es par d�faut
            dlg = wx.MessageDialog(self, _(u"Etes-vous s�r de ne pas vouloir importer les donn�es par d�faut ?"), _(u"Importation des donn�es"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES :
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            
            # D�sactivation des donn�es import�es par d�faut
            index = 0
            for categorie in self.listeTablesImportation :
                self.listeTablesImportation[index][2] = False
                index += 1
        
        # Identit� administrateur
        if self.ctrl_nom.IsEnabled() :
            
            if len(self.ctrl_nom.GetValue()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom d'administrateur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_nom.SetFocus()
                return
            
            if len(self.ctrl_code.GetValue()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un code d'acc�s personnel !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_code.SetFocus()
                return

        # Version RESEAU
        if self.radio_reseau.GetValue() == True or self.radio_internet.GetValue() == True :
            port = self.panelReseau.ctrl_port.GetValue()
            hote = self.panelReseau.ctrl_hote.GetValue()
            user = self.panelReseau.ctrl_user.GetValue()
            mdp = self.panelReseau.ctrl_mdp.GetValue()
            
            try :
                port = int(port)
            except Exception, err:
                dlg = wx.MessageDialog(self, _(u"Le num�ro de port n'est pas valide. \n\nErreur : %s") % err, _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_port.SetFocus()
                return
            
            if hote == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le serveur h�te."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_hote.SetFocus()
                return
            
            if user == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom d'utilisateur."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_user.SetFocus()
                return
            
            if mdp == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un mot de passe."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_mdp.SetFocus()
                return
            
            # Teste la connexion R�seau
            dictResultats = GestionDB.TestConnexionMySQL(typeTest="connexion", nomFichier=self.GetNomFichier() )
            if dictResultats["connexion"][0] == False :
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, _(u"La connexion au r�seau MySQL est impossible. \n\nErreur : %s") % erreur, "Erreur de connexion", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetMode(self):
        if self.radio_local.GetValue() == True : return "local"
        if self.radio_reseau.GetValue() == True : return "reseau"
        if self.radio_internet.GetValue() == True : return "internet"
        
    def GetNomFichier(self):
        # Version LOCAL
        if self.radio_local.GetValue() == True :
            nomFichier = self.text_nomFichier.GetValue()
            return nomFichier
    
        # Version RESEAU
        if self.radio_reseau.GetValue() == True or self.radio_internet.GetValue() == True :
            port = self.panelReseau.ctrl_port.GetValue()
            hote = self.panelReseau.ctrl_hote.GetValue()
            user = self.panelReseau.ctrl_user.GetValue()
            mdp = self.panelReseau.ctrl_mdp.GetValue()
            fichier = self.text_nomFichier.GetValue()
            nomFichier = u"%s;%s;%s;%s[RESEAU]%s" % (port, hote, user, mdp, fichier)
            return nomFichier
    
    def GetListeTables(self):
        listeDonnees = self.listeTablesImportation
        return listeDonnees
    
    def GetIdentiteAdministrateur(self):
        if self.ctrl_sexe.GetSelection() == 0 :
            sexe = "M"
        else:
            sexe = "F"
        nom = self.ctrl_nom.GetValue() 
        prenom = self.ctrl_prenom.GetValue() 
        code = self.ctrl_code.GetValue() 
        profil = "administrateur"
        actif = 1
        dictTemp = { "sexe":sexe, "nom":nom, "prenom":prenom, "mdp":code, "profil":profil, "actif":actif, "image":None }
        return dictTemp
    
    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyDialog(None)
    frame_1.ShowModal()
    app.MainLoop()
