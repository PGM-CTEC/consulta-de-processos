"""
Tests for StatsService - Phase 5 Coverage Extension
Story: REM-017 - Backend Unit Tests (70% Coverage)

Test Categories:
- Database statistics aggregation
- Tribunal grouping and counts
- Phase classification statistics
- Timeline/distribution analysis
- Error handling
"""

from datetime import datetime
from backend import models
from backend.services.stats_service import StatsService


class TestStatsServiceBasics:
    """Tests for basic statistics (3 tests)."""

    def test_get_database_stats_empty_database(self, test_db):
        """TC-1: Get stats from empty database returns zero counts.

        StatsService (BI-002) always returns all 15 phases for the dashboard,
        even when the database is empty — all with count == 0.
        """
        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.total_processes == 0
        assert stats.total_movements == 0
        assert len(stats.tribunals) == 0
        assert all(p.count == 0 for p in stats.phases)
        assert len(stats.timeline) == 0
        assert stats.last_updated is None

    def test_get_database_stats_single_process(self, test_db):
        """TC-2: Get stats with single process."""
        # Create single process
        process = models.Process(
            number="0000001-01.0000.1.00.0001",
            tribunal_name="TJSP",
            class_nature="Ação de Cobrança",
            phase="01",
            distribution_date=datetime(2024, 1, 15)
        )
        test_db.add(process)
        test_db.flush()

        # Add movement
        movement = models.Movement(
            process_id=process.id,
            description="Petição Inicial",
            code="001",
            date=datetime(2024, 1, 15)
        )
        test_db.add(movement)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.total_processes == 1
        assert stats.total_movements == 1
        assert len(stats.tribunals) == 1
        assert stats.tribunals[0].tribunal_name == "TJSP"
        assert stats.tribunals[0].count == 1

    def test_get_database_stats_multiple_processes(self, test_db):
        """TC-3: Get stats with multiple processes."""
        # Create multiple processes in different tribunals
        for i in range(5):
            tribunal = "TJSP" if i < 3 else "TJRJ"
            process = models.Process(
                number=f"000000{i}-01.0000.1.00.000{i}",
                tribunal_name=tribunal,
                phase=f"0{i % 5 + 1}",
                distribution_date=datetime(2024, 1, 10 + i)
            )
            test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.total_processes == 5
        assert len(stats.tribunals) == 2
        # TJSP should have 3, TJRJ should have 2
        tjsp_stat = next(t for t in stats.tribunals if t.tribunal_name == "TJSP")
        assert tjsp_stat.count == 3


class TestStatsServiceTribunals:
    """Tests for tribunal statistics (3 tests)."""

    def test_tribunal_grouping_and_count(self, test_db):
        """TC-4: Tribunals are properly grouped and counted."""
        tribunals = ["TJSP", "TJRJ", "TJMG", "TJBA"]
        for tribunal in tribunals:
            for i in range(2):
                process = models.Process(
                    number=f"{tribunal}-{i}-01.0000.1.00.0001",
                    tribunal_name=tribunal
                )
                test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert len(stats.tribunals) == 4
        for tribunal_stat in stats.tribunals:
            assert tribunal_stat.count == 2

    def test_tribunal_sorted_by_count_descending(self, test_db):
        """TC-5: Tribunals sorted by count descending."""
        # TJSP with 5 processes, TJRJ with 3, TJMG with 1
        for i in range(5):
            process = models.Process(
                number=f"TJSP-{i}-01.0000.1.00.0001",
                tribunal_name="TJSP"
            )
            test_db.add(process)

        for i in range(3):
            process = models.Process(
                number=f"TJRJ-{i}-01.0000.1.00.0001",
                tribunal_name="TJRJ"
            )
            test_db.add(process)

        process = models.Process(
            number="TJMG-0-01.0000.1.00.0001",
            tribunal_name="TJMG"
        )
        test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.tribunals[0].tribunal_name == "TJSP"
        assert stats.tribunals[0].count == 5
        assert stats.tribunals[1].tribunal_name == "TJRJ"
        assert stats.tribunals[1].count == 3
        assert stats.tribunals[2].tribunal_name == "TJMG"
        assert stats.tribunals[2].count == 1

    def test_tribunal_null_values_handled(self, test_db):
        """TC-6: Null tribunal names are handled."""
        process1 = models.Process(
            number="0000001-01.0000.1.00.0001",
            tribunal_name="TJSP"
        )
        process2 = models.Process(
            number="0000002-01.0000.1.00.0002",
            tribunal_name=None
        )
        test_db.add(process1)
        test_db.add(process2)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        # Only TJSP should be in results (nulls filtered out)
        assert len(stats.tribunals) == 1
        assert stats.tribunals[0].tribunal_name == "TJSP"


class TestStatsServicePhases:
    """Tests for phase statistics (3 tests)."""

    def test_phase_grouping_and_count(self, test_db):
        """TC-7: Phases are properly grouped and counted.

        StatsService (BI-002) returns all 15 phases; only 4 should have count > 0.
        """
        phases = ["01", "02", "03", "04"]
        process_id = 0
        for phase in phases:
            for i in range(2):
                process = models.Process(
                    number=f"000000{process_id}-01.0000.1.00.000{process_id}",
                    phase=phase
                )
                test_db.add(process)
                process_id += 1
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        phases_with_data = [p for p in stats.phases if p.count > 0]
        assert len(phases_with_data) == 4
        for phase_stat in phases_with_data:
            assert phase_stat.count == 2

    def test_phase_sorted_by_count_descending(self, test_db):
        """TC-8: Phase counts are correctly aggregated.

        StatsService (BI-002) sorts phases by code ascending (01, 02, 03...),
        not by count. This test verifies correct count aggregation per phase.
        """
        # Phase 01 with 5, Phase 02 with 3, Phase 03 with 1
        for i in range(5):
            process = models.Process(
                number=f"000000{i}-01.0000.1.00.0001",
                phase="01"
            )
            test_db.add(process)

        for i in range(3):
            process = models.Process(
                number=f"000001{i}-01.0000.1.00.0001",
                phase="02"
            )
            test_db.add(process)

        process = models.Process(
            number="0000020-01.0000.1.00.0001",
            phase="03"
        )
        test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        phase_01 = next(p for p in stats.phases if p.phase.startswith("01"))
        phase_02 = next(p for p in stats.phases if p.phase.startswith("02"))
        phase_03 = next(p for p in stats.phases if p.phase.startswith("03"))
        assert phase_01.count == 5
        assert phase_02.count == 3
        assert phase_03.count == 1

    def test_phase_null_values_handled(self, test_db):
        """TC-9: Null phase values are handled.

        StatsService (BI-002) always returns all 15 phases. Null phases are
        excluded from counting — only phase 01 should have count > 0.
        """
        process1 = models.Process(
            number="0000001-01.0000.1.00.0001",
            phase="01"
        )
        process2 = models.Process(
            number="0000002-01.0000.1.00.0002",
            phase=None
        )
        test_db.add(process1)
        test_db.add(process2)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        # Only phase 01 should have count > 0 (nulls excluded from counting)
        phase_01 = next(p for p in stats.phases if p.phase.startswith("01"))
        assert phase_01.count == 1
        phases_nonzero = [p for p in stats.phases if p.count > 0]
        assert len(phases_nonzero) == 1


class TestStatsServiceTimeline:
    """Tests for timeline statistics (3 tests)."""

    def test_timeline_grouping_by_month(self, test_db):
        """TC-10: Processes grouped by distribution month."""
        # Create processes in different months
        base_date = datetime(2024, 1, 1)
        for month in range(1, 4):
            for i in range(2):
                dist_date = base_date.replace(month=month)
                process = models.Process(
                    number=f"000000{month}{i}-01.0000.1.00.0001",
                    distribution_date=dist_date
                )
                test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert len(stats.timeline) == 3
        # Check months are present
        months = [t.month for t in stats.timeline]
        assert "2024-01" in months
        assert "2024-02" in months
        assert "2024-03" in months

    def test_timeline_sorted_oldest_to_newest(self, test_db):
        """TC-11: Timeline sorted from oldest to newest."""
        # Create processes across multiple years
        dates = [
            datetime(2023, 1, 10),
            datetime(2024, 1, 10),
            datetime(2024, 6, 15),
        ]
        for i, date in enumerate(dates):
            process = models.Process(
                number=f"000000{i}-01.0000.1.00.0001",
                distribution_date=date
            )
            test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        # Timeline should be sorted from oldest to newest
        assert len(stats.timeline) >= 2
        timeline_months = [t.month for t in stats.timeline]
        # Check ordering is ascending
        for i in range(len(timeline_months) - 1):
            assert timeline_months[i] <= timeline_months[i + 1]

    def test_timeline_null_distribution_dates_ignored(self, test_db):
        """TC-12: Null distribution dates are ignored."""
        process1 = models.Process(
            number="0000001-01.0000.1.00.0001",
            distribution_date=datetime(2024, 1, 10)
        )
        process2 = models.Process(
            number="0000002-01.0000.1.00.0002",
            distribution_date=None
        )
        test_db.add(process1)
        test_db.add(process2)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        # Only one timeline entry for the non-null date
        assert len(stats.timeline) == 1


class TestStatsServiceMovements:
    """Tests for movement counting (2 tests)."""

    def test_movement_count_accuracy(self, test_db):
        """TC-13: Movement count is accurate."""
        # Create process with multiple movements
        process = models.Process(
            number="0000001-01.0000.1.00.0001",
            tribunal_name="TJSP"
        )
        test_db.add(process)
        test_db.flush()

        movements_count = 5
        for i in range(movements_count):
            movement = models.Movement(
                process_id=process.id,
                description=f"Movimento {i}",
                code=str(i),
                date=datetime.now()
            )
            test_db.add(movement)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.total_movements == movements_count

    def test_multiple_processes_movement_count(self, test_db):
        """TC-14: Movement count across multiple processes."""
        # Create multiple processes with movements
        for p in range(3):
            process = models.Process(
                number=f"000000{p}-01.0000.1.00.000{p}",
                tribunal_name="TJSP"
            )
            test_db.add(process)
            test_db.flush()

            for m in range(2):
                movement = models.Movement(
                    process_id=process.id,
                    description=f"Movimento {m}",
                    code=str(m),
                    date=datetime.now()
                )
                test_db.add(movement)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.total_processes == 3
        assert stats.total_movements == 6  # 3 processes * 2 movements


class TestStatsServiceMetadata:
    """Tests for metadata fields (2 tests)."""

    def test_last_updated_timestamp(self, test_db):
        """TC-15: Last updated timestamp is correctly returned."""
        update_time = datetime.now()
        process = models.Process(
            number="0000001-01.0000.1.00.0001",
            tribunal_name="TJSP",
            last_update=update_time
        )
        test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.last_updated is not None

    def test_stats_schema_compliance(self, test_db):
        """TC-16: Stats response complies with schema."""
        process = models.Process(
            number="0000001-01.0000.1.00.0001",
            tribunal_name="TJSP",
            phase="01",
            distribution_date=datetime(2024, 1, 10)
        )
        test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        # Verify all required fields are present
        assert hasattr(stats, 'total_processes')
        assert hasattr(stats, 'total_movements')
        assert hasattr(stats, 'tribunals')
        assert hasattr(stats, 'phases')
        assert hasattr(stats, 'timeline')
        assert hasattr(stats, 'last_updated')

        # Verify types
        assert isinstance(stats.total_processes, int)
        assert isinstance(stats.total_movements, int)
        assert isinstance(stats.tribunals, list)
        assert isinstance(stats.phases, list)
        assert isinstance(stats.timeline, list)


class TestStatsServiceEdgeCases:
    """Tests for edge cases (2 tests)."""

    def test_large_dataset_performance(self, test_db):
        """TC-17: Stats generation handles large dataset."""
        # Create 100 processes
        for i in range(100):
            tribunal = f"TJSP{i % 5}"
            phase = f"{(i % 15) + 1:02d}"
            dist_month = (i % 12) + 1
            process = models.Process(
                number=f"{i:07d}-01.0000.1.00.0001",
                tribunal_name=tribunal,
                phase=phase,
                distribution_date=datetime(2024, dist_month, 10)
            )
            test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert stats.total_processes == 100
        assert len(stats.tribunals) <= 5
        assert len(stats.phases) <= 15
        assert len(stats.timeline) <= 12

    def test_stats_with_special_characters(self, test_db):
        """TC-18: Stats handles tribunal names with special characters."""
        special_name = "TJSP - Sede"
        process = models.Process(
            number="0000001-01.0000.1.00.0001",
            tribunal_name=special_name
        )
        test_db.add(process)
        test_db.commit()

        service = StatsService(test_db)
        stats = service.get_database_stats()

        assert len(stats.tribunals) == 1
        assert stats.tribunals[0].tribunal_name == special_name
