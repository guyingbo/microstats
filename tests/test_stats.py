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
    list1 = [0]
    d = microstats.get_stats(list1)
    assert d == {
        "sum": 0,
        "avg": 0,
        # 'max_p95': 0,
        # 'min_p95': 0,
        "max": 0,
        "min": 0,
        "cnt": 1,
    }
    assert len(lst) == 20
    d = microstats.get_stats(lst)
    assert d["sum"] == 200.6
    assert d["avg"] == 10.03
    # assert d['max_p95'] == 23
    # assert d['min_p95'] == 3
    assert d["max"] == 28
    assert d["min"] == 2


def test_micro_stats():
    stats = microstats.MicroStats()
    stats.flush()
    stats.incr("Requests", 50)
    stats.incr("Requests", 10)
    stats.decr("Price", 10)
    stats.gauge("ConcurrentRequest", 36)
    stats.gauge("ConcurrentRequest", 21)
    stats.gauge("ConcurrentRequest", 15)
    stats.gauge("ConcurrentRequest", 41)
    stats.gauge("ConcurrentRequest", 10, delta=True)
    with stats.timer("Latency"):
        time.sleep(0.008)
    with stats.timer("Latency"):
        time.sleep(0.006)
    for val in lst:
        stats.scatter("goods", val)
    stats.unique("User", "a")
    stats.unique("User", "b")
    stats.unique("User", "c")
    stats.unique("User", "b")
    stats.before_flush("ConcurrentRequest", lambda: 60)
    data = stats.flush()
    print(data)
    assert data["Requests"] == 60
    assert data["Price"] == -10
    assert data["ConcurrentRequest"] == 60
    assert data["ConcurrentRequest_max"] == 60
    assert data["ConcurrentRequest_min"] == 15
    assert data["goods_sum"] == 200.6
    assert data["goods_avg"] == 10.03
    # assert data['goods_max_p95'] == 23
    # assert data['goods_min_p95'] == 3
    assert data["User"] == 3
    data = stats.flush()
    assert data["ConcurrentRequest"] == 60
    assert data["ConcurrentRequest_max"] == 60
    assert data["ConcurrentRequest_min"] == 60
    assert data["Requests"] == 0
    assert data["User"] == 0


def test_stats_group():
    group = microstats.StatsGroup()
    group.group1.incr("Click")
    group.group2.incr("Conversion", 5)
    data = group.flush()
    assert data["group1"]["Click"] == 1
    assert data["group2"]["Conversion"] == 5
