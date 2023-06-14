#!\\usr\\bin\\env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
#-----------------------------------------------------------

import sys
import os
import glob
import os.path
import zipfile
import shutil


# Chemins
REP_COURANT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REP_COURANT)
NOETHYS_PATH = os.path.join(REP_COURANT, "noethys")
sys.path.insert(1, NOETHYS_PATH)

from setuptools import setup, find_packages

if "py2exe" in sys.argv :
    import py2exe
    import numpy



manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="Noethys"
    type="win32"
  />
  <description>Noethys</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="x86"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
"""



def GetVersion():
    """ Recherche du numéro de version """
    fichierVersion = open(os.path.join(NOETHYS_PATH, "Versions.txt"), "r")
    txtVersion = fichierVersion.readlines()[0]
    fichierVersion.close()
    pos_debut_numVersion = txtVersion.find("n")
    pos_fin_numVersion = txtVersion.find("(")
    numVersion = txtVersion[pos_debut_numVersion+1:pos_fin_numVersion].strip()
    return numVersion

VERSION_APPLICATION = GetVersion()


options = {
    "py2exe": {
        "includes" : [
                "matplotlib.backends",
                "matplotlib.figure", "matplotlib.backends.backend_wxagg", "pylab", "numpy",
                "email", "email.encoders", "email.generator", "email.iterators", "email.utils",
                "email.mime.base", "email.mime.multipart", "email.mime.text",
                "email.mime.image", "email.mime.audio", "email.base64mime",
                "pyttsx.drivers.sapi5", "zope.interface", "mysql.connector.locales.eng.client_error"
                ],

         'excludes' : [
                '_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg',
                '_fltkagg', '_gtk', '_gtkcairo',
                'backend_qt', 'backend_qt4', 'backend_qt4agg',
                'backend_qtagg',
                'backend_cairo', 'backend_cocoaagg',
                'Tkconstants', 'Tkinter', 'tcl',
                "_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk",
                ],

        'dll_excludes': [
                "tcl84.dll", "tk84.dll", "wxmsw26uh_vc.dll", "libgdk-win32-2.0-0.dll",
                "libgobject-2.0-0.dll", "UxTheme.dll", "mswsock.dll", "powrprof.dll",
                "msvcp90.dll", "msvcm90.dll",

                "AVICAP32.dll", "AVIFIL32.dll", "MPR.dll", "MSACM32.dll", "MSVFW32.dll",
                "KERNELBASE.dll", "crypt32.dll", "WLDAP32.dll",
                "combase.dll", "dhcpcsvc.DLL",
                "iertutil.dll", "IPHLPAPI.DLL", "NSI.dll", "OLEACC.dll",
                "PSAPI.DLL", "Secur32.dll", "SETUPAPI.dll", "urlmon.dll",
                "USERENV.dll", "USP10.dll", "WININET.dll", "WTSAPI32.dll",

                "api-ms-win-core-delayload-l1-1-1.dll", "api-ms-win-core-heap-obsolete-l1-1-0.dll",
                "api-ms-win-core-localization-obsolete-l1-2-0.dll", "api-ms-win-core-string-obsolete-l1-1-0.dll",
                "api-ms-win-core-string-l1-1-0.dll", "api-ms-win-core-registry-l1-1-0.dll",
                "api-ms-win-core-errorhandling-l1-1-1.dll", "api-ms-win-core-string-l2-1-0.dll",
                "api-ms-win-core-profile-l1-1-0.dll", "api-ms-win*.dll",
                "api-ms-win-core-processthreads-l1-1-2.dll", "api-ms-win-core-libraryloader-l1-2-1.dll",
                "api-ms-win-core-file-l1-2-1.dll", "api-ms-win-security-base-l1-2-0.dll",
                "api-ms-win-eventing-provider-l1-1-0.dll", "api-ms-win-core-heap-l2-1-0.dll",
                "api-ms-win-core-libraryloader-l1-2-0.dll", "api-ms-win-core-localization-l1-2-1.dll",
                "api-ms-win-core-sysinfo-l1-2-1.dll", "api-ms-win-core-synch-l1-2-0.dll",
                "api-ms-win-core-heap-l1-2-0.dll", "api-ms-win-core-handle-l1-1-0.dll",
                "api-ms-win-core-io-l1-1-1.dll", "api-ms-win-core-com-l1-1-1.dll",
                "api-ms-win-core-memory-l1-1-2.dll", "api-ms-win-core-version-l1-1-1.dll",
                "api-ms-win-core-version-l1-1-0.dll",

                "numpy-atlas.dll",

                ],

        "packages": [
                "pytz", "reportlab", "twisted", "twisted.web.resource", "sqlalchemy",
                "cffi", "cryptography", "lxml",
                ],

        "typelibs": [
                ('{C866CA3A-32F7-11D2-9602-00C04F8EE628}', 0, 5, 4), # Pour Pyttsx - Version Windows 7
                ],

        #'compressed' : 1 ,.
        #'optimize': 2,
        }
    }



def GetDossiers(rep) :
    listeFichiers = filter(os.path.isfile, glob.glob(os.path.join("noethys", rep, "*")))
    return rep, listeFichiers

data_files=[

            # Images
            GetDossiers("Static/Images/16x16"),
            GetDossiers("Static/Images/22x22"),
            GetDossiers("Static/Images/32x32"),
            GetDossiers("Static/Images/48x48"),
            GetDossiers("Static/Images/80x80"),
            GetDossiers("Static/Images/128x128"),
            GetDossiers("Static/Images/BoutonsImages"),
            GetDossiers("Static/Images/Drapeaux"),
            GetDossiers("Static/Images/Special"),
            GetDossiers("Static/Images/Badgeage"),
            GetDossiers("Static/Images/Menus"),
            GetDossiers("Static/Images/Teamword"),
            GetDossiers("Static/Images/Avatars/16x16"),
            GetDossiers("Static/Images/Avatars/128x128"),
            GetDossiers("Static/Images/Interface/Vert"),
            GetDossiers("Static/Images/Interface/Bleu"),
            GetDossiers("Static/Images/Interface/Noir"),

            # Databases
            GetDossiers("Static/Databases"),

            # Divers
            GetDossiers("Static/Divers"),

            # Exemples
            GetDossiers("Static/Exemples"),

            # Lang
            GetDossiers("Static/Lang"),

            # Polices
            GetDossiers("Static/Polices"),

            # Fichiers à importer :
            ('', ['noethys/Versions.txt', 'noethys/Licence.txt', 'noethys/Icone.ico']),

            ]


# Autres data_files
if "py2exe" in sys.argv :

    # Ajoute les fichiers de Matplotlib
    import matplotlib as mp
    matplotlib_font_afm = glob.glob(os.sep.join([mp.get_data_path(), 'fonts\\afm\\*']))
    matplotlib_font_pdfcorefonts = glob.glob(os.sep.join([mp.get_data_path(), 'fonts\\pdfcorefonts\\*']))
    matplotlib_font_ttf = glob.glob(os.sep.join([mp.get_data_path(), 'fonts\\ttf\\*']))
    matplotlib_images = glob.glob(os.sep.join([mp.get_data_path(), 'images\\*']))
    data_files += mp.get_py2exe_datafiles()

    # Ajoute les fichiers Windows
    data_files.append(('', ['noethys/msvcm90.dll', 'noethys/msvcp90.dll', 'noethys/msvcr90.dll', 'noethys/Microsoft.VC90.CRT.manifest', 'noethys/gdiplus.dll', ]))


setup(
    name = "Noethys",
    version = VERSION_APPLICATION,
    author = "Ivan LUCAS",
    description = u"Noethys, le logiciel libre et gratuit de gestion multi-activités",
    long_description = open("README.md").read().decode("utf8"),
    url = "http://www.noethys.com",
    license = "GPL V3",
    plateformes = "ALL",
    classifiers = [ "Topic :: Office/Business",
                    "Topic :: Education"
                    "Topic :: Utilities"],
    options = options,
    data_files = data_files,
    #dependency_links = [],
    packages = ["noethys", "noethys.Ctrl", "noethys.Data", "noethys.Dlg", "noethys.ObjectListView", "noethys.Ol", "noethys.Outils", "noethys.Utils"],
    install_requires = open("requirements.txt").readlines(),
    windows = [
        {
            "script" : "noethys/Noethys.py",
            "icon_resources" : [(1, "noethys/Icone.ico")],
            "other_resources": [(24,1, manifest)]
        }

    ],)


# Insertions manuelles dans le ZIP
if "py2exe" in sys.argv :

    z = zipfile.ZipFile(os.path.join("dist/", "library.zip"), 'a')

    # IMPORTANT : Ce code ne fonctione que si Pytz est unzippé :
    # Commande easy_install --upgrade --always-unzip pytz
    # Pour la mettre à jour avec un dézippe automatique

    # Timezone de pytz :
    print "Ajout manuel du repertoire Zoneinfo de pytz..."
    import pytz
    zoneinfo_dir = os.path.join(os.path.dirname(pytz.__file__), 'zoneinfo')
    disk_basedir = os.path.dirname(os.path.dirname(pytz.__file__))
    for absdir, directories, filenames in os.walk(zoneinfo_dir):
        assert absdir.startswith(disk_basedir), (absdir, disk_basedir)
        zip_dir = absdir[len(disk_basedir):]
        for f in filenames:
            z.write(os.path.join(absdir, f), os.path.join(zip_dir, f))

    # Typelibs Microsoft Speech pour Windows XP
    print "Ajout manuel du Typelibs Microsoft Speech pour Windows XP..."
    nom = "C866CA3A-32F7-11D2-9602-00C04F8EE628x0x5x0.py"
    z.write("noethys/Outils/%s" % nom, "win32com/gen_py/%s" % nom)

    # Importe le cacert.pem dans le répertoire certifi
    import certifi
    chemin_cert = certifi.where()
    z.write(chemin_cert, "certifi/cacert.pem")

    # Cloture le ZIP
    z.close()

    # Supprime le répertoire des données exemples de Matplotlib
    print "Supprime les donnees exemples de Matplotlib si besoin..."
    try :
        shutil.rmtree("dist/mpl-data/sample_data")
    except :
        pass


print "Fini !"
