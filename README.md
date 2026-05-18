# 🚀 ReportIQ_AI

Yapay zeka destekli mutabakat analiz ve aylık raporlama sistemi.

---

# 📌 Proje Hakkında

ReportIQ_AI, şirketlerde gerçekleştirilen aylık mutabakat süreçlerini otomatikleştirmek ve yönetsel analizleri hızlandırmak amacıyla geliştirilmiş AI destekli bir raporlama platformudur.

Sistem:

- Aylık mutabakat Excel dosyalarını yükler
- KPI metriklerini otomatik analiz eder
- Önceki ay ve güncel ay karşılaştırması yapar
- AI destekli yönetici özeti oluşturur
- Grafiklerle değişimleri görselleştirir
- Rapor geçmişini SQLite veritabanında saklar
- Dinamik raporlama akışını destekler

---

# ✨ Özellikler

## 📊 KPI Dashboard

Sistem otomatik olarak:

- Toplam Tutar
- İşlem Sayısı
- Firma Sayısı
- Bekleyen İşlem Sayısı

metriklerini hesaplar.

---

## 📈 Aylık Karşılaştırma Motoru

Karşılaştırılan veriler:

- Önceki ay vs Güncel ay
- Yüzdesel değişimler
- Operasyonel iyileşmeler
- Bekleyen işlem trendleri

---

## 🤖 AI Yönetici Özeti

Sistem otomatik olarak:

- Yönetici özeti
- Operasyonel yorumlar
- İyileştirme önerileri
- Risk bildirimleri

oluşturur.

---

## 🧠 Hafıza Sistemi

SQLite tabanlı hafıza sistemi sayesinde:

- Geçmiş raporlar saklanır
- KPI geçmişi tutulur
- Rapor geçmişi görüntülenebilir

---

## 📉 Görselleştirme Sistemi

Plotly destekli interaktif grafikler:

- KPI karşılaştırma grafikleri
- Yüzde değişim grafikleri
- Bekleyen işlem analizleri
- Aylık trend görselleri

---

# 🛠️ Kullanılan Teknolojiler

| Teknoloji | Amaç |
|---|---|
| Python | Backend geliştirme |
| Streamlit | Dashboard arayüzü |
| Pandas | Veri işleme |
| Plotly | Görselleştirme |
| SQLite | Lokal veritabanı |
| Git & GitHub | Versiyon kontrolü |
| AI Agent Mimarisi | Modüler iş akışı |

---

# 🧩 Proje Mimarisi

```bash
ReportIQ_AI
│
├── app.py
│
├── src
│   ├── analyzer.py
│   ├── comparator.py
│   ├── visualizer.py
│   ├── report_generator.py
│   └── memory_db.py
│
├── reportiq.db
│
└── .gitignore
```

---

# ⚙️ Kurulum

## 1. Projeyi Klonla

```bash
git clone https://github.com/Yaren323/ReportIQ_AI.git
```

---

## 2. Proje Klasörüne Gir

```bash
cd ReportIQ_AI
```

---

## 3. Virtual Environment Oluştur

```bash
python -m venv venv
```

---

## 4. Virtual Environment Aktifleştir

### Windows

```bash
venv\Scripts\activate
```

---

## 5. Paketleri Kur

```bash
pip install -r requirements.txt
```

---

## 6. Uygulamayı Çalıştır

```bash
streamlit run app.py
```

---

# 📷 Uygulama Özellikleri

## KPI Dashboard

- Aylık KPI kartları
- Karşılaştırma metrikleri
- AI yönetici özeti

---

## Grafikler

- Toplam tutar karşılaştırması
- Yüzde değişim analizi
- Bekleyen işlem karşılaştırması

---

# 🧠 AI Agent Yapısı

Proje modüler AI-Agent mantığıyla geliştirilmektedir.

## Mevcut Agentler

| Agent | Görevi |
|---|---|
| AnalyzerAgent | KPI analizi |
| CompareAgent | Aylık karşılaştırma |
| MemoryAgent | Hafıza yönetimi |
| VisualizerAgent | Grafik üretimi |

---


# 📌 Kullanım Alanları

- Finans mutabakat süreçleri
- Aylık operasyon analizleri
- KPI takibi
- Yönetici raporlamaları
- İç denetim süreçleri

---

# 👩‍💻 Geliştirici

**Yaren Esentürk**


---

# ⭐ Proje Vizyonu

ReportIQ_AI projesinin amacı; gelecekte tamamen otonom çalışan, yapay zeka destekli kurumsal mutabakat ve raporlama asistanına dönüşmektir.
