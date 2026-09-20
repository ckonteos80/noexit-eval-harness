"""
Interactive driver for one full harness session:
new session -> generate both characters -> narrator opening -> a
type-your-own-lines player loop -> write the run to the experiment store.

Usage:
    python run_session.py [--phase LABEL] [--root PATH]

    --phase   value stored in the run's meta.phase (default: "manual")
    --root    experiment store root (default: . -- project folder, so runs/
              and index.sqlite land next to run_viewer.html)

During the loop:
    type a message and press Enter to play a turn
    /quit       end the session and write it to the store
    /abandon    end the session WITHOUT writing it to the store
"""

import argparse
import json
from datetime import datetime, timezone

import simulator
import store
from save_version import current_version


def print_reply(reply: dict):
    for r in reply["replies"]:
        print(f"  Char {r['char_no']}: {r['text']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="manual", help="tag stored in run meta.phase")
    parser.add_argument("--root", default=".", help="experiment store root")
    args = parser.parse_args()

    state = simulator.new_session()
    print(f"Session {state.session_id} started.\n")

    c1 = simulator.generate_character(state, 1)
    c2 = simulator.generate_character(state, 2)
    print(f"Character 1: {c1.get('name', '?')} — {c1.get('occupation', '?')}")
    print(f"Character 2: {c2.get('name', '?')} — {c2.get('occupation', '?')}\n")

    narrator_line = simulator.run_narrator(state)
    print(f"Narrator: {narrator_line}\n")

    print("Type a message and press Enter to play a turn.")
    print("/quit to end and save, /abandon to end without saving.\n")

    abandoned = False
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not message:
            continue
        if message == "/quit":
            break
        if message == "/abandon":
            abandoned = True
            break

        result = simulator.run_player_turn(state, message)
        print_reply(result)

    if abandoned:
        print("\nSession abandoned — nothing written to the store.")
        return

    all_records = json.load(open(simulator.TRANSCRIPT_JSON, encoding="utf-8"))
    records = [r for r in all_records if r.get("session_id") == state.session_id]
    snapshot = json.load(open(simulator.STATE_JSON, encoding="utf-8"))

    current = current_version()
    game_state_version = current.name if current else None

    st = store.ExperimentStore(root=args.root)
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_") + state.session_id
    run_path = st.write_run(run_id, records, snapshot, meta={
        "phase": args.phase,
        "game_state_version": game_state_version,
    })

    print(f"\nSaved run '{run_id}' ({len(records)} calls) to {run_path}")
    print(f"Open run_viewer.html and drag in that file to inspect it.")


if __name__ == "__main__":
    main()
