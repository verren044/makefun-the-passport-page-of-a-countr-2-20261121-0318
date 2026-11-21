# BUILD_LOG — the-passport-page-of-a-countr-2-20261121-0318

Contest: The Passport Page of a Country That Isn't There
Slug: the-passport-page-of-a-countr-2-20261121-0318
Prize: $50 shared by top 20 (1st $18 … 20th $1)
Deadline: Sat 21 Nov 2026 13:18 WIB (06:18 UTC)
Built: Sat 21 Nov 2026 ~11:48–12:00 WIB

## What was built

`main.py` (Python 3.13, stdlib only) draws an open passport spread for the
invented Republic of Meridia and writes `/output/entry.png`:

- Left page (data page): navy "REPUBLIC OF MERIDIA" header band, gold
  emblem (shield + star), "PASSPORT", type P / code MRD / No. MRD4829137,
  stylised portrait of holder Elena Mara Voss (b. 14 JUN 1996, Port
  Aurelia), data fields (surname, given names, nationality, DOB, place of
  birth, sex F, issue 12 MAR 2024, expiry 11 MAR 2034, authority Ministry
  of the Interior — Port Aurelia, holder's signature), and an ICAO MRZ
  whose check digits are computed with 7-3-1 weights.
- Right page (visas): "VISAS" header, visitor-visa sticker (multiple
  entry, valid 90 days from first entry, fee paid 40 AUR, employment not
  permitted, No. V-2024-11873), four stamps from the three neighbours in
  travel order — Kestrelia ARRIVED 04 APR 2024 Trelhavn (blue circle),
  Vardonia DEPARTED 19 SEP 2024 Korvest (rotated rectangle), Ostara
  ARRIVED 02 FEB 2025 Veldmar (green circle), Kestrelia DEPARTED
  27 MAY 2025 Trelhavn (blue circle) — plus a red "FEE 40 AUR PAID" stamp
  and a trilingual language column at the foot.
- All stamp dates fall after issue (12 MAR 2024) and before expiry
  (11 MAR 2034); no stamp predates the passport.

## Verification

- Run 1 (MAKEFUN_OUTPUT_DIR=/tmp/out1): entry.png written.
- Run 2 (MAKEFUN_OUTPUT_DIR=/tmp/out2): entry.png written.
- sha256 run 1 = sha256 run 2 =
  `c1c560508ba228be077d5b336e2ea528dcec60d40d2efdc47367a74c0224c174`
  (byte-identical, deterministic).
- Dimensions: 1024 x 1024 (gate: at most 1024 x 1024). OK.
- Size: 29,175 bytes (gate: at most 1,048,576 bytes). OK.
- PNG signature valid; MRZ lines 44 chars each (ICAO TD3).
- Runtime: ~4 s per run (well inside the 60 s sandbox budget).
- Visual check: rendered PNG inspected — spread reads as a coherent
  passport document; all text legible; stamps inside their rings;
  no overlaps (authority/signature and visa-sticker lines fixed after
  first render).

## Files

- main.py — the entry program (root of repo)
- README.md — with make.fun badges for verren044 /
  makefun-the-passport-page-of-a-countr-2-20261121-0318
- LICENSE — MIT
- .makefun/owner.json — {"wallet": "5dzkJVQkKc2V2mMuQDsfv8EJwtw3uLDMARNVHkjmByaX"}

## Status

Built + committed locally. NOT pushed, NO GitHub repo created, NOT
submitted — push/repo/submit are the parent agent's step (needs the
browser session as verren044 and the kit bundle/check/submit flow).

## Revision (parent, 21 Nov 2026 ~12:57 WIB, thinking_revised fix)
- Added `draw_guilloche`: faint interlaced sine-wave security pattern on
  both pages, drawn under all content — the spread now reads as printed
  security paper, not flat cream (judge criterion 2).
- Fixed travel history (judge criterion 3): every departure now follows an
  arrival in the same country — Vardonia DEPARTED 19 SEP 2024 became
  Vardonia ARRIVED 19 SEP 2024, and the final Kestrelia DEPARTED 27 MAY
  2025 became Ostara DEPARTED 27 MAY 2025 (exit from Ostara, entered
  02 FEB 2025). No stamp now contradicts the travel history.
- Re-verified: two runs byte-identical, sha256
  `09ecef7ca9aadc17a7fc34cf06f1d1f5928c49f8f7127694d4b01db4c2a23d5c`
  (changed from builder sha `c1c56050…`), 1024x1024, within 1 MiB.
