from flask import Flask, render_template, request, redirect, url_for, session
import time
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
# NLP & Web scraping
import spacy
import requests
from bs4 import BeautifulSoup

# Selenium setup with headless mode and auto-installer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options

# Auto install matching ChromeDriver
chromedriver_autoinstaller.install()

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# API key for Mistral
MISTRAL_API_KEY = "aKFEMuDwJOvtphHDDOrh2qbfRP7jEA1L"

# Skill extraction keywords
skill_keywords = [
    "Python", "Java", "JavaScript", "C++", "SQL", "MongoDB", "PostgreSQL", "Machine Learning",
    "Deep Learning", "Neural Networks", "Data Science", "AI", "Django", "Flask", "React", "React Native", "Node.js",
    "TensorFlow", "PyTorch", "API", "AWS", "Cloud Computing", "DevOps", "Competitive Programming","Data Structures",
    "Algorithms", "Web Development", "Software Development", "Computer Vision", "Natural Language Processing",
    "Data Analysis", "Business Intelligence", "Power BI", "Tableau", "Big Data", "Hadoop", "Spark", "ETL", "CI/CD",
    "Kubernetes", "Docker", "Git", "Linux", "Unix", "Shell Scripting", "Automation", "Agile", "Scrum", "Kanban", 
    "Problem Solving","HTML", "CSS", "Bootstrap", "SASS", "LESS", "jQuery", "Angular", "Vue.js", "TypeScript",
    "Svelte", "Web Design", "UI/UX","REST", "GraphQL", "Microservices", "Serverless", "Blockchain", "Cryptocurrency",
    "Solidity", "Ethereum", "DeFi", "NFT","Cybersecurity", "Ethical Hacking", "Penetration Testing", "OWASP",
    "Firewall", "VPN", "Security Audits", "Compliance", "ISO 27001","Risk Management", "Fraud Detection",
    "Identity & Access Management", "SIEM", "Splunk", "Networking", "TCP/IP", "DNS", "HTTP", "SSL","Wireless Networks",
    "Network Security", "Cisco", "Juniper", "CompTIA", "CCNA", "CCNP", "CCIE", "CEH", "CISSP", "CISM","CISA",
]

# Exclude list
exclude_list = ["AuxPlutes Tech", "EBTS Organization"]


# Extract skills from profile
def extract_skills(about_text):
    extracted_skills = []
    lower_text = about_text.lower()

    for skill in skill_keywords:
        if skill.lower() in lower_text:
            extracted_skills.append(skill)

    doc = nlp(about_text)
    for token in doc.ents:
        if token.label_ in ["ORG", "PRODUCT"]:
            extracted_skills.append(token.text)

    extracted_skills = [skill for skill in extracted_skills if skill not in exclude_list]
    return list(set(extracted_skills))

# Log in using session-stored credentials
def login_linkedin_session(driver):
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)
    driver.find_element(By.ID, "username").send_keys(session['email'])
    driver.find_element(By.ID, "password").send_keys(session['password'] + Keys.RETURN)
    time.sleep(10)

# Scrape LinkedIn profile for skills
# Scrape LinkedIn profile for skills
def scrape_linkedin_profile(linkedin_url):
    options = webdriver.ChromeOptions()
    
    # Make sure the browser is visible (disable headless explicitly)
    options.headless = False
    options.add_argument("--start-maximized")  # Open full screen
    options.add_experimental_option("detach", True)  # Keep browser open after script ends

    # Optional: Suppress some logging
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # ✅ Fixed: using the correct login function
    login_linkedin_session(driver)

    driver.get(linkedin_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    name_section = soup.find("h1")
    name = name_section.text.strip() if name_section else "No Name Found"

    about_section = soup.find("div", {"class": "display-flex ph5 pv3"})
    about_text = about_section.text.strip() if about_section else "No About section found"

    extracted_skills = extract_skills(about_text)

    print(f"\n🔹 Name: {name}")
    print(f"\n🔹 About Section:\n{about_text}")
    print(f"\n✅ Extracted Skills: {extracted_skills}")

    return extracted_skills

# Generate quiz questions
def generate_quiz_questions(skills, num_questions=10):
    questions = []
    MODEL_NAME = "mistral-large-latest"
    questions_per_skill = max(1, num_questions // len(skills))

    for skill in skills:
        for _ in range(questions_per_skill):
            if len(questions) >= num_questions:
                break

            prompt_text = (
                f"Generate a hard multiple-choice question on {skill}. Make sure not to include any image or code. "
                "Format:\nQuestion: <question>\nA) <option 1>\nB) <option 2>\nC) <option 3>\nD) <option 4>\n"
                "Correct Answer: <correct option>\nExplanation: <why it's correct>"
            )

            try:
                response = requests.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": MODEL_NAME,
                        "messages": [{"role": "user", "content": prompt_text}],
                        "max_tokens": 300
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()

                    question, options, correct_answer, explanation = None, [], None, None
                    lines = content.split("\n")
                    for line in lines:
                        if line.startswith("Question:"):
                            question = line.split("Question:")[1].strip()
                        elif line.startswith(("A)", "B)", "C)", "D)")):
                            options.append(line[3:].strip())
                        elif line.startswith("Correct Answer:"):
                            correct_answer = line.split("Correct Answer:")[1].strip().split(")")[0]
                        elif line.startswith("Explanation:"):
                            explanation = line.split("Explanation:")[1].strip()

                    if question and len(options) == 4 and correct_answer and explanation:
                        questions.append({
                            "question": question,
                            "options": options,
                            "correct_answer": correct_answer,
                            "explanation": explanation,
                            "skill": skill
                        })

            except:
                continue

            time.sleep(1)

    return questions

# Study material generation
def generate_study_material(weak_skills):
    study_material = {}
    MODEL_NAME = "mistral-large-latest"

    for skill in weak_skills:
        prompt_text = (
            f"Provide a detailed study guide for {skill}. "
            "Include key concepts, best practices, and learning resources in 500 words."
        )

        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": prompt_text}],
                    "max_tokens": 500
                },
                timeout=15
            )

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                study_material[skill] = content

        except:
            continue

        time.sleep(1)

    return study_material

# ============= FLASK ROUTES ==============

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session['linkedin_url'] = request.form["linkedin_url"]
        session['email'] = request.form["email"]
        session['password'] = request.form["password"]
        return redirect(url_for("quiz"))
    return render_template("index.html")

@app.route("/quiz")
def quiz():
    linkedin_url = session.get("linkedin_url")
    if not linkedin_url:
        return redirect(url_for("index"))

    skills = scrape_linkedin_profile(linkedin_url)
    session["skills"] = skills
    session["questions"] = generate_quiz_questions(skills, 10)
    session["score"] = 0
    session["mistakes"] = {}

    return redirect(url_for("quiz_question", qid=0))

@app.route("/quiz/<int:qid>", methods=["GET", "POST"])
def quiz_question(qid):
    questions = session["questions"]
    if request.method == "POST":
        answer = request.form.get("answer")
        correct = questions[qid]["correct_answer"]
        if answer == correct:
            session["score"] += 1
        else:
            skill = questions[qid]["skill"]
            mistakes = session["mistakes"]
            mistakes[skill] = mistakes.get(skill, 0) + 1
            session["mistakes"] = mistakes
        return redirect(url_for("quiz_question", qid=qid + 1))

    if qid >= len(questions):
        return redirect(url_for("results"))

    return render_template("quiz.html", qid=qid, total=len(questions), q=questions[qid])

@app.route("/results")
def results():
    return render_template("results.html",
                           score=session["score"],
                           total=len(session["questions"]),
                           mistakes=session["mistakes"])

@app.route("/study")
def study():
    weak_skills = list(session["mistakes"].keys())
    study_content = generate_study_material(weak_skills)
    return render_template("study.html", study=study_content)

   
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Render sets PORT env var
    app.run(host='0.0.0.0', port=port)
