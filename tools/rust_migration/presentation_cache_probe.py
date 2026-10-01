"""E6 ordinary-native full trace and independent persistent presentation consumers.

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
MODES = ('baseline', 'reuse_constructed', 'reuse_typed')

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
        self.rows=defaultdict(lambda:[0,0]); self.originals=[]
        def wrap(obj,name,key):
            original=getattr(obj,name)
            def timed(*args,**kwargs):
                start=time.perf_counter_ns()
                try:return original(*args,**kwargs)
                finally:
                    row=self.rows[key];row[0]+=1;row[1]+=time.perf_counter_ns()-start
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
    def finish(self):
        for obj,name,original in reversed(self.originals):setattr(obj,name,original)
        return {key:dict(calls=n,total_ns=ns) for key,(n,ns) in sorted(self.rows.items())}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha',required=True)
    p.add_argument('--trace',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--task',choices=['diagnose','correctness','paired','single'],required=True)
    p.add_argument('--candidate',choices=MODES,default='reuse_typed');p.add_argument('--threads',type=int,choices=[1,4],default=1)
    p.add_argument('--driver',choices=['dummy','cocoa'],default='dummy');p.add_argument('--script',choices=['static','exercise'],default='static')
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
    engine=GameEngine(title='STAR E6 presentation research',width=2480,height=1239,fps=30)
    template=None;sessions=[];diagnosis=None
    if a.task=='paired':modes=['baseline',a.candidate,a.candidate,'baseline']
    elif a.task=='correctness':modes=list(MODES)
    else:modes=[a.candidate if a.task=='single' else 'baseline']
    samples=[[] for _ in modes];pending=[dict(request_ns=0,step_ns=0) for _ in modes]
    counts=Counter();stream=hashlib.sha256();checks=Counter();ticks=0;diagnostic_rows=[];memory=[]
    baseline_display=None;mutable_ids=set();singletons_dirty=set();reference_rebuilds=Counter()
    began=time.perf_counter()
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
            for system in (InputHandlingSystem(session.controls),UnitActionButtonSystem(session.controls),UIButtonSystem(session.controls),PanelRenderSystem(),UIRenderSystem(),MiniMapSystem()):session._mount(system)
            sessions.append(session)
        template.reset();template=None
        # Initial query/reference rosters are warmed identically, outside measured work.
        for session in sessions:
            RMS.screen.fill((0,0,0));session.update_display(0,inputs=False);RMS.update()
        if a.task=='diagnose':diagnosis=Diagnosis(sessions[0])
        gc.collect();gc.disable()
        def script(session,tick):
            if a.script=='static':return
            # New deterministic display input; not part of the historical world trace.
            phase=(tick//300)%4;camera=session.world.get_singleton_component(c.Camera);ui=session.world.get_singleton_component(c.UIState)
            camera.zoom=(1.,.5,1.25,1.)[phase]
            camera.offset_x=1240+(80 if phase==2 else 0);camera.offset_y=619
            ui.view_faction=(Faction.WEI,Faction.SHU,Faction.WU,Faction.WEI)[phase]
            ids=session.world.query().with_component(c.Unit).ordered_entities()
            ui.selected_unit=ids[0] if phase in (1,3) and ids else None
        def row_state(world,uid):
            return {t.__name__:encode(v) for t,v in world.entities.get(uid,{}).items()}
        # Every mutable presentation row is checked every tick. Terrain/cold
        # resources are initialized identically and compared fully at boundaries.
        def projection(session,ids):
            w=session.world;index=get_unit_spatial_index(w)
            return dict(rows={str(uid):row_state(w,uid) for uid in ids},
                singletons={t.__name__:encode(v) for t,v in w._singleton_components.items() if t is not c.RngService},
                spatial={str(k):encode(v) for k,v in index.by_entity.items()},
                queries={cls.__name__:w.query().with_component(cls).ordered_entities() for cls in _UNIT_COLUMNS.values()},
                entity_ids=tuple(w.entities),counter=w.entity_counter,revision=w.revision)
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
                    events=session.presentation._apply_research(delta,mode=mode);w=time.perf_counter_ns()
                    script(session,ticks)
                    draw_start=time.perf_counter_ns();RMS.screen.fill((0,0,0))
                    session.update_display(1/30,inputs=False);draw_end=time.perf_counter_ns();RMS.update();draw_done=time.perf_counter_ns()
                    if a.driver=='cocoa':pygame.display.flip()
                    platform_done=time.perf_counter_ns()
                    phases=dict(encode_ns=u-t,decode_ns=v-u,apply_ns=w-v,display_ns=draw_end-draw_start,submit_ns=draw_done-draw_end,platform_ns=platform_done-draw_done)
                    phases['chain_ns']=phases['decode_ns']+phases['apply_ns']+phases['display_ns']+phases['submit_ns']+phases['platform_ns']
                    phases['total_ns']=sum(pending[wi].values())+phases['encode_ns']+phases['chain_ns']
                    phases.update(pending[wi]);pending[wi]=dict(request_ns=0,step_ns=0)
                    samples[wi].append(phases)
                    assert digest(events)==op['events_sha256'];results.append(delta)
                    if a.task=='correctness':
                        ids=set(session.world.query().with_component(c.Unit).ordered_entities())|set(session.presentation.visuals.entities)|set(delta['removed'])|set(delta['visuals']['removed'])
                        actual=projection(session,ids)
                        rgb=hashlib.sha256(pygame.image.tobytes(RMS.screen,'RGB')).hexdigest()
                        commands=(rgb,actual)
                        if wi==0:baseline_display=commands
                        else:assert commands==baseline_display,('presentation/pixels',ticks,mode)
                        checks['pixels']+=1;checks['projection']+=1
                    if a.task=='diagnose':
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
        result=dict(source_sha=a.source_sha,source_dirty=git(src,'status','--porcelain','--untracked-files=no'),
            tool_sha256=sha(__file__),tooling_commit=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),
            extension_sha256=EXT_SHA,trace_sha256=TRACE_SHA,initial_sha256=sha(initial_path),original_source=trace['source'],
            argv=sys.argv,task=a.task,modes=modes,threads=a.threads,display_script=a.script,driver=pygame.display.get_driver(),
            surface=list(RMS.screen.get_size()),fixture_sha256=fixture_sha,counts=dict(counts),stream_sha256=stream.hexdigest(),
            final_state_sha256=digest(finals[0]),checks=dict(checks),all_passed=True,formal=not bool(a.limit),
            diagnostic=a.task=='diagnose',elapsed_seconds=time.perf_counter()-began,memory=memory,raw=raw,
            summaries=[{key:summary([row[key] for row in rows]) for key in rows[0]} for rows in samples],
            diagnosis=diag,diagnostic_raw=save(out.with_suffix('.diagnostic.json.gz'),diagnostic_rows) if diagnosis else None,
            dependency_lock_sha256=sha(src/'uv.lock'),python=sys.version,capacity_claim=False)
        # diag was restored above; save using the result rather than wrapper state.
        if diag is not None:result['diagnostic_raw']=save(out.with_suffix('.diagnostic.json.gz'),diagnostic_rows)
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(output=str(out),all_passed=True,formal=result['formal'])),flush=True)
    finally:
        if diagnosis:diagnosis.finish()
        gc.enable()
        for session in sessions:session.close()
        if template is not None:template.reset()
        (src/'rotk_env/maps'/f'{scenario}.json').unlink(missing_ok=True)
        pygame.quit()

if __name__=='__main__':main()
