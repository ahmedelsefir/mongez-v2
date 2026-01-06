import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from gtts import gTTS
import os
import io

# 1. إعداد الذاكرة الحديدية (قاعدة البيانات)
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

# 2. إعداد المحرك الاستقراري (Gemini 1.5 Flash)
# تم دمج المفتاح الخاص بك وإصلاح إعدادات الموديل
API_KEY = "AIzaSyCRSAXTgS-0siA2zcadDZQRoderEgXmnuw"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. تهيئة الواجهة الاحترافية
st.set_page_config(page_title="مُنجز v4.0", page_icon="🚀", layout="wide")
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# نظام الدخول والتسجيل
if not st.session_state['logged_in']:
    st.sidebar.title("🔐 بوابة مُنجز")
    menu = st.sidebar.selectbox("الدخول / التسجيل", ["تسجيل دخول", "إنشاء حساب جديد"])
    
    if menu == "إنشاء حساب جديد":
        st.subheader("إنشاء حساب مستخدم جديد")
        new_user = st.text_input("اسم المستخدم")
        new_pass = st.text_input("كلمة المرور", type='password')
        if st.button("إنشاء الحساب"):
            conn = sqlite3.connect('mongez_v4.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users VALUES (?,?)', (new_user, make_hashes(new_pass)))
                conn.commit()
                st.success("تم إنشاء الحساب بنجاح! انتقل لتسجيل الدخول")
            except:
                st.error("اسم المستخدم موجود مسبقاً")
            finally:
                conn.close()
    else:
        st.subheader("تسجيل الدخول")
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
                st.error("بيانات الدخول غير صحيحة")

# 4. لوحة تحكم مُنجز بعد الدخول
if st.session_state['logged_in']:
    st.title(f"🚀 مُنجز v4.0: الشريك التقني")
    st.sidebar.write(f"مرحباً بك، {st.session_state['user']}")
    
    # اختيار الأدوات المدمجة
    tool_choice = st.sidebar.radio("الأدوات المتاحة", ["المساعد الذكي", "محول النص لصوت", "ذاكرة المشاريع"])
    
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # نظام الدردشة المطور
    user_msg = st.chat_input("تحدث مع مُنجز...")
    
    if user_msg:
        try:
            # إضافة نظام تدريب الشخصية المهنية
            prompt = f"أنت مهندس برمجيات خبير. رد على المستخدم {st.session_state['user']}: {user_msg}"
            response = model.generate_content(prompt)
            
            # عرض الرد وحفظه
            st.chat_message("assistant").write(response.text)
            
            # تفعيل ميزة الصوت إذا تم اختيارها
            if tool_choice == "محول النص لصوت":
                tts = gTTS(text=response.text, lang='ar')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp)
                
        except Exception as e:
            st.error(f"حدث خطأ في الاتصال: {e}")

    if st.sidebar.button("تسجيل خروج"):
        st.session_state['logged_in'] = False
        st.rerun()
        
