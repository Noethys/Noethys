#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Parametres
import GestionDB


class CTRL_Unite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1))
        self.parent = parent
        self.MAJ()

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        self.Select(0)

    def GetListeDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDunite, unites.nom, unites.type, unites.IDactivite, activites.nom
        FROM unites
        LEFT JOIN activites ON activites.IDactivite = unites.IDactivite
        ORDER BY activites.date_fin DESC, unites.IDactivite, unites.ordre;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        listeItems = [_(u"-- Sélectionnez une unité --")]
        self.dictDonnees = {}
        self.dictDonnees[0] = None

        index = 1
        IDactiviteTemp = None
        for IDunite, unite_nom, unite_type, IDactivite, activite_nom in listeDonnees :
            if IDactivite != IDactiviteTemp :
                # Création d'une ligne activité
                self.dictDonnees[index] = None
                listeItems.append(activite_nom)
                IDactiviteTemp = IDactivite
                index += 1

            # Création d'une ligne unité
            self.dictDonnees[index] = {"ID" : IDunite, "unite_nom" : unite_nom, "IDactivite" : IDactivite, "activite_nom" : activite_nom}
            listeItems.append(u"    %s" % unite_nom)
            index += 1
        return listeItems

    def SetValeur(self, ID=0):
        try :
            ID = int(ID)
        except :
            ID = None
        if ID == None :
            self.SetSelection(0)
        else :
            for index, values in self.dictDonnees.items():
                if values != None and values["ID"] == ID :
                    self.SetSelection(index)
                    return

    def GetValeur(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        if self.dictDonnees[index] == None : return None
        return self.dictDonnees[index]["ID"]

    def GetInfos(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]

# -------------------------------------------------------------------------------------------------------------------
class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        # Bandeau
        titre = _(u"Recopier des consommations")
        self.SetTitle(titre)
        intro = _(u"Vous pouvez ici recopier les consommations d'une unité sur une autre unité. Sélectionnez les unités à impacter puis cliquez sur Ok.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier_modifier.png")

        # Unités
        self.staticbox_unites = wx.StaticBox(self, -1, _(u"Unités"))
        self.ctrl_unite_origine = CTRL_Unite(self)
        self.ctrl_image_recopiage = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_droite2.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_unite_destination = CTRL_Unite(self)

        # Paramètres
        self.staticbox_parametres = wx.StaticBox(self, -1, _(u"Informations à recopier"))
        self.check_param_horaires = wx.CheckBox(self, -1, _(u"Horaires"))
        self.check_param_quantite = wx.CheckBox(self, -1, _(u"Quantité"))
        self.check_param_etiquettes = wx.CheckBox(self, -1, _(u"Etiquettes"))
        self.check_param_etat = wx.CheckBox(self, -1, _(u"Etat"))

        # Options
        self.staticbox_options = wx.StaticBox(self, -1, _(u"Options"))
        self.radio_lignes_affichees = wx.RadioButton(self, -1, _(u"Toutes les lignes affichées"), style=wx.RB_GROUP)
        self.radio_lignes_selectionnees = wx.RadioButton(self, -1, _(u"Toutes les lignes sélectionnées"))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixUnite, self.ctrl_unite_origine)
        self.Bind(wx.EVT_CHOICE, self.OnChoixUnite, self.ctrl_unite_destination)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init
        self.ctrl_unite_origine.SetValeur(UTILS_Parametres.Parametres(mode="get", categorie="recopiage_conso", nom="unite_origine", valeur=None))
        self.ctrl_unite_destination.SetValeur(UTILS_Parametres.Parametres(mode="get", categorie="recopiage_conso", nom="unite_destination", valeur=None))
        self.check_param_horaires.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="recopiage_conso", nom="param_horaires", valeur=True))
        self.check_param_quantite.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="recopiage_conso", nom="param_quantite", valeur=True))
        self.check_param_etiquettes.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="recopiage_conso", nom="param_etiquettes", valeur=True))
        self.check_param_etat.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="recopiage_conso", nom="param_etat", valeur=True))

        option_lignes = UTILS_Parametres.Parametres(mode="get", categorie="recopiage_conso", nom="option_lignes", valeur="lignes_affichees")
        if option_lignes == "lignes_affichees" :
            self.radio_lignes_affichees.SetValue(True)
        if option_lignes == "lignes_selectionnees" :
            self.radio_lignes_selectionnees.SetValue(True)

        self.OnChoixUnite(None)

    def __set_properties(self):
        self.ctrl_unite_origine.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'unité à recopier")))
        self.ctrl_unite_destination.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'unité sur laquelle effectuer le recopiage")))
        self.check_param_horaires.SetToolTip(wx.ToolTip(_(u"Cochez cette option pour recopier les horaires")))
        self.check_param_quantite.SetToolTip(wx.ToolTip(_(u"Cochez cette option pour recopier la quantité")))
        self.check_param_etiquettes.SetToolTip(wx.ToolTip(_(u"Cochez cette option pour recopier les étiquettes. Cette option n'est disponible que lorsque les unités sélectionnées appartiennent à la même activité.")))
        self.check_param_etat.SetToolTip(wx.ToolTip(_(u"Cochez cette option pour recopier l'état")))
        self.radio_lignes_affichees.SetToolTip(wx.ToolTip(_(u"Sélectionnez cette option pour appliquer le recopiage sur toutes les lignes affichées")))
        self.radio_lignes_selectionnees.SetToolTip(wx.ToolTip(_(u"Sélectionnez cette option pour appliquer le recopiage uniquement sur les lignes sélectionnées")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((400, 510))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Unités
        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites, wx.VERTICAL)
        grid_sizer_unites = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_unites.Add(self.ctrl_unite_origine, 1, wx.EXPAND, 0)
        grid_sizer_unites.Add(self.ctrl_image_recopiage, 1, wx.EXPAND, 0)
        grid_sizer_unites.Add(self.ctrl_unite_destination, 1, wx.EXPAND, 0)
        staticbox_unites.Add(grid_sizer_unites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_unites, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Paramètres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_parametres.Add(self.check_param_horaires, 1, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.check_param_quantite, 1, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.check_param_etiquettes, 1, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.check_param_etat, 1, wx.EXPAND, 0)
        staticbox_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_options.Add(self.radio_lignes_affichees, 0, 0, 0)
        grid_sizer_options.Add(self.radio_lignes_selectionnees, 0, 0, 0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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

    def OnChoixUnite(self, event):
        dictUniteOrigine = self.ctrl_unite_origine.GetInfos()
        dictUniteDestination = self.ctrl_unite_destination.GetInfos()

        valide = True
        if dictUniteOrigine != None and dictUniteDestination != None :
            if dictUniteOrigine["IDactivite"] != dictUniteDestination["IDactivite"] :
                valide = False
        else :
            valide = False

        self.check_param_etiquettes.Enable(valide)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lagrilledesconsommations")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_unite_origine.GetValeur() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une unité à recopier !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_unite_destination.GetValeur() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner l'unité vers laquelle recopier !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_unite_origine.GetValeur() == self.ctrl_unite_destination.GetValeur()  :
            dlg = wx.MessageDialog(self, _(u"Les deux unités sélectionnées doivent être différentes !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Mémorisation des paramètres
        UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="unite_origine", valeur=self.ctrl_unite_origine.GetValeur())
        UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="unite_destination", valeur=self.ctrl_unite_destination.GetValeur())
        UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="param_horaires", valeur=self.check_param_horaires.GetValue())
        UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="param_quantite", valeur=self.check_param_quantite.GetValue())
        UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="param_etiquettes", valeur=self.check_param_etiquettes.GetValue())
        UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="param_etat", valeur=self.check_param_etat.GetValue())

        if self.radio_lignes_affichees.GetValue() == True :
            UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="option_lignes", valeur="lignes_affichees")
        if self.radio_lignes_selectionnees.GetValue() == True :
            UTILS_Parametres.Parametres(mode="set", categorie="recopiage_conso", nom="option_lignes", valeur="lignes_selectionnees")

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetDonnees(self):
        ID_unite_origine = self.ctrl_unite_origine.GetValeur()
        label_unite_origine = self.ctrl_unite_origine.GetStringSelection().strip()
        ID_unite_destination = self.ctrl_unite_destination.GetValeur()
        label_unite_destination = self.ctrl_unite_destination.GetStringSelection().strip()

        param_horaires = self.check_param_horaires.GetValue()
        param_quantite = self.check_param_quantite.GetValue()
        if self.check_param_etiquettes.IsEnabled() == False :
            param_etiquettes = False
        else :
            param_etiquettes = self.check_param_etiquettes.GetValue()
        param_etat = self.check_param_etat.GetValue()

        if self.radio_lignes_affichees.GetValue() == True :
            option_lignes = "lignes_affichees"
        if self.radio_lignes_selectionnees.GetValue() == True :
            option_lignes = "lignes_selectionnees"

        dictDonnees = {
            "ID_unite_origine" : ID_unite_origine, "label_unite_origine" : label_unite_origine,
            "ID_unite_destination" : ID_unite_destination,  "label_unite_destination" : label_unite_destination,
            "param_horaires" : param_horaires, "param_quantite" : param_quantite,
            "param_etiquettes" : param_etiquettes, "param_etat" : param_etat,
            "option_lignes" : option_lignes,
        }
        return dictDonnees




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
