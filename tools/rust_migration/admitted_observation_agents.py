"""E8-only audited Lab adapter; preserve the frozen per-request pump body.

AST insertion adds lifetime hooks, never replaces authorization or consumes a
queue prefix at once. All world operations still use the existing recorder.
"""
import ast
import hashlib
import inspect
import sys
import textwrap
import time
from pathlib import Path

LAB=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(LAB/'tools'))
import p3_local_agents as original
from native_loop_trace import NativeLoopTrace
from observation_admission_probe import FROZEN, ready_prefix


class AdmittedLoopTrace(NativeLoopTrace):
    query_scope = None
    def observation_json(self, session, params):
        if self.pending is not None:raise RuntimeError('observation payload was not recorded')
        wall=time.time()
        call=self.query_scope.get_faction_state_json if self.query_scope else self.runtime.get_faction_state_json
        result=call(**params,agent_id=session.agent_id,wall_time=wall)
        self.pending=self.append(kind='request',action='get_faction_state',parameters=params,
            agent_id=session.agent_id,wall_time=wall,registration_time=None,
            integer_string_limit=sys.get_int_max_str_digits(),response_wire_format='native-json')
        return result


def instrumented_pump():
    assert hashlib.sha256((LAB/'tools/p3_local_agents.py').read_bytes()).hexdigest()==FROZEN['tools/p3_local_agents.py']
    tree=ast.parse(textwrap.dedent(inspect.getsource(original.LocalAgents.pump)))
    class Hooks(ast.NodeTransformer):
        inserted = 0
        def visit_Assign(self,node):
            text=ast.unparse(node)
            if text.startswith('due, _, event, index = heapq.heappop'):
                self.inserted+=1
                return [ast.parse('self._before_dequeue()').body[0],node]
            if text.startswith("row['nominal_cycle_lag_ms'] ="):
                self.inserted+=1
                return [node,ast.parse('self._before_event((due, _, event, index), row, begin)').body[0]]
            if text.startswith("row['service_ms'] ="):
                self.inserted+=1
                return [ast.parse('self._after_consumption(row, begin)').body[0],node,
                        ast.parse("row['service_ms'] += row.get('admission_check_ms', 0.0)").body[0]]
            if text.startswith("row['response_ms'] ="):
                self.inserted+=1
                return [node,ast.parse("row['response_ms'] = row['actual_response_ms']").body[0]]
            return node
    hooks=Hooks();tree=hooks.visit(tree);assert hooks.inserted==4
    ast.fix_missing_locations(tree)
    namespace=dict(vars(original))
    exec(compile(tree,__file__,'exec'),namespace)
    return namespace['pump']


class AdmittedAgents(original.LocalAgents):
    research_mode='single'
    research_diagnostics=False
    _pump_body=instrumented_pump()

    def __init__(self,*args,**kwargs):
        if self.research_mode not in ('single','segment_no_reuse','segment_encoded'):
            raise ValueError('invalid admitted observation mode')
        super().__init__(*args,**kwargs)
        self._trace=getattr(self.observation_json_call,'__self__',None)
        if not isinstance(self._trace,AdmittedLoopTrace) or self.payload_callback.__self__ is not self._trace:
            raise ValueError('E8 requires the audited NativeLoopTrace wire/payload boundary')
        self._context=None;self._frozen=[];self._next=0;self._last_row=None
        self._check_ns=0;self.segment_records=[];self._segment_record=None

    def _close(self,reason,*,inside_current=False):
        if self._context is None:return
        began=time.perf_counter_ns()
        self._trace.query_scope=None
        context=self._context;self._context=None
        context.__exit__(*sys.exc_info())
        elapsed=(time.perf_counter_ns()-began)/1e6
        if not inside_current and self._last_row is not None:
            self._last_row['maintenance_ms']=self._last_row.get('maintenance_ms',0.)+elapsed
            self._last_row['service_ms']+=elapsed
        self._segment_record.update(close_reason=reason,drop_ms=elapsed,
                                    diagnostic=context.report)
        self.segment_records.append(self._segment_record)
        self._segment_record=None;self._frozen=[];self._next=0

    def _before_dequeue(self):
        began=time.perf_counter_ns()
        if self._context is not None and (self._next>=len(self._frozen) or self.heap[0]!=self._frozen[self._next]):
            self._close('changed_head')
            # Drop was allocated to the preceding query, not this head check.
            began=time.perf_counter_ns()
        self._check_ns=time.perf_counter_ns()-began

    def _before_event(self,entry,row,begin):
        row['admission_check_ms']=self._check_ns/1e6
        if entry[2]=='observe' and self._context is None:
            prefix,reason=ready_prefix(self.heap,begin,3)
            frozen=[entry,*prefix]
            if len(frozen)>=2:
                context=self._trace.runtime._admitted_observation_segment(
                    self.research_mode,diagnostics=self.research_diagnostics)
                scope=context.__enter__()
                self._context=context;self._trace.query_scope=scope
                self._frozen=frozen;self._next=0
                self._segment_record=dict(frozen=[list(e) for e in frozen],
                                          cutoff=begin,prefix_barrier=reason,executed=[])
        if self._context is not None:
            assert entry==self._frozen[self._next]
            self._next+=1;self._segment_record['executed'].append(entry[1])

    def _after_consumption(self,row,begin):
        # Actual client completion is distinct from maintenance attribution.
        row['actual_response_ms']=row['queue_ms']+(self.clock()-begin)*1000
        if row['event']=='observe':self._last_row=row
        if self._context is not None and self._next==len(self._frozen):
            self._close('frozen_end',inside_current=True)

    def pump(self,budget_ms=4.0):
        if self.research_mode=='single':return super().pump(budget_ms)
        try:return self._pump_body(budget_ms)
        finally:self._close('budget_or_pump_end')
