#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import os
import sys

import GestionDB

import CTRL_Bandeau
import CTRL_Saisie_date
import CTRL_Ultrachoice
import CTRL_Liste_factures

import UTILS_Parametres
import UTILS_Helios
import UTILS_Dates
import UTILS_Organisateur
import FonctionsPerso

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")


class CTRL_Type_impression(CTRL_Ultrachoice.CTRL):
    def __init__(self, parent, donnees=[]):
        CTRL_Ultrachoice.CTRL.__init__(self, parent, donnees=donnees) 
        self.parent = parent
        self.SetDonnees(donnees)
        self.Select(0)
                                        
    def SetID(self, index=0):
        self.SetSelection2(index)

    def GetID(self):
        return self.GetSelection2()
    
    def GetType(self):
        if self.GetSelection2() == 0 : return "detail"
        if self.GetSelection2() == 1 : return "simple"
        if self.GetSelection2() == 2 : return "recap"

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, filtres=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        # Bandeau
        intro = _(u"Vous pouvez ici exporter les factures au format ROLMRE pour H�lios. Cochez les factures � inclure dans le r�le puis cliquez sur le bouton Fichier pour g�n�rer un fichier de transfert normalis� ou le bouton Impression pour imprimer des versions papier.")
        titre = _(u"Export vers H�lios (ROLMRE)")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Helios.png")
        
        # Factures
        self.box_factures_staticbox = wx.StaticBox(self, -1, _(u"Factures"))
        self.ctrl_factures = CTRL_Liste_factures.CTRL(self, filtres=filtres)
        
        # Param�tres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Param�tres du r�le"))
        self.label_date = wx.StaticText(self, -1, _(u"Date d'�mission :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.label_exercice = wx.StaticText(self, -1, _(u"Exercice :"))
        self.ctrl_exercice = wx.TextCtrl(self, -1, u"")
        self.label_num_role = wx.StaticText(self, -1, _(u"Num�ro de r�le :"))
        self.ctrl_num_role = wx.TextCtrl(self, -1, u"")
        self.label_code_coll = wx.StaticText(self, -1, _(u"Code collectivit� :"))
        self.ctrl_code_coll = wx.TextCtrl(self, -1, u"")
        self.label_code_nat = wx.StaticText(self, -1, _(u"Code Nature :"))
        self.ctrl_code_nat = wx.TextCtrl(self, -1, u"")
        self.label_code_rec = wx.StaticText(self, -1, _(u"Code Recette :"))
        self.ctrl_code_rec = wx.TextCtrl(self, -1, u"")
        
        self.ctrl_code_coll.SetMaxLength(2)
        self.ctrl_code_nat.SetMaxLength(2)
        self.ctrl_code_rec.SetMaxLength(2)
        self.ctrl_num_role.SetMaxLength(2)
        self.ctrl_exercice.SetMaxLength(4)

        self.ctrl_code_coll.SetMinSize((50, -1))
        self.ctrl_code_nat.SetMinSize((50, -1))
        self.ctrl_code_rec.SetMinSize((50, -1))
        self.ctrl_num_role.SetMinSize((50, -1))

        # Sortie
        self.box_fichier_staticbox = wx.StaticBox(self, -1, _(u"Fichier"))
        self.box_impression_staticbox = wx.StaticBox(self, -1, _(u"Impression"))
        self.bouton_fichier = CTRL_Bouton_image.CTRL(self, texte=_(u"G�n�rer le fichier ROLMRE"), cheminImage="Images/32x32/Disk.png")
        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.label_type.Show(False)
        self.ctrl_type = CTRL_Type_impression(self, donnees=[ {"label" : _(u"R�le d�taill�"), "description" : _(u"D�tail des prestations par famille"), "image" : wx.Bitmap(u"Images/32x32/Facture.png", wx.BITMAP_TYPE_ANY)},
                                                                    {"label" : _(u"R�le simplifi�"), "description" : _(u"Total des prestations par famille"), "image" : wx.Bitmap(u"Images/32x32/Document_1.png", wx.BITMAP_TYPE_ANY)},
                                                                    {"label" : _(u"R�capitulatif"), "description" : _(u"Total des prestations par activit�"), "image" : wx.Bitmap(u"Images/32x32/Document_2.png", wx.BITMAP_TYPE_ANY)},
                                                                    ])
        self.bouton_apercu = CTRL_Bouton_image.CTRL(self, texte=_(u"Aper�u"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_apercu.SetMinSize((100, -1)) 
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonFichier, self.bouton_fichier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer) 
        
        # Init contr�les
        self.ctrl_date.SetDate(datetime.date.today())
        self.ctrl_num_role.SetValue("%02d" % datetime.date.today().month)
        self.ctrl_exercice.SetValue("%04d" % datetime.date.today().year)
        self.ctrl_code_coll.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="rolmre", nom="code_col", valeur=""))
        self.ctrl_code_nat.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="rolmre", nom="code_nat", valeur=""))
        self.ctrl_code_rec.SetValue(UTILS_Parametres.Parametres(mode="get", categorie="rolmre", nom="code_rec", valeur=""))

    def __set_properties(self):
        self.ctrl_date.SetToolTipString(_(u"Saisissez la date d'�mission du r�le"))
        self.ctrl_code_coll.SetToolTipString(_(u"Saisissez ici le code Collectivit� du r�le (ROLCOL)"))
        self.ctrl_exercice.SetToolTipString(_(u"Saisissez ici le code Exercice du r�le (ROLEX)"))
        self.ctrl_code_nat.SetToolTipString(_(u"Saisissez ici le code Nature du r�le (ROLNAT)"))
        self.ctrl_num_role.SetToolTipString(_(u"Saisissez ici le num�ro de r�le du r�le (ROLROL)"))
        self.ctrl_code_rec.SetToolTipString(_(u"Saisissez ici le code Recette du r�le (ROLREC)"))
        self.bouton_fichier.SetToolTipString(_(u"Cliquez ici pour g�n�rer le fichier ROLMRE"))
        self.ctrl_type.SetToolTipString(_(u"S�lectionnez ici le type de l'impression"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour afficher le r�le au format PDF"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((740, 740))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Factures
        box_factures = wx.StaticBoxSizer(self.box_factures_staticbox, wx.VERTICAL)
        box_factures.Add(self.ctrl_factures, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_factures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Param�tres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=8, vgap=5, hgap=10)
        
        grid_sizer_parametres.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_parametres.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_num_role, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_num_role, 0, 0, 0)
        grid_sizer_parametres.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_code_nat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_code_nat, 0, 0, 0)

        grid_sizer_parametres.Add(self.label_exercice, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_exercice, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_code_coll, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_code_coll, 0, 0, 0)
        grid_sizer_parametres.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_code_rec, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_code_rec, 0, 0, 0)
        
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Sortie
        grid_sizer_sortie = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)        

        box_fichier = wx.StaticBoxSizer(self.box_fichier_staticbox, wx.VERTICAL)
        box_fichier.Add(self.bouton_fichier, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_sortie.Add(box_fichier, 1, wx.EXPAND, 0)

        box_impression = wx.StaticBoxSizer(self.box_impression_staticbox, wx.VERTICAL)
        grid_sizer_impression = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_impression.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_impression.Add(self.ctrl_type, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_impression.Add((10, 10), 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_impression.Add(self.bouton_apercu, 0, wx.EXPAND, 0)
        grid_sizer_impression.AddGrowableCol(1)
        box_impression.Add(grid_sizer_impression, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_sortie.Add(box_impression, 1, wx.EXPAND, 0)
        
        grid_sizer_sortie.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_sortie, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("ExportversHelios")

    def OnBoutonFermer(self, event): 
        UTILS_Parametres.Parametres(mode="set", categorie="rolmre", nom="code_col", valeur=self.ctrl_code_coll.GetValue())
        UTILS_Parametres.Parametres(mode="set", categorie="rolmre", nom="code_nat", valeur=self.ctrl_code_nat.GetValue())
        UTILS_Parametres.Parametres(mode="set", categorie="rolmre", nom="code_rec", valeur=self.ctrl_code_rec.GetValue())
        self.EndModal(wx.ID_CANCEL)

    def ValidationSaisie(self):
        """ Validation des donn�es saisies """
        tracks = self.ctrl_factures.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune facture � inclure dans le r�le !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        for track in tracks :
            if -track.solde < 0.0 :
                dlg = wx.MessageDialog(self, _(u"La facture n�%s n'est pas valide car elle comporte un montant de %.2f %s, soit inf�rieure � 0.\n\nVeuillez la retirer de la s�lection.") % (track.numero, -track.solde, SYMBOLE), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        date_emission = self.ctrl_date.GetDate()
        if date_emission == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date d'�mission pour ce r�le !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False

        code_col = self.ctrl_code_coll.GetValue()
        if code_col == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir le code Collectivit� du r�le !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code_coll.SetFocus()
            return False
        
        code_nat = self.ctrl_code_nat.GetValue()
        if code_nat == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir le code Nature du r�le !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code_nat.SetFocus()
            return False

        code_rec = self.ctrl_code_rec.GetValue()
        if code_rec == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir le code Recette du r�le !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code_rec.SetFocus()
            return False
        
        exercice = self.ctrl_exercice.GetValue()
        if exercice == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir l'exercice du r�le !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_exercice.SetFocus()
            return False

        num_role = self.ctrl_num_role.GetValue()
        if num_role == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir le num�ro de r�le !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_num_role.SetFocus()
            return False

        return True

    def OnBoutonFichier(self, event): 
        if self.ValidationSaisie() == False :
            return
        
        # R�cup�ration des param�tres
        tracks = self.ctrl_factures.GetTracksCoches() 
        date_emission = self.ctrl_date.GetDate()
        code_col = self.ctrl_code_coll.GetValue()
        code_nat = self.ctrl_code_nat.GetValue()
        code_rec = self.ctrl_code_rec.GetValue()
        exercice = self.ctrl_exercice.GetValue()
        num_role = self.ctrl_num_role.GetValue()
        
        listeLignes = []
        for track in tracks :
            
            if track.prelevement == True :
                prelevement = True
                prelevement_etab = track.prelevement_etab
                prelevement_guichet = track.prelevement_guichet
                prelevement_compte = track.prelevement_numero
                prelevement_cle = track.prelevement_cle
                prelevement_titulaire = track.prelevement_payeur
            else :
                prelevement = False
                prelevement_etab = ""
                prelevement_guichet = ""
                prelevement_compte = ""
                prelevement_cle = ""
                prelevement_titulaire = ""
            
            if track.adresse_famille["rue"] != None : rue = track.adresse_famille["rue"]
            else : rue = u""
            if track.adresse_famille["cp"] != None : cp = track.adresse_famille["cp"]
            else : cp = u""
            if track.adresse_famille["ville"] != None : ville = track.adresse_famille["ville"]
            else : ville = u""
                
                
            dictDonnees = {
                "ROLCOL" : code_col, # Code Collectivit�
                "ROLNAT" : code_nat, # Nature du r�le
                "ROLEX" : exercice, # Exercice
                "ROLREC" : code_rec, # Code Recette
                "ROLROL" : num_role, # Num�ro de r�le
                "date_edition" : date_emission, # Date d'�dition
                
                "ROLDET" : track.numero, # Num�ro de dette
                "ROLEAU" : int(str(FloatToDecimal(-track.solde)).replace(".", "")), # Montant de la facture en centimes
                
                "nom" : track.nomsTitulaires, # Nom du d�biteur
                "rue" : rue, # Rue de r�sidence du d�biteur
                "code_postal" : cp, # Code postal de la ville de r�sidence du d�biteur
                "ville" : ville, # Nom de la ville de r�sidence du d�biteur
                "objet" : _(u"Facture n�%s") % track.numero, # Objet de la recette (64 caract max)
                
                "prelevement" : prelevement, # Activation du pr�l�vement
                "prelevement_etab" : prelevement_etab, # Code �tablissement
                "prelevement_guichet" : prelevement_guichet, # Code Guichet
                "prelevement_compte" : prelevement_compte, # Num�ro de compte
                "prelevement_cle" : prelevement_cle, # Cl� RIB
                "prelevement_titulaire" : prelevement_titulaire, # Nom titulaire du compte
                }
            
            ligne = UTILS_Helios.GetLigne(dictDonnees)
            listeLignes.append(ligne)
        
        # Finalisation du texte
        texte = "".join(listeLignes)
    
        # Demande � l'utilisateur le nom de fichier et le r�pertoire de destination
        nomFichier = "Rolmre.txt"
        wildcard = "Fichier texte (*.txt)|*.txt|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez s�lectionner le r�pertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe d�j� :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Cr�ation du fichier texte
        f = open(cheminFichier, "w")
        f.write(texte.encode("iso-8859-15"))
        f.close()
        
        # Confirmation de cr�ation du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier a �t� cr�� avec succ�s.\n\nSouhaitez-vous l'ouvrir d�s maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

    def OnBoutonApercu(self, event): 
        if self.ValidationSaisie() == False :
            return
        
        typeImpression = self.ctrl_type.GetType() 
        
        # R�cup�ration des param�tres
        tracks = self.ctrl_factures.GetTracksCoches() 
        date_emission = self.ctrl_date.GetDate()
        code_col = self.ctrl_code_coll.GetValue()
        code_nat = self.ctrl_code_nat.GetValue()
        code_rec = self.ctrl_code_rec.GetValue()
        exercice = self.ctrl_exercice.GetValue()
        num_role = self.ctrl_num_role.GetValue()
        
        listeIDfactures = []
        montantTotal = 0.0 
        for track in tracks :
            listeIDfactures.append(track.IDfacture)
            montantTotal += -track.solde

        if len(listeIDfactures) == 0 : conditionFactures = "()"
        elif len(listeIDfactures) == 1 : conditionFactures = "(%d)" % listeIDfactures[0]
        else : conditionFactures = str(tuple(listeIDfactures))

        DB = GestionDB.DB() 
        req = """
        SELECT prestations.IDprestation, prestations.IDfacture, prestations.label, prestations.montant, 
        prestations.IDindividu, individus.nom, individus.prenom,
        prestations.IDactivite, activites.nom
        FROM prestations
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        WHERE prestations.IDfacture IN %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % conditionFactures
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq() 
        DB.Close() 
        dictPrestations = {}
        dictIndividus = {}
        dictActivites = {}
        dictTotaux = {}
        for IDprestation, IDfacture, label, montant, IDindividu, nom, prenom, IDactivite, nomActivite in listePrestations :

            if dictActivites != None and dictActivites.has_key(IDactivite) == False :
                dictActivites[IDactivite] = nomActivite

            if IDindividu != None and dictIndividus.has_key(IDindividu) == False and prenom != None :
                dictIndividus[IDindividu] = u"%s %s" % (nom, prenom)
            
            if dictPrestations.has_key(IDfacture) == False :
                dictPrestations[IDfacture] = {}
            if dictPrestations[IDfacture].has_key(IDindividu) == False :
                dictPrestations[IDfacture][IDindividu] = {}
            if dictPrestations[IDfacture][IDindividu].has_key(label) == False :
                dictPrestations[IDfacture][IDindividu][label] = {"quantite" : 0, "montant" : 0.0, "IDactivite" : IDactivite}
            
            if dictTotaux.has_key(IDactivite) == False :
                dictTotaux[IDactivite] = {}
            if dictTotaux[IDactivite].has_key(label) == False :
                dictTotaux[IDactivite][label] = {"quantite" : 0, "montant" : 0.0}
            
            dictTotaux[IDactivite][label]["quantite"] += 1
            dictTotaux[IDactivite][label]["montant"] += montant

            dictPrestations[IDfacture][IDindividu][label]["quantite"] += 1
            dictPrestations[IDfacture][IDindividu][label]["montant"] += montant

        # Cr�ation du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Initialisation du PDF
        PAGE_WIDTH, PAGE_HEIGHT=defaultPageSize
        nomDoc = "Temp/ROLMRE%s.pdf" % FonctionsPerso.GenerationIDdoc() 
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = 520
        
        # Cr�ation du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (420, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"R�le n�%s-%s") % (exercice, num_role), _(u"%s\nEdit� le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                    ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                    ('ALIGN', (0,0), (0,0), 'LEFT'), 
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                    ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                    ('FONT',(1,0),(1,0), "Helvetica", 6), 
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0, 20))       
        
        # Ins�re un header
        Header() 
        
        couleurFond1 = (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)
        couleurFond2 = (0.9, 0.9, 1) # Vert -> (0.5, 1, 0.2)
        styleLabel = ParagraphStyle(name="label", fontName="Helvetica", alignment=1, fontSize=5, spaceAfter=0, leading=8, spaceBefore=0)
        styleTexte = ParagraphStyle(name="label", fontName="Helvetica", alignment=0, fontSize=7, spaceAfter=0, leading=8, spaceBefore=0)
        styleTexte2 = ParagraphStyle(name="label", fontName="Helvetica", alignment=1, fontSize=7, spaceAfter=0, leading=8, spaceBefore=0)
        styleMontant = ParagraphStyle(name="label", fontName="Helvetica", alignment=2, fontSize=7, spaceAfter=0, leading=8, spaceBefore=0)

        # Intro
        story.append(Paragraph(_(u"Date d'�mission : %s | Code Collectivit� : %s | Code Nature : %s | Code Recette : %s") % (UTILS_Dates.DateDDEnFr(date_emission), code_col, code_nat, code_rec), styleTexte))
        story.append(Spacer(0, 20))
        
        # Factures
        if typeImpression in ("detail", "simple") :
            
            for track in tracks :
                
                # Num�ro de facture
                dataTableau = []
                largeursColonnes = [100, 100, largeurContenu-100-100]
                dataTableau.append((
                    _(u"Facture n�%s") % track.numero, 
                    u"%.2f %s" % (-track.solde, SYMBOLE),
                    _(u"Edit� le %s | Ech�ance le %s | P�riode du %s au %s") % (UTILS_Dates.DateDDEnFr(track.date_edition), UTILS_Dates.DateDDEnFr(track.date_echeance), UTILS_Dates.DateDDEnFr(track.date_debut), UTILS_Dates.DateDDEnFr(track.date_fin)),
                    ))
                tableau = Table(dataTableau, largeursColonnes)
                listeStyles = [
                    ('FONT', (0, 0), (1, -1), "Helvetica-Bold", 7),
                    ('FONT', (2, -1), (2, -1), "Helvetica", 6),
                    ('BACKGROUND', (0, 0), (-1, -1), couleurFond1),
                    ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ]
                tableau.setStyle(TableStyle(listeStyles))
                story.append(tableau)
                
                # Famille
                if track.prelevement == True :
                    textePrelevement = _(u"N� Compte : %s | Etab : %s | Guichet : %s | Cl� : %s | Titulaire : %s") % (track.prelevement_numero, track.prelevement_etab, track.prelevement_guichet, track.prelevement_cle, track.prelevement_payeur)
                else :
                    textePrelevement = u""
                
                if track.adresse_famille["rue"] != None : rue = track.adresse_famille["rue"]
                else : rue = u""
                if track.adresse_famille["cp"] != None : cp = track.adresse_famille["cp"]
                else : cp = u""
                if track.adresse_famille["ville"] != None : ville = track.adresse_famille["ville"]
                else : ville = u""
                
                dataTableau = [(Paragraph(_(u"Famille"), styleLabel), Paragraph(_(u"Adresse"), styleLabel), Paragraph(_(u"Pr�l�vement bancaire"), styleLabel)),]
                largeursColonnes = [180, 140, largeurContenu-320]
                dataTableau.append((
                    Paragraph(track.nomsTitulaires, styleTexte), 
                    (Paragraph(rue, styleTexte), Paragraph(u"%s %s" % (cp, ville), styleTexte)),
                    Paragraph(textePrelevement, styleTexte),
                    ))
                tableau = Table(dataTableau, largeursColonnes)
                listeStyles = [
                    ('TOPPADDING', (0, 0), (-1, 0), 0), 
                    ('BOTTOMPADDING',(0, 0), (-1, 0), -1), 
                    ('FONT', (0, -1), (-1, -1), "Helvetica", 7),
                    ('GRID', (0, 0), (-1, 0), 0.25, colors.black),
                    ('BOX', (0, 1), (-1, 1), 0.25, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), couleurFond2),
                    ]
                tableau.setStyle(TableStyle(listeStyles))
                story.append(tableau)
                
                # D�tail des prestations
                if typeImpression == "detail" and dictPrestations.has_key(track.IDfacture) :
                    
                    dataTableau = [(Paragraph(_(u"Individu"), styleLabel), Paragraph(_(u"Activit�"), styleLabel), Paragraph(_(u"Prestation"), styleLabel), Paragraph(_(u"Quantit�"), styleLabel), Paragraph(_(u"Montant total"), styleLabel)),]
                    largeursColonnes = [130, 120, 185, 35, 50]
                    
                    for IDindividu, dictLabels in dictPrestations[track.IDfacture].iteritems() :
                        
                        if dictIndividus.has_key(IDindividu) :
                            labelIndividu = dictIndividus[IDindividu]
                        else :
                            labelIndividu = u""

                        listeActivites = []
                        listeLabels = []
                        listeQuantites = []
                        listeMontants = []
                        for labelPrestation, dictTemp in dictLabels.iteritems() :

                            if dictTemp["IDactivite"] != None and dictActivites.has_key(dictTemp["IDactivite"]) :
                                labelActivite = dictActivites[dictTemp["IDactivite"]]
                            else :
                                labelActivite = u""
                            
                            listeActivites.append(Paragraph(labelActivite[:35], styleTexte2)) 
                            listeLabels.append(Paragraph(labelPrestation[:40], styleTexte2)) 
                            listeQuantites.append(Paragraph(str(dictTemp["quantite"]), styleTexte2)) 
                            listeMontants.append(Paragraph(u"%.2f %s" % (dictTemp["montant"], SYMBOLE), styleMontant))
                        
                        dataTableau.append((
                            Paragraph(labelIndividu, styleTexte2), 
                            listeActivites,
                            listeLabels,
                            listeQuantites,
                            listeMontants,
                            ))
                            
                    tableau = Table(dataTableau, largeursColonnes)
                    listeStyles = [
                        ('TOPPADDING', (0, 0), (-1, 0), 0), 
                        ('BOTTOMPADDING',(0, 0), (-1, 0), -1), 
                        ('FONT', (0, -1), (-1, -1), "Helvetica", 7),
                        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('BACKGROUND', (0, 0), (-1, 0), couleurFond2),
                        ]
                    tableau.setStyle(TableStyle(listeStyles))
                    story.append(tableau)
                    
                story.append(Spacer(0, 10))
        
        # Totaux        
        dictTotaux[IDactivite][label]["montant"]

        dataTableau = [
            (_(u"Totaux par activit�s et prestations"), "", "", ""),
            (Paragraph(_(u"Activit�s"), styleLabel), Paragraph(_(u"Prestations"), styleLabel), Paragraph(_(u"Quantit�"), styleLabel), Paragraph(_(u"Montant"), styleLabel)),
            ]
        largeursColonnes = [200, 240, 30, 50]

        for IDactivite, dictLabels in dictTotaux.iteritems() :
            
            if IDactivite == None :
                nomActivite = _(u"Prestations familiales")
            else :
                nomActivite = dictActivites[IDactivite]
                
            listeLabels = []
            listeQuantites = []
            listeMontants = []
            quantiteActivite = 0
            totalActivite = 0.0
            for label, dictTemp in dictLabels.iteritems() :
                listeLabels.append(Paragraph(label, styleTexte2)) 
                listeQuantites.append(Paragraph(str(dictTemp["quantite"]), styleTexte2)) 
                listeMontants.append(Paragraph(u"%.2f %s" % (dictTemp["montant"], SYMBOLE), styleMontant))
                quantiteActivite += dictTemp["quantite"]
                totalActivite += dictTemp["montant"]
            
            listeLabels.append(Paragraph(_(u"<b><i>Total de l'activit�</i></b>"), styleTexte2)) 
            listeQuantites.append(Paragraph("<b><i>%d</i></b>" % quantiteActivite, styleTexte2)) 
            listeMontants.append(Paragraph(u"<b><i>%.2f %s</i></b>" % (totalActivite, SYMBOLE), styleMontant))
            
            dataTableau.append((
                Paragraph(nomActivite, styleTexte2), 
                listeLabels,
                listeQuantites,
                listeMontants,
                ))

        tableau = Table(dataTableau, largeursColonnes)
        listeStyles = [
            ('TOPPADDING', (0, 1), (-1, 1), 0), 
            ('BOTTOMPADDING',(0, 1), (-1, 1), -1), 
            ('FONT', (1, -1), (-1, -1), "Helvetica", 7),
            ('FONT', (0, 0), (0, 0), "Helvetica-Bold", 7),
            ('BOX', (0, 0), (-1, 0), 0.25, colors.black),
            ('GRID', (0, 1), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), couleurFond1),
            ('BACKGROUND', (0, 1), (-1, 1), couleurFond2),
            ]
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)

        story.append(Spacer(0, 10))

        story.append(Paragraph(_(u"%d factures | Montant total : %.2f %s") % (len(tracks), montantTotal, SYMBOLE), styleTexte))

        # Enregistrement et ouverture du PDF
        try :
            doc.build(story)
        except Exception, err :
            print "Erreur dans ouverture PDF :", err
            if "Permission denied" in err :
                dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas cr�er le PDF.\n\nVeuillez v�rifier qu'un autre PDF n'est pas d�j� ouvert en arri�re-plan..."), _(u"Erreur d'�dition"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        FonctionsPerso.LanceFichierExterne(nomDoc)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    filtres = [
        #{"type" : "numero_intervalle", "numero_min" : 100, "numero_max" : 200},
        ]

    dlg = Dialog(None, filtres=filtres)
    dlg.ctrl_factures.ctrl_factures.CocheTout()
##    dlg.OnBoutonApercu(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
