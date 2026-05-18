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


# Dashboard görünümünü daha modern yapmak için temel stil tanımları
def inject_dashboard_css():
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-size: 17px;
        }
        h1 {
            font-size: 2rem !important;
        }
        h2, h3 {
            font-size: 1.6rem !important;
        }
        .stMarkdown p, .stCaption, .stText, .stInfo, .stWarning, .stSuccess {
            font-size: 1rem !important;
        }
        .stExpander summary {
            font-size: 1rem !important;
            font-weight: 700 !important;
        }
        .stButton button, .stDownloadButton button {
            font-size: 1rem !important;
            font-weight: 700 !important;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] * {
            font-size: 1rem !important;
        }
        .riq-card {
            border-radius: 12px;
            padding: 14px 16px;
            margin: 8px 0 14px 0;
            border: 1px solid #2A3342;
        }
        .riq-card-prev {
            background: linear-gradient(135deg, #1A2235, #232D42);
        }
        .riq-card-current {
            background: linear-gradient(135deg, #1A2A36, #243244);
        }
        .riq-card-diff {
            background: linear-gradient(135deg, #1f2937, #2b3442);
        }
        .riq-card-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: #C6D4E3;
            margin-bottom: 8px;
        }
        .riq-section-wrap {
            border-radius: 14px;
            padding: 14px 14px 12px 14px;
            margin: 10px 0 16px 0;
            border: 1px solid #334155;
        }
        .riq-section-prev {
            background: #202630;
        }
        .riq-section-current {
            background: #20384a;
        }
        .riq-section-diff {
            background: #1f2937;
        }
        .riq-section-title {
            color: #D5E1EE;
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .riq-kpi {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid #2F3D4F;
            border-radius: 10px;
            padding: 10px 12px;
            min-height: 84px;
        }
        .riq-kpi-label {
            color: #9FB3C8;
            font-size: 1rem;
            margin-bottom: 3px;
        }
        .riq-kpi-value {
            color: #EEF4FF;
            font-size: 1.6rem;
            font-weight: 700;
        }
        .riq-diff-pos {
            color: #8DC9A5;
        }
        .riq-diff-neg {
            color: #E29A84;
        }
        .riq-diff-neutral {
            color: #AFC0D4;
        }
        .riq-pct-wrap {
            margin-top: 10px;
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid #364152;
            border-radius: 10px;
            padding: 8px 10px;
            max-width: 760px;
        }
        .riq-pct-row {
            display: grid;
            grid-template-columns: 210px 44px 1fr;
            align-items: center;
            gap: 8px;
            min-height: 44px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }
        .riq-pct-row:last-child {
            border-bottom: none;
        }
        .riq-pct-metric {
            color: #D2DCE9;
            font-size: 1.05rem;
            font-weight: 600;
        }
        .riq-pct-arrow {
            font-size: 1.2rem;
            font-weight: 700;
            text-align: center;
        }
        .riq-pct-value {
            color: #E8EFF8;
            font-size: 1.12rem;
            font-weight: 600;
        }
        .riq-good {
            color: #8DC9A5;
        }
        .riq-bad {
            color: #E29A84;
        }
        .riq-neutral {
            color: #E2C97A;
        }
        .riq-graph-card {
            border-radius: 14px;
            border: 1px solid #334155;
            padding: 12px 12px 8px 12px;
            margin: 8px 0 12px 0;
        }
        .riq-graph-card-1 { background: #1f2937; }
        .riq-graph-card-2 { background: #202b3a; }
        .riq-graph-card-3 { background: #1e3344; }
        .riq-graph-card-4 { background: #263241; }
        .riq-graph-title {
            color: #D5E1EE;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .riq-summary-card {
            background: #1f2937;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 18px;
            margin: 10px 0 14px 0;
        }
        .riq-summary-title {
            color: #E1EAF4;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 12px;
        }
        .riq-summary-item {
            background: #202b3a;
            border: 1px solid #3a4b61;
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .riq-summary-item h4 {
            margin: 0 0 6px 0;
            font-size: 1.32rem;
            font-weight: 800;
            color: #D8E4F2;
        }
        .riq-summary-item p {
            margin: 0;
            font-size: 1.06rem;
            color: #C6D4E3;
            line-height: 1.6;
        }
        .riq-archive-card {
            background: #1f2937;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 18px;
            margin-top: 8px;
        }
        .riq-archive-title {
            color: #E1EAF4;
            font-size: 1.85rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .riq-archive-subtitle {
            color: #D5E1EE;
            font-size: 1.3rem;
            font-weight: 700;
            margin: 12px 0 8px 0;
        }
        .riq-detail-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 10px;
        }
        .riq-detail-box {
            background: #202b3a;
            border: 1px solid #3a4b61;
            border-radius: 8px;
            padding: 10px;
        }
        .riq-detail-label {
            color: #9FB3C8;
            font-size: 1.02rem;
        }
        .riq-detail-value {
            color: #EAF1F9;
            font-size: 1.35rem;
            font-weight: 800;
            margin-top: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_card(title, card_class):
    st.markdown(
        f'<div class="riq-card {card_class}"><div class="riq-card-title">{title}</div></div>',
        unsafe_allow_html=True,
    )


def start_section_container(section_class, title):
    st.markdown(
        f'<div class="riq-section-wrap {section_class}"><div class="riq-section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def end_section_container():
    st.markdown("</div>", unsafe_allow_html=True)


def start_graph_card(title, card_class):
    st.markdown(
        f'<div class="riq-graph-card {card_class}"><div class="riq-graph-title">{title}</div>',
        unsafe_allow_html=True,
    )


def end_graph_card():
    st.markdown("</div>", unsafe_allow_html=True)


def render_kpi_card(label, value, value_class=""):
    class_text = f"riq-kpi-value {value_class}".strip()
    st.markdown(
        f"""
        <div class="riq-kpi">
            <div class="riq-kpi-label">{label}</div>
            <div class="{class_text}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_company_expander(df):
    with st.expander("Firma Detayları", expanded=False):
        company_list = df["Firma"].dropna().astype(str).drop_duplicates().sort_values().tolist()
        st.write(company_list)


def render_pending_expander(df):
    with st.expander("Bekleyen Detayları", expanded=False):
        pending_df = df[df["Durum"] == "Bekliyor"][
            ["Tarih", "Firma", "İşlem Tipi", "Tutar", "Durum"]
        ]
        st.dataframe(pending_df, use_container_width=True, hide_index=True)


def get_change_visual(metric_name, value):
    # Standart metriklerde pozitif iyi, negatif kötü kabul edilir.
    # Bekleyen işlemde tam tersi kural uygulanır.
    if metric_name == "Bekleyen İşlem":
        if value < 0:
            return "↓", "riq-good"
        if value > 0:
            return "↑", "riq-bad"
        return "↔", "riq-neutral"

    if value > 0:
        return "↑", "riq-good"
    if value < 0:
        return "↓", "riq-bad"
    return "↔", "riq-neutral"


def render_percentage_change_rows(percentage_df):
    # Tüm satırları tek bir HTML string içinde birleştiriyoruz.
    rows_html_parts = []
    for _, row in percentage_df.iterrows():
        metric_name = row["Metrik"]
        change_value = float(row["Yüzde Değişim (%)"])
        arrow, color_class = get_change_visual(metric_name, change_value)
        rows_html_parts.append(
            f'<div class="riq-pct-row">'
            f'<div class="riq-pct-metric">{metric_name}</div>'
            f'<div class="riq-pct-arrow {color_class}">{arrow}</div>'
            f'<div class="riq-pct-value {color_class}">%{change_value:.2f}</div>'
            f"</div>"
        )

    html_content = '<div class="riq-pct-wrap">' + "".join(rows_html_parts) + "</div>"
    st.markdown(html_content, unsafe_allow_html=True)


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


def create_executive_sections(current_results, comparison):
    total_pct = comparison["total_amount"]["percentage_change"]
    transaction_pct = comparison["transaction_count"]["percentage_change"]
    company_pct = comparison["company_count"]["percentage_change"]
    pending_diff = comparison["pending_count"]["difference"]

    general = (
        f"Bu dönemde toplam işlem tutarı <strong>{current_results['total_amount']:,.0f} TL</strong>, "
        f"işlem adedi <strong>{current_results['transaction_count']}</strong>, "
        f"firma sayısı <strong>{current_results['company_count']}</strong> ve "
        f"bekleyen işlem <strong>{current_results['pending_count']}</strong> seviyesindedir."
    )
    highlights = (
        f"Toplam tutarda <strong>%{total_pct:.2f}</strong>, işlem adedinde <strong>%{transaction_pct:.2f}</strong> "
        f"ve firma sayısında <strong>%{company_pct:.2f}</strong> değişim gözlemlenmiştir."
    )

    if pending_diff > 0:
        risks = "Bekleyen işlem adedi arttığı için operasyonel gecikme riski yükselmiştir."
        actions = "Bekleyen kayıtlar önceliklendirilmeli, günlük kapanış ve sorumlu takibi uygulanmalıdır."
    elif pending_diff < 0:
        risks = "Bekleyen işlem adedi azaldığı için operasyonel risk seviyesi gerilemiştir."
        actions = "İyileşen süreç korunmalı, sürdürülebilirlik için haftalık performans takibi sürdürülmelidir."
    else:
        risks = "Bekleyen işlem adedi sabit kaldığı için süreç hızında ek iyileştirme alanı bulunmaktadır."
        actions = "Onay adımları gözden geçirilmeli, darboğaz noktaları için kısa aksiyon planı hazırlanmalıdır."

    return {
        "Genel Durum": general,
        "Öne Çıkan Değişimler": highlights,
        "Riskli Noktalar": risks,
        "Önerilen Aksiyonlar": actions,
    }


def render_executive_summary_card(executive_sections):
    summary_html = '<div class="riq-summary-card"><div class="riq-summary-title">AI Yönetici Özeti</div>'
    for title, text in executive_sections.items():
        summary_html += (
            f'<div class="riq-summary-item"><h4>{title}</h4><p>{text}</p></div>'
        )
    summary_html += "</div>"
    st.markdown(summary_html, unsafe_allow_html=True)


def create_summary_text_for_storage(executive_sections):
    lines = []
    for title, text in executive_sections.items():
        lines.append(f"{title}: {text}")
    return "\n".join(lines)


st.title("ReportIQ AI Yönetici Dashboard")
st.caption("Önceki ay ve güncel ay mutabakat verilerini karşılaştırır, KPI ve yönetici raporu üretir.")
inject_dashboard_css()

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

        # Önceki ay KPI hesapları (net karşılaştırma için)
        previous_results = AnalyzerAgent(previous_df).run_full_analysis()

        compare_agent = CompareAgent(previous_df, current_df)
        compare_results = compare_agent.run_comparison()
        comparison = compare_results["comparison"]

        visualizer_agent = VisualizerAgent()
        memory_agent = MemoryAgent()
        memory_agent.create_database()

        report_date = datetime.now().strftime("%Y-%m-%d")
        month_name = get_month_name_from_date_column(current_df)

        st.divider()
        start_section_container("riq-section-prev", "Önceki Ay Verileri")
        prev_col1, prev_col2, prev_col3, prev_col4 = st.columns(4)
        with prev_col1:
            render_kpi_card("Toplam Tutar", f"{previous_results['total_amount']:,.0f} TL")
        with prev_col2:
            render_kpi_card("İşlem Sayısı", f"{previous_results['transaction_count']}")
        with prev_col3:
            render_kpi_card("Firma Sayısı", f"{previous_results['company_count']}")
            render_company_expander(previous_df)
        with prev_col4:
            render_kpi_card("Bekleyen İşlem", f"{previous_results['pending_count']}")
            render_pending_expander(previous_df)
        end_section_container()

        start_section_container("riq-section-current", "Güncel Ay Verileri")
        curr_col1, curr_col2, curr_col3, curr_col4 = st.columns(4)
        with curr_col1:
            render_kpi_card("Toplam Tutar", f"{current_results['total_amount']:,.0f} TL")
        with curr_col2:
            render_kpi_card("İşlem Sayısı", f"{current_results['transaction_count']}")
        with curr_col3:
            render_kpi_card("Firma Sayısı", f"{current_results['company_count']}")
            render_company_expander(current_df)
        with curr_col4:
            render_kpi_card("Bekleyen İşlem", f"{current_results['pending_count']}")
            render_pending_expander(current_df)
        end_section_container()

        start_section_container("riq-section-diff", "Aylık Değişim / Fark")
        st.caption("Bu bölüm güncel ay ile önceki ay arasındaki farkı gösterir.")

        diff_col1, diff_col2, diff_col3, diff_col4 = st.columns(4)
        total_diff = comparison["total_amount"]["difference"]
        transaction_diff = comparison["transaction_count"]["difference"]
        company_diff = comparison["company_count"]["difference"]
        pending_diff = comparison["pending_count"]["difference"]

        def diff_class(value):
            if value > 0:
                return "riq-diff-pos"
            if value < 0:
                return "riq-diff-neg"
            return "riq-diff-neutral"

        with diff_col1:
            render_kpi_card(
                "Toplam Tutar Farkı",
                f"{total_diff:,.0f} TL",
                diff_class(total_diff),
            )
        with diff_col2:
            render_kpi_card(
                "İşlem Sayısı Farkı",
                f"{transaction_diff}",
                diff_class(transaction_diff),
            )
        with diff_col3:
            render_kpi_card(
                "Firma Sayısı Farkı",
                f"{company_diff}",
                diff_class(company_diff),
            )
        with diff_col4:
            # Bekleyen işlem farkında iş kuralı ters çalışır:
            # Azalış olumlu, artış olumsuz kabul edilir.
            if pending_diff < 0:
                pending_diff_class = "riq-diff-pos"
                pending_diff_note = "Bekleyen işlem sayısında iyileşme gözlemlendi."
            elif pending_diff > 0:
                pending_diff_class = "riq-diff-neg"
                pending_diff_note = "Bekleyen işlem sayısında artış gözlemlendi."
            else:
                pending_diff_class = "riq-diff-neutral"
                pending_diff_note = "Bekleyen işlem sayısında değişim yok."

            render_kpi_card(
                "Bekleyen İşlem Farkı",
                f"{pending_diff}",
                pending_diff_class,
            )
            st.caption(pending_diff_note)

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
        st.markdown("**Yüzde Değişimler**")
        render_percentage_change_rows(percentage_df)
        end_section_container()

        st.divider()
        st.subheader("Yönetici Raporu Grafikleri")

        # 1) Firma bazlı grafik
        start_graph_card("Firma Bazlı Toplam Tutar", "riq-graph-card-1")
        company_total_chart = visualizer_agent.create_company_total_amount_chart(current_df)
        st.plotly_chart(company_total_chart, use_container_width=True)
        end_graph_card()

        # 2) Departman bazlı grafik
        start_graph_card("Departman Bazlı Toplam Tutar", "riq-graph-card-2")
        department_total_chart = visualizer_agent.create_department_total_amount_chart(current_df)
        st.plotly_chart(department_total_chart, use_container_width=True)
        end_graph_card()

        # 3) Alt satırda yan yana karşılaştırma grafikleri
        chart_col_left, chart_col_right = st.columns(2)
        with chart_col_left:
            start_graph_card("Toplam Tutar Karşılaştırması", "riq-graph-card-3")
            total_amount_chart = visualizer_agent.create_total_amount_comparison_chart(
                previous_amount=comparison["total_amount"]["previous"],
                current_amount=comparison["total_amount"]["current"],
            )
            st.plotly_chart(total_amount_chart, use_container_width=True)
            end_graph_card()

        with chart_col_right:
            start_graph_card("Bekleyen İşlem Karşılaştırması", "riq-graph-card-4")
            pending_count_chart = visualizer_agent.create_pending_count_comparison_chart(
                previous_pending=comparison["pending_count"]["previous"],
                current_pending=comparison["pending_count"]["current"],
            )
            st.plotly_chart(pending_count_chart, use_container_width=True)
            end_graph_card()

        st.divider()
        executive_summary = create_executive_summary(current_results, comparison)
        executive_sections = create_executive_sections(current_results, comparison)
        render_executive_summary_card(executive_sections)

        # HTML yönetici raporunu üret ve indirme butonu göster
        report_generator_agent = ReportGeneratorAgent()
        html_report = report_generator_agent.generate_html_report(
            current_results=current_results,
            comparison=comparison,
            percentage_df=percentage_df,
            executive_summary=executive_summary,
            executive_sections=executive_sections,
            report_month=month_name,
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
                st.warning("Bu ay için kayıtlı rapor zaten mevcut.")
            else:
                summary_for_storage = create_summary_text_for_storage(executive_sections)
                is_saved = memory_agent.save_report(
                    report_date=report_date,
                    month_name=month_name,
                    total_amount=float(current_results["total_amount"]),
                    transaction_count=int(current_results["transaction_count"]),
                    company_count=int(current_results["company_count"]),
                    pending_count=int(current_results["pending_count"]),
                    summary=summary_for_storage,
                )
                if is_saved:
                    st.success("Rapor başarıyla hafızaya kaydedildi.")
                else:
                    st.warning("Bu ay için kayıtlı rapor zaten mevcut.")

        st.divider()
        st.subheader("Rapor Arşivi")

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
        st.markdown('<div class="riq-archive-card"><div class="riq-archive-title">Rapor Arşivi</div>', unsafe_allow_html=True)

        if reports_df.empty:
            st.info("Henüz kayıtlı rapor bulunmuyor.")
        else:
            unique_reports = memory_agent.get_unique_month_reports()
            unique_reports_df = pd.DataFrame(
                unique_reports,
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

            unique_reports_df["report_date"] = pd.to_datetime(
                unique_reports_df["report_date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
            unique_reports_df["report_date"] = unique_reports_df["report_date"].fillna("")

            month_filter = st.text_input(
                label="",
                placeholder="Rapor ayı ara...",
                label_visibility="collapsed",
            )
            if month_filter:
                filtered_reports = unique_reports_df[
                    unique_reports_df["month_name"].astype(str).str.contains(month_filter, case=False, na=False)
                ]
            else:
                filtered_reports = unique_reports_df

            if filtered_reports.empty:
                st.warning("Arama kriterine uygun rapor bulunamadı.")
            else:
                option_map = {
                    f"{row['month_name']}": int(row["id"])
                    for _, row in filtered_reports.iterrows()
                }
                selected_label = st.selectbox(
                    "",
                    options=list(option_map.keys()),
                    label_visibility="collapsed",
                )
                selected_id = option_map[selected_label]
                selected_report = memory_agent.get_report_by_id(selected_id)

                if selected_report:
                    (
                        report_id,
                        selected_report_date,
                        selected_month_name,
                        selected_total_amount,
                        selected_transaction_count,
                        selected_company_count,
                        selected_pending_count,
                        selected_summary,
                    ) = selected_report

                    detail_html = f"""
                    <div class="riq-summary-card" style="margin-top: 10px;">
                        <div class="riq-archive-subtitle">Seçili Rapor Detayı</div>
                        <div class="riq-detail-grid">
                            <div class="riq-detail-box"><div class="riq-detail-label">Rapor Ayı</div><div class="riq-detail-value">{selected_month_name}</div></div>
                            <div class="riq-detail-box"><div class="riq-detail-label">Rapor Tarihi</div><div class="riq-detail-value">{selected_report_date}</div></div>
                            <div class="riq-detail-box"><div class="riq-detail-label">Toplam Tutar</div><div class="riq-detail-value">{selected_total_amount:,.0f} TL</div></div>
                            <div class="riq-detail-box"><div class="riq-detail-label">İşlem Sayısı</div><div class="riq-detail-value">{selected_transaction_count}</div></div>
                            <div class="riq-detail-box"><div class="riq-detail-label">Firma Sayısı</div><div class="riq-detail-value">{selected_company_count}</div></div>
                            <div class="riq-detail-box"><div class="riq-detail-label">Bekleyen İşlem</div><div class="riq-detail-value">{selected_pending_count}</div></div>
                        </div>
                        <div class="riq-summary-item"><h4>Yönetici Özeti</h4><p>{selected_summary}</p></div>
                    </div>
                    """
                    st.markdown(detail_html, unsafe_allow_html=True)

                    # Silme işlemi için iki adımlı onay akışı
                    if "confirm_delete" not in st.session_state:
                        st.session_state["confirm_delete"] = False
                    if "delete_target_id" not in st.session_state:
                        st.session_state["delete_target_id"] = None

                    if st.button("Seçili Raporu Sil", key=f"delete_report_{selected_id}"):
                        st.session_state["confirm_delete"] = True
                        st.session_state["delete_target_id"] = selected_id

                    if (
                        st.session_state["confirm_delete"]
                        and st.session_state["delete_target_id"] == selected_id
                    ):
                        st.warning("Bu raporu silmek istediğinizden emin misiniz?")
                        confirm_col1, confirm_col2 = st.columns(2)

                        with confirm_col1:
                            if st.button("Evet, Sil", key=f"confirm_yes_{selected_id}"):
                                is_deleted = memory_agent.delete_report(selected_id)
                                st.session_state["confirm_delete"] = False
                                st.session_state["delete_target_id"] = None
                                if is_deleted:
                                    st.success("Seçili rapor başarıyla silindi.")
                                    st.rerun()
                                else:
                                    st.warning("Silinecek rapor bulunamadı.")

                        with confirm_col2:
                            if st.button("Vazgeç", key=f"confirm_no_{selected_id}"):
                                st.session_state["confirm_delete"] = False
                                st.session_state["delete_target_id"] = None
                                st.info("Silme işlemi iptal edildi.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Devam etmek için önceki ay ve güncel ay Excel dosyalarını yükleyin.")
