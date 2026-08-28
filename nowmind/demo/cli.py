from __future__ import annotations

from nowmind.demo.scenarios import all_scenarios


def main() -> int:
    for index, scenario in enumerate(all_scenarios()):
        if index:
            print()
        print(scenario.title)
        print("=" * len(scenario.title))
        for line in scenario.lines:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

