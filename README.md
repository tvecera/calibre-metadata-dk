# Calibre Metadata Source Plugin pro Databáze knih CZ (DK)

## Verze

### v0.9.3 (12/2022)
* oprava vyhledávání knihy přes Google Search
* oprava nefunkčního pluginu ve vyšších verzích Calibre
* minimální podporovaná verze 6.10.0
* drobné opravy parsování metadat

### v0.9.2 (01/2021)
* oprava vyhledávání knihy přes Google Search
* kniha s identifikátorem z databazeknih se již nevyhledává přes google search
* ověření funkčnosti na verzi 5.9.0

### v0.9.1 (01/2021)
* první veřejná verze

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
* Calibre min. verze 6.10.0
* plugin byl testován pouze na MacOs / Calibre

## Instalace:
1. Spusťte Calibre
1. Přejděte na „Předvolby“ -> „Moduly“ a klikněte na tlačítko „Načíst modul ze souboru“.
1. Vyhledejte soubor s pluginem (databazeknihcz-vx_x_x.zip) a klikněte na tlačítko „Instalovat“.
1. Restartujte Calibre

## Známé problémy
* stahování velkého množství metadat - především přes hromadné stažení může skončit na HTTP error 429: too many requests - zablokování vyhledávání přes google z Calibre na několik hodin

## Inspirace pro plugin:
* Calibre Metadata Source Plugin for Deutsche Nationalbibliothek (DNB) - https://github.com/citronalco/calibre-dnb
* Calibre METADATA from ComicWiki.dk - https://github.com/mickkn/calibre_metadata_comicwiki/
* Databazeknih.CZ - Daniel Prazak <kret33n@gmail.com> - https://www.mobileread.com/forums/showthread.php?t=155524
