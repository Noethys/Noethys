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
import os
import datetime
import time
from Ctrl import CTRL_Bandeau
import GestionDB
from Ol import OL_Synchronisation_donnees

from threading import Thread 
import DLG_Badgeage_grille
import DLG_Messagebox
from Utils import UTILS_Fichiers


class Dialog(wx.Dialog):
    def __init__(self, parent, listeFichiers=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.listeFichiers = listeFichiers

        # Bandeau
        intro = _(u"Cliquez simplement sur le bouton Importer pour importer dans Noethys les données cochées.")
        titre = _(u"Importation des données")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Nomadhys.png")

        # Données
        self.box_donnees_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Données à importer"))
        self.ctrl_donnees = OL_Synchronisation_donnees.ListView(self, id=-1, listeFichiers=self.listeFichiers, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_donnees.SetMinSize((100, 100))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_recherche = OL_Synchronisation_donnees.CTRL_Outils(self, listview=self.ctrl_donnees, afficherCocher=True)
        self.check_cacher_doublons = wx.CheckBox(self, -1, _(u"Cacher les doublons"))
        self.check_cacher_doublons.SetValue(True)
        self.label_regroupement = wx.StaticText(self, -1, _(u"Regrouper par"))
        self.ctrl_regroupement = wx.Choice(self, -1, choices=[_(u"Catégorie"), _(u"Action"), _(u"Individu")])
        self.ctrl_regroupement.Select(0) 
        
        # Journal
        self.box_journal_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Journal d'évènements"))
        self.ctrl_journal = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.bouton_enregistrer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Sauvegarder.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Importer"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCacherDoublons, self.check_cacher_doublons)
        self.Bind(wx.EVT_CHOICE, self.OnChoixRegroupement, self.ctrl_regroupement)
        self.Bind(wx.EVT_BUTTON, self.ctrl_donnees.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_donnees.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_donnees.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_donnees.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnregistrer, self.bouton_enregistrer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)
        
        # Init
        self.ctrl_donnees.MAJ()
        
    def __set_properties(self):
        self.check_cacher_doublons.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour cacher les doublons")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_enregistrer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour enregistrer le contenu du journal dans un fichier")))
        self.ctrl_regroupement.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner une colonne de regroupement")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer l'importation des données")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        # Données
        box_donnees = wx.StaticBoxSizer(self.box_donnees_staticbox, wx.VERTICAL)
        grid_sizer_donnees = wx.FlexGridSizer(2, 2, 5, 5)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_donnees.Add(self.ctrl_donnees, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_donnees = wx.FlexGridSizer(6, 1, 5, 5)
        grid_sizer_boutons_donnees.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons_donnees.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons_donnees.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_donnees.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_boutons_donnees.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_donnees.Add(grid_sizer_boutons_donnees, 1, wx.EXPAND, 0)
        
        grid_sizer_recherche = wx.FlexGridSizer(2, 6, 5, 5)
        grid_sizer_recherche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add( (10, 5), 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add(self.label_regroupement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_recherche.Add(self.ctrl_regroupement, 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add( (10, 5), 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add(self.check_cacher_doublons, 0, wx.EXPAND, 0)
        grid_sizer_recherche.AddGrowableCol(0)
        grid_sizer_donnees.Add(grid_sizer_recherche, 0, wx.EXPAND, 0)
        
        grid_sizer_donnees.AddGrowableRow(0)
        grid_sizer_donnees.AddGrowableCol(0)
        box_donnees.Add(grid_sizer_donnees, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_donnees, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Journal
        box_journal = wx.StaticBoxSizer(self.box_journal_staticbox, wx.VERTICAL)
        grid_sizer_journal = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_journal.Add(self.ctrl_journal, 0, wx.EXPAND, 0)
        
        grid_sizer_boutons_journal = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_boutons_journal.Add(self.bouton_enregistrer, 0, 0, 0)
        grid_sizer_journal.Add(grid_sizer_boutons_journal, 1, wx.EXPAND, 0)
        grid_sizer_journal.AddGrowableRow(0)
        grid_sizer_journal.AddGrowableCol(0)
        box_journal.Add(grid_sizer_journal, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_journal, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def OnCheckCacherDoublons(self, event=None):
        self.ctrl_donnees.cacher_doublons = self.check_cacher_doublons.GetValue() 
        self.ctrl_donnees.MAJ() 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("SynchroniserNomadhys")

    def OnBoutonFermer(self, event):
        if self.ArchiverFichiers() == False :
            return
        try :
            self.EndModal(wx.ID_CANCEL)
        except :
            pass
        
    def OnChoixRegroupement(self, event):
        index = self.ctrl_regroupement.GetSelection()
        if index == 0 :
            self.ctrl_donnees.index_regroupement = 4
        elif index == 1 :
            self.ctrl_donnees.index_regroupement = 5
        elif index == 2 :
            self.ctrl_donnees.index_regroupement = 6
        self.ctrl_donnees.MAJ()         

    def EcritLog(self, message=""):
        horodatage = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        if len(self.ctrl_journal.GetValue()) >0 :
            texte = u"\n"
        else :
            texte = u""
        texte += u"[%s] %s" % (horodatage, message)
        self.ctrl_journal.AppendText(texte)
    
    def SetStatut(self, track=None, statut=None):
        track.statut = statut
        try :
            self.ctrl_donnees.EnsureCellVisible(self.ctrl_donnees.GetIndexOf(track)+1, 0)
        except :
            try :
                self.ctrl_donnees.EnsureCellVisible(self.ctrl_donnees.GetIndexOf(track), 0)
            except :
                pass

        self.ctrl_donnees.RefreshObject(track)
        if statut == "ok" :
            self.ctrl_donnees.Uncheck(track)
        
    def OnBoutonEnregistrer(self, event):
        standardPath = wx.StandardPaths.Get()
        wildcard = _(u"Tous les fichiers (*.*)|*.*")
        dlg = wx.FileDialog(None, message=_(u"Sélectionnez un répertoire et un nom de fichier"), defaultDir=standardPath.GetDocumentsDir(),  defaultFile="journal.txt", wildcard=wildcard, style=wx.FD_SAVE)
        nomFichier = None
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetPath()
        dlg.Destroy()
        if nomFichier == None : 
            return
        fichier = open(nomFichier, "w")
        fichier.write(self.ctrl_journal.GetValue())
        fichier.close()

    def OnBoutonOk(self, event):  
        listeTracks = self.ctrl_donnees.GetTracksCoches() 
        if len(listeTracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune action à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 

        dlg = Dialog_Traitement(self, listeTracks=listeTracks)
        dlg.ShowModal() 
        dlg.Destroy()
    
    def ArchiverFichiers(self):
        """ Archivage des fichiers traités """
        archiver = False
        
        # Récupère stats
        nbreTotal = 0
        nbreTraites = 0
        nbreNonTraites = 0
        nbreOk = 0
        nbreErreurs = 0
        for track in self.ctrl_donnees.donnees :
            nbreTotal += 1
            if track.statut != None : nbreTraites += 1
            if track.statut == None : nbreNonTraites += 1
            if track.statut == "ok" : nbreOk += 1
            if track.statut == "erreur" : nbreErreurs += 1
        
        #print nbreTotal, nbreTraites, nbreNonTraites, nbreOk, nbreErreurs
        
        # Si aucun traités
        if nbreTraites == 0 :
            return True
        
        # Si des erreurs ont été trouvées
        if nbreErreurs > 0 or nbreNonTraites > 0 :
            if nbreErreurs > 0 and nbreNonTraites == 0 : intro = _(u"%d erreurs ont été trouvées lors de l'importation. ") % nbreErreurs
            if nbreErreurs == 0 and nbreNonTraites > 0 : intro = _(u"%d actions n'ont pas été traitées. ") % nbreNonTraites
            if nbreErreurs > 0 and nbreNonTraites > 0 : intro = _(u"%d actions n'ont pas été traitées et %d erreurs ont été trouvées. ") % (nbreErreurs, nbreNonTraites)
            dlg = wx.MessageDialog(self, _(u"%s\n\nConfirmez-vous tout de même l'archivage des fichiers de synchronisation traités ?\n(Si vous choisissez Non, les fichiers seront conservés)") % intro, _(u"Archivage"), wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_CANCEL :
                return False
            if reponse == wx.ID_YES :
                archiver = True
                
        # Si tous ont été traités avec succès
        if nbreOk == nbreTotal :
            archiver = True
        
        # Archivage
        if archiver == True :
            
            # Récupération de la liste des fichiers
            if self.listeFichiers == None :
                listeFichiers = self.ctrl_donnees.listeFichiersTrouves
            else :
                listeFichiers = self.listeFichiers
            
            DB = GestionDB.DB()
            for nomFichier in listeFichiers :
                # Renommage et archivage
                if nomFichier.endswith(".archive") == False :
                    # Renommage
                    nomTemp = UTILS_Fichiers.GetRepSync(nomFichier.replace(".dat", ".archive"))
                    if os.path.isfile(nomTemp) == True :
                        os.remove(nomTemp)
                    os.rename(UTILS_Fichiers.GetRepSync(nomFichier), nomTemp)
                    # Mémorisation de l'archivage dans la base
                    nomFichierTemp = nomFichier.replace(".dat", "").replace(".archive", "")
                    ID_appareil = self.ctrl_donnees.dictIDappareil[nomFichierTemp]
                    IDarchive = DB.ReqInsert("nomade_archivage", [("nom_fichier", nomFichierTemp), ("ID_appareil", ID_appareil), ("date", datetime.date.today())])
            DB.Close()
            




# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Abort(Exception): 
    pass 

class Traitement(Thread): 
    def __init__(self, parent): 
        Thread.__init__(self) 
        self.parent = parent
        self.succes = False
        self.stop = False 
        self.index = 0

    def ConvertitHeure(self, heure=""):
        if heure in (None, "") :
            return None
        if "h" in heure :
            h, m = heure.split("h")
            if h == "" :
                h = 0
            else :
                h = int(h)
            if m == "" :
                m = 0
            else :
                m = int(m)
            heure = "%02d:%02d" % (h, m)
        return heure

    def run(self):
        nbre_tracks = len(self.parent.listeTracks)

        try: 
            
            listeAnomalies = []
            for track in self.parent.listeTracks :
                
                # Affichage
                texteIntro = u"[%d/%d] %s" % (self.index+1, len(self.parent.listeTracks), track.detail)
                self.parent.label_intro.SetLabel(texteIntro) 
                self.parent.ctrl_gauge.SetValue(self.index+1)

                if track.anomalie != False :
                    texte = track.detail + u" -> " + resultat
                    self.parent.parent.EcritLog(track.anomalie)
                    self.parent.parent.SetStatut(track, "erreur")
                    listeAnomalies.append(track.anomalie)

                else :

                    # ------------------- Traitement d'une consommation -------------------
                    if track.categorie == "consommation" :

                        # Initialisation de la grille
                        self.parent.ctrl_grille.InitGrille(IDindividu=track.IDindividu, IDfamille=track.IDfamille, IDactivite=track.IDactivite, date=track.date)
                        wx.Yield()

                        if track.etat == "reservation" : mode, etat = "reservation", "reservation"
                        if track.etat == "attente" : mode, etat = "attente", "reservation"
                        if track.etat == "refus" : mode, etat = "refus", "reservation"
                        if track.etat == "present" : mode, etat = "reservation", "present"
                        if track.etat == "absenti" : mode, etat = "reservation", "absenti"
                        if track.etat == "absentj" : mode, etat = "reservation", "absentj"

                        heure_debut = self.ConvertitHeure(track.heure_debut)
                        heure_fin = self.ConvertitHeure(track.heure_fin)

                        if track.action == "ajouter" or track.action == "modifier" :
                            resultat = self.parent.ctrl_grille.SaisieConso(IDunite=track.IDunite, mode=mode, etat=etat, heure_debut=heure_debut, heure_fin=heure_fin, quantite=track.quantite)
                        if track.action == "supprimer" :
                            resultat = self.parent.ctrl_grille.SupprimeConso(IDunite=track.IDunite, date=track.date)

                        # Sauvegarde de la grille des conso + Ecrit log
                        if resultat == True :
                            self.parent.ctrl_grille.Sauvegarde()
                            self.parent.parent.EcritLog(track.detail + u" -> ok")
                            self.parent.parent.SetStatut(track, "ok")
                        else :
                            texte = track.detail + u" -> " + resultat
                            self.parent.parent.EcritLog(texte)
                            self.parent.parent.SetStatut(track, "erreur")
                            listeAnomalies.append(texte)


                    # ------------------- Traitement d'un mémo journalier -------------------
                    if track.categorie == "memo_journee" :

                        DB = GestionDB.DB()
                        req = """SELECT IDmemo, IDindividu, date, texte FROM memo_journee WHERE IDindividu=%d AND date='%s';""" % (track.IDindividu, track.date)
                        DB.ExecuterReq(req)
                        listeMemos = DB.ResultatReq()
                        if len(listeMemos) > 1 :
                            IDmemo = listeMemos[0][0]
                        else :
                            IDmemo = None

                        listeDonnees = [("IDindividu", track.IDindividu), ("date", str(track.date)), ("texte", track.texte),]

                        if track.action == "ajouter" or track.action == "modifier" :
                            if IDmemo != None :
                                DB.ReqMAJ("memo_journee", listeDonnees, "IDmemo", IDmemo)
                            else :
                                DB.ReqInsert("memo_journee", listeDonnees)
                        if track.action == "supprimer" and IDmemo != None :
                            DB.ReqDEL("memo_journee", "IDmemo", IDmemo)

                        DB.Close()

                        self.parent.parent.EcritLog(track.detail + u" -> ok")
                        self.parent.parent.SetStatut(track, "ok")
                        
                # Arrête le traitement si bouton arrêter enfoncé
                if self.stop: 
                    raise Abort
                
                time.sleep(0.2)
                self.index += 1
            
            # Si fin 
            self.succes = True
            raise Abort
        
        except Abort, KeyBoardInterrupt: 
            if self.succes == True :
                self.parent.label_intro.SetLabel(_(u"Traitement terminé")) 
                self.parent.parent.EcritLog(_(u"Traitement terminé")) 
                self.parent.Fermer(forcer=True) 
            else:
                #print "arrete a l'index", self.index
                self.parent.label_intro.SetLabel(_(u"Traitement interrompu par l'utilisateur")) 
                self.parent.parent.EcritLog(_(u"Traitement interrompu par l'utilisateur")) 
                self.parent.bouton_fermer.SetBitmap(wx.Bitmap(Chemins.GetStaticPath(u"Images/BoutonsImages/Fermer_L72.png"), wx.BITMAP_TYPE_ANY))
        except Exception, err : 
            self.parent.parent.EcritLog("Erreur : " + str(err))
            self.stop = True 
            raise 
        
        # Message de confirmation de fin de traitement
        if len(listeAnomalies) > 0 :
            introduction = _(u"%d actions ont été importées avec succès et %d anomalies ont été trouvées :") % (nbre_tracks - len(listeAnomalies), len(listeAnomalies))
            conclusion = u""
            dlg = DLG_Messagebox.Dialog(None, titre=_(u"Information"), introduction=introduction, detail=u"\n".join(listeAnomalies), conclusion=conclusion, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Ok"),])
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
        else :
            dlg = wx.MessageDialog(None, _(u"Les %d actions ont été importées avec succès !") % nbre_tracks, _(u"Information"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def abort(self): 
        self.stop = True



class Dialog_Traitement(wx.Dialog):
    def __init__(self, parent, listeTracks=[], debug=False):
        wx.Dialog.__init__(self, parent, -1, style=wx.CAPTION|wx.SYSTEM_MENU)#wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.listeTracks = listeTracks
        self.debug = debug

        self.label_intro = wx.StaticText(self, -1, _(u"Initialisation..."))
        self.ctrl_gauge = wx.Gauge(self, -1, style=wx.GA_SMOOTH)
        self.ctrl_gauge.SetRange(len(listeTracks))
        self.ctrl_grille = DLG_Badgeage_grille.CTRL(self)
        if self.debug == False :
            self.ctrl_grille.Show(False) 
            
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Arreter_L72.png"), wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init
        self.bouton_ok.Show(False)
        wx.CallLater(1000, self.Demarrer)
        
    def __set_properties(self):
        self.SetTitle(_(u"Importation des données"))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer l'importation des données")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        if self.debug == False :
            self.SetMinSize((500, 100))
        else :
            self.SetMinSize((500, 300))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        grid_sizer_base.Add(self.label_intro, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_base.Add(self.ctrl_gauge, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_base.Add(self.ctrl_grille, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonFermer(self, event):
        self.Fermer() 
        
    def Fermer(self, forcer=False):
        # On vérifie si le thread n'a jamais été lancé avant :
        try:
            TraitmentEnCours = self.traitement.isAlive()
        except AttributeError :
            TraitmentEnCours = False
            
        if TraitmentEnCours:
            if forcer == True :
                self.traitement.abort()
            else :
                # Demande la confirmation de l'arrêt
                dlgConfirm = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment arrêter le traitement ?"), _(u"Confirmation d'arrêt"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                reponse = dlgConfirm.ShowModal()
                dlgConfirm.Destroy()
                if reponse == wx.ID_NO:
                    return
                # Si le traitement est en cours, on le stoppe :
                self.traitement.abort()
                self.label_intro.SetLabel(_(u"Vous avez interrompu le traitement."))
        
        # Fermeture de la fenêtre
        time.sleep(1)
        self.EndModal(wx.ID_CANCEL)
    
    def OnBoutonOk(self, event):
        self.Demarrer() 
    
    def Demarrer(self):
        self.parent.EcritLog(_(u"Lancement du traitement"))
        self.traitement = Traitement(self) 
        self.traitement.start()
        
            
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()