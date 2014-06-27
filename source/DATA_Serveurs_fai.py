#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

LISTE_SERVEURS_FAI = [
    ( u"9 Telecom", "smtp.neuf.fr", None, True),
    ( u"9ONLINE", "smtp.9online.fr", None, False),
    ( u"ALICE ADSL", "smtp.aliceadsl.fr", None, False),
    ( u"AOL", "smtp.neuf.fr", None, False),
    ( u"Bouygues BBOX", "smtp.bbox.fr", None, False),
    ( u"Bouygues Télécom", "smtp.bouygtel.fr", None, False),
    ( u"CEGETEL", "smtp.cegetel.net", None, False),
    ( u"CLUB INTERNET", "mail.club-internet.fr", None, False),
    ( u"DARTY BOX", "smtpauth.dbmail.com", None, False),
    ( u"FREE", "smtp.free.fr", None, False),
    ( u"FREESURF", "smtp.freesurf.fr", None, False),
    ( u"GAWAB", "smtp.gawab.com", None, False),
    ( u"GMAIL", "smtp.gmail.com", 587, True),
    ( u"HOTMAIL", "smtp.live.com", 25, True),
    ( u"IFrance", "smtp.ifrance.com", None, False),
    ( u"LA POSTE", "smtp.laposte.net", None, False),
    ( u"MAGIC ONLINE", "smtp.magic.fr", None, False),
    ( u"NERIM", "smtp.nerim.net", None, False),
    ( u"NOOS", "mail.noos.fr", None, False),
    ( u"Numéricable", "smtp.numericable.fr", None, False),
    ( u"ORANGE", "smtp.orange.fr", None, False),
    ( u"OREKA", "mail.oreka.fr", None, False),
    ( u"SYMPATICO", "smtp1.sympatico.ca", None, False),
    ( u"SFR", "smtp.sfr.fr", None, False),
    ( u"TELE2", "smtp.tele2.fr", None, False),
    ( u"TISCALI", "smtp.tiscali.fr", None, False),
    ( u"TISCALI-FREESBEE", "smtp.freesbee.fr", None, False),
    ( u"WANADOO", "smtp.wanadoo.fr", None, False),
    ( u"YAHOO", "smtp.mail.yahoo.fr", 465, True),
    ] # Nom FAI, serveur smtp, port, connexion ssl
