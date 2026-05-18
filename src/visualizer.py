import pandas as pd
import plotly.express as px


class VisualizerAgent:
    # Bu sınıf, dashboard için temel karşılaştırma grafiklerini üretir.

    def create_total_amount_comparison_chart(self, previous_amount, current_amount):
        # Önceki ay ve güncel ay toplam tutarlarını tek grafikte gösterir.
        chart_df = pd.DataFrame(
            {
                "Dönem": ["Önceki Ay", "Güncel Ay"],
                "Toplam Tutar": [previous_amount, current_amount],
            }
        )

        fig = px.bar(
            chart_df,
            x="Dönem",
            y="Toplam Tutar",
            color="Dönem",
            text="Toplam Tutar",
            title="Toplam Tutar Karşılaştırması",
        )

        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(showlegend=False)

        return fig

    def create_percentage_change_chart(self, percentage_df):
        # Yüzde değişim tablosunu çubuk grafik olarak görselleştirir.
        fig = px.bar(
            percentage_df,
            x="Metrik",
            y="Yüzde Değişim (%)",
            color="Metrik",
            text="Yüzde Değişim (%)",
            title="Metrik Bazlı Yüzde Değişim",
        )

        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(showlegend=False)

        return fig

    def create_pending_count_comparison_chart(self, previous_pending, current_pending):
        # Bekleyen işlem sayılarını dönem bazında karşılaştırır.
        chart_df = pd.DataFrame(
            {
                "Dönem": ["Önceki Ay", "Güncel Ay"],
                "Bekleyen İşlem": [previous_pending, current_pending],
            }
        )

        fig = px.bar(
            chart_df,
            x="Dönem",
            y="Bekleyen İşlem",
            color="Dönem",
            text="Bekleyen İşlem",
            title="Bekleyen İşlem Karşılaştırması",
        )

        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(showlegend=False)

        return fig

    def create_company_total_amount_chart(self, df):
        # Firma bazında toplam tutarları hesaplar ve bar grafik üretir.
        company_df = (
            df.groupby("Firma", as_index=False)["Tutar"]
            .sum()
            .sort_values("Tutar", ascending=False)
        )

        fig = px.bar(
            company_df,
            x="Firma",
            y="Tutar",
            color="Firma",
            text="Tutar",
            title="Firma Bazlı Toplam Tutar",
        )

        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(showlegend=False)

        return fig

    def create_department_total_amount_chart(self, df):
        # Departman bazında toplam tutarları hesaplar ve bar grafik üretir.
        department_df = (
            df.groupby("Departman", as_index=False)["Tutar"]
            .sum()
            .sort_values("Tutar", ascending=False)
        )

        fig = px.bar(
            department_df,
            x="Departman",
            y="Tutar",
            color="Departman",
            text="Tutar",
            title="Departman Bazlı Toplam Tutar",
        )

        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(showlegend=False)

        return fig
