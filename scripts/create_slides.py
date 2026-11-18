"""Create a concise presentation from VERIFIED project results."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUT = Path("Student_Retention_Intelligence_Presentation.pptx")
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BG = RGBColor(10, 17, 34)
CARD = RGBColor(22, 33, 54)
WHITE = RGBColor(238, 245, 255)
MUTED = RGBColor(157, 175, 198)
CYAN = RGBColor(49, 204, 215)
AMBER = RGBColor(255, 194, 94)


def textbox(slide, x, y, w, h, text, size=20, color=WHITE, bold=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    for idx, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.space_after = Pt(14)
    return shape


def panel(slide, x, y, w, h, title, desc, highlight=False):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = CARD
    sh.line.color.rgb = CYAN if highlight else RGBColor(37, 51, 73)
    textbox(slide, x+.25, y+.2, w-.5, .55, title, 21, CYAN if highlight else WHITE, True)
    textbox(slide, x+.25, y+.85, w-.5, h-1, desc, 16, MUTED)


def slide(title, kicker, footer=True):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
    textbox(s, .62, .25, 11.9, .3, kicker.upper(), 12, CYAN, True)
    textbox(s, .62, .75, 12, 1.15, title, 31, WHITE, True)
    if footer:
        textbox(s, .63, 7.1, 12, .2, "GROUP 12  •  INT395 SUPERVISED LEARNING  •  RESEARCH PROTOTYPE", 10, MUTED)
    return s


s = slide("Student Retention Intelligence", "Early detection • Explainability • Human support")
textbox(s, .7, 2.2, 11.8, 1.4, "An interpretable student-outcome prediction and advisor-support demonstration", 27, WHITE)
textbox(s, .7, 4.65, 11.8, .9, "Duggisetty Vasavi Vignan  •  Kabya Varun  •  Shivraj Singh", 20, CYAN)
textbox(s, .7, 5.55, 11.8, .5, "Academic project · Session 2026–27", 16, MUTED)

s = slide("The problem and our approach", "Why this project")
panel(s, .7, 2.0, 5.8, 3.6, "Challenge", "Academic difficulties may be recognized late. Early warnings can create an opportunity for voluntary, targeted support.")
panel(s, 6.8, 2.0, 5.8, 3.6, "Approach", "Use historical enrollment and semester data to model outcomes, explain estimates, and provide advisor review tools.", True)

s = slide("Real dataset, defined prediction moments", "Data integrity")
panel(s, .7, 2.0, 3.85, 3.8, "4,424 students", "Official UCI dataset 697, with three outcome labels: Dropout, Enrolled and Graduate.")
panel(s, 4.72, 2.0, 3.85, 3.8, "Three stages", "Enrollment, end of first semester and end of second semester. Future grades excluded at earlier stages.")
panel(s, 8.75, 2.0, 3.85, 3.8, "No invented data", "The UCI dataset does not contain individual attendance percentages. Enrolled is not guaranteed retained.")

s = slide("A reproducible ML workflow", "System architecture")
for i, (a,b) in enumerate([("01 Data", "Validate schema and outcomes"),("02 Prepare", "Encode, scale, prevent leakage"),("03 Learn", "Seven classifier families"),("04 Evaluate", "CV + untouched holdout"),("05 Explain", "SHAP, LIME, what-if"),("06 Support", "Fictional advisor review")]):
    panel(s, .7+(i%3)*4.02, 2.0+(i//3)*2.3, 3.85, 2.05, a, b, highlight=i==3)

s = slide("Seven-algorithm comparison", "Five-fold training cross-validation")
rows = [("Random Forest", .6819),("Logistic Regression", .6801),("SVM", .6787),("Gradient Boosting", .6554),("Decision Tree", .6254),("KNN", .5503),("Naïve Bayes", .2136)]
for i, (name, val) in enumerate(rows):
    y=2.02+i*.62
    textbox(s, .8, y, 3.6, .4, name, 17, WHITE)
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.35), Inches(y+.02), Inches(val*9.3), Inches(.3))
    sh.fill.solid();sh.fill.fore_color.rgb=CYAN if i==0 else RGBColor(61, 103, 145)
    sh.line.fill.background()
    textbox(s, 11.12, y, 1.1, .36, f"{val:.3f}", 16, WHITE, True)

s = slide("Model quality: performance and trade-offs", "Held-out evaluation")
panel(s, .7, 2.0, 3.85, 3.7, "0.625 macro-F1", "Calibrated Random Forest held-out performance. Baseline macro-F1 was 0.652.", True)
panel(s, 4.72, 2.0, 3.85, 3.7, "74.3% recall", "Training-selected threshold caught 211 of 284 dropout-labeled records; missed 73.")
panel(s, 8.75, 2.0, 3.85, 3.7, "71.3% precision", "85 non-dropout-labeled records were also flagged. False positives have costs.")

s = slide("Explainability is not causality", "Trust and transparency")
panel(s, .7, 2.0, 5.8, 3.8, "SHAP", "Attributes prediction contributions relative to a background. Validated on a trained model and a real UCI record.")
panel(s, 6.8, 2.0, 5.8, 3.8, "LIME", "Fits an interpretable approximation near one record. Models can be sensitive to feature changes without proving causal effects.")

s = slide("Advisor support, with humans in control", "Retention intelligence")
panel(s, .7, 2.0, 5.8, 3.8, "Demonstration workflow", "Use fictional DEMO identifiers to document support options: tutoring, advising, financial aid information and follow-up status.")
panel(s, 6.8, 2.0, 5.8, 3.8, "Safety boundary", "No real student case storage. No automated penalties, decisions or interventions. Production use requires explicit governance.", True)

s = slide("Limitations and professional next steps", "Honest engineering")
panel(s, .7, 2.0, 5.8, 3.8, "Known limitations", "Institution-specific dataset; calibration not externally validated; no protected case store or production monitoring.")
panel(s, 6.8, 2.0, 5.8, 3.8, "Deployment gates", "Calibration, privacy review, authorization, independent validation, educator feedback, drift monitoring and controlled trials.")

s = slide("Thank you", "Questions and discussion")
textbox(s, .85, 2.3, 11.7, 2.1, "Our goal: detect possible support needs earlier, explain model behavior, and keep decisions with educators.", 27, WHITE, True)
textbox(s, .85, 5.1, 11.7, .7, "UCI dataset 697  •  Python  •  Scikit-learn  •  Streamlit  •  SHAP  •  LIME", 17, CYAN)

prs.save(OUT)
print(OUT)
