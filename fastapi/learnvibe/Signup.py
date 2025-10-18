
#new code 
from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.errors import DuplicateKeyError
from typing import List, Optional
from fastapi.responses import JSONResponse
import database
import auth
from models import (
    UserCreate, UserLogin, UserResponse, UserInDB, Token,
    StudentProfileCreate, StudentProfileUpdate, StudentProfileResponse, StudentProfileInDB,
    ForgotPasswordRequest, VerifyResetCode, ResetPassword,
    AuthProvider, ContactForm, ContactResponse
)
from datetime import timedelta, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import asyncio
import logging
from jose import JWTError, jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LearnVibe API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kolaprasad2507@gmail.com"
SMTP_PASSWORD = "yetf anfm wree eabf"

# For development - if email fails, log to console
DEVELOPMENT_MODE = True

# ========================================
# DEPENDENCIES & MIDDLEWARE
# ========================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ========================================
# EMAIL SERVICE
# ========================================

async def send_reset_code_email(email: str, code: str):
    """Send password reset code via email"""
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = SMTP_USERNAME
        message["To"] = email
        message["Subject"] = "LearnVibe - Password Reset Code"
        
        # Email body
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #2563eb; text-align: center;">Password Reset Request</h2>
                    <p>You requested a password reset for your LearnVibe account.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="font-size: 32px; font-weight: bold; color: #2563eb; letter-spacing: 5px; padding: 20px; background: #f3f4f6; border-radius: 8px; display: inline-block;">
                            {code}
                        </div>
                    </div>
                    <p><strong>This code will expire in 1 hour.</strong></p>
                    <p>If you didn't request this reset, please ignore this email.</p>
                    <br>
                    <p>Best regards,<br><strong>LearnVibe Team</strong></p>
                </div>
            </body>
        </html>
        """
        
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
            
        logger.info(f"Reset code sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        
        # In development mode, log the code to console but don't show in response
        if DEVELOPMENT_MODE:
            logger.info(f"DEVELOPMENT MODE - Reset code for {email}: {code}")
            # Don't return True here - let the user know email failed
            return False
        
        return False

# ========================================
# USER AUTHENTICATION HELPERS
# ========================================

def get_user_by_email(email: str):
    """Get user by email from database"""
    try:
        user_data = database.user_registration_collection.find_one({"email": email})
        if user_data:
            return UserInDB(**user_data)
        return None
    except Exception as e:
        logger.error(f"Error fetching user by email {email}: {str(e)}")
        return None

def create_user(user: UserCreate):
    """Create a new user in the database"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password for email/password users
        hashed_password = None
        if user.auth_provider == AuthProvider.EMAIL:
            hashed_password = auth.get_password_hash(user.password)
        
        # Create user document
        user_dict = {
            "name": user.name,
            "email": user.email,
            "hashed_password": hashed_password,
            "auth_provider": user.auth_provider,
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = database.user_registration_collection.insert_one(user_dict)
        
        # Get the created user
        created_user = database.user_registration_collection.find_one({"_id": result.inserted_id})
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created user"
            )
        
        return UserInDB(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )

def create_token_response(user: UserInDB):
    """Create token response for successful authentication"""
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        auth_provider=user.auth_provider,
        profile_picture=user.profile_picture,
        created_at=user.created_at
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

@app.post("/api/auth/signup", response_model=Token)
async def signup(user_data: UserCreate):
    """Handle user signup"""
    try:
        # Validate input
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Create user
        user = create_user(user_data)
        return create_token_response(user)
        
    except HTTPException:
        raise
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        logger.error(f"Signup error for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signup"
        )

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Handle user login"""
    try:
        # Validate input
        if not user_credentials.email or not user_credentials.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Check if user exists
        user = get_user_by_email(user_credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check authentication method
        if user.auth_provider != AuthProvider.EMAIL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses different authentication method."
            )
        
        # Verify password
        if not user.hashed_password or not auth.verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create token response
        return create_token_response(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {user_credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@app.post("/api/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Send password reset code to email"""
    try:
        # Validate input
        if not request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Check if user exists (but don't reveal information)
        user = get_user_by_email(request.email)
        if not user:
            # Return success even if user doesn't exist for security
            return {
                "message": "If the email exists in our system, a reset code has been sent"
            }
        
        # Generate reset code
        reset_code = auth.generate_reset_code()
        
        # Store reset code in database with expiry
        reset_data = {
            "email": request.email,
            "code": reset_code,
            "created_at": datetime.utcnow()
        }
        
        # Delete any existing reset codes for this email
        database.password_reset_collection.delete_many({"email": request.email})
        
        # Insert new reset code
        database.password_reset_collection.insert_one(reset_data)
        
        # Send email in background
        email_sent = await send_reset_code_email(request.email, reset_code)
        
        if not email_sent:
            # Delete the reset code if email failed
            database.password_reset_collection.delete_many({"email": request.email})
            if DEVELOPMENT_MODE:
                # In development mode, we'll let it succeed but log the code
                logger.info(f"DEVELOPMENT: Email failed but code is: {reset_code}")
                return {
                    "message": "If the email exists in our system, a reset code has been sent"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send reset email. Please try again later."
                )
        
        # Always return the same message for security
        return {
            "message": "If the email exists in our system, a reset code has been sent"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing forgot password request"
        )

@app.post("/api/auth/verify-reset-code")
async def verify_reset_code(verification: VerifyResetCode):
    """Verify reset code"""
    try:
        # Validate input
        if not verification.email or not verification.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and code are required"
            )
        
        # Find valid reset code
        reset_data = database.password_reset_collection.find_one({
            "email": verification.email,
            "code": verification.code
        })
        
        if not reset_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset code"
            )
        
        # Check if code is expired (additional safety)
        code_created = reset_data["created_at"]
        if datetime.utcnow() - code_created > timedelta(hours=1):
            database.password_reset_collection.delete_one({"_id": reset_data["_id"]})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset code has expired"
            )
        
        return {"message": "Reset code verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify reset code error for {verification.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error verifying reset code"
        )

@app.post("/api/auth/reset-password")
async def reset_password(reset_data: ResetPassword):
    """Reset password with verified code"""
    try:
        # Validate input
        if not reset_data.email or not reset_data.code or not reset_data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email, code, and new password are required"
            )
        
        if len(reset_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Verify reset code first
        reset_record = database.password_reset_collection.find_one({
            "email": reset_data.email,
            "code": reset_data.code
        })
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset code"
            )
        
        # Get user
        user = get_user_by_email(reset_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        hashed_password = auth.get_password_hash(reset_data.new_password)
        database.user_registration_collection.update_one(
            {"email": reset_data.email},
            {"$set": {"hashed_password": hashed_password}}
        )
        
        # Delete used reset code
        database.password_reset_collection.delete_one({
            "email": reset_data.email,
            "code": reset_data.code
        })
        
        # Delete all other reset codes for this email
        database.password_reset_collection.delete_many({"email": reset_data.email})
        
        logger.info(f"Password reset successfully for {reset_data.email}")
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error for {reset_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error resetting password"
        )
    


# Add this to your existing signup.py file, in the AUTHENTICATION ENDPOINTS section

@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user by blacklisting the token
    """
    try:
        token = credentials.credentials
        
        # Verify the token is valid before blacklisting
        try:
            payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
            
            # Add token to blacklist
            auth.token_blacklist.add(token)
            
            logger.info(f"User {payload.get('sub')} logged out successfully")
            
            return {"message": "Logged out successfully"}
            
        except JWTError as e:
            # Even if token is invalid, we should still process logout
            # but don't add invalid tokens to blacklist
            logger.warning(f"Logout with invalid token: {str(e)}")
            return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# Update the get_current_user dependency to check blacklisted tokens
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token with blacklist check"""
    try:
        token = credentials.credentials
        
        # Check if token is blacklisted
        if token in auth.token_blacklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated"
            )
        
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ========================================
# PROTECTED ROUTES
# ========================================

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        auth_provider=current_user.auth_provider,
        profile_picture=current_user.profile_picture,
        created_at=current_user.created_at
    )

# ========================================
# STUDENT PROFILE ENDPOINTS
# ========================================

@app.post("/api/students", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_student_profile(profile: StudentProfileCreate):
    """Create a new student profile"""
    try:
        # Check if student ID already exists
        existing_profile = database.users_profile_collection.find_one({"studentId": profile.studentId})
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student ID '{profile.studentId}' already exists"
            )
        
        # Create profile document
        profile_dict = profile.dict()
        profile_dict["created_at"] = datetime.utcnow()
        profile_dict["updated_at"] = datetime.utcnow()
        
        # Insert into database
        result = database.users_profile_collection.insert_one(profile_dict)
        
        # Get the created profile
        created_profile = database.users_profile_collection.find_one({"_id": result.inserted_id})
        
        if not created_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created profile"
            )
        
        # Convert to response model
        return StudentProfileResponse(
            id=str(created_profile["_id"]),
            name=created_profile["name"],
            email=created_profile["email"],
            dob=created_profile.get("dob"),
            phone=created_profile.get("phone"),
            studentId=created_profile["studentId"],
            major=created_profile.get("major"),
            year=created_profile["year"],
            gpa=created_profile.get("gpa"),
            address=created_profile.get("address"),
            enrollmentDate=created_profile.get("enrollmentDate"),
            expectedGraduation=created_profile.get("expectedGraduation"),
            profilePic=created_profile.get("profilePic"),
            created_at=created_profile["created_at"],
            updated_at=created_profile["updated_at"]
        )
        
    except HTTPException:
        raise
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student ID '{profile.studentId}' already exists"
        )
    except Exception as e:
        logger.error(f"Error creating student profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating student profile"
        )

# ========================================
# CONTACT ENDPOINTS - UPDATED
# ========================================

async def send_contact_notification_email(contact_data: ContactForm):
    """Send notification email for contact form submission to domain email"""
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = SMTP_USERNAME
        message["To"] = SMTP_USERNAME  # Send to your domain email
        message["Reply-To"] = contact_data.email  # Allow replying directly to the user
        message["Subject"] = f"LearnVibe Contact: {contact_data.subject}"
        
        # Email body with better formatting
        body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px 8px 0 0; color: white; text-align: center; }}
                    .content {{ padding: 20px; background: #f8fafc; }}
                    .detail-section {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #667eea; }}
                    .message-section {{ background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #bae6fd; }}
                    .footer {{ margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin: 0; color: white;">📧 New Contact Form Submission</h2>
                        <p style="margin: 5px 0 0 0; opacity: 0.9;">LearnVibe Platform</p>
                    </div>
                    
                    <div class="content">
                        <div class="detail-section">
                            <h3 style="margin-top: 0; color: #374151; border-bottom: 2px solid #f3f4f6; padding-bottom: 10px;">Contact Details</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; width: 100px; font-weight: bold; color: #4b5563;">Name:</td>
                                    <td style="padding: 8px 0;">{contact_data.name}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #4b5563;">Email:</td>
                                    <td style="padding: 8px 0;">
                                        <a href="mailto:{contact_data.email}" style="color: #2563eb; text-decoration: none;">
                                            {contact_data.email}
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #4b5563;">Phone:</td>
                                    <td style="padding: 8px 0;">{contact_data.phone or 'Not provided'}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #4b5563;">Subject:</td>
                                    <td style="padding: 8px 0; color: #059669; font-weight: 500;">{contact_data.subject}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div class="message-section">
                            <h3 style="margin-top: 0; color: #374151; border-bottom: 2px solid #dbeafe; padding-bottom: 10px;">Message Content</h3>
                            <div style="white-space: pre-line; line-height: 1.8; color: #1e40af;">
                                {contact_data.message}
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>
                            This message was sent from the LearnVibe contact form<br>
                            <strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d at %H:%M:%S UTC')}
                        </p>
                        <p style="margin-top: 10px;">
                            💡 <em>You can reply directly to this email to respond to {contact_data.name}</em>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
            
        logger.info(f"Contact notification sent successfully to {SMTP_USERNAME} from {contact_data.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending contact notification: {str(e)}")
        
        # In development mode, log the contact details
        if DEVELOPMENT_MODE:
            logger.info(f"DEVELOPMENT MODE - Contact form submission:")
            logger.info(f"Name: {contact_data.name}")
            logger.info(f"Email: {contact_data.email}")
            logger.info(f"Phone: {contact_data.phone}")
            logger.info(f"Subject: {contact_data.subject}")
            logger.info(f"Message: {contact_data.message}")
            # In development, we'll consider it successful for testing
            return True
        
        return False

@app.post("/api/contact")
async def submit_contact_form(contact_data: ContactForm, background_tasks: BackgroundTasks):
    """Handle contact form submission with enhanced response"""
    try:
        # Validate input
        if not contact_data.name or not contact_data.email or not contact_data.subject or not contact_data.message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )
        
        # Validate email format
        if "@" not in contact_data.email or "." not in contact_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please enter a valid email address"
            )
        
        # Validate message length
        if len(contact_data.message) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message should be at least 10 characters long"
            )
        
        # Create contact document
        contact_dict = contact_data.dict()
        contact_dict["status"] = "pending"
        contact_dict["created_at"] = datetime.utcnow()
        
        # Insert into database
        result = database.contact_collection.insert_one(contact_dict)
        
        # Get the created contact
        created_contact = database.contact_collection.find_one({"_id": result.inserted_id})
        
        if not created_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit contact form"
            )
        
        # Send notification email in background
        email_sent = await send_contact_notification_email(contact_data)
        
        if not email_sent:
            # Update status to failed
            database.contact_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"status": "email_failed"}}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email notification. Please try again later."
            )
        
        # Update status to sent
        database.contact_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"status": "sent"}}
        )
        
        logger.info(f"Contact form submitted successfully by {contact_data.email}")
        
        # Return success response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Message sent successfully!",
                "data": {
                    "id": str(created_contact["_id"]),
                    "name": created_contact["name"],
                    "email": created_contact["email"],
                    "subject": created_contact["subject"],
                    "status": "sent"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contact form submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error submitting contact form"
        )

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        database.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")