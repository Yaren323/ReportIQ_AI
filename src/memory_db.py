import sqlite3


class MemoryAgent:
    # Basit kullanım için veritabanı dosya adını varsayılan olarak tanımlıyoruz.
    def __init__(self, db_path="reportiq.db"):
        self.db_path = db_path
        self.schema_warning = ""

    def _expected_columns(self):
        # reports tablosunda bulunmasını beklediğimiz kolonlar.
        return [
            "id",
            "report_date",
            "month_name",
            "total_tl",
            "total_usd",
            "project_count",
            "average_tl",
            "average_usd",
            "max_tl_project",
            "max_tl_amount",
            "max_usd_project",
            "max_usd_amount",
            "summary",
        ]

    def _get_existing_columns(self, cursor):
        cursor.execute("PRAGMA table_info(reports)")
        return [row[1] for row in cursor.fetchall()]

    def _set_schema_warning(self, missing_columns):
        missing_text = ", ".join(missing_columns)
        self.schema_warning = (
            "Veritabanı şeması yeni format ile uyumlu değil. "
            f"Eksik kolonlar: {missing_text}. "
            "Lütfen reportiq.db dosyasını yedekleyip sıfırlayın (silip uygulamayı yeniden başlatın)."
        )

    def create_database(self):
        """
        Veritabanını güvenli şekilde hazırlar.
        - Tablo yoksa yeni şema ile oluşturur.
        - Tablo varsa şema kontrolü yapar.
        - Şema uyumsuzsa hata fırlatmak yerine warning üretir ve False döner.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT,
                month_name TEXT,
                total_tl REAL,
                total_usd REAL,
                project_count INTEGER,
                average_tl REAL,
                average_usd REAL,
                max_tl_project TEXT,
                max_tl_amount REAL,
                max_usd_project TEXT,
                max_usd_amount REAL,
                summary TEXT
            )
            """
        )

        existing_columns = self._get_existing_columns(cursor)
        expected_columns = self._expected_columns()

        missing_columns = [col for col in expected_columns if col not in existing_columns]

        if missing_columns:
            self._set_schema_warning(missing_columns)
            connection.commit()
            connection.close()
            return False

        self.schema_warning = ""
        connection.commit()
        connection.close()
        return True

    def get_schema_warning(self):
        return self.schema_warning

    def save_report(
        self,
        report_date,
        month_name,
        total_tl,
        total_usd,
        project_count,
        average_tl,
        average_usd,
        max_tl_project,
        max_tl_amount,
        max_usd_project,
        max_usd_amount,
        summary,
    ):
        if not self.create_database():
            return False

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM reports WHERE month_name = ?",
            (month_name,),
        )
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            connection.close()
            return False

        cursor.execute(
            """
            INSERT INTO reports (
                report_date,
                month_name,
                total_tl,
                total_usd,
                project_count,
                average_tl,
                average_usd,
                max_tl_project,
                max_tl_amount,
                max_usd_project,
                max_usd_amount,
                summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_date,
                month_name,
                float(total_tl),
                float(total_usd),
                int(project_count),
                float(average_tl),
                float(average_usd),
                str(max_tl_project),
                float(max_tl_amount),
                str(max_usd_project),
                float(max_usd_amount),
                summary,
            ),
        )

        connection.commit()
        connection.close()
        return True

    def get_all_reports(self):
        if not self.create_database():
            return []

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                report_date,
                month_name,
                total_tl,
                total_usd,
                project_count,
                average_tl,
                average_usd,
                max_tl_project,
                max_tl_amount,
                max_usd_project,
                max_usd_amount,
                summary
            FROM reports
            ORDER BY id DESC
            """
        )

        reports = cursor.fetchall()
        connection.close()
        return reports

    def get_report_by_id(self, report_id):
        if not self.create_database():
            return None

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                report_date,
                month_name,
                total_tl,
                total_usd,
                project_count,
                average_tl,
                average_usd,
                max_tl_project,
                max_tl_amount,
                max_usd_project,
                max_usd_amount,
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
        if not self.create_database():
            return False

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        deleted_count = cursor.rowcount

        connection.commit()
        connection.close()
        return deleted_count > 0

    def get_unique_month_reports(self):
        if not self.create_database():
            return []

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                r.id,
                r.report_date,
                r.month_name,
                r.total_tl,
                r.total_usd,
                r.project_count,
                r.average_tl,
                r.average_usd,
                r.max_tl_project,
                r.max_tl_amount,
                r.max_usd_project,
                r.max_usd_amount,
                r.summary
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
