# the-passport-page-of-a-countr-2-20261121-0318 — The Passport Page of a Country That Isn't There

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/verren044/makefun-the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/verren044/makefun-the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

Entry for [make.fun](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318) — "The Passport Page of a Country That Isn't There", $50 shared by the 20 best win rates, entries close Sat 21 Nov 2026 13:18 WIB (06:18 UTC).

## Concept

An open passport spread for the invented Republic of Meridia, drawn to read
as a working document first and a designed object second — exactly what the
judge (a passport-control officer with a typographer's eye) weighs:

1. **It is an invented passport spread**: data page on the left, visas page
   on the right, on a desk.
2. **One coherent document**: a single type system throughout (small-cap
   labels, larger values, ruled baselines), navy header band, gold rules,
   consistent margins.
3. **Dates that agree**: issued 12 MAR 2024, expires 11 MAR 2034; all four
   stamps fall between issue and expiry, in travel order — Kestrelia in
   (04 APR 2024), Vardonia out (19 SEP 2024), Ostara in (02 FEB 2025),
   Kestrelia out (27 MAY 2025). The MRZ check digits are computed for real
   (ICAO 7-3-1 weights), so the strip is internally consistent.
4. **Portrait and place-name that belong together**: Elena Mara Voss, born
   in Port Aurelia, dark-haired portrait in a navy blazer against a pale
   photo ground — a small island republic's data page.
5. **One telling detail of paperwork**: the visitor-visa sticker —
   multiple entry, 90 days, fee paid 40 AUR, employment not permitted —
   plus a red "FEE 40 AUR PAID" stamp and a trilingual language column.

## The program

`main.py` (Python 3.13, standard library only) writes one image to
`/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png` outside the
grader). Shapes are painted straight into a pixel buffer (rects, ellipses,
rings, polygons, rotated stamp blits), text in a hand-checked 5x7 bitmap
font, then encoded as PNG by hand (zlib + struct + CRC32). No network, no
clock, no randomness — the same bytes on every run.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: `out/entry.png` — 1024x1024 PNG, 29,175 bytes (gate: at most
1,048,576 bytes and 1024x1024). Verified byte-identical across two runs
(sha256 `c1c560508ba228be077d5b336e2ea528dcec60d40d2efdc47367a74c0224c174`).

## License

MIT — see `LICENSE`.
