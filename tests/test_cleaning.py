"""Contract tests for the generated versalMotors cleaned database."""

from __future__ import annotations

import unittest
from datetime import date, timedelta
from pathlib import Path

import duckdb

from src.data.cleaning import CleaningPipeline


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "business.duckdb"


class CleaningContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.connection = duckdb.connect(str(DATABASE), read_only=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.connection.close()

    def scalar(self, sql: str) -> int:
        return self.connection.execute(sql).fetchone()[0]

    def test_exact_duplicates_are_removed(self) -> None:
        expected = {
            "branches": 15, "models": 54, "salespeople": 225, "inventory": 25_000,
            "sales": 20_520, "service_records": 48_025, "warranty_claims": 3_058,
            "complaints": 1_855, "satisfaction": 15_007,
        }
        for table, count in expected.items():
            with self.subTest(table=table):
                self.assertEqual(self.scalar(f"SELECT COUNT(*) FROM {table}"), count)

    def test_negative_amounts_are_flagged_and_nulled(self) -> None:
        checks = [
            ("inventory", "acquisition_cost"), ("sales", "net_sale_price"),
            ("service_records", "parts_cost"), ("warranty_claims", "approved_amount"),
            ("complaints", "resolution_cost"),
        ]
        for table, column in checks:
            with self.subTest(table=table, column=column):
                flagged = self.scalar(f"SELECT COUNT(*) FROM {table} WHERE {column}_negative_flag")
                still_populated = self.scalar(
                    f"SELECT COUNT(*) FROM {table} WHERE {column}_negative_flag AND {column} IS NOT NULL"
                )
                self.assertGreater(flagged, 0)
                self.assertEqual(still_populated, 0)

    def test_invalid_dates_are_flagged_and_nulled(self) -> None:
        flagged = self.scalar("SELECT COUNT(*) FROM satisfaction WHERE survey_date_invalid_flag")
        not_nulled = self.scalar(
            "SELECT COUNT(*) FROM satisfaction WHERE survey_date_invalid_flag AND survey_date IS NOT NULL"
        )
        self.assertEqual(flagged, 10)
        self.assertEqual(not_nulled, 0)

    def test_orphans_are_flagged_and_resolved_to_null(self) -> None:
        checks = [
            ("salespeople", "branch_id", 8), ("inventory", "model_id", 12),
            ("inventory", "branch_id", 10), ("sales", "salesperson_id", 15),
            ("complaints", "claim_id", 8), ("satisfaction", "complaint_id", 7),
        ]
        for table, column, expected in checks:
            with self.subTest(table=table, column=column):
                flagged = self.scalar(
                    f"SELECT COUNT(*) FROM {table} WHERE {column}_orphan_flag AND {column} IS NULL"
                )
                self.assertEqual(flagged, expected)

    def test_orphan_model_is_not_created_as_a_dimension_member(self) -> None:
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM models WHERE model_id = 9002"), 0)
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM inventory WHERE model_id_raw = 9002 "
                "AND model_id IS NULL AND model_id_orphan_flag AND _row_quality_status = 'ERROR'"
            ),
            12,
        )

    def test_explicit_mapping_behavior(self) -> None:
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM branches WHERE branch_name_unmapped_flag AND branch_name IS NOT NULL"),
            0,
        )
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM branches WHERE NOT branch_name_unmapped_flag AND branch_name IS NULL"),
            0,
        )
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM models WHERE model_name_unmapped_flag AND model_name IS NOT NULL"),
            0,
        )
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM models WHERE NOT model_name_unmapped_flag AND model_name IS NULL"),
            0,
        )

    def test_cleaning_log_contract(self) -> None:
        columns = [row[1] for row in self.connection.execute("PRAGMA table_info('cleaning_log')").fetchall()]
        self.assertEqual(columns, ["step", "table", "rows_affected", "reason", "action_taken"])
        self.assertGreater(self.scalar("SELECT COUNT(*) FROM cleaning_log"), 0)

    def test_missing_totals_stay_null_with_calculated_companions(self) -> None:
        missing = self.scalar(
            "SELECT COUNT(*) FROM sales "
            "WHERE total_sale_price_missing_flag AND total_sale_price IS NULL"
        )
        calculated = self.scalar(
            "SELECT COUNT(*) FROM sales "
            "WHERE total_sale_price_missing_flag AND total_sale_price_calculated IS NOT NULL"
        )
        self.assertGreater(missing, 0)
        self.assertGreater(calculated, 0)

    def test_out_of_range_scores_are_nulled(self) -> None:
        pairs = [
            ("overall_score", "overall_score_out_of_range_flag"),
            ("nps_score", "nps_score_out_of_range_flag"),
            ("product_score", "product_score_out_of_range_flag"),
            ("staff_score", "staff_score_out_of_range_flag"),
            ("timeliness_score", "timeliness_score_out_of_range_flag"),
            ("value_score", "value_score_out_of_range_flag"),
        ]
        flagged = 0
        for column, flag in pairs:
            flagged += self.scalar(f"SELECT COUNT(*) FROM satisfaction WHERE {flag}")
            self.assertEqual(
                self.scalar(f"SELECT COUNT(*) FROM satisfaction WHERE {flag} AND {column} IS NOT NULL"),
                0,
            )
        self.assertGreater(flagged, 0)

    def test_near_duplicates_are_flagged_not_deleted(self) -> None:
        for table in ["sales", "service_records", "warranty_claims", "complaints"]:
            with self.subTest(table=table):
                self.assertGreater(
                    self.scalar(f"SELECT COUNT(*) FROM {table} WHERE _possible_near_duplicate_flag"),
                    0,
                )


class CleaningStressTests(unittest.TestCase):
    def test_future_dates_are_flagged(self) -> None:
        pipeline = CleaningPipeline()
        future = (date.today() + timedelta(days=30)).isoformat()
        rows = [{"sale_date": future, "delivery_date": None, "created_at": None}]

        pipeline._parse_dates("sales", rows)

        self.assertTrue(rows[0]["sale_date_future_flag"])

    def test_sale_before_acquisition_and_claim_before_sale_are_flagged(self) -> None:
        pipeline = CleaningPipeline()
        pipeline.tables = {
            "inventory": [{
                "inventory_id": 1, "acquisition_date": "2025-02-01",
                "arrival_date": "2025-02-02", "inventory_status": "sold",
                "sold_date": "2025-02-03",
            }],
            "sales": [{
                "sale_id": 1, "inventory_id": 1, "sale_date": "2025-01-01",
                "delivery_date": None, "sale_status": "completed",
            }],
            "service_records": [],
            "warranty_claims": [{
                "claim_id": 1, "sale_id": 1, "service_id": None,
                "claim_date": "2024-12-01", "decision_date": None,
                "claim_status": "submitted",
            }],
            "complaints": [],
            "satisfaction": [],
        }

        pipeline._validate_chronology()

        self.assertTrue(pipeline.tables["sales"][0]["sale_before_acquisition_flag"])
        self.assertTrue(pipeline.tables["warranty_claims"][0]["claim_before_sale_flag"])


if __name__ == "__main__":
    unittest.main()
