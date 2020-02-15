#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Titulaires
from Utils import UTILS_Interface
from Utils import UTILS_Internet
from Utils import UTILS_Parametres
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter,  CTRL_Outils, PanelAvecFooter



class Track(object):
    def __init__(self, parent, donnees):
        self.IDfamille = donnees[0]
        self.internet_actif = donnees[1]
        self.internet_identifiant = donnees[2]
        self.internet_mdp = donnees[3]
        if self.internet_mdp.startswith("custom"):
            self.internet_mdp = "********"

        if self.IDfamille in parent.dict_titulaires:
            self.nomTitulaires = parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        else:
            self.nomTitulaires = _(u"Titulaires inconnus")


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.donnees = []
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.filtre_familles = None
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        req = """SELECT IDfamille, internet_actif, internet_identifiant, internet_mdp
        FROM familles
        ;"""
        DB.ExecuterReq(req)
        listeFamilles = DB.ResultatReq()
        DB.Close()

        listeListeView = []
        for item in listeFamilles :

            # Filtre
            valide = True
            IDfamille = item[0]
            if self.filtre_familles != None :

                # Filtre sans activité
                if self.filtre_familles["type_filtre"] == "sans" and IDfamille in self.filtre_familles["liste_familles"] :
                    valide = False

                # Filtre avec activité
                if self.filtre_familles["type_filtre"] == "avec" and IDfamille not in self.filtre_familles["liste_familles"] :
                    valide = False

            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track

        return listeListeView
      
    def InitObjectListView(self):
        # Images
        self.imgActif = self.AddNamedImages("actif", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4.png"), wx.BITMAP_TYPE_PNG))
        self.imgInactif = self.AddNamedImages("inactif", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateActivation(internet_activation):
            if internet_activation == 1 :
                return _(u"Oui")
            else :
                return _(u"Non")

        def GetImageActivation(track):
            if track.internet_actif == 1 :
                return "actif"
            else :
                return "inactif"

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), 'left', 350, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Activation"), "left", 120, "internet_actif", typeDonnee="bool", stringConverter=FormateActivation, imageGetter=GetImageActivation),
            ColumnDefn(_(u"Identifiant"), "left", 120, "internet_identifiant", typeDonnee="texte"),
            ColumnDefn(_(u"Mot de passe"), "left", 120, "internet_mdp", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune famille"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)

    def MAJ(self, ID=None):
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires(inclure_archives=True, afficher_tag_archive=True)
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
            "titre": _(u"Liste des comptes internet"),
            "total": _(u"> %s familles") % len(self.donnees),
            "orientation": wx.PORTRAIT,
        }
        return dictParametres

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des comptes internet"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des comptes internet"))

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
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, track.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDfamille)
        dlg.Destroy()

    def Activer(self, event=None):
        self.SetActivation(1)

    def Desactiver(self, event=None):
        self.SetActivation(0)

    def SetActivation(self, actif=1):
        """ Activation ou désactivation des comptes cochés """
        listeCoches = self.GetTracksCoches()
        if len(listeCoches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucun compte internet à modifier !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if actif == True :
            texte = _(u"activer")
        else :
            texte = _(u"désactiver")
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment %s les %d comptes sélectionnés ?") % (texte, len(listeCoches)), _(u"Modification"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        listeModifications = []
        for track in listeCoches :
            listeModifications.append((actif, track.IDfamille))
        DB = GestionDB.DB()
        DB.Executermany("UPDATE familles SET internet_actif=? WHERE IDfamille=?", listeModifications, commit=False)
        DB.Commit()
        DB.Close()
        self.MAJ()

    def ReinitPasswords(self, event=None):
        """ Régénération des mots de passe """
        listeCoches = self.GetTracksCoches()
        if len(listeCoches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucun compte internet à réinitialiser !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demandes de confirmation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment réinitialiser les mots de passe des %d comptes sélectionnés ?") % len(listeCoches), _(u"Modification"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        dlg = wx.MessageDialog(self, _(u"ATTENTION, TOUS LES MOTS DE PASSE SERONT REINITIALISES !\n\nSouhaitez-vous vraiment regénérer les mots de passe des %d comptes sélectionnés ?") % len(listeCoches), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Récupère la taille des mots de passe
        taille = UTILS_Parametres.Parametres(mode="get", categorie="comptes_internet", nom="taille_passwords", valeur=8)
        dlg = wx.MessageDialog(self, _(u"Les mots de passe comporteront %d caractères.\n\nSi cela vous convient, cliquez sur Oui, sinon annulez et allez dans Menu Paramétrage > Préférences pour modifier la taille des mots de passe des comptes internet.") % taille, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        dlg = wx.MessageDialog(self, _(u"DERNIER AVERTISSEMENT !\n\nConfirmez-vous la réinitialisation des mots de passe ? Vous ne pourrez pas revenir en arrière..."), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Regénération des mots de passe
        listeModifications = []
        for track in listeCoches :
            mdp = UTILS_Internet.CreationMDP(nbreCaract=taille)
            listeModifications.append((mdp, track.IDfamille))

        DB = GestionDB.DB()
        DB.Executermany("UPDATE familles SET internet_mdp=? WHERE IDfamille=?", listeModifications, commit=False)
        DB.Commit()
        DB.Close()
        self.MAJ()

    def SetFiltre(self, filtre=None):
        if filtre == None :
            self.filtre_familles = None
            self.MAJ()
            return

        type_filtre, date_limite = filtre

        liste_familles = []

        DB = GestionDB.DB()

        # Recherche les prestations
        req = """SELECT IDfamille, COUNT(IDprestation)
        FROM prestations
        WHERE date>='%s'
        GROUP BY IDfamille
        ;""" % date_limite
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        for IDfamille, nbre_prestations in listePrestations :
            if nbre_prestations > 0 and IDfamille not in liste_familles :
                liste_familles.append(IDfamille)

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
            if nbre_conso > 0 and IDfamille not in liste_familles :
                liste_familles.append(IDfamille)

        # Recherche les inscriptions
        req = """SELECT IDfamille, date_inscription
        FROM inscriptions
        WHERE date_inscription>='%s'
        GROUP BY IDfamille
        ;""" % date_limite
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        for IDfamille, date_inscription in listeInscriptions :
            if IDfamille not in liste_familles :
                liste_familles.append(IDfamille)

        # Recherche les familles
        req = """SELECT IDfamille, date_creation
        FROM familles
        WHERE date_creation>='%s'
        ;""" % date_limite
        DB.ExecuterReq(req)
        listeFamilles = DB.ResultatReq()
        for IDfamille, date_creation in listeFamilles :
            if IDfamille not in liste_familles :
                liste_familles.append(IDfamille)

        DB.Close()

        self.filtre_familles = {"type_filtre" : type_filtre, "liste_familles" : liste_familles}
        self.MAJ()


# -------------------------------------------------------------------------------------------------------------------------------------------
class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomTitulaires": {"mode": "nombre", "singulier": _(u"famille"), "pluriel": _(u"familles"), "alignement": wx.ALIGN_CENTER},
        }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)

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
