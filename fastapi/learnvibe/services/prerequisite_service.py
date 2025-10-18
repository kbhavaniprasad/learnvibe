from typing import List, Dict, Any
from models.schemas import Prerequisite

class PrerequisiteService:
    def __init__(self):
        self.prerequisite_mapping = self._load_prerequisite_mapping()
    
    def _load_prerequisite_mapping(self) -> Dict[str, List[Dict]]:
        """Load prerequisite mappings for different career goals"""
        return {
            "Data Scientist": [
                {
                    "name": "Mathematics Foundations",
                    "description": "Essential math concepts including algebra, calculus, probability, and linear algebra needed for data analysis and machine learning",
                    "importance": "high",
                    "estimated_time": "4-6 weeks",
                    "resources": [
                        "Khan Academy Mathematics", 
                        "3Blue1Brown YouTube channel",
                        "MIT OpenCourseWare Mathematics"
                    ]
                },
                {
                    "name": "Programming with Python", 
                    "description": "Python programming fundamentals and essential data science libraries (NumPy, Pandas, Matplotlib)",
                    "importance": "high",
                    "estimated_time": "6-8 weeks", 
                    "resources": [
                        "Python for Everybody",
                        "DataCamp Python courses",
                        "Real Python tutorials"
                    ]
                },
                {
                    "name": "Basic Statistics",
                    "description": "Statistical concepts, probability theory, and data analysis fundamentals",
                    "importance": "high",
                    "estimated_time": "4-5 weeks",
                    "resources": [
                        "Statistics Fundamentals on Coursera",
                        "Khan Academy Statistics", 
                        "Introduction to Statistical Learning"
                    ]
                }
            ],
            "Data Analyst": [
                {
                    "name": "Mathematics Foundations",
                    "description": "Basic math concepts including algebra and statistics for data analysis",
                    "importance": "medium",
                    "estimated_time": "3-4 weeks",
                    "resources": ["Khan Academy", "Basic Statistics courses"]
                },
                {
                    "name": "Programming Basics",
                    "description": "Fundamental programming concepts, preferably with Python or R",
                    "importance": "high", 
                    "estimated_time": "4-6 weeks",
                    "resources": ["Python basics courses", "R programming tutorials"]
                },
                {
                    "name": "Basic Statistics", 
                    "description": "Statistical concepts for data interpretation and analysis",
                    "importance": "high",
                    "estimated_time": "3-4 weeks",
                    "resources": ["Introductory statistics", "Data analysis fundamentals"]
                },
                {
                    "name": "SQL Fundamentals",
                    "description": "Database querying and data retrieval using SQL",
                    "importance": "high",
                    "estimated_time": "3-4 weeks", 
                    "resources": ["SQLZoo", "Mode Analytics SQL tutorial", "W3Schools SQL"]
                }
            ],
            "Machine Learning Engineer": [
                {
                    "name": "Advanced Mathematics",
                    "description": "Linear algebra, calculus, and probability theory for ML algorithms",
                    "importance": "high",
                    "estimated_time": "6-8 weeks",
                    "resources": ["Linear Algebra courses", "Calculus review", "Probability theory"]
                },
                {
                    "name": "Programming with Python",
                    "description": "Advanced Python programming with focus on ML libraries and algorithms",
                    "importance": "high", 
                    "estimated_time": "6-8 weeks",
                    "resources": ["Advanced Python", "ML with Python", "Algorithm implementation"]
                },
                {
                    "name": "Data Structures & Algorithms",
                    "description": "Computer science fundamentals and algorithm design",
                    "importance": "high",
                    "estimated_time": "5-7 weeks",
                    "resources": ["Algorithm courses", "Data structures practice", "Coding interviews"]
                }
            ],
            "Software Developer": [
                {
                    "name": "Programming Fundamentals",
                    "description": "Core programming concepts and logic building",
                    "importance": "high",
                    "estimated_time": "6-8 weeks", 
                    "resources": ["Programming basics", "Logic building exercises", "Intro to CS"]
                },
                {
                    "name": "Data Structures",
                    "description": "Essential data structures and their implementations",
                    "importance": "high",
                    "estimated_time": "5-6 weeks",
                    "resources": ["Data structures course", "Practice problems", "Algorithm visualization"]
                },
                {
                    "name": "Algorithms", 
                    "description": "Algorithm design and analysis techniques",
                    "importance": "high",
                    "estimated_time": "6-7 weeks",
                    "resources": ["Algorithm courses", "Problem solving", "Complexity analysis"]
                },
                {
                    "name": "System Design Basics",
                    "description": "Fundamental system architecture and design principles",
                    "importance": "medium",
                    "estimated_time": "3-4 weeks",
                    "resources": ["System design primer", "Architecture patterns", "Scalability basics"]
                }
            ]
        }
    
    def get_goal_prerequisites(self, career_goal: str) -> List[Prerequisite]:
        """Get filtered prerequisites for a specific career goal"""
        # Exact match
        if career_goal in self.prerequisite_mapping:
            return [Prerequisite(**p) for p in self.prerequisite_mapping[career_goal]]
        
        # Fuzzy matching based on keywords
        goal_lower = career_goal.lower()
        
        if any(word in goal_lower for word in ['data', 'analyst', 'scientist']):
            return [Prerequisite(**p) for p in self.prerequisite_mapping.get("Data Scientist", [])]
        elif any(word in goal_lower for word in ['machine learning', 'ml', 'ai']):
            return [Prerequisite(**p) for p in self.prerequisite_mapping.get("Machine Learning Engineer", [])]
        elif any(word in goal_lower for word in ['software', 'developer', 'engineer', 'programmer']):
            return [Prerequisite(**p) for p in self.prerequisite_mapping.get("Software Developer", [])]
        else:
            # Generic prerequisites for unknown careers
            return self._get_generic_prerequisites(career_goal)
    
    def _get_generic_prerequisites(self, career_goal: str) -> List[Prerequisite]:
        """Get generic prerequisites for unknown career goals"""
        return [
            Prerequisite(
                name="Industry Fundamentals",
                description=f"Basic concepts and principles of {career_goal} field",
                importance="high",
                estimated_time="4-6 weeks",
                resources=["Industry documentation", "Introductory courses", "Professional networks"]
            ),
            Prerequisite(
                name="Core Technical Skills",
                description="Essential technical abilities required for this role",
                importance="high", 
                estimated_time="6-10 weeks",
                resources=["Technical tutorials", "Hands-on projects", "Skill-specific courses"]
            ),
            Prerequisite(
                name="Tools & Technologies",
                description="Primary tools and technologies used in this field",
                importance="medium",
                estimated_time="3-5 weeks", 
                resources=["Tool documentation", "Practice environments", "Community forums"]
            )
        ]
    
    def get_prerequisite_details(self, prerequisite_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific prerequisite"""
        # Flatten all prerequisites to find the matching one
        all_prerequisites = []
        for career_prereqs in self.prerequisite_mapping.values():
            all_prerequisites.extend(career_prereqs)
        
        for prereq in all_prerequisites:
            if prereq["name"].lower() == prerequisite_name.lower():
                return prereq
        
        return {
            "name": prerequisite_name,
            "description": "General knowledge area",
            "importance": "medium",
            "estimated_time": "4-6 weeks",
            "resources": ["Online learning platforms", "Industry resources", "Practice materials"]
        }