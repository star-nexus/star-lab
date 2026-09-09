"""Regenerate P3 decision-grade matrix and long-candidate trend from the archive."""
from pathlib import Path
import hashlib
import json
import zipfile
import sys
from p3_local_agents import stats


def report(case):
    case = Path(case)
    names = ['poll100-a100-h1','poll1000-a1000-h1','poll3000-a1000-h1',
             'poll5000-a1000-h1','poll10000-a1000-h1','poll10000-a5000-h1',
             'poll10000-a10000-h1','poll5000-a1000-h5',
             'poll5000-a1000-h10-clean','poll5000-a1000-h30']
    matrix = []
    for name in names:
        d = json.loads((case/'results'/f'{name}.json').read_text())
        matrix.append({'run':name, 'source':d['source']['sha'], 'tooling':d['tooling'],
            'units':d['workload']['units'],'agents':d['workload']['agents'],
            'observation_hz':d['workload']['observation_hz'],
            'decision_delay_s':d['workload']['delay'],
            'frame_p99_ms':d['frame_work_ms']['p99'], 'world_hz':d['world_hz'],
            'observation_p99_ms':d['observation_response_ms']['p99'],
            'completed':d['completed_observations'],'offered':d['nominal_observations'],
            'load_fraction':d['nominal_load_fraction'], 'guards':d['guards'],
            'raw_package':d['raw_package']})
    (case/'results/discovery-matrix.json').write_text(json.dumps(matrix,indent=2)+'\n')
    d = json.loads((case/'results/gate5000-d30-300.json').read_text())
    package = case/d['raw_package']['path']
    assert hashlib.sha256(package.read_bytes()).hexdigest()==d['raw_package']['sha256']
    with zipfile.ZipFile(package) as z:
        blob = z.read(d['raw']['path'])
    assert hashlib.sha256(blob).hexdigest()==d['raw']['sha256']
    raw = json.loads(blob)
    blocks = []
    for start in range(30,330,30):
        rows = [r for r in raw['events'] if start<=r['t']<start+30 and r['event']=='observe']
        blocks.append({'start_s':start, 'end_s':start+30,
            **{key:stats([r[key] for r in rows]) for key in
               ('build_ms','encode_ms','bytes','terrain','enemies','reachable')}})
    (case/'results/long-candidate-trend.json').write_text(json.dumps({
        'raw_package':d['raw_package'],'blocks':blocks},indent=2)+'\n')
    for r in matrix:
        print(f"| {r['units']} | {r['agents']} | {r['observation_hz']:g} | {r['world_hz']:.2f} | {r['frame_p99_ms']:.2f} | {r['observation_p99_ms']/1000:.3f} | {100*r['load_fraction']:.2f}% |")


if __name__=='__main__':
    report(sys.argv[1] if len(sys.argv)>1 else 'experiments/2026-09-p3-local-agents')
