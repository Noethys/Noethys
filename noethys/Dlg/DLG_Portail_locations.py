#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
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
import wx.html as html
import GestionDB
import datetime
from Utils import UTILS_Dialogs
from Utils import UTILS_Texte
from Utils import UTILS_Historique
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Dlg.DLG_Portail_demandes import CTRL_Log
from Ol import OL_Portail_locations


class Dialog(wx.Dialog):
    def __init__(self, parent, track=None):
        if parent == None :
            dlgparent = None
        else :
            dlgparent = parent.parent
        wx.Dialog.__init__(self, dlgparent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.track = track
        self.reponse = ""

        # Bandeau
        intro = _(u"Vous pouvez gérer ici la demande de façon manuelle. Commencez par cliquer sur le bouton 'Appliquer la demande' pour voir apparaître les modifications demandées sur le portail. Vous pouvez alors effectuer manuellement d'éventuelles modifications avant de valider.")
        titre = _(u"Traitement manuel des locations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Location.png")

        # Locations
        self.box_locations_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Détail de la demande"))
        self.ctrl_locations = OL_Portail_locations.ListView(self, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)

        # Journal
        self.box_journal_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Journal d'évènements"))
        self.ctrl_log = CTRL_Log(self)
        self.ctrl_log.SetMinSize((100, 80))
        self.bouton_traiter = CTRL_Bouton_image.CTRL(self, texte=_(u"Appliquer la demande"), cheminImage="Images/32x32/Fleche_bas.png")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonTraiter, self.bouton_traiter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)

        # Init
        self.ctrl_locations.MAJ(track_demande=track)

    def __set_properties(self):
        self.bouton_traiter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer la demande")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1,wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(2, 1, 10, 10)

        # Locations
        box_grille = wx.StaticBoxSizer(self.box_locations_staticbox, wx.VERTICAL)
        box_grille.Add(self.ctrl_locations, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_grille, 1, wx.EXPAND, 10)

        # Journal
        box_journal = wx.StaticBoxSizer(self.box_journal_staticbox, wx.VERTICAL)
        grid_sizer_journal = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_journal.Add(self.ctrl_log, 0, wx.EXPAND, 0)

        sizer_boutons = wx.BoxSizer(wx.VERTICAL)
        sizer_boutons.Add(self.bouton_traiter, 1, wx.EXPAND, 0)
        grid_sizer_journal.Add(sizer_boutons, 1, wx.EXPAND, 0)
        
        grid_sizer_journal.AddGrowableRow(0)
        grid_sizer_journal.AddGrowableCol(0)
        box_journal.Add(grid_sizer_journal, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_contenu.Add(box_journal, 1, wx.EXPAND, 10)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 5, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Traiterlesdemandesduportail")

    def OnBoutonTraiter(self, event=None):
        self.parent.EcritLog(_(u"Application de la demande de locations"), self.ctrl_log)

        resultats = {"ajouter": {True: 0, False: 0}, "modifier": {True: 0, False: 0}, "supprimer": {True: 0, False: 0}}

        DB = GestionDB.DB()
        for track in self.ctrl_locations.donnees:
            listeDonnees = [
                ("IDfamille", self.track.IDfamille),
                ("IDproduit", track.IDproduit),
                ("date_debut", track.date_debut),
                ("date_fin", track.date_fin),
                ("quantite", track.quantite),
                ("partage", track.partage),
            ]

            if track.resultat != "ok":
                if track.etat == "ajouter":
                    if track.action_possible == True:
                        listeDonnees.append(("date_saisie", datetime.date.today()))
                        listeDonnees.append(("IDlocation_portail", track.IDlocation))
                        IDlocation = DB.ReqInsert("locations", listeDonnees)
                        resultat = _(u"Ajout de la location %s du %s") % (track.nom_produit, track.date_debut_txt)
                        DB.ReqMAJ("portail_reservations_locations", [("resultat", "ok")], "IDreservation", track.IDreservation)
                        UTILS_Historique.InsertActions([{"IDfamille": self.track.IDfamille, "IDcategorie": 37, "action": resultat, }], DB=DB)
                    else:
                        resultat = _(u"%s du %s : %s") % (track.nom_produit, track.date_debut_txt, track.statut)
                    self.parent.EcritLog(resultat, self.ctrl_log)

                if track.etat == "modifier":
                    if track.action_possible == True:
                        if "-" in track.IDlocation:
                            DB.ReqMAJ("locations", listeDonnees, "IDlocation_portail", track.IDlocation, IDestChaine=True)
                        else:
                            DB.ReqMAJ("locations", listeDonnees, "IDlocation", int(track.IDlocation))
                        resultat = _(u"Modification de la location %s du %s") % (track.nom_produit, track.date_debut_txt)
                        DB.ReqMAJ("portail_reservations_locations", [("resultat", "ok")], "IDreservation", track.IDreservation)
                        UTILS_Historique.InsertActions([{"IDfamille": self.track.IDfamille, "IDcategorie": 38, "action": resultat, }], DB=DB)
                    else:
                        resultat = _(u"%s du %s : %s") % (track.nom_produit, track.date_debut_txt, track.statut)
                    self.parent.EcritLog(resultat, self.ctrl_log)

                if track.etat == "supprimer":
                    if track.action_possible == True:
                        if "-" in track.IDlocation:
                            DB.ReqDEL("locations", "IDlocation_portail", track.IDlocation, IDestChaine=True)
                        else:
                            DB.ReqDEL("locations", "IDlocation", int(track.IDlocation))
                        resultat = _(u"Suppression de la location %s du %s") % (track.nom_produit, track.date_debut_txt)
                        DB.ReqMAJ("portail_reservations_locations", [("resultat", "ok")], "IDreservation", track.IDreservation)
                        UTILS_Historique.InsertActions([{"IDfamille": self.track.IDfamille, "IDcategorie": 39, "action": resultat, }], DB=DB)
                    else:
                        resultat = _(u"%s du %s : %s") % (track.nom_produit, track.date_debut_txt, track.statut)
                    self.parent.EcritLog(resultat, self.ctrl_log)

                # Mémorisation pour réponse
                resultats[track.etat][track.action_possible] += 1

        DB.Close()

        # Formatage de la réponse
        liste_resultats = []
        for etat, valeurs in resultats.items():
            for succes, quantite in valeurs.items():
                if quantite:
                    if succes == True:
                        txt_validation = u"validé"
                    else:
                        txt_validation = u"refusé"
                    if quantite == 1:
                        pluriel = ""
                    else:
                        pluriel = "s"

                    if etat == "ajouter": liste_resultats.append(u"%d ajout%s %s%s" % (quantite, pluriel, txt_validation, pluriel))
                    if etat == "modifier": liste_resultats.append(u"%d modification%s %se%s" % (quantite, pluriel, txt_validation, pluriel))
                    if etat == "supprimer": liste_resultats.append(u"%d suppression%s %se%s" % (quantite, pluriel, txt_validation, pluriel))

        if liste_resultats:
            self.reponse = UTILS_Texte.ConvertListeToPhrase(liste_resultats) + "."
            self.parent.EcritLog(_(u"Réponse : %s") % self.reponse, self.ctrl_log)

            # MAJ de la liste des actions
            self.ctrl_locations.MAJ(track_demande=self.track)

    def OnBoutonFermer(self, event=None):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        if event != None :
            self.EndModal(wx.ID_OK)

    def GetReponse(self):
        return self.reponse



        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()