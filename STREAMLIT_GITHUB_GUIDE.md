# 🚀 دليل تشغيل محكمة الأفكار مع Streamlit + GitHub

## 📋 الخطوات السريعة

### 1️⃣ استنساخ المشروع من GitHub

```bash
git clone https://github.com/your-username/bench-evidence.git
cd bench-evidence
```

### 2️⃣ تثبيت المكتبات

```bash
pip install -r requirements_streamlit.txt
```

### 3️⃣ تشغيل التطبيق

```bash
streamlit run streamlit_optimized.py
```

**النتيجة:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

---

## 🌐 نشر على Streamlit Cloud (مجاني)

### خطوات النشر:

1. **أضف `.streamlit/secrets.toml` لحفظ المفاتيح:**

```bash
mkdir .streamlit
cat > .streamlit/secrets.toml << EOF
ANTHROPIC_API_KEY = "your-api-key"
EOF
```

2. **أضف لـ `.gitignore`:**

```bash
echo ".streamlit/secrets.toml" >> .gitignore
```

3. **ادفع للـ GitHub:**

```bash
git add .
git commit -m "Add Streamlit config"
git push origin main
```

4. **انشر على Streamlit Cloud:**
   - اذهب إلى: https://share.streamlit.io
   - انقر "Deploy an app"
   - اختر repository و branch
   - اضبط secrets في الواجهة

---

## 💻 هيكل المشروع على GitHub

```
bench-evidence/
├── streamlit_optimized.py          ← الملف الرئيسي
├── requirements_streamlit.txt       ← المكتبات
├── .streamlit/
│   ├── config.toml                 ← الإعدادات
│   └── secrets.toml                ← المفاتيح (لا ترفعها!)
├── complete_quran_data.json        ← بيانات القرآن
├── .gitignore                      ← استبعد الملفات الحساسة
└── README.md                       ← التوثيق
```

---

## 🔐 إدارة المفاتيح الآمنة

### محليّاً:

```bash
# أنشئ ملف secrets محلي
cat > .streamlit/secrets.toml << EOF
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
EOF
```

### على Streamlit Cloud:

1. في لوحة التحكم: **Settings** → **Secrets**
2. أضف:
```
ANTHROPIC_API_KEY = sk-ant-...
```

---

## 📊 تحسين الأداء

### Cache للبيانات الثقيلة:

```python
@st.cache_data(ttl=3600)  # Cache لـ ساعة
def load_quran():
    # تحميل البيانات
    pass
```

### استخدام in-memory database:

```python
conn = sqlite3.connect(":memory:")  # أسرع من الملفات
```

### تقليل استدعاءات API:

```python
@st.cache_resource
def init_anthropic_client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: الملف كبير جداً

**الحل:**
```bash
# قسّم البيانات الكبيرة
split -b 10M complete_quran_data.json

# أو استخدم GitHub LFS
git lfs install
git lfs track "*.json"
git add complete_quran_data.json
```

### المشكلة: بطء التحميل من GitHub

**الحل:**
```python
@st.cache_data(ttl=3600)
def fetch_github(url):
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
```

### المشكلة: المفتاح لم يُحفظ

**الحل:**
```python
# استخدم st.secrets بدل variables عادية
api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
if not api_key:
    st.error("❌ مفتاح API غير موجود")
```

---

## 📱 عنوان التطبيق

بعد النشر:
```
https://bench-evidence.streamlit.app
```

أو محلياً:
```
http://localhost:8501
```

---

## 🔄 التحديثات التلقائية

عند دفع تحديث لـ GitHub:
```bash
git push origin main
# Streamlit سيحدّث التطبيق تلقائياً!
```

---

## ⚡ نصائح الأداء

### 1. استخدم in-memory بدل SQLite

```python
# سريع ✅
conn = sqlite3.connect(":memory:")

# بطيء ❌
conn = sqlite3.connect("data.db")
```

### 2. cache النتائج

```python
@st.cache_data
def expensive_operation():
    return result
```

### 3. استخدم lazy loading

```python
if st.button("تحميل البيانات"):
    data = load_data()  # لا تحمّل من البداية
```

---

## 🎓 أوامر مفيدة

```bash
# تشغيل مع الـ logging
streamlit run streamlit_optimized.py --logger.level=debug

# تشغيل على منفذ مختلف
streamlit run streamlit_optimized.py --server.port 8502

# عرض المعلومات
streamlit config show

# مسح الـ cache
streamlit cache clear
```

---

## ✅ قائمة التحقق

- [ ] المشروع موجود على GitHub
- [ ] `requirements_streamlit.txt` موجود
- [ ] `.streamlit/secrets.toml` في `.gitignore`
- [ ] التطبيق يشتغل محلياً: `streamlit run streamlit_optimized.py`
- [ ] تم نشره على Streamlit Cloud (اختياري)
- [ ] المفاتيح محفوظة بشكل آمن
- [ ] البيانات تحمّل بسرعة

---

## 🚀 الخطوة التالية

```bash
# 1. شغّل محلياً
streamlit run streamlit_optimized.py

# 2. تأكد من أنه يعمل
# افتح: http://localhost:8501

# 3. انشر على Streamlit Cloud
# (اختياري لكن موصى به)

# 4. شارك الرابط
https://bench-evidence.streamlit.app
```

---

**🎉 كل شيء جاهز الآن!**
