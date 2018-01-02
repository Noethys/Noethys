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
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Envoi_email
from Utils import UTILS_Titulaires
from Dlg import DLG_Messagebox
import GestionDB




class Dialog(wx.Dialog):
    def __init__(self, parent, listview=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.listview = listview

        # Bandeau
        titre = _(u"Envoyer un Email")
        self.SetTitle(titre)
        intro = _(u"Sélectionnez les paramètres et cliquez sur Ok pour accéder à l'outil d'envoi des emails.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Editeur_email.png")

        # Choix de l'adresse
        self.staticbox_adresse = wx.StaticBox(self, -1, _(u"Sélection de l'adresse"))
        self.radio_famille = wx.RadioButton(self, -1, _(u"L'adresse internet de la famille"), style=wx.RB_GROUP)
        self.radio_individu = wx.RadioButton(self, -1, _(u"L'adresse internet de l'individu"))
        self.staticbox_adresse.SetMinSize((350, -1))

        # Lignes
        self.staticbox_lignes = wx.StaticBox(self, -1, _(u"Sélection des lignes"))
        self.radio_lignes_affichees = wx.RadioButton(self, -1, _(u"Toutes les lignes affichées"), style=wx.RB_GROUP)
        self.radio_lignes_cochees = wx.RadioButton(self, -1, _(u"Toutes les lignes cochées"))
        self.radio_ligne_selectionnee = wx.RadioButton(self, -1, _(u"La ligne sélectionnée"))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init
        track = self.listview.GetObjects()[0]

        if hasattr(track, "IDfamille") == False :
            self.radio_famille.Show(False)
            self.radio_individu.SetValue(True)

        if hasattr(track, "IDindividu") == False :
            self.radio_individu.Show(False)

        if self.listview.checkStateColumn == None :
            self.radio_lignes_cochees.Show(False)

        if len(self.listview.GetSelectedObjects()) == 0 :
            self.radio_ligne_selectionnee.Show(False)

        self.__do_layout()

    def __set_properties(self):
        self.radio_famille.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner les adresses des familles")))
        self.radio_individu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner les adresses des individus")))
        self.radio_lignes_affichees.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner toutes les lignes affichées dans la liste")))
        self.radio_lignes_cochees.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner toutes les lignes cochées affichées")))
        self.radio_ligne_selectionnee.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la ligne sélectionnée")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Adresse
        staticbox_adresse = wx.StaticBoxSizer(self.staticbox_adresse, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_adresse.Add(self.radio_famille, 0, 0, 0)
        grid_sizer_adresse.Add(self.radio_individu, 0, 0, 0)
        staticbox_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Lignes
        staticbox_lignes = wx.StaticBoxSizer(self.staticbox_lignes, wx.VERTICAL)
        grid_sizer_lignes = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_lignes.Add(self.radio_lignes_affichees, 0, 0, 0)
        grid_sizer_lignes.Add(self.radio_lignes_cochees, 0, 0, 0)
        grid_sizer_lignes.Add(self.radio_ligne_selectionnee, 0, 0, 0)
        staticbox_lignes.Add(grid_sizer_lignes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_lignes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        # Sélection des lignes
        if self.radio_ligne_selectionnee.GetValue() == True :
            tracks = self.listview.GetSelectedObjects()

        if self.radio_lignes_affichees.GetValue() == True :
            tracks = self.listview.GetFilteredObjects()

        if self.radio_lignes_cochees.GetValue() == True :
            tracks = self.listview.GetCheckedObjects()

        # Récupération de toutes les adresses Emails
        listeDonnees = []
        listeAnomalies = []

        if self.radio_individu.GetValue() == True :
            DB = GestionDB.DB()
            req = """SELECT IDindividu, nom, prenom, mail
            FROM individus;"""
            DB.ExecuterReq(req)
            listeAdressesIndividus = DB.ResultatReq()
            DB.Close()
            dictAdressesIndividus = {}
            for IDindividu, nom, prenom, mail in listeAdressesIndividus:
                dictAdressesIndividus[IDindividu] = {"mail": mail, "nom": nom, "prenom" : prenom}

            for track in tracks :
                if dictAdressesIndividus.has_key(track.IDindividu) :
                    adresse = dictAdressesIndividus[track.IDindividu]["mail"]
                    nom, prenom = dictAdressesIndividus[track.IDindividu]["nom"], dictAdressesIndividus[track.IDindividu]["prenom"]
                    if prenom == None : prenom = ""
                    nomIndividu = u"%s %s" % (nom, prenom)
                    if adresse not in ("", None) :
                        dictTemp = {"adresse": adresse, "pieces": [], "champs": {}}
                        if dictTemp not in listeDonnees:
                            listeDonnees.append(dictTemp)
                    else :
                        listeAnomalies.append(nomIndividu)

        if self.radio_famille.GetValue() == True:
            dict_titulaires = UTILS_Titulaires.GetTitulaires()

            for track in tracks:
                adresse = None
                if dict_titulaires.has_key(track.IDfamille) :
                    #adresse = UTILS_Envoi_email.GetAdresseFamille(track.IDfamille, choixMultiple=False, muet=True, nomTitulaires=track.nomTitulaires)
                    listeEmails = dict_titulaires[track.IDfamille]["listeMails"]
                    if len(listeEmails) > 0 :
                        adresse = listeEmails[0]

                    # Mémorisation des données
                    if adresse != None :
                        dictTemp = {"adresse": adresse, "pieces": [], "champs": {}}
                        if dictTemp not in listeDonnees :
                            listeDonnees.append(dictTemp)
                    else:
                        listeAnomalies.append(dict_titulaires[track.IDfamille]["titulairesSansCivilite"])

        # Annonce les anomalies trouvées
        if len(listeAnomalies) > 0:
            if self.radio_famille.GetValue() == True :
                introduction = _(u"%d des familles sélectionnées n'ont pas d'adresse Email :") % len(listeAnomalies)
                conclusion = _(u"Souhaitez-vous quand même continuer avec les %d autres familles ?") % len(listeDonnees)
            else :
                introduction = _(u"%d des individus sélectionnés n'ont pas d'adresse Email :") % len(listeAnomalies)
                conclusion = _(u"Souhaitez-vous quand même continuer avec les %d autres individus ?") % len(listeDonnees)
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Anomalies"), introduction=introduction, detail=u"\n".join(listeAnomalies), conclusion=conclusion, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Oui"), _(u"Non"), _(u"Annuler")])
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse in (1, 2) :
                return False

        # Dernière vérification avant transfert
        if len(listeDonnees) == 0:
            dlg = wx.MessageDialog(self, _(u"Il ne reste finalement aucun email à envoyer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Transfert des données vers DLG Mailer
        from Dlg import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self)
        dlg.SetDonnees(listeDonnees, modificationAutorisee=True)
        dlg.ChargerModeleDefaut()
        dlg.ShowModal()
        dlg.Destroy()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
