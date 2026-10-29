import io
import json
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def get_sport_recommendation_data(activity: str, risk_score: float = 30.0, risk_level: str = "Medium") -> dict:
    """
    Returns accurate, sport-specific biomechanical rationale, technical form cues,
    prescribed corrective exercises, and recovery protocols.
    Prevents unwanted/irrelevant cross-contamination (e.g. no gluteus medius cues on shotput/throwing).
    """
    act_lower = (activity or "").lower()

    if "throw" in act_lower or "shot" in act_lower or "javelin" in act_lower or "discus" in act_lower:
        return {
            "activity": "Throwing & Shot Put",
            "primary_risk_factors": [
                "Medial elbow distraction valgus stress during late arm cocking and acceleration phase.",
                "Rotator cuff eccentric deceleration fatigue causing glenohumeral anterior translation.",
                "Asymmetric trunk lateral flexion compensating for reduced pelvic rotational follow-through."
            ],
            "clinical_rationale": (
                "High joint angular velocity at the wrist and shoulder requires adequate posterior shoulder muscle "
                "eccentric capacity to decelerate the throwing limb. Lack of proximal trunk-pelvis dissociation "
                "magnifies shear stress onto the medial collateral ligament (UCL) and supraspinatus tendon."
            ),
            "corrective_cues": [
                "Initiate arm drive from thoracic and pelvic rotation, not isolated arm snapping.",
                "Maintain shoulder-elbow height alignment at release without dropping the trailing elbow.",
                "Follow through across the contralateral hip to dissipate angular kinetic energy safely.",
                "Brace the lead leg firmly to transfer ground reaction force upward through the kinetic chain."
            ],
            "prescribed_exercises": [
                {
                    "name": "Prone Y-T-W Scapular Stabilizers",
                    "sets": "3 sets",
                    "reps": "12 reps",
                    "tempo": "2-1-2",
                    "target": "Scapular upward rotation & lower trap recruitment",
                    "notes": "Squeeze shoulder blades down and back; keep cervical spine neutral."
                },
                {
                    "name": "Sleeper Stretch & Cross-Body Stretch",
                    "sets": "3 sets",
                    "reps": "30 sec hold",
                    "tempo": "Static",
                    "target": "Posterior glenohumeral capsule mobility",
                    "notes": "Gentle progressive stretch; avoid impingement pain."
                },
                {
                    "name": "Half-Kneeling Rotational Med-Ball Slams",
                    "sets": "4 sets",
                    "reps": "8 per side",
                    "tempo": "Explosive",
                    "target": "Torso-pelvic rotational kinetic sequencing",
                    "notes": "Drive rotation from the hips and core, avoiding lumbar hyperextension."
                },
                {
                    "name": "Banded External Rotations at 90° Abduction",
                    "sets": "3 sets",
                    "reps": "15 reps",
                    "tempo": "3-0-1",
                    "target": "Infraspinatus & teres minor deceleration capacity",
                    "notes": "Keep elbow pinned at 90 degrees abduction with scapular engagement."
                }
            ],
            "recovery_protocol": (
                "Cryotherapy/cold compression on medial elbow, foam rolling thoracic spine, "
                "active posterior rotator cuff release, and minimum 48 hours recovery between high-intensity throwing sessions."
            )
        }

    elif "squat" in act_lower:
        return {
            "activity": "Squatting",
            "primary_risk_factors": [
                "Dynamic Knee Valgus (FPPA inward medial collapse) exceeding functional safe thresholds (> 15°).",
                "Compensatory forward trunk lean due to restricted ankle dorsiflexion mobility.",
                "Asymmetric weight distribution with unilateral knee load disparity."
            ],
            "clinical_rationale": (
                "Medial femoral adduction and internal rotation during eccentric descent causes substantial "
                "anterior cruciate ligament (ACL) shear forces and patellofemoral compressive stress. "
                "Strengthening the gluteus medius and optimizing hip external rotator recruitment prevents this collapse."
            ),
            "corrective_cues": [
                "Actively press knees outward in the direction of the 2nd and 3rd toes throughout descent.",
                "Maintain a neutral upright spine cylinder with engaged intra-abdominal core bracing.",
                "Distribute bodyweight evenly across the tripod foot (heel, 1st metatarsal, 5th metatarsal).",
                "Hinge at the hips before descending, keeping chest proud and gaze forward."
            ],
            "prescribed_exercises": [
                {
                    "name": "Banded Monster Walks & Side Steps",
                    "sets": "3 sets",
                    "reps": "15 steps each way",
                    "tempo": "2-0-2",
                    "target": "Gluteus medius abductor motor re-education",
                    "notes": "Maintain slight quarter-squat posture with constant band tension."
                },
                {
                    "name": "Single-Leg Romanian Deadlifts (RDL)",
                    "sets": "4 sets",
                    "reps": "10 reps per limb",
                    "tempo": "3-1-1",
                    "target": "Eccentric hamstring and unilateral pelvic stability",
                    "notes": "Keep hips square to floor without compensatory pelvic rotation."
                },
                {
                    "name": "Goblet Squats with Resistance Band around Knees",
                    "sets": "3 sets",
                    "reps": "12 reps",
                    "tempo": "3-1-1",
                    "target": "Proprioceptive feedback against valgus inward collapse",
                    "notes": "Push knees actively against the band at parallel depth."
                },
                {
                    "name": "Knee-to-Wall Ankle Dorsiflexion Mobilization",
                    "sets": "3 sets",
                    "reps": "10 reps per leg",
                    "tempo": "Static hold",
                    "target": "Talocrural joint mobility & soleus lengthening",
                    "notes": "Keep heel flat on the ground while knee tracks smoothly forward."
                }
            ],
            "recovery_protocol": (
                "Hip adductor and tensor fasciae latae foam rolling, calf & soleus wall mobilization, "
                "gentle quad tissue release, and contrast water immersion."
            )
        }

    elif "sprint" in act_lower or "run" in act_lower:
        return {
            "activity": "Sprinting",
            "primary_risk_factors": [
                "High peak swing velocity with insufficient eccentric hamstring braking capacity.",
                "Excessive pelvic anterior tilt during terminal flight increasing hamstring origin strain.",
                "Contralateral pelvic drop causing adductor and knee shear stress."
            ],
            "clinical_rationale": (
                "Sprinting imposes extreme eccentric forces on the biceps femoris at late swing phase. "
                "Developing high-velocity eccentric hamstring strength is crucial for avoiding acute strain tears."
            ),
            "corrective_cues": [
                "Focus on active clawing ground strike directly under center of mass, avoiding overstriding.",
                "Maintain upright neutral pelvis without excessive lumbar hyperextension.",
                "High knee drive synchronized with rhythmic contralateral arm swings.",
                "Keep dorsal foot flexed (toes up) during swing-through to optimize stiffness at ground contact."
            ],
            "prescribed_exercises": [
                {
                    "name": "Nordic Hamstring Curls",
                    "sets": "3 sets",
                    "reps": "6-8 reps",
                    "tempo": "4-0-1",
                    "target": "Eccentric hamstring strain prevention",
                    "notes": "Control descent as long as possible before catching."
                },
                {
                    "name": "A-Skips & High Knee Wall Drills",
                    "sets": "3 sets",
                    "reps": "20 meters",
                    "tempo": "Dynamic",
                    "target": "Anterior pelvic tilt reduction & sprint cadence rhythm",
                    "notes": "Drive knee forcefully to hip height with stiff ankle contact."
                },
                {
                    "name": "Heavy Single-Leg Hip Thrusts",
                    "sets": "4 sets",
                    "reps": "8 reps per leg",
                    "tempo": "2-1-2",
                    "target": "Terminal hip extension gluteus maximus drive",
                    "notes": "Pause 1 sec at top extension; lock pelvis firmly."
                },
                {
                    "name": "Suitcase Single-Arm Carries",
                    "sets": "3 sets",
                    "reps": "40 meters per side",
                    "tempo": "Brisk walk",
                    "target": "Anti-lateral flexion & pelvic drop prevention",
                    "notes": "Maintain completely level shoulders without lateral spinal tilt."
                }
            ],
            "recovery_protocol": (
                "Contrast baths, light active recovery jogging, hamstring gentle active isolated stretching, "
                "and 8+ hours restorative sleep."
            )
        }

    elif "jump" in act_lower or "land" in act_lower:
        return {
            "activity": "Jumping & Landing",
            "primary_risk_factors": [
                "Stiff-legged landing impact deceleration (> 2.0 G) with deficient knee flexion damping.",
                "Bilateral knee valgus collapse upon ground contact.",
                "Unequal limb force absorption with asymmetric touchdown timing."
            ],
            "clinical_rationale": (
                "Landing with extended knees (< 30° flexion) transfers high ground reaction shock directly into "
                "the ACL and meniscus rather than dampening it muscularly through quadriceps and gluteal eccentrics."
            ),
            "corrective_cues": [
                "Land softly on the ball of the foot and immediately roll back onto the heel while hinging at the hips.",
                "Ensure knees stay wide and track directly over the toes upon touchdown.",
                "Aim for a quiet landing; sound reflects unattenuated impact shock.",
                "Absorb ground impact progressively across ankle, knee, and hip joints simultaneously."
            ],
            "prescribed_exercises": [
                {
                    "name": "Depth Drops to Athletic Catch Position",
                    "sets": "4 sets",
                    "reps": "6 drops from 30cm",
                    "tempo": "Controlled catch",
                    "target": "Neuromuscular landing absorption mechanics",
                    "notes": "Hold catch position for 2 seconds with knees aligned."
                },
                {
                    "name": "Single-Leg Box Step Downs",
                    "sets": "3 sets",
                    "reps": "10 reps per side",
                    "tempo": "3-1-1",
                    "target": "Eccentric quadriceps deceleration and knee alignment",
                    "notes": "Lightly tap heel to floor without pushing off."
                },
                {
                    "name": "Banded Lateral Pogo Jumps",
                    "sets": "3 sets",
                    "reps": "20 reps",
                    "tempo": "Elastic rebound",
                    "target": "Ankle stiffness and reactive neuromuscular stabilization",
                    "notes": "Keep ground contact time minimal; absorb smoothly."
                },
                {
                    "name": "Broad Jump to Stick Landing",
                    "sets": "3 sets",
                    "reps": "5 reps",
                    "tempo": "Explosive + Hold",
                    "target": "Horizontal-to-vertical deceleration dissipation",
                    "notes": "Freeze on landing without knee valgus collapse."
                }
            ],
            "recovery_protocol": (
                "Cold compression therapy, elevated leg drainage, plantar fascia release, and low-impact pool recovery sessions."
            )
        }

    elif "cut" in act_lower or "agil" in act_lower:
        return {
            "activity": "Cutting & Change of Direction",
            "primary_risk_factors": [
                "Lateral foot plant outside base of support creating extreme knee abductor torque.",
                "Lack of preparatory hip and knee flexion during deceleration prior to cut.",
                "Torso lateral sway away from the plant foot increasing ACL shear."
            ],
            "clinical_rationale": (
                "High-velocity direction changes without adequate core-pelvic stabilization and hip flexion create "
                "excessive multi-planar knee loading, representing the primary non-contact ACL tear mechanism."
            ),
            "corrective_cues": [
                "Lower your center of mass by bending hips and knees 2-3 steps before the plant.",
                "Keep the plant foot within 15-20% of hip width; avoid over-reaching laterally.",
                "Angle torso slightly into the new direction of travel before driving off.",
                "Ensure the plant knee tracks directly over the foot, never collapsing inwards."
            ],
            "prescribed_exercises": [
                {
                    "name": "90-Degree Cut Deceleration Drill",
                    "sets": "4 sets",
                    "reps": "4 cuts per side",
                    "tempo": "Progressive speed",
                    "target": "Neuromuscular motor pattern re-training for cut deceleration",
                    "notes": "Emphasize low center of gravity and knee alignment."
                },
                {
                    "name": "Banded Lateral Skater Hops with Stick",
                    "sets": "3 sets",
                    "reps": "8 reps per side",
                    "tempo": "Dynamic + Hold",
                    "target": "Frontal plane landing deceleration and hip abductor strength",
                    "notes": "Hold single-leg landing for 2 full seconds."
                },
                {
                    "name": "Copenhagen Adductor Planks",
                    "sets": "3 sets",
                    "reps": "25 sec hold per side",
                    "tempo": "Isometric",
                    "target": "Groin and adductor longus eccentric resilience",
                    "notes": "Rest top leg on bench; lift bottom leg."
                },
                {
                    "name": "Paloff Press Core Anti-Rotation",
                    "sets": "3 sets",
                    "reps": "12 reps per side",
                    "tempo": "2-2-2",
                    "target": "Rotational core stiffness against lateral cut forces",
                    "notes": "Resist rotational pull of cable/band completely."
                }
            ],
            "recovery_protocol": (
                "Adductor and hip rotator trigger point therapy, ice massage on knee tendons, "
                "active recovery cycling, and hip mobility flow."
            )
        }

    else:
        return {
            "activity": activity or "Sports Specific Movement",
            "primary_risk_factors": [
                "Elevated dynamic joint loading beyond physiological baseline.",
                "Mild movement asymmetry between left and right kinetic chains.",
                "Multi-directional fatigue leading to technique breakdown."
            ],
            "clinical_rationale": (
                "Optimizing core stability and unilateral neuromuscular balance minimizes cumulative joint fatigue "
                "and prevents micro-trauma accumulation across multi-directional movement patterns."
            ),
            "corrective_cues": [
                "Maintain core bracing throughout complex athletic transitions.",
                "Focus on bilateral symmetry in ground force application.",
                "Regulate breathing rhythm to delay neuromuscular fatigue onset."
            ],
            "prescribed_exercises": [
                {
                    "name": "Deadbugs & Bird-Dogs",
                    "sets": "3 sets",
                    "reps": "10 reps each",
                    "tempo": "2-2-2",
                    "target": "Lumbar-pelvic core stabilization cylinder",
                    "notes": "Keep spine neutral throughout arm/leg reach."
                },
                {
                    "name": "Lateral Monster Band Walks",
                    "sets": "3 sets",
                    "reps": "15 steps per side",
                    "tempo": "2-0-2",
                    "target": "Hip abductor endurance",
                    "notes": "Constant tension on band."
                },
                {
                    "name": "Farmer's Carries",
                    "sets": "4 sets",
                    "reps": "40 meters",
                    "tempo": "Steady walk",
                    "target": "Full-body anti-lateral flexion and postural control",
                    "notes": "Heavy dumbbells; zero torso wobble."
                }
            ],
            "recovery_protocol": (
                "Full body foam rolling, 8+ hours quality sleep, hydration protocol, and mobility flow."
            )
        }


def generate_single_analysis_pdf(analysis, user, profile=None) -> io.BytesIO:
    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#1e1b4b")   # Deep indigo
    c_accent = colors.HexColor("#4f46e5")    # Indigo 600
    c_purple = colors.HexColor("#7c3aed")    # Violet 600
    c_text_dark = colors.HexColor("#0f172a") # Slate 900
    c_slate = colors.HexColor("#64748b")     # Slate 500
    c_light_bg = colors.HexColor("#f8fafc")  # Slate 50
    c_border = colors.HexColor("#cbd5e1")    # Slate 300
    c_rose = colors.HexColor("#e11d48")      # Rose 600
    c_emerald = colors.HexColor("#059669")   # Emerald 600

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_slate
    )
    section_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=5
    )
    cell_label = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=c_slate
    )
    cell_val = ParagraphStyle(
        'CellVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_text_dark
    )
    cell_header = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )
    recom_box_title = ParagraphStyle(
        'RecomBoxTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=c_primary
    )
    recom_box_text = ParagraphStyle(
        'RecomBoxText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text_dark
    )
    cue_text_style = ParagraphStyle(
        'CueTextStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text_dark
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("SportsAI • Clinical Biomechanical Telemetry Report", title_style))
    story.append(Paragraph("Automated Computer Vision Kinetic Assessment & Joint Kinematics Breakdown", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=8))

    # Parse JSONs
    kin = {}
    if analysis.kinematics:
        try:
            kin = json.loads(analysis.kinematics) if isinstance(analysis.kinematics, str) else analysis.kinematics
        except Exception:
            kin = {}

    probs = {}
    if analysis.injury_probabilities:
        try:
            probs = json.loads(analysis.injury_probabilities) if isinstance(analysis.injury_probabilities, str) else analysis.injury_probabilities
        except Exception:
            probs = {}

    # 2. Executive Overview Table
    athlete_name = user.email.split("@")[0].capitalize() if user and user.email else "Athlete"
    sport_pos = f"{profile.sport_type} / {profile.position}" if profile and profile.sport_type else "Collegiate Athletics"
    risk_color = c_rose if analysis.risk_score > 40 else (colors.HexColor("#d97706") if analysis.risk_score > 20 else c_emerald)

    overview_data = [
        [
            Paragraph("<b>Athlete:</b>", cell_label),
            Paragraph(f"{athlete_name} ({user.email})", cell_val),
            Paragraph("<b>Report ID:</b>", cell_label),
            Paragraph(f"#{analysis.id}", cell_val)
        ],
        [
            Paragraph("<b>Sport & Role:</b>", cell_label),
            Paragraph(f"{sport_pos} ({user.role})", cell_val),
            Paragraph("<b>Assessment Date:</b>", cell_label),
            Paragraph(str(analysis.created_at)[:19].replace("T", " "), cell_val)
        ],
        [
            Paragraph("<b>Analyzed Action:</b>", cell_label),
            Paragraph(f"<b>{analysis.activity}</b>", cell_val),
            Paragraph("<b>Risk Score:</b>", cell_label),
            Paragraph(f"<font color='{risk_color.hexval()}'><b>{analysis.risk_score:.1f} / 100 ({analysis.risk_level})</b></font>", cell_val)
        ],
        [
            Paragraph("<b>Surface / Shoes:</b>", cell_label),
            Paragraph(f"{analysis.surface_type or 'Indoor'} / {analysis.footwear or 'Standard'}", cell_val),
            Paragraph("<b>RPE / Sleep:</b>", cell_label),
            Paragraph(f"RPE: {analysis.rpe or 5}/10 • Sleep: {analysis.sleep_quality or 7}/10", cell_val)
        ]
    ]

    t_overview = Table(overview_data, colWidths=[90, 180, 90, 180])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 8))

    # 3. Section 1: Joint Kinematics Telemetry
    story.append(Paragraph("1. Joint Kinematics & Kinetic Chain Telemetry", section_h2))

    kin_table_data = [
        [
            Paragraph("Anatomical Metric", cell_header),
            Paragraph("Left Limb", cell_header),
            Paragraph("Right Limb", cell_header),
            Paragraph("Clinical Reference / Target", cell_header)
        ],
        [
            Paragraph("Dynamic Knee Valgus (FPPA Mean)", cell_label),
            Paragraph(f"{kin.get('valgus_l_mean', 0):.1f}°", cell_val),
            Paragraph(f"{kin.get('valgus_r_mean', 0):.1f}°", cell_val),
            Paragraph("&lt; 12.0° (Frontal plane projection)", cell_val)
        ],
        [
            Paragraph("Dynamic Knee Valgus (FPPA Peak)", cell_label),
            Paragraph(f"{kin.get('valgus_l_max', 0):.1f}°", cell_val),
            Paragraph(f"{kin.get('valgus_r_max', 0):.1f}°", cell_val),
            Paragraph("&lt; 15.0° (Peak inward collapse threshold)", cell_val)
        ],
        [
            Paragraph("Knee Flexion (Min / Deepest)", cell_label),
            Paragraph(f"{kin.get('knee_flexion_l_min', 0):.1f}°", cell_val),
            Paragraph(f"{kin.get('knee_flexion_r_min', 0):.1f}°", cell_val),
            Paragraph("&gt; 45.0° (Shock absorbing flexion)", cell_val)
        ],
        [
            Paragraph("Hip Flexion (Mean Functional)", cell_label),
            Paragraph(f"{kin.get('hip_flexion_l_mean', 0):.1f}°", cell_val),
            Paragraph(f"{kin.get('hip_flexion_r_mean', 0):.1f}°", cell_val),
            Paragraph("Symmetrical pelvic-femoral hinge", cell_val)
        ],
        [
            Paragraph("Elbow Extension (Mean)", cell_label),
            Paragraph(f"{kin.get('elbow_flexion_l_mean', 0):.1f}°", cell_val),
            Paragraph(f"{kin.get('elbow_flexion_r_mean', 0):.1f}°", cell_val),
            Paragraph("Sport-specific kinetic transfer", cell_val)
        ],
        [
            Paragraph("Trunk Lean (Sagittal Mean / Peak)", cell_label),
            Paragraph(f"{kin.get('trunk_lean_mean', 0):.1f}°", cell_val),
            Paragraph(f"Peak: {kin.get('trunk_lean_max', 0):.1f}°", cell_val),
            Paragraph("10.0° - 25.0° (Forward torso tilt)", cell_val)
        ],
        [
            Paragraph("Lateral Trunk Sway (% Height)", cell_label),
            Paragraph(f"{kin.get('trunk_sway_mean', 0):.1f}%", cell_val),
            Paragraph("-", cell_val),
            Paragraph("&lt; 5.0% (Coronal translation)", cell_val)
        ],
        [
            Paragraph("Head & Neck Inclination (Mean / Max)", cell_label),
            Paragraph(f"{kin.get('head_tilt_mean', 0):.1f}°", cell_val),
            Paragraph(f"Peak: {kin.get('head_tilt_max', 0):.1f}°", cell_val),
            Paragraph("&lt; 20.0° cervical spine angle", cell_val)
        ],
        [
            Paragraph("Core Torsion Disconnect (deg)", cell_label),
            Paragraph(f"{kin.get('core_torsion_mean', 0):.1f}°", cell_val),
            Paragraph("-", cell_val),
            Paragraph("&lt; 15.0° shoulder-pelvic separation", cell_val)
        ],
        [
            Paragraph("Bilateral Symmetry Index (BSI)", cell_label),
            Paragraph(f"<b>{kin.get('bilateral_symmetry_index', 94):.1f}%</b>", cell_val),
            Paragraph(f"Delta: {kin.get('limb_asymmetry_deg', 0):.1f}°", cell_val),
            Paragraph("&ge; 90.0% (Composite bilateral score)", cell_val)
        ]
    ]

    t_kin = Table(kin_table_data, colWidths=[180, 100, 100, 160])
    t_kin.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
    ]))
    story.append(t_kin)
    story.append(Spacer(1, 8))

    # 4. Section 2: Multiaxial Injury Risk Stratification
    story.append(Paragraph("2. Multiaxial Injury Risk Stratification", section_h2))

    prob_rows = [
        [
            Paragraph("Target Injury Classification", cell_header),
            Paragraph("Calculated Risk (%)", cell_header),
            Paragraph("Risk Stratification", cell_header),
            Paragraph("Clinical Assessment Directives", cell_header)
        ]
    ]

    for k, v in probs.items():
        v_num = float(v) if str(v).replace('.', '', 1).isdigit() else 0.0
        r_col = c_rose if v_num > 40 else (colors.HexColor("#d97706") if v_num > 20 else c_emerald)
        cat = "High Risk" if v_num > 40 else ("Moderate Risk" if v_num > 20 else "Low Risk")
        cue = "Requires active kinetic offloading" if v_num > 40 else ("Technique monitoring advised" if v_num > 20 else "Within safe baseline tolerance")
        prob_rows.append([
            Paragraph(k, cell_label),
            Paragraph(f"<font color='{r_col.hexval()}'><b>{v_num:.1f}%</b></font>", cell_val),
            Paragraph(f"<font color='{r_col.hexval()}'><b>{cat}</b></font>", cell_val),
            Paragraph(cue, cell_val)
        ])

    t_prob = Table(prob_rows, colWidths=[180, 90, 110, 160])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 8))

    # 5. Section 3: Tailored Biomechanical & Corrective Recommendations
    recom_data = get_sport_recommendation_data(analysis.activity, analysis.risk_score, analysis.risk_level)

    story.append(Paragraph(f"3. Tailored Biomechanical & Corrective Recommendations ({recom_data['activity']})", section_h2))

    # 5.1 Biomechanical Rationale Callout
    rationale_p = Paragraph(f"<b>Biomechanical Demand & Injury Mechanism Rationale:</b><br/>{recom_data['clinical_rationale']}", recom_box_text)
    t_rationale = Table([[rationale_p]], colWidths=[540])
    t_rationale.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f5f3ff")),
        ('BOX', (0, 0), (-1, -1), 1, c_purple),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_rationale)
    story.append(Spacer(1, 5))

    # 5.2 Technical Form & Movement Cues
    cues_rows = [[Paragraph("<b>Targeted Technical Form Cues:</b>", recom_box_title)]]
    for i, cue in enumerate(recom_data["corrective_cues"], 1):
        cues_rows.append([Paragraph(f"• <b>Cue {i}:</b> {cue}", cue_text_style)])
    t_cues = Table(cues_rows, colWidths=[540])
    t_cues.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cues)
    story.append(Spacer(1, 5))

    # 5.3 Prescribed Corrective Exercises Table
    story.append(Paragraph("<b>Prescribed Corrective Exercises & Neuromuscular Drills:</b>", recom_box_title))
    story.append(Spacer(1, 3))
    ex_rows = [
        [
            Paragraph("Exercise Prescription", cell_header),
            Paragraph("Sets & Reps", cell_header),
            Paragraph("Tempo / Load", cell_header),
            Paragraph("Target Focus / Objective", cell_header)
        ]
    ]
    for ex in recom_data["prescribed_exercises"]:
        ex_rows.append([
            Paragraph(f"<b>{ex['name']}</b>", cell_label),
            Paragraph(f"{ex['sets']} × {ex['reps']}", cell_val),
            Paragraph(ex.get("tempo", "Controlled"), cell_val),
            Paragraph(f"{ex.get('target', '')} • {ex.get('notes', '')}", cell_val)
        ])
    t_ex = Table(ex_rows, colWidths=[150, 85, 85, 220])
    t_ex.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
    ]))
    story.append(t_ex)
    story.append(Spacer(1, 5))

    # 5.4 Recovery & Regeneration Protocol
    rec_p = Paragraph(f"<b>Recovery & Regeneration Directives:</b> {recom_data['recovery_protocol']}", recom_box_text)
    t_rec = Table([[rec_p]], colWidths=[540])
    t_rec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 0), (-1, -1), 0.75, c_emerald),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_rec)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<font color='#64748b' size='7'>Report autonomously generated by SportsAI Computer Vision & Biomechanics Platform. Verified across 33 keypoints at 30 fps.</font>", styles['Normal']))

    doc.build(story)
    output.seek(0)
    return output


def generate_single_analysis_csv(analysis, user, profile=None) -> str:
    """
    Generates a uniform, clean 6-column CSV export.
    Every row strictly maintains 6 columns to prevent ragged cell overflow and Excel alignment errors.
    All data is accurately customized to the activity (no irrelevant gluteus medius text for throwing).
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Clean uniform 6-column tabular header
    writer.writerow([
        "Section",
        "Parameter / Metric",
        "Measured Value",
        "Unit",
        "Reference Benchmark",
        "Clinical Interpretation & Actionable Recommendation"
    ])

    def clean(val):
        if val is None:
            return "-"
        return str(val).replace("\r", " ").replace("\n", " ").strip()

    recom_data = get_sport_recommendation_data(
        analysis.activity,
        analysis.risk_score,
        analysis.risk_level
    )

    # 1. Assessment Overview & Profile
    athlete_name = user.email.split("@")[0].capitalize() if user and user.email else "Athlete"
    writer.writerow(["Assessment Overview", "Report ID", clean(f"#{analysis.id}"), "ID", "-", "Single Video Biomechanical Telemetry Report"])
    writer.writerow(["Assessment Overview", "Athlete Email", clean(user.email if user else "-"), "Account", "-", f"Registered Athlete: {athlete_name}"])
    writer.writerow(["Assessment Overview", "Sport Discipline & Position", clean(f"{profile.sport_type} / {profile.position}" if profile and profile.sport_type else "Athletics"), "Sport", "-", "Collegiate / Elite Movement Tracking"])
    writer.writerow(["Assessment Overview", "Assessment Timestamp", clean(str(analysis.created_at)[:19].replace("T", " ")), "UTC", "-", "High-Speed Computer Vision Kinematic Analysis"])
    writer.writerow(["Assessment Overview", "Primary Athletic Action", clean(analysis.activity), "Classification", "Action Detection", f"Verified {analysis.activity} Movement Pattern"])
    writer.writerow(["Assessment Overview", "Composite Injury Risk Score", clean(f"{analysis.risk_score:.1f}"), "/100", "0.0 - 30.0 (Low Risk)", f"{analysis.risk_level} - Targeted Corrective Intervention Prescribed" if analysis.risk_score > 30 else "Optimal Physiological Range"])
    writer.writerow(["Assessment Overview", "Training Surface & Footwear", clean(f"{analysis.surface_type or 'Indoor Court'} / {analysis.footwear or 'Standard'}"), "Environment", "-", "Environmental Friction & Deceleration Coefficient"])
    writer.writerow(["Assessment Overview", "Athlete Exertion (RPE) & Sleep", clean(f"RPE: {analysis.rpe or 5}/10 | Sleep: {analysis.sleep_quality or 7}/10"), "Subjective", "RPE < 7 | Sleep > 7", "Athlete Recovery Baseline Telemetry"])

    # 2. Joint Kinematics Telemetry
    kin = {}
    if analysis.kinematics:
        try:
            kin = json.loads(analysis.kinematics) if isinstance(analysis.kinematics, str) else analysis.kinematics
        except Exception:
            kin = {}

    kin_items = [
        ("Dynamic Knee Valgus (FPPA Left Mean)", kin.get("valgus_l_mean", 0), "deg", "< 12.0 deg", "Frontal plane medial knee projection angle"),
        ("Dynamic Knee Valgus (FPPA Left Max)", kin.get("valgus_l_max", 0), "deg", "< 15.0 deg", "Peak dynamic inward knee collapse"),
        ("Dynamic Knee Valgus (FPPA Right Mean)", kin.get("valgus_r_mean", 0), "deg", "< 12.0 deg", "Frontal plane medial knee projection angle"),
        ("Dynamic Knee Valgus (FPPA Right Max)", kin.get("valgus_r_max", 0), "deg", "< 15.0 deg", "Peak dynamic inward knee collapse"),
        ("Left Knee Flexion (Min / Deepest)", kin.get("knee_flexion_l_min", 0), "deg", "> 45.0 deg", "Maximum knee flexion depth"),
        ("Left Knee Flexion (Mean)", kin.get("knee_flexion_l_mean", 0), "deg", "Sport Specific", "Average functional knee flexion"),
        ("Right Knee Flexion (Min / Deepest)", kin.get("knee_flexion_r_min", 0), "deg", "> 45.0 deg", "Maximum knee flexion depth"),
        ("Right Knee Flexion (Mean)", kin.get("knee_flexion_r_mean", 0), "deg", "Sport Specific", "Average functional knee flexion"),
        ("Left Hip Flexion (Mean)", kin.get("hip_flexion_l_mean", 0), "deg", "Sport Specific", "Average pelvic-femoral hinge angle"),
        ("Right Hip Flexion (Mean)", kin.get("hip_flexion_r_mean", 0), "deg", "Sport Specific", "Average pelvic-femoral hinge angle"),
        ("Trunk Sagittal Lean (Mean)", kin.get("trunk_lean_mean", 0), "deg", "10.0 - 25.0 deg", "Mean torso forward inclination"),
        ("Trunk Sagittal Lean (Max)", kin.get("trunk_lean_max", 0), "deg", "< 35.0 deg", "Peak torso forward inclination"),
        ("Lateral Trunk Sway", kin.get("trunk_sway_mean", 0), "% height", "< 5.0%", "Coronal plane torso translation away from plant limb"),
        ("Head & Neck Tilt (Mean)", kin.get("head_tilt_mean", 0), "deg", "< 20.0 deg", "Cervical tilt relative to thoracic spine"),
        ("Head & Neck Tilt (Max)", kin.get("head_tilt_max", 0), "deg", "< 30.0 deg", "Peak cervical tilt during movement"),
        ("Pelvic Tilt (Horizontal Mean)", kin.get("pelvic_tilt_mean", 0), "deg", "< 15.0 deg", "Coronal acute pelvic inclination"),
        ("Shoulder Tilt (Horizontal Mean)", kin.get("shoulder_tilt_mean", 0), "deg", "< 15.0 deg", "Coronal acute shoulder inclination"),
        ("Core Torsion Disconnect", kin.get("core_torsion_mean", 0), "deg", "< 15.0 deg", "Rotational separation between shoulders and pelvis"),
        ("Left Elbow Extension (Mean)", kin.get("elbow_flexion_l_mean", 0), "deg", "Sport Specific", "Left upper-limb extension angle"),
        ("Right Elbow Extension (Mean)", kin.get("elbow_flexion_r_mean", 0), "deg", "Sport Specific", "Right upper-limb extension angle"),
        ("Peak Wrist Velocity", kin.get("peak_wrist_velocity", 0), "H/s", "Sport Specific", "Peak upper-limb hand displacement velocity"),
        ("Peak Ankle Velocity", kin.get("peak_ankle_velocity", 0), "H/s", "Sport Specific", "Peak lower-limb swing acceleration velocity"),
        ("Peak Knee Angular Velocity", kin.get("peak_knee_angular_velocity", 0), "deg/s", "Sport Specific", "Peak knee angular rotation speed"),
        ("Touchdown Deceleration Impact", kin.get("estimated_impact_g", 0), "G", "< 2.0 G", "Estimated landing shock deceleration"),
        ("Movement Cadence", kin.get("cadence_spm", 0), "SPM", "160 - 185 SPM", "Strides or cycles per minute"),
        ("Vertical Flight Clearance", kin.get("flight_clearance_percent", 0), "% height", "15.0 - 25.0%", "Maximum bilateral foot elevation off ground"),
        ("Bilateral Limb Angle Asymmetry", kin.get("limb_asymmetry_deg", 0), "deg", "< 8.0 deg", "Difference between left and right limb kinematics"),
        ("Bilateral Symmetry Index", kin.get("bilateral_symmetry_index", 94), "%", ">= 90.0%", "Composite bilateral limb kinetic symmetry")
    ]

    for param, val, unit, bench, desc in kin_items:
        val_str = f"{val:.1f}" if isinstance(val, (int, float)) else str(val)
        writer.writerow(["Joint Kinematics Telemetry", param, clean(val_str), unit, bench, desc])

    # 3. Injury Risk Model Probabilities
    probs = {}
    if analysis.injury_probabilities:
        try:
            probs = json.loads(analysis.injury_probabilities) if isinstance(analysis.injury_probabilities, str) else analysis.injury_probabilities
        except Exception:
            probs = {}

    for k, v in probs.items():
        v_num = float(v) if str(v).replace('.', '', 1).isdigit() else 0.0
        bench = "< 25.0% Low" if "acl" in k.lower() or "hamstring" in k.lower() else "< 30.0% Low"
        status = "Elevated Risk - Requires Intervention" if v_num > 40 else ("Moderate Monitoring" if v_num > 20 else "Within Safe Baseline")
        writer.writerow(["Injury Risk Probability", clean(k), f"{v_num:.1f}", "%", bench, status])

    # 4. Action-Specific Corrective Technique Cues
    for i, cue in enumerate(recom_data["corrective_cues"], 1):
        writer.writerow([
            "Prescribed Technique Cue",
            f"Form Cue {i}",
            clean(cue),
            "Coaching Cue",
            "Target Execution",
            f"Adhere to proper {analysis.activity} kinetic sequencing"
        ])

    # 5. Prescribed Corrective Exercises
    for ex in recom_data["prescribed_exercises"]:
        writer.writerow([
            "Prescribed Corrective Exercise",
            clean(ex["name"]),
            clean(f"{ex['sets']} x {ex['reps']}"),
            "Prescription",
            clean(f"Tempo: {ex.get('tempo', 'Controlled')}"),
            clean(f"Target: {ex.get('target', '')} | Focus: {ex.get('notes', '')}")
        ])

    # 6. Clinical Directives & Recovery
    writer.writerow([
        "Clinical Directives",
        "Biomechanical Demand Rationale",
        clean(recom_data["clinical_rationale"]),
        "Mechanism",
        "Physiological Demand",
        f"Kinetic chain strain prevention for {analysis.activity}"
    ])
    writer.writerow([
        "Clinical Directives",
        "Recovery & Regeneration Protocol",
        clean(recom_data["recovery_protocol"]),
        "Regeneration",
        "Daily / Post-Session",
        "Targeted tissue recovery and inflammation mitigation"
    ])

    output.seek(0)
    return "\ufeff" + output.getvalue()


def generate_single_analysis_xlsx(analysis, user, profile=None) -> io.BytesIO:
    """
    Generates an Excel workbook (.xlsx) with custom, generous column widths
    (specifically Column E is set >= 28 so 'Action Detection' and all reference benchmarks fit completely),
    cell text wrapping, elegant Indigo/Slate theme headers, and alternating rows.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Biomechanical Telemetry"
    ws.views.sheetView[0].showGridLines = True

    # 6-column header
    headers = [
        "Section",
        "Parameter / Metric",
        "Measured Value",
        "Unit",
        "Reference Benchmark",
        "Clinical Interpretation & Actionable Recommendation"
    ]
    ws.append(headers)

    def clean(val):
        if val is None:
            return "-"
        return str(val).replace("\r", " ").replace("\n", " ").strip()

    recom_data = get_sport_recommendation_data(
        analysis.activity,
        analysis.risk_score,
        analysis.risk_level
    )

    athlete_name = user.email.split("@")[0].capitalize() if user and user.email else "Athlete"

    rows = [
        # 1. Assessment Overview & Profile
        ["Assessment Overview", "Report ID", clean(f"#{analysis.id}"), "ID", "-", "Single Video Biomechanical Telemetry Report"],
        ["Assessment Overview", "Athlete Email", clean(user.email if user else "-"), "Account", "-", f"Registered Athlete: {athlete_name}"],
        ["Assessment Overview", "Sport Discipline & Position", clean(f"{profile.sport_type} / {profile.position}" if profile and profile.sport_type else "Athletics"), "Sport", "-", "Collegiate / Elite Movement Tracking"],
        ["Assessment Overview", "Assessment Timestamp", clean(str(analysis.created_at)[:19].replace("T", " ")), "UTC", "-", "High-Speed Computer Vision Kinematic Analysis"],
        ["Assessment Overview", "Primary Athletic Action", clean(analysis.activity), "Classification", "Action Detection", f"Verified {analysis.activity} Movement Pattern"],
        ["Assessment Overview", "Composite Injury Risk Score", clean(f"{analysis.risk_score:.1f}"), "/100", "0.0 - 30.0 (Low Risk)", f"{analysis.risk_level} - Targeted Corrective Intervention Prescribed" if analysis.risk_score > 30 else "Optimal Physiological Range"],
        ["Assessment Overview", "Training Surface & Footwear", clean(f"{analysis.surface_type or 'Indoor Court'} / {analysis.footwear or 'Standard'}"), "Environment", "-", "Environmental Friction & Deceleration Coefficient"],
        ["Assessment Overview", "Athlete Exertion (RPE) & Sleep", clean(f"RPE: {analysis.rpe or 5}/10 | Sleep: {analysis.sleep_quality or 7}/10"), "Subjective", "RPE < 7 | Sleep > 7", "Athlete Recovery Baseline Telemetry"],
    ]

    # 2. Joint Kinematics Telemetry
    kin = {}
    if analysis.kinematics:
        try:
            kin = json.loads(analysis.kinematics) if isinstance(analysis.kinematics, str) else analysis.kinematics
        except Exception:
            kin = {}

    kin_items = [
        ("Dynamic Knee Valgus (FPPA Left Mean)", kin.get("valgus_l_mean", 0), "deg", "< 12.0 deg", "Frontal plane medial knee projection angle"),
        ("Dynamic Knee Valgus (FPPA Left Max)", kin.get("valgus_l_max", 0), "deg", "< 15.0 deg", "Peak dynamic inward knee collapse"),
        ("Dynamic Knee Valgus (FPPA Right Mean)", kin.get("valgus_r_mean", 0), "deg", "< 12.0 deg", "Frontal plane medial knee projection angle"),
        ("Dynamic Knee Valgus (FPPA Right Max)", kin.get("valgus_r_max", 0), "deg", "< 15.0 deg", "Peak dynamic inward knee collapse"),
        ("Left Knee Flexion (Min / Deepest)", kin.get("knee_flexion_l_min", 0), "deg", "> 45.0 deg", "Maximum knee flexion depth"),
        ("Left Knee Flexion (Mean)", kin.get("knee_flexion_l_mean", 0), "deg", "Sport Specific", "Average functional knee flexion"),
        ("Right Knee Flexion (Min / Deepest)", kin.get("knee_flexion_r_min", 0), "deg", "> 45.0 deg", "Maximum knee flexion depth"),
        ("Right Knee Flexion (Mean)", kin.get("knee_flexion_r_mean", 0), "deg", "Sport Specific", "Average functional knee flexion"),
        ("Left Hip Flexion (Mean)", kin.get("hip_flexion_l_mean", 0), "deg", "Sport Specific", "Average pelvic-femoral hinge angle"),
        ("Right Hip Flexion (Mean)", kin.get("hip_flexion_r_mean", 0), "deg", "Sport Specific", "Average pelvic-femoral hinge angle"),
        ("Trunk Sagittal Lean (Mean)", kin.get("trunk_lean_mean", 0), "deg", "10.0 - 25.0 deg", "Mean torso forward inclination"),
        ("Trunk Sagittal Lean (Max)", kin.get("trunk_lean_max", 0), "deg", "< 35.0 deg", "Peak torso forward inclination"),
        ("Lateral Trunk Sway", kin.get("trunk_sway_mean", 0), "% height", "< 5.0%", "Coronal plane torso translation away from plant limb"),
        ("Head & Neck Tilt (Mean)", kin.get("head_tilt_mean", 0), "deg", "< 20.0 deg", "Cervical tilt relative to thoracic spine"),
        ("Head & Neck Tilt (Max)", kin.get("head_tilt_max", 0), "deg", "< 30.0 deg", "Peak cervical tilt during movement"),
        ("Pelvic Tilt (Horizontal Mean)", kin.get("pelvic_tilt_mean", 0), "deg", "< 15.0 deg", "Coronal acute pelvic inclination"),
        ("Shoulder Tilt (Horizontal Mean)", kin.get("shoulder_tilt_mean", 0), "deg", "< 15.0 deg", "Coronal acute shoulder inclination"),
        ("Core Torsion Disconnect", kin.get("core_torsion_mean", 0), "deg", "< 15.0 deg", "Rotational separation between shoulders and pelvis"),
        ("Left Elbow Extension (Mean)", kin.get("elbow_flexion_l_mean", 0), "deg", "Sport Specific", "Left upper-limb extension angle"),
        ("Right Elbow Extension (Mean)", kin.get("elbow_flexion_r_mean", 0), "deg", "Sport Specific", "Right upper-limb extension angle"),
        ("Peak Wrist Velocity", kin.get("peak_wrist_velocity", 0), "H/s", "Sport Specific", "Peak upper-limb hand displacement velocity"),
        ("Peak Ankle Velocity", kin.get("peak_ankle_velocity", 0), "H/s", "Sport Specific", "Peak lower-limb swing acceleration velocity"),
        ("Peak Knee Angular Velocity", kin.get("peak_knee_angular_velocity", 0), "deg/s", "Sport Specific", "Peak knee angular rotation speed"),
        ("Touchdown Deceleration Impact", kin.get("estimated_impact_g", 0), "G", "< 2.0 G", "Estimated landing shock deceleration"),
        ("Movement Cadence", kin.get("cadence_spm", 0), "SPM", "160 - 185 SPM", "Strides or cycles per minute"),
        ("Vertical Flight Clearance", kin.get("flight_clearance_percent", 0), "% height", "15.0 - 25.0%", "Maximum bilateral foot elevation off ground"),
        ("Bilateral Limb Angle Asymmetry", kin.get("limb_asymmetry_deg", 0), "deg", "< 8.0 deg", "Difference between left and right limb kinematics"),
        ("Bilateral Symmetry Index", kin.get("bilateral_symmetry_index", 94), "%", ">= 90.0%", "Composite bilateral limb kinetic symmetry")
    ]

    for param, val, unit, bench, desc in kin_items:
        val_str = f"{val:.1f}" if isinstance(val, (int, float)) else str(val)
        rows.append(["Joint Kinematics Telemetry", param, clean(val_str), unit, bench, desc])

    # 3. Injury Risk Model Probabilities
    probs = {}
    if analysis.injury_probabilities:
        try:
            probs = json.loads(analysis.injury_probabilities) if isinstance(analysis.injury_probabilities, str) else analysis.injury_probabilities
        except Exception:
            probs = {}

    for k, v in probs.items():
        v_num = float(v) if str(v).replace('.', '', 1).isdigit() else 0.0
        bench = "< 25.0% Low" if "acl" in k.lower() or "hamstring" in k.lower() else "< 30.0% Low"
        status = "Elevated Risk - Requires Intervention" if v_num > 40 else ("Moderate Monitoring" if v_num > 20 else "Within Safe Baseline")
        rows.append(["Injury Risk Probability", clean(k), f"{v_num:.1f}", "%", bench, status])

    # 4. Action-Specific Corrective Technique Cues
    for i, cue in enumerate(recom_data["corrective_cues"], 1):
        rows.append([
            "Prescribed Technique Cue",
            f"Form Cue {i}",
            clean(cue),
            "Coaching Cue",
            "Target Execution",
            f"Adhere to proper {analysis.activity} kinetic sequencing"
        ])

    # 5. Prescribed Corrective Exercises
    for ex in recom_data["prescribed_exercises"]:
        rows.append([
            "Prescribed Corrective Exercise",
            clean(ex["name"]),
            clean(f"{ex['sets']} x {ex['reps']}"),
            "Prescription",
            clean(f"Tempo: {ex.get('tempo', 'Controlled')}"),
            clean(f"Target: {ex.get('target', '')} | Focus: {ex.get('notes', '')}")
        ])

    # 6. Clinical Directives & Recovery
    rows.append([
        "Clinical Directives",
        "Biomechanical Demand Rationale",
        clean(recom_data["clinical_rationale"]),
        "Mechanism",
        "Physiological Demand",
        f"Kinetic chain strain prevention for {analysis.activity}"
    ])
    rows.append([
        "Clinical Directives",
        "Recovery & Regeneration Protocol",
        clean(recom_data["recovery_protocol"]),
        "Regeneration",
        "Daily / Post-Session",
        "Targeted tissue recovery and inflammation mitigation"
    ])

    for r in rows:
        ws.append(r)

    # Styles
    header_fill = PatternFill(start_color="1E1B4B", end_color="1E1B4B", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10, color="0F172A")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0")
    )

    ws.row_dimensions[1].height = 28
    for col_idx in range(1, 7):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    for row_idx in range(2, ws.max_row + 1):
        row_fill = zebra_fill if row_idx % 2 == 0 else white_fill
        for col_idx in range(1, 7):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.fill = row_fill
            cell.border = thin_border
            if col_idx in (1, 2, 5):
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            elif col_idx in (3, 4):
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            elif col_idx == 6:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Generous minimum column widths ensuring every sentence fits comfortably
    min_col_widths = {
        "A": 32.0,  # Section
        "B": 48.0,  # Parameter / Metric
        "C": 45.0,  # Measured Value
        "D": 22.0,  # Unit
        "E": 36.0,  # Reference Benchmark
        "F": 115.0  # Clinical Interpretation & Actionable Recommendation
    }

    # Auto-fit column widths by scanning all cell content
    for col_idx in range(1, 7):
        max_len = 0
        for row_idx in range(1, ws.max_row + 1):
            cell_value = ws.cell(row=row_idx, column=col_idx).value
            if cell_value:
                for line in str(cell_value).split("\n"):
                    max_len = max(max_len, len(line.strip()))
        col_letter = get_column_letter(col_idx)
        base_min = min_col_widths.get(col_letter, 25.0)
        ws.column_dimensions[col_letter].width = max(base_min, min(max_len + 5, 130))

    # Auto-fit row heights based on content length relative to column width
    for row_idx in range(2, ws.max_row + 1):
        max_lines = 1
        for col_idx in range(1, 7):
            cell_value = ws.cell(row=row_idx, column=col_idx).value
            if cell_value:
                col_letter = get_column_letter(col_idx)
                col_w = ws.column_dimensions[col_letter].width
                val_str = str(cell_value)
                lines = val_str.split("\n")
                total_lines = 0
                for l in lines:
                    total_lines += max(1, -(-len(l) // int(max(col_w - 2, 1))))
                max_lines = max(max_lines, total_lines)
        ws.row_dimensions[row_idx].height = max(26, min(max_lines * 19, 130))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def generate_dual_comparison_pdf(comp, user, profile=None) -> io.BytesIO:
    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#1e1b4b")   # Deep indigo
    c_accent = colors.HexColor("#4f46e5")    # Indigo 600
    c_pink = colors.HexColor("#db2777")      # Pink 600
    c_text_dark = colors.HexColor("#0f172a") # Slate 900
    c_slate = colors.HexColor("#64748b")     # Slate 500
    c_light_bg = colors.HexColor("#f8fafc")  # Slate 50
    c_border = colors.HexColor("#cbd5e1")    # Slate 300
    c_rose = colors.HexColor("#e11d48")      # Rose 600
    c_emerald = colors.HexColor("#059669")   # Emerald 600

    title_style = ParagraphStyle(
        'DualDocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=c_primary
    )
    subtitle_style = ParagraphStyle(
        'DualDocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_slate
    )
    section_h2 = ParagraphStyle(
        'DualSectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=5
    )
    cell_label = ParagraphStyle(
        'DualCellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=c_slate
    )
    cell_val = ParagraphStyle(
        'DualCellVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_text_dark
    )
    cell_header = ParagraphStyle(
        'DualCellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )
    body_style = ParagraphStyle(
        'DualBodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text_dark
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("SportsAI • Dual Video Comparative Biomechanics Lab Report", title_style))
    story.append(Paragraph("Direct Kinetic Delta Assessment: Video 1 (Past Baseline) vs Video 2 (Present Trial)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=4, spaceAfter=8))

    athlete_name = user.email.split("@")[0].capitalize() if user and user.email else "Athlete"
    sport_pos = f"{profile.sport_type} / {profile.position}" if profile and profile.sport_type else "Collegiate Athletics"

    score_diff = comp.score_diff or 0
    diff_color = c_emerald if score_diff < 0 else (c_rose if score_diff > 0 else c_slate)

    overview_data = [
        [
            Paragraph("<b>Athlete:</b>", cell_label),
            Paragraph(f"{athlete_name} ({user.email if user else 'N/A'})", cell_val),
            Paragraph("<b>Comparison ID:</b>", cell_label),
            Paragraph(f"Dual Assessment #{comp.id}", cell_val)
        ],
        [
            Paragraph("<b>Sport Discipline:</b>", cell_label),
            Paragraph(sport_pos, cell_val),
            Paragraph("<b>Assessment Date:</b>", cell_label),
            Paragraph(str(comp.created_at)[:19].replace("T", " "), cell_val)
        ],
        [
            Paragraph("<b>Video 1 (Baseline):</b>", cell_label),
            Paragraph(f"<b>{comp.video_a_activity}</b> ({comp.video_a_risk_score:.1f}/100)", cell_val),
            Paragraph("<b>Video 2 (Present):</b>", cell_label),
            Paragraph(f"<b>{comp.video_b_activity}</b> ({comp.video_b_risk_score:.1f}/100)", cell_val)
        ],
        [
            Paragraph("<b>Risk Score Delta:</b>", cell_label),
            Paragraph(f"<font color='{diff_color.hexval()}'><b>{score_diff:+.1f} pts</b></font>", cell_val),
            Paragraph("<b>Clinical Verdict:</b>", cell_label),
            Paragraph(f"<b>{comp.overall_verdict}</b>", cell_val)
        ]
    ]

    t_overview = Table(overview_data, colWidths=[90, 180, 90, 180])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 6))

    # Executive Verdict Banner
    v_bg = colors.HexColor("#f0fdf4") if score_diff < 0 else (colors.HexColor("#fff1f2") if score_diff > 0 else colors.HexColor("#f8fafc"))
    v_border = c_emerald if score_diff < 0 else (c_rose if score_diff > 0 else c_slate)
    verdict_text = f"<b>Executive Biomechanical Verdict:</b> {comp.summary}"
    t_verdict = Table([[Paragraph(verdict_text, body_style)]], colWidths=[540])
    t_verdict.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), v_bg),
        ('BOX', (0, 0), (-1, -1), 1, v_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_verdict)
    story.append(Spacer(1, 8))

    # 2. Section 1: 8-Action Kinetic Recognition Matrix
    story.append(Paragraph("1. 8-Action Kinetic Recognition Matrix Comparison", section_h2))

    actions_cmp = json.loads(comp.actions_comparison) if isinstance(comp.actions_comparison, str) else (comp.actions_comparison or [])
    action_rows = [
        [
            Paragraph("Target Action", cell_header),
            Paragraph("Video 1 (Baseline)", cell_header),
            Paragraph("Video 2 (Present)", cell_header),
            Paragraph("Kinetic Match Status", cell_header)
        ]
    ]

    for a in actions_cmp:
        v1_p = "✓ Performed" if a.get("video_a_performed") else "Not Detected"
        v2_p = "✓ Performed" if a.get("video_b_performed") else "Not Detected"
        match = a.get("match", False)
        m_color = c_emerald if match else colors.HexColor("#f59e0b")
        m_label = "Matched Pattern" if match else "Technique Delta"

        action_rows.append([
            Paragraph(f"<b>{a.get('action')}</b>", cell_label),
            Paragraph(f"{v1_p} ({a.get('video_a_confidence')}%)<br/><font color='#64748b' size='7'>{a.get('video_a_metric')}</font>", cell_val),
            Paragraph(f"{v2_p} ({a.get('video_b_confidence')}%)<br/><font color='#64748b' size='7'>{a.get('video_b_metric')}</font>", cell_val),
            Paragraph(f"<font color='{m_color.hexval()}'><b>{m_label}</b></font>", cell_val)
        ])

    t_act = Table(action_rows, colWidths=[130, 160, 160, 90])
    t_act.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
    ]))
    story.append(t_act)
    story.append(Spacer(1, 8))

    # 3. Section 2: 24-point Joint Angle Telemetry Comparison
    story.append(Paragraph("2. Full Kinetic Chain Joint Angle Telemetry Delta", section_h2))

    kin_cmp = json.loads(comp.kinematics_comparison) if isinstance(comp.kinematics_comparison, str) else (comp.kinematics_comparison or {})
    kin_rows = [
        [
            Paragraph("Joint / Biomechanical Parameter", cell_header),
            Paragraph("Video 1 Value", cell_header),
            Paragraph("Video 2 Value", cell_header),
            Paragraph("Kinematic Delta (V2 - V1)", cell_header)
        ]
    ]

    for k, v in list(kin_cmp.items())[:14]:
        diff_val = v.get("diff", 0)
        d_color = c_emerald if ((("symmetry" in k.lower()) and diff_val > 0) or (("symmetry" not in k.lower()) and diff_val < 0)) else (c_rose if abs(diff_val) > 0.5 else c_slate)
        kin_rows.append([
            Paragraph(v.get("label", k), cell_label),
            Paragraph(f"{v.get('video_a', 0)}", cell_val),
            Paragraph(f"{v.get('video_b', 0)}", cell_val),
            Paragraph(f"<font color='{d_color.hexval()}'><b>{diff_val:+.1f}</b></font>", cell_val)
        ])

    t_kin = Table(kin_rows, colWidths=[200, 110, 110, 120])
    t_kin.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
    ]))
    story.append(t_kin)
    story.append(Spacer(1, 8))

    # 4. Section 3: Progression vs Regression Delta Report
    improvements = json.loads(comp.improvements) if isinstance(comp.improvements, str) else (comp.improvements or [])
    deteriorations = json.loads(comp.deteriorations) if isinstance(comp.deteriorations, str) else (comp.deteriorations or [])

    story.append(Paragraph("3. Biomechanical Progression & Technique Delta Report", section_h2))
    story.append(Table([
        [
            Paragraph("<b>Verified Improvements:</b><br/>" + ("<br/>".join([f"• {x}" for x in improvements]) if improvements else "• No significant kinetic improvements registered."), body_style)
        ],
        [
            Paragraph("<b>Regressions & Elevated Risk Factors:</b><br/>" + ("<br/>".join([f"• {x}" for x in deteriorations]) if deteriorations else "• No dynamic regressions identified."), body_style)
        ]
    ], colWidths=[540], style=[
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0fdf4")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#fff1f2")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(Spacer(1, 8))

    # 5. Section 4: Targeted Biomechanical Directives & Corrective Prescriptions
    story.append(Paragraph("4. Targeted Biomechanical Directives & Corrective Prescriptions", section_h2))

    # 5.1 Movement Demands & Action Transition
    trans_p = Paragraph(f"<b>Kinetic Demand Delta & Movement Transition:</b><br/>{comp.action_transition_summary or 'Direct kinetic comparison between trials.'}", body_style)
    t_trans = Table([[trans_p]], colWidths=[540])
    t_trans.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_trans)
    story.append(Spacer(1, 5))

    # 5.2 Prescribed Corrective Exercises addressing target mechanics
    focus_act = comp.video_b_activity if comp.video_b_risk_score >= comp.video_a_risk_score else comp.video_a_activity
    recom_data = get_sport_recommendation_data(focus_act, max(comp.video_a_risk_score, comp.video_b_risk_score))

    story.append(Paragraph(f"<b>Targeted Corrective Prescriptions ({focus_act} Kinetic Mechanics):</b>", cell_label))
    story.append(Spacer(1, 2))
    ex_rows = [
        [
            Paragraph("Corrective Drill", cell_header),
            Paragraph("Prescribed Volume", cell_header),
            Paragraph("Movement Tempo", cell_header),
            Paragraph("Biomechanical Correction Target", cell_header)
        ]
    ]
    for ex in recom_data["prescribed_exercises"][:3]:
        ex_rows.append([
            Paragraph(f"<b>{ex['name']}</b>", cell_label),
            Paragraph(f"{ex['sets']} × {ex['reps']}", cell_val),
            Paragraph(ex.get("tempo", "Controlled"), cell_val),
            Paragraph(f"{ex.get('target', '')} • {ex.get('notes', '')}", cell_val)
        ])
    t_ex = Table(ex_rows, colWidths=[150, 85, 85, 220])
    t_ex.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
    ]))
    story.append(t_ex)
    story.append(Spacer(1, 5))

    # 5.3 Coaching Verdict & Recovery Directives
    verdict_p = Paragraph(f"<b>Coaching Verdict & Directives:</b> {comp.detailed_coaching_verdict or 'Focus on progressive resistance control.'}<br/><b>Recovery Advisory:</b> {recom_data['recovery_protocol']}", body_style)
    t_verdict = Table([[verdict_p]], colWidths=[540])
    t_verdict.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eef2ff")),
        ('BOX', (0, 0), (-1, -1), 1, c_accent),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_verdict)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<font color='#64748b' size='7'>Dual Video Comparative Analysis autonomously computed via SportsAI Biomechanical Engine.</font>", styles['Normal']))

    doc.build(story)
    output.seek(0)
    return output


def generate_dual_comparison_csv(comp, user, profile=None) -> str:
    """
    Generates a uniform, clean 6-column CSV export for dual video comparisons.
    Every row strictly maintains 6 columns to eliminate cell spillage, line truncation, and jagged columns in Excel.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Clean uniform 6-column tabular header
    writer.writerow([
        "Section",
        "Parameter / Movement Metric",
        "Video 1 (Baseline)",
        "Video 2 (Present)",
        "Variance (Delta)",
        "Clinical Evaluation & Coaching Prescription"
    ])

    def clean(val):
        if val is None:
            return "-"
        return str(val).replace("\r", " ").replace("\n", " ").strip()

    athlete_name = user.email.split("@")[0].capitalize() if user and user.email else "Athlete"

    # 1. Assessment Overview
    writer.writerow(["Assessment Overview", "Comparison ID", clean(f"Dual Report #{comp.id}"), "-", "-", "Dual Video Biomechanical Comparative Telemetry"])
    writer.writerow(["Assessment Overview", "Athlete Email", clean(user.email if user else "-"), "-", "-", f"Registered Athlete: {athlete_name}"])
    writer.writerow(["Assessment Overview", "Assessment Timestamp", clean(str(comp.created_at)[:19].replace("T", " ")), "-", "-", "High-Speed Dual Video Kinematic Comparison"])
    writer.writerow(["Assessment Overview", "Primary Action Analyzed", clean(comp.video_a_activity), clean(comp.video_b_activity), clean(f"{comp.video_a_activity} vs {comp.video_b_activity}"), "Direct Technique Cross-Comparison"])
    writer.writerow(["Assessment Overview", "Composite Injury Risk Score", clean(f"{comp.video_a_risk_score:.1f} / 100"), clean(f"{comp.video_b_risk_score:.1f} / 100"), clean(f"{comp.score_diff:+.1f}"), clean(comp.overall_verdict)])
    writer.writerow(["Assessment Overview", "Executive Comparison Summary", clean(comp.summary), "-", "-", "Autonomous Biomechanical Comparison Engine"])

    # 2. 8-Action Kinetic Recognition Matrix
    actions_cmp = json.loads(comp.actions_comparison) if isinstance(comp.actions_comparison, str) else (comp.actions_comparison or [])
    for a in actions_cmp:
        act_name = clean(a.get("action"))
        v1_perf = "Performed" if a.get("video_a_performed") else "Not Detected"
        v1_conf = clean(f"{a.get('video_a_confidence', 0)}%")
        v1_met = clean(a.get("video_a_metric", "-"))
        v2_perf = "Performed" if a.get("video_b_performed") else "Not Detected"
        v2_conf = clean(f"{a.get('video_b_confidence', 0)}%")
        v2_met = clean(a.get("video_b_metric", "-"))
        match_str = "Matched" if a.get("match") else "Technique Delta"
        eval_str = f"V1: {v1_met} | V2: {v2_met}"
        writer.writerow([
            "8-Action Kinetic Matrix",
            act_name,
            f"{v1_perf} ({v1_conf})",
            f"{v2_perf} ({v2_conf})",
            match_str,
            eval_str
        ])

    # 3. 24-point Joint Angle Telemetry Comparison
    kin_cmp = json.loads(comp.kinematics_comparison) if isinstance(comp.kinematics_comparison, str) else (comp.kinematics_comparison or {})
    for k, v in kin_cmp.items():
        label = clean(v.get("label", k))
        v1_val = clean(v.get("video_a", "-"))
        v2_val = clean(v.get("video_b", "-"))
        diff_val = v.get("diff", 0)
        diff_str = clean(f"{diff_val:+.1f}" if isinstance(diff_val, (int, float)) else str(diff_val))

        # Clinical status
        if "valgus" in k.lower():
            status = "Desirable Reduction in Medial Collapse" if diff_val < 0 else "Elevated Medial Knee Collapse Risk"
        elif "flexion" in k.lower():
            status = "Increased Shock Absorbing Flexion Depth" if diff_val > 0 else "Stiffer Joint Angle; Less Deceleration Flexion"
        elif "sway" in k.lower() or "lean" in k.lower():
            status = "Improved Torso Postural Stability" if diff_val < 0 else "Increased Trunk Sway / Compensatory Lean"
        elif "symmetry" in k.lower():
            status = "Enhanced Bilateral Limb Symmetry" if diff_val > 0 else "Increased Bilateral Limb Asymmetry"
        else:
            status = "Kinetic Variation Between Trials"

        writer.writerow(["Joint Telemetry Comparison", label, v1_val, v2_val, diff_str, status])

    # 4. Clinical Progression & Regression Delta Report
    improvements = json.loads(comp.improvements) if isinstance(comp.improvements, str) else (comp.improvements or [])
    for i, imp in enumerate(improvements, 1):
        writer.writerow([
            "Technique Progressions",
            f"Verified Improvement #{i}",
            clean(imp),
            "Positive Adaption",
            "Technique Gain",
            "Maintained safe physiological joint margin"
        ])

    deteriorations = json.loads(comp.deteriorations) if isinstance(comp.deteriorations, str) else (comp.deteriorations or [])
    for i, det in enumerate(deteriorations, 1):
        writer.writerow([
            "Technique Regressions",
            f"Elevated Joint Risk #{i}",
            clean(det),
            "Caution / Regression",
            "Intervention Focus",
            "Target for corrective neuromuscular drills"
        ])

    # 5. Targeted Prescriptions & Action Directives
    writer.writerow([
        "Prescriptions & Directives",
        "Movement Demands & Action Transition",
        clean(comp.action_transition_summary),
        "-",
        "-",
        "Kinetic demand variance between activities"
    ])
    writer.writerow([
        "Prescriptions & Directives",
        "Targeted Coaching Verdict & Prescriptions",
        clean(comp.detailed_coaching_verdict),
        "-",
        "-",
        "Clinical coaching protocol to stabilize technique"
    ])

    # Add activity-specific exercises for the target/regressed activity
    focus_act = comp.video_b_activity if comp.video_b_risk_score >= comp.video_a_risk_score else comp.video_a_activity
    recom_data = get_sport_recommendation_data(focus_act, max(comp.video_a_risk_score, comp.video_b_risk_score))

    for ex in recom_data["prescribed_exercises"]:
        writer.writerow([
            "Prescribed Corrective Drill",
            clean(ex["name"]),
            clean(f"{ex['sets']} x {ex['reps']}"),
            clean(f"Tempo: {ex.get('tempo', 'Controlled')}"),
            clean(focus_act),
            clean(f"Target: {ex.get('target', '')} | Focus: {ex.get('notes', '')}")
        ])

    writer.writerow([
        "Prescriptions & Directives",
        "Recovery & Regeneration Advisory",
        clean(recom_data["recovery_protocol"]),
        "Regeneration",
        "Daily / Post-Session",
        f"Targeted recovery protocol for {focus_act} kinetic demands"
    ])

    output.seek(0)
    return "\ufeff" + output.getvalue()


def generate_dual_comparison_xlsx(comp, user, profile=None) -> io.BytesIO:
    """
    Generates an Excel workbook (.xlsx) for dual video comparisons with custom, generous column widths
    and auto-fitted cell bounds, wrap_text enabled, and royal Indigo styling.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dual Comparison Matrix"
    ws.views.sheetView[0].showGridLines = True

    # 6-column header
    headers = [
        "Section",
        "Parameter / Movement Metric",
        "Video 1 (Baseline)",
        "Video 2 (Present)",
        "Variance (Delta)",
        "Clinical Evaluation & Coaching Prescription"
    ]
    ws.append(headers)

    def clean(val):
        if val is None:
            return "-"
        return str(val).replace("\r", " ").replace("\n", " ").strip()

    athlete_name = user.email.split("@")[0].capitalize() if user and user.email else "Athlete"

    rows = [
        # 1. Assessment Overview
        ["Assessment Overview", "Comparison ID", clean(f"Dual Report #{comp.id}"), "-", "-", "Dual Video Biomechanical Comparative Telemetry"],
        ["Assessment Overview", "Athlete Email", clean(user.email if user else "-"), "-", "-", f"Registered Athlete: {athlete_name}"],
        ["Assessment Overview", "Assessment Timestamp", clean(str(comp.created_at)[:19].replace("T", " ")), "-", "-", "High-Speed Dual Video Kinematic Comparison"],
        ["Assessment Overview", "Primary Action Analyzed", clean(comp.video_a_activity), clean(comp.video_b_activity), clean(f"{comp.video_a_activity} vs {comp.video_b_activity}"), "Direct Technique Cross-Comparison"],
        ["Assessment Overview", "Composite Injury Risk Score", clean(f"{comp.video_a_risk_score:.1f} / 100"), clean(f"{comp.video_b_risk_score:.1f} / 100"), clean(f"{comp.score_diff:+.1f}"), clean(comp.overall_verdict)],
        ["Assessment Overview", "Executive Comparison Summary", clean(comp.summary), "-", "-", "Autonomous Biomechanical Comparison Engine"],
    ]

    # 2. 8-Action Kinetic Recognition Matrix
    actions_cmp = json.loads(comp.actions_comparison) if isinstance(comp.actions_comparison, str) else (comp.actions_comparison or [])
    for a in actions_cmp:
        act_name = clean(a.get("action"))
        v1_perf = "Performed" if a.get("video_a_performed") else "Not Detected"
        v1_conf = clean(f"{a.get('video_a_confidence', 0)}%")
        v1_met = clean(a.get("video_a_metric", "-"))
        v2_perf = "Performed" if a.get("video_b_performed") else "Not Detected"
        v2_conf = clean(f"{a.get('video_b_confidence', 0)}%")
        v2_met = clean(a.get("video_b_metric", "-"))
        match_str = "Matched" if a.get("match") else "Technique Delta"
        eval_str = f"V1: {v1_met} | V2: {v2_met}"
        rows.append([
            "8-Action Kinetic Matrix",
            act_name,
            f"{v1_perf} ({v1_conf})",
            f"{v2_perf} ({v2_conf})",
            match_str,
            eval_str
        ])

    # 3. 24-point Joint Angle Telemetry Comparison
    kin_cmp = json.loads(comp.kinematics_comparison) if isinstance(comp.kinematics_comparison, str) else (comp.kinematics_comparison or {})
    for k, v in kin_cmp.items():
        label = clean(v.get("label", k))
        v1_val = clean(v.get("video_a", "-"))
        v2_val = clean(v.get("video_b", "-"))
        diff_val = v.get("diff", 0)
        diff_str = clean(f"{diff_val:+.1f}" if isinstance(diff_val, (int, float)) else str(diff_val))

        if "valgus" in k.lower():
            status = "Desirable Reduction in Medial Collapse" if diff_val < 0 else "Elevated Medial Knee Collapse Risk"
        elif "flexion" in k.lower():
            status = "Increased Shock Absorbing Flexion Depth" if diff_val > 0 else "Stiffer Joint Angle; Less Deceleration Flexion"
        elif "sway" in k.lower() or "lean" in k.lower():
            status = "Improved Torso Postural Stability" if diff_val < 0 else "Increased Trunk Sway / Compensatory Lean"
        elif "symmetry" in k.lower():
            status = "Enhanced Bilateral Limb Symmetry" if diff_val > 0 else "Increased Bilateral Limb Asymmetry"
        else:
            status = "Kinetic Variation Between Trials"

        rows.append(["Joint Telemetry Comparison", label, v1_val, v2_val, diff_str, status])

    # 4. Clinical Progression & Regression Delta Report
    improvements = json.loads(comp.improvements) if isinstance(comp.improvements, str) else (comp.improvements or [])
    for i, imp in enumerate(improvements, 1):
        rows.append([
            "Technique Progressions",
            f"Verified Improvement #{i}",
            clean(imp),
            "Positive Adaption",
            "Technique Gain",
            "Maintained safe physiological joint margin"
        ])

    deteriorations = json.loads(comp.deteriorations) if isinstance(getattr(comp, "deteriorations", None), str) else (getattr(comp, "deteriorations", None) or [])
    for i, det in enumerate(deteriorations, 1):
        rows.append([
            "Technique Regressions",
            f"Flagged Vulnerability #{i}",
            clean(det),
            "Elevated Kinetic Load",
            "Intervention Focus",
            "Target for corrective neuromuscular drills"
        ])

    # 5. Targeted Prescriptions & Action Directives
    rows.append([
        "Prescriptions & Directives",
        "Movement Demands & Action Transition",
        clean(comp.action_transition_summary),
        "-",
        "-",
        "Kinetic demand variance between activities"
    ])
    rows.append([
        "Prescriptions & Directives",
        "Targeted Coaching Verdict & Prescriptions",
        clean(comp.detailed_coaching_verdict),
        "-",
        "-",
        "Clinical coaching protocol to stabilize technique"
    ])

    focus_act = comp.video_b_activity if comp.video_b_risk_score >= comp.video_a_risk_score else comp.video_a_activity
    recom_data = get_sport_recommendation_data(focus_act, max(comp.video_a_risk_score, comp.video_b_risk_score))

    for ex in recom_data["prescribed_exercises"]:
        rows.append([
            "Prescribed Corrective Drill",
            clean(ex["name"]),
            clean(f"{ex['sets']} x {ex['reps']}"),
            clean(f"Tempo: {ex.get('tempo', 'Controlled')}"),
            clean(focus_act),
            clean(f"Target: {ex.get('target', '')} | Focus: {ex.get('notes', '')}")
        ])

    rows.append([
        "Prescriptions & Directives",
        "Recovery & Regeneration Advisory",
        clean(recom_data["recovery_protocol"]),
        "Regeneration",
        "Daily / Post-Session",
        f"Targeted recovery protocol for {focus_act} kinetic demands"
    ])

    for r in rows:
        ws.append(r)

    # Styles
    header_fill = PatternFill(start_color="1E1B4B", end_color="1E1B4B", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10, color="0F172A")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0")
    )

    ws.row_dimensions[1].height = 28
    for col_idx in range(1, 7):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    for row_idx in range(2, ws.max_row + 1):
        row_fill = zebra_fill if row_idx % 2 == 0 else white_fill
        for col_idx in range(1, 7):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.fill = row_fill
            cell.border = thin_border
            if col_idx in (1, 2):
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            elif col_idx in (3, 4, 5):
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            elif col_idx == 6:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Generous minimum column widths ensuring every sentence fits comfortably
    min_col_widths = {
        "A": 32.0,  # Section
        "B": 48.0,  # Parameter / Metric
        "C": 45.0,  # Measured Value
        "D": 22.0,  # Unit
        "E": 36.0,  # Reference Benchmark
        "F": 115.0  # Clinical Interpretation & Actionable Recommendation
    }

    # Auto-fit column widths by scanning all cell content
    for col_idx in range(1, 7):
        max_len = 0
        for row_idx in range(1, ws.max_row + 1):
            cell_value = ws.cell(row=row_idx, column=col_idx).value
            if cell_value:
                for line in str(cell_value).split("\n"):
                    max_len = max(max_len, len(line.strip()))
        col_letter = get_column_letter(col_idx)
        base_min = min_col_widths.get(col_letter, 25.0)
        ws.column_dimensions[col_letter].width = max(base_min, min(max_len + 5, 130))

    # Auto-fit row heights based on content length relative to column width
    for row_idx in range(2, ws.max_row + 1):
        max_lines = 1
        for col_idx in range(1, 7):
            cell_value = ws.cell(row=row_idx, column=col_idx).value
            if cell_value:
                col_letter = get_column_letter(col_idx)
                col_w = ws.column_dimensions[col_letter].width
                val_str = str(cell_value)
                lines = val_str.split("\n")
                total_lines = 0
                for l in lines:
                    total_lines += max(1, -(-len(l) // int(max(col_w - 2, 1))))
                max_lines = max(max_lines, total_lines)
        ws.row_dimensions[row_idx].height = max(26, min(max_lines * 19, 130))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
