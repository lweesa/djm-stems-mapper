# DJM-900NXS2 Stems Knob Mapper for Serato DJ Suite

> Map your EQ knobs (LOW / MID / HIGH / TRIM) to Serato Stems pads - with threshold zones, FX triggers, and full MIDI proxy support. Built for DJs who want real hardware control over Stems without buying dedicated Rane gear.

---

## Who I Am

My name's Jason. I'm a DJ, Turntablist, Beatmaker, and Sound Engineer with 15+ years of experience, rooted in hip-hop, funk, house, electronic music and club culture. I work primarily with vinyl and high-end club setups, and I take my workflow seriously.

This repo is both a **personal backup** and a **public share** - if you run a similar setup and want to push your Stems game further, this is the most efficient club DJ workflow I've found. No paid middleware, no compromises.

---

## Why This Exists

Serato DJ Pro's **Stems** feature is powerful - isolate drums, bass, melody, and vocals in real time. But native Stems control (EQ-style knob per stem, continuous gain, FX per stem) is locked behind Rane hardware via HID protocol.

### The CDJ-3000 Option - And Why I Don't Use It

If you're running CDJ-3000s alongside your DJM, Serato offers a built-in option: **"Replace Accessory Hardware Pad Mode with Stems"**. This remaps the CDJ-3000 hot cue pads to Stems controls directly. Even better - you can assign a MIDI Learn to toggle this option on and off on the fly.

It works. But it's not the workflow I want. Reassigning my hot cue pads to Stems means losing instant access to cue points mid-set, which is a non-starter for the way I DJ. I need both, independently, at the same time.

### The Real Problem

If you want to keep your CDJ pads free and still control Stems from hardware, your only option is the EQ knobs on the DJM - but Serato doesn't expose Stems parameters as MIDI-mappable destinations natively. Those knobs just send raw CC values that Serato ignores for Stems purposes.

This project fixes that.

---

## What It Does

A lightweight Python script sits between your DJM and Serato DJ Suite, acting as a full MIDI proxy. It intercepts the 8 EQ knobs (LOW / MID / HIGH / TRIM on Ch1 and Ch4), translates them into discrete Stems pad triggers based on threshold zones, and forwards everything else - cues, faders, transport, loops - to Serato untouched.

Each EQ knob is split into 3 zones:

```
[0 ──── 30]  →  LOW zone   →  fires STEM OFF pad  (cuts that stem)
[31 ─── 96]  →  MID zone   →  neutral (no action, returns to previous state)
[97 ─── 127] →  HIGH zone  →  fires STEM FX pad   (activates FX on that stem)
```

The script only fires **once per zone crossing** - no flickering, no MIDI floods.

### Stem Assignments

| Knob | Stem | LOW zone action | HIGH zone action |
|---|---|---|---|
| EQ LOW | Drums | Drums OFF | FX Drums Echo |
| EQ MID | Bass | Bass OFF | FX Instrumental Braker |
| EQ HIGH | Melody | Melody OFF | FX Instrumental Echo |
| TRIM / GAIN | Vocal | Vocal OFF | Vocal Echo |

Applies identically to **Deck 1 (Ch1)** and **Deck 2 (Ch4)**.

### Bonus Mapping

| Button | Action in Serato |
|---|---|
| CUE headphone Ch1 | Instant Double → Deck Left |
| CUE headphone Ch4 | Instant Double → Deck Right |

---

## How It Works

```
DJM-900NXS2
     │
     ▼
Python Script (jay_stems.py)
     │
     ├── EQ knob CC detected?
     │     ├── Zone LOW  → fires Note OFF stem  → IAC Bus
     │     ├── Zone HIGH → fires Note FX stem   → IAC Bus
     │     └── Zone MID  → no output
     │
     └── Any other CC/Note → forwarded as-is → IAC Bus
                                                    │
                                                    ▼
                                            Serato
```

**Serato never sees the DJM directly.** The Python script acts as a full MIDI proxy. All DJM messages pass through - cues, loops, transport, faders - everything works exactly as before. Only the 8 knobs get intercepted and translated into discrete Stems pad triggers.

---

## My Setup

- 2× Pioneer CDJ-3000
- 1× Pioneer DJM-900NXS2
- Serato DJ Suite (latest)
- macOS Apple Silicon M1

---

## CC Reference - DJM-900NXS2

Captured via MIDI Monitor:

| Knob | Channel 1 (Deck 1) | Channel 4 (Deck 2) |
|---|---|---|
| EQ LOW | CC 4 | CC 82 |
| EQ MID | CC 3 | CC 92 |
| EQ HIGH | CC 2 | CC 81 |
| TRIM / GAIN | CC 1 | CC 80 |
| CUE headphone | CC 70 | CC 73 |

All on MIDI Channel 1. Center position = 64. Min = 0. Max = 127.

---

## Note Map - IAC Bus → Serato

| Note | Deck | Stem | Action |
|---|---|---|---|
| 36 | 1 | Drums | OFF |
| 37 | 1 | Drums | FX Echo |
| 38 | 1 | Bass | OFF |
| 39 | 1 | Bass | FX Braker |
| 40 | 1 | Melody | OFF |
| 41 | 1 | Melody | FX Echo |
| 42 | 1 | Vocal | OFF |
| 43 | 1 | Vocal | Echo |
| 44 | 2 | Drums | OFF |
| 45 | 2 | Drums | FX Echo |
| 46 | 2 | Bass | OFF |
| 47 | 2 | Bass | FX Braker |
| 48 | 2 | Melody | OFF |
| 49 | 2 | Melody | FX Echo |
| 50 | 2 | Vocal | OFF |
| 51 | 2 | Vocal | Echo |

---

## Requirements

- macOS (tested on macOS Sequoia / Tahoe, Apple Silicon M1)
- Python 3.x (pre-installed on macOS)
- [python-rtmidi](https://pypi.org/project/python-rtmidi/)
- Pioneer DJM-900NXS2
- Serato DJ Suite

---

## Installation

### 1. Install python-rtmidi

Open Terminal and run:

```bash
sudo pip3 install python-rtmidi
```

Enter your macOS password when prompted.

### 2. Set up the IAC Driver

The IAC Driver is a virtual MIDI bus built into macOS - it lets the script communicate with Serato without any third-party software.

1. Open **Audio MIDI Studio** (Spotlight: `Cmd + Space` → type "Audio MIDI Studio")
2. Go to **Window → Show MIDI Studio**
3. Double-click **IAC Driver**
4. Check **"Device is online"**
5. Click **+** to add a bus if none exists → name it `JAY_STEMS`
6. Close

### 3. Place the script

```bash
mkdir -p ~/Scripts
# copy jay_stems.py into ~/Scripts/
```

### 4. Create the launcher

This creates a double-clickable file on your Desktop - no Terminal typing needed to start the mapper:

```bash
cat > ~/Desktop/JAY_STEMS.command << 'EOF'
#!/bin/bash
python3 ~/Scripts/jay_stems.py
EOF
chmod +x ~/Desktop/JAY_STEMS.command
```

---

## Serato DJ Suite Setup

1. Launch `JAY_STEMS.command` first (keep the Terminal window open)
2. Open Serato DJ Suite
3. Go to **Setup → MIDI**
4. **Disable DJM-900NXS2 as a MIDI source** - it keeps working for HID (jogs, CDJ pads, etc.)
5. **Enable `IAC Driver JAY_STEMS`** as your MIDI input source

### MIDI Learn

For each Stems pad in Serato:

1. Click the MIDI button in the Serato **toolbar** next to the FX button (top left).
2. Click the Stems pad you want to map (in the Performance Pad area, Stems mode). It highlights.
3. Move the corresponding knob into the target zone (LOW, MID, HIGH, or TRIM). Serato captures the incoming Note from the IAC Bus and assigns it.
4. Once all pads are mapped, click the MIDI button again to exit assign mode and lock your mappings.

Repeat for all 16 actions across both decks using the Note Map table above.

---

## Usage

1. **Double-click `JAY_STEMS.command`** on your Desktop
2. Verify Terminal shows:

```
=============================================
  JAY STEMS MAPPER - running
  IN  : DJM-900NXS2
  OUT : IAC Driver JAY_STEMS
=============================================
```

3. Open Serato DJ Suite
4. Load tracks, enable Stems mode
5. Turn EQ knobs to the floor → stem cuts. Crank to the top → FX fires.

### Live Monitoring

```
[STEM OFF]    Deck 1 - Drums -> muted   (val 12)
[STEM FX]     Deck 1 - Drums -> FX ON   (val 120)
[STEM OFF]    Deck 2 - Vocal -> muted   (val 0)
[INSTANT DBL] Deck left  -> triggered
[INSTANT DBL] Deck right -> triggered
```

Keep the Terminal window open and minimized during your session. Closing it stops the script.

---

## Files

```
djm-stems-mapper/
├── README.md
└── jay_stems.py
```

---

## Notes & Limitations

- The script must be running **before** you open Serato
- Closing the Terminal window stops the script
- The continuous Stems EQ knob behavior (like on Rane One MK2 / Rane System One) is **not replicable** on DJM - that feature uses a proprietary HID protocol exclusive to Rane hardware. This script is the closest alternative: threshold-based pad triggers from analog knobs
- Tested on DJM-900NXS2 only. Other mixers may send different CC numbers - use [MIDI Monitor](https://www.snoize.com/midimonitor/) to identify yours before editing the script

---

## Tools Used

| Tool | Purpose |
|---|---|
| [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi) | MIDI I/O in Python |
| macOS IAC Driver | Virtual MIDI bus, built into macOS |
| [MIDI Monitor](https://www.snoize.com/midimonitor/) | Identify CC numbers from hardware |

---

## License

MIT - use it, modify it, share it.
