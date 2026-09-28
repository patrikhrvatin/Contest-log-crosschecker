# IARU HF World Championship Cross-Checker & Log Analyzer

A high-performance Python script designed to process, cross-check, and analyze massive volumes of Cabrillo log files (100,000+ connections) for radio amateur contests—specifically tuned for the **IARU HF World Championship**.

---

## 🚀 Key Optimizations for Large Datasets

Processing tens of thousands of log records can easily become a performance bottleneck due to $O(N)$ search complexities. This script implements several architectural improvements:
1. **$O(1)$ Partner Indexing:** Instead of linearly scanning partner logs for every single QSO, the script pre-builds hash-map indexes (`partner_indeks[partner] = [qso_list]`), dropping lookup times to near-instantaneous.
2. **Fast Membership Checks (`set`):** Utilizes Python sets for rapid verification against HQ databases, `master.scp`, and `RECEIVED_LOG.TXT`.
3. **Multi-Band Memory Caching:** Caches partner-band combinations into memory sets for ultra-fast multi-band validation.
4. **Optimized Disk I/O:** Accumulates log text lines in lists and performs a single write operation (`"".join()`) at the end of each report generation, avoiding heavy I/O overhead.

---

## 🛠️ Features

- **Cross-Check Validation:** Compares your logs against your partners' logs within a strict 10-minute time window and matching frequency band.
- **HQ Base Verification:** Validates official IARU HQ stations and matches expected organization acronyms.
- **Smart Typo Detection (`[TIPFELER?]`):** Uses Python's `difflib` along with activity filters to suggest correct callsigns when a typo is encountered.
- **Comprehensive Error Categorization:** Detects:
  - `[OK - CROSS]` (Mutually confirmed)
  - `[NIL - Not in Log]`
  - `[GREŠKA VREMENA]` (Time difference > 10 min)
  - `[GREŠKA BANDA]` (Logged on a different band)
  - `[HQ / BAZA greške]`
- **Automated Reporting:** Generates individual text reports (`izvjestaj_<CALL>.txt`) for every station and a global sorted summary file (`all_calls_stats.txt`).

---

## 📂 Required File Structure

Place the script in a directory alongside your log files and reference databases:
```text
C:\Your_Folder\
│
├── cross20.py            # The optimization script
├── iaruhq.txt            # Official IARU HQ stations list
├── master.scp            # Super Check Partial callsign database
├── RECEIVED_LOG.TXT      # Official received logs list
└── *.log / *.cbr         # Cabrillo contest log files to analyze
```

---

## 💻 Installation & Usage

1. Ensure you have **Python 3.x** installed. No external third-party libraries are required (uses standard library modules like `os`, `difflib`, and `datetime`).
2. Place `cross20.py` in your working directory containing your `.log` or `.cbr` files.
3. Run the script from your terminal:

```bash
python cross20.py
```

---

## 📜 License
This project is open-source and free to use for the radio amateur community. Contributions and improvements are welcome!
