from datetime import datetime


class ReportGeneratorAgent:
    # Bu sınıf, yönetici için indirilebilir HTML raporu üretir.

    def _format_number(self, value, suffix=""):
        return f"{float(value):,.2f} {suffix}".strip()

    def _build_kpi_summary_html(self, current_results):
        return f"""
        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-label">Toplam TL</div><div class="kpi-value">{self._format_number(current_results['total_tl'], 'TL')}</div></div>
            <div class="kpi-card"><div class="kpi-label">Toplam USD</div><div class="kpi-value">{self._format_number(current_results['total_usd'], 'USD')}</div></div>
            <div class="kpi-card"><div class="kpi-label">Proje Sayısı</div><div class="kpi-value">{int(current_results['project_count'])}</div></div>
        </div>
        """

    def _build_peak_amounts_html(self, current_results):
        return f"""
        <div class="two-col-grid">
            <div class="detail-card">
                <div class="detail-title">En Yüksek TL Tutar</div>
                <div class="detail-project">{current_results['max_tl_project']}</div>
                <div class="detail-amount">{self._format_number(current_results['max_tl_amount'], 'TL')}</div>
            </div>
            <div class="detail-card">
                <div class="detail-title">En Yüksek USD Tutar</div>
                <div class="detail-project">{current_results['max_usd_project']}</div>
                <div class="detail-amount">{self._format_number(current_results['max_usd_amount'], 'USD')}</div>
            </div>
        </div>
        """

    def _build_comparison_summary_html(self, comparison_results):
        return f"""
        <div class="row-item"><span class="row-title">TL Farkı</span><span class="row-text"><strong>{self._format_number(comparison_results['total_tl_diff'], 'TL')}</strong></span></div>
        <div class="row-item"><span class="row-title">USD Farkı</span><span class="row-text"><strong>{self._format_number(comparison_results['total_usd_diff'], 'USD')}</strong></span></div>
        <div class="row-item"><span class="row-title">Proje Sayısı Farkı</span><span class="row-text"><strong>{int(comparison_results['project_count_diff'])}</strong></span></div>
        """

    def _build_top_increasing_projects_html(self, project_changes, top_n=5):
        if not project_changes:
            return '<div class="empty-note">Aynı projeler arasında karşılaştırma verisi bulunmuyor.</div>'

        sorted_changes = sorted(
            project_changes,
            key=lambda item: float(item.get("tl_diff", 0)),
            reverse=True,
        )

        top_projects = [row for row in sorted_changes if float(row.get("tl_diff", 0)) > 0][:top_n]

        if not top_projects:
            return '<div class="empty-note">TL bazında artış gösteren proje bulunmuyor.</div>'

        rows = []
        for row in top_projects:
            rows.append(
                f'<div class="row-item">'
                f'<span class="row-title">{row.get("project", "-")}</span>'
                f'<span class="row-text"><strong>{self._format_number(row.get("tl_diff", 0), "TL")}</strong></span>'
                f'</div>'
            )
        return "".join(rows)

    def _build_simple_list_html(self, items, empty_text):
        if not items:
            return f'<div class="empty-note">{empty_text}</div>'

        lines = []
        for item in items:
            lines.append(f'<div class="tag-item">{item}</div>')
        return "".join(lines)

    def _build_project_changes_html(self, comparison_results):
        project_changes = comparison_results.get("project_changes", [])
        new_projects = comparison_results.get("new_projects", [])
        removed_projects = comparison_results.get("removed_projects", [])

        top_increasing_html = self._build_top_increasing_projects_html(project_changes)
        new_projects_html = self._build_simple_list_html(
            new_projects,
            "Yeni eklenen proje bulunmuyor.",
        )
        removed_projects_html = self._build_simple_list_html(
            removed_projects,
            "Kaldırılan proje bulunmuyor.",
        )

        return f"""
        <div class="three-col-grid">
            <div class="detail-card">
                <div class="detail-title">En Çok Artan Projeler (TL)</div>
                {top_increasing_html}
            </div>
            <div class="detail-card">
                <div class="detail-title">Yeni Eklenen Projeler</div>
                {new_projects_html}
            </div>
            <div class="detail-card">
                <div class="detail-title">Kaldırılan Projeler</div>
                {removed_projects_html}
            </div>
        </div>
        """

    def _build_executive_summary_html(self, executive_sections):
        if isinstance(executive_sections, dict):
            parts = []
            for title, text in executive_sections.items():
                parts.append(
                    f'<div class="summary-item"><h3>{title}</h3><p>{text}</p></div>'
                )
            return "".join(parts)

        return f'<div class="summary-item"><p>{str(executive_sections)}</p></div>'

    def generate_html_report(
        self,
        current_results,
        comparison_results,
        executive_sections,
        report_month="Bilinmiyor",
    ):
        report_title = f"ReportIQ Yönetici Raporu - {report_month}"
        report_date = datetime.now().strftime("%Y-%m-%d")

        kpi_summary_html = self._build_kpi_summary_html(current_results)
        peak_amounts_html = self._build_peak_amounts_html(current_results)
        comparison_summary_html = self._build_comparison_summary_html(comparison_results)
        project_changes_html = self._build_project_changes_html(comparison_results)
        ai_summary_html = self._build_executive_summary_html(executive_sections)

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
                    background: #eef3f8;
                    color: #243447;
                }}
                .title-card {{
                    background: #1f3a5b;
                    border: 1px solid #2b4a6e;
                    border-radius: 14px;
                    padding: 18px;
                    margin-bottom: 14px;
                    text-align: center;
                }}
                .title-card h1 {{ margin: 0; font-size: 31px; color: #f4f8fc; }}
                .title-card p {{ margin: 8px 0 0 0; color: #d8e4f0; font-size: 16px; }}
                .section {{
                    background: #ffffff;
                    border: 1px solid #d6e0eb;
                    border-radius: 12px;
                    padding: 14px;
                    margin-bottom: 12px;
                }}
                .section h2 {{
                    margin: 0 0 10px 0;
                    font-size: 22px;
                    color: #1f3a5b;
                }}
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: 10px;
                }}
                .kpi-card {{
                    background: #f2f7fc;
                    border: 1px solid #d9e5f0;
                    border-radius: 10px;
                    padding: 10px;
                }}
                .kpi-label {{ color: #4a6078; font-size: 15px; }}
                .kpi-value {{ color: #1f3a5b; font-size: 20px; font-weight: 700; margin-top: 4px; }}
                .two-col-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }}
                .three-col-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: 10px;
                }}
                .detail-card {{
                    background: #f7fafd;
                    border: 1px solid #dbe6f1;
                    border-radius: 10px;
                    padding: 10px;
                }}
                .detail-title {{ color: #385370; font-size: 15px; font-weight: 700; margin-bottom: 6px; }}
                .detail-project {{ color: #1f3a5b; font-size: 19px; font-weight: 700; margin-bottom: 3px; }}
                .detail-amount {{ color: #2a557f; font-size: 16px; font-weight: 700; }}
                .row-item {{
                    display: flex;
                    justify-content: space-between;
                    gap: 12px;
                    padding: 8px 10px;
                    background: #f4f8fc;
                    border: 1px solid #dce7f2;
                    border-radius: 8px;
                    margin-bottom: 8px;
                }}
                .row-title {{ font-weight: 700; color: #2c435d; font-size: 15px; }}
                .row-text {{ color: #3a4f67; text-align: right; font-size: 15px; }}
                .tag-item {{
                    background: #eef5fc;
                    border: 1px solid #d7e4f2;
                    border-radius: 8px;
                    padding: 7px 9px;
                    margin-bottom: 7px;
                    color: #2f4c68;
                    font-size: 14px;
                    font-weight: 600;
                }}
                .empty-note {{
                    color: #5a6d84;
                    font-size: 14px;
                    padding: 8px;
                    background: #f5f8fc;
                    border: 1px dashed #cfddeb;
                    border-radius: 8px;
                }}
                .summary-item {{
                    background: #f5f8fc;
                    border: 1px solid #d8e4ef;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 8px;
                }}
                .summary-item h3 {{ margin: 0 0 6px 0; font-size: 19px; color: #1f3a5b; }}
                .summary-item p {{ margin: 0; color: #344b63; font-size: 16px; line-height: 1.6; }}
            </style>
        </head>
        <body>
            <div class="title-card">
                <h1>{report_title}</h1>
                <p>Rapor Oluşturma Tarihi: <strong>{report_date}</strong></p>
            </div>

            <div class="section">
                <h2>1. KPI Özeti</h2>
                {kpi_summary_html}
            </div>

            <div class="section">
                <h2>2. En Yüksek Tutarlar</h2>
                {peak_amounts_html}
            </div>

            <div class="section">
                <h2>3. Karşılaştırma Özeti</h2>
                {comparison_summary_html}
            </div>

            <div class="section">
                <h2>4. Proje Bazlı Değişimler</h2>
                {project_changes_html}
            </div>

            <div class="section">
                <h2>5. AI Yönetici Özeti</h2>
                {ai_summary_html}
            </div>
        </body>
        </html>
        """

        return html_content
