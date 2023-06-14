#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

LISTE_SERVEURS_FAI = [
    ( u"9 Telecom", "smtp.neuf.fr", None, True, True),
    ( u"9ONLINE", "smtp.9online.fr", None, False, False),
    ( u"ALICE ADSL", "smtp.aliceadsl.fr", None, False, False),
    ( u"AOL", "smtp.neuf.fr", None, False, False),
    ( u"Bouygues BBOX", "smtp.bbox.fr", None, False, False),
    ( u"Bouygues Télécom", "smtp.bouygtel.fr", None, False, False),
    ( u"CEGETEL", "smtp.cegetel.net", None, False, False),
    ( u"CLUB INTERNET", "mail.club-internet.fr", None, False, False),
    ( u"DARTY BOX", "smtpauth.dbmail.com", None, False, False),
    ( u"FREE", "smtp.free.fr", None, False, False),
    ( u"FREESURF", "smtp.freesurf.fr", None, False, False),
    ( u"GAWAB", "smtp.gawab.com", None, False, False),
    ( u"GMAIL", "smtp.gmail.com", 587, True, True),
    ( u"HOTMAIL", "smtp.live.com", 25, True, True),
    ( u"IFrance", "smtp.ifrance.com", None, False, False),
    ( u"LA POSTE", "smtp.laposte.net", None, False, False),
    ( u"MAGIC ONLINE", "smtp.magic.fr", None, False, False),
    ( u"NERIM", "smtp.nerim.net", None, False, False),
    ( u"NOOS", "mail.noos.fr", None, False, False),
    ( u"Numéricable", "smtp.numericable.fr", None, False, False),
    ( u"ORANGE", "smtp.orange.fr", None, False, False),
    ( u"OREKA", "mail.oreka.fr", None, False, False),
    ( u"SYMPATICO", "smtp1.sympatico.ca", None, False, False),
    ( u"SFR", "smtp.sfr.fr", None, False, False),
    ( u"TELE2", "smtp.tele2.fr", None, False, False),
    ( u"TISCALI", "smtp.tiscali.fr", None, False, False),
    ( u"TISCALI-FREESBEE", "smtp.freesbee.fr", None, False, False),
    ( u"WANADOO", "smtp.wanadoo.fr", None, False, False),
    ( u"YAHOO", "smtp.mail.yahoo.fr", 465, True, True),
    ] # Nom FAI, serveur smtp, port, connexionAuthentifiee, startTLS
