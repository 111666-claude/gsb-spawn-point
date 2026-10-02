"""出生点选择：危险度、队友距离、冷却与轮转惩罚。

缺陷：危险度算成加分、队友边界用严格小于、冷却不生效、没有轮转惩罚、
每次选择都按点数乘队友数扫描。
"""

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

    def add_point(self, pid, x, y, threat=0):
        self.points[pid] = {"id": pid, "x": x, "y": y, "threat": threat,
                            "picks": 0, "last_used": None}

    def set_threat(self, pid, threat):
        if pid in self.points:
            self.points[pid]["threat"] = threat

    def add_ally(self, x, y):
        self.allies.append((x, y))

    def nearby_allies(self, pid):
        """出生点附近（含边界）的队友数量。"""
        point = self.points.get(pid)
        if point is None:
            return 0
        count = 0
        for ax, ay in self.allies:
            if math.hypot(ax - point["x"], ay - point["y"]) < self.ally_radius:
                count += 1
        return count

    def choose(self, now_ms):
        """挑一个出生点，全部不可用时返回 None。"""
        self.scanned += len(self.points) * max(1, len(self.allies))
        best = None
        best_score = 0
        for pid, point in self.points.items():
            score = point["threat"] * 10 + self.nearby_allies(pid) * 5
            if best is None or score > best_score or (score == best_score and pid < best):
                best = pid
                best_score = score
        if best is None:
            return None
        self.points[best]["last_used"] = now_ms
        self.points[best]["picks"] += 1
        return best

    def picks(self, pid):
        if pid in self.points:
            return self.points[pid]["picks"]
        return 0

    def scanned_count(self):
        return self.scanned
