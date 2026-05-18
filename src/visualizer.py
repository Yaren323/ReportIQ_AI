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
            color_discrete_sequence=["#7FB3D5", "#6FA8DC"],
            text="Toplam Tutar",
            title="Toplam Tutar Karşılaştırması",
        )

        fig.update_traces(
            texttemplate="%{y:,.0f} TL",
            textposition="outside",
            width=0.42,
            textfont=dict(size=14),
            cliponaxis=False,
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=70, b=20),
            yaxis_title="Toplam Tutar (TL)",
            bargap=0.35,
        )
        fig.update_yaxes(range=[0, max(chart_df["Toplam Tutar"]) * 1.22 if max(chart_df["Toplam Tutar"]) > 0 else 1])

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
            color_discrete_sequence=["#8DC9A5", "#D9B08C"],
            text="Bekleyen İşlem",
            title="Bekleyen İşlem Karşılaştırması",
        )

        fig.update_traces(
            texttemplate="%{y:.0f}",
            textposition="outside",
            width=0.42,
            textfont=dict(size=14),
            cliponaxis=False,
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=70, b=20),
            yaxis_title="Bekleyen İşlem Sayısı",
            bargap=0.35,
        )
        fig.update_yaxes(range=[0, max(chart_df["Bekleyen İşlem"]) * 1.22 if max(chart_df["Bekleyen İşlem"]) > 0 else 1])

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
            color_discrete_sequence=["#6FA8DC"],
            text="Tutar",
            title="Firma Bazlı Toplam Tutar",
        )

        fig.update_traces(
            texttemplate="%{y:,.0f} TL",
            textposition="outside",
            width=0.55,
            textfont=dict(size=13),
            cliponaxis=False,
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=75, b=20),
            yaxis_title="Toplam Tutar (TL)",
            bargap=0.30,
        )
        fig.update_yaxes(range=[0, max(company_df["Tutar"]) * 1.18 if len(company_df) > 0 and max(company_df["Tutar"]) > 0 else 1])

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
            color_discrete_sequence=["#8FB9D9"],
            text="Tutar",
            title="Departman Bazlı Toplam Tutar",
        )

        fig.update_traces(
            texttemplate="%{y:,.0f} TL",
            textposition="outside",
            width=0.55,
            textfont=dict(size=13),
            cliponaxis=False,
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=75, b=20),
            yaxis_title="Toplam Tutar (TL)",
            bargap=0.30,
        )
        fig.update_yaxes(range=[0, max(department_df["Tutar"]) * 1.18 if len(department_df) > 0 and max(department_df["Tutar"]) > 0 else 1])

        return fig
