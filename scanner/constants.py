"""Uniden Scanner Python API
Copyright (C) 2014 Anton Komarov

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License
as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License
along with this program;
if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from collections import OrderedDict

scanner_onoff = {"on": "1", "off": "0"}
human_onoff = {"0": "off", "1": "on"}

scanner_lout = {"unlock": "0", "lockout": "1"}
human_lout = {"0": "unlock", "1": "lockout"}

scanner_audiot = {"all": "0", "analog": "1", "digital": "2"}
human_audiot = {"0": "all", "1": "analog", "2": "digital"}

scanner_altp = {"on": "0", "slow": "1", "fast": "2"}
human_altp = {"0": "on", "1": "slow", "2": "fast"}

human_ctcss_dcs = {
    "0": "all",
    "64": "67.0Hz",
    "65": "69.3Hz",
    "66": "71.9Hz",
    "67": "74.4Hz",
    "68": "77.0Hz",
    "69": "79.7Hz",
    "70": "82.5Hz",
    "71": "85.4Hz",
    "72": "88.5Hz",
    "73": "91.5Hz",
    "74": "94.8Hz",
    "75": "97.4Hz",
    "76": "100.0Hz",
    "77": "103.5Hz",
    "78": "107.2Hz",
    "79": "110.9Hz",
    "80": "114.8Hz",
    "81": "118.8Hz",
    "82": "123.0Hz",
    "83": "127.3Hz",
    "84": "131.8Hz",
    "85": "136.5Hz",
    "86": "141.3Hz",
    "87": "146.2Hz",
    "88": "151.4Hz",
    "89": "156.7Hz",
    "90": "159.8Hz",
    "91": "162.2Hz",
    "92": "165.5Hz",
    "93": "167.9Hz",
    "94": "171.3Hz",
    "95": "173.8Hz",
    "96": "177.3Hz",
    "97": "179.9Hz",
    "98": "183.5Hz",
    "99": "186.2Hz",
    "100": "189.9Hz",
    "101": "192.8Hz",
    "102": "196.6Hz",
    "103": "199.5Hz",
    "104": "203.5Hz",
    "105": "206.5Hz",
    "106": "210.7Hz",
    "107": "218.1Hz",
    "108": "225.7Hz",
    "109": "229.1Hz",
    "110": "233.6Hz",
    "111": "241.8Hz",
    "112": "250.3Hz",
    "113": "254.1Hz",
    "127": "search",
    "128": "023",
    "129": "025",
    "130": "026",
    "131": "031",
    "132": "032",
    "133": "036",
    "134": "043",
    "135": "047",
    "136": "051",
    "137": "053",
    "138": "054",
    "139": "065",
    "140": "071",
    "141": "072",
    "142": "073",
    "143": "074",
    "144": "114",
    "145": "115",
    "146": "116",
    "147": "122",
    "148": "125",
    "149": "131",
    "150": "132",
    "151": "134",
    "152": "143",
    "153": "145",
    "154": "152",
    "155": "155",
    "156": "156",
    "157": "162",
    "158": "165",
    "159": "172",
    "160": "174",
    "161": "205",
    "162": "212",
    "163": "223",
    "164": "225",
    "165": "226",
    "166": "243",
    "167": "244",
    "168": "245",
    "169": "246",
    "170": "251",
    "171": "252",
    "172": "255",
    "173": "261",
    "174": "263",
    "175": "265",
    "176": "266",
    "177": "271",
    "178": "274",
    "179": "306",
    "180": "311",
    "181": "315",
    "182": "325",
    "183": "331",
    "184": "332",
    "185": "343",
    "186": "346",
    "187": "351",
    "188": "356",
    "189": "364",
    "190": "365",
    "191": "371",
    "192": "411",
    "193": "412",
    "194": "413",
    "195": "423",
    "196": "431",
    "197": "432",
    "198": "445",
    "199": "446",
    "200": "452",
    "201": "454",
    "202": "455",
    "203": "462",
    "204": "464",
    "205": "465",
    "206": "466",
    "207": "503",
    "208": "506",
    "209": "516",
    "210": "523",
    "211": "526",
    "212": "532",
    "213": "546",
    "214": "565",
    "215": "606",
    "216": "612",
    "217": "624",
    "218": "627",
    "219": "631",
    "220": "632",
    "221": "654",
    "222": "662",
    "223": "664",
    "224": "703",
    "225": "712",
    "226": "723",
    "227": "731",
    "228": "732",
    "229": "734",
    "230": "743",
    "231": "754",
}

scanner_ctcss_dcs = {
    "all": "0",
    "67.0Hz": "64",
    "69.3Hz": "65",
    "71.9Hz": "66",
    "74.4Hz": "67",
    "77.0Hz": "68",
    "79.7Hz": "69",
    "82.5Hz": "70",
    "85.4Hz": "71",
    "88.5Hz": "72",
    "91.5Hz": "73",
    "94.8Hz": "74",
    "97.4Hz": "75",
    "100.0Hz": "76",
    "103.5Hz": "77",
    "107.2Hz": "78",
    "110.9Hz": "79",
    "114.8Hz": "80",
    "118.8Hz": "81",
    "123.0Hz": "82",
    "127.3Hz": "83",
    "131.8Hz": "84",
    "136.5Hz": "85",
    "141.3Hz": "86",
    "146.2Hz": "87",
    "151.4Hz": "88",
    "156.7Hz": "89",
    "159.8Hz": "90",
    "162.2Hz": "91",
    "165.5Hz": "92",
    "167.9Hz": "93",
    "171.3Hz": "94",
    "173.8Hz": "95",
    "177.3Hz": "96",
    "179.9Hz": "97",
    "183.5Hz": "98",
    "186.2Hz": "99",
    "189.9Hz": "100",
    "192.8Hz": "101",
    "196.6Hz": "102",
    "199.5Hz": "103",
    "203.5Hz": "104",
    "206.5Hz": "105",
    "210.7Hz": "106",
    "218.1Hz": "107",
    "225.7Hz": "108",
    "229.1Hz": "109",
    "233.6Hz": "110",
    "241.8Hz": "111",
    "250.3Hz": "112",
    "254.1Hz": "113",
    "search": "127",
    "023": "128",
    "025": "129",
    "026": "130",
    "031": "131",
    "032": "132",
    "036": "133",
    "043": "134",
    "047": "135",
    "051": "136",
    "053": "137",
    "054": "138",
    "065": "139",
    "071": "140",
    "072": "141",
    "073": "142",
    "074": "143",
    "114": "144",
    "115": "145",
    "116": "146",
    "122": "147",
    "125": "148",
    "131": "149",
    "132": "150",
    "134": "151",
    "143": "152",
    "145": "153",
    "152": "154",
    "155": "155",
    "156": "156",
    "162": "157",
    "165": "158",
    "172": "159",
    "174": "160",
    "205": "161",
    "212": "162",
    "223": "163",
    "225": "164",
    "226": "165",
    "243": "166",
    "244": "167",
    "245": "168",
    "246": "169",
    "251": "170",
    "252": "171",
    "255": "172",
    "261": "173",
    "263": "174",
    "265": "175",
    "266": "176",
    "271": "177",
    "274": "178",
    "306": "179",
    "311": "180",
    "315": "181",
    "325": "182",
    "331": "183",
    "332": "184",
    "343": "185",
    "346": "186",
    "351": "187",
    "356": "188",
    "364": "189",
    "365": "190",
    "371": "191",
    "411": "192",
    "412": "193",
    "413": "194",
    "423": "195",
    "431": "196",
    "432": "197",
    "445": "198",
    "446": "199",
    "452": "200",
    "454": "201",
    "455": "202",
    "462": "203",
    "464": "204",
    "465": "205",
    "466": "206",
    "503": "207",
    "506": "208",
    "516": "209",
    "523": "210",
    "526": "211",
    "532": "212",
    "546": "213",
    "565": "214",
    "606": "215",
    "612": "216",
    "624": "217",
    "627": "218",
    "631": "219",
    "632": "220",
    "654": "221",
    "662": "222",
    "664": "223",
    "703": "224",
    "712": "225",
    "723": "226",
    "731": "227",
    "732": "228",
    "734": "229",
    "743": "230",
    "754": "231",
}

scanner_alert_tones = {
    "off": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
}
human_alert_tones = {
    "0": "off",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
}

scanner_alert_tlevels = {
    "auto": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "11": "11",
    "12": "12",
    "13": "13",
    "14": "14",
    "15": "15",
}
human_alert_tlevels = {
    "0": "auto",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "11": "11",
    "12": "12",
    "13": "13",
    "14": "14",
    "15": "15",
}

scanner_sys_type = {
    "conventional": "CNV",
    "motorola": "MOT",
    "edacs narrow/wide": "EDC",
    "edacs scat": "EDS",
    "ltr": "LTR",
    "p25 standard": "P25S",
    "p25 1f trunk": "P25F",
}
human_sys_type = {
    "CNV": "conventional",
    "MOT": "motorola",
    "EDC": "edacs narrow/wide",
    "EDS": "edacs scat",
    "LTR": "ltr",
    "P25S": "p25 standard",
    "P25F": "p25 1f trunk",
}

scanner_id_search = {"scan": "0", "search": "1"}
human_id_search = {"0": "scan", "1": "search"}

scanner_sbit = {"ignore": "0", "yes": "1"}
human_sbit = {"0": "ignore", "1": "yes"}

scanner_end_code = {"ignore": "0", "analog": "1", "analog/digital": "2"}
human_end_code = {"0": "ignore", "1": "analog", "2": "analog/digital"}

scanner_mot_id = {"decimal": 0, "hex": "1"}
human_mot_id = {"0": "decimal", "1": "hex"}

scanner_afs = {"decimal": "0", "afs": "1"}
human_afs = {"0": "decimal", "1": "afs"}

human_cc_modes = {"0": "off", "1": "pri", "2": "dnd"}
scanner_cc_modes = {"off": "0", "pri": "1", "dnd": "2"}

code_mode = {"nac": "2", "dsc": "1", "off": "0"}
p25w_values = (0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)
dly_values = (-10, -5, -2, -1, 0, 1, 2, 5, 10, 30)
mod_values = ("AUTO", "AM", "FM", "NFM", "WFM", "FMB")

scanner_events = {
    "infinite": "IF",
    "10sec": "10",
    "30sec": "30",
    "keypress": "KY",
    "squelch": "SQ",
}
human_events = {
    "IF": "infinite",
    "10": "10sec",
    "30": "30sec",
    "KY": "keypress",
    "SQ": "squelch",
}

color_values = ("BLUE", "RED", "MAGENTA", "GREEN", "CYAN", "YELLOW", "WHITE")

scanner_dimmers = {"low": "1", "middle": "2", "high": "3"}
human_dimmers = {"1": "low", "2": "middle", "3": "high"}

baudrate_values = ("OFF", "4800", "9600", "19200", "38400", "57600", "115200")

beep_level_values = {
    "auto": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "11": "11",
    "12": "12",
    "13": "13",
    "14": "14",
    "15": "15",
    "off": "99",
}

scanner_pri_modes = {"off": "0", "on": "1", "plus on": "2"}
human_pri_modes = {"0": "off", "1": "on", "2": "plus on"}

disp_mode_values = {"mode1": "1", "mode2": "2", "mode3": "3"}

scanner_ch_logs = {"off": "0", "on": "1", "extend": "2"}
human_ch_logs = {"0": "off", "1": "on", "2": "extend"}

# list of commands available via serial port and the first line of response
# technically all responses end in "\r"
# todo: finish adding to this list
SCANNER_COMMAND_RESPONSE = {
    # information
    "MDL": ("MDL", "MODEL_NAME"),
    "VER": ("VER", "VERSION", r"\r"),
    "KEY": ("KEY", "OK"),
    "STS": r"",
    "GLT": r"",
    # xml formatted responses
    "PSI": ("PSI", "<XML"),
    "GSI": ("GSI", "<XML>"),
    "MSI": r"MSI,<XML>\r",
    # getters/setters
    "FQK": r"",
    "SQK": r"",
    "DQK": r"",
    "SVC": r"",
    "DTM": r"",
    "LCR": r"",
    "URC": r"",
    # set only
    "HLD": r"HDL,OK\r",
    "MSV": r"MSV,OK\r",
    "AVD": r"AVD,OK\r",
    "JPM": r"JPM,OK\r",
    # navigation
    "JNT": r"JNT,OK\r",
    "QSH": r"",
    "NXT": r"",
    "PRV": r"",
    "MNU": r"MNU,OK\r",
    "MSB": r"MSB,OK\r",
    # misc
    "AST": r"",
    "APR": r"",
}

# list of parameters the scanner outputs when running GSI command
# this must match the order and number in database
# todo: compare GSI output to tag names used for wav metadata parsing
GSI_OUTPUT = OrderedDict(
    [
        ("date_code", (376, 14)),
        ("ScannerInfo:Mode", "---"),
        ("ScannerInfo:V_Screen", "---"),
        ("MonitorList:Name", "---"),
        ("MonitorList:Index", "---"),
        ("MonitorList:ListType", "---"),
        ("MonitorList:Q_Key", "---"),
        ("MonitorList:N_Tag", "---"),
        ("MonitorList:DB_Counter", "---"),
        ("System:Name", "---"),
        ("System:Index", "---"),
        ("System:Avoid", "---"),
        ("System:SystemType", "---"),
        ("System:Q_Key", "---"),
        ("System:N_Tag", "---"),
        ("System:Hold", "---"),
        ("Department:Name", "---"),
        ("Department:Index", "---"),
        ("Department:Avoid", "---"),
        ("Department:Q_Key", "---"),
        ("Department:Hold", "---"),
        ("TGID:Name", "---"),
        ("TGID:Index", "---"),
        ("TGID:Avoid", "---"),
        ("TGID:TGID", "---"),
        ("TGID:SetSlot", "---"),
        ("TGID:RecSlot", "---"),
        ("TGID:N_Tag", "---"),
        ("TGID:Hold", "---"),
        ("TGID:SvcType", "---"),
        ("TGID:P_Ch", "---"),
        ("TGID:LVL", "---"),
        ("UnitID:Name", "---"),
        ("UnitID:U_Id", "---"),
        ("Site:Name", "---"),
        ("Site:Index", "---"),
        ("Site:Avoid", "---"),
        ("Site:Q_Key", "---"),
        ("Site:Hold", "---"),
        ("Site:Mod", "---"),
        ("SiteFrequency:Freq", "---"),
        ("SiteFrequency:IFX", "---"),
        ("SiteFrequency:SAS", "---"),
        ("SiteFrequency:SAD", "---"),
        ("DualWatch:PRI", "---"),
        ("DualWatch:CC", "---"),
        ("DualWatch:WX", "---"),
        ("Property:F", "---"),
        ("Property:VOL", "---"),
        ("Property:SQL", "---"),
        ("Property:Sig", "---"),
        ("Property:Att", "---"),
        ("Property:Rec", "---"),
        ("Property:KeyLock", "---"),
        ("Property:P25Status", "---"),
        ("Property:Mute", "---"),
        ("Property:Backlight", "---"),
        ("Property:A_Led", "---"),
        ("Property:Dir", "---"),
        ("Property:Rssi", "---"),
        ("ViewDescription:", "---"),
    ]
)

# human readable metadata names and their corresponding tag/location in WAV
# header metadata
WAV_METADATA = OrderedDict(
    [
        ("transmission_end:1", "ICRD"),
        ("ICRD", "transmission_end:1"),
        ("ScannerInfo:Mode:1", "---"),
        ("ScannerInfo:V_Screen", "---"),
        ("MonitorList:Name:1", "ISBJ"),
        ("ISBJ", "MonitorList:Name:1"),
        ("MonitorList:Name", "fav_list_name"),
        ("MonitorList:Index", "---"),
        ("MonitorList:ListType", "---"),
        ("MonitorList:Q_Key", "---"),
        ("MonitorList:N_Tag", "---"),
        ("MonitorList:DB_Counter", "---"),
        ("System:Name:1", "IART"),
        ("IART", "System:Name:1"),
        ("System:Index", "---"),
        ("System:Avoid", "---"),
        ("System:SystemType", "---"),
        ("System:Q_Key", "---"),
        ("System:N_Tag", "---"),
        ("System:Hold", "---"),
        ("Department:Name:1", "IGNR"),
        ("IGNR", "Department:Name:1"),
        ("Department:Index", "---"),
        ("Department:Avoid", "---"),
        ("Department:Q_Key", "---"),
        ("Department:Hold", "---"),
        ("Channel:Name", "INAM"),
        ("INAM", "Channel:Name:1"),
        ("Channel:Avoid", "---"),
        ("Channel:TGID", "ICMT"),
        ("ICMT", "Channel:TGID:1"),
        ("Channel:SetSlot", "---"),
        ("Channel:RecSlot", "---"),
        ("Channel:N_Tag", "---"),
        ("Channel:Hold", "---"),
        ("Channel:SvcType", "---"),
        ("Channel:P_Ch", "---"),
        ("Channel:LVL", "---"),
        ("UnitID:Name", "---"),
        ("UnitID:U_Id", "ITCH"),
        ("ITCH", "UnitID:U_Id:1"),
        ("Site:Index", "---"),
        ("Site:Avoid", "---"),
        ("Site:Q_Key", "---"),
        ("Site:Hold", "---"),
        ("Site:Mod", "---"),
        ("SiteFrequency:Freq", "---"),
        ("SiteFrequency:IFX", "---"),
        ("SiteFrequency:SAS", "---"),
        ("SiteFrequency:SAD", "---"),
        ("DualWatch:PRI", "---"),
        ("DualWatch:CC", "---"),
        ("DualWatch:WX", "---"),
        ("Property:F", "---"),
        ("Property:VOL", "---"),
        ("Property:SQL", "---"),
        ("Property:Sig", "---"),
        ("Property:Att", "---"),
        ("Property:Rec", "---"),
        ("Property:KeyLock", "---"),
        ("Property:P25Status", "ISRC"),
        ("ISRC", "Property:P25Status:1"),
        ("Property:Mute", "---"),
        ("Property:Backlight", "---"),
        ("Property:A_Led", "---"),
        ("Property:Dir", "---"),
        ("Property:Rssi", "---"),
        ("Property:CodeSpec", "IPRD"),  # don't know best name
        ("IPRD", "Property:CodeSpec:1"),
        ("ViewDescription:", "---"),
        ("dump", (576, 743)),
        ("dump2", (786, 62)),
        ("IKEY", "IKEY"),
        ("ICOP", "ICOP"),
    ]
)

# uniden proprietary metadata that is 0x00 delimited. «list index» specifies
# the order corresponding to each property value.
# ("name", «list index»)
# UNID_METADATA = OrderedDict(
#     [
#         ("FavoritesList:Name", 0),
#         ("FavoritesList:File", 2),
#         ("System:Name", 14),
#         ("Department:Name", 27),
#         ("Department:Lat", 29),
#         ("Department:Lon", 30),
#         ("Department:Radius", 31),
#         ("Department:Shape", 32),
#         ("Channel:Name", 33),
#         ("Channel:TGID", 35),
#         ("Site:Name", 38),
#         ("Site:Lat", 40),
#         ("Site:Lon", 41),
#         ("Site:Radius", 42),
#         ("Site:Shape", 43),
#     ]
# )

# These are values located at static positions in WAV header.
# {name, (offset:start, length)}
# UNID_STATIC_OFFSETS = {
#     "Byte:Ordered": (591, 1456),
#     "UnitID:UID": (707, 11),
#     "TGID:1": (607, 10),
#     "TGID:2": (824, 10),
# }

# Only the first 64 bytes of this data are recorded
UNID_FAVORITES_DATA = [
    "MonitorList:Name",  # favorites list name
    "MonitorList:Filename",
    "MonitorList:LocationControl",
    "MonitorList:Monitor",
    "MonitorList:QuickKey",
    "MonitorList:NumberTag",
    # remaining items are QKey states and not needed
]

# Only the first 64 bytes of this data are recorded
UNID_SYSTEM_DATA = [
    "System:Name",
    "System:Avoid",
    "System:Reserve",
    "System:Type",
    "System:IDSearch",
    "System:AlertTone",
    "System:AlertVolume",
    "System:StatusBit",
    "System:Reserve(NAC)",
    "System:QuickKey",
    "System:NumberTag",
    "System:SiteHoldTime",
    # remaining items unlikely to be recorded
]

UNID_DEPARTMENT_DATA = [
    "Department:Name",
    "Department:Avoid",
    "Department:Latitude",
    "Department:Longitude",
    "Department:Range",
    "Department:LocationType",
    "Department:QuickKey",
]

UNID_CHANNEL_DATA = [
    "TGID:Name",
    "TGID:Avoid",
    "TGID:TGID",
    "TGID:AudioType",
    "TGID:FuncTagID",
    "TGID:Delay",
    "TGID:VolOffset",
    "TGID:AlertTone",
    "TGID:AlertVol",
    "TGID:AlertColor",
    "TGID:AlertPattern",
    "TGID:NumberTag",
    "TGID:PriorityChannel",
]

UNID_SITE_DATA = [
    "Site:Name",
    "Site:Avoid",
    "Site:Latitude",
    "Site:Longitude",
    "Site:Range",
    "Site:Modulation",
    "Site:MotBandType",
    "Site:EdacsBandType",
    "Site:LocationType",
    "Site:Attenuator",
    "Site:DigitalWaitingTime",
    "Site:DigitalThresholdMode",
    "Site:DigitalThresholdLevel",
    "Site:QuickKey",
    "Site:NAC",
]


UNID_CONVENTIONAL_DATA = [
    "Conventional",
    "Conventional:MyId",
    "Conventional:ParentId",
    "Conventional:NameTag",
    "Conventional:Avoid",
    "Conventional:Reserve",
    "Conventional:SystemType",
    "Conventional:QuickKey",
    "Conventional:Numbertag",
    "Conventional:SystemHoldTime",
    "Conventional:AnalogAGC",
    "Conventional:DigitalAGC",
    "Conventional:DigitalWaitingTime",
    "Conventional:DigitalThresholdMode",
    "Conventional:DigitalThresholdLevel",
]

UNID_UNITID_DATA = [
    "UnitIds",
    "UnitIds:Reserve",
    "UnitIds:NameTag",
    "UnitIds:UnitID",
    "UnitIds:AlertTone",
    "UnitIds:AlertVolue",
    "UnitIds:AlertColor",
    "UnitIds:AlertPattern",
]
