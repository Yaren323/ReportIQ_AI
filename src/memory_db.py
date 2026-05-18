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

    def get_report_by_id(self, report_id):
        # Tek bir raporu kimliğine göre getirir.
        self.create_database()

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

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
            WHERE id = ?
            """,
            (report_id,),
        )

        report = cursor.fetchone()
        connection.close()

        return report

    def delete_report(self, report_id):
        # Seçilen raporu kimliğine göre siler.
        self.create_database()

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        deleted_count = cursor.rowcount

        connection.commit()
        connection.close()

        return deleted_count > 0

    def get_unique_month_reports(self):
        # Her ay için en güncel (id'si en yüksek) tek raporu getirir.
        self.create_database()

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT r.id, r.report_date, r.month_name, r.total_amount, r.transaction_count,
                   r.company_count, r.pending_count, r.summary
            FROM reports r
            INNER JOIN (
                SELECT month_name, MAX(id) AS max_id
                FROM reports
                GROUP BY month_name
            ) grouped_reports
            ON r.id = grouped_reports.max_id
            ORDER BY r.id DESC
            """
        )

        reports = cursor.fetchall()
        connection.close()

        return reports
