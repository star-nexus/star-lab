"""Validate prepared E7 default dispatch in a temporary module, without activation."""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--patch', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    source = a.source.resolve()
    patch = a.patch.resolve()
    relative = 'rotk_env/systems/window_map_render_system.py'
    original = (source / relative).read_bytes()
    checks = []
    os.environ.update(HEADLESS='1', SDL_VIDEODRIVER='dummy', PYGAME_HIDE_SUPPORT_PROMPT='1')
    sys.path.insert(0, str(source))
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / relative
        path.parent.mkdir(parents=True)
        path.write_bytes(original)
        subprocess.run(['git', 'apply', str(patch)], cwd=folder, check=True)
        name = 'rotk_env.systems._e7_default_validation'
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        from rotk_env.systems.map_render_system import MapRenderSystem
        parent = module.FastMapRenderSystem
        original_update = parent.update
        renderer = module.WindowMapRenderSystem()
        results = []

        def observe(self, dt):
            results.append((self._e7_frame_active,
                            self._render_territory_boundaries_optimized.__func__, dt))
            return 'completed'

        try:
            parent.update = observe
            assert renderer.update(.1) == 'completed'
            assert results.pop() == (True, renderer._render_territory_boundaries_empty.__func__, .1)
            assert not renderer._e7_frame_active
            assert '_e7_territory_original' not in renderer.__dict__
            assert '_render_territory_boundaries_optimized' not in renderer.__dict__
            checks.append('Ordinary update selects existing candidate and restores inherited binding')
            with renderer._display_research_frame('baseline'):
                renderer.update(.2)
                assert results.pop() == (True, MapRenderSystem._render_territory_boundaries_optimized, .2)
            checks.append('Explicit baseline overrides default; retains original method')
            with renderer._display_research_frame('empty_territory'):
                renderer.update(.3)
                assert results.pop() == (True, renderer._render_territory_boundaries_empty.__func__, .3)
            checks.append('Explicit candidate does not nest or double-select frame scope')

            class Failure(Exception):
                pass

            error = Failure('successful prefix already submitted')

            def fail(self, dt):
                assert self._e7_frame_active
                raise error

            custom = lambda *args: None
            renderer._render_territory_boundaries_optimized = custom
            parent.update = fail
            try:
                renderer.update(.4)
            except Failure as caught:
                assert caught is error
            else:
                raise AssertionError('Error swallowed')
            assert renderer._render_territory_boundaries_optimized is custom
            assert not renderer._e7_frame_active
            assert '_e7_territory_original' not in renderer.__dict__
            checks.append('Exception identity retained; scope and custom instance binding restored')
        finally:
            parent.update = original_update
            sys.modules.pop(name, None)
        candidate_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    assert (source / relative).read_bytes() == original
    result = dict(classification='Isolated default-dispatch contract; not performance or full pixel evidence',
                  applied_to_product=False, passed=True, checks=checks,
                  source_file_sha256=hashlib.sha256(original).hexdigest(),
                  candidate_file_sha256=candidate_hash, patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest(),
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
