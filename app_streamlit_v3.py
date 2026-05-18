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

