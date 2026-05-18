import streamlit as st
import pandas as pd
import re
import os
import json
from datetime import datetime

# 1️⃣ الإعدادات البصرية والمادية
st.set_page_config(page_title="مجلس البينة V5", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    html, body, [data-testid="stAppViewContainer"] { background: #000000 !important; color: #ffffff !important; }
    
    .blackboard-container {
        background: #000000;
        border: 1px solid #333333;
        padding: 20px;
        margin-top: 10px;
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
    
    /* أزرار مصفوفة الكلمات - منع التكسير العمودي */
    div.stButton > button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 0px !important;
        border: 1px solid #333333 !important;
        width: 100% !important;
        text-align: center !important;
        padding: 8px !important;
        font-weight: bold !important;
        font-size: 14px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
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

# 2️⃣ دوال التنظيف والتطهير المادي لمنع المربعات
def clean_quran_text(text):
    if not isinstance(text, str): return ""
    # إزالة علامات التشكيل والضبط العثماني والرموز الخاصة
    return re.sub(r"[\u0610-\u0615\u064B-\u065E\u06D6-\u06ED\u200B-\u200D\uFEFF]", "", text).strip()

def clean_surah_names(name):
    if not isinstance(name, str): return ""
    name = clean_quran_text(name)
    # تنظيف مخصص للرموز المسببة للمربعات في أسماء السور الشائعة
    name = re.sub(r"[^\u0621-\u064A\s0-9:]", "", name)
    return name.strip()

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

# 3️⃣ ميكانيكا حفظ الأوراق المستقلة
RESULTS_DIR = 'data/mfolder_results'
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_paper(query, title_suffix, text_content, extra_data=None):
    sanitized = re.sub(r'[^\u0621-\u064A0-9]', '_', query).strip('_')
    filename = sorted(sanitized.split(), key=len)[-1] if sanitized.split() else "research"
    filepath = os.path.join(RESULTS_DIR, f"{filename}_{title_suffix}_{datetime.now().strftime('%H%M%S')}.json")
    
    data = {
        'query': query,
        'title': title_suffix,
        'main_content': text_content,
        'extra': extra_data,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except: return False

# 4️⃣ إدارة حالة الذاكرة (Session State) الموحدة
if "main_query" not in st.session_state: st.session_state.main_query = ""
if "selected_main_verse" not in st.session_state: st.session_state.selected_main_verse = None
if "tracked_word" not in st.session_state: st.session_state.tracked_word = None

def reset_all():
    st.session_state.main_query = ""
    st.session_state.selected_main_verse = None
    st.session_state.tracked_word = None

def on_main_query_change():
    st.session_state.selected_main_verse = None
    st.session_state.tracked_word = None

def set_active_main_verse(v_key):
    st.session_state.selected_main_verse = v_key
    st.session_state.tracked_word = None # تصفير التتبع الفرعي عند تغيير الآية المختارة

def set_tracked_word(word):
    st.session_state.tracked_word = word

# 5️⃣ تحميل قاعدة البيانات الإحصائية
df_quran = load_quran_data()
if df_quran is None:
    st.error("خطأ مادي: ملف البيانات غير موجود.")
    st.stop()

cols = df_quran.columns
surah_col = next((c for c in cols if c in ['السورة', 'surah']), cols[0])
verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number', 'الآية']), cols[1])
text_col = next((c for c in cols if c in ['نص الآية', 'text', 'الآية_نص']), cols[2])

# تطبيق التطهير الفوري لأسماء السور لتفادي المربعات بالكامل
df_quran[surah_col] = df_quran[surah_col].apply(clean_surah_names)

# 6️⃣ شريط التحكم العلوي
col_input, col_clear = st.columns([5, 1])

with col_input:
    st.text_input(
        "المبحث الرئيسي الكبير:", 
        key="main_query", 
        on_change=on_main_query_change, 
        placeholder="أدخل مبحث البحث الأول الكبير هنا...", 
        label_visibility="collapsed"
    )
with col_clear:
    if st.button("🔄 تصفير الشاشة"):
        reset_all()

# 7️⃣ السبورة السوداء التحليلية
st.markdown('<div class="blackboard-container">', unsafe_allow_html=True)

if st.session_state.main_query:
    # معالجة مطابقات البحث الأول الكبير
    mq_norm = normalize_arabic(st.session_state.main_query)
    main_matches = []
    
    for idx, row in df_quran.iterrows():
        t_norm = normalize_arabic(str(row[text_col]))
        if mq_norm in t_norm:
            main_matches.append({
                'surah': row[surah_col], 'verse': int(row[verse_col]), 
                'text': row[text_col], 'idx': idx
            })
            
    # تقسيم الشاشة إلى شقين مستقلين هندسياً
    col_right_main, col_left_sub = st.columns([1, 1])
    
    # ---------------- الشق الأيمن: البحث الرئيسي الكبير وثابت دائماً ----------------
    with col_right_main:
        st.markdown(f"### 🔍 نتائج المبحث الكبير: ({len(main_matches)})")
        
        # أرشفة وحفظ المبحث الكبير كاملاً
        if len(main_matches) > 0:
            if st.button("💾 حفظ المبحث الكبير كاملاً", key="save_main_large"):
                all_texts = [f"({m['surah']}:{m['verse']}) {m['text']}" for m in main_matches]
                if save_paper(st.session_state.main_query, "البحث_الكبير", "\n".join(all_texts)):
                    st.success("✅ تم حفظ نتائج المبحث الكبير")
        
        st.write("---")
        
        # قائمة آيات المبحث الكبير
        for i, match in enumerate(main_matches):
            v_key = f"{match['surah']}_{match['verse']}"
            active_mark = "🔹 " if st.session_state.selected_main_verse == v_key else ""
            btn_label = f"{active_mark}﴿ {match['text'][:35]}... ﴾ ({match['surah']}:{match['verse']})"
            
            st.button(
                btn_label, 
                key=f"main_v_{i}_{v_key}", 
                on_click=set_active_main_verse, 
                args=(v_key,)
            )

    # ---------------- الشق الأيسر: يتغير بالكامل عند تفكيك الكلمات وتتبعها ----------------
    with col_left_sub:
        if st.session_state.selected_main_verse and not st.session_state.tracked_word:
            # تظهر الآية المختارة وسياقها وتفكيكها في البداية
            target = next((m for m in main_matches if f"{m['surah']}_{m['verse']}" == st.session_state.selected_main_verse), None)
            if target:
                st.markdown("### 📄 المعاينة الهيكلية للآية")
                st.markdown(f"<div class='verse-preview'>{target['text']}</div>", unsafe_allow_html=True)
                
                st.markdown("### 🔗 السياق التدبري")
                start_v = max(1, target['verse'] - 2)
                end_v = target['verse'] + 2
                ctx_mask = (df_quran[surah_col] == target['surah']) & (df_quran[verse_col].astype(int).between(start_v, end_v))
                
                for _, c_row in df_quran[ctx_mask].sort_values(verse_col).iterrows():
                    v_num = int(c_row[verse_col])
                    is_tgt = (v_num == target['verse'])
                    cls = "context-verse context-verse-center" if is_tgt else "context-verse"
                    prefix = "⭐ " if is_tgt else ""
                    st.markdown(f"<div class='{cls}'>{prefix}[{v_num}] {c_row[text_col]}</div>", unsafe_allow_html=True)
                
                st.markdown("### 🛠️ تفكيك الآية (اضغط على كلمة لتتبعها وإحلالها هنا)")
                words = [w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم") for w in target['text'].split() if len(w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم")) > 1]
                
                cols_per_row = 4
                for i in range(0, len(words), cols_per_row):
                    row_cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        if i + j < len(words):
                            word = words[i + j]
                            with row_cols[j]:
                                st.button(word, key=f"word_clk_{i+j}_{word}", on_click=set_tracked_word, args=(word,))
                                
        elif st.session_state.tracked_word:
            # إحلال كامل وتدمير محتوى المعاينة ليعوضه ناتج اللفظ المضغوط
            st.markdown(f"### 🎯 تتبع اللفظ: [ {st.session_state.tracked_word} ]")
            
            sub_q_norm = normalize_arabic(st.session_state.tracked_word)
            sub_matches = []
            
            for idx, row in df_quran.iterrows():
                t_norm = normalize_arabic(str(row[text_col]))
                if sub_q_norm in t_norm:
                    sub_matches.append({
                        'surah': row[surah_col], 'verse': int(row[verse_col]), 'text': row[text_col]
                    })
            
            st.markdown(f"**عدد نتائج اللفظ الفرعي المتتبع: ({len(sub_matches)})**")
            
            # زر حفظ مستقل للفظ المتتبع
            if st.button("💾 حفظ ورقة اللفظ المتتبع الحالية", use_container_width=True):
                sub_texts = [f"({sm['surah']}:{sm['verse']}) {sm['text']}" for sm in sub_matches]
                if save_paper(st.session_state.tracked_word, "تتبع_لفظ", "\n".join(sub_texts)):
                    st.success(f"✅ تم حفظ ورقة تتبع اللفظ [{st.session_state.tracked_word}]")
                    
            if st.button("⬅️ العودة لمعاينة الآية وتفكيكها", use_container_width=True):
                st.session_state.tracked_word = None
                st.rerun()
                
            st.write("---")
            
            # عرض مطابقات اللفظ المتتبع الجديد وسياقها مباشرة
            for idx, sm in enumerate(sub_matches):
                st.markdown(f"<div class='context-verse-center'>﴿ {sm['text']} ﴾ <span style='color:#aaa; font-size:12px;'>[{sm['surah']}:{sm['verse']}]</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:100px; color:#444;'>اختر آية من المبحث الكبير لعرض تفاصيلها وتتبع ألفاظها هندسياً.</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
