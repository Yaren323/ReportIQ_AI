import streamlit as st
import pandas as pd
from datetime import datetime

from src.analyzer import AnalyzerAgent
from src.comparator import CompareAgent
from src.memory_db import MemoryAgent
from src.visualizer import VisualizerAgent
from src.report_generator import ReportGeneratorAgent

st.set_page_config(page_title="ReportIQ AI", layout="wide")

REQUIRED_COLUMNS = ["Tarih", "Departman", "Firma", "İşlem Tipi", "Tutar", "Durum"]


# Tarih kolonundan ay bilgisini güvenli şekilde alır.
def get_month_name_from_date_column(df):
    parsed_dates = pd.to_datetime(df["Tarih"], errors="coerce")
    valid_dates = parsed_dates.dropna()

    if len(valid_dates) == 0:
        return "Bilinmiyor"

    # Aynı ay için tek kayıt kontrolünü güvenli yapmak adına yıl-ay formatı kullanıyoruz.
    return valid_dates.iloc[0].strftime("%Y-%m")


# Eksik zorunlu kolonları döndürür.
def get_missing_columns(df):
    return [column for column in REQUIRED_COLUMNS if column not in df.columns]


# Uzun özetleri tablo için kısaltır.
def shorten_text(text, max_length=120):
    if text is None:
        return ""
    text = str(text).strip()
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# Yönetici özeti metnini daha profesyonel başlıklarla üretir.
def create_executive_summary(current_results, comparison):
    total_pct = comparison["total_amount"]["percentage_change"]
    pending_diff = comparison["pending_count"]["difference"]
    transaction_pct = comparison["transaction_count"]["percentage_change"]

    if total_pct > 0:
        total_trend = "artış"
    elif total_pct < 0:
        total_trend = "azalış"
    else:
        total_trend = "değişim yok"

    if pending_diff > 0:
        risk_text = "Bekleyen işlem sayısı artmıştır; operasyonel gecikme riski vardır."
        action_text = "Bekleyen kayıtlar önceliklendirilerek günlük takip listesi oluşturulmalıdır."
    elif pending_diff < 0:
        risk_text = "Bekleyen işlem sayısı düşmüştür; operasyonel risk seviyesi azalmıştır."
        action_text = "Mevcut süreç disiplini korunmalı ve kapanan işlemler haftalık izlenmelidir."
    else:
        risk_text = "Bekleyen işlem sayısı sabit kalmıştır; süreçte ek hızlanma fırsatı vardır."
        action_text = "Onay ve mutabakat adımlarında darboğaz analizi yapılarak iyileştirme planı hazırlanmalıdır."

    summary = f"""
### Genel Durum
Güncel ayda toplam işlem tutarı **{current_results['total_amount']:,.0f} TL** seviyesindedir. Toplam işlem adedi **{current_results['transaction_count']}** ve firma sayısı **{current_results['company_count']}** olarak gerçekleşmiştir.

### Öne Çıkan Değişimler
Önceki aya göre toplam tutarda **%{total_pct:.2f}** oranında **{total_trend}** görülmüştür. İşlem adedindeki değişim oranı **%{transaction_pct:.2f}** seviyesindedir.

### Riskli Noktalar
{risk_text}

### Önerilen Aksiyonlar
{action_text}
"""

    return summary


st.title("ReportIQ AI Yönetici Dashboard")
st.caption("Önceki ay ve güncel ay mutabakat verilerini karşılaştırır, KPI ve yönetici raporu üretir.")

upload_col1, upload_col2 = st.columns(2)

with upload_col1:
    previous_file = st.file_uploader("Önceki ay Excel dosyası", type=["xlsx", "xls"], key="previous_month_file")

with upload_col2:
    current_file = st.file_uploader("Güncel ay Excel dosyası", type=["xlsx", "xls"], key="current_month_file")

if previous_file and current_file:
    previous_df = pd.read_excel(previous_file)
    current_df = pd.read_excel(current_file)

    previous_missing = get_missing_columns(previous_df)
    current_missing = get_missing_columns(current_df)

    if previous_missing or current_missing:
        st.error("Excel kolonları beklenen standartta değil. Lütfen zorunlu kolonları kontrol edin.")

        if previous_missing:
            st.warning(f"Önceki ay dosyasında eksik kolonlar: {', '.join(previous_missing)}")

        if current_missing:
            st.warning(f"Güncel ay dosyasında eksik kolonlar: {', '.join(current_missing)}")

    else:
        # Tutar kolonunu sayısala çevirerek hesaplamaları güvenli hale getir.
        previous_df["Tutar"] = pd.to_numeric(previous_df["Tutar"], errors="coerce").fillna(0)
        current_df["Tutar"] = pd.to_numeric(current_df["Tutar"], errors="coerce").fillna(0)

        analyzer_agent = AnalyzerAgent(current_df)
        current_results = analyzer_agent.run_full_analysis()

        compare_agent = CompareAgent(previous_df, current_df)
        compare_results = compare_agent.run_comparison()
        comparison = compare_results["comparison"]

        visualizer_agent = VisualizerAgent()
        memory_agent = MemoryAgent()
        memory_agent.create_database()

        report_date = datetime.now().strftime("%Y-%m-%d")
        month_name = get_month_name_from_date_column(current_df)

        st.divider()
        st.subheader("KPI Özeti")

        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.metric("Toplam Tutar", f"{current_results['total_amount']:,.0f} TL")
        kpi_col2.metric("İşlem Sayısı", current_results["transaction_count"])
        kpi_col3.metric("Firma Sayısı", current_results["company_count"])
        kpi_col4.metric("Bekleyen İşlem", current_results["pending_count"])

        st.subheader("Karşılaştırma Sonuçları")
        cmp_col1, cmp_col2, cmp_col3, cmp_col4 = st.columns(4)
        cmp_col1.metric("Toplam Tutar Farkı", f"{comparison['total_amount']['difference']:,.0f} TL")
        cmp_col2.metric("İşlem Sayısı Farkı", f"{comparison['transaction_count']['difference']}")
        cmp_col3.metric("Firma Sayısı Farkı", f"{comparison['company_count']['difference']}")
        cmp_col4.metric("Bekleyen İşlem Farkı", f"{comparison['pending_count']['difference']}")

        st.subheader("Yüzde Değişimler")
        percentage_df = pd.DataFrame(
            {
                "Metrik": ["Toplam Tutar", "İşlem Sayısı", "Firma Sayısı", "Bekleyen İşlem"],
                "Yüzde Değişim (%)": [
                    comparison["total_amount"]["percentage_change"],
                    comparison["transaction_count"]["percentage_change"],
                    comparison["company_count"]["percentage_change"],
                    comparison["pending_count"]["percentage_change"],
                ],
            }
        )
        percentage_df["Yüzde Değişim (%)"] = percentage_df["Yüzde Değişim (%)"].round(2)
        st.dataframe(percentage_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Yönetici Raporu Grafikleri")

        total_amount_chart = visualizer_agent.create_total_amount_comparison_chart(
            previous_amount=comparison["total_amount"]["previous"],
            current_amount=comparison["total_amount"]["current"],
        )
        st.plotly_chart(total_amount_chart, use_container_width=True)

        pending_count_chart = visualizer_agent.create_pending_count_comparison_chart(
            previous_pending=comparison["pending_count"]["previous"],
            current_pending=comparison["pending_count"]["current"],
        )
        st.plotly_chart(pending_count_chart, use_container_width=True)

        percentage_change_chart = visualizer_agent.create_percentage_change_chart(percentage_df)
        st.plotly_chart(percentage_change_chart, use_container_width=True)

        company_total_chart = visualizer_agent.create_company_total_amount_chart(current_df)
        st.plotly_chart(company_total_chart, use_container_width=True)

        department_total_chart = visualizer_agent.create_department_total_amount_chart(current_df)
        st.plotly_chart(department_total_chart, use_container_width=True)

        st.divider()
        st.subheader("AI Yönetici Özeti")
        executive_summary = create_executive_summary(current_results, comparison)
        st.markdown(executive_summary)

        # HTML yönetici raporunu üret ve indirme butonu göster
        report_generator_agent = ReportGeneratorAgent()
        html_report = report_generator_agent.generate_html_report(
            current_results=current_results,
            comparison=comparison,
            percentage_df=percentage_df,
            executive_summary=executive_summary,
            report_title="ReportIQ AI Yönetici Raporu",
        )

        st.download_button(
            label="Yönetici Raporunu İndir",
            data=html_report,
            file_name="reportiq_yonetici_raporu.html",
            mime="text/html",
            key="download_executive_report_button",
        )

        # Aynı ayın tekrar kaydedilmemesi için month_name kontrolü yapılır.
        all_reports_for_check = memory_agent.get_all_reports()
        existing_month_names = {report[2] for report in all_reports_for_check}

        if st.button("Raporu Hafızaya Kaydet", key="save_report_button"):
            if month_name in existing_month_names:
                st.warning("Bu ay için rapor zaten kayıtlı.")
            else:
                is_saved = memory_agent.save_report(
                    report_date=report_date,
                    month_name=month_name,
                    total_amount=float(current_results["total_amount"]),
                    transaction_count=int(current_results["transaction_count"]),
                    company_count=int(current_results["company_count"]),
                    pending_count=int(current_results["pending_count"]),
                    summary=executive_summary,
                )
                if is_saved:
                    st.success("Rapor başarıyla hafızaya kaydedildi.")
                else:
                    st.warning("Bu ay için rapor zaten kayıtlı.")

        st.divider()
        st.subheader("Geçmiş Raporlar")

        all_reports = memory_agent.get_all_reports()
        reports_df = pd.DataFrame(
            all_reports,
            columns=[
                "id",
                "report_date",
                "month_name",
                "total_amount",
                "transaction_count",
                "company_count",
                "pending_count",
                "summary",
            ],
        )

        if not reports_df.empty:
            # Tarih, tutar ve özet kolonlarını daha okunabilir hale getiriyoruz.
            reports_df["report_date"] = pd.to_datetime(
                reports_df["report_date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
            reports_df["report_date"] = reports_df["report_date"].fillna("")

            reports_df["total_amount"] = reports_df["total_amount"].apply(
                lambda value: f"{value:,.0f} TL"
            )
            reports_df["summary"] = reports_df["summary"].apply(shorten_text)

            # id kolonunu en sona alarak tabloyu sadeleştiriyoruz.
            reports_df = reports_df[
                [
                    "report_date",
                    "month_name",
                    "total_amount",
                    "transaction_count",
                    "company_count",
                    "pending_count",
                    "summary",
                    "id",
                ]
            ]

        st.dataframe(reports_df, use_container_width=True, hide_index=True)

else:
    st.info("Devam etmek için önceki ay ve güncel ay Excel dosyalarını yükleyin.")
