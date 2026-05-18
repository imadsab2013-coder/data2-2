import streamlit as st
import pandas as pd
import re
import os

# 1️⃣ الإعدادات البصرية النقية - الهوية العريضة
st.set_page_config(page_title="مجلس البينة V4", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    html, body, [data-testid="stAppViewContainer"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* وعاء السبورة السوداء الحاصر والشامل لكافة المخرجات والمعاينات */
    .blackboard {
        background: #000000 !important;
        border: 1px solid #333333 !important;
        padding: 25px;
        margin-top: 15px;
        min-height: 500px;
    }
    
    .verse-preview {
        background: #111111;
        border-right: 3px solid #ffffff;
        padding: 15px;
        font-size: 18px;
        line-height: 2;
        margin: 15px 0;
        color: #ffffff;
    }
    
    .context-verse {
        background: #161616;
        border-right: 2px solid #333333;
        padding: 10px;
        margin: 6px 0;
        font-size: 15px;
        color: #cccccc;
    }
    
    .context-verse-center {
        border-right: 2px solid #00ffcc;
        background: #1f1f1f;
        font-weight: bold;
        color: #ffffff;
    }
    
    /* أزرار ميكانيكية عريضة ومستقرة */
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
        background-color: #222222 !important;
    }
    
    div[data-testid="stTextInput"] input {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
    }
    header, footer { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 2️⃣ تنظيف ومعالجة الحروف لمنع الرموز المشوهة
def clean_quran_text(text):
    if not isinstance(text, str):
        return ""
    # عزل وعزل علامات الضبط المصحفي الدقيقة التي تسبب المربعات الفارغة
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
    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_excel(path)
                for col in df.columns:
                    if df[col].dtype == object:
                        df[col] = df[col].astype(str).apply(clean_quran_text)
                return df
            except:
                continue
    return None

# 3️⃣ تأمين الذاكرة المستمرة وتفادي شلل الأزرار التتبعية
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "selected_verse_key" not in st.session_state:
    st.session_state.selected_verse_key = None

df_quran = load_quran_data()
if df_quran is None:
    st.error("خطأ مادي: ملف قاعدة البيانات غير موجود")
    st.stop()

# كشف الأعمدة ماديّاً
cols = df_quran.columns
surah_col = next((c for c in cols if c in ['السورة', 'surah']), cols[0])
verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number', 'الآية']), cols[1])
text_col = next((c for c in cols if c in ['نص الآية', 'text', 'الآية_نص']), cols[2])

# 4️⃣ مدخل البحث الرئيسي العلوي
col_input, col_clear = st.columns([5, 1])
with col_input:
    # ربط المدخل بمتغير وسيط ومفتاح ثابت لمنع الارتداد والتجميد
    user_input = st.text_input("المبحث:", value=st.session_state.search_query, placeholder="أدخل اللفظ المراد رصده منطقياً...", label_visibility="collapsed", key="search_bar_input")
    if user_input != st.session_state.search_query:
        st.session_state.search_query = user_input
        st.session_state.selected_verse_key = None
        st.rerun()

with col_clear:
    if st.button("🔄 تصفير الجلسة"):
        st.session_state.search_query = ""
        st.session_state.selected_verse_key = None
        st.rerun()

# 5️⃣ فتح لسان وعاء السبورة السوداء الشاملة لحبس كافة المخرجات بالداخل ماديّاً
st.markdown('<div class="blackboard">', unsafe_allow_html=True)

if st.session_state.search_query:
    q_norm = normalize_arabic(st.session_state.search_query)
    matched_rows = []
    
    for idx, row in df_quran.iterrows():
        t_norm = normalize_arabic(str(row[text_col]))
        if q_norm in t_norm:
            matched_rows.append({
                'surah': row[surah_col],
                'verse': int(row[verse_col]),
                'text': row[text_col],
                'idx': idx
            })
            
    if not matched_rows:
        st.markdown("<p style='color:#666;'>السبورة لا تحتوي على نتائج مطابقة للفظ الحالي.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"**المطابقات المادية المكتشفة: ({len(matched_rows)})**")
        
        # تقسيم داخلي متوازن داخل السبورة السوداء
        # العمود الأيمن: قائمة أزرار الآيات المطابقة
        # العمود الأيسر: المعاينة المستقرة والتفكيك الأفقي بدون نافذة منبثقة
        col_list, col_view = st.columns([2, 3])
        
        with col_list:
            st.markdown("<p style='color:#888; font-size:13px;'>اختر آية لمعاينتها وتفكيكها هندسياً:</p>", unsafe_allow_html=True)
            for i, match in enumerate(matched_rows):
                v_key = f"{match['surah']}_{match['verse']}"
                # وسم بصري للآية النشطة حالياً
                active_mark = "🔹 " if st.session_state.selected_verse_key == v_key else ""
                btn_label = f"{active_mark}﴿ {match['text'][:35]}... ﴾ ── ({match['surah']}:{match['verse']})"
                
                if st.button(btn_label, key=f"v_btn_{i}_{v_key}"):
                    st.session_state.selected_verse_key = v_key
                    st.rerun()
                    
        with col_view:
            if st.session_state.selected_verse_key:
                target = next((m for m in matched_rows if f"{m['surah']}_{m['verse']}" == st.session_state.selected_verse_key), None)
                if target:
                    st.markdown("### 📄 المعاينة الهيكلية للآية النشطة")
                    st.markdown(f"<div class='verse-preview'>{target['text']}</div>", unsafe_allow_html=True)
                    
                    # جلب مصفوفة السياق المتسلسل (قبل وبعد بآيتين) في نفس الوعاء
                    st.markdown("### 🔗 السياق التدبري المرتبط")
                    start_v = max(1, target['verse'] - 2)
                    end_v = target['verse'] + 2
                    
                    ctx_mask = (df_quran[surah_col] == target['surah']) & (df_quran[verse_col].astype(int).between(start_v, end_v))
                    for _, c_row in df_quran[ctx_mask].sort_values(verse_col).iterrows():
                        v_num = int(c_row[verse_col])
                        is_tgt = (v_num == target['verse'])
                        cls = "context-verse context-verse-center" if is_tgt else "context-verse"
                        prefix = "⭐ " if is_tgt else ""
                        st.markdown(f"<div class='{cls}'>{prefix}[{v_num}] {c_row[text_col]}</div>", unsafe_allow_html=True)
                    
                    # 6️⃣ التتبع الأفقي المستقر للألفاظ (معالجة مشكلة عدم استجابة الزر)
                    st.markdown("### 🔍 تتبع اللفظ أفقياً (البحث المستمر)")
                    # تنظيف دقيق للكلمات المفككة لعزل حروف الوقف من الأزرار تماماً
                    words = [w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم") for w in target['text'].split() if len(w.strip(".,:-()\"' ﴿﴾ۖۗقليجۘم")) > 1]
                    
                    word_cols = st.columns(len(words) if words else 1)
                    for w_idx, word in enumerate(words):
                        with word_cols[w_idx % len(word_cols)]:
                            # استخدام مفتاح فريد مركّب يضمن تحديث الـ State فور الضغط وإعادة تشغيل المسح
                            if st.button(word, key=f"ttrack_word_{w_idx}_{word}_{st.session_state.selected_verse_key}"):
                                st.session_state.search_query = word
                                st.session_state.selected_verse_key = None  # تصفير المعاينة القديمة لاستيعاب مخرجات اللفظ الجديد
                                st.rerun()
            else:
                st.markdown("<div style='text-align:center; padding-top:100px; color:#444;'>← اضغط على أي آية من القائمة اليمنى لعرض تفكيكها ماديّاً بالكامل هنا داخل السبورة.</div>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align:center; color:#555; padding:80px 0;'>السبورة بانتظار إدخال كلمة البحث الموحد لبدء العمل المادي البنيوي.</p>", unsafe_allow_html=True)

# إغلاق وعاء السبورة السوداء الشامل ماديّاً لحبس كل المخرجات بالداخل تماماً
st.markdown('</div>', unsafe_allow_html=True)
