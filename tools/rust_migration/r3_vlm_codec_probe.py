"""Isolate the inherited TGA capture from world state and native computation."""
import argparse,base64,hashlib,io,json,os,sys
from pathlib import Path
from r3_observations_probe import git


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    src=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);os.chdir(src);sys.path.insert(0,str(src))
    import pygame
    from framework.engine.renders import RenderEngine
    from rotk_env.systems.llm_action_handler import LLMActionHandler
    surface=pygame.Surface((3,1),pygame.SRCALPHA)
    colors=[(200,80,30,128),(10,20,30,0),(20,90,140,255)]
    for x,color in enumerate(colors):surface.set_at((x,0),color)
    RenderEngine().screen=surface
    frame,error=LLMActionHandler._capture_frame_base64(None);assert error is None
    raw=base64.b64decode(frame);decoded=pygame.image.load(io.BytesIO(raw),'frame.tga')
    actual=[list(decoded.get_at((x,0))) for x in range(3)]
    expected=[[100,40,15,128],[0,0,0,0],[20,90,140,255]]
    assert actual==expected,actual
    # A raw RLE packet from the encoded file gives evidence independent of a decoder.
    assert raw[2]==10 and raw[16]==32
    stored=[];cursor=18+raw[0]
    while len(stored)<3:
        packet=raw[cursor];cursor+=1;count=(packet&127)+1
        if packet&128:
            stored.extend([list(raw[cursor:cursor+4])]*count);cursor+=4
        else:
            stored.extend(list(raw[cursor+i*4:cursor+(i+1)*4]) for i in range(count));cursor+=count*4
    assert stored==[[15,40,100,128],[0,0,0,0],[140,90,20,255]],stored
    (out/'frame.tga').write_bytes(raw);pygame.image.save(surface,out/'surface.png');pygame.image.save(decoded,out/'decoded.png')
    result=dict(source_sha=git(src,'rev-parse','HEAD'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),source_dirty=git(src,'status','--porcelain'),input_rgba=colors,decoded_rgba=actual,stored_bgra=stored,bytes_sha256=hashlib.sha256(raw).hexdigest(),all_guards_passed=True,legacy_behavior=True,pygame=pygame.version.ver,actual_encoding='TGA',native_runtime_used=False)
    assert not result['source_dirty'];(out/'compact.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
