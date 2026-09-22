"""Check saved settlement files and reproduce the prior recorder's missing wall time."""
import argparse
from copy import deepcopy
import csv
import hashlib
import json
import lzma
import os
from pathlib import Path
import sys
from r3_observations_probe import git
from r3_scene_host_probe import replay


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--window',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=args.source.resolve();window=args.window.resolve();output=args.output.resolve()
    os.chdir(source);sys.path.insert(0,str(source));os.environ['SDL_VIDEODRIVER']='dummy'
    from rotk_env.runtime.native import RustRuntime
    cases=json.loads(lzma.decompress((window/'trace.json.xz').read_bytes()))
    results=[]
    for case in cases:
        folder=window/case['name']/'settlement_reports';files=list(folder.glob('report_*.json'))
        assert len(files)==1
        report=json.loads(files[0].read_text())
        with (folder/'settlement_results.csv').open() as stream:rows=list(csv.DictReader(stream))
        assert len(rows)==1
        row=rows[0]
        assert report['game_mode']==row['game_mode']==case['mode']
        assert report['experiment_id']==row['experiment_id']
        assert report['is_tie'] and report['end_reason']=='timeout'
        assert report['map_type']==row['map_type']=='Custom map (chibi-small)'
        for faction in ('wei','shu'):
            assert report['units_info'][faction]['total_units']==int(row[f'{faction}_total_units'])==5
            assert report['units_info'][faction]['surviving_units']==int(row[f'{faction}_surviving_units'])==5
        results.append(dict(case=case['name'],json=str(files[0].relative_to(window)),csv=str((folder/'settlement_results.csv').relative_to(window)),all_passed=True))
    # Fault injection is a diagnostic reproduction, never an alternate formal trace.
    faulty=deepcopy(cases[0]);step=next(n for n in faulty['nodes'] if n['method']=='step')
    expected_wall_time=step['kwargs']['wall_time'];step['kwargs']['wall_time']=None
    try:replay([faulty],RustRuntime)
    except AssertionError as exc:difference=exc.args[0]
    else:raise AssertionError('missing wall metadata must break replay')
    assert difference['method']=='step' and difference['kind']=='state',difference
    assert difference['path'].endswith('.UnitObservation.last_seen_time') and difference['expected']==expected_wall_time,difference
    result=dict(all_passed=True,reports=results,recorder_fault_injection=difference,source_sha=git(source,'rev-parse','HEAD'),
        tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),trace_sha256=hashlib.sha256((window/'trace.json.xz').read_bytes()).hexdigest())
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(all_passed=True,reports=len(results),diagnostic_path=difference['path'])))


if __name__=='__main__':main()
