import json
from datetime import datetime
import models

ALL_CLINICAL_TRAINING_PLANS = [
    {
        "plan_id": "throwing-scapular-stability",
        "title": "Scapular & Rotator Cuff Dynamic Stabilization",
        "duration": "4 Weeks",
        "status": "Active",
        "focus": "Scapular Upward Rotation, Rotator Cuff Deceleration & Medial Elbow (UCL) Offloading",
        "target_joint": "Shoulder, Scapulothoracic Axis & Medial Elbow (UCL)",
        "description": "Designed specifically for throwing and overhead projectile athletes (shot put, javelin, baseball, handball) exhibiting elevated shoulder anterior translation or medial elbow valgus stress.",
        "prescribed_exercises": json.dumps([
            "Prone Y-T-W Scapular Stabilizers",
            "Sleeper Stretch & Cross-Body Stretch",
            "Half-Kneeling Rotational Med-Ball Slams",
            "Banded External Rotations at 90°"
        ]),
        "exercises_detail": json.dumps([
            {
                "name": "Prone Y-T-W Scapular Stabilizers",
                "alias": "Prone Scapular Trap & Serratus Protocol",
                "target_muscles": ["Lower Trapezius", "Rhomboids", "Serratus Anterior"],
                "frequency": "4x / week",
                "sets": 3,
                "reps": "12 reps",
                "rest": "45 seconds",
                "tempo": "2-1-2",
                "completed": False,
                "biomechanical_rationale": "Retrains upward scapular rotation and posterior tilt, opening the subacromial space and eliminating anterior glenohumeral shear during maximum external rotation.",
                "form_cues": [
                    "Squeeze shoulder blades down and back before raising arms into Y, T, and W positions.",
                    "Keep cervical spine completely neutral with chin lightly tucked.",
                    "Hold top contraction for 1 second; avoid shrugging through the upper traps."
                ]
            },
            {
                "name": "Sleeper Stretch & Cross-Body Stretch",
                "alias": "Posterior Glenohumeral Capsule Mobilization",
                "target_muscles": ["Posterior Capsule", "Infraspinatus", "Teres Minor"],
                "frequency": "Daily",
                "sets": 3,
                "reps": "30 sec hold",
                "rest": "30 seconds",
                "tempo": "Static Hold",
                "completed": False,
                "biomechanical_rationale": "Restores glenohumeral internal rotation deficit (GIRD) to reduce compensatory elbow valgus stress and prevent superior labral tears.",
                "form_cues": [
                    "Lie on throwing side with elbow flexed to 90 degrees.",
                    "Use opposite hand to gently guide forearm toward floor without forcing through sharp pinch.",
                    "Breathe steadily and relax posterior shoulder musculature."
                ]
            },
            {
                "name": "Half-Kneeling Rotational Med-Ball Slams",
                "alias": "Thoracic-Pelvic Sequential Power Transfer",
                "target_muscles": ["Internal & External Obliques", "Thoracic Spine Rotators", "Gluteals"],
                "frequency": "3x / week",
                "sets": 4,
                "reps": "8 per side",
                "rest": "60 seconds",
                "tempo": "Explosive",
                "completed": False,
                "biomechanical_rationale": "Conditions the oblique sling systems to initiate rotational force from the pelvic core rather than overloading the distal arm and elbow.",
                "form_cues": [
                    "Kneel on the rear throwing knee; lock front foot firmly into the ground.",
                    "Accelerate the ball from the rear hip using torso rotation, slamming down opposite lead hip.",
                    "Decelerate smoothly without collapsing the lumbar spine."
                ]
            },
            {
                "name": "Banded External Rotations at 90°",
                "alias": "High-Velocity Deceleration Loading",
                "target_muscles": ["Infraspinatus", "Teres Minor", "Posterior Deltoid"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "15 reps",
                "rest": "45 seconds",
                "tempo": "3-0-1",
                "completed": False,
                "biomechanical_rationale": "Enhances eccentric braking capacity of posterior rotator cuff to resist distraction forces at ball release.",
                "form_cues": [
                    "Maintain elbow abducted at 90 degrees with arm parallel to ground.",
                    "Rotate forearm upward against band resistance; control the 3-second descent.",
                    "Keep scapula stabilized against rib cage."
                ]
            }
        ]),
        "weekly_schedule": json.dumps([
            {"week": "Week 1", "objective": "Scapular Positioning & Posterior Capsule Mobility", "intensity": "Bodyweight & light band resistance; focus on neuromuscular activation."},
            {"week": "Week 2", "objective": "Loaded Rotator Cuff Deceleration & Isometric Holds", "intensity": "Medium band tension; 2-second hold at end-range external rotation."},
            {"week": "Week 3", "objective": "Thoracic-Pelvic Kinetic Sequencing", "intensity": "4kg medicine ball rotational throws with maximum velocity."},
            {"week": "Week 4", "objective": "Sport-Specific Release Simulation & Perturbation", "intensity": "Dynamic deceleration catch drills under fatigue."}
        ]),
        "clinical_notes": "Prescribed following elevated shoulder anterior translation and medial elbow distraction shear during throwing movement analysis.",
        "progress_percent": 0
    },
    {
        "plan_id": "knee-valgus",
        "title": "Knee Valgus Correction & Dynamic Hip Abduction",
        "duration": "4 Weeks",
        "status": "Active",
        "focus": "Dynamic Knee Valgus (FPPA) Prevention & Gluteus Medius Motor Re-Education",
        "target_joint": "Patellofemoral Joint, Anterior Cruciate Ligament (ACL) & Hip Complex",
        "description": "Targets frontal plane medial knee collapse during squatting, decelerations, and jump landings. Strengthens hip external rotators to stabilize the femoral-tibial axis.",
        "prescribed_exercises": json.dumps([
            "Banded Monster Walks & Side Steps",
            "Single Leg Romanian Deadlifts",
            "Goblet Squats with Resistance Band around Knees",
            "Knee-to-Wall Ankle Dorsiflexion Mobilization"
        ]),
        "exercises_detail": json.dumps([
            {
                "name": "Banded Monster Walks & Side Steps",
                "alias": "Lateral Monster Walks",
                "target_muscles": ["Gluteus Medius", "Gluteus Minimus", "Tensor Fasciae Latae"],
                "frequency": "4x / week",
                "sets": 3,
                "reps": "15 steps each direction",
                "rest": "45 seconds",
                "tempo": "2-0-2",
                "completed": False,
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
                "tempo": "3-1-1",
                "completed": False,
                "biomechanical_rationale": "Develops unilateral eccentric hamstring tension, essential for absorbing anterior tibial shear force and protecting the ACL during deceleration.",
                "form_cues": [
                    "Maintain a soft 15-20° bend in the stance knee throughout.",
                    "Drive non-working heel straight back towards the rear wall.",
                    "Keep pelvis level and square to the ground without rotating the hip open."
                ]
            },
            {
                "name": "Goblet Squats with Resistance Band around Knees",
                "alias": "RNT Squat Re-Patterning",
                "target_muscles": ["Vastus Medialis Oblique", "Gluteus Medius", "Quadriceps"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "12 reps",
                "rest": "60 seconds",
                "tempo": "3-1-1",
                "completed": False,
                "biomechanical_rationale": "Provides reactive neuromuscular training (RNT) proprioceptive biofeedback against dynamic inward knee collapse.",
                "form_cues": [
                    "Hold dumbbell or kettlebell tight to chest.",
                    "Push knees outward actively against the band at parallel depth.",
                    "Distribute weight evenly across heel, 1st and 5th metatarsals (tripod foot)."
                ]
            },
            {
                "name": "Knee-to-Wall Ankle Dorsiflexion Mobilization",
                "alias": "Talocrural Joint Mobilization",
                "target_muscles": ["Soleus", "Gastrocnemius", "Talocrural Joint Capsule"],
                "frequency": "Daily",
                "sets": 3,
                "reps": "10 reps per leg",
                "rest": "30 seconds",
                "tempo": "Static hold",
                "completed": False,
                "biomechanical_rationale": "Restores closed-chain ankle dorsiflexion to prevent compensatory knee pronation and excessive trunk pitch.",
                "form_cues": [
                    "Position toes 4-5 inches from wall.",
                    "Drive knee directly forward over 2nd toe touching wall without lifting heel.",
                    "Ensure foot arch does not collapse medially."
                ]
            }
        ]),
        "weekly_schedule": json.dumps([
            {"week": "Week 1", "objective": "Neuromuscular Activation & Baseline Form Calibration", "intensity": "Light band tension, focus on perfect joint alignment."},
            {"week": "Week 2", "objective": "Loaded Hip Abduction & Isometric End-Range Holds", "intensity": "Medium band tension, 2-second hold at end range."},
            {"week": "Week 3", "objective": "Eccentric Deceleration & Added External Load", "intensity": "Add 6-8kg dumbbell to single-leg RDL."},
            {"week": "Week 4", "objective": "Dynamic Cutting Reassessment & Sport-Specific Perturbations", "intensity": "Reactive lateral bounds with stick landing."}
        ]),
        "clinical_notes": "Prescribed following motion capture indicating an 18.4° valgus excursion during cutting deceleration.",
        "progress_percent": 0
    },
    {
        "plan_id": "sprint-hamstring-resilience",
        "title": "High-Velocity Hamstring Eccentric Resilience",
        "duration": "4 Weeks",
        "status": "Active",
        "focus": "Biceps Femoris Deceleration, Pelvic Neutral & High-Knee Cadence",
        "target_joint": "Biceps Femoris, Ischial Tuberosity & Anterior Pelvic Tilt",
        "description": "Formulated for sprint acceleration and maximum velocity maintenance. Develops high-velocity eccentric capacity in the long head of the biceps femoris to shield against acute strain tears during terminal swing phase.",
        "prescribed_exercises": json.dumps([
            "Nordic Hamstring Curls",
            "A-Skips & High Knee Wall Drills",
            "Heavy Single-Leg Hip Thrusts",
            "Suitcase Single-Arm Carries"
        ]),
        "exercises_detail": json.dumps([
            {
                "name": "Nordic Hamstring Curls",
                "alias": "Eccentric Hamstring Lengthening Protocol",
                "target_muscles": ["Biceps Femoris (Long Head)", "Semitendinosus", "Semimembranosus"],
                "frequency": "2x / week",
                "sets": 3,
                "reps": "6-8 reps",
                "rest": "90 seconds",
                "tempo": "4-0-1",
                "completed": False,
                "biomechanical_rationale": "Gold-standard intervention proven to shift muscle optimal fascicle length to longer muscle lengths, drastically mitigating strain injuries during high-velocity sprint deceleration.",
                "form_cues": [
                    "Maintain completely straight alignment from knees through hips to shoulders.",
                    "Control the descent as slowly as possible without bending at the waist.",
                    "Catch lightly with hands on floor and push back up smoothly."
                ]
            },
            {
                "name": "A-Skips & High Knee Wall Drills",
                "alias": "Sprint Mechanical Rhythm & Knee Drive",
                "target_muscles": ["Iliopsoas", "Rectus Femoris", "Anterior Core"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "20 meters",
                "rest": "45 seconds",
                "tempo": "Dynamic Rhythm",
                "completed": False,
                "biomechanical_rationale": "Reinforces front-side sprint mechanics, reducing overstriding and terminal hamstring stretch strain.",
                "form_cues": [
                    "Drive lead knee forcefully to 90 degrees with dorsal foot flexed upward.",
                    "Strike the ground directly underneath your center of mass with ball of foot.",
                    "Keep torso upright with engaged core cylinder."
                ]
            },
            {
                "name": "Heavy Single-Leg Hip Thrusts",
                "alias": "Terminal Hip Extension Drive",
                "target_muscles": ["Gluteus Maximus", "Upper Hamstring Origin"],
                "frequency": "3x / week",
                "sets": 4,
                "reps": "8 reps per leg",
                "rest": "60 seconds",
                "tempo": "2-1-2",
                "completed": False,
                "biomechanical_rationale": "Recruits gluteus maximus as primary hip extensor, offloading synergistic dominance from the hamstrings.",
                "form_cues": [
                    "Upper back rests on bench; non-working leg elevated at 90 degrees.",
                    "Drive working heel into ground until hip reaches full extension.",
                    "Pause for 1 second at top with neutral pelvis; avoid arching lumbar spine."
                ]
            },
            {
                "name": "Suitcase Single-Arm Carries",
                "alias": "Anti-Lateral Flexion Core & Pelvic Lock",
                "target_muscles": ["Quadratus Lumborum", "Internal Obliques", "Hip Abductors"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "40 meters per side",
                "rest": "60 seconds",
                "tempo": "Brisk Walk",
                "completed": False,
                "biomechanical_rationale": "Prevents contralateral pelvic drop during high-speed unilateral footstrike.",
                "form_cues": [
                    "Hold heavy dumbbell or kettlebell in one hand.",
                    "Walk tall without allowing torso to lean toward or away from the weight.",
                    "Maintain steady diaphragmatic nasal breathing."
                ]
            }
        ]),
        "weekly_schedule": json.dumps([
            {"week": "Week 1", "objective": "Submaximal Eccentric Conditioning", "intensity": "Assisted Nordic curls with resistance band, focus on 4-second tempo."},
            {"week": "Week 2", "objective": "Unassisted Eccentric Overload", "intensity": "Bodyweight Nordic curls to 45° angle before catch."},
            {"week": "Week 3", "objective": "High-Velocity Hip Extension Synergy", "intensity": "Add load to hip thrusts; sprint bounding drills."},
            {"week": "Week 4", "objective": "Full Range Deceleration Verification", "intensity": "Full-speed flying 20m sprint evaluations."}
        ]),
        "clinical_notes": "Prescribed for high swing velocity with insufficient eccentric braking capacity and excessive forward pelvic tilt.",
        "progress_percent": 0
    },
    {
        "plan_id": "landing-shock-absorption",
        "title": "Vertical Shock Attenuation & Soft Landing Mechanics",
        "duration": "3 Weeks",
        "status": "Active",
        "focus": "Eccentric Knee Deceleration (>45° Flexion), Bilateral Touchdown Symmetry & ACL Shielding",
        "target_joint": "Knee Joint Complex, Menisci & Ankle Mortise",
        "description": "Designed for athletes exhibiting stiff-legged touchdown deceleration (>2.0 G). Re-trains deep knee flexion cushioning and equal bilateral weight distribution upon contact.",
        "prescribed_exercises": json.dumps([
            "Depth Drops to Athletic Catch Position",
            "Single-Leg Box Step Downs",
            "Banded Lateral Pogo Jumps",
            "Broad Jump to Stick Landing"
        ]),
        "exercises_detail": json.dumps([
            {
                "name": "Depth Drops to Athletic Catch Position",
                "alias": "Drop Landing Motor Re-Education",
                "target_muscles": ["Quadriceps", "Gluteals", "Gastrocnemius"],
                "frequency": "3x / week",
                "sets": 4,
                "reps": "6 drops from 30cm",
                "rest": "60 seconds",
                "tempo": "Controlled Catch",
                "completed": False,
                "biomechanical_rationale": "Re-educates neuromuscular pre-activation and immediate eccentric knee flexion (>45°) upon contact to dissipate ground reaction forces muscularly.",
                "form_cues": [
                    "Step off box (do not jump up); drop vertically.",
                    "Land softly on ball of foot and immediately sink into a deep athletic quarter/half squat.",
                    "Aim for completely silent touchdown; freeze catch for 2 seconds."
                ]
            },
            {
                "name": "Single-Leg Box Step Downs",
                "alias": "Eccentric Knee Deceleration Alignment",
                "target_muscles": ["Vastus Medialis Oblique", "Gluteus Medius"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "10 reps per side",
                "rest": "45 seconds",
                "tempo": "3-1-1",
                "completed": False,
                "biomechanical_rationale": "Eliminates inward knee valgus collapse during unilateral deceleration loading.",
                "form_cues": [
                    "Stand on 6-inch step on one foot.",
                    "Slowly lower opposite heel to floor for 3 seconds while bending stance knee.",
                    "Ensure stance knee tracks directly over 2nd toe without wavering inward."
                ]
            },
            {
                "name": "Banded Lateral Pogo Jumps",
                "alias": "Reactive Ankle Stiffness & Rebound",
                "target_muscles": ["Achilles Tendon", "Plantar Flexors", "Peroneals"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "20 reps",
                "rest": "45 seconds",
                "tempo": "Elastic Rebound",
                "completed": False,
                "biomechanical_rationale": "Optimizes reactive tendon stiffness to prevent ankle collapse upon multi-directional landing impacts.",
                "form_cues": [
                    "Loop light resistance band around ankles.",
                    "Perform quick, bouncy lateral hops with minimal ground contact time.",
                    "Keep knees soft and aligned."
                ]
            },
            {
                "name": "Broad Jump to Stick Landing",
                "alias": "Horizontal Deceleration Force Absorption",
                "target_muscles": ["Hamstrings", "Gluteus Maximus", "Quadriceps"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "5 reps",
                "rest": "60 seconds",
                "tempo": "Explosive + Hold",
                "completed": False,
                "biomechanical_rationale": "Dissipates horizontal kinetic momentum into vertical muscular damping, protecting the ACL from anterior tibial translation.",
                "form_cues": [
                    "Jump forward explosively from both feet.",
                    "Absorb landing into deep squat with chest up and knees wide.",
                    "Hold landing completely motionless for 3 seconds."
                ]
            }
        ]),
        "weekly_schedule": json.dumps([
            {"week": "Week 1", "objective": "Soundless Bilateral Catch Mechanics", "intensity": "Low box depth drops (20cm), emphasis on knee flexion angle."},
            {"week": "Week 2", "objective": "Increased Deceleration Height & Unilateral Deceleration", "intensity": "30cm depth drops and single-leg box step downs."},
            {"week": "Week 3", "objective": "Multi-Directional Perturbation & Reaction", "intensity": "Broad jump to stick landing with visual catch cues."}
        ]),
        "clinical_notes": "Prescribed for stiff-legged landing impact deceleration (>2.0 G) and asymmetrical touchdown timing.",
        "progress_percent": 0
    },
    {
        "plan_id": "cutting-acl-protection",
        "title": "Multi-Planar Deceleration & ACL Cutting Shield",
        "duration": "4 Weeks",
        "status": "Active",
        "focus": "Center of Mass Lowering, Narrow Lateral Plant Width & Copenhagen Groin Strength",
        "target_joint": "Anterior Cruciate Ligament (ACL), Adductor Longus & Lateral Meniscus",
        "description": "Protects against non-contact ACL tears during rapid multi-directional cuts and agility transitions. Focuses on low center of gravity, knee-over-toe alignment, and groin resilience.",
        "prescribed_exercises": json.dumps([
            "90-Degree Cut Deceleration Drill",
            "Banded Lateral Skater Hops with Stick",
            "Copenhagen Adductor Planks",
            "Paloff Press Core Anti-Rotation"
        ]),
        "exercises_detail": json.dumps([
            {
                "name": "90-Degree Cut Deceleration Drill",
                "alias": "Agility Plant & Directional Transfer",
                "target_muscles": ["Gluteus Medius", "Quadriceps", "Biceps Femoris"],
                "frequency": "3x / week",
                "sets": 4,
                "reps": "4 cuts per side",
                "rest": "60 seconds",
                "tempo": "Progressive Speed",
                "completed": False,
                "biomechanical_rationale": "Teaches preparatory deceleration 2 steps prior to plant, preventing excessive knee abduction moments and lateral foot over-reaching.",
                "form_cues": [
                    "Lower center of mass by bending hips and knees 2 steps before the plant.",
                    "Keep plant foot within 15-20% of hip width; avoid reaching wide.",
                    "Ensure knee stays aligned over toes throughout directional push-off."
                ]
            },
            {
                "name": "Banded Lateral Skater Hops with Stick",
                "alias": "Frontal Plane Single-Leg Deceleration",
                "target_muscles": ["Gluteus Medius", "Vastus Lateralis", "Anterior Tibialis"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "8 reps per side",
                "rest": "60 seconds",
                "tempo": "Dynamic + Hold",
                "completed": False,
                "biomechanical_rationale": "Develops unilateral frontal plane braking force capacity and eliminates medial knee cave during direction changes.",
                "form_cues": [
                    "Bound sideways off inside leg, landing softly on outside single foot.",
                    "Hinge at the hip and stick the landing with knee aligned over foot.",
                    "Freeze motionless for 2 full seconds before next hop."
                ]
            },
            {
                "name": "Copenhagen Adductor Planks",
                "alias": "Eccentric Groin Resilience Protocol",
                "target_muscles": ["Adductor Longus", "Adductor Magnus", "Gracilis"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "25 sec hold per side",
                "rest": "60 seconds",
                "tempo": "Isometric",
                "completed": False,
                "biomechanical_rationale": "High-level eccentric groin strengthening proven to reduce adductor strains and stabilize the medial knee kinetic chain.",
                "form_cues": [
                    "Side plank position with top ankle resting on a bench (knee height).",
                    "Elevate hips into straight line, lifting bottom leg up toward bottom of bench.",
                    "Maintain tight abdominal bracing; do not let hips sag."
                ]
            },
            {
                "name": "Paloff Press Core Anti-Rotation",
                "alias": "Anti-Rotation Core Cylinder",
                "target_muscles": ["Internal & External Obliques", "Transverse Abdominis"],
                "frequency": "3x / week",
                "sets": 3,
                "reps": "12 reps per side",
                "rest": "45 seconds",
                "tempo": "2-2-2",
                "completed": False,
                "biomechanical_rationale": "Resists trunk rotational torque during lateral cutting, preventing the torso from twisting away from the planted knee.",
                "form_cues": [
                    "Athletic stance perpendicular to cable/resistance band.",
                    "Hold handle at sternum; press straight out in front of chest.",
                    "Hold for 2 seconds without allowing band to twist torso; return slowly."
                ]
            }
        ]),
        "weekly_schedule": json.dumps([
            {"week": "Week 1", "objective": "Frontal Plane Deceleration & Adductor Strength", "intensity": "Skater hops with 3-second stick and bent-knee Copenhagen holds."},
            {"week": "Week 2", "objective": "Rotational Core Bracing & Narrow Plant Geometry", "intensity": "Paloff press progression & 45-degree angle deceleration cuts."},
            {"week": "Week 3", "objective": "Full 90-Degree Reactive Cutting Drills", "intensity": "Submaximal agility ladder and cone cut drills."},
            {"week": "Week 4", "objective": "Maximum Velocity Sport Agility Reassessment", "intensity": "Full speed reactive direction changes."}
        ]),
        "clinical_notes": "Prescribed for lateral plant wide base of support and lack of preparatory deceleration.",
        "progress_percent": 0
    },
    {
        "plan_id": "core-stability",
        "title": "Core Stability & Anti-Rotation Cylinder",
        "duration": "Ongoing",
        "status": "Active",
        "focus": "Anti-Extension Lumbopelvic Bracing & Rotational Energy Transfer",
        "target_joint": "Lumbar Spine, Pelvis & Thoracolumbar Fascia",
        "description": "Foundation trunk stiffness protocol to eliminate rotational energy leaks and preserve neutral pelvic alignment during complex multi-planar drills.",
        "prescribed_exercises": json.dumps([
            "Deadbugs & Bird-Dogs",
            "Lateral Monster Band Walks",
            "Farmer's Carries",
            "Forearm Anti-Extension Planks"
        ]),
        "exercises_detail": json.dumps([
            {
                "name": "Deadbugs & Bird-Dogs",
                "alias": "McGill Big 3 Lumbopelvic Bracing",
                "target_muscles": ["Transverse Abdominis", "Multifidus", "Erector Spinae"],
                "frequency": "Daily",
                "sets": 3,
                "reps": "10 reps each",
                "rest": "45 seconds",
                "tempo": "2-2-2",
                "completed": False,
                "biomechanical_rationale": "Builds endurance in deep spinal stabilizers while moving reciprocal extremities, keeping lumbar disc shear near zero.",
                "form_cues": [
                    "Keep spine completely neutral; do not allow lower back to arch or rotate.",
                    "Reach opposite arm and leg out long, not high.",
                    "Maintain 360-degree intra-abdominal pressure throughout."
                ]
            },
            {
                "name": "Lateral Monster Band Walks",
                "alias": "Hip Abductor Cylinder Endurance",
                "target_muscles": ["Gluteus Medius", "Gluteus Minimus", "TFL"],
                "frequency": "4x / week",
                "sets": 3,
                "reps": "15 steps per side",
                "rest": "45 seconds",
                "tempo": "2-0-2",
                "completed": False,
                "biomechanical_rationale": "Maintains constant tension on the hip abductor complex, eliminating coronal plane pelvic wobble.",
                "form_cues": [
                    "Band around mid-foot or above knees.",
                    "Maintain quarter-squat hinge; keep feet pointing straight ahead.",
                    "Step deliberately with control; never let feet snap together."
                ]
            },
            {
                "name": "Farmer's Carries",
                "alias": "Heavy Unilateral/Bilateral Load Carriage",
                "target_muscles": ["Full Core Cylinder", "Trapezius", "Forearm Grip"],
                "frequency": "3x / week",
                "sets": 4,
                "reps": "40 meters",
                "rest": "60 seconds",
                "tempo": "Steady Walk",
                "completed": False,
                "biomechanical_rationale": "Creates high axial core stiffness and trains anti-lateral flexion under heavy kinetic load.",
                "form_cues": [
                    "Pick up heavy weights with flat back and braced core.",
                    "Walk smoothly with tall posture and level shoulders.",
                    "Avoid side-to-side torso sway or pelvic swaying."
                ]
            },
            {
                "name": "Forearm Anti-Extension Planks",
                "alias": "RKC High-Tension Plank",
                "target_muscles": ["Rectus Abdominis", "Internal Obliques", "Serratus Anterior"],
                "frequency": "Daily",
                "sets": 4,
                "reps": "45 - 60 sec hold",
                "rest": "45 seconds",
                "tempo": "Maximal Tension",
                "completed": False,
                "biomechanical_rationale": "Prevents anterior pelvic tilt and shields lumbar vertebrae from extension shear.",
                "form_cues": [
                    "Drive forearms into turf to engage serratus anterior.",
                    "Tuck tailbone slightly into neutral posterior pelvic tilt.",
                    "Squeeze glutes and quadriceps continuously."
                ]
            }
        ]),
        "weekly_schedule": json.dumps([
            {"phase": "Foundation Phase", "objective": "Static Bracing & Intra-Abdominal Pressure", "intensity": "Bodyweight holds focusing on 360° breathing."},
            {"phase": "Rotational Phase", "objective": "Multi-Planar Torque & Deceleration Tolerance", "intensity": "Introduce resistance band Paloff holds and farmer's carries."},
            {"phase": "Reactive Phase", "objective": "High-Velocity Power Transfer", "intensity": "Dynamic medicine ball rotational throws and perturbation drills."}
        ]),
        "clinical_notes": "Maintains pelvic neutral during sprint top-speed phases and complex sport drills.",
        "progress_percent": 0
    },
    {
        "plan_id": "post-match-recovery",
        "title": "Post-Match Recovery & Tissue Regeneration",
        "duration": "1 Day",
        "status": "Active",
        "focus": "Metabolic Clearance, Myofascial Downregulation & Cryotherapy",
        "target_joint": "Systemic Musculoskeletal & Neuromuscular Axis",
        "description": "Acute post-match regeneration regimen designed to expedite lactate and metabolite clearance, relieve hypertonic muscle spasm, and lower inflammatory cytokines within 24 hours.",
        "prescribed_exercises": json.dumps([
            "Full Body Foam Rolling",
            "Light Dynamic Stretching & Joint Mobilization",
            "Cold Plunge & Cryotherapy Contrast Immersion"
        ]),
        "exercises_detail": json.dumps([
            {
                "name": "Full Body Foam Rolling",
                "alias": "Self-Myofascial Release (SMR)",
                "target_muscles": ["Calves", "Hamstrings", "Quadriceps", "IT Bands", "Thoracic Spine"],
                "frequency": "Post-match",
                "sets": 1,
                "reps": "20 minutes",
                "rest": "None",
                "tempo": "Slow Rolling",
                "completed": False,
                "biomechanical_rationale": "Stimulates mechanoreceptors to reduce neuromuscular tone, improve short-term range of motion, and reduce delayed onset muscle soreness (DOMS).",
                "form_cues": [
                    "Roll slowly along the muscle belly, pausing 30-45s on tender trigger points.",
                    "Avoid rolling directly over bony prominences or knee joints.",
                    "Breathe deeply into diaphragm to downregulate sympathetic tone."
                ]
            },
            {
                "name": "Light Dynamic Stretching & Joint Mobilization",
                "alias": "Active Restorative Mobility Flow",
                "target_muscles": ["Hip Flexors", "Thoracic Spine", "Adductors", "Soleus"],
                "frequency": "Post-match",
                "sets": 1,
                "reps": "15 minutes",
                "rest": "None",
                "tempo": "Gentle Flow",
                "completed": False,
                "biomechanical_rationale": "Enhances microcirculation and re-aligns collagen fibrils post-exertion.",
                "form_cues": [
                    "Perform low-intensity flowing movements (world's greatest stretch, cat-cow, 90/90 hip flow).",
                    "Never force into painful end-ranges; emphasize gentle relaxation.",
                    "Synchronize movement rhythm with smooth nasal exhalations."
                ]
            },
            {
                "name": "Cold Plunge & Cryotherapy Contrast Immersion",
                "alias": "Hydrotherapy Vascular Pump Protocol",
                "target_muscles": ["Systemic Vascular System", "Peripheral Musculature"],
                "frequency": "Post-match",
                "sets": 3,
                "reps": "3 min cold / 2 min warm",
                "rest": "Immediate transition",
                "tempo": "Contrast Immersion",
                "completed": False,
                "biomechanical_rationale": "Alternates vasoconstriction and vasodilation to create a natural vascular pump, flushing interstitial edema and speeding recovery.",
                "form_cues": [
                    "Cold immersion at 10-12°C for 3 minutes.",
                    "Warm shower/whirlpool at 38°C for 2 minutes.",
                    "Complete 3 cycles, always finishing on cold to limit post-exercise inflammation."
                ]
            }
        ]),
        "weekly_schedule": json.dumps([
            {"phase": "Acute Regeneration", "objective": "Metabolic Waste Clearance", "intensity": "Passive recovery and cold water immersion."},
            {"phase": "Tissue Normalization", "objective": "Restoring Resting Muscle Length", "intensity": "Gentle foam rolling and dynamic stretching."}
        ]),
        "clinical_notes": "Accelerates return-to-play timeline by 36% following high-intensity matches.",
        "progress_percent": 0
    }
]


def ensure_user_training_plans(db, user_id: int):
    """
    Ensures that the user has all 8 clinical training plans seeded and synchronized.
    Preserves existing progress and completions.
    """
    catalog_by_id = {p["plan_id"]: p for p in ALL_CLINICAL_TRAINING_PLANS}
    user_plans = db.query(models.TrainingPlan).filter(models.TrainingPlan.user_id == user_id).all()
    existing_plans = {p.plan_id: p for p in user_plans}
    now_str = datetime.utcnow().isoformat()

    added = False
    for plan_id, catalog_plan in catalog_by_id.items():
        if plan_id not in existing_plans:
            np = models.TrainingPlan(
                user_id=user_id,
                plan_id=catalog_plan["plan_id"],
                title=catalog_plan["title"],
                duration=catalog_plan["duration"],
                status=catalog_plan["status"],
                focus=catalog_plan["focus"],
                target_joint=catalog_plan["target_joint"],
                description=catalog_plan["description"],
                prescribed_exercises=catalog_plan["prescribed_exercises"],
                exercises_detail=catalog_plan["exercises_detail"],
                weekly_schedule=catalog_plan["weekly_schedule"],
                clinical_notes=catalog_plan["clinical_notes"],
                progress_percent=catalog_plan["progress_percent"],
                created_at=now_str,
                updated_at=now_str
            )
            db.add(np)
            added = True
        else:
            # Plan exists; verify it has rich exercises_detail
            existing = existing_plans[plan_id]
            needs_update = False
            try:
                curr_exercises = json.loads(existing.exercises_detail) if existing.exercises_detail else []
            except Exception:
                curr_exercises = []
            
            cat_exercises = json.loads(catalog_plan["exercises_detail"])
            if len(curr_exercises) < len(cat_exercises):
                # Merge completed statuses from curr_exercises into cat_exercises
                completed_names = {e.get("name", "").lower() for e in curr_exercises if e.get("completed")}
                for e in cat_exercises:
                    if e.get("name", "").lower() in completed_names:
                        e["completed"] = True
                existing.exercises_detail = json.dumps(cat_exercises)
                existing.prescribed_exercises = catalog_plan["prescribed_exercises"]
                existing.weekly_schedule = catalog_plan["weekly_schedule"]
                existing.clinical_notes = catalog_plan["clinical_notes"]
                existing.focus = catalog_plan["focus"]
                existing.target_joint = catalog_plan["target_joint"]
                existing.description = catalog_plan["description"]
                existing.title = catalog_plan["title"]
                needs_update = True
                
            if needs_update:
                added = True

    if added:
        db.commit()
        user_plans = db.query(models.TrainingPlan).filter(models.TrainingPlan.user_id == user_id).all()

    return user_plans
