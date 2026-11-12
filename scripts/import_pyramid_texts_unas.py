#!/usr/bin/env python3
"""
import_pyramid_texts_unas.py -- the Pyramid Texts in the pyramid of Unas (Saqqara,
end of the 5th Dynasty, c. 2350 BCE): every inscribed wall, utterance by utterance.

Collection key: pyramid-texts-unas   (entries verified-pyramid-texts-unas-*)

Chain of evidence
-----------------
1. OBJECT   The inscribed walls of the burial apartments of the pyramid of Unas at
            Saqqara, in situ: sarcophagus chamber (north wall in three registers,
            east gable, south wall, east wall, west gable), the passage to the
            antechamber (north and south walls), the antechamber (west gable, west
            wall, south wall, east gable, east wall, north wall) and the corridor
            (west and east walls). Column numbers are Sethe's numbering of the Unas
            (W) columns, 1-649, as carried in the TLA text.
2. SCANS    Seventeen wall photographs, one per inscribed surface, as published on
            Pyramid Texts Online (Vincent Brown, pyramidtextsonline.com, pages
            *h.html). They are montages of the black and white photographs taken by
            L. F. Husson under the direction of Natacha Rambova for A. Piankoff, The
            Pyramid of Unas (Bollingen Series XL.5, Princeton 1968) (site credits page).
            Terms of use are not stated; used with credit under the owner's rule 9.
            Mapping: for every photograph the columns were counted by eye on zoomed
            bands with a pixel ruler, the count compared with the TLA column numbers
            of that wall, and the start edge fixed by the content of the first and
            last columns (see WALLS[...]['check']). Two TLA texts run over a corner
            (PT 219: W 240-261 south wall, W 262-268 east wall; PT 260: W 452 west
            wall, W 453-460 south wall); their sections list both photographs.
3. ORIGINAL Thesaurus Linguae Aegyptiae, Pyramid Texts of Unas, edition by Doris
            Topmann, from the TLA database extract of January 2018
            (urn:nbn:de:kobv:b4-opus4-29190) as converted to TEI by S. D. Schweitzer,
            AED-TEI (github.com/simondschweitzer/aed-tei, commit 462c722e, files/),
            CC BY-SA 4.0. The repository's concordance file lists only 144 of these
            texts; the other 87 are present in files/ (found by their TEI headers:
            date "Unas", place Saqqara, title "PT n"; PT 219 has no date and was
            added by hand). The TLA has no Unicode hieroglyphs for these texts, so only
            the transliteration is given. PT 271 (W 492-494) is not in the extract.
4. ENGLISH  Samuel A. B. Mercer, The Pyramid Texts in Translation and Commentary,
            vol. 1 (New York: Longmans, Green & Co., 1952), as transcribed by the
            Internet Sacred Text Archive (sacred-texts.com/egy/pyt/). sacred-texts.com
            blocks automated access, so the pages were taken from the Internet
            Archive's Wayback Machine (captures of 2019; data/sources/.../mercer/cdx.txt).
            Public domain in the United States: published 1952, no renewal of
            copyright found in the Copyright Office records. Mercer translates
            Sethe's composite text of every pyramid, utterance by utterance with
            Sethe's section numbers; each utterance's English is matched to the TLA
            Unas text of the same utterance number. Mercer's separate headings,
            postscripts and variants from other pyramids are left out.

Usage:  python3 scripts/import_pyramid_texts_unas.py           (build)
        python3 scripts/import_pyramid_texts_unas.py --force   (re-download images)
"""

import argparse
import html
import io
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
KEY = "pyramid-texts-unas"
PREFIX = f"verified-{KEY}-"
SRC = ROOT / "data" / "sources" / KEY
SCAN_DIR = ROOT / "site" / "assets" / "scans" / KEY
PUB = ROOT / "translations" / "published"
COLL = ROOT / "data" / "collections" / f"{KEY}.json"
TODAY = date.today().isoformat()

T = "{http://www.tei-c.org/ns/1.0}"
XID = "{http://www.w3.org/XML/1998/namespace}id"
AED_COMMIT = "462c722e0323e05641aea2eee8cdf1e27303d939"
AED_RAW = f"https://raw.githubusercontent.com/simondschweitzer/aed-tei/{AED_COMMIT}/files/"
PTO = "https://pyramidtextsonline.com/"
WAYBACK = "https://web.archive.org/web/{ts}id_/{url}"
UA = "TheosisLibrary/1.0 (https://theosislibrary.com; non-commercial research)"

# --------------------------------------------------------------------------
# TLA texts of the pyramid of Unas (utterance, AED-TEI id), in column order.
# --------------------------------------------------------------------------
TEXTS = [
    ("23", "CE3VRL7YXRDRVPJCNON7QCJW4U"), ("25", "WYFIEB4XPRALJLODJBAIPQGPPI"), ("32", "TDAK5SDHLNHVZJ6NERLKMXSHGM"), ("34", "VGPK6Q6WTVGJ7ADUSJLLJEMB2E"),
    ("35", "7G4OKBMSK5E7XD5EWLW3QGWVOQ"), ("36", "SUV3LQUGENA77HX5P6ERWYCU3I"), ("37", "ELSTQHVY45C57OD6OGCZUXRS7Q"), ("38", "4GTWFEIOUJAYJOVZUWQ7PZCVAI"),
    ("39", "NEEX247XSRFZJA7W7XQZGIILTY"), ("40", "TKDQHIVBOBAD3HJMG5SZZUINFA"), ("41", "TBO4KMCS3JEGBB2KWRCCRHTFQU"), ("42", "5CFUTNVED5GR5K73SVBNM2OT3A"),
    ("32", "AHMSDTEIBRFLZABH6R5VCLJUNA"), ("43", "Z3JPSSGOFVE4HFFD4WIXB7RQJA"), ("44", "67LYPMJSBRCN7NAJY6OL43V4YI"), ("45", "IORCXHX2GVAMNIIIS5GDGMB4ZI"),
    ("46", "XZO6NFGIABAB3OCITB3I4AEUCM"), ("47", "RZIGSNETL5DDJLVOOG2PEMDHNM"), ("48", "APKVKHBWSZGC3KBKIYOS3ZENXU"), ("49", "YNS5B3PCMZEDZHRVFMY7B6CMNY"),
    ("50", "HXVXQV4AM5HAHHU527LOXIT77Y"), ("51", "GJGQZWE6Q5EDHOY2SI4XFUFTWE"), ("52", "Q7T6757XZVDKRACOUK7QAU72E4"), ("53", "C4OHAC6LRZBKVGVNA4HWDV7IHE"),
    ("54", "NKRWE2ZNENAJ7BZEAI4DEYD4OA"), ("55", "YNNWA4TIBJC5DPSJE4B5YCHUME"), ("56", "Z3GF4XSZGRH5NOQLYQRPYMHRRY"), ("57", "HXYHG5GOEFBEXAW6TQ5QMW5HJA"),
    ("72", "E5SFATUBYRGHTFVKQ3JVDM3CWQ"), ("73", "X2PDRHHABNDDNHS677FFHZWDS4"), ("74", "XURIER3CAZHCPFXZSMW5VRVNIE"), ("75", "KADMKHYFPREQNENWK33RNKENFI"),
    ("76", "VFNHE7VU6NHEPA7B6X47YGFI5U"), ("77", "E3VCHHHEFBACFHUAN4CCERPZVQ"), ("78", "CUCMO4XFP5ATBAPV536H4HEG44"), ("79", "F3ARSBWGPJE5NAETNJZP6TNFXA"),
    ("81", "UL5GAPGNJBCDTBRKZ3OH2MJRTM"), ("25", "D7FXXPG4LFBGBMNPTTXLOIIXPA"), ("32", "4HOOJO42GJEOZFVKVC2BFJGCEQ"), ("82", "YTPFHCGJ6BGDJA6NSYAEWND3Z4"),
    ("83", "ES65UU54UZCWTKI3TDHF6JUUVQ"), ("84", "HLI2WRSO6JEIRNGBBIE3FM563U"), ("85", "SJEDMMDGXRAHLC44HYJIFNNNJY"), ("86", "L7ZN2HCZ4NCLJF3CMOHISU47O4"),
    ("87", "2RBVPSP3ZFCT7EMXOI2X3ASGLM"), ("88", "NHPPFHB6Y5ALXG4FZFWUFF3QTQ"), ("89", "KO4FLVTW7JECTMIQQSN2U7E2NU"), ("90", "GXN5SAKTKFFOPJU6RPJCXHBCWE"),
    ("91", "L445MVZG75CY7AY6CLINVCU4ZA"), ("92", "AE3U4PTBGRG7BIFJER3WQV2GWI"), ("93", "O6L76W7F2RCOLLPNQXHDUP5RUQ"), ("94", "Q4FIWH7XVBFXRGQ2KN3ES3ZZKI"),
    ("95", "VVDBEPFWDND67BKTYQ2LTRWFAA"), ("96", "5XVOVC6JHRGYBMGKML6NFDLUFU"), ("108", "AZX42CRMT5FOTLAI6JPT4DWZAE"), ("109", "45KK3LE4UVGODO6X7Z6K4HS6CE"),
    ("110", "QE3UYHKZCZAEVABWGNIBOHGWBM"), ("111", "ZIWKXR4QSJC2HD4NFW5W3MDINU"), ("112", "IAHBVVGJZVDIHIAHQUQ3E4EODQ"), ("113", "NBVANXNNSVE6JDDTJDBCMLEQKE"),
    ("114", "SV7VUVIX75CINM4YOCHT7KHS5U"), ("115", "NRMEPRZ3ZNEXTHSNSQCJRRXWDU"), ("116", "R6RDF66UCZDPPJ2MBXS57JDS2Q"), ("117", "FRJ35WWBAZG6HFE42SHLIIKWWY"),
    ("118", "JLNJIYLHC5CBZDNG6SR7OFH36E"), ("119", "MW2IYSQRM5B7RM3GFA7OO22ZKE"), ("120", "YRLTPMBH6REHJG7PY4IW5H6ONM"), ("121", "M2TBYCBWGJA3XATVWL6FZFILGY"),
    ("122", "WLY6APNWG5DTPFWWC44BS2FRII"), ("123", "UNI5E3DUJZCCJMSURVFHUNMG6I"), ("124", "NR5VBCCRJRBSPKSJHDFQGRMPTA"), ("125", "NBDUOS5PLJFLPGVVNQAXISWFBI"),
    ("126", "F6VZMTNMJNHP5NDY73JV32OFNA"), ("127", "LOAJTPNWGRATHHGVVQYUGI22TI"), ("128", "2BSTZWDNWVBWNJ3PI6I2NCFZRA"), ("129", "ZHZZEXBFYZGVROVE7GFIOZR7SA"),
    ("130", "C2C4YKOJTJHHDBQDT7R4IOXZJE"), ("131", "SO75XSVSAJG4HFFVSNNPS762BM"), ("132", "7WET7VSMWZBPXJTYLELHBR3FSE"), ("133", "QLL6EURGPBFALE7WTAF2GVZCAI"),
    ("134", "O57T7F5TNVBCXB62IIWZPVBMNU"), ("135", "4XGBBWO4YRDB3ASZIS3V3NZSPU"), ("136", "KN7LHUDX6VCQBFI2PZYDAYGWBA"), ("137", "WN4JI64DZVBEZKJOX2Z3RSN4V4"),
    ("138", "H2YJPS5D5JFOFKCRHTFLSJYIKY"), ("139", "3SKHUMUDWNBGDNTVDNLL4C6MMQ"), ("140", "7PELI3IESVAHRJJOWXES74WTNM"), ("141", "MRB4N3TDIFC2TM3THGE75AQZR4"),
    ("142", "JPRTHZ7MOFFABMOH35HPTYS3SQ"), ("143", "RNTPAN2J5RBPJKA6LIY45WRIVM"), ("144", "NLEQD7R43FGEVLT6XF373GCTCQ"), ("145", "KKOP7JZJD5GWVN5ACG2ALTEZRU"),
    ("146", "AWHUJOZDEVCSHKQLDE5WOYPM3U"), ("147", "BNMVUHO6YBC6RIELHK6CTSENT4"), ("148", "RXLVEMG7H5GS3PPZYODORKYH4U"), ("149", "G47GLGZJKJG5JNGFR72WQ5NRAI"),
    ("150", "HTG2GHPWDVAPBG4UEPMCVASXQE"), ("151", "D66VWRB4GVEB3AMVDSQMQADPKM"), ("152", "7WTSOVIXFZDDNDLRSQ6GYRPHAI"), ("153", "JAP62I6Z5BGP7BY45B4R355M5E"),
    ("154", "FKPHDHXQUZDO3J5G4AVKOWWZO4"), ("155", "VEUVAJZNKJAEXBC252IOSZ3Y2A"), ("156", "QNC2UO7TXNA6NJ2KWBUU2GPWZA"), ("157", "K5ANUGBLV5DPLLXBMRFJOWLQNA"),
    ("158", "Z4USDCPXK5FUPHIL67PM2XRV6A"), ("159", "537OXCS3VZCQ7FS4MF7CMSSGS4"), ("160", "6DOOZWJU5RDSZIHOFSUO2D52RE"), ("161", "EM2SEX5VMFFZFJ3MCGHZ6JQEYQ"),
    ("162", "DNZTUDZE4BFKVFPUAUMOSDYYAA"), ("163", "BCQ56UJUSFEERAIQAWRB6FOCUM"), ("164", "OQUAWSQTV5GR3BMZJTT2PGKZAY"), ("165", "2X73ASP4XFAHVMUPEA5OKNSYAE"),
    ("166", "7OQR4ICWWVETJNIHYOITKWBMJM"), ("167", "A3XGNKFBRFHADLJBATYRK22DSM"), ("168", "LGYU6IWSMJEGJDXFRQQ3GC6TQI"), ("169", "7Y43FVK7WZAD3G37GYMZLG776Q"),
    ("170", "UDWYNNJZVJFKLOTJYJD5IIXBKA"), ("171", "HSCY6QF2HFGZZFNMY2VRZNNECE"), ("204", "TO4NWLUC6VD4BE5XDDL3XCFZNY"), ("205", "KXEWJOROLZD2VFIMCDI3MZ2L7I"),
    ("207", "XKM43GV3RNHBXMFG4HBBZOGFBQ"), ("209", "LA3HXSVEJFFQDFQ6FVI4YISLGE"), ("210", "YR6RRJBT7JERNMCX53QOUS3PVE"), ("211", "5YN2JC2OMNALLIGFM7FNTHVL2Q"),
    ("212", "GWL76GB3V5DARMLIBOMSH2J7CA"), ("213", "TF2LOMXASJFZLLVT7N4FRIOTUM"), ("214", "S7RQGCGRAJGB7FLNAX52B3HVDM"), ("215", "XAKREPY7ANEHFGJLEE7ONNRH2Y"),
    ("216", "LPSDFR3NERAP3MSPNRE7WGMJFU"), ("217", "FZQ6IM7ENFHHROXB2W6PTYMXNE"), ("218", "MWZLJP3NWJBBNLIJ6HTAJQVI4U"), ("219", "LL7OMQELWZDY7KOZ2UUBVSSVH4"),
    ("220", "JARS7QOU2NEMROJYT32RLXVL5A"), ("221", "XZGBO2VDSFBYBM2HMUXYZQXEHU"), ("222", "USXOQHMRHJDX3LJKRIGZHHPSXI"), ("223", "MGTSNHTSLBBBRMUUAVVSGBJRLY"),
    ("224", "AQXZDO2EIVCCBK24S5ICOLSXLE"), ("226", "4WVXFJZFLNAYHP3Y5O5SLWD7DA"), ("227", "BA3SJHBVFFAWHPFRE57E73IJPA"), ("228", "Z3UH6TF6LJFJDCJGV2AEFUMCHA"),
    ("229", "TLEYIU4DF5A43NTNAJ7MRPMFFM"), ("230", "FQ2UTSQQ3NEU7PPTWWGJJ45QRM"), ("231", "5IRGWKNNNVGQ5E7KY53BX6PLCI"), ("232", "UZFCUMXJXNDSLPU7DJKKUUMYFY"),
    ("233", "I7DRARBJKBBP5BUYBIOYN4MI6I"), ("234", "Q7WNWM5IARGNRHPQFLTJYYIWAI"), ("235", "XXB5LOVMXJGATOOU6KMICV2GE4"), ("236", "GNWO6Z6OOZAZ3MOTCVRD5TJXNM"),
    ("238", "B7XOG6AD4RGJHD3DBJFWIEGOAI"), ("237", "V4OTWFEINFFGDNAAOACAYNKXR4"), ("239", "PQYJ3H6RAFCB5NPIOT23EH4T2E"), ("240", "FQ4WGS62RBATZC5PZZAUW4NATY"),
    ("241", "GTCTE3XYOREV5LPVZICBLTNQIM"), ("242", "MIHGGVD75BANVIWR3MPI3K6PBE"), ("243", "OYCTDSOI4VFKVAJXPY7XAK4UPE"), ("199", "TEYACGBAPVFCXDUXWYWBIG5UZM"),
    ("32", "TIFUGMELFNBCTCKNVV45UFWMVE"), ("23", "USO7VZUDJJH2HLGGXVAJL673RM"), ("25", "KKYQBYXMR5FZNEXN67GHQG7ALA"), ("200", "SNX4ZG56WZGB5DJXXAPFTZOAUE"),
    ("244", "NNBXBQDR25BXHFZRJ47LQNTCBQ"), ("245", "LQS7MCBIWJEUBBADVMCSZUWNHE"), ("246", "PUZHMOWV3FDERA7JNBRAD3BPYQ"), ("247", "SNKQ4BEL5VDMDM7R762AATFYRE"),
    ("248", "SI2FK5UDSZBHNF7GXWOJTWJPUA"), ("249", "BUXDVJA2CRBV7DMHHZKYN27ZFI"), ("250", "2XN5YDF5Q5GQLJW2EBCPZTNWF4"), ("251", "F4V3SKGHJZH3NH7LYR2X2VM27Y"),
    ("252", "42MZX3WYQZDGTPRX7FEKPQLRPQ"), ("253", "T63PAYRG7BGZNMTV6XPIW2CUOA"), ("254", "LJWVROTIJJGRLCE7A6IYACJHCA"), ("255", "5HUBHABMRBHH5EZVI6P7LVCCJY"),
    ("256", "63KOXQC5GJHZPLQ4KQM6KVSKYY"), ("257", "WEJWYAVJBNHNZPEHKDPXW4QCGM"), ("258", "ZZZCXTQETZEUVN5XLKO6TUYXFI"), ("260", "RFFC6NC2DRAQ5AZERHPHMIVZTM"),
    ("261", "MDTCBQUF4VBT7EURTOXHFSOO3Y"), ("262", "GZCQVLC3VJEIPHRXNQ6XLSSBBA"), ("263", "NFZYFUEJZJGXVCSOGMFCUFX7KM"), ("267", "7I34C6KP7RC6POB3FI5TSGGMUU"),
    ("268", "X45ANH3NFREGZJKROGSMVLUS2M"), ("269", "5WZWA4T5XVHRBGRHD2RXKOUB54"), ("270", "KWURO2F7MRARNOQUMCDLKWAXQA"), ("272", "LKAXLZLLG5HFNN27BJT7TCVFO4"),
    ("273 + PT 274", "BRJCKLT7KNED5EKQX5DWGX3T4A"), ("275", "SB4Q2TH2E5CNJDR4WMX63Z3FXM"), ("276", "DPTKJV36EBDTNESD7GLL3PXFWY"), ("278", "HRGYVZUHZJCNVK5BAD4PB3GMSM"),
    ("277", "NNSOQGCNUBCFVMBZ6QBQ6Z2ZNM"), ("279", "LGTRUBFFXJH6TLH2UBHK3ITCKU"), ("281", "LTCKPYCK2VGPRNRQMA3TWFXZAA"), ("280", "APTLA54XXZCGDKV4YVRNWEYMUI"),
    ("282", "UKJYFS6HWNHNHHV6BW2JRQHYYI"), ("283", "LB5UD2BAANGAPJUV5O4LSRB5KM"), ("284", "3O3ER5NZHBFHVJQMEZOXYWUASA"), ("285", "QTEXZIYCNRBHNH7WNZGOAFD3II"),
    ("286", "HXF6TMY7ZBEFFIQ2IR2ZKFSMBU"), ("287", "WXKDHQUE5BBDPIYQF66EVMACVU"), ("288", "FWNAGXLTVJHYBPB5EVUKSJT7PI"), ("290", "KDP65JDUC5FJNHN2X2QAL74FMQ"),
    ("289", "AEZ5AKY3VVA43P3HGBY2NE62VY"), ("291", "ZGU3PB7YB5HHDMSO3HYCHY5USI"), ("292", "PHBJV3V5OZC3JKKWAQDSRLSQBI"), ("293", "J4EXFY7JJVEMLPLITXKMJILJ6E"),
    ("294", "XI5WHTAR75B65C5L7XMRSX5JNQ"), ("295", "JFODJ3ZRTRFAVGAB5QF756QTRA"), ("296 + PT 297", "LAFCWI37HNFRBLON6X7RGVVROQ"), ("298", "YRABA56A4ZF2DF322XYLDFW2JQ"),
    ("299", "4KOW5ZNIEVGRTJRF2APQSEFX54"), ("300", "C5XEDMCN3NETTD2M6HOCGTOM7A"), ("301", "7JLX3LVKY5C5RM2S323QLSH4EA"), ("302", "ZI3U3TNFEFBY7D4NUGT6WMGU7E"),
    ("303", "LBUJ5R4FKBECNF3FRMS4FES2EE"), ("304", "A3USFOX5Y5F2VLGIQ2OJXRN55E"), ("305", "74ESL4BGT5DPTHBGBJ7VQEFYEI"), ("306", "3OKMEWIUAND2XAHSACCABANLZI"),
    ("307", "SKRMP6GA6VA2TNNBAAICFR3GUU"), ("308", "6GTM6SX4VJE47JJJITKBWHA5V4"), ("309", "YBWWGYQIHFHXXEYCYNSNDC6QE4"), ("310", "5S5RBN4EKVBWHNPUF2L4AAW66I"),
    ("311", "UKVJJQLZXBCDHDYDT56GAJAJJQ"), ("312", "R6AG5SSQIZEAZIBS7RA3PZLYIA"), ("313", "BQMOEVIMQZHRLL72R7BGA4SELE"), ("314", "KQ5TVTCMGBGGBGKVE7GDO3YMSA"),
    ("315", "6DQ2OCMBOJB43E2RU6LDLG3UVI"), ("316", "TLVAW2FZEFHQJNJH6EEPOZD2VY"), ("317", "GU5EXSLELVFQDGPWFQTRNGJKYE"), ("318", "7MY4L4JTPJHYLH4QDCHDF7C6OQ"),
    ("319", "AIBUH7NGNFBD5EJGUEN7Z26VKA"), ("320", "YQHBJBNEWJGBPBOBR4DJSXYJ7U"), ("321", "6EFWDBITKZASVN5X7ALAOAYVSM"),
]
# TLA texts that the Unas edition combines: their Mercer utterances
MERCER_KEYS = {"273 + PT 274": ["273-274"], "296 + PT 297": ["296", "297"]}


def rng(a, b):
    return [str(i) for i in range(a, b + 1)]


# --------------------------------------------------------------------------
# Walls: physical columns in order from the start edge of the photograph.
# 'check' records what was verified by eye on the photograph.
# --------------------------------------------------------------------------
WALLS = [
    dict(key="sarc-north-1", slug="sarcophagus-north-wall-register-1", pto="SarcNorth1R.jpg", page="sarcnorth1rh.html",
         file="sarc-north-register-1.jpg", room="sarcophagus chamber", wall="north wall, upper register",
         title="Utterances 23-57", cols=rng(1, 55), start="left", start_dir="west",
         check="55 columns on the photograph, as many as W 1-55; the columns follow each other from left (west) to right (east) "
               "although the signs face right. Checked on the image: the leftmost column has the Unas cartouche in mid-column "
               "(W 1 'Wsjr jṯi̯ n=k msḏḏ.w Wnjs'), the four rightmost columns each open with the cartouche and end in an offering "
               "label at the foot (W 52-55 'Wnjs m n=k ...')."),
    dict(key="sarc-north-2", slug="sarcophagus-north-wall-register-2", pto="SarcNorth2R.jpg", page="sarcnorth2rh.html",
         file="sarc-north-register-2.jpg", room="sarcophagus chamber", wall="north wall, middle register",
         title="Utterances 72-116", cols=rng(56, 61) + ["61+1"] + rng(62, 109), start="left", start_dir="west",
         check="55 columns on the photograph: W 56-109 and the extra column that the TLA numbers 61+1 (in PT 77). "
               "Checked on the image: the five leftmost columns open with 'Osiris Unas' (W 56-60), the next four do not "
               "(PT 77, W 61-63), and the ten rightmost columns again open with 'Osiris Unas' (W 100-109)."),
    dict(key="sarc-north-3", slug="sarcophagus-north-wall-register-3", pto="SarcNorth3R.jpg", page="sarcnorth3rh.html",
         file="sarc-north-register-3.jpg", room="sarcophagus chamber", wall="north wall, lower register",
         title="Utterances 117-171", cols=rng(110, 128) + rng(130, 165), start="left", start_dir="west",
         check="55 columns on the photograph, as many as W 110-128 and 130-165 (the numbering has no W 129 and the wall has "
               "no column for it). Checked on the image: the offering counts at the foot of the columns are four strokes in the "
               "nine leftmost columns (W 110-118), one stroke in the next sixteen (W 119-135) and two strokes from the 26th "
               "column on (W 136-164)."),
    dict(key="sarc-east-gable", slug="sarcophagus-east-gable", pto="SarcEastGH.jpg", page="sarceastgableh.html",
         file="sarc-east-gable.jpg", room="sarcophagus chamber", wall="east gable",
         title="Utterances 204-212", cols=rng(166, 205), start="right", start_dir="south",
         check="40 columns under the gable, as many as W 166-205, from the right-hand (south) corner to the left-hand (north) "
               "corner. Checked on the image: the second column from the right corner shows the hoe, two water signs and chick "
               "of ḥnn.w (W 167), and the owls of the repeated 'jm' of W 204 stand in the second column from the left corner."),
    dict(key="sarc-south", slug="sarcophagus-south-wall", pto="SarcSouth.jpg", page="sarcsouthh.html",
         file="sarc-south-wall.jpg", room="sarcophagus chamber", wall="south wall",
         title="Utterances 213-219", cols=rng(206, 261), start="right", start_dir="west",
         check="56 columns on the photograph (the leftmost partly cut by the edge), W 206 at the right-hand (west) end to "
               "W 261 at the left-hand (east) end; with the 38 columns of the east wall this gives exactly W 206-299. Checked "
               "on the image: the rightmost column opens with hꜣ and the Unas cartouche and ends with three ankh signs "
               "(ꜥnḫ.w, end of W 206); the next column repeats the owl and sledge of 'm Jtm' (W 207)."),
    dict(key="sarc-east", slug="sarcophagus-east-wall", pto="Sarceast.jpg", page="sarceasth.html",
         file="sarc-east-wall.jpg", room="sarcophagus chamber", wall="east wall",
         title="Utterances 220-224", cols=rng(262, 299), start="right", start_dir="south",
         check="38 text columns between the palace-facade borders at both edges, W 262 at the right-hand (south) end to "
               "W 299 at the left-hand (north) end, around the doorway to the passage. Checked on the image: the second "
               "column from the left shows near its foot the three crested ibises of ꜣḫ.w in W 298, and 56 + 38 columns on "
               "the south and east walls equal W 206-299."),
    dict(key="sarc-west-gable", slug="sarcophagus-west-gable", pto="SarcWestGH.jpg", page="sarcwestgableh.html",
         file="sarc-west-gable.jpg", room="sarcophagus chamber", wall="west gable",
         title="Utterances 226-243", cols=rng(300, 317) + rng(319, 340), start="right", start_dir="north",
         check="40 columns counted by eye on the lower band of the gable (39 dividers at a 43 px pitch), as many as W 300-317 "
               "and 319-340 (the numbering has no W 318), from the right-hand (north) corner to the left-hand (south) corner. "
               "Checked on the image: the only cluster of cartouches is in the 15th-18th columns from the right (W 314-317, "
               "eleven cartouches) and the 10th-11th columns from the left (W 330-331)."),
    dict(key="passage-north", slug="passage-north-wall", pto="PassageNorth.jpg", page="passagenorthh.html",
         file="passage-north-wall.jpg", room="passage between sarcophagus chamber and antechamber", wall="north wall",
         title="Utterances 199, 32, 23, 25 and 200", cols=rng(341, 359), start="left", start_dir="west",
         check="19 columns (partial ones at both edges), W 341 at the left-hand (west) edge to W 359 at the right. Checked on "
               "the image: the repeated kꜣ arms of PT 25 fill the 11th and 12th columns from the left (W 351-352); the "
               "cartouche is low in the 7th column (W 347) and high in the 9th (W 349), as in the text."),
    dict(key="passage-south", slug="passage-south-wall", pto="PassageSouth.jpg", page="passagesouthh.html",
         file="passage-south-wall.jpg", room="passage between sarcophagus chamber and antechamber", wall="south wall",
         title="Utterances 244-246", cols=rng(360, 378), start="right", start_dir="west",
         check="19 columns (partial ones at both edges), W 360 at the right-hand (west) edge to W 378 at the left. Checked on "
               "the image: two cartouches in the second column from the right (W 361 'jyi̯ n=ṯ Wnjs pn Nw,t' twice), the three "
               "stars of sbꜣ.pl in the fifth (W 364) and a cartouche in mid-column in the eighth (W 367)."),
    dict(key="ante-west-gable", slug="antechamber-west-gable", pto="AntewestGH.jpg", page="antewestgableh.html",
         file="ante-west-gable.jpg", room="antechamber", wall="west gable",
         title="Utterances 247-253", cols=rng(379, 415), start="right", start_dir="north",
         check="37 columns under the gable, as many as W 379-415, from the right-hand (north) corner to the left-hand (south) "
               "corner. Checked on the image: the five columns at the right corner have no cartouche (W 379-383) and the sixth "
               "has two (W 384); the second and third columns from the left corner have one each (W 414, 413)."),
    dict(key="ante-west", slug="antechamber-west-wall", pto="Antewest.jpg", page="antewesth.html",
         file="ante-west-wall.jpg", room="antechamber", wall="west wall",
         title="Utterances 254-258", cols=rng(416, 452), start="right", start_dir="north",
         check="37 columns counted by eye, W 416 at the right-hand (north) edge to W 452 at the left-hand (south) edge, around "
               "the doorway to the passage. Checked on the image: the second column from the right opens with the Unas "
               "cartouche (W 417 'Wnjs fꜣ,t m jtj=f Gbb'); the leftmost column shows the goose and the bull of 'j Gbb kꜣ Nw,t' "
               "(W 452, the first column of PT 260)."),
    dict(key="ante-south", slug="antechamber-south-wall", pto="AnteSouthWall.jpg", page="antesouthh.html",
         file="ante-south-wall.jpg", room="antechamber", wall="south wall",
         title="Utterances 260-272", cols=rng(453, 495), start="right", start_dir="west",
         check="43 columns counted by eye, W 453 at the right-hand (west) edge to W 495 at the left-hand (east) edge. Checked "
               "on the image: the fifth and eighth columns from the right open with the Unas cartouche (W 457 'Wnjs m jr,t=f', "
               "W 460 'Wnjs n nsr=ṯn')."),
    dict(key="ante-east-gable", slug="antechamber-east-gable", pto="AnteeastGH.jpg", page="anteeastgableh.html",
         file="ante-east-gable.jpg", room="antechamber", wall="east gable",
         title="Utterances 273-276", cols=rng(496, 531), start="right", start_dir="south",
         check="36 columns under the gable at a regular 48 px pitch, as many as W 496-531, from the right-hand (south) corner "
               "to the left-hand (north) corner. Checked on the image: the short column in the right corner ends in stars "
               "(W 496 'gp p,t jḥy sbꜣ.pl', 'the sky is overcast, the stars are darkened')."),
    dict(key="ante-east", slug="antechamber-east-wall", pto="Anteeast.jpg", page="anteeasth.html",
         file="ante-east-wall.jpg", room="antechamber", wall="east wall",
         title="Utterances 277-301", cols=rng(532, 544) + ["544+1"] + rng(545, 566), start="right", start_dir="south",
         check="36 columns counted by eye between the edge at the right and the palace-facade border at the left: W 532-566 "
               "and the extra column that the TLA numbers 544+1, W 532 at the right-hand (south) end. Checked on the image: the "
               "30th and 31st columns from the right have cartouches (W 560-561) and the three columns to their left have none "
               "(W 562-564)."),
    dict(key="ante-north", slug="antechamber-north-wall", pto="AnteNorthWall.jpg", page="antenorthh.html",
         file="ante-north-wall.jpg", room="antechamber", wall="north wall",
         title="Utterances 302-312", cols=rng(567, 609), start="left", start_dir="west",
         check="43 columns counted by eye, W 567 at the left-hand (west) edge to W 609 at the right, next to the palace-facade "
               "border. Checked on the image: the leftmost column has an ankh near the top (W 567 'sbš p,t ꜥnḫ Spd,t') and the "
               "second a cartouche high up (W 568 'n ḥtm ns,t Wnjs')."),
    dict(key="corridor-west", slug="corridor-west-wall", pto="Corridoor-west.jpg", page="corridorwesth.html",
         file="corridor-west-wall.jpg", room="corridor", wall="west wall",
         title="Utterances 313-317", cols=rng(610, 629), start="left", start_dir="south", lost={"610"},
         check="W 610 lies in the broken area at the left-hand (south) edge and is almost entirely lost (the TLA restores most of "
               "it); the 19 visible columns are W 611-629. Checked on the image: the sixth visible column from the left has four "
               "cartouches (W 616 'Wnjs jmꜣḫ Wnjs ḥr-tp Wnjs jri̯ Wnjs'), the third two (W 613) and the rightmost one (W 629)."),
    dict(key="corridor-east", slug="corridor-east-wall", pto="Corridoor-east.jpg", page="corridoreasth.html",
         file="corridor-east-wall.jpg", room="corridor", wall="east wall",
         title="Utterances 318-321", cols=rng(630, 649), start="right", start_dir="south",
         check="20 columns, W 630 at the right-hand (south) edge to W 649 at the left. Checked on the image: the leftmost column "
               "has two cartouches (W 649), the third from the left shows the jackal and the ankh of W 647, and the seventh "
               "opens with a cartouche (W 643 'Wnjs grḥ'). The TLA gives no break for W 646, the fourth column from the left; "
               "its text runs on under 645."),
]
SPLIT_NOTES = {
    "219": "PT 219 runs from the south wall round the corner onto the east wall: W 240-261 are on the south wall, W 262-268 "
           "are the first seven columns at the right-hand (south) end of the east wall photograph.",
    "260": "PT 260 begins in the last column of the antechamber west wall (W 452, the leftmost column on the west wall "
           "photograph) and continues on the south wall (W 453-460).",
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


def tla_tokens(tid):
    p = source("aedtei", f"{tid}.xml", AED_RAW + f"{tid}.xml")
    root = ET.parse(p).getroot()
    meta = {"title": root.findtext(f".//{T}titleStmt/{T}title"), "wall": root.findtext(f".//{T}msName")}
    ab = root.find(f".//{T}body/{T}ab")
    toks = []

    def walk(e):
        tag = e.tag.replace(T, "")
        if tag == "lb":
            toks.append(("lb", e.get("n").strip().strip("[]")))
        elif tag == "w":
            toks.append(("w", render_word(e)))
        elif tag == "gap":
            toks.append(("gap",))
        else:
            for c in e:
                walk(c)
    for c in ab:
        walk(c)
    return toks, meta


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


def columns_of(toks):
    """Physical columns named by the line markers (labels such as '1a', '47/8a' are column feet)."""
    cols = []
    for t in toks:
        if t[0] == "lb" and not t[1].endswith("a"):
            if t[1] not in cols:
                cols.append(t[1])
    return cols


# ---------------------------- Mercer 1952 ---------------------------------
U_MAP = {"d": "ḏ", "t": "ṯ", "h": "ẖ", "D": "Ḏ", "T": "Ṯ", "H": "H̱"}
SKIP_HEAD = re.compile(r"^(Heading|Postscript|A Variant|Heading and postscript)", re.I)


def mercer_pages():
    cdx = (SRC / "mercer" / "cdx.txt").read_text().split("\n")
    for line in cdx:
        if not line.strip():
            continue
        ts, url = line.split()
        name = url.rsplit("/", 1)[1]
        source("mercer", name, WAYBACK.format(ts=ts, url=url))
    return sorted((SRC / "mercer").glob("pyt*.htm"))


def mercer_utterances():
    utt = {}
    for f in mercer_pages():
        if f.name in ("pyt00.htm", "pyt01.htm", "pyt02.htm", "pyt03.htm"):
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        i, j = t.find("<h3"), t.rfind("<HR>")
        body = t[i:j if j > i else len(t)]
        cur = None
        for m in re.finditer(r'<p align="center">(.*?)</p>|<p>(.*?)</p>', body, re.S | re.I):
            if m.group(1) is not None or re.match(r"\s*<i>Utterance\s+\d+</i>\.?\s*$", m.group(2) or "", re.I):
                h = re.sub(r"<[^>]+>", "", m.group(1) if m.group(1) is not None else m.group(2))
                h = re.sub(r"\s+", " ", h).strip().rstrip(".")
                if SKIP_HEAD.match(h):
                    cur = None
                    continue
                me = re.match(r"^End of (\d+)$", h)
                mu = re.match(r"^Utterances?,?\s+(\d+[A-Z]?)(?:\s*-\s*(\d+[A-Z]?))?(?:\.\s*(\d+[A-Z]?))?$", h)
                mn = re.match(r"^(\d+[A-Z]?)$", h)
                if me:
                    cur = me.group(1)
                elif mu and mu.group(3):                 # 'Utterances 49-52. 49'
                    cur = mu.group(3)
                elif mu and mu.group(2):                 # group heading 'Utterances 45-48'
                    cur = f"{mu.group(1)}-{mu.group(2)}"
                elif mu:
                    cur = mu.group(1)
                elif mn:
                    cur = mn.group(1)
                else:
                    cur = None
                continue
            p = re.sub(r'<A NAME="page_\d+">.*?</A>', "", m.group(2), flags=re.S | re.I)
            p = re.sub(r"\s+", " ", p).strip()
            if not p or cur is None:
                continue
            m96 = re.match(r"^(\d+)\.\s+(\d+[a-z]\..*)$", p)     # '96. 64d. To say ...' starts utterance 96
            if m96 and int(m96.group(1)) > 20:
                cur, p = m96.group(1), m96.group(2)
            if re.fullmatch(r"\d+\.", p):                         # '<p>116.</p>' starts utterance 116
                cur = p[:-1]
                continue
            utt.setdefault(cur, []).append(p)
    # 'Utterances 79-80' carries 54d, the offering line of PT 79 (Unas has no PT 80)
    utt["79"] = utt["79"] + utt.pop("79-80")
    return utt


def mercer_html(pars):
    lines, secs = [], []
    for p in pars:
        p = re.sub(r"<u>([A-Za-z])</u>", lambda m: U_MAP.get(m.group(1), m.group(1)), p)
        p = re.sub(r"<i>(.*?)</i>", r"<em>\1</em>", p, flags=re.S)
        p = re.sub(r"<(?!/?em>)[^>]+>", "", p)
        p = html.unescape(p)
        m = re.match(r"^(\d+[a-z]?)\.\s+(.*)$", p)
        if m:
            secs.append(m.group(1))
            lines.append(f"<sup>{m.group(1)}</sup>{m.group(2)}")
        else:
            lines.append(p)
    return "<br>".join(lines), secs


# ---------------------------- images --------------------------------------
def build_scan(w, force):
    dest = SCAN_DIR / w["file"]
    if dest.exists() and not force:
        return dest
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    raw = SRC / "photos" / w["pto"]
    if force or not raw.exists():
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_bytes(fetch(PTO + "images/" + w["pto"], binary=True))
    data = raw.read_bytes()
    assert data[:3] == b"\xff\xd8\xff", w["pto"]
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if max(im.size) <= 2600:
        dest.write_bytes(data)                 # already a JPEG of the right size: keep the bytes as published
        return dest
    im.thumbnail((2600, 2600), Image.LANCZOS)
    im.save(dest, "JPEG", quality=88, optimize=True)
    return dest


# ---------------------------- mapping -------------------------------------
COL_WALL = {}
for _w in WALLS:
    for _c in _w["cols"]:
        COL_WALL[_c] = _w["key"]
WALL_BY_KEY = {w["key"]: w for w in WALLS}


def span(cols):
    return cols[0] if len(cols) == 1 else f"{cols[0]}-{cols[-1]}"


def position(w, cols):
    lst, lost = w["cols"], w.get("lost", set())
    vis = [c for c in lst if c not in lost]
    here = [c for c in cols if c in lst]
    lost_here = [c for c in here if c in lost]
    shown = [c for c in here if c not in lost]
    parts = []
    if lost_here:
        parts.append(f"W {span(lost_here)} lies in the broken area at the {w['start']}-hand edge of the photograph and is "
                     f"almost entirely lost")
    if shown:
        a, b = vis.index(shown[0]) + 1, vis.index(shown[-1]) + 1
        where = f"column {a}" if a == b else f"columns {a}-{b}"
        kind = "visible columns" if lost else "columns"
        parts.append(f"W {span(shown)} {'is' if a == b else 'are'} {where} of the {len(vis)} {kind} on the photograph of the "
                     f"{w['room'].split(' between')[0]}, {w['wall']}, "
                     f"counted from the {w['start']}-hand ({w['start_dir']}) edge")
    return "; ".join(parts)


def sect_range(sects):
    """First-last section number, ignoring misprinted numbers far from the rest (e.g. '43m' for 431a)."""
    nums = sorted(int(re.match(r"\d+", x).group(0)) for x in sects)
    med = nums[len(nums) // 2]
    ok = [x for x in sects if abs(int(re.match(r"\d+", x).group(0)) - med) <= 60]
    if len(ok) < len(sects):                      # a misprint was dropped: give the paragraph numbers only
        n = [int(re.match(r"\d+", x).group(0)) for x in ok]
        return str(n[0]) if n[0] == n[-1] else f"{n[0]}-{n[-1]}"
    return ok[0] if len(ok) == 1 else f"{ok[0]}-{ok[-1]}"


def utt_label(title):
    return title[3:].replace(" + PT ", "-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    mercer = mercer_utterances()
    for w in WALLS:
        build_scan(w, args.force)

    # build one section per TLA text
    secs_by_wall = {w["key"]: [] for w in WALLS}
    distinct = set()
    for utt, tid in TEXTS:
        toks, meta = tla_tokens(tid)
        assert meta["title"] == f"PT {utt}", (tid, meta["title"], utt)
        cols = columns_of(toks)
        walls = []
        for c in cols:
            wk = COL_WALL[c]
            if wk not in walls:
                walls.append(wk)
        home = max(walls, key=lambda k: sum(1 for c in cols if COL_WALL[c] == k))
        label = utt_label(meta["title"])
        for n in re.findall(r"\d+", label):
            distinct.add(int(n))
        mkeys = MERCER_KEYS.get(utt, [utt])
        pars = []
        for i, mk in enumerate(mkeys):
            assert mk in mercer and mercer[mk], ("no Mercer text", mk)
            if i:
                pars.append(f"<i>Utterance {mk}</i>.")
            pars.extend(mercer[mk])
        eng, sects = mercer_html(pars)
        assert sects, utt
        egy = tla_html(toks)
        where = ". ".join(position(WALL_BY_KEY[k], cols) for k in walls)
        note = f"Unas W {span(cols)}: {where}."
        if label in SPLIT_NOTES:
            note += " " + SPLIT_NOTES[label]
        for k in walls:
            note += f" Wall check ({WALL_BY_KEY[k]['wall']}): {WALL_BY_KEY[k]['check']}"
        note += (" Mercer's English renders Sethe's composite text of this utterance from all pyramids; it can contain words "
                 "that are not in the Unas copy.")
        sec = {
            "section": label,
            "original_ref": f"PT {label} (Sethe §§ {sect_range(sects)}); Unas W {span(cols)}",
            "original_text": egy,
            "text": eng,
            "scan_pages": [f"{KEY}/{WALL_BY_KEY[k]['file']}" for k in walls],
            "scan_note": note,
        }
        secs_by_wall[home].append(sec)

    # unique section ids inside an entry (PT 32 twice on the upper register)
    for k, secs in secs_by_wall.items():
        seen = {}
        for s in secs:
            n = seen.get(s["section"], 0) + 1
            seen[s["section"]] = n
            if n > 1:
                s["section"] = f"{s['section']}-{n}"
                s["original_ref"] += f" (copy {n} on this wall)"

    general = (
        "<p>The Pyramid Texts are the oldest large body of Egyptian religious writing: spells, called utterances, for the "
        "resurrection of the dead king, his protection, his meals and his ascent to the sky, cut in vertical columns of "
        "hieroglyphs on the walls of the burial apartments of late Old Kingdom pyramids. The pyramid of Unas at Saqqara, the last "
        "king of the 5th Dynasty (about 2375-2345 BCE), is the first to carry them. Its sarcophagus chamber, the passage to the "
        "antechamber, the antechamber and the corridor hold 649 numbered columns of text; this library gives every column, wall "
        f"by wall, in seventeen entries ({len(distinct)} different utterances, some of them inscribed more than once).</p>")
    reading = (
        "<p>Each section is one utterance. The Egyptian is the transliteration of the Thesaurus Linguae Aegyptiae (edition by "
        "Doris Topmann), with Sethe's Unas column number (W) before each column; a number ending in 'a' marks the offering label "
        "at the foot of a column. Signs restored by the editor are in square brackets, signs the scribe left out in angle "
        "brackets, damaged signs in half brackets. The English is Samuel A. B. Mercer's translation of 1952. Mercer translates "
        "Sethe's composite text made from all the pyramids that have an utterance, so his wording can include clauses that are not "
        "in the Unas copy, and his section numbers (134a, 134b ...) are Sethe's paragraph numbers, not column numbers; he writes "
        "'N.' where the wall has the king's name. The photograph shows the whole wall; each section's note gives its columns "
        "counted from the edge where the text on that wall begins.</p>")
    wall_notes = {
        "sarc-north-2": " The TLA numbers one extra column in PT 77 as 61+1.",
        "sarc-north-3": " Sethe's numbering skips W 129; the wall has no column for it.",
        "sarc-south": " PT 219, the long litany of Osiris, continues round the corner onto the east wall (W 262-268); it is given "
                      "here in full, with both photographs.",
        "sarc-east": " The first seven columns at the right-hand end (W 262-268) carry the end of PT 219, which is given in full in "
                     "the entry for the south wall.",
        "sarc-west-gable": " Sethe's numbering skips W 318; the gable has 40 columns.",
        "ante-west": " The leftmost column (W 452) begins PT 260, which is given in full in the entry for the south wall.",
        "ante-south": " PT 260 begins on the west wall (W 452). PT 271 (the end of W 492, W 493 and the top of W 494) is not in "
                      "the TLA data used here and is therefore not given; the gap is shown by the column numbers.",
        "ante-east": " The TLA numbers one extra column in PT 293 as 544+1.",
        "corridor-west": " The southern end of the wall is broken: W 610, the first column of PT 313, is almost entirely lost on "
                         "the photograph, and the TLA restores most of its words.",
        "corridor-east": " The TLA text of PT 320 has no marker for the start of W 646; the words of W 645 and 646 stand together "
                         "under 645.",
    }

    entries, rows = [], []
    for order, w in enumerate(WALLS, start=1):
        secs = secs_by_wall[w["key"]]
        assert secs, w["key"]
        eid = PREFIX + w["slug"]
        n = len(w["cols"])
        utts = ", ".join(s["section"].split("-")[0] if re.fullmatch(r"\d+-\d", s["section"]) else s["section"] for s in secs)
        wall_par = (f"<p>This entry is the {w['wall']} of the {w['room']}: {n} columns of hieroglyphs, Sethe's W "
                    f"{w['cols'][0]}-{w['cols'][-1]}, which follow each other from the {w['start']}-hand ({w['start_dir']}) "
                    f"edge of the photograph. It holds the utterances {utts}.{wall_notes.get(w['key'], '')}</p>")
        title = f"Pyramid Texts of Unas: {w['title']} ({w['room'].split(' between')[0]}, {w['wall']})"
        scan = f"{KEY}/{w['file']}"
        scans = [scan] + [p for s in secs for p in s["scan_pages"] if p != scan]
        scans = list(dict.fromkeys(scans))
        e = {
            "id": eid, "slug": eid, "title": title,
            "language": "Egyptian (TLA transliteration) / English",
            "source": f"Pyramid of Unas, Saqqara, {w['room']}, {w['wall']} (photograph: L. F. Husson for A. Piankoff 1968, via "
                      "Pyramid Texts Online) + TLA transliteration (ed. D. Topmann, CC BY-SA 4.0) + English of S. A. B. Mercer "
                      "(1952, public domain in the US)",
            "description": f"The Pyramid Texts on the {w['wall']} of the {w['room']} in the pyramid of Unas (c. 2350 BCE), "
                           f"utterance by utterance, with the TLA transliteration and Mercer's English.",
            "introduction": general + "\n\n" + wall_par + "\n\n" + reading,
            "translator_notes": [
                "Mercer's separate headings, postscripts and variants taken from other pyramids are left out.",
                "Letters follow the sacred-texts transcription of Mercer: ȝ stands for aleph and ‘ for ayin; letters underlined in "
                "the printed book are given as ḏ, ṯ, ẖ.",
                "Sethe's section numbers are kept as printed in that transcription, including a few misprints (for example "
                "'146.' for 141b in Utterance 215).",
                "The TLA has no hieroglyphic encoding for these texts, so only the transliteration is shown.",
            ],
            "translation": secs,
            "verification": {
                "scan_source": f"Pyramid Texts Online (Vincent Brown), {PTO}{w['page']} (image {PTO}images/{w['pto']}); "
                               "photographs by L. F. Husson under the direction of Natacha Rambova for A. Piankoff, The Pyramid "
                               "of Unas (Bollingen Series XL.5, Princeton University Press, 1968), credited on " + PTO + "contact.html",
                "scan_license": "No terms stated by Pyramid Texts Online; photographs of 1968 (Bollingen Foundation / Princeton "
                                "University Press). Used with credit for non-commercial reference (library rule 9).",
                "scan_manuscript": f"Pyramid of Unas, Saqqara, {w['room']}, {w['wall']}, in situ; reign of Unas, end of the "
                                   "5th Dynasty, c. 2350 BCE",
                "scan_mapping": "Column of every utterance from the Unas column numbers (Sethe's W numbering) in the TLA text and "
                                "the TLA wall names; wall of every utterance also listed on the Pyramid Texts Online wall pages. "
                                "On the photograph the columns were counted by eye on zoomed bands with a pixel ruler and the "
                                "count compared with the column numbers of the wall; the edge where the text begins was fixed "
                                "from the content of the first and last columns. " + w["check"],
                "scan_mapping_urls": [PTO + w["page"], PTO + "plan.html",
                                      "https://github.com/simondschweitzer/aed-tei/tree/" + AED_COMMIT + "/files"],
                "scan_local_paths": scans,
                "original_text_source": "Thesaurus Linguae Aegyptiae, Pyramid Texts of Unas, edition by Doris Topmann; TLA "
                                        "database extract of January 2018 (urn:nbn:de:kobv:b4-opus4-29190), TEI by S. D. "
                                        "Schweitzer, AED-TEI, https://github.com/simondschweitzer/aed-tei (commit "
                                        f"{AED_COMMIT[:8]}); text ids in scripts/import_pyramid_texts_unas.py",
                "original_text_license": "CC BY-SA 4.0 (BBAW / SAW Leipzig, Thesaurus Linguae Aegyptiae; AED-TEI)",
                "translation_source": "Samuel A. B. Mercer, The Pyramid Texts in Translation and Commentary, vol. 1 (New York: "
                                      "Longmans, Green & Co., 1952), transcription of the Internet Sacred Text Archive "
                                      "(https://sacred-texts.com/egy/pyt/), read from Internet Archive Wayback Machine captures "
                                      "of 2019",
                "translation_license": "public domain in the United States (published 1952; no copyright renewal found in the "
                                       "Copyright Office records)",
                "translator": "Samuel A. B. Mercer (1952)",
                "verified_date": TODAY,
            },
        }
        (PUB / f"{eid}.json").write_text(json.dumps(e, indent=2, ensure_ascii=False), encoding="utf-8")
        entries.append(e)
        print(f"wrote {eid}: {len(secs)} sections")
        rows.append({
            "id": eid, "slug": eid, "order": order, "title": title, "author_id": "unas-pyramid",
            "language": "Egyptian", "era": "Ancient Near East", "tradition": "egyptian", "category": "sacred-text",
            "date_approx": "c. 2350 BCE (pyramid of Unas, end of the 5th Dynasty)", "century": -24,
            "source": e["source"], "description": e["description"],
            "themes": ["pyramid-texts", "unas", "afterlife", "egypt", "verified"],
            "is_first_translation": False, "status": "published",
            "scans": {"pages": [{"file": scan, "caption": f"Pyramid of Unas, {w['room']}, {w['wall']} (W {w['cols'][0]}-{w['cols'][-1]})"}]},
        })

    coll = {
        "collection": {
            "key": KEY, "prefix": PREFIX, "label": "Pyramid Texts of Unas", "group": "Egypt", "date_sort": -2350,
            "author_name": "Pyramid of Unas, Saqqara (c. 2350 BCE)",
            "source_url": PTO + "plan.html",
            "critical_edition": "Thesaurus Linguae Aegyptiae, ed. Doris Topmann (2018 data, AED-TEI)",
            "translator_name": "Samuel A. B. Mercer (1952)",
            "original_lang_label": "Egyptian · TLA transliteration",
            "original_lang_code": "egy",
            "edition_label": "",
            "search_terms": "pyramid texts unas unis wenis saqqara utterance spell osiris atum re horus seth cannibal hymn "
                            "offering ritual serpent spells ascent sky",
            "description": "The Pyramid Texts in the pyramid of Unas at Saqqara (c. 2350 BCE), the oldest Egyptian religious texts: "
                           "all seventeen inscribed walls, utterance by utterance, with the TLA transliteration and Mercer's 1952 "
                           "English, each section placed on its wall photograph by column number.",
        },
        "texts": rows,
        "authors": [{
            "id": "unas-pyramid", "name": "Pyramid of Unas (royal funerary texts)", "dates": "reign of Unas, c. 2375-2345 BCE",
            "century": -24, "era": "Ancient Near East", "tradition": "egyptian", "language": "Egyptian",
            "bio": "Unas, last king of the 5th Dynasty, was buried at Saqqara in the first pyramid whose inner walls carry the "
                   "Pyramid Texts; the spells were compiled by priests from older rituals.",
        }],
    }
    COLL.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {COLL.relative_to(ROOT)}; {sum(len(e['translation']) for e in entries)} sections, {len(distinct)} utterances")


if __name__ == "__main__":
    main()
