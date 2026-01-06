import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from gtts import gTTS
import os
import io

# 1. إعداد قاعدة البيانات (الذاكرة الحديدية لمُنجز)
def init_db():
    conn = sqlite3.connect('mongez_v4.db')
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    # جدول الذاكرة لحفظ تدريبات المشاريع
    c.execute('''CREATE TABLE IF NOT EXISTS memory 
                 (username TEXT, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# 2. النظام الأمني (استدعاء المفتاح من الأسرار)
try:
    # سيتم جلب المفتاح من إعدادات Secrets في Streamlit كما في صورتك
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # التعديل الهام: استخدام gemini-1.5-flash لضمان التوافق واختفاء خطأ 404
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.warning("⚠️ يرجى التأكد من ضبط GOOGLE_API_KEY في إعدادات Secrets")

# 3. إعدادات واجهة المستخدم
st.set_page_config(page_title="Mongez AI v4.0", page_icon="🚀", layout="wide")
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 4. بوابة الدخول والتسجيل
if not st.session_state['logged_in']:
    st.sidebar.title("🔐 بوابة مُنجز v4.0")
    menu = st.sidebar.selectbox("الدخول / التسجيل", ["تسجيل دخول", "إنشاء حساب جديد"])
    
    if menu == "إنشاء حساب جديد":
        st.subheader("📝 إنشاء حساب تقني جديد")
        new_user = st.text_input("اسم المستخدم")
        new_pass = st.text_input("كلمة المرور", type='password')
        if st.button("تفعيل الحساب"):
            conn = sqlite3.connect('mongez_v4.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users VALUES (?,?)', (new_user, make_hashes(new_pass)))
                conn.commit()
                st.success("تم الإنشاء بنجاح! يمكنك الآن تسجيل الدخول")
            except:
                st.error("اسم المستخدم مأخوذ مسبقاً")
            finally:
                conn.close()
    else:
        st.subheader("🔑 تسجيل الدخول")
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
                st.error("خطأ في بيانات الدخول")

# 5. لوحة التحكم والتدريب (بعد الدخول)
if st.session_state['logged_in']:
    st.title(f"🚀 مُنجز v4.0: الشريك التقني")
    st.sidebar.success(f"متصل الآن: {st.session_state['user']}")
    
    tool = st.sidebar.radio("الأدوات المتاحة", ["المساعد الذكي", "محول النص لصوت", "ذاكرة المشاريع"])
    
    user_input = st.chat_input("ابدأ التدريب أو اطلب كوداً...")
    
    if user_input:
        try:
            prompt = f"أنت مهندس برمجيات خبير. رد على {st.session_state['user']}: {user_input}"
            response = model.generate_content(prompt)
            
            st.chat_message("assistant").write(response.text)
            
            # ميزة الصوت عند الطلب
            if tool == "محول النص لصوت":
                tts = gTTS(text=response.text, lang='ar')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp)
                
        except Exception as e:
            st.error(f"حدث خطأ في الاتصال بالموديل: {e}")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()
