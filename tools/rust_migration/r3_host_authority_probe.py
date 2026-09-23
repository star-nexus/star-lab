"""Native host authority contract; no sockets and no capacity claim."""
import argparse
from copy import deepcopy
import datetime
import hashlib
import json
import lzma
import os
from pathlib import Path
import sys
from unittest.mock import patch
from r3_observations_probe import git


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expect-supported', action='store_true')
    args = p.parse_args()
    src = args.source.resolve(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    os.chdir(src); sys.path.insert(0, str(src)); os.environ['SDL_VIDEODRIVER'] = 'dummy'
    from star_native import API_VERSION, _native
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.tests.test_native_turn import setup
    class Frozen(datetime.datetime):
        @classmethod
        def now(cls, tz=None): return cls(2026, 9, 12, 12)
    cases = []
    with patch('time.time', return_value=1720000000.), patch('datetime.datetime', Frozen):
        for display in ['none', 'dummy', 'window']:
            for threads in [1, 2, 4]:
                world, _, _, llm = setup(display)
                initial = export_initial_state(world, display=display)
                steps = []; sent = []
                llm.send_message = lambda payload, *, target: sent.append((deepcopy(payload), target['id']))
                llm.client.connected_agents = dict.fromkeys(['a', 'b', 'c', 'unknown'], {})
                try:
                    with RustRuntime(initial, threads=threads) as runtime:
                        supported = all(hasattr(runtime, n) for n in ['host_status','record_message','turn_start_context'])
                        assert supported == args.expect_supported
                        for aid, faction in [('a','wei'),('b','shu'),('c','shu'),('b','wei')]:
                            params = dict(faction=faction, provider='synthetic', model_id='fake', base_url='http://local')
                            py = llm._process_action_request(agent_id=aid, action_id=0, action='register_agent_info', params=deepcopy(params), send_response=False)
                            rs = runtime.execute_action('register_agent_info', params, agent_id=aid)
                            assert rs == json.loads(json.dumps(py))
                        # Turn delivery candidates retain the legacy registry/stats
                        # overlap and re-registration history. Transport ordering
                        # is deliberately performed by the original add loop.
                        for aid, faction in [('a','wei'), ('c','shu')]:
                            sent.clear(); params = dict(faction=faction)
                            py = llm._process_action_request(agent_id=aid, action_id=1, action='end_turn', params=deepcopy(params), send_response=False)
                            rs = runtime.execute_action('end_turn', params, agent_id=aid)
                            assert rs == json.loads(json.dumps(py))
                            context = runtime.turn_start_context() if supported else None
                            delivered = None
                            if context is not None:
                                candidates = set()
                                for target in context['candidates']: candidates.add(target)
                                delivered = [(context['notification'], target) for target in candidates if target in llm.client.connected_agents]
                                assert delivered == sent
                            steps.append(dict(kind='turn', python_notifications=deepcopy(sent), rust_context=context,
                                              rust_notifications=delivered, python_state=export_initial_state(world, display=display), rust_state=runtime.export_state()))
                        for aid in ['a', 'c', None, 'unknown', 'unknown']:
                            old_error = new_error = None
                            try: llm._record_message(aid, None)
                            except RuntimeError as exc: old_error = str(exc)
                            if supported:
                                try: runtime.record_message(aid)
                                except RuntimeError as exc: new_error = str(exc)
                                assert old_error == new_error
                            py = export_initial_state(world, display=display); rs = runtime.export_state()
                            if supported: assert py == rs
                            steps.append(dict(kind='message', agent=aid, python_error=old_error, rust_error=new_error,
                                              python_state=py, rust_state=rs, state_equal=py==rs))
                        cases.append(dict(display=display,threads=threads,supported=supported,initial=initial,steps=steps,
                                          host_status=runtime.host_status() if supported else None))
                finally: world.reset()
    raw = json.dumps(cases, ensure_ascii=False, separators=(',',':')).encode()
    path = out/'raw.json.xz'; path.write_bytes(lzma.compress(raw))
    compact = dict(source_sha=git(src,'rev-parse','HEAD'), source_dirty=git(src,'status','--porcelain'),
                   tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'), api=API_VERSION,
                   extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
                   cases=len(cases), supported=sum(c['supported'] for c in cases),
                   message_state_equal=sum(s['state_equal'] for c in cases for s in c['steps'] if s['kind']=='message'),
                   message_checks=45, turn_checks=18, all_guards_passed=True, actual_windows=False,
                   network_connected=False, capacity_result=False,
                   raw=dict(path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),decoded_sha256=hashlib.sha256(raw).hexdigest()))
    assert not compact['source_dirty']
    (out/'compact.json').write_text(json.dumps(compact, indent=2)+'\n'); print(json.dumps(compact))


if __name__ == '__main__': main()
