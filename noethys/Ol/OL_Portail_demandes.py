#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
import datetime
from Dlg import DLG_Saisie_portail_demande
from Utils import UTILS_Interface
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates

from Ctrl.CTRL_ObjectListView import GroupListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, parent=None, donnees={}, dictTitulaires={}, dictUtilisateurs={}):
        self.parent = parent

        self.IDaction = donnees["IDaction"]
        self.horodatage = donnees["horodatage"]
        self.IDfamille = donnees["IDfamille"]
        self.IDindividu = donnees["IDindividu"]
        self.IDutilisateur = donnees["IDutilisateur"]

        self.categorie = donnees["categorie"]
        self.FormateCategorie()

        self.action = donnees["action"]
        self.description = donnees["description"]
        self.commentaire = donnees["commentaire"]
        self.parametres = donnees["parametres"]
        self.etat = donnees["etat"]
        self.FormateEtat()

        self.IDperiode = donnees["IDperiode"]
        self.periode_nom = donnees["periode_nom"]
        self.periode_date_debut = donnees["periode_date_debut"]
        self.periode_date_fin = donnees["periode_date_fin"]
        self.periode_IDmodele = donnees["periode_IDmodele"]

        self.traitement_date = donnees["traitement_date"]
        self.reponse = donnees["reponse"]
        self.email_date = donnees["email_date"]

        self.IDpaiement = donnees["IDpaiement"]
        self.ventilation = donnees["ventilation"]

        self.nom_groupe = donnees["nom_groupe"]

        # Nom
        self.nom = ""

        if self.IDfamille != None :
            if self.IDfamille in dictTitulaires :
                self.nom = dictTitulaires[self.IDfamille]["titulairesAvecCivilite"]
                self.IDcompte_payeur = dictTitulaires[self.IDfamille]["IDcompte_payeur"]
                self.ville = dictTitulaires[self.IDfamille]["adresse"]["ville"]
            else :
                self.nom = "?"
                self.IDcompte_payeur = None
                self.ville = None

        if self.IDutilisateur != None :
            if self.IDutilisateur in dictUtilisateurs :
                self.nom = dictUtilisateurs[self.IDutilisateur]
            else :
                self.nom = "?"


    def FormateCategorie(self):
        if self.categorie == "factures" : self.categorie_label = _(u"Factures")
        elif self.categorie == "reglements" : self.categorie_label = _(u"R�glements")
        elif self.categorie == "inscriptions" : self.categorie_label = _(u"Inscriptions")
        elif self.categorie == "reservations" : self.categorie_label = _(u"R�servations")
        elif self.categorie == "renseignements": self.categorie_label = _(u"Renseignements")
        elif self.categorie == "locations": self.categorie_label = _(u"Locations")
        elif self.categorie == "pieces": self.categorie_label = _(u"Pi�ces")
        elif self.categorie == "compte":self.categorie_label = _(u"Compte")
        else : self.categorie_label = _(u"")

    def FormateEtat(self):
        if self.etat == "attente" : self.etat_label = _(u"En attente")
        elif self.etat == "validation" : self.etat_label = _(u"Trait�")
        else : self.etat_label = _(u"")

    def Refresh(self):
        self.FormateCategorie()
        self.FormateEtat()
        self.parent.RefreshObject(self)

    def Select(self):
        self.parent.SelectObject(self, ensureVisible=True)

    def EcritLog(self, message=""):
        if self.parent.log != None :
            self.parent.log.EcritLog(message)


    
class ListView(GroupListView):
    def __init__(self, *args, **kwds):
        self.IDfamille = kwds.pop("IDfamille", None)
        # Initialisation du listCtrl
        self.log = None
        self.cacher_traitees = True
        self.regroupement = None
        self.tri = "horodatage"
        GroupListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, event):
        self.Traiter()

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires()

        DB = GestionDB.DB()

        # Importation des noms des utilisateurs
        req = """SELECT IDutilisateur, nom, prenom
        FROM utilisateurs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictUtilisateurs = {}
        for IDutilisateur, nom, prenom in listeDonnees :
            self.dictUtilisateurs[IDutilisateur] = u"%s %s" % (prenom, nom)

        liste_conditions = []
        if self.cacher_traitees == True :
            liste_conditions.append("portail_actions.etat <> 'validation'")

        if self.IDfamille != None :
            liste_conditions.append("portail_actions.IDfamille=%d" % self.IDfamille)

        if len(liste_conditions) > 0 :
            conditions = "WHERE %s" % " AND ".join(liste_conditions)
        else :
            conditions = ""

        # Lecture des r�servations
        req = """SELECT portail_reservations.IDaction, groupes.nom
        FROM portail_reservations
        LEFT JOIN portail_actions ON portail_actions.IDaction = portail_reservations.IDaction
        LEFT JOIN inscriptions ON inscriptions.IDinscription = portail_reservations.IDinscription
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        %s;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dict_inscriptions = {IDaction: nom_groupe for IDaction, nom_groupe in listeDonnees}

        # Lecture Actions
        req = """SELECT IDaction, horodatage, IDfamille, IDindividu, IDutilisateur, categorie, action, description, commentaire, 
        parametres, etat, traitement_date, portail_actions.IDperiode, reponse, email_date, IDpaiement, ventilation,
        portail_periodes.nom, portail_periodes.date_debut, portail_periodes.date_fin, portail_periodes.IDmodele
        FROM portail_actions
        LEFT JOIN portail_periodes ON portail_periodes.IDperiode = portail_actions.IDperiode
        %s;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeActions = []
        for IDaction, horodatage, IDfamille, IDindividu, IDutilisateur, categorie, action, description, commentaire, parametres, etat, traitement_date, IDperiode, reponse, email_date, IDpaiement, ventilation, periode_nom, periode_date_debut, periode_date_fin, periode_IDmodele in listeDonnees :
            traitement_date = UTILS_Dates.DateEngEnDateDD(traitement_date)
            email_date = UTILS_Dates.DateEngEnDateDD(email_date)
            horodatage = UTILS_Dates.DateEngEnDateDDT(horodatage)
            periode_date_debut = UTILS_Dates.DateEngEnDateDD(periode_date_debut)
            periode_date_fin = UTILS_Dates.DateEngEnDateDD(periode_date_fin)
            listeActions.append({
                "IDaction" : IDaction, "horodatage" : horodatage, "IDfamille" : IDfamille, "IDindividu" : IDindividu, "IDutilisateur" : IDutilisateur,
                "categorie" : categorie, "action" : action, "description" : description, "commentaire" : commentaire, "parametres" : parametres,
                "etat" : etat, "traitement_date" : traitement_date, "IDperiode" : IDperiode, "reponse" : reponse, "email_date" : email_date,
                "periode_nom" : periode_nom, "periode_date_debut" : periode_date_debut, "periode_date_fin" : periode_date_fin,
                "periode_IDmodele" : periode_IDmodele, "IDpaiement" : IDpaiement, "ventilation" : ventilation,
                "nom_groupe": dict_inscriptions.get(IDaction, None),
            })

        listeListeView = []
        for action in listeActions :
            listeListeView.append(Track(self, action, self.dictTitulaires, self.dictUtilisateurs))
        return listeListeView
      
    def InitObjectListView(self):          
        # Images
        #self.image_attente = self.AddNamedImages("attente", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attente.png"), wx.BITMAP_TYPE_PNG))
        self.image_validation = self.AddNamedImages("validation", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4.png"), wx.BITMAP_TYPE_PNG))
        self.image_reglement = self.AddNamedImages("reglements", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Reglement.png"), wx.BITMAP_TYPE_PNG))
        self.image_facture = self.AddNamedImages("factures", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Facture.png"), wx.BITMAP_TYPE_PNG))
        self.image_inscription = self.AddNamedImages("inscriptions", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Activite.png"), wx.BITMAP_TYPE_PNG))
        self.image_reservation = self.AddNamedImages("reservations", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier_modification.png"), wx.BITMAP_TYPE_PNG))
        self.image_renseignement = self.AddNamedImages("renseignements", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etiquette2.png"), wx.BITMAP_TYPE_PNG))
        self.image_location = self.AddNamedImages("locations", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Location.png"), wx.BITMAP_TYPE_PNG))
        self.image_piece = self.AddNamedImages("pieces", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Piece.png"), wx.BITMAP_TYPE_PNG))
        self.image_compte = self.AddNamedImages("compte", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        self.image_email = self.AddNamedImages("email", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG))

        self.useExpansionColumn = True
        self.oddRowsBackColor = wx.Colour(255, 255, 255)
        self.evenRowsBackColor = wx.Colour(255, 255, 255)

        couleur_verte = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))

        def rowFormatter(listItem, track):
            if track.etat == "validation" :
                listItem.SetBackgroundColour(couleur_verte)

        def GetImageEtat(track):
            return track.etat

        def GetImageCategorie(track):
            return track.categorie

        def FormateHorodatage(horodatage):
            return UTILS_Dates.DateEngEnDateDDT(horodatage).strftime("%d/%m/%Y  %H:%M:%S")

        def FormateDate(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateDDEnFr(dateDD)

        def GetImageEmail(track):
            if track.email_date != None :
                return self.image_email
            else :
                return None

        dictColonnes = {
            "IDaction" : ColumnDefn(_(u"IDaction"), "left", 0, "", typeDonnee="texte"),
            "horodatage" : ColumnDefn(_(u"Horodatage"), "left", 140, "horodatage", typeDonnee="dateheure", stringConverter=FormateHorodatage),
            "etat" : ColumnDefn(_(u"Etat"), "left", 90, "etat_label", typeDonnee="texte", imageGetter=GetImageEtat),
            "traitement_date" : ColumnDefn(_(u"Trait�e le"), "left", 80, "traitement_date", typeDonnee="date", stringConverter=FormateDate),
            "categorie" : ColumnDefn(_(u"Cat�gorie"), "left", 120, "categorie_label", typeDonnee="texte", imageGetter=GetImageCategorie),
            "nom" : ColumnDefn(_(u"Nom"), "left", 180, "nom", typeDonnee="texte"),
            "description" : ColumnDefn(_(u"Description"), "left", 300, "description", typeDonnee="texte"),
            "periode" : ColumnDefn(_(u"P�riode"), "left", 200, "periode_nom", typeDonnee="texte"),
            "commentaire" : ColumnDefn(_(u"Commentaire"), "left", 200, "commentaire", typeDonnee="texte"),
            "email_date": ColumnDefn(_(u"Email"), "left", 95, "email_date", typeDonnee="date", stringConverter=FormateDate, imageGetter=GetImageEmail),
            "reponse" : ColumnDefn(_(u"R�ponse"), "left", 200, "reponse", typeDonnee="texte"),
            "ville": ColumnDefn(_(u"Ville de r�sidence"), "left", 150, "ville", typeDonnee="texte"),
            "nom_groupe": ColumnDefn(_(u"Groupe"), "left", 120, "nom_groupe", typeDonnee="texte"),
            }

        # Liste des colonnes par d�faut
        liste_colonnes = ["horodatage", "etat", "traitement_date", "categorie", "nom", "description", "periode",
                          "commentaire", "email_date", "reponse", "ville", "nom_groupe"]

        # Regroupement
        if self.regroupement != None :
            self.SetAlwaysGroupByColumn(liste_colonnes.index(self.regroupement))
            self.SetShowGroups(True)
        else :
            liste_colonnes.insert(0, "IDaction")
            self.SetShowGroups(False)
        self.useExpansionColumn = False
        self.showItemCounts = False
        self.rowFormatter = rowFormatter

        listeTemp = []
        for code in liste_colonnes:
            listeTemp.append(dictColonnes[code])
        self.SetColumns2(colonnes=listeTemp, nomListe="OL_Portail_demandes")

        self.SetEmptyListMsg(_(u"Aucune demande"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(dictColonnes[self.tri]) #(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.Freeze()
        self.InitModel()
        self.InitObjectListView()
        self.Thaw()
        #self.CocheListeTout()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Traiter
        item = wx.MenuItem(menuPop, 10, _(u"Traiter la demande"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Traiter, id=10)
        if len(self.Selection()) == 0:
            item.Enable(False)

        menuPop.AppendSeparator()

        # G�n�ration automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des donn�es � synchroniser"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def Commencer(self):
        tracks = self.GetObjects()
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune demande � traiter dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Ouverture de la fen�tre de traitement des demandes
        dlg = DLG_Saisie_portail_demande.Dialog(self, track=tracks[0], tracks=self.GetObjects())
        dlg.ShowModal()
        dlg.Destroy()

    def Traiter(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune ligne � traiter dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        # Ouverture de la fen�tre de traitement des demandes
        dlg = DLG_Saisie_portail_demande.Dialog(self, track=track, tracks=self.GetObjects())
        dlg.ShowModal()
        dlg.Destroy()




# -------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
