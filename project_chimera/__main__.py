from __future__ import annotations

import argparse
import uuid
from typing import Sequence


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project_chimera",
        description="Project Chimera service runner (Planner/Worker/Judge).",
    )
    sub = parser.add_subparsers(dest="command")

    planner = sub.add_parser("planner", help="Run Planner service loop")
    planner.add_argument("--campaign-id", default="test-campaign-001")
    planner.add_argument("--redis-url", default=None)

    worker = sub.add_parser("worker", help="Run Worker service loop")
    worker.add_argument("--worker-id", default=None)
    worker.add_argument("--redis-url", default=None)

    judge = sub.add_parser("judge", help="Run Judge service loop")
    judge.add_argument("--redis-url", default=None)

    sub.add_parser("demo", help="Run a short demo (no infinite loops)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "planner":
        from services.planner import Planner

        planner = Planner(redis_url=args.redis_url) if args.redis_url else Planner()
        planner.run(campaign_id=args.campaign_id)
        return 0

    if args.command == "worker":
        from services.worker import Worker

        worker_id = args.worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        worker = Worker(worker_id=worker_id, redis_url=args.redis_url) if args.redis_url else Worker(worker_id=worker_id)
        worker.run()
        return 0

    if args.command == "judge":
        from services.judge import Judge

        judge = Judge(redis_url=args.redis_url) if args.redis_url else Judge()
        judge.run()
        return 0

    if args.command == "demo":
        # Keep demo quick and non-blocking.
        from services.planner import Planner, GlobalState
        from services.worker import Worker
        from services.judge import Judge

        planner = Planner()
        worker = Worker(worker_id=f"worker-{uuid.uuid4().hex[:8]}")
        judge = Judge()

        print("Planner connected:", planner.is_connected())
        print("Worker connected:", worker.is_connected())
        print("Judge connected:", judge.is_connected())

        gs = GlobalState(
            campaign_id="demo",
            goals=["Research AI trends", "Generate content about AI agents"],
            budget_limit=100.0,
        )
        print("Sample GlobalState:", gs.model_dump())
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

