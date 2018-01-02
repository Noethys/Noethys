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
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ol import OL_Saisie_lot_cotisations
from Dlg.DLG_Saisie_cotisation import CTRL_Parametres
import datetime
from Utils import UTILS_Dates
from Utils import UTILS_Historique
from Utils import UTILS_Texte



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez saisir ici un lot de cotisations. Sélectionnez les paramètres des cotisations à créer, cochez les individus ou les familles puis cliquez sur le bouton Ok. Utilisez la commande de Filtrage de liste pour effectuer une sélection rapide des individus ou des familles.")
        titre = _(u"Saisir un lot de cotisations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Cotisation.png")

        # Liste
        self.staticbox_individus_staticbox = wx.StaticBox(self, -1, _(u"Individus / Familles"))

        self.label_info = wx.StaticText(self, -1, _(u"Double-cliquez sur une ligne pour modifier le numéro de cotisation à générer."))
        self.label_info.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.ctrl_listview = OL_Saisie_lot_cotisations.ListView(self, id=-1, categorie="individu", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((10, 10))
        self.ctrl_recherche = OL_Saisie_lot_cotisations.CTRL_Outils(self, listview=self.ctrl_listview, afficherCocher=True)

        # Paramètres
        self.ctrl_parametres = CTRL_Parametres(self, mode_lot=True)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer les cotisations"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init
        self.ShowLabelInfo(False)
        self.ctrl_parametres.Init()

        if len(self.ctrl_listview.donnees) == 0 :
            self.ctrl_listview.MAJ()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour inscrire les individus cochés")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((920, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        grid_sizer_contenu.Add(self.ctrl_parametres, 0, wx.EXPAND, 10)

        # Contenu
        staticbox_individus = wx.StaticBoxSizer(self.staticbox_individus_staticbox, wx.VERTICAL)

        self.grid_sizer_individus = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        self.grid_sizer_individus.Add(self.label_info, 0, wx.EXPAND, 0)
        self.grid_sizer_individus.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        self.grid_sizer_individus.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        self.grid_sizer_individus.AddGrowableRow(1)
        self.grid_sizer_individus.AddGrowableCol(0)
        
        staticbox_individus.Add(self.grid_sizer_individus, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_contenu.Add(staticbox_individus, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def ShowLabelInfo(self, etat=False):
        self.label_info.Show(etat)
        self.grid_sizer_individus.Layout()

    def SetLabelBox(self, label=""):
        self.staticbox_individus_staticbox.SetLabel(label)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
    
    def OnBoutonOk(self, event):
        # Validation
        if self.ctrl_parametres.Validation() == False :
            return False
        if self.ctrl_listview.Validation() == False :
            return False

        # Sauvegarde
        if self.Sauvegarde() == False :
            return False

        # Fermeture de la fenêtre
        #self.EndModal(wx.ID_OK)

    def Sauvegarde(self):
        # Récupération des tracks
        liste_tracks = self.ctrl_listview.GetTracksCoches()

        # Récupération des paramètres
        IDtype_cotisation = self.ctrl_parametres.ctrl_type.GetID()
        IDunite_cotisation = self.ctrl_parametres.ctrl_unite.GetID()
        date_saisie = self.ctrl_parametres.date_saisie
        IDutilisateur = self.ctrl_parametres.IDutilisateur
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate()
        activites = self.ctrl_parametres.ctrl_activites.GetDonnees(format="texte")
        observations = self.ctrl_parametres.ctrl_observations.GetValue()

        # Création de la carte
        if self.ctrl_parametres.ctrl_creation.GetValue() == True:
            numero_manuel = self.ctrl_parametres.radio_numero_manuel.GetValue()
            date_creation_carte = self.ctrl_parametres.ctrl_date_creation.GetDate()
            numero = self.ctrl_parametres.ctrl_numero.GetValue()
        else:
            numero_manuel = False
            date_creation_carte = None
            numero = None

        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la génération de %d cotisations ?") % len(liste_tracks), _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES:
            return False

        # Sauvegarde
        DB = GestionDB.DB()

        dlgprogress = wx.ProgressDialog(_(u"Génération des cotisations"), _(u"Veuillez patienter..."), maximum=len(liste_tracks), parent=None, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        index = 1
        for track in liste_tracks :

            dlgprogress.Update(index, _(u"Génération de la cotisation %d sur %d") % (index, len(liste_tracks)))

            if numero_manuel == True :
                numero = track.numero

            listeDonnees = [
                ("IDfamille", track.IDfamille),
                ("IDindividu", track.IDindividu),
                ("IDtype_cotisation", IDtype_cotisation),
                ("IDunite_cotisation", IDunite_cotisation),
                ("date_saisie", date_saisie),
                ("IDutilisateur", IDutilisateur),
                ("date_creation_carte", date_creation_carte),
                ("numero", numero),
                ("date_debut", date_debut),
                ("date_fin", date_fin),
                ("observations", observations),
                ("activites", activites),
            ]
            IDcotisation = DB.ReqInsert("cotisations", listeDonnees)

            # Sauvegarde de la prestation
            facturer = self.ctrl_parametres.ctrl_facturer.GetValue()
            date_facturation = self.ctrl_parametres.ctrl_date_prestation.GetDate()
            montant = self.ctrl_parametres.ctrl_montant.GetMontant()
            label_prestation = self.ctrl_parametres.ctrl_label.GetValue()

            if facturer == True:

                # Création d'une prestation
                listeDonnees = [
                    ("IDcompte_payeur", track.IDcompte_payeur),
                    ("date", date_facturation),
                    ("categorie", "cotisation"),
                    ("label", label_prestation),
                    ("montant_initial", montant),
                    ("montant", montant),
                    ("IDfamille", track.IDfamille),
                    ("IDindividu", track.IDindividu),
                ]
                listeDonnees.append(("date_valeur", str(datetime.date.today())))
                IDprestation = DB.ReqInsert("prestations", listeDonnees)

                # Insertion du IDprestation dans la cotisation
                DB.ReqMAJ("cotisations", [("IDprestation", IDprestation), ], "IDcotisation", IDcotisation)

            # Mémorise l'action dans l'historique
            date_debut_periode = UTILS_Dates.DateEngFr(str(date_debut))
            date_fin_periode = UTILS_Dates.DateEngFr(str(date_fin))
            UTILS_Historique.InsertActions([{
                "IDindividu": track.IDindividu,
                "IDfamille": track.IDfamille,
                "IDcategorie": 21,
                "action": _(u"Saisie de la cotisation ID%d '%s' pour la période du %s au %s") % (IDcotisation, label_prestation, date_debut_periode, date_fin_periode),
            }, ])

            # Génération du prochain numéro de cotisation
            if numero != None :
                numero = UTILS_Texte.Incrementer(numero)

            index += 1

        DB.Close()
        dlgprogress.Destroy()

        # Succès
        dlg = wx.MessageDialog(self, _(u"Les %d cotisations ont été générées avec succès.") % len(liste_tracks), _(u"Fin"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        return True



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
