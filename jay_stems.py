#!/usr/bin/env python3
import rtmidi, time, sys

DJM_KEYWORD = "DJM-900NXS2"
IAC_KEYWORD = "JAY_STEMS"
LOW_MAX  = 30
HIGH_MIN = 97

CC_MAP = {
    4:  (36, 37,  "Deck 1 - Drums"),
    3:  (38, 39,  "Deck 1 - Bass"),
    2:  (40, 41,  "Deck 1 - Melody"),
    1:  (42, 43,  "Deck 1 - Vocal"),
    82: (44, 45,  "Deck 2 - Drums"),
    92: (46, 47,  "Deck 2 - Bass"),
    81: (48, 49,  "Deck 2 - Melody"),
    80: (50, 51,  "Deck 2 - Vocal"),
}

state = {cc: "mid" for cc in CC_MAP}

def get_zone(val):
    if val <= LOW_MAX:  return "low"
    if val >= HIGH_MIN: return "high"
    return "mid"

def get_note(prev, new, note_off, note_fx):
    if prev == new:    return None
    if new  == "low":  return note_off
    if new  == "high": return note_fx
    if prev == "low":  return note_off
    if prev == "high": return note_fx
    return None

midi_in  = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()
in_ports  = midi_in.get_ports()
out_ports = midi_out.get_ports()
in_idx  = next((i for i,n in enumerate(in_ports)  if DJM_KEYWORD in n), None)
out_idx = next((i for i,n in enumerate(out_ports) if IAC_KEYWORD in n), None)

if in_idx is None:
    print(f"ERROR: DJM not found. Available ports:\n{in_ports}")
    sys.exit(1)
if out_idx is None:
    print(f"ERROR: IAC JAY_STEMS not found. Available ports:\n{out_ports}")
    sys.exit(1)

midi_in.open_port(in_idx)
midi_out.open_port(out_idx)
midi_in.ignore_types(sysex=True, timing=True, active_sense=True)

print("=" * 45)
print("  JAY STEMS MAPPER — running")
print(f"  IN  : {in_ports[in_idx]}")
print(f"  OUT : {out_ports[out_idx]}")
print("=" * 45)

while True:
    msg = midi_in.get_message()
    if msg:
        data, _ = msg
        if len(data) == 3 and (data[0] & 0xF0) == 0xB0:
            cc  = data[1]
            val = data[2]
            if cc in CC_MAP:
                note_off, note_fx, label = CC_MAP[cc]
                new_z  = get_zone(val)
                prev_z = state[cc]
                note   = get_note(prev_z, new_z, note_off, note_fx)
                state[cc] = new_z
                if note is not None:
                    if note == note_off:
                        print(f"[STEM OFF]    {label} -> muted   (val {val})")
                    else:
                        print(f"[STEM FX]     {label} -> FX ON   (val {val})")
                    midi_out.send_message([0x90, note, 127])
                    time.sleep(0.03)
                    midi_out.send_message([0x80, note, 0])
            else:
                midi_out.send_message(list(data))
                if cc == 70 and val == 127:
                    print(f"[INSTANT DBL] Deck left  -> triggered")
                elif cc == 73 and val == 127:
                    print(f"[INSTANT DBL] Deck right -> triggered")
        else:
            midi_out.send_message(list(data))
    time.sleep(0.001)
