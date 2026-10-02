# spawn-point

出生点选择：危险度、队友距离、冷却与轮转惩罚，只用 Python 标准库。

```
python3 -m spawn.cli --sample threat
python3 -m spawn.cli --sample ally
python3 -m spawn.cli --sample edge
python3 -m spawn.cli --sample cooldown
python3 -m spawn.cli --sample rotate
python3 -m spawn.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **评分**：`score = -threat * 10 + nearby_allies * 5 - rotation_penalty * picks`，
  取分数最高的点；同分按点 id 字典序升序。
- **队友计数**：距离不超过 `ally_radius` 的队友都算，正好等于半径也算一个。
- **冷却**：`cooldown_ms` 内用过的点不参与选择；全部点在冷却时返回 None。
- **轮转**：点每被选中一次，`picks` 加一，下次评分多扣一份惩罚，避免连续刷同一个点。
- **不变量**：同一串选择重复执行结果相同；被选中的点一定不在冷却期。
- **查询代价**：`choose` 不许按点数乘队友数扫描，`scanned_count` 不随点数线性增长。
- **规模**：10 万个出生点、10 万队友、每秒 10 万次选择，单次摊还 O(候选点数)。

## 输出契约（不改格式）

```
pick=..
allies=..
second=..
scanned=..
```

## 目录

```
spawn/core.py   评分、冷却与轮转
spawn/cli.py    命令行入口
tests/          unittest 用例
```
