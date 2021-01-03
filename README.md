# Calibre Metadata Source Plugin pro Databáze knih CZ (DK)

## Vlastnosti
* odkaz na knihu se vybledává přes Google - díky tomu plugin dokáže správně najít i knihu s nejednoznačným názvem - např. HOT (jak uspět v digitálním světě)
* u knih vyplňuje:
    * popis (v kalibre označeno jako Komentáře)
    * hodnocení
    * tagy
    * jazyk
    * obálku
    * identifikátory - DK, ISBN

## Požadavky
* Calibre min. verze 5.0.1
* plugin byl testován pouze na Windows 10 / Calibre

### Instalace:
1. Spusťte Calibre
1. Přejděte na „Předvolby“ -> „Moduly“ a klikněte na tlačítko „Načíst modul ze souboru“.
1. Vyhledejte soubor s pluginem (databazeknihcz-vx_x_x.zip) a klikněte na tlačítko „Instalovat“.
1. Restartujte Calibre

## Další rozvoj:
* testy na dalších platformách (linux, macos)
* možnost vypnout parsing problematických metadat
* vypnutí / zapnutí rozšířeného logování
* testy na více verzích Calibre  
* optimalizace, komentáře v kódu ...
* multijazyčnost
* možnost si v konfiguraci upravit:
  * URL pro "celý text..."
  * některé XPATH

## Inspirace pro plugin:
* Calibre Metadata Source Plugin for Deutsche Nationalbibliothek (DNB) - https://github.com/citronalco/calibre-dnb
* Calibre METADATA from ComicWiki.dk - https://github.com/mickkn/calibre_metadata_comicwiki/
* Databazeknih.CZ - Daniel Prazak <kret33n@gmail.com> - https://www.mobileread.com/forums/showthread.php?t=155524
