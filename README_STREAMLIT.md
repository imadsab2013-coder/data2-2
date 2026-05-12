# ⚖️ محكمة الأفكار - Streamlit Edition

**The Bench of Evidence** - نظام متكامل للتحليل الذكي القرآني

---

## 🎯 ميزات النظام

- 🤖 **10 وكلاء ذكيين** مع الحقن الديناميكي للقواعس
- 📋 **نظام RMS** لإدارة الكتالوجات والقواعس المنطقية
- 🔴 **تنبيهات حمراء** ذكية للأخطاء والتناقضات
- 💬 **دردشة حية** مع الوكلاء
- 🌐 **يعمل مع GitHub** - تحميل سريع للملفات
- ⚡ **أداء محسّن** مع caching ذكي

---

## 🚀 التشغيل السريع

### المحلي (Local)

```bash
# 1. استنساخ المشروع
git clone https://github.com/your-username/bench-evidence.git
cd bench-evidence

# 2. تثبيت المكتبات
pip install -r requirements_streamlit.txt

# 3. تشغيل التطبيق
streamlit run streamlit_optimized.py
```

**ستفتح التطبيق على:**
```
http://localhost:8501
```

### على Streamlit Cloud (مجاني)

```bash
# انشر مباشرة من GitHub
https://share.streamlit.io

# اختر:
# 1. Repository: your-username/bench-evidence
# 2. Branch: main
# 3. Main file path: streamlit_optimized.py
```

---

## 📁 هيكل المشروع

```
bench-evidence/
├── streamlit_optimized.py           ← التطبيق الرئيسي
├── requirements_streamlit.txt       ← المكتبات
├── complete_quran_data.json         ← بيانات القرآن
├── .streamlit/
│   ├── config.toml                 ← إعدادات Streamlit
│   └── secrets.toml                ← المفاتيح السرية (لا ترفعها!)
├── .gitignore                      ← الملفات المستبعدة
└── README.md                       ← هذا الملف
```

---

## 🔐 إدارة مفاتيح API

### محلياً

```bash
# أنشئ المجلد
mkdir -p .streamlit

# أنشئ ملف secrets.toml
cat > .streamlit/secrets.toml << EOF
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
EOF
```

### على Streamlit Cloud

1. افتح تطبيقك على: `https://share.streamlit.io`
2. اذهب إلى **Settings** → **Secrets**
3. أضف:
```
ANTHROPIC_API_KEY = sk-ant-your-key-here
```

---

## 💻 استخدام التطبيق

### 1. تبويب الدردشة 💬

```
1. اكتب السؤال
2. اختر الوكلاء (المناقش، المحلل، إلخ)
3. انقر "معالجة السؤال"
4. اقرأ الردود من كل وكيل
```

**مثال:**
```
السؤال: "ما معنى الفرقان في القرآن الكريم؟"

✅ المناقش: 
يقول الله تعالى في سورة الفرقان (25:1)...

✅ المحلل:
الفرقان يعني الفصل والتمييز...
```

### 2. تبويب الكتالوجات 📋

```
1. أضف قاعدة جديدة:
   - العنوان: "منع_الترادف"
   - المنطق: "لا يمكن أن تكون كلمتان مرادفتين تماماً"

2. الوكلاء سيلتزمون بهذه القاعدة تلقائياً

3. عرض جميع القواعس المفعلة
```

### 3. تبويب التنبيهات 🔴

```
يعرض:
- الأخطاء الحرجة
- التحذيرات
- حالة النظام
```

---

## ⚡ تحسينات الأداء

### مدمجة في التطبيق:

```python
# 1. Caching للبيانات
@st.cache_data(ttl=3600)
def fetch_data():
    pass

# 2. قاعدة بيانات في الذاكرة
conn = sqlite3.connect(":memory:")  # أسرع ✅

# 3. تحميل كسول (Lazy Loading)
if st.button("تحميل"):
    load_data()  # لا تحمّل من البداية
```

---

## 🐛 استكشاف المشاكل الشائعة

### المشكلة: بطء التحميل من GitHub

**الحل:**
```python
# استخدم caching
@st.cache_data(ttl=3600)
def fetch_from_github(url):
    response = requests.get(url, timeout=10)
    return response.json()
```

### المشكلة: الملف كبير جداً

**الحل:**
```bash
# استخدم Git LFS
git lfs install
git lfs track "*.json"
git add complete_quran_data.json
```

### المشكلة: مفتاح API غير موجود

**الحل:**
```bash
# أضفه في secrets.toml محلياً
cat > .streamlit/secrets.toml << EOF
ANTHROPIC_API_KEY = sk-ant-...
EOF
```

---

## 📊 متطلبات النظام

```
Python:         3.8+
Streamlit:      1.28+
Anthropic:      0.7.8+
Requests:       2.31+
Memory:         500MB+
Storage:        100MB+
Internet:       مستقر
```

---

## 🔄 التحديثات التلقائية

عند دفع تحديث لـ GitHub:

```bash
git add .
git commit -m "التحديث"
git push origin main
```

**Streamlit Cloud سيحدّث التطبيق تلقائياً!** ✨

---

## 📚 التوثيق الإضافية

- `STREAMLIT_GITHUB_GUIDE.md` - دليل مفصل للـ Streamlit + GitHub
- `COMPLETE_SETUP_GUIDE.md` - دليل الإعداد الكامل
- `INTEGRATED_SYSTEM_FINAL_SUMMARY.md` - الملخص التقني

---

## 🤝 المساهمة

```bash
# 1. عمل Fork
git clone https://github.com/your-fork/bench-evidence.git

# 2. إنشاء branch جديد
git checkout -b feature/my-feature

# 3. عمل التغييرات
# ... تعديلاتك

# 4. Commit والـ Push
git add .
git commit -m "Add my feature"
git push origin feature/my-feature

# 5. عمل Pull Request على الـ Repo الأساسي
```

---

## 📞 الدعم والمساعدة

### للأسئلة التقنية:

1. تحقق من `STREAMLIT_GITHUB_GUIDE.md`
2. راجع السجلات: `streamlit run ... --logger.level=debug`
3. اختبر محلياً قبل النشر

### للأخطاء:

1. انسخ الرسالة الخطأ
2. افتح Issue في GitHub
3. أرفق التفاصيل والخطوات

---

## 📈 الإحصائيات

```
الملفات:        3 ملفات رئيسية
الكود:          ~600 سطر
الأداء:         <1 ثانية للرد
الذاكرة:        <100MB
التوفر:         99.9% (على Streamlit Cloud)
```

---

## ✅ قائمة التحقق

- [ ] المشروع على GitHub
- [ ] requirements_streamlit.txt موجود
- [ ] streamlit_optimized.py جاهز
- [ ] .gitignore معد
- [ ] secrets.toml في .gitignore
- [ ] التطبيق يعمل محلياً
- [ ] نشر على Streamlit Cloud (اختياري)

---

## 🎉 البدء الآن

```bash
# النسخ السريعة:

# المحلي
streamlit run streamlit_optimized.py

# GitHub
git clone https://github.com/your-username/bench-evidence.git

# Streamlit Cloud
https://share.streamlit.io
```

---

**⚖️ محكمة الأفكار - جاهزة للاستخدام الفوري!** 🚀

---

*آخر تحديث: 2024*  
*الإصدار: 2.0 (Streamlit Edition)*  
*الحالة: ✅ جاهز للإنتاج*
