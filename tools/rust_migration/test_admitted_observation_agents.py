"""Queue/consumer/RNG contracts for E8's actual hook adapter."""
import json
from admitted_observation_agents import AdmittedAgents
from test_observation_admission_probe import make, original


class Scope:
    report=None
    def __init__(self, runtime):self.runtime=runtime
    def __enter__(self):self.runtime.opens+=1;return self
    def __exit__(self,*exc):self.runtime.closes+=1


class Runtime:
    opens=0;closes=0
    def _admitted_observation_segment(self,*a,**kw):return Scope(self)


class Trace:
    query_scope=None
    def __init__(self):self.runtime=Runtime()


def candidate():
    a=make(AdmittedAgents)
    a.research_mode='segment_encoded';a.research_diagnostics=False
    a._trace=Trace();a._context=None;a._frozen=[];a._next=0;a._last_row=None
    a._check_ns=0;a.segment_records=[];a._segment_record=None
    return a


def semantic_records(a):
    timing={'service_ms','response_ms','actual_response_ms','maintenance_ms','admission_check_ms'}
    return [{k:v for k,v in r.items() if k not in timing} for r in a.records]


def compare(base, candidate):
    assert semantic_records(base)==semantic_records(candidate)
    assert base.heap==candidate.heap and base.request_id==candidate.request_id
    assert base.counts==candidate.counts and base.sessions==candidate.sessions
    assert base.rng.getstate()==candidate.rng.getstate()
    assert [x.getstate() for x in base.delay_rngs]==[x.getstate() for x in candidate.delay_rngs]
    assert candidate._trace.runtime.opens==candidate._trace.runtime.closes
    assert candidate._context is None and candidate._trace.query_scope is None


def main():
    base,a=make(original.LocalAgents),candidate()
    base.pump(8);a.pump(8);compare(base,a)
    assert a.segment_records[0]['executed']==[1,2,3,4]
    for inserted in (False,True):
        base,a=make(original.LocalAgents),candidate()
        for controller in (base,a):
            now=[10.]
            controller.clock=lambda _now=now:_now[0]
            call=controller.observation_json_call
            def tick(*args,_call=call,_now=now):
                result=_call(*args);_now[0]+=.005;return result
            controller.observation_json_call=tick
            if inserted:
                consume=controller._consume_observation
                def push(*args,_a=controller,_consume=consume):
                    _consume(*args)
                    if _a.counts['observations']==1:_a._push(5.5,'act',0)
                controller._consume_observation=push
        base.pump(8);a.pump(8);compare(base,a)
        if inserted:assert a.segment_records[0]['executed']==[1]
        else:
            assert a.segment_records[0]['executed']==[1,2]
            assert a.heap[0]==(7.,3,'observe',2), 'Untouched original suffix'
    # Actual callback exceptions close the active context without retrying.
    a=candidate()
    def failure(*args):raise ValueError('client failed')
    a.payload_callback=failure
    try:a.pump(8)
    except ValueError:pass
    else:raise AssertionError('missing client exception')
    assert a.request_id==1 and len(a.heap)==3
    assert a._trace.runtime.opens==a._trace.runtime.closes==1
    print('PASS: unchanged request/consume/queue/RNG; frozen end; budget suffix; changed head; callback failure cleanup')


if __name__=='__main__':main()
