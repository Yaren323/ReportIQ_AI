from datetime import datetime


class ReportGeneratorAgent:
    # Bu sınıf, yönetici için indirilebilir HTML raporu üretir.

    def generate_html_report(
        self,
        current_results,
        comparison,
        percentage_df,
        executive_summary,
        executive_sections=None,
        report_month="Bilinmiyor",
    ):
        report_title = f"ReportIQ Yönetici Raporu - [{report_month}]"
        # KPI özetini kutular halinde hazırlıyoruz.
        kpi_cards_html = f"""
        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-label">Toplam Tutar</div><div class="kpi-value">{current_results['total_amount']:,.0f} TL</div></div>
            <div class="kpi-card"><div class="kpi-label">İşlem Sayısı</div><div class="kpi-value">{current_results['transaction_count']}</div></div>
            <div class="kpi-card"><div class="kpi-label">Firma Sayısı</div><div class="kpi-value">{current_results['company_count']}</div></div>
            <div class="kpi-card"><div class="kpi-label">Bekleyen İşlem</div><div class="kpi-value">{current_results['pending_count']}</div></div>
        </div>
        """

        # Karşılaştırma özetini kısa satırlar halinde hazırlıyoruz.
        comparison_rows = ""
        metric_labels = {
            "total_amount": "Toplam Tutar",
            "transaction_count": "İşlem Sayısı",
            "company_count": "Firma Sayısı",
            "pending_count": "Bekleyen İşlem",
        }
        for key, label in metric_labels.items():
            metric = comparison[key]
            previous_value = metric["previous"]
            current_value = metric["current"]
            difference_value = metric["difference"]
            percentage_value = metric["percentage_change"]

            if key == "total_amount":
                previous_value = f"{previous_value:,.0f} TL"
                current_value = f"{current_value:,.0f} TL"
                difference_value = f"{difference_value:,.0f} TL"

            comparison_rows += (
                f'<div class="row-item"><span class="row-title">{label}</span>'
                f'<span class="row-text">Önceki: <strong>{previous_value}</strong> | '
                f'Güncel: <strong>{current_value}</strong> | '
                f'Fark: <strong>{difference_value}</strong> | '
                f'Değişim: <strong>%{percentage_value:.2f}</strong></span></div>'
            )

        # Yüzde değişim satırlarını kısa kartlara çeviriyoruz.
        percentage_rows = ""
        for _, row in percentage_df.iterrows():
            percentage_rows += (
                f'<div class="row-item"><span class="row-title">{row["Metrik"]}</span>'
                f'<span class="row-text"><strong>%{row["Yüzde Değişim (%)"]:.2f}</strong></span></div>'
            )

        # Yönetici özeti bölümlerini gösteriyoruz.
        if executive_sections is None:
            executive_sections = {
                "Genel Durum": executive_summary,
                "Öne Çıkan Değişimler": "",
                "Riskli Noktalar": "",
                "Önerilen Aksiyonlar": "",
            }

        summary_sections_html = ""
        for title, text in executive_sections.items():
            css_class = ""
            if title == "Riskli Noktalar":
                css_class = "summary-risk"
            elif title == "Önerilen Aksiyonlar":
                css_class = "summary-action"
            summary_sections_html += (
                f'<div class="summary-item {css_class}"><h3>{title}</h3><p>{text}</p></div>'
            )

        report_date = datetime.now().strftime("%Y-%m-%d")

        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8" />
            <title>{report_title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 24px;
                    line-height: 1.45;
                    background: #edf2f7;
                    color: #243447;
                }}
                .title-card {{
                    background: #1f3a5b;
                    border: 1px solid #2b4a6e;
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 14px;
                    text-align: center;
                }}
                .title-card h1 {{
                    margin: 0;
                    font-size: 32px;
                    color: #f4f8fc;
                }}
                .title-card p {{
                    margin: 8px 0 0 0;
                    color: #d8e4f0;
                    font-size: 17px;
                }}
                .section {{
                    background: #ffffff;
                    border: 1px solid #d8e1eb;
                    border-radius: 12px;
                    padding: 14px;
                    margin-bottom: 12px;
                }}
                .section h2 {{
                    margin: 0 0 10px 0;
                    font-size: 24px;
                    color: #1f3a5b;
                }}
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, minmax(0, 1fr));
                    gap: 10px;
                }}
                .kpi-card {{
                    background: #eef4fa;
                    border: 1px solid #d4e0ec;
                    border-radius: 10px;
                    padding: 10px;
                }}
                .kpi-label {{
                    color: #4a6078;
                    font-size: 16px;
                }}
                .kpi-value {{
                    color: #1f3a5b;
                    font-size: 26px;
                    font-weight: 700;
                    margin-top: 4px;
                }}
                .two-column-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                    margin-bottom: 12px;
                }}
                .row-item {{
                    display: flex;
                    justify-content: space-between;
                    gap: 12px;
                    padding: 8px 10px;
                    background: #f3f7fb;
                    border: 1px solid #dbe6f1;
                    border-radius: 8px;
                    margin-bottom: 8px;
                }}
                .row-title {{
                    font-weight: 700;
                    color: #2c435d;
                    font-size: 16px;
                }}
                .row-text {{
                    color: #3a4f67;
                    text-align: right;
                    font-size: 16px;
                }}
                .summary-item {{
                    background: #f5f8fc;
                    border: 1px solid #d8e4ef;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 8px;
                }}
                .summary-item h3 {{
                    margin: 0 0 6px 0;
                    font-size: 21px;
                    color: #1f3a5b;
                }}
                .summary-item p {{
                    margin: 0;
                    color: #344b63;
                    font-size: 17px;
                    line-height: 1.6;
                }}
                .summary-risk {{
                    background: #fff3ee;
                    border-color: #f0d4c7;
                }}
                .summary-action {{
                    background: #eef8f2;
                    border-color: #cde7d7;
                }}
            </style>
        </head>
        <body>
            <div class="title-card">
                <h1>{report_title}</h1>
                <p>Rapor Oluşturma Tarihi: <strong>{report_date}</strong></p>
            </div>

            <div class="section">
                <h2>Güncel Ay KPI Özeti</h2>
                {kpi_cards_html}
            </div>

            <div class="two-column-grid">
                <div class="section">
                    <h2>Karşılaştırma Özeti</h2>
                    {comparison_rows}
                </div>
                <div class="section">
                    <h2>Yüzde Değişimler</h2>
                    {percentage_rows}
                </div>
            </div>

            <div class="section">
                <h2>AI Yönetici Özeti</h2>
                {summary_sections_html}
            </div>
        </body>
        </html>
        """

        return html_content
