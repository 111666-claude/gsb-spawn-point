"""命令行入口：跑出生点样例。"""

import argparse

from .core import Spawner


def build_parser():
    parser = argparse.ArgumentParser(prog="spawn-point", description="出生点选择")
    parser.add_argument("--sample", default="threat",
                        help="threat / ally / edge / cooldown / rotate / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "threat":
        spawner = Spawner(ally_radius=10, cooldown_ms=0)
        spawner.add_point("a", 0, 0, threat=5)
        spawner.add_point("b", 100, 0, threat=0)
        print("pick=%s" % spawner.choose(0))
    elif args.sample == "ally":
        spawner = Spawner(ally_radius=10, cooldown_ms=0)
        spawner.add_point("a", 0, 0, threat=0)
        spawner.add_point("b", 100, 0, threat=4)
        spawner.add_ally(1, 0)
        spawner.add_ally(2, 0)
        spawner.add_ally(3, 0)
        print("pick=%s" % spawner.choose(0))
    elif args.sample == "edge":
        spawner = Spawner(ally_radius=10, cooldown_ms=0)
        spawner.add_point("a", 0, 0, threat=0)
        spawner.add_ally(10, 0)
        print("allies=%d" % spawner.nearby_allies("a"))
    elif args.sample == "cooldown":
        spawner = Spawner(ally_radius=10, cooldown_ms=5000)
        spawner.add_point("a", 0, 0, threat=0)
        spawner.choose(0)
        second = spawner.choose(1)
        print("second=%s" % ("none" if second is None else second))
    elif args.sample == "rotate":
        spawner = Spawner(ally_radius=10, cooldown_ms=0, rotation_penalty=3)
        spawner.add_point("a", 0, 0, threat=0)
        spawner.add_point("b", 100, 0, threat=0)
        spawner.choose(0)
        second = spawner.choose(1)
        print("second=%s" % ("none" if second is None else second))
    elif args.sample == "scan":
        spawner = Spawner(ally_radius=10, cooldown_ms=0)
        spawner.add_ally(1, 0)
        for index in range(3000):
            spawner.add_point("p-%d" % index, index, 0)
        for _ in range(3000):
            spawner.choose(0)
        print("scanned=%d" % spawner.scanned_count())
    else:
        raise SystemExit("需要 --sample threat|ally|edge|cooldown|rotate|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
