import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore, auth
import hashlib

# 1. الاتصال بالسحاب (Firebase) بدلاً من SQLite [cite: 2026-01-13]
if not firebase_admin._apps:
    try:
        # تأكد أن ملف الجيسون في نفس مجلد المشروع
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"خطأ في الاتصال بالسحاب: {e}")

db = firestore.client()

# 2. وظائف الحماية وتشفير البيانات
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# 3. إعدادات الذكاء الاصطناعي (Gemini)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.warning("يرجى التأكد من مفتاح API لـ Gemini")

# --- واجهة البرنامج الاحترافية ---
st.set_page_config(page_title="Mongez Cloud v5.0", page_icon="🛡️", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 4. وظائف تسجيل الدخول السحابية (Authentication)
if not st.session_state['logged_in']:
    st.title("🛡️ تسجيل دخول المنجز (السحابي)")
    user_email = st.text_input("البريد الإلكتروني")
    user_pw = st.text_input("كلمة السر", type='password')
    
    if st.button("دخول"):
        try:
            # التحقق من المستخدم في Firebase
            user_record = auth.get_user_by_email(user_email)
            # جلب دور المستخدم (قائد/موظف/مندوب) من Firestore
            user_doc = db.collection("users").document(user_record.uid).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = user_email
                st.session_state['role'] = user_data.get('role', 'user')
                st.rerun()
        except Exception as e:
            st.error("بيانات الدخول غير صحيحة أو المستخدم غير موجود")

# 5. تفعيل محركات العمل بناءً على "وظيفة المستخدم"
if st.session_state['logged_in']:
    role = st.session_state['role']
    st.sidebar.success(f"مرحباً: {st.session_state['user_email']} ({role})")
    
    # القائمة تتغير حسب الوظيفة (Role-Based Menu)
    menu_options = ["المساعد الذكي"]
    if role == "صاحب عمل": # القائد
        menu_options += ["برنامج المحاسب المعتمد", "إدارة الموظفين", "جالب العملاء SEO"]
    if role == "موظف دعم" or role == "صاحب عمل":
        menu_options += ["مركز خدمة العملاء 🎧"]
    
    app_choice = st.sidebar.radio("قائمة التحكم", menu_options)

    # --- وظيفة مركز خدمة العملاء (رد الموظفين) ---
    if app_choice == "مركز خدمة العملاء 🎧":
        st.title("🎧 نظام دعم العملاء")
        tickets = db.collection("support_tickets").where("status", "==", "open").stream()
        for ticket in tickets:
            t_data = ticket.to_dict()
            with st.expander(f"تذكرة من: {t_data.get('user_email')}"):
                st.write(f"الرسالة: {t_data.get('message')}")
                reply = st.text_area("رد الموظف هنا...", key=ticket.id)
                if st.button("إرسال الرد", key=f"btn_{ticket.id}"):
                    db.collection("support_tickets").document(ticket.id).update({
                        "reply": reply,
                        "status": "closed",
                        "replied_by": st.session_state['user_email']
                    })
                    st.success("تم الرد وإغلاق الطلب!")

    # --- وظيفة المساعد الذكي (Gemini) ---
    elif app_choice == "المساعد الذكي":
        st.title("🚀 مُنجز AI")
        u_input = st.chat_input("اسأل مُنجز عن أي شيء في عملك...")
        if u_input:
            resp = model.generate_content(u_input)
            st.write(resp.text)
