"""出生点选择：危险度、队友距离、冷却与轮转惩罚。

评分: score = -threat * 10 + nearby_allies * 5 - rotation_penalty * picks。
队友距离用 ally_radius 网格的 9 个邻接格子查询，并按点缓存，choose 不再
按点数乘队友数扫描；候选点用最小堆按 (分数, id) 排序，配合版本号懒删除
冷却/过期条目，单次选择摊还 O(log 点数 + 本次触及的冷却条目)。
"""

import heapq
import math


class Spawner:
    """出生点评分与轮转。"""

    def __init__(self, ally_radius, cooldown_ms, rotation_penalty=3):
        self.ally_radius = ally_radius
        self.cooldown_ms = cooldown_ms
        self.rotation_penalty = rotation_penalty
        self.points = {}
        self.allies = []
        self.scanned = 0
        self._grid = None
        self._heap = None
        self._dirty = False
        self._ally_version = 0

    def add_point(self, pid, x, y, threat=0):
        self.points[pid] = {"id": pid, "x": x, "y": y, "threat": threat,
                            "picks": 0, "last_used": None, "ver": 0}
        self._dirty = True

    def set_threat(self, pid, threat):
        if pid in self.points:
            point = self.points[pid]
            point["threat"] = threat
            point["ver"] += 1
            self._dirty = True

    def add_ally(self, x, y):
        self.allies.append((x, y))
        self._grid = None
        self._ally_version += 1
        self._dirty = True

    def _build_grid(self):
        self._grid = {}
        radius = self.ally_radius
        if radius > 0:
            for ax, ay in self.allies:
                key = (math.floor(ax / radius), math.floor(ay / radius))
                self._grid.setdefault(key, []).append((ax, ay))
        else:
            for ax, ay in self.allies:
                self._grid.setdefault((ax, ay), []).append((ax, ay))

    def _ally_count(self, point):
        cached = point.get("ally_cache")
        if cached is not None and cached[0] == self._ally_version:
            return cached[1]
        if self._grid is None:
            self._build_grid()
        radius = self.ally_radius
        px, py = point["x"], point["y"]
        count = 0
        if radius > 0:
            r2 = radius * radius
            cx = math.floor(px / radius)
            cy = math.floor(py / radius)
            for gx in (cx - 1, cx, cx + 1):
                for gy in (cy - 1, cy, gy + 1 if False else cy + 1):
                    for ax, ay in self._grid.get((gx, gy), ()):
                        self.scanned += 1
                        dx = ax - px
                        dy = ay - py
                        if dx * dx + dy * dy <= r2:
                            count += 1
        else:
            for ax, ay in self._grid.get((px, py), ()):
                self.scanned += 1
                if ax == px and ay == py:
                    count += 1
        point["ally_cache"] = (self._ally_version, count)
        return count

    def nearby_allies(self, pid):
        """出生点附近（含边界）的队友数量。"""
        point = self.points.get(pid)
        if point is None:
            return 0
        return self._ally_count(point)

    def _score(self, point):
        return (-point["threat"] * 10
                + self._ally_count(point) * 5
                - self.rotation_penalty * point["picks"])

    def _cooling(self, point, now_ms):
        last = point["last_used"]
        return last is not None and now_ms - last < self.cooldown_ms

    def _build_heap(self):
        heap = []
        for pid, point in self.points.items():
            heapq.heappush(heap, (-self._score(point), pid, point["ver"]))
        self._heap = heap
        self._dirty = False

    def choose(self, now_ms):
        """挑一个出生点，全部不可用时返回 None。"""
        if not self.points:
            return None
        if self._dirty or self._heap is None:
            self._build_heap()
        deferred = []
        chosen = None
        while self._heap:
            neg_score, pid, ver = heapq.heappop(self._heap)
            point = self.points.get(pid)
            if point is None or point["ver"] != ver:
                continue
            if self._cooling(point, now_ms):
                deferred.append((neg_score, pid, ver))
                continue
            chosen = pid
            break
        for entry in deferred:
            heapq.heappush(self._heap, entry)
        if chosen is None:
            return None
        point = self.points[chosen]
        point["last_used"] = now_ms
        point["picks"] += 1
        point["ver"] += 1
        heapq.heappush(self._heap,
                       (-self._score(point), chosen, point["ver"]))
        return chosen

    def picks(self, pid):
        if pid in self.points:
            return self.points[pid]["picks"]
        return 0

    def scanned_count(self):
        return self.scanned
