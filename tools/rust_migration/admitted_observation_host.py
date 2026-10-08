"""E8 full Lab host: original live pump and complete production window update.

Reuse the audited E8 lifetime hooks, substituting an owned-wire boundary without
the correctness recorder's full exports, JSON hashing or operation retention.
No production defaults or frozen measurement tools are changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from admitted_observation_agents import AdmittedAgents, AdmittedLoopTrace, LAB
import p3_runtime
import rust_migration.native_loop_trace as recorder_module

EXTENSION_SHA = '9bb2fa4412bc810fbd751c42f525614f8cddb42e8c136612a51495fa0679f0d9'


class LiveWire(AdmittedLoopTrace):
    """Same per-request call/owned wire/payload callback, no measurement hash."""
    def __init__(self, runtime, output, source, extension, threads):
        assert extension['sha256'] == EXTENSION_SHA and threads == 1
        self.runtime = runtime
        self.query_scope = None
        self.pending = False
        self.queries = self.payloads = self.calls = 0

    def call(self, session, verb, params):
        assert not self.pending
        self.calls += 1
        return self.runtime.execute_action(verb, params, agent_id=session.agent_id)

    def observation_json(self, session, params):
        assert not self.pending
        call = self.query_scope.get_faction_state_json if self.query_scope else self.runtime.get_faction_state_json
        result = call(**params, agent_id=session.agent_id)
        self.pending = True
        self.queries += 1
        return result

    def payload(self, payload):
        assert self.pending and isinstance(payload, bytes)
        self.pending = False
        self.payloads += 1

    def finish(self):
        assert not self.pending and self.query_scope is None
        assert self.queries == self.payloads
        return dict(queries=self.queries, payloads=self.payloads, actions_and_setup=self.calls,
                    input_recording=False, full_world_exports_during_measurement=0,
                    scope='Owned wire callback only; live sessions and heap unchanged')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-mode', choices=['single', 'segment_encoded'], required=True)
    parser.add_argument('--smoke', action='store_true')
    opts, args = parser.parse_known_args()
    assert '--record-native-inputs' in args and '--native-wire' in args
    instances = []

    class Configured(AdmittedAgents):
        research_mode = opts.host_mode
        research_diagnostics = False

        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            instances.append(self)

    p3_runtime.LocalAgents = Configured
    recorder_module.NativeLoopTrace = LiveWire
    sys.argv = [sys.argv[0], *args]
    meta = p3_runtime.main()
    assert len(instances) == 1
    agent = instances[0]
    assert agent._context is None and agent._trace.query_scope is None
    assert all(s['diagnostic'] is None for s in agent.segment_records)
    meta['hardware'].pop('chrome', None)
    meta['hardware']['other_applications'] = 'not controlled; pressure telemetry archived'
    meta['host_mode'] = opts.host_mode
    meta['smoke'] = opts.smoke
    meta['formal_full_host_acceptance'] = False
    meta['default_adoption'] = False
    meta['host_scope'] = ('Complete Lab local live queue, per-request budget, original sessions/RNG/consumption, '
                          'world, delta, ordinary presentation, drawing, SDL flip; excludes production network')
    meta['causal_scope'] = 'Live trajectories differ; one ABBA runtime screen, not paired fixed-input speedup'
    meta['instrumentation_scope'] = ('Frozen p3_runtime coarse phases and 1Hz census; no fact diagnostics, '
                                      'per-operation hashes, full exports, pixels or vmmap in timing')
    lengths = {}
    for segment in agent.segment_records:
        n = len(segment['executed'])
        lengths[str(n)] = lengths.get(str(n), 0) + 1
    meta['admitted_segments'] = dict(count=len(agent.segment_records), lengths=lengths,
                                    executed_queries=sum(len(s['executed']) for s in agent.segment_records))
    target = Path(meta['workload']['output'])
    segments = target.with_suffix('.segments.json')
    assert not segments.exists()
    segments.write_text(json.dumps(agent.segment_records, separators=(',', ':')) + '\n')
    meta['segments_raw'] = dict(file=segments.name, sha256=hashlib.sha256(segments.read_bytes()).hexdigest())
    target.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(status='full_local_host_complete', mode=opts.host_mode,
                          guards=meta['guards'], frame=meta['frame_work_ms'], segments=meta['admitted_segments'])), flush=True)


if __name__ == '__main__':
    main()
