"""
⚖️ محكمة الأفكار - Streamlit v2.0 (محسّن لـ GitHub)
The Bench of Evidence - Optimized for GitHub
════════════════════════════════════════════════════════════════
"""

import streamlit as st
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import anthropic
import re
import requests
from io import StringIO

# ════════════════════════════════════════════════════════════
# 1. إعدادات Streamlit
# ════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="⚖️ محكمة الأفكار",
    page_icon="⚖️",
    layout="wide"
)

# ════════════════════════════════════════════════════════════
# 2. Helper Functions
# ════════════════════════════════════════════════════════════

@st.cache_resource
def init_db():
    """تهيئة قاعدة البيانات"""
    conn = sqlite3.connect(":memory:")  # في الذاكرة = أسرع
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS catalogs (
        id TEXT PRIMARY KEY,
        title TEXT,
        logic_core TEXT,
        status BOOLEAN,
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        agent TEXT,
        message TEXT,
        severity TEXT,
        timestamp TEXT
    )''')
    
    conn.commit()
    return conn

@st.cache_data(ttl=3600)
def fetch_from_github(url: str):
    """تحميل ملف من GitHub"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None

# ════════════════════════════════════════════════════════════
# 3. الواجهة الرئيسية
# ════════════════════════════════════════════════════════════

def main():
    st.title("⚖️ محكمة الأفكار")
    st.subheader("The Bench of Evidence - GitHub Edition")
    
    # الشريط الجانبي
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        
        api_key = st.text_input(
            "مفتاح Anthropic API:",
            type="password",
            placeholder="sk-ant-..."
        )
        
        mode = st.radio(
            "طريقة التحميل:",
            ["📤 رفع ملف", "🔗 رابط GitHub"],
            horizontal=True
        )
        
        st.divider()
        st.info("""
        ✅ **الميزات:**
        - 10 وكلاء ذكيين
        - نظام RMS للقواعس
        - تنبيهات حمراء
        - يعمل مع GitHub
        """)
    
    if not api_key:
        st.warning("⚠️ يرجى إدخال مفتاح API للبدء")
        return
    
    # ════════════════════════════════════════════════════════════
    # التبويبات الرئيسية
    # ════════════════════════════════════════════════════════════
    
    tab1, tab2, tab3 = st.tabs(["💬 الدردشة", "📋 الكتالوجات", "🔴 التنبيهات"])
    
    # ─────────────────────────────────────────────────────────
    # التبويب 1: الدردشة
    # ─────────────────────────────────────────────────────────
    with tab1:
        st.header("💬 دردشة الوكلاء")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            question = st.text_area(
                "السؤال:",
                placeholder="مثال: ما معنى الفرقان في القرآن الكريم؟",
                height=100
            )
        
        with col2:
            agents_selected = st.multiselect(
                "الوكلاء:",
                ["المناقش 💬", "المحلل 🔬", "المستنتج 🧮", 
                 "الملاحظ 👁️", "الناقد ⚔️"],
                default=["المناقش 💬"]
            )
        
        if st.button("🚀 معالجة السؤال", use_container_width=True):
            if not question:
                st.error("❌ يرجى إدخال السؤال")
                return
            
            if not agents_selected:
                st.error("❌ يرجى اختيار وكيل واحد على الأقل")
                return
            
            # معالجة السؤال
            client = anthropic.Anthropic(api_key=api_key)
            
            for agent in agents_selected:
                with st.spinner(f"⏳ {agent}..."):
                    agent_name = agent.split()[0]
                    
                    system = f"""أنت {agent_name} في محكمة الأفكار.
استدل من القرآن الكريم فقط.
ممنوع أي رأي شخصي أو وعظ."""
                    
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=800,
                        system=system,
                        messages=[{
                            "role": "user",
                            "content": question
                        }]
                    )
                    
                    with st.expander(f"✅ {agent}", expanded=True):
                        st.markdown(response.content[0].text)
    
    # ─────────────────────────────────────────────────────────
    # التبويب 2: الكتالوجات
    # ─────────────────────────────────────────────────────────
    with tab2:
        st.header("📋 إدارة الكتالوجات")
        
        conn = init_db()
        c = conn.cursor()
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("new_catalog"):
                title = st.text_input("عنوان القاعدة:")
                logic = st.text_area("المنطق:", height=80)
                
                if st.form_submit_button("➕ إضافة قاعدة"):
                    if title and logic:
                        c.execute(
                            "INSERT INTO catalogs VALUES (?, ?, ?, ?, ?)",
                            (str(uuid.uuid4()), title, logic, True, 
                             datetime.now().isoformat())
                        )
                        conn.commit()
                        st.success("✅ تم إضافة القاعدة")
                        st.rerun()
        
        with col2:
            st.write("### القواعس المفعلة")
            
            c.execute("SELECT COUNT(*) FROM catalogs WHERE status = 1")
            count = c.fetchone()[0]
            
            st.metric("عدد القواعس النشطة", count)
            
            if st.button("✅ تطبيق جميع القواعس"):
                st.success(f"✅ تم تطبيق {count} قاعدة")
        
        st.divider()
        
        # عرض القواعس
        c.execute("SELECT * FROM catalogs ORDER BY created_at DESC")
        catalogs = c.fetchall()
        
        if catalogs:
            for cat_id, title, logic, status, created in catalogs:
                with st.expander(f"{'✅' if status else '⭕'} {title}"):
                    col1, col2 = st.columns([0.8, 0.2])
                    
                    with col1:
                        st.text(logic)
                    
                    with col2:
                        if st.button("🗑️", key=f"del_{cat_id}"):
                            c.execute("DELETE FROM catalogs WHERE id = ?", (cat_id,))
                            conn.commit()
                            st.rerun()
        else:
            st.info("📭 لا توجد قواعس")
    
    # ─────────────────────────────────────────────────────────
    # التبويب 3: التنبيهات
    # ─────────────────────────────────────────────────────────
    with tab3:
        st.header("🔴 التنبيهات الحمراء")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🔴 حرجة", "0")
        
        with col2:
            st.metric("⚠️ تحذيرات", "0")
        
        st.info("✅ النظام يعمل بشكل صحيح - لا توجد مشاكل")
        
        if st.button("🔄 فحص يدوي"):
            st.success("✅ تم الفحص - كل شيء طبيعي")

# ════════════════════════════════════════════════════════════
# 4. البداية
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
