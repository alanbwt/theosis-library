#!/usr/bin/env python3
"""
import_enoch-ethiopic.py -- 1 Enoch, complete (chapters 1-108), on the pages of an
Ethiopic manuscript, with Dillmann's Ge'ez text and R. H. Charles's English.

Chain of evidence for every section (one section = one chapter)
---------------------------------------------------------------
1. SCAN     Manchester, John Rylands Library, Ethiopic MS 23 ("Enoch, Job, and the
            Book of Kings", 18th c., 3 columns, 40 lines). 1 Enoch fills fol. 2r-16v
            (fol. 1r-1v: pen trials and a contents note; fol. 17r-17v blank; Job from
            fol. 18r), per the library's own logical structure in the IIIF manifest.
            Images: Manchester Digital Collections IIIF, MS-ETHIOPIC-00023, CC BY-NC 4.0
            ("Images made available for download are licensed under ... CC BY-NC 4.0").
            One JPEG per page (2000 px tall, the largest full-page size the server gives).
2. MAPPING  By reading the photographs. The first line of every one of the 90 text
            columns (fol. 2r col. a - fol. 16v col. c) was read on full-resolution crops
            and transcribed (COLUMN_STARTS below, the scribe's spelling as read).  Each
            reading is located in Dillmann's text by a consonant-skeleton match that
            merges the Ge'ez homophones (h/H/x, s/s', '/`, ts/tz); every match must score
            >= 0.85 and the 90 positions must run in text order.  A chapter's pages are
            then the columns between the column where it begins and the column where it
            ends.  Boundary cases were checked on the image: chapter 30 begins exactly at
            the top of fol. 4v col. c; chapter 61 begins on the last line of fol. 7v
            col. a (red section mark, then "ወርኢኩ፡ በ"); chapter 106 begins in line 1 of
            fol. 16r col. c after a red section mark; the book ends in line 4 of fol. 16v
            col. c, followed by a scribal note and a decorated band.
3. GE'EZ    August Dillmann, Liber Henoch Aethiopice (Leipzig 1851), as digitized by
            Michal Jerabek (Library of Ethiopian Texts, Prague 1995) and converted to
            Unicode by Ran HaCohen (Tel Aviv University, 2011):
            https://www.tau.ac.il/~hacohen/Henoch/Henoch%20<n>.html .  Jerabek's notice:
            free for any non-commercial purpose with the copyright notice kept.  The
            digital text has chapter divisions but no verse numbers.  It is Dillmann's
            critical text, not a transcription of Rylands MS 23.
4. ENGLISH  R. H. Charles, The Book of Enoch (Translations of Early Documents, SPCK,
            London 1917), Project Gutenberg eBook #77935 (public domain).  Where Charles
            prints the Ethiopic (E) and the Akhmim Greek (Gg) side by side (chs. 22, 27,
            32) the E column is used here.  Charles's own order is kept inside chapters;
            his transposition of 91:12-17 (printed after ch. 93) and of ch. 92 (printed
            before ch. 91) is undone by gathering each chapter's verses under its number.
            The parallel doublet columns of 90:13-18 are given in verse order.

Writes (and nothing else):
  data/sources/enoch-ethiopic/  (Dillmann HTML, Gutenberg HTML, IIIF manifest,
                                 charles_1917_chapters.json for import_akhmim-codex.py)
  site/assets/scans/enoch-ethiopic/rylands-eth23-fNNx.jpg
  translations/published/verified-enoch-ethiopic-*.json
  data/collections/enoch-ethiopic.json

Usage:
  python3 scripts/import_enoch-ethiopic.py            # build
  python3 scripts/import_enoch-ethiopic.py --mapping  # print the chapter -> column map
"""
import argparse
import difflib
import html
import io
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "enoch-ethiopic"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()
UA = "TheosisLibrary/1.0 (non-commercial research)"

MANIFEST_URL = "https://www.digitalcollections.manchester.ac.uk/iiif/MS-ETHIOPIC-00023"
VIEW_URL = "https://www.digitalcollections.manchester.ac.uk/view/MS-ETHIOPIC-00023"
DILLMANN_URL = "https://www.tau.ac.il/~hacohen/Henoch/Henoch%20{n}.html"
DILLMANN_INFO = "https://www.tau.ac.il/~hacohen/Henoch/InformationDill.html"
CHARLES_URL = "https://www.gutenberg.org/cache/epub/77935/pg77935-images.html"
CHARLES_PAGE = "https://www.gutenberg.org/ebooks/77935"

PAGES = [f"{n}{s}" for n in range(2, 17) for s in "rv"]   # fol. 2r - 16v

# First line of each text column as read on the photographs (scribe's spelling).
# fol. 2r col. a opens with a rubricated invocation and heading, then chapter 1.
COLUMN_STARTS = [
    ("2r", "b", "ወጠል፡ ወዝናም፡ የአርፍ፡ ላዕሌሃ፡ ጠየቁ፡ ወርአዩ፡ ኩ"),
    ("2r", "c", "ሕይወቶሙ፡ በሰላም፡ ወዓመታተ፡ ፍሥሓሆሙ፡ ይበዝኍ፡ በትፍሥሕት፡ ወበሰላም፡ ዘለዓለም፡"),
    ("2v", "a", "ትዩ፡ እምኔሃ፡ አሜሃ፡ ምድር፡ ስከየቶሙ፡ ለአማፅያን፡ ወአዛዝኤል፡ መሐሮሙ፡ ለሰብእ፡"),
    ("2v", "b", "ልአት፡ ኵላ፡ ምድር፡ ደመ፡ ወዓመፃ፡ ወይእዜኒ፡ ናሁ፡ ይጸርሑ፡ ነፍሳት፡ እለ፡ ሞቱ፡ ወይሰክዩ፡"),
    ("2v", "c", "እግዚአብሔር፡ ሑር፡ አይድዕ፡ ለስምያዛ፡ ወለካልአን፡ እለ፡ ምስሌሁ፡ እለ፡ ኀብሩ፡ ምስለ፡ አን"),
    ("3r", "a", "ውልድ፡ ትውልድ፡ ወእስከ፡ ለዓለም፡ ወበእማንቱ፡ መዋዕል፡ አፈትሕ፡ መዛግብተ፡ በ"),
    ("3r", "b", "መንፈስሙ፡ ወለለ፡ ዕምግባሮሙ፡ ወበእንተ፡ ዘይስዕሉ፡ ከመ፡ ይኩኖሙ፡ ሥርየት፡ ወኑኃ"),
    ("3r", "c", "ኒ፡ ወያጔጕጉኒ፡ ወነሥኡኒ፡ ለዕለ፡ ውስተ፡ ሰማይ፡ ወበእኩ፡ እስከ፡ ዕቀርብ፡ ኀበ፡ ጥቅም፡ ዘሐንጽ"),
    ("3v", "a", "አቅረበኒ፡ እስከ፡ ኆኅት፡ ወአንሰ፡ ገጽየ፡ ታሕተ፡ እኔጽር፡ ወአውሥአኒ፡ ወይቤለኒ፡"),
    ("3v", "b", "ት፡ ዲበ፡ ውሉደ፡ ሰብእ፡ ወዲበ፡ አንስት፡ እስመ፡ ወፅኡ፡ አመ፡ መዋዕለ፡ ቀትል፡ ወሙስና፡"),
    ("3v", "c", "ውሙ፡ ማዕከለ፡ ሰማይ፡ ወምድር፡ እሙንቱ፡ ውእቶሙ፡ አዕማደ፡ ሰማይ፡ ወርኢኩ፡ ነፋሳተ፡"),
    ("4r", "a", "ለሰብእ፡ ከመ፡ ይሡዑ፡ ለአጋንንት፡ ከመ፡ አማ"),
    ("4r", "b", "ነጸርኩ፡ ወስእንኩ፡ ነጽሮ፡ ዓይኑ፡ ውእቱ፡ ጊዜ፡"),
    ("4r", "c", "ንኔ፡ ኢኮነ፡ በላዕሌሆሙ፡ በሕይወቶሙ፡ ወበዝየ፡ ይትፈለጣ፡ ነፍሳቲሆሙ፡ ዲበ፡ ዛቲ፡ ዐባይ፡"),
    ("4v", "a", "ሁ፡ ኢኮነ፡ ዘይምዕዝ፡ እምኵሉ፡ መዓዛ፡ ወቈጽሉ፡ ወጽጌሁ፡ ወዕፁ፡ ኢይጸመሂ፡ ለዓለም፡"),
    ("4v", "b", "ጽባሕ፡ ካልአ፡ ደብረ፡ ዘይነውኅ፡ ከመዝ፡ ወማዕከሎሙ፡ ቈላ፡ ዕሙቀ፡ ወአልቦ፡"),
    ("4v", "c", "ወላዕሌሁ፡ ላዕለ፡ እሎንቱ፡ ላዕለ፡ ደብረ፡ ጽባሕ፡"),
    ("5r", "a", "ፍሂ፡ ይትዌለጥ፡ ገጾሙ፡ ወስሞሙ፡ ወቃሎሙ፡"),
    ("5r", "b", "ኃይሉ፡ ወይሴብሕዎ፡ ለግብረ፡ እደዊሁ፡ ዐቢይ፡ ወይባርክዎ፡ እስከ፡ ለዓለም፡ ራእይ፡ ዘ"),
    ("5r", "c", "ፍት፡ ቅንዓት፡ ወመዓት፡ ወመጽሐፍት፡ ጕጕአ፡ ወሀውክ፡ ወምሕረት፡ ኢይከውን፡ ላዕሌሆሙ፡"),
    ("5v", "a", "ወበህየ፡ ርእያ፡ አዕይንትየ፡ ኵሎሙ፡ እለ፡ ኢይነውሙ፡ ይቀውሙ፡ ቅድሜሁ፡ ወይባርኩ፡ ወይብሉ፡"),
    ("5v", "b", "ሰን፡ ወርእያ፡ አዕይንትየ፡ በህየ፡ ኵሎሙ፡ ኃጥአን፡ እንዘ፡ ይሰደዱ፡ እምህየ፡ እለ፡ ይክህድዎ፡"),
    ("5v", "c", "ያት፡ ወዕለት፡ ጥበብ፡ ከመ፡ ትኅድር፡ ውስተ፡ ውሉደ፡ ሰብእ፡ ወኢረከበት፡ ማኅደረ፡"),
    ("6r", "a", "በሰላም፡ ለጻድቃንየ፡ ወአነ፡ በርክሙ፡ ቅድሜየ፡ ወቀርበት፡ ኀቤየ፡ ኵነኔየ፡ ለኃጥአን፡ ከመ፡"),
    ("6r", "b", "የኃ፡ ሩ፡ ቅዱሳን፡ እለ፡ ይነብሩ፡ መልዕልተ፡ ሰማያት፡ በ፩ቃል፡ ወያስተበቍዑ፡ ወይጼልዩ፡ ወ"),
    ("6r", "c", "ወቶሙ፡ ወበውእቱ፡ መዋዕል፡ ኮኑ፡ ትሑታነ፡ ገጽ፡ ነገሥተ፡ ምድር፡ ወጽኑዓን፡ እለ፡ ይእኅዝዋ፡ ለየ"),
    ("6v", "a", "ንታ፡ ወሲአል፡ ታገብእ፡ ማኅፀንታ፡ ዘተመጠወት፡ ወሲኦል፡ ያገብእ፡ ዘይፈደይ፡ ወየኀሪ፡ ጻድቃነ፡ ወቅ"),
    ("6v", "b", "ትኃለቍ፡ ወዓረር፡ ኢይትፈቀድ፡ እሉ፡ ኵሎሙ፡ ይትከሐዱ፡ ወይትኀጐሉ፡ ሀለዉ፡ እምገጸ፡"),
    ("6v", "c", "ወውስተ፡ ዕቶን፡ እሳት፡ ዘይነድድ፡ ይወድይዎሙ፡ ወእተ፡ ዕለተ፡ ከመ፡ ይትበቀል፡ እምኔሆሙ፡"),
    ("7r", "a", "ውእቱ፡ ቈላ፡ እምነ፡ ኃሩያን፡ ወፍቁራን፡ ዚአሆሙ፡ ወይትዌዳዕ፡ ዕለተ፡ ሕይወቶሙ፡ ወዕለተ፡ ስሕተ"),
    ("7r", "b", "ወእምድኅረዝ፡ ይትበሀል፡ ለቅዱሳን፡ ከመ፡ ይኅሥሡ፡ በሰማያት፡ ኀቡአተ፡ ጽድቅ"),
    ("7r", "c", "ጽእ፡ ዕለት፡ ወኃይል፡ ወመቅሠፍት፡ ወኵነኔ፡ እንተ፡ አስተዳለወ፡ እግዚአ፡ መናፍስት፡ ለእለ፡"),
    ("7v", "a", "ዙ፡ ወይትመየጡ፡ በኃይለ፡ መንፈስ፡ ወይትነዳዕ፡ ከመዝ፡ በኀ መ፡ ብዝኃ፡ አድዋለ፡ ምድር፡ ወ"),
    ("7v", "b", "እማንቱ፡ መዋዕል፡ ተውህበ፡ ለእልኩ፡ መላእክት፡ አኃብል፡ነዊኃን፡ ወነሥኡ፡ ሎሙ፡ ክንፈ፡"),
    ("7v", "c", "በመንፈስ፡ ምሕረት፡ ወበመንፈሰ፡ ኵነኔ፡ ወሰላም፡ ወበመንፈሰ፡ ኂሩት፡ ወይብሉ፡ ኵሎሙ፡ በ፩"),
    ("8r", "a", "ድሜሁ፡ ኵሎሙ፡ ኅሩያን፡ በይእቲ፡ ዕለት፡ ወይወድቁ፡ ኵሎሙ፡ ነገሥት፡ አዚዛን፡ ወልዑላን፡ ወእ"),
    ("8r", "b", "ሀበነ፡ ዕረፍተ፡ ከመ፡ ንሰብሕ፡ ወናዕኵቶ፡ ወንባርኮ፡ ወንእመን፡ ቅድመ፡ ስብሐቲሁ፡ ወይእዜኒ፡"),
    ("8r", "c", "አ፡ እምኀበ፡ ገጸ፡ እግዚእ፡ ዲበ፡ እለ፡ የኀድሩ፡ ውስተ፡ የብስ፡ ከመ፡ ውእቱ፡ ይኩን፡ ኅልቀቶሙ፡ እስመ፡ አ"),
    ("8v", "a", "ወአዓቅብ፡ ወትከውን፡ እምኔሃ፡ ዘርአ፡ ሕይወት፡ ወትውላጥ፡ ይበእ፡ ከመ፡ ኢይንበር፡ የብስ፡ ዕራቆ፡"),
    ("8v", "b", "ለሞት፡ ሥጋሆሙ፡ ወኢይሬእዩ፡ ወኢየአምኑ፡ ከመ፡ ይትመየጡ፡ እሙንቱ፡ ማያት፡ ወይከውኑ፡"),
    ("8v", "c", "ወመኰንን፡ ዚአሆሙ፡ ወመኰንን፡ ዚአሆሙ፡ ስሙ፡ ለቀዳማዊ፡ ይቁን፡ ወዝንቱ፡ ዘአስሐ"),
    ("9r", "a", "ወአንበሮ፡ ለዝ፡ መሐላ፡ አካዕ፡ በእዴሁ፡ ለቅዱስ፡ ሚካኤል፡ ወእሉ፡ እሙንቱ፡ ኅቡአቲሁ፡ ለዝ፡"),
    ("9r", "b", "እቱ፡ ወልደ፡ ብእሲ፡ ተርእየ፡ ወነበረ፡ ዲበ፡ መንበረ፡ ስብሐቲሁ፡ ወኵሉ፡ እኩይ፡ እምቅድመ፡ ገጹ፡"),
    ("9r", "c", "ትእላፋት፡ የዓውድዎ፡ ለውእቱ፡ ቤት፡ ወሚካኤል፡ ወሩፋኤል፡ ወገብርኤል፡ ወፋኑኤል፡ ወመላእክት፡"),
    ("9v", "a", "ብርሃን፡ ሙፃአ፡ በኃዋኅው፡ ሰማይ፡ እለ፡ መንገለ፡ ጽባሕ፡ ወምዕራቢሁ፡ በኃዋኅው፡ ሰማይ፡ ዘምዕራብ፡"),
    ("9v", "b", "ለት፡ ትነውኅ፡ ዕለት፡ እምሌሊት፡ ወትከውን፡ ዕለት፡ ከዕበተ፡ ሌሊት፡ ወትከውን፡ ዕለት፡"),
    ("9v", "c", "ወትከውን፡ ከዕበተ፡ ለመዓልት፡ ወትከውን፡ ሌሊት፡ ወ፲ክፍለ፡ ጥንቁቀ፡ ወመዓልት፡"),
    ("10r", "a", "ፀሐይ፡ ወሰበ፡ ይሬኢ፡ ከዊነ፡ ብርሃኑ፡ ይከውን፡"),
    ("10r", "b", "ወይፌጽም፡ ኵሎ፡ ብርሃኖ፡ ወይጸንን፡ ወይበው"),
    ("10r", "c", "መንበረ፡ ዓለም፡ እስመ፡ ለትእምርት፡ ወለአዝ"),
    ("10v", "a", "አ፡ ቀዳማይ፡ ነፋስ፡ እምእልኩ፡ ኃዋኅው፡ ዘስሙ፡ ጽባሐይ፡ በቀዳሚት፡ ኆኅት፡ እንተ፡ መንገለ፡ ጽባ"),
    ("10v", "b", "ዘስሙ፡ መስዕ፡ ይትከፈል፡ ክፍለ፡ እምኔሆሙ፡ ማኅደር፡ ለሰብእ፡ ወካልእ፡ ለአብሕርተ፡ ማያት፡ ወ"),
    ("10v", "c", "ክፍለ፡ ወበታስእ፡ የሐፅፅ፡ ክፍለ፡ ወበዓሥር፡ የሐፅፅ፡ ምስተ፡ ክፍለ፡ ወበ፲ወ፩የሐፅፅ፡"),
    ("11r", "a", "ርእስ፡ ወርኅ፡ ወታሕፃጺት፡ ዘይትገበር፡ በኆኅት፡ ቀዳሚት፡ በዘመኑ፡ ዚአሁ፡ እስከ፡ ይትፌጸም፡"),
    ("11r", "b", "ወአንበብክዎ፡ ለመጽሐፍ፡ ወኵሎ፡ ዘጽሑፍ፡ ውስቴታ፡ ኵሎ፡ ምግባሮሙ፡ ለሰብእ፡ ወኵ"),
    ("11r", "c", "ሎሙ፡ ብፁዓን፡ ኵሎሙ፡ እለ፡ የሐውሩ፡ በፍኖተ፡ ጽድቅ፡ ወአልቦሙ፡ ኃጢአተ፡ ከመ፡ ኃጥ"),
    ("11v", "a", "ለ፡ ሥሩዓን፡ ምልክኤል፡ ወህልአምሜሌክ፡ ወሜልኤየል፡ ወናሬል፡ ወአስማቲሆሙ፡ ለእለ፡"),
    ("11v", "b", "ም፡ ለእግዚእ፡ ስኩበ፡ ኮንኩ፡ በቤተ፡ መላልኤል፡ እምሔውየ፡ ርኢኩ፡ በራእይ፡ ሰማይ፡ ይትነጸሕ፡ ወይት"),
    ("11v", "c", "ወለኵሉ፡ ትውልደ፡ ትውልድ፡ ሥልጣንከ፡ ወኵሎሙ፡ ሰማያት፡ መንበርከ፡ ለዓለም፡ ወኵላ፡ ምድ"),
    ("12r", "a", "አርመማ፡ እምይእቲ፡ ጊዜ፡ ኢጸርሐት፡ ወእምድኅረዝ፡ ወለደት፡ ካልአ፡ ላህመ፡ ፀዓዳ፡ ወእም"),
    ("12r", "b", "ደ፡ ምድር፡ ወዓልአሉኒ፡ ዲበ፡ መካን፡ ነዋኅ፡ ወአርአዩኒ፡ ማኅፈደ፡ ነዋኃ፡ እምድር፡ ወኮነ፡ ሕፁ"),
    ("12r", "c", "ጕሉ፡ በውእቱ፡ ማይ፡ ወሙስቱ፡ መስቀር፡ ይጸቢ፡ ዲበ፡ ማይ፡ ወኵሎሙ፡ አልህምት፡ ወነጌ"),
    ("12v", "a", "ጠቅምሙ፡ እስከ፡ ያሐልቁ፡ ደቂቆሙ፡ ወገደፉ፡ ደቂቆሙ፡ በውሒዘ፡ ማይ፡ ብዙኅ፡ ወእልኩ፡ አባግዕ፡ ወጠኑ፡ ይጽርሑ፡ በእንተ፡ ደቂቆሙ፡"),
    ("12v", "b", "ለአባግዕ፡ ወሮጹ፡ ድኅሬሆሙ፡ እልኩ፡ አዝዕብት፡ በዝኩ፡ አይገ፡ ማይ፡ ወሰበ፡ ርእይዎ፡ ለእግዚኦሙ፡"),
    ("12v", "c", "ዕ፡ አቀምሙ፡ በውእቱ፡ ቤት፡ ወርኢኩ፡ እስከ፡ ሰከበ፡ ውእቱ፡ በግዕ፡ ዘተራከበ፡ ለዝኩ፡ በግዕ፡"),
    ("13r", "a", "ይኃራዊ፡ ተንሥአ፡ ወመርሐሙ፡ ለአባግዕ፡ ንዑሳን፡ ወዝኩ፡ ሐርጌ፡ ወለደ፡ አባግዐ፡ ብዙኃን፡"),
    ("13r", "b", "ዎሙ፡ ውስተ፡ እደዊሆሙ፡ ለኵሎሙ፡ አራዊት፡ ወአነ፡ አኃዝኩ፡ እጽራኅ፡ በኵሉ፡ ኃይልየ፡ ወእጸው"),
    ("13r", "c", "ለእልኩ፡ አባግዕ፡ ለእመ፡ ይበውኡ፡ ኀበ፡ ዝኩ፡ ቤት፡ ወኖላውያን፡ ወጸማድሙ፡ መጠውዎሙ፡ ለእለ"),
    ("13v", "a", "ቀዳማዊያን፡ ወበዕደን፡ ተመጠውምሙ፡ ውስተ፡ እደዊሆሙ፡ ከመ፡ ይርአይዎሙ፡ በበጊዜሆሙ፡"),
    ("13v", "b", "ለቁዓት፡ ከመ፡ ይቀጥቅጥዎ፡ ለቀርኑ፡ ዝኩ፡ ደቤላ፡ ወተበአሱ፡ ምስሌሁ፡ ወተቃተሉ፡ ወውእቱ፡"),
    ("13v", "c", "ዘአዝከርምሙ፡ እሙንቱ፡ ወናሁ፡ ኵሎሙ፡ እሡራን፡ ርኢኩ፡ ወቆሙ፡ ቅድሜሁ፡ ኵሎሙ፡ ወኵነኔ፡ ከ"),
    ("14r", "a", "ብእዎ፡ ውስተ፡ ቤቱ፡ ወኃተማ፡ ቅድመ፡ ገጹ፡ ለእግዚእ፡ ወኵሎሙ፡ አባግዕ፡ ተዓፀው፡ በውእቱ፡ ቤ"),
    ("14r", "b", "ዋት፡ ኄራት፡ ወጽድቅ፡ ይከውን፡ ለክሙ፡ ሱታፌ፡ እስመ፡ አአምር፡ ከመ፡ ይጸንዕ፡ ኃላዌ፡ ግፍዕ፡"),
    ("14r", "c", "ወኵሉ፡ ኃይላተ፡ ሰማያት፡ ያበርሁ፡ ለዓለም፡ ምክዕቤተ፡ ወእምድኅረዝ፡ ሰንበታት፡ ብዙኃት፡ እለ፡"),
    ("14v", "a", "እምድኅረዝ፡ በሣልስት፡ ሰንበት፡ በተፍጻሜታ፡ ይትኃረይ፡ ብእሲ፡ ለተክለ፡ ኵነኔ፡ ጽድቅ፡"),
    ("14v", "b", "ዎሙ፡ ወይእዜኒ፡ ለክሙ፡ እብል፡ ለጻድቃን፡ ኢተሐውሩ፡ በፍኖት፡ እኩይ፡ ወግፍዕ፡ ወኢበፍናዋተ፡"),
    ("14v", "c", "ሙዋ፡ ለዓመፃ፡ እስመ፡ ፍጡነ፡ ትትኃጐሉ፡ አሌ፡ ለክሙ፡ ኃጥአን፡ እስመ፡ ለጻድቃን፡ ትሰድድዎ"),
    ("15r", "a", "ሱታፌነ፡ ኮንክሙ፡ ለኃጥአን፡ ወበእማንቱ፡ መዋዕል፡ ትበጽሕ፡ ጸሎቶሙ፡ ለቅዱሳን፡ ኀበ፡ እግዚአብሔር፡"),
    ("15r", "b", "ዩ፡ ኵሉ፡ ኃጢአት፡ በሰማይ፡ ይጸሐፍ፡ ሀሎ፡ በኵሉ፡ ዕለት፡ በቅድሜሁ፡ ለልዑል፡ እምይእዜ፡ ተአም"),
    ("15r", "c", "ቱ፡ መዋዕል፡ ይትሀወኩ፡ አሕዛብ፡ ወይትነሥኡ፡ አዝማደ፡ አሕዛብ፡ በዕለት፡ እንተ፡ ኃጕል፡ ወበ"),
    ("15v", "a", "ስለ፡ ውሉዶሙ፡ ይትኃደጉ፡ ወአኃው፡ ምስለ፡ ቢጾሙ፡ ይወድቁ፡ በሞት፡ እስከ፡ ይውኅዝ፡ ከመ፡ ተከዚ፡"),
    ("15v", "b", "ወጠል፡ እመ፡ ተመጠወ፡ እምኔክሙ፡ ወርቀ፡ ወብሩረ፡ ከመ፡ ይረድ፡ ሶበ፡ ይወድቅ፡ ዲቤክሙ፡"),
    ("15v", "c", "እምቅድመ፡ ዓቢየ፡ ስብሐት፡ ወርዕዱ፡ ደቂቀ፡ ምድር፡ ወይትሀወኩ፡ ወአንትሙ፡ ኃጥአን፡ ርጉማ"),
    ("16r", "a", "ወይብሉ፡ እለ፡ እለ፡ ክማክሙ፡ ዲቤክሙ፡ ብፁዓን፡ እሙንቱ፡ ኃጥአን፡ ኵሎሙ፡ መዋዕ"),
    ("16r", "b", "ተ፡ ሰማይ፡ ወትትረአዩ፡ ወኆኃተ፡ ሰማይ፡ ይትረኃው፡ ለክሙ፡ ወጽራኃ፡ ዚአክሙ፡ ኵነኔ፡ ጸርሑ፡ ወያስተርኢ፡ ለክሙ፡"),
    ("16r", "c", "ሑ፡ ውሉደ፡ ርትዕ፡ በአማን፡ ወእምድኅረ፡ መዋዕል፡ ነሥአ፡ ወልድየ፡ ማቱሳላ፡ ወልዱ፡ ለሜክ፡"),
    ("16v", "a", "ይገብሩ፡ ኃጢአተ፡ ወየኃልፉ፡ ሥርዓተ፡ ወምስለ፡ አንስት፡ ተደመሩ፡ ወምስሌሆን፡ ይገብሩ፡ ኃጢአተ፡"),
    ("16v", "b", "ይትቀተሉ፡ ወይጸርሑ፡ ወየአወዩ፡ በመካን፡ በድው፡ ዘኢያስተርኢ፡ ወበእሳት፡ ነዱ፡ እስመ፡ ኢሀሎ፡ ህየ፡ ምድር፡"),
    ("16v", "c", "ይትወደዩ፡ በጽልመት፡ እንዘ፡ ይትወሀውሁ፡ ጽድቃን፡ ወይጸርሑ፡ ወይሬእይዎሙ፡ ኃጥአን፡"),
]
FIRST_COLUMN = ("2r", "a", "rubricated invocation ‹በስመ፡ እግዚአብሔር፡ መሐሪ፡ ወመስተሣህል፡› and heading ‹እጽሕፍ፡ አንስ፡ መጽሐፈ፡ ሄኖክ፡ ነቢይ› (red), then chapter 1")

# Observations made on the image at chapter boundaries (recorded in scan_note).
BOUNDARY_NOTES = {
    15: "In line 2 of fol. 3v col. a a red section mark stands before ‹ወአውሥአኒ፡ ወይቤለኒ› (15:1).",
    30: "Chapter 30 begins exactly at the top of fol. 4v col. c (‹ወላዕሌሁ፡ ላዕለ፡ እሎንቱ፡ ላዕለ፡ ደብረ፡ ጽባሕ›).",
    61: "Chapter 61 begins in the last line of fol. 7v col. a: ‹ሕረቱ፡ ወበትዕግሥቱ፡› (end of 60:25), a red section mark, then ‹ወርኢኩ፡ በ›.",
    106: "Chapter 106 begins in line 1 of fol. 16r col. c: ‹ሑ፡ ውሉደ፡ ርትዕ፡ በአማን፡› (end of 105:2), a red section mark, then ‹ወእምድኅረ፡ መዋዕል፡ ነሥአ፡ ወልድየ፡ ማቱሳላ›.",
    108: "The book ends in line 4 of fol. 16v col. c (‹... በኀበ፡ ተጽሕፈ፡ ሎሙ፡ መዋዕል፡ ወአዝማን›), followed by a one-line scribal note and a decorated band.",
}

BOOKS = [
    {"slug": "watchers", "chapters": (1, 36), "order": 1,
     "title": "1 Enoch 1-36: The Book of the Watchers (Ethiopic)",
     "date_approx": "c. 3rd century BC (composition); Ethiopic copy 18th c. (Rylands Ethiopic MS 23)",
     "century": -3,
     "themes": ["watchers", "nephilim", "giants", "fallen-angels", "azazel", "sheol", "heavenly-journey"],
     "intro": "<p>The Book of the Watchers is the oldest part of 1 Enoch. After a prophecy of judgement (chapters 1-5) it tells how the Watchers, angels led by Semjaza and Azazel, came down in the days of Jared, took wives from the daughters of men and fathered the giants, and taught mankind metalwork, cosmetics, sorcery and astrology (chapters 6-11; compare Genesis 6:1-4). Enoch is asked to intercede for the Watchers, sees God's throne in a vision (chapter 14) and is told their sentence (chapters 15-16). Chapters 17-36 describe his journeys with the archangels to the ends of the earth, the prisons of the fallen angels, the hollow places where the souls of the dead wait for judgement (chapter 22) and the tree of life. Aramaic fragments of this book were found at Qumran, and Jude 14-15 quotes 1:9.</p>"},
    {"slug": "parables", "chapters": (37, 71), "order": 2,
     "title": "1 Enoch 37-71: The Book of Parables (Ethiopic)",
     "date_approx": "c. 1st century BC to 1st century AD (composition); Ethiopic copy 18th c. (Rylands Ethiopic MS 23)",
     "century": -1,
     "themes": ["son-of-man", "elect-one", "messiah", "judgement", "parables", "similitudes"],
     "intro": "<p>The Book of Parables (also called the Similitudes) contains three parables or visions of the coming judgement. Its central figure is a heavenly judge called the Elect One, the Righteous One and the Son of Man, who sits on the throne of glory and judges kings and the mighty (chapters 46-51, 61-62, 69). Chapters 65-69 contain Noah material, and chapters 70-71 tell of Enoch's final ascent. No fragment of this book was found at Qumran; it survives complete only in Ethiopic.</p>"},
    {"slug": "luminaries", "chapters": (72, 82), "order": 3,
     "title": "1 Enoch 72-82: The Astronomical Book (Ethiopic)",
     "date_approx": "c. 3rd century BC (composition); Ethiopic copy 18th c. (Rylands Ethiopic MS 23)",
     "century": -3,
     "themes": ["astronomy", "calendar", "364-day-year", "uriel", "luminaries"],
     "intro": "<p>The Astronomical Book, or Book of the Heavenly Luminaries, records what the angel Uriel showed Enoch about the sun, moon, stars and winds: the portals through which the sun and moon rise and set, the waxing and waning of the moon, and a year of 364 days (chapters 72-82). Aramaic copies of a longer form of this book were found at Qumran.</p>"},
    {"slug": "dream-visions", "chapters": (83, 90), "order": 4,
     "title": "1 Enoch 83-90: The Book of Dream Visions (Ethiopic)",
     "date_approx": "c. 165-160 BC (composition); Ethiopic copy 18th c. (Rylands Ethiopic MS 23)",
     "century": -2,
     "themes": ["animal-apocalypse", "flood", "history-of-israel", "seventy-shepherds", "maccabees"],
     "intro": "<p>The Book of Dream Visions contains two dreams that Enoch tells his son Methuselah. The first (chapters 83-84) foresees the Flood. The second, the Animal Apocalypse (chapters 85-90), retells the history of the world from Adam to the Maccabean revolt with people drawn as animals: the patriarchs and Israel as bulls and sheep, the nations as wild beasts and birds, the fallen angels as stars, and seventy shepherds who rule over the sheep. It ends with the judgement, a new house and a white bull. The reference to the Maccabean wars dates it to the 160s BC.</p>"},
    {"slug": "epistle", "chapters": (91, 108), "order": 5,
     "title": "1 Enoch 91-108: The Epistle of Enoch, the Birth of Noah and the Last Book (Ethiopic)",
     "date_approx": "c. 2nd century BC (composition of chs. 91-105); Ethiopic copy 18th c. (Rylands Ethiopic MS 23)",
     "century": -2,
     "themes": ["epistle-of-enoch", "apocalypse-of-weeks", "woes", "birth-of-noah", "righteous-and-sinners"],
     "intro": "<p>The last part of 1 Enoch begins with Enoch's admonition to his children (chapters 91-92) and the Apocalypse of Weeks, which divides history into ten weeks (93:1-10 with 91:11-17). Chapters 94-105, the Epistle of Enoch, set woes against the sinners and the rich beside promises to the righteous. Chapters 106-107 tell of the wondrous birth of Noah, and chapter 108 is a separate closing book. Parts of the Epistle survive in Aramaic from Qumran and in a Greek papyrus (Chester Beatty-Michigan).</p>"},
]



# ---------------------------------------------------------------------------
# HTTP + sources
# ---------------------------------------------------------------------------
def fetch(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:  # noqa
            if k == tries - 1:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(3 * (k + 1))


def cached(path, url):
    if not path.exists() or path.stat().st_size < 200:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(fetch(url))
    return path


def manifest():
    return json.loads(cached(SRC / "manchester_ethiopic23_manifest.json", MANIFEST_URL).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Dillmann Ge'ez
# ---------------------------------------------------------------------------
def dillmann_chapter(n):
    t = cached(SRC / "dillmann" / f"henoch_{n}.html", DILLMANN_URL.format(n=n)).read_text(encoding="utf-8")
    m = re.search(r"<!--Cap\.-->\s*(\d+)\s*<!--Cap\.end -->\s*</a>(.*?)</p>", t, re.S)
    assert m and int(m.group(1)) == n, n
    body = html.unescape(m.group(2)).replace(" ", "")
    body = re.sub(r"<[^>]+>", "", body)
    return re.sub(r"\s+", " ", body).strip()


def corpus():
    chs = {n: dillmann_chapter(n) for n in range(1, 109)}
    full, starts = "", {}
    for n in range(1, 109):
        starts[n] = len(full)
        full += chs[n] + " "
    return chs, full, starts


# consonant skeleton: drop vowels, merge the homophone series
_MERGE = {(0x1210 - 0x1200) // 8: 0, (0x1280 - 0x1200) // 8: 0, (0x1288 - 0x1200) // 8: 0,
          (0x1220 - 0x1200) // 8: (0x1230 - 0x1200) // 8,
          (0x12D0 - 0x1200) // 8: (0x12A0 - 0x1200) // 8,
          (0x1340 - 0x1200) // 8: (0x1338 - 0x1200) // 8}


def _base(c):
    cp = ord(c)
    if 0x1200 <= cp <= 0x1357:
        b = (cp - 0x1200) // 8
        return chr(0xE000 + _MERGE.get(b, b))
    return ""


def locate(query, skel, idx):
    q = "".join(_base(c) for c in query)
    L = len(q)
    scored = []
    for i in range(0, len(skel) - L + 1):
        w = skel[i:i + L]
        if sum(a == b for a, b in zip(w, q)) < L * 0.3:
            continue
        scored.append((difflib.SequenceMatcher(None, w, q, autojunk=False).ratio(), i))
    scored.sort(reverse=True)
    best = scored[0]
    second = next((s for s in scored[1:] if abs(s[1] - best[1]) >= L), (0, 0))
    return best[0], second[0], idx[best[1]]


def column_map(full, starts):
    skel, idx = [], []
    for i, c in enumerate(full):
        b = _base(c)
        if b:
            skel.append(b)
            idx.append(i)
    skel = "".join(skel)
    cols = [dict(page=FIRST_COLUMN[0], col=FIRST_COLUMN[1], pos=0, reading=FIRST_COLUMN[2], score=1.0)]
    for pg, col, q in COLUMN_STARTS:
        sc, sc2, pos = locate(q, skel, idx)
        # clear winner; in the formulaic lunar tables (ch. 78) the runner-up is the
        # neighbouring formula, so a smaller margin is accepted when the score is high
        assert sc >= 0.85 and (sc - sc2 >= 0.2 or (sc >= 0.9 and sc - sc2 >= 0.1)), (pg, col, sc, sc2)
        cols.append(dict(page=pg, col=col, pos=pos, reading=q, score=round(sc, 3)))
    for a, b in zip(cols, cols[1:]):
        assert a["pos"] < b["pos"], (a, b)
    assert [c["page"] + c["col"] for c in cols] == [p + c for p in PAGES for c in "abc"]
    for k, c in enumerate(cols):
        c["end"] = cols[k + 1]["pos"] if k + 1 < len(cols) else len(full)
        c["chapter"] = max(n for n, s in starts.items() if s <= c["pos"])
    return cols


def chapter_columns(n, cols, starts, full):
    s = starts[n]
    e = starts[n + 1] if n < 108 else len(full)
    return [c for c in cols if c["pos"] < e and c["end"] > s]


# ---------------------------------------------------------------------------
# Charles 1917 English
# ---------------------------------------------------------------------------
ROMAN={'I':1,'V':5,'X':10,'L':50,'C':100}
def roman(s):
    s=s.strip().rstrip('.')
    if not re.fullmatch(r'[CLXVI]+',s): return None
    t=0
    for i,ch in enumerate(s):
        v=ROMAN[ch]; n=ROMAN[s[i+1]] if i+1<len(s) else 0
        t+= -v if v<n else v
    return t

def chapter_abbr(el):
    if not (isinstance(el,Tag) and el.name=='abbr'): return None
    title=el.get('title','')
    if not title or 'through' in title or ' to ' in title or title in ('pages','number'): return None
    return roman(el.get_text())

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def inline(nodes):
    out=[]
    for el in nodes:
        if isinstance(el,NavigableString):
            out.append(esc(str(el))); continue
        if el.name=='span' and 'pageno' in (el.get('class') or []): continue
        if el.name=='a' and el.find('sup'): continue
        n=chapter_abbr(el)
        if n: out.append(f'\x00CH{n}\x00'); continue
        if el.name in ('b','i','em','strong'):
            inner=inline(el.children)
            out.append(inner if re.fullmatch(r'\s*([a-z]\.|i\. e\.|e\. g\.)\s*',inner) else f'<em>{inner}</em>'); continue
        out.append(inline(el.children))
    return ''.join(out)

def clean(h):
    h=re.sub(r'\s+',' ',h).strip()
    return h

def stream_items(path):
    s=BeautifulSoup(open(path,encoding='utf-8').read(),'lxml')
    start=[h for h in s.find_all('h2') if 'THE BOOK OF ENOCH' in h.get_text() and 'I-XXXVI' in h.get_text()][0]
    items=[]; mode=None
    for el in start.find_all_next(['p','h2','h3','h4','div']):
        if el.name=='p' and 'Printed in Great Britain' in el.get_text(): break
        cls=el.get('class') or []
        if el.name in ('h2','h3','h4'):
            items.append(('head',None,re.sub(r'\s+',' ',el.get_text()).strip())); mode=None; continue
        if el.name=='div':
            if any(c.startswith('lg-container') for c in cls):
                rows=[]
                for g in el.find_all('div',class_='group'):
                    for l in g.find_all('div',class_='line'):
                        rows.append(clean(inline(l.children)))
                    rows.append(None)
                items.append(('lines',mode,rows))
            continue
        if el.name=='p':
            if el.find_parent('div',class_=re.compile(r'lg-container')): continue
            txt=re.sub(r'\s+','',''.join(t for t in el.find_all(string=True) if not (t.parent.name=='span' and 'pageno' in (t.parent.get('class') or []))))
            if txt in ('E','Gg'):
                mode='E' if txt=='E' else 'G'; continue
            if not ('c018' in cls or 'c019' in cls): mode=None
            items.append(('p',mode,clean(inline(el.children))))
    return items

VERSE=re.compile(r'(^|(?<=[\s\[(⌜〚]))(\d{1,2})((?:\s?[a-z])?)\.(?=\s)')
LETTER=re.compile(r'^([a-z])\.(?=\s)')
def sup(h):
    h=VERSE.sub(lambda m: f'{m.group(1)}<sup>{m.group(2)}{m.group(3).strip()}</sup>', h)
    return h

def build(path):
    items=stream_items(path)
    ch={}
    cur=0
    def put(mode,html):
        if cur==0 or not html.strip(): return
        d=ch.setdefault(cur,{'E':[],'G':[]})
        if mode in (None,'E'): d['E'].append(html)
        if mode in (None,'G'): d['G'].append(html)
    for kind,mode,obj in items:
        if kind=='head':
            m=re.match(r'^([CLXVI]+)\.\s+(\d|[A-Z][a-z])',obj)
            if m: cur=roman(m.group(1))
            continue
        if kind=='p':
            parts=re.split(r'\x00CH(\d+)\x00',obj)
            # parts: text, n, text, n, text...
            pre=parts[0].strip()
            assert len(parts)==1 or re.fullmatch(r'[\[(⌜〚]?',pre), ('marker mid-paragraph', obj[:120])
            if len(parts)==1:
                put(mode,'<p>'+sup(obj)+'</p>')
            else:
                for i in range(1,len(parts),2):
                    cur=int(parts[i]); body=parts[i+1].strip()
                    body=re.sub(r'^\.\s*','',body)
                    if i==1 and pre: body=pre+body
                    put(mode,'<p>'+sup(body)+'</p>')
            continue
        if kind=='lines':
            buf=[]
            def flush():
                lines=list(buf); buf.clear()
                while lines and lines[-1] is None: lines.pop()
                if not lines: return
                html='<br>'.join(sup(LETTER.sub(r'<sup>\1</sup>',l)) if l is not None else '' for l in lines)
                html=re.sub(r'(<br>){3,}','<br><br>',html)
                put(mode,'<p>'+html+'</p>')
            for row in obj:
                if row is not None and '\x00CH' in row:
                    m=re.match(r'^\x00CH(\d+)\x00\.?\s*(.*)$',row)
                    assert m, ('marker mid-line',row)
                    flush(); cur=int(m.group(1)); row=m.group(2)
                buf.append(row)
            flush()
    return ch


SUP=re.compile(r'<sup>(\d+)([a-z]?)</sup>')
def fix_false_verses(html):
    mx=0; out=[]; last=0
    for m in SUP.finditer(html):
        n=int(m.group(1))
        out.append(html[last:m.start()])
        if mx and n>mx+8:
            out.append(f'{n}.')   # restore the number as printed (not a verse number)
        else:
            out.append(m.group(0)); mx=max(mx,n)
        last=m.end()
    out.append(html[last:])
    return ''.join(out)

def chapters(path):
    ch=build(path)
    res={}
    for n,d in ch.items():
        res[n]={}
        for k in ('E','G'):
            paras=list(d[k])
            if n==90:
                idx=[i for i,p in enumerate(paras) if re.match(r'<p><sup>(1[3-9])</sup>',p)]
                assert idx==list(range(idx[0],idx[0]+7)), idx
                block=sorted((paras[i] for i in idx), key=lambda p:int(re.match(r'<p><sup>(\d+)',p).group(1)))
                paras[idx[0]:idx[0]+7]=block
            res[n][k]=fix_false_verses('\n'.join(paras))
    return res


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def scan_name(page):
    return f"rylands-eth23-f{int(page[:-1]):02d}{page[-1]}.jpg"


def get_scans(man, force=False):
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    canv = {c["label"]: c for c in man["sequences"][0]["canvases"]}
    for p in PAGES:
        path = SCAN_DIR / scan_name(p)
        if path.exists() and not force:
            continue
        svc = canv[p]["images"][0]["resource"]["service"]["@id"]
        im = Image.open(io.BytesIO(fetch(f"{svc}/full/,2000/0/default.jpg"))).convert("RGB")
        im.save(path, quality=85)
        print(f"  {path.name} {im.size}")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def colname(c):
    return f"fol. {c['page']} col. {c['col']}"


def geez_html(text):
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\s*።\s*", " ።<br>", t).strip()
    t = re.sub(r"(<br>)+$", "", t)
    return f"<p>{t}</p>"


def scan_note(n, ccols, cols):
    first, last = ccols[0], ccols[-1]
    k_last = cols.index(last)
    nxt = cols[k_last + 1] if k_last + 1 < len(cols) else None
    span = colname(first) if first is last else f"{colname(first)} to {colname(last)}"
    parts = [f"Rylands Ethiopic MS 23, {span}."]
    if first["page"] == "2r" and first["col"] == "a":
        parts.append("Fol. 2r col. a opens with a " + FIRST_COLUMN[2] + ".")
    else:
        parts.append(f"Checked on the photograph: {colname(first)} opens with ‹{first['reading']}› "
                     f"(Dillmann ch. {first['chapter']}), so chapter {n} begins in this column.")
    if nxt is not None:
        parts.append(f"The next column, {colname(nxt)}, opens with ‹{nxt['reading']}› "
                     f"(Dillmann ch. {nxt['chapter']}), so the chapter ends in {colname(last)}.")
    if n in BOUNDARY_NOTES:
        parts.append(BOUNDARY_NOTES[n])
    parts.append("Mapping by reading the first line of every column on the photographs; "
                 "the Ge'ez shown is Dillmann's 1851 critical text, so the scribe's spelling differs in places.")
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    chs, full, starts = corpus()
    cols = column_map(full, starts)
    if args.mapping:
        for c in cols:
            print(f"{c['page']}{c['col']}  ch{c['chapter']:<4} score {c['score']}  {c['reading'][:40]}")
        for n in range(1, 109):
            print(n, [c["page"] + c["col"] for c in chapter_columns(n, cols, starts, full)])
        return

    man = manifest()
    get_scans(man, args.force)
    charles_html = cached(SRC / "charles" / "pg77935.html", CHARLES_URL)
    eng = chapters(str(charles_html))
    assert sorted(eng) == list(range(1, 109)), [n for n in range(1, 109) if n not in eng]
    (SRC / "charles_1917_chapters.json").write_text(
        json.dumps({str(k): v for k, v in sorted(eng.items())}, ensure_ascii=False, indent=1), encoding="utf-8")

    rows = []
    for book in BOOKS:
        a, b = book["chapters"]
        tid = PREFIX + book["slug"]
        sections, pages_used = [], []
        for n in range(a, b + 1):
            ccols = chapter_columns(n, cols, starts, full)
            pages = []
            for c in ccols:
                f = f"{KEY}/{scan_name(c['page'])}"
                if f not in pages:
                    pages.append(f)
            for f in pages:
                if f not in pages_used:
                    pages_used.append(f)
            span = colname(ccols[0]) if len(ccols) == 1 else f"{colname(ccols[0])} - {colname(ccols[-1])}"
            sections.append({
                "section": str(n),
                "original_ref": f"1 Enoch {n}; Rylands Ethiopic MS 23, {span}",
                "original_text": geez_html(chs[n]),
                "text": eng[n]["E"],
                "scan_pages": pages,
                "scan_note": scan_note(n, ccols, cols),
            })
        intro = (
            book["intro"]
            + "<p><strong>The manuscript.</strong> The photographs are of Manchester, John Rylands Library, Ethiopic MS 23, "
            "an 18th-century parchment codex written in three columns of 40 lines, which contains Enoch, Job and the four books of Kings. "
            "1 Enoch fills fol. 2r-16v. The Book of Enoch survives complete only in Ge'ez (classical Ethiopic), "
            "translated from Greek in late antiquity; it belongs to the Old Testament of the Ethiopian Orthodox Tewahedo Church.</p>"
            f"<p><strong>How the sections map to the pages.</strong> Each section is one chapter. "
            "The first line of every column of the manuscript was read on the photographs and found in Dillmann's text, "
            "so each chapter points at the page or pages that carry it, and the note under each chapter gives the column where it begins and ends "
            "with the words read there. The scribe marks many section openings with red signs.</p>"
            "<p><strong>Texts.</strong> The Ge'ez is August Dillmann's critical edition (Leipzig 1851), "
            "in the digital text of Michal Jerabek and Ran HaCohen; it has no verse numbers and is not a transcription of this manuscript, "
            "so spelling and wording on the page differ in places. The English is R. H. Charles's translation (1917), "
            "made from his own critical text of 1906, with his verse numbers and signs.</p>"
        )
        entry = {
            "id": tid, "slug": tid, "title": book["title"],
            "language": "Ge'ez (Dillmann 1851) / English (Charles 1917)",
            "source": "Rylands Ethiopic MS 23 (Manchester Digital Collections, CC BY-NC 4.0) + Ge'ez of Dillmann 1851 (digital text Jerabek/HaCohen) + English of R. H. Charles 1917 (Project Gutenberg, public domain)",
            "description": f"{book['title'].replace(' (Ethiopic)', '')}, chapter by chapter in Ge'ez and English, each chapter linked to the page of the Ethiopic manuscript (Rylands Ethiopic MS 23) that carries it.",
            "introduction": intro,
            "translator_notes": [
                "Charles's signs: words in ⌜ ⌝ are found in the Akhmim Greek but not in the Ethiopic; words in 〚 〛 are in the Ethiopic but not in the Greek; ‹ › marks restored words; [ ] marks interpolations; ( ) marks words supplied by the translator; † † marks a corrupt text; ... marks lost words.",
                "Words in italics are those Charles printed in thick type to mark an emended reading.",
                "Where Charles prints the Ethiopic and the Akhmim Greek side by side (chapters 22, 27 and 32), the translation of the Ethiopic column is given here.",
                "Charles prints chapter 92 before chapter 91 and moves 91:12-17 after chapter 93; here each chapter's verses stand under their own chapter number, in the order Charles prints them. He also moves some verses inside chapters (for example 106:17 after 106:14); that order is kept.",
                "The Ge'ez is shown with a line break after each full stop (።); the digital text has no verse numbers, so verses cannot be matched line by line.",
            ],
            "translation": sections,
            "verification": {
                "scan_source": f"The University of Manchester Library, Manchester Digital Collections, Ethiopic MS 23, IIIF ({MANIFEST_URL}); viewer {VIEW_URL}",
                "scan_license": "CC BY-NC 4.0 (\"Images made available for download are licensed under a Creative Commons Attribution-NonCommercial 4.0 International License\"); credit: The University of Manchester",
                "scan_manuscript": "Manchester, John Rylands Library, Ethiopic MS 23, 18th century, Ethiopia; 67 folios, 3 columns of 40 lines; 1 Enoch on fol. 2r-16v; formerly Bibliotheca Lindesiana, bequeathed to the John Rylands Library by Enriqueta Rylands",
                "scan_mapping": "Visual check: the first line of each of the 90 text columns (fol. 2r col. a to fol. 16v col. c) was read on full-resolution crops of the photographs and located in Dillmann's text; chapter boundaries at column edges were read on the image (see each scan_note).",
                "scan_mapping_urls": [VIEW_URL, MANIFEST_URL],
                "scan_local_paths": pages_used,
                "original_text_source": f"A. Dillmann, Liber Henoch Aethiopice (Leipzig 1851); digital text by M. Jerabek (Library of Ethiopian Texts, 1995), Unicode version by R. HaCohen (2011): {DILLMANN_INFO}",
                "original_text_license": "Edition public domain (1851). Digital text: \"Permission to use, copy, and distribute this text, for any NONCOMMERCIAL purpose is hereby granted without fee, provided that the copyright notice and this permission notice appear in all copies\" (Copyright 1995 Library of Ethiopian Texts, Michal Jerabek, Prague).",
                "translation_source": f"R. H. Charles, The Book of Enoch (SPCK, London 1917), Project Gutenberg eBook #77935: {CHARLES_PAGE}",
                "translation_license": "public domain (published 1917)",
                "translator": "R. H. Charles (1917)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{tid}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
        rows.append({
            "id": tid, "slug": tid, "order": book["order"], "title": book["title"],
            "author_id": "enoch-author", "language": "Ge'ez",
            "era": "Second Temple", "tradition": "jewish", "category": "sacred-text",
            "date_approx": book["date_approx"], "century": book["century"],
            "source": entry["source"], "description": entry["description"],
            "themes": ["1-enoch", "enoch", "ethiopic", "geez", "pseudepigrapha"] + book["themes"] + ["verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": f, "caption": f"Rylands Ethiopic MS 23, fol. {f.split('-f')[-1][:-4].lstrip('0')}"} for f in pages_used]},
        })
        print(f"wrote {tid}: {len(sections)} sections, {len(pages_used)} pages")

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX,
            "label": "1 Enoch (Ethiopic, Rylands MS 23)",
            "group": "Dead Sea Scrolls & Second Temple",
            "date_sort": -250,
            "author_name": "1 Enoch (3rd c. BC - 1st c. AD; Ethiopic manuscript, 18th c.)",
            "source_url": VIEW_URL,
            "critical_edition": "A. Dillmann, Liber Henoch Aethiopice (1851), digital text Jerabek/HaCohen",
            "translator_name": "R. H. Charles (1917)",
            "original_lang_label": "Ge'ez · Dillmann 1851",
            "original_lang_code": "gez",
            "edition_label": "",
            "search_terms": "1 enoch book of enoch ethiopic geez henok watchers giants nephilim azazel semjaza parables son of man astronomical book animal apocalypse epistle of enoch",
            "description": "The complete Book of Enoch (1 Enoch, chapters 1-108) in Ge'ez and English, every chapter linked to the page of an 18th-century Ethiopic manuscript in the John Rylands Library, Manchester, that carries it.",
        },
        "texts": rows,
    }
    COLL.write_text(json.dumps(coll, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
