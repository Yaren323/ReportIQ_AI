import re
from datetime import datetime

import pandas as pd
import streamlit as st

from src.analyzer import AnalyzerAgent
from src.agent_report import AgentReportBuilder
from src.comparator import CompareAgent
from src.excel_agent import ExcelAgent, ExcelAgentConfig
from src.memory_db import MemoryAgent
from src.reconciliation_module import render_reconciliation_module
from src.report_generator import ReportGeneratorAgent
from src.visualizer import VisualizerAgent

st.set_page_config(page_title="ReportIQ AI", layout="wide")

REQUIRED_COLUMNS = [
    "Projeler",
    "Aylık Tutar (KDV Hariç - TL)",
    "Aylık Tutar (KDV Hariç - USD)",
]


def inject_dashboard_css():
    st.markdown(
        """
        <style>
        :root {
            --riq-bg: #0b0f17;
            --riq-text: #f8fafc;
            --riq-muted: #cbd5e1;
            --riq-border: #334155;
            --riq-card-bg: #111827;
            --riq-title: #f8fafc;
            --riq-pos: #86efac;
            --riq-neg: #fca5a5;
            --riq-neutral: #cbd5e1;
            --riq-prev-bg: #151b24;
            --riq-current-bg: #151b24;
            --riq-diff-bg: #151b24;
            --riq-summary-bg: #111827;
            --riq-summary-item-bg: #151b24;
            --riq-summary-item-border: #334155;
            --riq-graph-bg: #111827;
            --riq-button-bg: #93c5fd;
            --riq-button-text: #0b0f17;
        }
        html, body, [class*="css"] { font-size: 17px; color: var(--riq-text); }
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] section.main,
        [data-testid="stAppViewContainer"] > .main {
            background: var(--riq-bg) !important;
        }
        .stApp,
        [data-testid="stAppViewContainer"],
        .main,
        .block-container {
            background-color: #0b0f17 !important;
            color: #f8fafc !important;
        }
        [data-testid="stHeader"] {
            background-color: #0b0f17 !important;
        }
        .metric-card,
        .section-card,
        .upload-card,
        .riq-kpi,
        .riq-section-wrap,
        .riq-summary-card,
        .riq-archive-card {
            background-color: #111827 !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: inherit;
        }
        h1 { font-size: 2rem !important; }
        h2, h3 { font-size: 1.6rem !important; }
        .stCaption, .stMarkdown, .stText { color: var(--riq-text); }
        .riq-section-wrap {
            border-radius: 14px;
            padding: 14px;
            margin: 10px 0 16px 0;
            border: 1px solid var(--riq-border);
        }
        .riq-section-prev { background: var(--riq-prev-bg); }
        .riq-section-current { background: var(--riq-current-bg); }
        .riq-section-diff { background: var(--riq-diff-bg); }
        .riq-section-title {
            color: var(--riq-title);
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 10px;
            background: #1f2937;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 8px 10px;
        }
        .riq-kpi {
            background-color: var(--riq-card-bg);
            border: 1px solid var(--riq-border);
            border-radius: 10px;
            padding: 10px 12px;
            min-height: 112px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 10px;
        }
        .riq-kpi-label { color: var(--riq-muted); font-size: 1rem; margin-bottom: 3px; }
        .riq-kpi-value {
            color: var(--riq-text);
            font-size: 1.45rem;
            font-weight: 700;
            text-align: center;
            word-break: break-word;
            overflow-wrap: anywhere;
            line-height: 1.2;
        }
        .riq-kpi-project {
            text-align: center;
            white-space: normal;
            word-break: break-word;
            overflow-wrap: anywhere;
            font-size: 1.2rem;
            display: block;
        }
        .riq-diff-pos { color: var(--riq-pos); }
        .riq-diff-neg { color: var(--riq-neg); }
        .riq-diff-neutral { color: var(--riq-neutral); }
        .riq-graph-card {
            border-radius: 14px;
            border: 1px solid var(--riq-border);
            background: var(--riq-graph-bg);
            padding: 12px;
            margin: 8px 0 12px 0;
        }
        .riq-graph-title {
            color: var(--riq-title);
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .riq-summary-card {
            background: var(--riq-summary-bg);
            border: 1px solid var(--riq-border);
            border-radius: 14px;
            padding: 18px;
            margin: 10px 0 14px 0;
        }
        .riq-summary-title { color: var(--riq-title); font-size: 1.8rem; font-weight: 700; margin-bottom: 12px; }
        .riq-summary-item {
            background: var(--riq-summary-item-bg);
            border: 1px solid var(--riq-summary-item-border);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .riq-summary-item h4 { margin: 0 0 6px 0; font-size: 1.15rem; font-weight: 800; color: var(--riq-title); }
        .riq-summary-item p { margin: 0; font-size: 1.02rem; color: var(--riq-text); line-height: 1.7; }
        .riq-archive-card {
            background: var(--riq-summary-bg);
            border: 1px solid var(--riq-border);
            border-radius: 14px;
            padding: 18px;
            margin-top: 8px;
        }
        .riq-detail-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 10px;
        }
        .riq-detail-box {
            background: var(--riq-summary-item-bg);
            border: 1px solid var(--riq-summary-item-border);
            border-radius: 8px;
            padding: 10px;
        }
        .riq-detail-label { color: var(--riq-muted); font-size: 1.02rem; }
        .riq-detail-value { color: var(--riq-text); font-size: 1.15rem; font-weight: 800; margin-top: 4px; word-break: break-word; overflow-wrap: anywhere; }

        .stFileUploader, .stFileUploader > div {
            background: var(--riq-card-bg);
            border-color: var(--riq-border) !important;
            color: var(--riq-text) !important;
        }
        .stButton > button, .stDownloadButton > button {
            background: var(--riq-button-bg);
            color: var(--riq-button-text);
            border: 1px solid var(--riq-border);
            border-radius: 10px;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            filter: brightness(1.06);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def start_section_container(section_class, title):
    st.markdown(
        f'<div class="riq-section-wrap {section_class}"><div class="riq-section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def end_section_container():
    st.markdown("</div>", unsafe_allow_html=True)


def start_graph_card(title):
    st.markdown(
        f'<div class="riq-graph-card"><div class="riq-graph-title">{title}</div>',
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


def get_missing_columns(df):
    return [column for column in REQUIRED_COLUMNS if column not in df.columns]


def parse_month_name(file_obj, fallback="Bilinmiyor"):
    if file_obj is None:
        return fallback
    file_name = str(getattr(file_obj, "name", ""))

    match = re.search(r"(20\d{2})[-_\.](0[1-9]|1[0-2])", file_name)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    match = re.search(r"(0[1-9]|1[0-2])[-_\.](20\d{2})", file_name)
    if match:
        return f"{match.group(2)}-{match.group(1)}"

    return fallback


def create_executive_sections(previous_results, current_results, comparison_results):
    total_tl_diff = comparison_results["total_tl_diff"]
    total_usd_diff = comparison_results["total_usd_diff"]
    project_count_diff = comparison_results["project_count_diff"]

    new_projects = comparison_results["new_projects"]
    removed_projects = comparison_results["removed_projects"]

    if len(new_projects) == 0 and len(removed_projects) == 0:
        project_flow = (
            "Proje portföyünde net bir giriş/çıkış görülmemektedir; bu durum operasyonel istikrarı destekler. "
            "Mevcut projelerde hacim değişimleri takip edilerek büyümenin derinleşme mi yoksa dağılım etkisi mi olduğu doğrulanmalıdır."
        )
    else:
        project_flow = (
            f"Bu dönemde {len(new_projects)} yeni proje portföye eklenmiş, {len(removed_projects)} proje portföyden çıkmıştır. "
            "Portföy bileşimindeki bu hareketlilik, gelir kalitesinin sürdürülebilirliği açısından proje bazlı katkı ve kayıp analizini kritik hale getirmektedir."
        )

    general = (
        f"Güncel ay toplam TL {current_results['total_tl']:,.2f}, toplam USD {current_results['total_usd']:,.2f}, "
        f"proje sayısı {current_results['project_count']} olarak hesaplanmıştır."
    )

    financial_comment = (
        f"Önceki döneme göre TL bazında {total_tl_diff:,.2f} TL, USD bazında {total_usd_diff:,.2f} USD fark oluşmuştur. "
        "Bu değişim yalnızca toplam seviyede değil, proje bazlı yoğunlaşma açısından da değerlendirilmelidir. "
        "Özellikle yüksek tutarlı projelerde hacim değişimi, nakit akışı planı ve kaynak tahsisi üzerindeki etkilerle birlikte okunmalıdır."
    )

    top_projects = (
        f"TL bazında en yüksek proje '{current_results['max_tl_project']}' olup {current_results['max_tl_amount']:,.2f} TL seviyesindedir. "
        f"USD bazında en yüksek proje '{current_results['max_usd_project']}' olup {current_results['max_usd_amount']:,.2f} USD seviyesindedir. "
        "Bu iki proje, dönem performansının yönünü belirleyen ana kaldıraçlar olarak ayrı bir yönetim takibine alınmalıdır."
    )

    risks = []
    if total_tl_diff > 0:
        risks.append(
            "TL toplamındaki artışın hangi projelerden kaynaklandığı ayrıştırılmalı, tekil projelerde aşırı yoğunlaşma riski için erken uyarı eşikleri belirlenmelidir."
        )
    else:
        risks.append(
            "TL toplamındaki daralma eğilimi, proje teslim takvimi ve tahsilat zamanlaması ile birlikte incelenerek dönemsel sapma mı yapısal düşüş mü olduğu netleştirilmelidir."
        )
    if total_usd_diff < 0:
        risks.append(
            "USD bazlı gelirde gerileme bulunduğundan, döviz gelir kaybının proje kırılımında kaynağı tespit edilip sözleşme/yenileme riskleri proaktif biçimde yönetilmelidir."
        )
    else:
        risks.append(
            "USD gelir tarafındaki görünüm pozitif olsa da kur oynaklığı ve proje bazlı sürdürülebilirlik birlikte değerlendirilerek korunma senaryoları güncellenmelidir."
        )
    if project_count_diff > 0:
        risks.append(
            "Proje adedindeki artış, operasyonel kapasiteyi zorlayabileceğinden yeni projelerin marj, ödeme disiplini ve teslim performansı ayrı KPI setiyle izlenmelidir."
        )
    elif project_count_diff < 0:
        risks.append(
            "Proje adedindeki azalışın toplam gelire etkisi ve kaybedilen proje segmentleri analiz edilerek satış boru hattında telafi aksiyonları planlanmalıdır."
        )
    risks_text = " ".join(risks)

    actions = (
        "Yönetim seviyesinde ilk adım olarak TL ve USD farkını oluşturan ilk 5 projenin katkı analizi çıkarılmalı; büyümeyi taşıyan projeler için kapasite ve tahsilat planı eş zamanlı güncellenmelidir. "
        "USD tarafında zayıflama görülen projelerde fiyatlama, kapsam ve sözleşme koşulları yeniden değerlendirilerek gelir erozyonunu önleyecek düzeltici aksiyonlar devreye alınmalıdır. "
        "Yeni eklenen projeler için ilk 60 günlük performans izleme çerçevesi tanımlanmalı; çıkarılan projelerin etkisi için neden analizi ve telafi pipeline'ı yönetim raporuna bağlanmalıdır. "
        "En yüksek TL ve USD proje sahipleriyle periyodik yönetim gözden geçirme toplantıları yapılarak bütçe sapmaları, riskler ve aksiyon sahiplikleri netleştirilmelidir."
    )

    return {
        "Genel Durum Özeti": general,
        "Finansal Değişim Yorumu": financial_comment,
        "Proje Hareketliliği Yorumu": project_flow,
        "En Yüksek Tutar Getiren Projeler": top_projects,
        "Riskler / Dikkat Edilmesi Gerekenler": risks_text,
        "Önerilen Aksiyonlar": actions,
    }


def render_executive_summary_card(executive_sections):
    summary_html = '<div class="riq-summary-card"><div class="riq-summary-title">AI Yönetici Özeti</div>'
    for title, text in executive_sections.items():
        summary_html += f'<div class="riq-summary-item"><h4>{title}</h4><p>{text}</p></div>'
    summary_html += "</div>"
    st.markdown(summary_html, unsafe_allow_html=True)


def create_summary_text_for_storage(executive_sections):
    return "\n".join([f"{title}: {text}" for title, text in executive_sections.items()])


def format_diff_value(value, suffix):
    if isinstance(value, (int, float)):
        return f"{value:,.2f} {suffix}" if suffix else f"{value:,.2f}"
    return str(value)




def render_excel_agent_test_area():
    st.subheader("Excel Agent Test Alan\u0131")
    st.caption("Bu alan mevcut rapor analizinden ba\u011f\u0131ms\u0131zd\u0131r. Her sayfa ayr\u0131 analiz edilir.")

    uploaded_test_excel = st.file_uploader(
        "Analiz i\u00e7in bir Excel dosyas\u0131 y\u00fckleyin",
        type=["xlsx", "xls"],
        key="excel_agent_test_uploader",
        accept_multiple_files=False,
    )

    if not uploaded_test_excel:
        st.info("Agent testi i\u00e7in bir Excel dosyas\u0131 y\u00fckleyin.")
        return

    if st.button("Agent ile Analiz Et", key="run_excel_agent_test"):
        try:
            excel_agent = ExcelAgent(ExcelAgentConfig(sample_size=1000, preview_size=20))
            analysis_result = excel_agent.analyze_excel(uploaded_test_excel)
            st.session_state["excel_agent_last_result"] = analysis_result
        except ValueError as exc:
            st.error(f"Excel analiz hatas\u0131: {exc}")
            return
        except Exception as exc:
            st.error(f"Beklenmeyen bir hata olu\u015ftu: {exc}")
            return

    analysis_result = st.session_state.get("excel_agent_last_result")
    if not analysis_result:
        st.warning("Analizi g\u00f6rmek i\u00e7in 'Agent ile Analiz Et' butonuna t\u0131klay\u0131n.")
        return

    if analysis_result.get("file_name") != getattr(uploaded_test_excel, "name", ""):
        st.info("Y\u00fcklenen dosya de\u011fi\u015fti. L\u00fctfen analiz butonuna tekrar bas\u0131n.")
        return

    st.markdown("### Hızlı Yönetici Özeti")
    f1, f2, f3 = st.columns(3)
    with f1:
        render_kpi_card("Dosyada Bulunan Sheet Sayısı", str(analysis_result["sheet_count"]))
    with f2:
        render_kpi_card("Başlığı Olan Toplam Sütun Sayısı", f"{analysis_result['total_titled_columns']:,}")
    with f3:
        render_kpi_card("Toplam Veri Satırı Sayısı", f"{analysis_result['total_data_rows']:,}")

    st.markdown("### Excel'de Bulunan Toplam Satırları")
    total_rows_summary = analysis_result.get("total_rows_summary", [])
    if not total_rows_summary:
        st.info("Toplam satırı tespit edilmedi.")
    else:
        for item in total_rows_summary:
            with st.expander(f"{item['sheet_name']} - Toplam Satırı: {item['toplam_satiri_sayisi']}", expanded=False):
                st.write(f"Header benzeri satır sayısı: {item.get('header_benzeri_satir_sayisi', 0)}")
                rows = item.get("satirlar", [])
                if not rows:
                    st.write("Bu sayfada toplam satırı bulunamadı.")
                else:
                    for idx, row in enumerate(rows, start=1):
                        st.write(f"{idx}. Metin: {row.get('metin', '-')}")
                        numeric_values = row.get("sayisal_degerler", {})
                        if numeric_values:
                            st.json(numeric_values)

    sheet_errors = analysis_result.get("sheet_errors", [])
    if sheet_errors:
        st.warning("Bazı sayfalarda analiz hatası oluştu, diğer sayfalar gösterilmeye devam ediyor.")
        for err in sheet_errors:
            st.caption(f"{err['sheet_name']}: {err['hata']}")

    for sheet_report in analysis_result["sheets"]:
        try:
            AgentReportBuilder.render_sheet_card(st, sheet_report, render_kpi_card)
        except Exception as exc:
            st.error(f"{sheet_report.get('sheet_name', 'Bilinmeyen Sayfa')} kartı oluşturulurken hata alındı: {exc}")
            continue


def render_existing_dashboard():

    st.title("ReportIQ AI Yönetici Dashboard")
    st.caption("Önceki ay ve güncel ay proje bazlı ödeme raporlarını karşılaştırır.")
    inject_dashboard_css()
    
    if "previous_uploaded_file" not in st.session_state:
        st.session_state["previous_uploaded_file"] = None
    if "current_uploaded_file" not in st.session_state:
        st.session_state["current_uploaded_file"] = None
    
    upload_col1, upload_col2 = st.columns(2)
    with upload_col1:
        if st.session_state["previous_uploaded_file"] is None:
            previous_input_file = st.file_uploader(
                "Önceki ay raporu",
                type=["xlsx", "xls"],
                key="previous_month_file_input",
                accept_multiple_files=False,
            )
            if previous_input_file is not None:
                st.session_state["previous_uploaded_file"] = previous_input_file
                st.rerun()
        else:
            previous_name = getattr(st.session_state["previous_uploaded_file"], "name", "Bilinmeyen dosya")
            st.success(f"Dosya yüklendi: {previous_name}")
            prev_btn_col1, prev_btn_col2 = st.columns(2)
            with prev_btn_col1:
                if st.button("Dosyayı değiştir", key="change_previous_file"):
                    st.session_state["previous_uploaded_file"] = None
                    st.session_state.pop("previous_month_file_input", None)
                    st.rerun()
            with prev_btn_col2:
                if st.button("Temizle", key="clear_previous_file"):
                    st.session_state["previous_uploaded_file"] = None
                    st.session_state.pop("previous_month_file_input", None)
                    st.rerun()
    with upload_col2:
        if st.session_state["current_uploaded_file"] is None:
            current_input_file = st.file_uploader(
                "Güncel ay raporu",
                type=["xlsx", "xls"],
                key="current_month_file_input",
                accept_multiple_files=False,
            )
            if current_input_file is not None:
                st.session_state["current_uploaded_file"] = current_input_file
                st.rerun()
        else:
            current_name = getattr(st.session_state["current_uploaded_file"], "name", "Bilinmeyen dosya")
            st.success(f"Dosya yüklendi: {current_name}")
            curr_btn_col1, curr_btn_col2 = st.columns(2)
            with curr_btn_col1:
                if st.button("Dosyayı değiştir", key="change_current_file"):
                    st.session_state["current_uploaded_file"] = None
                    st.session_state.pop("current_month_file_input", None)
                    st.rerun()
            with curr_btn_col2:
                if st.button("Temizle", key="clear_current_file"):
                    st.session_state["current_uploaded_file"] = None
                    st.session_state.pop("current_month_file_input", None)
                    st.rerun()
    
    previous_file = st.session_state["previous_uploaded_file"]
    current_file = st.session_state["current_uploaded_file"]
    
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
            previous_analyzer = AnalyzerAgent(previous_df)
            current_analyzer = AnalyzerAgent(current_df)
            previous_results = previous_analyzer.run_full_analysis()
            current_results = current_analyzer.run_full_analysis()
    
            with st.expander("Debug - Excel parse kontrolü"):
                st.markdown("**Önceki Ay**")
                st.dataframe(previous_results["debug_df"], use_container_width=True, hide_index=True)
                st.markdown("**Güncel Ay**")
                st.dataframe(current_results["debug_df"], use_container_width=True, hide_index=True)
    
            compare_agent = CompareAgent(previous_df, current_df)
            comparison_results = compare_agent.run_comparison()
            # Aylık fark metrikleri yalnızca üstte doğrulanmış analiz sonuçlarından türetilir.
            comparison_results["total_tl_diff"] = current_results["total_tl"] - previous_results["total_tl"]
            comparison_results["total_usd_diff"] = current_results["total_usd"] - previous_results["total_usd"]
            comparison_results["project_count_diff"] = current_results["project_count"] - previous_results["project_count"]
    
            previous_projects = set(
                previous_analyzer.analysis_df["Projeler"].dropna().astype(str).str.strip()
            )
            current_projects = set(
                current_analyzer.analysis_df["Projeler"].dropna().astype(str).str.strip()
            )
            comparison_results["new_projects"] = sorted(current_projects - previous_projects)
            comparison_results["removed_projects"] = sorted(previous_projects - current_projects)
    
            visualizer_agent = VisualizerAgent()
            memory_agent = MemoryAgent()
            db_ready = memory_agent.create_database()
            if not db_ready and memory_agent.get_schema_warning():
                st.warning(memory_agent.get_schema_warning())
    
            report_date = datetime.now().strftime("%Y-%m-%d")
            month_name = parse_month_name(current_file)
    
            st.divider()
            start_section_container("riq-section-prev", "Önceki Ay Verileri")
            p1, p2, p3 = st.columns(3)
            with p1:
                render_kpi_card("Toplam TL", f"{previous_results['total_tl']:,.2f} TL")
            with p2:
                render_kpi_card("Toplam USD", f"{previous_results['total_usd']:,.2f} USD")
            with p3:
                render_kpi_card("Proje Sayısı", str(previous_results["project_count"]))
    
            p4, p5, p6 = st.columns(3)
            with p4:
                render_kpi_card("En Yüksek TL Tutarı", f"{previous_results['max_tl_amount']:,.2f} TL")
            with p5:
                render_kpi_card("En Yüksek TL Projesi", previous_results["max_tl_project"], "riq-kpi-project")
            with p6:
                render_kpi_card("En Yüksek USD Projesi", previous_results["max_usd_project"], "riq-kpi-project")
            end_section_container()
    
            start_section_container("riq-section-current", "Güncel Ay Verileri")
            c1, c2, c3 = st.columns(3)
            with c1:
                render_kpi_card("Toplam TL", f"{current_results['total_tl']:,.2f} TL")
            with c2:
                render_kpi_card("Toplam USD", f"{current_results['total_usd']:,.2f} USD")
            with c3:
                render_kpi_card("Proje Sayısı", str(current_results["project_count"]))
    
            c4, c5, c6 = st.columns(3)
            with c4:
                render_kpi_card("En Yüksek TL Tutarı", f"{current_results['max_tl_amount']:,.2f} TL")
            with c5:
                render_kpi_card("En Yüksek TL Projesi", current_results["max_tl_project"], "riq-kpi-project")
            with c6:
                render_kpi_card("En Yüksek USD Projesi", current_results["max_usd_project"], "riq-kpi-project")
            end_section_container()
    
            start_section_container("riq-section-diff", "Aylık Değişim / Fark")
            d1, d2, d3 = st.columns(3)
    
            def diff_class(value):
                if value > 0:
                    return "riq-diff-pos"
                if value < 0:
                    return "riq-diff-neg"
                return "riq-diff-neutral"
    
            with d1:
                render_kpi_card("Toplam TL Farkı", format_diff_value(comparison_results["total_tl_diff"], "TL"), diff_class(comparison_results["total_tl_diff"]))
            with d2:
                render_kpi_card("Toplam USD Farkı", format_diff_value(comparison_results["total_usd_diff"], "USD"), diff_class(comparison_results["total_usd_diff"]))
            with d3:
                render_kpi_card("Proje Sayısı Farkı", str(comparison_results["project_count_diff"]), diff_class(comparison_results["project_count_diff"]))
    
            st.caption(f"Yeni Projeler: {len(comparison_results['new_projects'])} | Çıkarılan Projeler: {len(comparison_results['removed_projects'])}")
            end_section_container()
    
            st.divider()
            st.subheader("Proje Bazlı Grafikler")
    
            start_graph_card("Proje Bazlı TL Tutar Grafiği")
            st.plotly_chart(visualizer_agent.create_project_tl_chart(current_df), use_container_width=True)
            end_graph_card()
    
            start_graph_card("Proje Bazlı USD Tutar Grafiği")
            st.plotly_chart(visualizer_agent.create_project_usd_chart(current_df), use_container_width=True)
            end_graph_card()
    
            g1, g2 = st.columns(2)
            with g1:
                start_graph_card("Önceki Ay / Güncel Ay Toplam TL Karşılaştırması")
                st.plotly_chart(
                    visualizer_agent.create_total_tl_comparison_chart(
                        previous_results["total_tl"], current_results["total_tl"]
                    ),
                    use_container_width=True,
                )
                end_graph_card()
            with g2:
                start_graph_card("Önceki Ay / Güncel Ay Toplam USD Karşılaştırması")
                st.plotly_chart(
                    visualizer_agent.create_total_usd_comparison_chart(
                        previous_results["total_usd"], current_results["total_usd"]
                    ),
                    use_container_width=True,
                )
                end_graph_card()
    
            g3, g4 = st.columns(2)
            with g3:
                start_graph_card("Proje Bazlı TL Değişim Grafiği")
                st.plotly_chart(
                    visualizer_agent.create_project_tl_change_chart(comparison_results["project_changes"]),
                    use_container_width=True,
                )
                end_graph_card()
            with g4:
                start_graph_card("Proje Bazlı USD Değişim Grafiği")
                st.plotly_chart(
                    visualizer_agent.create_project_usd_change_chart(comparison_results["project_changes"]),
                    use_container_width=True,
                )
                end_graph_card()
    
            st.divider()
            executive_sections = create_executive_sections(previous_results, current_results, comparison_results)
            render_executive_summary_card(executive_sections)
    
            report_generator_agent = ReportGeneratorAgent()
            html_report = report_generator_agent.generate_html_report(
                current_results=current_results,
                comparison_results=comparison_results,
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
                        total_tl=current_results["total_tl"],
                        total_usd=current_results["total_usd"],
                        project_count=current_results["project_count"],
                        average_tl=0.0,
                        average_usd=0.0,
                        max_tl_project=current_results["max_tl_project"],
                        max_tl_amount=current_results["max_tl_amount"],
                        max_usd_project=current_results["max_usd_project"],
                        max_usd_amount=current_results["max_usd_amount"],
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
                    "total_tl",
                    "total_usd",
                    "project_count",
                    "average_tl",
                    "average_usd",
                    "max_tl_project",
                    "max_tl_amount",
                    "max_usd_project",
                    "max_usd_amount",
                    "summary",
                ],
            )
    
            st.markdown('<div class="riq-archive-card">', unsafe_allow_html=True)
    
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
                        "total_tl",
                        "total_usd",
                        "project_count",
                        "average_tl",
                        "average_usd",
                        "max_tl_project",
                        "max_tl_amount",
                        "max_usd_project",
                        "max_usd_amount",
                        "summary",
                    ],
                )
    
                month_filter = st.text_input("", placeholder="Rapor ayı ara...", label_visibility="collapsed")
                if month_filter:
                    filtered_reports = unique_reports_df[
                        unique_reports_df["month_name"].astype(str).str.contains(month_filter, case=False, na=False)
                    ]
                else:
                    filtered_reports = unique_reports_df
    
                if filtered_reports.empty:
                    st.warning("Arama kriterine uygun rapor bulunamadı.")
                else:
                    option_map = {f"{row['month_name']}": int(row["id"]) for _, row in filtered_reports.iterrows()}
                    selected_label = st.selectbox("", options=list(option_map.keys()), label_visibility="collapsed")
                    selected_id = option_map[selected_label]
                    selected_report = memory_agent.get_report_by_id(selected_id)
    
                    if selected_report:
                        (
                            report_id,
                            selected_report_date,
                            selected_month_name,
                            selected_total_tl,
                            selected_total_usd,
                            selected_project_count,
                            _selected_average_tl,
                            _selected_average_usd,
                            selected_max_tl_project,
                            selected_max_tl_amount,
                            selected_max_usd_project,
                            selected_max_usd_amount,
                            selected_summary,
                        ) = selected_report
    
                        detail_html = f"""
                        <div class="riq-summary-card" style="margin-top: 10px;">
                            <div class="riq-detail-grid">
                                <div class="riq-detail-box"><div class="riq-detail-label">Ay</div><div class="riq-detail-value">{selected_month_name}</div></div>
                                <div class="riq-detail-box"><div class="riq-detail-label">Toplam TL</div><div class="riq-detail-value">{selected_total_tl:,.2f} TL</div></div>
                                <div class="riq-detail-box"><div class="riq-detail-label">Toplam USD</div><div class="riq-detail-value">{selected_total_usd:,.2f} USD</div></div>
                                <div class="riq-detail-box"><div class="riq-detail-label">Proje Sayısı</div><div class="riq-detail-value">{selected_project_count}</div></div>
                                <div class="riq-detail-box"><div class="riq-detail-label">En Yüksek TL Projesi</div><div class="riq-detail-value">{selected_max_tl_project}</div></div>
                                <div class="riq-detail-box"><div class="riq-detail-label">En Yüksek TL Tutarı</div><div class="riq-detail-value">{selected_max_tl_amount:,.2f} TL</div></div>
                                <div class="riq-detail-box"><div class="riq-detail-label">En Yüksek USD Projesi</div><div class="riq-detail-value">{selected_max_usd_project}</div></div>
                                <div class="riq-detail-box"><div class="riq-detail-label">En Yüksek USD Tutarı</div><div class="riq-detail-value">{selected_max_usd_amount:,.2f} USD</div></div>
                            </div>
                            <div class="riq-summary-item"><h4>Yönetici Özeti</h4><p>{selected_summary}</p></div>
                        </div>
                        """
                        st.markdown(detail_html, unsafe_allow_html=True)
    
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
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                if st.button("Evet, Sil", key=f"confirm_yes_{selected_id}"):
                                    is_deleted = memory_agent.delete_report(selected_id)
                                    st.session_state["confirm_delete"] = False
                                    st.session_state["delete_target_id"] = None
                                    if is_deleted:
                                        st.success("Seçili rapor başarıyla silindi.")
                                        st.rerun()
                                    else:
                                        st.warning("Silinecek rapor bulunamadı.")
                            with cc2:
                                if st.button("Vazgeç", key=f"confirm_no_{selected_id}"):
                                    st.session_state["confirm_delete"] = False
                                    st.session_state["delete_target_id"] = None
                                    st.info("Silme işlemi iptal edildi.")
    
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Devam etmek için önceki ay ve güncel ay proje bazlı ödeme Excel dosyalarını yükleyin.")

inject_dashboard_css()
tab_main, tab_agent, tab_reconciliation = st.tabs(
    ["Mevcut Rapor Analizi", "Excel Agent Test Alanı", "AI Mutabakat ve Kapasite Karşılaştırma"]
)

with tab_main:
    render_existing_dashboard()

with tab_agent:
    render_excel_agent_test_area()

with tab_reconciliation:
    render_reconciliation_module()
