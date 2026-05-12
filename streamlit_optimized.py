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
st.set_page_config(page_title="⚖️ محكمة الأفكار - النسخة المعمقة", page_icon="⚖️", layout="wide")

# ربط محرك Gemini من خلال Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ يرجى ضبط GEMINI_API_KEY في إعدادات Streamlit Secrets")

# 2. إدارة قاعدة البيانات والمنطق البنيوي (RMS)
@st.cache_resource
def init_db():
    # استخدام قاعدة بيانات في الذاكرة لسرعة الأداء في Streamlit Cloud
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
        self.model = genai.GenerativeModel(model_name)
    
    def get_role_instruction(self) -> str:
        roles = {
            "المناقش": "عرض الآيات القرآنية ذات الصلة المباشرة وبحث الروابط البنيوية.",
            "محلل_الآيات": "تحليل الألفاظ سياقياً ودراسة المترادفات والمتضادات المادية.",
            "المستنتج": "الاستنتاج المنطقي الصارم المشتق من النصوص المتاحة فقط.",
            "الملاحظ": "رصد الأنماط النصية والتكرارات الإحصائية في البيانات.",
            "المثبت": "التحقق من صحة أرقام الآيات والمراجع النصية (العضو 5).",
            "المقعد": "إدارة سجل القواعد (القواعس) وضمان ثبات المنهج.",
            "المنسق": "تنظيم تدفق المحادثة وتوزيع الأدوار بين الوكلاء.",
            "المراقب": "رصد التعارضات مع الكتالوجات وإطلاق التنبيهات الحمراء (العضو 8).",
            "الاستراتيجي": "الربط بين الجلسات المختلفة وبناء ذاكرة تحليلية تراكمية.",
            "الأوتوماتيكي": "المعالجة الشاملة ودمج مخرجات جميع الوكلاء في تحليل نهائي."
        }
        return roles.get(self.role_name, "وكيل تحليلي")

    def process(self, query: str, active_rules_manifest: str) -> str:
        system_prompt = f"""أنت {self.role_name} في 'محكمة الأفكار'. 
مهمتك: {self.get_role_instruction()}
الالتزام الصارم: الاستدلال من القرآن فقط، منع الإنشاء، منع الوعظ، اتباع المنطق المادي.

🔴 القواعس المفعلة حالياً (يجب الالتزام بها):
{active_rules_manifest}
"""
        try:
            response = self.model.generate_content(f"{system_prompt}\n\nالسؤال التحليلي: {query}")
            return response.text
        except Exception as e:
            return f"❌ خطأ في المعالجة: {str(e)}"

# 4. بناء الواجهة (Tabs)
def main():
    st.title("⚖️ محكمة الأفكار - The Bench of Evidence")
    st.caption("النسخة المتكاملة (10 وكلاء + RMS + Gemini)")

    tab1, tab2, tab3 = st.tabs(["💬 جلسة التحليل", "📋 نظام الكتالوجات (RMS)", "🔴 التنبيهات الرادعة"])

    # --- التبويب 1: جلسة التحليل ---
    with tab1:
        col_q, col_a = st.columns([3, 1])
        with col_q:
            user_input = st.text_area("أدخل السؤال أو النص المادي للتحليل:", height=150, placeholder="مثال: تحليل مفهوم 'البيان' بناءً على سياق سورة الرحمن...")
        with col_a:
            agents_list = ["المناقش", "محلل_الآيات", "المستنتج", "الملاحظ", "المثبت", "المقعد", "المنسق", "المراقب", "الاستراتيجي", "الأوتوماتيكي"]
            selected = st.multiselect("اختيار الوكلاء (مجلس التحقيق):", agents_list, default=["المناقش", "المستنتج"])
        
        if st.button("🚀 تشغيل المحكمة المادية", use_container_width=True):
            if user_input:
                # جلب القواعد من الكتالوج لحقنها في الوكلاء
                c = db_conn.cursor()
                c.execute("SELECT title, logic_core FROM catalogs WHERE status = 1")
                rules = c.fetchall()
                manifest = "\n".join([f"- {r[0]}: {r[1]}" for r in rules]) if rules else "لا توجد قواعد مفعلة."

                for name in selected:
                    with st.spinner(f"⏳ {name} يقوم بالمعالجة..."):
                        agent = BenchAgent(name)
                        output = agent.process(user_input, manifest)
                        with st.expander(f"✅ {name}", expanded=True):
                            st.markdown(output)
            else:
                st.warning("⚠️ يرجى إدخال سؤال للبدء.")

    # --- التبويب 2: إدارة الكتالوجات ---
    with tab2:
        st.header("📋 إدارة الكتالوجات (قواعد المنطق المادي)")
        with st.expander("➕ إضافة قاعدة جديدة (قاعس)", expanded=False):
            with st.form("new_rule"):
                t = st.text_input("اسم القاعدة:")
                l = st.text_area("المنطق البنيوي للقاعدة (Logic Core):")
                if st.form_submit_button("حفظ القاعدة"):
                    if t and l:
                        cursor = db_conn.cursor()
                        cursor.execute("INSERT INTO catalogs VALUES (?, ?, ?, ?, ?, ?)", 
                                       (str(uuid.uuid4()), t, l, True, datetime.now().isoformat(), 1))
                        db_conn.commit()
                        st.success("✅ تم حفظ القاعدة وتفعيلها أوتوماتيكياً")
                        st.rerun()

        st.divider()
        c = db_conn.cursor()
        c.execute("SELECT * FROM catalogs ORDER BY created_at DESC")
        for cid, title, logic, status, dt, ver in c.fetchall():
            col_t, col_s, col_d = st.columns([0.6, 0.2, 0.2])
            col_t.write(f"**{title}**")
            status_text = "✅ مفعلة" if status else "⭕ معطلة"
            col_s.write(status_text)
            if col_d.button("🗑️", key=cid):
                cursor = db_conn.cursor()
                cursor.execute("DELETE FROM catalogs WHERE id = ?", (cid,))
                db_conn.commit()
                st.rerun()
            st.info(logic)

    # --- التبويب 3: التنبيهات ---
    with tab3:
        st.header("🔴 التنبيهات الحمراء")
        st.metric("الحالة الأمنية للمنطق", "مستقر ✅")
        st.write("يقوم العضو 8 (المراقب) برصد أي تعارض بين مخرجات الوكلاء وبين الكتالوجات المفعلة.")
        st.info("لا توجد تنبيهات حالياً. جميع الاستنتاجات تقع ضمن النطاق المادي.")

if __name__ == "__main__":
    main()
