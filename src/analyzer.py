import re

import pandas as pd


class AnalyzerAgent:
    """
    Proje bazlı aylık ödeme Excel verisini analiz eder.
    Beklenen kolonlar:
    - Projeler
    - Aylık Tutar (KDV Hariç - TL)
    - Aylık Tutar (KDV Hariç - USD)
    """

    PROJECT_COLUMN = "Projeler"
    TL_COLUMN = "Aylık Tutar (KDV Hariç - TL)"
    USD_COLUMN = "Aylık Tutar (KDV Hariç - USD)"
    TOTAL_ROW_LABEL = "Aylık Toplam Ödenecek Tutar:"
    TOTAL_TOKENS = ("toplam", "genel toplam", "total", "grand total")

    def __init__(self, df):
        self.df = df.copy()
        self.analysis_df, self.total_row_df, self.debug_df = self._prepare_dataframes()

    @staticmethod
    def _normalize_project_name(value):
        if pd.isna(value):
            return ""
        return str(value).strip()

    @staticmethod
    def _is_total_row(project_name):
        name = project_name.lower().strip()
        if name == "":
            return False
        return any(token in name for token in AnalyzerAgent.TOTAL_TOKENS)

    @staticmethod
    def _is_header_row(project_name):
        name = project_name.lower().strip()
        return name in {"projeler", "project", "projects"}

    @staticmethod
    def _extract_numeric_text(text):
        return re.sub(r"[^0-9,.\-]", "", text)

    def _parse_tl_value(self, value):
        if pd.isna(value):
            return pd.NA

        text = str(value).strip()
        if text == "":
            return pd.NA

        numeric_text = self._extract_numeric_text(text.replace("TL", "").replace("tl", ""))
        if numeric_text in {"", "-", ".", ","}:
            return pd.NA

        # 1) 647,606.00 / 7,653,274.55
        if re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?", numeric_text):
            normalized = numeric_text.replace(",", "")
        # 2) 647.606,00 / 7.653.274,55
        elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", numeric_text):
            normalized = numeric_text.replace(".", "").replace(",", ".")
        # 3) Sadece virgül varsa TL için binlik ayracı kabul et (ondalık gibi yorumlama)
        elif "," in numeric_text and "." not in numeric_text:
            normalized = numeric_text.replace(",", "")
        else:
            normalized = numeric_text

        try:
            return float(normalized)
        except (TypeError, ValueError):
            return pd.NA

    def _parse_usd_value(self, value):
        if pd.isna(value):
            return pd.NA

        text = str(value).strip()
        if text == "":
            return pd.NA

        numeric_text = self._extract_numeric_text(text)
        if numeric_text in {"", "-", ".", ","}:
            return pd.NA

        comma_count = numeric_text.count(",")
        dot_count = numeric_text.count(".")

        if comma_count > 0 and dot_count > 0:
            # Son görülen ayraç ondalık kabul edilir.
            if numeric_text.rfind(",") > numeric_text.rfind("."):
                normalized = numeric_text.replace(".", "").replace(",", ".")
            else:
                normalized = numeric_text.replace(",", "")
        elif comma_count > 0:
            # Tek virgül ve sonunda 1-2 hane varsa ondalık kabul et.
            decimal_part_len = len(numeric_text.split(",")[-1])
            if comma_count == 1 and decimal_part_len in (1, 2):
                normalized = numeric_text.replace(",", ".")
            else:
                normalized = numeric_text.replace(",", "")
        elif dot_count > 0:
            # Tek nokta ve sonunda 1-2 hane varsa ondalık kabul et.
            decimal_part_len = len(numeric_text.split(".")[-1])
            if dot_count == 1 and decimal_part_len in (1, 2):
                normalized = numeric_text
            else:
                normalized = numeric_text.replace(".", "")
        else:
            normalized = numeric_text

        try:
            return float(normalized)
        except (TypeError, ValueError):
            return pd.NA

    def _classify_row(self, project_name, parsed_tl, parsed_usd):
        if project_name == "":
            return "bos"
        if self._is_header_row(project_name):
            return "baslik"
        if self._is_total_row(project_name):
            return "toplam"
        if pd.notna(parsed_tl) or pd.notna(parsed_usd):
            return "proje"
        return "baslik"

    def _prepare_dataframes(self):
        prepared_df = self.df.copy()

        raw_tl = prepared_df[self.TL_COLUMN].copy()
        raw_usd = prepared_df[self.USD_COLUMN].copy()
        project_series = prepared_df[self.PROJECT_COLUMN].apply(self._normalize_project_name)

        parsed_tl = raw_tl.apply(self._parse_tl_value)
        parsed_usd = raw_usd.apply(self._parse_usd_value)

        row_type = [
            self._classify_row(project_name, tl_value, usd_value)
            for project_name, tl_value, usd_value in zip(project_series, parsed_tl, parsed_usd)
        ]

        prepared_df[self.PROJECT_COLUMN] = project_series
        prepared_df[self.TL_COLUMN] = parsed_tl
        prepared_df[self.USD_COLUMN] = parsed_usd

        debug_df = pd.DataFrame(
            {
                "proje adı": project_series,
                "raw TL": raw_tl,
                "parsed TL": parsed_tl,
                "raw USD": raw_usd,
                "parsed USD": parsed_usd,
                "satır tipi": row_type,
            }
        )

        row_type_series = pd.Series(row_type, index=prepared_df.index)
        analysis_df = prepared_df[row_type_series == "proje"].copy()
        total_row_df = prepared_df[row_type_series == "toplam"].copy()

        return analysis_df, total_row_df, debug_df

    def get_debug_dataframe(self):
        return self.debug_df.copy()

    def _get_total_row_for_validation(self):
        if self.total_row_df.empty:
            return None
        return self.total_row_df.iloc[-1]

    def calculate_total_tl(self):
        return float(self.analysis_df[self.TL_COLUMN].fillna(0).sum())

    def calculate_total_usd(self):
        return float(self.analysis_df[self.USD_COLUMN].fillna(0).sum())

    def calculate_project_count(self):
        return int(len(self.analysis_df))

    def get_max_tl_project_info(self):
        if self.analysis_df.empty:
            return "-", 0.0

        tl_valid_df = self.analysis_df[self.analysis_df[self.TL_COLUMN].notna()].copy()
        if tl_valid_df.empty:
            return "-", 0.0

        max_index = tl_valid_df[self.TL_COLUMN].idxmax()
        max_row = tl_valid_df.loc[max_index]
        return str(max_row[self.PROJECT_COLUMN]).strip(), float(max_row[self.TL_COLUMN])

    def get_max_usd_project_info(self):
        if self.analysis_df.empty:
            return "USD verisi yok", 0.0

        usd_valid_df = self.analysis_df[self.analysis_df[self.USD_COLUMN].notna()].copy()
        if usd_valid_df.empty:
            return "USD verisi yok", 0.0

        max_index = usd_valid_df[self.USD_COLUMN].idxmax()
        max_row = usd_valid_df.loc[max_index]
        return str(max_row[self.PROJECT_COLUMN]).strip(), float(max_row[self.USD_COLUMN])

    def calculate_average_tl(self):
        project_count = self.calculate_project_count()
        if project_count == 0:
            return 0.0
        # Ortalama gerçek proje satırlarına göre hesaplanır: Ortalama TL = Toplam TL / Gerçek Proje Sayısı
        return float(self.calculate_total_tl() / project_count)

    def calculate_average_usd(self):
        project_count = self.calculate_project_count()
        if project_count == 0:
            return 0.0
        # Ortalama gerçek proje satırlarına göre hesaplanır: Ortalama USD = Toplam USD / Gerçek Proje Sayısı
        return float(self.calculate_total_usd() / project_count)

    def generate_summary(self):
        total_tl = self.calculate_total_tl()
        total_usd = self.calculate_total_usd()
        project_count = self.calculate_project_count()
        max_tl_project, max_tl_amount = self.get_max_tl_project_info()
        max_usd_project, max_usd_amount = self.get_max_usd_project_info()

        total_row = self._get_total_row_for_validation()
        if total_row is None:
            validation_note = (
                "Excel içinde toplam satırı bulunmadığı için toplam doğrulaması yapılamamıştır."
            )
        else:
            total_row_tl = float(total_row[self.TL_COLUMN]) if pd.notna(total_row[self.TL_COLUMN]) else 0.0
            total_row_usd = float(total_row[self.USD_COLUMN]) if pd.notna(total_row[self.USD_COLUMN]) else 0.0
            tl_diff = total_tl - total_row_tl
            usd_diff = total_usd - total_row_usd
            validation_note = (
                f"Toplam satırı doğrulaması: TL farkı {tl_diff:,.2f}, "
                f"USD farkı {usd_diff:,.2f}."
            )

        return f"""
Bu ay proje bazlı ödeme analizinde toplam {project_count} proje değerlendirilmiştir.
Toplam ödeme tutarı TL bazında {total_tl:,.2f}, USD bazında {total_usd:,.2f} seviyesindedir.
En yüksek TL tutarlı proje: {max_tl_project} ({max_tl_amount:,.2f} TL).
En yüksek USD tutarlı proje: {max_usd_project} ({max_usd_amount:,.2f} USD).
{validation_note}
        """.strip()

    def run_full_analysis(self):
        max_tl_project, max_tl_amount = self.get_max_tl_project_info()
        max_usd_project, max_usd_amount = self.get_max_usd_project_info()

        return {
            "total_tl": self.calculate_total_tl(),
            "total_usd": self.calculate_total_usd(),
            "project_count": self.calculate_project_count(),
            "max_tl_project": max_tl_project,
            "max_tl_amount": max_tl_amount,
            "max_usd_project": max_usd_project,
            "max_usd_amount": max_usd_amount,
            "summary": self.generate_summary(),
            "debug_df": self.get_debug_dataframe(),
        }
