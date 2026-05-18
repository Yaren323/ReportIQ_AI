from datetime import datetime


class ReportGeneratorAgent:
    # Bu sınıf, yönetici için indirilebilir HTML raporu üretir.

    def generate_html_report(
        self,
        current_results,
        comparison,
        percentage_df,
        executive_summary,
        report_title="ReportIQ AI Yönetici Raporu",
    ):
        # KPI özeti satırlarını HTML için hazırlıyoruz.
        kpi_html = f"""
        <ul>
            <li><strong>Toplam Tutar:</strong> {current_results['total_amount']:,.0f} TL</li>
            <li><strong>İşlem Sayısı:</strong> {current_results['transaction_count']}</li>
            <li><strong>Firma Sayısı:</strong> {current_results['company_count']}</li>
            <li><strong>Bekleyen İşlem:</strong> {current_results['pending_count']}</li>
        </ul>
        """

        # Karşılaştırma sonuçlarını okunabilir listeye çeviriyoruz.
        comparison_html = "<ul>"
        metric_labels = {
            "total_amount": "Toplam Tutar",
            "transaction_count": "İşlem Sayısı",
            "company_count": "Firma Sayısı",
            "pending_count": "Bekleyen İşlem",
        }

        for key, label in metric_labels.items():
            metric = comparison[key]
            comparison_html += (
                f"<li><strong>{label}:</strong> "
                f"Önceki: {metric['previous']}, "
                f"Güncel: {metric['current']}, "
                f"Fark: {metric['difference']}, "
                f"Değişim: %{metric['percentage_change']:.2f}</li>"
            )

        comparison_html += "</ul>"

        # Yüzde değişim tablosunu HTML tablo formatına çeviriyoruz.
        percentage_rows = ""
        for _, row in percentage_df.iterrows():
            percentage_rows += (
                f"<tr><td>{row['Metrik']}</td><td>%{row['Yüzde Değişim (%)']:.2f}</td></tr>"
            )

        percentage_html = f"""
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <thead>
                <tr>
                    <th>Metrik</th>
                    <th>Yüzde Değişim</th>
                </tr>
            </thead>
            <tbody>
                {percentage_rows}
            </tbody>
        </table>
        """

        # Markdown başlıklarını sade HTML başlıklarına çeviriyoruz.
        summary_html = executive_summary
        summary_html = summary_html.replace("### ", "<h3>")
        summary_html = summary_html.replace("\n\n", "</h3><p>")
        summary_html = summary_html.replace("\n", "</p><p>")
        summary_html = f"<p>{summary_html}</p>"

        report_date = datetime.now().strftime("%Y-%m-%d")

        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8" />
            <title>{report_title}</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 24px; line-height: 1.5;">
            <h1>{report_title}</h1>

            <h2>Güncel Ay KPI Özeti</h2>
            {kpi_html}

            <h2>Karşılaştırma Sonuçları</h2>
            {comparison_html}

            <h2>Yüzde Değişimler</h2>
            {percentage_html}

            <h2>AI Yönetici Özeti</h2>
            {summary_html}

            <h2>Rapor Oluşturma Tarihi</h2>
            <p>{report_date}</p>
        </body>
        </html>
        """

        return html_content
