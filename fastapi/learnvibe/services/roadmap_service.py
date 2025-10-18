from typing import Dict, List, Any, Optional
from models.schemas import SkillNode, Prerequisite, Roadmap, CareerLevel

class RoadmapService:
    def __init__(self):
        self.roadmap_data = self._load_roadmap_data()
    
    def _load_roadmap_data(self) -> Dict[str, Any]:
        """Load comprehensive roadmap data"""
        return {
            "Data Scientist": {
                "prerequisites": [
                    {
                        "name": "Mathematics Foundations",
                        "description": "Essential math concepts including algebra, calculus, and linear algebra",
                        "importance": "high",
                        "estimated_time": "4-6 weeks",
                        "resources": ["Khan Academy Mathematics", "3Blue1Brown YouTube channel"]
                    },
                    {
                        "name": "Programming with Python",
                        "description": "Python programming fundamentals and data science libraries",
                        "importance": "high", 
                        "estimated_time": "6-8 weeks",
                        "resources": ["Python for Everybody", "DataCamp Python courses"]
                    },
                    {
                        "name": "Basic Statistics",
                        "description": "Statistical concepts and probability theory",
                        "importance": "high",
                        "estimated_time": "4-5 weeks", 
                        "resources": ["Statistics Fundamentals on Coursera", "Khan Academy Statistics"]
                    }
                ],
                "skill_tree": {
                    "name": "Data Science",
                    "description": "Complete data science skill development path",
                    "level": "beginner",
                    "prerequisites": ["Mathematics Foundations", "Programming with Python", "Basic Statistics"],
                    "children": [
                        {
                            "name": "Data Analysis & Visualization",
                            "description": "Data manipulation, exploration and visualization techniques",
                            "level": "beginner",
                            "children": [
                                {
                                    "name": "Pandas & NumPy",
                                    "description": "Data manipulation with Python libraries",
                                    "level": "beginner",
                                    "resources": ["Pandas documentation", "NumPy user guide"],
                                    "estimated_duration": "3-4 weeks"
                                },
                                {
                                    "name": "Data Visualization",
                                    "description": "Creating insightful visualizations with Matplotlib and Seaborn",
                                    "level": "beginner", 
                                    "resources": ["Matplotlib tutorials", "Seaborn gallery"],
                                    "estimated_duration": "2-3 weeks"
                                }
                            ]
                        },
                        {
                            "name": "Machine Learning",
                            "description": "Machine learning algorithms and model development",
                            "level": "intermediate", 
                            "children": [
                                {
                                    "name": "Supervised Learning",
                                    "description": "Regression and classification algorithms",
                                    "level": "intermediate",
                                    "resources": ["Scikit-learn documentation", "Machine Learning by Andrew Ng"],
                                    "estimated_duration": "6-8 weeks"
                                },
                                {
                                    "name": "Unsupervised Learning",
                                    "description": "Clustering and dimensionality reduction",
                                    "level": "intermediate",
                                    "resources": ["Pattern Recognition and Machine Learning"],
                                    "estimated_duration": "4-5 weeks"
                                }
                            ]
                        },
                        {
                            "name": "Advanced Topics",
                            "description": "Specialized data science areas",
                            "level": "advanced",
                            "children": [
                                {
                                    "name": "Deep Learning",
                                    "description": "Neural networks and deep learning frameworks",
                                    "level": "advanced",
                                    "resources": ["Deep Learning Specialization", "PyTorch tutorials"],
                                    "estimated_duration": "8-10 weeks"
                                },
                                {
                                    "name": "Big Data Technologies",
                                    "description": "Distributed computing and big data tools",
                                    "level": "advanced",
                                    "resources": ["Spark documentation", "Hadoop ecosystem"],
                                    "estimated_duration": "6-8 weeks"
                                }
                            ]
                        }
                    ]
                },
                "levels": [
                    {"name": "Junior Data Scientist", "description": "Entry-level data science role", "min_score": 0, "max_score": 60},
                    {"name": "Data Scientist", "description": "Mid-level data professional", "min_score": 60, "max_score": 75},
                    {"name": "Senior Data Scientist", "description": "Advanced data science practitioner", "min_score": 75, "max_score": 90},
                    {"name": "Lead Data Scientist", "description": "Leadership and strategic role", "min_score": 90, "max_score": 100}
                ]
            }
        }
    
    def get_roadmap(self, career_goal: str, current_level: Optional[str] = None) -> Dict[str, Any]:
        """Get complete roadmap for a career goal"""
        goal_data = self.roadmap_data.get(career_goal)
        
        if not goal_data:
            # Generate generic roadmap for unknown careers
            return self._generate_generic_roadmap(career_goal)
        
        # Convert to proper schema objects
        prerequisites = [Prerequisite(**p) for p in goal_data["prerequisites"]]
        levels = [CareerLevel(**l) for l in goal_data["levels"]]
        skill_tree = self._build_skill_tree(goal_data["skill_tree"])
        
        return Roadmap(
            career_goal=career_goal,
            levels=levels,
            skill_tree=skill_tree,
            prerequisites=prerequisites,
            timeline_estimate="12-18 months"
        ).dict()
    
    def _build_skill_tree(self, tree_data: Dict) -> SkillNode:
        """Recursively build skill tree from data"""
        children = []
        for child_data in tree_data.get("children", []):
            children.append(self._build_skill_tree(child_data))
        
        return SkillNode(
            name=tree_data["name"],
            description=tree_data["description"],
            level=tree_data["level"],
            prerequisites=tree_data.get("prerequisites", []),
            children=children,
            resources=tree_data.get("resources", []),
            estimated_duration=tree_data.get("estimated_duration", "")
        )
    
    def _generate_generic_roadmap(self, career_goal: str) -> Dict[str, Any]:
        """Generate a generic roadmap for unknown careers"""
        return {
            "career_goal": career_goal,
            "levels": [
                {"name": f"Junior {career_goal}", "description": "Entry-level position", "min_score": 0, "max_score": 60},
                {"name": career_goal, "description": "Mid-level professional", "min_score": 60, "max_score": 75},
                {"name": f"Senior {career_goal}", "description": "Advanced practitioner", "min_score": 75, "max_score": 90},
                {"name": f"Lead {career_goal}", "description": "Leadership role", "min_score": 90, "max_score": 100}
            ],
            "prerequisites": [
                {
                    "name": "Foundational Knowledge",
                    "description": "Basic concepts and principles of the field",
                    "importance": "high",
                    "estimated_time": "4-6 weeks",
                    "resources": ["Industry blogs", "Introductory courses", "Professional networks"]
                },
                {
                    "name": "Technical Skills", 
                    "description": "Core technical abilities required for the role",
                    "importance": "high",
                    "estimated_time": "8-12 weeks",
                    "resources": ["Online tutorials", "Practice projects", "Technical documentation"]
                }
            ],
            "skill_tree": {
                "name": career_goal,
                "description": f"Skill development path for {career_goal}",
                "level": "beginner",
                "children": [
                    {
                        "name": "Fundamentals",
                        "description": "Core concepts and basic skills",
                        "level": "beginner",
                        "estimated_duration": "3-4 months"
                    },
                    {
                        "name": "Intermediate Skills", 
                        "description": "Advanced techniques and specialized knowledge",
                        "level": "intermediate",
                        "estimated_duration": "4-6 months"
                    },
                    {
                        "name": "Advanced Expertise",
                        "description": "Master-level skills and leadership capabilities", 
                        "level": "advanced",
                        "estimated_duration": "6-8 months"
                    }
                ]
            },
            "timeline_estimate": "12-18 months"
        }