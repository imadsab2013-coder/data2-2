import streamlit as st
import pandas as pd
import re
import os
import json
from datetime import datetime

# 1️⃣ الإعدادات البصرية والمادية
st.set_page_config(page_title="مجلس البينة V6", layout="wide", initial_sidebar_state="collapsed")

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
        padding: 10px;
        margin: 5px 0;
    }
    
    div.stButton > button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 0px !important;
        border: 1px solid #333333 !important;
        width: 100% !important;
        text-align: right !important;
        padding: 8px !important;
        font-weight: bold !important;
        font-size: 14px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis;
    }
    
    div.stButton > button:hover {
        border-color: #ffffff !important;
        background-color: #262626 !important;
    }
    
    .nav-box {
        background-color: #1a1a1a;
        padding: 10px;
        border: 1px dashed #555555;
        margin-bottom: 15px;
    }
    
    header, footer { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# 2️⃣ دوال التنظيف والتنقية ونحت النصوص
def clean_quran_text(text):
    if not isinstance(text, str): return ""
    return re.sub(r"[\u0610-\u0615\u064B-\u065E\u06D6-\u06ED\u200B-\u200D\uFEFF]", "", text).strip()

def clean_surah_names(name):
    if not isinstance(name, str): return ""
    name = clean_quran_text(name)
    name = re.sub(r"[^\u0621-\u064A\s0-9:]", "", name)
    return name.strip()

def normalize_arabic(text):
    text = clean_quran_text(text)
    text = re.sub(r"[إأآٱا]", "ا", text)
    text = re.sub(r"[ىي]", "ي", text)
    text = re.sub(r"[ةه]", "ه", text)
    return text

def truncate_from_keyword(text, keyword, max_chars=45):
    """يبدأ النص المعروض من الكلمة المفتاحية المطلوبة صعوداً لسهولة الفحص البصري"""
    norm_text = normalize_arabic(text)
    norm_key = normalize_arabic(keyword)
    
    pos = norm_text.find(norm_key)
    if pos != -1 and pos > 0:
        truncated = "..." + text[pos:]
    else:
        truncated = text
        
    if len(truncated) > max_chars:
        return truncated[:max_chars] + "..."
    return truncated

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

# 3️⃣ ميكانيكا حفظ المستندات والأوراق المالية
RESULTS_DIR = 'data/mfolder_results'
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_paper(query, title_suffix, text_content):
    sanitized = re.sub(r'[^\u0621-\u064A0-9]', '_', query).strip('_')
    filename = sorted(sanitized.split(), key=len)[-1] if sanitized.split() else "research"
    filepath = os.path.join(RESULTS_DIR, f"{filename}_{title_suffix}_{datetime.now().strftime('%H%M%S')}.json")
    
    data = {
        'query': query,
        'title': title_suffix,
        'main_content': text_content,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except: return False

# 4️⃣ إدارة حالة الذاكرة (Session State) للغوص اللانهائي
if "main_query" not in st.session_state: st.session_state.main_query = ""
if "selected_main_verse" not in st.session_state: st.session_state.selected_main_verse = None
# مصفوفة التتبع المتداخل: تحتوي على قواميس تحوي الكلمة المستهدفة والآية المختارة داخلياً
if "history" not in st.session_state: st.session_state.history = [] 

def reset_all():
    st.session_state.main_query = ""
    st.session_state.selected_main_verse = None
    st.session_state.history = []

def on_main_query_change():
    st.session_state.selected_main_verse = None
    st.session_state.history = []

def set_active_main_verse(v_key):
    st.session_state.selected_main_verse = v_key
    st.session_state.history = [] # تصفير الغوص الفرعي عند تغيير المبحث الأساسي

def dive_into_word(word):
    # إضافة مستوى غوص جديد إلى التاريخ
    st.session_state.history.append({
        "word": word,
        "selected_verse": None
    })

def set_sub_verse(v_key):
    if st.session_state.history:
        st.session_state.history[-1]["selected_verse"] = v_key

def go_back():
    if st.session_state.history:
        # إذا كانت الآية داخل المستوى الحالي مختارة، نلغي اختيار الآية أولاً
        if st.session_state.history[-1]["selected_verse"] is not None:
            st.session_state.history[-1]["selected_verse"] = None
        else:
            # وإلا نخرج من مستوى الكلمة بالكامل إلى المستوى الذي قبله
            st.session_state.history.pop()

# 5️⃣ تحميل قاعدة البيانات
df_quran = load_quran_data()
if df_quran is None:
    st.error("خطأ مادي: ملف البيانات غير موجود.")
    st.stop()

cols = df_quran.columns
surah_col = next((c for c in cols if c in ['السورة', 'surah']), cols[0])
verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number', 'الآية']), cols[1])
text_col = next((c for c in cols if c in ['نص الآية', 'text', 'الآية_نص']), cols[2])

df_quran[surah_col] = df_quran[surah_col].apply(clean_surah_names)

# 6️⃣ واجهة المستخدم والتحكم
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
        st.rerun()

# 7️⃣ السبورة السوداء التحليلية
st.markdown('<div class="blackboard-container">', unsafe_allow_html=True)

if st.session_state.main_query:
    mq_norm = normalize_arabic(st.session_state.main_query)
    main_matches = []
    
    for idx, row in df_quran.iterrows():
        t_norm = normalize_arabic(str(row[text_col]))
        if mq_norm in t_norm:
            main_matches.append({
                'surah': row[surah_col], 'verse': int(row[verse_col]), 
                'text': row[text_col], 'idx': idx
            })
            
    col_right_main, col_left_sub = st.columns([1, 1])
    
    # ---------------- الشق الأيمن: ناتج البحث الأول الكبير (ثابت ومقصوص مادياً) ----------------
    with col_right_main:
        st.markdown(f"### 🔍 نتائج المبحث الكبير: ({len(main_matches)})")
        
        if len(main_matches) > 0:
            if st.button("💾 حفظ المبحث الكبير كاملاً", key="save_main_large"):
                all_texts = [f"({m['surah']}:{m['verse']}) {m['text']}" for m in main_matches]
                if save_paper(st.session_state.main_query, "البحث_الكبير", "\n".join(all_texts)):
                    st.success("✅ تم حفظ نتائج المبحث الكبير")
        st.write("---")
        
        for i, match in enumerate(main_matches):
            v_key = f"{match['surah']}_{match['verse']}"
            active_mark = "🔹 " if st.session_state.selected_main_verse == v_key else ""
            
            # تطبيق تقنية البدء من الكلمة المطلوبة داخل أزرار المبحث الكبير
            display_text = truncate_from_keyword(match['text'], st.session_state.main_query)
            btn_label = f"{active_mark}﴿ {display_text} ﴾ ({match['surah']}:{match['verse']})"
            
            st.button(
                btn_label, 
                key=f"main_v_{i}_{v_key}", 
                on_click=set_active_main_verse, 
                args=(v_key,)
            )

    # ---------------- الشق الأيسر: نظام المعالجة والغوص المتداخل ----------------
    with col_left_sub:
        if not st.session_state.history:
            # المستوى الثاني: معاينة الآية المختارة وتفكيكها
            if st.session_state.selected_main_verse:
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
                        st.markdown(f"<div class='{cls}'>{'⭐ ' if is_tgt else ''}[{v_num}] {c_row[text_col]}</div>", unsafe_allow_html=True)
                    
                    st.markdown("### 🛠️ تفكيك الآية (اضغط على كلمة للغوص المتداخل)")
                    words = [w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم") for w in target['text'].split() if len(w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم")) > 1]
                    
                    cols_per_row = 4
                    for i in range(0, len(words), cols_per_row):
                        row_cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(words):
                                word = words[i + j]
                                with row_cols[j]:
                                    st.button(word, key=f"w_lvl2_{i+j}_{word}", on_click=dive_into_word, args=(word,))
            else:
                st.markdown("<div style='text-align:center; padding:100px; color:#444;'>اختر آية من المبحث الكبير لتفكيكها والغوص في مستوياتها.</div>", unsafe_allow_html=True)
        
        else:
            # تفعيل نظام الغوص اللانهائي (المستويات المتقدمة)
            current_level_idx = len(st.session_state.history)
            current_level = st.session_state.history[-1]
            active_word = current_level["word"]
            active_verse = current_level["selected_verse"]
            
            # شريط التتبع البصري للمستويات
            path_str = " ➔ ".join([h["word"] for h in st.session_state.history])
            st.markdown(f"<div class='nav-box'>🧬 مسار الغوص الحالي (مستوى {current_level_idx + 2}):<br><b>{path_str}</b></div>", unsafe_allow_html=True)
            
            if st.button("⬅️ العودة خطوة للخلف", key=f"back_btn_{current_level_idx}"):
                go_back()
                st.rerun()
                
            if not active_verse:
                # عرض الآيات المطابقة للكلمة المتتبعة في هذا المستوى
                sub_q_norm = normalize_arabic(active_word)
                sub_matches = []
                for idx, row in df_quran.iterrows():
                    if sub_q_norm in normalize_arabic(str(row[text_col])):
                        sub_matches.append({'surah': row[surah_col], 'verse': int(row[verse_col]), 'text': row[text_col]})
                
                st.markdown(f"🎯 **مطابقات اللفظ [ {active_word} ]: ({len(sub_matches)})**")
                
                if st.button(f"💾 حفظ أوراق اللفظ [{active_word}]", key=f"save_sub_{current_level_idx}"):
                    sub_texts = [f"({sm['surah']}:{sm['verse']}) {sm['text']}" for sm in sub_matches]
                    if save_paper(active_word, f"غوص_مستوى_{current_level_idx}", "\n".join(sub_texts)):
                        st.success("✅ تم حفظ الورقة الحالية")
                st.write("---")
                
                for idx, sm in enumerate(sub_matches):
                    v_sub_key = f"{sm['surah']}_{sm['verse']}"
                    # عرض النص مقصوصاً بدءاً من الكلمة المتتبعة لسهولة القراءة والفرز
                    sub_display_text = truncate_from_keyword(sm['text'], active_word)
                    st.button(
                        f"﴿ {sub_display_text} ﴾ [{sm['surah']}:{sm['verse']}]", 
                        key=f"sub_v_btn_{current_level_idx}_{idx}_{v_sub_key}",
                        on_click=set_sub_verse,
                        args=(v_sub_key,)
                    )
            else:
                # تم اختيار آية معينة داخل هذا المستوى الفرعي -> نعرض سياقها وتفكيك كلماتها للغوص أعمق
                surah_name, v_num_str = active_verse.split('_')
                v_num = int(v_num_str)
                
                # جلب نص الآية الفرعية المختارة
                v_row = df_quran[(df_quran[surah_col] == surah_name) & (df_quran[verse_col].astype(int) == v_num)]
                if not v_row.empty:
                    v_text = v_row.iloc[0][text_col]
                    
                    st.markdown("### 📄 المعاينة الهيكلية للآية الفرعية")
                    st.markdown(f"<div class='verse-preview'>{v_text}</div>", unsafe_allow_html=True)
                    
                    st.markdown("### 🔗 السياق التدبري للآية الفرعية")
                    start_v = max(1, v_num - 2)
                    end_v = v_num + 2
                    ctx_mask = (df_quran[surah_col] == surah_name) & (df_quran[verse_col].astype(int).between(start_v, end_v))
                    
                    for _, c_row in df_quran[ctx_mask].sort_values(verse_col).iterrows():
                        cv_num = int(c_row[verse_col])
                        is_tgt = (cv_num == v_num)
                        cls = "context-verse context-verse-center" if is_tgt else "context-verse"
                        st.markdown(f"<div class='{cls}'>{'⭐ ' if is_tgt else ''}[{cv_num}] {c_row[text_col]}</div>", unsafe_allow_html=True)
                    
                    st.markdown("### 🛠️ تفكيك الآية الفرعية (اضغط للغوص إلى مستوى أعمق)")
                    sub_words = [w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم") for w in v_text.split() if len(w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم")) > 1]
                    
                    cols_per_row = 4
                    for i in range(0, len(sub_words), cols_per_row):
                        row_cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(sub_words):
                                sw = sub_words[i + j]
                                with row_cols[j]:
                                    st.button(sw, key=f"w_dive_{current_level_idx}_{i+j}_{sw}", on_click=dive_into_word, args=(sw,))

st.markdown('</div>', unsafe_allow_html=True)
