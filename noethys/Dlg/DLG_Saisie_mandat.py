#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import string
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Ultrachoice
from Ctrl import CTRL_Saisie_adresse
from Ctrl import CTRL_Saisie_date
import GestionDB
from Utils import UTILS_Prelevements
from Utils import UTILS_Titulaires
from Utils import UTILS_Texte
from Data import DATA_Bic
from Ol import OL_Prelevements
from Ol import OL_PES_mandat
import FonctionsPerso

from Utils.UTILS_Mandats import LISTE_SEQUENCES
from Utils.UTILS_Mandats import CTRL_Sequence


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import ParagraphAndImage, Image
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet



class MyValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return MyValidator()

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        for x in val:
            if x not in string.digits:
                return False
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in string.digits or chr(key) in string.letters :
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        return

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Banque(CTRL_Ultrachoice.CTRL):
    def __init__(self, parent, donnees=[]):
        CTRL_Ultrachoice.CTRL.__init__(self, parent, donnees) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeDonnees = self.GetListeDonnees()
        if len(listeDonnees) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetDonnees(listeDonnees)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDbanque, nom, rue_resid, cp_resid, ville_resid
        FROM banques
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDbanque, nom, rue_resid, cp_resid, ville_resid in listeDonnees :
            if rue_resid == None : rue_resid = ""
            if cp_resid == None : cp_resid = ""
            if ville_resid == None : ville_resid = ""
            self.dictDonnees[index] = { "ID" : IDbanque, "nom" : nom}
            listeItems.append({"label" : nom, "description" : u"%s %s %s" % (rue_resid, cp_resid, ville_resid)})
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection2(index)

    def GetID(self):
        index = self.GetSelection2()
        if index == -1 or self.dictDonnees.has_key(index) == False : 
            return None
        return self.dictDonnees[index]["ID"]
    
    def GetNomBanque(self):
        index = self.GetSelection2()
        if index == -1 or self.dictDonnees.has_key(index) == False : 
            return ""
        return self.dictDonnees[index]["nom"]
        


# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Titulaire(wx.Choice):
    def __init__(self, parent, IDfamille=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDfamille = IDfamille
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        if self.IDfamille == None :
            return []
        # Récupération de la liste des représentants de la famille
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, nom, prenom
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDfamille=%d AND IDcategorie=1
        GROUP BY individus.IDindividu
        ORDER BY nom, prenom;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeRepresentants = []
        for IDindividu, nom, prenom in listeDonnees :
            listeRepresentants.append({"IDindividu":IDindividu, "nom":nom, "prenom":prenom})
        
        # Remplissage du contrôle
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for donnees in listeRepresentants :
            label = u"%s %s" % (donnees["prenom"], donnees["nom"])
            self.dictDonnees[index] = { "ID" : donnees["IDindividu"], "nom " : label}
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]

    def GetNomIndividu(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["nom"]


# -----------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, IDmandat=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDmandat = IDmandat
                                
        # Mandat
        self.box_mandat_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques du mandat"))
        self.label_reference_mandat = wx.StaticText(self, -1, _(u"Référence Unique du Mandat (RUM) :"))
        self.ctrl_reference_mandat = wx.TextCtrl(self, -1, str(self.IDfamille), style=wx.TE_CENTRE)
        self.label_date_mandat = wx.StaticText(self, -1, _(u"Date de signature du mandat :"))
        self.ctrl_date_mandat = CTRL_Saisie_date.Date2(self)
        self.label_type_mandat = wx.StaticText(self, -1, _(u"Type de mandat :"))
        self.ctrl_type_mandat = wx.Choice(self, -1, choices=[_(u"Récurrent"), _(u"Ponctuel")])
        self.ctrl_type_mandat.Select(0) 
        self.ctrl_actif = wx.CheckBox(self, -1, "")
        self.ctrl_actif.SetValue(True)

        # RIB
        self.box_rib_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées bancaires"))
                
        # IBAN
        self.label_iban = wx.StaticText(self, -1, _(u"IBAN"))
        self.label_bic = wx.StaticText(self, -1, _(u"BIC"))
        self.ctrl_iban = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE)
        self.ctrl_bic = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE)
        
        self.image_valide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ok4.png"), wx.BITMAP_TYPE_ANY)
        self.image_nonvalide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Interdit2.png"), wx.BITMAP_TYPE_ANY)
        self.ctrl_controle = wx.StaticBitmap(self, -1, self.image_nonvalide)
        self.label_analyse_iban = wx.StaticText(self, -1, _(u"Analyse IBAN"))
        self.label_analyse_iban.SetForegroundColour((130, 130, 130))
        
##        # Etablissement
##        self.label_banque = wx.StaticText(self, -1, _(u"Etablissement"))
##        self.ctrl_banque = CTRL_Banque(self)
##        self.bouton_banques = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # Titulaire
        self.box_titulaire_staticbox = wx.StaticBox(self, -1, _(u"Titulaire du compte bancaire"))
        
        self.radio_membre = wx.RadioButton(self, -1, _(u"Le membre :"), style=wx.RB_GROUP)
        self.ctrl_membre = CTRL_Titulaire(self, IDfamille=IDfamille)
        
        self.radio_individu = wx.RadioButton(self, -1, _(u"Le titulaire suivant :"))
        self.label_individu_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_individu_nom = wx.TextCtrl(self, -1, u"")
        self.label_individu_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_individu_rue = wx.TextCtrl(self, -1, u"")
        self.label_individu_ville = wx.StaticText(self, -1, _(u"C.P. :"))
        self.ctrl_individu_ville = CTRL_Saisie_adresse.Adresse(self)

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_sequence = wx.StaticText(self, -1, _(u"Séquence suiv. :"))
        self.ctrl_sequence = CTRL_Sequence(self)
        self.ctrl_sequence.Select(0) 
        self.label_memo = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_memo = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_actif = wx.StaticText(self, -1, _(u"Mandat activé :"))
        
        # Liste des prélèvements
        self.box_prelevements_staticbox = wx.StaticBox(self, -1, _(u"Prélèvements rattachés"))
        self.notebook = wx.Notebook(self, -1, style=wx.BK_TOP)
        
        if self.IDmandat == None :
            IDmandatTemp = 0
        else :
            IDmandatTemp = self.IDmandat
        self.ctrl_prelevements = OL_Prelevements.ListView(self.notebook, id=-1, IDmandat=IDmandatTemp, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_prelevements.SetMinSize((50, 180)) 
        self.ctrl_prelevements.MAJ() 
        
        if self.IDmandat == None :
            IDmandatTemp = 0
        else :
            IDmandatTemp = self.IDmandat
        self.ctrl_pieces = OL_PES_mandat.ListView(self.notebook, id=-1, IDmandat=IDmandatTemp, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_pieces.SetMinSize((50, 180)) 
        self.ctrl_pieces.MAJ() 
        
        
        self.notebook.AddPage(self.ctrl_prelevements, _(u"Prélèvements directs SEPA (%d)") % len(self.ctrl_prelevements.donnees))
        self.notebook.AddPage(self.ctrl_pieces, _(u"Prélèvements PES ORMC (%d)") % len(self.ctrl_pieces.donnees))
        self.notebook.SetMinSize((50, 180)) 
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_TEXT, self.OnSaisieIBAN, self.ctrl_iban)
        self.Bind(wx.EVT_TEXT, self.OnSaisieIBAN, self.ctrl_bic)
##        self.Bind(wx.EVT_BUTTON, self.OnBoutonBanques, self.bouton_banques)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTitulaire, self.radio_membre)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTitulaire, self.radio_individu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        if self.IDmandat != None :
            self.SetTitle(_(u"Modification d'un mandat SEPA"))
            self.Importation() 
        else :
            self.SetTitle(_(u"Saisie d'un mandat SEPA"))
            self.ctrl_reference_mandat.SetValue(self.GetProchainRUM())
            self.ImportationAncienRIB()
        self.OnSaisieIBAN(None)
        self.OnRadioTitulaire(None)

    def __set_properties(self):
        self.ctrl_iban.SetMinSize((200, -1))
        self.ctrl_bic.SetMinSize((120, -1))
        self.ctrl_controle.SetToolTip(wx.ToolTip(_(u"Une coche verte apparaît si les coordonnées bancaires sont valides")))
##        self.ctrl_banque.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici l'établissement du compte")))
        self.ctrl_iban.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numéro IBAN")))
        self.ctrl_bic.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numéro BIC")))
##        self.bouton_banques.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des établissements bancaires")))
        self.radio_membre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un membre de la famille")))
        self.ctrl_membre.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici un membre de la famille en tant que titulaire du compte bancaire")))
        self.radio_individu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir manuellement un titulaire de compte bancaire")))
        self.ctrl_individu_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom de titulaire pour ce compte bancaire")))
        self.ctrl_individu_rue.SetToolTip(wx.ToolTip(_(u"Saisissez la rue de l'individu")))
        self.ctrl_reference_mandat.SetToolTip(wx.ToolTip(_(u"Lors de la saisie d'un mandat, il est attribué automatiquement par Noethys en fonction du RUM du dernier mandat saisi. Mais vous pouvez le modifier en fonction de vos besoins (Ex : '004567', 'XZA-34654', etc...). Attention, il doit s'agir d'une référence alphanumérique unique.")))
        self.ctrl_date_mandat.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de signature du mandat SEPA")))
        self.ctrl_type_mandat.SetToolTip(wx.ToolTip(_(u"Utilisez le type 'Récurrent' si le mandant est utilisable pour plusieurs prélèvements ou 'Ponctuel' s'il n'était destiné qu'à un prélèvement unique.")))
        self.ctrl_memo.SetToolTip(wx.ToolTip(_(u"Saisissez des observations")))
        self.ctrl_sequence.SetToolTip(wx.ToolTip(_(u"Sélectionnez la séquence de la prochaine opération (Automatique par défaut)\n\nImportant : Sélectionnez RCUR si ce mandat a déjà été utilisé hors de Noethys ou avant le 01/01/2014.")))
        self.ctrl_actif.SetToolTip(wx.ToolTip(_(u"Mandat activé ou non. Si vous le désactivez, il ne sera plus utilisable pour de futurs prélèvements.")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer le mandat au format PDF")))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer le mandat en PDF par Email")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
                
        # RIB
        box_rib = wx.StaticBoxSizer(self.box_rib_staticbox, wx.VERTICAL)
        
        grid_sizer_iban = wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5)
        grid_sizer_iban.Add(self.label_iban, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_iban.Add(self.label_bic, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_iban.Add( (2, 2), 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_iban.Add(self.ctrl_iban, 0, wx.EXPAND, 0)
        grid_sizer_iban.Add(self.ctrl_bic, 0, wx.EXPAND, 0)
        grid_sizer_iban.AddGrowableCol(0)
        box_rib.Add(grid_sizer_iban, 1, wx.LEFT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_controle = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_controle.Add(self.ctrl_controle, 0, wx.LEFT, 10)
        grid_sizer_controle.Add(self.label_analyse_iban, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_controle.AddGrowableCol(1)
        box_rib.Add(grid_sizer_controle, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Banque
##        grid_sizer_banque = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
##        grid_sizer_banque.Add(self.ctrl_banque, 0, wx.EXPAND, 0)
##        grid_sizer_banque.Add(self.bouton_banques, 0, wx.EXPAND, 0)
##        grid_sizer_banque.AddGrowableCol(0)
##        box_rib.Add(grid_sizer_banque, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
                
        # Titulaire
        box_titulaire = wx.StaticBoxSizer(self.box_titulaire_staticbox, wx.VERTICAL)
        grid_sizer_titulaire = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)

        grid_sizer_membre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_membre.Add(self.radio_membre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_membre.Add(self.ctrl_membre, 0, wx.EXPAND, 0)
        grid_sizer_membre.AddGrowableCol(1)
        grid_sizer_titulaire.Add(grid_sizer_membre, 1, wx.EXPAND, 0)
        
        grid_sizer_titulaire.Add(self.radio_individu, 0, 0, 0)
        
        grid_sizer_individu = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_individu.Add(self.label_individu_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_individu.Add(self.ctrl_individu_nom, 0, wx.EXPAND, 0)
        grid_sizer_individu.Add(self.label_individu_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_individu.Add(self.ctrl_individu_rue, 0, wx.EXPAND, 0)
        grid_sizer_individu.Add(self.label_individu_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_individu.Add(self.ctrl_individu_ville, 0, wx.EXPAND, 0)
        grid_sizer_individu.AddGrowableCol(1)
        grid_sizer_titulaire.Add(grid_sizer_individu, 1, wx.LEFT|wx.EXPAND, 47)
        grid_sizer_titulaire.AddGrowableCol(0)
        box_titulaire.Add(grid_sizer_titulaire, 1, wx.ALL|wx.EXPAND, 10)
        
        # Mandat SEPA
        box_mandat = wx.StaticBoxSizer(self.box_mandat_staticbox, wx.VERTICAL)
        grid_sizer_mandat = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_mandat.Add(self.label_reference_mandat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mandat.Add(self.ctrl_reference_mandat, 0, wx.EXPAND, 0)
        grid_sizer_mandat.Add(self.label_date_mandat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mandat.Add(self.ctrl_date_mandat, 0, wx.EXPAND, 0)
        grid_sizer_mandat.Add(self.label_type_mandat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mandat.Add(self.ctrl_type_mandat, 0, wx.EXPAND, 0)
        grid_sizer_mandat.Add(self.label_actif, 0, wx.ALIGN_RIGHT , 0)
        grid_sizer_mandat.Add(self.ctrl_actif, 0, wx.EXPAND, 0)
        grid_sizer_mandat.AddGrowableCol(1)
        box_mandat.Add(grid_sizer_mandat, 1, wx.ALL|wx.EXPAND, 10)
        
        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)

        grid_sizer_options = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_options.Add(self.label_sequence, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_sequence, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_memo, 0, wx.ALIGN_RIGHT , 0)
        grid_sizer_options.Add(self.ctrl_memo, 0, wx.EXPAND, 0)

        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_options.AddGrowableRow(1)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)

        # Placement de tous les box du contenu
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_droite = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        grid_sizer_gauche.Add(box_mandat, 1, wx.EXPAND, 0)
        grid_sizer_gauche.Add(box_rib, 1, wx.EXPAND, 0)
        
        grid_sizer_droite.Add(box_titulaire, 1, wx.EXPAND, 0)
        grid_sizer_droite.Add(box_options, 1, wx.EXPAND, 0)
        grid_sizer_droite.AddGrowableRow(1)
        grid_sizer_droite.AddGrowableCol(0)
        
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        
        # Liste des prélèvements
        box_prelevements = wx.StaticBoxSizer(self.box_prelevements_staticbox, wx.VERTICAL)
        box_prelevements.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_prelevements, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 

    def OnSaisieIBAN(self, event):
        self.ControleIBAN() 
        if event != None : event.Skip() 
    
    def ControleIBAN(self):
        iban = self.ctrl_iban.GetValue() 
        bic = self.ctrl_bic.GetValue() 
        if UTILS_Prelevements.ControleIBAN(iban) == True and UTILS_Prelevements.ControleBIC(bic) == True :
            self.MAJcontrole(iban, bic, True)
            return True
        else :
            self.MAJcontrole(iban, bic, False)
            return False
    
    def MAJcontrole(self, iban="", bic="", valide=True):
        if valide == True :
            self.ctrl_controle.SetBitmap(self.image_valide)
            texte = _(u"Coordonnées bancaires valides")
            infosBanque = DATA_Bic.RechercherBIC(bic)
            if infosBanque != None : 
                nomBanque, villeBanque = infosBanque
                texte += u"\n%s (%s)" % (nomBanque, villeBanque)
            else :
                texte += _(u"\nBanque inconnue")
        else :
            self.ctrl_controle.SetBitmap(self.image_nonvalide)
            texte = _(u"Coordonnées bancaires non valides")
        self.label_analyse_iban.SetLabel(texte) 
        
        
    def OnBoutonBanques(self, event):
        IDbanque = self.ctrl_banque.GetID()
        import DLG_Banques
        dlg = DLG_Banques.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_banque.MAJ() 
        self.ctrl_banque.SetID(IDbanque)

    def OnRadioTitulaire(self, event):
        etat = self.radio_membre.GetValue()
        self.ctrl_membre.Enable(etat)
        self.ctrl_individu_nom.Enable(not etat)
        self.ctrl_individu_rue.Enable(not etat)
        self.ctrl_individu_ville.Enable(not etat)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Rglements1")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def GetProchainRUM(self):
        """ Recherche le prochain RUM pour un nouveau mandat """
        DB = GestionDB.DB()
        req = """SELECT IDmandat, rum FROM mandats
        ORDER BY IDmandat DESC;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 :
            dernierRum = "0"
        else :
            IDmandat, dernierRum = listeDonnees[0]
        if dernierRum == None : 
            dernierRum = "0"
        rum = UTILS_Texte.Incrementer(dernierRum)
        return rum
    
    def ImportationAncienRIB(self):
        """ Importe le IBAN de l'ancien RIB s'il existe """
        try :
            DB = GestionDB.DB()
            req = """SELECT
            prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, prelevement_cle_iban, prelevement_bic
            FROM familles 
            WHERE IDfamille=%d;""" % self.IDfamille
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 : return
            etab, guichet, numero, cle_rib, cle_iban, bic = listeDonnees[0]

            if etab == None : etab = ""
            if guichet == None : guichet = ""
            if numero == None : numero = ""
            if cle_rib == None : cle_rib = ""
            if cle_iban == None or cle_iban == "" : 
                cle_iban = "FR76"
            if bic == None : bic = ""
            
            iban = cle_iban + etab + guichet + numero + cle_rib
            if len(iban) > 5 :
                self.ctrl_iban.SetValue(iban) 
            if len(bic) > 5 :
                self.ctrl_bic.SetValue(bic)
        except :
            pass

    def Importation(self):
        """ Importation des données """
        if self.IDfamille == None :
            return
        DB = GestionDB.DB()
        req = """SELECT IDfamille, rum, type, date, IDbanque, IDindividu, individu_nom, individu_rue, individu_cp, individu_ville, iban, bic, memo, sequence, actif
        FROM mandats 
        WHERE IDmandat=%d;""" % self.IDmandat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        self.IDfamille, rum, typeMandat, date, IDbanque, IDindividu, nom, rue, cp, ville, iban, bic, memo, sequence, actif = listeDonnees[0]

        if nom == None : nom = ""
        if rue == None : rue = ""
        if cp == None : cp = ""
        if ville == None : ville = ""
        if iban == None : iban = ""
        if bic == None : bic = ""
        if rum == None : rum = ""
        if memo == None : memo = ""
        
        # Mandat
        self.ctrl_reference_mandat.SetValue(rum) 
        self.ctrl_date_mandat.SetDate(date)        
        if typeMandat == "recurrent" :
            self.ctrl_type_mandat.Select(0)
        else :
            self.ctrl_type_mandat.Select(1)
        
        # Coords compte
        self.ctrl_iban.SetValue(iban) 
        self.ctrl_bic.SetValue(bic)
##        self.ctrl_banque.SetID(IDbanque)
        
        # Titulaire
        if IDindividu != None :
            self.radio_membre.SetValue(True)
            self.ctrl_membre.SetID(IDindividu)
        else :
            self.radio_individu.SetValue(True)
            self.ctrl_individu_nom.SetValue(nom)
            self.ctrl_individu_rue.SetValue(rue)
            self.ctrl_individu_ville.SetValueCP(cp)
            self.ctrl_individu_ville.SetValueVille(ville)
        
        # Mémo
        self.ctrl_memo.SetValue(memo) 
        self.ctrl_sequence.SetCode(sequence)
        
        # Actif
        if actif == 1 :
            self.ctrl_actif.SetValue(True) 
        else :
            self.ctrl_actif.SetValue(False) 
            

    def OnBoutonOk(self, event):
        # Récupération des données
##        IDbanque = self.ctrl_banque.GetID()
        IDindividu = self.ctrl_membre.GetID()
        nom = self.ctrl_individu_nom.GetValue()
        rue = self.ctrl_individu_rue.GetValue()
        cp = self.ctrl_individu_ville.GetValueCP()
        ville = self.ctrl_individu_ville.GetValueVille()
        iban = self.ctrl_iban.GetValue() 
        bic = self.ctrl_bic.GetValue() 
        rum = self.ctrl_reference_mandat.GetValue() 
        date = self.ctrl_date_mandat.GetDate() 
        typeMandat = self.ctrl_type_mandat.GetSelection() 
        memo = self.ctrl_memo.GetValue() 
        actif = self.ctrl_actif.GetValue() 

        if self.radio_membre.GetValue() == True :
            nom = None
            rue = None
            cp = None
            ville = None
        else :
            IDindividu = None

        # Vérification des données saisies
        if len(rum) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir la référence du mandat !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_reference_mandat.SetFocus()
            return

        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir la date de signature du mandat !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_mandat.SetFocus()
            return

        if UTILS_Prelevements.ControleIBAN(iban) == False :
            dlg = wx.MessageDialog(self, _(u"Le IBAN semble erroné !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_iban.SetFocus()
            return
        
        if UTILS_Prelevements.ControleBIC(bic) == False :
            dlg = wx.MessageDialog(self, _(u"Le BIC semble erroné !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_bic.SetFocus()
            return
            
##        if IDbanque == None :
##            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un établissement bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_banque.SetFocus()
##            return
        
        if self.radio_membre.GetValue() == True :
            if IDindividu == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas sélectionné de titulaire du compte bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_membre.SetFocus()
                return
        else :
            if nom == "" :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le titulaire du compte bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_individu_nom.SetFocus()
                return
        
        if typeMandat == 0 : 
            typeMandat = "recurrent"
        else :
            typeMandat = "ponctuel"
        
        sequence = self.ctrl_sequence.GetCode() 
        
        # Vérifie que le RUM n'est pas déjà attribué à un autre mandat
        if self.IDmandat == None :
            IDmandatTemp = 0
        else :
            IDmandatTemp = self.IDmandat
        DB = GestionDB.DB()
        req = """SELECT IDmandat, rum FROM mandats WHERE rum='%s' AND IDmandat !=%d;""" % (rum, IDmandatTemp) 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Le RUM saisi a déjà été enregistré pour un autre mandat alors qu'il doit être unique ! \n\nVeuillez en saisir un différent..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_reference_mandat.SetFocus() 
            return

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("IDfamille", self.IDfamille),
                ("rum", rum),
                ("type", typeMandat),
                ("date", date),
                ("IDbanque", None),
                ("IDindividu", IDindividu),
                ("individu_nom", nom),
                ("individu_rue", rue),
                ("individu_cp", cp),
                ("individu_ville", ville),
                ("iban", iban),
                ("bic", bic),
                ("memo", memo),
                ("sequence", sequence),
                ("actif", int(actif)),
            ]
        
        if self.IDmandat == None :
            self.IDmandat = DB.ReqInsert("mandats", listeDonnees)
        else :
            DB.ReqMAJ("mandats", listeDonnees, "IDmandat", self.IDmandat)
        DB.Close()

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDmandat(self):
        return self.IDmandat

    def OnBoutonEmail(self, event): 
        """ Envoi par mail """
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("MANDAT_SEPA", "pdf") , categorie="mandat_sepa")

    def OnBoutonImprimer(self, event):
        self.CreationPDF() 

    def CreationPDF(self, nomDoc=FonctionsPerso.GenerationNomDoc("MANDAT_SEPA", "pdf"), afficherDoc=True):
        dictChampsFusion = {}
        dictDonnees = {}
        
        # Récupère infos sur organisateur
        from Utils import UTILS_Organisateur
        dictOrganisateur = UTILS_Organisateur.GetDonnees(tailleLogo=(200, 200))
        
        # ICS
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero, code_ics
        FROM comptes_bancaires;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()       
        ics = ""
        if len(listeDonnees) > 0 :
            IDcompte, nomCompte, numeroCompte, ics = listeDonnees[0]
            if ics == None :
                ics = ""
         
        # Récupère données du mandat        
        titulaire_nom = ""
        titulaire_rue = ""
        titulaire_cp = ""
        titulaire_ville = ""
        
        if self.radio_membre.GetValue() :
            IDindividu = self.ctrl_membre.GetID() 
            if IDindividu != None :
                dictIndividus = UTILS_Titulaires.GetIndividus()
                titulaire_nom = dictIndividus[IDindividu]["nom_complet"]
                titulaire_rue = dictIndividus[IDindividu]["rue"]
                titulaire_cp = dictIndividus[IDindividu]["cp"]
                titulaire_ville = dictIndividus[IDindividu]["ville"]
        else :
            titulaire_nom = self.ctrl_individu_nom.GetValue()
            titulaire_rue = self.ctrl_individu_rue.GetValue()
            titulaire_cp = self.ctrl_individu_ville.GetValueCP()
            titulaire_ville = self.ctrl_individu_ville.GetValueVille()
            
        iban = self.ctrl_iban.GetValue() 
        bic = self.ctrl_bic.GetValue() 
        rum = self.ctrl_reference_mandat.GetValue() 
        date = self.ctrl_date_mandat.GetDate() 
        if date == None :
            date = ""
        if self.ctrl_type_mandat.GetSelection() == 0 :
            typeMandat = "recurrent"
        else :
            typeMandat = "ponctuel"

        dictDonnees = {
            "titulaire_nom" : titulaire_nom,
            "titulaire_rue" : titulaire_rue,
            "titulaire_cp" : titulaire_cp,
            "titulaire_ville" : titulaire_ville,
            "iban" : iban,
            "bic" : bic,
            "rum" : rum,
            "date" : date,
            "typeMandat" : typeMandat,
            "organisateur" : dictOrganisateur,
            "ics" : ics,
            }
        
        # Mémorisation pour la fusion Emails
        dictChampsFusion["{RUM}"] = rum
        dictChampsFusion["{DATE}"] = date

        # Lancement de l'édition du PDF
        Impression(dictDonnees, nomDoc=nomDoc, afficherDoc=afficherDoc)
        
        return dictChampsFusion


class Impression():
    def __init__(self, dictDonnees={}, nomDoc=FonctionsPerso.GenerationNomDoc("MANDAT_SEPA", "pdf"), afficherDoc=True):
        """ Imprime un mandat SEPA """
        styleSheet = getSampleStyleSheet()
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        self.inch = inch
        
        # Initialisation du PDF
        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        doc = SimpleDocTemplate(nomDoc)
        story = []
        
        largeurContenu = 500
        dataTableau = []

        # ---------------- Titre du document ----------------------------------------------------------------
        
        largeursColonnes = (100, largeurContenu-100-100, 100)

        titre = Paragraph(u"""<para align=center fontSize=16><b>Mandat de prélèvement SEPA</b></para>""", styleSheet['BodyText'])
        dataTableau.append([titre,])

        # Nom de l'organisateur
        ligne1 = Paragraph(u"""<para align=center fontSize=10>%s - ICS n°%s</para>""" % (dictDonnees["organisateur"]["nom"], dictDonnees["ics"]), styleSheet['BodyText'])
        ligne2 = Paragraph(u"""<para align=center fontSize=8>%s %s %s</para>""" % (dictDonnees["organisateur"]["rue"], dictDonnees["organisateur"]["cp"], dictDonnees["organisateur"]["ville"]), styleSheet['BodyText'])
        dataTableau.append([ [ligne1, ligne2],])

        # Mention légale obligatoire sur le SEPA
        mention_sepa = Paragraph(u"""
        <para align=left leading=10 fontSize=7>En signant ce mandat, vous autorisez %s à envoyer des instructions à votre banque pour débiter votre compte, et votre banque à débiter votre compte conformément aux instructions de %s.
        Vous bénéficiez du droit d'être remboursé par votre banque selon les conditions décrites dans la convention que vous avez passée avec elle.
        Une demande de remboursement doit être présentée dans les 8 semaines suivant la date de début de votre compte pour un prélèvement autorisé.
        Vos droits concernant le prélèvement sont expliqués dans un document que vous pouvez obtenir auprès de votre banque.
        </para>""" % (dictDonnees["organisateur"]["nom"], dictDonnees["organisateur"]["nom"]), styleSheet['BodyText'])
        dataTableau.append([mention_sepa,])
        
        # RUM
        dataTableau.append([Paragraph(_(u"<para align=center fontSize=8><b>Référence unique du mandat</b></para>"), styleSheet['BodyText']),])
        dataTableauTemp = [
            [Paragraph(_(u"<para align=right fontSize=10>RUM :</para>"), styleSheet['BodyText']), self.Cases(modele=[1 for x in range(38)], texte=dictDonnees["rum"])],
            ]
        style = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), "MIDDLE"), 
                            ])
        tableauTemp = Table(dataTableauTemp, [100, 400])
        tableauTemp.setStyle(style)
        dataTableau.append([tableauTemp,])

        # Nom et coordonnées et débiteur
        dataTableau.append([Paragraph(_(u"<para align=center fontSize=8><b>Identité et coordonnées du débiteur</b></para>"), styleSheet['BodyText']),])
        dataTableauTemp = [
            [Paragraph(_(u"<para align=right fontSize=10>Nom et prénom :</para>"), styleSheet['BodyText']), self.Cases(modele=[1 for x in range(38)], texte=dictDonnees["titulaire_nom"])],
            [Paragraph(_(u"<para align=right fontSize=10>Adresse :</para>"), styleSheet['BodyText']), self.Cases(modele=[1 for x in range(38)], texte=dictDonnees["titulaire_rue"])],
            [Paragraph(_(u"<para align=right fontSize=10>Code postal :</para>"), styleSheet['BodyText']), self.Cases(modele=[1 for x in range(38)], texte=dictDonnees["titulaire_cp"])],
            [Paragraph(_(u"<para align=right fontSize=10>Ville :</para>"), styleSheet['BodyText']), self.Cases(modele=[1 for x in range(38)], texte=dictDonnees["titulaire_ville"])],
            ]
        style = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), "MIDDLE"), 
                            ])
        tableauTemp = Table(dataTableauTemp, [100, 400])
        tableauTemp.setStyle(style)
        dataTableau.append([tableauTemp,])

        # Compte à débiter
        dataTableau.append([Paragraph(_(u"<para align=center fontSize=8><b>Compte à débiter</b></para>"), styleSheet['BodyText']),])
        
        iban = self.Cases(modele=[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1], texte=dictDonnees["iban"])
        bic = self.Cases(modele=[1 for x in range(11)], texte=dictDonnees["bic"])
        dataTableauTemp = [
            [Paragraph(_(u"<para align=right fontSize=10>IBAN :</para>"), styleSheet['BodyText']), iban],
            [Paragraph(_(u"<para align=right fontSize=10>BIC :</para>"), styleSheet['BodyText']), bic],
            ]
        style = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), "MIDDLE"), 
                            ])
        tableauTemp = Table(dataTableauTemp, [100, 400])
        tableauTemp.setStyle(style)
        dataTableau.append([tableauTemp,])
        
        # Type de paiement
        dataTableau.append([Paragraph(_(u"<para align=center fontSize=8><b>Type de paiement</b></para>"), styleSheet['BodyText']),])
        
        if dictDonnees["typeMandat"] == "recurrent" : 
            recurrent = "X"
            ponctuel = ""
        else :
            recurrent = ""
            ponctuel = "X"
        dataTableauTemp = [
            "", 
            Paragraph(_(u"<para align=left fontSize=10>Paiement récurrent :</para>"), styleSheet['BodyText']), 
            self.Cases(modele=[1,], texte=recurrent),
            "",
            Paragraph(_(u"<para align=left fontSize=10>Paiement ponctuel :</para>"), styleSheet['BodyText']), 
            self.Cases(modele=[1,], texte=ponctuel),
            ]
        style = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), "MIDDLE"), 
                            ('ALIGN', (0, 0), (-1, -1), "CENTER"), 
                            ])
        tableauTemp = Table([dataTableauTemp,], [100, 105, 10, 50, 105, 10])
        tableauTemp.setStyle(style)
        dataTableau.append([tableauTemp,])
        
        # Signature
        dataTableau.append([Paragraph(_(u"<para align=center fontSize=8><b>Signature</b></para>"), styleSheet['BodyText']),])
        dataTableauTemp = [
            [Paragraph(_(u"<para align=right fontSize=10>Fait à :</para>"), styleSheet['BodyText']), self.Cases(modele=[1 for x in range(38)])],
            [Paragraph(_(u"<para align=right fontSize=10>Le :</para>"), styleSheet['BodyText']), self.Cases(modele=[1, 1, 2, 1, 1, 2, 1, 1, 1, 1], texte="  /  /    ")],
            [Paragraph(_(u"<para align=right fontSize=10>Signature :</para>"), styleSheet['BodyText']), ""],
            ["", ""],
            ["", ""],
            ["", ""],
            ["", ""],
            ["", ""],
            ]
        style = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), "MIDDLE"), 
                            ])
        tableauTemp = Table(dataTableauTemp, [100, 400])
        tableauTemp.setStyle(style)
        dataTableau.append([tableauTemp,])

        # Mention CNIL
        mention_cnil = Paragraph(u"""
        <para align=left leading=10 fontSize=7>Les informations contenus dans le présent mandat, qui doit être complété, sont destinés à n'être utilisées par le créancier que pour la gestion
        de sa relation avec son client. Elles pourront donner lieu à l'exercice, par ce dernier, de ses droits d'oppositions, d'accès et de rectifications tels 
        que prévus aux articles 38 et suivants de la loi n°78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés.
        </para>""", styleSheet['BodyText'])
        dataTableau.append([mention_cnil,])
        
        
        
        
        # Formatage du tableau principal
        listeStyles = [
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black), 
            ('VALIGN', (0, 0), (-1, -1), "MIDDLE"), 
            ('TOPPADDING', (0, 0), (0, 0), 20), 
            ('BOTTOMPADDING', (0, 0), (0, 0), 25), 
            ]
        for ligne in (0, 3, 5, 7, 9, 11) :
            listeStyles.append(('BACKGROUND', (0, ligne), (-1, ligne), (0.8, 0.8, 0.8) ))
        style = TableStyle(listeStyles)
        tableau = Table(dataTableau, [largeurContenu,])
        tableau.setStyle(style)
        dataTableau.append(tableau)
        story.append(tableau)
            
        # Enregistrement du PDF
        try :
            doc.build(story)
        except Exception, err :
            print "Erreur dans ouverture PDF :", err
            if "Permission denied" in err :
                dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas créer le PDF.\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."), _(u"Erreur d'édition"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Affichage du PDF
        if afficherDoc == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)


    def Cases(self, modele=[1, 1, 1, 0, 1, 1, 1], texte="", largeurColonnes=10, couleur=(0.8, 0.8, 0.8)) :
        """ 
        1 = Case à avec texte avec cadre
        2 = Case avec texte sans cadre
        0 = Case sans texte et sans cadre
        """        
        if texte == None : texte = ""
        dataTableau = []
        largeursColonnes = []
        listeStyles = [
            ('VALIGN', (0, 0), (-1, -1), "MIDDLE"), 
            ('ALIGN', (0, 0), (-1, -1), "CENTER"), 
            ]
        indexColonne = 0
        indexTexte = 0
        for code in modele :
            largeursColonnes.append(largeurColonnes) 
            
            if code == 1 or code == 2 :
                if len(texte) > indexTexte :
                    dataTableau.append(texte[indexTexte])
                    indexTexte += 1
                else :
                    dataTableau.append("")
                if code == 1 :
                    listeStyles.append(('GRID', (indexColonne, 0), (indexColonne, -1), 0.25, couleur))
            else :
                dataTableau.append("")
            indexColonne += 1

        style = TableStyle(listeStyles)
        tableau = Table([dataTableau,], largeursColonnes)
        tableau.setStyle(style)
        return tableau





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=14, IDmandat=6)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
