"""Generate the anonymized .xlsx examples locally; no binary files are committed."""

from datetime import date
from pathlib import Path

from openpyxl import Workbook


HERE = Path(__file__).resolve().parent


def save_work_orders() -> Path:
    book = Workbook()
    sheet = book.active
    sheet.title = "Work Orders"
    sheet.append([
        "Record Ref", "Item Ref", "Planned Units", "Due On", "Work Area",
        "Urgency", "Operator Note", "T 90", "T PL", "E", "Weight",
    ])
    sheet.append([
        "WO-DEMO-001", "ITEM-ALPHA", 24, date(2030, 1, 15), "AREA-01",
        "NORMAL", "Fictional training record", 90, 42, 7.5, 12.25,
    ])
    sheet.append([
        "WO-DEMO-002", "ITEM-BETA", 8, date(2030, 1, 16), "AREA-02",
        "HIGH", "Anonymized example only", 91, 43, 8, 10.5,
    ])
    path = HERE / "anonymized_work_orders.xlsx"
    book.save(path)
    return path


def save_measurements() -> Path:
    book = Workbook()
    sheet = book.active
    sheet.title = "Measurements"
    sheet.append(["ANONYMIZED MEASUREMENT REPORT"])
    for _ in range(18):
        sheet.append([])
    sheet.append([
        "Cav #", "T @ 90", "T @ 10", "T avg", "T ovality", "E @ 90",
        "E @ 10", "E avg", "E ovality", "Weight",
    ])
    for row in (
        (1, 2.441, 2.436, 2.439, 0.005, 2.350, 2.338, 2.344, 0.011, 36.290),
        (2, 2.438, 2.437, 2.437, 0.001, 2.346, 2.339, 2.343, 0.008, 35.180),
        (3, 2.439, 2.435, 2.437, 0.004, 2.349, 2.337, 2.343, 0.012, 35.900),
        (4, 2.437, 2.438, 2.438, 0.001, 2.348, 2.340, 2.344, 0.008, 35.770),
        (5, 2.441, 2.436, 2.438, 0.005, 2.351, 2.338, 2.344, 0.013, 36.240),
        (6, 2.438, 2.437, 2.438, 0.001, 2.347, 2.341, 2.344, 0.006, 34.160),
        (7, 2.441, 2.436, 2.439, 0.004, 2.348, 2.340, 2.344, 0.008, 36.170),
        (8, 2.438, 2.439, 2.438, 0.000, 2.347, 2.342, 2.344, 0.006, 35.960),
    ):
        sheet.append(row)
    path = HERE / "anonymized_measurement_report.xlsx"
    book.save(path)
    return path


if __name__ == "__main__":
    for generated in (save_work_orders(), save_measurements()):
        print(generated)
