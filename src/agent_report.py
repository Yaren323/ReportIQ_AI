from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px


class AgentReportBuilder:
    @staticmethod
    def _find_descriptor_column(sheet_report: dict[str, Any]) -> str | None:
        classes = sheet_report["column_classes"]
        if classes["identity_like"]:
            return classes["identity_like"][0]
        if classes["text"]:
            return classes["text"][0]
        return None

    @staticmethod
    def _numeric_overview(sheet_report: dict[str, Any]) -> pd.DataFrame:
        numeric_df = sheet_report["numeric_summary"].copy()
        if numeric_df.empty:
            return numeric_df

        preview = sheet_report["preview"]
        descriptor_col = AgentReportBuilder._find_descriptor_column(sheet_report)
        descriptor_values: list[str] = []
        max_values: list[float] = []

        for _, row in numeric_df.iterrows():
            col = row["Kolon"]
            try:
                series = pd.to_numeric(preview[col], errors="coerce")
                if series.notna().any():
                    idx = series.idxmax()
                    max_values.append(float(series.loc[idx]))
                    if descriptor_col and descriptor_col in preview.columns:
                        descriptor_values.append(str(preview.loc[idx, descriptor_col]))
                    else:
                        descriptor_values.append("-")
                else:
                    max_values.append(float("nan"))
                    descriptor_values.append("-")
            except Exception:
                max_values.append(float("nan"))
                descriptor_values.append("-")

        numeric_df["En Yuksek Deger"] = max_values
        numeric_df["En Yuksek Degerin Aciklamasi"] = descriptor_values
        return numeric_df

    @staticmethod
    def _categorical_overview(sheet_report: dict[str, Any]) -> pd.DataFrame:
        preview = sheet_report["preview"]
        classes = sheet_report["column_classes"]
        rows = []
        for col in classes["text"][:6]:
            try:
                s = preview[col].dropna().astype(str).str.strip()
                top_vals = s.value_counts().head(5)
                rows.append(
                    {
                        "Sutun": col,
                        "Benzersiz Deger Sayisi": int(s.nunique()),
                        "En Sik Ilk 5 Deger": ", ".join([f"{k} ({v})" for k, v in top_vals.items()]) or "-",
                    }
                )
            except Exception:
                continue
        return pd.DataFrame(rows)

    @staticmethod
    def _executive_comment(sheet_report: dict[str, Any]) -> str:
        classes = sheet_report["column_classes"]
        money_cols = classes["money_like"]
        descriptor_col = AgentReportBuilder._find_descriptor_column(sheet_report)
        preview = sheet_report["preview"]

        if not money_cols:
            return (
                "Bu sayfada belirgin finansal sutun sinirli gorunuyor. "
                "Sayfa daha cok operasyonel veya siniflandirma amacli veri iceriyor olabilir."
            )

        money_col = money_cols[0]
        try:
            series = pd.to_numeric(preview[money_col], errors="coerce")
            total = float(series.sum()) if series.notna().any() else 0.0
            if series.notna().any():
                idx = series.idxmax()
                max_val = float(series.loc[idx])
                owner = str(preview.loc[idx, descriptor_col]) if descriptor_col and descriptor_col in preview.columns else "ilgili kayit"
            else:
                max_val = 0.0
                owner = "ilgili kayit"
        except Exception:
            total = 0.0
            max_val = 0.0
            owner = "ilgili kayit"

        return (
            f"Bu sayfada agirlikli olarak finansal icerik bulunuyor olabilir. "
            f"{money_col} alaninda toplam deger yaklasik {total:,.2f} seviyesindedir. "
            f"En yuksek deger {owner} kaydinda {max_val:,.2f} olarak gorulmektedir. "
            "Veriler, belirli kayitlarin toplam tutar uzerinde daha yuksek etkiye sahip olabilecegini gostermektedir."
        )

    @staticmethod
    def _render_charts(st, sheet_report: dict[str, Any]):
        preview = sheet_report["preview"]
        classes = sheet_report["column_classes"]
        numeric_cols = classes["numeric"]
        text_cols = classes["text"]
        date_cols = classes["date_like"]
        chart_count = 0

        if numeric_cols:
            try:
                means = []
                for col in numeric_cols[:10]:
                    s = pd.to_numeric(preview[col], errors="coerce")
                    means.append({"Sutun": col, "Ortalama": float(s.mean()) if s.notna().any() else 0.0})
                mean_df = pd.DataFrame(means)
                if not mean_df.empty:
                    fig = px.bar(mean_df, x="Sutun", y="Ortalama", title="Sayisal Alanlarin Ortalama Dagilimi")
                    st.plotly_chart(fig, use_container_width=True)
                    chart_count += 1
            except Exception:
                st.info("Bu grafik olusturulurken veri formati nedeniyle atlandi.")

        if text_cols and numeric_cols:
            try:
                cat_col = text_cols[0]
                num_col = numeric_cols[0]
                grp = (
                    preview[[cat_col, num_col]]
                    .assign(_n=pd.to_numeric(preview[num_col], errors="coerce"))
                    .dropna(subset=[cat_col, "_n"])
                    .groupby(cat_col, as_index=False)["_n"]
                    .sum()
                    .sort_values("_n", ascending=False)
                    .head(10)
                )
                if not grp.empty:
                    fig = px.bar(grp, x=cat_col, y="_n", title=f"{cat_col} Bazinda Toplam {num_col}")
                    st.plotly_chart(fig, use_container_width=True)
                    chart_count += 1
            except Exception:
                st.info("Bu grafik olusturulurken veri formati nedeniyle atlandi.")

        if date_cols and numeric_cols:
            try:
                date_col = date_cols[0]
                num_col = numeric_cols[0]
                ts = preview[[date_col, num_col]].copy()
                ts[date_col] = pd.to_datetime(ts[date_col], errors="coerce", dayfirst=True)
                ts[num_col] = pd.to_numeric(ts[num_col], errors="coerce")
                ts = ts.dropna(subset=[date_col, num_col]).sort_values(date_col)
                if not ts.empty:
                    fig = px.line(ts, x=date_col, y=num_col, title=f"{date_col} Bazinda {num_col} Zaman Serisi")
                    st.plotly_chart(fig, use_container_width=True)
                    chart_count += 1
            except Exception:
                st.info("Bu grafik olusturulurken veri formati nedeniyle atlandi.")

        if chart_count == 0:
            st.info("Bu sayfada grafik olusturmak icin yeterli uygun veri bulunamadi.")

    @staticmethod
    def render_sheet_card(st, sheet_report: dict[str, Any], render_kpi_card):
        st.divider()
        st.markdown(f"### Sayfa Analizi: {sheet_report['sheet_name']}")

        st.markdown("#### Sayfa Genel Bilgileri")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_kpi_card("Satir Sayisi", str(sheet_report["row_count"]))
        with m2:
            render_kpi_card("Sutun Sayisi", str(sheet_report["column_count"]))
        with m3:
            render_kpi_card("Dolu Hucre", f"{sheet_report['filled_cell_count']:,}")
        with m4:
            render_kpi_card("Bos Hucre", f"{sheet_report['empty_cell_count']:,}")

        with st.expander("Sutunlar", expanded=False):
            st.dataframe(pd.DataFrame({"Sutun Adi": sheet_report["columns"]}), use_container_width=True, hide_index=True)

        st.markdown("#### Sayisal Ozet")
        numeric_overview = AgentReportBuilder._numeric_overview(sheet_report)
        if numeric_overview.empty:
            st.info("Bu sayfada sayisal ozet icin uygun sutun bulunamadi.")
        else:
            st.dataframe(numeric_overview, use_container_width=True, hide_index=True)

        st.markdown("#### Kategorik Ozet")
        cat_overview = AgentReportBuilder._categorical_overview(sheet_report)
        if cat_overview.empty:
            st.info("Bu sayfada kategorik ozet icin uygun sutun bulunamadi.")
        else:
            st.dataframe(cat_overview, use_container_width=True, hide_index=True)
            classes = sheet_report["column_classes"]
            identity_col = classes["identity_like"][0] if classes["identity_like"] else None
            if identity_col and identity_col in sheet_report["preview"].columns:
                uniq = int(sheet_report["preview"][identity_col].dropna().astype(str).nunique())
                st.caption(f"Benzersiz {identity_col} sayisi: {uniq}")

        st.markdown("#### Yonetici Yorumu")
        st.info(AgentReportBuilder._executive_comment(sheet_report))

        st.markdown("#### Onerilen Metrikler")
        for metric in sheet_report["suggestions"]["dashboard_metrics"]:
            st.write(f"- {metric}")

        st.markdown("#### Onerilen Grafikler")
        for chart in sheet_report["suggestions"]["recommended_charts"]:
            st.write(f"- {chart}")

        st.markdown("#### Grafikler")
        AgentReportBuilder._render_charts(st, sheet_report)

        with st.expander("Ilk 20 Satir Onizleme", expanded=False):
            st.dataframe(sheet_report["preview"], use_container_width=True, hide_index=True)
