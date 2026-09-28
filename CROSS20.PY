import os
import difflib
from datetime import datetime, timedelta

def ucitaj_iaru_hq_baze(putanja_baze="iaruhq.txt"):
    hq_rjecnik = {}
    hq_set = set()
    if not os.path.exists(putanja_baze):
        print(f"Upozorenje: Datoteka '{putanja_baze}' nije pronađena!")
        return hq_rjecnik, hq_set
        
    print(f"Učitavam HQ bazu iz '{putanja_baze}'...")
    with open(putanja_baze, 'r', encoding='utf-8', errors='ignore') as f:
        for redak in f:
            redak_s = redak.strip()
            if redak_s and not redak_s.startswith(('#', '!')):
                if '=' in redak_s:
                    pozivni, savez = redak_s.split('=', 1)
                    hq_rjecnik[pozivni.strip().upper()] = savez.strip().upper()
                    hq_set.add(pozivni.strip().upper())
                    
    print(f"Učitano {len(hq_rjecnik)} HQ stanica iz baze.")
    return hq_rjecnik, hq_set

def ucitaj_master_scp(putanja_scp="master.scp"):
    znakovi = set()
    if not os.path.exists(putanja_scp):
        print(f"Info: 'master.scp' nije pronađen. Nastavljam bez njega.")
        return znakovi
        
    print(f"Učitavam Super Check Partial bazu iz '{putanja_scp}'...")
    with open(putanja_scp, 'r', encoding='utf-8', errors='ignore') as f:
        for redak in f:
            redak_s = redak.strip()
            if redak_s and not redak_s.startswith(('!', '#')):
                dijelovi = redak_s.split()
                if dijelovi:
                    znakovi.add(dijelovi[0].upper())
                    
    print(f"Učitano {len(znakovi)} znakova iz master.scp baze.")
    return znakovi

def pronadji_log_datoteke(direktorij="."):
    podrzane_datoteke = {}
    for datoteka in os.listdir(direktorij):
        if datoteka.lower().endswith(('.log', '.cbr')):
            if datoteka.upper() != "RECEIVED_LOG.TXT":
                naziv_stanice = os.path.splitext(datoteka)[0].upper()
                podrzane_datoteke[naziv_stanice] = datoteka
    return podrzane_datoteke

def parsiraj_vrijeme(datum_str, vrijeme_str):
    for fmt_d in ("%Y-%m-%d", "%Y%m%d", "%d-%m-%Y"):
        for fmt_t in ("%H%M", "%H:%M"):
            try:
                return datetime.strptime(f"{datum_str} {vrijeme_str}", f"{fmt_d} {fmt_t}")
            except ValueError:
                continue
    return None

def odredi_band(freq_str):
    try:
        f = float(freq_str)
        if f > 1000:
            if 1800 <= f <= 2000: return "160M"
            if 3500 <= f <= 4000: return "80M"
            if 7000 <= f <= 7200: return "40M"
            if 14000 <= f <= 14350: return "20M"
            if 21000 <= f <= 21450: return "15M"
            if 28000 <= f <= 29700: return "10M"
        else:
            if 1.8 <= f <= 2.0: return "160M"
            if 3.5 <= f <= 4.0: return "80M"
            if 7.0 <= f <= 7.2: return "40M"
            if 14.0 <= f <= 14.35: return "20M"
            if 21.0 <= f <= 21.45: return "15M"
            if 28.0 <= f <= 29.7: return "10M"
        return f"HQ/Other ({freq_str})"
    except ValueError:
        return freq_str

def ucitaj_cabrillo_detaljno(putanja_datoteke, pozivni_znak=""):
    qso_lista = []
    if not os.path.exists(putanja_datoteke):
        return qso_lista
        
    with open(putanja_datoteke, 'r', encoding='utf-8', errors='ignore') as f:
        linije = f.readlines()
        
    for redak in linije:
        if redak.startswith("QSO:"):
            dijelovi = redak.strip().split()
            if len(dijelovi) >= 10:
                partner = dijelovi[8].upper()
                primljena_razmjena = " ".join(dijelovi[9:]).strip()
                dt = parsiraj_vrijeme(dijelovi[3], dijelovi[4])
                band = odredi_band(dijelovi[1])
                mod = dijelovi[2].upper()
                
                qso_lista.append({
                    'frekvencija': dijelovi[1],
                    'band': band,
                    'mod': mod,
                    'datum': dijelovi[3],
                    'vrijeme': dijelovi[4],
                    'datetime': dt,
                    'partner': partner,
                    'razmjena': primljena_razmjena
                })
                    
    return qso_lista

def odredi_izvor_znaka(znak, hq_set, received_set, scp_set, globalni_indeksi_partnera):
    izvori = []
    pronadjen_u_logovima = [p for p, indeks in globalni_indeksi_partnera.items() if p == znak or znak in indeks]
                        
    if pronadjen_u_logovima:
        izvori.append(f"logovi: {', '.join(pronadjen_u_logovima)}")
    if znak in received_set:
        izvori.append("RECEIVED_LOG.TXT")
    if znak in hq_set:
        izvori.append("HQ baza")
    if znak in scp_set:
        izvori.append("master.scp")
        
    return " | ".join(izvori) if izvori else "nepoznat izvor"

def generiraj_txt_statistiku(sve_statistike):
    sortirane_statistike = sorted(sve_statistike, key=lambda x: x['ukupno_qso'], reverse=True)
    
    tekst = "==================================================\n"
    tekst += " SVEUKUPNA STATISTIKA SVIH POZIVNIH ZNAKOVA\n"
    tekst += "==================================================\n\n"
    
    for stat in sortirane_statistike:
        call = stat['pozivni']
        tekst += f"SAŽETAK ZA {call}:\n"
        tekst += "--------------------------------------------------\n"
        tekst += f" - Ukupno QSO: {stat['ukupno_qso']}\n"
        tekst += f" - Obostrano potvrđenih (Cross-check OK): {stat['ok_cross']}\n"
        tekst += f" - Ostalih ispravnih veza (HQ / baza): {stat['ok_ostalo']}\n"
        tekst += f" - HQ grešaka: {stat['hq_err']}\n"
        tekst += f" - Grešaka vremena (>10 min): {stat['err_time']}\n"
        tekst += f" - Grešaka banda: {stat['err_band']}\n"
        tekst += f" - Nema u logu partnera (NIL): {stat['nil']}\n"
        tekst += f" - Mogućih tipfelera: {stat['tip']}\n"
        tekst += f" - Nepoznatih: {stat['nepoznato']}\n\n"
        
    with open("all_calls_stats.txt", "w", encoding="utf-8") as f:
        f.write(tekst)
    print("Kreirana zbirna tekstualna statistika: 'all_calls_stats.txt'")

def generiraj_zasebne_izvjestaje(hq_rjecnik, hq_set, received_set, scp_set):
    rjecnik_stanica = pronadji_log_datoteke()
    if not rjecnik_stanica:
        print("Nisu pronađene nikakve .log ili .cbr datoteke u ovoj mapi!")
        return

    print(f"\nPronađene log datoteke za obradu: {list(rjecnik_stanica.values())}\n")
    
    globalni_logovi = {}
    globalni_indeksi_partnera = {}
    aktivnost_mreze = {} 
    svi_poznati_pozivni_u_mreze = set(received_set).union(hq_set).union(scp_set)
    
    for pozivni, putanja in rjecnik_stanica.items():
        print(f"Učitavam i indeksiram log za: {pozivni} ({putanja})...")
        qso_s = ucitaj_cabrillo_detaljno(putanja, pozivni)
        globalni_logovi[pozivni] = qso_s
        
        # Izgradnja O(1) indeksa partnera za brže pretraživanje
        partner_indeks = {}
        for q in qso_s:
            p = q['partner']
            if p not in partner_indeks:
                partner_indeks[p] = []
            partner_indeks[p].append(q)
        globalni_indeksi_partnera[pozivni] = partner_indeks
        
        svi_poznati_pozivni_u_mreze.add(pozivni)
        
        if pozivni not in aktivnost_mreze:
            aktivnost_mreze[pozivni] = set()
            
        for veza in qso_s:
            aktivnost_mreze[pozivni].add((veza['band'], veza['mod']))
            p = veza['partner']
            svi_poznati_pozivni_u_mreze.add(p)
            if p not in aktivnost_mreze:
                aktivnost_mreze[p] = set()
            aktivnost_mreze[p].add((veza['band'], veza['mod']))

    print("\nPokrećem brzu unakrsnu provjeru i analizu tipfelera...\n")

    sve_statistike = []

    for pozivni_znak, putanja_loga in rjecnik_stanica.items():
        qso_lista = globalni_logovi[pozivni_znak]
        
        # Brzi set za multi-band provjeru u vlastitom logu: pohranjuje (partner, band)
        vlastiti_partner_bandovi = {(q['partner'], q['band']) for q in qso_lista}
        
        ok_cross_count = 0
        ok_count = 0
        hq_ok_count = 0
        hq_err_count = 0
        cross_err_time_count = 0
        cross_err_band_count = 0
        nil_count = 0
        tip_count = 0
        nepoznato_count = 0
        
        izlazni_redci = [
            "==================================================",
            f" IZVJEŠTAJ ANALIZE NATJECANJA: {pozivni_znak}",
            f" Izvorna datoteka: {putanja_loga}",
            "==================================================\n"
        ]
        
        for veza in qso_lista:
            partner = veza['partner']
            razmjena = veza['razmjena']
            trenutni_band = veza['band']
            trenutni_mod = veza['mod']
            status_tekst = ""
            detalji_statusa = ""
            
            if partner in globalni_logovi:
                # O(1) dohvat preko indeksa umjesto petlje kroz sve veze
                partner_indeks = globalni_indeksi_partnera[partner]
                partner_qso_lista = partner_indeks.get(pozivni_znak, [])
                pronaden_partner_qso = None
                greska_tip = None 
                
                for pq in partner_qso_lista:
                    isti_band = (pq['band'] == trenutni_band)
                    ista_vremenska_blizina = False
                    if veza['datetime'] and pq['datetime']:
                        diff = abs(veza['datetime'] - pq['datetime'])
                        if diff <= timedelta(minutes=10):
                            ista_vremenska_blizina = True
                    
                    if isti_band and ista_vremenska_blizina:
                        pronaden_partner_qso = pq
                        break
                    elif not isti_band and ista_vremenska_blizina:
                        greska_tip = 'band'
                    elif isti_band and not ista_vremenska_blizina:
                        greska_tip = 'vrijeme'

                if pronaden_partner_qso:
                    ok_cross_count += 1
                    status_tekst = "[OK - CROSS]"
                    detalji_statusa = "Obostrano potvrđeno u logu partnera (vrijeme i band usklađeni)"
                elif greska_tip == 'band':
                    cross_err_band_count += 1
                    status_tekst = "[GREŠKA BANDA]"
                    detalji_statusa = "Partner vas je zabilježio na drugom bandu"
                elif greska_tip == 'vrijeme':
                    cross_err_time_count += 1
                    status_tekst = "[GREŠKA VREMENA]"
                    detalji_statusa = "Partner vas je zabilježio, ali je razlika u vremenu veća od 10 minuta!"
                else:
                    nil_count += 1
                    status_tekst = "[NIL - NEMA U LOGU]"
                    detalji_statusa = "Partner (natjecatelj) ima vaš pozivni znak u logu, ali nema ove veze (NIL)"

            elif partner in hq_set:
                ocekivani_savez = hq_rjecnik[partner]
                if ocekivani_savez in razmjena:
                    hq_ok_count += 1
                    status_tekst = "[OK - HQ]"
                    detalji_statusa = f"Usklađeno s HQ bazom (Očekivano: {ocekivani_savez})"
                else:
                    hq_err_count += 1
                    status_tekst = "[GREŠKA HQ]"
                    detalji_statusa = f"Upisan savez '{razmjena}', očekivani je '{ocekivani_savez}'!"
            elif partner in received_set:
                ok_count += 1
                status_tekst = "[OK]"
                detalji_statusa = "Usklađeno s RECEIVED_LOG.TXT bazom"
            elif postojec_u_ostalim_logovima(partner, globalni_logovi, pozivni_znak):
                ok_count += 1
                status_tekst = "[OK]"
                detalji_statusa = "Znak postoji u ostalim logovima natjecatelja"
            elif any(p == partner and b != trenutni_band for p, b in vlastiti_partner_bandovi):
                ok_count += 1
                status_tekst = "[OK - MULTI]"
                detalji_statusa = "Znak je već uspješno odrađen na drugom bandu u vašem logu (siguran unos)"
            else:
                slicni = difflib.get_close_matches(partner, list(svi_poznati_pozivni_u_mreze), n=5, cutoff=0.7)
                validirani_prijedlozi = []
                for s in slicni:
                    if s == partner:
                        continue  
                        
                    aktivnost_kandidata = aktivnost_mreze.get(s, set())
                    aktivan = (not aktivnost_kandidata or (trenutni_band, trenutni_mod) in aktivnost_kandidata)
                    izvor_str = odredi_izvor_znaka(s, hq_set, received_set, scp_set, globalni_indeksi_partnera)
                    validirani_prijedlozi.append((s, aktivan, izvor_str))
                
                validirani_prijedlozi.sort(key=lambda x: x[1], reverse=True)
                top_slicni = validirani_prijedlozi[:3]
                
                if top_slicni:
                    tip_count += 1
                    prijedlozi_opisi = [f"{item[0]} [{item[2]}]" for item in top_slicni]
                    prijedlozi_str = ", ".join(prijedlozi_opisi)
                    status_tekst = "[TIPFELER?]"
                    detalji_statusa = f"Jeste li mislili na: {prijedlozi_str}? (Provjereno po bandu/modu: {trenutni_band} {trenutni_mod}, Primljeno: {razmjena})"
                else:
                    nepoznato_count += 1
                    status_tekst = "[NEPOZNATO]"
                    detalji_statusa = f"Nema sličnosti u bazama niti u mreži logova. (Primljeno: {razmjena})"
                    
            izlazni_redci.append(f"QSO: {veza['datum']} {veza['vrijeme']} | Band: {trenutni_band} ({veza['frekvencija']} kHz) | {trenutni_mod} | Partner: {partner} | Razmjena: {razmjena} | Status: {status_tekst} - {detalji_statusa}")
            
        ukupno = len(qso_lista)
        sve_statistike.append({
            'pozivni': pozivni_znak,
            'ukupno_qso': ukupno,
            'ok_cross': ok_cross_count,
            'ok_ostalo': ok_count + hq_ok_count,
            'hq_err': hq_err_count,
            'err_time': cross_err_time_count,
            'err_band': cross_err_band_count,
            'nil': nil_count,
            'tip': tip_count,
            'nepoznato': nepoznato_count
        })

        izlazni_redci.extend([
            "\n--------------------------------------------------",
            f"SAŽETAK ZA {pozivni_znak}:",
            "--------------------------------------------------",
            f" - Ukupno QSO: {ukupno}",
            f" - Obostrano potvrđenih (Cross-check OK): {ok_cross_count}",
            f" - Ostalih ispravnih veza (HQ / baza): {ok_count + hq_ok_count}",
            f" - HQ grešaka: {hq_err_count}",
            f" - Grešaka vremena (>10 min): {cross_err_time_count}",
            f" - Grešaka banda: {cross_err_band_count}",
            f" - Nema u logu partnera (NIL): {nil_count}",
            f" - Mogućih tipfelera: {tip_count}",
            f" - Nepoznatih: {nepoznato_count}"
        ])

        naziv_izvjestaja = f"izvjestaj_{pozivni_znak}.txt"
        # Korištenje .join() umjesto višekratnog spajanja stringova značajno ubrzava I/O zapis na disk
        with open(naziv_izvjestaja, 'w', encoding='utf-8') as izlaz_txt:
            izlaz_txt.write("\n".join(izlazni_redci))
        print(f"Kreiran pojedinačni izvještaj: '{naziv_izvjestaja}'")

    generiraj_txt_statistiku(sve_statistike)
    print("\nSve analize, zasebni izvještaji i zbirna tekstualna statistika uspješno su generirani!")

def postojec_u_ostalim_logovima(partner, globalni_logovi, trenutna_stanica):
    for p_stanica, qso_s in globalni_logovi.items():
        if p_stanica == trenutna_stanica:
            continue
        for veza in qso_s:
            if veza['partner'] == partner:
                return True
    return False

if __name__ == "__main__":
    hq_rjecnik, hq_set = ucitaj_iaru_hq_baze("iaruhq.txt")
    scp_set = ucitaj_master_scp("master.scp")
    
    received_set = set()
    if os.path.exists("RECEIVED_LOG.TXT"):
        with open("RECEIVED_LOG.TXT", 'r', encoding='utf-8', errors='ignore') as f:
            for redak in f:
                received_set.update(redak.strip().split())
                
    print(f"Učitano {len(received_set)} znakova iz RECEIVED_LOG.TXT baze.\n")
    generiraj_zasebne_izvjestaje(hq_rjecnik, hq_set, received_set, scp_set)