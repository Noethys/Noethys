#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import FonctionsPerso
import os

import CTRL_Bandeau
import CTRL_Liste_fichiers
import DATA_Tables as Tables
import GestionDB




class CTRL_Options(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.dictDonnees = {}
        self.dictIndex = {}
        self.listeOptions = [
            ("abonnements", _(u"Listes de diffusion et abonnements")),
            ("scolarite", _(u"Donn�es de scolarit� : �tapes, �coles, classes...")),
            ("questionnaire", _(u"Questionnaires familiaux et individuels")),
            ("pieces", _(u"Pi�ces et types de pi�ces")),
            ("messages", _(u"Messages de type famille, individuel ou accueil")),
            ("quotients", _(u"Quotients familiaux des familles")),
            ("mandats", _(u"Mandats SEPA des familles")),
            ]
        self.MAJ() 
        
    def MAJ(self):
        self.Clear()
        self.dictIndex = {}
        index = 0
        for code, label in self.listeOptions :
            self.Append(label) 
            self.dictIndex[index] = code
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeOptions)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.dictIndex[index])
        return listeIDcoches



# ----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)

        # Bandeau
        titre = _(u"Importer des familles depuis un fichier Noethys")
        intro = _(u"Cette fonctionnalit� vous permet d'importer les fiches familles d'un autre fichier de donn�es Noethys. <u>Attention, toutes les fiches familles d�j� saisies seront �cras�es !</u> Il est donc conseill� d'utiliser cette fonction uniquement apr�s la cr�ation d'un nouveau fichier. S�lectionnez un fichier � importer, cochez des options puis cliquez sur OK.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Document_import.png")
        self.SetTitle(titre)

        # Mode
        self.box_mode_staticbox = wx.StaticBox(self, -1, _(u"Mode"))
        self.radio_local = wx.RadioButton(self, -1, _(u"Local"), style=wx.RB_GROUP)
        self.radio_reseau = wx.RadioButton(self, -1, _(u"R�seau"))
        
        # Codes d'acc�s
        self.box_codes_staticbox = wx.StaticBox(self, -1, _(u"Codes d'acc�s r�seau"))
        self.label_port = wx.StaticText(self, -1, _(u"Port :"))
        self.ctrl_port = wx.TextCtrl(self, -1, u"3306", style=wx.TE_CENTRE)
        self.label_hote = wx.StaticText(self, -1, _(u"H�te :"))
        self.ctrl_hote = wx.TextCtrl(self, -1, u"")
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Utilisateur :"))
        self.ctrl_utilisateur = wx.TextCtrl(self, -1, u"")
        self.label_motdepasse = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_motdepasse = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        self.bouton_valider_codes = wx.Button(self, -1, _(u"Valider"), style=wx.BU_EXACTFIT)
        
        # Liste fichiers
        self.box_fichiers_staticbox = wx.StaticBox(self, -1, _(u"1. S�lection du fichier"))
        self.ctrl_fichiers = CTRL_Liste_fichiers.CTRL(self, mode="local")
        self.ctrl_fichiers.SetMinSize((-1, 200))

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"2. S�lection des donn�es optionnelles"))
        self.ctrl_options = CTRL_Options(self)
        self.ctrl_options.SetMinSize((20, 140))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMode, self.radio_local)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMode, self.radio_reseau)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonValiderCodes, self.bouton_valider_codes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contr�les
        self.OnChoixMode(None) 
        

    def __set_properties(self):
        self.radio_local.SetToolTipString(_(u"Cliquez ici pour afficher les fichiers disponibles en mode local"))
        self.radio_reseau.SetToolTipString(_(u"Cliquez ici pour afficher les fichiers disponibles en mode r�seau"))
        self.ctrl_port.SetMinSize((40, -1))
        self.ctrl_port.SetToolTipString(_(u"Le num�ro de port est 3306 par d�faut"))
        self.ctrl_hote.SetMinSize((90,-1))
        self.ctrl_hote.SetToolTipString(_(u"Indiquez ici le nom du serveur h�te"))
        self.ctrl_utilisateur.SetMinSize((90,-1))
        self.ctrl_utilisateur.SetToolTipString(_(u"Indiquez ici le nom de l'utilisateur"))
        self.ctrl_motdepasse.SetToolTipString(_(u"Indiquez ici le mot de passe n�cessaire � la connexion � MySQL"))
        self.bouton_valider_codes.SetToolTipString(_(u"Cliquez ici pour valider les codes r�seau et afficher la liste des fichiers disponibles"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour ouvrir le fichier s�lectionn� dans la liste"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        
        # Fichier
        box_fichiers = wx.StaticBoxSizer(self.box_fichiers_staticbox, wx.VERTICAL)
        grid_sizer_fichiers = wx.FlexGridSizer(2, 1, 10, 10)
        
        grid_sizer_parametres = wx.FlexGridSizer(1, 2, 10, 10)
        
        # Mode
        box_mode = wx.StaticBoxSizer(self.box_mode_staticbox, wx.VERTICAL)
        box_mode.Add(self.radio_local, 0, wx.ALL, 5)
        box_mode.Add(self.radio_reseau, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        grid_sizer_parametres.Add(box_mode, 1, wx.EXPAND, 0)
        
        # Codes
        box_codes = wx.StaticBoxSizer(self.box_codes_staticbox, wx.VERTICAL)
        grid_sizer_codes = wx.FlexGridSizer(1, 10, 5, 5)
        grid_sizer_codes.Add(self.label_port, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_port, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.label_hote, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_hote, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.label_utilisateur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_utilisateur, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.label_motdepasse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_motdepasse, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.bouton_valider_codes, 0, 0, 0)
        grid_sizer_codes.AddGrowableCol(7)
        box_codes.Add(grid_sizer_codes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_parametres.Add(box_codes, 1, wx.EXPAND, 0)
        
        grid_sizer_parametres.AddGrowableCol(1)
        grid_sizer_fichiers.Add(grid_sizer_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)


        grid_sizer_fichiers.Add(self.ctrl_fichiers, 1, wx.EXPAND, 0)
        grid_sizer_fichiers.AddGrowableRow(1)
        grid_sizer_fichiers.AddGrowableCol(0)
        box_fichiers.Add(grid_sizer_fichiers, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_fichiers, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        box_options.Add(self.ctrl_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnChoixMode(self, event): 
        modeReseau = self.radio_reseau.GetValue()
        self.ctrl_port.Enable(modeReseau)
        self.ctrl_hote.Enable(modeReseau)
        self.ctrl_utilisateur.Enable(modeReseau)
        self.ctrl_motdepasse.Enable(modeReseau)
        self.bouton_valider_codes.Enable(modeReseau)
        self.MAJliste() 
    
    def MAJliste(self):
        """ Met � jour la liste des fichiers """
        modeLocal = self.radio_local.GetValue()
        if modeLocal == True :
            # Mode local
            self.ctrl_fichiers.SetMode(mode="local")
        else :
            # Mode r�seau
            dictCodes = self.GetCodesReseau() 
            self.ctrl_fichiers.SetMode(mode="reseau", codesReseau=dictCodes)
    
    def GetCodesReseau(self):
        """ R�cup�ration des codes r�seau saisis """
        try :
            port = int(self.ctrl_port.GetValue())
        except Exception, err:
            port = ""
        hote = self.ctrl_hote.GetValue()
        utilisateur = self.ctrl_utilisateur.GetValue()
        motdepasse = self.ctrl_motdepasse.GetValue()
        return {"port":port, "hote":hote, "utilisateur":utilisateur, "motdepasse":motdepasse}
    
    def OnBoutonValiderCodes(self, event): 
        dictCodes = self.GetCodesReseau() 
        
        if dictCodes["port"] == "" :
            dlg = wx.MessageDialog(self, _(u"Le num�ro de port n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_port.SetFocus()
            return
        
        if dictCodes["hote"] == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le serveur h�te !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_hote.SetFocus()
            return
        
        if dictCodes["utilisateur"] == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom d'utilisateur !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_utilisateur.SetFocus()
            return

        if dictCodes["motdepasse"] == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un mot de passe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_motdepasse.SetFocus()
            return
        
        self.MAJliste() 
        
        # Test de la connexion
        test = self.ctrl_fichiers.TestConnexionReseau() 
        if test != True  :
            dlg = wx.MessageDialog(self, _(u"Erreur de connexion MySQL :\n\n%s") % test, _(u"Erreur de connexion"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def OnBoutonModifierFichier(self, event): 
        index = self.ctrl_fichiers.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner un fichier � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 
        titre = self.ctrl_fichiers.GetItemPyData(index)["titre"]
        if self.fichierOuvert == titre :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas modifier un fichier d�j� ouvert !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        self.ctrl_fichiers.ModifierFichier(titre)

    def OnBoutonSupprimerFichier(self, event): 
        index = self.ctrl_fichiers.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner un fichier � supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 
        titre = self.ctrl_fichiers.GetItemPyData(index)["titre"]
        if self.fichierOuvert == titre :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer un fichier d�j� ouvert !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        self.ctrl_fichiers.SupprimerFichier(titre)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetNomFichier(self):
        index = self.ctrl_fichiers.GetFirstSelected()
        dictItem = self.ctrl_fichiers.GetItemPyData(index)
        modeLocal = self.radio_local.GetValue()

        # Version LOCAL
        if modeLocal == True :
            nomFichier = dictItem["titre"]
            nomFichier = nomFichier.decode("iso-8859-15")
    
        # Version RESEAU
        if modeLocal == False :
            dictCodes = self.GetCodesReseau() 
            port = dictCodes["port"]
            hote = dictCodes["hote"]
            utilisateur = dictCodes["utilisateur"]
            motdepasse = dictCodes["motdepasse"]
            fichier = dictItem["titre"]
            nomFichier = u"%s;%s;%s;%s[RESEAU]%s" % (port, hote, utilisateur, motdepasse, fichier)
        
        return nomFichier

    def OnBoutonOk(self, event): 
        index = self.ctrl_fichiers.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner un fichier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        titre = self.ctrl_fichiers.GetItemPyData(index)["titre"]
        nomFichier = self.GetNomFichier() 
        listeOptions = self.ctrl_options.GetIDcoches() 
        
        # Demande de confirmation
        nbreFamilles = self.GetNbreFamilles() 
        if nbreFamilles > 0 :
            dlg = wx.MessageDialog(self, _(u"Attention, %d fiches familles sont d�j� saisies dans ce fichier. Si vous utilisez la fonction d'importation, TOUTES les fiches actuelles seront �cras�es !!!\n\nSouhaitez-vous tout de m�me continuer ?") % nbreFamilles, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                return False
            dlg.Destroy()
        
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment lancer l'importation des familles du fichier '%s' ?\n\nAttention, toutes les donn�es actuelles seront �cras�es !") % titre, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return False
        dlg.Destroy()

        # Importation des tables
        listeTables = [
            "comptes_payeurs", "familles", "individus", "liens", 
            "medecins", "payeurs", "categories_travail", "caisses", 
            "rattachements", "regimes", "secteurs", "types_sieste", 
            "problemes_sante", "types_maladies", "types_vaccins", "vaccins", "vaccins_maladies",
            ]
            
        if "abonnements" in listeOptions : listeTables.extend(["abonnements", "listes_diffusion"])
        if "scolarite" in listeOptions : listeTables.extend(["classes", "ecoles", "niveaux_scolaires", "scolarite"])
        if "questionnaire" in listeOptions : listeTables.extend(["questionnaire_categories", "questionnaire_choix", "questionnaire_filtres", "questionnaire_questions", "questionnaire_reponses"])
        if "pieces" in listeOptions : listeTables.extend(["pieces", "types_pieces"])
        if "messages" in listeOptions : listeTables.extend(["messages", "messages_categories"])
        if "quotients" in listeOptions : listeTables.extend(["quotients",])
        if "mandats" in listeOptions : listeTables.extend(["mandats",])
            
        DB = GestionDB.DB() 
        for nomTable in listeTables :
            # R�initialisation de la table
            print "Reinitialisation de la table %s..." % nomTable
            DB.ExecuterReq("DROP TABLE %s;" % nomTable)
            DB.Commit() 
            DB.CreationTable(nomTable, Tables.DB_DATA)
            # Importation des donn�es
            print "Importation de la table %s..." % nomTable
            if self.radio_local.GetValue() == True :
                DB.Importation_table(nomTable=nomTable, nomFichierdefault=u"Data/%s_DATA.dat" % nomFichier)
            else :
                DB.Importation_table(nomTable=nomTable, nomFichierdefault=nomFichier+"_data", mode="reseau")
        DB.Close()
        
        # Fin
        nbreFamilles = self.GetNbreFamilles() 
        dlg = wx.MessageDialog(self, _(u"La proc�dure d'importation est termin�e !\n\n%d familles ont �t� import�es avec succ�s.") % nbreFamilles, _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        self.EndModal(wx.ID_OK)
    
    def GetNbreFamilles(sel):
        DB = GestionDB.DB()
        DB.ExecuterReq("""SELECT IDfamille FROM familles;""")
        listeFamilles = DB.ResultatReq()
        DB.Close() 
        return len(listeFamilles)


if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal() 
    dlg.Destroy() 
    app.MainLoop()
