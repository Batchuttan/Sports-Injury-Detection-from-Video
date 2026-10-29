from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # Athlete, Coach, Physiotherapist, Sports Scientist, Administrator
    profile_picture = Column(String, nullable=True)
    email_alerts = Column(Integer, default=1)
    daily_wellness = Column(Integer, default=1)
    sound_effects = Column(Integer, default=0)
    
    athlete_profile = relationship("AthleteProfile", back_populates="user", uselist=False)

class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    sport_type = Column(String)
    position = Column(String)
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    injury_history = Column(String)
    training_load = Column(String)
    phone = Column(String, nullable=True)
    dominant_side = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    personal_bio = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    user = relationship("User", back_populates="athlete_profile")

class PhysicalAssessment(Base):
    __tablename__ = "physical_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(String)
    test_name = Column(String)
    score = Column(Float)
    notes = Column(String)

    user = relationship("User")

class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(String)
    metric = Column(String)
    value = Column(Float)
    unit = Column(String)

    user = relationship("User")

class VideoAnalysis(Base):
    __tablename__ = "video_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    activity = Column(String)
    surface_type = Column(String)
    footwear = Column(String)
    rpe = Column(Integer)
    sleep_quality = Column(Integer)
    risk_score = Column(Float)
    risk_level = Column(String)
    injury_probabilities = Column(String)
    corrective_recommendation = Column(String)
    actions_detected = Column(String, nullable=True)
    kinematics = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    is_cleared_from_overview = Column(Integer, default=0)
    created_at = Column(String)

    user = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String)
    message = Column(String)
    type = Column(String) # alert, warning, info
    is_read = Column(Integer, default=0)
    created_at = Column(String)

    user = relationship("User")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(String)  # ISO timestamp
    is_used = Column(Integer, default=0)  # 0 = active, 1 = used
    created_at = Column(String)

    user = relationship("User")

class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    plan_id = Column(String, index=True)  # e.g. "knee-valgus", "core-stability", "post-match-recovery"
    title = Column(String)
    duration = Column(String)
    status = Column(String, default="Active")  # Active, Pending, Completed
    focus = Column(String)
    target_joint = Column(String)
    description = Column(String)
    prescribed_exercises = Column(String)  # JSON list of strings
    exercises_detail = Column(String)  # JSON rich details
    weekly_schedule = Column(String)  # JSON schedule
    clinical_notes = Column(String)
    progress_percent = Column(Integer, default=0)
    created_at = Column(String)
    updated_at = Column(String)

    user = relationship("User")

class DualVideoComparison(Base):
    __tablename__ = "dual_video_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    video_a_id = Column(Integer, ForeignKey("video_analyses.id"), nullable=True)
    video_b_id = Column(Integer, ForeignKey("video_analyses.id"), nullable=True)
    video_a_activity = Column(String)
    video_b_activity = Column(String)
    video_a_filename = Column(String, nullable=True)
    video_b_filename = Column(String, nullable=True)
    video_a_risk_score = Column(Float)
    video_b_risk_score = Column(Float)
    score_diff = Column(Float)
    overall_verdict = Column(String)
    verdict_color = Column(String)
    summary = Column(String)
    insights = Column(String)  # JSON list
    improvements = Column(String, nullable=True)  # JSON list
    deteriorations = Column(String, nullable=True)  # JSON list
    neutral_observations = Column(String, nullable=True)  # JSON list
    action_transition_summary = Column(String, nullable=True)
    detailed_coaching_verdict = Column(String, nullable=True)
    actions_comparison = Column(String, nullable=True)  # JSON list of 8 actions
    kinematics_comparison = Column(String, nullable=True)  # JSON dict of 24 metrics
    metrics_diff = Column(String, nullable=True)  # JSON
    injury_probabilities_comparison = Column(String, nullable=True)  # JSON
    created_at = Column(String)

    user = relationship("User")


