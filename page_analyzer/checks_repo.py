import psycopg2
from psycopg2.extras import RealDictCursor


class CheckRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def get_content_by_url_id(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC", (id,))
                return cur.fetchall()
            
    def get_last_check_date_by_id(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT created_at FROM url_checks WHERE url_id = %s ORDER BY id DESC", (id,))
                return cur.fetchone()["created_at"]

            
    def save(self, url_id):
        self._create(url_id)

    def _create(self, url_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO url_checks (url_id, created_at) VALUES (%s, CURRENT_DATE)
                    RETURNING id
                    """,
                    (url_id,)
                )
                id = cur.fetchone()[0]
            conn.commit()
            
    
            
    