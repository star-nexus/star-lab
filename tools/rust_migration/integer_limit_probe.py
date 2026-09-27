"""Public telemetry boundary audit against the pinned CPython default digit limit."""
import argparse, datetime, hashlib, json, lzma, os, subprocess, sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


def cases():
    for n in (4299, 4300, 4301):
        for style in ('ascii', 'unicode', 'separators', 'signed'):
            text = '0' * (n - 1) + '1'
            if style == 'unicode': text = text.translate(str.maketrans('01', '０１'))
            if style == 'separators': text = '_'.join(text)
            if style == 'signed': text = ' \t-' + text + '\u2003'
            yield f'{style}-{n}', text
    for name, text in [('empty', ''), ('malformed', '1__0'), ('float', '1.5'),
                       ('bool', True), ('number', 2.75), ('list', [1]),
                       ('zeros-over', '0' * 4301), ('long-float-score', '0.' + '0'*5000 + '1')]:
        yield name, text


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--expect-equal',action='store_true');a=p.parse_args()
    src=a.source.resolve();out=a.output.resolve();os.chdir(src);sys.path.insert(0,str(src));os.environ['SDL_VIDEODRIVER']='dummy'
    assert sys.get_int_max_str_digits()==4300, 'This audit targets the pinned default oracle limit'
    from star_native import _native, API_VERSION
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.tests.test_native_vision import make_vision_world
    from rotk_env.systems.llm_system import LLMSystem
    class Frozen(datetime.datetime):
        @classmethod
        def now(cls,tz=None):return cls(2026,9,12,12)
    rows=[]
    with patch('time.time',return_value=1720000000.),patch('datetime.datetime',Frozen):
        for name,value in cases():
            world,_,_=make_vision_world('none');gate=LLMSystem();world.add_system(gate)
            try:
                initial=export_initial_state(world)
                with RustRuntime(initial) as native:
                    steps=[]
                    for action,params in [('register_agent_info',dict(faction='wei',provider='synthetic',model_id='m',base_url='http://local')),
                        ('report_llm_stats',dict(faction='wei',api_stats=dict(prompt_tokens=value),toolcall_error_total=value)),
                        ('report_llm_stats',dict(faction='wei',api_stats=dict(prompt_tokens=2),toolcall_error_total=2))]:
                        py=gate._process_action_request(agent_id='a',action_id=0,action=action,params=deepcopy(params),send_response=False)
                        rs=native.execute_action(action,deepcopy(params),agent_id='a')
                        ps=export_initial_state(world);ns=native.export_state()
                        steps.append(dict(action=action,parameters=params,python=py,rust=rs,python_state=ps,rust_state=ns,response_equal=py==rs,state_equal=ps==ns))
                    rows.append(dict(name=name,initial=initial,steps=steps))
            finally:world.reset()
    compact=[]
    for row in rows:
        last=row['steps'][-1];compact.append(dict(name=row['name'],response_equal=all(s['response_equal'] for s in row['steps']),state_equal=all(s['state_equal'] for s in row['steps']),python_counter=last['python_state']['singletons']['GameStats']['llm_api_stats']['wei']['prompt_tokens'],rust_counter=last['rust_state']['singletons']['GameStats']['llm_api_stats']['wei']['prompt_tokens']))
    out.mkdir(parents=True,exist_ok=True);raw=lzma.compress(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode());(out/'raw.json.xz').write_bytes(raw)
    git=lambda root,*args:subprocess.check_output(['git',*args],cwd=root,text=True).strip()
    result=dict(source_sha=git(src,'rev-parse','HEAD'),source_dirty=git(src,'status','--porcelain'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),python=sys.version,int_max_str_digits=sys.get_int_max_str_digits(),api=API_VERSION,extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),cases=compact,all_equal=all(r['response_equal'] and r['state_equal'] for r in compact),raw=dict(path='raw.json.xz',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),capacity_claim=False)
    assert not result['source_dirty'];(out/'compact.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    assert result['all_equal']==a.expect_equal

if __name__=='__main__':main()
