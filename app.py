import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json

app = Flask(__name__, template_folder='.')
CORS(app)

CLINICS_LIST = """
"الباطنة-العامة", "غدد-صماء-وسكر", "جهاز-هضمي-ومناظير", "باطنة-وقلب", "الجراحة-العامة",
"مناعة-وروماتيزم", "نساء-وتوليد", "أنف-وأذن-وحنجرة", "الصدر", "أمراض-الذكورة", "الجلدية",
"العظام", "المخ-والأعصاب-باطنة", "جراحة-المخ-والأعصاب", "المسالك-البولية", "الأوعية-الدموية",
"الأطفال", "الرمد", "تغذية-الأطفال", "مناعة-وحساسية-الأطفال", "القلب", "رسم-قلب-بالمجهود-وإيكو",
"جراحة-التجميل", "علاج-البواسير-والشرخ-بالليزر", "الأسنان", "السمعيات", "أمراض-الدم"
"""

@app.route("/api/recommend", methods=["POST"])
def recommend_clinic():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms')
        if not symptoms: return jsonify({"error": "Missing symptoms"}), 400
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("CRITICAL ERROR: GEMINI_API_KEY is not set.")
            return jsonify({"error": "Server configuration error."}), 500

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        أنت مساعد طبي خبير ومحترف في مستشفى كبير. مهمتك هي تحليل شكوى المريض بدقة واقتراح أفضل عيادتين بحد أقصى من قائمة العيادات المتاحة.
        قائمة معرفات (IDs) العيادات المتاحة هي: [{CLINICS_LIST}]
        شكوى المريض: "{symptoms}"
        ردك يجب أن يكون بصيغة JSON فقط، بدون أي نصوص إضافية، ويحتوي على قائمة اسمها "recommendations" بداخلها عناصر تحتوي على "id" و "reason".
        """
        
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        json_response = json.loads(cleaned_text)
        return jsonify(json_response)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/')
def serve_index():
    return render_template('index.html')

if __name__ == "__main__":
    # This part is for local development, Google Cloud Run uses the Procfile.
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
