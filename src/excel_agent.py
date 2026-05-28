import re
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class ExcelAgentConfig:
    sample_size: int = 1000
    preview_size: int = 20


class ExcelAgent:
    DATE_HINTS = ("date", "tarih", "zaman", "time", "day", "month", "year")
    MONEY_HINTS = ("tutar", "amount", "fiyat", "price", "cost", "ucret", "ücret", "usd", "tl", "eur", "gelir", "ciro")
    IDENTITY_HINTS = ("proje", "project", "musteri", "müşteri", "client", "customer", "aciklama", "açıklama", "desc", "name", "ad")
    TOTAL_TOKENS = ("toplam", "toplam tutar", "genel toplam", "total", "grand total", "sum")

    def __init__(self, config: ExcelAgentConfig | None = None):
        self.config = config or ExcelAgentConfig()

    @staticmethod
    def _normalize_name(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value).strip().lower())

    @staticmethod
    def _make_unique_columns(columns: list[Any]) -> list[str]:
        seen: dict[str, int] = {}
        out: list[str] = []
        for col in columns:
            base = str(col).strip() if str(col).strip() else "Kolon"
            count = seen.get(base, 0) + 1
            seen[base] = count
            out.append(base if count == 1 else f"{base}_{count}")
        return out

    def _is_total_row(self, row: pd.Series) -> bool:
        text = " ".join([str(v).strip().lower() for v in row.tolist() if pd.notna(v)])
        if not text:
            return False
        return any(token in text for token in self.TOTAL_TOKENS)

    def _is_header_like_row(self, row: pd.Series, columns: list[str]) -> bool:
        row_values = [str(v).strip().lower() for v in row.tolist()]
        if not any(row_values):
            return False
        col_values = [str(c).strip().lower() for c in columns]
        overlap = sum(1 for v in row_values if v and v in col_values)
        return overlap >= max(2, len(columns) // 3)

    def _split_total_rows(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        if df.empty:
            return df.copy(), df.head(0).copy()
        total_mask = df.apply(self._is_total_row, axis=1)
        return df.loc[~total_mask].copy(), df.loc[total_mask].copy()

    def _clean_data_rows(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        if df.empty:
            return df.copy(), df.head(0).copy()
        work = df.copy()
        work = work[~work.isna().all(axis=1)].copy()
        header_like_mask = work.apply(lambda r: self._is_header_like_row(r, list(work.columns)), axis=1)
        header_like_rows = work.loc[header_like_mask].copy()
        work = work.loc[~header_like_mask].copy()
        return work, header_like_rows

    def _classify_columns(self, sample_df: pd.DataFrame) -> dict[str, list[str]]:
        numeric_cols: list[str] = []
        text_cols: list[str] = []
        date_like_cols: list[str] = []
        money_like_cols: list[str] = []
        identity_like_cols: list[str] = []

        for col in sample_df.columns:
            s = sample_df[col]
            col_name = self._normalize_name(col)

            numeric_candidate = pd.to_numeric(s, errors="coerce")
            non_null_count = int(s.notna().sum())
            numeric_ratio = float((numeric_candidate.notna().sum() / non_null_count) if non_null_count else 0)

            if pd.api.types.is_numeric_dtype(s) or numeric_ratio >= 0.8:
                numeric_cols.append(str(col))
            else:
                text_cols.append(str(col))

            try:
                date_candidate = pd.to_datetime(s, errors="coerce", dayfirst=True)
                date_ratio = float((date_candidate.notna().sum() / non_null_count) if non_null_count else 0)
                if date_ratio >= 0.7 or any(token in col_name for token in self.DATE_HINTS):
                    date_like_cols.append(str(col))
            except Exception:
                if any(token in col_name for token in self.DATE_HINTS):
                    date_like_cols.append(str(col))

            if any(token in col_name for token in self.MONEY_HINTS):
                money_like_cols.append(str(col))
            elif str(col) in numeric_cols:
                abs_mean = float(numeric_candidate.dropna().abs().mean()) if numeric_candidate.notna().any() else 0.0
                if abs_mean >= 100:
                    money_like_cols.append(str(col))

            if any(token in col_name for token in self.IDENTITY_HINTS):
                identity_like_cols.append(str(col))
            elif str(col) in text_cols and non_null_count > 0:
                nunique_ratio = float(s.astype(str).nunique(dropna=True) / non_null_count)
                if 0.1 <= nunique_ratio <= 0.95:
                    identity_like_cols.append(str(col))

        return {
            "numeric": sorted(set(numeric_cols)),
            "text": sorted(set(text_cols)),
            "date_like": sorted(set(date_like_cols)),
            "money_like": sorted(set(money_like_cols)),
            "identity_like": sorted(set(identity_like_cols)),
        }

    @staticmethod
    def _column_health(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for col in df.columns:
            s = df[col]
            rows.append(
                {
                    "Kolon": str(col),
                    "Bos Deger": int(s.isna().sum()),
                    "Bos Orani (%)": round(float(s.isna().mean() * 100), 2),
                    "Benzersiz Deger": int(s.nunique(dropna=True)),
                }
            )
        return pd.DataFrame(rows).sort_values(by=["Bos Deger", "Kolon"], ascending=[False, True]).reset_index(drop=True)

    def _numeric_summary(self, df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
        rows = []
        for col in numeric_cols:
            s = pd.to_numeric(df[col], errors="coerce")
            if s.notna().any():
                rows.append({"Kolon": col, "Toplam": float(s.sum()), "Ortalama": float(s.mean()), "Min": float(s.min()), "Max": float(s.max())})
        return pd.DataFrame(rows)

    def _text_summary(self, df: pd.DataFrame, text_cols: list[str]) -> pd.DataFrame:
        rows = []
        for col in text_cols:
            s = df[col].astype(str)
            rows.append({"Kolon": col, "Benzersiz Deger Sayisi": int(s.nunique(dropna=True))})
        return pd.DataFrame(rows)

    def _date_summary(self, df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
        rows = []
        for col in date_cols:
            try:
                s = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
                if s.notna().any():
                    rows.append({"Kolon": col, "Baslangic": s.min(), "Bitis": s.max()})
            except Exception:
                continue
        return pd.DataFrame(rows)

    def _money_summary(self, df: pd.DataFrame, money_cols: list[str]) -> pd.DataFrame:
        rows = []
        for col in money_cols:
            s = pd.to_numeric(df[col], errors="coerce")
            if s.notna().any():
                rows.append({"Kolon": col, "Toplam": float(s.sum()), "En Yuksek": float(s.max())})
        return pd.DataFrame(rows)

    @staticmethod
    def _suggestions(classes: dict[str, list[str]]) -> dict[str, list[str]]:
        numeric_cols = classes["numeric"]
        identity_cols = classes["identity_like"] or classes["text"]
        money_cols = classes["money_like"]
        date_cols = classes["date_like"]
        total_candidates = money_cols if money_cols else numeric_cols[:5]
        group_candidates = identity_cols[:5] + date_cols[:2]
        metric_candidates = []
        for col in total_candidates[:5]:
            metric_candidates.extend([f"Toplam {col}", f"Ortalama {col}", f"En yuksek {col}"])
        if identity_cols:
            metric_candidates.extend([f"{identity_cols[0]} sayisi", f"Benzersiz {identity_cols[0]} sayisi"])
        if date_cols:
            metric_candidates.append(f"{date_cols[0]} bazinda aylik degisim")
        chart_candidates = []
        if identity_cols and total_candidates:
            chart_candidates.append(f"{identity_cols[0]} bazinda {total_candidates[0]} cubuk grafik")
        if date_cols and total_candidates:
            chart_candidates.append(f"{date_cols[0]} bazinda {total_candidates[0]} cizgi grafik")
        if len(total_candidates) >= 2:
            chart_candidates.append(f"{total_candidates[0]} ve {total_candidates[1]} karsilastirma grafigi")
        return {
            "summable_columns": sorted(set(total_candidates)),
            "groupable_columns": sorted(set(group_candidates)),
            "dashboard_metrics": metric_candidates[:10],
            "recommended_charts": chart_candidates[:8],
        }

    @staticmethod
    def _extract_total_rows_values(total_rows_df: pd.DataFrame) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        if total_rows_df.empty:
            return out
        for _, row in total_rows_df.iterrows():
            text_parts = [str(v).strip() for v in row.tolist() if pd.notna(v)]
            nums = {}
            for col in total_rows_df.columns:
                n = pd.to_numeric(pd.Series([row[col]]), errors="coerce").iloc[0]
                if pd.notna(n):
                    nums[str(col)] = float(n)
            out.append({"metin": " | ".join(text_parts)[:500], "sayisal_degerler": nums})
        return out

    def analyze_excel(self, file_obj) -> dict[str, Any]:
        excel_file = pd.ExcelFile(file_obj)
        if not excel_file.sheet_names:
            raise ValueError("Excel icinde sayfa bulunamadi.")

        sheet_reports = []
        total_rows = 0
        total_data_rows = 0
        total_cols = 0
        total_titled_columns = 0
        total_rows_summary = []
        sheet_errors = []

        for sheet_name in excel_file.sheet_names:
            try:
                df = excel_file.parse(sheet_name=sheet_name)
                df.columns = self._make_unique_columns(list(df.columns))
                df_no_total, total_rows_df = self._split_total_rows(df)
                clean_df, header_like_rows = self._clean_data_rows(df_no_total)
                sample_df = clean_df.head(self.config.sample_size).copy()

                classes = self._classify_columns(sample_df)
                suggestions = self._suggestions(classes)

                empty_rows = int(sample_df.isna().all(axis=1).sum())
                empty_columns = [str(c) for c in sample_df.columns if sample_df[c].isna().all()]
                duplicate_rows = int(sample_df.duplicated().sum())
                empty_cell_ratio = round(float(sample_df.isna().mean().mean() * 100), 2) if not sample_df.empty else 0.0
                missing_data_columns = [str(c) for c in sample_df.columns if sample_df[c].isna().any() and c not in empty_columns]

                report = {
                    "sheet_name": sheet_name,
                    "row_count": int(len(clean_df)),
                    "data_row_count": int(len(clean_df)),
                    "column_count": int(len(df.columns)),
                    "columns": [str(c) for c in df.columns.tolist()],
                    "titled_column_count": int(sum(1 for c in df.columns if str(c).strip() and str(c).strip().lower() != "unnamed")),
                    "filled_cell_count": int(clean_df.notna().sum().sum()) if not clean_df.empty else 0,
                    "empty_cell_count": int(clean_df.isna().sum().sum()) if not clean_df.empty else 0,
                    "empty_row_count": empty_rows,
                    "empty_columns": empty_columns,
                    "duplicate_row_count": duplicate_rows,
                    "empty_cell_ratio": empty_cell_ratio,
                    "missing_data_columns": missing_data_columns,
                    "column_classes": classes,
                    "column_health": self._column_health(sample_df),
                    "numeric_summary": self._numeric_summary(sample_df, classes["numeric"]),
                    "text_summary": self._text_summary(sample_df, classes["text"]),
                    "date_summary": self._date_summary(sample_df, classes["date_like"]),
                    "money_summary": self._money_summary(sample_df, classes["money_like"]),
                    "suggestions": suggestions,
                    "preview": sample_df.head(self.config.preview_size),
                }
                sheet_reports.append(report)

                total_rows += int(len(df))
                total_cols += int(len(df.columns))
                total_data_rows += int(len(clean_df))
                total_titled_columns += report["titled_column_count"]

                total_rows_summary.append(
                    {
                        "sheet_name": sheet_name,
                        "toplam_satiri_sayisi": int(len(total_rows_df)),
                        "header_benzeri_satir_sayisi": int(len(header_like_rows)),
                        "satirlar": self._extract_total_rows_values(total_rows_df),
                    }
                )
            except Exception as exc:
                sheet_errors.append({"sheet_name": sheet_name, "hata": str(exc)})
                continue

        return {
            "file_name": getattr(file_obj, "name", "Bilinmeyen Dosya"),
            "sheet_count": len(sheet_reports),
            "total_rows": total_rows,
            "total_data_rows": total_data_rows,
            "total_columns": total_cols,
            "total_titled_columns": total_titled_columns,
            "sheets": sheet_reports,
            "total_rows_summary": total_rows_summary,
            "sheet_errors": sheet_errors,
        }
