"""E7 independent diagnostic scopes; wrappers never select rendering policy."""
from collections import Counter, defaultdict
from contextlib import contextmanager
from functools import wraps
import inspect
import time


class DisplayDiagnosis:
    def __init__(self, session):
        from framework.ecs import profiling
        from framework.engine import RMS
        from framework.engine.renders import BlitCommand, DrawCommand
        import pygame
        self.session = session
        self.rows = defaultdict(lambda: [0, 0, 0])
        self.counts = Counter()
        self.frames = []
        self.originals = []
        self.stack = []
        self.active = False
        self.started = None
        self.frame_counts = Counter()
        self.metric_snapshot = {}
        self.cache_snapshots = []

        def wrap(obj, name, key):
            original = getattr(obj, name)
            @wraps(original)
            def measured(*args, **kwargs):
                if not self.active:
                    return original(*args, **kwargs)
                with self.scope(key):
                    result = original(*args, **kwargs)
                self.counts[key] += 1
                self.frame_counts[key] += 1
                if name == '_get_visible_units':
                    self.counts['units.visible'] += len(result)
                elif name == '_get_fast_animation_screen_position':
                    self.counts['units.animated' if result is not None else 'units.static_candidate'] += 1
                elif name == '_render_unit_group_optimized':
                    self.counts['units.group_members'] += len(args[1])
                return result
            setattr(obj, name, measured)
            self.originals.append((obj, name, original))

        for system in session.world.systems:
            name = type(system).__name__
            for method, bound in inspect.getmembers(system, inspect.ismethod):
                if method == 'update' or method.startswith((
                    '_render', '_draw', '_build', '_patch', '_prepare', '_ensure',
                    '_get_visible', '_get_fast_animation', '_update_fog', '_update_overscan',
                    '_current_faction', '_get_font', '_get_terrain',
                )):
                    wrap(system, method, 'method.' + name + '.' + method)
        for name in ('draw', '_add_command', 'clear', 'clear_layer'):
            wrap(RMS, name, 'rms.' + name)
        for cls in (BlitCommand, DrawCommand):
            wrap(cls, '__init__', 'construct.' + cls.__name__)
        for name in ('rect', 'circle', 'polygon', 'line', 'lines', 'ellipse', 'arc'):
            wrap(pygame.draw, name, 'sdl.draw.' + name)
        for name in ('scale', 'smoothscale', 'rotate', 'rotozoom'):
            wrap(pygame.transform, name, 'sdl.transform.' + name)
        original_timer = profiling.profiler.time_system
        @contextmanager
        def timer(name, *args, **kwargs):
            if not self.active:
                with original_timer(name, *args, **kwargs) as result:
                    yield result
                return
            with self.scope('profile.' + name):
                with original_timer(name, *args, **kwargs) as result:
                    yield result
        profiling.profiler.time_system = timer
        self.originals.append((profiling.profiler, 'time_system', original_timer))
        original_metric = profiling.profiler.set_frame_metric
        def metric(name, value):
            if self.active:
                self.metric_snapshot[name] = value
            return original_metric(name, value)
        profiling.profiler.set_frame_metric = metric
        self.originals.append((profiling.profiler, 'set_frame_metric', original_metric))

    @contextmanager
    def scope(self, key):
        start = time.perf_counter_ns()
        entry = [key, 0]
        self.stack.append(entry)
        try:
            yield
        finally:
            elapsed = time.perf_counter_ns() - start
            assert self.stack.pop() is entry
            row = self.rows[key]
            row[0] += 1
            row[1] += elapsed
            row[2] += elapsed - entry[1]
            if self.stack:
                self.stack[-1][1] += elapsed

    def begin_tick(self, tick):
        assert not self.active and not self.stack
        self.frame_counts.clear()
        self.metric_snapshot.clear()
        self.active = True
        self.started = time.perf_counter_ns()

    def end_tick(self, tick):
        elapsed = time.perf_counter_ns() - self.started
        assert not self.stack
        self.active = False
        self.frames.append(dict(tick=tick,display_wall_ns=elapsed,
                                calls=dict(self.frame_counts),metrics=dict(self.metric_snapshot)))
        if tick % 500 == 0 or tick == 9880:
            self.cache_snapshots.append(self.cache_state(tick))

    def cache_state(self, tick):
        import pygame
        systems = {}
        for system in self.session.world.systems:
            values = {}
            for key, value in vars(system).items():
                if isinstance(value, (dict, list, set)) and any(
                    word in key for word in ('cache', 'overscan', 'pending', 'dirty', 'roster')
                ):
                    values[key] = dict(kind=type(value).__name__,items=len(value))
                elif isinstance(value, pygame.Surface):
                    values[key] = dict(kind='Surface',size=list(value.get_size()),
                                       bytes=value.get_pitch()*value.get_height())
            systems[type(system).__name__] = values
        return dict(tick=tick,systems=systems)

    def finish(self):
        assert not self.stack
        self.active = False
        for obj, name, original in reversed(self.originals):
            setattr(obj, name, original)
        self.originals.clear()
        return dict(scopes={key:dict(calls=v[0],inclusive_ns=v[1],self_ns=v[2])
                            for key,v in sorted(self.rows.items())},
                    counts=dict(self.counts),frames=self.frames,caches=self.cache_snapshots,
                    diagnostic_only=True,probe_overhead_included=True,
                    semantic='self scopes exclude timed children; enqueue belongs to display, not RMS submission')
