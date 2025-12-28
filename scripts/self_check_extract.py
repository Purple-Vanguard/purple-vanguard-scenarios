#!/usr/bin/env python3
import sys

from verify_scenario_artifacts import MISSING_PYYAML_NOTE, YAML_AVAILABLE, select_list_field


def main() -> int:
    if not YAML_AVAILABLE:
        print(f"[WARN] {MISSING_PYYAML_NOTE}")
    try:
        result = select_list_field(
            [{"version": "1.0.0"}, {"version": "2.0.0"}],
            "version",
            "self_check",
        )
        assert result == ["1.0.0", "2.0.0"]
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] valid select failed: {exc}")
        return 1

    try:
        select_list_field([{"name": "missing"}], "version", "self_check")
        print("[FAIL] missing select field did not raise")
        return 1
    except ValueError:
        pass

    try:
        select_list_field(["not-a-mapping"], "version", "self_check")
        print("[FAIL] non-mapping item did not raise")
        return 1
    except ValueError:
        pass

    print("[PASS] select_list_field self-checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
