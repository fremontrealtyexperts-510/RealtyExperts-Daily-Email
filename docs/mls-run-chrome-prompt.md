# MLS Run — Claude-in-Chrome prompt

The paste-in instruction for the Claude for Chrome extension. It does the browser half only: log in → run the "RealtyExperts" saved search → export "MLS Defined Spread Sheet 4" to CSV. The CSV download is then picked up by `mls-csv-to-images.py` to build RE-Daily-1/2.png.

---

## One-time setup (NOT part of the paste — do once in Chrome)

1. Chrome → Settings → Downloads → turn **OFF** "Ask where to save each file before downloading" (so the export auto-downloads with no macOS Save dialog the agent can't operate).
2. Set the Download **Location** to the Google-Drive-for-Desktop folder that maps to `Daily-Reports/Daily-Realty-Experts/Raw-data` (so the CSV syncs to Drive where the renderer reads it). *(Path TBD — confirm the local mount path.)*
3. Be signed into the Chrome profile that has the MLS session / the right Google account (`harvrealtor@gmail.com`).

Before pasting: replace `{{MLS_USERNAME}}` and `{{MLS_PASSWORD}}` with your MLS login (or delete the login block and log in manually first, then paste). Keep your filled-in copy private — don't commit it.

---

## THE PROMPT (copy everything in the block)

```
You are operating my Chrome browser to run my daily MLS report export. Work carefully and verify each step before moving on. You are ONLY running an existing saved search and exporting it — do NOT change any search criteria, save anything, or modify any settings.

GOAL: Log into the MLS, run my saved search "RealtyExperts", open the "MLS Defined Spread Sheet 4" report, and export it to CSV for all listings. The file downloads automatically.

STEPS:

1. Go to https://maxebrdi.clareityiam.net/idp/login
   - If you are already logged in and land on the Paragon / BAYEAST dashboard ("Welcome Harv Balu"), skip to step 3.
   - Otherwise log in with:
     Username: {{MLS_USERNAME}}
     Password: {{MLS_PASSWORD}}
   Click the sign-in button and wait for the Paragon dashboard to load.

2. Confirm the Paragon dashboard loaded (top navigation shows HOME, SEARCH, LISTINGS, CMA, CONTACTS, ...).

3. Click "SEARCH" in the top navigation. In the menu that appears, under "SEARCH BY CLASS", click "Residential".

4. On the Residential search page, click "Load Search" in the toolbar near the top-left (its tooltip says "Load Saved Search").

5. In the "Load Saved Search" popup:
   - Set the Filter dropdown to "My Searches".
   - Click the saved search named exactly "RealtyExperts".
   - The popup closes and the criteria load (Status and City chips fill in).
   - VERIFY the City chips include FREMONT, OAKLAND, HAYWARD, etc. If "RealtyExperts" is not in the list, STOP and tell me.

6. Click the "Search" button (top-right, next to "Count") to run the search.

7. Wait for the results grid to load and note the total listing count (shown as "Page 1 of N" and/or a count near the top).
   - SANITY CHECK: the count should be roughly 2,000-5,000 (usually ~2,900-3,300). If it is far outside that range, STOP and tell me the count — do not export.

8. Click the green "REPORTS" button (top-right). An "Available Reports" panel opens.

9. In that panel, under "Favorites", click "MLS Defined Spread Sheet 4".

10. The report loads as a spreadsheet view. In the toolbar click "Export", then click "Export to CSV".

11. In the "Export to (CSV) Excel" popup:
    - Under SELECT LISTING(S), choose "All Listings".
    - Under SELECT SPREADSHEET, confirm it is "MLS Defined Spread Sheet 4".
    - Click "Export".

12. The CSV downloads automatically. Confirm the download completed.

WHEN DONE, report back: the total listing count you saw, the downloaded file name, and confirmation that the CSV export succeeded.

IF ANYTHING IS UNEXPECTED — a login you can't complete, a macOS "Save As" dialog box appears, the "RealtyExperts" search isn't found, the count is out of range, or a popup blocks you — STOP and describe exactly what you see instead of guessing.
```

---

## Notes
- The exact downloaded filename doesn't matter; the renderer picks the newest `MLS_Defined_Spread_Sheet_4*.csv`.
- If a native "Save As" dialog appears, the one-time setup (step 1) wasn't applied — the agent can't operate it.
- You can test this prompt's browser half right now: it will download the CSV wherever Chrome saves. Wiring the CSV→PNG→Drive auto-step is the next piece.
