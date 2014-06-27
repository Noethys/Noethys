#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import wx.lib.masked as masked

import GestionDB
import DATA_Civilites as Civilites

import CTRL_Saisie_civilite
import CTRL_Saisie_adresse
import CTRL_Saisie_numSecu
import CTRL_Saisie_pays
import CTRL_Saisie_date

import UTILS_Utilisateurs

DICT_CIVILITES = Civilites.GetDictCivilites() 



class Sieste(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, choices=[]) 
        self.parent = parent
        self.SetToolTipString(u"Sélectionnez le type de sieste nécessaire pour cet individu")
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDtype_sieste, nom FROM types_sieste ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.dictDonnees = { 0 : (None, u"Ne fait pas la sieste") }
        listeNoms = [ u"Ne fait pas la sieste"]
        index = 1
        for IDtype_sieste, nom in listeDonnees :
            listeNoms.append(nom)
            self.dictDonnees[index] = (IDtype_sieste, nom)
            index += 1
        return listeNoms

    def SetID(self, ID=0):
        if ID == None : return
        for index, values in self.dictDonnees.iteritems():
            if values[0] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        if index == 0 : return None
        return self.dictDonnees[index][0]

# -------------------------------------------------------------------------------------------------------------------------



class Panel_identite(wx.Panel):
    def __init__(self, parent, IDindividu=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_identite", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        
        self.majEffectuee = False
        
        # Identité
        self.staticbox_etatcivil_staticbox = wx.StaticBox(self, -1, u"Etat-civil")
        self.label_civilite = wx.StaticText(self, -1, u"Civilité/genre :")
        self.ctrl_civilite = CTRL_Saisie_civilite.Civilite(self)
        self.label_nomjfille = wx.StaticText(self, -1, u"Nom de jeune fille :")
        self.ctrl_nomjfille = wx.TextCtrl(self, -1, u"")
        self.label_nom = wx.StaticText(self, -1, u"Nom :")
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.label_prenom = wx.StaticText(self, -1, u"Prénom :")
        self.ctrl_prenom = wx.TextCtrl(self, -1, "")
        self.label_numsecu = wx.StaticText(self, -1, u"Num. sécu. :")
        self.ctrl_numsecu = CTRL_Saisie_numSecu.NumSecu(self)
        self.label_nationalite = wx.StaticText(self, -1, u"Nationalité :")
        self.ctrl_nationalite = CTRL_Saisie_pays.SaisiePays(self, mode="nationalite")
        
        # Naissance
        self.staticbox_naiss_staticbox = wx.StaticBox(self, -1, u"Naissance")
        self.label_datenaiss = wx.StaticText(self, -1, u"Date :")
        self.ctrl_datenaiss = CTRL_Saisie_date.Date(self)
        self.ctrl_age = wx.TextCtrl(self, -1, "", style=wx.TE_CENTRE, size=(46,-1))
        self.label_paysnaiss = wx.StaticText(self, -1, u"Pays de naissance :")
        self.ctrl_paysnaiss = CTRL_Saisie_pays.SaisiePays(self, mode="pays")
        self.label_lieunaiss = wx.StaticText(self, -1, u"Lieu | C.P. :")
        self.ctrl_adressenaiss = CTRL_Saisie_adresse.Adresse(self)
        
        # Décès
        self.staticbox_deces = wx.StaticBox(self, -1, u"Décès")
        self.ctrl_deces = wx.CheckBox(self, -1, u"")
        self.label_deces = wx.StaticText(self, -1, u"Année :")
        self.ctrl_annee_deces = wx.TextCtrl(self, -1, u"")
        
        # Sieste
        self.staticbox_sieste = wx.StaticBox(self, -1, u"Sieste")
        self.ctrl_sieste = Sieste(self)
        self.bouton_sieste = wx.Button(self, -1, "...", size=(20, 20))
        
        # Mémo
        self.staticbox_memo = wx.StaticBox(self, -1, u"Mémo")
        self.ctrl_memo = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoiceCivilite, self.ctrl_civilite)
        
        self.ctrl_nom.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNom)
        self.ctrl_prenom.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusPrenom)
        self.ctrl_datenaiss.Bind(wx.EVT_TEXT, self.OnKillFocusDatenaiss)
        
        self.ctrl_nom.Bind(wx.EVT_TEXT, self.OnTextNomOuPrenom)
        self.ctrl_prenom.Bind(wx.EVT_TEXT, self.OnTextNomOuPrenom)
        
        self.ctrl_deces.Bind(wx.EVT_CHECKBOX, self.OnCheckDeces)
        
        self.Bind(wx.EVT_BUTTON, self.OnGestionSieste, self.bouton_sieste)
        
        self.OnCheckDeces(None)
        self.ctrl_nationalite.SetValue(IDpays=73)
        self.ctrl_paysnaiss.SetValue(IDpays=73)
        
    def __set_properties(self):
        self.ctrl_nomjfille.SetToolTipString(u"Saisissez ici le nom de jeune fille de l'individu")
        self.ctrl_nomjfille.Enable(False)
        self.label_nomjfille.Enable(False)
        self.ctrl_nom.SetToolTipString(u"Saisissez ici le nom de l'individu")
        self.ctrl_prenom.SetToolTipString(u"Saisissez ici le prénom de l'individu")
        self.ctrl_datenaiss.SetToolTipString(u"Saisissez ici la date de naissance de l'individu")
        self.ctrl_datenaiss.SetMinSize((95, -1))
        self.ctrl_age.SetMinSize((60, -1))
        self.ctrl_age.SetToolTipString(u"Age de l'individu")
        self.ctrl_age.Enable(False)
        self.ctrl_deces.SetToolTipString(u"Cochez cette case si l'individu est décédé")
        self.ctrl_annee_deces.SetToolTipString(u"Saisissez ici l'année de décès de l'individu")
        self.ctrl_annee_deces.SetMinSize((40, -1))
        self.ctrl_sieste.SetToolTipString(u"Sélectionnez ici un type de sieste pour cet individu")
        self.bouton_sieste.SetToolTipString(u"Cliquez ici pour accéder à la fenêtre de gestion des types de sieste")
        self.ctrl_memo.SetToolTipString(u"Saisissez ici les informations de votre choix concernant cet individu")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        # StaticBox Etat-civil
        staticbox_etatcivil = wx.StaticBoxSizer(self.staticbox_etatcivil_staticbox, wx.VERTICAL)
        grid_sizer_etatcivil = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_civilite = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_etatcivil.Add(self.label_civilite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_civilite.Add(self.ctrl_civilite, 0, 0, 0)
        grid_sizer_civilite.Add((10, 10), 0, 0, 0)
        grid_sizer_civilite.Add(self.label_nomjfille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_civilite.Add(self.ctrl_nomjfille, 0, wx.EXPAND, 0)
        grid_sizer_civilite.AddGrowableCol(3)
        grid_sizer_etatcivil.Add(grid_sizer_civilite, 1, wx.EXPAND, 0)
        grid_sizer_etatcivil.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etatcivil.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_etatcivil.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etatcivil.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        grid_sizer_etatcivil.Add(self.label_numsecu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numsecu = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_numsecu.Add(self.ctrl_numsecu, 0, 0, 0)
        grid_sizer_numsecu.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_numsecu.Add(self.label_nationalite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numsecu.Add(self.ctrl_nationalite, 0, 0, 0)
        grid_sizer_etatcivil.Add(grid_sizer_numsecu, 1, wx.EXPAND, 0)
        grid_sizer_etatcivil.AddGrowableCol(1)
        staticbox_etatcivil.Add(grid_sizer_etatcivil, 1, wx.ALL|wx.EXPAND, 5)
        
        grid_sizer_gauche.Add(staticbox_etatcivil, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        # StaticBox Naissance
        staticbox_naiss = wx.StaticBoxSizer(self.staticbox_naiss_staticbox, wx.VERTICAL)
        grid_sizer_naiss = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_naiss.Add(self.label_datenaiss, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_datenaiss = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_datenaiss.Add(self.ctrl_datenaiss, 0, 0, 0)
        grid_sizer_datenaiss.Add(self.ctrl_age, 0, 0, 0)
        grid_sizer_datenaiss.Add((10, 10), 0, 0, 0)
        grid_sizer_datenaiss.Add(self.label_paysnaiss, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_datenaiss.Add(self.ctrl_paysnaiss, 0, 0, 0)
        grid_sizer_datenaiss.AddGrowableCol(2)
        grid_sizer_naiss.Add(grid_sizer_datenaiss, 1, wx.EXPAND, 0)
        grid_sizer_naiss.Add(self.label_lieunaiss, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_naiss.Add(self.ctrl_adressenaiss, 1, wx.EXPAND, 0)
        grid_sizer_naiss.AddGrowableCol(1)
        staticbox_naiss.Add(grid_sizer_naiss, 1, wx.ALL|wx.EXPAND, 5)
        
        grid_sizer_gauche.Add(staticbox_naiss, 1, wx.EXPAND | wx.LEFT | wx.RIGHT , 5)
        
        # Grid sizer Décès + Sieste
        grid_sizer_deces_sieste = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # StaticBox Décès
        staticbox_deces = wx.StaticBoxSizer(self.staticbox_deces, wx.VERTICAL)
        grid_sizer_deces = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_deces.Add(self.ctrl_deces, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_deces.Add(self.label_deces, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_deces.Add(self.ctrl_annee_deces, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_deces.Add(grid_sizer_deces, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_deces_sieste.Add(staticbox_deces, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # StaticBox Sieste
        staticbox_sieste = wx.StaticBoxSizer(self.staticbox_sieste, wx.VERTICAL)
        grid_sizer_sieste = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_sieste.Add(self.ctrl_sieste, 1, wx.EXPAND, 0)
        grid_sizer_sieste.Add(self.bouton_sieste, 1, wx.EXPAND, 0)
        staticbox_sieste.Add(grid_sizer_sieste, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_sieste.AddGrowableCol(0)
        grid_sizer_deces_sieste.Add(staticbox_sieste, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        grid_sizer_gauche.Add(grid_sizer_deces_sieste, 1, wx.EXPAND, 0)
        grid_sizer_deces_sieste.AddGrowableCol(1)
        
        # Finalisation du sizer gauche
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # StaticBox Mémo
        staticbox_memo = wx.StaticBoxSizer(self.staticbox_memo, wx.VERTICAL)
        staticbox_memo.Add(self.ctrl_memo, 1, wx.ALL|wx.EXPAND, 5)
        
        grid_sizer_droit.Add(staticbox_memo, 1, wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM, 5)
        
        # Finalisation du sizer droit
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_droit.AddGrowableRow(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(1)
        grid_sizer_base.Fit(self)

    
    def OnTextNomOuPrenom(self, event):
        nom = self.ctrl_nom.GetValue()
        prenom = self.ctrl_prenom.GetValue()
        rubriqueCivilite = self.ctrl_civilite.GetRubrique()
        if rubriqueCivilite == "AUTRE" :
            # Si c'est un organisme
            self.Set_Header(nomLigne="nom", texte=nom)
        else:
            # Si c'est un individu
            if len(nom) != 0 : 
                nom = nom.upper()
            else:
                nom = u"NOM"
            if len(prenom) > 0 : 
                prenom = prenom[:1].upper() + prenom[1:]
            else:
                prenom = u"Prénom"
            self.Set_Header(nomLigne="nom", texte=u"%s, %s" % (nom, prenom))
        if event != None :
            event.Skip() 
    
    def OnKillFocusNom(self, event):
        nom = self.ctrl_nom.GetValue()
        if len(nom) != 0 : nom = nom.upper()
        self.ctrl_nom.SetValue(nom)
        if event != None :
            event.Skip() 

    def OnKillFocusPrenom(self, event):
        prenom = self.ctrl_prenom.GetValue()
        if len(prenom) != 0 : prenom = prenom[:1].upper() + prenom[1:]
        self.ctrl_prenom.SetValue(prenom)
        if event != None :
            event.Skip() 
    
    def OnKillFocusDatenaiss(self, event):
##        valide = self.ctrl_datenaiss.FonctionValiderDate()
##        if valide == False :
##            self.ctrl_datenaiss.SetFocus()
##            return
        dateFR = self.ctrl_datenaiss.GetDate(FR=True)
        texte = u""
        if dateFR == None : 
            texte = u"Date et lieu de naissance inconnus"
            self.ctrl_age.SetValue(u"")
        else:
            age = self.ctrl_datenaiss.GetAge()
            sexe = self.ctrl_civilite.GetSexe()
            if sexe == "M" : texte = u"Né le %s (%d ans)" % (dateFR, age)
            if sexe == "F" : texte = u"Née le %s (%d ans)" % (dateFR, age)
            if age != None : self.ctrl_age.SetValue(u"%d ans" % age)
        self.Set_Header(nomLigne="datenaiss", texte=texte)
        if event != None : event.Skip() 
        
    def OnChoiceCivilite(self, event):
        # Signale que c'est une rubrique qui a été sélectionnée
        if self.ctrl_civilite.GetType() == "rubrique" :
            self.ctrl_civilite.SetFocus()
            return
        # Applique la photo à la fiche
        self.SetPhoto(nomFichier=u"Images/128x128/%s" % self.ctrl_civilite.GetPhoto())
        # Active ou non le controle NOM DE JEUNE FILLE
        if self.ctrl_civilite.GetCivilite() == "Madame" :
            self.label_nomjfille.Enable(True)
            self.ctrl_nomjfille.Enable(True)
            self.ctrl_nomjfille.SetFocus()
        else:
            self.label_nomjfille.Enable(False)
            self.ctrl_nomjfille.Enable(False)
            self.ctrl_nom.SetFocus()
        # MAJ Header Nom
        self.OnTextNomOuPrenom(None)
        # Désactive certains contrôles si c'est un organisme
        if self.ctrl_civilite.GetRubrique() == "AUTRE" :
            self.Set_Header(nomLigne="datenaiss", texte=self.ctrl_civilite.GetCivilite())
            etat = False
        else :
            self.OnKillFocusDatenaiss(None)
            etat = True
        self.ctrl_prenom.Enable(etat)
        self.ctrl_numsecu.Enable(etat)
        self.ctrl_nationalite.Enable(etat)
        self.ctrl_datenaiss.Enable(etat)
        self.ctrl_paysnaiss.Enable(etat)
        self.ctrl_adressenaiss.Enable(etat)
##        self.ctrl_deces.SetValue(False)
##        self.OnCheckDeces(None)
##        self.ctrl_deces.Enable(etat)
        self.ctrl_sieste.Enable(etat)
        self.bouton_sieste.Enable(etat)
    
    def OnCheckDeces(self, event):
        if self.ctrl_deces.GetValue() == True :
            self.label_deces.Enable(True)
            self.ctrl_annee_deces.Enable(True)
        else:
            self.label_deces.Enable(False)
            self.ctrl_annee_deces.Enable(False)
    
    def OnGestionSieste(self, event):
        IDtype_sieste = self.ctrl_sieste.GetID()
        import DLG_Types_sieste
        dlg = DLG_Types_sieste.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_sieste.MAJ() 
        self.ctrl_sieste.SetID(IDtype_sieste)

        
    def Set_Header(self, nomLigne, texte):
        try :
            self.ficheIndividu = self.Parent.GetParent()
            if self.ficheIndividu.GetName() != "fiche_individu" :
                self.ficheIndividu = None
        except : 
            self.ficheIndividu = None
        if self.ficheIndividu != None :
            self.ficheIndividu.Set_Header(nomLigne, texte)
    
    def SetPhoto(self, IDphoto=None, nomFichier=None):
        try :
            self.ficheIndividu = self.Parent.GetParent()
            if self.ficheIndividu.GetName() != "fiche_individu" :
                self.ficheIndividu = None
        except : 
            self.ficheIndividu = None
        if self.ficheIndividu != None :
            self.ficheIndividu.ctrl_photo.SetPhoto(self.IDindividu, nomFichier, taillePhoto=(128, 128), qualite=100)
            
    def MAJ(self):
        if self.majEffectuee == True :
            return
        self.IDindividu = self.GetGrandParent().IDindividu
        if self.IDindividu == None :
            print "pas de IDindividu !"
            return
        if self.GetGrandParent().nouvelleFiche == True :
            return
        db = GestionDB.DB()
        req = """SELECT IDcivilite, nom, nom_jfille, prenom, num_secu, IDnationalite, date_naiss, 
        IDpays_naiss, cp_naiss, ville_naiss, deces, annee_deces, memo, IDtype_sieste FROM individus WHERE IDindividu=%d;""" % self.IDindividu
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        individu = listeDonnees[0]
        self.ctrl_civilite.SetID(individu[0])
        self.ctrl_nom.SetValue(individu[1])
        try : self.ctrl_nomjfille.SetValue(individu[2])
        except : pass
        self.ctrl_prenom.SetValue(individu[3])
        self.ctrl_numsecu.SetValue(individu[4])
        self.ctrl_nationalite.SetValue(IDpays=individu[5])
        
        self.ctrl_datenaiss.SetDate(individu[6])
        self.ctrl_paysnaiss.SetValue(IDpays=individu[7])
        self.ctrl_adressenaiss.SetValueCP(individu[8])
        self.ctrl_adressenaiss.SetValueVille(individu[9])
        
        deces = individu[10]
        annee_deces = individu[11]
        if deces != None : 
            self.ctrl_deces.SetValue(deces)
        if annee_deces != None : 
            self.ctrl_annee_deces.SetValue(str(annee_deces))
        
        memo = individu[12]
        if memo != None : self.ctrl_memo.SetValue(memo)
        
        self.ctrl_sieste.SetID(individu[13])
        
        self.majEffectuee = True
        
        # MAJ controles
        self.OnChoiceCivilite(None)
        self.OnCheckDeces(None)
        
        # Verrouillage utilisateurs
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_identite", "modifier", afficheMessage=False) == False : 
            for ctrl in self.GetChildren() :
                ctrl.Enable(False)
            
        
    
    def ValidationData(self):
        """ Validation des données avant Sauvegarde """
        # Vérification de la civilité
        if self.ctrl_civilite.GetID() == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner une civilité !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Vérification du nom
        if self.ctrl_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Vérification de la civilité
        if self.ctrl_civilite.GetRubrique() != "AUTRE" and self.ctrl_prenom.GetValue() == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un prénom !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Vérification de l'année de décès
        if self.ctrl_deces.GetValue() == True :
            if self.ctrl_annee_deces.GetValue() != "" :
                try :
                    annee_deces = int(self.ctrl_annee_deces.GetValue())
                except :
                    dlg = wx.MessageDialog(self, u"L'année de décès que vous avez saisi n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                if annee_deces < 1500 or annee_deces > 3000 :
                    dlg = wx.MessageDialog(self, u"L'année de décès que vous avez saisi n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
            
        return True
        
        
    def GetData(self):
        dictDonnees = {
            "IDcivilite" : self.ctrl_civilite.GetID(),
            "nom_jfille" : self.ctrl_nomjfille.GetValue(),
            "nom" : self.ctrl_nom.GetValue(),
            "prenom" : self.ctrl_prenom.GetValue(),
            "numsecu" : self.ctrl_numsecu.GetValue(),
            "nationalite" : self.ctrl_nationalite.GetValue(),
            "datenaiss" : self.ctrl_datenaiss.GetDate(),
            "paysnaiss" : self.ctrl_paysnaiss.GetValue(),
            "cpnaiss" : self.ctrl_adressenaiss.GetValueCP(),
            "villenaiss" : self.ctrl_adressenaiss.GetValueVille(),
            "deces" : int(self.ctrl_deces.GetValue()),
            "memo" : self.ctrl_memo.GetValue(),
            "IDtype_sieste" : self.ctrl_sieste.GetID(),
            }
        # Si c'est un organisme, on efface le prénom saisi :
        IDcivilite = dictDonnees["IDcivilite"]
        if DICT_CIVILITES[IDcivilite]["sexe"] == None :
            dictDonnees["prenom"] = u""
        
        # Année de décès
        if self.ctrl_annee_deces.GetValue() != "" :
            if self.ctrl_deces.GetValue() == True :
                dictDonnees["annee_deces"] = int(self.ctrl_annee_deces.GetValue())
            else:
                dictDonnees["annee_deces"] = None
        else:
            dictDonnees["annee_deces"] = None
        
        return dictDonnees

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base """
        dictDonnees = self.GetData()
        DB = GestionDB.DB()
        listeDonnees = [    
                            ("IDcivilite", dictDonnees["IDcivilite"]),
                            ("nom_jfille", dictDonnees["nom_jfille"]),
                            ("nom", dictDonnees["nom"]),
                            ("prenom", dictDonnees["prenom"]),
                            ("num_secu", dictDonnees["numsecu"]),
                            ("IDnationalite", dictDonnees["nationalite"]),
                            ("date_naiss", dictDonnees["datenaiss"]),
                            ("IDpays_naiss", dictDonnees["paysnaiss"]),
                            ("cp_naiss", dictDonnees["cpnaiss"]),
                            ("ville_naiss",  dictDonnees["villenaiss"]),
                            ("deces",  dictDonnees["deces"]),
                            ("annee_deces",  dictDonnees["annee_deces"]),
                            ("memo",  dictDonnees["memo"]),
                            ("IDtype_sieste", dictDonnees["IDtype_sieste"]),
                        ]
        DB.ReqMAJ("individus", listeDonnees, "IDindividu", self.IDindividu)
        DB.Close()

    def SetValeursDefaut(self, nom="", prenom="", IDcategorie=1):
        """ Importe des valeurs par défaut lors de la création d'une fiche """
        self.parent.AffichePage("identite")
        # Nom et prénom
        self.ctrl_nom.SetValue(nom.upper())
        self.ctrl_prenom.SetValue(prenom)
        # Civilité
        genre = self.RechercheGenre(prenom)
        if genre == None :
            self.ctrl_civilite.SetFocus()
        else:
            if IDcategorie == 1 and genre == "M" : IDcivilite = 1
            if IDcategorie == 1 and genre == "F" : IDcivilite = 3
            if IDcategorie == 2 and genre == "M" : IDcivilite = 4
            if IDcategorie == 2 and genre == "F" : IDcivilite = 5
            if IDcategorie == 3 and genre == "M" : IDcivilite = 1
            if IDcategorie == 3 and genre == "F" : IDcivilite = 3
            self.ctrl_civilite.SetID(IDcivilite)
        self.OnChoiceCivilite(None)

    def RechercheGenre(self, prenom=""):
        import FonctionsPerso
        #prenom = FonctionsPerso.supprime_accent(prenom)
        """ Recherche le genre de l'individu suivant son prénom """
        db = GestionDB.DB(nomFichier="Prenoms.dat", suffixe=None)
        req = """SELECT prenom, genre
        FROM prenoms WHERE prenom='%s';""" % prenom.lower()
        db.ExecuterReq(req)
        listePrenoms = db.ResultatReq()
        db.Close()
        if len(listePrenoms) == 1 :
            genre = listePrenoms[0][1]
            if genre == "m" : return "M"
            elif genre == "f" : return "F"
            else: return None
        else:
            return None
            



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel_identite(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        sizer_2.Fit(self)
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()