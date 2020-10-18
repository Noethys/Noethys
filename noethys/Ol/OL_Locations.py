#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import GestionDB
import FonctionsPerso
import six
from Utils import UTILS_Titulaires
from Utils import UTILS_Interface
from Utils import UTILS_Questionnaires
from Utils import UTILS_Dates
from Utils import UTILS_Gestion
from Utils import UTILS_Historique
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
from Dlg import DLG_Messagebox


def Supprimer_location(parent, IDlocation=None):
    gestion = UTILS_Gestion.Gestion(None)

    def GetLocations(condition=""):
        DB = GestionDB.DB()
        # Récupère les infos sur cette location
        req = """SELECT IDlocation, IDfamille, date_debut, date_fin, serie, produits.nom, produits_categories.nom
        FROM locations 
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE %s;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        liste_resultats = []
        for IDlocation, IDfamille, date_debut, date_fin, serie, nom_produit, nom_categorie in listeDonnees:
            if isinstance(date_debut, str) or isinstance(date_debut, six.text_type):
                date_debut = datetime.datetime.strptime(date_debut, "%Y-%m-%d %H:%M:%S")
            if date_fin == None:
                date_fin = datetime.datetime(2999, 1, 1)
            if isinstance(date_fin, str) or isinstance(date_fin, six.text_type):
                date_fin = datetime.datetime.strptime(date_fin, "%Y-%m-%d %H:%M:%S")
            periode = _(u"%s - %s") % (date_debut.strftime("%d/%m/%Y %H:%M:%S"), date_fin.strftime("%d/%m/%Y %H:%M:%S") if (date_fin and date_fin.year != 2999) else _(u"Illimitée"))
            label_produit = u"%s (%s)" % (nom_produit, nom_categorie)
            liste_resultats.append({"IDlocation": IDlocation, "IDfamille": IDfamille, "date_debut": date_debut, "date_fin": date_fin, "periode": periode, "label_produit": label_produit, "serie": serie, "prestations": []})
        return liste_resultats

    # Importe de la location cliquée
    liste_locations = GetLocations(condition="IDlocation=%d" % IDlocation)

    # Vérifie si la location est dans une série
    if liste_locations[0]["serie"]:
        num_serie = liste_locations[0]["serie"]
        liste_locations_serie = GetLocations(condition="serie='%s'" % num_serie)

        introduction = _(u"Cette location fait partie d'une série de %d occurences.") % len(liste_locations_serie)
        conclusion = _(u"Que souhaitez-vous supprimer ?")
        dlg = DLG_Messagebox.Dialog(None, titre=_(u"Confirmation"), introduction=introduction, conclusion=conclusion,
                                    icone=wx.ICON_QUESTION, boutons=[_(u"L'occurence sélectionnée"), _(u"Toutes les occurences de la série"), _(u"Annuler")])
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == 2:
            return False
        if reponse == 1:
            liste_locations = liste_locations_serie

    # Vérifie si les prestations de cette location sont déjà facturées
    liste_anomalies = []
    liste_valides = []

    DB = GestionDB.DB()
    index = 0
    for dict_location in liste_locations:
        valide = True

        req = """SELECT
        IDprestation, date, IDfacture
        FROM prestations 
        WHERE categorie="location" and IDdonnee=%d;""" % dict_location["IDlocation"]
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeIDprestations = []
        listePrestations = []
        nbrePrestationsFacturees = 0
        for IDprestation, date, IDfacture in listeDonnees:
            date = UTILS_Dates.DateEngEnDateDD(date)
            listePrestations.append({"IDprestation" : IDprestation, "date" : date, "IDfacture" : IDfacture})
            listeIDprestations.append(IDprestation)

            # Vérifie la période de gestion
            if gestion.Verification("prestations", date) == False:
                liste_anomalies.append(u"Location du %s : Impossible à supprimer car une prestation associée est comprise dans une période de gestion verrouillée")
                valide = False

            if IDfacture != None :
                nbrePrestationsFacturees += 1

        liste_locations[index]["prestations"] = listeIDprestations

        if nbrePrestationsFacturees > 0:
            liste_anomalies.append(u"Location du %s : Impossible à supprimer car %d prestations y sont déjà associées" % (dict_location["periode"], nbrePrestationsFacturees))
            valide = False

        if valide:
            liste_valides.append(dict_location)
        index += 1

    DB.Close()

    # Annonce les anomalies trouvées
    if len(liste_anomalies) > 0:
        introduction = _(u"%d anomalies ont été détectées :") % len(liste_anomalies)
        if len(liste_valides) > 0:
            conclusion = _(u"Souhaitez-vous continuer avec les %d autres locations ?") % len(liste_valides)
            dlg = DLG_Messagebox.Dialog(None, titre=_(u"Anomalies"), introduction=introduction, detail=u"\n".join(liste_anomalies), conclusion=conclusion, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Oui"), _(u"Non"), _(u"Annuler")])
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse in (1, 2):
                return False
        else:
            dlg = DLG_Messagebox.Dialog(None, titre=_(u"Anomalies"), introduction=introduction, detail=u"\n".join(liste_anomalies), icone=wx.ICON_EXCLAMATION, boutons=[_(u"Fermer")])
            reponse = dlg.ShowModal()
            dlg.Destroy()
            return False

    # Suppression
    if len(liste_valides) == 1:
        dlg = wx.MessageDialog(parent, _(u"Souhaitez-vous vraiment supprimer la location ?"), _(u"Confirmation de suppression"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
    else:
        introduction = _(u"Confirmez-vous la suppression des %d locations suivantes :") % len(liste_valides)
        liste_locations_temp = [dict_location["periode"] for dict_location in liste_valides]
        dlg = DLG_Messagebox.Dialog(None, titre=_(u"Confirmation de suppression"), introduction=introduction, detail=u"\n".join(liste_locations_temp), icone=wx.ICON_EXCLAMATION, boutons=[_(u"Oui"), _(u"Non"), _(u"Annuler")])
        reponse = dlg.ShowModal()
        dlg.Destroy()

    if reponse not in (0, wx.ID_YES):
        return False

    DB = GestionDB.DB()
    for dict_location in liste_valides:
        # Suppression
        DB.ReqDEL("locations", "IDlocation", dict_location["IDlocation"])
        DB.ExecuterReq("DELETE FROM questionnaire_reponses WHERE type='location' AND IDdonnee=%d;" % dict_location["IDlocation"])
        DB.ReqMAJ("locations_demandes", [("statut", "attente"), ], "IDlocation", dict_location["IDlocation"])
        DB.ReqMAJ("locations_demandes", [("IDlocation", None), ], "IDlocation", dict_location["IDlocation"])
        DB.ExecuterReq("DELETE FROM prestations WHERE categorie='location' AND IDdonnee=%d;" % dict_location["IDlocation"])
        for IDprestation in dict_location["prestations"]:
            DB.ReqDEL("ventilation", "IDprestation", IDprestation)
        # Historique
        texte_historique = _(u"Suppression de la location ID%d : %s %s") % (dict_location["IDlocation"], dict_location["label_produit"], dict_location["periode"])
        UTILS_Historique.InsertActions([{"IDfamille": dict_location["IDfamille"], "IDcategorie": 39, "action": texte_historique, "IDdonnee": dict_location["IDlocation"]}], DB=DB)
    DB.Close()

    return True



class Track(object):
    def __init__(self, listview=None, donnees=None):
        self.IDlocation = donnees[0]
        self.IDfamille = donnees[1]
        self.IDproduit = donnees[2]
        self.observations = donnees[3]
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.quantite = donnees[6]
        self.nomProduit = donnees[7]
        self.nomCategorie = donnees[8]

        if self.quantite == None :
            self.quantite = 1

        # Période
        if isinstance(self.date_debut, str) or isinstance(self.date_debut, six.text_type) :
            self.date_debut = datetime.datetime.strptime(self.date_debut, "%Y-%m-%d %H:%M:%S")

        if isinstance(self.date_fin, str) or isinstance(self.date_fin, six.text_type) :
            self.date_fin = datetime.datetime.strptime(self.date_fin, "%Y-%m-%d %H:%M:%S")

        # Récupération des réponses des questionnaires
        for dictQuestion in listview.liste_questions :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], listview.GetReponse(dictQuestion["IDquestion"], self.IDproduit))

        # Famille
        if listview.IDfamille == None :
            self.nomTitulaires = listview.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
            self.rue = listview.dict_titulaires[self.IDfamille]["adresse"]["rue"]
            self.cp = listview.dict_titulaires[self.IDfamille]["adresse"]["cp"]
            self.ville = listview.dict_titulaires[self.IDfamille]["adresse"]["ville"]

        # Durée
        self.duree = None
        if self.date_debut != None and self.date_fin != None:
            self.duree = (self.date_fin.date() - self.date_debut.date()).days

        # jours restants
        self.temps_restant = None
        if self.date_debut != None and self.date_fin != None:
            self.temps_restant = (self.date_fin.date() - datetime.date.today()).days






class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.IDproduit = kwds.pop("IDproduit", None)
        self.checkColonne = kwds.pop("checkColonne", False)
        self.afficher_uniquement_actives = kwds.pop("afficher_uniquement_actives", False)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.dirty = False

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        # Initialisation des questionnaires
        categorie = "location"
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type=categorie)
        self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type=categorie)

        # MAJ du listview
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        liste_conditions = []

        if self.IDfamille != None :
            liste_conditions.append("IDfamille=%d" % self.IDfamille)
        if self.IDproduit != None :
            liste_conditions.append("locations.IDproduit=%d" % self.IDproduit)
        if self.afficher_uniquement_actives == True :
            today = datetime.datetime.now()
            liste_conditions.append("locations.date_debut<='%s' AND (locations.date_fin IS NULL OR locations.date_fin>='%s')" % (today, today))

        if len(liste_conditions) > 0 :
            conditions = "WHERE %s" % " AND ".join(liste_conditions)
        else :
            conditions = ""

        listeID = None
        db = GestionDB.DB()
        req = """SELECT locations.IDlocation, locations.IDfamille, locations.IDproduit, 
        locations.observations, locations.date_debut, locations.date_fin, locations.quantite,
        produits.nom, 
        produits_categories.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        %s;""" % conditions
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
                track = Track(listview=self, donnees=item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        self.AddNamedImages("attention", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Reservation.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("pasok", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Refus.png"), wx.BITMAP_TYPE_PNG))

        def FormateDate(date):
            if date == None :
                return _(u"Non définie")
            else :
                return datetime.datetime.strftime(date, "%d/%m/%Y - %Hh%M")

        def FormateJoursRestants(temps_restant):
            if temps_restant == None:
                return ""
            else:
                return str(temps_restant)

        def GetImageReste(track):
            if track.temps_restant != None:
                if track.temps_restant < 0:
                    return "pasok"
                elif track.temps_restant < track.duree * 10 // 100:
                    return "attention"
            return None

        dict_colonnes = {
            "IDlocation" : ColumnDefn(u"", "left", 0, "IDlocation", typeDonnee="entier"),
            "date_debut" : ColumnDefn(_(u"Début"), "left", 130, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            "date_fin" : ColumnDefn(_(u"Fin"), "left", 130, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            "nomProduit" : ColumnDefn(_(u"Nom du produit"), 'left', 200, "nomProduit", typeDonnee="texte"),
            "nomCategorie" : ColumnDefn(_(u"Catégorie du produit"), 'left', 200, "nomCategorie", typeDonnee="texte"),
            "quantite": ColumnDefn(u"Qté", "left", 60, "quantite", typeDonnee="entier"),
            "nomTitulaires" : ColumnDefn(_(u"Loueur"), 'left', 270, "nomTitulaires", typeDonnee="texte"),
            "rue" : ColumnDefn(_(u"Rue"), 'left', 200, "rue", typeDonnee="texte"),
            "cp" : ColumnDefn(_(u"C.P."), 'left', 70, "cp", typeDonnee="texte"),
            "ville" : ColumnDefn(_(u"Ville"), 'left', 150, "ville", typeDonnee="texte"),
            "nbre_jours_restants": ColumnDefn(u"Jours restants", "left", 60, "temps_restant", typeDonnee="entier", imageGetter=GetImageReste, stringConverter=FormateJoursRestants),
            }

        liste_temp = ["IDlocation", "date_debut", "date_fin", "nomProduit", "nomCategorie", "quantite", "nomTitulaires", "rue", "cp", "ville", "nbre_jours_restants"]

        if self.IDfamille != None :
            liste_temp = ["IDlocation", "date_debut", "date_fin", "nomProduit", "nomCategorie", "quantite", "nbre_jours_restants"]

        if self.IDproduit != None :
            liste_temp = ["IDlocation", "date_debut", "date_fin", "quantite", "nomTitulaires", "rue", "cp", "ville", "nbre_jours_restants"]

        liste_Colonnes = []
        for code in liste_temp :
            liste_Colonnes.append(dict_colonnes[code])

        # Ajout des questions des questionnaires
        liste_Colonnes.extend(UTILS_Questionnaires.GetColonnesForOL(self.liste_questions))

        # self.SetColumns(liste_Colonnes)
        self.SetColumns2(colonnes=liste_Colonnes, nomListe="OL_Locations")

        if self.checkColonne == True :
            self.CreateCheckStateColumn(1)
            self.SetSortColumn(self.columns[2])
        else :
            self.SetSortColumn(self.columns[1])

        self.SetEmptyListMsg(_(u"Aucune location"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))

        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if self.IDfamille == None:
            self.dict_titulaires = UTILS_Titulaires.GetTitulaires()
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

    def GetReponse(self, IDquestion=None, ID=None):
        if IDquestion in self.dict_questionnaires :
            if ID in self.dict_questionnaires[IDquestion] :
                return self.dict_questionnaires[IDquestion][ID]
        return u""

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
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

        # Item Imprimer
        item = wx.MenuItem(menuPop, 100, _(u"Imprimer la location"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ImprimerPDF, id=100)
        if noSelection == True : item.Enable(False)

        # Item Envoyer par Email
        item = wx.MenuItem(menuPop, 110, _(u"Envoyer la location par Email"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=110)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des locations"))

        # Commandes standards
        self.AjouterCommandesMenuContext(menuPop)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDlocation=None, IDfamille=self.IDfamille, IDproduit=self.IDproduit)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDlocation())
            self.dirty = True
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDlocation=track.IDlocation, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDlocation())
            self.dirty = True
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        resultat = Supprimer_location(self, IDlocation=track.IDlocation)
        if resultat == True :
            self.MAJ()
            self.dirty = True

    def ImprimerPDF(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à imprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDlocation = self.Selection()[0].IDlocation
        from Utils import UTILS_Locations
        location = UTILS_Locations.Location()
        location.Impression(listeLocations=[IDlocation,])

    def EnvoyerEmail(self, event):
        """ Envoyer la location par Email """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à envoyer par Email !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Envoi du mail
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=track.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("LOCATION", "pdf") , categorie="location")

    def CreationPDF(self, nomDoc="", afficherDoc=True):
        """ Création du PDF pour Email """
        IDlocation = self.Selection()[0].IDlocation
        from Utils import UTILS_Locations
        location = UTILS_Locations.Location()
        resultat = location.Impression(listeLocations=[IDlocation,], nomDoc=nomDoc, afficherDoc=False)
        if resultat == False :
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[IDlocation]

    def GetID(self):
        track = self.Selection()[0]
        return track.IDlocation

    def SetID(self, IDlocation=None):
        for track in self.donnees :
            if track.IDlocation == IDlocation :
                self.SelectObject(track, deselectOthers=True, ensureVisible=True)
                return True
        return False

    def GetTracksCoches(self):
        return self.GetCheckedObjects()


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date_debut": {"mode": "nombre", "singulier": _(u"location"), "pluriel": _(u"locations"), "alignement": wx.ALIGN_CENTER},
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
        self.myOlv = ListView(panel, id=-1, afficher_uniquement_actives=False, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
