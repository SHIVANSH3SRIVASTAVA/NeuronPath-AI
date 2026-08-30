import json
import re
from .provider import LLMProvider

ROLE_PATTERNS = [
    # Programming Languages
    (r'\b(python|django|fastapi|flask)\b', 'Python Developer', 'Master Python & Backend Engineering', ['Python Basics']),
    (r'\b(java|spring|spring\s+boot)\b', 'Java Developer', 'Master Enterprise Java & Spring Boot', ['Java Fundamentals']),
    (r'\b(c\s+programming|c\s+language|learn\s+c)\b', 'C Developer', 'Master C & Systems Programming', ['C Programming Basics']),
    (r'\b(c\+\+|cpp|modern\s+c\+\+)\b', 'C++ Developer', 'Master C++ & Systems Software', ['C++ Fundamentals']),
    (r'\b(c#|csharp|\.net|dotnet|asp\.net)\b', 'C# & .NET Developer', 'Master C# & .NET Core Development', ['C# Basics & OOP']),
    (r'\b(typescript|ts)\b', 'TypeScript Developer', 'Master Modern TypeScript & Static Typing', ['JavaScript Essentials']),
    (r'\b(javascript|js|es6)\b', 'JavaScript Developer', 'Master Modern JavaScript Development', ['JavaScript Essentials']),
    (r'\b(golang|go\s+developer|go\s+language|learn\s+go)\b', 'Go Developer', 'Master Go & Concurrent Backend Services', ['Go Fundamentals']),
    (r'\b(rust|cargo|rustlang)\b', 'Rust Developer', 'Master Rust & Memory-Safe Systems', ['Rust Syntax & Ownership']),
    (r'\b(kotlin)\b', 'Kotlin Developer', 'Master Kotlin & Modern Android Development', ['Kotlin Basics']),
    (r'\b(swift|swiftui)\b', 'Swift Developer', 'Master Swift & iOS App Development', ['Swift Syntax & Basics']),
    (r'\b(r\s+programming|tidyverse|r\s+language)\b', 'R Data Analyst', 'Master R for Statistical Computing & Analytics', ['R for Statistical Computing']),
    (r'\b(php|laravel)\b', 'PHP & Laravel Developer', 'Master Modern PHP & Laravel Web Development', ['PHP Fundamentals']),

    # Data & AI
    (r'\b(data\s+analyst|data\s+analytics|bi\s+analyst)\b', 'Data Analyst', 'Become a Professional Data Analyst', ['SQL Fundamentals', 'Descriptive Statistics']),
    (r'\b(data\s+scientist|data\s+science)\b', 'Data Scientist', 'Become a Professional Data Scientist', ['Python Basics', 'Descriptive Statistics']),
    (r'\b(machine\s+learning|ml\s+engineer|mle)\b', 'Machine Learning Engineer', 'Become a Machine Learning Engineer', ['Python Basics', 'ML Fundamentals']),
    (r'\b(ai\s+engineer|llm|rag|prompt\s+engineering)\b', 'AI Engineer', 'Master AI Engineering & LLM Systems', ['Python Basics', 'Transformers & LLM Engineering']),
    (r'\b(deep\s+learning|neural\s+network)\b', 'Deep Learning Specialist', 'Master Deep Learning with PyTorch', ['Linear Algebra', 'Neural Networks Basics']),
    (r'\b(nlp|natural\s+language|transformers)\b', 'NLP Engineer', 'Master Natural Language Processing & Transformers', ['Python Basics', 'Natural Language Processing']),
    (r'\b(computer\s+vision|opencv|image\s+recognition)\b', 'Computer Vision Engineer', 'Master Computer Vision & CNN Architectures', ['Python Basics', 'Computer Vision & CNNs']),
    (r'\b(data\s+engineer|data\s+engineering|etl|spark)\b', 'Data Engineer', 'Master Big Data Engineering & ETL Pipelines', ['SQL Fundamentals', 'ETL Pipelines & Data Warehousing']),
    (r'\b(business\s+intelligence|power\s*bi|tableau)\b', 'Business Intelligence Developer', 'Master Business Intelligence & Data Dashboards', ['SQL Fundamentals', 'Power BI & Tableau Dashboarding']),

    # Software / Web / Mobile
    (r'\b(frontend|react|vue|angular)\b', 'Frontend Developer', 'Become a Modern Frontend Engineer', ['HTML & CSS Responsive Layouts', 'JavaScript Essentials']),
    (r'\b(backend|api\s+developer|microservices)\b', 'Backend Developer', 'Master Backend Engineering & REST APIs', ['RESTful API Design', 'SQL Fundamentals']),
    (r'\b(full\s*stack|fullstack)\b', 'Full Stack Developer', 'Become a Full Stack Software Developer', ['HTML & CSS Responsive Layouts', 'RESTful API Design']),
    (r'\b(web\s+developer|web\s+development)\b', 'Web Developer', 'Master Full-Stack Web Development', ['HTML & CSS Responsive Layouts', 'JavaScript Essentials']),
    (r'\b(mobile\s+app|flutter|dart)\b', 'Mobile App Developer', 'Master Cross-Platform Mobile App Development', ['Cross-Platform Flutter & Dart']),
    (r'\b(android)\b', 'Android Developer', 'Master Native Android App Development', ['Kotlin Basics']),
    (r'\b(ios)\b', 'iOS Developer', 'Master Native iOS Development with SwiftUI', ['Swift Syntax & Basics']),
    (r'\b(game\s+developer|unity|unreal)\b', 'Game Developer', 'Master Game Development & Interactive 3D', ['Unity & C# Game Scripting']),
    (r'\b(software\s+engineer|software\s+engineering)\b', 'Software Engineer', 'Master Software Engineering & System Architecture', ['Data Structures (Arrays, Lists, Trees)']),
    (r'\b(api\s+design|graphql|rest\s+api)\b', 'API Developer', 'Master Scalable API Design & GraphQL', ['RESTful API Design']),

    # Cloud & DevOps
    (r'\b(devops|ci/cd|continuous\s+integration)\b', 'DevOps Engineer', 'Master DevOps & Cloud Infrastructure', ['Linux Command Line', 'Docker Basics']),
    (r'\b(docker|container|containerization)\b', 'Docker & Container Specialist', 'Master Docker & Containerized Architectures', ['Docker Basics', 'Linux Command Line']),
    (r'\b(kubernetes|k8s)\b', 'Kubernetes Administrator', 'Master Kubernetes Orchestration & Cluster Management', ['Docker Basics', 'Kubernetes Orchestration']),
    (r'\b(cloud\s+engineer|cloud\s+architecture)\b', 'Cloud Engineer', 'Master Cloud Engineering & Cloud Architecture', ['AWS Cloud Foundations', 'Linux Command Line']),
    (r'\b(aws|amazon\s+web\s+services)\b', 'AWS Cloud Architect', 'Master AWS Cloud Solutions Architecture', ['AWS Cloud Foundations']),
    (r'\b(azure|microsoft\s+cloud)\b', 'Microsoft Azure Specialist', 'Master Microsoft Azure Cloud Solutions', ['Microsoft Azure Foundations']),
    (r'\b(gcp|google\s+cloud)\b', 'Google Cloud Engineer', 'Master Google Cloud Platform Infrastructure', ['Google Cloud Platform (GCP)']),
    (r'\b(sre|site\s+reliability)\b', 'Site Reliability Engineer (SRE)', 'Master Site Reliability Engineering & Observability', ['Linux Command Line', 'Site Reliability & Monitoring']),

    # Database / CS / Security
    (r'\b(sql|database\s+developer|postgres|mysql)\b', 'SQL Developer', 'Master SQL & Relational Database Engineering', ['SQL Fundamentals']),
    (r'\b(dba|database\s+admin|database\s+management)\b', 'Database Administrator (DBA)', 'Master Database Administration & Performance Tuning', ['SQL Fundamentals', 'SQL Advanced']),
    (r'\b(data\s+structures|algorithms|dsa|leetcode)\b', 'Data Structures & Algorithms Specialist', 'Master Data Structures & Algorithm Design', ['Data Structures (Arrays, Lists, Trees)']),
    (r'\b(system\s+design|distributed\s+systems)\b', 'System Design Architect', 'Master Large-Scale Distributed System Design', ['System Design Fundamentals']),
    (r'\b(computer\s+networks|networking|tcp/ip)\b', 'Computer Networks Engineer', 'Master Computer Networks & Network Protocols', ['Computer Networks & Protocols']),
    (r'\b(operating\s+systems|os|kernel)\b', 'Operating Systems Engineer', 'Master Operating Systems Architecture & Concurrency', ['Operating Systems & Concurrency']),
    (r'\b(cyber\s*security|security\s+analyst|infosec|ethical\s+hacking)\b', 'Cybersecurity Engineer', 'Become a Cybersecurity & Threat Defense Specialist', ['Linux Command Line', 'Network Security & Cryptography']),

    # Specializations
    (r'\b(blockchain|solidity|smart\s+contracts)\b', 'Blockchain Developer', 'Master Blockchain Engineering & Smart Contracts', ['Solidity & Smart Contracts']),
    (r'\b(web3|dapp|decentralized)\b', 'Web3 Developer', 'Master Web3 & Decentralized Applications', ['Web3 & Decentralized Apps']),
    (r'\b(embedded|microcontroller|arduino|stm32)\b', 'Embedded Systems Engineer', 'Master Embedded Systems & Microcontroller Firmware', ['C Programming Basics', 'Embedded Systems & Microcontrollers']),
    (r'\b(iot|internet\s+of\s+things)\b', 'IoT Solutions Engineer', 'Master IoT Architectures & Telemetry Edge Systems', ['IoT Protocols & Edge Computing']),
    (r'\b(robotics|ros)\b', 'Robotics Engineer', 'Master Autonomous Robotics & ROS Systems', ['Robotics & ROS']),
    (r'\b(qa|test\s+automation|selenium|playwright)\b', 'QA & Test Automation Engineer', 'Master Software QA & Test Automation Engineering', ['Test Automation & QA']),
    (r'\b(ui/ux|ui\s+design|ux\s+design|figma)\b', 'UI/UX Designer', 'Master UI/UX Design & Interactive Design Systems', ['UI/UX Design & Wireframing', 'Figma & Design Systems']),
    (r'\b(product\s+manager|product\s+management|scrum|agile)\b', 'Product Manager', 'Master Product Strategy, Agile & Product Delivery', ['Product Strategy & Management']),
]

def rule_based_goal_extraction(text: str) -> dict:
    """Extract realistic structured goal from text using pattern matching."""
    text_lower = text.lower().strip()
    
    matched_role = None
    matched_title = None
    matched_known = []
    
    for pattern, role, title, default_known in ROLE_PATTERNS:
        if re.search(pattern, text_lower):
            matched_role = role
            matched_title = title
            matched_known = default_known
            break
            
    if not matched_role:
        clean_text = re.sub(r'^(i\s+want\s+to\s+learn|i\s+want\s+to\s+become\s+a|i\s+want\s+to\s+become|learn|become\s+a|become)\s+', '', text_lower, flags=re.IGNORECASE).strip()
        if clean_text:
            clean_title = clean_text.title()
            matched_role = f"{clean_title} Specialist" if not any(w in clean_title.lower() for w in ['engineer', 'developer', 'analyst', 'specialist']) else clean_title
            matched_title = f"Master {clean_title}"
        else:
            matched_role = "Software & Data Professional"
            matched_title = "Personalized Learning Path"

    timeline_months = 6
    time_match = re.search(r'(\d+)\s*(month|months|mo)', text_lower)
    if time_match:
        timeline_months = max(1, min(24, int(time_match.group(1))))
    elif 'year' in text_lower or '12 months' in text_lower:
        timeline_months = 12
    elif '3 months' in text_lower:
        timeline_months = 3

    weekly_hours = 10.0
    hours_match = re.search(r'(\d+)\s*(hour|hours|hr|hrs|h)', text_lower)
    if hours_match:
        weekly_hours = max(2.0, min(60.0, float(hours_match.group(1))))

    experience_level = "beginner"
    if any(w in text_lower for w in ["advanced", "expert", "senior", "lead", "proficient"]):
        experience_level = "advanced"
    elif any(w in text_lower for w in ["intermediate", "some experience", "know basics", "working knowledge", "mid-level"]):
        experience_level = "intermediate"

    return {
        "title": matched_title,
        "target_role": matched_role,
        "timeline_months": timeline_months,
        "known_skills": list(set(matched_known)),
        "weekly_hours": weekly_hours,
        "experience_level": experience_level,
        "learning_style": "hands-on" if "hands-on" in text_lower or "project" in text_lower else "visual",
        "preferred_formats": ["course", "practice", "video"]
    }

async def extract_goal_from_text(text: str, llm: LLMProvider) -> dict:
    """Extract structured goal information and learner profile from user's free-text input."""
    if not llm.is_available():
        return rule_based_goal_extraction(text)
        
    system_prompt = """
    You are an expert career counselor and learning advisor across all modern tech fields.
    Extract the learning goal and profile from the user's text.
    Return ONLY a JSON object with these keys:
    - title (string): A short, inspiring title matching the user's actual goal (e.g. "Master Go & Concurrency", "Become a Kubernetes Administrator", "Master UI/UX Design")
    - target_role (string): The professional role they want to achieve (e.g. "Go Developer", "Kubernetes Administrator", "UI/UX Designer", "Cybersecurity Engineer")
    - timeline_months (integer): A realistic number of months (default 6)
    - known_skills (list of strings): Skills they already know from the text
    - weekly_hours (integer): Hours they can study per week (default 10)
    - experience_level (string): "beginner", "intermediate", or "advanced"
    - learning_style (string): "visual", "hands-on", or "theoretical"
    - preferred_formats (list of strings): e.g. ["course", "video", "practice"]
    """
    
    prompt = f"User's goal description: {text}"
    
    try:
        response_text = await llm.generate(prompt, system_prompt, json_mode=True)
        cleaned_json = re.sub(r'^```json\s*|\s*```$', '', response_text.strip(), flags=re.MULTILINE)
        data = json.loads(cleaned_json)
        
        if not data.get("target_role") or not data.get("title"):
            return rule_based_goal_extraction(text)
            
        return {
            "title": data.get("title", "Personal Learning Goal"),
            "target_role": data.get("target_role", "Software Professional"),
            "timeline_months": int(data.get("timeline_months", 6)),
            "known_skills": data.get("known_skills", []),
            "weekly_hours": float(data.get("weekly_hours", 10)),
            "experience_level": data.get("experience_level", "beginner"),
            "learning_style": data.get("learning_style", "visual"),
            "preferred_formats": data.get("preferred_formats", ["course", "practice"])
        }
    except Exception:
        return rule_based_goal_extraction(text)
