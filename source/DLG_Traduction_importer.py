#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import wx.lib.filebrowsebutton as filebrowse
import os
import shelve




class CTRL_Langue(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        self.listeLabels = []
        self.listeDonnees = []
        
        # Recherche les fichiers de langues existants
        listeFichiers = os.listdir("Lang/") 
        listeCodes = []
        for nomFichier in listeFichiers :
            code, extension = nomFichier.split(".")
            fichier = shelve.open("Lang/" + nomFichier, "r")
            
            # Lecture des caractéristiques
            dictInfos = fichier["###INFOS###"]
            nom = dictInfos["nom_langue"]
            code = dictInfos["code_langue"]
            
            # Lecture des textes
            listeTextes = []
            for texte, traduction in fichier.iteritems() :
                if texte != "###INFOS###" :
                    listeTextes.append(texte)
            
            # Fermeture du fichier
            fichier.close()
            
            label = u"%s (%s)" % (nom, code)
            if code not in listeCodes :
                listeCodes.append(code)
                self.listeLabels.append(label)
                self.listeDonnees.append({"nom":nom, "code":code, "textes":listeTextes})
            
        # Remplissage du contrôle
        if len(self.listeLabels) == 0 :
            self.Enable(False)
        self.SetItems(self.listeLabels)

    def SetCode(self, code=""):
        index = 0
        for dictTemp in self.listeDonnees :
            if dictTemp["code"] == code :
                 self.SetSelection(index)
            index += 1

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        # Bandeau
        titre = _(u"Import/Export de traductions au format texte")
        intro = _(u"Sélectionnez une langue dans la liste puis exportez ou importez les textes au format TXT.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Traduction.png")
        
        # Langue
        self.box_langue_staticbox = wx.StaticBox(self, -1, _(u"Langue"))
        self.ctrl_langues = CTRL_Langue(self)
        
        # Exporter
        self.box_exporter_staticbox = wx.StaticBox(self, -1, _(u"Exporter"))
        self.check_nontraduits = wx.CheckBox(self, -1, _(u"Inclure uniquement les textes non traduits"))
        self.check_nontraduits.SetValue(True)
        self.bouton_exporter = CTRL_Bouton_image.CTRL(self, texte=_(u"Exporter"), cheminImage="Images/32x32/Fleche_haut.png")
        self.bouton_exporter.SetMinSize((400, -1))
        
        # Importer
        self.box_importer_staticbox = wx.StaticBox(self, -1, _(u"Importer"))
        
        wildcard = _(u"Fichiers texte|*.txt|Tous les fichiers (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        self.ctrl_fichier_importer_original = filebrowse.FileBrowseButton(self, -1, labelText=_(u"Fichier des textes originaux :"), buttonText=_(u"Sélectionner"), toolTip=_(u"Cliquez ici pour sélectionner un fichier"), dialogTitle=_(u"Sélectionner un fichier"), fileMask=wildcard, startDirectory=cheminDefaut)
        self.ctrl_fichier_importer_traduction = filebrowse.FileBrowseButton(self, -1, labelText=_(u"Fichier des textes traduits :"), buttonText=_(u"Sélectionner"), toolTip=_(u"Cliquez ici pour sélectionner un fichier"), dialogTitle=_(u"Sélectionner un fichier"), fileMask=wildcard, startDirectory=cheminDefaut)
        self.bouton_importer = CTRL_Bouton_image.CTRL(self, texte=_(u"Importer"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExporter, self.bouton_exporter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImporter, self.bouton_importer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        

    def __set_properties(self):
        self.ctrl_langues.SetToolTipString(_(u"Sélectionnez la langue souhaitée"))
        self.check_nontraduits.SetToolTipString(_(u"Cochez cette case pour inclure uniquement les textes non traduits"))
        self.bouton_exporter.SetToolTipString(_(u"Cliquez ici pour exporter les textes originaux au format txt"))
        self.bouton_importer.SetToolTipString(_(u"Cliquez ici pour importer les traductions du fichier txt"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(5, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Langue
        box_langue = wx.StaticBoxSizer(self.box_langue_staticbox, wx.VERTICAL)
        box_langue.Add(self.ctrl_langues, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_langue, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Exporter
        box_exporter = wx.StaticBoxSizer(self.box_exporter_staticbox, wx.VERTICAL)
        grid_sizer_exporter = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_exporter.Add(self.bouton_exporter, 0, wx.EXPAND, 0)
        grid_sizer_exporter.Add(self.check_nontraduits, 0, 0, 0)
        grid_sizer_exporter.AddGrowableCol(0)
        box_exporter.Add(grid_sizer_exporter, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_exporter, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Importer
        box_importer = wx.StaticBoxSizer(self.box_importer_staticbox, wx.VERTICAL)
        grid_sizer_importer = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_importer.Add(self.ctrl_fichier_importer_original, 0, wx.EXPAND, 0)
        grid_sizer_importer.Add(self.ctrl_fichier_importer_traduction, 0, wx.EXPAND, 0)
        grid_sizer_importer.Add(self.bouton_importer, 0, wx.EXPAND, 0)
        grid_sizer_importer.AddGrowableCol(0)
        box_importer.Add(grid_sizer_importer, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_importer, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 3, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)        

    def OnBoutonExporter(self, event):
        # Récupération de la langue
        dictLangue = self.ctrl_langues.GetCode()
        if dictLangue == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une langue dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        nom = dictLangue["nom"]
        textesLangue = dictLangue["textes"]
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nom_fichier = u"Textes_originaux.txt"
        wildcard = u"Fichier Texte (*.txt)|*.xml| Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nom_fichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()
        
        # Lecture du fichier dat
        fichier = shelve.open("Textes.dat", "r")
        listeTextes = []
        for texte, listeFichiers in fichier.iteritems() :
            listeTextes.append(texte)
        fichier.close()
        listeTextes.sort() 
        
        # Enregistrement du fichier texte
        fichier = open(cheminFichier, "w")
        nbreTextes = 0
        for texte in listeTextes :
            if self.check_nontraduits.GetValue() == False or (self.check_nontraduits.GetValue() == True and texte not in textesLangue) :
                fichier.write(texte + "\n")
                nbreTextes += 1
        fichier.close() 
        
        # Confirmation fin
        dlg = wx.MessageDialog(self, _(u"Le fichier a été généré avec succès (%d textes) !") % nbreTextes, _(u"Génération"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonImporter(self, event):
        # Récupération de la langue
        dictLangue = self.ctrl_langues.GetCode()
        if dictLangue == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une langue dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        nom_langue = dictLangue["nom"]
        code_langue = dictLangue["code"]
        textes_langue = dictLangue["textes"]
        
        # Récupération des fichiers
        fichier_original = self.ctrl_fichier_importer_original.GetValue() 
        if fichier_original == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un fichier de textes originaux !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        fichier_traduction = self.ctrl_fichier_importer_traduction.GetValue() 
        if fichier_traduction == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un fichier de textes traduits !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Lecture des textes
        fichier = open(fichier_original, "r")
        lignesOriginal = fichier.readlines()
        fichier.close() 
        
        fichier = open(fichier_traduction, "r")
        lignesTraduction = fichier.readlines()
        fichier.close() 

        if len(lignesOriginal) !=  len(lignesTraduction) :
            dlg = wx.MessageDialog(self, _(u"Le nombre de lignes des deux fichiers doit être identique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
    
        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Confirmez-vous l'insertion de %d textes traduits dans le fichier '%s' ?") % (len(lignesOriginal), nom_langue), "Confirmation", wx.YES_NO | wx.YES_DEFAULT | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_NO :
            return False
            dlg.Destroy()
        else:
            dlg.Destroy()
        
        # Fusion des traductions
        dictTraductions = {}
        indexLigne = 0
        for texte in lignesOriginal :
            if len(texte) > 0 :
                dictTraductions[texte[:-1]] = lignesTraduction[indexLigne][:-1]
            indexLigne += 1
        
        # Création du fichier de traduction perso
        nomFichier = "Lang/%s.xlang" % code_langue
        if os.path.isfile(nomFichier) :
            flag = "w"
        else :
            flag = "n"
        fichier = shelve.open(nomFichier, flag)
        
        # Remplissage du fichier
        fichier["###INFOS###"] = {"nom_langue" : nom_langue, "code_langue" : code_langue}
        for texte, traduction in dictTraductions.iteritems() :
            fichier[texte] = traduction
            if "Bienvenue" in texte :
                print texte, " --> ", (traduction,)
        # Clôture du fichier
        fichier.close()
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"L'importation des traductions s'est déroulée avec succès !"), _(u"Succès"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


        
    
    
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
