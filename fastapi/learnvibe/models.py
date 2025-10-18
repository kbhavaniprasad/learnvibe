
#new one
from pydantic import BaseModel, EmailStr, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Any, Optional
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ])
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}

class AuthProvider(str, Enum):
    EMAIL = "email"

# ========================================
# USER AUTHENTICATION MODELS
# ========================================

class UserCreate(BaseModel):
    """Model for user signup request"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    auth_provider: AuthProvider = Field(default=AuthProvider.EMAIL)

class UserLogin(BaseModel):
    """Model for user login request"""
    email: EmailStr
    password: str = Field(..., min_length=6)

class ForgotPasswordRequest(BaseModel):
    """Model for forgot password request"""
    email: EmailStr

class VerifyResetCode(BaseModel):
    """Model for reset code verification"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class ResetPassword(BaseModel):
    """Model for password reset"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    """Model for user response (without sensitive data)"""
    id: str
    name: str
    email: str
    auth_provider: AuthProvider
    profile_picture: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserInDB(BaseModel):
    """Model for user stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    hashed_password: Optional[str] = None
    auth_provider: AuthProvider = Field(default=AuthProvider.EMAIL)
    profile_picture: Optional[str] = None
    reset_code: Optional[str] = None
    reset_code_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class Token(BaseModel):
    """Model for authentication token response"""
    access_token: str
    token_type: str
    user: UserResponse

# ========================================
# STUDENT PROFILE MODELS
# ========================================

class StudentProfileCreate(BaseModel):
    """Model for creating a student profile"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    dob: Optional[str] = None
    phone: Optional[str] = None
    studentId: str = Field(..., min_length=1)
    major: Optional[str] = None
    year: str = Field(default="Freshman (1st Year)")
    gpa: Optional[str] = None
    address: Optional[str] = None
    enrollmentDate: Optional[str] = None
    expectedGraduation: Optional[str] = None
    profilePic: Optional[str] = None

class StudentProfileUpdate(BaseModel):
    """Model for updating a student profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    dob: Optional[str] = None
    phone: Optional[str] = None
    studentId: Optional[str] = None
    major: Optional[str] = None
    year: Optional[str] = None
    gpa: Optional[str] = None
    address: Optional[str] = None
    enrollmentDate: Optional[str] = None
    expectedGraduation: Optional[str] = None
    profilePic: Optional[str] = None

class StudentProfileResponse(BaseModel):
    """Model for student profile response"""
    id: str
    name: str
    email: str
    dob: Optional[str] = None
    phone: Optional[str] = None
    studentId: str
    major: Optional[str] = None
    year: str
    gpa: Optional[str] = None
    address: Optional[str] = None
    enrollmentDate: Optional[str] = None
    expectedGraduation: Optional[str] = None
    profilePic: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StudentProfileInDB(BaseModel):
    """Model for student profile stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    dob: Optional[str] = None
    phone: Optional[str] = None
    studentId: str
    major: Optional[str] = None
    year: str = "Freshman (1st Year)"
    gpa: Optional[str] = None
    address: Optional[str] = None
    enrollmentDate: Optional[str] = None
    expectedGraduation: Optional[str] = None
    profilePic: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

# ========================================
# CONTACT MODELS
# ========================================

class ContactForm(BaseModel):
    """Model for contact form submission"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)
    phone: Optional[str] = None

class ContactResponse(BaseModel):
    """Model for contact form response"""
    id: str
    name: str
    email: str
    subject: str
    message: str
    phone: Optional[str] = None
    status: str = "pending"
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }