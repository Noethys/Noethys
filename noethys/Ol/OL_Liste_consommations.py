#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Historique
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Gestion
from Utils import UTILS_Config
from Utils import UTILS_Titulaires
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils import UTILS_Interface, UTILS_Dates, UTILS_Questionnaires
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

        
class Track(object):
    def __init__(self, parent, donnees):
        self.parent = parent
        self.IDconso = donnees[0]
        self.date = UTILS_Dates.DateEngEnDateDD(donnees[1])
        self.etat = donnees[2]
        self.date_saisie = UTILS_Dates.DateEngEnDateDD(donnees[3])
        self.quantite = donnees[4]
        self.nom = donnees[5]
        self.prenom = donnees[6]
        self.nom_unite = donnees[7]
        self.nom_activite = donnees[8]
        self.nom_groupe = donnees[9]
        self.IDfamille = donnees[10]
        self.heure_debut = donnees[11]
        self.heure_fin = donnees[12]
        self.forfait = donnees[13]
        self.nom_evenement = donnees[14]
        self.IDprestation = donnees[15]
        self.label_prestation = donnees[16]
        self.montant_prestation = donnees[17]
        self.IDindividu = donnees[18]

        # Récupération du nom des titulaires
        try :
            self.nomTitulaires = self.parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        except :
            self.nomTitulaires = _(" ")

        # Récupération des réponses des questionnaires
        for dictQuestion in self.parent.LISTE_QUESTIONS :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], self.parent.GetReponse(dictQuestion["IDquestion"], self.IDindividu))

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []

        # Importation des titulaires
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Importation des questionnaires
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        # Récupération des questionnaires
        self.LISTE_QUESTIONS = self.UtilsQuestionnaires.GetQuestions(type="individu")
        self.DICT_QUESTIONNAIRES = self.UtilsQuestionnaires.GetReponses(type="individu")

        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        criteres = ""

        # Filtres
        if len(self.listeFiltres) > 0 :
            filtreStr = " AND ".join(self.listeFiltres)
            if criteres == "" :
                criteres = "WHERE " + filtreStr
            else :
                criteres = criteres + " AND " + filtreStr

        db = GestionDB.DB()
        req = """SELECT 
        IDconso, consommations.date, consommations.etat, date_saisie, quantite,
        individus.nom, individus.prenom,
        unites.nom, activites.nom, groupes.nom,
        inscriptions.IDfamille,
        consommations.heure_debut, consommations.heure_fin, consommations.forfait,
        evenements.nom,
        consommations.IDprestation, prestations.label, prestations.montant, individus.IDindividu
        FROM consommations
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = consommations.IDgroupe
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        LEFT JOIN evenements ON evenements.IDevenement = consommations.IDevenement
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        %s
        ;""" % criteres
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        
        listeListeView = []
        for item in listeDonnees :
            track = Track(self, item)
            listeListeView.append(track)
            if self.selectionID == item[0] :
                self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        def Formate_forfait(forfait):
            if forfait == 1: return "Forfait non verrouillé"
            if forfait == 2: return "Forfait verrouillé"
            return ""

        def FormateEtat(etat):
            if etat == "reservation": return _(u"Réservation")
            if etat == "attente": return _(u"Attente")
            if etat == "refus": return _(u"Refus")
            if etat == "present": return _(u"Présent")
            if etat == "absentj": return _(u"Absence justifiée")
            if etat == "absenti": return _(u"Absence injustifiée")

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDconso", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 90, "date", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Activité"), 'left', 120, "nom_activite", typeDonnee="texte"),
            ColumnDefn(_(u"Unité"), 'left', 100, "nom_unite", typeDonnee="texte"),
            ColumnDefn(_(u"Etat"), 'left', 100, "etat", typeDonnee="texte", stringConverter=FormateEtat),
            ColumnDefn(_(u"Groupe"), 'left', 100, "nom_groupe", typeDonnee="texte"),
            ColumnDefn(_(u"Nom"), 'left', 120, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Prénom"), 'left', 120, "prenom", typeDonnee="texte"),
            ColumnDefn(_(u"Famille"), 'left', 160, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Date de saisie"), 'left', 90, "date", typeDonnee="date_saisie", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Début"), 'left', 60, "heure_debut", typeDonnee="texte"),
            ColumnDefn(_(u"Fin"), 'left', 60, "heure_fin", typeDonnee="texte"),
            ColumnDefn(_(u"Forfait"), 'left', 100, "forfait", typeDonnee="texte", stringConverter=Formate_forfait),
            ColumnDefn(_(u"Evénement"), 'left', 110, "evenement", typeDonnee="texte"),
            ColumnDefn(_(u"IDprestation"), "left", 80, "IDprestation", typeDonnee="entier"),
            ColumnDefn(_(u"Label prestation"), 'left', 140, "label_prestation", typeDonnee="texte"),
            ColumnDefn(_(u"Montant prestation"), 'left', 120, "montant_prestation", typeDonnee="montant", stringConverter=FormateMontant),
        ]

        # Ajout des questions des questionnaires
        liste_Colonnes.extend(UTILS_Questionnaires.GetColonnesForOL(self.LISTE_QUESTIONS))

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune consommation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SortBy(1)
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
        if ID == None :
            self.DefileDernier() 

    def GetReponse(self, IDquestion=None, ID=None):
        if IDquestion in self.DICT_QUESTIONNAIRES :
            if ID in self.DICT_QUESTIONNAIRES[IDquestion] :
                return self.DICT_QUESTIONNAIRES[IDquestion][ID]
        return u""

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDconso
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()
    
        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        intro = u""

        dictParametres = {
            "titre" : _(u"Liste des consommations"),
            "intro" : intro,
            "orientation" : wx.LANDSCAPE,
            }
        return dictParametres

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune consommation à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        # Vérifie l'état
        if track.etat in ("present", "absenti", "absentj"):
            dlg = wx.MessageDialog(self, _(u"Cette consommation ne peut pas être supprimée car elle a déjà été pointée !"), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que le règlement n'est pas dans une période de gestion
        gestion = UTILS_Gestion.Gestion(None)
        if gestion.Verification("consommations", track.date) == False: return False

        # Demande confirmation si prestation associée
        if track.IDprestation:
            dlg = wx.MessageDialog(self, _(u"Attention, cette consommation est associée à la prestation ID%d %s. Cette prestation ne sera pas supprimée automatiquement. Souhaitez-vous tout de même continuer ?") % (track.IDprestation, track.label_prestation), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() != wx.ID_YES:
                return False

        # Demande de confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la suppression de cette consommation ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("consommations", "IDconso", track.IDconso)
            DB.Close()
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDfamille": track.IDfamille,
                "IDcategorie": 10,
                "action": _(u"Suppression de la consommation ID%d : %s le %s pour %s %s") % (track.IDconso, track.nom_unite, track.date, track.nom, track.prenom),
                },])

            # MAJ de l'affichage
            self.MAJ()
        dlg.Destroy()



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
        self.SetSize((800, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
