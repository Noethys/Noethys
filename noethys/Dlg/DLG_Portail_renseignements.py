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
import wx.html as html
import GestionDB
import datetime
from Utils import UTILS_Dialogs
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_adresse
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_tel
from Ctrl import CTRL_Saisie_mail

from Dlg.DLG_Portail_demandes import CTRL_Log

if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC


DICT_RENSEIGNEMENTS = {"nom" : u"Nom", "prenom" : u"Prénom", "date_naiss" : u"date de naissance", "cp_naiss" : u"CP de naissance", "ville_naiss" : u"Ville de naissance", "adresse_auto" : u"Adresse rattachée", "rue_resid" : u"Rue de l'adresse", "cp_resid" : u"CP de l'adresse", "ville_resid" : u"Ville de l'adresse",
                    "tel_domicile" : u"Tél. Domicile", "tel_mobile" : u"Tél. Mobile", "mail" : u"Email", "profession" : u"Profession", "employeur" : u"Employeur", "travail_tel" : u"Tél. Pro.", "travail_mail" : u"Email Pro."}




class CTRL_Adresse_auto(wx.Choice):
    def __init__(self, parent, IDindividu=None, size=(-1, -1)):
        wx.Choice.__init__(self, parent, -1, size=size)
        self.parent = parent
        self.IDindividu = IDindividu
        self.SetToolTip(wx.ToolTip(_(u"Sélectionnez une adresse de rattachement ou saisissez une adresse")))

    def MAJ(self):
        if self.parent.IDindividu != None:
            listeItems = self.GetListeDonnees()
            self.SetItems(listeItems)
            if len(listeItems) > 0:
                self.Select(0)

    def GetListeDonnees(self):
        DB = GestionDB.DB()

        # Recherche des familles rattachées de l'individu
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
        FROM rattachements
        WHERE IDindividu=%d;""" % self.parent.IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeFamilles = []
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in listeDonnees:
            listeFamilles.append(IDfamille)
        if len(listeFamilles) == 0:
            self.dictDonnees = {}
            return []
        elif len(listeFamilles) == 1:
            condition = "(%s)" % listeFamilles[0]
        else:
            condition = str(tuple(listeFamilles))
        # Recherche des représentants des familles rattachées
        req = """SELECT individus.IDindividu, individus.nom, individus.prenom, rue_resid, cp_resid, ville_resid, tel_domicile
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDfamille IN %s;""" % condition  # J'ai enlevé ici "IDcategorie=1 AND " pour afficher également les contacts
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        self.dictDonnees = {0 : {"ID" : None} }
        listeNoms = [_(u"L'adresse suivante")]
        index = 1
        for IDindividu, nom, prenom, rue, cp, ville, tel_domicile in listeDonnees:
            if IDindividu != self.parent.IDindividu:
                if rue != "" and cp != "" and ville != "":
                    nomComplet = u"L'adresse de %s %s" % (nom, prenom)
                    listeNoms.append(nomComplet)
                    self.dictDonnees[index] = {"ID": IDindividu, "rue": rue, "cp": cp, "ville": ville, "tel_domicile": tel_domicile}
                    index += 1
        return listeNoms

    def SetID(self, ID=None):
        if ID == None :
            self.SetSelection(0)
            return True
        else :
            for index, values in self.dictDonnees.items():
                if values["ID"] == int(ID):
                    self.SetSelection(index)
                    return True
            return False

    def GetID(self):
        index = self.GetSelection()
        if index in (-1, 0): return None
        return self.dictDonnees[index]["ID"]




class Adresse(wx.Panel):
    def __init__(self, parent, IDindividu=None, size=(-1, -1)):
        wx.Panel.__init__(self, parent, id=-1, size=size, style=wx.TAB_TRAVERSAL)
        self.SetMinSize(size)
        self.IDindividu = IDindividu

        self.ctrl_adresse_auto = CTRL_Adresse_auto(self, IDindividu=IDindividu, size=(size[0], -1))
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.label_cp = wx.StaticText(self, -1, _(u"CP :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_adresse_auto, 0, wx.EXPAND, 0)

        grid_sizer_adresse_manuelle = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_adresse_manuelle.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse_manuelle.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_adresse_manuelle.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse_manuelle.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_adresse_manuelle.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_adresse_manuelle, 0, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_adresse_auto)

        # Init
        self.ctrl_adresse_auto.MAJ()
        self.OnChoix()

    def OnChoix(self, event=None):
        etat = self.ctrl_adresse_auto.GetID() == None
        self.label_cp.Enable(etat)
        self.label_rue.Enable(etat)
        self.ctrl_rue.Enable(etat)
        self.ctrl_ville.Enable(etat)

    def SetValeur(self, champ="", valeur=None):
        if champ == "adresse_auto" :
            resultat = self.ctrl_adresse_auto.SetID(valeur)
            self.OnChoix()
        if champ == "rue_resid" :
            resultat = True
            self.ctrl_rue.SetValue(valeur)
        if champ == "cp_resid" :
            resultat = self.ctrl_ville.SetValueCP(valeur)
        if champ == "ville_resid" :
            resultat = True
            self.ctrl_ville.SetValueVille(valeur)
        return resultat

    def GetValeurs(self):
        dictValeurs = {}

        adresse_auto = self.ctrl_adresse_auto.GetID()
        dictValeurs["adresse_auto"] = adresse_auto

        if adresse_auto == None :
            dictValeurs["rue_resid"] = self.ctrl_rue.GetValue()
            dictValeurs["cp_resid"] = self.ctrl_ville.GetValueCP()
            dictValeurs["ville_resid"] = self.ctrl_ville.GetValueVille()
        else :
            dictValeurs["rue_resid"] = ""
            dictValeurs["cp_resid"] = ""
            dictValeurs["ville_resid"] = ""

        return dictValeurs




class CTRL_Renseignements(ULC.UltimateListCtrl):
    def __init__(self, parent):
        ULC.UltimateListCtrl.__init__(self, parent, -1, agwStyle=wx.LC_REPORT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | wx.LC_NO_HEADER)
        self.parent = parent
        self.IDindividu = None

        self.EnableSelectionVista()

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Binds
        self.Bind(ULC.EVT_LIST_ITEM_CHECKED, self.OnCheck)

    def MAJ(self, IDindividu=None):
        self.IDindividu = IDindividu
        self.Freeze()
        self.ClearAll()
        self.Remplissage()
        self.MAJaffichage()
        if IDindividu != None :
            self.Importation(IDindividu)
        self.Thaw()

    def Remplissage(self):
        """ Remplissage """
        self.dictControles = {}

        # Création des colonnes
        largeurColonneDonnee = 300
        self.InsertColumn(0, _(u"Champ"), width=180)
        self.InsertColumn(1, _(u"Valeur"), width=largeurColonneDonnee+5, format=ULC.ULC_FORMAT_LEFT)

        # Création des lignes
        self.liste_lignes = [
            {"code": "nom", "label": _(u"Nom de famille"), "ctrl": wx.TextCtrl(self, -1, "", size=(largeurColonneDonnee, -1))},
            {"code": "prenom", "label": _(u"Prénom"), "ctrl": wx.TextCtrl(self, -1, "", size=(largeurColonneDonnee, -1))},

            {"code": "date_naiss", "label": _(u"Date de naissance"), "ctrl": CTRL_Saisie_date.Date2(self, size=(largeurColonneDonnee, -1))},
            {"code": "ville_naiss", "label": _(u"Ville de naissance"), "ctrl": CTRL_Saisie_adresse.Adresse(self, size=(largeurColonneDonnee, -1))},

            {"code": "adresse", "label": _(u"Adresse"), "ctrl": Adresse(self, IDindividu=self.IDindividu, size=(largeurColonneDonnee, 100))},

            {"code": "tel_domicile", "label": _(u"Tél. Domicile"), "ctrl": CTRL_Saisie_tel.Tel(self, intitule=_(u"Domicile"), size=(largeurColonneDonnee, -1))},
            {"code": "tel_mobile", "label": _(u"Tél. Mobile"), "ctrl": CTRL_Saisie_tel.Tel(self, intitule=_(u"Mobile"), size=(largeurColonneDonnee, -1))},
            {"code": "mail", "label": _(u"Email"), "ctrl": CTRL_Saisie_mail.Mail(self, size=(largeurColonneDonnee, -1))},

            {"code": "profession", "label": _(u"Profession"), "ctrl": wx.TextCtrl(self, -1, "", size=(largeurColonneDonnee, -1))},
            {"code": "employeur", "label": _(u"Employeur"), "ctrl": wx.TextCtrl(self, -1, "", size=(largeurColonneDonnee, -1))},
            {"code": "travail_tel", "label": _(u"Tél. Pro."), "ctrl": CTRL_Saisie_tel.Tel(self, intitule=_(u"Tél.Pro."), size=(largeurColonneDonnee, -1))},
            {"code": "travail_mail", "label": _(u"Email Pro."), "ctrl": CTRL_Saisie_mail.Mail(self, size=(largeurColonneDonnee, -1))},
            ]

        index = 0
        for ligne in self.liste_lignes :

            # Colonne Nom de colonne
            label = _(u" Colonne %d") % (index + 1)
            self.InsertStringItem(index, ligne["label"], it_kind=1)
            self.SetItemPyData(index, ligne)

            # Type de donnée
            item = self.GetItem(index, 1)
            ctrl = ligne["ctrl"]
            ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
            item.SetWindow(ctrl)
            self.SetItem(item)
            self.dictControles[index] = {"code" : ligne["code"], "ctrl": ctrl, "item": item}

            index += 1

    def GetCtrlByCode(self, code=""):
        for index, dictTemp in self.dictControles.items() :
            if dictTemp["code"] == code :
                return dictTemp["ctrl"]
        return None

    def GetIndexByCode(self, code=""):
        for index, dictTemp in self.dictControles.items() :
            if dictTemp["code"] == code:
                return index
        return -1

    def MAJaffichage(self):
        # Correction du bug d'affichage du ultimatelistctrl
        self._mainWin.RecalculatePositions()
        self.Layout()

    def OnCheck(self, event):
        """ Quand une sélection d'activités est effectuée... """
        index = event.m_itemIndex
        item = self.GetItem(index, 0)
        etat = item.IsChecked()
        self.dictControles[index]["ctrl"].Enable(etat)

    def SetCoche(self, index=None, etat=True):
        item = self.GetItem(index, 0)
        item.Check(etat)
        self.SetItem(item)
        self.dictControles[index]["ctrl"].Enable(etat)

    def CocherTout(self):
        self.Cocher(etat=True)

    def CocherRien(self):
        self.Cocher(etat=False)

    def Cocher(self, etat):
        for index in range(0, len(self.liste_lignes)):
            item = self.GetItem(index, 0)
            item.Check(etat)
            self.SetItem(item)
            self.SetCoche(index, etat=etat)

    def GetCoches(self):
        listeResultats = []
        for index in range(0, len(self.liste_lignes)):
            item = self.GetItem(index, 0)
            if item.IsChecked():
                code = self.dictControles[index]["code"]
                ctrl = self.dictControles[index]["ctrl"]
                listeResultats.append((code, ctrl))
        return listeResultats

    def Importation(self, IDindividu=None):
        DB = GestionDB.DB()
        req = """SELECT IDcivilite, nom, prenom, date_naiss, cp_naiss, ville_naiss, 
        adresse_auto, rue_resid, cp_resid, ville_resid, profession, employeur, 
        travail_tel, travail_mail, tel_domicile, tel_mobile, mail
        FROM individus WHERE IDindividu=%d;""" % IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :

            individu = listeDonnees[0]

            # Remplissage des champs
            self.GetCtrlByCode("nom").SetValue(individu[1])
            self.GetCtrlByCode("prenom").SetValue(individu[2])

            self.GetCtrlByCode("date_naiss").SetDate(individu[3])
            self.GetCtrlByCode("ville_naiss").SetValueCP(individu[4])
            self.GetCtrlByCode("ville_naiss").SetValueVille(individu[5])

            self.GetCtrlByCode("adresse").SetValeur("adresse_auto", individu[6])
            self.GetCtrlByCode("adresse").SetValeur("rue_resid", individu[7])
            self.GetCtrlByCode("adresse").SetValeur("cp_resid", individu[8])
            self.GetCtrlByCode("adresse").SetValeur("ville_resid", individu[9])

            self.GetCtrlByCode("profession").SetValue(individu[10])
            self.GetCtrlByCode("employeur").SetValue(individu[11])

            self.GetCtrlByCode("travail_tel").SetNumero(individu[12])
            self.GetCtrlByCode("travail_mail").SetMail(individu[13])
            self.GetCtrlByCode("tel_domicile").SetNumero(individu[14])
            self.GetCtrlByCode("tel_mobile").SetNumero(individu[15])
            self.GetCtrlByCode("mail").SetMail(individu[16])

        self.CocherRien()

# -----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Html(html.HtmlWindow):
    def __init__(self, parent, texte="", couleurFond=(255, 255, 255), style=wx.SIMPLE_BORDER):
        html.HtmlWindow.__init__(self, parent, -1, style=style)  # , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(3)
        self.couleurFond = couleurFond
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetTexte(texte)

    def SetTexte(self, texte=""):
        self.SetPage(u"""<BODY><FONT SIZE=3 COLOR='#000000'>%s</FONT></BODY>""" % texte)
        self.SetBackgroundColour(self.couleurFond)



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
        titre = _(u"Traitement manuel des renseignements")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Cotisation.png")

        # Détail demande
        self.box_demande_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Détail de la demande"))
        self.ctrl_demande = CTRL_Html(self, couleurFond=self.GetBackgroundColour())
        self.ctrl_demande.SetMinSize((275, 100))

        # Renseignements
        self.box_renseignements_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Renseignements"))
        self.ctrl_renseignements = CTRL_Renseignements(self)

        # Journal
        self.box_journal_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Journal d'évènements"))
        self.ctrl_log = CTRL_Log(self)
        self.ctrl_log.SetMinSize((100, 80))
        self.bouton_traiter = CTRL_Bouton_image.CTRL(self, texte=_(u"Appliquer la demande"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_reinit = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler les modifications"), cheminImage="Images/32x32/Actualiser.png")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonTraiter, self.bouton_traiter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)

        # Init
        self.ctrl_renseignements.MAJ()

        # Importation
        if self.parent != None :
            self.ctrl_renseignements.MAJ(self.track.IDindividu)
            self.ctrl_demande.SetTexte(self.parent.parent.ctrl_description.GetTexte())


    def __set_properties(self):
        self.bouton_traiter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer la demande")))
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler les modifications")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour commencer le traitement des demandes")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1,wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(2, 1, 10, 10)

        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)

        # Renseignements
        box_grille = wx.StaticBoxSizer(self.box_renseignements_staticbox, wx.VERTICAL)
        box_grille.Add(self.ctrl_renseignements, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_haut.Add(box_grille, 1, wx.EXPAND, 10)

        grid_sizer_droit = wx.FlexGridSizer(2, 1, 10, 10)

        # Demande
        box_demande = wx.StaticBoxSizer(self.box_demande_staticbox, wx.VERTICAL)
        box_demande.Add(self.ctrl_demande, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_droit.Add(box_demande, 1, wx.EXPAND, 10)

        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableRow(1)
        grid_sizer_droit.AddGrowableCol(0)

        grid_sizer_haut.Add(grid_sizer_droit, 1, wx.EXPAND, 10)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(0)

        grid_sizer_contenu.Add(grid_sizer_haut, 1, wx.EXPAND, 10)

        # Journal
        box_journal = wx.StaticBoxSizer(self.box_journal_staticbox, wx.VERTICAL)
        grid_sizer_journal = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_journal.Add(self.ctrl_log, 0, wx.EXPAND, 0)

        sizer_boutons = wx.BoxSizer(wx.VERTICAL)
        sizer_boutons.Add(self.bouton_traiter, 1, wx.EXPAND, 0)
        sizer_boutons.Add(self.bouton_reinit, 1, wx.EXPAND | wx.TOP, 5)
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
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
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
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonTraiter(self, event=None):
        self.parent.EcritLog(_(u"Application de la demande de modification de renseignements"), self.ctrl_log)

        # Recherche le détail des renseignements associés
        DB = GestionDB.DB()
        req = """SELECT champ, valeur
        FROM portail_renseignements
        WHERE IDaction=%d;""" % self.track.IDaction
        DB.ExecuterReq(req)
        listeRenseignements = DB.ResultatReq()
        DB.Close()

        liste_champs_importes = []
        listeAnomalies = []
        for champ, valeur in listeRenseignements:

            try :
                # Formatage des valeurs
                if champ == "date_naiss":
                    valeur = datetime.datetime.strptime(valeur, '%d/%m/%Y')
                    valeur = datetime.date(year=valeur.year, month=valeur.month, day=valeur.day)

                # Remplissage
                if "date" in champ :
                    self.ctrl_renseignements.GetCtrlByCode(champ).SetDate(valeur)
                elif champ == "adresse_auto" :
                    resultat = self.ctrl_renseignements.GetCtrlByCode("adresse").SetValeur("adresse_auto", valeur)
                elif champ == "rue_resid" :
                    resultat = self.ctrl_renseignements.GetCtrlByCode("adresse").SetValeur("rue_resid", valeur)
                elif champ == "cp_resid" :
                    resultat = self.ctrl_renseignements.GetCtrlByCode("adresse").SetValeur("cp_resid", valeur)
                elif champ == "ville_resid" :
                    resultat = self.ctrl_renseignements.GetCtrlByCode("adresse").SetValeur("ville_resid", valeur)
                elif champ == "cp_naiss" :
                    resultat = self.ctrl_renseignements.GetCtrlByCode("ville_naiss").SetValueCP(valeur)
                elif champ == "ville_naiss" :
                    resultat = self.ctrl_renseignements.GetCtrlByCode("ville_naiss").SetValueVille(valeur)
                elif "tel" in champ:
                    self.ctrl_renseignements.GetCtrlByCode(champ).SetNumero(valeur)
                elif "mail" in champ:
                    self.ctrl_renseignements.GetCtrlByCode(champ).SetMail(valeur)
                else :
                    self.ctrl_renseignements.GetCtrlByCode(champ).SetValue(valeur)

                # Coche la ligne
                if champ in ("adresse_auto", "rue_resid", "cp_resid", "ville_resid") :
                    index = self.ctrl_renseignements.GetIndexByCode("adresse")
                elif champ == "cp_naiss" :
                    index = self.ctrl_renseignements.GetIndexByCode("ville_naiss")
                else :
                    index = self.ctrl_renseignements.GetIndexByCode(champ)
                self.ctrl_renseignements.SetCoche(index, etat=True)

                liste_champs_importes.append(champ)

            except Exception as err:
                self.parent.EcritLog(_(u"Le champ '%s' n'a pas pu être importé. Erreur : %s") % (DICT_RENSEIGNEMENTS[champ], err), self.ctrl_log)
                listeAnomalies.append(champ)

        # Création du texte de réponse
        if len(liste_champs_importes) == 0 :
            reponse = _(u"Aucun renseignement modifié")
        elif len(liste_champs_importes) == 1 :
            reponse = _(u"1 renseignement modifié")
        else :
            reponse = _(u"%d renseignements modifiés") % len(liste_champs_importes)

        if len(liste_champs_importes) > 0 :
            reponse += u" (%s)" % ", ".join([DICT_RENSEIGNEMENTS[champ] for champ in liste_champs_importes])

        self.parent.EcritLog(_(u"Réponse : %s") % reponse, self.ctrl_log)

        self.reponse = reponse


    def OnBoutonReinit(self, event):
        self.ctrl_renseignements.MAJ(self.track.IDindividu)
        self.ctrl_renseignements.Importation(self.track.IDindividu)

    def OnBoutonOk(self, event=None):
        # Sauvegarde
        listeDonnees = []
        for champ, ctrl in self.ctrl_renseignements.GetCoches() :

            # Validation
            if hasattr(ctrl, "Validation") :
                if ctrl.Validation() == False :
                    dlg = wx.MessageDialog(self, _(u"La valeur du champ '%s' semble incorrecte !") % DICT_RENSEIGNEMENTS[champ], _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

            # Préparation des données à sauvegarder
            if "date" in champ:
                listeDonnees.append((champ, ctrl.GetDate()))
            elif "adresse" in champ:
                valeurs = ctrl.GetValeurs()
                listeDonnees.append(("adresse_auto", valeurs["adresse_auto"]))
                listeDonnees.append(("rue_resid", valeurs["rue_resid"]))
                listeDonnees.append(("cp_resid", valeurs["cp_resid"]))
                listeDonnees.append(("ville_resid", valeurs["ville_resid"]))
            elif champ in ("cp_naiss", "ville_naiss"):
                listeDonnees.append(("cp_naiss", ctrl.GetValueCP()))
                listeDonnees.append(("ville_naiss", ctrl.GetValueVille()))
            elif "tel" in champ:
                listeDonnees.append((champ, ctrl.GetNumero()))
            elif "mail" in champ:
                listeDonnees.append((champ, ctrl.GetMail()))
            else:
                listeDonnees.append((champ, ctrl.GetValue()))

        # Enregistrement
        DB = GestionDB.DB()
        DB.ReqMAJ("individus", listeDonnees, "IDindividu", self.track.IDindividu)
        DB.Close()

        # Fermeture de la dlg
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