#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
from Utils import UTILS_Dates
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Titulaires
from Utils import UTILS_Interface
from Utils import UTILS_Parametres
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter,  CTRL_Outils, PanelAvecFooter
from Ol import OL_Soldes
from Ol import OL_Individus
from Utils import UTILS_Archivage
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


class Track_famille(object):
    def __init__(self, parent, donnees):
        self.IDfamille = donnees[0]
        self.ID = self.IDfamille
        self.etat = donnees[1]

        self.nomTitulaires = parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        self.solde = 0.0
        self.IDcompte_payeur = None

        if parent.dict_soldes.has_key(self.IDfamille):
            track_solde = parent.dict_soldes[self.IDfamille]
            self.solde = track_solde.solde
            self.IDcompte_payeur = track_solde.IDcompte_payeur

class Track_individu(object):
    def __init__(self, parent, donnees):
        self.IDindividu = donnees[0]
        self.ID = self.IDindividu
        self.nom = donnees[1]
        self.prenom = donnees[2]
        self.date_naiss = donnees[3]
        self.etat = donnees[4]



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.mode = kwds.pop("mode", "familles")
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.donnees = []
        self.itemSelected = False
        self.popupIndex = -1
        self.filtre = None
        self.dict_soldes = self.GetSoldes()
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def GetSoldes(self):
        dict_soldes = {}
        liste_soldes = OL_Soldes.Importation()
        for track in liste_soldes :
            dict_soldes[track.IDfamille] = track
        return dict_soldes

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        if self.mode == "familles" :
            req = """SELECT IDfamille, etat FROM familles WHERE etat IS NULL OR etat='archive';"""
        else :
            req = """SELECT IDindividu, nom, prenom, date_naiss, etat FROM individus WHERE etat IS NULL OR etat='archive';"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        listeListeView = []
        for item in listeDonnees :

            # Filtre
            valide = True
            ID = item[0]
            if self.filtre != None :

                # Filtre sans activité
                if self.filtre["type_filtre"] == "sans" and ID in self.filtre["liste"] :
                    valide = False

                # Filtre avec activité
                if self.filtre["type_filtre"] == "avec" and ID not in self.filtre["liste"] :
                    valide = False

            if valide == True :
                if self.mode == "familles" :
                    track = Track_famille(self, item)
                else :
                    track = Track_individu(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track

        return listeListeView
      
    def InitObjectListView(self):
        # Images
        self.imgArchive = self.AddNamedImages("archive", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Archiver.png"), wx.BITMAP_TYPE_PNG))
        self.imgEfface = self.AddNamedImages("efface", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_PNG))
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateEtat(etat):
            if etat == "archive" :
                return _(u"Archivé")
            elif etat == "efface" :
                return _(u"Effacé")
            else :
                return ""

        def GetImageEtat(track):
            return track.etat

        def FormateSolde(montant):
            if montant == None :
                return u""
            if montant == 0.0 :
                return u"%.2f %s" % (montant, SYMBOLE)
            if montant > FloatToDecimal(0.0) :
                return u"+ %.2f %s" % (montant, SYMBOLE)
            if montant < FloatToDecimal(0.0) :
                return u"- %.2f %s" % (-montant, SYMBOLE)

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        def FormateAge(age):
            if age == None: return ""
            return _(u"%d ans") % age

        if self.mode == "familles" :
            liste_Colonnes = [
                ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
                ColumnDefn(_(u"Famille"), 'left', 350, "nomTitulaires", typeDonnee="texte"),
                ColumnDefn(_(u"Solde"), 'right', 110, "solde", typeDonnee="montant", stringConverter=FormateSolde),
                ]
        else :
            liste_Colonnes = [
                ColumnDefn(_(u"ID"), "left", 0, "IDindividu", typeDonnee="entier"),
                ColumnDefn(_(u"Nom"), 'left', 180, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Prénom"), 'left', 180, "prenom", typeDonnee="texte"),
                ColumnDefn(_(u"Date naiss."), "left", 100, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
                ]

        liste_Colonnes.append(ColumnDefn(_(u"Etat"), "left", 120, "etat", typeDonnee="texte", stringConverter=FormateEtat, imageGetter=GetImageEtat))

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        if self.mode == "familles":
            self.SetEmptyListMsg(_(u"Aucune famille"))
        else :
            self.SetEmptyListMsg(_(u"Aucune individu"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)

    def MAJ(self, ID=None):
        if self.mode == "familles":
            self.dict_titulaires = UTILS_Titulaires.GetTitulaires(inclure_archives=True)
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

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre": _(u"Liste des %s") % self.mode,
            "total": _(u"> %s %s") % (len(self.donnees), self.mode),
            "orientation": wx.PORTRAIT,
        }
        return dictParametres

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des %s") % self.mode)
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des %s") % self.mode)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def OuvrirFicheFamille(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        if self.mode == "familles":

            # Mode familles
            from Dlg import DLG_Famille
            dlg = DLG_Famille.Dialog(self, track.IDfamille)
            if dlg.ShowModal() == wx.ID_OK:
                self.MAJ(track.IDfamille)
            dlg.Destroy()

        else :

            # Mode individus
            IDindividu = track.IDindividu

            rattachements, dictTitulaires, txtTitulaires = OL_Individus.GetRattachements(IDindividu)
            if rattachements != None:
                rattachements.sort()

            # Rattaché à aucune famille
            if rattachements == None:
                dlg = wx.MessageDialog(self, _(u"Cet individu n'est rattaché à aucune famille.\n\nSouhaitez-vous ouvrir sa fiche individuelle ?"), _(u"Confirmation"), wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse != wx.ID_YES:
                    return False
                else:
                    # Ouverture de la fiche individuelle
                    from Dlg import DLG_Individu
                    dlg = DLG_Individu.Dialog(None, IDindividu=IDindividu)
                    if dlg.ShowModal() == wx.ID_OK:
                        pass
                    dlg.Destroy()
                    self.MAJ()
                    return

            # Rattachée à une seule famille
            elif len(rattachements) == 1:
                IDcategorie, IDfamille, titulaire = rattachements[0]
            # Rattachée à plusieurs familles
            else:
                listeNoms = []
                for IDcategorie, IDfamille, titulaire in rattachements:
                    nomTitulaires = dictTitulaires[IDfamille]
                    if IDcategorie == 1:
                        nomCategorie = _(u"représentant")
                        if titulaire == 1:
                            nomCategorie += _(u" titulaire")
                    if IDcategorie == 2: nomCategorie = _(u"enfant")
                    if IDcategorie == 3: nomCategorie = _(u"contact")
                    listeNoms.append(_(u"%s (en tant que %s)") % (nomTitulaires, nomCategorie))
                dlg = wx.SingleChoiceDialog(self, _(u"Cet individu est rattaché à %d familles.\nLa fiche de quelle famille souhaitez-vous ouvrir ?") % len(listeNoms), _(u"Rattachements multiples"), listeNoms, wx.CHOICEDLG_STYLE)
                IDfamilleSelection = None
                if dlg.ShowModal() == wx.ID_OK:
                    indexSelection = dlg.GetSelection()
                    IDcategorie, IDfamille, titulaire = rattachements[indexSelection]
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    return

            # Ouverture de la fiche famille
            if IDfamille != None and IDfamille != -1:
                from Dlg import DLG_Famille
                dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille)
                if dlg.ShowModal() == wx.ID_OK:
                    self.MAJ(IDindividu)
                try:
                    dlg.Destroy()
                except:
                    pass

    def Archiver(self):
        self.ModifierArchivage("archiver")

    def Desarchiver(self):
        self.ModifierArchivage("desarchiver")

    def ModifierArchivage(self, etat="archiver"):
        listeID = []
        for track in self.GetTracksCoches():
            listeID.append(track.ID)

        if len(listeID) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une ligne !"), _(u"Action impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        resultat = False
        archivage = UTILS_Archivage.Archivage()
        if self.mode == "familles" :
            resultat = archivage.Archiver(etat, liste_familles=listeID)
        if self.mode == "individus" :
            resultat = archivage.Archiver(etat, liste_individus=listeID)
        if resultat == True:
            self.MAJ()

    def Effacer(self):
        listeID = []
        for track in self.GetTracksCoches():
            listeID.append(track.ID)

        if len(listeID) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une ligne !"), _(u"Action impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        resultat = False
        archivage = UTILS_Archivage.Archivage()
        if self.mode == "familles" :
            resultat = archivage.Effacer(liste_familles=listeID)
        if self.mode == "individus" :
            resultat = archivage.Effacer(liste_individus=listeID)
        if resultat == True:
            self.MAJ()

    def SetFiltre(self, filtre=None):
        if filtre == None :
            self.filtre = None
            self.MAJ()
            return

        type_filtre, date_limite = filtre

        liste = []

        DB = GestionDB.DB()

        if self.mode == "familles" :

            # MODE FAMILLES

            # Recherche les prestations
            req = """SELECT IDfamille, COUNT(IDprestation)
            FROM prestations
            WHERE date>='%s'
            GROUP BY IDfamille
            ;""" % date_limite
            DB.ExecuterReq(req)
            listePrestations = DB.ResultatReq()
            for IDfamille, nbre_prestations in listePrestations :
                if nbre_prestations > 0 and IDfamille not in liste :
                    liste.append(IDfamille)

            # Recherche les consommations
            req = """SELECT comptes_payeurs.IDfamille, COUNT(IDconso)
            FROM consommations
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
            WHERE date>='%s'
            GROUP BY comptes_payeurs.IDfamille
            ;""" % date_limite
            DB.ExecuterReq(req)
            listeConsommations = DB.ResultatReq()
            for IDfamille, nbre_conso in listeConsommations :
                if nbre_conso > 0 and IDfamille not in liste :
                    liste.append(IDfamille)

            # Recherche les inscriptions
            req = """SELECT IDfamille, date_inscription
            FROM inscriptions
            WHERE date_inscription>='%s'
            GROUP BY IDfamille
            ;""" % date_limite
            DB.ExecuterReq(req)
            listeInscriptions = DB.ResultatReq()
            for IDfamille, date_inscription in listeInscriptions :
                if IDfamille not in liste :
                    liste.append(IDfamille)

            # Recherche les familles
            req = """SELECT IDfamille, date_creation
            FROM familles
            WHERE date_creation>='%s'
            ;""" % date_limite
            DB.ExecuterReq(req)
            listeFamilles = DB.ResultatReq()
            for IDfamille, date_creation in listeFamilles :
                if IDfamille not in liste :
                    liste.append(IDfamille)

        else :

            # MODE INDIVIDUS

            # Recherche les prestations
            req = """SELECT IDindividu, COUNT(IDprestation)
            FROM prestations
            WHERE date>='%s'
            GROUP BY IDindividu
            ;""" % date_limite
            DB.ExecuterReq(req)
            listePrestations = DB.ResultatReq()
            for IDindividu, nbre_prestations in listePrestations:
                if nbre_prestations > 0 and IDindividu not in liste:
                    liste.append(IDindividu)

            # Recherche les consommations
            req = """SELECT IDindividu, COUNT(IDconso)
            FROM consommations
            WHERE date>='%s'
            GROUP BY IDindividu
            ;""" % date_limite
            DB.ExecuterReq(req)
            listeConsommations = DB.ResultatReq()
            for IDindividu, nbre_conso in listeConsommations:
                if nbre_conso > 0 and IDindividu not in liste:
                    liste.append(IDindividu)

            # Recherche les inscriptions
            req = """SELECT IDindividu, date_inscription
            FROM inscriptions
            WHERE date_inscription>='%s'
            GROUP BY IDindividu
            ;""" % date_limite
            DB.ExecuterReq(req)
            listeInscriptions = DB.ResultatReq()
            for IDindividu, date_inscription in listeInscriptions:
                if IDindividu not in liste:
                    liste.append(IDindividu)

            # Recherche les individus
            req = """SELECT IDindividu, date_creation
            FROM individus
            WHERE date_creation>='%s'
            ;""" % date_limite
            DB.ExecuterReq(req)
            listeIndividus = DB.ResultatReq()
            for IDindividu, date_creation in listeIndividus:
                if IDindividu not in liste:
                    liste.append(IDindividu)

        DB.Close()

        self.filtre = {"type_filtre" : type_filtre, "liste" : liste}
        self.MAJ()


# -------------------------------------------------------------------------------------------------------------------------------------------
class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        if kwargs["mode"] == "familles" :
            dictColonnes = {"nomTitulaires": {"mode": "nombre", "singulier": _(u"famille"), "pluriel": _(u"familles"), "alignement": wx.ALIGN_CENTER},}
        else :
            dictColonnes = {"nom": {"mode": "nombre", "singulier": _(u"individu"), "pluriel": _(u"individus"), "alignement": wx.ALIGN_CENTER}, }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, mode="familles", name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
