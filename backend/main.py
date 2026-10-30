import os



import shutil



import secrets



import json
import time



from datetime import datetime, timedelta



from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request



from fastapi.responses import StreamingResponse, FileResponse



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



from training_plans_catalog import ALL_CLINICAL_TRAINING_PLANS, ensure_user_training_plans







# Create all tables



models.Base.metadata.create_all(bind=engine)







app = FastAPI(title="Sports Injury Risk Detection API")







@app.on_event("startup")
def seed_default_accounts():
    db = SessionLocal()
    try:
        accounts = [
            ("superadmin@gmail.com", "superadmin", "Administrator"),
            ("athlete@gmail.com", "athlete123", "Athlete"),
            ("coach@gmail.com", "coach123", "Coach"),
            ("doctor@gmail.com", "doctor123", "Doctor"),
            ("physiotherapist@gmail.com", "physiotherapist@123", "Physiotherapist"),
            ("sportsscientist@gmail.com", "sportsscientist123", "Sports Scientist"),
            ("demo@sportsai.com", "password123", "Athlete"),
            ("athlete@sportsai.com", "password123", "Athlete"),
            ("aizalbegenemeliteachu@gmail.com", "password123", "Athlete"),
            ("yourtubeentertainments@gmail.com", "password123", "Athlete"),
        ]
        for email, password, role in accounts:
            clean_email = email.strip().lower()
            u = db.query(models.User).filter(models.User.email.ilike(clean_email)).first()
            hashed = auth.get_password_hash(password)
            if not u:
                u = models.User(email=clean_email, hashed_password=hashed, role=role)
                db.add(u)
                db.commit()
                db.refresh(u)
            else:
                u.hashed_password = hashed
                u.role = role
                db.commit()

            if role in ("Athlete", "Administrator"):
                prof = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == u.id).first()
                if not prof:
                    prof = models.AthleteProfile(
                        user_id=u.id,
                        sport_type="Football",
                        position="Forward" if role == "Athlete" else "Director",
                        age=24 if role == "Athlete" else 35,
                        height=180.0,
                        weight=75.0,
                        injury_history="None",
                        training_load="Medium",
                        dominant_side="Right",
                        personal_bio=f"System account for {role}."
                    )
                    db.add(prof)
                    db.commit()
    except Exception as e:
        print("Startup seed warning:", e)
    finally:
        db.close()







app.add_middleware(



    CORSMiddleware,



    allow_origins=[



        "http://localhost:3000",



        "http://127.0.0.1:3000",



        "http://localhost:3001",



        "http://127.0.0.1:3001",



    ],



    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:[0-9]+)?$",



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



os.makedirs("uploads/avatars", exist_ok=True)



# High-Performance Video Streaming with Caching & 206 Partial Content (Optimized for Screen Sharing & GMeet)



@app.get("/processed/{filename}")



async def stream_processed_video(filename: str, request: Request):



    filepath = os.path.join("processed", filename)



    if not os.path.exists(filepath):



        raise HTTPException(status_code=404, detail="Video file not found")



    



    filesize = os.path.getsize(filepath)



    range_header = request.headers.get("range") or request.headers.get("Range")



    



    base_headers = {



        "Accept-Ranges": "bytes",



        "Cache-Control": "public, max-age=31536000, immutable",



        "Content-Type": "video/mp4",



    }



    



    if range_header:



        byte_range = range_header.strip().replace("bytes=", "").split("-")



        start = int(byte_range[0]) if byte_range[0] else 0



        end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else filesize - 1



        end = min(end, filesize - 1)



        chunk_length = end - start + 1



        



        headers = dict(base_headers)



        headers["Content-Range"] = f"bytes {start}-{end}/{filesize}"



        headers["Content-Length"] = str(chunk_length)



        



        def file_chunk_generator():



            with open(filepath, "rb") as f:



                f.seek(start)



                remaining = chunk_length



                while remaining > 0:



                    chunk_size = min(remaining, 64 * 1024)



                    chunk = f.read(chunk_size)



                    if not chunk:



                        break



                    remaining -= len(chunk)



                    yield chunk



        



        return StreamingResponse(



            file_chunk_generator(),



            status_code=206,



            headers=headers,



            media_type="video/mp4"



        )



    else:



        headers = dict(base_headers)



        headers["Content-Length"] = str(filesize)



        return FileResponse(filepath, headers=headers, media_type="video/mp4")







BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))



PROCESSED_DIR = os.path.join(BACKEND_DIR, "processed")



UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads")



os.makedirs(PROCESSED_DIR, exist_ok=True)



os.makedirs(UPLOADS_DIR, exist_ok=True)



app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")



app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")







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







@app.get("/auth/device-accounts")
def get_device_accounts(db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    clean_list = []
    seen = set()
    for u in users:
        em = (u.email or "").strip().lower()
        if not em or em.startswith("newuser_") or em.startswith("nonexistent_"):
            continue
        if em not in seen:
            seen.add(em)
            clean_list.append({
                "email": u.email,
                "role": u.role or "Athlete"
            })
    return clean_list

@app.post("/auth/google", response_model=schemas.Token)



def login_with_google(google_data: schemas.GoogleLogin, db: Session = Depends(get_db)):



    clean_email = (google_data.email or "").strip().lower()



    if not clean_email or "@" not in clean_email:



        raise HTTPException(status_code=400, detail="Invalid email address provided.")







    action = (google_data.action or "login").strip().lower()



    user = db.query(models.User).filter(models.User.email.ilike(clean_email)).first()







    if action == "login":



        if not user:



            raise HTTPException(



                status_code=status.HTTP_404_NOT_FOUND,



                detail="No registered account found for this Google email. Please register your account.",



                headers={"X-Error-Code": "ACCOUNT_NOT_REGISTERED"}



            )



        # Ensure athlete profile exists if role is Athlete



        if user.role == "Athlete":



            prof = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == user.id).first()



            if not prof:



                prof = models.AthleteProfile(



                    user_id=user.id,



                    sport_type="Football",



                    position="Midfielder",



                    age=22,



                    height=175.0,



                    weight=70.0,



                    injury_history="None",



                    training_load="Medium",



                    dominant_side="Right",



                    personal_bio="Profile initialized upon Google sign in."



                )



                db.add(prof)



                db.commit()



    else:  # action == "register"



        if not user:



            hashed_password = auth.get_password_hash("google_auth_secure_" + secrets.token_hex(8))



            chosen_role = google_data.role or "Athlete"



            user = models.User(email=clean_email, hashed_password=hashed_password, role=chosen_role)



            db.add(user)



            db.commit()



            db.refresh(user)







            if user.role == "Athlete":



                athlete_profile = models.AthleteProfile(



                    user_id=user.id,



                    sport_type="Football",



                    position="Midfielder",



                    age=22,



                    height=175.0,



                    weight=70.0,



                    injury_history="None",



                    training_load="Medium",



                    dominant_side="Right",



                    personal_bio="Registered via Google authentication."



                )



                db.add(athlete_profile)



                db.commit()







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







@app.get("/user/settings")



def get_user_settings(current_user: models.User = Depends(get_current_user)):



    return {



        "id": current_user.id,



        "email": current_user.email,



        "role": current_user.role,



        "email_alerts": bool(current_user.email_alerts if current_user.email_alerts is not None else 1),



        "daily_wellness": bool(current_user.daily_wellness if current_user.daily_wellness is not None else 1),



        "sound_effects": bool(current_user.sound_effects if current_user.sound_effects is not None else 0),



        "profile_picture": current_user.profile_picture or "",



        "sound_cue": current_user.sound_cue or "chime",



        "custom_sound_url": current_user.custom_sound_url or "",



        "sound_volume": current_user.sound_volume if current_user.sound_volume is not None else 80



    }







@app.put("/user/settings")



def update_user_settings(



    settings_in: schemas.UserSettingsUpdate,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if settings_in.email_alerts is not None:



        current_user.email_alerts = 1 if settings_in.email_alerts else 0



    if settings_in.daily_wellness is not None:



        current_user.daily_wellness = 1 if settings_in.daily_wellness else 0



    if settings_in.sound_effects is not None:



        current_user.sound_effects = 1 if settings_in.sound_effects else 0



    if settings_in.sound_cue is not None:



        current_user.sound_cue = settings_in.sound_cue



    if settings_in.custom_sound_url is not None:



        current_user.custom_sound_url = settings_in.custom_sound_url



    if settings_in.sound_volume is not None:



        current_user.sound_volume = max(0, min(100, int(settings_in.sound_volume)))



    if settings_in.profile_picture is not None:



        current_user.profile_picture = settings_in.profile_picture



        prof = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()



        if prof:



            prof.profile_picture = settings_in.profile_picture







    db.commit()



    db.refresh(current_user)



    return {



        "success": True,



        "message": "Settings updated successfully",



        "settings": {



            "id": current_user.id,



            "email": current_user.email,



            "role": current_user.role,



            "email_alerts": bool(current_user.email_alerts),



            "daily_wellness": bool(current_user.daily_wellness),



            "sound_effects": bool(current_user.sound_effects),



            "profile_picture": current_user.profile_picture or "",



            "sound_cue": current_user.sound_cue or "chime",



            "custom_sound_url": current_user.custom_sound_url or "",



            "sound_volume": current_user.sound_volume if current_user.sound_volume is not None else 80



        }



    }







@app.post("/user/avatar")



async def upload_user_avatar(



    file: UploadFile = File(...),



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    ext = os.path.splitext(file.filename)[1].lower() or ".jpg"



    safe_filename = f"avatar_{current_user.id}_{int(datetime.utcnow().timestamp())}{ext}"



    avatar_path = os.path.join("uploads", "avatars", safe_filename)



    



    with open(avatar_path, "wb") as buffer:



        shutil.copyfileobj(file.file, buffer)



        



    avatar_url = f"http://127.0.0.1:8000/uploads/avatars/{safe_filename}"



    current_user.profile_picture = avatar_url



    



    prof = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()



    if prof:



        prof.profile_picture = avatar_url



        



    db.commit()



    return {"success": True, "profile_picture": avatar_url}







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



        # Auto-create standard profile for user



        profile = models.AthleteProfile(



            user_id=current_user.id,



            sport_type="Football",



            position="Left Back",



            age=20,



            height=170.0,



            weight=50.0,



            injury_history="Small bone cracks on right leg and recent crack on right leg small finger",



            training_load="Football camp",



            phone="+1 (555) 234-8901",



            dominant_side="Left Foot",



            emergency_contact="Dr. Marcus Vance (Physio) - +1 (555) 019-2834",



            personal_bio="Left-back athlete specializing in wing overlaps and high-speed defensive recovery sprints. Rebuilding load tolerance following right lower-limb micro-fractures.",



            profile_picture=current_user.profile_picture



        )



        db.add(profile)



        db.commit()



        db.refresh(profile)



    return profile







@app.put("/athlete/profile", response_model=schemas.AthleteProfileResponse)



def update_athlete_profile(profile_update: schemas.AthleteProfileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    if current_user.role != "Athlete":



        raise HTTPException(status_code=403, detail="Only Athletes can update a profile")



    



    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == current_user.id).first()



    if not profile:



        profile = models.AthleteProfile(**profile_update.model_dump(), user_id=current_user.id)



        db.add(profile)



    else:



        for key, value in profile_update.model_dump().items():



            setattr(profile, key, value)



    



    if profile_update.profile_picture:



        current_user.profile_picture = profile_update.profile_picture







    db.commit()



    db.refresh(profile)



    return profile







# Training Plans Endpoints



@app.get("/training/plans")



def get_training_plans(



    include_completed: bool = False,



    status_filter: str = "active",



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    # Ensure all clinical plans are seeded for this user



    user_plans = ensure_user_training_plans(db, current_user.id)







    # Filter completed plans if requested



    if status_filter == "completed":



        filtered_plans = [p for p in user_plans if (p.progress_percent or 0) >= 100 or (p.status or "").lower() == "completed"]



    elif status_filter == "all" or include_completed:



        filtered_plans = user_plans



    else:  # "active"



        filtered_plans = [p for p in user_plans if (p.progress_percent or 0) < 100 and (p.status or "").lower() != "completed"]







    # Format response



    result = []



    for p in filtered_plans:



        tasks = []



        try:



            tasks = json.loads(p.prescribed_exercises) if p.prescribed_exercises else []



        except:



            tasks = []



        result.append({



            "id": p.id,



            "plan_id": p.plan_id,



            "title": p.title,



            "duration": p.duration,



            "status": p.status,



            "focus": p.focus,



            "target_joint": p.target_joint,



            "tasks": tasks,



            "progress_percent": p.progress_percent or 0,



            "description": p.description



        })



    return result







@app.get("/training/plans/{plan_identifier}")



def get_training_plan_detail(



    plan_identifier: str,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    ensure_user_training_plans(db, current_user.id)



    plan = None



    if plan_identifier.isdigit():



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.id == int(plan_identifier),



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.plan_id == plan_identifier,



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        # Fallback to global template



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.plan_id == plan_identifier,



            models.TrainingPlan.user_id == None



        ).first()



        



    if not plan:



        raise HTTPException(status_code=404, detail=f"Training plan '{plan_identifier}' not found")







    tasks = []



    details = []



    schedule = []



    try:



        if plan.prescribed_exercises:



            tasks = json.loads(plan.prescribed_exercises)



    except:



        pass



    try:



        if plan.exercises_detail:



            details = json.loads(plan.exercises_detail)



    except:



        pass



    try:



        if plan.weekly_schedule:



            schedule = json.loads(plan.weekly_schedule)



    except:



        pass







    return {



        "id": plan.id,



        "plan_id": plan.plan_id,



        "title": plan.title,



        "duration": plan.duration,



        "status": plan.status,



        "focus": plan.focus,



        "target_joint": plan.target_joint,



        "description": plan.description,



        "prescribed_exercises": tasks,



        "exercises_detail": details,



        "weekly_schedule": schedule,



        "clinical_notes": plan.clinical_notes,



        "progress_percent": plan.progress_percent or 0,



        "updated_at": plan.updated_at



    }







@app.post("/training/plans/{plan_identifier}/toggle-task")



def toggle_training_plan_task(



    plan_identifier: str,



    req: schemas.TogglePlanTaskRequest,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    ensure_user_training_plans(db, current_user.id)



    plan = None



    if plan_identifier.isdigit():



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.id == int(plan_identifier),



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.plan_id == plan_identifier,



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        raise HTTPException(status_code=404, detail="Training plan not found for user")







    try:



        exercises = json.loads(plan.exercises_detail) if plan.exercises_detail else []



    except:



        exercises = []







    matched = False



    for ex in exercises:



        if ex.get("name", "").lower() == req.exercise_name.lower():



            ex["completed"] = req.completed



            matched = True



            break







    if not matched and exercises:



        # Also check alias



        for ex in exercises:



            if req.exercise_name.lower() in ex.get("name", "").lower():



                ex["completed"] = req.completed



                matched = True



                break







    # Recalculate progress & auto-update status



    if exercises:



        completed_count = sum(1 for e in exercises if e.get("completed", False))



        plan.progress_percent = int((completed_count / len(exercises)) * 100)



        if plan.progress_percent >= 100:



            plan.status = "Completed"



        else:



            plan.status = "Active"







    plan.exercises_detail = json.dumps(exercises)



    plan.updated_at = datetime.utcnow().isoformat()



    db.commit()



    db.refresh(plan)







    return {



        "success": True,



        "plan_id": plan.plan_id,



        "status": plan.status,



        "progress_percent": plan.progress_percent,



        "exercises_detail": exercises



    }







@app.post("/training/plans/{plan_identifier}/reactivate")



def reactivate_training_plan(



    plan_identifier: str,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    ensure_user_training_plans(db, current_user.id)



    plan = None



    if plan_identifier.isdigit():



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.id == int(plan_identifier),



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.plan_id == plan_identifier,



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        raise HTTPException(status_code=404, detail="Training plan not found")







    try:



        exercises = json.loads(plan.exercises_detail) if plan.exercises_detail else []



    except:



        exercises = []







    for ex in exercises:



        ex["completed"] = False







    plan.exercises_detail = json.dumps(exercises)



    plan.progress_percent = 0



    plan.status = "Active"



    plan.updated_at = datetime.utcnow().isoformat()



    db.commit()



    db.refresh(plan)







    return {



        "success": True,



        "message": f"Training plan '{plan.title}' reactivated successfully.",



        "plan_id": plan.plan_id,



        "status": plan.status,



        "progress_percent": 0



    }







@app.put("/training/plans/{plan_identifier}")



def update_training_plan(



    plan_identifier: str,



    update_data: schemas.TrainingPlanUpdate,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    plan = None



    if plan_identifier.isdigit():



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.id == int(plan_identifier),



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        plan = db.query(models.TrainingPlan).filter(



            models.TrainingPlan.plan_id == plan_identifier,



            models.TrainingPlan.user_id == current_user.id



        ).first()



    if not plan:



        raise HTTPException(status_code=404, detail="Training plan not found")







    if update_data.status:



        plan.status = update_data.status



    if update_data.progress_percent is not None:



        plan.progress_percent = update_data.progress_percent



    if update_data.exercises_detail:



        plan.exercises_detail = update_data.exercises_detail







    plan.updated_at = datetime.utcnow().isoformat()



    db.commit()



    db.refresh(plan)



    return {"success": True, "message": "Plan updated"}







@app.post("/athlete/assessments", response_model=schemas.PhysicalAssessmentResponse)



def create_physical_assessment(assessment: schemas.PhysicalAssessmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    db_assessment = models.PhysicalAssessment(**assessment.model_dump(), user_id=current_user.id)



    db.add(db_assessment)



    db.commit()



    db.refresh(db_assessment)



    return db_assessment







@app.get("/athlete/assessments", response_model=list[schemas.PhysicalAssessmentResponse])



def get_physical_assessments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    records = db.query(models.PhysicalAssessment).filter(models.PhysicalAssessment.user_id == current_user.id).order_by(models.PhysicalAssessment.date.desc()).all()



    if not records:



        # Seed standard baseline assessments for this athlete



        baseline = [



            ("2026-10-15", "VO2 Max Aerobic Capacity", 56.4, "Top 10th percentile for collegiate wing-backs. High aerobic recovery baseline."),



            ("2026-10-18", "Functional Movement Screen (FMS)", 17.0, "Score 17/21. Slight asymmetry noted in in-line lunge and active straight-leg raise."),



            ("2026-10-22", "Countermovement Jump (CMJ)", 44.5, "Peak vertical impulse 2450 N. Takeoff symmetry 96.2% between left and right limb."),



            ("2026-10-25", "Y-Balance Dynamic Stability", 95.8, "Anterior reach 68cm, posteromedial 82cm, posterolateral 84cm. Safe limb symmetry."),



            ("2026-10-28", "Reactive Strength Index (RSI)", 2.18, "Drop jump from 30cm box. Ground contact time 210ms with high elastic rebound efficiency.")



        ]



        created = []



        for dt, tname, score, notes in baseline:



            rec = models.PhysicalAssessment(user_id=current_user.id, date=dt, test_name=tname, score=score, notes=notes)



            db.add(rec)



            created.append(rec)



        db.commit()



        for r in created:



            db.refresh(r)



        return created



    return records







@app.post("/athlete/performance", response_model=schemas.PerformanceRecordResponse)



def create_performance_record(record: schemas.PerformanceRecordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    db_record = models.PerformanceRecord(**record.model_dump(), user_id=current_user.id)



    db.add(db_record)



    db.commit()



    db.refresh(db_record)



    return db_record







@app.get("/athlete/performance", response_model=list[schemas.PerformanceRecordResponse])



def get_performance_records(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    records = db.query(models.PerformanceRecord).filter(models.PerformanceRecord.user_id == current_user.id).order_by(models.PerformanceRecord.date.desc()).all()



    if not records:



        seed_data = [



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



        created = []



        for dt, metric, val, unit in seed_data:



            rec = models.PerformanceRecord(user_id=current_user.id, date=dt, metric=metric, value=val, unit=unit)



            db.add(rec)



            created.append(rec)



        db.commit()



        for r in created:



            db.refresh(r)



        return created



    return records







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



            actions_detected=json.dumps(result['analytics'].get('actions_breakdown', [])),



            kinematics=json.dumps(result['analytics'].get('kinematics', {})),



            video_url=f"/processed/{result['filename']}",



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



            actions_detected=json.dumps(result_a['analytics'].get('actions_breakdown', [])),



            kinematics=json.dumps(result_a['analytics'].get('kinematics', {})),



            video_url=f"/processed/{result_a['filename']}",



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



            actions_detected=json.dumps(result_b['analytics'].get('actions_breakdown', [])),



            kinematics=json.dumps(result_b['analytics'].get('kinematics', {})),



            video_url=f"/processed/{result_b['filename']}",



            created_at=now_iso



        )



        db.add(db_analysis_a)



        db.add(db_analysis_b)



        db.commit()







        response_payload = {



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







        # Persist dual comparison history



        try:



            db_comp = models.DualVideoComparison(



                user_id=current_user.id,



                video_a_id=db_analysis_a.id,



                video_b_id=db_analysis_b.id,



                video_a_activity=db_analysis_a.activity,



                video_b_activity=db_analysis_b.activity,



                video_a_filename=db_analysis_a.video_url or file_a.filename,



                video_b_filename=db_analysis_b.video_url or file_b.filename,



                video_a_risk_score=db_analysis_a.risk_score,



                video_b_risk_score=db_analysis_b.risk_score,



                score_diff=comparison_data.get("score_diff", db_analysis_b.risk_score - db_analysis_a.risk_score),



                overall_verdict=comparison_data.get("overall_verdict", "Comparative Evaluation"),



                verdict_color=comparison_data.get("verdict_color", "emerald"),



                summary=comparison_data.get("summary", ""),



                insights=json.dumps(comparison_data.get("insights", [])),



                improvements=json.dumps(comparison_data.get("improvements", [])),



                deteriorations=json.dumps(comparison_data.get("deteriorations", [])),



                neutral_observations=json.dumps(comparison_data.get("neutral_observations", [])),



                action_transition_summary=comparison_data.get("action_transition_summary", ""),



                detailed_coaching_verdict=comparison_data.get("detailed_coaching_verdict", ""),



                actions_comparison=json.dumps(comparison_data.get("actions_comparison", [])),



                kinematics_comparison=json.dumps(comparison_data.get("kinematics_comparison", {})),



                metrics_diff=json.dumps(comparison_data.get("metrics_diff", {})),



                injury_probabilities_comparison=json.dumps(comparison_data.get("injury_probabilities_comparison", {})),



                created_at=datetime.utcnow().isoformat()



            )



            db.add(db_comp)



            db.commit()



            db.refresh(db_comp)



            response_payload["comparison_id"] = db_comp.id



        except Exception as save_err:



            print("Warning: failed to persist dual comparison:", save_err)







        return response_payload



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



    actions_a = json.loads(analysis_a.actions_detected) if hasattr(analysis_a, 'actions_detected') and analysis_a.actions_detected else []



    actions_b = json.loads(analysis_b.actions_detected) if hasattr(analysis_b, 'actions_detected') and analysis_b.actions_detected else []



    kin_a = json.loads(analysis_a.kinematics) if analysis_a.kinematics else {}



    kin_b = json.loads(analysis_b.kinematics) if analysis_b.kinematics else {}







    bio_a = {



        "max_trunk_lean": kin_a.get("trunk_lean_max", 0.0),



        "movement_asymmetry": round(abs(kin_a.get("knee_flexion_l_mean", 0.0) - kin_a.get("knee_flexion_r_mean", 0.0)), 2),



        "max_knee_valgus": max(kin_a.get("valgus_l_max", 0.0), kin_a.get("valgus_r_max", 0.0))



    }



    bio_b = {



        "max_trunk_lean": kin_b.get("trunk_lean_max", 0.0),



        "movement_asymmetry": round(abs(kin_b.get("knee_flexion_l_mean", 0.0) - kin_b.get("knee_flexion_r_mean", 0.0)), 2),



        "max_knee_valgus": max(kin_b.get("valgus_l_max", 0.0), kin_b.get("valgus_r_max", 0.0))



    }







    real_result_a = {



        "filename": analysis_a.video_url or "",



        "analytics": {



            "activity_analyzed": analysis_a.activity,



            "risk_score": analysis_a.risk_score,



            "risk_level": analysis_a.risk_level,



            "injury_probabilities": probs_a,



            "actions_breakdown": actions_a,



            "biomechanics": bio_a,



            "kinematics": kin_a



        }



    }



    real_result_b = {



        "filename": analysis_b.video_url or "",



        "analytics": {



            "activity_analyzed": analysis_b.activity,



            "risk_score": analysis_b.risk_score,



            "risk_level": analysis_b.risk_level,



            "injury_probabilities": probs_b,



            "actions_breakdown": actions_b,



            "biomechanics": bio_b,



            "kinematics": kin_b



        }



    }







    comparison_data = compare_two_video_analyses(real_result_a, real_result_b)







    comp_id = None



    try:



        db_comp = models.DualVideoComparison(



            user_id=current_user.id,



            video_a_id=analysis_a.id,



            video_b_id=analysis_b.id,



            video_a_activity=analysis_a.activity,



            video_b_activity=analysis_b.activity,



            video_a_filename=analysis_a.video_url,



            video_b_filename=analysis_b.video_url,



            video_a_risk_score=analysis_a.risk_score,



            video_b_risk_score=analysis_b.risk_score,



            score_diff=comparison_data.get("score_diff", analysis_b.risk_score - analysis_a.risk_score),



            overall_verdict=comparison_data.get("overall_verdict", "Comparative Evaluation"),



            verdict_color=comparison_data.get("verdict_color", "emerald"),



            summary=comparison_data.get("summary", ""),



            insights=json.dumps(comparison_data.get("insights", [])),



            improvements=json.dumps(comparison_data.get("improvements", [])),



            deteriorations=json.dumps(comparison_data.get("deteriorations", [])),



            neutral_observations=json.dumps(comparison_data.get("neutral_observations", [])),



            action_transition_summary=comparison_data.get("action_transition_summary", ""),



            detailed_coaching_verdict=comparison_data.get("detailed_coaching_verdict", ""),



            actions_comparison=json.dumps(comparison_data.get("actions_comparison", [])),



            kinematics_comparison=json.dumps(comparison_data.get("kinematics_comparison", {})),



            metrics_diff=json.dumps(comparison_data.get("metrics_diff", {})),



            injury_probabilities_comparison=json.dumps(comparison_data.get("injury_probabilities_comparison", {})),



            created_at=datetime.utcnow().isoformat()



        )



        db.add(db_comp)



        db.commit()



        db.refresh(db_comp)



        comp_id = db_comp.id



    except Exception as save_err:



        print("Warning: failed to persist existing comparison:", save_err)







    return {



        "success": True,



        "comparison_id": comp_id,



        "video_a": {



            "id": analysis_a.id,



            "activity": analysis_a.activity,



            "risk_score": analysis_a.risk_score,



            "risk_level": analysis_a.risk_level,



            "created_at": analysis_a.created_at,



            "injury_probabilities": probs_a,



            "processed_url": analysis_a.video_url or "",



            "video_url": analysis_a.video_url or "",



            "analytics": real_result_a["analytics"]



        },



        "video_b": {



            "id": analysis_b.id,



            "activity": analysis_b.activity,



            "risk_score": analysis_b.risk_score,



            "risk_level": analysis_b.risk_level,



            "created_at": analysis_b.created_at,



            "injury_probabilities": probs_b,



            "processed_url": analysis_b.video_url or "",



            "video_url": analysis_b.video_url or "",



            "analytics": real_result_b["analytics"]



        },



        "comparison": comparison_data



    }







from pdf_generator import (



    generate_single_analysis_pdf,



    generate_single_analysis_csv,



    generate_single_analysis_xlsx,



    generate_dual_comparison_pdf,



    generate_dual_comparison_csv,



    generate_dual_comparison_xlsx



)



from fastapi import Header



from typing import Optional







def resolve_user_for_export(token: Optional[str], authorization: Optional[str], db: Session):



    jwt_token = token



    if not jwt_token and authorization:



        parts = authorization.split(" ")



        if len(parts) == 2 and parts[0].lower() == "bearer":



            jwt_token = parts[1]



    if jwt_token:



        try:



            payload = auth.jwt.decode(



                jwt_token,



                auth.SECRET_KEY,



                algorithms=[auth.ALGORITHM],



                options={"verify_exp": False}



            )



            email = payload.get("sub")



            if email:



                u = db.query(models.User).filter(models.User.email == email).first()



                if u:



                    return u



        except Exception:



            pass



    # Fallback



    return db.query(models.User).filter(models.User.email == "demo@sportsai.com").first()







@app.get("/athlete/comparisons")



def get_athlete_comparisons(



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if current_user.role == "Administrator":

        comps = db.query(models.DualVideoComparison).order_by(models.DualVideoComparison.created_at.desc()).all()

    else:

        comps = db.query(models.DualVideoComparison).filter(

            models.DualVideoComparison.user_id == current_user.id

        ).order_by(models.DualVideoComparison.created_at.desc()).all()







    if not comps:



        # Seed initial comparison histories if athlete has existing analyses



        analyses = db.query(models.VideoAnalysis).filter(



            models.VideoAnalysis.user_id == current_user.id



        ).order_by(models.VideoAnalysis.id.desc()).all()



        



        if len(analyses) >= 2:



            seed_pairs = [(analyses[0], analyses[1])]



            if len(analyses) >= 4:



                seed_pairs.append((analyses[0], analyses[3]))







            for a1, a2 in seed_pairs:



                try:



                    p_a = json.loads(a1.injury_probabilities) if a1.injury_probabilities else {}



                    p_b = json.loads(a2.injury_probabilities) if a2.injury_probabilities else {}



                    k_a = json.loads(a1.kinematics) if a1.kinematics else {}



                    k_b = json.loads(a2.kinematics) if a2.kinematics else {}



                    r_a = {



                        "filename": a1.video_url or "",



                        "analytics": {



                            "activity_analyzed": a1.activity,



                            "risk_score": a1.risk_score,



                            "risk_level": a1.risk_level,



                            "injury_probabilities": p_a,



                            "actions_breakdown": [],



                            "biomechanics": {},



                            "kinematics": k_a



                        }



                    }



                    r_b = {



                        "filename": a2.video_url or "",



                        "analytics": {



                            "activity_analyzed": a2.activity,



                            "risk_score": a2.risk_score,



                            "risk_level": a2.risk_level,



                            "injury_probabilities": p_b,



                            "actions_breakdown": [],



                            "biomechanics": {},



                            "kinematics": k_b



                        }



                    }



                    cmp_d = compare_two_video_analyses(r_a, r_b)



                    sc_comp = models.DualVideoComparison(



                        user_id=current_user.id,



                        video_a_id=a1.id,



                        video_b_id=a2.id,



                        video_a_activity=a1.activity,



                        video_b_activity=a2.activity,



                        video_a_filename=a1.video_url,



                        video_b_filename=a2.video_url,



                        video_a_risk_score=a1.risk_score,



                        video_b_risk_score=a2.risk_score,



                        score_diff=cmp_d.get("score_diff", a2.risk_score - a1.risk_score),



                        overall_verdict=cmp_d.get("overall_verdict", "Comparative Evaluation"),



                        verdict_color=cmp_d.get("verdict_color", "emerald"),



                        summary=cmp_d.get("summary", ""),



                        insights=json.dumps(cmp_d.get("insights", [])),



                        improvements=json.dumps(cmp_d.get("improvements", [])),



                        deteriorations=json.dumps(cmp_d.get("deteriorations", [])),



                        neutral_observations=json.dumps(cmp_d.get("neutral_observations", [])),



                        action_transition_summary=cmp_d.get("action_transition_summary", ""),



                        detailed_coaching_verdict=cmp_d.get("detailed_coaching_verdict", ""),



                        actions_comparison=json.dumps(cmp_d.get("actions_comparison", [])),



                        kinematics_comparison=json.dumps(cmp_d.get("kinematics_comparison", {})),



                        metrics_diff=json.dumps(cmp_d.get("metrics_diff", {})),



                        injury_probabilities_comparison=json.dumps(cmp_d.get("injury_probabilities_comparison", {})),



                        created_at=datetime.utcnow().isoformat()



                    )



                    db.add(sc_comp)



                except Exception as seed_err:



                    print("Seed error:", seed_err)



            db.commit()



            comps = db.query(models.DualVideoComparison).filter(



                models.DualVideoComparison.user_id == current_user.id



            ).order_by(models.DualVideoComparison.created_at.desc()).all()







    # Format list response



    results = []



    for c in comps:



        def _res_url(fn, vid):



            if fn and (fn.startswith("http") or fn.startswith("/processed") or fn.startswith("/uploads")):



                return fn



            if vid:



                va = db.query(models.VideoAnalysis).filter(models.VideoAnalysis.id == vid).first()



                if va and va.video_url:



                    return va.video_url



            if fn:



                return fn if fn.startswith("/") else f"/processed/{fn}"



            return None



        v_a = _res_url(c.video_a_filename, c.video_a_id)



        v_b = _res_url(c.video_b_filename, c.video_b_id)







        results.append({



            "id": c.id,



            "user_id": c.user_id,



            "video_a_id": c.video_a_id,



            "video_b_id": c.video_b_id,



            "video_a_activity": c.video_a_activity,



            "video_b_activity": c.video_b_activity,



            "video_a_filename": c.video_a_filename,



            "video_b_filename": c.video_b_filename,



            "video_a_url": v_a,



            "video_b_url": v_b,



            "video_a_risk_score": c.video_a_risk_score,



            "video_b_risk_score": c.video_b_risk_score,



            "score_diff": c.score_diff,



            "overall_verdict": c.overall_verdict,



            "verdict_color": c.verdict_color,



            "summary": c.summary,



            "created_at": c.created_at



        })



    return results







@app.get("/athlete/comparisons/{comparison_id}")



def get_single_comparison(



    comparison_id: int,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if current_user.role == "Administrator":

        comp = db.query(models.DualVideoComparison).filter(models.DualVideoComparison.id == comparison_id).first()

    else:

        comp = db.query(models.DualVideoComparison).filter(

            models.DualVideoComparison.id == comparison_id,

            models.DualVideoComparison.user_id == current_user.id

        ).first()



    if not comp:



        raise HTTPException(status_code=404, detail=f"Dual comparison #{comparison_id} not found")







    def _parse(val, default):



        if not val:



            return default



        try:



            return json.loads(val) if isinstance(val, str) else val



        except:



            return default







    def _res_single_url(fn, vid):



        if fn and (fn.startswith("http") or fn.startswith("/processed") or fn.startswith("/uploads")):



            return fn



        if vid:



            va = db.query(models.VideoAnalysis).filter(models.VideoAnalysis.id == vid).first()



            if va and va.video_url:



                return va.video_url



        if fn:



            return fn if fn.startswith("/") else f"/processed/{fn}"



        return None



    v_a = _res_single_url(comp.video_a_filename, comp.video_a_id)



    v_b = _res_single_url(comp.video_b_filename, comp.video_b_id)







    return {



        "id": comp.id,



        "user_id": comp.user_id,



        "video_a_id": comp.video_a_id,



        "video_b_id": comp.video_b_id,



        "video_a_activity": comp.video_a_activity,



        "video_b_activity": comp.video_b_activity,



        "video_a_filename": comp.video_a_filename,



        "video_b_filename": comp.video_b_filename,



        "video_a_url": v_a,



        "video_b_url": v_b,



        "video_a_risk_score": comp.video_a_risk_score,



        "video_b_risk_score": comp.video_b_risk_score,



        "score_diff": comp.score_diff,



        "overall_verdict": comp.overall_verdict,



        "verdict_color": comp.verdict_color,



        "summary": comp.summary,



        "insights": _parse(comp.insights, []),



        "improvements": _parse(comp.improvements, []),



        "deteriorations": _parse(comp.deteriorations, []),



        "neutral_observations": _parse(comp.neutral_observations, []),



        "action_transition_summary": comp.action_transition_summary,



        "detailed_coaching_verdict": comp.detailed_coaching_verdict,



        "actions_comparison": _parse(comp.actions_comparison, []),



        "kinematics_comparison": _parse(comp.kinematics_comparison, {}),



        "metrics_diff": _parse(comp.metrics_diff, {}),



        "injury_probabilities_comparison": _parse(comp.injury_probabilities_comparison, {}),



        "created_at": comp.created_at



    }







@app.post("/athlete/comparisons/delete")



def delete_athlete_comparisons(



    req: schemas.DeleteComparisonsRequest,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if not req.comparison_ids:



        return {"success": True, "deleted_count": 0}



        



    deleted_count = db.query(models.DualVideoComparison).filter(



        models.DualVideoComparison.id.in_(req.comparison_ids),



        models.DualVideoComparison.user_id == current_user.id



    ).delete(synchronize_session=False)



    db.commit()



    



    return {



        "success": True,



        "deleted_count": deleted_count,



        "message": f"Successfully deleted {deleted_count} dual video comparison report(s)."



    }







@app.get("/athlete/comparisons/{comparison_id}/export/pdf")



def export_dual_comparison_pdf_endpoint(



    comparison_id: int,



    token: Optional[str] = None,



    authorization: Optional[str] = Header(None),



    db: Session = Depends(get_db)



):



    user = resolve_user_for_export(token, authorization, db)



    if not user:



        raise HTTPException(status_code=401, detail="Authentication required for PDF download")







    comp = db.query(models.DualVideoComparison).filter(



        models.DualVideoComparison.id == comparison_id,



        models.DualVideoComparison.user_id == user.id



    ).first()



    if not comp:



        raise HTTPException(status_code=404, detail="Dual video comparison report not found")







    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == user.id).first()



    pdf_buffer = generate_dual_comparison_pdf(comp, user, profile)







    safe_title = f"{comp.video_a_activity}_vs_{comp.video_b_activity}".replace(" ", "_")



    filename = f"SportsAI_Dual_Report_{comp.id}_{safe_title}.pdf"







    return StreamingResponse(



        pdf_buffer,



        media_type="application/pdf",



        headers={



            "Content-Disposition": f'attachment; filename="{filename}"'



        }



    )







@app.get("/athlete/comparisons/{comparison_id}/export/csv")



def export_dual_comparison_csv_endpoint(



    comparison_id: int,



    token: Optional[str] = None,



    authorization: Optional[str] = Header(None),



    format: str = "xlsx",



    db: Session = Depends(get_db)



):



    user = resolve_user_for_export(token, authorization, db)



    if not user:



        raise HTTPException(status_code=401, detail="Authentication required for export")







    comp = db.query(models.DualVideoComparison).filter(



        models.DualVideoComparison.id == comparison_id,



        models.DualVideoComparison.user_id == user.id



    ).first()



    if not comp:



        raise HTTPException(status_code=404, detail="Dual video comparison report not found")







    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == user.id).first()



    safe_title = f"{comp.video_a_activity}_vs_{comp.video_b_activity}".replace(" ", "_")







    if format.lower() == "csv":



        csv_content = generate_dual_comparison_csv(comp, user, profile)



        filename = f"SportsAI_Dual_Report_{comp.id}_{safe_title}.csv"



        return StreamingResponse(



            iter([csv_content]),



            media_type="text/csv; charset=utf-8",



            headers={"Content-Disposition": f'attachment; filename="{filename}"'}



        )



    else:



        xlsx_stream = generate_dual_comparison_xlsx(comp, user, profile)



        filename = f"SportsAI_Dual_Report_{comp.id}_{safe_title}.xlsx"



        return StreamingResponse(



            xlsx_stream,



            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",



            headers={"Content-Disposition": f'attachment; filename="{filename}"'}



        )







@app.get("/athlete/analyses", response_model=list[schemas.VideoAnalysisResponse])



def get_athlete_analyses(



    overview_only: bool = False,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if current_user.role == "Administrator":

        query = db.query(models.VideoAnalysis)

    else:

        query = db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == current_user.id)



    if overview_only:

        query = query.filter(models.VideoAnalysis.is_cleared_from_overview == 0)



    return query.order_by(models.VideoAnalysis.created_at.desc()).all()







@app.post("/athlete/analyses/clear-overview")



def clear_athlete_overview(



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    """



    Clears all analyses from the Home/Overview display while leaving them permanently intact in the Reports section.



    """



    db.query(models.VideoAnalysis).filter(



        models.VideoAnalysis.user_id == current_user.id,



        models.VideoAnalysis.is_cleared_from_overview == 0



    ).update({"is_cleared_from_overview": 1})



    db.commit()



    return {



        "success": True,



        "message": "All reports have been cleared from My Overview. They remain preserved in the Reports tab."



    }







@app.post("/athlete/analyses/restore-overview")



def restore_athlete_overview(



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    """



    Restores cleared reports back to the Home/Overview display.



    """



    db.query(models.VideoAnalysis).filter(



        models.VideoAnalysis.user_id == current_user.id,



        models.VideoAnalysis.is_cleared_from_overview == 1



    ).update({"is_cleared_from_overview": 0})



    db.commit()



    return {



        "success": True,



        "message": "All reports restored to My Overview."



    }







@app.post("/athlete/analyses/delete")



def delete_athlete_analyses(



    req: schemas.DeleteAnalysesRequest,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    """



    Deletes specific selected video analysis reports permanently.



    """



    if not req.analysis_ids:



        return {"success": True, "deleted_count": 0}



        



    deleted_count = db.query(models.VideoAnalysis).filter(



        models.VideoAnalysis.id.in_(req.analysis_ids),



        models.VideoAnalysis.user_id == current_user.id



    ).delete(synchronize_session=False)



    db.commit()



    



    return {



        "success": True,



        "deleted_count": deleted_count,



        "message": f"Successfully deleted {deleted_count} report(s)."



    }







@app.get("/athlete/analyses/{analysis_id}")



def get_single_analysis(



    analysis_id: int,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if current_user.role == "Administrator":

        analysis = db.query(models.VideoAnalysis).filter(models.VideoAnalysis.id == analysis_id).first()

    else:

        analysis = db.query(models.VideoAnalysis).filter(

            models.VideoAnalysis.id == analysis_id,

            models.VideoAnalysis.user_id == current_user.id

        ).first()



    if not analysis:



        raise HTTPException(status_code=404, detail=f"Analysis report #{analysis_id} not found")







    probs = {}



    try:



        probs = json.loads(analysis.injury_probabilities) if analysis.injury_probabilities else {}



    except:



        probs = {}







    actions = []



    try:



        actions = json.loads(analysis.actions_detected) if analysis.actions_detected else []



    except:



        actions = []







    kin = {}



    try:



        kin = json.loads(analysis.kinematics) if analysis.kinematics else {}



    except:



        kin = {}







    return {



        "id": analysis.id,



        "user_id": analysis.user_id,



        "activity": analysis.activity,



        "surface_type": analysis.surface_type,



        "footwear": analysis.footwear,



        "rpe": analysis.rpe,



        "sleep_quality": analysis.sleep_quality,



        "risk_score": analysis.risk_score,



        "risk_level": analysis.risk_level,



        "injury_probabilities": probs,



        "corrective_recommendation": analysis.corrective_recommendation,



        "actions_detected": actions,



        "kinematics": kin,



        "video_url": analysis.video_url or "",



        "created_at": analysis.created_at,



        "is_cleared_from_overview": analysis.is_cleared_from_overview or 0



    }







@app.get("/athlete/analyses/{analysis_id}/export/pdf")



def export_single_analysis_pdf_endpoint(



    analysis_id: int,



    token: Optional[str] = None,



    authorization: Optional[str] = Header(None),



    db: Session = Depends(get_db)



):



    user = resolve_user_for_export(token, authorization, db)



    if not user:



        raise HTTPException(status_code=401, detail="Authentication required for PDF download")







    analysis = db.query(models.VideoAnalysis).filter(



        models.VideoAnalysis.id == analysis_id,



        models.VideoAnalysis.user_id == user.id



    ).first()



    if not analysis:



        raise HTTPException(status_code=404, detail="Analysis report not found")







    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == user.id).first()



    pdf_buffer = generate_single_analysis_pdf(analysis, user, profile)







    safe_activity = (analysis.activity or "Report").replace(" ", "_")



    filename = f"SportsAI_Report_{analysis.id}_{safe_activity}.pdf"







    return StreamingResponse(



        pdf_buffer,



        media_type="application/pdf",



        headers={



            "Content-Disposition": f'attachment; filename="{filename}"'



        }



    )







@app.get("/athlete/analyses/{analysis_id}/export/csv")



def export_single_analysis_csv_endpoint(



    analysis_id: int,



    token: Optional[str] = None,



    authorization: Optional[str] = Header(None),



    format: str = "xlsx",



    db: Session = Depends(get_db)



):



    user = resolve_user_for_export(token, authorization, db)



    if not user:



        raise HTTPException(status_code=401, detail="Authentication required for export")







    analysis = db.query(models.VideoAnalysis).filter(



        models.VideoAnalysis.id == analysis_id,



        models.VideoAnalysis.user_id == user.id



    ).first()



    if not analysis:



        raise HTTPException(status_code=404, detail="Analysis report not found")







    profile = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == user.id).first()



    safe_activity = (analysis.activity or "Report").replace(" ", "_")







    if format.lower() == "csv":



        csv_content = generate_single_analysis_csv(analysis, user, profile)



        filename = f"SportsAI_Report_{analysis.id}_{safe_activity}.csv"



        return StreamingResponse(



            iter([csv_content]),



            media_type="text/csv; charset=utf-8",



            headers={"Content-Disposition": f'attachment; filename="{filename}"'}



        )



    else:



        xlsx_stream = generate_single_analysis_xlsx(analysis, user, profile)



        filename = f"SportsAI_Report_{analysis.id}_{safe_activity}.xlsx"



        return StreamingResponse(



            xlsx_stream,



            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",



            headers={"Content-Disposition": f'attachment; filename="{filename}"'}



        )







@app.get("/recommendations/{activity}")



def get_activity_recommendations(



    activity: str,



    risk_level: str = "High Risk",



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    """



    Returns clinical recommendations, form cues, and corrective plans tailored specifically



    for the activity and risk level, linked directly to their dedicated training plans.



    """



    act_lower = activity.lower()



    



    # Defaults



    data = {



        "activity": activity,



        "risk_level": risk_level,



        "primary_risk_factors": [],



        "clinical_rationale": "",



        "corrective_cues": [],



        "prescribed_exercises": [],



        "training_plan_ref": "core-stability",



        "recovery_protocol": ""



    }







    if "throw" in act_lower or "shot" in act_lower or "javelin" in act_lower or "overhead" in act_lower:



        data["activity"] = "Throwing"



        data["primary_risk_factors"] = [



            "Medial elbow distraction valgus stress during late arm cocking and acceleration phase.",



            "Rotator cuff eccentric deceleration fatigue causing glenohumeral anterior translation.",



            "Asymmetric trunk lateral flexion compensating for reduced pelvic rotational follow-through."



        ]



        data["clinical_rationale"] = (



            "High joint angular velocity at the wrist and shoulder requires adequate posterior shoulder muscle "



            "eccentric capacity to decelerate the throwing limb. Lack of proximal trunk-pelvis dissociation "



            "magnifies shear stress onto the medial collateral ligament (UCL) and supraspinatus tendon."



        )



        data["corrective_cues"] = [



            "Initiate arm drive from thoracic and pelvic rotation, not isolated arm snapping.",



            "Maintain shoulder-elbow height alignment at release without dropping the trailing elbow.",



            "Follow through across the contralateral hip to dissipate angular kinetic energy safely.",



            "Brace the lead leg firmly to transfer ground reaction force upward through the kinetic chain."



        ]



        data["prescribed_exercises"] = [



            {"name": "Prone Y-T-W Scapular Stabilizers", "sets": 3, "reps": "12 reps", "tempo": "2-1-2", "notes": "Scapular upward rotation control and lower trap activation."},



            {"name": "Sleeper Stretch & Cross-Body Stretch", "sets": 3, "reps": "30 sec hold", "tempo": "Static", "notes": "Posterior capsule mobility preservation."},



            {"name": "Half-Kneeling Rotational Med-Ball Slams", "sets": 4, "reps": "8 per side", "tempo": "Explosive", "notes": "Torso-pelvic rotational power sequencing."},



            {"name": "Banded External Rotations at 90°", "sets": 3, "reps": "15 reps", "tempo": "3-0-1", "notes": "Infraspinatus & teres minor deceleration capacity."}



        ]



        data["training_plan_ref"] = "throwing-scapular-stability"



        data["recovery_protocol"] = "Cold compression on medial elbow, foam rolling thoracic spine, active posterior rotator cuff release."







    elif "squat" in act_lower:



        data["activity"] = "Squatting"



        data["primary_risk_factors"] = [



            "Dynamic Knee Valgus (FPPA inward medial collapse) exceeding functional safe thresholds (> 15°).",



            "Compensatory forward trunk lean due to restricted ankle dorsiflexion mobility.",



            "Asymmetric weight distribution with unilateral knee load disparity."



        ]



        data["clinical_rationale"] = (



            "Medial femoral adduction and internal rotation during the eccentric descent causes substantial "



            "anterior cruciate ligament (ACL) shear forces and patellofemoral compressive stress. "



            "Strengthening the gluteus medius and optimizing hip external rotator recruitment prevents this collapse."



        )



        data["corrective_cues"] = [



            "Actively press knees outward in the direction of the 2nd and 3rd toes throughout descent.",



            "Maintain a neutral upright spine cylinder with engaged intra-abdominal core bracing.",



            "Distribute bodyweight evenly across the tripod foot (heel, 1st metatarsal, 5th metatarsal)."



        ]



        data["prescribed_exercises"] = [



            {"name": "Banded Monster Walks & Side Steps", "sets": 3, "reps": "15 steps each way", "tempo": "2-0-2", "notes": "Gluteus medius abductor motor re-education."},



            {"name": "Single Leg Romanian Deadlifts", "sets": 4, "reps": "10 reps per limb", "tempo": "3-1-1", "notes": "Eccentric hamstring and unilateral pelvic stability."},



            {"name": "Goblet Squats with Resistance Band around Knees", "sets": 3, "reps": "12 reps", "tempo": "3-1-1", "notes": "Real-time proprioceptive feedback against valgus inward collapse."},



            {"name": "Knee-to-Wall Ankle Dorsiflexion Mobilization", "sets": 3, "reps": "10 reps per leg", "tempo": "Static hold", "notes": "Talocrural joint closed-chain dorsiflexion restoration."}



        ]



        data["training_plan_ref"] = "knee-valgus"



        data["recovery_protocol"] = "Hip adductor foam rolling, calf & soleus wall mobilization, gentle quad tissue release."







    elif "sprint" in act_lower or "run" in act_lower:



        data["activity"] = "Sprinting"



        data["primary_risk_factors"] = [



            "High peak swing velocity with insufficient eccentric hamstring braking capacity.",



            "Excessive pelvic anterior tilt during terminal flight increasing hamstring origin strain.",



            "Contralateral pelvic drop causing adductor and knee shear stress."



        ]



        data["clinical_rationale"] = (



            "Sprinting imposes extreme eccentric forces on the biceps femoris at late swing phase. "



            "Developing high-velocity eccentric hamstring strength is crucial for avoiding acute strain tears."



        )



        data["corrective_cues"] = [



            "Focus on active clawing ground strike directly under center of mass, avoiding overstriding.",



            "Maintain upright neutral pelvis without excessive lumbar hyperextension.",



            "High knee drive synchronized with rhythmic contralateral arm swings."



        ]



        data["prescribed_exercises"] = [



            {"name": "Nordic Hamstring Curls", "sets": 3, "reps": "6-8 reps", "tempo": "4-0-1", "notes": "Gold-standard eccentric hamstring strain prevention."},



            {"name": "A-Skips & High Knee Wall Drills", "sets": 3, "reps": "20 meters", "tempo": "Dynamic", "notes": "Anterior pelvic tilt reduction and sprint posture rhythm."},



            {"name": "Heavy Single-Leg Hip Thrusts", "sets": 4, "reps": "8 reps per leg", "tempo": "2-1-2", "notes": "Terminal hip extension gluteus maximus drive."},



            {"name": "Suitcase Carries & Anti-Lateral Trunk Flexion", "sets": 3, "reps": "30 meters per side", "tempo": "Controlled", "notes": "Quadratus lumborum and pelvic drop prevention."}



        ]



        data["training_plan_ref"] = "sprint-hamstring-resilience"



        data["recovery_protocol"] = "Contrast baths, light active recovery jogging, hamstring gentle active isolated stretching."











    elif "jump" in act_lower or "land" in act_lower:



        data["activity"] = "Jumping / Landing"



        data["primary_risk_factors"] = [



            "Stiff-legged landing impact deceleration (> 2.0 G) with deficient knee flexion damping.",



            "Bilateral knee valgus collapse upon ground contact.",



            "Unequal limb force absorption with asymmetric touchdown timing."



        ]



        data["clinical_rationale"] = (



            "Landing with extended knees (< 30° flexion) transfers high ground reaction shock directly into "



            "the ACL and meniscus rather than dampening it muscularly through quadriceps and gluteal eccentrics."



        )



        data["corrective_cues"] = [



            "Land softly on the ball of the foot and immediately roll back onto the heel while hinging at the hips.",



            "Ensure knees stay wide and track directly over the toes upon touchdown.",



            "Aim for a quiet landing; sound reflects unattenuated impact shock."



        ]



        data["prescribed_exercises"] = [



            {"name": "Depth Drops to Athletic Catch Position", "sets": 4, "reps": "6 drops from 30cm", "tempo": "Controlled catch", "notes": "Neuromuscular landing absorption mechanics and knee valgus control."},



            {"name": "Single-Leg Box Step Downs", "sets": 3, "reps": "10 reps per side", "tempo": "3-1-1", "notes": "Eccentric quadriceps deceleration and patellofemoral tracking."},



            {"name": "Banded Lateral Pogo Jumps", "sets": 3, "reps": "20 reps", "tempo": "Elastic rebound", "notes": "Ankle stiffness and reactive neuromuscular ground contact stabilization."},



            {"name": "Broad Jump to Stick with 3-Second Freeze", "sets": 3, "reps": "5 jumps", "tempo": "Stick & hold", "notes": "Dissipates horizontal kinetic momentum safely through hip hinge."}



        ]



        data["training_plan_ref"] = "landing-shock-absorption"



        data["recovery_protocol"] = "Cold compression therapy, elevated leg drainage, plantar fascia release."







    elif "cut" in act_lower or "agility" in act_lower:



        data["activity"] = "Cutting Movements"



        data["primary_risk_factors"] = [



            "High knee abduction moment (valgus collapse) combined with foot plant internal rotation.",



            "Excessive lateral trunk sway over the plant foot magnifying knee joint shear force.",



            "Adductor groin strain vulnerability during maximum lateral deceleration redirection."



        ]



        data["clinical_rationale"] = (



            "Sharp change of direction generates multi-planar shear forces across the ACL and adductor complex. "



            "Athletes with insufficient anti-rotational core stiffness and weak eccentric hip abductors demonstrate high rates of non-contact ligament injury."



        )



        data["corrective_cues"] = [



            "Drop center of mass prior to plant step rather than braking with an upright extended posture.",



            "Plant foot firmly aligned with intended direction vector; avoid lateral foot spinning.",



            "Brace core muscles to keep trunk centered over base of support throughout the redirection phase."



        ]



        data["prescribed_exercises"] = [



            {"name": "90° Cut Deceleration & Plant Drill", "sets": 4, "reps": "5 cuts each side", "tempo": "Decelerate & hold", "notes": "Low center of mass cut mechanics without knee abduction collapse."},



            {"name": "Banded Lateral Skater Hops", "sets": 3, "reps": "12 reps", "tempo": "1-2-1", "notes": "Frontal plane explosive force absorption and dynamic knee stabilization."},



            {"name": "Copenhagen Adductor Planks", "sets": 3, "reps": "25 sec per side", "tempo": "Isometric", "notes": "Protects groin/adductor complex during intense lateral cut plants."},



            {"name": "Pallof Press with Lateral Step", "sets": 3, "reps": "10 reps per side", "tempo": "2-1-2", "notes": "Anti-rotational core rigidity preventing upper body sway during direction change."}



        ]



        data["training_plan_ref"] = "cutting-acl-protection"



        data["recovery_protocol"] = "Adductor isometric squeeze recovery, contrast water therapy, dynamic hip opening flow."







    elif "recov" in act_lower or "post-match" in act_lower:



        data["activity"] = "Post-Match Recovery"



        data["primary_risk_factors"] = [



            "Accumulated central nervous system fatigue and delayed neuromuscular reaction time.",



            "Elevated systemic muscle soreness and micro-trauma inflammatory markers.",



            "Soft tissue tightness restricting functional joint range of motion."



        ]



        data["clinical_rationale"] = (



            "High athletic training volumes require intentional active restoration to clear metabolic byproducts, "



            "normalize sympathetic tone, and prevent overtraining injury syndromes."



        )



        data["corrective_cues"] = [



            "Prioritize full diaphragmatic nasal breathing to trigger parasympathetic down-regulation.",



            "Focus on smooth, non-forced mobility through multi-planar movement patterns."



        ]



        data["prescribed_exercises"] = [



            {"name": "Full Body Foam Rolling & Myofascial Release", "sets": 1, "reps": "10 mins", "tempo": "Continuous", "notes": "Targeting quads, IT band, calves, thoracic spine."},



            {"name": "Dynamic Multi-Planar Stretching Flow", "sets": 1, "reps": "10 mins", "tempo": "Fluid", "notes": "World's greatest stretch, hip flexor opening, hamstring sweep."},



            {"name": "Cold Plunge / Contrast Hydrotherapy", "sets": 3, "reps": "3 min cold / 1 min warm", "tempo": "Contrast", "notes": "Reduces inflammatory markers and microvascular swelling."},



            {"name": "Diaphragmatic Parasympathetic Down-Regulation Breathing", "sets": 1, "reps": "5 mins", "tempo": "4-7-8 rhythm", "notes": "Shifts autonomic nervous system to parasympathetic recovery state."}



        ]



        data["training_plan_ref"] = "post-match-recovery"



        data["recovery_protocol"] = "8+ hours restorative sleep, high-electrolyte hydration, 1.6-2.0g/kg protein re-synthesis."







    else:



        # General athletic movement / Sports Specific Drills



        data["activity"] = activity if activity else "Sports Specific Drills"



        data["primary_risk_factors"] = [



            "Elevated dynamic joint loading beyond physiological baseline.",



            "Mild movement asymmetry between left and right kinetic chains."



        ]



        data["clinical_rationale"] = (



            "Optimizing core stability and unilateral neuromuscular balance minimizes cumulative joint fatigue "



            "and prevents micro-trauma accumulation across multi-directional movement patterns."



        )



        data["corrective_cues"] = [



            "Maintain core bracing throughout complex athletic transitions.",



            "Focus on bilateral symmetry in ground force application."



        ]



        data["prescribed_exercises"] = [



            {"name": "Deadbugs & Bird-Dogs", "sets": 3, "reps": "10 reps each", "tempo": "2-2-2", "notes": "Lumbar-pelvic core stabilization cylinder."},



            {"name": "Lateral Monster Band Walks", "sets": 3, "reps": "15 steps", "tempo": "2-0-2", "notes": "Hip abductor endurance."},



            {"name": "Farmer's Carries", "sets": 4, "reps": "40 meters", "tempo": "Steady walk", "notes": "Full-body anti-lateral flexion and postural control."},



            {"name": "Forearm Planks with Shoulder Taps", "sets": 3, "reps": "12 reps", "tempo": "Controlled", "notes": "Anti-rotational trunk stability."}



        ]



        data["training_plan_ref"] = "core-stability"



        data["recovery_protocol"] = "Full body foam rolling, 8+ hours quality sleep, hydration protocol."







    return data







# ==============================================================================



# MODULE 2: PHYSICAL ASSESSMENT & PERFORMANCE TRACKING ENDPOINTS



# ==============================================================================







@app.post("/athlete/assessments", response_model=schemas.PhysicalAssessmentResponse)



def create_physical_assessment(



    assessment: schemas.PhysicalAssessmentCreate,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    db_assessment = models.PhysicalAssessment(**assessment.model_dump(), user_id=current_user.id)



    db.add(db_assessment)



    db.commit()



    db.refresh(db_assessment)



    return db_assessment







@app.get("/athlete/assessments", response_model=list[schemas.PhysicalAssessmentResponse])



def get_physical_assessments(



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if current_user.role in ["Coach", "Physiotherapist", "Sports Scientist", "Administrator"]:



        assessments = db.query(models.PhysicalAssessment).order_by(models.PhysicalAssessment.date.desc()).all()



    else:



        assessments = db.query(models.PhysicalAssessment).filter(



            models.PhysicalAssessment.user_id == current_user.id



        ).order_by(models.PhysicalAssessment.date.desc()).all()



    



    if not assessments:



        starter_tests = [



            {"date": (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d"), "test_name": "VO2 Max Aerobic Capacity", "score": 54.2, "notes": "High aerobic baseline sustained during ramp protocol."},



            {"date": (datetime.utcnow() - timedelta(days=9)).strftime("%Y-%m-%d"), "test_name": "Countermovement Jump (CMJ) Height", "score": 48.5, "notes": "Explosive triple extension with balanced landing mechanics."},



            {"date": (datetime.utcnow() - timedelta(days=4)).strftime("%Y-%m-%d"), "test_name": "Single-Leg Y-Balance Stability Test", "score": 92.0, "notes": "Within normal range (<4cm bilateral anterior reach difference)."},



            {"date": datetime.utcnow().strftime("%Y-%m-%d"), "test_name": "Hamstring Eccentric NordBord Peak Force", "score": 380.0, "notes": "Good bilateral torque symmetry (380N Left vs 375N Right)."}



        ]



        for t in starter_tests:



            rec = models.PhysicalAssessment(**t, user_id=current_user.id)



            db.add(rec)



        db.commit()



        assessments = db.query(models.PhysicalAssessment).filter(



            models.PhysicalAssessment.user_id == current_user.id



        ).order_by(models.PhysicalAssessment.date.desc()).all()



    return assessments







@app.delete("/athlete/assessments/{assessment_id}")



def delete_physical_assessment(



    assessment_id: int,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    query = db.query(models.PhysicalAssessment).filter(models.PhysicalAssessment.id == assessment_id)



    if current_user.role not in ["Coach", "Administrator"]:



        query = query.filter(models.PhysicalAssessment.user_id == current_user.id)



    rec = query.first()



    if not rec:



        raise HTTPException(status_code=404, detail="Assessment not found")



    db.delete(rec)



    db.commit()



    return {"success": True, "message": "Assessment record deleted successfully"}







@app.post("/athlete/performance", response_model=schemas.PerformanceRecordResponse)



def create_performance_record(



    record: schemas.PerformanceRecordCreate,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    db_rec = models.PerformanceRecord(**record.model_dump(), user_id=current_user.id)



    db.add(db_rec)



    db.commit()



    db.refresh(db_rec)



    return db_rec







@app.get("/athlete/performance", response_model=list[schemas.PerformanceRecordResponse])



def get_performance_records(



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if current_user.role in ["Coach", "Sports Scientist", "Administrator"]:



        records = db.query(models.PerformanceRecord).order_by(models.PerformanceRecord.date.desc()).all()



    else:



        records = db.query(models.PerformanceRecord).filter(



            models.PerformanceRecord.user_id == current_user.id



        ).order_by(models.PerformanceRecord.date.desc()).all()



    



    if not records:



        starter_records = [



            {"date": (datetime.utcnow() - timedelta(days=21)).strftime("%Y-%m-%d"), "metric": "40m Sprint Time", "value": 4.95, "unit": "sec"},



            {"date": (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d"), "metric": "40m Sprint Time", "value": 4.88, "unit": "sec"},



            {"date": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"), "metric": "40m Sprint Time", "value": 4.82, "unit": "sec"},



            {"date": datetime.utcnow().strftime("%Y-%m-%d"), "metric": "40m Sprint Time", "value": 4.79, "unit": "sec"},



            {"date": (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d"), "metric": "Max Dynamic Knee Valgus", "value": 18.5, "unit": "deg"},



            {"date": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"), "metric": "Max Dynamic Knee Valgus", "value": 15.2, "unit": "deg"},



            {"date": datetime.utcnow().strftime("%Y-%m-%d"), "metric": "Max Dynamic Knee Valgus", "value": 12.8, "unit": "deg"},



            {"date": datetime.utcnow().strftime("%Y-%m-%d"), "metric": "Acute:Chronic Workload Ratio (ACWR)", "value": 1.15, "unit": "ratio"}



        ]



        for r in starter_records:



            rec = models.PerformanceRecord(**r, user_id=current_user.id)



            db.add(rec)



        db.commit()



        records = db.query(models.PerformanceRecord).filter(



            models.PerformanceRecord.user_id == current_user.id



        ).order_by(models.PerformanceRecord.date.desc()).all()



    return records







@app.delete("/athlete/performance/{record_id}")



def delete_performance_record(



    record_id: int,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    query = db.query(models.PerformanceRecord).filter(models.PerformanceRecord.id == record_id)



    if current_user.role not in ["Coach", "Administrator"]:



        query = query.filter(models.PerformanceRecord.user_id == current_user.id)



    rec = query.first()



    if not rec:



        raise HTTPException(status_code=404, detail="Performance record not found")



    db.delete(rec)



    db.commit()



    return {"success": True, "message": "Performance record deleted successfully"}







# ==============================================================================



# MODULE 11: NOTIFICATION & ALERT SYSTEM ENDPOINTS



# ==============================================================================







@app.get("/notifications", response_model=list[schemas.NotificationResponse])



def get_notifications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    notifs = db.query(models.Notification).filter(



        models.Notification.user_id == current_user.id



    ).order_by(models.Notification.created_at.desc()).all()



    



    if not notifs:



        starter_notifs = [



            models.Notification(



                user_id=current_user.id,



                title="High Injury Risk Detected",



                message="Your recent analysis for Throwing indicated high valgus stress. Please review corrective recommendations.",



                type="alert",



                created_at=(datetime.utcnow() - timedelta(hours=2)).isoformat()



            ),



            models.Notification(



                user_id=current_user.id,



                title="Training Load Advisory",



                message="Weekly volume increased by 22%. Maintain adequate hydration and sleep hygiene.",



                type="warning",



                created_at=(datetime.utcnow() - timedelta(hours=14)).isoformat()



            ),



            models.Notification(



                user_id=current_user.id,



                title="Recovery Protocol Assigned",



                message="Your physiotherapist updated the Scapular Stabilization plan. 4 targeted exercises prescribed.",



                type="info",



                created_at=(datetime.utcnow() - timedelta(days=1)).isoformat()



            )



        ]



        for n in starter_notifs:



            db.add(n)



        db.commit()



        notifs = db.query(models.Notification).filter(



            models.Notification.user_id == current_user.id



        ).order_by(models.Notification.created_at.desc()).all()



    return notifs







@app.post("/notifications", response_model=schemas.NotificationResponse)



def create_notification(



    notif_in: schemas.NotificationCreate,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    target_user_id = notif_in.user_id if notif_in.user_id else current_user.id



    db_notif = models.Notification(



        user_id=target_user_id,



        title=notif_in.title,



        message=notif_in.message,



        type=notif_in.type or "info",



        created_at=datetime.utcnow().isoformat()



    )



    db.add(db_notif)



    db.commit()



    db.refresh(db_notif)



    return db_notif







@app.delete("/notifications/{notification_id}")



def delete_notification(



    notification_id: int,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    notif = db.query(models.Notification).filter(



        models.Notification.id == notification_id,



        models.Notification.user_id == current_user.id



    ).first()



    if notif:



        db.delete(notif)



        db.commit()



    return {"success": True, "message": "Notification dismissed successfully"}







@app.delete("/notifications/clear-all")



def clear_all_notifications(



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    db.query(models.Notification).filter(models.Notification.user_id == current_user.id).delete()



    db.commit()



    return {"success": True, "message": "All notifications cleared"}







# ==============================================================================



# MODULE 10: COACH, PHYSIO, SCIENTIST & ADMIN DASHBOARD ENDPOINTS



# ==============================================================================







@app.get("/coach/team-monitoring")



def get_coach_team_monitoring(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    athletes = db.query(models.User).filter(models.User.role == "Athlete").all()



    roster = []



    total_risk = 0



    count_risk = 0



    high_count = 0



    mod_count = 0



    low_count = 0







    for a in athletes:



        prof = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == a.id).first()



        latest_analysis = db.query(models.VideoAnalysis).filter(



            models.VideoAnalysis.user_id == a.id



        ).order_by(models.VideoAnalysis.created_at.desc()).first()







        risk = round(latest_analysis.risk_score, 1) if latest_analysis else 24.0



        level = latest_analysis.risk_level if latest_analysis else "Low"



        activity = latest_analysis.activity if latest_analysis else "Sprinting"



        



        total_risk += risk



        count_risk += 1



        if risk > 35:



            high_count += 1



            status = "Restricted"



        elif risk > 20:



            mod_count += 1



            status = "Under Observation"



        else:



            low_count += 1



            status = "Cleared to Play"







        roster.append({



            "id": a.id,



            "name": a.email.split("@")[0].replace(".", " ").title(),



            "email": a.email,



            "sport": prof.sport_type if prof else "Track & Field",



            "position": prof.position if prof else "Sprinter",



            "latest_activity": activity,



            "risk_score": risk,



            "risk_level": level,



            "status": status,



            "avatar": a.profile_picture or "",



            "last_assessed": latest_analysis.created_at[:10] if latest_analysis and latest_analysis.created_at else "Recently"



        })







    avg_team_risk = round(total_risk / count_risk, 1) if count_risk > 0 else 28.0







    return {



        "team_overall_risk_score": avg_team_risk,



        "total_athletes": len(roster),



        "high_risk_count": high_count,



        "moderate_risk_count": mod_count,



        "low_risk_count": low_count,



        "athlete_roster": roster



    }







@app.get("/coach/workload-alerts")



def get_coach_workload_alerts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    return {



        "team_acwr_average": 1.28,



        "status": "Optimal (Safe Progression Range 0.8 - 1.3)",



        "alerts": [



            {



                "id": 1,



                "athlete_name": "Michael Smith",



                "severity": "Critical",



                "metric": "Acute:Chronic Workload Ratio",



                "value": "1.62 (Spike Detected)",



                "description": "Weekly training load jumped 38% above 4-week rolling baseline. High risk of hamstring or adductor strain.",



                "recommended_action": "Prescribe 48-hour deload and lower sprint volume by 30%."



            },



            {



                "id": 2,



                "athlete_name": "David Johnson",



                "severity": "Warning",



                "metric": "Frontal Plane Knee Sway",



                "value": "19.4° Valgus Peak",



                "description": "Fatigue-induced medial knee collapse emerging in late-practice jump trials.",



                "recommended_action": "Incorporate Banded Glute Bridges and Neuromuscular Jump Landing Drills."



            },



            {



                "id": 3,



                "athlete_name": "Sarah Connor",



                "severity": "Advisory",



                "metric": "Sleep Hygiene & Recovery Index",



                "value": "4.2 / 10 Sleep Score",



                "description": "Sub-optimal autonomic recovery. Elevated risk of cumulative micro-trauma.",



                "recommended_action": "Prioritize active recovery, contrast hydrotherapy, and sleep extension."



            }



        ]



    }







@app.get("/physio/recovery-status")



def get_physio_recovery_status(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    trends = [



        {"name": "Mon", "injuries": 1, "recoveries": 2},



        {"name": "Tue", "injuries": 0, "recoveries": 1},



        {"name": "Wed", "injuries": 2, "recoveries": 0},



        {"name": "Thu", "injuries": 1, "recoveries": 3},



        {"name": "Fri", "injuries": 0, "recoveries": 2},



        {"name": "Sat", "injuries": 3, "recoveries": 1},



        {"name": "Sun", "injuries": 0, "recoveries": 4}



    ]







    patients = [



        {



            "id": 1,



            "athlete_name": "David Johnson",



            "injury": "Grade 1 Hamstring Strain",



            "protocol": "Sprint & Hamstring Eccentric Resilience",



            "completion_percent": 82,



            "target_joint": "Hamstrings / Posterior Chain",



            "rom_degrees": "95° (Target 105°)",



            "clearance_phase": "Phase 3: High-Speed Deceleration",



            "status": "Progressing Well"



        },



        {



            "id": 2,



            "athlete_name": "Michael Smith",



            "injury": "Patellofemoral Pain / ACL Guarding",



            "protocol": "Knee Valgus Dynamic Correction",



            "completion_percent": 65,



            "target_joint": "Knee / Patellofemoral",



            "rom_degrees": "135° (Target 140°)",



            "clearance_phase": "Phase 2: Closed Kinetic Chain Loading",



            "status": "In Rehab"



        },



        {



            "id": 3,



            "athlete_name": "Marcus Aurelius",



            "injury": "Rotator Cuff Impingement",



            "protocol": "Scapular & Rotator Cuff Dynamic Stabilization",



            "completion_percent": 100,



            "target_joint": "Shoulder / Rotator Cuff",



            "rom_degrees": "178° (Target 180°)",



            "clearance_phase": "Return to Full Competition",



            "status": "Cleared to Play"



        }



    ]







    return {



        "active_injuries_count": 4,



        "rehab_plans_active": 12,



        "cleared_this_week": 3,



        "injury_recovery_trends": trends,



        "rehab_patients": patients



    }







@app.get("/scientist/biomechanical-insights")



def get_scientist_biomechanical_insights(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    analyses = db.query(models.VideoAnalysis).all()



    



    valgus_scores = []



    trunk_scores = []



    for a in analyses:



        if a.kinematics:



            try:



                k = json.loads(a.kinematics)



                if "valgus_l_max" in k and k["valgus_l_max"] is not None:



                    valgus_scores.append(float(k["valgus_l_max"]))



                if "trunk_lean_max" in k and k["trunk_lean_max"] is not None:



                    trunk_scores.append(float(k["trunk_lean_max"]))



            except:



                pass







    avg_valgus = round(sum(valgus_scores) / len(valgus_scores), 1) if valgus_scores else 14.8



    avg_trunk = round(sum(trunk_scores) / len(trunk_scores), 1) if trunk_scores else 18.2







    weighted_model = [



        {"factor": "Biomechanical Deviations", "weight": 35, "description": "Frontal/sagittal joint angle deviations & FPPA valgus"},



        {"factor": "Historical Injury Factors", "weight": 20, "description": "Prior ligament sprains, micro-fractures & chronic load history"},



        {"factor": "Movement Asymmetry", "weight": 20, "description": "Bilateral kinetic imbalance between left and right limbs"},



        {"factor": "Training Load Indicators", "weight": 15, "description": "Acute-to-chronic workload spikes (ACWR > 1.3)"},



        {"factor": "Fatigue Indicators", "weight": 10, "description": "Decreased jump velocity, posture sway & RPE exertion"}



    ]







    fatigue_data = [



        {"day": "Day 1", "load": 60, "fatigue": 40},



        {"day": "Day 2", "load": 80, "fatigue": 55},



        {"day": "Day 3", "load": 40, "fatigue": 30},



        {"day": "Day 4", "load": 95, "fatigue": 85},



        {"day": "Day 5", "load": 85, "fatigue": 75},



        {"day": "Day 6", "load": 50, "fatigue": 45},



        {"day": "Day 7", "load": 100, "fatigue": 90}



    ]







    return {



        "team_fatigue_index": "Normal Baseline (38 / 100)",



        "workload_spikes": 3,



        "mean_valgus": avg_valgus,



        "mean_trunk_sway": avg_trunk,



        "total_sessions_analyzed": len(analyses),



        "weighted_scoring_model": weighted_model,



        "fatigue_load_trends": fatigue_data



    }







@app.get("/admin/users")



def get_admin_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    users = db.query(models.User).order_by(models.User.id.asc()).all()



    result = []



    for u in users:



        prof = db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == u.id).first()



        analysis_count = db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == u.id).count()



        result.append({



            "id": u.id,



            "email": u.email,



            "role": u.role or "Athlete",



            "profile_picture": u.profile_picture or "",



            "sport": prof.sport_type if prof else "N/A",



            "position": prof.position if prof else "N/A",



            "analyses_count": analysis_count



        })



    return result







@app.patch("/admin/users/{user_id}/role")



def update_user_role(



    user_id: int,



    req: schemas.RoleUpdateRequest,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    target = db.query(models.User).filter(models.User.id == user_id).first()



    if not target:



        raise HTTPException(status_code=404, detail="User not found")



    valid_roles = ["Athlete", "Coach", "Physiotherapist", "Sports Scientist", "Administrator"]



    if req.role not in valid_roles:



        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")



    target.role = req.role



    db.commit()



    return {"success": True, "message": f"User {target.email} role updated to {req.role}", "role": req.role}







@app.delete("/admin/users/{user_id}")



def delete_admin_user(



    user_id: int,



    db: Session = Depends(get_db),



    current_user: models.User = Depends(get_current_user)



):



    if user_id == current_user.id:



        raise HTTPException(status_code=400, detail="Cannot delete your own active administrator account")



    target = db.query(models.User).filter(models.User.id == user_id).first()



    if not target:



        raise HTTPException(status_code=404, detail="User not found")



    



    db.query(models.AthleteProfile).filter(models.AthleteProfile.user_id == user_id).delete()



    db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == user_id).delete()



    db.query(models.DualVideoComparison).filter(models.DualVideoComparison.user_id == user_id).delete()



    db.query(models.TrainingPlan).filter(models.TrainingPlan.user_id == user_id).delete()



    db.query(models.Notification).filter(models.Notification.user_id == user_id).delete()



    db.query(models.PhysicalAssessment).filter(models.PhysicalAssessment.user_id == user_id).delete()



    db.query(models.PerformanceRecord).filter(models.PerformanceRecord.user_id == user_id).delete()



    db.delete(target)



    db.commit()



    return {"success": True, "message": f"User #{user_id} and associated records deleted successfully"}







@app.get("/admin/platform-stats")



def get_admin_platform_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    user_count = db.query(models.User).count()



    analysis_count = db.query(models.VideoAnalysis).count()



    comp_count = db.query(models.DualVideoComparison).count()



    plan_count = db.query(models.TrainingPlan).count()



    assessment_count = db.query(models.PhysicalAssessment).count()







    storage_bytes = 0



    for folder in ["processed", "uploads"]:



        if os.path.exists(folder):



            for f in os.listdir(folder):



                p = os.path.join(folder, f)



                if os.path.isfile(p):



                    storage_bytes += os.path.getsize(p)



    storage_mb = round(storage_bytes / (1024 * 1024), 2)







    return {



        "total_users": user_count,



        "total_video_analyses": analysis_count,



        "total_dual_comparisons": comp_count,



        "total_training_plans": plan_count,



        "total_physical_assessments": assessment_count,



        "storage_used_mb": storage_mb,



        "system_health": "99.98%",



        "uptime": "Continuous (Zero Downtime)",



        "server_status": "Healthy / Docker Containerized",



        "platform_usage_series": [



            {"name": "Week 1", "users": max(10, user_count - 15), "analyses": max(20, analysis_count - 30)},



            {"name": "Week 2", "users": max(15, user_count - 10), "analyses": max(35, analysis_count - 20)},



            {"name": "Week 3", "users": max(20, user_count - 5), "analyses": max(50, analysis_count - 10)},



            {"name": "Week 4", "users": user_count, "analyses": analysis_count}



        ]



    }







from fastapi.responses import StreamingResponse



import io



import csv



from reportlab.pdfgen import canvas







@app.get("/export/csv")



def export_csv(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    analyses = db.query(models.VideoAnalysis).all() if current_user.role == 'Administrator' else db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == current_user.id).all()



    



    output = io.StringIO()



    writer = csv.writer(output)



    writer.writerow(["Activity", "Risk Score", "Risk Level", "Recommendations", "Date"])



    



    for analysis in analyses:



        writer.writerow([analysis.activity, analysis.risk_score, analysis.risk_level, analysis.corrective_recommendation, analysis.created_at])



        



    output.seek(0)



    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=analyses.csv"})







@app.get("/export/pdf")



def export_pdf(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):



    analyses = db.query(models.VideoAnalysis).all() if current_user.role == 'Administrator' else db.query(models.VideoAnalysis).filter(models.VideoAnalysis.user_id == current_user.id).all()



    



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









@app.post("/user/upload-sound")
def upload_user_sound(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    valid_exts = [".mp3", ".wav", ".ogg", ".aac", ".m4a"]
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in valid_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format. Allowed: {', '.join(valid_exts)}")
    
    sound_dir = os.path.join("uploads", "sounds")
    os.makedirs(sound_dir, exist_ok=True)
    clean_name = f"user_{current_user.id}_{int(time.time())}{ext}"
    dest_path = os.path.join(sound_dir, clean_name)
    
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    sound_url = f"/uploads/sounds/{clean_name}"
    current_user.custom_sound_url = sound_url
    current_user.sound_cue = "custom"
    current_user.sound_effects = 1
    db.commit()
    db.refresh(current_user)
    
    return {
        "status": "success",
        "custom_sound_url": sound_url,
        "sound_cue": "custom",
        "sound_effects": True,
        "sound_volume": current_user.sound_volume or 80,
        "message": "Custom sound cue uploaded and activated successfully!"
    }
