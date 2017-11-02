import math
import time
from collections import defaultdict
from contextlib import contextmanager
__version__ = '0.1.2'


class GaugeValue:
    def __init__(self):
        self.val = 0
        self.val_min = float('inf')
        self.val_max = float('-inf')

    def add(self, val):
        new_val = self.val + val
        self.set(new_val)

    def set(self, val):
        self.val_min = min(val, self.val_min)
        self.val_max = max(val, self.val_max)
        self.val = val

    def reset(self):
        self.val_max = self.val_min = self.val


def get_stats(lst):
    if not lst:
        return {}
    lst.sort()
    total = sum(lst)
    length = len(lst)
    avg = total / length
    p95 = int(math.ceil(length * 95.0 / 100)) - 1
    p5 = length - p95 - 1
    return {
        'sum': total,
        'avg': avg,
        'max_p95': lst[p95],
        'min_p95': lst[p5],
        'max': lst[-1],
        'min': lst[0],
    }


class MicroStats:
    def __init__(self, default=None):
        self.default = default or {}
        self.metrics = {}
        self.functions = {}

    def incr(self, stat, count=1, rate=1):
        if stat not in self.metrics:
            self.metrics[stat] = 0
        self.metrics[stat] += count / rate

    def decr(self, stat, count=1, rate=1):
        if stat not in self.metrics:
            self.metrics[stat] = 0
        self.metrics[stat] -= count / rate

    def gauge(self, stat, value, delta=False):
        if stat not in self.metrics:
            self.metrics[stat] = GaugeValue()
        if delta:
            self.metrics[stat].add(value)
        else:
            self.metrics[stat].set(value)

    def scatter(self, stat, val):
        if stat not in self.metrics:
            self.metrics[stat] = []
        self.metrics[stat].append(val)

    def timing(self, stat, delta):
        return self.scatter(stat, delta)

    @contextmanager
    def timer(self, stat):
        start = time.time()
        yield
        end = time.time()
        self.timing(stat, int((end-start) * 1000))

    def unique(self, stat, value):
        if stat not in self.metrics:
            self.metrics[stat] = set()
        self.metrics[stat].add(value)

    def before_flush(self, stat, func):
        self.functions[stat] = func

    def _flush(self):
        result = {}
        for stat, func in self.functions.items():
            self.gauge(stat, func())
        for k, v in self.metrics.items():
            if isinstance(v, GaugeValue):
                result[k] = v.val
                result['%s_max' % k] = v.val_max
                result['%s_min' % k] = v.val_min
                v.reset()
            elif isinstance(v, (int, float)):
                result[k] = v
                self.metrics[k] = 0
            elif isinstance(v, set):
                result[k] = len(v)
                v.clear()
            elif isinstance(v, list):
                for postfix, val in get_stats(v).items():
                    result['%s_%s' % (k, postfix)] = val
                # for python2
                del v[:]
                # for python3
                # v.clear()
        return result

    def flush(self):
        data = self._flush()
        data.update(self.default)
        return data


class StatsGroup:
    def __init__(self, factory=lambda: MicroStats()):
        self.stats = defaultdict(factory)

    def __getattr__(self, name):
        return self.stats[name]

    def flush(self):
        return {k: v.flush() for k, v in self.stats.items()}
