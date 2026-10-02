"""Diagnostic/correctness-only normalization of ordered software draw commands."""
import hashlib
import inspect
import json


def fingerprint(renderer):
    import pygame
    from framework.engine.renders import BlitCommand, DrawCommand
    surfaces = {}
    def value(item):
        if isinstance(item, pygame.Surface):
            identity = id(item)
            if identity not in surfaces:
                surfaces[identity] = dict(surface=list(item.get_size()),
                    rgba=hashlib.sha256(pygame.image.tobytes(item, 'RGBA')).hexdigest(),
                    alpha=item.get_alpha(),colorkey=value(item.get_colorkey()),flags=item.get_flags())
            return surfaces[identity]
        if isinstance(item, (pygame.Rect, pygame.Color)):
            return list(item)
        if isinstance(item, (tuple, list)):
            return [value(child) for child in item]
        if isinstance(item, dict):
            return {key:value(child) for key,child in item.items()}
        if callable(item):
            fn = inspect.unwrap(item)
            return [getattr(fn,'__module__',''),getattr(fn,'__qualname__',type(fn).__name__)]
        if item is None or isinstance(item, (bool, int, float, str)):
            return item
        raise TypeError(('Unsupported research draw argument', type(item).__name__))
    layers = []
    for layer in sorted(renderer._render_queue):
        commands = []
        for command in renderer._render_queue[layer]:
            if isinstance(command, BlitCommand):
                commands.append(['blit',value(command.surface),value(command.dest),
                                 value(command.area),command.special_flags])
            elif isinstance(command, DrawCommand):
                commands.append(['draw',value(command.draw_func),value(command.args),value(command.kwargs)])
            else:
                raise TypeError(('Unsupported research command',type(command).__name__))
        layers.append([layer,commands])
    return hashlib.sha256(json.dumps(layers,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
