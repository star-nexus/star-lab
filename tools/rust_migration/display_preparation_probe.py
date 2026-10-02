"""E7 ordinary-native full trace and independent persistent presentation consumers.

Diagnostic instrumentation is isolated. Paired work excludes validation, hashing,
input IO, initialization and pacing; includes ordinary requests/steps/encoding,
client decoding, presentation, all mounted display systems and render submission.
Fixed display scripts supplement, never rewrite, the historical world trace.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gc
import gzip
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

TRACE_SHA = '1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77'
EXT_SHA = '838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
MODES = ('baseline', 'empty_territory')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def git(root,*args): return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
def save(path,value):
    data=gzip.compress(json.dumps(value,separators=(',',':'),allow_nan=False).encode(),mtime=0)
    path.write_bytes(data)
    return dict(file=path.name,sha256=sha(path),bytes=len(data))
def summary(values):
    v=sorted(values)
    return dict(samples=len(v),mean_ns=sum(v)/len(v),p99_ns=v[int(len(v)*.99)],max_ns=v[-1]) if v else {}

class Diagnosis:
    """Inclusive timings. Component subphases are exclusive within _component."""
    def __init__(self, session):
        import rotk_env.runtime.world_presentation as wp
        import ast
        import inspect
        import textwrap
        from rotk_env.utils.unit_spatial_index import get_unit_spatial_index
        self.rows=defaultdict(lambda:[0,0]); self.originals=[]
        def wrap(obj,name,key):
            original=getattr(obj,name)
            def timed(*args,**kwargs):
                start=time.perf_counter_ns()
                before=getattr(obj,'_faction_roster_members',None) if name=='_current_faction_counts' else None
                spatial_before=get_unit_spatial_index(args[0]).revision if key=='spatial.update' else None
                try:return original(*args,**kwargs)
                finally:
                    elapsed=time.perf_counter_ns()-start
                    row=self.rows[key];row[0]+=1;row[1]+=elapsed
                    if name=='add_component':
                        typed=self.rows['ecs.write.'+type(args[1]).__name__];typed[0]+=1;typed[1]+=elapsed
                    if name=='_current_faction_counts' and getattr(obj,'_faction_roster_members',None)!=before:
                        self.rows['reference.UI.roster_rebuild'][0]+=1
                    if spatial_before is not None and get_unit_spatial_index(args[0]).revision!=spatial_before:
                        self.rows['spatial.changed'][0]+=1
            setattr(obj,name,timed);self.originals.append((obj,name,original))
        original=wp._component
        def component(cls,state):
            key='component.'+cls.__name__
            t=time.perf_counter_ns();values=wp.deepcopy(state);u=time.perf_counter_ns()
            self.rows[key+'.copy'][0]+=1;self.rows[key+'.copy'][1]+=u-t
            for name,enum in wp._ENUM_FIELDS.get(cls,{}).items():
                if values.get(name) is not None: values[name]=enum(values[name])
            if cls is wp.c.UnitStatus and values.pop('current_status_is_enum',False):
                values['current_status']=wp.UnitState(values['current_status'])
            if cls is wp.c.Player:
                values['color']=tuple(values['color']);values['units']=set(values['units']['$set'])
            if cls is wp.c.MovementAnimation:
                values['path']=[tuple(cell) for cell in values['path']]
                for name in ('start_pixel_pos','target_pixel_pos'):
                    if values[name] is not None:values[name]=tuple(values[name])
            v=time.perf_counter_ns();self.rows[key+'.normalize'][0]+=1;self.rows[key+'.normalize'][1]+=v-u
            result=cls(**values);end=time.perf_counter_ns()
            self.rows[key+'.construct'][0]+=1;self.rows[key+'.construct'][1]+=end-v
            return result
        wp._component=component;self.originals.append((wp,'_component',original))
        for obj,name,key in [(session.world,'add_component','ecs.add_replace'),(session.world,'remove_component','ecs.remove'),
            (session.world,'_invalidate_cache','ecs.invalidate'),(session.world,'_drop_cache_entry','ecs.eviction'),
            (session.presentation,'_apply_fog','fog'),(session.presentation,'_apply_hud','hud'),
            (session.presentation.visuals,'apply','visuals.compute'),(wp,'update_unit_spatial_index','spatial.update')]:wrap(obj,name,key)
        for system in session.world.systems:
            wrap(system,'update','display.'+type(system).__name__)
            if hasattr(system,'_current_faction_counts'):wrap(system,'_current_faction_counts','reference.UI.roster')
        # Diagnostic-only AST instrumentation preserves the original statements,
        # ordering and return/error prefix. It does not instrument research modes.
        original=wp.WorldPresentation.apply
        tree=ast.parse(textwrap.dedent(inspect.getsource(original)));fn=tree.body[0];body=[]
        def finished(key,start):
            row=self.rows['apply.block.'+key];row[0]+=1;row[1]+=time.perf_counter_ns()-start
        for statement in fn.body:
            literal=ast.unparse(statement)
            key='other'
            if 'delta[\'units\']' in literal:key='units'
            elif 'delta[\'tiles\']' in literal:key='tiles'
            elif 'delta[\'state\']' in literal:key='singleton'
            elif literal.startswith(('players =','if players[','for row in players[')):key='players'
            elif 'self._apply_fog' in literal:key='fog'
            elif 'self._apply_hud' in literal:key='hud'
            elif 'visual' in literal:key='visuals'
            elif 'delta[\'removed\']' in literal:key='removed'
            elif literal.startswith('return '):key='events'
            body.extend(ast.parse('_e6_diag_t0 = _e6_diag_clock()').body)
            final=ast.parse(f'_e6_diag_finished({key!r}, _e6_diag_t0)').body
            body.append(ast.Try(body=[statement],handlers=[],orelse=[],finalbody=final))
        fn.body=body;ast.fix_missing_locations(tree)
        namespace=dict(wp.__dict__,_e6_diag_clock=time.perf_counter_ns,_e6_diag_finished=finished)
        exec(compile(tree,'<E6 diagnosis: original apply statements>','exec'),namespace)
        wp.WorldPresentation.apply=namespace['apply'];self.originals.append((wp.WorldPresentation,'apply',original))
    def finish(self):
        for obj,name,original in reversed(self.originals):setattr(obj,name,original)
        return {key:dict(calls=n,total_ns=ns) for key,(n,ns) in sorted(self.rows.items())}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha',required=True)
    p.add_argument('--trace',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--consumer',choices=['baseline','reuse_typed'],default='baseline')
    p.add_argument('--full-authority',action='store_true')
    p.add_argument('--probe-control',action='store_true')
    p.add_argument('--task',choices=['diagnose','correctness','paired','single'],required=True)
    p.add_argument('--candidate',choices=MODES,default='empty_territory');p.add_argument('--threads',type=int,choices=[1,4],default=1)
    p.add_argument('--driver',choices=['dummy','cocoa'],default='dummy');p.add_argument('--script',choices=['static','exercise'],default='static')
    p.add_argument('--overscan-clock',choices=['wall','items'],default='wall',help='Pixel contract only: fixed item quota, with the real performance clock unchanged')
    p.add_argument('--archive-deltas',action='store_true',help='Diagnostic only: archive regenerated complete native JSONL outside timed intervals')
    p.add_argument('--display-clock',choices=['fixed','wall'],default='fixed',help='Fixed display-only wall time is separate from real perf clocks')
    p.add_argument('--same-mode-control',action='store_true',help='Development baseline/baseline pixel control')
    p.add_argument('--limit',type=int,help='Development smoke only, never accepted as formal evidence')
    a=p.parse_args();src=a.source.resolve();out=a.output.resolve();out.parent.mkdir(parents=True,exist_ok=True)
    assert not out.exists(),out
    assert git(src,'rev-parse','HEAD')==a.source_sha
    assert not git(src,'status','--porcelain','--untracked-files=no')
    assert sha(a.trace)==TRACE_SHA
    trace=json.loads(gzip.decompress(a.trace.read_bytes()));initial_path=a.trace.with_name(trace['initial']['file'])
    assert sha(initial_path)==trace['initial']['sha256'];initial=json.loads(gzip.decompress(initial_path.read_bytes()))
    os.chdir(src);sys.path.insert(0,str(src));sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    os.environ.update(HEADLESS='0',SDL_VIDEODRIVER=a.driver,PYGAME_HIDE_SUPPORT_PROMPT='1',STAR_SCALE_MINIMAP_UNITS='off')
    import pygame
    from framework.engine.game_engine import GameEngine
    from framework.engine import RMS
    from rotk_env import components as c
    from rotk_env.prefabs.config import Faction,PlayerType
    from rotk_env.runtime.bootstrap import prepare_display_world,encode
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.world_presentation import WorldPresentation,_UNIT_COLUMNS
    from rotk_env.runtime.session import NativeSession
    from rotk_env.runtime.local_controls import LocalControls
    from rotk_env.runtime.window_presentation import attach_battlefield_renderers
    from rotk_env.runtime.native_input import InputHandlingSystem,UnitActionButtonSystem,UIButtonSystem
    from rotk_env.systems.panel_render_system import PanelRenderSystem
    from rotk_env.systems.ui_render_system import UIRenderSystem
    from rotk_env.systems.window_minimap_system import MiniMapSystem
    from rotk_env.tests.test_native_world_presentation import detached_world
    from rotk_env.utils.unit_spatial_index import get_unit_spatial_index
    from star_native import _native
    from p3_local_agents import fixture
    assert sha(_native.__file__)==EXT_SHA
    scenario,fixture_sha=fixture(src,5000)
    engine=GameEngine(title='STAR E7 display preparation research',width=2480,height=1239,fps=30)
    template=None;sessions=[];diagnosis=None
    if a.task=='paired':modes=['baseline',a.candidate,a.candidate,'baseline']
    elif a.task=='correctness':modes=['baseline']*3 if a.same_mode_control else list(MODES)
    else:modes=[a.candidate if a.task=='single' else 'baseline']
    samples=[[] for _ in modes];pending=[dict(request_ns=0,step_ns=0) for _ in modes]
    counts=Counter();stream=hashlib.sha256();checks=Counter();ticks=0;diagnostic_rows=[];memory=[]
    baseline_display=None;mutable_ids=set();singletons_dirty=set();reference_rebuilds=Counter()
    delta_stream=None
    if a.archive_deltas:
        assert a.task=='diagnose'
        delta_stream=gzip.GzipFile(filename=str(out.with_suffix('.deltas.jsonl.gz')),mode='wb',mtime=0)
    began=time.perf_counter();original_wall=time.time
    if a.display_clock=='fixed':time.time=lambda:1720000000.+ticks/30
    baseline_rgb=None
    try:
        template,prepared=prepare_display_world(display='window',mode='real_time',scenario=scenario,seed=42,
            players={Faction.WEI:PlayerType.HUMAN,Faction.SHU:PlayerType.AI,Faction.WU:PlayerType.AI})
        assert sorted(row['id'] for row in initial['entities'] if 'Unit' in row['components'])==list(template.query().with_component(c.Unit).ordered_entities())
        for mode in modes:
            session=NativeSession.__new__(NativeSession);session.closed=False;session.failure=None
            session.world=detached_world(template);session.runtime=RustRuntime(initial,threads=a.threads)
            session.presentation=WorldPresentation(session.world)
            session.controls=LocalControls(session.runtime,session.presentation,initial,on_error=session._fail)
            session.controls.refresh()
            attach_battlefield_renderers(session.presentation)
            if a.overscan_clock=='items':
                assert a.task=='correctness', 'Fixed build quota cannot be used for performance'
                for system in session.world.systems:
                    if hasattr(system,'OVERSCAN_BUILD_BUDGET_MS'):
                        system.OVERSCAN_BUILD_BUDGET_MS=float('inf')
            for system in (InputHandlingSystem(session.controls),UnitActionButtonSystem(session.controls),UIButtonSystem(session.controls),PanelRenderSystem(),UIRenderSystem(),MiniMapSystem()):session._mount(system)
            sessions.append(session)
        template.reset();template=None
        # Initial query/reference rosters are warmed identically, outside measured work.
        for session in sessions:
            RMS.screen.fill((0,0,0));session.update_display(0,inputs=False);RMS.update()
        if a.task=='diagnose' or a.probe_control:
            from display_preparation_diagnosis import DisplayDiagnosis
            diagnosis=DisplayDiagnosis(sessions[1] if a.probe_control else sessions[0])
        gc.collect();gc.disable()
        from display_preparation_script import apply as display_script
        def script(session,tick):display_script(session,tick,a.script)
        pixel_stream=hashlib.sha256();pixel_rows=[];authority_rows=[]
        def compare_display(left,right,delta):
            x=left.world;y=right.world
            assert x.entities.keys()==y.entities.keys()
            assert x.entity_counter==y.entity_counter and x.revision==y.revision
            ids=set(x.query().with_component(c.Unit).ordered_entities())|set(left.presentation.visuals.entities)|set(delta['removed'])|set(delta['visuals']['removed'])|{r['id'] for r in delta['tiles']}
            for uid in ids:
                arow=x.entities.get(uid,{});brow=y.entities.get(uid,{})
                assert arow.keys()==brow.keys(),('components',uid)
                for cls,component in arow.items():
                    assert vars(component)==vars(brow[cls]),('fields',uid,cls.__name__)
            assert x._singleton_components.keys()==y._singleton_components.keys()
            for cls,component in x._singleton_components.items():
                if cls is not c.RngService:assert vars(component)==vars(y._singleton_components[cls]),('singleton',cls.__name__)
                else:
                    assert component.seed==y._singleton_components[cls].seed
                    assert {k:v.getstate() for k,v in component._rngs.items()}=={k:v.getstate() for k,v in y._singleton_components[cls]._rngs.items()}
            assert get_unit_spatial_index(x).by_entity==get_unit_spatial_index(y).by_entity
            for cls in _UNIT_COLUMNS.values():
                assert x.query().with_component(cls).ordered_entities()==y.query().with_component(cls).ordered_entities()
            # Cold/terrain rows are never written by the candidate. Still inspect
            # all their fields every 100 ticks and at the final boundary.
            if ticks%100==0 or ticks==9880:
                for uid,row in x.entities.items():
                    other=y.entities[uid];assert row.keys()==other.keys()
                    for cls,v in row.items():assert vars(v)==vars(other[cls]),('full world',uid,cls.__name__)
                checks['full_cold_world']+=1
        for op in trace['entries']:
            assert op['seq']==sum(counts.values());kind=op['kind'];counts[kind]+=1
            order=[0,1,2,3] if ticks%2==0 else [1,0,3,2] if a.task=='paired' else list(range(len(sessions)))
            if a.task!='paired':order=list(range(len(sessions)))
            results=[]
            for wi in order:
                session=sessions[wi];runtime=session.runtime;mode=modes[wi]
                if kind=='request':
                    if 'integer_string_limit' in op:sys.set_int_max_str_digits(op['integer_string_limit'])
                    t=time.perf_counter_ns()
                    if op.get('response_wire_format')=='native-json':
                        wire=runtime.get_faction_state_json(**op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'])
                        result=json.loads(wire);wire_sha=None
                    else:
                        result=runtime.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                        wire_sha=None
                    pending[wi]['request_ns']+=time.perf_counter_ns()-t
                    if op.get('response_wire_format')=='native-json':wire_sha=hashlib.sha256(wire.encode()).hexdigest()
                    if 'response_wire_sha256' in op:
                        if wire_sha is None:wire_sha=hashlib.sha256(json.dumps(result,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
                        assert wire_sha==op['response_wire_sha256']
                    else:assert digest(result)==op['response_sha256']
                    results.append(result)
                elif kind=='step':
                    t=time.perf_counter_ns();runtime.step(op['dt'],wall_time=op['wall_time']);pending[wi]['step_ns']+=time.perf_counter_ns()-t
                    continue
                elif kind=='presentation':
                    t=time.perf_counter_ns();wire=runtime._native.take_presentation_delta_json();u=time.perf_counter_ns()
                    delta=json.loads(wire);v=time.perf_counter_ns()
                    events=session.presentation._apply_research(delta,mode=a.consumer);w=time.perf_counter_ns()
                    script(session,ticks)
                    if diagnosis and (not a.probe_control or wi==1):diagnosis.begin_tick(ticks)
                    authority_before=runtime._native.export_state_json(None) if a.full_authority else None
                    from contextlib import ExitStack
                    draw_start=time.perf_counter_ns()
                    with ExitStack() as frame_scope:
                        renderers=[system for system in session.world.systems if hasattr(system,'_display_research_frame')]
                        if mode!='baseline' and not renderers:raise RuntimeError('Map prototype not installed')
                        for renderer in renderers:frame_scope.enter_context(renderer._display_research_frame(mode))
                        RMS.screen.fill((0,0,0));session.update_display(1/30,inputs=False)
                        commands=None
                        if a.task=='correctness':
                            from display_preparation_contract import fingerprint
                            commands=fingerprint(RMS)
                        draw_end=time.perf_counter_ns();RMS.update()
                    draw_done=time.perf_counter_ns()
                    if a.full_authority:
                        assert runtime._native.export_state_json(None)==authority_before,('authority written by display',ticks,mode)
                        authority_digest=hashlib.sha256(authority_before.encode()).hexdigest()
                        if wi==0:
                            baseline_authority_digest=authority_digest
                            authority_rows.append(dict(tick=ticks,sha256=authority_digest))
                        else:assert authority_digest==baseline_authority_digest,('authority',ticks,mode)
                        checks['full_authority']+=1
                    if commands is not None:
                        if wi==0:baseline_commands=commands
                        else:assert commands==baseline_commands,('command stream',ticks,mode)
                        checks['command_stream']+=1
                    if diagnosis and (not a.probe_control or wi==1):diagnosis.end_tick(ticks)
                    if a.driver=='cocoa':pygame.display.flip()
                    platform_done=time.perf_counter_ns()
                    phases=dict(encode_ns=u-t,decode_ns=v-u,apply_ns=w-v,display_ns=draw_end-draw_start,submit_ns=draw_done-draw_end,platform_ns=platform_done-draw_done)
                    phases['render_ns']=phases['display_ns']+phases['submit_ns']
                    phases['chain_ns']=phases['decode_ns']+phases['apply_ns']+phases['display_ns']+phases['submit_ns']+phases['platform_ns']
                    phases['total_ns']=sum(pending[wi].values())+phases['encode_ns']+phases['chain_ns']
                    phases.update(pending[wi]);pending[wi]=dict(request_ns=0,step_ns=0)
                    samples[wi].append(phases)
                    assert digest(events)==op['events_sha256'];results.append(delta)
                    if a.task=='correctness':
                        rgb=hashlib.sha256(pygame.image.tobytes(RMS.screen,'RGB')).hexdigest()
                        if wi==0:
                            baseline_rgb=pygame.image.tobytes(RMS.screen,'RGB')
                            baseline_display=rgb;pixel_stream.update(bytes.fromhex(rgb));pixel_rows.append(rgb)
                        else:
                            compare_display(sessions[0],session,delta)
                            if rgb!=baseline_display:
                                pygame.image.save(pygame.image.frombytes(baseline_rgb,RMS.screen.get_size(),'RGB'),str(out.with_suffix('.baseline-failure.png')))
                                pygame.image.save(RMS.screen,str(out.with_suffix('.candidate-failure.png')))
                                out.with_suffix('.failure.json').write_text(json.dumps(dict(tick=ticks,mode=mode,display_clock=a.display_clock,fields_equal=True,baseline=baseline_display,candidate=rgb),indent=2)+'\n')
                                raise AssertionError(('pixels',ticks,mode))
                        checks['pixels']+=1;checks['projection']+=1
                    if a.task=='diagnose' or a.probe_control:
                        if delta_stream:delta_stream.write(wire.encode()+b'\n')
                        stats=session.world.get_cache_stats()
                        diagnostic_rows.append(dict(tick=ticks,**phases,units=len(delta['units']),bytes=len(wire.encode()),cache=stats,
                            reference_versions={cls.__name__:session.world.component_reference_version(cls) for cls in _UNIT_COLUMNS.values()},
                            spatial_revision=get_unit_spatial_index(session.world).revision))
                else:raise ValueError(kind)
            if kind=='step':ticks+=1
            else:
                assert all(value==results[0] for value in results[1:]),('full response/delta',op['seq'])
                stream.update(bytes.fromhex(digest(results[0])))
            if kind=='presentation' and ticks%500==0:
                memory.append(dict(tick=ticks,maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    entities=[len(s.world.entities) for s in sessions],rosters=[len(next(sys for sys in s.world.systems if type(sys).__name__=='UIRenderSystem')._faction_roster_units) for s in sessions]))
                print(json.dumps(dict(progress=ticks,task=a.task,threads=a.threads)),flush=True)
            if a.limit and ticks>=a.limit and kind=='presentation':break
        finals=[s.runtime.export_state() for s in sessions]
        assert all(value==finals[0] for value in finals[1:])
        if not a.limit:
            assert counts==dict(request=40994,step=9880,presentation=9880)
            assert digest(finals[0])==trace['final_state_sha256']
            assert stream.hexdigest()=='e01f2147b0fba41b27d15634c552bfb96ee84480a7628926890e57027a65b76b'
        raw=save(out.with_suffix('.samples.json.gz'),samples)
        diag=diagnosis.finish() if diagnosis else None;diagnosis=None
        if delta_stream:delta_stream.close();delta_stream=None
        result=dict(source_sha=a.source_sha,source_dirty=git(src,'status','--porcelain','--untracked-files=no'),
            tool_sha256=sha(__file__),tooling_commit=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),
            extension_sha256=EXT_SHA,trace_sha256=TRACE_SHA,initial_sha256=sha(initial_path),original_source=trace['source'],
            argv=sys.argv,task=a.task,modes=modes,consumer=a.consumer,full_authority=a.full_authority,threads=a.threads,display_script=a.script,display_script_sha256=sha(Path(__file__).with_name('display_preparation_script.py')),display_clock=a.display_clock,overscan_clock=a.overscan_clock,driver=pygame.display.get_driver(),
            surface=list(RMS.screen.get_size()),fixture_sha256=fixture_sha,counts=dict(counts),stream_sha256=stream.hexdigest(),
            final_state_sha256=digest(finals[0]),checks=dict(checks),all_passed=True,formal=not bool(a.limit),
            diagnostic=a.task=='diagnose' or a.probe_control,probe_control=a.probe_control,elapsed_seconds=time.perf_counter()-began,memory=memory,raw=raw,
            summaries=[{key:summary([row[key] for row in rows]) for key in rows[0]} for rows in samples],
            authority_raw=save(out.with_suffix('.authority.json.gz'),authority_rows) if authority_rows else None,
            authority_contract='complete native JSON bytes before/after display and between persistent instances',
            pixel_stream_sha256=pixel_stream.hexdigest() if pixel_rows else None,
            pixel_raw=save(out.with_suffix('.pixels.json.gz'),pixel_rows) if pixel_rows else None,
            diagnosis=diag,diagnostic_raw=save(out.with_suffix('.diagnostic.json.gz'),diagnostic_rows) if diagnosis else None,
            dependency_lock_sha256=sha(src/'uv.lock'),python=sys.version,capacity_claim=False)
        # diag was restored above; save using the result rather than wrapper state.
        if diag is not None:result['diagnostic_raw']=save(out.with_suffix('.diagnostic.json.gz'),diagnostic_rows)
        if a.archive_deltas:
            path=out.with_suffix('.deltas.jsonl.gz');result['regenerated_deltas']=dict(file=path.name,sha256=sha(path),bytes=path.stat().st_size,rows=ticks)
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(output=str(out),all_passed=True,formal=result['formal'])),flush=True)
    finally:
        if delta_stream:delta_stream.close()
        time.time=original_wall
        if diagnosis:diagnosis.finish()
        gc.enable()
        for session in sessions:session.close()
        if template is not None:template.reset()
        (src/'rotk_env/maps'/f'{scenario}.json').unlink(missing_ok=True)
        pygame.quit()

if __name__=='__main__':main()
