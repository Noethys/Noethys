#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import copy
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Parametres



def ConvertListeEnTexte(listeColonnes=[]):
    # listeChaines = []
    # for col in listeColonnes :
    #     nom = col.valueGetter
    #     if col.visible == True :
    #         visible = "oui"
    #     else :
    #         visible = "non"
    #     listeChaines.append("%s;%s" % (nom, visible))
    # texte = "##".join(listeChaines)

    listeChaines = []
    for col in listeColonnes:
        if col.visible == True:
            listeChaines.append(col.valueGetter)
    texte = "##".join(listeChaines)
    return texte


def SauvegardeConfiguration(nomListe=None, listeColonnes=[]):
    texte = ConvertListeEnTexte(listeColonnes)
    UTILS_Parametres.Parametres(mode="set", categorie="configuration_liste_colonnes", nom=nomListe, valeur=texte)
    
def RestaurationConfiguration(nomListe=None, listeColonnesDefaut=[]):
    # Mémorise les colonnes par défaut
    dictColonnes = {}
    for col in listeColonnesDefaut :
        dictColonnes[col.valueGetter] = col
    
    # Lecture du paramètres stocké
    texteDefaut = ConvertListeEnTexte(listeColonnesDefaut)
    texte = UTILS_Parametres.Parametres(mode="get", categorie="configuration_liste_colonnes", nom=nomListe, valeur=texteDefaut)

    listeColonnesFinale = []
    listeNomsTemp = []
    for code in texte.split("##"):
        # Pour gérer les anciennes configurations de liste
        visible = True
        if ";" in code :
            code, visible = code.split(";")
            visible = bool(visible)
        # Mémorisation des colonnes sélectionnées
        if visible == True :
            listeNomsTemp.append(code)
            if dictColonnes.has_key(code) :
                col = dictColonnes[code]
                col.visible = True
                listeColonnesFinale.append(col)

    # Vérifie que toutes les colonnes de la liste initiale ont été traitées
    for code, col in dictColonnes.iteritems() :
        if code not in listeNomsTemp :
            col.visible = False
            listeColonnesFinale.append(col)

    return listeColonnesFinale




# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, ctrl=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.ctrl = ctrl
        self.rechercheEnCours = False

        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)

        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

        # HACK pour avoir le EVT_CHAR
        for child in self.GetChildren():
            if isinstance(child, wx.TextCtrl):
                child.Bind(wx.EVT_CHAR, self.OnKeyDown)
                break

    def OnKeyDown(self, event):
        """ Efface tout si touche ECHAP """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE :
            self.OnCancel(None)
        event.Skip()

    def OnSearch(self, evt):
        self.Recherche()

    def OnCancel(self, evt):
        self.SetValue("")

    def OnDoSearch(self, evt):
        self.Recherche()

    def Recherche(self):
        filtre = self.GetValue()
        self.ShowCancelButton(len(filtre))
        self.ctrl.SetFiltre(filtre)
        self.Refresh()



# -----------------------------------------------------------------------------------------------------------------

class CTRL_Elements(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, -1)
        self.parent = parent
        self.filtre = None
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDoubleClick)

    def OnDoubleClick(self, event):
        event.Skip()

    def SetColonnes(self, listeColonnes=[]):
        self.listeColonnes = listeColonnes
        self.dictDonnees = {}
        listeLabels = []
        index = 0
        for dictElement in self.listeColonnes :
            self.dictDonnees[index] = dictElement
            listeLabels.append(dictElement["nom"])
            index += 1
        self.SetItems(listeLabels)

    def SetFiltre(self, filtre=None):
        self.filtre = filtre
        self.MAJ()

    def GetColonne(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["code"]

    def GetIndex(self):
        return self.GetSelection()

# ---------------------------------------------------------------------------------------------------------------------

class CTRL_Dispo(CTRL_Elements):
    def __init__(self, parent):
        CTRL_Elements.__init__(self, parent)
        self.parent = parent

    def MAJ(self, code=None, index=None):
        liste_colonnes = []
        idx = 0
        for dictColonne in self.parent.colonnes_dispo:
            if dictColonne["code"] not in self.parent.colonnes_selection:
                if self.filtre == None or (self.filtre.lower() in dictColonne["nom"].lower()):
                    liste_colonnes.append(dictColonne)
                    if code == dictColonne["code"]:
                        index = idx
                    idx += 1
        self.SetColonnes(liste_colonnes)
        self.parent.label_dispo.SetLabel(_(u"%d colonnes disponibles") % len(liste_colonnes))
        if index != None :
            if index > len(liste_colonnes)-1 :
                index = len(liste_colonnes)-1
            self.SetSelection(index)

    def OnDoubleClick(self, event):
        code = self.GetCode()
        if code != None:
            self.parent.EnvoyerVersDroite(code)


# ---------------------------------------------------------------------------------------------------------------------

class CTRL_Selection(CTRL_Elements):
    def __init__(self, parent):
        CTRL_Elements.__init__(self, parent)
        self.parent = parent

    def MAJ(self, code=None, index=None):
        liste_colonnes = []
        idx = 0
        for codeTemp in self.parent.colonnes_selection:
            dictColonne = self.parent.dict_colonnes[codeTemp]
            if self.filtre == None or (self.filtre.lower() in dictColonne["nom"].lower()):
                liste_colonnes.append(dictColonne)
                if code == codeTemp:
                    index = idx
                idx += 1
        self.SetColonnes(liste_colonnes)
        self.parent.label_selection.SetLabel(_(u"%d colonnes sélectionnées") % len(liste_colonnes))
        if index != None :
            if index > len(liste_colonnes)-1 :
                index = len(liste_colonnes)-1
            self.SetSelection(index)

    def OnDoubleClick(self, event):
        code = self.GetCode()
        if code != None:
            self.parent.EnvoyerVersGauche(code)

    def Deplacer(self, sens=-1):
        code = self.GetCode()
        if code == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une colonne à déplacer dans la liste de droite !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        index = self.parent.colonnes_selection.index(code)
        if (sens == -1 and index == 0) or (sens == 1 and index == len(self.parent.colonnes_selection)-1):
            return
        self.parent.colonnes_selection.pop(index)
        self.parent.colonnes_selection.insert(index + sens, code)
        self.MAJ(code=code)

    def Monter(self, event):
        self.Deplacer(sens=-1)

    def Descendre(self, event):
        self.Deplacer(sens=1)


# --------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, colonnes_dispo=[], colonnes_defaut=[], colonnes_selection=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        # Mémorisation des colonnes
        self.colonnes_dispo = colonnes_dispo
        self.colonnes_defaut = colonnes_defaut
        self.colonnes_selection = colonnes_selection
        self.dict_colonnes = self.GetDictColonnes()

        intro = _(u"Vous pouvez configurer ici les colonnes de la liste. Double-cliquez sur les titres de colonnes disponibles pour les inclure dans votre sélection ou utilisez les flèches droite et gauche. Les flèches haut et bas permettent de modifier l'ordre des colonnes sélectionnées.")
        titre = _(u"Configuration de la liste")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Configuration2.png")

        # Elements
        self.box_elements_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Organisation des colonnes"))

        self.label_dispo = wx.StaticText(self, wx.ID_ANY, _(u"Colonnes disponibles"))
        self.ctrl_dispo = CTRL_Dispo(self)
        self.ctrl_dispo.SetMinSize((250, 50))

        self.ctrl_recherche_dispo = BarreRecherche(self, ctrl=self.ctrl_dispo)

        self.bouton_droite_double = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_double_droite.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_droite = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Avancer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_gauche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Reculer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_gauche_double = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_double_gauche.png"), wx.BITMAP_TYPE_ANY))

        self.label_selection = wx.StaticText(self, wx.ID_ANY, _(u"Colonnes sélectionnées"))
        self.ctrl_selection = CTRL_Selection(self)
        self.ctrl_selection.SetMinSize((250, 50))

        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_reinitialiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonDroiteDouble, self.bouton_droite_double)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGaucheDouble, self.bouton_gauche_double)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDroite, self.bouton_droite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonGauche, self.bouton_gauche)
        self.Bind(wx.EVT_BUTTON, self.ctrl_selection.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_selection.Descendre, self.bouton_descendre)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinitialiser)

        # Init contrôle
        self.ctrl_dispo.MAJ()
        self.ctrl_selection.MAJ()

    def __set_properties(self):
        self.label_dispo.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_selection.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_droite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la colonne (Vous pouvez également double-cliquer dessus)")))
        self.bouton_gauche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour retirer la colonne sélectionnée (Vous pouvez également double-cliquer dessus)")))
        self.bouton_droite_double.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner toutes les colonnes")))
        self.bouton_gauche_double.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour désélectionner toutes les colonnes")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour déplacer cette colonne")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour déplacer cette colonne")))
        self.bouton_reinitialiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici restaurer les valeurs par défaut")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.SetMinSize((750, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        box_elements = wx.StaticBoxSizer(self.box_elements_staticbox, wx.VERTICAL)
        grid_sizer_elements = wx.FlexGridSizer(rows=2, cols=4, vgap=5, hgap=5)

        grid_sizer_elements.Add(self.label_dispo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_elements.Add((20, 5), 0, wx.EXPAND, 0)
        grid_sizer_elements.Add(self.label_selection, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_elements.Add((20, 5), 0, wx.EXPAND, 0)

        grid_sizer_dispo = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_dispo.Add(self.ctrl_dispo, 1, wx.EXPAND, 0)
        grid_sizer_dispo.Add(self.ctrl_recherche_dispo, 1, wx.EXPAND, 0)
        grid_sizer_dispo.AddGrowableRow(0)
        grid_sizer_dispo.AddGrowableCol(0)
        grid_sizer_elements.Add(grid_sizer_dispo, 1, wx.EXPAND, 0)

        # Boutons déplacer
        grid_sizer_boutons_deplacer = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_boutons_deplacer.Add(self.bouton_droite, 0, 0, 0)
        grid_sizer_boutons_deplacer.Add(self.bouton_gauche, 0, 0, 0)
        grid_sizer_boutons_deplacer.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons_deplacer.Add(self.bouton_droite_double, 0, 0, 0)
        grid_sizer_boutons_deplacer.Add(self.bouton_gauche_double, 0, 0, 0)
        grid_sizer_elements.Add(grid_sizer_boutons_deplacer, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_elements.Add(self.ctrl_selection, 1, wx.EXPAND, 0)

        grid_sizer_boutons_elements = wx.FlexGridSizer(4, 1, 5, 5)
        grid_sizer_boutons_elements.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_boutons_elements.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_boutons_elements.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons_elements.Add(self.bouton_reinitialiser, 0, 0, 0)

        grid_sizer_elements.Add(grid_sizer_boutons_elements, 1, wx.EXPAND, 0)
        grid_sizer_elements.AddGrowableRow(1)
        grid_sizer_elements.AddGrowableCol(0)
        grid_sizer_elements.AddGrowableCol(2)
        box_elements.Add(grid_sizer_elements, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_elements, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def GetDictColonnes(self):
        dict_colonnes = {}
        for dictColonne in self.colonnes_dispo:
            dict_colonnes[dictColonne["code"]] = dictColonne
        return dict_colonnes

    def EnvoyerVersDroite(self, code=None):
        if code == None :
            # Envoyer toutes les colonnes vers la droite
            index = None
            for dictColonne in self.colonnes_dispo:
                if dictColonne["code"] not in self.colonnes_selection:
                    self.colonnes_selection.append(dictColonne["code"])
        else :
            # Envoyer une colonne
            index = self.ctrl_dispo.GetIndex()
            self.colonnes_selection.append(code)
        self.ctrl_dispo.MAJ(index=index)
        self.ctrl_selection.MAJ()

    def EnvoyerVersGauche(self, code=None):
        if code == None :
            # Envoyer toutes les colonnes vers la gauche
            index = None
            self.colonnes_selection = []
        else:
            # Envoyer une colonne
            index = self.ctrl_selection.GetIndex()
            self.colonnes_selection.remove(code)
        self.ctrl_dispo.MAJ()
        self.ctrl_selection.MAJ(index=index)

    def OnBoutonDroite(self, event):
        code = self.ctrl_dispo.GetCode()
        if code == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une colonne dans la liste de gauche !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        self.EnvoyerVersDroite(code)

    def OnBoutonGauche(self, event):
        code = self.ctrl_selection.GetCode()
        if code == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une colonne dans la liste de droite !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        self.EnvoyerVersGauche(code)

    def OnBoutonDroiteDouble(self, event):
        self.EnvoyerVersDroite(None)

    def OnBoutonGaucheDouble(self, event):
        self.EnvoyerVersGauche(None)

    def OnBoutonReinit(self, event=None):
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment réinitialiser la liste des colonnes ?"), _(u"Réinitialisation"), wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == wx.ID_YES:
            self.colonnes_selection = copy.copy(self.colonnes_defaut)
            self.ctrl_dispo.MAJ()
            self.ctrl_selection.MAJ()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
        
    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)

    def GetSelections(self, mode="code"):
        """ mode = 'code' ou 'dict' """
        if mode == "code" :
            return self.colonnes_selection
        else :
            listeTemp = []
            for code in self.colonnes_selection :
                listeTemp.append(self.dict_colonnes[code])
            return listeTemp







if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    colonnes_dispo = [{"nom": _(u"Colonne %d") % x, "code": "COLONNE%d" % x} for x in range(0, 300)]
    colonnes_defaut = ["COLONNE1", "COLONNE2", "COLONNE3", "COLONNE4", "COLONNE5"]
    colonnes_selection = ["COLONNE10", "COLONNE11", "COLONNE12", "COLONNE13", "COLONNE14", "COLONNE15"]
    dialog_1 = Dialog(None, colonnes_dispo=colonnes_dispo, colonnes_defaut=colonnes_defaut, colonnes_selection=colonnes_selection)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
