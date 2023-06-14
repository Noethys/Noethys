#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx, os, datetime, importlib
import GestionDB
from Utils import UTILS_Export_tables


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text




class Exporter(UTILS_Export_tables.Exporter):
    """ Adaptation de l'exportation """
    def __init__(self, categorie="activite", nouveauNom=""):
        UTILS_Export_tables.Exporter.__init__(self, categorie)
        self.nouveauNom = nouveauNom
        
    def Exporter(self, ID=None):
        # Généralités
        if self.nouveauNom != "" :
            remplacementNom = ("nom", self.nouveauNom)
        else :
            remplacementNom = None
        self.ExporterTable("activites", "IDactivite=%d" % ID, remplacement=remplacementNom)
        self.ExporterTable("responsables_activite", "IDactivite=%d" % ID)
        self.ExporterTable("groupes_activites", "IDactivite=%d" % ID)
        # Groupes
        self.ExporterTable("groupes", "IDactivite=%d" % ID)
        # Agréments
        self.ExporterTable("agrements", "IDactivite=%d" % ID)
        # Renseignements
        self.ExporterTable("pieces_activites", "IDactivite=%d" % ID)
        self.ExporterTable("cotisations_activites", "IDactivite=%d" % ID)
        self.ExporterTable("renseignements_activites", "IDactivite=%d" % ID)
        # Unités
        self.ExporterTable("unites", "IDactivite=%d" % ID)
        self.ExporterTable("unites_groupes", self.FormateCondition("IDunite", self.dictID["unites"]))
        self.ExporterTable("unites_incompat", self.FormateCondition("IDunite", self.dictID["unites"]))
        # Etiquettes
        self.ExporterTable("etiquettes", "IDactivite=%d" % ID)
        # Unités de remplissage
        self.ExporterTable("unites_remplissage", "IDactivite=%d" % ID)
        self.ExporterTable("unites_remplissage_unites", self.FormateCondition("IDunite_remplissage", self.dictID["unites_remplissage"]))
        # Calendrier
        self.ExporterTable("ouvertures", "IDactivite=%d" % ID)
        self.ExporterTable("remplissage", "IDactivite=%d" % ID)
        # Tarifs
        self.ExporterTable("categories_tarifs", "IDactivite=%d" % ID)
        self.ExporterTable("categories_tarifs_villes", self.FormateCondition("IDcategorie_tarif", self.dictID["categories_tarifs"]))
        self.ExporterTable("noms_tarifs", "IDactivite=%d" % ID)
        self.ExporterTable("tarifs", "IDactivite=%d" % ID, [
                                                                                ("categories_tarifs", "IDcategorie_tarif", ";"),
                                                                                ("groupes", "IDgroupe", ";"),
                                                                                ])
        self.ExporterTable("combi_tarifs", self.FormateCondition("IDtarif", self.dictID["tarifs"]))
        self.ExporterTable("combi_tarifs_unites", self.FormateCondition("IDtarif", self.dictID["tarifs"]))
        self.ExporterTable("tarifs_lignes", "IDactivite=%d" % ID)
        self.ExporterTable("questionnaire_filtres", self.FormateCondition("IDtarif", self.dictID["tarifs"]))
        # Portail
        self.ExporterTable("portail_periodes", "IDactivite=%d" % ID)
        self.ExporterTable("portail_unites", "IDactivite=%d" % ID)
        # Evènements
        self.ExporterTable("evenements", "IDactivite=%d" % ID)

        # Correspondances spéciales
        self.correspondances_speciales.append({"table" : "etiquettes", "champ" : "parent", "champ_reference" : "IDetiquette"})
        self.correspondances_speciales.append({"table" : "activites", "champ" : "psu_unite_prevision", "champ_reference" : "IDunite"})
        self.correspondances_speciales.append({"table" : "activites", "champ" : "psu_unite_presence", "champ_reference" : "IDunite"})
        self.correspondances_speciales.append({"table" : "activites", "champ" : "psu_tarif_forfait", "champ_reference" : "IDtarif"})
        self.correspondances_speciales.append({"table" : "activites", "champ" : "psu_etiquette_rtt", "champ_reference" : "IDetiquette"})



class Track(object):
    def __init__(self, donnees):
        self.IDactivite = donnees[0]
        self.nom = donnees[1]
        self.abrege = donnees[2]
        self.coords_org = donnees[3]
        self.rue = donnees[4]
        self.cp = donnees[5]
        self.ville = donnees[6]
        self.tel = donnees[7]
        self.fax = donnees[8]
        self.mail = donnees[9]
        self.site = donnees[10]
        self.logo_org = donnees[11]
        self.date_debut = donnees[12]
        self.date_fin = donnees[13]
        self.public = donnees[14]
        self.date_creation = donnees[15]
        self.vaccins_obligatoires = donnees[16]
        
        # Période
        if self.date_debut == "1977-01-01" and self.date_fin == "2999-01-01" :
            self.periode = "illimitee"
            self.labelPeriode = _(u"Illimitée")
        else:
            if self.date_debut != None and self.date_fin != None :
                self.periode = u"%s;%s" % (self.date_fin, self.date_debut)
                self.labelPeriode = _(u"Du %s au %s") % (DateEngFr(self.date_debut), DateEngFr(self.date_fin))
            else:
                self.periode = None
                self.labelPeriode = _(u"Pas de période")

        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDactivite = kwds.pop("IDactivite", None)
        self.modificationAutorisee = kwds.pop("modificationAutorisee", True)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.activites_ouvertes = False
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        if self.modificationAutorisee :
            self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None

        if self.activites_ouvertes:
            conditionDate = "WHERE date_fin >= '%s' " % str(datetime.date.today())
        else:
            conditionDate = ""

        db = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege, coords_org, rue, cp, ville, tel, fax, mail, site, 
        logo_org, date_debut, date_fin, public, date_creation, vaccins_obligatoires
        FROM activites 
        %s
        ORDER BY date_fin, nom;""" % conditionDate
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormatePeriode(periode):
            if periode == None :
                return _(u"Pas de période")
            if periode == "illimitee" :
                return _(u"Illimitée")
            else:
                date_fin, date_debut = periode.split(";")
            return _(u"Du %s au %s") % (DateEngFr(date_debut), DateEngFr(date_fin))

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDactivite", typeDonnee="entier"),
            ColumnDefn(_(u"Nom de l'activité"), 'left', 220, "nom", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Abrégé"), 'left', 90, "abrege", typeDonnee="texte"),
            ColumnDefn(_(u"Période de validité"), 'left', 200, "periode", typeDonnee="texte", stringConverter=FormatePeriode),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune activité"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SortBy(3, False)
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
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDactivite
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        if self.modificationAutorisee :
            
            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

            # Item Modifier
            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
            if noSelection == True : item.Enable(False)
            
            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
            if noSelection == True : item.Enable(False)
            
            menuPop.AppendSeparator()
            
            # Item Dupliquer
            item = wx.MenuItem(menuPop, 60, _(u"Dupliquer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Dupliquer, id=60)
            if noSelection == True : item.Enable(False)

            menuPop.AppendSeparator()

            # Item Importer
            item = wx.MenuItem(menuPop, 80, _(u"Importer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_import.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Importer, id=80)

            # Item Exporter
            item = wx.MenuItem(menuPop, 90, _(u"Exporter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_export.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Exporter, id=90)

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

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des activités"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des activités"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des activités"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des activités"))


    def Ajouter(self, event):        
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_activites", "creer") == False : return

        # Propose assistants de génération d'activités
        from Dlg import DLG_Nouvelle_activite
        dlg = DLG_Nouvelle_activite.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            code = dlg.GetCode()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return

        if code == "nouveau" :
            # Création manuelle de l'activité
            from Dlg import DLG_Activite
            dlg = DLG_Activite.Assistant(self, IDactivite=None)
        else :
            # Création avec assistant de l'activité
            module = importlib.import_module("Ctrl.CTRL_Assistant_%s" % code)
            dlg = module.Dialog(self)

        if dlg.ShowModal() == wx.ID_OK:
            IDactivite = dlg.GetIDactivite()
            self.MAJ(IDactivite)
        dlg.Destroy()



    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDactivite = self.Selection()[0].IDactivite
        nom = self.Selection()[0].nom
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_activites", "modifier", IDactivite=IDactivite) == False : return
        from Dlg import DLG_Activite
        dlg = DLG_Activite.Dialog(self, IDactivite=IDactivite)      
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDactivite)
        dlg.Destroy() 

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDactivite = self.Selection()[0].IDactivite
        nom = self.Selection()[0].nom
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_activites", "supprimer", IDactivite=IDactivite) == False : return
        from Dlg import DLG_Activite
        resultat = DLG_Activite.Supprimer_activite(IDactivite=IDactivite)
        if resultat == True :
            self.MAJ()

    def Dupliquer(self, event):
        """ Dupliquer un modèle """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_activites", "creer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité à dupliquer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDactivite = self.Selection()[0].IDactivite
        nom = self.Selection()[0].nom

        dlg = wx.MessageDialog(None, _(u"Confirmez-vous la duplication de l'activité '%s' ?") % nom, _(u"Duplication"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Exportation
        exportation = Exporter(categorie="activite", nouveauNom=_(u"Copie de %s") % nom)
        exportation.Ajouter(ID=IDactivite, nom=nom)
        contenu = exportation.GetContenu()
        # Importation
        importation = UTILS_Export_tables.Importer(contenu=contenu)
        importation.Ajouter(index=0)
        newIDactivite = importation.GetNewID("IDactivite", IDactivite)
        # MAJ listView
        self.MAJ(newIDactivite)
        
    def Importer(self, event):
        """ Importer """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_activites", "creer") == False : return
        # Ouverture de la fenêtre de dialogue
        wildcard = _(u"Activité Noethys (*.nxa)|*.nxa|Tous les fichiers (*.*)|*.*")
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
        else:
            dlg.Destroy()
            return
        
        # Demande confirmation
        importation = UTILS_Export_tables.Importer(fichier=nomFichierLong)
        nbreChoix = importation.DemandeChoix() 
        
        # Confirmation
        if nbreChoix > 0 :
            dlg = wx.MessageDialog(self, _(u"%d activité(s) ont été importées avec succès.") % nbreChoix, _(u"Importation"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        # MAJ listView
        self.MAJ()

    def Exporter(self, event):
        """ Exporter """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_activites", "consulter") == False : return
        # Demande les activités à exporter
        listeActivites = []
        listeLabels = []
        for track in self.GetObjects() :
            label = u"%s (%s)" % (track.nom, track.labelPeriode)
            listeLabels.append(label)
            listeActivites.append((track.IDactivite, track.nom))

        dlg = wx.MultiChoiceDialog(None, _(u"Sélectionnez les activités à exporter :"), _(u"Exportation"), listeLabels)
        dlg.SetSize((550, 500))
        if dlg.ShowModal() == wx.ID_OK :
            selections = dlg.GetSelections()
        else :
            selections = []
        dlg.Destroy()
        if len(selections) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité à exporter !\n\nExportation annulée."), _(u"Exportation"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        listeSelection = []
        for index in selections :
            listeSelection.append(listeActivites[index])

        # Demande le chemin pour la sauvegarde du fichier
        standardPath = wx.StandardPaths.Get()
        dlg = wx.FileDialog(self, message=_(u"Enregistrer le fichier sous..."),
                            defaultDir = standardPath.GetDocumentsDir(), defaultFile="activites.nxa",
                            wildcard=_(u"Activité Noethys (*.nxa)|*.nxa"), style=wx.FD_SAVE)

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
        exportation = Exporter(categorie="activite")
        for IDactivite, nom in listeSelection :
            exportation.Ajouter(IDactivite, nom)
        exportation.Enregistrer(fichier=path)

        # Confirmation
        dlg = wx.MessageDialog(self, _(u"%d activité(s) ont été exportées avec succès.") % len(listeSelection), _(u"Exportation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()



# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une activité..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 


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
