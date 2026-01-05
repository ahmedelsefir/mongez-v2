import streamlit as st
import google.generativeai as genai
import os

# 1. إعدادات الصفحة والهوية
st.set_page_config(page_title="Mongez AI v3.0", page_icon="🚀", layout="wide")

# 2. التحقق من الهوية (نظام الحماية الذي طلبته)
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login():
    st.title("🔐 تسجيل دخول مبرمج أحمد")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "ahmed" and pw == "123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("بيانات خاطئة")

if not st.session_state.auth:
    login()
    st.stop()

# 3. إعداد محرك Gemini 2.0 Flash
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# 4. واجهة المستخدم (صانع التطبيقات)
st.sidebar.title("🛠️ أدوات منجز")
mode = st.sidebar.selectbox("اختر الوضع", ["المساعد الذكي", "صانع الأكواد", "تحليل الصور"])

st.title("🚀 مُنجز: الشريك التقني الذكي")
st.info("الوضع الحالي: تطوير التطبيقات والبرمجة الاحترافية")

# نظام الشات
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("كيف يمكن لمنجز مساعدتك في بناء تطبيقك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = model.generate_content(f"انت منجز، صانع تطبيقات خبير. طلب المستخدم: {prompt}")
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
