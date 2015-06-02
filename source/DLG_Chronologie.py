#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import CTRL_Bandeau
import UTILS_Historique

import CTRL_Timeline
import UTILS_TL_db as TL

import datetime

try: import psyco; psyco.full()
except: pass


class Track(object):
    def __init__(self, donnees):
        self.IDaction = donnees[0]
        # Date
        self.date = donnees[1]
        self.heure = donnees[2]
        self.dateHeure = "%s|%s" % (self.date, self.heure)
        # Utilisateur
        self.IDutilisateur = donnees[3]
        self.nom_utilisateur = donnees[8]
        if self.nom_utilisateur == None : 
            self.nom_utilisateur = u""
        self.prenom_utilisateur = donnees[9]
        if self.prenom_utilisateur == None : 
            self.prenom_utilisateur = u""
        self.nomComplet_utilisateur = u"%s %s" % (self.nom_utilisateur, self.prenom_utilisateur)
        # Famille
        self.IDfamille = donnees[4]
        # Individu
        self.IDindividu = donnees[5]
        self.nom_individu = donnees[10]
        if self.nom_individu == None : 
            self.nom_individu = u""
        self.prenom_individu = donnees[11]
        if self.prenom_individu == None : 
            self.prenom_individu = u""
        if self.IDindividu != None :
            self.nomComplet_individu = u"%s %s" % (self.nom_individu, self.prenom_individu)
        else:
            self.nomComplet_individu = u""
        # Catégorie
        self.IDcategorie = donnees[6]
        self.nomCategorie = UTILS_Historique.CATEGORIES[self.IDcategorie]
        # Texte de l'action
        self.action = donnees[7]
        self.description = _(u"%s \n\n- par %s -") % (self.action, self.nomComplet_utilisateur)
        if self.nomComplet_individu != "" :
            self.description = u"%s : %s" % (self.nomComplet_individu, self.description)
            
            

def GetTracks(IDfamille=None, IDindividu=None):
    """ Récupération des données """
    if IDfamille != None : conditions = "WHERE historique.IDfamille=%d" % IDfamille
    elif IDindividu != None : conditions = "WHERE historique.IDindividu=%d" % IDindividu
    else : return [] 
    
    DB = GestionDB.DB()
    req = """SELECT 
    historique.IDaction, historique.date, historique.heure, historique.IDutilisateur, 
    historique.IDfamille, historique.IDindividu, historique.IDcategorie, historique.action,
    utilisateurs.nom, utilisateurs.prenom,
    individus.nom, individus.prenom
    FROM historique
    LEFT JOIN utilisateurs ON utilisateurs.IDutilisateur = historique.IDutilisateur
    LEFT JOIN individus ON individus.IDindividu = historique.IDindividu
    %s
    ORDER BY historique.date, historique.heure""" % conditions
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    
    listeListeView = []
    for item in listeDonnees :
        listeListeView.append(Track(item))
    return listeListeView


class Timeline(TL.TimelinePerso):
    def __init__(self, IDfamille=None, IDindividu=None):
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        TL.TimelinePerso.__init__(self)
        
    def _load_data(self):
        """ Importation des données """
        self.preferred_period = None
        self.categories = []
        self.events = []
        
        # Période préférée
        dateDuJour = datetime.datetime.today()
        dateDebut = dateDuJour - datetime.timedelta(6)
        dateFin = dateDuJour + datetime.timedelta(1)
        self.preferred_period = TL.TimePeriod(dateDebut, dateFin)
        
        # Récupération des catégories de l'historique
        from UTILS_Historique import CATEGORIES as dictCategories
        from UTILS_Historique import DICT_COULEURS as dictCouleurs
        dictCategorieTemp = {}
        for IDcategorie, nomCategorie in dictCategories.iteritems() :
            couleur = (255, 255, 255)
            for couleurTmp, listeIDcat in dictCouleurs.iteritems() :
                for IDcat in listeIDcat :
                    if IDcategorie == IDcat : 
                        couleur = couleurTmp
            categorie = TL.Category(nomCategorie, couleur, True)
            self.categories.append(categorie)
            dictCategorieTemp[IDcategorie] = categorie
        
        # Récupération des events de l'HISTORIQUE
        listeHistorique = GetTracks(self.IDfamille, self.IDindividu)
        for track in listeHistorique :
            date = TL.DateEngEnDateDD(track.date)
            heure = TL.HeureStrEnTime(track.heure)
            dateDebut = datetime.datetime(date.year, date.month, date.day, heure.hour, heure.minute, heure.second)
            nomCategorie = dictCategories[track.IDcategorie]
            texte = nomCategorie
            categorie = dictCategorieTemp[track.IDcategorie]
            description = track.description
            icon = None
            
            evt = TL.Event(dateDebut, dateDebut, texte, categorie)
            if description != None : evt.set_data("description", description)
            if icon != None : evt.set_data("icon", icon)
            self.events.append(evt)

        
        # Récupération des events des CONSOMMATIONS
        if self.IDfamille != None : conditions = "WHERE IDfamille=%d" % self.IDfamille
        elif self.IDindividu != None : conditions = "WHERE consommations.IDindividu=%d" % self.IDindividu
        else: conditions = ""
        DB = GestionDB.DB()
        req = """SELECT IDconso, consommations.IDindividu, individus.nom, prenom, consommations.IDactivite, 
        date, heure_debut, heure_fin, IDunite, consommations.IDgroupe, etat, groupes.nom,
        activites.nom
        FROM consommations
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN groupes ON groupes.IDgroupe = consommations.IDgroupe
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        %s
        GROUP BY date, consommations.IDindividu
        ORDER BY date;""" % conditions
        DB.ExecuterReq(req)
        listeConso = DB.ResultatReq()
        DB.Close()
        
        for IDconso, IDindividu, nom, prenom, IDactivite, date, heure_debut, heure_fin, IDunite, IDgroupe, etat, nomGroupe, nomActivite in listeConso :
            date = TL.DateEngEnDateDD(date)
            heure_debut = TL.HeureStrEnTime("04:00")
            heure_fin = TL.HeureStrEnTime("20:00")
            dateDebut = datetime.datetime(date.year, date.month, date.day, heure_debut.hour, heure_debut.minute, heure_debut.second)
            dateFin = datetime.datetime(date.year, date.month, date.day, heure_fin.hour, heure_fin.minute, heure_fin.second)
            texte = prenom
            categorie = None
            description = _(u"Activité : %s\nGroupe : %s") % (nomActivite, nomGroupe)
            icon = None
            
            evt = TL.Event(dateDebut, dateFin, texte, categorie)
            if description != None : evt.set_data("description", description)
            if icon != None : evt.set_data("icon", icon)
            self.events.append(evt)




class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, IDindividu=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        
        # Bandeau
        intro = _(u"Vous pouvez ici consulter l'historique des évènements et des consommations sous forme chronologique. Vous pouvez déplacer le graphique vers la droite ou vers la gauche en le faisant glisser avec la souris ou en utilisant sa molette, et basculer entre un affichage annuel, mensuel, hebdomadaire ou quotidien. Les évènements de l'historique apparaissent au-dessus de la ligne et les consommations individuelles au-dessous.")
        titre = _(u"Chronologie")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Timeline.png")
        
        # Timeline
        self.ctrl_timeline = CTRL_Timeline.CTRL(self, 
                            afficheSidebar=False, modele=Timeline(IDfamille, IDindividu),
                            afficheToolbar=True, positionToolbar="bas",
                            lectureSeule=True,
                            )
        self.ctrl_timeline.SetPositionVerticale(65)
        self.ctrl_timeline.MAJ() 
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
    def __set_properties(self):
        self.SetTitle(_(u"Chronologie"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Timeline
        grid_sizer_base.Add(self.ctrl_timeline, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

##    def MAJ_timeline(self, donnees=None):
##        if hasattr(self, "ctrl_timeline") :
##            self.ctrl_timeline.modele = Timeline(donnees)
##            self.ctrl_timeline.MAJ() 
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Chronologie1")
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=14, IDindividu=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
