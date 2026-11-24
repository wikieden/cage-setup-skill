"""Read-only Cage Agent API acceptance check. Output contains no proxy credentials."""
import argparse
import ipaddress
import json
import subprocess
import sys


def call(cli, operation):
    result = subprocess.run(
        [cli, "agent", "call", operation], stdin=subprocess.DEVNULL,
        capture_output=True, text=True, timeout=30,
    )
    reply = json.loads(result.stdout)
    if result.returncode or reply.get("status") != "completed":
        code = (reply.get("error") or {}).get("code", "incomplete")
        raise ValueError(f"{operation}: {code}")
    return reply["data"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True)
    parser.add_argument("--hop", action="append", default=[])
    parser.add_argument("--expect-ip", type=ipaddress.ip_address)
    args = parser.parse_args()
    try:
        state = call(args.cli, "status")
        proxy = call(args.cli, "proxy.status")
        names = {n["id"]: n["name"] for s in proxy["sources"] for n in s["nodes"]}
        hops = [names[i] for i in proxy["route"]]
        safety = state["safety"]
        critical = [c for c in safety["report"]["checks"] if c.get("critical") is True]
        passed = sum(c.get("state") == "passed" for c in critical)
        observed = safety.get("exit_ip")
        live = all(v is True for v in (
            state.get("ready"), state.get("vm_running"), proxy.get("running"), proxy.get("network_open")
        )) and safety["gate"]["mode"] == "open"
        ok = bool(live and hops and critical and passed == len(critical)
                  and (not args.hop or hops == args.hop)
                  and (not args.expect_ip or ipaddress.ip_address(observed) == args.expect_ip))
        print(json.dumps(dict(ok=ok, live=live, route=hops, exit_ip=observed,
                              critical_passed=passed, critical_total=len(critical)), ensure_ascii=False))
        return 0 if ok else 1
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as exc:
        print(f"Cage check incomplete: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
