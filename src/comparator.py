import pandas as pd


class CompareAgent:
    """
    Önceki ay ve güncel ay proje bazlı ödeme raporlarını karşılaştırır.
    Beklenen kolonlar:
    - Projeler
    - Aylık Tutar (KDV Hariç - TL)
    - Aylık Tutar (KDV Hariç - USD)
    """

    PROJECT_COLUMN = "Projeler"
    TL_COLUMN = "Aylık Tutar (KDV Hariç - TL)"
    USD_COLUMN = "Aylık Tutar (KDV Hariç - USD)"
    TOTAL_ROW_LABEL = "Aylık Toplam Ödenecek Tutar:"

    def __init__(self, previous_df: pd.DataFrame, current_df: pd.DataFrame):
        self.previous_df_raw = previous_df.copy()
        self.current_df_raw = current_df.copy()

        self.previous_df = self._prepare_dataframe(self.previous_df_raw)
        self.current_df = self._prepare_dataframe(self.current_df_raw)

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Veriyi karşılaştırmaya hazırlar:
        - TL/USD kolonlarını sayısal yapar
        - Toplam satırını analiz dışında bırakır
        - Proje adını temizler
        """
        prepared_df = df.copy()

        prepared_df[self.TL_COLUMN] = pd.to_numeric(
            prepared_df[self.TL_COLUMN], errors="coerce"
        ).fillna(0)
        prepared_df[self.USD_COLUMN] = pd.to_numeric(
            prepared_df[self.USD_COLUMN], errors="coerce"
        ).fillna(0)

        prepared_df[self.PROJECT_COLUMN] = (
            prepared_df[self.PROJECT_COLUMN].astype(str).str.strip()
        )

        total_mask = (
            prepared_df[self.PROJECT_COLUMN].str.lower()
            == self.TOTAL_ROW_LABEL.lower()
        )
        prepared_df = prepared_df[~total_mask].copy()

        prepared_df = prepared_df[prepared_df[self.PROJECT_COLUMN] != ""].copy()
        return prepared_df

    def calculate_percentage_change(self, old_value, new_value):
        """
        0'a bölmeyi güvenli şekilde yönetir.
        """
        old_value = float(old_value)
        new_value = float(new_value)

        if old_value == 0:
            if new_value == 0:
                return 0.0
            return 100.0

        return ((new_value - old_value) / old_value) * 100

    def get_basic_metrics(self, df: pd.DataFrame):
        total_tl = float(df[self.TL_COLUMN].sum())
        total_usd = float(df[self.USD_COLUMN].sum())
        project_count = int(len(df))

        if project_count == 0:
            average_tl = 0.0
            average_usd = 0.0
        else:
            average_tl = float(df[self.TL_COLUMN].mean())
            average_usd = float(df[self.USD_COLUMN].mean())

        return {
            "total_tl": total_tl,
            "total_usd": total_usd,
            "project_count": project_count,
            "average_tl": average_tl,
            "average_usd": average_usd,
        }

    def _aggregate_by_project(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aynı proje birden fazla satırda varsa tek projede toplar.
        """
        grouped_df = (
            df.groupby(self.PROJECT_COLUMN, as_index=False)[[self.TL_COLUMN, self.USD_COLUMN]]
            .sum()
        )
        return grouped_df

    def _calculate_project_changes(self):
        previous_grouped = self._aggregate_by_project(self.previous_df)
        current_grouped = self._aggregate_by_project(self.current_df)

        merged_df = previous_grouped.merge(
            current_grouped,
            on=self.PROJECT_COLUMN,
            how="inner",
            suffixes=("_previous", "_current"),
        )

        changes = []
        for _, row in merged_df.iterrows():
            prev_tl = float(row[f"{self.TL_COLUMN}_previous"])
            curr_tl = float(row[f"{self.TL_COLUMN}_current"])
            prev_usd = float(row[f"{self.USD_COLUMN}_previous"])
            curr_usd = float(row[f"{self.USD_COLUMN}_current"])

            tl_diff = curr_tl - prev_tl
            usd_diff = curr_usd - prev_usd

            changes.append(
                {
                    "project": row[self.PROJECT_COLUMN],
                    "previous_tl": prev_tl,
                    "current_tl": curr_tl,
                    "tl_diff": tl_diff,
                    "tl_pct_change": self.calculate_percentage_change(prev_tl, curr_tl),
                    "previous_usd": prev_usd,
                    "current_usd": curr_usd,
                    "usd_diff": usd_diff,
                    "usd_pct_change": self.calculate_percentage_change(prev_usd, curr_usd),
                }
            )

        return changes

    def _get_new_and_removed_projects(self):
        previous_projects = set(
            self.previous_df[self.PROJECT_COLUMN].dropna().astype(str).str.strip()
        )
        current_projects = set(
            self.current_df[self.PROJECT_COLUMN].dropna().astype(str).str.strip()
        )

        new_projects = sorted(current_projects - previous_projects)
        removed_projects = sorted(previous_projects - current_projects)

        return new_projects, removed_projects

    def generate_comparison_summary(self, results):
        total_tl_diff = results["total_tl_diff"]
        total_usd_diff = results["total_usd_diff"]
        project_count_diff = results["project_count_diff"]
        average_tl_diff = results["average_tl_diff"]
        average_usd_diff = results["average_usd_diff"]

        summary = f"""
Önceki ay ve güncel ay proje bazlı ödeme raporu karşılaştırılmıştır.
Toplam TL tutar farkı: {total_tl_diff:,.2f} TL.
Toplam USD tutar farkı: {total_usd_diff:,.2f} USD.
Proje sayısı farkı: {project_count_diff}.
Ortalama TL tutar farkı: {average_tl_diff:,.2f} TL.
Ortalama USD tutar farkı: {average_usd_diff:,.2f} USD.
Aynı projeler için detaylı TL/USD değişimleri project_changes alanında listelenmiştir.
Yeni projeler new_projects, çıkarılan projeler removed_projects alanlarında sunulmuştur.
        """.strip()

        return summary

    def run_comparison(self):
        previous_metrics = self.get_basic_metrics(self.previous_df)
        current_metrics = self.get_basic_metrics(self.current_df)

        total_tl_diff = current_metrics["total_tl"] - previous_metrics["total_tl"]
        total_usd_diff = current_metrics["total_usd"] - previous_metrics["total_usd"]
        project_count_diff = current_metrics["project_count"] - previous_metrics["project_count"]
        average_tl_diff = current_metrics["average_tl"] - previous_metrics["average_tl"]
        average_usd_diff = current_metrics["average_usd"] - previous_metrics["average_usd"]

        project_changes = self._calculate_project_changes()
        new_projects, removed_projects = self._get_new_and_removed_projects()

        results = {
            "total_tl_diff": total_tl_diff,
            "total_usd_diff": total_usd_diff,
            "project_count_diff": project_count_diff,
            "average_tl_diff": average_tl_diff,
            "average_usd_diff": average_usd_diff,
            "project_changes": project_changes,
            "new_projects": new_projects,
            "removed_projects": removed_projects,
        }

        results["summary"] = self.generate_comparison_summary(results)
        return results
