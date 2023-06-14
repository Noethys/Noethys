#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
import GestionDB
import wx.html as html
from Utils import UTILS_Dates
from Utils import UTILS_Texte

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES, LISTE_COLONNES, LISTE_METHODES



class CTRL_Activites(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, -1)
        self.parent = parent
        self.dictDonnees = {}
        self.MAJ()

    def MAJ(self):
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY date_fin DESC
        ;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()
        DB.Close()
        if len(listeActivites) == 0 :
            self.Enable(False)
        listeLabels = []
        index = 0
        for IDactivite, nom in listeActivites :
            self.dictDonnees[index] = IDactivite
            if nom == None : nom = u"Activité inconnue"
            listeLabels.append(nom)
            index += 1
        self.SetItems(listeLabels)

    def SetID(self, IDactivite=None):
        for index, IDactiviteTmp in self.dictDonnees.items() :
            if IDactiviteTmp == IDactivite :
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]

    def GetLabelActivite(self):
        if self.GetID() == None :
            return _(u"Aucune")
        else :
            return self.GetStringSelection()



class CTRL_Tarifs(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25, couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.BORDER_THEME | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.source = ""
        self.couleurFond = couleurFond
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(10)
        self.SetMinSize((-1, hauteur))
        self.SetTexte(texte)

    def SetTexte(self, texte=u""):
        self.source = texte
        self.SetPage(texte)
        self.SetBackgroundColour(self.couleurFond)

    def GetSource(self):
        return self.source

    def MAJ(self, IDactivite=None):
        source = self.GetHTML(IDactivite=IDactivite)
        self.SetTexte(source)

    def GetHTML(self, IDactivite=None):
        if IDactivite == None :
            return ""

        DB = GestionDB.DB()

        # Importation des infos sur l'activité
        req = """SELECT nom, date_debut, date_fin
        FROM activites
        WHERE IDactivite=%d
        ;""" % IDactivite
        DB.ExecuterReq(req)
        listeInfos = DB.ResultatReq()

        if len(listeInfos) == 0 :
            return ""

        activite_nom, activite_date_debut, activite_date_fin = listeInfos[0]

        # Importation des tarifs
        req = """SELECT IDtarif, categories_tarifs, date_debut, date_fin, methode, noms_tarifs.IDnom_tarif, noms_tarifs.nom
        FROM tarifs
        LEFT JOIN noms_tarifs ON noms_tarifs.IDnom_tarif = tarifs.IDnom_tarif
        WHERE tarifs.IDactivite=%d
        ORDER BY date_debut DESC;""" % IDactivite
        DB.ExecuterReq(req)
        listeTarifs = DB.ResultatReq()

        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs
        WHERE IDactivite=%d;""" % IDactivite
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        dictCategories = {}
        for IDcategorie_tarif, nom in listeCategories :
            dictCategories[IDcategorie_tarif] = nom

        # Importation des lignes de tarif
        champsTable = ", ".join(CHAMPS_TABLE_LIGNES)
        req = """SELECT %s
        FROM tarifs_lignes
        WHERE IDactivite=%d
        ORDER BY num_ligne;""" % (champsTable, IDactivite)
        DB.ExecuterReq(req)
        listeLignes = DB.ResultatReq()

        DB.Close()

        source = []

        source.append(u"<FONT SIZE=+1><B>%s</B></FONT>" % activite_nom)
        source.append(u"<HR WIDTH='100%'>")

        if len(listeTarifs) == 0 :
            source.append(u"<P>Aucun tarif</P>")

        for IDtarif, categories_tarifs, date_debut, date_fin, methode, IDnom_tarif, nom_prestation in listeTarifs :
            listeCategories = UTILS_Texte.ConvertStrToListe(categories_tarifs)
            liste_temp = []
            for IDcategorie_tarif in listeCategories :
                liste_temp.append(dictCategories[IDcategorie_tarif])
            texte_categories = u", ".join(liste_temp)

            if True :#IDtarif in liste_tarifs_valides :

                # Création des champs
                index = 0
                for dictMethode in LISTE_METHODES :
                    if dictMethode["code"] == methode :
                        champs = dictMethode["champs"]
                    index += 1

                tableau = []
                ligne = []
                dict_remplissage_colonnes = {}
                numColonne = 0
                for code in champs :
                    for dict_colonne in LISTE_COLONNES :
                        if dict_colonne["code"] == code :
                            ligne.append(dict_colonne["label"])
                            dict_remplissage_colonnes[numColonne] = 0
                    numColonne += 1
                tableau.append(ligne)

                numLigne = 0
                for valeurs in listeLignes :
                    IDtarif_ligne = valeurs[2]
                    code = valeurs[3]

                    ligne = []
                    if IDtarif == IDtarif_ligne :
                        dictValeurs = {}

                        # Récupération des valeurs de la base
                        indexValeur = 0
                        for valeur in valeurs :
                            if valeur == "None" : valeur = None
                            dictValeurs[CHAMPS_TABLE_LIGNES[indexValeur]] = valeur
                            indexValeur += 1

                        # Remplissage de la ligne
                        numColonne = 0
                        for codeChamp in champs :
                            valeur = dictValeurs[codeChamp]
                            if type(valeur) == int or type(valeur) == float :
                                if codeChamp in ("montant_unique", "montant_min", "montant_max", "ajustement", "revenu_min", "revenu_max") :
                                    valeur = u"%.2f %s" % (valeur, SYMBOLE)
                                else :
                                    valeur = str(valeur)
                            if valeur == "None" : valeur = ""
                            if codeChamp == "date" and valeur != None :
                                valeur = UTILS_Dates.DateEngFr(valeur)
                            if valeur == None : valeur = ""
                            ligne.append(valeur)

                            if valeur != "" :
                                dict_remplissage_colonnes[numColonne] += 1

                            numColonne += 1


                        tableau.append(ligne)

                        numLigne += 1

                # Enlève des colonnes vides
                numColonne = 0
                tableau2 = []
                for ligne in tableau :

                    ligne2 = []
                    numColonne = 0
                    for valeur in ligne :
                        if dict_remplissage_colonnes[numColonne] > 0 :
                            ligne2.append(valeur)
                        numColonne += 1
                    tableau2.append(ligne2)

                #print (nom_prestation, date_debut, date_fin)
                #for ligne in tableau2 :
                #    print "   ", ligne

                source.append(u"<P><B>%s</B><BR><FONT SIZE=-2>%s - Tarif à partir du %s</FONT></P>" % (nom_prestation, texte_categories, UTILS_Dates.DateEngFr(date_debut)))

                source.append(u"<P><TABLE BORDER CELLSPACING=1 BORDER=0>")

                for ligne in tableau2 :
                    source.append(u"<TR ALIGN=CENTER>")
                    for valeur in ligne :
                        source.append(u"<TD>%s</TD>" % valeur)
                    source.append(u"</TR>")
                source.append(u"</TABLE></P>")


        return "\n".join(source)

    def Apercu(self, event=None):
        # Aperçu avant impression
        html = self.GetSource()
        printout = HtmlPrintout(html)
        printout2 = HtmlPrintout(html)
        preview = wx.PrintPreview(printout, printout2)

        preview.SetZoom(100)
        frame = wx.GetApp().GetTopWindow()
        preview_window = wx.PreviewFrame(preview, None, _(u"Aperçu avant impression"))
        preview_window.Initialize()
        if 'phoenix' not in wx.PlatformInfo:
            preview_window.MakeModal(False)
        preview_window.SetPosition(frame.GetPosition())
        preview_window.SetSize(frame.GetSize())
        preview_window.Show(True)


class HtmlPrintout(wx.html.HtmlPrintout):
    def __init__(self, html=""):
        wx.html.HtmlPrintout.__init__(self)
        self.SetHtmlText(html)
        self.SetMargins(10, 10, 10, 10, spaces=0)


class DLG_Tarifs(wx.Dialog):
    def __init__(self, parent, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self.ctrl_tarifs = CTRL_Tarifs(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Propriétés
        self.SetTitle(_(u"Détail des tarifs"))
        self.SetMinSize((700, 500))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_tarifs, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

        # Init
        self.ctrl_tarifs.MAJ(IDactivite)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedestarifs")

    def OnBouton_ok(self, event):
        self.EndModal(wx.ID_OK)




class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   

        # Bandeau
        intro = _(u"Vous pouvez consulter ici la liste des tarifs d'une activité. Cette liste sommaire est uniquement destinée à la consultation. Le paramétrage des tarifs se fait depuis la commande Activités du menu Paramétrage. Cliquez sur le nom d'une activité dans la liste de gauche pour afficher les tarifs correspondants.")
        titre = _(u"Liste des tarifs")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # Activités
        self.box_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((300, -1))
        
        # Tarifs
        self.box_tarifs_staticbox = wx.StaticBox(self, -1, _(u"Tarifs"))
        self.ctrl_tarifs = CTRL_Tarifs(self)
        self.ctrl_tarifs.MAJ()

        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LISTBOX, self.OnChoixActivite, self.ctrl_activites)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)


    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((990, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Activités
        box_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)
        box_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(box_activites, 1, wx.EXPAND, 0)


        # Tarifs
        box_tarifs = wx.StaticBoxSizer(self.box_tarifs_staticbox, wx.VERTICAL)
        grid_sizer_tarifs = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)


        grid_sizer_tarifs.Add(self.ctrl_tarifs, 0, wx.EXPAND, 0)

        grid_sizer_boutons_tarifs = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_tarifs.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_tarifs.Add(grid_sizer_boutons_tarifs, 1, wx.EXPAND, 0)

        grid_sizer_tarifs.AddGrowableRow(0)
        grid_sizer_tarifs.AddGrowableCol(0)
        box_tarifs.Add(grid_sizer_tarifs, 1, wx.ALL|wx.EXPAND, 5)

        grid_sizer_contenu.Add(box_tarifs, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)

        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
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

    def OnChoixActivite(self, event):
        IDactivite = self.ctrl_activites.GetID()
        self.ctrl_tarifs.MAJ(IDactivite)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedestarifs")
        
    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    #dialog_1 = DLG_Tarifs(None, IDactivite=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
