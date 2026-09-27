"""Replay the actual roki-ng gait without importing Roki or sending commands."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--roki-ng", type=Path, required=True)
parser.add_argument("--module-dir", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.roki_ng.resolve()))
sys.path.insert(0, str(args.module_dir.resolve()))
import starkit
from roki_ng.motion.engine import Engine
from roki_ng.parameters import Parameters

scenarios = [("spot", 0, 0, 0), ("short", 12, 0, 0),
             ("long", 24, 0, 0), ("backward", -24, 0, 0),
             ("side", 0, 12, 0), ("turn_left", 0, 0, .15),
             ("turn_right", 0, 0, -.15), ("combined", 24, 12, .15),
             ("stride64", 64, 0, 0)]
args.output.mkdir(parents=True, exist_ok=True)
report = {"module": starkit.__file__, "scenarios": []}
with tempfile.TemporaryDirectory() as state, (args.output / "trace.jsonl").open("w") as trace:
    defaults = Parameters(state).values
    for height in (32, 40):
        for name, step, side, rotation in scenarios:
            for right in (True, False):
                summary = dict(name=name, step_height=height, right_first=right,
                               ik_calls=0, missing=0, servo_frames=0, invalid_commands=0)
                engine = Engine(defaults, log=lambda *a: None)
                engine.stepHeight = height
                engine.first_Leg_Is_Right_Leg = right
                stage = "initial"

                def solve(leg, *inputs):
                    summary["ik_calls"] += 1
                    solutions = starkit.alpha_calculation(*inputs)
                    summary["missing"] += not bool(solutions)
                    trace.write(json.dumps(dict(scenario=name, height=height, right_first=right,
                                                stage=stage, leg=leg, inputs=inputs,
                                                solutions=solutions)) + "\n")
                    return solutions

                engine.solve_leg = solve

                def consume(generator):
                    for command in generator:
                        if command[0] == "servo":
                            _, values, frames, pause = command
                            summary["servo_frames"] += 1
                            summary["invalid_commands"] += sum(not 0 <= s.Data <= 16383 for s in values)
                            trace.write(json.dumps(dict(scenario=name, height=height, right_first=right,
                                                        stage=stage, frames=frames, pause=pause,
                                                        servos=[[s.Id, s.Sio, s.Data] for s in values])) + "\n")

                try:
                    consume(engine.walk_Initial_Pose(start_mixing=False))
                    for cycle in range(10):
                        stage = f"cycle_{cycle}"
                        consume(engine.walk_Cycle(step, side, rotation, cycle, 10))
                    stage = "terminal"
                    consume(engine.walk_Cycle(0, 0, 0, 0, 1))
                    stage = "final"
                    consume(engine.walk_Final_Pose())
                except Exception as exc:
                    summary["error"] = f"{type(exc).__name__}: {exc}"
                summary["skipped_frames"] = engine.exitFlag
                report["scenarios"].append(summary)
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
