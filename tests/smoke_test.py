"""
Smoke test: import agent và chạy 1 turn với observation giả.
Cần torch. Dùng: python tests/smoke_test.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  

assert callable(main.agent), "main.agent phải callable"

# Observation tối thiểu: 1 home của mình + 1 trung lập + 1 địch
obs = {
    "player": 0,
    "angular_velocity": 0.04,
    "comet_planet_ids": [],
    "planets": [
        # [id, owner, x, y, radius, ships, production]
        [0, 0,  20.0, 20.0, 1.0, 10, 3],
        [1, -1, 35.0, 25.0, 2.0, 12, 4],
        [2, 1,  80.0, 80.0, 1.0, 10, 3],
    ],
    "fleets": [],
}

action = main.agent(obs)
print("agent(obs) ->", action)
assert isinstance(action, list), "action phải là list các move"
for mv in action:
    assert len(mv) == 3, "mỗi move = [from_planet_id, angle, num_ships]"
print("SMOKE TEST PASSED")
