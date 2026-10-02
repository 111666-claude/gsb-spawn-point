"""出生点选择：危险度、队友距离、冷却与轮转惩罚。

评分 score = -threat * 10 + nearby_allies * 5 - rotation_penalty * picks，
取最高分，同分按点 id 字典序升序。choose 通过懒删除堆取最优候选，
队友计数用空间网格维护，不按点数乘队友数扫描。
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
        self._heap = []
        self._cell = ally_radius if ally_radius > 0 else 1.0
        self._ally_grid = {}
        self._point_grid = {}

    def _score(self, point):
        return (-point["threat"] * 10 + point["allies"] * 5
                - self.rotation_penalty * point["picks"])

    def _push(self, pid):
        point = self.points[pid]
        point["version"] += 1
        heapq.heappush(self._heap, (-self._score(point), pid, point["version"]))

    def _cells_around(self, x, y):
        cell_x = math.floor(x / self._cell)
        cell_y = math.floor(y / self._cell)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                yield (cell_x + dx, cell_y + dy)

    def _grid_add(self, grid, key, x, y):
        cell = (math.floor(x / self._cell), math.floor(y / self._cell))
        grid.setdefault(cell, []).append(key)
        return cell

    def _count_allies(self, x, y):
        count = 0
        for cell in self._cells_around(x, y):
            for ax, ay in self._ally_grid.get(cell, ()):
                if math.hypot(ax - x, ay - y) <= self.ally_radius:
                    count += 1
        return count

    def add_point(self, pid, x, y, threat=0):
        old = self.points.get(pid)
        if old is not None and old["cell"] in self._point_grid:
            self._point_grid[old["cell"]].remove(pid)
        point = {"id": pid, "x": x, "y": y, "threat": threat,
                 "picks": 0, "last_used": None, "allies": 0, "version": 0,
                 "cell": None}
        point["allies"] = self._count_allies(x, y)
        point["cell"] = self._grid_add(self._point_grid, pid, x, y)
        self.points[pid] = point
        self._push(pid)

    def set_threat(self, pid, threat):
        if pid in self.points:
            self.points[pid]["threat"] = threat
            self._push(pid)

    def add_ally(self, x, y):
        self.allies.append((x, y))
        self._grid_add(self._ally_grid, (x, y), x, y)
        for cell in self._cells_around(x, y):
            for pid in self._point_grid.get(cell, ()):
                point = self.points[pid]
                if math.hypot(x - point["x"], y - point["y"]) <= self.ally_radius:
                    point["allies"] += 1
                    self._push(pid)

    def nearby_allies(self, pid):
        """出生点附近（含边界）的队友数量。"""
        point = self.points.get(pid)
        if point is None:
            return 0
        return point["allies"]

    def _in_cooldown(self, point, now_ms):
        last = point["last_used"]
        return last is not None and now_ms - last < self.cooldown_ms

    def choose(self, now_ms):
        """挑一个出生点，全部不可用时返回 None。"""
        held = []
        best = None
        while self._heap:
            neg_score, pid, version = heapq.heappop(self._heap)
            self.scanned += 1
            point = self.points[pid]
            if version != point["version"]:
                continue
            if self._in_cooldown(point, now_ms):
                held.append((neg_score, pid, version))
                continue
            best = pid
            break
        for entry in held:
            heapq.heappush(self._heap, entry)
        if best is None:
            return None
        point = self.points[best]
        point["last_used"] = now_ms
        point["picks"] += 1
        self._push(best)
        return best

    def picks(self, pid):
        if pid in self.points:
            return self.points[pid]["picks"]
        return 0

    def scanned_count(self):
        return self.scanned
