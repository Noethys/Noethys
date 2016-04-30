#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image

import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
import shelve
import os
import shutil
import DLG_Messagebox

from wx.lib import langlistctrl
import UTILS_Fichiers


class Track(object):
    def __init__(self, donnees):
        self.nom = donnees["nom"]
        self.code = donnees["code"]
        self.initial = donnees["initial"]
        self.perso = donnees["perso"]
    
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        # Langues existantes
        dictLangues = {}
        for rep in ("Lang/", UTILS_Fichiers.GetRepLang()) :
            for nomFichier in os.listdir(rep) :
                if nomFichier.endswith("lang") :
                    code, extension = nomFichier.split(".")
                    fichier = shelve.open(os.path.join(rep, nomFichier), "r")
                    dictInfos = fichier["###INFOS###"]
                    nom = dictInfos["nom_langue"]
                    code = dictInfos["code_langue"]
                    nbreTextes = len(fichier) - 1
                    fichier.close()

                    if dictLangues.has_key(code) == False :
                        dictLangues[code] = {"nom" : nom, "initial" : 0, "perso" : 0}

                    if extension == "lang" :
                        dictLangues[code]["initial"] = nbreTextes
                    else :
                        dictLangues[code]["perso"] = nbreTextes

        # Remplissage
        listeListeView = []
        for code, valeurs in dictLangues.iteritems() :
            dictDonnees = {"code" : code, "initial" : valeurs["initial"], "perso" : valeurs["perso"], "nom" : valeurs["nom"]}
            listeListeView.append(Track(dictDonnees))
        
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        liste_Colonnes = [
            ColumnDefn("ID", "left", 0, "", typeDonnee="entier"),
            ColumnDefn(_(u"Nom"), 'left', 140, "nom", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Code"), "center", 60, "code", typeDonnee="texte"), 
            ColumnDefn(_(u"Trad. officielles"), "center", 100, "initial", typeDonnee="entier"), 
            ColumnDefn(_(u"Trad. perso."), "center", 100, "perso", typeDonnee="entier"), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune langue"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        menuPop.AppendSeparator()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()

        # Item Importer
        item = wx.MenuItem(menuPop, 80, _(u"Importer"))
        bmp = wx.Bitmap("Images/16x16/Document_import.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Importer, id=80)

        # Item Exporter
        item = wx.MenuItem(menuPop, 90, _(u"Exporter"))
        bmp = wx.Bitmap("Images/16x16/Document_export.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Exporter, id=90)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des langues"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des langues"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        dlg = Saisie(self)
        code = None
        if dlg.ShowModal() == wx.ID_OK:
            code = dlg.GetCode()
            nom = dlg.GetNom()
        dlg.Destroy()
        if code == None : 
            return
        
        import DLG_Saisie_traduction
        dlg = DLG_Saisie_traduction.Dialog(self, code=code, nom=nom)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()
        
    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune langue à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        import DLG_Saisie_traduction
        dlg = DLG_Saisie_traduction.Dialog(self, code=track.code, nom=track.nom)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun fichier de traduction à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        if track.perso == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune traduction personnalisée à supprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce fichier de traduction personnalisé (%d traductions) ?\n\nAttention, toute suppression est irréversible.") % track.perso, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            nomFichier = UTILS_Fichiers.GetRepLang(u"%s.xlang" % track.code)
            os.remove(nomFichier)
            self.MAJ() 
        dlg.Destroy()
    
    def Importer(self, event):
        """ Importer un fichier de langue """
        # Ouverture de la fenêtre de dialogue
        wildcard = "Fichiers de langue (*.lang, *.xlang)|*.lang;*.xlang|Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez un fichier de langue à importer"),
            defaultDir=sp.GetDocumentsDir(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Vérifie si un fichier existe déjà
        if os.path.isfile(UTILS_Fichiers.GetRepLang(nomFichierCourt)) == False :
            shutil.copyfile(nomFichierLong, UTILS_Fichiers.GetRepLang(nomFichierCourt))
            self.MAJ()
        else :
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Importer"), introduction=_(u"Ce fichier est déjà présent !"), detail=None, conclusion=_(u"Souhaitez-vous le remplacer ou les fusionner ?"), icone=wx.ICON_EXCLAMATION, boutons=[_(u"Fusionner"), _(u"Remplacer"), _(u"Annuler")])
            reponse = dlg.ShowModal()
            dlg.Destroy()
            
            if reponse == 0 : 
                # Fusionner
                dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment fusionner les deux fichiers ?"), _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_NO :
                    return
                
                # Lecture des 2 fichiers
                dictDonnees = {}
                for nomFichier in [UTILS_Fichiers.GetRepLang(nomFichierCourt), nomFichierLong] :
                    fichier = shelve.open(nomFichier, "r")
                    for key, valeur in fichier.iteritems() :
                        dictDonnees[key] = valeur
                    fichier.close()
                
                # Ecriture du fichier final
                nomFichier = UTILS_Fichiers.GetRepLang(nomFichierCourt)
                if os.path.isfile(nomFichier) :
                    flag = "w"
                else :
                    flag = "n"
                fichier = shelve.open(nomFichier, flag)
                fichier.clear() 
                for key, valeur in dictDonnees.iteritems() :
                    fichier[key] = valeur
                fichier.close()
                self.MAJ()

                dlg = wx.MessageDialog(self, _(u"Le fichier a été importé avec succès !"), _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

            if reponse == 1 :
                # Remplacer
                dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment remplacer le fichier ?"), _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_NO :
                    return
                
                # Copie du fichier vers le répertoire Lang
                os.remove(UTILS_Fichiers.GetRepLang(nomFichierCourt))
                shutil.copyfile(nomFichierLong, UTILS_Fichiers.GetRepLang(nomFichierCourt))
                self.MAJ()
 
                dlg = wx.MessageDialog(self, _(u"Le fichier a été importé avec succès !"), _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
               
            if reponse == 2 :
                return False
        
    def Exporter(self, event):
        """ Exporter le modèle sélectionné """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune langue dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        
        if track.perso == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune traduction personnalisée à exporter !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        nomFichier = track.code + ".xlang"
        
        # Demande le chemin pour la sauvegarde du fichier
        standardPath = wx.StandardPaths.Get()
        dlg = wx.FileDialog(self, message=_(u"Envoyer le fichier de traduction personnalisé vers..."),
                            defaultDir = standardPath.GetDocumentsDir(), defaultFile=nomFichier,
                            wildcard="Fichier de traduction (*.xlang)|*.xlang", style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        else :
            path = None
        dlg.Destroy()
        if path == None :
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(path) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Exportation
        shutil.copyfile(UTILS_Fichiers.GetRepLang(nomFichier), path)

        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Le fichier de traduction a été exporté avec succès !"), _(u"Exportation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        



# -------------------------------------------------------------------------------------------------------------------------------------------




class Saisie(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.SetTitle(_(u"Saisie d'une nouvelle traduction"))
        self.SetMinSize((400, 400)) 
        
        self.label_langue = wx.StaticText(self, -1, _(u"Sélectionnez une langue :"))
        self.ctrl_langue = langlistctrl.LanguageListCtrl(self, -1, filter=langlistctrl.LC_ALL)
        self.dictLangues = langlistctrl.BuildLanguageCountryMapping() 
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_langue, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_langue, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.CenterOnScreen()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
    def OnBoutonOk(self, event):
        index = self.ctrl_langue.GetLanguage()
        if index == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une langue dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.EndModal(wx.ID_OK)

    def GetCode(self):
        index = self.ctrl_langue.GetLanguage()
        return self.dictLangues[index]
    
    def GetNom(self):
        index = self.ctrl_langue.GetFirstSelected() 
        return self.ctrl_langue.GetItemText(index)
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
