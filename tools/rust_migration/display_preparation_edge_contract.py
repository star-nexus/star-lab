"""E7 live ownership/style, errors, viewport and membership transition contracts."""
import argparse,hashlib,json,os,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--driver',default='dummy',choices=['dummy','cocoa']);a=p.parse_args();sys.path.insert(0,str(a.source));os.environ['SDL_VIDEODRIVER']=a.driver
import pygame
from framework.ecs.world import World
from framework.engine import RMS
from framework.engine.game_engine import GameEngine
from rotk_env.components import MapData,TerritoryControl
from rotk_env.prefabs.config import Faction
from rotk_env.systems.window_map_render_system import WindowMapRenderSystem
from display_preparation_contract import fingerprint
engine=GameEngine(title='E7 territory edge contracts',width=320,height=200,fps=30)
w=World();r=WindowMapRenderSystem();r.world=w;w.systems.append(r);ids=[w.create_entity() for _ in range(3)];data=MapData(width=2,height=2,tiles={(0,0):ids[0],(1,0):ids[1],(0,1):ids[2]});w.add_singleton_component(data)
rows=[]
def check(name,cells={(0,0),(1,0),(0,1)},offset=(100,100),zoom=1):
 outcomes=[]
 for mode in ('baseline','empty_territory'):
  RMS.clear();RMS.screen.fill((0,0,0));error=None
  try:
   with r._display_research_frame(mode):r._render_territory_boundaries_optimized(cells,offset,zoom)
  except Exception as e:error=(type(e).__name__,str(e))
  commands=fingerprint(RMS);RMS.update();pixels=hashlib.sha256(pygame.image.tobytes(RMS.screen,'RGB')).hexdigest()
  outcomes.append((error,commands,pixels))
 assert outcomes[0]==outcomes[1],(name,outcomes)
 rows.append(dict(case=name,error=outcomes[0][0],command_sha256=outcomes[0][1],pixel_sha256=outcomes[0][2]))
check('empty')
control=TerritoryControl(controlling_faction=Faction.WEI);w.add_component(ids[0],control)
for faction in (Faction.WEI,Faction.SHU,Faction.WU,None):
 for progress,level in ((0,0),(.3,1),(.8,2),(1,3)):
  control.controlling_faction=faction;control.capture_progress=progress;control.fortification_level=level
  check(f'live_style_{faction}_{progress}_{level}')
control.controlling_faction=Faction.WEI;control.capture_progress='bad';check('error_prefix')
w.remove_component(ids[0],TerritoryControl);check('remove')
w.add_component(ids[1],TerritoryControl(controlling_faction=Faction.SHU));check('other_tile')
w.add_component(ids[1],TerritoryControl(controlling_faction=Faction.WU,capture_progress=.9));check('replacement')
w.destroy_entity(ids[1]);check('destroy')
data.tiles[(0,0)]=None;check('mutable_map_none');data.tiles[(0,0)]=0;check('mutable_map_zero');data.tiles[(0,0)]='unknown';check('unknown_id')
check('bad_coordinate',cells={(0,0,1)})
for size in ((640,360),(320,200),(800,450)):
 RMS.screen=pygame.display.set_mode(size)
 check('resize_'+str(size),zoom=.75,offset=(50,50))
w.reset();assert '_e7_valid_coordinates' not in r.__dict__;check('reset_no_map')
a.output.write_text(json.dumps(dict(driver=pygame.display.get_driver(),cases=rows,all_passed=True,formal_speed=False,source='67308329c3096119d65870d400bf4624f74803df'),indent=2)+'\n');pygame.quit();print(a.output)
