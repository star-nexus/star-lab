"""E6 960 real Cocoa frames per mode, selected/plain, RT/TB, melee/ranged.

Reuse the independent R3 integration script; freeze gameplay wall dates, retain
actual pacing/perf clocks. Hash every displayed RGB frame, not just screenshots.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import time


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=['baseline','reuse_constructed','reuse_typed'],required=True);p.add_argument('--selection',action='store_true');a=p.parse_args()
    src=a.source.resolve();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
    os.chdir(src);sys.path.insert(0,str(src));os.environ.update(HEADLESS='0',SDL_VIDEODRIVER='cocoa',PYGAME_HIDE_SUPPORT_PROMPT='1')
    import pygame
    from rotk_env.runtime.world_presentation import WorldPresentation
    import r3_window_presentation_probe as legacy
    ordinary=WorldPresentation.apply
    if a.mode!='baseline':WorldPresentation.apply=lambda self,d:self._apply_research(d,mode=a.mode)
    old_time=time.time;time.time=lambda:1720000000.
    original_date=datetime.datetime
    class Frozen(original_date):
        @classmethod
        def now(cls,tz=None):return cls(2026,9,12,12)
    datetime.datetime=Frozen
    hashes=[];flip=pygame.display.flip
    def displayed():
        hashes.append(hashlib.sha256(pygame.image.tobytes(pygame.display.get_surface(),'RGB')).hexdigest());flip()
    pygame.display.flip=displayed
    sys.argv=[str(Path(legacy.__file__)), '--source',str(src),'--output',str(out),'--driver','cocoa']+(['--selection'] if a.selection else [])
    try:legacy.main()
    finally:
        WorldPresentation.apply=ordinary;datetime.datetime=original_date;time.time=old_time;pygame.display.flip=flip
    assert len(hashes)==480
    data=gzip.compress(json.dumps(hashes,separators=(',',':')).encode(),mtime=0);(out/'pixels.json.gz').write_bytes(data)
    result=dict(mode=a.mode,selection=a.selection,frames=len(hashes),all_passed=True,driver='cocoa',
        pixel_sha256=hashlib.sha256(data).hexdigest(),pixel_stream_sha256=hashlib.sha256(''.join(hashes).encode()).hexdigest(),
        legacy_tool_sha256=hashlib.sha256(Path(legacy.__file__).read_bytes()).hexdigest(),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),capacity_claim=False)
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
