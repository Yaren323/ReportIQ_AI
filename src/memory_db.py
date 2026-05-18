import sqlite3


class MemoryAgent:
    # Basit kullanım için veritabanı dosya adını varsayılan olarak tanımlıyoruz
    def __init__(self, db_path="reportiq.db"):
        self.db_path = db_path

    def create_database(self):
        # Veritabanına bağlan (yoksa otomatik oluşturulur)
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        # reports tablosunu oluştur (zaten varsa tekrar oluşturmaz)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT,
                month_name TEXT,
                total_amount REAL,
                transaction_count INTEGER,
                company_count INTEGER,
                pending_count INTEGER,
                summary TEXT
            )
            """
        )

        # Değişiklikleri kaydet ve bağlantıyı kapat
        connection.commit()
        connection.close()

    def save_report(
        self,
        report_date,
        month_name,
        total_amount,
        transaction_count,
        company_count,
        pending_count,
        summary,
    ):
        # Kayıt eklemeden önce tabloyu hazır hale getir
        self.create_database()

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        # Aynı ay daha önce kaydedildiyse tekrar kayıt ekleme
        cursor.execute(
            "SELECT COUNT(*) FROM reports WHERE month_name = ?",
            (month_name,),
        )
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            connection.close()
            return False

        # Yeni analiz raporunu tabloya ekle
        cursor.execute(
            """
            INSERT INTO reports (
                report_date,
                month_name,
                total_amount,
                transaction_count,
                company_count,
                pending_count,
                summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_date,
                month_name,
                total_amount,
                transaction_count,
                company_count,
                pending_count,
                summary,
            ),
        )

        connection.commit()
        connection.close()
        return True

    def get_all_reports(self):
        # Tablonun mevcut olduğundan emin ol
        self.create_database()

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        # Tüm raporları en yeni kayıt üstte olacak şekilde getir
        cursor.execute(
            """
            SELECT
                id,
                report_date,
                month_name,
                total_amount,
                transaction_count,
                company_count,
                pending_count,
                summary
            FROM reports
            ORDER BY id DESC
            """
        )

        reports = cursor.fetchall()
        connection.close()

        return reports
