"""
🌟 مجلس البينة V4 - نظام السبورة السوداء النقية
البروتوكول الصارم: ألوان ثلاثية + روابط inline + أوراق مستقلة
"""

import streamlit as st
import pandas as pd
import re
import os
import json
from datetime import datetime

# إعدادات Streamlit
st.set_page_config(page_title="مجلس البينة V4", layout="wide", initial_sidebar_state="collapsed")

# التصميم النقي - ألوان ثلاثية فقط
st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #000000;
        color: #ffffff;
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stVerticalBlockBG"] {
        background: #000000;
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
    
    .blackboard {
        background: #000000;
        border: 1px solid #333333;
        border-radius: 0;
        padding: 20px;
        margin: 20px;
        min-height: 400px;
        max-height: 70vh;
        overflow-y: auto;
    }
    
    .blackboard::-webkit-scrollbar {
        width: 6px;
    }
    
    .blackboard::-webkit-scrollbar-track {
        background: #000000;
    }
    
    .blackboard::-webkit-scrollbar-thumb {
        background: #333333;
    }
    
    .result-button {
        display: block;
        width: 100%;
        background: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 0;
        padding: 15px;
        margin: 10px 0;
        color: #ffffff;
        text-align: right;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .result-button:hover {
        background: #2a2a2a;
        border-color: #555555;
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
        border-right: 2px solid #555555;
        background: #222222;
        font-weight: bold;
    }
    
    .stButton>button {
        background-color: #333333 !important;
        color: #ffffff !important;
        font-weight: normal !important;
        border-radius: 0 !important;
        border: 1px solid #555555 !important;
        padding: 8px 16px !important;
    }
    
    .stButton>button:hover {
        background-color: #444444 !important;
        border-color: #777777 !important;
    }
    
    .empty-state {
        text-align: center;
        padding: 50px 20px;
        color: #666666;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] { display: none; }
    footer { display: none; }
    
    </style>
""", unsafe_allow_html=True)

# دوال مساعدة
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
            return pd.read_excel(path)
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

def save_paper(query, surah, verse, text, context_verses):
    os.makedirs('data/mfolder_results', exist_ok=True)
    
    filename = re.sub(r'[^\u0621-\u064A0-9]', '_', query)[:50]
    if not filename:
        filename = f"{surah}_{verse}"
    
    filepath = f'data/mfolder_results/{filename}.json'
    
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
    papers_dir = 'data/mfolder_results'
    if not os.path.exists(papers_dir):
        return {}
    
    papers = {}
    for filename in os.listdir(papers_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(papers_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    papers[filename[:-5]] = json.load(f)
            except:
                pass
    return papers

# تهيئة الجلسة
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'verses_before' not in st.session_state:
    st.session_state.verses_before = 2
if 'verses_after' not in st.session_state:
    st.session_state.verses_after = 2

# تحميل البيانات
df_quran = load_quran_data()
if df_quran is None:
    st.error("خطأ في تحميل البيانات")
    st.stop()

# شريط البحث العلوي
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_left:
    with st.popover("⚙️"):
        st.markdown("**المعايير**")
        st.session_state.verses_before = st.number_input("قبل:", 1, 20, st.session_state.verses_before)
        st.session_state.verses_after = st.number_input("بعد:", 1, 20, st.session_state.verses_after)

with col_center:
    search_query = st.text_input("🔍", placeholder="ابحث...", label_visibility="collapsed")
    st.session_state.search_query = search_query

with col_right:
    with st.popover("💾"):
        st.markdown("**الأوراق**")
        papers = load_papers()
        if papers:
            for paper_name, paper_data in papers.items():
                if st.button(f"📄 {paper_name}", use_container_width=True):
                    st.session_state.search_query = paper_data['query']
                    st.rerun()
        else:
            st.write("لا توجد أوراق محفوظة")

st.divider()

# السبورة السوداء
st.markdown('<div class="blackboard">', unsafe_allow_html=True)

if search_query:
    results = search_unified(df_quran, search_query)
    
    if not results:
        st.markdown('<div class="empty-state"><p>لم يتم العثور على نتائج</p></div>', unsafe_allow_html=True)
    else:
        for idx, result in enumerate(results):
            if st.button(
                f"{result['text'][:60]}...\n{result['surah']} : {result['verse']}",
                key=f"result_{idx}",
                use_container_width=True
            ):
                st.markdown("**الآية**")
                st.markdown(f"<div class='verse-preview'>{result['text']}</div>", unsafe_allow_html=True)
                
                context_verses = get_context(
                    df_quran,
                    result['surah'],
                    result['verse'],
                    st.session_state.verses_before,
                    st.session_state.verses_after
                )
                
                st.markdown("**السياق**")
                for ctx in context_verses:
                    if ctx['is_center']:
                        st.markdown(f"<div class='context-verse context-verse-center'>⭐ [{ctx['verse']}] {ctx['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='context-verse'>[{ctx['verse']}] {ctx['text']}</div>", unsafe_allow_html=True)
                
                st.markdown("**الكلمات**")
                words = result['text'].split()
                word_cols = st.columns(min(len(words), 5))
                
                for i, word in enumerate(words):
                    with word_cols[i % len(word_cols)]:
                        if st.button(word[:12], key=f"word_{idx}_{i}"):
                            st.session_state.search_query = word
                            st.rerun()
                
                st.divider()
                if st.button("💾 حفظ الورقة", use_container_width=True):
                    if save_paper(st.session_state.search_query, result['surah'], result['verse'], result['text'], context_verses):
                        st.success("✅ تم الحفظ")
else:
    st.markdown('<div class="empty-state"><p>ابدأ البحث</p></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
