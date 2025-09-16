from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import spacy
import PyPDF2
import io
from fastapi.staticfiles import StaticFiles
import os


# load spacy model
nlp = spacy.load("en_core_web_sm")

SKILLS_DB = [
    #Computer Science / IT
    "python","java","c++","sql","javascript","react","node.js","html","css",
    "aws","docker","nlp","ml","iam","cv","pytorch","tensorflow","flask","django","linux","git",

    #Mechanical
    "solidworks","autocad","ansys","catia","matlab","thermodynamics","fluid mechanics",
    "heat transfer","cad","cfd","hvac","manufacturing",

    #Electronics & Communication
    "vhdl","verilog","fpga","arduino","raspberry pi","signal processing","embedded systems",
    "iot","communication systems","antennas",

    #Electrical & Electronics
    "power systems","control systems","microcontrollers","pcb design","scada",
    "switchgear","electric drives","power electronics","renewable energy",

    #Civil
    "staad pro","etabs","primavera","revit","autocad civil","construction management",
    "surveying","geotechnical","structural analysis","project management",

    #Finance
    "financial analysis","budgeting","forecasting","excel","tally","quickbooks","sap",
    "financial modeling","investment banking","auditing","risk management","portfolio management",
    "taxation","derivatives","equity research"
]

app = FastAPI()

# serve frontend folder (where index.html is kept)
app.mount("/sih", StaticFiles(directory="sih", html=True), name="sih")

# allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Resume Skill Extractor API running 🚀"}

@app.post("/extract_skills/")
async def extract_skills(file: UploadFile = File(...)):
    # check if uploaded file is PDF
    if file.filename.endswith(".pdf"):
        pdf_bytes = await file.read()
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    else:
        # fallback: try reading as text
        text = (await file.read()).decode("utf-8", errors="ignore")

    text = text.lower()
    doc = nlp(text)
    found = set()

    # keyword match
    for skill in SKILLS_DB:
        if skill in text:
            found.add(skill)

    # optional: nlp noun chunks
    for chunk in doc.noun_chunks:
        if chunk.text in SKILLS_DB:
            found.add(chunk.text)

    return {"skills": list(found)}

