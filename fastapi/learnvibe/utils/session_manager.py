import uuid
import time
from typing import Dict, Any, Optional

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour in seconds
    
    def create_session(self, initial_data: Dict[str, Any] = None) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "data": initial_data or {},
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        session = self.sessions.get(session_id)
        if session:
            # Check if session has expired
            if time.time() - session["last_accessed"] > self.session_timeout:
                self.delete_session(session_id)
                return None
            
            # Update last accessed time
            session["last_accessed"] = time.time()
            return session["data"]
        return None
    
    def set_session(self, session_id: str, data: Dict[str, Any]):
        """Set or update session data"""
        if session_id in self.sessions:
            self.sessions[session_id]["data"] = data
            self.sessions[session_id]["last_accessed"] = time.time()
        else:
            self.sessions[session_id] = {
                "data": data,
                "created_at": time.time(),
                "last_accessed": time.time()
            }
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update specific fields in session data"""
        session = self.sessions.get(session_id)
        if session:
            session["data"].update(updates)
            session["last_accessed"] = time.time()
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session["last_accessed"] > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        return len(expired_sessions)
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)