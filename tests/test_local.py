import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  # noqa: E402


def run(games, seed, opponent):
    try:
        from kaggle_environments import make
    except ImportError:
        print("Thiếu kaggle-environments. Cài: pip install 'kaggle-environments>=1.28.0'")
        sys.exit(1)

    wins = losses = ties = 0
    for g in range(games):
        env = make("orbit_wars", configuration={"seed": seed + g}, debug=False)
        env.run([main.agent, opponent])
        final = env.steps[-1]
        r0 = final[0].reward or 0
        r1 = final[1].reward or 0
        res = "WIN" if r0 > r1 else "LOSS" if r0 < r1 else "TIE"
        wins += r0 > r1
        losses += r0 < r1
        ties += r0 == r1
        print(f"Game {g+1:>3} (seed {seed+g}): us={r0}  opp={r1}  -> {res}")

    print(f"\nvs {opponent}: {wins}W / {losses}L / {ties}T "
          f"({wins/games*100:.0f}% thắng)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--opponent", default="random")
    args = ap.parse_args()
    run(args.games, args.seed, args.opponent)
