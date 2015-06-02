#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.dialogs as dialogs
import GestionDB
import UTILS_Dates
import UTILS_Titulaires
import UTILS_Historique
import DLG_Appliquer_forfait

import datetime
import time

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, donnees):
        self.IDindividu = donnees["IDindividu"]
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        self.nomTitulaires = donnees["nomTitulaires"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.IDfamille = donnees["IDfamille"]
        self.rue = donnees["rue"]
        self.cp = donnees["cp"]
        self.ville = donnees["ville"]
        self.nomSecteur = donnees["nomSecteur"]
        self.inscrit = "non"
        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.IDactivite = None
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        print "ok"
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        dictTitulaires = UTILS_Titulaires.GetTitulaires()
        
        DB = GestionDB.DB()
        
        # Récupération des inscriptions existantes
        req = """SELECT IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, IDcompte_payeur, date_inscription, parti
        FROM inscriptions;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictInscriptions = {}
        for IDinscription, IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, IDcompte_payeur, date_inscription, parti in listeDonnees :
            self.dictInscriptions[(IDindividu, IDfamille, IDactivite) ] = {"IDinscription" : IDinscription, "IDgroupe" : IDgroupe, "IDcategorie_tarif" : IDcategorie_tarif} 
        
        # Récupération des individus
        req = """SELECT individus.IDindividu, nom, prenom, date_naiss, rattachements.IDfamille, comptes_payeurs.IDcompte_payeur
        FROM individus
        LEFT JOIN rattachements ON rattachements.IDindividu = individus.IDindividu
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = rattachements.IDfamille
        WHERE IDcategorie IN (1, 2) AND rattachements.IDfamille IS NOT NULL
        GROUP BY individus.IDindividu, rattachements.IDfamille;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        DB.Close()
        listeListeView = []
        for IDindividu, nom, prenom, date_naiss, IDfamille, IDcompte_payeur in listeDonnees :
            date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
            age = UTILS_Dates.CalculeAge(date_naiss=date_naiss)
            nomTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
            rue = dictTitulaires[IDfamille]["adresse"]["rue"]
            cp = dictTitulaires[IDfamille]["adresse"]["cp"]
            ville = dictTitulaires[IDfamille]["adresse"]["ville"]
            nomSecteur = dictTitulaires[IDfamille]["adresse"]["nomSecteur"]
            dictTemp = {
                "IDindividu" : IDindividu, "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss, "age" : age, "nomTitulaires" : nomTitulaires, "IDfamille" : IDfamille, "IDcompte_payeur" : IDcompte_payeur,
                "rue" : rue, "cp" : cp, "ville" : ville, "nomSecteur" : nomSecteur,
                }
            listeListeView.append(Track(dictTemp))
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)
        
        def FormateAge(age):
            if age == None : return ""
            return _(u"%d ans") % age
        
        def FormateInscrit(inscrit):
            if inscrit == "oui" :
                return "Oui"
            else :
                return ""
            
        liste_Colonnes = [
            ColumnDefn(_(u"IDindividu"), "left", 0, "IDindividu", typeDonnee="entier"),
            ColumnDefn(_(u"Inscrit"), 'left', 50, "inscrit", typeDonnee="texte", stringConverter=FormateInscrit),
            ColumnDefn(_(u"Nom"), 'left', 120, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Prénom"), "left", 120, "prenom", typeDonnee="texte"),
            ColumnDefn(_(u"Date naiss."), "left", 80, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Age"), "left", 60, "age", typeDonnee="entier", stringConverter=FormateAge),
            ColumnDefn(_(u"Famille"), "left", 280, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Rue"), "left", 200, "rue", typeDonnee="texte"),
            ColumnDefn(_(u"CP"), "left", 50, "cp", typeDonnee="texte"),
            ColumnDefn(_(u"Ville"), "left", 150, "ville", typeDonnee="texte"),
            ColumnDefn(_(u"Secteur"), "left", 150, "nomSecteur", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucun individu"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[3])
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = wx.Menu()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)

        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des individus à inscrire"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des individus à inscrire"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des individus à inscrire"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des individus à inscrire"))
    
    def SetIDactivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        listeTemp = []
        for track in self.donnees :
            key = (track.IDindividu, track.IDfamille, IDactivite)
            if self.dictInscriptions.has_key(key) :
                track.inscrit = "oui"
            else :
                track.inscrit = "non"
            listeTemp.append(track)
        self.RefreshObjects(listeTemp) 
        
    def Inscrire(self, IDactivite=None, nomActivite="", IDgroupe=None, nomGroupe="", IDcategorie_tarif=None, nomCategorie=""):
        """ Lance la procédure d'inscription """
        tracks = self.GetCheckedObjects() 
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment inscrire %d individus à l'activité '%s' ?") % (len(tracks), nomActivite), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy() 
        if reponse  != wx.ID_YES :
            return
        
        dlgprogress = wx.ProgressDialog(_(u"Veuillez patienter"), _(u"Lancement de la procédure..."), maximum=len(tracks), parent=None, style= wx.PD_SMOOTH | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        
        listeAnomalies = []
        listeValidees = []
        index = 0
        for track in tracks :            
            # Recherche du nom de l'individu
            if track.prenom == None :
                nomIndividu = track.nom
            else :
                nomIndividu = u"%s %s" % (track.nom, track.prenom)
            
            keepGoing, skip = dlgprogress.Update(index, _(u"[%d/%d] Inscription de %s...") % (index, len(tracks), nomIndividu))
            
            # Vérifie si individu déjà inscrit
            if track.inscrit == "oui" :
                listeAnomalies.append(_(u"%s (Famille de %s) : Individu déjà inscrit") % (nomIndividu, track.nomTitulaires))
                index += 1
                
            else :
                # Sauvegarde
                DB = GestionDB.DB()
                listeDonnees = [
                    ("IDindividu", track.IDindividu ),
                    ("IDfamille", track.IDfamille ),
                    ("IDactivite", IDactivite ),
                    ("IDgroupe", IDgroupe),
                    ("IDcategorie_tarif", IDcategorie_tarif),
                    ("IDcompte_payeur", track.IDcompte_payeur),
                    ("date_inscription", str(datetime.date.today()) ),
                    ("parti", 0),
                    ]
                IDinscription = DB.ReqInsert("inscriptions", listeDonnees)
                DB.Close()
                
                # Mémorise l'action dans l'historique
                UTILS_Historique.InsertActions([{
                    "IDindividu" : track.IDindividu,
                    "IDfamille" : track.IDfamille,
                    "IDcategorie" : 18, 
                    "action" : _(u"Inscription à l'activité '%s' sur le groupe '%s' avec la tarification '%s'") % (nomActivite, nomGroupe, nomCategorie)
                    },])
                
                # Saisie de forfaits auto
                f = DLG_Appliquer_forfait.Forfaits(IDfamille=track.IDfamille, listeActivites=[IDactivite,], listeIndividus=[track.IDindividu,], saisieManuelle=False, saisieAuto=True)
                f.Applique_forfait(selectionIDcategorie_tarif=IDcategorie_tarif, inscription=True, selectionIDactivite=IDactivite) 
                            
                # Actualise l'affichage
                self.dictInscriptions[(track.IDindividu, track.IDfamille, IDactivite)] = {"IDinscription" : IDinscription, "IDgroupe" : IDgroupe, "IDcategorie_tarif" : IDcategorie_tarif} 
                track.inscrit = "oui"
                self.RefreshObject(track)
                
                # Attente
                listeValidees.append(track)
                time.sleep(0.2)
                index += 1
            
            # Stoppe la procédure
            if keepGoing == False :
                break
            
        # Fermeture dlgprogress
        dlgprogress.Destroy()
        
        # Messages de fin
        if len(listeAnomalies) > 0 :
            message1 = _(u"%d inscriptions ont été créées avec succès mais les %d anomalies suivantes ont été trouvées :") % (len(listeValidees), len(listeAnomalies))
            message2 = u"\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, message1, caption = _(u"Inscription"), msg2=message2, style = wx.ICON_EXCLAMATION | wx.YES|wx.YES_DEFAULT, btnLabels={wx.ID_YES : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
        else :
            dlg = wx.MessageDialog(self, _(u"%d inscriptions ont été créées avec succès !") % len(listeValidees), _(u"Fin"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()










# -------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
