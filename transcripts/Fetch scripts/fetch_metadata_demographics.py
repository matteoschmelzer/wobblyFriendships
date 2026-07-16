"""
Fetch trial metadata and participant demographics (including relationship_to_interlocutor)
from the Balance Corpus API. Companion to fetch_textgrid_transcripts.py.

Demographics are per-participant, not per-trial, and constant across all of a pair's trials --
so this fetches every trial (to also build a full trial-level metadata table with taboo words,
session timing, etc.) but de-duplicates to one demographics record per participant, flagging
any inconsistency across repeated observations (there shouldn't be any, but worth checking).

Output (in OUT_DIR):
    trials_metadata.csv   -- one row per trial: ids, condition, target word, taboo words, timing
    participants.csv      -- one row per participant: demographics + relationship_to_interlocutor
"""
import os
import time
import requests
import pandas as pd

BASE_URL = "https://thebalancecorpus.warwick.ac.uk/api/trials/{pair}__trial{trial}"

PAIR_IDS = ["103_203", "108_208", "109_209", "115_215", "116_216",
            "118_218", "123_223", "158_258", "180_280", "188_288"]
TRIAL_NUMBERS = range(12, 55)   # 12-54 inclusive; not every pair has every number

OUT_DIR = "metadata"
REQUEST_DELAY = 0.1
RETRIES = 3
TIMEOUT = 15

# The two relationship_to_interlocutor response options seen in the API so far. Anything else
# (e.g. a future third option, or a null) falls through to "other/unknown" rather than being
# silently miscategorised.
RELATIONSHIP_MAP = {
    "The person who is also in my session is someone I have never interacted with before "
    "(e.g. a stranger).": "stranger",
    "The person I am here with is someone I have interacted with before (e.g. a friend).": "friend",
}


def normalize_relationship(text):
    return RELATIONSHIP_MAP.get((text or "").strip(), "other/unknown")


def fetch_trial(pair_id, trial_number, session):
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


def parse_metadata(data):
    """Returns (trial_row, [participant_row, participant_row]) for one API response."""
    meta = data["metadata"]
    stem = meta["audio_file_name"].rsplit(".", 1)[0]

    trial_row = dict(
        trial_id=stem,
        pair_id=meta["pair_id"],
        trial_number=int(meta["trial_number"]),
        condition=data.get("condition", meta.get("clue_giver_condition")),
        target_word=data["target_word"],
        clue_giver_id=str(meta["clue_giver_id"]),
        participant_1_id=str(meta["participant_1_id"]),
        participant_2_id=str(meta["participant_2_id"]),
        taboo_1=meta.get("taboo_1"), taboo_2=meta.get("taboo_2"), taboo_3=meta.get("taboo_3"),
        taboo_4=meta.get("taboo_4"), taboo_5=meta.get("taboo_5"),
        session_date=meta.get("session_date"),
        trial_end_time=meta.get("trial_end_time"),
    )

    participant_rows = []
    demo = data.get("demographics", {})
    for key in ("p1", "p2"):
        d = demo.get(key)
        if not d:
            continue
        row = dict(d)   # copy every field as-is (height, weight, gender, handedness, etc.)
        row["pair_id"] = meta["pair_id"]
        row["relationship_to_interlocutor_raw"] = row.get("relationship_to_interlocutor")
        row["relationship_to_interlocutor"] = normalize_relationship(row.get("relationship_to_interlocutor"))
        participant_rows.append(row)

    return trial_row, participant_rows


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    session = requests.Session()

    combos = [(p, t) for p in PAIR_IDS for t in TRIAL_NUMBERS]
    trial_rows = []
    participants = {}          # participant_id -> first-seen demographics row
    mismatches = []            # (participant_id, field, first_value, later_value)
    missing, failed = [], []

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
            trial_row, p_rows = parse_metadata(data)
        except (KeyError, TypeError) as e:
            print(f"FAILED to parse ({e})")
            failed.append((pair_id, trial_number, f"parse error: {e}"))
            time.sleep(REQUEST_DELAY)
            continue

        trial_rows.append(trial_row)
        for row in p_rows:
            pid = row["participant_id"]
            if pid not in participants:
                participants[pid] = row
            else:
                for field in ("relationship_to_interlocutor", "gender", "age_in_years_1_text",
                               "height", "weight"):
                    if participants[pid].get(field) != row.get(field):
                        mismatches.append((pid, field, participants[pid].get(field), row.get(field)))
        print("ok")
        time.sleep(REQUEST_DELAY)

    trials_df = pd.DataFrame(trial_rows)
    participants_df = pd.DataFrame(participants.values())

    trials_df.to_csv(os.path.join(OUT_DIR, "trials_metadata.csv"), index=False)
    participants_df.to_csv(os.path.join(OUT_DIR, "participants.csv"), index=False)

    print(f"\n{len(trials_df)} trials, {len(participants_df)} unique participants")
    print(f"{len(missing)} trial number(s) not found (expected)")
    if failed:
        print(f"\n{len(failed)} request(s) failed after retries:")
        for pair_id, trial_number, err in failed:
            print(f"  {pair_id} trial {trial_number}: {err}")
    if mismatches:
        print(f"\nWARNING: {len(mismatches)} inconsistent demographic value(s) across repeated "
              f"observations of the same participant (shouldn't happen -- worth checking):")
        for pid, field, v1, v2 in mismatches:
            print(f"  participant {pid}, field {field}: {v1!r} vs {v2!r}")

    print(f"\nrelationship_to_interlocutor breakdown:")
    print(participants_df.relationship_to_interlocutor.value_counts())


if __name__ == "__main__":
    main()
