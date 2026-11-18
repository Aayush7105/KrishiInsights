"""
KrishiInsights - Primary Neon Integration & Application Verification
Validates that FastAPI, SQLAlchemy, and dependencies interact exclusively with Neon.
Performs read test, safe write & read-back test, and verifies zero localhost usage.
"""

import sys
import os
import json
from sqlalchemy import text

# Add backend and root directories to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for path in (backend_path, root_path):
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from app.core.config import settings  # type: ignore[import-not-found]
    from app.database.session import SessionLocal  # type: ignore[import-not-found]
    from app.api.routes.health import health_check  # type: ignore[import-not-found]
except ImportError:
    from backend.app.core.config import settings  # type: ignore[import-not-found, no-redef]
    from backend.app.database.session import SessionLocal  # type: ignore[import-not-found, no-redef]
    from backend.app.api.routes.health import health_check  # type: ignore[import-not-found, no-redef]

def run_tests():
    print("\n========================================================")
    print("TESTING APPLICATION AGAINST NEON AS PRIMARY DATABASE")
    print("========================================================")

    # 1. Verify Configuration Target
    print("\n[1. TARGET VERIFICATION]")
    assert "neon.tech" in settings.DATABASE_URL, f"DATABASE_URL does not point to Neon: {settings.DATABASE_URL}"
    assert "localhost" not in settings.DATABASE_URL, "DATABASE_URL points to localhost!"
    assert "neondb" in settings.DATABASE_URL, "DATABASE_URL does not point to neondb!"
    print("  * Target Host        : Neon Cloud (neon.tech)")
    print("  * Target Database    : neondb")
    print("  * Primary Database   : NEON (Verified, zero localhost reference)")

    # 2. Test FastAPI Health Check
    print("\n[2. FASTAPI HEALTH ENDPOINT TEST]")
    health = health_check()
    print("  * Health Response    :", health)
    assert health["status"] == "healthy"
    assert health["database"] == "connected"
    print("  * Health Check Status: PASSED (Database reported connected)")

    # 3. Test Application Reads
    print("\n[3. APPLICATION READ QUERY TEST]")
    db = SessionLocal()
    try:
        # Query agricultural records joined with state and crop
        sample = db.execute(text("""
            SELECT s.state_name, d.district_name, c.crop_name, c.crop_category,
                   a.season, a.year, a.area, a.production, a.yield_amount, a.yield_unit
            FROM agricultural_records a
            JOIN states s ON a.state_id = s.id
            JOIN districts d ON a.district_id = d.id
            JOIN crops c ON a.crop_id = c.id
            WHERE c.crop_name = 'Rice' AND a.year = 2014
            LIMIT 3;
        """)).fetchall()
        assert len(sample) == 3, f"Expected 3 sample rows, got {len(sample)}"
        print(f"  * Sample Records Retrieved from Neon ({len(sample)} rows):")
        for r in sample:
            print(f"    - {r[0]} | {r[1]} | {r[2]} ({r[3]}) | {r[4]} {r[5]} | Yield: {r[8]} {r[9]}")
        print("  * Read Query Status  : PASSED")

        # 4. Safe Database Write & Read-Back Test
        print("\n[4. SAFE WRITE & READ-BACK TEST]")
        test_payload = {"test": True, "description": "Neon Primary Verification", "timestamp": "2026-11-17"}
        insert_stmt = text("""
            INSERT INTO prediction_records 
                (input_features, predicted_yield, unit, model_name, model_version)
            VALUES 
                (:features, :yield_val, :unit, :model, :ver)
            RETURNING id, created_at;
        """)
        insert_res = db.execute(insert_stmt, {
            "features": json.dumps(test_payload),
            "yield_val": 3.75,
            "unit": "Tonnes/Hectare",
            "model": "NeonVerificationModel",
            "ver": "v1.0"
        }).fetchone()
        db.commit()
        record_id = insert_res[0]
        created_at = insert_res[1]
        print(f"  * Record Written to Neon: ID={record_id}, CreatedAt={created_at}")

        # Read back written record
        read_back = db.execute(text("SELECT id, predicted_yield, model_name FROM prediction_records WHERE id = :id;"), {"id": record_id}).fetchone()
        assert read_back is not None, "Failed to read back newly created prediction record!"
        assert read_back[1] == 3.75, f"Expected yield 3.75, got {read_back[1]}"
        print(f"  * Read-Back Verified   : ID={read_back[0]}, Yield={read_back[1]}, Model={read_back[2]}")

        # Clean up test record to maintain pristine database
        db.execute(text("DELETE FROM prediction_records WHERE id = :id;"), {"id": record_id})
        db.commit()
        remaining = db.execute(text("SELECT COUNT(*) FROM prediction_records WHERE id = :id;"), {"id": record_id}).scalar()
        assert remaining == 0, "Failed to delete test verification record!"
        print("  * Clean-up Completed   : Test record removed, prediction_records returned to original state.")
        print("  * Write Test Status    : PASSED")

    finally:
        db.close()

    print("\n========================================================")
    print("ALL APPLICATION NEON INTEGRATION TESTS PASSED 100%!")
    print("========================================================\n")

if __name__ == "__main__":
    run_tests()
