import os
from fpdf import FPDF
from datetime import datetime

class WalkthroughPDF(FPDF):
    def header(self):
        # Top banner background
        self.set_fill_color(29, 53, 87) # Deep Blue
        self.rect(0, 0, 210, 18, "F")
        
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 4)
        self.cell(0, 10, "LOOM VIDEO WALKTHROUGH GUIDE & SCRIPT", ln=True)
        
        # Subtitle details
        self.set_font("Helvetica", "I", 8)
        self.set_xy(10, 11)
        self.cell(0, 5, "Scaler AI Engineer Screening  |  Candidate: Anurag Sajwan", ln=True)
        
        # Reset spacing
        self.set_y(22)

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f"Page {self.page_no()} of 2", align="C")

def build_walkthrough_pdf():
    pdf = WalkthroughPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 10, 10)
    
    # PAGE 1
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(29, 53, 87)
    pdf.cell(0, 6, "1. OVERVIEW & PRE-RECORDING CHECKLIST", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 51, 51)
    intro_p = (
        "This guide provides a step-by-step recording plan and script for your Loom walkthrough video (target: <= 3 minutes). "
        "The goal is to demonstrate technical depth, system responsiveness, and clear reasoning under pressure to the Scaler evaluators."
    )
    pdf.multi_cell(0, 4, intro_p)
    pdf.ln(2)
    
    # Checklist Table
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(0, 5, "Preparation Steps:", fill=True, ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 4.5, "  [ ] Browser Tabs: Open Vercel Chat UI, Vapi Call logs, Cal.com Dashboard, and GitHub Repo (README.md).", ln=True)
    pdf.cell(0, 4.5, "  [ ] Terminal: Open a terminal window showing the fastapi logs in the background if running locally.", ln=True)
    pdf.cell(0, 4.5, "  [ ] Audio Check: Ensure your microphone is clear and background noise is minimized.", ln=True)
    pdf.cell(0, 4.5, "  [ ] Pace: Speak calmly and deliberately. Keep your cursor steady; avoid frantic page scrolling.", ln=True)
    pdf.ln(3)
    
    # Scene Breakdown Section
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(29, 53, 87)
    pdf.cell(0, 6, "2. LOOM SCENE-BY-SCENE WALKTHROUGH SCRIPT", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    # Scene 1
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(166, 25, 46) # Accent Red
    pdf.cell(0, 4.5, "Scene 1: Introduction & Live Chat Demo (0:00 - 0:45)", ln=True)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Visual: Live deployed chat window (https://scaler-ai-persona-pi.vercel.app).", ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 51, 51)
    script_1 = (
        "\"Hi, I'm Anurag Sajwan. Today, I'll walk you through my Autonomous AI Persona, designed for the Scaler AI screening. "
        "Here is the live Next.js chat interface. Let's ask it a question about my background to show it is fully grounded in my resume: "
        "[Type: 'What is your experience with AI Agents?']... As you see, the response streams back instantly, pulling facts directly "
        "from my resume corpus. Let's book a slot: [Type: 'Book an interview']... The backend dynamically checks my real calendar and "
        "recommends only 3 open slots. Let's type 'ram, ram@gmail.com' and choose 9:30 AM. The booking is confirmed instantly.\""
    )
    pdf.multi_cell(0, 4, script_1)
    pdf.ln(2.5)
    
    # Scene 2
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(166, 25, 46)
    pdf.cell(0, 4.5, "Scene 2: Core Architecture Overview (0:45 - 1:20)", ln=True)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Visual: GitHub README.md showing the Mermaid architecture diagram.", ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 51, 51)
    script_2 = (
        "\"Here is the system architecture. We have a decoupled Next.js web client and a FastAPI backend. "
        "For voice calls, we use Vapi integrated with Deepgram STT, ElevenLabs TTS, and a GPT-4o-mini orchestrator, "
        "delivering natural, sub-2s responses with custom interruption handling. "
        "For chat RAG, we use NVIDIA NIM's nv-embedqa-e5-v5 embeddings stored in Pinecone serverless, "
        "and meta/llama-3.1-8b-instruct for lightning-fast token generation.\""
    )
    pdf.multi_cell(0, 4, script_2)
    
    # PAGE 2
    pdf.add_page()
    
    # Scene 3
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(166, 25, 46)
    pdf.cell(0, 4.5, "Scene 3: Hard Engineering Problems Solved (1:20 - 2:20)", ln=True)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Visual: Code editor showing backend/main.py, scroll to the book_meeting endpoint.", ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 51, 51)
    script_3 = (
        "\"The hardest problem I solved was preventing the LLM from hallucinating booking details. Eager models like Llama 3.1 8B "
        "often try to call the booking tool immediately by fabricating a date, time, and guest details, without asking the user. "
        "To solve this, I designed strict, stateful backend validation filters in FastAPI. "
        "First, the backend uses regular expressions to confirm a valid email address was explicitly entered by the user. "
        "Second, it parses the conversation history to verify that availability slots were actually checked and presented to the user. "
        "If either check fails, the backend raises a descriptive validation error, which forces the LLM to self-correct, "
        "ask the user for details, and follow the correct booking pipeline. This ensures a clean, bulletproof scheduling UX.\""
    )
    pdf.multi_cell(0, 4, script_3)
    pdf.ln(2.5)
    
    # Scene 4
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(166, 25, 46)
    pdf.cell(0, 4.5, "Scene 4: Latency Optimization & Evaluation Results (2:20 - 3:00)", ln=True)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Visual: Open the generated eval/EVAL_REPORT.pdf file.", ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 51, 51)
    script_4 = (
        "\"Finally, let's look at the evaluation report. By moving from Llama 3.1 70B to the 8B-Instruct model and implementing "
        "global HTTP connection pooling for embedding queries, we reduced first-token latency by over 90%, from 42 seconds to "
        "an average of 3.8 seconds. The voice agent's average response latency is 650 milliseconds, and the system achieves "
        "a 0% hallucination rate on the golden Q&A suite. Thanks for watching! All code is pushed and live.\""
    )
    pdf.multi_cell(0, 4, script_4)
    pdf.ln(4)
    
    # Tips Section
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(29, 53, 87)
    pdf.cell(0, 6, "3. KEY TALKING POINTS & TIPS FOR UPLOADING", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 4.5, "- Highlight Honesty: Emphasize that the RAG model is strictly grounded and will report when it doesn't know an answer.", ln=True)
    pdf.cell(0, 4.5, "- Focus on System Design: Explain that you chose stateful backend filters over soft prompts because it provides absolute reliability.", ln=True)
    pdf.cell(0, 4.5, "- Keep it concise: Watch your timer during recording. If you go over 3 minutes, pause, delete, and re-record a slide.", ln=True)
    pdf.cell(0, 4.5, "- Trim if needed: Use Loom's built-in trim editor to cut out any long loading pauses or throat clears.", ln=True)
    
    pdf.output("eval/WALKTHROUGH_GUIDE.pdf")
    print("Saved guide to eval/WALKTHROUGH_GUIDE.pdf")

if __name__ == "__main__":
    build_walkthrough_pdf()
