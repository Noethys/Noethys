#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.hyperlink as Hyperlink
import webbrowser
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Liste_fichiers
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Json


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        if self.URL == "telecharger" :
            webbrowser.open("http://www.noethys.com/index.php?option=com_phocadownload&view=category&id=2:fichiers-exemple&Itemid=21")
        self.UpdateLink()


class MyDialog(wx.Dialog):
    def __init__(self, parent, fichierOuvert=None):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.fichierOuvert = fichierOuvert
        if self.fichierOuvert != None and "[RESEAU]" in self.fichierOuvert :
            self.fichierOuvert = self.fichierOuvert[self.fichierOuvert.index("[RESEAU]"):]

        # Bandeau
        titre = _(u"Ouvrir un fichier")
        intro = _(u"Sélectionnez le mode Local pour afficher les fichiers disponibles sur cet ordinateur. Pour afficher les fichiers réseau, sélectionnez le mode Réseau, saisissez les codes d'accès MySQL puis cliquez sur le bouton Valider. Double-cliquez sur le nom d'un fichier dans la liste pour l'ouvrir.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Fichier_ouvrir.png")
        self.SetTitle(titre)

        # Mode
        self.box_mode_staticbox = wx.StaticBox(self, -1, _(u"Mode"))
        self.radio_local = wx.RadioButton(self, -1, _(u"Local"), style=wx.RB_GROUP)
        self.radio_reseau = wx.RadioButton(self, -1, _(u"Réseau"))
        
        # Codes d'accès
        self.box_codes_staticbox = wx.StaticBox(self, -1, _(u"Codes d'accès réseau"))
        self.label_port = wx.StaticText(self, -1, _(u"Port :"))
        self.ctrl_port = wx.TextCtrl(self, -1, u"3306", style=wx.TE_CENTRE)
        self.label_hote = wx.StaticText(self, -1, _(u"Hôte :"))
        self.ctrl_hote = wx.TextCtrl(self, -1, u"")
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Utilisateur :"))
        self.ctrl_utilisateur = wx.TextCtrl(self, -1, u"")
        self.label_motdepasse = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_motdepasse = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        self.bouton_valider_codes = wx.Button(self, -1, _(u"Valider"), style=wx.BU_EXACTFIT)
        self.bouton_importer_codes = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_import.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_exporter_codes = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_export.png"), wx.BITMAP_TYPE_ANY))

        
        # Liste fichiers
        self.box_fichiers_staticbox = wx.StaticBox(self, -1, _(u"Liste des fichiers"))
        self.ctrl_fichiers = CTRL_Liste_fichiers.CTRL(self, mode="local")
        self.ctrl_fichiers.SetMinSize((-1, 400))
        self.bouton_modifier_fichier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_fichier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Updater.png"), wx.BITMAP_TYPE_ANY))
        self.hyper_telecharger = Hyperlien(self, label=_(u"Télécharger d'autres fichiers exemples"), infobulle=_(u"Cliquez ici pour télécharger d'autres fichiers exemples sur internet"), URL="telecharger")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMode, self.radio_local)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChoixMode, self.radio_reseau)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonValiderCodes, self.bouton_valider_codes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImporterCodes, self.bouton_importer_codes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExporterCodes, self.bouton_exporter_codes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifierFichier, self.bouton_modifier_fichier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimerFichier, self.bouton_supprimer_fichier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnBoutonOk, self.ctrl_fichiers)
        
        # Init contrôles
        self.OnChoixMode(None) 
        

    def __set_properties(self):
        self.radio_local.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher les fichiers disponibles en mode local")))
        self.radio_reseau.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher les fichiers disponibles en mode réseau")))
        self.ctrl_port.SetMinSize((40, -1))
        self.ctrl_port.SetToolTip(wx.ToolTip(_(u"Le numéro de port est 3306 par défaut")))
        self.ctrl_hote.SetMinSize((90,-1))
        self.ctrl_hote.SetToolTip(wx.ToolTip(_(u"Indiquez ici le nom du serveur hôte")))
        self.ctrl_utilisateur.SetMinSize((90,-1))
        self.ctrl_utilisateur.SetToolTip(wx.ToolTip(_(u"Indiquez ici le nom de l'utilisateur")))
        self.ctrl_motdepasse.SetToolTip(wx.ToolTip(_(u"Indiquez ici le mot de passe nécessaire à la connexion à MySQL")))
        self.bouton_valider_codes.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider les codes réseau et afficher la liste des fichiers disponibles")))
        self.bouton_importer_codes.SetToolTip(wx.ToolTip(_(u"Importer une configuration de fichier réseau")))
        self.bouton_exporter_codes.SetToolTip(wx.ToolTip(_(u"Exporter une configuration de fichier réseau")))
        self.bouton_modifier_fichier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le nom du fichier sélectionné dans la liste")))
        self.bouton_supprimer_fichier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le fichier sélectionné dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir le fichier sélectionné dans la liste")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        box_fichiers = wx.StaticBoxSizer(self.box_fichiers_staticbox, wx.VERTICAL)
        grid_sizer_fichiers = wx.FlexGridSizer(2, 2, 5, 5)
        grid_sizer_boutons_fichiers = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_parametres = wx.FlexGridSizer(1, 2, 10, 10)
        box_codes = wx.StaticBoxSizer(self.box_codes_staticbox, wx.VERTICAL)
        grid_sizer_codes = wx.FlexGridSizer(1, 12, 5, 5)
        box_mode = wx.StaticBoxSizer(self.box_mode_staticbox, wx.VERTICAL)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        box_mode.Add(self.radio_local, 0, wx.ALL, 5)
        box_mode.Add(self.radio_reseau, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        grid_sizer_parametres.Add(box_mode, 1, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.label_port, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_port, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.label_hote, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_hote, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.label_utilisateur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_utilisateur, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.label_motdepasse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_codes.Add(self.ctrl_motdepasse, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.bouton_valider_codes, 0, wx.RIGHT, 5)
        grid_sizer_codes.Add(self.bouton_importer_codes, 0, wx.EXPAND, 0)
        grid_sizer_codes.Add(self.bouton_exporter_codes, 0, wx.EXPAND, 0)
        grid_sizer_codes.AddGrowableCol(3)
        grid_sizer_codes.AddGrowableCol(5)
        grid_sizer_codes.AddGrowableCol(7)
        box_codes.Add(grid_sizer_codes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_parametres.Add(box_codes, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_fichiers.Add(self.ctrl_fichiers, 1, wx.EXPAND, 0)
        grid_sizer_boutons_fichiers.Add(self.bouton_modifier_fichier, 0, 0, 0)
        grid_sizer_boutons_fichiers.Add(self.bouton_supprimer_fichier, 0, 0, 0)
        grid_sizer_fichiers.Add(grid_sizer_boutons_fichiers, 1, wx.EXPAND, 0)

        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=3, vgap=3, hgap=3)
        grid_sizer_commandes.Add(self.ctrl_image, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_telecharger, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_fichiers.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)

        grid_sizer_fichiers.AddGrowableRow(0)
        grid_sizer_fichiers.AddGrowableCol(0)
        box_fichiers.Add(grid_sizer_fichiers, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_fichiers, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
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
        self.bouton_importer_codes.Enable(modeReseau)
        self.bouton_exporter_codes.Enable(modeReseau)
        self.MAJliste()
    
    def MAJliste(self):
        """ Met à jour la liste des fichiers """
        modeLocal = self.radio_local.GetValue()
        if modeLocal == True :
            # Mode local
            self.ctrl_fichiers.SetMode(mode="local")
        else :
            # Mode réseau
            dictCodes = self.GetCodesReseau() 
            self.ctrl_fichiers.SetMode(mode="reseau", codesReseau=dictCodes)
    
    def GetCodesReseau(self):
        """ Récupération des codes réseau saisis """
        try :
            port = int(self.ctrl_port.GetValue())
        except Exception as err:
            port = ""
        hote = self.ctrl_hote.GetValue()
        utilisateur = self.ctrl_utilisateur.GetValue()
        motdepasse = self.ctrl_motdepasse.GetValue()
        return {"port":port, "hote":hote, "utilisateur":utilisateur, "motdepasse":motdepasse}
    
    def OnBoutonImporterCodes(self, event):
        wildcard = _(u"Paramétrage fichier réseau Noethys (*.nnc)|*.nnc|Tous les fichiers (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez un fichier à importer"),
            defaultDir=sp.GetDocumentsDir(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN
        )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
            data = UTILS_Json.Lire(nomFichierLong)
            self.ctrl_hote.SetValue(data["host"])
            self.ctrl_utilisateur.SetValue(data["user"])
            self.ctrl_motdepasse.SetValue(data["pwd"])
            self.ctrl_port.SetValue(data["port"])
            self.OnBoutonValiderCodes(event)
        else:
            dlg.Destroy()
            return

        return

    def OnBoutonExporterCodes(self, event):
        wildcard = _(u"Paramétrage fichier réseau Noethys (*.nnc)|*.nnc|Tous les fichiers (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez un fichier à importer"),
            defaultDir=sp.GetDocumentsDir(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_SAVE
        )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
            data = {
                "host": self.ctrl_hote.GetValue(),
                "user": self.ctrl_utilisateur.GetValue(),
                "pwd": self.ctrl_motdepasse.GetValue(),
                "port": self.ctrl_port.GetValue(),
            }
            UTILS_Json.Ecrire(nomFichierLong, data=data)
        else:
            dlg.Destroy()
            return

        return

    def OnBoutonValiderCodes(self, event):
        dictCodes = self.GetCodesReseau()
        
        if dictCodes["port"] == "" :
            dlg = wx.MessageDialog(self, _(u"Le numéro de port n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_port.SetFocus()
            return
        
        if dictCodes["hote"] == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le serveur hôte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
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
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_fichier", "modifier") == False : return
        index = self.ctrl_fichiers.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un fichier à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 
        titre = self.ctrl_fichiers.GetItemPyData(index)["titre"]
        if self.fichierOuvert == titre :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas modifier un fichier déjà ouvert !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        self.ctrl_fichiers.ModifierFichier(titre)

    def OnBoutonSupprimerFichier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("fichier_fichier", "supprimer") == False : return
        index = self.ctrl_fichiers.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un fichier à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 
        titre = self.ctrl_fichiers.GetItemPyData(index)["titre"]
        if self.fichierOuvert == titre :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer un fichier déjà ouvert !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        self.ctrl_fichiers.SupprimerFichier(titre)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Ouvrirunfichier")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetNomFichier(self):
        index = self.ctrl_fichiers.GetFirstSelected()
        dictItem = self.ctrl_fichiers.GetItemPyData(index)
        modeLocal = self.radio_local.GetValue()

        # Version LOCAL
        if modeLocal == True :
            nomFichier = dictItem["titre"]
            #nomFichier = nomFichier.decode("utf8")
    
        # Version RESEAU
        if modeLocal == False :
            dictCodes = self.GetCodesReseau() 
            port = dictCodes["port"]
            hote = dictCodes["hote"]
            utilisateur = dictCodes["utilisateur"]
            motdepasse = dictCodes["motdepasse"]
            if motdepasse not in (None, "") and motdepasse.startswith("#64#") == False :
                motdepasse = GestionDB.EncodeMdpReseau(motdepasse)
            fichier = dictItem["titre"]
            nomFichier = u"%s;%s;%s;%s[RESEAU]%s" % (port, hote, utilisateur, motdepasse, fichier)
        
        return nomFichier

    def OnBoutonOk(self, event): 
        index = self.ctrl_fichiers.GetFirstSelected()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un fichier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        titre = self.ctrl_fichiers.GetItemPyData(index)["titre"]
        if self.fichierOuvert == titre :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas ouvrir un fichier déjà ouvert !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        self.EndModal(wx.ID_OK)



if __name__ == "__main__":
    app = wx.App(0)
    dlg = MyDialog(None)
    if dlg.ShowModal() == wx.ID_OK :
        print(dlg.GetNomFichier()) 
    dlg.Destroy() 
    app.MainLoop()
