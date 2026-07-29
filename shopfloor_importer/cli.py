import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import load_config
from .duplicates import SubmissionLedger
from .submit import submit
from .workbook import read_workbook

CONFIRMATION = "SUBMIT"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Validate and import a shop-floor workbook")
    result.add_argument("workbook")
    result.add_argument("--config", default="config/example.yaml")
    result.add_argument("--submit", action="store_true", help="write valid, non-duplicate rows")
    result.add_argument("--confirm", help=f"required with --submit; must equal {CONFIRMATION!r}")
    result.add_argument("--ledger", default="state/submitted.json")
    result.add_argument("--results", help="result CSV path (default: timestamped under results/)")
    result.add_argument("--record", help="mold/report number, for example 9167")
    result.add_argument("--machine", help="shop-floor machine, for example A11 or A16")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.submit and args.confirm != CONFIRMATION:
        parser().error(f"writing requires --submit --confirm {CONFIRMATION}")
    config = load_config(args.config)
    if config.record_selector and not args.record:
        parser().error("this configuration requires --record")
    if config.machine_selector and not args.machine:
        parser().error("this configuration requires --machine")
    machine = args.machine.upper() if args.machine else None
    if machine and config.allowed_machines and machine not in config.allowed_machines:
        parser().error(f"--machine must be one of: {', '.join(config.allowed_machines)}")
    records = read_workbook(args.workbook, config.fields, config.header_row)
    for record in records:
        if config.record_selector:
            record.mapped[config.record_selector] = args.record
        if config.machine_selector:
            record.mapped[config.machine_selector] = machine
    ledger = SubmissionLedger(args.ledger)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result_path = Path(args.results or f"results/import-{timestamp}.csv")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    report = []
    for record in records:
        status, detail = "preview", json.dumps(record.mapped, sort_keys=True)
        if not record.valid:
            status, detail = "validation_failed", "; ".join(record.errors)
        elif ledger.contains(record.mapped):
            status, detail = "duplicate", "identical record was submitted previously"
        elif args.submit:
            try:
                detail = submit(config, record.mapped)
                ledger.add(record.mapped)
                status = "success"
            except Exception as error:  # row-level reporting must continue after transport errors
                status, detail = "failure", str(error)
        report.append((record.row_number, status, detail))
        print(f"row {record.row_number}: {status}: {detail}")
    with result_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("row", "status", "detail"))
        writer.writerows(report)
    print(f"results: {result_path}")
    return 1 if any(status in {"validation_failed", "failure"} for _, status, _ in report) else 0


if __name__ == "__main__":
    raise SystemExit(main())
