#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import UTILS_Parametres



class CTRL_Etat(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1))
        self.parent = parent
        self.listeEtats = [
            (None, _(u"-- Sélectionnez un état --")),
            ("reservation", _(u"Réservation")),
            ("attente", _(u"Attente")),
            ("refus", _(u"Refus")),
            ("present", _(u"Présence")),
            ("absentj", _(u"Absence justifiée")),
            ("absenti", _(u"Absence injustifiée")),
            ]
        self.MAJ()

    def MAJ(self):
        listeItems = []
        for code, label in self.listeEtats :
            listeItems.append(label)
        self.SetItems(listeItems)
        self.Select(0)

    def SetValeur(self, valeur=None):
        index = 0
        for code, label in self.listeEtats :
            if code == valeur :
                 self.SetSelection(index)
            index += 1

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]


# ----------------------------------------------------------------------------------------------------------------------------
class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent

        # Bandeau
        titre = _(u"Convertir l'état des consommations")
        self.SetTitle(titre)
        intro = _(u"Sélectionnez l'état à convertir puis l'état souhaité. Vous pouvez également préciser les lignes à impacter.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier_modifier.png")

        # Conversion
        self.staticbox_conversion = wx.StaticBox(self, -1, _(u"Etat à convertir"))
        self.ctrl_etat_avant = CTRL_Etat(self)
        self.ctrl_image_conversion = wx.StaticBitmap(self, -1, wx.Bitmap(u"Images/16x16/Fleche_droite2.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_etat_apres = CTRL_Etat(self)

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

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init
        etat_avant = UTILS_Parametres.Parametres(mode="get", categorie="conversion_etat", nom="etat_avant", valeur=None)
        self.ctrl_etat_avant.SetValeur(etat_avant)

        etat_apres = UTILS_Parametres.Parametres(mode="get", categorie="conversion_etat", nom="etat_apres", valeur=None)
        self.ctrl_etat_apres.SetValeur(etat_apres)

        option_lignes = UTILS_Parametres.Parametres(mode="get", categorie="conversion_etat", nom="option_lignes", valeur="lignes_affichees")
        if option_lignes == "lignes_affichees" :
            self.radio_lignes_affichees.SetValue(True)
        if option_lignes == "lignes_selectionnees" :
            self.radio_lignes_selectionnees.SetValue(True)

    def __set_properties(self):
        self.ctrl_etat_avant.SetToolTipString(_(u"Sélectionnez l'état à convertir. Seules les consommations ayant cet état seront converties."))
        self.ctrl_etat_apres.SetToolTipString(_(u"Sélectionnez l'état souhaité"))
        self.radio_lignes_affichees.SetToolTipString(_(u"Sélectionnez cette option pour appliquer la conversion sur toutes les lignes affichées"))
        self.radio_lignes_selectionnees.SetToolTipString(_(u"Sélectionnez cette option pour appliquer la conversion uniquement sur les lignes sélectionnées"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((400, 510))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Conversion
        staticbox_conversion = wx.StaticBoxSizer(self.staticbox_conversion, wx.VERTICAL)
        grid_sizer_conversion = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_conversion.Add(self.ctrl_etat_avant, 1, wx.EXPAND, 0)
        grid_sizer_conversion.Add(self.ctrl_image_conversion, 1, wx.EXPAND, 0)
        grid_sizer_conversion.Add(self.ctrl_etat_apres, 1, wx.EXPAND, 0)
        staticbox_conversion.Add(grid_sizer_conversion, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_conversion, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Lagrilledesconsommations")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_etat_avant.GetValeur() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un état à convertir !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_etat_apres.GetValeur() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner l'état souhaité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_etat_avant.GetValeur() == self.ctrl_etat_apres.GetValeur()  :
            dlg = wx.MessageDialog(self, _(u"Les deux états sélectionnés doivent être différents !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Mémorisation des paramètres
        etat_avant = self.ctrl_etat_avant.GetValeur()
        UTILS_Parametres.Parametres(mode="set", categorie="conversion_etat", nom="etat_avant", valeur=etat_avant)
        etat_apres = self.ctrl_etat_apres.GetValeur()
        UTILS_Parametres.Parametres(mode="set", categorie="conversion_etat", nom="etat_apres", valeur=etat_apres)

        if self.radio_lignes_affichees.GetValue() == True :
            UTILS_Parametres.Parametres(mode="set", categorie="conversion_etat", nom="option_lignes", valeur="lignes_affichees")
        if self.radio_lignes_selectionnees.GetValue() == True :
            UTILS_Parametres.Parametres(mode="set", categorie="conversion_etat", nom="option_lignes", valeur="lignes_selectionnees")

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetDonnees(self):
        code_etat_avant = self.ctrl_etat_avant.GetValeur()
        label_etat_avant = self.ctrl_etat_avant.GetStringSelection()
        code_etat_apres = self.ctrl_etat_apres.GetValeur()
        label_etat_apres = self.ctrl_etat_apres.GetStringSelection()
        if self.radio_lignes_affichees.GetValue() == True :
            option_lignes = "lignes_affichees"
        if self.radio_lignes_selectionnees.GetValue() == True :
            option_lignes = "lignes_selectionnees"
        dictDonnees = {
            "code_etat_avant" : code_etat_avant, "label_etat_avant" : label_etat_avant,
            "code_etat_apres" : code_etat_apres,  "label_etat_apres" : label_etat_apres,
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
