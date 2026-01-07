import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from gtts import gTTS
import os
import io

# 1. إعداد قاعدة بيانات مُنجز (الذاكرة)
def init_db():
    conn = sqlite3.connect('mongez_v4.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS memory 
                 (username TEXT, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text
# الربط الآلي الجذري مع سيرفر جوجل
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # برمجة الطرفية لاختيار الموديل المتاح تلقائياً
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    selected_model = available_models[0] if available_models else 'gemini-1.5-flash'
    model = genai.GenerativeModel(selected_model)
    
except Exception as e:
    st.error(f"⚠️ خطأ في الربط مع السيرفر: {e}")

# 3. واجهة مُنجز الاحترافية
st.set_page_config(page_title="Mongez v4.0", page_icon="🚀", layout="wide")
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 4. نظام الدخول
if not st.session_state['logged_in']:
    st.sidebar.title("🔐 بوابة مُنجز")
    menu = st.sidebar.selectbox("القائمة", ["تسجيل دخول", "إنشاء حساب"])
    
    if menu == "إنشاء حساب":
        new_user = st.text_input("اسم المستخدم")
        new_pass = st.text_input("كلمة المرور", type='password')
        if st.button("تسجيل"):
            conn = sqlite3.connect('mongez_v4.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users VALUES (?,?)', (new_user, make_hashes(new_pass)))
                conn.commit()
                st.success("تم الإنشاء! سجل دخولك الآن")
            except:
                st.error("الاسم موجود مسبقاً")
            finally:
                conn.close()
    else:
        user = st.sidebar.text_input("اسم المستخدم")
        pw = st.sidebar.text_input("كلمة المرور", type='password')
        if st.sidebar.button("دخول"):
            conn = sqlite3.connect('mongez_v4.db')
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username =?', (user,))
            result = c.fetchone()
            conn.close()
            if result and check_hashes(pw, result[0]):
                st.session_state['logged_in'] = True
                st.session_state['user'] = user
                st.rerun()
            else:
                st.error("بيانات خاطئة")

# 5. تشغيل المساعد
if st.session_state['logged_in']:
    st.title(f"🚀 مرحباً {st.session_state['user']} في مُنجز v4.0")
    
    tool = st.sidebar.radio("الأدوات", ["المساعد الذكي", "محول الصوت"])
    user_input = st.chat_input("تحدث مع شريكك التقني...")
    
    if user_input:
        try:
            response = model.generate_content(user_input)
            st.chat_message("assistant").write(response.text)
            
            if tool == "محول الصوت":
                tts = gTTS(text=response.text, lang='ar')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp)
        except Exception as e:
            st.error(f"خطأ: {e}")
