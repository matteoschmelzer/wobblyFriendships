"""
Fetch human-annotated transcripts from the Balance Corpus API and turn them into
role-labeled, timestamped CSVs -- the same shape as Notebook 1's ASR-based transcripts,
but ground-truth, so no ASR noise, no missing guesser segments, and trial duration comes
for free (parsed.xmax) instead of needing to read .wav headers.

Output: one CSV per trial in OUT_DIR, plus a combined transcripts_all.csv and a
trial_durations.csv (duration-based success can be computed straight from the latter).

Usage:
    python fetch_textgrid_transcripts.py
"""
import os
import time
import requests
import pandas as pd

BASE_URL = "https://thebalancecorpus.warwick.ac.uk/api/trials/{pair}__trial{trial}"

PAIR_IDS = ["103_203", "108_208", "109_209", "115_215", "116_216",
            "118_218", "123_223", "158_258", "180_280", "188_288"]
TRIAL_NUMBERS = range(12, 55)   # 12-54 inclusive; not every pair will have every number

OUT_DIR = "textgrid_transcripts"
REQUEST_DELAY = 0.1             # seconds between requests, be polite to the API
RETRIES = 3
TIMEOUT = 15

# Interval texts that aren't actual speech -- dropped rather than kept as empty rows
SKIP_TEXT = {"", "<pause>", "<PAUSE>", "<silence>"}


def fetch_trial(pair_id, trial_number, session):
    """GET one trial from the API. Returns the parsed JSON, or None if the trial
    genuinely doesn't exist (404 -- expected, since trial numbers aren't contiguous
    for every pair). Raises after exhausting retries on other failures."""
    url = BASE_URL.format(pair=pair_id, trial=trial_number)
    last_err = None
    for attempt in range(RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT)
        except requests.RequestException as e:
            last_err = e
            time.sleep(2.0 * (attempt + 1))
            continue
        if r.status_code == 404:
            return None
        if r.status_code == 200:
            return r.json()
        last_err = requests.HTTPError(f"HTTP {r.status_code} for {url}")
        time.sleep(2.0 * (attempt + 1))
    raise last_err


def parse_trial(data):
    """Turn one trial's API response into a list of role-labeled segment rows,
    plus the trial's total duration. Only the 'clue-giver' and 'guesser' tiers are
    kept -- 'noise'/overlap tiers are ignored. If a trial has more than one textgrid
    entry (e.g. separate per-participant files), all are merged; duration is the max
    xmax seen across them."""
    meta = data["metadata"]
    stem = meta["audio_file_name"].rsplit(".", 1)[0]

    clue_giver_id = str(meta["clue_giver_id"])
    p1, p2 = str(meta["participant_1_id"]), str(meta["participant_2_id"])
    guesser_id = p2 if clue_giver_id == p1 else p1
    role_to_pid = {"clue-giver": clue_giver_id, "guesser": guesser_id}

    rows = []
    trial_duration = 0.0
    for tg in data.get("textgrids", []):
        parsed = tg.get("parsed", {})
        trial_duration = max(trial_duration, parsed.get("xmax", 0.0))
        for tier in parsed.get("tiers", []):
            role = tier.get("name")
            if role not in role_to_pid:
                continue
            for k, iv in enumerate(tier.get("intervals", [])):
                text = (iv.get("text") or "").strip()
                if text in SKIP_TEXT:
                    continue
                rows.append(dict(
                    trial_id=stem,
                    pair_id=meta["pair_id"],
                    trial_number=int(meta["trial_number"]),
                    condition=meta.get("clue_giver_condition", data.get("condition")),
                    target_word=data["target_word"],
                    participant_id=role_to_pid[role],
                    role="clue_giver" if role == "clue-giver" else "guesser",
                    seg=k,
                    start=round(iv["xmin"], 3),
                    end=round(iv["xmax"], 3),
                    text=text,
                    source="textgrid",
                ))
    return stem, rows, trial_duration


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    session = requests.Session()

    combos = [(p, t) for p in PAIR_IDS for t in TRIAL_NUMBERS]
    all_rows, durations, missing, failed = [], [], [], []

    for i, (pair_id, trial_number) in enumerate(combos, 1):
        print(f"[{i}/{len(combos)}] {pair_id} trial {trial_number} ...", end=" ", flush=True)
        try:
            data = fetch_trial(pair_id, trial_number, session)
        except Exception as e:
            print(f"FAILED after retries ({e})")
            failed.append((pair_id, trial_number, str(e)))
            continue

        if data is None:
            print("not found")
            missing.append((pair_id, trial_number))
            time.sleep(REQUEST_DELAY)
            continue

        try:
            stem, rows, duration = parse_trial(data)
        except (KeyError, TypeError) as e:
            print(f"FAILED to parse ({e})")
            failed.append((pair_id, trial_number, f"parse error: {e}"))
            time.sleep(REQUEST_DELAY)
            continue

        durations.append(dict(trial_id=stem, pair_id=pair_id, trial_number=trial_number,
                               duration=duration))

        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(os.path.join(OUT_DIR, stem + ".csv"), index=False)
            all_rows.append(df)
            print(f"{len(df)} segments, {duration:.1f}s")
        else:
            print(f"0 usable segments, {duration:.1f}s")

        time.sleep(REQUEST_DELAY)

    combined = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    combined.to_csv(os.path.join(OUT_DIR, "transcripts_all.csv"), index=False)
    pd.DataFrame(durations).to_csv(os.path.join(OUT_DIR, "trial_durations.csv"), index=False)

    print(f"\n{len(combined)} segments across {combined.trial_id.nunique() if len(combined) else 0} trials")
    print(f"{len(missing)} trial number(s) not found (expected -- pairs don't all have "
          f"the same trial numbers)")
    if failed:
        print(f"\n{len(failed)} request(s) failed after retries -- worth re-running just these:")
        for pair_id, trial_number, err in failed:
            print(f"  {pair_id} trial {trial_number}: {err}")


if __name__ == "__main__":
    main()
