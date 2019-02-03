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
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Dates
from Utils import UTILS_Config
from Dlg import DLG_Saisie_quotient
import GestionDB



class CTRL_Drag(wx.TextCtrl):
    def __init__(self, parent, texte=""):
        wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_READONLY)
        self.parent = parent
        self.SetBackgroundColour(wx.Colour(248, 248, 248))
        self.SetValue(texte)

        # Propriétés
        self.SetToolTip(wx.ToolTip(_(u"Faites un glisser-déposer pour envoyer cette information dans le formulaire de votre navigateur internet")))

        # Binds
        self.Bind(wx.EVT_MOTION, self.OnStartDrag)

    def OnStartDrag(self, evt):
        if evt.Dragging():
            url = self.GetValue()
            data = wx.URLDataObject()
            data.SetURL(url)

            dropSource = wx.DropSource(self)
            dropSource.SetData(data)
            result = dropSource.DoDragDrop()




# -----------------------------------------------------------------------------------------------------

class MyTextDropTarget(wx.TextDropTarget):
    def __init__(self, window):
        wx.TextDropTarget.__init__(self)
        self.window = window

    def OnDropText(self, x, y, text):
        try :
            quotient = int(text)
        except :
            dlg = wx.MessageDialog(self.window, _(u"La donnée que vous avez déposé ne semble pas valide. Il ne peut s'agit que d'un nombre entier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.window.SetTexte(str(quotient))

    def OnDragOver(self, x, y, d):
        return wx.DragCopy


class CTRL_Drop_archive(wx.TextCtrl):
    def __init__(self, parent, texte=""):
        wx.TextCtrl.__init__(self, parent, -1, texte, style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL|wx.TE_READONLY)
        self.parent = parent
        self.SetBackgroundColour(wx.WHITE)

        # Activation du drop
        dt = MyTextDropTarget(self)
        self.SetDropTarget(dt)

        # Propriétés
        self.SetToolTip(wx.ToolTip(_(u"Sélectionnez le quotient dans votre navigateur internet et glissez-le jusqu'ici")))

    def SetTexte(self, texte=None):
        if texte == None :
            texte = ""
        self.SetValue(texte)



class CTRL_Drop(wx.StaticBitmap):
    def __init__(self, parent, taille=(64, 64), texte_defaut="", tip=""):
        wx.StaticBitmap.__init__(self, parent, -1, size=taille)
        self.parent = parent
        self.taille = taille
        self.texte_defaut = texte_defaut
        self.texte = None

        # Activation du drop
        dt = MyTextDropTarget(self)
        self.SetDropTarget(dt)

        # Propriétés
        self.SetToolTip(wx.ToolTip(tip))

        # Binds
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDLeftDown)

        # Init
        self.MAJ()

    def OnDLeftDown(self, event):
        dlg = wx.TextEntryDialog(self, _(u"Veuillez modifier la valeur :"), _(u"Modification"))
        if self.texte != None :
            dlg.SetValue(self.texte)
        reponse = dlg.ShowModal()
        if reponse != wx.ID_OK:
            dlg.Destroy()
            return
        texte = dlg.GetValue()
        dlg.Destroy()
        if texte == "" :
            texte = None
        else :
            try :
                quotient = int(texte)
            except :
                dlg = wx.MessageDialog(self, _(u"La donnée que vous avez saisi ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        self.SetTexte(texte)

    def MAJ(self):
        bmp = self.CreationImageDrop()
        self.SetBitmap(bmp)
        self.GetParent().Layout()

    def SetTexte(self, texte=None):
        self.texte = texte
        self.MAJ()
        self.GetGrandParent().bouton_ok.Enable(True)

    def GetTexte(self):
        return self.texte

    def CreationImageDrop(self):
        """ Création d'une image pour la réception drop de données """
        # Création du bitmap
        largeurImage, hauteurImage = self.taille
        bmp = wx.EmptyBitmap(largeurImage, hauteurImage)
        mdc = wx.MemoryDC(bmp)
        dc = wx.GCDC(mdc)
        mdc.SetBackgroundMode(wx.TRANSPARENT)
        mdc.Clear()

        # Texte
        if self.texte == None :
            # Texte par défaut si valeur vide
            taille_police = 7
            couleur_texte = wx.Colour(150, 150, 150)
            couleur_fond = wx.Colour(248, 248, 248)
            texte = self.texte_defaut
            dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        else :
            # Texte si valeur
            taille_police = 20
            couleur_texte = wx.Colour(50, 50, 50)
            couleur_fond = wx.Colour(255, 255, 255)
            texte = self.texte
            dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        dc.SetTextForeground(couleur_texte)
        largeurTexte, hauteurTexte = dc.GetTextExtent(texte)

        # Image
        #image = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Badgeage.png"), wx.BITMAP_TYPE_PNG)
        #mdc.DrawBitmap(image, 0, 0)

        # Cadre
        dc.SetBrush(wx.Brush(couleur_fond))
        dc.SetPen(wx.Pen(couleur_texte, width=2, style=wx.PENSTYLE_DOT))
        dc.DrawRoundedRectangleRect(wx.Rect(0, 0, largeurImage, hauteurImage), 10)

        # Texte
        if texte != None :
            xTexte = largeurImage / 2.0 - largeurTexte / 2.0
            yTexte = hauteurImage / 2.0 - hauteurTexte / 2.0 - 1
            dc.DrawLabel(texte, wx.Rect(xTexte, yTexte, largeurTexte, hauteurTexte), wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)


        if texte != None :
            xTexte = largeurImage / 2.0 - largeurTexte / 2.0
            yTexte = hauteurImage / 2.0 - hauteurTexte / 2.0 - 1
            dc.DrawLabel(texte, wx.Rect(xTexte, yTexte, largeurTexte, hauteurTexte), wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        mdc.SelectObject(wx.NullBitmap)
        return bmp



# ------------------------------------------------------------------------------------------------------------------------------

class Frame(wx.Frame):
    def __init__(self, parent, IDfamille=None, dictDonnees={}):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP)
        self.parent = parent
        self.IDfamille = IDfamille

        self.panel = wx.Panel(self)

        # Bandeau
        titre = _(u"Consultation CAF-CDAP")
        intro = _(u"Glissez-déposez le numéro d'allocataire et le nom vers le formulaire de CDAP. Puis sélectionnez et glissez-déposez le QF ou le revenu ci-dessous.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self.panel, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Caf.png")

        # Informations
        self.box_informations = wx.StaticBox(self.panel, -1, _(u"Informations"))
        self.label_nom = wx.StaticText(self.panel, -1, _(u"Nom de famille :"))
        self.ctrl_nom = CTRL_Drag(self.panel, texte="")
        self.label_numero = wx.StaticText(self.panel, -1, _(u"Numéro d'allocataire :"))
        self.ctrl_numero = CTRL_Drag(self.panel, texte="")

        # Informations
        self.box_quotient = wx.StaticBox(self.panel, -1, _(u"Quotient familial/Revenu"))
        self.ctrl_quotient = CTRL_Drop(self.panel, taille=(180, 80), texte_defaut=_(u"Sélectionnez et glissez-déposez\nle quotient familial ici"), tip=_(u"Double-cliquez sur le quotient dans votre navigateur internet pour le sélectionner et glissez-le jusqu'ici.\n\nVous pouvez également faire un double-clic pour saisir ou modifier la valeur manuellement."))
        self.ctrl_revenu = CTRL_Drop(self.panel, taille=(180, 80), texte_defaut=_(u"Sélectionnez et glissez-déposez\nle revenu annuel ici"), tip=_(u"Double-cliquez sur le revenu dans votre navigateur internet pour le sélectionner et glissez-le jusqu'ici.\n\nVous pouvez également faire un double-clic pour saisir ou modifier la valeur manuellement."))

        texte_dernier_qf = self.GetTexteDernierQF()
        self.label_dernier_qf = wx.StaticText(self.panel, -1, texte_dernier_qf, style=wx.ALIGN_CENTER)
        self.label_dernier_qf.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, False, 'Arial'))
        self.label_dernier_qf.SetForegroundColour(wx.Colour(150, 150, 150))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Enregistrer"), cheminImage="Images/32x32/Sauvegarder.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Init
        self.bouton_ok.Enable(False)

        # Remplissage des champs
        if "nom_allocataire" in dictDonnees :
            self.ctrl_nom.SetValue(dictDonnees["nom_allocataire"])
        if "numero_allocataire" in dictDonnees :
            self.ctrl_numero.SetValue(dictDonnees["numero_allocataire"])

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour enregistrer le nouveau quotient familial dans la fiche famille")))
        self.SetMinSize((440, 420))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_base)

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=10)

        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.ALL|wx.EXPAND, 0)

        # Contenu
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Informations
        box_informations = wx.StaticBoxSizer(self.box_informations, wx.VERTICAL)
        grid_sizer_informations = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_informations.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_informations.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_informations.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_informations.Add(self.ctrl_numero, 0, wx.EXPAND, 0)
        grid_sizer_informations.AddGrowableCol(1)
        box_informations.Add(grid_sizer_informations, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_informations, 1, wx.ALL|wx.EXPAND, 0)

        # Quotient familial
        box_quotient = wx.StaticBoxSizer(self.box_quotient, wx.VERTICAL)
        grid_sizer_quotient = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=10)
        grid_sizer_quotient.Add(self.ctrl_quotient, 0, wx.EXPAND, 0)
        grid_sizer_quotient.Add(self.ctrl_revenu, 0, wx.EXPAND, 0)
        grid_sizer_quotient.AddGrowableRow(0)
        grid_sizer_quotient.AddGrowableCol(0)
        grid_sizer_quotient.AddGrowableCol(1)
        box_quotient.Add(grid_sizer_quotient, 1, wx.ALL | wx.EXPAND, 10)
        box_quotient.Add(self.label_dernier_qf, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(box_quotient, 1, wx.ALL|wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

        sizer_base.Fit(self)
        self.panel.SetSizer(grid_sizer_base)
        self.Layout()

        # Position de la fenêtre
        position = UTILS_Config.GetParametre("position_fenetre_cafpro", defaut=None)
        if position != None:
            self.SetPosition(position)
        else :
            marge = 50
            largeur_ecran, hauteur_ecran = wx.GetDisplaySize()
            x = largeur_ecran - self.GetSize()[0] - marge
            y = marge
            self.SetPosition((x, y))
            #self.CentreOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnClose(self, event):
        self.MemoriserParametres()
        event.Skip()

    def OnBoutonFermer(self, event):
        self.MemoriserParametres()
        # Fermer
        self.Destroy()

    def MemoriserParametres(self):
        UTILS_Config.SetParametre("position_fenetre_cafpro", self.GetPosition())

    def GetTexteDernierQF(self):
        DB = GestionDB.DB()
        req = """
        SELECT date_debut, date_fin, quotient, revenu, types_quotients.nom
        FROM quotients
        LEFT JOIN types_quotients ON types_quotients.IDtype_quotient = quotients.IDtype_quotient
        WHERE IDfamille=%d
        ORDER BY date_fin DESC
        """ % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        texte = _(u"Aucun précédent QF")
        if len(listeDonnees) > 0 :
            date_debut, date_fin, quotient, revenu, nom_quotient = listeDonnees[0]
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            if revenu == 0.0 :
                revenu = None
            if quotient != None and revenu == None :
                texte = _(u"Dernier quotient familial : %d du %s au %s (%s)") % (quotient, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin), nom_quotient)
            elif quotient == None and revenu != None :
                texte = _(u"Dernier revenu : %d du %s au %s (%s)") % (revenu, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin), nom_quotient)
            elif quotient != None and revenu != None :
                texte = _(u"Dernier quotient/revenu : %s/%s du %s au %s (%s)") % (quotient, revenu, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin), nom_quotient)
        return texte

    def OnBoutonOk(self, event):
        quotient = self.ctrl_quotient.GetTexte()
        revenu = self.ctrl_revenu.GetTexte()

        dlg = DLG_Saisie_quotient.Dialog(self, IDfamille=self.IDfamille)
        if quotient != None :
            dlg.SetQuotient(quotient)
        if revenu != None :
            dlg.SetRevenu(float(revenu))
        dlg.SetTitle(_(u"Saisie d'un quotient familial/revenu"))
        if dlg.ShowModal() == wx.ID_OK:
            IDquotient = dlg.GetIDquotient()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return

        # Fermeture de la dlg
        self.Destroy()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = Frame(None, IDfamille=1)
    app.SetTopWindow(frm)
    frm.Show()
    app.MainLoop()
