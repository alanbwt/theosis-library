#!/usr/bin/env python3
"""
import_book_of_the_dead.py -- the Book of the Dead (spells for "going forth by day") in the
papyrus of Iuefankh, Turin, Museo Egizio Cat. 1791 (Ptolemaic period): every spell of the
roll for which an open transliteration and a public-domain English exist, spell by spell.

Collection key: book-of-the-dead   (entries verified-book-of-the-dead-spell-NNN)

Chain of evidence
-----------------
1. OBJECT   Papyrus of Iuefankh, Turin, Museo Egizio, Cat. 1791, a Book of the Dead roll of
            the Ptolemaic period (TLA: 332-31 BCE), from Thebes (TLA). Published by R. Lepsius,
            Das Todtenbuch der Aegypter nach dem hieroglyphischen Papyrus in Turin (Leipzig
            1842), 79 plates (Taf. I-LXXIX). Lepsius divided the roll into 165 chapters; every
            plate is headed by its chapter numbers and carries the column numbers of each
            chapter at its foot. The TLA text of every spell uses Lepsius's chapter and column
            numbers. Plate-to-chapter list: PLATES below (read on the BSB/MDZ scan,
            bsb10801356, canvases 31-189).
2. SCANS    31 photographs of the roll by the Museo Egizio, released under CC0 and published
            on Wikimedia Commons (Category:Book of the Dead of Iuefankh - Museo Egizio (Turin)
            C. 1791), files "..._papyrus_-_Museo_Egizio_Turin_C_1791_p04.jpg" to "..._p034.jpg"
            (6048 x 4032 px). They run from the end of the roll (p04) to its beginning (p034);
            the stitched strip ..._p03.jpg of the same series confirms the sequence. Here they
            are numbered 1-31 in reading order (photograph 1 = p034, photograph 31 = p04). A
            further CC0 photograph, ..._p02.jpg, shows the judgment vignette of Spell 125.
            Mapping: every photograph was compared by eye with Lepsius's plates (vignettes, red
            titles, framed compartments); the spells it carries and the position of their
            titles and vignettes, measured from the left edge of the photograph, are in PHOTOS
            below. The edges of neighbouring photographs overlap; the overlaps were checked side
            by side, so a spell that runs over an edge lists both photographs.
3. ORIGINAL Thesaurus Linguae Aegyptiae, Totenbuch, pTurin Museo Egizio 1791, edition by
            Burkhard Backes; TLA database extract of January 2018 (urn:nbn:de:kobv:b4-opus4-29190)
            as converted to TEI by S. D. Schweitzer, AED-TEI (github.com/simondschweitzer/aed-tei,
            commit 462c722e, files/), CC BY-SA 4.0: 182 texts (TLA list below). Transliteration
            only: the AED-TEI hieroglyph files of these texts are empty.
4. ENGLISH  Samuel Birch, "The Funereal Ritual or Book of the Dead", in C. C. J. Bunsen,
            Egypt's Place in Universal History, vol. V (London: Longmans, Green, 1867), from
            p. 161. Birch's note 60: "The text followed is that of the Turin Ritual; Lepsius,
            Das Todtenbuch, 4to, Leipzig, 1842", i.e. he translated this same papyrus. Public
            domain (1867). Text from three Internet Archive scans (bub_gb_fCSiSJ7OxSIC,
            egyptsplaceinun00cottgoog, india.history.resource.41142): the three OCR texts were
            cleaned of running heads, page numbers and footnotes, aligned word by word
            (difflib), and each word settled by agreement (see birch_* functions). Birch's
            chapter numbers equal Lepsius's up to 144; Birch splits the rubric of 144 off as
            "CXLV", so his CXLVI-CLXVI are Lepsius 145-165. Every pairing was checked against
            the TLA German sentence translations (*_st.xml).
            Not published: Spells 20, 111 and 121 (Birch gives only a summary or "same as
            Chapter XIII/CVIII"), and the vignette-only Spells 16, 143 and 150 (no text).

Usage:  python3 scripts/import_book_of_the_dead.py           (build)
        python3 scripts/import_book_of_the_dead.py --force   (re-make the images)
"""

import argparse
import difflib
import html
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parent.parent
KEY = "book-of-the-dead"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()

T = "{http://www.tei-c.org/ns/1.0}"
AED_COMMIT = "462c722e0323e05641aea2eee8cdf1e27303d939"
AED_RAW = f"https://raw.githubusercontent.com/simondschweitzer/aed-tei/{AED_COMMIT}/files/"
COMMONS = "https://commons.wikimedia.org/wiki/File:"
COMMONS_REDIRECT = "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/"
COMMONS_CAT = "https://commons.wikimedia.org/wiki/Category:Book_of_the_Dead_of_Iuefankh_-_Museo_Egizio_(Turin)_C._1791"
LEPSIUS = "https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb10801356/manifest"
UA = "TheosisLibrary/1.0 (https://theosislibrary.com; non-commercial research)"
BIRCH_SCANS = [  # (archive.org id, djvu text file); the first is the base text of the vote
    ("bub_gb_fCSiSJ7OxSIC", "bub_gb_fCSiSJ7OxSIC_djvu.txt"),
    ("egyptsplaceinun00cottgoog", "egyptsplaceinun00cottgoog_djvu.txt"),
    ("india.history.resource.41142", "41142_djvu.txt"),
]

# --------------------------------------------------------------------------
# TLA texts of pTurin 1791 (title, AED-TEI id), in roll order
# --------------------------------------------------------------------------
TLA = [
    ("Tb 001", "GW5VRQGSOFBYJAU4UO7H233CZM"), ("Tb 002", "ZVFIVUBVNBBEXH4Z66BSQE7IFM"), ("Tb 003", "GAF5E77IXJGUFB2ND62TH5R3LA"), ("Tb 004", "X4ETIPW2OVDUTOBJPXEGP7Z2CE"),
    ("Tb 005", "WPWK3MCZKRCNTEPZFSY7R5DOCA"), ("Tb 006", "NIZ6T7YPTZFPLM4T32PGSK5Q5I"), ("Tb 007", "4PX7VUUC2ZFOXAQTV4S7MNP3O4"), ("Tb 008", "GZIE6GDHMNEFVKGQ7J6E2UKJUA"),
    ("Tb 009", "MGW2WBEE7FAXVPCWIICP5YRDEE"), ("Tb 010", "I35BSKK3GJH7BG6HLY6VGCR5BQ"), ("Tb 011", "XMTXHZ5U3NAWNEH534GQK2TATA"), ("Tb 012", "IJ64I6GPLJDDDJSLAQ7UM6O2VY"),
    ("Tb 013", "O6RAEPJJCNC6ZMSYOMAWHSJ4IM"), ("Tb 014", "2M25N7UGJNB5VIWOATWT4GGLOY"), ("Tb 015 a", "I2WLCBM7ZVDB5EJNCJLOWAHUYA"), ("Tb 015 b", "TUS4LSAQ3VANBIQLXARFI2RIWY"),
    ("Tb 015 c", "O6UDIOMN3NBPHG5BO7PXX6IRFI"), ("Tb 015 d", "6PJB3ATTDFCNPNJNSTF6C3PYOM"), ("Tb 015 e", "MNLJFI6RGFBJPMJUB3KFELKRZ4"), ("Tb 015 f", "JCCNMNBQ4VGGFCTRUCMSMRHFWY"),
    ("Tb 015 g", "5NQPA5LHPVB6RMXJJK5XEJA6TY"), ("Tb 015 h", "TRTWUJFAQBB4VM4HZFSJRXMTKA"), ("Tb 015 i", "3GP3Q4HTXJFNXJQ73XYPNSXTOY"), ("Tb 017", "GV56MS6DMFFRFHFXKUFR2MXX2Y"),
    ("Tb 018", "SQY3IC5NRRD7VLZ5LZMIBABEHY"), ("Tb 019", "6QBRB4KZ7REYLATAU5I7KL5LJY"), ("Tb 020", "H6YF3CTZ7ZF6TIEB4ZVOMTGVLM"), ("Tb 021", "KZMTGUPYXVGETAYWYGARXDRKOY"),
    ("Tb 022", "HAAYJPWFHFEWLC34RZSLZL4Q4M"), ("Tb 023", "M7CPU3XI7BCSVHG7STVISA2ZLU"), ("Tb 024", "WUQN5PZKMFAR5O4KMDJNU6EYVE"), ("Tb 025", "7RKFJ32M5BB2XKJJCHYD6ILFVU"),
    ("Tb 026", "FFWVTX3CTFHRXAAEFU5ASEXGYQ"), ("Tb 027", "C3YHWR24TBDKXO7ITYOERSSMZE"), ("Tb 028", "XD7CQ2MW5RCLZLSTFDZCTO4EWI"), ("Tb 029", "J642PQMFEJARHLJURCCWHETCHA"),
    ("Tb 030", "272LV3L2N5D3HFHTCF5XWIPOT4"), ("Tb 031", "GX3BNL6PY5EP3MIKAILPTUZSKQ"), ("Tb 032", "IQNPVBYSK5BLPOIXXVPWSKK4GM"), ("Tb 033", "VGTO4TRK5ZH37HJUKRJ7ZQAHRY"),
    ("Tb 034", "IRLQBQPMA5DODDITG2DT63QIJY"), ("Tb 035", "R3RBEOIKBVDDVK7WPMNID3DO5E"), ("Tb 036", "J32IUMX6AJDVXOGGVCJ6VTYNV4"), ("Tb 037", "GM5BP4H2ZJDTDAPXWJ34K5VJLM"),
    ("Tb 038", "6NU77LFFP5B7NKLDCPL4KMUCGU"), ("Tb 039", "4FW7OXQKDZF35AJHTLC4KN6BOM"), ("Tb 040", "FDU3P7FEFJC5VDFXIFCCGIF3GU"), ("Tb 041", "43AVV2BH3NBM7F2I34IDIOTSCY"),
    ("Tb 042", "NNI2CAW23VBDZKAAQ4HK3NYALE"), ("Tb 043", "E3JBSFWVSBCTRMIBNG54THC5TQ"), ("Tb 044", "VMTSAMKMIZAIDG52ITN6TKBGWI"), ("Tb 045", "REOWSEXFOVD5PJVXCMK6FYSFBQ"),
    ("Tb 046", "WU2M2W35HJECTB7GFYGK4WJMTM"), ("Tb 047", "YBYAKN4KDFFUJJLLA7W3IJ2YEA"), ("Tb 048", "32AH5CVEUZFJLOEVYQ27MM3OO4"), ("Tb 049", "QXJL5USZKBEMVEWIKXIV6ILEXQ"),
    ("Tb 050", "7SYX5D5YPBFDPMOA4QX4YO6CCE"), ("Tb 051", "RIIYQ3GQO5FVHBQCVJ5225NUUI"), ("Tb 052", "A5M4O5YLTZCDZMN2P457S7OBDE"), ("Tb 053", "MENMJG5X6FFWHIMZMYZJOVQTZ4"),
    ("Tb 054", "DLMTQBUNZNFWRKTZ4KFOXICQLM"), ("Tb 055", "CMUVB5ZZYJBPPO646NGEVEIZNE"), ("Tb 056", "HAAYZN7URRGAXE37NO7OHOCKJ4"), ("Tb 057", "X5HRPEZXVJF3NAJOWSGUPS46DY"),
    ("Tb 058", "3GMOT6ZTXVAY7AULZN7HHZOX2U"), ("Tb 059", "M5FFZK3OEZGITGMBGV3FVPVUGA"), ("Tb 060", "QMHKLNCIEJF2LALGOX6Z7TCVSA"), ("Tb 061", "O56UR2VAHBGPRBILRAWHVU4UOM"),
    ("Tb 062", "Z5QXJUBSXBF65CUOKUZNOMKBLM"), ("Tb 063", "IFM3BI3PCBHTRLPCSMXA43HACI"), ("Tb 064", "JGFHZFA4KND7XAWUXKGGH7ZJPQ"), ("Tb 065", "7M4WCCYTBNGODK3M3MN6G66B6E"),
    ("Tb 066", "E3LW6IHARND5HDUDLWPJALCILU"), ("Tb 067", "5QLZEQ2G75BHLOZXO73TDVEHRI"), ("Tb 068", "7HLTTASHFNCPTGBNYCJ7I6EUOM"), ("Tb 069", "EAGGFPVPKJAVXHRUSNKZZZHQF4"),
    ("Tb 070", "QJBWRSFRRZDDTFNSTIKPRIUHEI"), ("Tb 071", "GVH3O3BSHFCIHDCO4QZV74KAXA"), ("Tb 072", "JZHLPWBJRFEGBJHT4TOLE3RVIQ"), ("Tb 073", "CUDS76BGNJEMDO2WIMKJHTYBVY"),
    ("Tb 074", "F2O5OQEZZZEFTDZ2R2NXUKXAEA"), ("Tb 075", "U3ATTXJ5INCSHHKYB6ELMAGRYM"), ("Tb 076", "7VZJVTN7SRH7TGDDY6L4F5O3AA"), ("Tb 077", "5UDFIWXA3ZFUXEMNYXJRIUYYYY"),
    ("Tb 078", "SXE3M33ORJBVJPI44ACR3HQOJQ"), ("Tb 079", "3EMD4IIA6VCBVHNIRZ3JDSONQU"), ("Tb 080", "6PXYITILY5DLDJJ4EY2MMRGJMI"), ("Tb 081", "RRIFXB5ITJBIHHDCTDBOMU6TWQ"),
    ("Tb 082", "TUH57I4AEJACHJA5UJTAXGF6TE"), ("Tb 083", "2UTZVBEF7NC3TLNTFHGPPEWUXI"), ("Tb 084", "HOFQMULTAZF6VAYC6EGWQFXYGE"), ("Tb 085", "KAVNWEKOMFEMBPGMR7VA3GAGJY"),
    ("Tb 086", "AF7CNMP7PFEURFFADRO2LJ7QZE"), ("Tb 087", "FRX46AUCSFH45HP7DUFCQAUKOE"), ("Tb 088", "WHHGUEU52NDYVFXBFBDA2H6C7Q"), ("Tb 089", "KQUI4C7KVZF2TGL7PL7V65MCXM"),
    ("Tb 090", "BRJXMLHCZRGCZBQGWDUNI5FTYI"), ("Tb 091", "YKHRSAYLKZH3FMI4TH7VYDIY3I"), ("Tb 092", "VFE4XX7USFDYBG6X5SZY3AXGUI"), ("Tb 093", "S6VILX6QBNCHNGVLJJJDDOST3Y"),
    ("Tb 094", "JXFCCY2DZJESBFCOWIAOPLX5AM"), ("Tb 095", "526OSQAQ3VBCZJUFFWZHMPODPQ"), ("Tb 096", "NUC2K6UHX5ECNN2WCYI7QOVAHU"), ("Tb 097", "ZKX4PLGIEZA53G25HZ563FDHEU"),
    ("Tb 098", "YN7PSXWRSJG2PHAHWLXQRB5TTQ"), ("Tb 099", "5DLE645KPRH6FLDK7FGFFBPHHA"), ("Tb 100", "OGFAOOPCHJEMBK5IWP4GZ5NDC4"), ("Tb 101〈1〉", "52L2FXACGRF4DN3W2GIIZC5YOY"),
    ("Tb 101〈2〉", "B3KLPLYOGJBLDMGH2Y57GSCOLQ"), ("Tb 102", "MB4SQWZMIJBVFPU5ULB7AI2GPA"), ("Tb 103", "FRQOLRSDTVHAZJNBOVKR4XFWOM"), ("Tb 104", "7JRL2UKQBVASPLBG3OR2ITS7SU"),
    ("Tb 105", "BHRIWSKP6RHUNP4Q76WLGYTM7M"), ("Tb 106", "LEGKGZGXQBEW5LWDW2IWIMI3WY"), ("Tb 107", "WNAD2NVK4RAJBNET4RP7GAUUK4"), ("Tb 108", "PAEQ764DGVFH3KK4K6KOPG5T7I"),
    ("Tb 109", "QLRXPYXZWBHWNOWKETQUDEPJEI"), ("Tb 110〈1〉", "C2REOU37KNA3HKR7UO4TQHADH4"), ("Tb 110〈2〉", "AOT7NIL3GNH7DKXFECJATCRUSY"), ("Tb 111", "U6JBF24HXZHMLP3BYJ2AN4UJZI"),
    ("Tb 112", "H2HW7WDYJFAVXJULW7TIT66J4M"), ("Tb 113", "KLGOAZY4BZBBZHE6HGJF72H7XA"), ("Tb 114", "4PJCEMK2HBDYVFXHLXSYZB46AQ"), ("Tb 115", "D33SKDHPTJHSLKJY734JR5CGWU"),
    ("Tb 116", "A2OJFOYUHJCP7JZYSR6NN46GMY"), ("Tb 117", "KKYYU7E6IFC2XLEGNSNQT7QSYY"), ("Tb 118", "HQF6N7HJVRAMJDGXQUB6VCY7TE"), ("Tb 119", "VLK3UIGSMFEVJPUUEPX6TC24TY"),
    ("Tb 120", "X4NWH7EXSRFILCTNXXFXXEJNUE"), ("Tb 121", "XCFXWJ72OFBZ3FPMSWVBJEWBPA"), ("Tb 122", "S462LNRKRZBLRBQ35MO32VQ7XY"), ("Tb 123", "ES2TWVBB2BH3TK2IM6J54PD4MA"),
    ("Tb 124", "V5NVVBGPNRD4DF7UYPABHCIOAA"), ("Tb 125〈A〉", "CPLF5PTQARHP3DDZNVHN3SFEUI"), ("Tb 125〈B〉", "SPXNENYKDJFE3BAOXGWMPXY22E"), ("Tb 125〈C〉", "JYUKBUBKCRAIDDXGDCZLOZGKCY"),
    ("Tb 125〈D〉", "M6M5EKWCUFGVZCBHYYWZBOPMTM"), ("V Tb 125", "3756ZSABFVBYDED4YZZPYCKWEE"), ("Tb 126", "NVDU6SZEMVAYBGBVXSTHXCYLP4"), ("Tb 127", "LRP3IFYU3VG53BWLSBU6OF33TE"),
    ("Tb 128", "F5V2FZHXLNBARIKLFQIR4WAO6I"), ("Tb 129", "WJWD4DJSEBFBTLE7QDF7N436LU"), ("Tb 130", "7HPAERIZFNGYXCS7A3MBRBGPD4"), ("Tb 131", "VPDVLE6VMJBMLEPQSB2S7MH2GY"),
    ("Tb 132", "2QALUJ63IVGS5M3OOMR3QQGZIU"), ("Tb 133", "ATZXK3PDE5G5RGANYUNU444DHU"), ("Tb 134", "B32T6XD6VFECRIDPGXJR3LXMYU"), ("Tb 135", "NNPEFJXBONAR3AMRLINUAZWGMA"),
    ("Tb 136", "2ZZEBEPNZRAJBOWTNQ77C35CP4"), ("Tb 137", "RJPC4L3NOZBXNBEV46QWS7A67M"), ("Tb 138", "JQ5KIT34TFBNTOTWD4JP7MLLH4"), ("Tb 139", "DCNZKHODJJAMFMROCHSNPVJRAI"),
    ("Tb 140", "G6OSXNYXSJC3BHZPWESG4PJAAM"), ("Tb 141", "B35DLKLJOZCOHPN3AXBCE3TTWE"), ("Tb 142", "H23S4XGLKJGTZDHJIUJE7C437E"), ("Tb 144", "LSGB6RPUORGS3AT5D6IJEZOOWI"),
    ("Tb 145〈1〉", "35AJJ2RX5JCVPFP5477YV7BBJQ"), ("Tb 145〈2〉", "CTDG5LOIYJFCXMAIPRDK347BDA"), ("Tb 145〈3〉", "URT3Q2ET2ZBTPHVFG4TKVLSVBU"), ("Tb 145〈4〉", "OQGQP7I7NRG6FOPZB4GCPLULEE"),
    ("Tb 146〈1〉", "UHHNYIBEVNBFJLWKMJ64STCYNA"), ("Tb 146〈2〉", "H2FH4QJK2JGANE5YW6JLDGFLSE"), ("Tb 147", "X4DIXNQTRNFV7ASGIGX2MFXR64"), ("Tb 148", "TJXI3AQQJNH5BPBBPQNV5OFHBY"),
    ("Tb 149〈1〉", "CXVP277CPJANNGG2XTSK3XRBQQ"), ("Tb 149〈2〉", "DJIDTTIR6BFYBAIW5M6HNDT3OA"), ("Tb 149〈3〉", "FPJRIXSZTZGGRC7MAH7UIR74BY"), ("Tb 151", "QLN2E7ZEIJBAXIFJYIC4BF5HAE"),
    ("Tb 152", "CQKQ2PVIWFEA5L4FNQCJZFABY4"), ("Tb 153", "WQCJHA77KFEOJKEPWNVRXS3TEU"), ("Tb 154", "5BYXZRKLDZHT3CVZRUQVAEUOLQ"), ("Tb 155", "XQQ4O7MAXBGDNGZMS7WOIYI4VE"),
    ("Tb 156", "OMVD2P35HBAXTBTIEUKNRR3WB4"), ("Tb 157", "NDBUHD64SNGCZICV5ZYOT5WYIU"), ("Tb 158", "QL26LQBPO5GKZI4HV773Y55RW4"), ("Tb 159", "WXVSAG7FI5AG3IJ42AQ4TAMQSI"),
    ("Tb 160", "VNAY2LNMIVFPJDULAI6KEPYZGE"), ("Tb 161", "KTETFTWINZFNPMQ74OWRJGS3E4"), ("Tb 162", "QAUURHQRYJDLPCYLTZTOOR2BZY"), ("Tb 163", "N6FN7ZBW5RFJ7OVDEFRJE447E4"),
    ("Tb 164", "MYTJUXR63ZH4FIUR4JB52RGOI4"), ("Tb 165", "ZCIHVFZV2NCK3MW3GDTYHOV6TM"),]

# Lepsius 1842, chapters on each plate (plate headers, read on the MDZ scan)
PLATES_TXT = ("I:1 II:1-6 III:7-12 IV:13-15 V:15 VI:15,16 VII:17 VIII:17 IX:17 X:17 XI:17,18 XII:18 XIII:18,19 "
              "XIV:20-24 XV:25-29 XVI:30-32 XVII:32-38 XVIII:39,40 XIX:41,42 XX:42-47 XXI:48-52 XXII:53-58 "
              "XXIII:59-64 XXIV:64 XXV:64-68 XXVI:68-71 XXVII:71-74 XXVIII:75-78 XXIX:78 XXX:78-80 XXXI:80-84 "
              "XXXII:85-87 XXXIII:88-92 XXXIV:92-96 XXXV:97-99 XXXVI:99 XXXVII:99-101 XXXVIII:102-106 "
              "XXXIX:107-109 XL:109,110 XLI:110 XLII:110,111 XLIII:112-114 XLIV:115-119 XLV:120-124 XLVI:124,125 "
              "XLVII:125 XLVIII:125 XLIX:125 L:125 LI:126-128 LII:128-130 LIII:130 LIV:130-133 LV:133-135 "
              "LVI:136,137 LVII:138-140 LVIII:141 LIX:142,143 LX:144 LXI:144,145 LXII:145 LXIII:145 LXIV:145 "
              "LXV:145,146 LXVI:146 LXVII:146,147 LXVIII:147 LXIX:148 LXX:148 LXXI:149 LXXII:149 LXXIII:149,150 "
              "LXXIV:151-153 LXXV:154-156 LXXVI:157-161 LXXVII:162,163 LXXVIII:163,164 LXXIX:164,165")

# --------------------------------------------------------------------------
# Photographs, in reading order. 'first'/'last' = the spells at the right-hand and left-hand
# edges (the text runs from right to left). 'anchors' = what was checked by eye on the image;
# percentages are positions measured from the left edge of the photograph.
# --------------------------------------------------------------------------
PHOTOS = [
    dict(n=1, p="034", first="1", last="7", anchors={
        "1": "the inscribed area begins at 72% (the right part of the photograph is the blank start of the roll); Spell 1 "
             "stands under the long title line and the vignette of the funeral procession (the boat with the mummy drawn by "
             "oxen, Anubis, the mourning women), as on Lepsius pl. I-II",
        "7": "its first columns are near the left-hand edge, under the offering bearers who carry animals on their heads "
             "(Lepsius pl. III); they are also at the right-hand edge of photograph 2"}),
    dict(n=2, p="033", first="7", last="15", anchors={
        "7": "its columns are at the right-hand edge under the offering bearers, also seen at the left-hand edge of photograph 1",
        "13": "under the scene of slaughter and the piled offerings (Lepsius pl. IV)",
        "15": "the hymns of Spell 15 fill the left part of the photograph under the vignette of obelisks, the offering table "
              "and the kneeling worshipper (Lepsius pl. IV-V), with the red heading of its seventh hymn at 2-10%; they "
              "continue on photograph 3"}),
    dict(n=3, p="032", first="15", last="17", anchors={
        "15": "the last hymns of Spell 15 fill the right part (60-100%) under the vignette of the shrine, the pyramid, the "
              "kneeling man and the enthroned god (Lepsius pl. V-VI)",
        "17": "begins at 56% with the red end of its title line, the god in a shrine, the falcon and the boat of the gods "
              "(Lepsius pl. VII); its columns run to the left-hand edge and on to photographs 4 and 5"}),
    dict(n=4, p="031", first="17", last="17", anchors={
        "17": "the whole photograph is filled by the columns of Spell 17 under its continuous vignette band (the two kneeling "
              "women, the mummy on its bier, the boat of the sun, seated gods; Lepsius pl. VIII-XI)"}),
    dict(n=5, p="030", first="17", last="19", anchors={
        "17": "its last columns are at the right-hand edge (85-100%), under the vignette of the enthroned god with the "
              "kneeling figures, which also stands at the left-hand edge of photograph 4",
        "18": "the framed compartments of Spell 18 (gods above short columns) run from the frame line at 86% to 21% "
              "(Lepsius pl. XI-XIII)",
        "19": "red title at 10-20%; its columns run to the left-hand edge and on to photograph 6"}),
    dict(n=6, p="029", first="19", last="31", anchors={
        "19": "its last columns are at the right-hand edge (86-100%)",
        "20": "two-line red heading at 73-86% (Lepsius pl. XIV)",
        "30": "the scarab vignette at 7-13% (Lepsius pl. XVI)",
        "31": "its vignette of a man spearing crocodiles begins at the left-hand edge (0-6%); it continues on photograph 7"}),
    dict(n=7, p="028", first="30", last="40", anchors={
        "30": "its red title column and last columns at the right-hand edge (96-100%)",
        "31": "the man spearing crocodiles and its columns at 76-95%",
        "32": "the crocodiles at 59-75%",
        "33": "the man and the snake at 55-59%",
        "38": "at 36-42% (Lepsius pl. XVII)",
        "39": "the man spearing a serpent under a long red title at 24-35%, its columns to 11% (Lepsius pl. XVIII)",
        "40": "the ass bitten by a snake at 2-11%; it continues on photograph 8"}),
    dict(n=8, p="027", first="40", last="51", anchors={
        "40": "the ass vignette at 91-97%",
        "41": "the man spearing at 85-91% (Lepsius pl. XIX)",
        "42": "long red title at 70-84% over the table of the members of the body; its columns run to 46%",
        "50": "the stele and figure at 5-9% (Lepsius pl. XXI)",
        "51": "at the left-hand edge (0-4%), also at the right of photograph 9"}),
    dict(n=9, p="026", first="50", last="64", anchors={
        "50": "the stele and figure at 93-99%",
        "52": "the man seated at an offering table at 84-88% (Lepsius pl. XXI)",
        "64": "red title at 9-20% with the man before the sun disc (15-20%; Lepsius pl. XXIII); its columns run to the "
              "left-hand edge and on to photograph 10"}),
    dict(n=10, p="025", first="64", last="71", anchors={
        "64": "its columns fill the right part (53-100%; Lepsius pl. XXIV-XXV)",
        "71": "long red title at 0-12% with the falcon and the cow; it continues on photograph 11 (Lepsius pl. XXVI)"}),
    dict(n=11, p="024", first="71", last="78", anchors={
        "71": "the falcon vignette and the red title at 82-100%",
        "72": "red title at 64-80% with the seated gods (Lepsius pl. XXVII)",
        "77": "the falcon at 38-45%",
        "78": "the second falcon at 31-38% (Lepsius pl. XXVIII); its columns run to the left-hand edge and on to "
              "photograph 12"}),
    dict(n=12, p="023", first="78", last="85", anchors={
        "78": "its columns fill the right part (64-100%; Lepsius pl. XXIX-XXX)",
        "79": "four gods under a red title at 55-64%",
        "80": "the figure with the sun disc at 37-50%",
        "81": "the lotus and the figure at 30-37%",
        "83": "the first heron at 17-24% (Lepsius pl. XXXI)",
        "84": "the second heron at 8-17%",
        "85": "begins at the left-hand edge (0-8%) and continues on photograph 13"}),
    dict(n=13, p="022", first="85", last="93", anchors={
        "85": "the walking figure and its red title at 88-91%",
        "86": "the swallow on a pedestal at 71-74% (Lepsius pl. XXXII)",
        "87": "the serpent at 62-63%",
        "89": "the ba-bird over the bier at 51-56% (Lepsius pl. XXXIII)",
        "93": "the man with raised arms and the boat at 6-16% (Lepsius pl. XXXIV); its vignette is also at the right-hand "
              "edge of photograph 14"}),
    dict(n=14, p="021", first="93", last="99", anchors={
        "93": "the left part of its boat vignette and its last columns at the right-hand edge",
        "94": "Thoth and the kneeling man with the palette near the right-hand edge (Lepsius pl. XXXIV)",
        "98": "the man in a boat and the standing man at 61-71% (Lepsius pl. XXXV)",
        "99": "red title at 51-60%, then its columns with red tops in two registers to the left-hand edge (Lepsius pl. "
              "XXXV-XXXVII); it continues on photograph 15"}),
    dict(n=15, p="020", first="99", last="109", anchors={
        "99": "its last columns at 93-100%",
        "100": "Ra in his boat under a red title at 82-91%",
        "102": "the boat with Ra and a man at 60-69% (Lepsius pl. XXXVIII)",
        "103": "the shrine at 56-59%",
        "108": "the four gods at 23-31% (Lepsius pl. XXXIX)",
        "109": "red title at 8-15% over the boat, the two plants and the man; it continues on photograph 16"}),
    dict(n=16, p="019", first="109", last="110", anchors={
        "109": "its last columns at 85-100%",
        "110": "its columns at 66-84% with a man adoring at their foot (Lepsius pl. XL), the vignette of the Field of "
               "Offerings in three registers at 12-65% (Lepsius pl. XLI), and its next columns with a second adoring man "
               "at 0-12%; it continues on photograph 17"}),
    dict(n=17, p="018", first="110", last="120", anchors={
        "110": "its last columns at the right-hand edge (89-100%; Lepsius pl. XLII)",
        "111": "red title at 71-79%",
        "112": "the gods at 63-71% (Lepsius pl. XLIII)",
        "115": "the sun-headed gods at 30-38% (Lepsius pl. XLIV)",
        "119": "the shrine and the standing man at 7-12%, also seen at the right-hand edge of photograph 18",
        "120": "red title at the left-hand edge (0-6%); it continues on photograph 18"}),
    dict(n=18, p="017", first="119", last="125B", anchors={
        "119": "the shrine and the standing man at 92-97%",
        "120": "at 88-92%",
        "122": "the shrine and the bending man at 76-88% (Lepsius pl. XLV)",
        "124": "the five figures at 60-70%; its columns run to 52%",
        "125A": "the title line in red and black at 30-52% over its columns (Lepsius pl. XLVI)",
        "125B": "the columns with red tops in two registers run from 30% to the left-hand edge (Lepsius pl. XLVII); "
                "they continue on photograph 19"}),
    dict(n=19, p="016", first="125B", last="125V", anchors={
        "125B": "its last columns with red tops at 88-100%",
        "125C": "its columns at 37-88% (Lepsius pl. XLVIII-XLIX)",
        "125D": "its four columns stand just right of the vignette",
        "125V": "the judgment vignette begins at 36% (lotus column, the adoring deceased, Maat, the row of the 42 judges "
                "under a frieze of cobras and feathers) and runs to the left-hand edge and on to photograph 20"}),
    dict(n=20, p="015", first="125V", last="128", anchors={
        "125V": "the rest of the judgment vignette at 49-100%: the balance with Anubis and Horus, Thoth writing, the "
                "Devourer, and Osiris enthroned in his shrine (53-62%) (Lepsius pl. L)",
        "126": "the baboons around the lake of fire at 40-46% (Lepsius pl. LI)",
        "127": "red title at 22-37% over its gods",
        "128": "the gods and the adoring man at 6-17%; its last columns are at the right-hand edge of photograph 21"}),
    dict(n=21, p="014", first="128", last="133", anchors={
        "128": "its last columns at the right-hand edge (95-100%)",
        "129": "red title and the boat with a man at 80-95% (Lepsius pl. LII)",
        "130": "the boat of four gods with the sun-headed god at 65-79%; its columns run to 30% (Lepsius pl. LIII)",
        "131": "red title at 29-30%",
        "132": "the figure at 17-20%",
        "133": "the boat with the shrine at 0-16% (Lepsius pl. LIV); it continues on photograph 22"}),
    dict(n=22, p="013", first="133", last="140", anchors={
        "133": "the rest of its boat vignette and its columns at 86-100%",
        "134": "the boat with the disc and the row of gods at 69-80% (Lepsius pl. LV)",
        "136": "the boat with the sun-headed god under a red title at 49-62% (Lepsius pl. LVI)",
        "137": "the small figures at 34-38%",
        "138": "the shrine and two figures at 27-33% (Lepsius pl. LVII)",
        "140": "red title at 8-23% with the sun god, the kneeling figures and the jackal on a shrine; it continues on "
               "photograph 23"}),
    dict(n=23, p="012", first="140", last="144", anchors={
        "140": "its last columns at 88-100%",
        "141": "the title in red and black at 57-88% over a two-line heading and a table of short columns ending in cattle "
               "signs (Lepsius pl. LVIII)",
        "142": "the three registers of short columns, each ending in a god sign, at 15-57% (Lepsius pl. LIX)",
        "144": "its red title and first gate compartment at 0-9% (Lepsius pl. LX); the narrow strip of small boats "
               "at 9-15% is the vignette of Spell 143, which has no text; it continues on photograph 24"}),
    dict(n=24, p="011", first="144", last="145", anchors={
        "144": "a detached piece at the right-hand edge (88-100%) with its red title and first gates, and its gate "
               "compartments (guardians, the deceased kneeling in a shrine, short lines in red and black) at 46-82%",
        "145": "red title at 28-46% and its gates (god, pylon, adoring man) at 0-46% (Lepsius pl. LXI-LXII); it continues "
               "on photographs 25 and 26"}),
    dict(n=25, p="010", first="145", last="146", anchors={
        "145": "its gates fill 25-100% (Lepsius pl. LXII-LXIV) and its last columns 6-25%",
        "146": "its red title and first portal at the left-hand edge (0-6%; Lepsius pl. LXV); it continues on photograph 26"}),
    dict(n=26, p="09", first="145", last="147", anchors={
        "145": "its last columns at 90-100%",
        "146": "red title at 67-94% and its portals (shrines with a serpent frieze, short red-headed lines) at 29-90% "
               "(Lepsius pl. LXV-LXVII)",
        "147": "red title at 4-28% and its doorways with gods and the adoring man at 0-29%; it continues on photograph 27"}),
    dict(n=27, p="08", first="147", last="149", anchors={
        "147": "its doorways and columns at 76-100% (Lepsius pl. LXVIII)",
        "148": "the horizontal lines at 50-76% (Lepsius pl. LXIX) and the vignette of the cows and the bull under a "
               "cornice at 15-50% (Lepsius pl. LXX)",
        "149": "its first mounds with their figures from 15% to the left-hand edge (Lepsius pl. LXXI); it continues on "
               "photograph 28"}),
    dict(n=28, p="07", first="149", last="149", anchors={
        "149": "its mounds, each a framed figure over columns with red tops, fill 9-100% (Lepsius pl. LXXI-LXXIII); the "
               "map vignette of Spell 150 (no text) is at 0-9%"}),
    dict(n=29, p="06", first="151", last="160", anchors={
        "151": "the framed figures with short lines at 80-88% (Lepsius pl. LXXIV)",
        "152": "red title at 72-79% with the seated and kneeling figures",
        "153": "red title at 61-67%, its columns at 55-68%",
        "154": "red title at 50-55% with the mummy on a bier, its columns at 33-55% (Lepsius pl. LXXV)",
        "155": "the djed pillar at 26-33%",
        "156": "the tyet knot at 20-26%",
        "157": "the vulture at 15-20% (Lepsius pl. LXXVI)",
        "158": "the collar at 11-15%",
        "159": "the papyrus column at 9-11%",
        "160": "at 2-8%, also at the right-hand edge of photograph 30"}),
    dict(n=30, p="05", first="160", last="164", anchors={
        "160": "at the right-hand edge (96-100%)",
        "161": "the two figures of Thoth with short columns at 80-96% (Lepsius pl. LXXVI)",
        "162": "red title at 68-79% with the cow, its columns at 60-80% (Lepsius pl. LXXVII)",
        "163": "the title in black and red at 30-60% over the two winged eyes (Lepsius pl. LXXVII-LXXVIII)",
        "164": "red title at 27-29% over the winged goddess between two dwarf figures; its columns at 0-30%; it "
               "continues on photograph 31"}),
    dict(n=31, p="04", first="164", last="165", anchors={
        "164": "its last columns at 90-100%",
        "165": "red title at 62-89% over the ithyphallic god with a scarab body and a standing figure; its columns at "
               "62-89% (Lepsius pl. LXXIX); the rest of the roll (0-62%) is blank"}),
]
VIGNETTE_P = "Book_of_the_Dead_of_Iuefankh,_papyrus_-_Museo_Egizio_Turin_C_1791_p02.jpg"
SKIP_NO_ENGLISH = {"20": "Birch summarises the table of the fourteen tribunals and translates only the rubric",
                   "111": "Birch prints only 'In text and rubric this Chapter is a repetition of Chapter CVIII'",
                   "121": "Birch prints only 'Same as Chapter XIII'"}

# German position labels of the TLA, in English
LABELS = [
    (r"^Titelzeile(?: (\d))?$", lambda m: "title" + (f" {m.group(1)}" if m.group(1) else "")),
    (r"^(\d+)\. Tor$", lambda m: f"gate {m.group(1)}"),
    (r"^(\d+) Zeilen unter (\d+)\. Tor$", lambda m: f"{m.group(1)} lines below gate {m.group(2)}"),
    (r"^unter (\d+)$", lambda m: f"below {m.group(1)}"),
    (r"^Zeile$", lambda m: "line"),
    (r"^(\d+)\. Zeile$", lambda m: f"line {m.group(1)}"),
    (r"^Zeile als Beginn für (.*)$", lambda m: f"line opening {m.group(1)}"),
    (r"^(?:2|zwei) Zeilen über Spalte (.*)$", lambda m: f"2 lines above columns {m.group(1)}"),
    (r"^waagerecht unter Spruchende ergänzt$", lambda m: "added horizontally below the end of the spell"),
    (r"^(oberes|mittleres|unteres) Register, von rechts nach links$",
     lambda m: {"oberes": "upper", "mittleres": "middle", "unteres": "lower"}[m.group(1)] + " register, right to left"),
    (r"^Beischrift zum Verstorbenen$", lambda m: "caption of the deceased"),
    (r"^Beischrift zu Maat$", lambda m: "caption of Maat"),
    (r"^zwischen Maat und dem Verstorbenen$", lambda m: "between Maat and the deceased"),
    (r"^an der Waage, über der Figur des Horus$", lambda m: "at the balance, above Horus"),
    (r"^über der linken Seite der Waage$", lambda m: "above the left side of the balance"),
    (r"^Beischrift zu Thot$", lambda m: "caption of Thoth"),
    (r"^Gottheiten vor Thot$", lambda m: "gods before Thoth"),
    (r"^Totenfresserin$", lambda m: "the Devourer"),
    (r"^im Schrein des Osiris$", lambda m: "in the shrine of Osiris"),
    (r"^[\da-z,]+$", lambda m: m.group(0)),
]

# Short titles shown in the library (Birch's headings, shortened; a few in plainer words)
TITLE_OVERRIDES = {
    "1": "The beginning of the spells of going forth by day (the funeral)",
    "15": "Hymns to the rising and setting sun",
    "17": "The great spell of going forth by day",

    "64": "Going forth by day in a single spell",
    "110": "The Field of Offerings",
    "125": "The Hall of the Two Truths (the judgment of the dead)",
}


# --------------------------------------------------------------------------
def fetch(url, binary=False):
    out = subprocess.run(["curl", "-sL", "--compressed", "-m", "300", "-A", UA, url], capture_output=True, check=True).stdout
    if not out:
        raise RuntimeError(f"empty download {url}")
    return out if binary else out.decode("utf-8")


def source(sub, name, url):
    p = SRC / sub / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url, binary=True))
        time.sleep(0.3)
    return p


# ---------------------------- TLA TEI -------------------------------------
def render_word(el):
    def walk(e):
        tag = e.tag.replace(T, "")
        if tag == "fs":
            return e.tail or ""
        inner = (e.text or "") + "".join(walk(c) for c in e)
        if tag == "supplied":
            inner = f"[{inner}]" if e.get("reason") == "lost" else f"〈{inner}〉"
        elif tag == "surplus":
            inner = "{" + inner + "}"
        elif tag in ("damage", "unclear"):
            inner = f"⸢{inner}⸣"
        elif tag == "add":
            inner = f"\\{inner}/"
        elif tag == "gap":
            inner = "[…]"
        return inner + (e.tail or "") if tag != "w" else inner
    return re.sub(r"\s+", "", walk(el))


def label(raw):
    s = raw.strip().strip("[]").strip()
    for rx, fn in LABELS:
        m = re.match(rx, s)
        if m:
            return fn(m)
    raise ValueError(f"unknown TLA line label {raw!r}")


def tla_tokens(tid):
    p = source("aedtei", f"{tid}.xml", AED_RAW + f"{tid}.xml")
    root = ET.parse(p).getroot()
    title = root.findtext(f".//{T}titleStmt/{T}title")
    ab = root.find(f".//{T}body/{T}ab")
    toks = []

    def walk(e):
        tag = e.tag.replace(T, "")
        if tag == "lb":
            toks.append(("lb", label(e.get("n"))))
        elif tag == "w":
            toks.append(("w", render_word(e)))
        elif tag == "gap":
            toks.append(("gap",))
        else:
            for c in e:
                walk(c)
    for c in ab:
        walk(c)
    return toks, title


def tla_html(toks):
    out = []
    for t in toks:
        if t[0] == "lb":
            out.append(f"<sup>{t[1]}</sup>")
        elif t[0] == "w":
            out.append(t[1])
        else:
            out.append('<span class="lacuna">[…]</span>')
    return " ".join(out).replace("</sup> ", "</sup>").replace(" <sup>", "<br><sup>").lstrip()


def col_range(toks):
    labs = [t[1] for t in toks if t[0] == "lb"]
    nums = [l for l in labs if re.fullmatch(r"\d+", l)]
    parts = []
    if any(l.startswith("title") for l in labs):
        parts.append("title line")
    if nums:
        parts.append(f"columns {nums[0]}-{nums[-1]}" if len(nums) > 1 else f"column {nums[0]}")
    other = [l for l in labs if not re.fullmatch(r"\d+", l) and not l.startswith("title")]
    if other and not nums:
        parts.append(f"{len(other)} labelled lines ({other[0]} ... {other[-1]})" if len(other) > 1 else other[0])
    return ", ".join(parts)


# ---------------------------- Birch 1867 (three OCR texts) -----------------
B_START = "I. The Beginning of the Chapters of the coming forth"
B_END = "The following chapters, containing an adoration"
B_BREAK = re.compile(r"^\s*Digitized by", re.I)
B_PAGENUM = re.compile(r"^\W*\d{1,3}\W*$")
B_SIG = re.compile(r"^\s*(v\s*o\s*l|VOL|VoL|vOL)\b.*$|^\s*[A-Z]{1,2}\s?\d?\s*$|^\s*[a-z]( ?\d)?\s*$")  # signatures
B_ROMAN = re.compile(r"^[CLXVI]+\.\s*$")
B_FOOT = re.compile(r"^\W?(\d{2,3}|\d[!'’?\"]|[©®°*†‡§¢])\s*[A-Z“\"‘'(\[]")


def _is_runhead(s):
    if not s or B_ROMAN.match(s) or re.search(r"[a-z]", s):
        return False
    return bool(re.search(r"[A-Z]{4,}", s)) and len(s) < 70


def birch_clean(t):
    """Cut the translation out of one OCR text; drop running heads, page numbers, signatures and
    the footnotes standing before each page break; mark page breaks as ⟦PB⟧."""
    t = t[t.index(B_START):t.index(B_END)]
    lines = [l.rstrip() for l in t.split("\n")]
    kind = []
    for l in lines:
        s = l.strip()
        brk = B_BREAK.match(s) or (s and B_PAGENUM.match(s)) or (s and B_SIG.match(s)) or _is_runhead(s)
        kind.append("brk" if brk else "txt")
    n = len(lines)
    drop = [k == "brk" for k in kind]
    k = 0
    while k < n:
        if kind[k] == "brk":
            m = k - 1
            while m >= 0 and (not lines[m].strip() or kind[m] == "brk"):
                m -= 1
            while m >= 0:                                   # footnote blocks just above the break
                b = m
                while b - 1 >= 0 and lines[b - 1].strip() and kind[b - 1] == "txt":
                    b -= 1
                if B_FOOT.match(lines[b].strip()) and not drop[b]:
                    for q in range(b, m + 1):
                        drop[q] = True
                    m = b - 1
                    while m >= 0 and not lines[m].strip():
                        m -= 1
                else:
                    break
            while k < n and kind[k] == "brk":
                k += 1
        else:
            k += 1
    kept = []
    for l, d in zip(lines, drop):
        if d:
            if kept and kept[-1] != "⟦PB⟧":
                kept.append("⟦PB⟧")
        else:
            kept.append(l)
    out = "\n".join(kept)
    out = re.sub(r"\s*⟦PB⟧\s*", "\n⟦PB⟧\n", out)
    return re.sub(r"\n{3,}", "\n\n", out)


def roman_value(s):
    s = s.replace("H", "II").replace("U", "II").replace("n", "II").replace("T", "I").replace("l", "I").replace("1", "I")
    s = s.replace("m", "III")
    if not re.fullmatch(r"[CLXVI]+", s):
        return None
    v = {"C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
    return sum(-v[c] if i + 1 < len(s) and v[c] < v[s[i + 1]] else v[c] for i, c in enumerate(s))


def roman(n):
    out = ""
    for v, r in ((100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


HEAD_RX = re.compile(r"^\W{0,3}([CLXVIlHUTn1m]{1,9})[\.,]\s*(\(Bis\)\s*)?(The|Another|A |Said|S\.aid|\[The|Chapter|Thechapter|\[Tue|\[)")
# headings the automatic pass misses because the OCR garbled the numeral (Birch numbers; 1370 = his CXXXVII bis)
HEAD_MANUAL = {
    15: r"^XV\.\s*$", 16: r"^XVI\.\s*$", 26: r"^XXYI\. The chapter", 38: r"^XXXVIIL The chapter of Life",
    43: r"^XLIIL The chapter", 44: r"^XLIY\. The chapter", 48: r"^XLVin\. The chapter", 52: r"^LIL The chapter of Not eating",
    53: r"^LIIL The chapter", 54: r"^LIY\. The chapter", 57: r"^LVH The chapter", 66: r"^LXVL A chapter",
    68: r"^LXVHL A chapter", 74: r"^LXXLV\. The chapter", 83: r"^LXXXin\. The chapter", 87: r"^LXXXVTL The chapter",
    103: r"^dll\. The chapter", 115: r"^CXY\. The chapter", 124: r"^CXXIY\. The chapter", 126: r"^CXXVI\.\s*$",
    134: r"^CXXXIY\. The Adoration to the Sun", 137: r"^CXXXVIL The chapter of Lighting a Spark",
    1370: r"^CXXXVII\. \(bit\.\)", 139: r"^C XXXIX\. The Adoration", 141: r"^CXLL The book", 143: r"^CXLIII\.\s*$",
    145: r"^CXLV\. Things", 150: r"^CL\.\s*$", 151: r"^CLI\.\s*$", 152: r"^CLII\.\s*$", 157: r"^CLVIL The chapter",
    158: r"^CL VIII\. The chapter", 162: r"^CLXII\.\s*$", 163: r"^CLX1IJ\. The chapter",
}


def birch_mark(text):
    lines = text.split("\n")
    found = {}
    exp = 1
    for i, l in enumerate(lines):
        m = HEAD_RX.match(l)
        if not m:
            continue
        n = roman_value(m.group(1))
        if n and n not in found and exp <= n <= exp + 3 and (not found or i > max(found.values())):
            found[n] = i
            exp = n + 1
    for n, rx in HEAD_MANUAL.items():
        hits = [i for i, l in enumerate(lines) if re.search(rx, l)]
        assert len(hits) == 1, (n, rx, hits)
        found[n] = hits[0]
    missing = [k for k in range(1, 167) if k not in found]
    assert not missing, missing
    pos = sorted(found.items(), key=lambda kv: kv[1])
    assert [k for k, _ in pos] == sorted(found, key=lambda k: (k if k != 1370 else 137.5)), "headings out of order"
    for n, i in pos:
        lines[i] = f"⟦CH{n:04d}⟧ " + lines[i]
    return "\n".join(lines)


def birch_tokens(text):
    text = re.sub(r"(⟦PB⟧\s*)+", " ⟦PB⟧ ", text)
    text = re.sub(r"\n\s*\n", " ¶ ", text)
    return text.split()


GARB = re.compile(r"[®™©°†‡§¢•«»*■□▪]")


def _g(w):
    return GARB.sub("", w)


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def birch_align(A, Y):
    sm = difflib.SequenceMatcher(None, [_norm(w) for w in A], [_norm(w) for w in Y], autojunk=False)
    m = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1):
                m[i1 + k] = [Y[j1 + k]]
        elif tag == "replace":
            m[i1] = Y[j1:j2]
            for k in range(i1 + 1, i2):
                m[k] = []
        elif tag == "delete":
            for k in range(i1, i2):
                m[k] = []
        elif tag == "insert":
            m[("ins", i1)] = Y[j1:j2]
    return m


DROPPED = []
WORDS = set(x.strip().lower() for x in open("/usr/share/dict/words")) if Path("/usr/share/dict/words").exists() else set()


def birch_vote(A, B, C):
    """A (the first scan, with chapter markers) is the base text. A word of A is replaced only when
    the other two scans agree on a different reading that is a known word and more frequent in the
    three texts together; punctuation marks of A survive only when one of the others has them."""
    mB, mC = birch_align(A, B), birch_align(A, C)
    freq = Counter(_norm(_g(w)) for w in A + B + C)
    punct = re.compile(r"^[\W\d_]+$")

    def known(w):
        n = _norm(w)
        return bool(n) and (n in WORDS or freq[n] >= 6 or (n.endswith("s") and n[:-1] in WORDS)
                            or (n.endswith("ed") and n[:-2] in WORDS) or (n.endswith("ing") and n[:-3] in WORDS))
    # runs that neither other scan has and that are running heads or scanner marks
    orphan = set()
    i = 0
    while i < len(A):
        j = i
        while j < len(A) and not A[j].startswith("⟦") and A[j] != "¶" and not mB.get(j) and not mC.get(j):
            j += 1
        run = A[i:j]
        if run and (all(not re.search("[a-z]", x) for x in run if len(x) > 2) or "Google" in run or "Digitiz" in run):
            orphan.update(range(i, j))
            DROPPED.append(" ".join(A[i:j]))
        i = max(j, i + 1)
    out = []
    for i, a in enumerate(A):
        if i in orphan:
            continue
        if a in ("⟦PB⟧", "¶") or a.startswith("⟦CH"):
            out.append(a)
            continue
        a2 = _g(a)
        b = [_g(x) for x in mB.get(i, [])]
        c = [_g(x) for x in mC.get(i, [])]
        b1 = b[0] if len(b) == 1 else None
        c1 = c[0] if len(c) == 1 else None
        if not a2.strip():
            continue
        if punct.match(a2):
            if b1 and c1 and b1 == c1 and re.fullmatch(r"I\W*", b1):
                out.append(b1)                       # 'I' read as '!' or '1' in the base scan
            elif a2 in (b1, c1) or (re.fullmatch(r"\[\?\]\W*|\(\?\)\W*|[\.\,;:!\?\]\)—\-]+", a2) and (b1 or c1)):
                out.append(a2)
            continue
        if b1 and c1 and b1 == c1 and _norm(b1) == _norm(a2):
            out.append(b1)
            continue
        similar = difflib.SequenceMatcher(None, _norm(a2), _norm(b1 or "")).ratio() >= 0.5 or \
            (len(_norm(a2)) <= 2 and len(_norm(b1 or "")) <= 2)
        if b1 and c1 and _norm(b1) == _norm(c1) and _norm(b1) != _norm(a2) and known(b1) and similar:
            if not known(a2) or freq[_norm(b1)] > freq[_norm(a2)]:
                out.append(b1)
                continue
        out.append(a2)
    return out, known


# OCR misreadings left after the vote (word for word; checked against the printed page images)
FIXES = {
    "Tiiou": "Thou", "Tiiy": "Thy", "Oiiris,": "Osiris,", "Oslrii,": "Osiris,", "Otlris": "Osiris", "Oslrl": "Osiris",
    "Ostri": "Osiris", "sniNE": "shine", "ttje": "the", "Ilapi,": "Hapi,", "Khnurn,": "Khnum,", "nny": "any",
    "I’asht,": "Pasht,", "fortli": "forth", "arhis": "arms", "hq,": "he,", "PUh.]": "Ptah.]", "uroeus.": "uraeus.",
    "ITndes.": "Hades.", "human-beaded": "human-headed", "Jackal-beaded": "Jackal-headed", "Docaased": "Deceased",
    "liis": "his", "Deceaied": "Deceased", "Anubii,": "Anubis,", "Ilawk,": "Hawk,", "IIall,": "Hall,", "raado": "made",
    "ymbollcal": "symbolical", "Sworda,": "Swords,", "Sworda,and": "Swords, and", "dUk,": "disk,", "plumei,": "plumes,",
    "the'water": "the water", "the’Land": "the Land", "from'its": "from its", "repretent": "represent",
    "-Deccaed": "Deceased", "mavest": "mayest", "Tcfnu.]": "Tefnu.]", "Tefuu,": "Tefnu,", "AmsetJ": "Amset.]",
    "[Ilermo-": "[Hermo-", "o^Purgatorial": "of Purgatorial", "Urtrus": "Uraeus", "Urteus,": "Uraeus,",
    "Scarabicus.]": "Scarabaeus.]", "scarabteus": "scarabaeus", "scaraboeus": "scarabaeus", "Scarabacus,": "Scarabaeus,",
    "scarabmus": "scarabaeus", "uneus": "uraeus", "uraci": "uraei", "Uriei": "Uraei", "ursei": "uraei",
    "cedal\\": "cedar.", "[Viguette.": "[Vignette.", "[Vignrttc.-": "[Vignette.—", "CynocephaluB-headcd": "Cynocephalus-headed",
    "Cyr.o-": "Cyno-", "cephalua": "cephalus", "Typbon-headcd": "Typhon-headed", "Staibcase.": "Staircase.",
    "Hauis": "Hades", "oddest": "Goddess", "Ptah-Sokharia.": "Ptah-Sokharis.", "gagjbfuscated.": "go obfuscated.",
    "Decoa'd": "Deceased", "[mom]": "[morn]", "shiningfrom": "shining from", "Asp3.": "Asps.", "Osirt,": "Osiris,", "Iiii,": "Isis,",
    "ilorm,": "Horus,", "Nrphthjr]": "Nephthys]", "Ix": "six", "Oil": "Oh", "lvhenem": "Khenem", "[Estnun],": "[Eshmun],",
    "nottake[n": "not take[n", "[oris]": "[or is]", "them[?J.": "them[?].",
}
# words lost in the base scan (a large initial or a damaged line), restored from the other two scans
PHRASE_FIXES = [
    (30, "heart was my mother my heart was my mother", "My heart was my mother — my heart was my mother"),
    (3, "oh Tum! oh Tam! coming", "Oh Tum! oh Tum! coming"),
    (44, "open is the Gate! open is the Gate the Spirits", "Open is the Gate! open is the Gate! the Spirits"),
    (63, "his return, he has not been scorched", ". . . . his return, he has not been scorched"),
]
JUNK_TOKENS = {"Google", "Digitized", "Igitized", "Digitiz", "23G"}


def birch_text(tokens, known):
    """Tokens of one chapter -> list of paragraphs."""
    toks = [FIXES.get(t, t) for t in tokens if t not in JUNK_TOKENS]
    toks = [t for t in toks if t]
    out = []
    for t in toks:
        if t == "¶":
            out.append("\n\n")
        elif t == "⟦PB⟧":
            out.append(" ⟦PB⟧ ")
        else:
            out.append(t + " ")
    s = re.sub(r"[ \t]+", " ", "".join(out))

    def dehyph(m):                       # line-end hyphen: join when the joined word is known
        a, b = m.group(1), m.group(2)
        return a + b if known(a + b) else a + "-" + b
    s = re.sub(r"(\w+)- +(?:⟦PB⟧ +)?([a-z]\w*)", dehyph, s)
    s = re.sub(r" *⟦PB⟧ *", " ", s)
    s = re.sub(r"(\S) ([!;:,\.])(?=\s|$)", r"\1\2", s)           # 'Osiris !' -> 'Osiris!'
    s = re.sub(r"([!\?,;:])(?:\s*\1)+", r"\1", s)                 # doubled marks from the OCR
    s = re.sub(r"([!\?])”\1", r"\1”", s)
    s = re.sub(r" *\n\n *", "\n\n", s)
    pars = [p.strip() for p in re.split(r"\n{2,}", s) if p.strip()]
    keep = []
    for k, p in enumerate(pars):
        p = re.sub(r"^[a-z] (?=\[?\s*Vignette)", "", p)      # a signature letter run into the next line
        w = p.split()
        unknown = sum(1 for x in w if not known(x.strip("[]().,;:!?“”\"'‘’")))
        if len(p.strip()) <= 3 or re.match(r"^\W{0,3}\[?\s*Here ends?\b", p):
            continue                                          # Birch's group markers, not translation
        if k and len(w) <= 10 and (unknown / len(w) >= 0.5) and p.lstrip("0123456789 ").startswith(("[", "(", "|", "$", "C", "£")):
            continue                                          # garbled black-letter group titles
        if keep and re.match(r"^[a-z]", p) and not re.search(r"[\.!\?\]\)]”?$", keep[-1]):
            keep[-1] += " " + p                               # a paragraph broken by a blank line in the OCR
            continue
        keep.append(p)
    while keep and len(keep) > 1 and re.fullmatch(r"\W{0,3}[\[\(][^\[\]]{0,60}[\]\)]\W{0,3}", keep[-1]) and "Vignette" not in keep[-1]:
        keep.pop()                                            # a group title of Birch at the end of a chapter
    return keep


def birch_chapters(force=False):
    texts = []
    for ident, fname in BIRCH_SCANS:
        p = source("birch", fname, f"https://archive.org/download/{ident}/{fname}")
        texts.append(birch_clean(p.read_text(encoding="utf-8", errors="replace")))
    A = birch_tokens(birch_mark(texts[0]))
    B, C = birch_tokens(texts[1]), birch_tokens(texts[2])
    voted, known = birch_vote(A, B, C)
    chs, cur, buf = {}, None, []
    for t in voted:
        m = re.match(r"⟦CH(\d{4})⟧", t)
        if m:
            if cur is not None:
                chs[cur] = buf
            cur, buf = int(m.group(1)), []
        else:
            buf.append(t)
    chs[cur] = buf
    out = {}
    for n, toks in chs.items():
        pars = birch_text(toks, known)
        if n != 1370:                                          # the OCR numeral of the heading -> the printed one
            toks = pars[0].split()
            k = 0
            while k < 2 and k < len(toks) and re.fullmatch(r"\W{0,2}[CLXVIlHUTnm1Ydi]{1,9}[\.,:]?", toks[k]):
                k += 1
            pars[0] = roman(n) + ". " + " ".join(toks[k:])
        out[n] = pars
    for n, a, b in PHRASE_FIXES:
        hits = [i for i, p in enumerate(out[n]) if a in p]
        assert len(hits) == 1, (n, a)
        out[n][hits[0]] = out[n][hits[0]].replace(a, b)
    return out


def birch_numbers(spell):
    n = int(spell)
    if n <= 143:
        return [n]
    if n == 144:
        return [144, 145]
    return [n + 1]


def english_html(pars):
    return "".join(f"<p>{html.escape(p, quote=False)}</p>" for p in pars)


def split_125(pars):
    def at(prefix):
        hits = [i for i, p in enumerate(pars) if p.startswith(prefix)]
        assert len(hits) == 1, (prefix, hits)
        return hits[0]
    b, c, v = at("1. Oh Str"), at("Hail, ye Gods who are in the Hall of Truth"), at("In the Hall of Justice")
    d_par = [i for i in range(c, v) if "Said by a pure person" in pars[i]]
    assert len(d_par) == 1, d_par
    i = d_par[0]
    head, tail = pars[i].split("Said by a pure person", 1)
    end = [k for k in range(v, len(pars)) if pars[k].startswith("“ Says the Osiris") or pars[k].startswith("Says the Osiris")
           or pars[k].startswith("“Says the Osiris")]
    assert end, "end of the vignette texts"
    return {"125A": pars[:b], "125B": pars[b:c], "125C": pars[c:i] + [head.strip()],
            "125D": ["Said by a pure person" + tail] + pars[i + 1:v], "125V": pars[v:end[0] + 1]}


# ---------------------------- images --------------------------------------
def photo_name(p):
    return f"Book_of_the_Dead_of_Iuefankh,_papyrus_-_Museo_Egizio_Turin_C_1791_p{p}.jpg"


def scan_file(k):
    return f"turin1791-photo-{k:02d}.jpg"


VIGNETTE_FILE = "turin1791-spell125-vignette-detail.jpg"


def build_scan(name, dest_name, force):
    dest = SCAN_DIR / dest_name
    if dest.exists() and not force:
        return
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    raw = SRC / "photos" / name
    if not raw.exists():
        raw.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(6):
            data = fetch(COMMONS_REDIRECT + name, binary=True)
            if data[:3] == b"\xff\xd8\xff":
                break
            time.sleep(10 * (attempt + 1))
        raw.write_bytes(data)
    im = Image.open(raw).convert("RGB")
    if max(im.size) > 2600:
        im.thumbnail((2600, 2600), Image.LANCZOS)
    im.save(dest, "JPEG", quality=86, optimize=True)


# ---------------------------- mapping -------------------------------------
def roll_units():
    """Units in roll order: spell numbers, with 125 split into the TLA parts A-D and the vignette V."""
    units, texts = [], {}
    for title, tid in TLA:
        m = re.match(r"^(V )?Tb (\d+)(?: ?([a-i]|[〈〈][A-D1-4][〉〉]))?$", title)
        assert m, title
        n = str(int(m.group(2)))
        if n == "125":
            u = "125V" if m.group(1) else "125" + m.group(3).strip("〈〉〈〉")
        else:
            u = n
        if u not in texts:
            units.append(u)
            texts[u] = []
        texts[u].append(tid)
    return units, texts


def plates_of(spell):
    out = []
    for item in PLATES_TXT.split():
        pl, ch = item.split(":")
        nums = set()
        for part in ch.split(","):
            a, _, b = part.partition("-")
            nums.update(range(int(a), int(b or a) + 1))
        if int(spell) in nums:
            out.append(pl)
    return out


def plate_span(pls):
    return pls[0] if len(pls) == 1 else f"{pls[0]}-{pls[-1]}"


def photos_of(unit, units):
    idx = units.index(unit)
    out = []
    for ph in PHOTOS:
        a, b = units.index(ph["first"]), units.index(ph["last"])
        if a <= idx <= b:
            out.append(ph)
    assert out, unit
    return out


def where(unit, ph, units):
    if unit in ph["anchors"]:
        return ph["anchors"][unit]
    a, b = units.index(ph["first"]), units.index(ph["last"])
    on = units[a:b + 1]
    i = on.index(unit)
    left = [u for u in on[i + 1:] if u in ph["anchors"]]
    right = [u for u in reversed(on[:i]) if u in ph["anchors"]]
    sp = lambda u: "Spell " + (u if not u.startswith("125") else "125 " + u[3:])
    if unit == ph["first"]:
        return f"its last columns are at the right-hand edge, continued from photograph {ph['n'] - 1}"
    if unit == ph["last"]:
        return f"it begins near the left-hand edge and continues on photograph {ph['n'] + 1}"
    return (f"it stands between {sp(right[0]) if right else 'the right-hand edge'} and "
            f"{sp(left[0]) if left else 'the left-hand edge'} on this photograph (the roll is continuous, so every spell "
            f"between two identified spells lies between them)")


# ---------------------------- entries -------------------------------------
GENERAL = (
    "<p>The Book of the Dead, in Egyptian the spells for going forth by day, is a collection of funerary spells written on "
    "papyrus rolls and placed in burials from the New Kingdom to the Roman period. Each roll was made for one person, with "
    "spells taken from a large repertoire and illustrated with drawings (vignettes). This library gives one complete roll: "
    "the papyrus of Iuefankh in the Museo Egizio, Turin (Cat. 1791), written in the Ptolemaic period (332-30 BCE) and "
    "coming from Thebes. Richard Lepsius published it in 1842 and divided it into 165 chapters; his numbering is still the "
    "standard numbering of the spells, and it is used here.</p>")
READING = (
    "<p>The Egyptian is the transliteration of the Thesaurus Linguae Aegyptiae (edition by Burkhard Backes), with the "
    "column number of the spell before each column; the numbers are those of Lepsius's plates. On the papyrus the text runs "
    "in vertical columns of cursive hieroglyphs from right to left along the roll; titles and some words are written in red. "
    "Signs restored by the editor are in square brackets, signs the scribe left out in angle brackets, superfluous signs in "
    "braces and damaged signs in half brackets. The English is the translation by Samuel Birch, published in 1867 and made "
    "from Lepsius's copy of this papyrus, so the English and the Egyptian come from the same manuscript. It was the first "
    "complete English translation of the Book of the Dead; many passages are now understood differently. Birch's own square "
    "brackets give his alternatives and explanations. The photographs are by the Museo Egizio; each shows a stretch of the "
    "roll, and the note of each section says where the spell stands on it.</p>")
NOTES = [
    "Birch's English was taken from three scans of Bunsen's Egypt's Place in Universal History, vol. V (1867), on the "
    "Internet Archive. The three OCR texts were aligned word by word and each word was settled by their agreement; running "
    "heads, page numbers, footnote markers and footnotes were removed. Some OCR errors may remain, chiefly in proper names.",
    "Birch uses the terms and name forms of his time: Hades, Aahlu (Elysium), Tum for Atum, Seb for Geb, Anup for Anubis, "
    "Phoenix or Bennu for the heron.",
    "Labels such as 'title line' or 'gate 1' before a line of the Egyptian translate the position labels of the TLA.",
    "The TLA has no hieroglyphic encoding for these texts, so only the transliteration is shown.",
]
EXTRA = {
    "15": "Spell 15 is a series of hymns to the sun; the TLA divides it into nine parts (a-i) with continuous column "
          "numbers, given here together because Birch's English is not divided in the same way.",
    "17": "Spell 17 is the longest spell of the roll (95 columns): a statement of the dead man's identity with the creator "
          "god, with explanations ('What is that?') added to almost every sentence. It runs over three photographs.",
    "110": "The vignette of the Field of Offerings (Lepsius pl. XLI) shows the dead man ploughing, reaping and sailing in "
           "the fields of the next world. The TLA gives its captions as a second text (upper, middle and lower register); "
           "they follow the columns here, and Birch's English describes the vignette in his divisions I-III.",
    "125": "Spell 125 is the judgment of the dead in the Hall of the Two Truths. Its sections follow the TLA: A, the "
           "address to the god and the first declaration of innocence; B, the second declaration (the 'negative "
           "confession') to the 42 judges, written in two registers; C, the address to the gods of the hall and the "
           "questioning at the door; D, the closing rubric; V, the captions of the judgment vignette, which shows the "
           "weighing of the heart before Osiris. A separate detail photograph of the vignette is added to section V.",
    "144": "Birch prints the rubric at the end of this spell as a separate chapter (his CXLV); both parts are given here.",
    "145": "The TLA divides this spell into four parts with continuous column numbers; they are given here together.",
    "146": "The TLA gives the names of the portals (gates 1-15) and the following columns as two texts; they are given here "
           "together.",
    "149": "The TLA divides this spell into three parts with continuous column numbers; they are given here together.",
    "101": "The TLA gives the rubric of this spell as a second text; it follows the spell here.",
}


def short_title(spell, pars):
    if spell in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[spell]
    h = re.sub(r"^[CLXVI]+\.\s*", "", pars[0]).strip()
    h = re.sub(r"^(The chapters? of|The [Bb]ook of|The)\s+", "", h)
    h = h.rstrip(". ")
    words = h.split()
    if len(words) > 14:
        h = " ".join(words[:14]).rstrip(",;") + " ..."
    return h[:1].upper() + h[1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    for ph in PHOTOS:
        build_scan(photo_name(ph["p"]), scan_file(ph["n"]), args.force)
    build_scan(VIGNETTE_P, VIGNETTE_FILE, args.force)

    birch = birch_chapters()
    (SRC / "birch" / "vote_log.json").write_text(json.dumps({"dropped_runs": DROPPED}, indent=1,
                                                             ensure_ascii=False), encoding="utf-8")
    units, texts = roll_units()
    for ph in PHOTOS:
        for u in (ph["first"], ph["last"], *ph["anchors"]):
            assert u in units, (ph["n"], u)

    # sections, grouped by spell
    spells = []
    for u in units:
        s = u[:3] if u.startswith("125") else u
        if s not in spells:
            spells.append(s)
    b125 = split_125(birch[125])
    entries, rows = [], []
    order = 0
    for spell in spells:
        if spell in SKIP_NO_ENGLISH:
            continue
        sp_units = [u for u in units if (u[:3] if u.startswith("125") else u) == spell]
        bn = birch_numbers(spell)
        all_pars = [p for b in bn for p in birch[b]]
        secs, scans = [], []
        for u in sp_units:
            toks_all, titles = [], []
            for tid in texts[u]:
                toks, title = tla_tokens(tid)
                titles.append(title)
                toks_all.extend(toks)
            egy = tla_html(toks_all)
            eng_pars = b125[u] if spell == "125" else all_pars
            phs = photos_of(u, units)
            pages = [f"{KEY}/{scan_file(ph['n'])}" for ph in phs]
            if u == "125V":
                pages.append(f"{KEY}/{VIGNETTE_FILE}")
            pls = plates_of(spell)
            label_u = u if not u.startswith("125") else "125 " + u[3:]
            note = (f"Turin 1791, Spell {label_u} (TLA {', '.join(titles)}: {col_range(toks_all)}; Lepsius 1842, pl. "
                    f"{plate_span(pls)}). ")
            for ph in phs:
                note += (f"Photograph {ph['n']} of 31 (Commons {photo_name(ph['p'])}): {where(u, ph, units)}. ")
            if u == "125V":
                note += (f"The detail photograph (Commons {VIGNETTE_P}) shows the whole vignette, from the enthroned Osiris "
                         "to the adoring deceased, in one frame. ")
            note += ("Checked by eye: the photographs were matched to Lepsius's plates by their vignettes, red titles and "
                     "framed compartments, and the overlapping edges of neighbouring photographs were compared. ")
            if spell == "125":
                note += ("Birch's chapter CXXV was divided at the same points as the TLA text: B begins with his '1. Oh "
                         "Strider', C with 'Hail, ye Gods who are in the Hall of Truth', D with 'Said by a pure person', V "
                         "with 'In the Hall of Justice'.")
            elif spell == "144":
                note += "The English is Birch's chapters CXLIV and CXLV (his CXLV is the rubric of this spell)."
            elif int(spell) >= 145:
                note += f"Birch numbers this spell {roman(bn[0])} (his numbers run one ahead of Lepsius's from 145 on)."
            sec = {
                "section": u,
                "original_ref": f"pTurin 1791, Tb {label_u}; Lepsius pl. {plate_span(pls)}; {col_range(toks_all)}",
                "original_text": egy,
                "text": english_html(eng_pars),
                "scan_pages": pages,
                "scan_note": note.strip(),
            }
            secs.append(sec)
            scans += [p for p in pages if p not in scans]
        order += 1
        eid = f"{PREFIX}spell-{int(spell):03d}"
        title_short = short_title(spell, birch[bn[0]])
        title = f"Book of the Dead, Spell {spell}: {title_short} (papyrus of Iuefankh)"
        phs_all = sorted({ph["n"] for u in sp_units for ph in photos_of(u, units)})
        pls = plates_of(spell)
        heading = re.sub(r"^[CLXVI]+\.\s*", "", birch[bn[0]][0]).strip()
        spell_par = (f"<p>Spell {spell} (Birch: '{html.escape(heading)}') is on Lepsius's plate"
                     f"{'s' if len(pls) > 1 else ''} {plate_span(pls)} and on photograph"
                     f"{'s' if len(phs_all) > 1 else ''} {', '.join(map(str, phs_all))} of the 31 Museo Egizio photographs "
                     f"of the roll.{(' ' + EXTRA[spell]) if spell in EXTRA else ''}</p>")
        e = {
            "id": eid, "slug": eid, "title": title,
            "language": "Egyptian (TLA transliteration) / English",
            "source": "Papyrus of Iuefankh, Turin, Museo Egizio Cat. 1791 (Museo Egizio photographs, CC0) + TLA "
                      "transliteration (ed. B. Backes, CC BY-SA 4.0) + English of Samuel Birch (1867, public domain)",
            "description": f"Spell {spell} of the Book of the Dead in the Turin papyrus of Iuefankh (Ptolemaic period): "
                           f"{title_short[:1].lower() + title_short[1:]}, with the TLA transliteration and Birch's 1867 English.",
            "introduction": GENERAL + "\n\n" + spell_par + "\n\n" + READING,
            "translator_notes": NOTES,
            "translation": secs,
            "verification": {
                "scan_source": f"Museo Egizio, Turin, photographs of Cat. 1791 on Wikimedia Commons ({COMMONS_CAT}), e.g. "
                               f"{COMMONS}{photo_name(PHOTOS[0]['p'])}",
                "scan_license": "CC0 1.0 (Museo Egizio, as stated on Wikimedia Commons)",
                "scan_manuscript": "Turin, Museo Egizio, Cat. 1791 (papyrus of Iuefankh), Book of the Dead, Ptolemaic period "
                                   "(332-30 BCE), from Thebes",
                "scan_mapping": "Spell order, plate and column numbers from Lepsius, Das Todtenbuch der Aegypter (1842), whose "
                                "plates reproduce this papyrus and are headed by their chapter numbers; the TLA uses the same "
                                "numbers. The 31 Museo Egizio photographs (Commons p034 to p04, from the start to the end of "
                                "the roll) were each compared by eye with Lepsius's plates: vignettes, red titles and framed "
                                "compartments identify the spells on each photograph, and the overlapping edges of "
                                "neighbouring photographs were compared side by side. Positions in the notes are measured "
                                "from the left edge of the photograph.",
                "scan_mapping_urls": [COMMONS_CAT, LEPSIUS,
                                      "https://github.com/simondschweitzer/aed-tei/tree/" + AED_COMMIT + "/files"],
                "scan_local_paths": scans,
                "original_text_source": "Thesaurus Linguae Aegyptiae, Totenbuch, pTurin Museo Egizio 1791, edition by Burkhard "
                                        "Backes; TLA database extract of January 2018 (urn:nbn:de:kobv:b4-opus4-29190), TEI by "
                                        f"S. D. Schweitzer, AED-TEI (commit {AED_COMMIT[:8]}), texts "
                                        + ", ".join(t for u in sp_units for t in texts[u]),
                "original_text_license": "CC BY-SA 4.0 (BBAW / SAW Leipzig, Thesaurus Linguae Aegyptiae; AED-TEI)",
                "translation_source": "Samuel Birch, The Funereal Ritual or Book of the Dead, in C. C. J. Bunsen, Egypt's Place "
                                      "in Universal History, vol. V (London: Longmans, Green, 1867), translated from Lepsius's "
                                      "edition of this papyrus; OCR of https://archive.org/details/bub_gb_fCSiSJ7OxSIC, "
                                      "https://archive.org/details/egyptsplaceinun00cottgoog and "
                                      "https://archive.org/details/india.history.resource.41142, compared word by word",
                "translation_license": "public domain (published 1867; Samuel Birch died 1885)",
                "translator": "Samuel Birch (1867)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{eid}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False), encoding="utf-8")
        entries.append(e)
        rows.append({
            "id": eid, "slug": eid, "order": order, "title": title, "author_id": "iuefankh-papyrus",
            "language": "Egyptian", "era": "Ancient Near East", "tradition": "egyptian", "category": "sacred-text",
            "date_approx": "Ptolemaic period (332-30 BCE); papyrus from Thebes", "century": -3,
            "source": e["source"], "description": e["description"],
            "themes": ["book-of-the-dead", "afterlife", "egypt", "funerary-texts", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": p, "caption": (f"Papyrus of Iuefankh (Turin 1791), photograph "
                                                         f"{int(re.search(r'photo-(\d+)', p).group(1))} of 31"
                                                         if "photo-" in p else "Papyrus of Iuefankh, vignette of Spell 125")}
                                for p in scans]},
        })
    # remove stale entries of this prefix
    keep = {e["id"] for e in entries}
    for f in PUB.glob(f"{PREFIX}*.json"):
        if f.stem not in keep:
            f.unlink()
    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Book of the Dead (papyrus of Iuefankh, Turin)", "group": "Egypt",
            "date_sort": -250,
            "author_name": "Papyrus of Iuefankh, Turin Museo Egizio Cat. 1791 (Ptolemaic period)",
            "source_url": COMMONS_CAT,
            "critical_edition": "Thesaurus Linguae Aegyptiae, ed. Burkhard Backes (2018 data, AED-TEI)",
            "translator_name": "Samuel Birch (1867)",
            "original_lang_label": "Egyptian · TLA transliteration",
            "original_lang_code": "egy",
            "edition_label": "",
            "search_terms": "book of the dead coming forth by day going forth by day spells chapters iuefankh turin 1791 "
                            "lepsius todtenbuch birch funereal ritual negative confession weighing of the heart judgment "
                            "hall of the two truths field of reeds field of offerings osiris ra thoth anubis",
            "description": "The Book of the Dead in the papyrus of Iuefankh (Turin, Ptolemaic period), the roll from which "
                           "Lepsius took the standard numbering of the spells: spell by spell, with the TLA transliteration, "
                           "Samuel Birch's 1867 English made from the same papyrus, and the Museo Egizio photographs of "
                           "the whole roll.",
        },
        "texts": rows,
        "authors": [{
            "id": "iuefankh-papyrus", "name": "Papyrus of Iuefankh (Book of the Dead)", "dates": "Ptolemaic period, 332-30 BCE",
            "century": -3, "era": "Ancient Near East", "tradition": "egyptian", "language": "Egyptian",
            "bio": "A Book of the Dead roll made for Iuefankh, now in the Museo Egizio, Turin (Cat. 1791); Lepsius's 1842 "
                   "edition of it gave the spells their standard numbers.",
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(entries)} entries, {sum(len(e['translation']) for e in entries)} sections; {COLL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
