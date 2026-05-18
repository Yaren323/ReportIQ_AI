import pandas as pd


class CompareAgent:
    """
    Önceki ay ve güncel ay mutabakat verilerini karşılaştıran agent.
    """

    def __init__(self, previous_df: pd.DataFrame, current_df: pd.DataFrame):
        self.previous_df = previous_df
        self.current_df = current_df

    def calculate_percentage_change(self, old_value, new_value):
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100

    def get_basic_metrics(self, df):
        return {
            "total_amount": df["Tutar"].sum(),
            "transaction_count": len(df),
            "company_count": df["Firma"].nunique(),
            "pending_count": len(df[df["Durum"] == "Bekliyor"])
        }

    def compare_metrics(self):
        previous_metrics = self.get_basic_metrics(self.previous_df)
        current_metrics = self.get_basic_metrics(self.current_df)

        comparison = {}

        for key in previous_metrics:
            old_value = previous_metrics[key]
            new_value = current_metrics[key]

            comparison[key] = {
                "previous": old_value,
                "current": new_value,
                "difference": new_value - old_value,
                "percentage_change": self.calculate_percentage_change(old_value, new_value)
            }

        return comparison

    def generate_comparison_summary(self):
        comparison = self.compare_metrics()

        total_diff = comparison["total_amount"]["difference"]
        total_pct = comparison["total_amount"]["percentage_change"]

        pending_diff = comparison["pending_count"]["difference"]

        if total_diff > 0:
            total_comment = "artış göstermiştir"
        elif total_diff < 0:
            total_comment = "azalış göstermiştir"
        else:
            total_comment = "değişmemiştir"

        summary = f"""
        Güncel ay toplam tutarı, önceki aya göre {abs(total_diff):,.0f} TL fark ile
        %{total_pct:.2f} oranında {total_comment}.

        Bekleyen işlem sayısındaki değişim: {pending_diff}

        Bekleyen işlem sayısı arttıysa ilgili kayıtların kontrol edilmesi önerilir.
        Bekleyen işlem sayısı azaldıysa mutabakat sürecinde iyileşme olduğu düşünülebilir.
        """

        return summary

    def run_comparison(self):
        return {
            "comparison": self.compare_metrics(),
            "summary": self.generate_comparison_summary()
        }