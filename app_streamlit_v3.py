"""
🌟 مجلس البينة V4 - النسخة الهندسية المستقرة
يعتمد على نظام Callbacks لتأمين تدفق البيانات ومنع الارتداد
"""

import streamlit as st
import pandas as pd
import re
import os
import json
from datetime import datetime

# 1️⃣ الإعدادات البصرية الصارمة (ألوان ثلاثية وتصميم مسطح)
st.set_page_config(page_title="مجلس البينة V4", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    html, body, [data-testid="stAppViewContainer"] { background: #000000 !important; color: #ffffff !important; }
    
    .blackboard-container {
        background: #000000;
        border: 1px solid #333333;
        padding: 20px;
        margin-top: 10px;
        border-radius: 0px;
    }
    
    .verse-preview {
        background: #111111;
        border-right: 3px solid #ffffff;
        padding: 15px;
        font-size: 18px;
        line-height: 2;
        margin: 15px 0;
    }
    
    .context-verse {
        background: #161616;
        border-right: 2px solid #333333;
        padding: 10px;
        margin: 5px 0;
        font-size: 15px;
        color: #cccccc;
    }
    
    .context-verse-center {
        border-right: 2px solid #ffffff;
        background: #222222;
        font-weight: bold;
        color: #ffffff;
    }
    
    div.stButton > button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 0px !important;
        border: 1px solid #333333 !important;
        width: 100% !important;
        text-align: right !important;
        padding: 10px !important;
    }
    
    div.stButton > button:hover {
        border-color: #ffffff !important;
        background-color: #262626 !important;
    }
    
    div[data-testid="stTextInput"] input {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
    }
    
    header, footer { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# 2️⃣ تنظيف مادي للنصوص (حظر المربعات والرموز المشوهة)
def clean_quran_text(text):
    if not isinstance(text, str): return ""
    return re.sub(r"[\u0610-\u0615\u064B-\u065E\u06D6-\u06ED]", "", text).strip()

def normalize_arabic(text):
    text = clean_quran_text(text)
    text = re.sub(r"[إأآٱا]", "ا", text)
    text = re.sub(r"[ىي]", "ي", text)
    text = re.sub(r"[ةه]", "ه", text)
    return text

@st.cache_data
def load_quran_data():
    paths = ["data/data_quran.xlsx", "data_quran.xlsx"]
    for p in paths:
        if os.path.exists(p):
            try:
                df = pd.read_excel(p)
                for col in df.columns:
                    if df[col].dtype == object:
                        df[col] = df[col].astype(str).apply(clean_quran_text)
                return df
            except: continue
    return None

# 3️⃣ ميكانيكا الحفظ واسترجاع الأوراق المستقلة
RESULTS_DIR = 'data/mfolder_results'
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_paper(query, surah, verse, text, context_verses):
    sanitized = re.sub(r'[^\u0621-\u064A0-9]', '_', query).strip('_')
    filename = sorted(sanitized.split(), key=len)[-1] if sanitized.split() else f"{surah}_{verse}"
    filepath = os.path.join(RESULTS_DIR, f"{filename}_{surah}_{verse}.json")
    
    data = {
        'query': query, 'surah': surah, 'verse': verse,
        'text': text, 'context': context_verses,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except: return False

def load_papers():
    if not os.path.exists(RESULTS_DIR): return {}
    papers = {}
    for f in os.listdir(RESULTS_DIR):
        if f.endswith('.json'):
            try:
                with open(os.path.join(RESULTS_DIR, f), 'r', encoding='utf-8') as file:
                    papers[f[:-5]] = json.load(file)
            except: pass
    return papers

# 4️⃣ تهيئة الذاكرة والدوال الميكانيكية (Callbacks) لمنع الانهيار والارتداد
if "search_query" not in st.session_state: st.session_state.search_query = ""
if "main_search_input" not in st.session_state: st.session_state.main_search_input = ""
if "selected_verse_key" not in st.session_state: st.session_state.selected_verse_key = None

# دالة تُستدعى عند الكتابة في خانة البحث
def on_search_type():
    st.session_state.search_query = st.session_state.main_search_input
    st.session_state.selected_verse_key = None

# دالة تُستدعى عند الضغط على أي زر تتبعي (كلمة أو ورقة)
def force_search_update(new_word, verse_key=None):
    st.session_state.main_search_input = new_word
    st.session_state.search_query = new_word
    st.session_state.selected_verse_key = verse_key

# دالة تُستدعى عند اختيار آية لمعاينتها
def set_active_verse(v_key):
    st.session_state.selected_verse_key = v_key


# تحميل البيانات
df_quran = load_quran_data()
if df_quran is None:
    st.error("خطأ مادي: ملف البيانات غير موجود.")
    st.stop()

cols = df_quran.columns
surah_col = next((c for c in cols if c in ['السورة', 'surah']), cols[0])
verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number', 'الآية']), cols[1])
text_col = next((c for c in cols if c in ['نص الآية', 'text', 'الآية_نص']), cols[2])

# 5️⃣ بناء الواجهة الثابتة
col_input, col_papers, col_clear = st.columns([4, 1, 1])

with col_input:
    st.text_input(
        "المبحث الموحد:", 
        key="main_search_input", 
        on_change=on_search_type, 
        placeholder="أدخل اللفظ المراد تتبعه منطقياً...", 
        label_visibility="collapsed"
    )

with col_papers:
    with st.popover("📁 الأوراق"):
        saved_papers = load_papers()
        if saved_papers:
            for p_name, p_data in saved_papers.items():
                v_key = f"{p_data['surah']}_{p_data['verse']}"
                st.button(
                    f"📄 {p_name}", 
                    key=f"load_p_{p_name}", 
                    on_click=force_search_update, 
                    args=(p_data['query'], v_key)
                )
        else:
            st.text("المجلد خاوٍ.")

with col_clear:
    if st.button("🔄 تصفير"):
        force_search_update("")

# 6️⃣ السبورة السوداء المدمجة ماديّاً
st.markdown('<div class="blackboard-container">', unsafe_allow_html=True)

if st.session_state.search_query:
    q_norm = normalize_arabic(st.session_state.search_query)
    matched_rows = []
    
    for idx, row in df_quran.iterrows():
        t_norm = normalize_arabic(str(row[text_col]))
        if q_norm in t_norm:
            matched_rows.append({
                'surah': row[surah_col], 'verse': int(row[verse_col]), 
                'text': row[text_col], 'idx': idx
            })
            
    if not matched_rows:
        st.markdown("<p style='color:#666;'>لا توجد نتائج مطابقة.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"**المطابقات: ({len(matched_rows)})**")
        
        # الاعتماد على الحاويات الأصلية لـ Streamlit داخل تصميم السبورة لمنع تسرب النتائج
        col_list, col_view = st.columns([1, 1])
        
        with col_list:
            st.markdown("<p style='color:#888; font-size:13px;'>قائمة النتائج:</p>", unsafe_allow_html=True)
            for i, match in enumerate(matched_rows):
                v_key = f"{match['surah']}_{match['verse']}"
                active_mark = "🔹 " if st.session_state.selected_verse_key == v_key else ""
                btn_label = f"{active_mark}﴿ {match['text'][:40]}... ﴾ ({match['surah']}:{match['verse']})"
                
                st.button(
                    btn_label, 
                    key=f"v_btn_{i}_{v_key}", 
                    on_click=set_active_verse, 
                    args=(v_key,)
                )
                    
        with col_view:
            if st.session_state.selected_verse_key:
                target = next((m for m in matched_rows if f"{m['surah']}_{m['verse']}" == st.session_state.selected_verse_key), None)
                if target:
                    st.markdown("### 📄 المعاينة الهيكلية")
                    st.markdown(f"<div class='verse-preview'>{target['text']}</div>", unsafe_allow_html=True)
                    
                    st.markdown("### 🔗 السياق التدبري")
                    start_v = max(1, target['verse'] - 2)
                    end_v = target['verse'] + 2
                    
                    ctx_mask = (df_quran[surah_col] == target['surah']) & (df_quran[verse_col].astype(int).between(start_v, end_v))
                    context_verses = []
                    
                    for _, c_row in df_quran[ctx_mask].sort_values(verse_col).iterrows():
                        v_num = int(c_row[verse_col])
                        is_tgt = (v_num == target['verse'])
                        context_verses.append({'verse': v_num, 'text': c_row[text_col], 'is_center': is_tgt})
                        
                        cls = "context-verse context-verse-center" if is_tgt else "context-verse"
                        prefix = "⭐ " if is_tgt else ""
                        st.markdown(f"<div class='{cls}'>{prefix}[{v_num}] {c_row[text_col]}</div>", unsafe_allow_html=True)
                    
                    st.markdown("### 🔍 تتبع اللفظ أفقياً")
                    # عزل حروف الوقف تماماً
                    words = [w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم") for w in target['text'].split() if len(w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم")) > 1]
                    
                    word_cols = st.columns(len(words) if words else 1)
                    for w_idx, word in enumerate(words):
                        with word_cols[w_idx % len(word_cols)]:
                            # استخدام Callbacks هنا ينهي مشكلة تجميد الأزرار للأبد
                            st.button(
                                word, 
                                key=f"track_{w_idx}_{word}_{st.session_state.selected_verse_key}", 
                                on_click=force_search_update, 
                                args=(word,)
                            )
                                
                    st.write("---")
                    if st.button("💾 حفظ كـ ورقة مستقلة", use_container_width=True):
                        if save_paper(st.session_state.search_query, target['surah'], target['verse'], target['text'], context_verses):
                            st.success("✅ تم حفظ الورقة مادياً بنجاح")
            else:
                st.markdown("<div style='text-align:center; padding:50px; color:#444;'>اختر آية لعرض التفاصيل.</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
