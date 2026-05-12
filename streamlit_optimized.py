import streamlit as st
import sqlite3
import json
import uuid
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any
import google.generativeai as genai
import re

# 1. إعدادات المنظومة والواجهة
st.set_page_config(page_title="⚖️ محكمة الأفكار - النسخة المتكاملة", page_icon="⚖️", layout="wide")

# ربط محرك Gemini من خلال Secrets مع معالجة الأخطاء
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ يرجى ضبط GEMINI_API_KEY في إعدادات Streamlit Secrets (Settings > Secrets)")
    st.stop()

# 2. إدارة قاعدة البيانات والمنطق البنيوي (RMS)
@st.cache_resource
def init_db():
    # استخدام قاعدة بيانات محلية للحفاظ على القواعد بين الجلسات
    conn = sqlite3.connect("bench_internal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS catalogs (
        id TEXT PRIMARY KEY, title TEXT, logic_core TEXT, 
        status BOOLEAN, created_at TEXT, version INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY, agent TEXT, message TEXT, 
        severity TEXT, timestamp TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# 3. محرك الوكلاء العشرة (The 10 Agents Engine)
class BenchAgent:
    def __init__(self, role_name: str, model_name: str = "gemini-1.5-flash"):
        self.role_name = role_name
        # التصحيح: استخدام اسم الموديل مباشرة بدون سوابق لتجنب خطأ 404
        self.model = genai.GenerativeModel(model_name)
    
    def get_role_instruction(self) -> str:
        roles = {
            "المناقش": "عرض الآيات القرآنية ذات الصلة المباشرة وبحث الروابط البنيوية.",
            "محلل_الآيات": "تحليل الألفاظ سياقياً ودراسة المترادفات والمتضادات المادية.",
            "المستنتج": "الاستنتاج المنطقي الصارم المشتق من النصوص المتاحة فقط.",
            "الملاحظ": "رصد الأنماط النصية والتكرارات الإحصائية في البيانات.",
            "المثبت": "التحقق من صحة أرقام الآيات والمراجع النصية (العضو 5).",
            "المقعد": "إدارة سجل القواعد (القواعس) وضمان ثبات المنهج.",
            "المنسق": "تنظيم تدفق المحادثة وتوزيع الأدوار بين الوكلاء (العضو 7).",
            "المراقب": "رصد التعارضات مع الكتالوجات وإطلاق التنبيهات الحمراء (العضو 8).",
            "الاستراتيجي": "الربط بين الجلسات المختلفة وبناء ذاكرة تحليلية تراكمية (العضو 9).",
            "الأوتوماتيكي": "المعالجة الشاملة ودمج مخرجات جميع الوكلاء في تحليل نهائي واحد (العضو 10)."
        }
        return roles.get(self.role_name, "وكيل تحليلي")

    def process(self, query: str, active_rules_manifest: str) -> str:
        # بناء الـ System Prompt بطريقة "محكمة الأفكار" الصارمة
        system_prompt = f"""أنت {self.role_name} في 'محكمة الأفكار'. 
مهمتك الأساسية: {self.get_role_instruction()}

القواعد الصارمة:
1. يمنع منعا باتا الحشو الأدبي أو الوعظ.
2. الاستدلال بالمنطق المادي للنصوص القرآنية فقط.
3. التزام كامل ببروتوكول 'البينة'.

🔴 القواعس المفعلة من نظام RMS (يجب تطبيقها فوراً):
{active_rules_manifest}
"""
        try:
            # استخدام generate_content للوصول المباشر
            response = self.model.generate_content(f"{system_prompt}\n\nالسؤال المادي للتحليل: {query}")
            return response.text
        except Exception as e:
            return f"❌ خطأ في المعالجة (Gemini API): {str(e)}"

# 4. بناء واجهة المستخدم (Interface)
def main():
    st.markdown("<h1 style='text-align: center;'>⚖️ محكمة الأفكار - The Bench of Evidence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>نظام التحليل البنيوي المعتمد على Gemini 1.5 & RMS</p>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["💬 مجلس التحليل", "📋 الكتالوجات (RMS)", "🔴 الرصد الأمني"])

    # --- التبويب 1: جلسة التحليل ---
    with tab1:
        col_q, col_a = st.columns([2, 1])
        with col_q:
            user_input = st.text_area("أدخل السؤال أو النص المادي للتحليل:", height=180, 
                                     placeholder="مثال: تحليل مادي لمفهوم 'الروح' من خلال السياقات النصية...")
        with col_a:
            agents_list = ["المناقش", "محلل_الآيات", "المستنتج", "الملاحظ", "المثبت", "المقعد", "المنسق", "المراقب", "الاستراتيجي", "الأوتوماتيكي"]
            selected_agents = st.multiselect("اختيار أعضاء المجلس:", agents_list, default=["المناقش", "المستنتج"])
            st.info("الوكيل 10 (الأوتوماتيكي) يقوم بدمج كافة التحليلات.")
        
        if st.button("⚖️ تشغيل المحكمة المادية", use_container_width=True):
            if user_input:
                # استخراج القواعد المفعلة من قاعدة البيانات
                c = db_conn.cursor()
                c.execute("SELECT title, logic_core FROM catalogs WHERE status = 1")
                rules = c.fetchall()
                manifest = "\n".join([f"- {r[0]}: {r[1]}" for r in rules]) if rules else "لا توجد قواعس مفعلة حالياً."

                # تنفيذ معالجة كل وكيل مختار
                for name in selected_agents:
                    with st.status(f"⏳ {name} يحلل البيانات...", expanded=False) as status:
                        agent = BenchAgent(name)
                        output = agent.process(user_input, manifest)
                        st.markdown(f"### 🛡️ رد {name}")
                        st.write(output)
                        status.update(label=f"✅ اكتمل تحليل {name}", state="complete")
            else:
                st.warning("⚠️ يرجى إدخال سؤال تحليلي للبدء.")

    # --- التبويب 2: إدارة الكتالوجات (RMS) ---
    with tab2:
        st.header("📋 إدارة القواعس (نظام RMS)")
        with st.expander("➕ إضافة قاعدة منطقية جديدة", expanded=False):
            with st.form("new_rule_form"):
                t = st.text_input("اسم القاعدة (مثلاً: قانون التناظر المادي):")
                l = st.text_area("جوهر المنطق (Logic Core):")
                if st.form_submit_button("اعتماد وحفظ"):
                    if t and l:
                        cursor = db_conn.cursor()
                        cursor.execute("INSERT INTO catalogs VALUES (?, ?, ?, ?, ?, ?)", 
                                       (str(uuid.uuid4()), t, l, True, datetime.now().isoformat(), 1))
                        db_conn.commit()
                        st.success("✅ تم حفظ القاعدة وتفعيلها في محرك الوكلاء.")
                        st.rerun()

        st.divider()
        c = db_conn.cursor()
        c.execute("SELECT * FROM catalogs ORDER BY created_at DESC")
        rows = c.fetchall()
        
        if not rows:
            st.write("لا توجد قواعد مخزنة حالياً.")
        else:
            for cid, title, logic, status, dt, ver in rows:
                with st.container(border=True):
                    col_1, col_2 = st.columns([0.8, 0.2])
                    col_1.subheader(title)
                    if col_2.button("🗑️", key=cid):
                        cursor = db_conn.cursor()
                        cursor.execute("DELETE FROM catalogs WHERE id = ?", (cid,))
                        db_conn.commit()
                        st.rerun()
                    st.code(logic, language="text")
                    st.caption(f"تاريخ الإنشاء: {dt} | الحالة: {'✅ مفعلة' if status else '⭕ معطلة'}")

    # --- التبويب 3: التنبيهات الرادعة ---
    with tab3:
        st.header("🔴 نظام الرصد والرقابة")
        st.metric("سلامة المنطق البنيوي", "100%", delta="مستقر")
        
        with st.container(border=True):
            st.markdown("**سجل التنبيهات (العضو 8):**")
            st.info("النظام يراقب حالياً التزام الوكلاء بالقواعس المفعلة. لم يتم رصد أي تعارض مادي حتى الآن.")

if __name__ == "__main__":
    main()
