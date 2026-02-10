from pathlib import Path

from src.data_inventory_audit import build_inventory_document


def test_build_inventory_document_includes_csv_and_excel_sections() -> None:
    content = build_inventory_document(Path('.'), Path('data'))

    assert '# Data Inventory Audit' in content
    assert 'data/raw/federalHolidayData/us_federal_holidays_2015_2026.csv' in content
    assert 'data/raw/weatherData/SBBWK_2016.xlsx' in content
    assert 'Format: CSV' in content
    assert 'Format: Excel workbook' in content


def test_generated_inventory_lists_expected_column_headers() -> None:
    content = build_inventory_document(Path('.'), Path('data'))

    assert 'Column names: year, holiday_name, actual_date' in content
    assert 'Column names: ID = SBBWK, TMP ° F, DWP °F' in content
