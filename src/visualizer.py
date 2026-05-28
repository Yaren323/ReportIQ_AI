import pandas as pd
import plotly.express as px


class VisualizerAgent:
    """
    Proje bazlı ödeme raporu için grafik üreten sınıf.
    """

    PROJECT_COLUMN = "Projeler"
    TL_COLUMN = "Aylık Tutar (KDV Hariç - TL)"
    USD_COLUMN = "Aylık Tutar (KDV Hariç - USD)"

    def _apply_dark_theme(self, fig, y_title):
        """
        Tüm grafiklerde ortak koyu tema düzeni uygular.
        """
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1f2937",
            plot_bgcolor="#1f2937",
            font=dict(color="#E5E7EB", size=13),
            title_font=dict(size=18, color="#F3F4F6"),
            xaxis=dict(
                title_font=dict(size=13),
                tickfont=dict(size=12),
                gridcolor="rgba(255,255,255,0.08)",
            ),
            yaxis=dict(
                title=y_title,
                title_font=dict(size=13),
                tickfont=dict(size=12),
                gridcolor="rgba(255,255,255,0.12)",
                zerolinecolor="rgba(255,255,255,0.18)",
            ),
            margin=dict(l=30, r=20, t=70, b=20),
            showlegend=False,
            bargap=0.35,
            height=420,
        )

        fig.update_traces(
            width=0.42,
            textposition="outside",
            textfont=dict(size=12, color="#F9FAFB"),
            cliponaxis=False,
        )

        return fig

    def _remove_total_row(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        'Aylık Toplam Ödenecek Tutar:' satırını grafik verisinden çıkarır.
        """
        chart_df = df.copy()
        project_series = chart_df[self.PROJECT_COLUMN].astype(str).str.strip()
        total_mask = project_series.str.lower() == "aylık toplam ödenecek tutar:".lower()
        return chart_df[~total_mask].copy()

    def create_project_tl_chart(self, df: pd.DataFrame):
        """
        1) Proje Bazlı TL Tutar Grafiği
        """
        chart_df = self._remove_total_row(df)
        chart_df[self.TL_COLUMN] = pd.to_numeric(chart_df[self.TL_COLUMN], errors="coerce").fillna(0)

        fig = px.bar(
            chart_df,
            x=self.PROJECT_COLUMN,
            y=self.TL_COLUMN,
            color_discrete_sequence=["#60A5FA"],
            text=self.TL_COLUMN,
            title="Proje Bazlı TL Tutar Grafiği",
        )

        fig.update_traces(texttemplate="%{y:,.2f} TL")
        return self._apply_dark_theme(fig, "TL Tutar")

    def create_project_usd_chart(self, df: pd.DataFrame):
        """
        2) Proje Bazlı USD Tutar Grafiği
        """
        chart_df = self._remove_total_row(df)
        chart_df[self.USD_COLUMN] = pd.to_numeric(chart_df[self.USD_COLUMN], errors="coerce").fillna(0)

        fig = px.bar(
            chart_df,
            x=self.PROJECT_COLUMN,
            y=self.USD_COLUMN,
            color_discrete_sequence=["#34D399"],
            text=self.USD_COLUMN,
            title="Proje Bazlı USD Tutar Grafiği",
        )

        fig.update_traces(texttemplate="%{y:,.2f} USD")
        return self._apply_dark_theme(fig, "USD Tutar")

    def create_total_tl_comparison_chart(self, previous_total_tl, current_total_tl):
        """
        3) Önceki Ay / Güncel Ay Toplam TL Karşılaştırması
        """
        chart_df = pd.DataFrame(
            {
                "Dönem": ["Önceki Ay", "Güncel Ay"],
                "Toplam TL": [float(previous_total_tl), float(current_total_tl)],
            }
        )

        fig = px.bar(
            chart_df,
            x="Dönem",
            y="Toplam TL",
            color="Dönem",
            color_discrete_sequence=["#3B82F6", "#93C5FD"],
            text="Toplam TL",
            title="Önceki Ay / Güncel Ay Toplam TL Karşılaştırması",
        )

        fig.update_traces(texttemplate="%{y:,.2f} TL")
        return self._apply_dark_theme(fig, "Toplam TL")

    def create_total_usd_comparison_chart(self, previous_total_usd, current_total_usd):
        """
        4) Önceki Ay / Güncel Ay Toplam USD Karşılaştırması
        """
        chart_df = pd.DataFrame(
            {
                "Dönem": ["Önceki Ay", "Güncel Ay"],
                "Toplam USD": [float(previous_total_usd), float(current_total_usd)],
            }
        )

        fig = px.bar(
            chart_df,
            x="Dönem",
            y="Toplam USD",
            color="Dönem",
            color_discrete_sequence=["#10B981", "#6EE7B7"],
            text="Toplam USD",
            title="Önceki Ay / Güncel Ay Toplam USD Karşılaştırması",
        )

        fig.update_traces(texttemplate="%{y:,.2f} USD")
        return self._apply_dark_theme(fig, "Toplam USD")

    def create_project_tl_change_chart(self, project_changes):
        """
        5) Proje Bazlı TL Değişim Grafiği
        project_changes: comparator çıktısındaki liste.
        """
        change_df = pd.DataFrame(project_changes)

        if change_df.empty:
            change_df = pd.DataFrame({"project": [], "tl_diff": []})

        fig = px.bar(
            change_df,
            x="project",
            y="tl_diff",
            color="tl_diff",
            color_continuous_scale=["#EF4444", "#9CA3AF", "#22C55E"],
            text="tl_diff",
            title="Proje Bazlı TL Değişim Grafiği",
        )

        fig.update_traces(texttemplate="%{y:,.2f} TL")
        fig.update_layout(coloraxis_showscale=False)
        return self._apply_dark_theme(fig, "TL Değişimi")

    def create_project_usd_change_chart(self, project_changes):
        """
        6) Proje Bazlı USD Değişim Grafiği
        project_changes: comparator çıktısındaki liste.
        """
        change_df = pd.DataFrame(project_changes)

        if change_df.empty:
            change_df = pd.DataFrame({"project": [], "usd_diff": []})

        fig = px.bar(
            change_df,
            x="project",
            y="usd_diff",
            color="usd_diff",
            color_continuous_scale=["#EF4444", "#9CA3AF", "#22C55E"],
            text="usd_diff",
            title="Proje Bazlı USD Değişim Grafiği",
        )

        fig.update_traces(texttemplate="%{y:,.2f} USD")
        fig.update_layout(coloraxis_showscale=False)
        return self._apply_dark_theme(fig, "USD Değişimi")
