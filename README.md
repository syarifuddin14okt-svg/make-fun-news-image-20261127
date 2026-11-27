# The World Today — Friday, 27 November 2026

A one-page newspaper front page summing up the world news of Friday,
27 November 2026, drawn by a pure-stdlib Python program (no network, no
third-party code) as a 1024x1024 PNG.

## What the image shows

- **Lead story — Kuwait drone strike fallout:** two Italian Rheinmetall
  technicians were killed when a drone struck a Kuwait air-defence
  station. Italy and Kuwait blame Iran; Tehran denies any role and
  accuses Zelenskyy of staging a "false flag".
- **Houthis escalate:** strikes on Saudi Arabia escalate; Saudi defences
  intercept ballistic missiles aimed at Riyadh; Houthi drones target
  Red Sea ports.
- **EU budget deadlock:** EU leaders struggle to agree a long-term
  budget and a $49bn loan for Ukraine.
- **Britain calls up reservists:** the first call-up since the Cold War
  as the Russia threat grows.
- **Thanksgiving storms:** severe US storms snarl Thanksgiving travel —
  800,000+ homes without power, 1,000+ flights hit, the 100th Macy's
  parade postponed.
- **Zelenskyy to BBC:** the US is "too focused on the Middle East";
  he questions the "strange" Trump-Putin friendship.
- **In brief:** Myanmar and the ICJ genocide ruling, the Bangkok
  refinery explosion, Gukesh vs Sindarov at the World Chess
  Championship, Gérard Depardieu's trial, a tanker capsizing off
  Ibiza, and Kim's nuclear expansion plans.

## How to run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, under 1 MiB). Two runs write
byte-identical files: the layout, colours and text are fixed, with no
clock, no randomness and no network.

## Licence

MIT — see `LICENSE`.
