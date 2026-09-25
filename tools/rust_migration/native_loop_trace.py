"""Bounded native input recorder; payload hashing reuses the existing client wire."""
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import time


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def artifact(path,value):
    body=json.dumps(value,separators=(',',':'),allow_nan=False).encode()
    path.write_bytes(gzip.compress(body,mtime=0))
    return dict(file=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())


class NativeLoopTrace:
    def __init__(self,runtime,output,source,extension,threads):
        self.runtime=runtime;self.output=Path(output);self.source=source;self.extension=extension;self.threads=threads
        self.entries=[];self.pending=None
        self.initial=artifact(self.output.with_suffix('.initial.json.gz'),runtime.export_state())
        original_step=runtime.step
        def step(dt,*,wall_time=None):
            wall=time.time() if wall_time is None else wall_time
            result=original_step(dt,wall_time=wall)
            self.append(kind='step',dt=dt,wall_time=wall)
            return result
        runtime.step=step
        original_delta=runtime.take_presentation_delta
        def delta(*,expected_epoch=None):
            result=original_delta(expected_epoch=expected_epoch)
            self.append(kind='presentation',events_sha256=digest(result['events']))
            return result
        runtime.take_presentation_delta=delta

    def append(self,**op):
        if len(self.entries)>=200000:raise RuntimeError('native input recorder overflow')
        op['seq']=len(self.entries);self.entries.append(op)
        return op

    def call(self,session,verb,params):
        if self.pending is not None:raise RuntimeError('observation payload was not recorded')
        wall=time.time();registration=datetime.datetime.now().isoformat() if verb=='register_agent_info' else None
        result=self.runtime.execute_action(verb,params,agent_id=session.agent_id,wall_time=wall,registration_time=registration)
        op=self.append(kind='request',action=verb,parameters=params,agent_id=session.agent_id,wall_time=wall,registration_time=registration)
        if verb=='get_faction_state':self.pending=op
        else:op['response_sha256']=digest(result)
        return result

    def payload(self,payload):
        if self.pending is None:raise RuntimeError('unexpected observation payload')
        self.pending['response_wire_sha256']=hashlib.sha256(payload).hexdigest();self.pending=None

    def finish(self):
        if self.pending is not None:raise RuntimeError('unfinished observation capture')
        raw=dict(schema='star-rendered-native-inputs-v1',source=self.source,extension=self.extension,threads=self.threads,
                 initial=self.initial,entries=self.entries,final_state_sha256=digest(self.runtime.export_state()))
        saved=artifact(self.output.with_suffix('.trace.json.gz'),raw)
        return dict(trace=saved,initial=self.initial,operations=len(self.entries),final_state_sha256=raw['final_state_sha256'])
