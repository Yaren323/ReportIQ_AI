import pandas as pd


class AnalyzerAgent:

    def __init__(self, df):
        self.df = df

    def calculate_total_amount(self):
        return self.df["Tutar"].sum()

    def calculate_transaction_count(self):
        return len(self.df)

    def calculate_company_count(self):
        return self.df["Firma"].nunique()

    def calculate_pending_count(self):
        return len(self.df[self.df["Durum"] == "Bekliyor"])

    def generate_summary(self):

        total_amount = self.calculate_total_amount()
        transaction_count = self.calculate_transaction_count()
        company_count = self.calculate_company_count()
        pending_count = self.calculate_pending_count()

        summary = f"""
        Bu ay toplam {total_amount:,.0f} TL işlem gerçekleştirilmiştir.

        Toplam işlem sayısı: {transaction_count}

        Sistemde işlem yapan toplam firma sayısı: {company_count}

        Bekleyen işlem sayısı: {pending_count}

        Bekleyen işlemlerin kontrol edilmesi önerilir.
        """

        return summary

    def run_full_analysis(self):

        results = {
            "total_amount": self.calculate_total_amount(),
            "transaction_count": self.calculate_transaction_count(),
            "company_count": self.calculate_company_count(),
            "pending_count": self.calculate_pending_count(),
            "summary": self.generate_summary()
        }

        return results