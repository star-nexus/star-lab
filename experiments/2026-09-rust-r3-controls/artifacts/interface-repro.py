"""Run with the matched interpreter from a production checkout root."""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
from star_native import API_VERSION, _native
from rotk_env.runtime.bootstrap import export_initial_state
from rotk_env.runtime.native import RustRuntime
from rotk_env.tests.test_native_unit_actions import setup

with contextlib.redirect_stdout(io.StringIO()):
    world, (a, b, c), _, _ = setup()
    try:
        with RustRuntime(export_initial_state(world)) as runtime:
            before = runtime.export_state()
            try:
                result = runtime.execute_control('move', unit_id=b, position=(-1, 1))
                error = None
            except AttributeError as exc:
                result = None; error = str(exc)
            after = runtime.export_state()
    finally:
        world.reset()
print(json.dumps(dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    api=API_VERSION, extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
    result=result, error=error, state_changed=before != after),indent=2))
