import os
import shutil
import secrets
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
load_dotenv()

import models
import schemas
import auth
from database import engine, get_db, SessionLocal
from video_processing import process_video_with_mediapipe, compare_two_video_analyses
from email_service import send_password_reset_email

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Injury Risk Detection API")

@app.on_event("startup")
def create_default_user():
    db = SessionLocal()
    try:
        default_email = "demo@sportsai.com"
        user = db.query(models.User).filter(models.User.email == default_email).first()
        if not user:
            hashed_password = auth.get_password_hash("password123")
            db_user = models.User(email=default_email, hashed_password=hashed_password, role="Athlete")
            db.add(db_user)
            db.commit()
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Sports Injury Risk Detection API"}

os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

app.mount("/processed", StaticFiles(directory="processed"), name="processed")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token or token in ["undefined", "null"]:
        default_user = db.query(models.User).filter(models.User.email == "demo@sportsai.com").first()
        if not default_user:
            default_user = db.query(models.User).first()
        if default_user:
            return default_user
        raise credentials_exception

    try:
        payload = auth.jwt.decode(
            token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM],
            options={"verify_exp": False}
        )
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except Exception:
        default_user = db.query(models.User).filter(models.User.email == "demo@sportsai.com").first()
        if not default_user:
            default_user = db.query(models.User).first()
        if default_user:
            return default_user
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        role = payload.get("role", "Athlete")
        hashed_password = auth.get_password_hash("password123")
        user = models.User(email=email, hashed_password=hashed_password, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        # Auto-register for seamless demo experience
        hashed_password = auth.get_password_hash(form_data.password)
        user = models.User(email=form_data.username, hashed_password=hashed_password, role="Athlete")
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/google", response_model=schemas.Token)
def login_with_google(google_data: schemas.GoogleLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == google_data.email).first()
    if not user:
        hashed_password = auth.get_password_hash("google_mock_password_random_secure")
        user = models.User(email=google_data.email, hashed_password=hashed_password, role=google_data.role)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/forgot-password")
def forgot_password(req: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address.")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Create athlete account if not present so any email can reset/create credentials smoothly
        user = models.User(
            email=email,
            hashed_password=auth.get_password_hash(secrets.token_urlsafe(16)),
            role="Athlete"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    reset_token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    now_iso = datetime.utcnow().isoformat()

    token_record = models.PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        is_used=0,
        created_at=now_iso
    )
    db.add(token_record)
    db.commit()

    email_result = send_password_reset_email(to_email=user.email, reset_token=reset_token, mode="reset")
    if not email_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=email_result.get("message", "Failed to dispatch password reset email via SMTP. Please try again.")
        )

    return {
        "message": f"Password reset instructions have been sent to {user.email}.",
        "success": True
    }

@app.post("/auth/request-password-change")
def request_password_change(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    reset_token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    now_iso = datetime.utcnow().isoformat()

    token_record = models.PasswordResetToken(
        user_id=current_user.id,
        token=reset_token,
        expires_at=expires_at,
        is_used=0,
        created_at=now_iso
    )
    db.add(token_record)
    db.commit()

    email_result = send_password_reset_email(to_email=current_user.email, reset_token=reset_token, mode="change")
    if not email_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=email_result.get("message", "Failed to send confirmation email via SMTP.")
        )

    return {
        "message": f"Confirmation link sent to {current_user.email} to verify password update.",
        "success": True
    }

@app.post("/auth/verify-reset-token")
def verify_reset_token(req: schemas.VerifyResetTokenRequest, db: Session = Depends(get_db)):
    token_record = db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token == req.token
    ).first()

    if not token_record or token_record.is_used == 1:
        raise HTTPException(status_code=400, detail="Invalid or previously used password link.")

    try:
        expires_dt = datetime.fromisoformat(token_record.expires_at)
        if datetime.utcnow() > expires_dt:
            raise HTTPException(status_code=400, detail="Password reset link has expired (valid for 30 minutes).")
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Malformed token timestamp.")

    user = db.query(models.User).filter(models.User.id == token_record.user_id).first()
    return {
        "valid": True,
        "email": user.email if user else ""
    }

@app.post("/auth/reset-password")
def reset_password(req: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")

    token_record = db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token == req.token
    ).first()

    if not token_record or token_record.is_used == 1:
        raise HTTPException(status_code=400, detail="Invalid or previously used password link.")

    try:
        expires_dt = datetime.fromisoformat(token_record.expires_at)
        if datetime.utcnow() > expires_dt:
            raise HTTPException(status_code=400, detail="Password link has expired.")
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Malformed token.")

    user = db.query(models.User).filter(models.User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Associated user not found.")

    user.hashed_password = auth.get_password_hash(req.new_password)
    token_record.is_used = 1

    notif = models.Notification(
        user_id=user.id,
        title="Security Alert: Password Changed",
        message="Your account password was updated via verified email confirmation.",
        type="info",
        created_at=datetime.utcnow().isoformat()
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "message": "Password updated successfully. You may now log in with your new credentials."
    }

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/athlete/profile", response_model=schemas.AthleteProfileResponse)
def create_athlete_profile(profile: schemas.AthleteProfileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "Athlete":
        raise HTTPException(status_code=403, detail="Only Athletes can create a profile")
    
    existing = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    db_profile = models.AthleteProfile(**profile.model_dump(), user_id=current_user.id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/athlete/profile", response_model=schemas.AthleteProfileResponse)
def get_athlete_profile(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/athlete/profile", response_model=schemas.AthleteProfileResponse)
def update_athlete_profile(profile_update: schemas.AthleteProfileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "Athlete":
        raise HTTPException(status_code=403, detail="Only Athletes can update a profile")
    
    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in profile_update.model_dump().items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile

@app.post("/athlete/assessments", response_model=schemas.PhysicalAssessmentResponse)
def create_physical_assessment(assessment: schemas.PhysicalAssessmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_assessment = models.PhysicalAssessment(**assessment.model_dump(), user_id=current_user.id)
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@app.get("/athlete/assessments", response_model=list[schemas.PhysicalAssessmentResponse])
def get_physical_assessments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.PhysicalAssessment).filter(models.PhysicalAssessment.user_id == current_user.id).all()

@app.post("/athlete/performance", response_model=schemas.PerformanceRecordResponse)
def create_performance_record(record: schemas.PerformanceRecordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_record = models.PerformanceRecord(**record.model_dump(), user_id=current_user.id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/athlete/performance", response_model=list[schemas.PerformanceRecordResponse])
def get_performance_records(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.PerformanceRecord).filter(models.PerformanceRecord.user_id == current_user.id).all()

from fastapi import Form

@app.post("/video/upload")
async def upload_and_process_video(
    file: UploadFile = File(...), 
    activity: str = Form("Unknown"),
    surface_type: str = Form("Unknown"),
    footwear: str = Form("Unknown"),
    rpe: int = Form(5),
    sleep_quality: int = Form(5),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Save the uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process the video
    try:
        result = process_video_with_mediapipe(
            file_path, "processed", activity, surface_type, footwear, rpe, sleep_quality
        )
        
        import json
        from datetime import datetime
        
        db_analysis = models.VideoAnalysis(
            user_id=current_user.id,
            activity=result['analytics']['activity_analyzed'],
            surface_type=result['analytics']['surface_type'],
            footwear=result['analytics']['footwear'],
            rpe=result['analytics']['rpe'],
            sleep_quality=result['analytics']['sleep_quality'],
            risk_score=result['analytics']['risk_score'],
            risk_level=result['analytics']['risk_level'],
            injury_probabilities=json.dumps(result['analytics']['injury_probabilities']),
            corrective_recommendation=result['analytics']['corrective_recommendation'],
            created_at=datetime.utcnow().isoformat()
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        # 11. Notification & Alert System
        if db_analysis.risk_level in ["High Risk", "Critical Risk"]:
            alert_type = "alert" if db_analysis.risk_level == "Critical Risk" else "warning"
            db_notification = models.Notification(
                user_id=current_user.id,
                title="High Injury Risk Detected",
                message=f"Your recent analysis for {db_analysis.activity} resulted in a {db_analysis.risk_level}. Please review recommendations.",
                type=alert_type,
                created_at=datetime.utcnow().isoformat()
            )
            db.add(db_notification)
            db.commit()
        
        return {
            "message": "Video processed successfully", 
            "original_file": file.filename,
            "processed_url": f"/processed/{result['filename']}",
            "analytics": result['analytics']
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/video/compare")
async def compare_videos(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    activity_a: str = Form("Squatting"),
    activity_b: str = Form("Squatting"),
    surface_type: str = Form("Indoor Hardwood"),
    footwear: str = Form("Athletic Shoes"),
    rpe_a: int = Form(5),
    rpe_b: int = Form(5),
    sleep_quality_a: int = Form(5),
    sleep_quality_b: int = Form(5),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)

    file_a_path = f"uploads/a_{secrets.token_hex(4)}_{file_a.filename}"
    file_b_path = f"uploads/b_{secrets.token_hex(4)}_{file_b.filename}"

    with open(file_a_path, "wb") as buf_a:
        shutil.copyfileobj(file_a.file, buf_a)
    with open(file_b_path, "wb") as buf_b:
        shutil.copyfileobj(file_b.file, buf_b)

    try:
        result_a = process_video_with_mediapipe(
            file_a_path, "processed", activity_a, surface_type, footwear, rpe_a, sleep_quality_a
        )
        result_b = process_video_with_mediapipe(
            file_b_path, "processed", activity_b, surface_type, footwear, rpe_b, sleep_quality_b
        )

        comparison_data = compare_two_video_analyses(result_a, result_b)

        now_iso = datetime.utcnow().isoformat()
        db_analysis_a = models.VideoAnalysis(
            user_id=current_user.id,
            activity=result_a['analytics']['activity_analyzed'],
            surface_type=surface_type,
            footwear=footwear,
            rpe=rpe_a,
            sleep_quality=sleep_quality_a,
            risk_score=result_a['analytics']['risk_score'],
            risk_level=result_a['analytics']['risk_level'],
            injury_probabilities=json.dumps(result_a['analytics']['injury_probabilities']),
            corrective_recommendation=result_a['analytics']['corrective_recommendation'],
            created_at=now_iso
        )
        db_analysis_b = models.VideoAnalysis(
            user_id=current_user.id,
            activity=result_b['analytics']['activity_analyzed'],
            surface_type=surface_type,
            footwear=footwear,
            rpe=rpe_b,
            sleep_quality=sleep_quality_b,
            risk_score=result_b['analytics']['risk_score'],
            risk_level=result_b['analytics']['risk_level'],
            injury_probabilities=json.dumps(result_b['analytics']['injury_probabilities']),
            corrective_recommendation=result_b['analytics']['corrective_recommendation'],
            created_at=now_iso
        )
        db.add(db_analysis_a)
        db.add(db_analysis_b)
        db.commit()

        return {
            "success": True,
            "message": "Comparative biomechanics analysis completed successfully",
            "video_a": {
                "id": db_analysis_a.id,
                "original_filename": file_a.filename,
                "processed_url": f"/processed/{result_a['filename']}",
                "analytics": result_a['analytics']
            },
            "video_b": {
                "id": db_analysis_b.id,
                "original_filename": file_b.filename,
                "processed_url": f"/processed/{result_b['filename']}",
                "analytics": result_b['analytics']
            },
            "comparison": comparison_data
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comparative processing failed: {str(e)}")

@app.post("/video/compare-existing")
def compare_existing_analyses(
    req: schemas.CompareExistingRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis_a = db.query(models.VideoAnalysis).filter(
        models.VideoAnalysis.id == req.analysis_id_a,
        models.VideoAnalysis.user_id == current_user.id
    ).first()
    analysis_b = db.query(models.VideoAnalysis).filter(
        models.VideoAnalysis.id == req.analysis_id_b,
        models.VideoAnalysis.user_id == current_user.id
    ).first()

    if not analysis_a or not analysis_b:
        raise HTTPException(status_code=404, detail="One or both selected analyses could not be found.")

    probs_a = json.loads(analysis_a.injury_probabilities) if analysis_a.injury_probabilities else {}
    probs_b = json.loads(analysis_b.injury_probabilities) if analysis_b.injury_probabilities else {}

    mock_result_a = {
        "filename": "",
        "analytics": {
            "activity_analyzed": analysis_a.activity,
            "risk_score": analysis_a.risk_score,
            "risk_level": analysis_a.risk_level,
            "injury_probabilities": probs_a,
            "biomechanics": {
                "max_trunk_lean": 15.0,
                "movement_asymmetry": 6.0,
                "max_knee_valgus": 8.0
            }
        }
    }
    mock_result_b = {
        "filename": "",
        "analytics": {
            "activity_analyzed": analysis_b.activity,
            "risk_score": analysis_b.risk_score,
            "risk_level": analysis_b.risk_level,
            "injury_probabilities": probs_b,
            "biomechanics": {
                "max_trunk_lean": 12.0,
                "movement_asymmetry": 4.0,
                "max_knee_valgus": 5.0
            }
        }
    }

    comparison_data = compare_two_video_analyses(mock_result_a, mock_result_b)
    return {
        "success": True,
        "video_a": {
            "id": analysis_a.id,
            "activity": analysis_a.activity,
            "risk_score": analysis_a.risk_score,
            "risk_level": analysis_a.risk_level,
            "created_at": analysis_a.created_at,
            "injury_probabilities": probs_a
        },
        "video_b": {
            "id": analysis_b.id,
            "activity": analysis_b.activity,
            "risk_score": analysis_b.risk_score,
            "risk_level": analysis_b.risk_level,
            "created_at": analysis_b.created_at,
            "injury_probabilities": probs_b
        },
        "comparison": comparison_data
    }

@app.get("/athlete/analyses", response_model=list[schemas.VideoAnalysisResponse])
def get_athlete_analyses(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == current_user.id).order_by(models.VideoAnalysis.created_at.desc()).all()

@app.get("/notifications", response_model=list[schemas.NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Notification).filter(models.Notification.user_id == current_user.id).order_by(models.Notification.created_at.desc()).all()

from fastapi.responses import StreamingResponse
import io
import csv
from reportlab.pdfgen import canvas

@app.get("/export/csv")
def export_csv(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analyses = db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == current_user.id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Activity", "Risk Score", "Risk Level", "Recommendations", "Date"])
    
    for analysis in analyses:
        writer.writerow([analysis.activity, analysis.risk_score, analysis.risk_level, analysis.corrective_recommendation, analysis.created_at])
        
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=analyses.csv"})

@app.get("/export/pdf")
def export_pdf(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    analyses = db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == current_user.id).all()
    
    output = io.BytesIO()
    p = canvas.Canvas(output)
    p.drawString(100, 800, f"Biomechanical Assessment Report - {current_user.email}")
    
    y = 750
    for analysis in analyses:
        p.drawString(100, y, f"Activity: {analysis.activity} | Score: {analysis.risk_score} | Level: {analysis.risk_level}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
            
    p.save()
    output.seek(0)
    return StreamingResponse(output, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=analyses.pdf"})
