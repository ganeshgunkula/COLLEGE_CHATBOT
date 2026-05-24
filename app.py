import os
from flask import Flask, render_template, request, jsonify, session
from chatterbot import ChatBot
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to pick best available text model dynamically
def get_best_text_model():
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods and "flash" in m.name and "image" not in m.name:
                print(f"✅ Selected model: {m.name}")
                return m.name
    except Exception as e:
        print("⚠️ Could not auto-select model:", e)
    return "gemini-2.5-flash"

# Create Gemini model
MODEL_NAME = get_best_text_model()
model = genai.GenerativeModel(MODEL_NAME)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-please-change")

# Load trained ChatterBot model
chatbot = ChatBot('CollegeBot', database_uri='sqlite:///database/college_chatbot.db')

# Comprehensive College Knowledge Base - Updated from Official Website
COLLEGE_KNOWLEDGE_BASE = {
    # About College
    "about": "Sphoorthy Engineering College, established in 2004, is an AICTE-approved autonomous institution affiliated with JNTU Hyderabad. Located on a 25-acre green campus with excellent infrastructure, it provides quality engineering and management education with 92% placement rate and NAAC A Grade accreditation.",
    "established": "Sphoorthy Engineering College was established in 2004.",
    "location": "Sphoorthy Engineering College is located at Nadargul Village, Saroornagar Mandal, Hyderabad, Telangana - 501510, India.",
    "address": "Nadargul Village, Saroornagar Mandal, Hyderabad, Telangana - 501510, India",
    "website": "https://www.sphoorthyengg.ac.in/",
    "contact": "Phone: +91 9392 11 9392 | +91 99 666 31091 | Email: admissions@sphoorthyengg.ac.in",
    "accreditation": "AICTE-approved, NAAC A Grade accredited, Autonomous Institution, JNTU Hyderabad Affiliated, Established in 2004.",
    "campus": "25-acre green campus with state-of-the-art facilities, sustainable environment, and modern infrastructure.",
    
    # Principal & Leadership
    "principal": "Dr. M.V.S. Ram Prasad is the Director of Sphoorthy Engineering College.",
    "director": "Dr. M.V.S. Ram Prasad is the Director of the institution.",
    "chairman": "S. Chalama Reddy is the Chairman (Master's in Mathematics and Education, 25+ years in education, President of Thoma Educational Society).",
    "secretary": "S. Jagan Mohan Reddy is the Secretary and Correspondent. Awarded 'Visionary Leader in Engineering Education' by Times of India and 'Best Pioneer in Engineering Education' at ET Educational Leadership Summit.",
    "ceo": "Mr. S. Holydhar Reddy is the Chief Executive Officer (CEO).",
    "leadership": "Institution headed by Chairman S. Chalama Reddy, Secretary S. Jagan Mohan Reddy, CEO Mr. S. Holydhar Reddy, and Director Dr. M.V.S. Ram Prasad.",
    "thoma educational society": "Founded by Sri S. Chalama Reddy to foster excellence in education and establish engineering colleges.",
    
    # Departments & HODs
    "departments": "7 departments: CSE, AIML, Data Science, Cyber Security, Freshman Engineering, ECE, and Civil Engineering.",
    "cse hod": "Prof. Dr. Kiran B. M. (M.Tech, PhD) - Head of Computer Science Engineering. Contact: hodcse@sphoorthyengg.ac.in | 7416081491",
    "aiml hod": "Dr. KVSN RAMARAO - Head of Artificial Intelligence & Machine Learning. Contact: ramarao.kvsn@sphoorthyengg.ac.in | 9603899920",
    "data science hod": "Dr. Allam Balaram (M.Tech, PhD) - Head of Data Science (CSE-DS). Contact: hodds@sphoorthyengg.ac.in | 7093908833",
    "cybersecurity hod": "Mr. P. Sandhya Rani (M.Tech PhD) - Head of Cyber Security (CSE-CS). Contact: hodcs@sphoorthyengg.ac.in | 7013999909",
    "freshman hod": "Dr. P. Gayathri Pavani (M.Sc, PhD) - Head of Freshman Engineering. Contact: hodhns@sphoorthyengg.ac.in | 9392118525",
    
    # Programs & Courses
    "b.tech": "4-year B.Tech programs available in: CSE, AIML, Data Science, Cyber Security, Civil Engineering, and ECE.",
    "m.tech": "2-year M.Tech programs including Computer Science Engineering and AIML specialization.",
    "mba": "2-year MBA program with specializations.",
    "programs": "B.Tech (4 years, 6+ specializations), M.Tech (2 years), MBA (2 years).",
    "courses offered": "CSE, CSE-AIML (Artificial Intelligence & Machine Learning), CSE-Data Science, CSE-Cyber Security, Civil Engineering, ECE (Electronics & Communication Engineering).",
    
    # Placements & Statistics
    "placement": "Active placement cell with 24+ recruiting companies visiting campus. 92% placement rate with excellent salary packages.",
    "placement 2022-2023": "600+ offers received (still counting) - Best placement year.",
    "placement 2021-2022": "754 students placed successfully.",
    "placement 2020-2021": "235 placements.",
    "placement 2019-2020": "480 placements.",
    "placement rate": "92% of students placed successfully across all batches.",
    "average salary": "The average salary offered to graduates varies by department and specialization.",
    "highest package": "Highest packages offered based on specialization and excellent performance.",
    "companies": "24+ recruiters: Accenture, Infosys, TCS, Wipro, Tech Mahindra, HCL, Capgemini, IBM, Deloitte, Cadila Global, Hexaware, EPAM, Five 9s Solutions, Cogent, Corizo, and many more.",
    "recruiters": "Major recruiters: Accenture, Infosys, TCS, Wipro, Tech Mahindra, HCL, Capgemini, IBM, Deloitte, Cadila Global, Hexaware, EPAM.",
    
    # Infrastructure & Facilities
    "infrastructure": "25-acre campus with modern facilities including labs, library, computer centers, hostels, gym, sports complex, and green initiatives.",
    "hostel": "Separate boys and girls hostels with furnished rooms, nutritious multi-cuisine food, Wi-Fi, gymnasium, yoga studio, 24/7 security, and ragging-free environment.",
    "girls hostel": "Exclusive girls hostel with safe environment, resident warden, nutritious meals, gymnasium, yoga studio, indoor/outdoor games, and female faculty supervision.",
    "library": "Advanced library with 50,000+ books, e-journals, digital resources, reading areas, and quiet study spaces.",
    "computer center": "Three (3) state-of-the-art computer labs with latest software and hardware, UPS backup, campus-wide LAN, high-speed internet, and centralized AC.",
    "labs": "Well-equipped laboratories for each department with latest equipment, practical training, project facilities, and simulation software.",
    "gym": "Separate gymnasium facilities for boys and girls equipped with latest equipment and professional trainers for fitness training.",
    "sports": "Sports complex with courts for Basketball, Volleyball, Badminton, Tennis grounds, Football field, Cricket facility. Teams in Cricket, Football, Basketball, Badminton, Table Tennis, and Athletics.",
    "sports facilities": "Indoor and outdoor sports facilities including Basketball, Volleyball, Badminton courts, Football ground, Tennis courts, Gymnasium, and recreation areas.",
    "health center": "On-campus health center with doctor, first aid facilities, emergency medical support, and regular health check-up camps.",
    "cafeteria": "Spacious college cafeteria and separate canteen for girls hostel serving nutritious, multi-cuisine food in clean and hygienic environment.",
    "transport": "College transport facility covering major areas of Hyderabad with affordable rates, on-time service, safe drivers, and parent tracking system. Free transport for teaching and non-teaching staff.",
    "parking": "Spacious parking facility available for students and staff vehicles.",
    "yoga": "Yoga studio with professional instructors for physical and mental wellness.",
    "green campus": "25-acre green campus with ornamental plants, solar panels for energy conservation, and eco-friendly initiatives.",
    
    # Research & Development
    "r&d": "Active Research & Development cell promoting innovation, research projects, and faculty publications.",
    "aicte idea lab": "AICTE-sanctioned IDEA Lab fostering creative thinking, innovation, and startup ideas. Students trained in problem-solving and collaboration.",
    "iedc": "NewGen IEDC (Institutional Entrepreneurship Development Cell) supporting student entrepreneurs and startup development.",
    "research": "Multiple research facilities and centers for excellence including AICTE IDEA Lab, R&D Cell, NEWGEN IEDC, and Teaching-Learning Center.",
    
    # Student Activities
    "clubs": "12 student clubs: Coders Club, Creators Club, Cultural Club (Prathiba Yogyata), Eco Club, Fitness Club (Yogyata), Gamers Club, Literary/Fine Arts Club, Multimedia Club (Trinetra), NSS Club (Devna), Radio Club, Sports Club (Sankalp), Women's Chapter (SheInspires).",
    "ncc": "National Cadet Corps (NCC) providing military training, discipline, and leadership development to students.",
    
    # Admissions & Eligibility
    "admission": "B.Tech through EAMCET merit (70% - Category A) and Management Seats (30% - Category B). Lateral Entry available for Diploma holders.",
    "elibility": "10+2 pass with Math, Physics, Chemistry. For Lateral Entry: Diploma in any branch.",
    "category a": "70% seats filled by TSEAMCET merit-based selection.",
    "category b": "30% seats filled by college management selection.",
    "lateral entry": "10% seats available for Diploma holders through TSECET exam.",
    "fee": "B.Tech: ₹85,000 per year | M.Tech: ₹50,000 per year | MBA: ₹1,00,000 per year",
    "fees": "B.Tech: ₹85,000 per year | M.Tech: ₹50,000 per year | MBA: ₹1,00,000 per year",
    "scholarship": "Merit-based scholarships, EWS scholarships, SC/ST scholarships, and sports scholarships available.",
    "sunday hours": "College remains open on Sundays from 9:00 AM to 5:00 PM for admissions inquiries.",
    
    # Awards & Achievements
    "awards": "Best Performing Engineering Institute 2025 (South-Central Zone), 55 All India Ranking (EduSkills Virtual Internship Rankings 2025), Outstanding Institute of Future Ready Engineers, Best Infrastructure among Private Engineering Colleges in Telangana.",
    "achievements": "Multiple awards for excellence in engineering education, digital learning, infrastructure, and leadership. Faculty and students recognized nationally and internationally.",
    "google cloud": "Approved by Google for Google Cloud Career Readiness Program.",
    "accreditation": "NAAC A Grade Accreditation, Autonomous Institution status, AICTE Approval, JNTU Hyderabad Affiliation.",
}

# Function to find best matching answer from knowledge base
def get_knowledge_base_answer(user_input):
    user_input_lower = user_input.lower()
    user_words = user_input_lower.split()
    
    best_match = None
    best_score = 0
    
    for key, value in COLLEGE_KNOWLEDGE_BASE.items():
        # Check for exact keyword match
        if key in user_input_lower:
            return value
        
        # Check for partial matches
        score = sum(1 for word in key.split() if word in user_words)
        if score > best_score:
            best_score = score
            best_match = value
    
    if best_score >= 1:
        return best_match
    return None

# Gemini fallback with strict college context (Comprehensive 2026 Data)
def get_gemini_response(user_input, history=None):
    """
    Generate college-specific answers using Google Gemini.
    Uses recent conversation history for context-awareness and answers ONLY about Sphoorthy Engineering College.
    """
    # Build a short conversation context (last few messages)
    convo_context = ""
    if history:
        last = history[-8:]
        convo_context = "\n\nPREVIOUS CONVERSATION (most recent last):\n"
        for item in last:
            role = item.get("role", "user")
            text = item.get("content", "")
            convo_context += f"{role.upper()}: {text}\n"

    prompt = f"""You are "CollegeBot", the official virtual assistant for Sphoorthy Engineering College, Hyderabad. Answer ONLY about this college.

SPHOORTHY ENGINEERING COLLEGE - COMPLETE 2026 INFORMATION:

IDENTITY & ACCREDITATION:
- Established: 2004
- Status: AICTE-Approved Autonomous Institution
- Affiliation: JNTU Hyderabad
- Accreditation: NAAC A Grade
- Campus: 25-acre green campus with sustainable environment
- Location: Nadargul Village, Saroornagar Mandal, Hyderabad, Telangana - 501510
- Contact: +91 9392 11 9392 | +91 99 666 31091 | admissions@sphoorthyengg.ac.in

LEADERSHIP (Verified 2026):
- Director: Dr. M.V.S. Ram Prasad
- Chairman: S. Chalama Reddy (Master's Math/Education, 25+ years, President Thoma Educational Society)
- Secretary & Correspondent: S. Jagan Mohan Reddy (Visionary Leader Award Times of India 2025)
- CEO: Mr. S. Holydhar Reddy

DEPARTMENTS & HEAD OF DEPARTMENTS:
1. CSE (Computer Science): Prof. Dr. Kiran B. M. - 7416081491 - hodcse@sphoorthyengg.ac.in
2. AIML (AI & Machine Learning): Dr. KVSN RAMARAO - 9603899920 - ramarao.kvsn@sphoorthyengg.ac.in
3. Data Science: Dr. Allam Balaram (M.Tech PhD) - 7093908833 - hodds@sphoorthyengg.ac.in
4. Cyber Security: Mrs. P. Sandhya Rani (M.Tech PhD) - 7013999909 - hodcs@sphoorthyengg.ac.in
5. Freshman Engineering: Dr. P. Gayathri Pavani (M.Sc PhD) - 9392118525 - hodhns@sphoorthyengg.ac.in
6. Electronics & Communication Engineering (ECE)
7. Civil Engineering

ACADEMIC PROGRAMS:
- B.Tech (4 years): CSE | AIML | Data Science | Cyber Security | Civil | ECE
- M.Tech (2 years): CSE | AIML Specialization
- MBA (2 years)
- Admission: Category A (70% EAMCET merit) | Category B (30% management) | Lateral Entry (10% diploma holders via TSECET)
- Fees: B.Tech ₹85,000/yr | M.Tech ₹50,000/yr | MBA ₹1,00,000/yr
- Scholarships: Merit-based, EWS, SC/ST, Sports scholarships available

PLACEMENTS (2024-2025):
- 92% placement rate across all batches
- 2022-23: 600+ offers | 2021-22: 754 placements | 2020-21: 235 placements | 2019-20: 480 placements
- 24+ Recruiting Companies: Accenture, Infosys, TCS, Wipro, Tech Mahindra, HCL, Capgemini, IBM, Deloitte, Cadila Global, Hexaware, EPAM, Five 9s, Cogent, Corizo, and others
- Average & Highest packages vary by branch and performance

INFRASTRUCTURE & FACILITIES:
- 3 Computer Labs: Latest software/hardware, UPS, Campus-wide LAN, High-speed internet, Centralized AC
- 50,000+ Book Library: E-journals, digital resources, reading areas
- Well-Equipped Department Labs: Modern equipment, practical training, simulation software
- Hostels: Separate boys/girls with furnished rooms, nutritious food, Wi-Fi, 24/7 security, ragging-free environment
- Girls Hostel: Female faculty supervision, Yoga studio, Gymnasium, Indoor/outdoor games
- Gym: Separate facilities for boys and girls, Latest equipment, Professional trainers
- Sports: Basketball, Volleyball, Badminton, Tennis, Football, Cricket facilities. Teams & Annual Sports Carnival
- Health Center: On-campus doctor, First aid, Emergency support, Regular health camps
- Cafeteria: Spacious, Nutritious multi-cuisine food, Separate girls hostel canteen, Hygienic preparation
- Transport: Fleet of buses, Affordable rates, On-time service, Safe drivers, Parent tracking. Free for staff
- Green Campus: Solar panels, Ornamental plants, Sustainable environment initiatives

RESEARCH & INNOVATION:
- AICTE IDEA Lab: Sanctioned by AICTE New Delhi, Fosters creative thinking and innovation
- R&D Cell: Active research and publications
- NEWGEN IEDC: Entrepreneurship development cell for startups
- Teaching-Learning Center: Focus on innovative pedagogy

STUDENT ACTIVITIES:
- 12 Student Clubs: Coders (Code Architects) | Creators | Cultural (Prathiba Yogyata) | Eco | Fitness (Yogyata) | Gamers | Literary/Fine Arts | Multimedia (Trinetra) | NSS (Devna) | Radio | Sports (Sankalp) | Women's Chapter (SheInspires)
- NCC: National Cadet Corps for discipline and military training
- Alumni Network: Active alumni community with networking opportunities

AWARDS & ACHIEVEMENTS (2025-2026):
- Best Performing Engineering Institute 2025 (South-Central Zone)
- 55 All India Ranking: EduSkills Virtual Internship Rankings 2025 Engineering
- Outstanding Institute of Future Ready Engineers (Elets FutureEd Summit 2025)
- Best Infrastructure among Private Engineering Colleges in Telangana (HMTV Technical Education Awards 2025)
- Google Cloud Career Readiness Program Approval
- Multiple awards for digital learning, infrastructure, and leadership excellence

CORE VALUES:
- "Sphoorthy embodies inspiration and provides a stimulating atmosphere for young minds to reform and recreate their potentials to break barriers of success"
- Focus on holistic development, technical excellence, ethics, and innovation
- Emphasis on outcome-based education and industry alignment

RESPONSE RULES:
1. Answer ONLY about Sphoorthy Engineering College
2. If asked about other colleges/irrelevant topics, politely decline with: "I'm specifically designed to help with Sphoorthy Engineering College questions. Please ask about our college!"
3. Keep answers factual, brief (2-3 sentences max unless detailed info requested)
4. Use official contact numbers and emails when relevant
5. If unsure about a fact, say "I'll suggest contacting the college directly for the latest information"
6. Always be professional, welcoming, and encouraging

{convo_context}
\n\nUSER QUESTION: "{user_input}"\n
Respond in a friendly, informative manner. If it's about Sphoorthy Engineering College, provide accurate information. Otherwise, politely decline:"""

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
        reply = reply.replace("**", "")

        # Check if Gemini declined to answer
        if "i don't" in reply.lower() or "outside" in reply.lower() or "cannot" in reply.lower():
            return "I'm specifically designed to help with Sphoorthy Engineering College questions. Please ask about our college!"

        return reply
    except Exception as e:
        print("Gemini Error:", e)
        return "Sorry, I couldn't process that. Please try again or ask about our college."

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_input = request.json.get("msg", "").strip()
    
    if not user_input:
        return jsonify({"reply": "Please ask a question about Sphoorthy Engineering College!"})
    
    user_input_lower = user_input.lower()
    # initialize session history
    if "history" not in session:
        session["history"] = []
    history = session["history"]

    # append user message to history
    history.append({"role": "user", "content": user_input})
    if len(history) > 200:
        history = history[-200:]
    session["history"] = history

    # 1️⃣ Check knowledge base first (most accurate)
    kb_answer = get_knowledge_base_answer(user_input)
    if kb_answer:
        # store assistant reply in history
        history = session.get("history", [])
        history.append({"role": "assistant", "content": kb_answer})
        session["history"] = history
        return jsonify({"reply": kb_answer})

    # If question likely asks for names/entities prefer Gemini directly when KB misses
    name_keywords = ["who is", "who are", "name of", "hod", "hods", "chairman", "secretary", "director", "principal", "who's", "contact", "phone", "email"]
    if any(k in user_input_lower for k in name_keywords):
        gemini_reply = get_gemini_response(user_input, history=history)
        history = session.get("history", [])
        history.append({"role": "assistant", "content": gemini_reply})
        session["history"] = history
        return jsonify({"reply": gemini_reply})

    # 2️⃣ Try ChatterBot with confidence threshold
    try:
        response = chatbot.get_response(user_input)
        confidence = float(response.confidence)
        if confidence >= 0.6:
            bot_text = str(response)
            history = session.get("history", [])
            history.append({"role": "assistant", "content": bot_text})
            session["history"] = history
            return jsonify({"reply": bot_text})
    except Exception as e:
        print(f"ChatterBot error: {e}")

    # 3️⃣ Use Gemini for contextual answers (with college context and conversation history)
    gemini_reply = get_gemini_response(user_input, history=history)
    history = session.get("history", [])
    history.append({"role": "assistant", "content": gemini_reply})
    session["history"] = history
    return jsonify({"reply": gemini_reply})

if __name__ == "__main__":
    app.run(debug=True)
