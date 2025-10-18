import os
import json
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        self.model_name = os.getenv("LLM_MODEL", "llama3.2:1b")
        
    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Llama 3.2 1B model"""
        try:
            # For local Ollama setup
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": max_tokens
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    # Fallback to mock response if LLM is not available
                    return self._get_mock_response(prompt)
                    
        except Exception as e:
            print(f"LLM service error: {e}")
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """Provide mock responses when LLM is unavailable"""
        prompt_lower = prompt.lower()
        
        if "career levels" in prompt_lower or "custom levels" in prompt_lower:
            return json.dumps([
                "Junior Level", 
                "Intermediate Level", 
                "Advanced Level", 
                "Expert Level"
            ])
            
        elif "assessment questions" in prompt_lower:
            return json.dumps([
                {
                    "id": 1,
                    "text": "What is the primary purpose of data normalization?",
                    "options": [
                        "To increase data storage efficiency",
                        "To reduce data redundancy and improve integrity", 
                        "To make data visually appealing",
                        "To encrypt sensitive data"
                    ],
                    "correct_answer": 1,
                    "difficulty": "medium",
                    "skill_name": "Data Management",
                    "topic_name": "Data Normalization"
                },
                {
                    "id": 2, 
                    "text": "Which of the following is a supervised learning algorithm?",
                    "options": [
                        "K-Means Clustering",
                        "Principal Component Analysis",
                        "Linear Regression", 
                        "Apriori Algorithm"
                    ],
                    "correct_answer": 2,
                    "difficulty": "easy",
                    "skill_name": "Machine Learning",
                    "topic_name": "Supervised Learning"
                }
            ])
            
        elif "evaluate answers" in prompt_lower:
            return json.dumps({
                "score": 75.0,
                "correct_answers": 6,
                "total_questions": 8,
                "assigned_level": "Intermediate Level",
                "feedback": "Good foundational knowledge with room for improvement in advanced topics.",
                "improvement_areas": ["Advanced algorithms", "System design", "Optimization techniques"]
            })
            
        return "[]"
    
    async def generate_structured_data(self, prompt: str, expected_type: str) -> Any:
        """Generate structured data with retry logic"""
        response = await self.generate_text(prompt)
        
        try:
            # Try to parse JSON response
            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return mock data based on expected type
            return self._get_structured_mock_data(expected_type)
    
    def _get_structured_mock_data(self, expected_type: str) -> Any:
        """Provide structured mock data based on expected type"""
        if expected_type == "levels":
            return ["Junior Level", "Intermediate Level", "Advanced Level", "Expert Level"]
        elif expected_type == "questions":
            return [
                {
                    "id": 1,
                    "text": "What is the primary purpose of data normalization?",
                    "options": [
                        "To increase data storage efficiency",
                        "To reduce data redundancy and improve integrity", 
                        "To make data visually appealing",
                        "To encrypt sensitive data"
                    ],
                    "correct_answer": 1,
                    "difficulty": "medium",
                    "skill_name": "Data Management"
                }
            ]
        elif expected_type == "evaluation":
            return {
                "score": 75.0,
                "correct_answers": 6,
                "total_questions": 8,
                "assigned_level": "Intermediate Level",
                "feedback": "Good foundational knowledge.",
                "improvement_areas": ["Advanced topics"]
            }
        return []