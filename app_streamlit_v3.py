import streamlit as st
import pandas as pd
import re
import os
import json
from datetime import datetime

# 1️⃣ الإعدادات البصرية وقوالب التصميم المادي
st.set_page_config(page_title="مجلس البينة V7", layout="wide", initial_sidebar_state="collapsed")

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
    
    /* بطاقات آيات البحث المطور - تدعم سطرين وتبرز الكلمة */
    .verse-card {
        background: #0f0f0f;
        border: 1px solid #222222;
        border-right: 4px solid #ffcc00;
        padding: 12px;
        margin-top: 12px;
        margin-bottom: 2px;
        font-size: 15px;
        line-height: 1.6;
        color: #ffffff;
    }
    
    .verse-card-header {
        font-size: 12px;
        color: #888888;
        margin-bottom: 5px;
        display: block;
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
    
    /* أزرار تفكيك الكلمات الفرعية */
    div.word-grid button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 0px !important;
        border: 1px solid #333333 !important;
        width: 100% !important;
        text-align: center !important;
        padding: 6px !important;
        font-size: 14px !important;
    }
    div.word-grid button:hover {
        border-color: #ffffff !important;
        background-color: #262626 !important;
    }
    
    /* أزرار الاختيار المرافقة للبطاقات */
    div.select-action button {
        background-color: #1a1a1a !important;
        color: #ffcc00 !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
        font-size: 12px !important;
        padding: 2px 12px !important;
        width: auto !important;
        margin-bottom: 12px !important;
    }
    div.select-action button:hover {
        background-color: #ffcc00 !important;
        color: #000000 !important;
    }
    
    .nav-box {
        background-color: #111111;
        padding: 10px;
        border: 1px dashed #444444;
        margin-bottom: 15px;
        font-size: 13px;
    }
    
    header, footer { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# 2️⃣ دوال التطهير والنحت البصري للنصوص
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

def get_highlighted_snippet(text, keyword, max_chars=130):
    """صياغة بطاقة بيانية تمتد لسطرين تبدأ من موقع الكلمة المفتاحية وتلونها بصرياً"""
    norm_text = normalize_arabic(text)
    norm_key = normalize_arabic(keyword)
    pos = norm_text.find(norm_key)
    
    if pos == -1:
        snippet = text[:max_chars] + "..." if len(text) > max_chars else text
        return f"﴿ {snippet} ﴾"
        
    start_pos = max(0, pos - 15)
    if start_pos > 0:
        space_pos = text.find(' ', start_pos, pos)
        if space_pos != -1: start_pos = space_pos + 1
        
    prefix = "..." if start_pos > 0 else ""
    end_pos = start_pos + max_chars
    suffix = "..." if len(text) > end_pos else ""
    
    snippet = text[start_pos:end_pos]
    norm_snippet = normalize_arabic(snippet)
    k_pos = norm_snippet.find(norm_key)
    
    if k_pos != -1:
        k_len = len(keyword)
        actual_word = snippet[k_pos:k_pos+k_len]
        highlighted = snippet[:k_pos] + f"<span style='color:#ffcc00; font-weight:bold; border-bottom:1px solid #ffcc00;'>{actual_word}</span>" + snippet[k_pos+k_len:]
        return f"{prefix}﴿ {highlighted} ﴾{suffix}"
        
    return f"{prefix}﴿ {snippet} ﴾{suffix}"

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

# 3️⃣ أرشفة الأوراق المالية والنتائج
RESULTS_DIR = 'data/mfolder_results'
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_paper(query, title_suffix, text_content):
    sanitized = re.sub(r'[^\u0621-\u064A0-9]', '_', query).strip('_')
    filename = sorted(sanitized.split(), key=len)[-1] if sanitized.split() else "research"
    filepath = os.path.join(RESULTS_DIR, f"{filename}_{title_suffix}_{datetime.now().strftime('%H%M%S')}.json")
    
    data = {'query': query, 'title': title_suffix, 'main_content': text_content, 'timestamp': datetime.now().isoformat()}
    try:
        with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except: return False

# 4️⃣ إدارة هندسة الجلسة والذاكرة العميقة
if "main_query" not in st.session_state: st.session_state.main_query = ""
if "selected_main_verse" not in st.session_state: st.session_state.selected_main_verse = None
if "history" not in st.session_state: st.session_state.history = []

def reset_all():
    st.session_state.main_query = ""
    st.session_state.selected_main_verse = None
    st.session_state.history = []

def dive_into_word(word):
    st.session_state.history.append({"word": word, "selected_verse": None})

def set_sub_verse(v_key):
    if st.session_state.history:
        st.session_state.history[-1]["selected_verse"] = v_key

def go_back():
    if st.session_state.history:
        if st.session_state.history[-1]["selected_verse"] is not None:
            st.session_state.history[-1]["selected_verse"] = None
        else:
            st.session_state.history.pop()

# 5️⃣ استدعاء البيانات وتطهير السور لمنع المربعات
df_quran = load_quran_data()
if df_quran is None:
    st.error("خطأ مادي: ملف البيانات غير موجود.")
    st.stop()

cols = df_quran.columns
surah_col = next((c for c in cols if c in ['السورة', 'surah']), cols[0])
verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number', 'الآية']), cols[1])
text_col = next((c for c in cols if c in ['نص الآية', 'text', 'الآية_نص']), cols[2])

df_quran[surah_col] = df_quran[surah_col].apply(clean_surah_names)

# 6️⃣ صياغة الاستمارات (المستوى الأول الشاشات النظيفة)
with st.form(key="search_form_panel", clear_on_submit=False):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        search_input = st.text_input(
            "المبحث الرئيسي الكبير:",
            value="",
            placeholder="أدخل لفظ المبحث الأول الكبير هنا (الشريط يبدأ فارغاً)...",
            label_visibility="collapsed"
        )
    with col_btn:
        submit_search = st.form_submit_button("🔍 إطلاق البحث")

if submit_search and search_input:
    st.session_state.main_query = search_input
    st.session_state.selected_main_verse = None
    st.session_state.history = []
    st.rerun()

# زر تصفير الشاشة المستقل خارج الاستمارة
if st.session_state.main_query:
    if st.button("🔄 تصفير شاشة المعالجة"):
        reset_all()
        st.rerun()

# 7️⃣ تشغيل المطبخ التحليلي المشترك
st.markdown('<div class="blackboard-container">', unsafe_allow_html=True)

if st.session_state.main_query:
    mq_norm = normalize_arabic(st.session_state.main_query)
    main_matches = []
    
    for idx, row in df_quran.iterrows():
        if mq_norm in normalize_arabic(str(row[text_col])):
            main_matches.append({'surah': row[surah_col], 'verse': int(row[verse_col]), 'text': row[text_col], 'idx': idx})
            
    col_right_main, col_left_sub = st.columns([1, 1])
    
    # ---------------- 📑 الشق الأيمن: ناتج البحث الأول الكبير (المستوى الأول ثابت ملوّن وممتد) ----------------
    with col_right_main:
        st.markdown(f"### 🔍 نتائج المبحث الكبير: ({len(main_matches)})")
        
        if len(main_matches) > 0:
            if st.button("💾 حفظ نتائج المبحث الكبير", key="save_main_large"):
                all_texts = [f"({m['surah']}:{m['verse']}) {m['text']}" for m in main_matches]
                if save_paper(st.session_state.main_query, "البحث_الكبير", "\n".join(all_texts)):
                    st.success("✅ تم الحفظ")
        st.write("---")
        
        for i, match in enumerate(main_matches):
            v_key = f"{match['surah']}_{match['verse']}"
            is_active = (st.session_state.selected_main_verse == v_key)
            
            # صياغة بطاقة البيان الممتدة لسطرين مع التلوين
            html_snippet = get_highlighted_snippet(match['text'], st.session_state.main_query)
            active_border = "border-right: 4px solid #00ffcc;" if is_active else ""
            
            st.markdown(f"""
                <div class="verse-card" style="{active_border}">
                    <span class="verse-card-header"> سورة {match['surah']} | الآية: {match['verse']} {"(مختارة حالياً) 🔹" if is_active else ""}</span>
                    {html_snippet}
                </div>
            """, unsafe_allow_html=True)
            
            # زر مالي أسفل البطاقة للاختيار والتفكيك
            with st.container():
                st.markdown('<div class="select-action">', unsafe_allow_html=True)
                if st.button(f"🎯 تحليل الآية [{match['surah']}:{match['verse']}]", key=f"btn_m_{i}_{v_key}"):
                    st.session_state.selected_main_verse = v_key
                    st.session_state.history = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- 🧬 الشق الأيسر: هندسة الغوص التكراري اللانهائي (المستويات المتداخلة) ----------------
    with col_left_sub:
        if not st.session_state.history:
            # المستوى الثاني: معاينة وسياق وتفكيك الآية الكبرى المختارة
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
                    
                    st.markdown("### 🛠️ تفكيك الآية (اضغط على كلمة للغوص المتداخل - مستوى 3)")
                    words = [w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم") for w in target['text'].split() if len(w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم")) > 1]
                    
                    st.markdown('<div class="word-grid">', unsafe_allow_html=True)
                    cols_per_row = 4
                    for i in range(0, len(words), cols_per_row):
                        row_cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(words):
                                word = words[i + j]
                                with row_cols[j]:
                                    st.button(word, key=f"w_lvl2_{i+j}_{word}", on_click=dive_into_word, args=(word,))
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align:center; padding:100px; color:#444;'>اختر آية من المبحث الكبير لتفكيكها والغوص في مستوياتها التكرارية.</div>", unsafe_allow_html=True)
        
        else:
            # تفعيل خوارزمية الغوص التكراري (المستويات 3، 5، 7... إلخ) الملونة والممتدة لسطرين
            current_level_idx = len(st.session_state.history)
            current_level = st.session_state.history[-1]
            active_word = current_level["word"]
            active_verse = current_level["selected_verse"]
            
            path_str = " ➔ ".join([h["word"] for h in st.session_state.history])
            st.markdown(f"<div class='nav-box'>🧬 مسار الغوص الحالي (المستوى التحليلي {current_level_idx + 2}):<br><b>{path_str}</b></div>", unsafe_allow_html=True)
            
            if st.button("⬅️ العودة خطوة للخلف", key=f"back_btn_{current_level_idx}"):
                go_back()
                st.rerun()
                
            if not active_verse:
                # عرض الآيات المطابقة للكلمة المتتبعة في هذا المستوى (تطبيق السطرين والتلوين المطور)
                sub_q_norm = normalize_arabic(active_word)
                sub_matches = []
                for idx, row in df_quran.iterrows():
                    if sub_q_norm in normalize_arabic(str(row[text_col])):
                        sub_matches.append({'surah': row[surah_col], 'verse': int(row[verse_col]), 'text': row[text_col]})
                
                st.markdown(f"🎯 **مطابقات اللفظ المتتبع [ {active_word} ]: ({len(sub_matches)})**")
                st.write("---")
                
                for idx, sm in enumerate(sub_matches):
                    v_sub_key = f"{sm['surah']}_{sm['verse']}"
                    
                    # صياغة البطاقة الفرعية الممتدة والملونة للكلمة الفرعية المتتبعة
                    html_snippet_sub = get_highlighted_snippet(sm['text'], active_word)
                    st.markdown(f"""
                        <div class="verse-card">
                            <span class="verse-card-header"> سورة {sm['surah']} | الآية: {sm['verse']}</span>
                            {html_snippet_sub}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.container():
                        st.markdown('<div class="select-action">', unsafe_allow_html=True)
                        st.button(f"🎯 الانتقال لتفكيك آية [{sm['surah']}:{sm['verse']}]", key=f"sub_v_btn_{current_level_idx}_{idx}_{v_sub_key}", on_click=set_sub_verse, args=(v_sub_key,))
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                # تفعيل تفكيك آية فرعية داخل مستوى متقدم للغوص أعمق (مستويات 4، 6، 8)
                surah_name, v_num_str = active_verse.split('_')
                v_num = int(v_num_str)
                
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
                    
                    st.markdown('<div class="word-grid">', unsafe_allow_html=True)
                    cols_per_row = 4
                    for i in range(0, len(sub_words), cols_per_row):
                        row_cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(sub_words):
                                sw = sub_words[i + j]
                                with row_cols[j]:
                                    st.button(sw, key=f"w_dive_{current_level_idx}_{i+j}_{sw}", on_click=dive_into_word, args=(sw,))
                    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
