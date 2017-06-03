#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
import os
import FonctionsPerso


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

LISTE_EXTENSIONS = ["bmp", "doc", "docx", "gif", "jpeg", "jpg", "pdf", "png", "tous", "xls", "xlsx", "zip", "plusieurs",]


class Track(object):
    def __init__(self, parent, dictDonnees={}):
        self.parent = parent
        self.adresse = dictDonnees["adresse"]
        self.pieces = dictDonnees["pieces"]
        self.champs = dictDonnees["champs"]
        
        if dictDonnees.has_key("IDfamille") :
            self.IDfamille = dictDonnees["IDfamille"]
        else :
            self.IDfamille = None
        if dictDonnees.has_key("IDindividu") :
            self.IDindividu = dictDonnees["IDindividu"]
        else :
            self.IDindividu = None
            
        if self.parent.memoire_pieces.has_key(self.adresse) :
            self.pieces = self.parent.memoire_pieces[self.adresse]
        if self.parent.memoire_champs.has_key(self.adresse) :
            self.champs = self.parent.memoire_champs[self.adresse]

        self.TraitementPieces() 
    
    def TraitementPieces(self):
        """ Traitement des pièces """
        if len(self.pieces) > 0 :
            self.listeLabelsPieces = []
            listeExtensions = []
            for fichier in self.pieces :
                nomFichier = os.path.basename(fichier)
                extension = fichier.split('.')[-1].lower()
                if extension not in listeExtensions :
                    listeExtensions.append(extension)
                taille = os.path.getsize(fichier)
                if taille != None :
                    if taille >= 1000000 :
                        texteTaille = "%s Mo" % (taille/1000000)
                    else :
                        texteTaille = "%s Ko" % (taille/1000)
                    label = u"%s (%s)" % (nomFichier, texteTaille)
                else :
                    label = nomFichier
                self.listeLabelsPieces.append(label)
                
            self.texte_pieces = ", ".join(self.listeLabelsPieces)
            
            if len(listeExtensions) > 1 :
                self.extension_pieces = "plusieurs"
            else :
                extension = listeExtensions[0]
                if extension in LISTE_EXTENSIONS :
                    self.extension_pieces = extension
                else :
                    self.extension_pieces = "tous"
            
        else :
            self.texte_pieces = ""
            self.listeLabelsPieces = []
            self.extension_pieces = None
        
        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        listeDonneesManuelles = kwds.pop("listeDonnees", [])
        self.modificationAutorisee = kwds.pop("modificationAutorisee", True)

        self.listeDonnees = []
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []

##        self.valeurs_manuel = u""
##        self.valeurs_diff = []
##        self.valeurs_familles = []
##        self.valeurs_individus = []
        
        self.memoire_donnees = {}
        self.memoire_pieces = {}
        self.memoire_champs = {}

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
        # Init données
        if len(listeDonneesManuelles) > 0 :
            self.SetDonneesManuelles(listeDonneesManuelles)
                
    def InitModel(self):
        self.donnees = self.GetTracks()
        
        # Mémorise les pièces jointes personnelles et les champs
        for track in self.donnees :
            if self.memoire_pieces.has_key(track.adresse) == False :
                self.memoire_pieces[track.adresse] = []
            self.memoire_pieces[track.adresse] = track.pieces
            
            if self.memoire_champs.has_key(track.adresse) == False :
                self.memoire_champs[track.adresse] = []
            self.memoire_champs[track.adresse] = track.champs
            
    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        listeListeView = []
        for item in self.listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == track.adresse :
                    self.selectionTrack = track                
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        self.dictImages = {}
        for extension in LISTE_EXTENSIONS :
            self.AddNamedImages(extension, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fichier_%s.png" % extension), wx.BITMAP_TYPE_PNG))
        
        # Formatage des données
        def GetImagePiece(track):
            return track.extension_pieces

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, None),
            ColumnDefn(_(u"Adresse"), 'left', 150, "adresse", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Pièces jointes personnelles"), 'left', 190, "texte_pieces", typeDonnee="texte", imageGetter=GetImagePiece),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun destinataire"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            selection = None
        else:
            selection = self.Selection()[0]

        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter ou retirer des destinataires"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Email_destinataires.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=10)
        if self.modificationAutorisee == False :
            item.Enable(False)

        menuPop.AppendSeparator()
        
        # Ajouter pièce jointe
        item = wx.MenuItem(menuPop, 20, _(u"Ajouter une pièce personnelle"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.AjouterPiece, id=20)
        if selection == None :
            item.Enable(False)
        
        # Retirer pièce jointe
        item = wx.MenuItem(menuPop, 30, _(u"Retirer une pièce personnelle"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.RetirerPiece, id=30)
        if selection == None or selection.pieces == [] :
            item.Enable(False)

        menuPop.AppendSeparator()

        # Ouvrir pièce jointe
        item = wx.MenuItem(menuPop, 60, _(u"Ouvrir une pièce personnelle"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirPiece, id=60)
        if selection == None or selection.pieces == [] :
            item.Enable(False)

        menuPop.AppendSeparator()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)

        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Modifier(self, event=None):
        from Dlg import DLG_Selection_mails
        dlg = DLG_Selection_mails.Dialog(self)
        dlg.SetDonnees(self.memoire_donnees)
        dlg.ShowModal()
        self.memoire_donnees, listeAdresses = dlg.GetDonnees()
        dlg.Destroy()
        
        listeTemp = []
        for adresse in listeAdresses :
            dictTemp = {"adresse":adresse, "pieces":[], "champs":{} }
            listeTemp.append(dictTemp)
        self.SetDonnees(listeTemp)

    def SetDonnees(self, listeDonnees=[]):
        """ Remplit la liste des mails """
        self.listeDonnees = listeDonnees
        self.MAJ()
        try :
            if len(self.listeMails) > 0 :
                self.parent.box_destinataires_staticbox.SetLabel("Destinataires (%d)" % len(self.listeDonnees))
            else:
                self.parent.box_destinataires_staticbox.SetLabel("Destinataires")
        except :
            pass
    
    def SetDonneesManuelles(self, listeDonnees=[], modificationAutorisee=None):
        # Autorisation des modifications
        if modificationAutorisee != None :
            self.modificationAutorisee = modificationAutorisee
        # IMportation des données
        self.SetDonnees(listeDonnees)
        listeTemp = []
        for track in self.donnees :
            if track.adresse != None :
                listeTemp.append(track.adresse) 
        self.memoire_donnees["saisie_manuelle"] = {
            "texte" : ";".join(listeTemp),
            "liste_adresses" : listeTemp,
            }

    def AjouterPiece(self, event):
        """ Demande l'emplacement du fichier à joindre """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un destinataire dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        standardPath = wx.StandardPaths.Get()
        rep = standardPath.GetDocumentsDir()
        dlg = wx.FileDialog(self, message=_(u"Veuillez sélectionner le ou les fichiers à joindre"), defaultDir=rep, defaultFile="", style=wx.OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            chemins = dlg.GetPaths()
        else:
            return
        dlg.Destroy()
        listeTemp = []
        for fichier in chemins :
            valide = True
            if fichier in track.pieces :
                dlg = wx.MessageDialog(self, _(u"Le fichier '%s' est déjà dans la liste !") % os.path.basename(fichier), "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
                dlg.ShowModal()
                dlg.Destroy()
                valide = False
            if valide == True :
                track.pieces.append(fichier)
                self.memoire_pieces[track.adresse] = track.pieces
        self.MAJ()
        
    def RetirerPiece(self, event):
        """ Retirer pièces """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un destinataire dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        if track.pieces == [] :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune pièce à retirer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MultiChoiceDialog(self, _(u"Cochez les pièces personnelles à retirer :"), _(u"Retirer des pièces personnelles"), track.listeLabelsPieces)
        if dlg.ShowModal() == wx.ID_OK :
            selections = dlg.GetSelections()
            for index in selections :
                track.pieces.pop(index)
                self.memoire_pieces[track.adresse] = track.pieces
            self.MAJ() 
        dlg.Destroy()

    def OuvrirPiece(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un destinataire à ouvrir dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        if track.pieces == [] :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune pièce à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Demande le fichier à ouvrir
        if len(track.pieces) > 1 :
            dlg = wx.SingleChoiceDialog(self, _(u"Sélectionnez la pièce jointe personnelle à ouvrir :"), _(u"Ouvrir une pièce jointe personnelle"), track.pieces, wx.CHOICEDLG_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                fichier = track.pieces[dlg.GetSelection()]
                dlg.Destroy()
            else :
                dlg.Destroy()
                return
        else :
            fichier = track.pieces[0]
        # Ouverture du fichier
        FonctionsPerso.LanceFichierExterne(fichier)


    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des destinataires"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des destinataires"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event=None):
        """ Export de la liste au format texte """
        # Vérifie qu"il y a des adresses mails saisies
        if len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"La liste des destinataires est vide !"), "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportTexte.txt"
        wildcard = "Fichier texte (*.txt)|*.txt|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
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
        # Création du fichier texte
        texte = ""
        separateur = ";"
        for track in self.donnees :
            texte += track.adresse + separateur
        texte = texte[:-1]
        # Création du fichier texte
        f = open(cheminFichier, "w")
        f.write(texte.encode("iso-8859-15"))
        f.close()
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Texte a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)
        
    def ExportExcel(self, event=None):
        """ Export Excel """
        titre = _(u"Destinataires")
        # Vérifie qu"il y a des adresses mails saisies
        if len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"La liste des destinataires est vide !"), "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xls" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xls)|*.xls|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
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
        # Export
        import pyExcelerator
        # Création d'un classeur
        wb = pyExcelerator.Workbook()
        # Création d'une feuille
        ws1 = wb.add_sheet(titre)
        # Remplissage de la feuille
        x = 0
        for track in self.donnees :
            ws1.write(x, 0, track.adresse)
            x += 1                    
        # Finalisation du fichier xls
        wb.save(cheminFichier)
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)


    def GetDonnees(self):
        """ Renvoie les données au format track """
        return self.donnees

    def GetDonneesDict(self):
        """ Renvoie les données au format dict """
        listeTemp = []
        for track in self.donnees :
            dictTemp = {"adresse":track.adresse, "pieces":track.pieces, "champs":track.champs}
            listeTemp.append(dictTemp)
        return listeTemp


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
        
        listeDonnees = [
            {"adresse" : "monadresse1@gmail.com", "pieces" : [], "champs" : {"{UTILISATEUR_NOM}" : _(u"nom1"), "{UTILISATEUR_PRENOM}" : _(u"prenom1") } },
            {"adresse" : "monadresse2@gmail.com", "pieces" : [], "champs" : {"{UTILISATEUR_NOM}" : _(u"nom2"), "{UTILISATEUR_PRENOM}" : _(u"prenom2") } },
            {"adresse" : "monadresse3@gmail.com", "pieces" : [], "champs" : {"{UTILISATEUR_NOM}" : _(u"nom3"), "{UTILISATEUR_PRENOM}" : _(u"prenom3") } },
            ]
        self.myOlv.SetDonneesManuelles(listeDonnees, modificationAutorisee=True)
        
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
