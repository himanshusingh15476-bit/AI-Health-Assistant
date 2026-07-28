import os
import io

from flask import Flask, render_template, request, send_file
from google import genai

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ================= GEMINI API =================
# Set your key as an environment variable instead of hardcoding it:
#   export GEMINI_API_KEY="your-key-here"   (Mac/Linux)
#   setx GEMINI_API_KEY "your-key-here"      (Windows)

API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(
    api_key=API_KEY
)


# ================= HOME PAGE =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= PATIENT PAGE =================

@app.route("/patient")
def patient():
    return render_template("patient.html")


# ================= ANALYZE =================

@app.route("/analyze", methods=["POST"])
def analyze():

    # Patient Details
    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]

    height = float(request.form["height"])
    weight = float(request.form["weight"])

    symptoms = request.form["symptoms"]
    description = request.form["description"]

    # ================= BMI =================

    height_meter = height / 100
    bmi = weight / (height_meter * height_meter)

    if bmi < 18.5:
        bmi_status = "Underweight"
    elif bmi < 25:
        bmi_status = "Normal"
    elif bmi < 30:
        bmi_status = "Overweight"
    else:
        bmi_status = "Obese"
    # ================= HEALTH RISK =================

    if bmi < 18.5:
        risk = "🟡 Moderate Risk"

    elif bmi < 25:
        risk = "🟢 Low Risk"

    elif bmi < 30:
        risk = "🟠 Moderate Risk"

    else:
        risk = "🔴 High Risk" 
    # ================= HEALTH SCORE =================

    if bmi < 18.5:
        health_score = 65

    elif bmi < 25:
        health_score = 95

    elif bmi < 30:
        health_score = 75

    else:
        health_score = 45       

    # ================= AI PROMPT =================

    prompt = f"""
You are an experienced medical AI assistant.

Patient Information
Name : {name}
Age : {age}
Gender : {gender}
Height : {height} cm
Weight : {weight} kg
BMI : {round(bmi, 1)}

Symptoms :
{symptoms}

Problem Description :
{description}

Please generate a professional report.

Format:
1. Possible Health Conditions
2. Possible Causes
3. Home Care Advice
4. Foods to Eat
5. Foods to Avoid
6. General OTC Medicines (if appropriate)
7. When to Visit a Doctor
8. Disclaimer

Write in simple English.
Never claim a confirmed diagnosis.
"""

    # ================= GEMINI =================

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
        ai_report = response.text

    except Exception as e:
        ai_report = f"""
AI Error

{str(e)}

Please check:
• API Key
• Internet Connection
• Gemini Model
"""

    # ================= RESULT =================

    return render_template(

    "result.html",

    name=name,

    age=age,

    gender=gender,

    height=height,

    weight=weight,

    bmi=round(bmi,1),

    bmi_status=bmi_status,

    risk=risk,

    health_score=health_score,

    symptoms=symptoms,

    description=description,

    report=ai_report

)

# ================= DOWNLOAD =================

@app.route("/download")
def download():

    report = request.args.get("report", "No Report")

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI Health Report</b>", styles["Heading1"]))
    story.append(Paragraph(report.replace("\n", "<br/>"), styles["BodyText"]))

    pdf.build(story)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="AI_Health_Report.pdf",
        mimetype="application/pdf"
    )


@app.route("/test")
def test():
    return "Download route is working!"


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)