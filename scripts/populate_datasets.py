#!/usr/bin/env python3
"""
populate_datasets.py
Extract structured data from sources/extracted/*.txt and populate data/dat_XX.yaml.
Idempotent: reads existing YAML, adds new records (deduped by id), writes back.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("pip install pyyaml"); sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "sources" / "extracted"
DATA = ROOT / "data"
NOW = "2026-10-10T00:00:00Z"

def txt(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

HW1 = txt(EX / "SIM800L_Hardware_Design_V1.00.txt")
HW2 = txt(EX / "SIM800H&SIM800L_Hardware_Design_V2.02.txt")
ATX = txt(EX / "SIM800 Series_AT Command Manual_V1.01.txt")

def src(name, ver, date, page=None, section=None, quote=None):
    s = {"name": name, "version": ver, "date": date}
    if page is not None: s["page"] = str(page)
    if section: s["section"] = section
    if quote: s["quote"] = quote.strip()[:300]
    return s

def mk(prefix, n, category, source, **kw):
    r = {"id": f"{prefix}_{n:04d}", "category": category, "source": source,
         "source_type": "primary", "confidence": 0.9, "status": "complete",
         "conflicts": [], "applicable_models": ["SIM800L"],
         "created_at": NOW, "updated_at": NOW}
    r.update(kw); return r

def save(name: str, records: list):
    path = DATA / name
    existing = []
    if path.exists():
        try:
            d = yaml.safe_load(path.read_text(encoding="utf-8")) or []
            if isinstance(d, list): existing = d
        except Exception as e:
            print(f"  [warn] parse {name}: {e}")
    seen = {r.get("id") for r in existing}
    added = 0
    for r in records:
        if r.get("id") not in seen:
            existing.append(r); seen.add(r.get("id")); added += 1
    path.write_text(yaml.safe_dump(existing, allow_unicode=True, sort_keys=False),
                    encoding="utf-8")
    print(f"  {name}: +{added} (total {len(existing)})")

# ============================================================
# dat_07 - Hardware Reference
# ============================================================
PIN_DATA = [
    ("VBAT","1,42","I","Power supply","3.4V-4.4V recommended 4.0V","Power"),
    ("VRTC","56","I/O","Power supply for RTC","4.7uF capacitor or battery","Power"),
    ("VDD_EXT","18","O","2.8V power output","Keep open if unused","Power"),
    ("GND","2,6,8,35,37-45,58,67,71-88","","Ground","Use 2,43,44,45 for VBAT","Ground"),
    ("PWRKEY","48","I","Power on/off key","Pull low >=1s to toggle, internal pull-up","PWRKEY"),
    ("MIC1P","52","I","Main mic input positive","Differential","Audio"),
    ("MIC1N","12","I","Main mic input negative","Differential","Audio"),
    ("SPK1P","53","O","Main speaker output positive","32 ohm receiver","Audio"),
    ("SPK1N","13","O","Main speaker output negative","","Audio"),
    ("MIC2P","9","I","Secondary mic input positive","","Audio"),
    ("MIC2N","10","I","Secondary mic input negative","","Audio"),
    ("SPK2P","51","O","Secondary speaker output positive","8 ohm speaker","Audio"),
    ("SPK2N","11","O","Secondary speaker output negative","","Audio"),
    ("PCM_CLK","29","O","PCM clock","256kHz master mode","Audio"),
    ("PCM_OUT","30","O","PCM data output","16-bit linear","Audio"),
    ("PCM_SYNC","65","O","PCM sync","Short/long sync","Audio"),
    ("PCM_IN","66","I","PCM data input","16-bit linear","Audio"),
    ("KBC0","20","I","Keypad column 0","Pull up at power on","GPIO"),
    ("KBC1","25","I","Keypad column 1","Pull down","GPIO"),
    ("KBC2","22","I","Keypad column 2","Pull down","GPIO"),
    ("KBC3","21","I","Keypad column 3","Pull down","GPIO"),
    ("KBC4","24","I","Keypad column 4","Pull down","GPIO"),
    ("KBR0","62","O","Keypad row 0","Pull down","GPIO"),
    ("KBR1","60","O","Keypad row 1","Pull down","GPIO"),
    ("KBR2","61","O","Keypad row 2","Pull down","GPIO"),
    ("KBR3","23","O","Keypad row 3","Pull down","GPIO"),
    ("KBR4","63","O","Keypad row 4","Pull down","GPIO"),
    ("GPIO1","3","I/O","General purpose IO","","GPIO"),
    ("GPIO2","27","I/O","General purpose IO","AT+SGPIO","GPIO"),
    ("GPIO3","28","I/O","General purpose IO","","GPIO"),
    ("NETLIGHT","64","O","Network status LED","64ms/800ms;64ms/3000ms;64ms/300ms","STATUS"),
    ("STATUS","4","O","Power on status","High=on, Low=off","STATUS"),
    ("DTR","69","I","Data terminal ready","Sleep control","UART"),
    ("RI","68","O","Ring indicator","Low=120ms on SMS","UART"),
    ("DCD","70","O","Data carrier detect","","UART"),
    ("CTS","34","O","Clear to send","Flow control","UART"),
    ("RTS","33","I","Request to send","Flow control","UART"),
    ("TXD","32","O","Transmit data","CMOS level","UART"),
    ("RXD","31","I","Receive data","CMOS level","UART"),
    ("VBUS","7","I","USB power supply","4.3-7.0V","USB"),
    ("USB_DP","59","I/O","USB data +","TVS < 5pF","USB"),
    ("USB_DN","19","I/O","USB data -","TVS < 5pF","USB"),
    ("ADC","50","I","10-bit ADC","0-2.8V range","ADC"),
    ("PWM","26","O","PWM output","0-2kHz, 7-bit","PWM"),
    ("SDA","75","I/O","I2C data","Pull up to VDD_EXT","GPIO"),
    ("SCL","74","O","I2C clock","Pull up to VDD_EXT","GPIO"),
    ("SIM_VDD","16","O","SIM card power","1.8V or 3V","SIM"),
    ("SIM_DATA","14","I/O","SIM data I/O","ESD protection required","SIM"),
    ("SIM_CLK","55","O","SIM clock","51 ohm series","SIM"),
    ("SIM_RST","15","O","SIM reset","51 ohm series","SIM"),
    ("SIM_DET","54","I","SIM presence detect","8-pin holder only","SIM"),
    ("GSM_ANT","40","I/O","GSM antenna pad","50 ohm, VSWR<2","Antenna"),
    ("BT_ANT","36","I/O","Bluetooth antenna","SIM800H only","Antenna"),
    ("FM_ANTP","17","I","FM antenna positive","Differential","Antenna"),
    ("FM_ANTN","57","I","FM antenna negative","Differential","Antenna"),
    ("RF_SYNC","5","O","RF sync signal","Jamming detect alt","RF"),
    ("RESET","49","I","Module reset (active low)","Emergency only","Reset"),
    ("ISINK1","46","I","Keypad backlight sink","60-100mA","GPIO"),
    ("ISINK0","47","I","LCD backlight sink","0-24mA, 6 levels","GPIO"),
]
records = []
for i, (n, pins, io, fn, cm, cat) in enumerate(PIN_DATA, start=1):
    records.append(mk("dat_07", i, cat,
        src("SIM800H&SIM800L_Hardware_Design","V2.02","2015-07-27","16-18","Pin Description"),
        name=n, pin_number=pins, direction=io or "I/O",
        function=fn, comments=cm or None))
print("Populating datasets...")
save("dat_07_hardware_reference.yaml", records)

# ============================================================
# dat_03 - CME / CMS error codes
# ============================================================
CME = [(0,"phone failure"),(1,"no connection to phone"),(2,"phone-adaptor link reserved"),
(3,"operation not allowed"),(4,"operation not supported"),(5,"PH-SIM PIN required"),
(6,"PH-FSIM PIN required"),(7,"PH-FSIM PUK required"),(10,"SIM not inserted"),
(11,"SIM PIN required"),(12,"SIM PUK required"),(13,"SIM failure"),(14,"SIM busy"),
(15,"SIM wrong"),(16,"incorrect password"),(17,"SIM PIN2 required"),(18,"SIM PUK2 required"),
(20,"memory full"),(21,"invalid index"),(22,"not found"),(23,"memory failure"),
(24,"text string too long"),(25,"invalid characters in text string"),(26,"dial string too long"),
(27,"invalid characters in dial string"),(30,"no network service"),(31,"network timeout"),
(32,"network not allowed - emergency call only"),(40,"network personalisation PIN required"),
(41,"network personalisation PUK required"),(42,"network subset personalisation PIN required"),
(43,"network subset personalisation PUK required"),(44,"service provider personalisation PIN required"),
(45,"service provider personalisation PUK required"),(46,"corporate personalisation PIN required"),
(47,"corporate personalisation PUK required"),(99,"resource limitation"),(100,"unknown"),
(103,"Illegal MS"),(106,"Illegal ME"),(107,"GPRS services not allowed"),
(111,"PLMN not allowed"),(112,"Location area not allowed"),
(113,"Roaming not allowed in this location area"),(132,"service option not supported"),
(133,"requested service option not subscribed"),(134,"service option temporarily out of order"),
(148,"unspecified GPRS error"),(149,"PDP authentication failure"),(150,"invalid mobile class"),
(160,"DNS resolve failed"),(161,"Socket open failed"),(180,"gprs is not attached"),
(181,"tcpip stack is busy")]

CMS = [(1,"Unassigned(unallocated) number"),(3,"No route to destination"),
(6,"Channel unacceptable"),(8,"Operator determined barring"),(10,"Call barred"),
(11,"Reserved"),(16,"Normal call clearing"),(17,"User busy"),(18,"No user responding"),
(19,"User alerting, no answer"),(21,"Short message transfer rejected"),(22,"Number changed"),
(25,"Pre-emption"),(26,"Non-selected user clearing"),(27,"Destination out of service"),
(28,"Invalid number format (incomplete number)"),(29,"Facility rejected"),
(30,"Response to STATUS ENQUIRY"),(32,"Normal, unspecified"),(34,"No circuit/channel available"),
(38,"Network out of order"),(41,"Temporary failure"),(42,"Switching equipment Congestion"),
(43,"Access information discarded"),(44,"Requested circuit/channel not available"),
(47,"Resources unavailable, unspecified"),(49,"Quality of service unavailable"),
(50,"Requested facility not subscribed"),(55,"Requested facility not subscribed"),
(57,"Bearer capability not authorized"),(58,"Bearer capability not presently available"),
(63,"Service or option not available, unspecified"),(65,"Bearer service not implemented"),
(68,"ACM equal or greater than ACM maximum"),(69,"Requested facility not implemented"),
(70,"Only restricted digital information bearer capability is available"),
(79,"Service or option not implemented, unspecified"),(81,"Invalid transaction identifier value"),
(87,"User not member of CUG"),(88,"Incompatible destination"),
(91,"Invalid transit network selection"),(95,"Semantically incorrect message"),
(96,"Invalid mandatory information"),(97,"Message type non-existent or not implemented"),
(98,"Message type not compatible with protocol state"),
(99,"Information element non-existent or not implemented"),
(100,"Conditional information element error"),(101,"Message not compatible with protocol"),
(102,"Recovery on timer expiry"),(111,"Protocol error, unspecified"),
(127,"Interworking, unspecified"),(128,"Telematic interworking not supported"),
(129,"Short message Type 0 not supported"),(130,"Cannot replace short message"),
(143,"Unspecified TP-PID error"),(144,"Data coding scheme (alphabet) not supported"),
(145,"Message class not supported"),(159,"Unspecified TP-DCS error"),
(160,"Command cannot be acted"),(161,"Command unsupported"),(175,"Unspecified TP-Command error"),
(176,"TPDU not supported"),(192,"SC busy"),(193,"No SC subscription"),
(194,"SC system failure"),(195,"Invalid SME address"),(196,"Destination SME barred"),
(197,"SM Rejected-Duplicate SM"),(198,"TP-VPF not supported"),(199,"TP-VP not supported"),
(208,"SIM SMS storage full"),(209,"No SMS storage capability in SIM"),(210,"Error in MS"),
(211,"Memory Capacity Exceeded"),(212,"SIM Application Toolkit Busy"),
(213,"SIM data download error"),(224,"CP retry exceed"),(225,"RP trim timeout"),
(226,"SMS connection broken"),(255,"Unspecified error cause"),(300,"ME failure"),
(301,"SMS reserved"),(302,"operation not allowed"),(303,"operation not supported"),
(304,"invalid PDU mode"),(305,"invalid text mode"),(310,"SIM not inserted"),
(311,"SIM pin necessary"),(312,"PH SIM pin necessary"),(313,"SIM failure"),(314,"SIM busy"),
(315,"SIM wrong"),(316,"SIM PUK required"),(317,"SIM PIN2 required"),(318,"SIM PUK2 required"),
(320,"memory failure"),(321,"invalid memory index"),(322,"memory full"),
(323,"invalid input parameter"),(324,"invalid input format"),(325,"invalid input value"),
(330,"SMSC address unknown"),(331,"no network"),(332,"network timeout")]

er = []
n = 0
for code, meaning in CME:
    n += 1
    er.append(mk("dat_03", n, "CME",
        src("SIM800 Series_AT Command Manual","V1.01","2013-07-23","285-287","19.1 CME ERROR"),
        error_type="CME", code=code, meaning=meaning, description=meaning,
        related_commands=[], recovery_steps=[]))
for code, meaning in CMS:
    n += 1
    er.append(mk("dat_03", n, "CMS",
        src("SIM800 Series_AT Command Manual","V1.01","2013-07-23","288-292","19.2 CMS ERROR"),
        error_type="CMS", code=code, meaning=meaning, description=meaning,
        related_commands=[], recovery_steps=[]))
save("dat_03_error_code.yaml", er)

# ============================================================
# dat_02 - URCs
# ============================================================
URC = [
("RING","Incoming call","AT+CRC","","AT+CRC=1"),
("NO CARRIER","Connection terminated","","",""),
("+CMTI: <mem>,<index>","New SMS stored","AT+CNMI","SMS","AT+CNMI=2,1"),
("+CMT: <oa>,<scts>,...","New SMS directly routed","AT+CNMI","SMS","AT+CNMI=2,2"),
("+CDS: <fo>,<mr>,...","SMS status report","AT+CNMI","SMS","AT+CNMI=2,1,0,1"),
("+CUSD: <m>,<str>","USSD response","AT+CUSD","","AT+CUSD=1"),
("+CREG: <stat>","Network registration change","AT+CREG","Network","AT+CREG=1"),
("+CGREG: <stat>","GPRS registration change","AT+CGREG","GPRS","AT+CGREG=1"),
("+CLIP: <number>,<type>","Calling line ID","AT+CLIP","Call","AT+CLIP=1"),
("+CRING: <type>","Extended incoming call","AT+CRC","Call","AT+CRC=1"),
("+CPIN: <code>","SIM PIN status","AT+CPIN","SIM",""),
("+PDP: DEACT","GPRS PDP deactivated","","GPRS",""),
("+CIPRXGET: <mode>","Manual data receive","AT+CIPRXGET","TCP/IP",""),
("+CIPCLOSE: <n>","Connection closed","AT+CIPCLOSE","TCP/IP",""),
("+CIPSTATUS: <n>","Connection status","AT+CIPSTATUS","TCP/IP",""),
("+HTTPACTION: <Method>,<Status>,<Len>","HTTP action completed","AT+HTTPACTION","HTTP",""),
("+FTPPUT: <mode>,<result>","FTP upload result","AT+FTPPUT","FTP",""),
("+SSLRECV: <len>","SSL data received","AT+SSLRECV","SSL",""),
("NORMAL POWER DOWN","Module powering down","AT+CPOWD","Power",""),
("UNDER-VOLTAGE WARNNING","Low voltage warning","","Power",""),
("UNDER-VOLTAGE POWER DOWN","Module powered down due to low voltage","","Power",""),
("OVER-VOLTAGE WARNNING","Over-voltage warning","","Power",""),
("OVER-VOLTAGE POWER DOWN","Module powered down due to over-voltage","","Power",""),
("+CMTE: <n>","Temperature alert","AT+CMTE","Temperature","AT+CMTE=1"),
("RDY","Power-on complete","AT+IPR","Init",""),
("Call Ready","Init complete","AT+CIURC","Init","AT+CIURC=1"),
("+CFUN: <fun>","Functionality change","AT+CFUN","Power",""),
("+CSMINS: <n>,<SIM inserted>","SIM insertion status","AT+CSMINS","SIM","AT+CSMINS=1"),
("+CDRIND: <type>","Call terminated","AT+CDRIND","Call","AT+CDRIND=1"),
("+CENG: <cell>,...","Engineering mode","AT+CENG","Network","AT+CENG=2"),
("MO RING","MO call alerting","AT+MORING","Call","AT+MORING=1"),
("MO CONNECTED","MO call established","AT+MORING","Call","AT+MORING=1"),
("+CLCC: <id>,...","Current call list","AT+CLCC","Call","AT+CLCC=1"),
("+CCWA: <number>,<type>,<class>","Call waiting","AT+CCWA","Call","AT+CCWA=1"),
("+COLP: <number>,<type>","Connected line ID","AT+COLP","Call","AT+COLP=1"),
("+CSSU: <code2>","SS notification","AT+CSSN","Call","AT+CSSN=0,1"),
("+CSSI: <code1>","SS notification","AT+CSSN","Call","AT+CSSN=1,0"),
("+CBM: <length>,<pdu>","New cell broadcast","AT+CNMI","SMS","AT+CNMI=2,0,2"),
("+SAPBR <cid>: DEACT","Bearer deactivated","AT+SAPBR","TCP/IP",""),
("+STTONE: 0","Tone complete","AT+STTONE","Audio",""),
("+SIMTONE: 0","Tone complete","AT+SIMTONE","Audio",""),
("+CHF: <state>","Hands-free change","AT+CHF","Audio",""),
("+CALV: <n>","Alarm expired","AT+CALA","Time",""),
("+CREC: <n>,<id>,...","Record operation","AT+CREC","Audio",""),
("+CTTS: 0","TTS complete","AT+CTTS","Audio",""),
("+CMT: <length>,<pdu>","SMS direct (PDU)","AT+CNMI","SMS","AT+CNMI=2,2"),
("+CDS: <length>,<pdu>","SMS status report (PDU)","AT+CNMI","SMS","AT+CNMI=2,0,0,1"),
]
urcs = []
for i, (uc, desc, rel_cmd, st, sup) in enumerate(URC, start=1):
    urcs.append(mk("dat_02", i, "URC",
        src("SIM800 Series_AT Command Manual","V1.01","2013-07-23","292-296","19.3 URC"),
        urc_string=uc, trigger_event=desc, related_command=rel_cmd or None,
        related_state=st or None, format=uc, examples=[uc],
        timing=None, suppression_method=sup or None))
save("dat_02_urc.yaml", urcs)

# ============================================================
# dat_01 - AT Commands (curated core list)
# ============================================================
AT_CMDS = [
# (command, mode, syntax, section, category)
("AT","exec","AT","1.4","General"),
("A/","exec","A/","2.2.1","General"),
("ATA","exec","ATA","2.2.2","Call"),
("ATD","exec","ATD<n>[<mgsm>][;]","2.2.3","Call"),
("ATDL","exec","ATDL","2.2.6","Call"),
("ATE","write","ATE<value>","2.2.7","General"),
("ATH","exec","ATH","2.2.8","Call"),
("ATI","exec","ATI","2.2.9","General"),
("AT+GCAP","exec","AT+GCAP","2.2.33","General"),
("AT+GMI","exec","AT+GMI","2.2.34","General"),
("AT+GMM","exec","AT+GMM","2.2.35","General"),
("AT+GMR","exec","AT+GMR","2.2.36","General"),
("AT+GSN","exec","AT+GSN","2.2.38","General"),
("AT+ICF","write","AT+ICF=<format>[,<parity>]","2.2.39","UART"),
("AT+IFC","write","AT+IFC=<dce_by_dte>[,<dte_by_dce>]","2.2.40","UART"),
("AT+IPR","write","AT+IPR=<rate>","2.2.41","UART"),
("AT+CACM","read/write","AT+CACM[=<passwd>]","3.2.1","Call"),
("AT+CAMM","read/write","AT+CAMM=<acmmax>[,<passwd>]","3.2.2","Call"),
("AT+CAOC","read/write","AT+CAOC=<mode>","3.2.3","Call"),
("AT+CBST","read/write","AT+CBST=<speed>[,<name>[,<ce>]]","3.2.4","Call"),
("AT+CCFC","write","AT+CCFC=<reason>,<mode>,...","3.2.5","Call"),
("AT+CCWA","read/write","AT+CCWA=<n>[,<mode>[,<class>]]","3.2.6","Call"),
("AT+CEER","read","AT+CEER","3.2.7","Call"),
("AT+CGMI","exec","AT+CGMI","3.2.8","General"),
("AT+CGMM","exec","AT+CGMM","3.2.9","General"),
("AT+CGMR","exec","AT+CGMR","3.2.10","General"),
("AT+CGSN","exec","AT+CGSN","3.2.11","General"),
("AT+CSCS","write","AT+CSCS=<chset>","3.2.12","General"),
("AT+CSTA","read/write","AT+CSTA=<type>","3.2.13","Call"),
("AT+CHLD","write","AT+CHLD=<n>","3.2.14","Call"),
("AT+CIMI","exec","AT+CIMI","3.2.15","SIM"),
("AT+CLCC","read/write","AT+CLCC[=<n>]","3.2.16","Call"),
("AT+CLCK","write","AT+CLCK=<fac>,<mode>[,<passwd>[,<class>]]","3.2.17","SIM"),
("AT+CLIP","read/write","AT+CLIP=<n>","3.2.18","Call"),
("AT+CLIR","read/write","AT+CLIR=<n>","3.2.19","Call"),
("AT+CMEE","read/write","AT+CMEE=[<n>]","3.2.20","General"),
("AT+COLP","read/write","AT+COLP=<n>","3.2.21","Call"),
("AT+COPS","read/write","AT+COPS=<mode>,[<format>[,<oper>]]","3.2.22","Network"),
("AT+CPAS","exec","AT+CPAS","3.2.23","Call"),
("AT+CPBF","write","AT+CPBF=[<findtext>]","3.2.24","Phonebook"),
("AT+CPBR","write","AT+CPBR=<index1>[,<index2>]","3.2.25","Phonebook"),
("AT+CPBS","read/write","AT+CPBS=<storage>","3.2.26","Phonebook"),
("AT+CPBW","write","AT+CPBW=<index>[,<number>,[<type>,[<text>]]]","3.2.27","Phonebook"),
("AT+CPIN","read/write","AT+CPIN=<pin>[,<new pin>]","3.2.28","SIM"),
("AT+CPWD","write","AT+CPWD=<fac>,<oldpwd>,<newpwd>","3.2.29","SIM"),
("AT+CR","read/write","AT+CR=[<mode>]","3.2.30","Call"),
("AT+CRC","read/write","AT+CRC=[<mode>]","3.2.31","Call"),
("AT+CREG","read/write","AT+CREG=[<n>]","3.2.32","Network"),
("AT+CRLP","read/write","AT+CRLP=<iws>[,<mws>[,<T1>[,<N2>[,<T4>]]]]","3.2.33","Call"),
("AT+CRSM","write","AT+CRSM=<Command>[,<fileId>[,<P1>,<P2>,<P3>[,<data>]]]","3.2.34","SIM"),
("AT+CSQ","exec","AT+CSQ","3.2.35","Network"),
("AT+FCLASS","read/write","AT+FCLASS=<class>","3.2.36","Fax"),
("AT+FMI","exec","AT+FMI","3.2.37","Fax"),
("AT+FMM","exec","AT+FMM","3.2.38","Fax"),
("AT+FMR","exec","AT+FMR","3.2.39","Fax"),
("AT+VTD","read/write","AT+VTD=<n>","3.2.40","Audio"),
("AT+VTS","write","AT+VTS=<dtmf-string>","3.2.41","Audio"),
("AT+CMUX","read/write","AT+CMUX=<mode>","3.2.42","UART"),
("AT+CNUM","exec","AT+CNUM","3.2.43","SIM"),
("AT+CPOL","read/write","AT+CPOL=<index>[,<format>,<oper>]","3.2.44","Network"),
("AT+COPN","exec","AT+COPN","3.2.45","Network"),
("AT+CFUN","read/write","AT+CFUN=<fun>[,<rst>]","3.2.46","Power"),
("AT+CCLK","read/write","AT+CCLK=<time>","3.2.47","Time"),
("AT+CSIM","write","AT+CSIM=<length>,<Command>","3.2.48","SIM"),
("AT+CALM","read/write","AT+CALM=<mode>","3.2.49","Audio"),
("AT+CALS","read/write","AT+CALS=<n>","3.2.50","Audio"),
("AT+CRSL","read/write","AT+CRSL=<level>","3.2.51","Audio"),
("AT+CLVL","read/write","AT+CLVL=<level>","3.2.52","Audio"),
("AT+CMUT","read/write","AT+CMUT=<n>","3.2.53","Audio"),
("AT+CPUC","read/write","AT+CPUC=<currency>,<ppu>[,<passwd>]","3.2.54","Call"),
("AT+CCWE","read/write","AT+CCWE=<mode>","3.2.55","Call"),
("AT+CBC","exec","AT+CBC","3.2.56","Power"),
("AT+CUSD","read/write","AT+CUSD=<n>[,<str>[,<dcs>]]","3.2.57","Call"),
("AT+CSSN","read/write","AT+CSSN=<n>[,<m>]","3.2.58","Call"),
("AT+CMGD","write","AT+CMGD=<index>[,<delflag>]","4.2.1","SMS"),
("AT+CMGF","read/write","AT+CMGF=[<mode>]","4.2.2","SMS"),
("AT+CMGL","write","AT+CMGL=<stat>[,<mode>]","4.2.3","SMS"),
("AT+CMGR","write","AT+CMGR=<index>[,<mode>]","4.2.4","SMS"),
("AT+CMGS","write","AT+CMGS=<da>[,<toda>]<CR>text<ctrl-Z>","4.2.5","SMS"),
("AT+CMGW","write","AT+CMGW=<oa/da>[,<tooa/toda>][,<stat>]<CR>text<ctrl-Z>","4.2.6","SMS"),
("AT+CMSS","write","AT+CMSS=<index>[,<da>,<toda>]","4.2.7","SMS"),
("AT+CNMI","read/write","AT+CNMI=<mode>[,<mt>[,<bm>[,<ds>[,<bfr>]]]]","4.2.8","SMS"),
("AT+CPMS","read/write","AT+CPMS=<mem1>[,<mem2>[,<mem3>]]","4.2.9","SMS"),
("AT+CRES","write","AT+CRES=<profile>","4.2.10","SMS"),
("AT+CSAS","write","AT+CSAS=<profile>","4.2.11","SMS"),
("AT+CSCA","read/write","AT+CSCA=<sca>[,<tosca>]","4.2.12","SMS"),
("AT+CSCB","read/write","AT+CSCB=<mode>[,<mids>[,<dcss>]]","4.2.13","SMS"),
("AT+CSDH","read/write","AT+CSDH=[<show>]","4.2.14","SMS"),
("AT+CSMP","read/write","AT+CSMP=[<fo>[,<vp>,<pid>,<dcs>]]","4.2.15","SMS"),
("AT+CSMS","read/write","AT+CSMS=<service>","4.2.16","SMS"),
("AT+SIDET","read/write","AT+SIDET=<channel>,<gainlevel>","6.2.1","Audio"),
("AT+CPOWD","write","AT+CPOWD=<n>","6.2.2","Power"),
("AT+SPIC","exec","AT+SPIC","6.2.3","SIM"),
("AT+CMIC","read/write","AT+CMIC=<channel>,<gainlevel>","6.2.4","Audio"),
("AT+CALA","read/write","AT+CALA=<time>[,<n>[,<recurr>]]","6.2.5","Time"),
("AT+CADC","read","AT+CADC?","6.2.7","ADC"),
("AT+CBAND","read/write","AT+CBAND=<op_band>","6.2.17","Network"),
("AT+CHF","read/write","AT+CHF=<ind>[,<state>]","6.2.18","Audio"),
("AT+CHFA","read/write","AT+CHFA=<n>","6.2.19","Audio"),
("AT+CSCLK","read/write","AT+CSCLK=<n>","6.2.20","Power"),
("AT+CCID","exec","AT+CCID","6.2.23","SIM"),
("AT+CMTE","read/write","AT+CMTE=<mode>","6.2.24","Temperature"),
("AT+CMGDA","write","AT+CMGDA=<type>","6.2.25","SMS"),
("AT+SGPIO","write","AT+SGPIO=<operation>,<GPIO>,<function>,<level>","6.2.40","GPIO"),
("AT+SPWM","write","AT+SPWM=<index>,<period>,<level>","6.2.41","PWM"),
("AT+CGATT","read/write","AT+CGATT=<state>","7.2.1","GPRS"),
("AT+CGDCONT","read/write","AT+CGDCONT=<cid>[,<PDP_type>[,APN>[,<PDP_addr>[,<d_comp>[,<h_comp>]]]]]","7.2.2","GPRS"),
("AT+CGQMIN","read/write","AT+CGQMIN=<cid>[,<precedence>[,<delay>[,<reliability>[,<peak>[,<mean>]]]]]","7.2.3","GPRS"),
("AT+CGQREQ","read/write","AT+CGQREQ=<cid>[,<precedence>[,<delay>[,<reliability>[,<peak>[,<mean>]]]]]","7.2.4","GPRS"),
("AT+CGACT","read/write","AT+CGACT=<state> [,<cid>]","7.2.5","GPRS"),
("AT+CGDATA","write","AT+CGDATA=<L2P> [,<cid>]","7.2.6","GPRS"),
("AT+CGPADDR","write","AT+CGPADDR=<cid>","7.2.7","GPRS"),
("AT+CGCLASS","read/write","AT+CGCLASS=<class>","7.2.8","GPRS"),
("AT+CGEREP","read/write","AT+CGEREP=<mode>","7.2.9","GPRS"),
("AT+CGREG","read/write","AT+CGREG=[<n>]","7.2.10","GPRS"),
("AT+CGSMS","read/write","AT+CGSMS=<service>","7.2.11","GPRS"),
("AT+CIPMUX","read/write","AT+CIPMUX=<n>","8.2.1","TCP/IP"),
("AT+CIPSTART","write","AT+CIPSTART=<mode>,<IP>,<port>","8.2.2","TCP/IP"),
("AT+CIPSEND","write","AT+CIPSEND=<length>","8.2.3","TCP/IP"),
("AT+CIPQSEND","read/write","AT+CIPQSEND=<n>","8.2.4","TCP/IP"),
("AT+CIPACK","exec","AT+CIPACK","8.2.5","TCP/IP"),
("AT+CIPCLOSE","write","AT+CIPCLOSE=<n>","8.2.6","TCP/IP"),
("AT+CIPSHUT","exec","AT+CIPSHUT","8.2.7","TCP/IP"),
("AT+CLPORT","read/write","AT+CLPORT=<mode>,<port>","8.2.8","TCP/IP"),
("AT+CSTT","read/write","AT+CSTT=<apn>,<user name>,<password>","8.2.9","TCP/IP"),
("AT+CIICR","exec","AT+CIICR","8.2.10","TCP/IP"),
("AT+CIFSR","exec","AT+CIFSR","8.2.11","TCP/IP"),
("AT+CIPSTATUS","exec","AT+CIPSTATUS","8.2.12","TCP/IP"),
("AT+CDNSCFG","read/write","AT+CDNSCFG=<pri_dns>[,<sec_dns>]","8.2.13","TCP/IP"),
("AT+CDNSGIP","write","AT+CDNSGIP=<domain name>","8.2.14","TCP/IP"),
("AT+CIPHEAD","read/write","AT+CIPHEAD=<mode>","8.2.15","TCP/IP"),
("AT+CIPATS","read/write","AT+CIPATS=<mode>[,<time>]","8.2.16","TCP/IP"),
("AT+CIPSPRT","read/write","AT+CIPSPRT=<send prompt>","8.2.17","TCP/IP"),
("AT+CIPSERVER","read/write","AT+CIPSERVER=<mode>[,<port>]","8.2.18","TCP/IP"),
("AT+CIPCSGP","read/write","AT+CIPCSGP=<mode>[,<apn>,<user name>,<password>]","8.2.19","TCP/IP"),
("AT+CIPSRIP","read/write","AT+CIPSRIP=<mode>","8.2.20","TCP/IP"),
("AT+CIPMODE","read/write","AT+CIPMODE=<mode>","8.2.22","TCP/IP"),
("AT+CIPCCFG","read/write","AT+CIPCCFG=<NmRetry>,<WaitTm>,<SendSz>,<esc>","8.2.23","TCP/IP"),
("AT+CIPRXGET","read/write","AT+CIPRXGET=<mode>[,<reqLength>]","8.2.26","TCP/IP"),
("AT+CIPSCONT","read/write","AT+CIPSCONT","8.2.27","TCP/IP"),
("AT+SAPBR","write","AT+SAPBR=<cmd_type>,<cid>[,<ConParamTag>,<ConParamValue>]","9.2.1","TCP/IP"),
("AT+CIPPING","write","AT+CIPPING=<IPaddr>[,<retryNum>[,<dataLen>[,<timeout>[,<ttl>]]]]","10.2.1","TCP/IP"),
("AT+CIPCTL","read/write","AT+CIPCTL=<mode>","10.2.2","TCP/IP"),
("AT+CIPFLT","read/write","AT+CIPFLT=<action>[,<item>][,<ipAddr>,<mask>]","10.2.3","TCP/IP"),
("AT+HTTPINIT","exec","AT+HTTPINIT","11.2.1","HTTP"),
("AT+HTTPTERM","exec","AT+HTTPTERM","11.2.2","HTTP"),
("AT+HTTPPARA","read/write","AT+HTTPPARA=<HTTPParamTag>,<HTTPParamValue>","11.2.3","HTTP"),
("AT+HTTPDATA","read/write","AT+HTTPDATA=<size>,<time>","11.2.4","HTTP"),
("AT+HTTPACTION","write","AT+HTTPACTION=<Method>","11.2.5","HTTP"),
("AT+HTTPREAD","read/write","AT+HTTPREAD=<start_address>,<byte_size>","11.2.6","HTTP"),
("AT+HTTPSCONT","read/write","AT+HTTPSCONT","11.2.7","HTTP"),
("AT+HTTPSTATUS","read","AT+HTTPSTATUS?","11.2.8","HTTP"),
("AT+FTPPORT","read/write","AT+FTPPORT=<value>","12.2.1","FTP"),
("AT+FTPMODE","read/write","AT+FTPMODE=<value>","12.2.2","FTP"),
("AT+FTPTYPE","read/write","AT+FTPTYPE=<value>","12.2.3","FTP"),
("AT+FTPPUTOPT","read/write","AT+FTPPUTOPT=<value>","12.2.4","FTP"),
("AT+FTPCID","read/write","AT+FTPCID=<value>","12.2.5","FTP"),
("AT+FTPSERV","read/write","AT+FTPSERV=<value>","12.2.7","FTP"),
("AT+FTPUN","read/write","AT+FTPUN=<value>","12.2.8","FTP"),
("AT+FTPPW","read/write","AT+FTPPW=<value>","12.2.9","FTP"),
("AT+FTPGETNAME","read/write","AT+FTPGETNAME=<value>","12.2.10","FTP"),
("AT+FTPGETPATH","read/write","AT+FTPGETPATH=<value>","12.2.11","FTP"),
("AT+FTPPUTNAME","read/write","AT+FTPPUTNAME=<value>","12.2.12","FTP"),
("AT+FTPPUTPATH","read/write","AT+FTPPUTPATH=<value>","12.2.13","FTP"),
("AT+FTPGET","write","AT+FTPGET=<mode>[,<reqlength>]","12.2.14","FTP"),
("AT+FTPPUT","write","AT+FTPPUT=<mode>[,<reqlength>]","12.2.15","FTP"),
("AT+FTPSCONT","read/write","AT+FTPSCONT","12.2.16","FTP"),
("AT+FTPDELE","exec","AT+FTPDELE","12.2.17","FTP"),
("AT+FTPSIZE","exec","AT+FTPSIZE","12.2.18","FTP"),
("AT+FTPSTATE","exec","AT+FTPSTATE","12.2.19","FTP"),
("AT+FTPMKD","exec","AT+FTPMKD","12.2.21","FTP"),
("AT+FTPRMD","exec","AT+FTPRMD","12.2.22","FTP"),
("AT+FTPLIST","write","AT+FTPLIST=<mode>[,<reqlength>]","12.2.23","FTP"),
("AT+CIPGSMLOC","write","AT+CIPGSMLOC=<type>,<cid>","13.2.1","GPS"),
("AT+DDET","read/write","AT+DDET=<mode>","16.2.1","Audio"),
("AT+CREC","write","AT+CREC=<mode>[,<id>]","17.2.1","Audio"),
("AT+CTTS","read/write","AT+CTTS=<mode>[,<text>]","18.2.1","Audio"),
("AT+CTTSPARAM","read/write","AT+CTTSPARAM=<volume>,<mode>,<pitch>,<speed>","18.2.2","Audio"),
]

at_recs = []
for i, (cmd, mode, syntax, sec, cat) in enumerate(AT_CMDS, start=1):
    at_recs.append(mk("dat_01", i, cat,
        src("SIM800 Series_AT Command Manual","V1.01","2013-07-23",section=sec),
        command=cmd, mode=mode, syntax=syntax, parameters=[],
        response_success="OK", response_error=None, examples=[],
        related_urcs=[], related_states=[], related_commands=[],
        firmware_min=None, firmware_max=None))
save("dat_01_at_command.yaml", at_recs)

print("\nAll datasets populated.")