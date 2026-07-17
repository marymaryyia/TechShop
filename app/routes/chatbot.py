import os
from flask import Blueprint, request, jsonify, session
from dotenv import load_dotenv
from google import genai

chatbot_bp = Blueprint('chatbot', __name__)

load_dotenv()
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("ყურადღება: API გასაღები ვერ მოიძებნა!")

ai_client = genai.Client(api_key=GOOGLE_API_KEY)

@chatbot_bp.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'შეტყობინება ცარიელია',
                'response': 'გთხოვთ, მოიწეროთ შეტყობინება.',
                'reply': 'გთხოვთ, მოიწეროთ შეტყობინება.'
            }), 200

        prompt = (
            "შენ ხარ ტექნიკის მაღაზია 'TechShop'-ის მეგობრული AI ასისტენტი. "
            "შენი მიზანია დაეხმარო მომხმარებლებს. ილაპარაკე მოკლედ, გასაგებად და თავაზიანად. "
            "თუ კითხვა არ ეხება ტექნიკას ან მაღაზიას, თავაზიანად შეახსენე შენი ფუნქცია. "
            f"მომხმარებლის შეკითხვა: {user_message}"
        )

        response = ai_client.models.generate_content(
            model='gemini-flash-lite-latest',  
            contents=prompt,
        )
        
        reply_text = response.text if response.text else "ბოდიში, პასუხის მომზადება ვერ მოხერხდა."

        print(f"\n[AI SUCCESS] მომხმარებელი: {user_message}")
        print(f"[AI SUCCESS] პასუხი: {reply_text}\n")
        
        return jsonify({
            'response': reply_text,
            'reply': reply_text
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"\n[AI ERROR] Chatbot API Error: {error_msg}\n")
        
        lang = session.get('lang', 'ka')
        
        messages = {
            'quota_exceeded': {
                'ka': 'ბოდიში, ამჟამად ძალიან ბევრი მომართვა გვაქვს. გთხოვთ, სცადოთ რამდენიმე წუთში. 🤖',
                'en': 'Sorry, we are receiving too many requests right now. Please try again in a few minutes. 🤖'
            },
            'overloaded': {
                'ka': 'სისტემა დროებით გადატვირთულია 🤯. გთხოვთ, მომწეროთ 1-2 წუთში. 🤖',
                'en': 'The system is temporarily overloaded 🤯. Please message me in 1-2 minutes. 🤖'
            },
            'generic_error': {
                'ka': 'ბოდიში, მცირე ტექნიკური შეფერხებაა 🛠️. გთხოვთ, სცადოთ მოგვიანებით.',
                'en': 'Sorry, there is a minor technical issue 🛠️. Please try again later.'
            }
        }
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            err_text = messages['quota_exceeded'][lang]
            status_code = 429
            
        elif "503" in error_msg or "UNAVAILABLE" in error_msg:
            err_text = messages['overloaded'][lang]
            status_code = 503
            
        else:
            err_text = messages['generic_error'][lang]
            status_code = 500
            
        return jsonify({
            'error': error_msg,
            'response': err_text,
            'reply': err_text
        }), status_code