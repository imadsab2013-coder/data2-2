import streamlit as st
import pandas as pd
import re
import os
import json
from datetime import datetime

# 1️⃣ الإعدادات والاضطلاع بالهوية البصرية العريضة (ألوان ثلاثية فقط)
st.set_page_config(page_title="مجلس البينة V4", layout="wide", initial_sidebar_state="collapsed")

# التصميم النقي - ألوان ثلاثية فقط وحبس المخرجات داخل السبورة
st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #000000 !important;
        color: #ffffff !important;
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stVerticalBlockBG"] {
        background: #000000 !important;
        padding: 0;
    }
    
    .search-header {
        background: #1a1a1a;
        border-bottom: 1px solid #333333;
        padding: 15px;
        margin: 0;
        position: sticky;
        top: 0;
        z-index: 100;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    
    /* وعاء السبورة السوداء الحاصر للنتائج */
    .blackboard {
        background: #000000;
        border: 1px solid #333333;
        border-radius: 0;
        padding: 20px;
        margin: 20px;
        min-height: 400px;
    }
    
    .verse-preview {
        background: #1a1a1a;
        border-right: 2px solid #555555;
        padding: 18px;
        border-radius: 0;
        font-size: 16px;
        line-height: 2;
        margin: 15px 0;
        color: #ffffff;
    }
    
    .context-verse {
        background: #1a1a1a;
        border-right: 2px solid #333333;
        padding: 12px;
        margin: 8px 0;
        border-radius: 0;
        font-size: 14px;
        line-height: 1.8;
        color: #ffffff;
    }
    
    .context-verse-center {
        border-right: 2px solid #ffffff;
        background: #222222;
        font-weight: bold;
    }
    
    /* ضبط ميكانيكا أزرار السبورة لتكون مستقرة وعريضة */
    div.stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        font-weight: normal !important;
        border-radius: 0 !important;
        border: 1px solid #333333 !important;
        padding: 12px !important;
        width: 100% !important;
        text-align: right !important;
        font-size: 14px !important;
    }
    
    div.stButton > button:hover {
        background-color: #262626 !important;
        border-color: #ffffff !important;
    }
    
    /* مدخلات البحث */
    div[data-testid="stTextInput"] input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
    }
    
    /* النوافذ العائمة ومربعات الحوار المحمية */
    div[data-testid="stPopoverWindow"] {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
    }
    
    .empty-state {
        text-align: center;
        padding: 50px 20px;
        color: #666666;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stSidebarCollapsedControl"] { display: none !important; }
    footer { display: none !important; }
    header { visibility: hidden !important; }
    
    </style>
""", unsafe_allow_html=True)

# 2️⃣ معالجة النصوص والدوال الميكانيكية للبيانات
def normalize_arabic(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\u064B-\u0652]", "", text)
    text = re.sub(r"[إأآٱا]", "ا", text)
    text = re.sub(r"[ىي]", "ي", text)
    text = re.sub(r"[ةه]", "ه", text)
    return text.strip()

@st.cache_data
def load_quran_data():
    for path in ["data/data_quran.xlsx", "data_quran.xlsx"]:
        if os.path.exists(path):
            try:
                return pd.read_excel(path)
            except:
                return None
    return None

def identify_columns(df):
    cols = df.columns
    surah_col = next((c for c in cols if c in ['السورة', 'surah']), None)
    verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number']), None)
    text_col = next((c for c in cols if c in ['نص الآية', 'text']), None)
    return surah_col, verse_col, text_col

def search_unified(df, query):
    query_norm = normalize_arabic(query)
    if not query_norm:
        return []
    
    results = []
    surah_col, verse_col, text_col = identify_columns(df)
    
    for idx, row in df.iterrows():
        text_norm = normalize_arabic(str(row[text_col]))
        if query_norm in text_norm:
            results.append({
                'surah': row[surah_col],
                'verse': int(row[verse_col]),
                'text': row[text_col],
                'idx': idx
            })
    
    seen = set()
    unique = []
    for r in results:
        key = (r['surah'], r['verse'])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    
    return unique

def get_context(df, surah, verse, before, after):
    surah_col, verse_col, text_col = identify_columns(df)
    start = max(1, verse - before)
    end = verse + after
    
    mask = (
        (df[surah_col] == surah) &
        (df[verse_col].astype(int).between(start, end))
    )
    
    context = []
    for _, row in df[mask].sort_values(verse_col).iterrows():
        v_num = int(row[verse_col])
        context.append({
            'verse': v_num,
            'text': row[text_col],
            'is_center': (v_num == verse)
        })
    return context

# 3️⃣ إدارة الأوراق المستقلة والمجلد المادي
RESULTS_DIR = 'data/mfolder_results'
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_paper(query, surah, verse, text, context_verses):
    sanitized = re.sub(r'[^\u0621-\u064A0-9]', '_', query).strip('_')
    # إذا كان البحث طويلاً، نشتق الاسم من الكلمة الأكبر، وإلا نعتمد رقم السورة والآية كمحدد مادي ثابت
    filename = sorted(sanitized.split(), key=len)[-1] if sanitized.split() else f"{surah}_{verse}"
    filepath = os.path.join(RESULTS_DIR, f"{filename}_{surah}_{verse}.json")
    
    data = {
        'query': query,
        'surah': surah,
        'verse': verse,
        'text': text,
        'context': context_verses,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_papers():
    if not os.path.exists(RESULTS_DIR):
        return {}
    
    papers = {}
    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(RESULTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    papers[filename[:-5]] = json.load(f)
            except:
                pass
    return papers

# 4️⃣ تهيئة وتأمين الذاكرة المستمرة للجلسة لضمان استقرار حركة البيانات ومنع الارتداد
if 'main_search' not in st.session_state:
    st.session_state.main_search = ""
if 'active_verse_idx' not in st.session_state:
    st.session_state.active_verse_idx = None
if 'verses_before' not in st.session_state:
    st.session_state.verses_before = 2
if 'verses_after' not in st.session_state:
    st.session_state.verses_after = 2

# تحميل قاعدة البيانات ماديّاً
df_quran = load_quran_data()
if df_quran is None:
    st.text("خطأ مادي: ملف قاعدة البيانات غير موجود")
    st.stop()

# 5️⃣ بناء لوحة التحكم العلوية والمحافظة على المساحة
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_left:
    with st.popover("⚙️"):
        st.markdown("**المعايير**")
        st.session_state.verses_before = st.number_input("قبل:", 1, 20, st.session_state.verses_before)
        st.session_state.verses_after = st.number_input("بعد:", 1, 20, st.session_state.verses_after)

with col_center:
    # استخدام الـ key المباشر يربط الحقل بالذاكرة فوراً ويمنع تجميد البحث عند الـ Rerun
    st.text_input("🔍", key="main_search", placeholder="ابحث عن لفظ أو شطر آية...", label_visibility="collapsed")

with col_right:
    with st.popover("💾"):
        st.markdown("**الأوراق المستقلة**")
        papers = load_papers()
        if papers:
            for paper_name, paper_data in papers.items():
                if st.button(f"📄 {paper_name}", use_container_width=True, key=f"p_load_{paper_name}"):
                    st.session_state.main_search = paper_data['query']
                    st.session_state.active_verse_idx = f"{paper_data['surah']}_{paper_data['verse']}"
                    st.rerun()
        else:
            st.text("المجلد خاوٍ ماديّاً.")

st.divider()

# 6️⃣ لسان وعاء السبورة السوداء الشاملة (حبس النتائج بالكامل في الوعاء)
st.markdown('<div class="blackboard">', unsafe_allow_html=True)

current_search = st.session_state.main_search

if current_search:
    results = search_unified(df_quran, current_search)
    
    if not results:
        st.markdown('<div class="empty-state"><p>السبورة لا تحتوي على نتائج مطابقة.</p></div>', unsafe_allow_html=True)
    else:
        # أولاً: طباعة قائمة أسطر الآيات المطابقة داخل الوعاء
        for idx, result in enumerate(results):
            v_key = f"{result['surah']}_{result['verse']}"
            label = f"﴿ {result['text'][:50]}... ﴾ ─── ({result['surah']}: {result['verse']})"
            
            if st.button(label, key=f"res_btn_{idx}", use_container_width=True):
                st.session_state.active_verse_idx = v_key
                st.rerun()
        
        # ثانياً: تفكيك وعرض المعاينة والسياق والحفظ للآية النشطة المستقرة في الجلسة
        if st.session_state.active_verse_idx:
            matched_target = next((r for r in results if f"{r['surah']}_{r['verse']}" == st.session_state.active_verse_idx), None)
            
            if matched_target:
                st.write("---")
                st.markdown("### 📄 المعاينة الهيكلية للآية")
                st.markdown(f"<div class='verse-preview'>{matched_target['text']}</div>", unsafe_allow_html=True)
                
                # جلب مصفوفة السياق المتسلسل بناءً على المعايير
                context_verses = get_context(
                    df_quran,
                    matched_target['surah'],
                    matched_target['verse'],
                    st.session_state.verses_before,
                    st.session_state.verses_after
                )
                
                st.markdown("### 🔗 السياق التدبري المرتبط")
                for ctx in context_verses:
                    if ctx['is_center']:
                        st.markdown(f"<div class='context-verse context-verse-center'>⭐ [{ctx['verse']}] {ctx['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='context-verse'>[{ctx['verse']}] {ctx['text']}</div>", unsafe_allow_html=True)
                
                # تفكيك الألفاظ أفقيّاً وتنظيفها من حروف الوقف المشوهة وعزل الحروف القصيرة أقل من حرفين
                st.markdown("### 🔍 تتبع اللفظ أفقياً (البحث المستمر)")
                raw_words = matched_target['text'].split()
                clean_words = [w.strip("ۖۗقليجۘم") for w in raw_words if len(w.strip("ۖۗقليجۘم")) > 1]
                
                word_cols = st.columns(len(clean_words) if len(clean_words) > 0 else 1)
                for i, word in enumerate(clean_words):
                    with word_cols[i % len(word_cols)]:
                        if st.button(word, key=f"wd_lnk_{i}_{word}", use_container_width=True):
                            # إحلال وتحديث البحث الرئيسي باللفظ الجديد مباشرة وتصفير المعاينة لبدء مستوى تتبع مستقر
                            st.session_state.main_search = word
                            st.session_state.active_verse_idx = None
                            st.rerun()
                
                # آلية تشغيل زر حفظ الأوراق المستقلة خارج الحلقات التكرارية التدميرية
                st.write("---")
                if st.button("💾 حفظ هذه المعاينة كـ ورقة مستقلة", use_container_width=True, key="save_action_btn"):
                    success = save_paper(
                        current_search, 
                        matched_target['surah'], 
                        matched_target['verse'], 
                        matched_target['text'], 
                        context_verses
                    )
                    if success:
                        st.toast("تم تسجيل الورقة ماديّاً في المجلد")
else:
    st.markdown('<div class="empty-state"><p>السبورة بانتظار إدخال كلمة البحث الموحد.</p></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
