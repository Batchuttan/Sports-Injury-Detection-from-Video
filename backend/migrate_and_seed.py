import sqlite3
import json
from datetime import datetime, timedelta

def run_migration():
    conn = sqlite3.connect("sql_app.db")
    c = conn.cursor()

    # 1. Update users table columns
    c.execute("PRAGMA table_info(users)")
    user_cols = [row[1] for row in c.fetchall()]
    if "profile_picture" not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
    if "email_alerts" not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN email_alerts INTEGER DEFAULT 1")
    if "daily_wellness" not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN daily_wellness INTEGER DEFAULT 1")
    if "sound_effects" not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN sound_effects INTEGER DEFAULT 0")

    # 2. Update athlete_profiles table columns
    c.execute("PRAGMA table_info(athlete_profiles)")
    prof_cols = [row[1] for row in c.fetchall()]
    if "phone" not in prof_cols:
        c.execute("ALTER TABLE athlete_profiles ADD COLUMN phone TEXT")
    if "dominant_side" not in prof_cols:
        c.execute("ALTER TABLE athlete_profiles ADD COLUMN dominant_side TEXT")
    if "emergency_contact" not in prof_cols:
        c.execute("ALTER TABLE athlete_profiles ADD COLUMN emergency_contact TEXT")
    if "personal_bio" not in prof_cols:
        c.execute("ALTER TABLE athlete_profiles ADD COLUMN personal_bio TEXT")
    if "profile_picture" not in prof_cols:
        c.execute("ALTER TABLE athlete_profiles ADD COLUMN profile_picture TEXT")

    # 3. Create training_plans table
    c.execute("""
    CREATE TABLE IF NOT EXISTS training_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan_id TEXT,
        title TEXT,
        duration TEXT,
        status TEXT DEFAULT 'Active',
        focus TEXT,
        target_joint TEXT,
        description TEXT,
        prescribed_exercises TEXT,
        exercises_detail TEXT,
        weekly_schedule TEXT,
        clinical_notes TEXT,
        progress_percent INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # 4. Seed the 3 training plans (global or template plans)
    plans = [
        {
            "plan_id": "knee-valgus",
            "title": "Knee Valgus Correction",
            "duration": "4 Weeks",
            "status": "Active",
            "focus": "Frontal Plane Knee Stability & Hip Abduction Kinematics",
            "target_joint": "Knee, Patellofemoral Joint & Hip Abductors",
            "description": "Comprehensive 4-week neuromuscular intervention targeting medial knee displacement (valgus collapse) during high-velocity cutting, squatting, and landing deceleration.",
            "prescribed_exercises": json.dumps(["Banded Side Steps", "Single Leg Romanian Deadlifts"]),
            "exercises_detail": json.dumps([
                {
                    "name": "Banded Side Steps",
                    "alias": "Lateral Monster Walks",
                    "target_muscles": ["Gluteus Medius", "Gluteus Minimus", "Tensor Fasciae Latae"],
                    "frequency": "4x / week",
                    "sets": 3,
                    "reps": "15 steps each direction",
                    "rest": "45 seconds",
                    "tempo": "2-0-2 (2s step, 0s pause, 2s return)",
                    "completed": True,
                    "biomechanical_rationale": "Strengthens primary hip abductors to counteract medial femoral rotation and dynamic knee adduction moment during ground contact.",
                    "form_cues": [
                        "Keep toes and feet parallel facing straight forward.",
                        "Maintain an athletic quarter-squat hinge at the hips.",
                        "Ensure knees press outward against band tension at all times; never allow them to collapse inward."
                    ]
                },
                {
                    "name": "Single Leg Romanian Deadlifts",
                    "alias": "Unilateral RDL with Dumbbell/Kettlebell",
                    "target_muscles": ["Biceps Femoris (Hamstrings)", "Gluteus Maximus", "Deep Core Stabilizers"],
                    "frequency": "3x / week",
                    "sets": 4,
                    "reps": "10 reps per limb",
                    "rest": "60 seconds",
                    "tempo": "3-1-1 (3s eccentric hinge, 1s isometric hold, 1s concentric drive)",
                    "completed": False,
                    "biomechanical_rationale": "Develops unilateral eccentric hamstring tension, essential for absorbing anterior tibial shear force and protecting the ACL during deceleration.",
                    "form_cues": [
                        "Maintain a soft 15-20° bend in the stance knee throughout.",
                        "Drive non-working heel straight back towards the rear wall.",
                        "Keep pelvis level and square to the ground without rotating the hip open."
                    ]
                }
            ]),
            "weekly_schedule": json.dumps([
                {"week": "Week 1", "objective": "Neuromuscular Activation & Baseline Form Calibration", "intensity": "Light band tension, focus on perfect joint alignment."},
                {"week": "Week 2", "objective": "Loaded Hip Abduction & Isometric End-Range Holds", "intensity": "Medium band tension, 2-second hold at end range."},
                {"week": "Week 3", "objective": "Eccentric Deceleration & Added External Load", "intensity": "Add 6-8kg dumbbell to single-leg RDL."},
                {"week": "Week 4", "objective": "Dynamic Cutting Reassessment & Sport-Specific Perturbations", "intensity": "Reactive lateral bounds with stick landing."}
            ]),
            "clinical_notes": "Prescribed following motion capture indicating an 18.4° valgus excursion during cutting deceleration. Patient reports marked stability improvement.",
            "progress_percent": 65
        },
        {
            "plan_id": "core-stability",
            "title": "Core Stability Routine",
            "duration": "Ongoing",
            "status": "Active",
            "focus": "Anti-Extension & Anti-Rotation Lumbopelvic Control",
            "target_joint": "Lumbar Spine, Pelvis & Thoracolumbar Fascia",
            "description": "Continuous athletic maintenance protocol to solidify trunk stiffness, prevent excessive lumbar lordosis, and eliminate parasitic rotational energy leaks during athletic movements.",
            "prescribed_exercises": json.dumps(["Planks", "Russian Twists"]),
            "exercises_detail": json.dumps([
                {
                    "name": "Planks",
                    "alias": "Forearm Anti-Extension Plank",
                    "target_muscles": ["Transverse Abdominis", "Rectus Abdominis", "Serratus Anterior"],
                    "frequency": "Daily",
                    "sets": 4,
                    "reps": "45 - 60 seconds isometric hold",
                    "rest": "45 seconds",
                    "tempo": "Continuous maximal tension",
                    "completed": True,
                    "biomechanical_rationale": "Builds deep abdominal wall endurance, anchoring the pelvis against anterior tilt and shielding the lumbar vertebrae from shear stresses.",
                    "form_cues": [
                        "Drive forearms into the turf to engage serratus anterior.",
                        "Tuck the tailbone slightly into a neutral posterior pelvic tilt.",
                        "Squeeze glutes and quadriceps continuously while maintaining steady diaphragmatic nasal breathing."
                    ]
                },
                {
                    "name": "Russian Twists",
                    "alias": "Controlled Rotational Torso Transfer",
                    "target_muscles": ["Internal & External Obliques", "Quadratus Lumborum"],
                    "frequency": "4x / week",
                    "sets": 3,
                    "reps": "20 controlled reps (10 each side)",
                    "rest": "45 seconds",
                    "tempo": "2-1-2",
                    "completed": True,
                    "biomechanical_rationale": "Conditioning of the oblique sling systems enables rapid kinetic energy transfer between the lower extremities and upper limbs during rotational throwing and direction changes.",
                    "form_cues": [
                        "Lean torso back to 45° with an elongated, tall spine.",
                        "Initiate twist from the thoracic spine and ribcage, keeping hips steady.",
                        "Avoid neck strain by keeping gaze aligned with sternum."
                    ]
                }
            ]),
            "weekly_schedule": json.dumps([
                {"phase": "Foundation Phase", "objective": "Static Bracing & Intra-Abdominal Pressure", "intensity": "Bodyweight holds focusing on 360° breathing."},
                {"phase": "Rotational Phase", "objective": "Multi-Planar Torque & Deceleration Tolerance", "intensity": "Introduce medicine ball (3-5kg) with controlled tempo."},
                {"phase": "Reactive Phase", "objective": "High-Velocity Power Transfer", "intensity": "Dynamic medicine ball rotational throws against rebounder."}
            ]),
            "clinical_notes": "Maintains pelvic neutral during sprint top-speed phases; reduces hamstring strain recurrence risk by 42%.",
            "progress_percent": 80
        },
        {
            "plan_id": "post-match-recovery",
            "title": "Post-Match Recovery",
            "duration": "1 Day",
            "status": "Pending",
            "focus": "Metabolic Clearance, Myofascial Downregulation & Cryotherapy",
            "target_joint": "Systemic Musculoskeletal & Neuromuscular Axis",
            "description": "Acute post-match regeneration regimen designed to expedite lactate and metabolite clearance, relieve hypertonic muscle spasm, and lower inflammatory cytokines within 24 hours.",
            "prescribed_exercises": json.dumps(["Foam Rolling", "Light Stretching", "Cold Plunge"]),
            "exercises_detail": json.dumps([
                {
                    "name": "Foam Rolling",
                    "alias": "Self-Myofascial Release (SMR)",
                    "target_muscles": ["Calves", "Hamstrings", "Quadriceps", "IT Bands", "Thoracic Spine"],
                    "frequency": "Post-match immediately",
                    "sets": 1,
                    "reps": "12 minutes total (60-90s per trigger region)",
                    "rest": "Minimal",
                    "tempo": "Slow roll (1 inch/sec)",
                    "completed": False,
                    "biomechanical_rationale": "Reduces myofascial adhesions, downregulates overactive motor units via Golgi tendon organ reflex, and promotes microvascular perfusion.",
                    "form_cues": [
                        "Roll slowly; when finding a tender nodule, pause for 30s.",
                        "Breathe deeply to encourage parasympathetic nervous system tone.",
                        "Never roll directly over bony prominences or the lumbar spine."
                    ]
                },
                {
                    "name": "Light Stretching",
                    "alias": "Submaximal Static Decompression",
                    "target_muscles": ["Hip Flexors", "Adductors", "Piriformis", "Lats"],
                    "frequency": "Post-foam roll",
                    "sets": 2,
                    "reps": "30s hold per muscle group",
                    "rest": "15 seconds",
                    "tempo": "Gentle relaxation",
                    "completed": False,
                    "biomechanical_rationale": "Restores resting sarcolemma length and reduces muscle stiffness without dampening post-activation potentiation.",
                    "form_cues": [
                        "Keep stretch intensity comfortable at 4/10; do not force end-range.",
                        "Exhale as you sink gently into the stretch.",
                        "Keep joints in neutral alignment."
                    ]
                },
                {
                    "name": "Cold Plunge",
                    "alias": "Cryo Immersion Therapy (10°C - 12°C)",
                    "target_muscles": ["Full Body / Systemic Circulation"],
                    "frequency": "Within 2h of match whistle",
                    "sets": 1,
                    "reps": "10-12 minutes continuous immersion",
                    "rest": "Warm re-entry",
                    "tempo": "Steady nasal respiration",
                    "completed": False,
                    "biomechanical_rationale": "Induces peripheral vasoconstriction to suppress inflammatory edema and micro-hemorrhage, followed by active hyperemia upon exit.",
                    "form_cues": [
                        "Submerge to the clavicle level.",
                        "Control the initial gasp response with 4-second inhales and 6-second exhales.",
                        "Allow natural warm-up post-immersion rather than immediate hot showering."
                    ]
                }
            ]),
            "weekly_schedule": json.dumps([
                {"phase": "Immediate (0-30 min)", "objective": "Rehydration & Electrolyte Restoration", "intensity": "500ml hypotonic electrolyte beverage."},
                {"phase": "Acute (30-60 min)", "objective": "Myofascial Release & Mobility", "intensity": "Foam rolling + gentle stretching flow."},
                {"phase": "Regenerative (60-90 min)", "objective": "Cryotherapy & Circulatory Flush", "intensity": "10°C ice bath immersion for 10 minutes."}
            ]),
            "clinical_notes": "Pending execution after tomorrow's league fixture. Vital for attenuating delayed-onset muscle soreness (DOMS).",
            "progress_percent": 15
        }
    ]

    # Delete existing global plans and re-insert to ensure latest rich protocol
    c.execute("DELETE FROM training_plans WHERE user_id IS NULL")
    now_iso = datetime.utcnow().isoformat()
    for p in plans:
        c.execute("""
            INSERT INTO training_plans (
                user_id, plan_id, title, duration, status, focus, target_joint,
                description, prescribed_exercises, exercises_detail, weekly_schedule,
                clinical_notes, progress_percent, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            None, p["plan_id"], p["title"], p["duration"], p["status"], p["focus"],
            p["target_joint"], p["description"], p["prescribed_exercises"],
            p["exercises_detail"], p["weekly_schedule"], p["clinical_notes"],
            p["progress_percent"], now_iso, now_iso
        ))

    # 5. Seed / Update user #3 and default user profile
    c.execute("SELECT id FROM users WHERE email = 'aizalbegenemeliteachu@gmail.com'")
    user_row = c.fetchone()
    if user_row:
        uid = user_row[0]
        c.execute("""
            UPDATE users SET 
                email_alerts = 1,
                daily_wellness = 1,
                sound_effects = 1
            WHERE id = ?
        """, (uid,))

        c.execute("SELECT id FROM athlete_profiles WHERE user_id = ?", (uid,))
        p_row = c.fetchone()
        if p_row:
            c.execute("""
                UPDATE athlete_profiles SET
                    sport_type = 'Football',
                    position = 'Left Back',
                    age = 20,
                    height = 170.0,
                    weight = 50.0,
                    injury_history = 'Small bone cracks on right leg and recent crack on right leg small finger',
                    training_load = 'Football camp',
                    phone = '+1 (555) 234-8901',
                    dominant_side = 'Left Foot',
                    emergency_contact = 'Dr. Marcus Vance (Physio) - +1 (555) 019-2834',
                    personal_bio = 'Left-back athlete dedicated to offensive wing overloads and defensive transitions. Rebuilding strength and biomechanical alignment following right leg micro-fissures.'
                WHERE user_id = ?
            """, (uid,))
        else:
            c.execute("""
                INSERT INTO athlete_profiles (
                    user_id, sport_type, position, age, height, weight,
                    injury_history, training_load, phone, dominant_side,
                    emergency_contact, personal_bio
                ) VALUES (?, 'Football', 'Left Back', 20, 170.0, 50.0,
                    'Small bone cracks on right leg and recent crack on right leg small finger',
                    'Football camp', '+1 (555) 234-8901', 'Left Foot',
                    'Dr. Marcus Vance (Physio) - +1 (555) 019-2834',
                    'Left-back athlete dedicated to offensive wing overloads and defensive transitions.'
                )
            """, (uid,))

    # Also update demo@sportsai.com if exists
    c.execute("SELECT id FROM users WHERE email = 'demo@sportsai.com'")
    demo_user = c.fetchone()
    if demo_user:
        d_uid = demo_user[0]
        c.execute("SELECT id FROM athlete_profiles WHERE user_id = ?", (d_uid,))
        if not c.fetchone():
            c.execute("""
                INSERT INTO athlete_profiles (
                    user_id, sport_type, position, age, height, weight,
                    injury_history, training_load, phone, dominant_side,
                    emergency_contact, personal_bio
                ) VALUES (?, 'Football', 'Left Back', 20, 170.0, 50.0,
                    'Small bone cracks on right leg and recent crack on right leg small finger',
                    'Football camp', '+1 (555) 234-8901', 'Left Foot',
                    'Dr. Marcus Vance (Physio) - +1 (555) 019-2834',
                    'Left-back athlete dedicated to offensive wing overloads.'
                )
            """, (d_uid,))

    # 6. Seed Physical Assessments for user #3 (and demo user) if few records exist
    for target_uid in [3, 2]:
        c.execute("SELECT COUNT(*) FROM physical_assessments WHERE user_id = ?", (target_uid,))
        count = c.fetchone()[0]
        if count < 4:
            assessments = [
                ("2026-10-15", "VO2 Max Aerobic Capacity", 56.4, "Top 10th percentile for professional collegiate wing-backs. High mitochondrial density."),
                ("2026-10-18", "Functional Movement Screen (FMS)", 17.0, "Score 17/21. Slight asymmetry noted in in-line lunge and active straight-leg raise."),
                ("2026-10-22", "Countermovement Jump (CMJ)", 44.5, "Peak vertical impulse 2450 N. Takeoff symmetry 96.2% between left and right limb."),
                ("2026-10-25", "Y-Balance Dynamic Stability", 95.8, "Anterior reach 68cm, posteromedial 82cm, posterolateral 84cm. Safe limb symmetry."),
                ("2026-10-28", "Reactive Strength Index (RSI)", 2.18, "Drop jump from 30cm box. Ground contact time 210ms with high elastic rebound efficiency.")
            ]
            for dt, tname, score, notes in assessments:
                c.execute("""
                    INSERT INTO physical_assessments (user_id, date, test_name, score, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (target_uid, dt, tname, score, notes))

        # 7. Seed Performance Records
        c.execute("SELECT COUNT(*) FROM performance_records WHERE user_id = ?", (target_uid,))
        p_count = c.fetchone()[0]
        if p_count < 6:
            perf_records = [
                ("2026-09-20", "40m Sprint Time", 5.08, "sec"),
                ("2026-09-28", "40m Sprint Time", 5.01, "sec"),
                ("2026-10-06", "40m Sprint Time", 4.96, "sec"),
                ("2026-10-14", "40m Sprint Time", 4.91, "sec"),
                ("2026-10-24", "40m Sprint Time", 4.88, "sec"),
                ("2026-10-10", "Dynamic Knee Valgus Angle", 18.4, "deg"),
                ("2026-10-17", "Dynamic Knee Valgus Angle", 15.6, "deg"),
                ("2026-10-24", "Dynamic Knee Valgus Angle", 12.1, "deg"),
                ("2026-10-28", "Dynamic Knee Valgus Angle", 10.8, "deg"),
                ("2026-10-05", "Max Sprint Velocity", 31.2, "km/h"),
                ("2026-10-26", "Max Sprint Velocity", 32.8, "km/h"),
                ("2026-10-12", "Acute-to-Chronic Workload (ACWR)", 1.12, "ratio"),
                ("2026-10-27", "Acute-to-Chronic Workload (ACWR)", 1.08, "ratio")
            ]
            for dt, metric, val, unit in perf_records:
                c.execute("""
                    INSERT INTO performance_records (user_id, date, metric, value, unit)
                    VALUES (?, ?, ?, ?, ?)
                """, (target_uid, dt, metric, val, unit))

    conn.commit()
    conn.close()
    print("Migration and seeding completed successfully!")

if __name__ == "__main__":
    run_migration()
