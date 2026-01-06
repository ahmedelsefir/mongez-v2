import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from gtts import gTTS
import os

# 1. إعدادات قاعدة البيانات (الذاكرة الحديدية)
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
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# 2. إعدادات Gemini الاستقراية (v1.5 Flash)
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # ضع مفتاحك هنا
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. واجهة المستخدم ونظام التسجيل
st.set_page_config(page_title="مُنجز v4.0", layout="wide")
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    cols = st.sidebar.selectbox("الدخول / التسجيل", ["تسجيل دخول", "إنشاء حساب جديد"])
    
    if cols == "إنشاء حساب جديد":
        new_user = st.text_input("اسم المستخدم الجديد")
        new_pass = st.text_input("كلمة المرور", type='password')
        if st.button("إنشاء"):
            conn = sqlite3.connect('mongez_v4.db')
            c = conn.cursor()
            c.execute('INSERT INTO users VALUES (?,?)', (new_user, make_hashes(new_pass)))
            conn.commit()
            st.success("تم إنشاء الحساب بنجاح! انتقل لتسجيل الدخول")
    else:
        user = st.sidebar.text_input("اسم المستخدم")
        pw = st.sidebar.text_input("كلمة المرور", type='password')
        if st.sidebar.button("دخول"):
            conn = sqlite3.connect('mongez_v4.db')
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username =?', (user,))
            result = c.fetchone()
            if result and check_hashes(pw, result[0]):
                st.session_state['logged_in'] = True
                st.session_state['user'] = user
                st.rerun()

# 4. لوحة تحكم مُنجز (بعد الدخول)
if st.session_state['logged_in']:
    st.title("🚀 مُنجز: الشريك التقني v4.0")
    st.sidebar.write(f"مرحباً بك، {st.session_state['user']}")
    
    # ميزة النطق الصوتي
    mode = st.sidebar.radio("الأدوات", ["المساعد الذكي", "محول النص لصوت", "ذاكرة المشاريع"])
    
    user_input = st.chat_input("تحدث مع مُنجز...")
    
    if user_input:
        response = model.generate_content(user_input)
        st.write(response.text)
        
        if mode == "محول النص لصوت":
            tts = gTTS(text=response.text, lang='ar')
            tts.save("response.mp3")
            st.audio("response.mp3")

    if st.sidebar.button("تسجيل خروج"):
        st.session_state['logged_in'] = False
        st.rerun()
