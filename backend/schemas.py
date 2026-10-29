from pydantic import BaseModel
from typing import Optional, List, Any

# User Schemas
class UserBase(BaseModel):
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    profile_picture: Optional[str] = None
    email_alerts: Optional[int] = 1
    daily_wellness: Optional[int] = 1
    sound_effects: Optional[int] = 0
    class Config:
        from_attributes = True

class UserSettingsUpdate(BaseModel):
    email_alerts: Optional[bool] = None
    daily_wellness: Optional[bool] = None
    sound_effects: Optional[bool] = None
    profile_picture: Optional[str] = None

# Athlete Schemas
class AthleteProfileBase(BaseModel):
    sport_type: str
    position: str
    age: int
    height: float
    weight: float
    injury_history: Optional[str] = None
    training_load: Optional[str] = None
    phone: Optional[str] = None
    dominant_side: Optional[str] = None
    emergency_contact: Optional[str] = None
    personal_bio: Optional[str] = None
    profile_picture: Optional[str] = None

class AthleteProfileCreate(AthleteProfileBase):
    pass

class AthleteProfileResponse(AthleteProfileBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Physical Assessment Schemas
class PhysicalAssessmentBase(BaseModel):
    date: str
    test_name: str
    score: float
    notes: Optional[str] = None

class PhysicalAssessmentCreate(PhysicalAssessmentBase):
    pass

class PhysicalAssessmentResponse(PhysicalAssessmentBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Performance Record Schemas
class PerformanceRecordBase(BaseModel):
    date: str
    metric: str
    value: float
    unit: str

class PerformanceRecordCreate(PerformanceRecordBase):
    pass

class PerformanceRecordResponse(PerformanceRecordBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str

class GoogleLogin(BaseModel):
    email: str
    role: Optional[str] = "Athlete"

class VideoAnalysisResponse(BaseModel):
    id: int
    activity: str
    surface_type: Optional[str] = None
    footwear: Optional[str] = None
    rpe: Optional[int] = None
    sleep_quality: Optional[int] = None
    risk_score: float
    risk_level: str
    injury_probabilities: str
    corrective_recommendation: str
    actions_detected: Optional[str] = None
    kinematics: Optional[str] = None
    video_url: Optional[str] = None
    is_cleared_from_overview: Optional[int] = 0
    created_at: str
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: int
    created_at: str
    class ConfigDict:
        from_attributes = True

# Password Reset Schemas
class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyResetTokenRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class CompareExistingRequest(BaseModel):
    analysis_id_a: int
    analysis_id_b: int

class DeleteAnalysesRequest(BaseModel):
    analysis_ids: list[int]

class DeleteComparisonsRequest(BaseModel):
    comparison_ids: list[int]

# Training Plan Schemas
class TrainingPlanResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    plan_id: str
    title: str
    duration: str
    status: str
    focus: Optional[str] = None
    target_joint: Optional[str] = None
    description: Optional[str] = None
    prescribed_exercises: str
    exercises_detail: Optional[str] = None
    weekly_schedule: Optional[str] = None
    clinical_notes: Optional[str] = None
    progress_percent: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    class Config:
        from_attributes = True

class TrainingPlanUpdate(BaseModel):
    status: Optional[str] = None
    progress_percent: Optional[int] = None
    exercises_detail: Optional[str] = None

class TogglePlanTaskRequest(BaseModel):
    exercise_name: str
    completed: bool

class RoleUpdateRequest(BaseModel):
    role: str

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: Optional[str] = "info"
    user_id: Optional[int] = None

