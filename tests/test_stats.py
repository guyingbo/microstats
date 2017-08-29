import time
import microstats
lst = [7, 4, 8, 6, 3.6, 8, 3, 3, 5, 2, 23, 9, 20, 7, 28, 22, 22, 6, 7, 7]


def test_gauge_value():
    g = microstats.GaugeValue()
    assert g.val == 0
    g.set(20)
    g.set(25)
    g.set(10)
    assert g.val == 10
    assert g.val_max == 25
    assert g.val_min == 10
    g.add(-5)
    g.add(3)
    assert g.val == 8
    assert g.val_max == 25
    assert g.val_min == 5
    g.add(6)
    g.reset()
    assert g.val == g.val_max == g.val_min == 14


def test_get_stats():
    l = [0]
    d = microstats.get_stats(l)
    assert d == {'sum': 0, 'avg': 0, 'max_p95': 0, 'min_p95': 0}
    assert len(lst) == 20
    d = microstats.get_stats(lst)
    assert d['sum'] == 200.6
    assert d['avg'] == 10.03
    assert d['max_p95'] == 23
    assert d['min_p95'] == 3


def test_micro_stats():
    stats = microstats.MicroStats()
    stats.flush()
    stats.incr('Requests', 50)
    stats.incr('Requests', 10)
    stats.gauge('ConcurrentRequest', 36)
    stats.gauge('ConcurrentRequest', 21)
    stats.gauge('ConcurrentRequest', 15)
    stats.gauge('ConcurrentRequest', 41)
    with stats.timer('Latency'):
        time.sleep(0.008)
    with stats.timer('Latency'):
        time.sleep(0.006)
    for val in lst:
        stats.scatter('goods', val)
    stats.unique('User', 'a')
    stats.unique('User', 'b')
    stats.unique('User', 'c')
    stats.unique('User', 'b')
    stats.before_flush('ConcurrentRequest', lambda: 60)
    data = stats.flush()
    print(data)
    assert data['Requests'] == 60
    assert data['ConcurrentRequest'] == 60
    assert data['ConcurrentRequest_max'] == 60
    assert data['ConcurrentRequest_min'] == 15
    assert data['goods_sum'] == 200.6
    assert data['goods_avg'] == 10.03
    assert data['goods_max_p95'] == 23
    assert data['goods_min_p95'] == 3
    assert data['User'] == 3
    data = stats.flush()
    assert data['ConcurrentRequest'] == 60
    assert data['ConcurrentRequest_max'] == 60
    assert data['ConcurrentRequest_min'] == 60
    assert data['Requests'] == 0
    assert data['User'] == 0
