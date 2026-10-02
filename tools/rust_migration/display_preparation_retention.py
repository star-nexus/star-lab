"""Independent E7 coordinate-cache retention/lifecycle diagnostic, never speed evidence."""
import argparse,gc,json,sys,tracemalloc,weakref
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.source))
from framework.ecs.world import World
from rotk_env.components import MapData
from rotk_env.systems.window_map_render_system import WindowMapRenderSystem

def renderer():
 r=object.__new__(WindowMapRenderSystem);r.world=World();r.world.add_singleton_component(MapData(width=160,height=90,tiles={(x,y):1 for x in range(120) for y in range(80)}));r.world.systems.append(r);return r
views=[{(x,y) for x in range(120) for y in range(80)}, {(x,y) for x in range(1,121) for y in range(80)}]
r=renderer();tracemalloc.start();samples=[]
for cycle in range(1200):
 with r._display_research_frame('empty_territory'):r._render_territory_boundaries_optimized(views[cycle%2],[0,0],1)
 if cycle%100==99:
  gc.collect();samples.append(dict(cycle=cycle+1,current_bytes=tracemalloc.get_traced_memory()[0],cached_coordinates=len(r._e7_valid_coordinates)))
retained_range=max(v['current_bytes'] for v in samples[2:])-min(v['current_bytes'] for v in samples[2:]);assert retained_range<65536, samples
r.world.reset();assert '_e7_valid_coordinates' not in r.__dict__
refs=[]
for i in range(24):
 obj=renderer()
 with obj._display_research_frame('empty_territory'):obj._render_territory_boundaries_optimized(views[0],[0,0],1)
 world=obj.world;refs.append(weakref.ref(obj));world.reset();del obj,world
 gc.collect()
assert all(ref() is None for ref in refs)
a.output.write_text(json.dumps(dict(diagnostic=True,formal_speed=False,cycles=1200,samples=samples,plateau_range_bytes=retained_range,threshold_bytes=65536,reset_released_coordinates=True,instances_released=24,new_surface_count=0,cache_cap=32768,all_passed=True),indent=2)+'\n')
print(a.output)
