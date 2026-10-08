"""Independent raw/statistical and archive audit of the frozen census host ABBA."""
import argparse
import bisect
import hashlib
import json
import math
from pathlib import Path
import zipfile
import numpy as np


def digest(data):
    return hashlib.sha256(data).hexdigest()


def statistics(values):
    rows = sorted(values)
    assert rows and all(math.isfinite(v) and v >= 0 for v in rows)
    return dict(count=len(rows), min=rows[0], avg=sum(values)/len(rows),
                p50=rows[math.ceil(.5*len(rows))-1],
                p95=rows[math.ceil(.95*len(rows))-1],
                p99=rows[math.ceil(.99*len(rows))-1], max=rows[-1])


def verify(runs, experiment):
    reg = json.loads((experiment/'results/census-host-preregister.json').read_text())
    complete = json.loads((experiment/'results/census-host-complete.json').read_text())
    assert complete['status'] == 'complete' and complete['completed'] == complete['total'] == 4
    original = complete['analysis']
    points, checked = [], []
    for number, mode in enumerate(reg['order'], 1):
        path = runs/f'{number}-{mode}.json'
        meta = json.loads(path.read_text())
        for key, namekey in [('raw','path'), ('screenshot','file'), ('segments_raw','file')]:
            data = (runs/meta[key][namekey]).read_bytes()
            assert digest(data) == meta[key]['sha256']
            checked.append(meta[key][namekey])
        raw = json.loads((runs/meta['raw']['path']).read_text())
        guard = json.loads(path.with_suffix('.monitor.json').read_text())
        assert guard['command'] == [str(Path(reg['source'])/'.venv/bin/python'),
            str(Path(meta['tooling']['path'])/'tools/rust_migration/census_observation_host.py'),
            '--scan-mode', mode, *reg['runtime_args'], '--output', meta['workload']['output']]
        assert guard['status'] == 'passed' and guard['child_exit'] == 0
        assert guard['samples'] and all(s['pressure'] == 1 for s in guard['samples'])
        assert not guard['events'] and not guard['automatic_pause'] and not guard['automatic_termination']
        assert not guard['budget_enforced']
        assert meta['source']['sha'] == reg['source_sha'] and not meta['source']['dirty']
        assert meta['tooling']['sha'] == '1c9e5fe9af7450f2c7946e244bc070b995e5ec7b' and not meta['tooling']['dirty']
        assert meta['extension']['sha256'] == reg['extension_sha256'] and meta['extension']['api'] == 18
        assert meta['hardware']['window'] == meta['surface_size'] == reg['fixed_window']
        assert meta['display_driver'] == reg['display_driver']
        w = meta['workload']
        assert (w['units'],w['agents'],w['native_threads'],w['warmup'],w['seconds']) == (5000,1000,1,30,60)
        assert w['presentation_research_mode'] == 'baseline' and not w['attribute'] and not w['presentation_research_profile']
        assert w['clock_mode'] == 'fixed' and w['cycle_mode'] == 'post-action' and w['gc_policy'] == 'realtime_defer'
        assert meta['host_mode'] == 'single' and meta['census_scan_mode'] == mode
        assert not meta['smoke'] and not meta['default_adoption']
        record = meta['native_recording']
        assert record['scan_mode'] == mode and record['scan_mode_persisted'] and record['scan_configuration_calls'] == 1
        assert record['queries'] == record['payloads'] == sum(e['event']=='observe' for e in raw['events'])
        assert record['full_world_exports_during_measurement'] == 0 and not record['input_recording']
        assert meta['admitted_segments'] == dict(count=0,lengths={},executed_queries=0)
        assert json.loads((runs/meta['segments_raw']['file']).read_text()) == []
        frames = [f for f in raw['frames'] if f['t'] >= 30]
        events = [e for e in raw['events'] if e['t'] >= 30]
        cens = [c for c in raw['censuses'] if c['t'] >= 30]
        assert len(frames) == meta['frame_count'] == 1800
        assert raw['frames'][-1]['t'] >= 89.9
        assert all(abs(f['dt']-1/30)<1e-12 for f in raw['frames'])
        assert all(abs(c['board_time']-c['sim_time'])<1e-6 for c in raw['censuses'])
        assert cens and all(c['fog'] and not c['game_over'] and c['alive']>=4750 for c in cens)
        assert raw['censuses'][0]['alive'] == 5000 and sum(c['position_changes'] for c in cens) > 0
        assert meta['final_native']['living_units'] == 5000 and meta['agents']['sessions'] == 1000
        assert meta['agents']['oldest_overdue_ms'] <= 100
        for verb in ('move','attack'):
            assert any(a['verb']==verb and a['accepted'] for e in events for a in e.get('actions',[]))
        assert meta['world_hz'] == len(frames)/60 == 30
        assert meta['completed_observations'] >= .95*meta['nominal_observations']
        assert all(meta['guards'].values()) and meta['pass']
        for field, rows, value in [('frame_work_ms',frames,'work_ms'),
                ('observation_response_ms',[e for e in events if e['event']=='observe'],'response_ms'),
                ('observation_queue_ms',[e for e in events if e['event']=='observe'],'queue_ms'),
                ('action_queue_ms',[e for e in events if e['event']=='act'],'queue_ms')]:
            computed = statistics([r[value] for r in rows])
            assert computed == meta[field]
            assert computed['p99'] <= (1000/30 if field=='frame_work_ms' else 100)
        points.append((meta,raw,frames,events))
    for field in ('fixture_sha256','dependency_lock_sha256','extension','surface_size','display_driver'):
        assert all(p[0][field] == points[0][0][field] for p in points)
    metrics = {}
    for key, kind, value in [('frame_work_ms','frame','work_ms'),('observation_service_ms','observe','service_ms')]:
        summaries, samples = [], []
        rng = np.random.default_rng(42)
        for meta,raw,frames,events in points:
            rows = frames if kind=='frame' else [e for e in events if e['event']=='observe']
            summaries.append(statistics([r[value] for r in rows]))
            stamps = [f['t'] for f in raw['frames']]
            first = next(i for i,f in enumerate(raw['frames']) if f['t']>=30)
            blocks = np.zeros((math.ceil(len(frames)/100),2))
            for row in rows:
                index = max(0,bisect.bisect_right(stamps,row['t'])-1-first)//100
                index = min(index,len(blocks)-1)
                blocks[index] += (row[value],1)
            drawn = blocks[rng.integers(0,len(blocks),size=(10000,len(blocks)))]
            totals = drawn.sum(axis=1)
            assert (totals[:,1]>0).all()
            samples.append(totals[:,0]/totals[:,1])
        base = (summaries[0]['avg']+summaries[3]['avg'])/2
        candidate = (summaries[1]['avg']+summaries[2]['avg'])/2
        interval = np.quantile((samples[0]+samples[3]-samples[1]-samples[2])/2,[.025,.975]).tolist()
        metric = original['metrics'][key]
        assert summaries == metric['per_run']
        assert math.isclose(base,metric['baseline_mean'],abs_tol=1e-12)
        assert math.isclose(candidate,metric['candidate_mean'],abs_tol=1e-12)
        assert np.allclose(interval,metric['ci95_live_block_difference_ms'],rtol=0,atol=1e-12)
        p99 = max(summaries[1]['p99'],summaries[2]['p99']) <= max(summaries[0]['p99'],summaries[3]['p99'])
        pct = 100*(base-candidate)/base
        passed = interval[0]>0 and p99 and pct>0 and (kind=='frame' or pct>=5)
        assert passed == metric['screening_passed']
        metrics[key] = dict(baseline=base,candidate=candidate,improvement_percent=pct,ci95_ms=interval,passed=bool(passed))
    for field, envelope in original['queue_envelopes'].items():
        values = [p[0][field]['p99'] for p in points]
        assert values == envelope['per_run_p99']
        assert envelope['no_regression'] == (max(values[1:3])<=max(values[0],values[3]))
    assert original['resource_valid'] == [True]*4 and original['operational_guards_passed']
    assert original['screening_positive'] == (all(m['passed'] for m in metrics.values()) and all(q['no_regression'] for q in original['queue_envelopes'].values()))
    archive = experiment/complete['raw']['path']
    assert digest(archive.read_bytes()) == complete['raw']['sha256']
    assert archive.stat().st_size == complete['raw']['bytes']
    members = 0
    with zipfile.ZipFile(archive) as z:
        hashes = z.read('SHA256SUMS').decode().splitlines()
        assert len(z.namelist()) == len(hashes)+1 == complete['raw']['members']+1
        for row in hashes:
            expected,name = row.split('  ',1)
            data = z.read(name)
            assert digest(data) == expected,name
            current = runs/Path(name).name if name.startswith('raw/') else None
            if current is not None:
                assert current.read_bytes() == data,name
            members += 1
        for file,expected in reg['frozen_files'].items():
            assert digest(z.read('tools/'+Path(file).name)) == expected
        assert z.read('preregister.json') == (experiment/'results/census-host-preregister.json').read_bytes()
    return dict(passed=True,attempts=4,formal_frames=[len(p[2]) for p in points],
        formal_observations=[sum(e['event']=='observe' for e in p[3]) for p in points],
        all_observations=[p[0]['native_recording']['queries'] for p in points],
        final_overdue_events=[p[0]['agents']['overdue_events'] for p in points],
        final_oldest_overdue_ms=[p[0]['agents']['oldest_overdue_ms'] for p in points],
        raw_hashes_checked=checked,inner_members_checked=members,metrics_recomputed=metrics,
        method='Independent nearest-rank statistics and bisect 100-frame blocks,10000 bootstrap,seed42,equal run weights',
        raw=complete['raw'],all_guards=True,all_pressure_normal=True,
        verdict='service gain supported; full-frame CI crosses zero; default stays off',
        full_canonical_or_native4_or_production_network_validation=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--experiment',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    result = verify(a.runs,a.experiment)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False))
