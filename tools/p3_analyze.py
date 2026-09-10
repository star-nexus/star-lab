"""Recompute P3 timing/service metrics from checksummed raw evidence (no STAR import)."""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from p3_local_agents import stats


def analyze(point_path, raw_path=None):
    point_path = Path(point_path)
    point = json.loads(point_path.read_text())
    raw_path = Path(raw_path) if raw_path else point_path.with_suffix('.raw.json')
    blob = raw_path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != point['raw']['sha256']:
        raise ValueError('raw SHA256 mismatch')
    raw = json.loads(blob)
    warmup = point['workload']['warmup']
    frames = [r for r in raw['frames'] if r['t'] >= warmup]
    events = [r for r in raw['events'] if r['t'] >= warmup]
    metrics = {
        'frame_work_ms': stats([r['work_ms'] for r in frames]),
        'observation_response_ms': stats([r['response_ms'] for r in events if r['event']=='observe']),
        'action_queue_ms': stats([r['queue_ms'] for r in events if r['event']=='act']),
    }
    for name, recomputed in metrics.items():
        original = point[name]
        if any(original.get(k) != v for k,v in recomputed.items() if k in original):
            raise ValueError(f'{name} differs from raw recomputation')
    admitted_census = [r for r in raw['censuses'] if r['t'] >= warmup]
    action_rows = [a for r in events for a in r.get('actions', [])]
    counts = Counter(r['agent'] for r in events if r['event'] == 'observe')
    session_count = point['workload']['agents']
    return {'verified':True, 'source':point['source']['sha'], 'metrics':metrics,
        'frame_count':len(frames), 'completed_observations':metrics['observation_response_ms']['count'],
        'alive_units':stats([r['alive'] for r in admitted_census]),
        'moving_units':stats([r['moving'] for r in admitted_census]),
        'observations_per_session':stats([counts[i] for i in range(session_count)]),
        'observation_build_ms':stats([r['build_ms'] for r in events if r['event']=='observe']),
        'observation_decode_ms':stats([r['decode_ms'] for r in events if 'decode_ms' in r]),
        'observed_batch_size':stats([r['batch_size'] for r in events if 'batch_size' in r]),
        'observation_encode_ms':stats([r['encode_ms'] for r in events if r['event']=='observe']),
        'observation_bytes':stats([r['bytes'] for r in events if 'bytes' in r]),
        'agent_frame_ms':stats([r['agent_ms'] for r in frames]),
        'simulation_seconds':sum(r['dt'] for r in frames),
        'maxrss_bytes':max([0]+[r['maxrss'] for r in admitted_census]),
        'sampled_position_changes':sum(r['position_changes'] for r in admitted_census),
        'accepted_moves':sum(a['verb']=='move' and a['accepted'] for a in action_rows),
        'accepted_attacks':sum(a['verb']=='attack' and a['accepted'] for a in action_rows),
        'rejected_actions':sum(not a['accepted'] for a in action_rows),
        'frame_deadline_miss_fraction':sum(r['work_ms']>1000/point['workload'].get('fps',30) for r in frames)/max(1,len(frames)),
        'guard_pass_as_recorded':point['pass']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('point')
    p.add_argument('--raw')
    p.add_argument('--output')
    args = p.parse_args()
    result = json.dumps(analyze(args.point,args.raw),indent=2)+'\n'
    if args.output:
        Path(args.output).write_text(result)
    else:
        print(result,end='')
