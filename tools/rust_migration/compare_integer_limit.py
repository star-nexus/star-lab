"""Recheck paired full-state compatibility; only cross-run creation wall times differ."""
import argparse,copy,hashlib,json,lzma,subprocess
from pathlib import Path


def normalized(state):
    state=copy.deepcopy(state)
    for key in ('last_update_time','game_start_time','turn_start_time'):
        state['singletons']['GameTime'][key]=0
    return state


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',type=Path,required=True);root=p.parse_args().results
    data={}
    for name in ('before','after'):
        summary=json.loads((root/name/'compact.json').read_text());payload=(root/name/summary['raw']['path']).read_bytes()
        assert hashlib.sha256(payload).hexdigest()==summary['raw']['sha256']
        data[name]=(summary,json.loads(lzma.decompress(payload)))
    before,after=data['before'][1],data['after'][1];assert len(before)==len(after)==20
    cases=[]
    for b,a in zip(before,after):
        assert b['name']==a['name'] and normalized(b['initial'])==normalized(a['initial'])
        for bs,az in zip(b['steps'],a['steps']):
            assert bs['action']==az['action'] and bs['parameters']==az['parameters']
            assert bs['python']==az['python'] and normalized(bs['python_state'])==normalized(az['python_state'])
            assert az['python']==az['rust'] and az['python_state']==az['rust_state']
        cases.append(dict(name=a['name'],before_response_equal=all(s['python']==s['rust'] for s in b['steps']),before_state_equal=all(s['python_state']==s['rust_state'] for s in b['steps']),after_response_equal=True,after_state_equal=True))
    assert sum(not c['before_state_equal'] for c in cases)==4
    result=dict(cases=cases,initial_and_python_across_versions_equal_except_creation_wall_times=True,cross_run_normalized_fields=['singletons.GameTime.'+k for k in ('last_update_time','game_start_time','turn_start_time')],within_run_full_state_comparison_excludes_nothing=True,all_after_equal=True,tool_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[2],text=True).strip(),capacity_claim=False)
    (root/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('20 paired cases verified; 4 old state differences fixed')

if __name__=='__main__':main()
