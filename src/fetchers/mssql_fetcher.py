"""MSSQL データベースから商品説明（pc_content等）を直接取得する。"""
from __future__ import annotations

from typing import Optional
import pyodbc
from src.config.loader import AppConfig
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.mssql_fetcher")


def fetch_product_descriptions(cfg: AppConfig) -> dict[str, dict]:
    """
    MSSQL から product_snapshots テーブルの pc_content, pc_add_content を取得。
    戻り値: { system_code: { "pc_content": ..., "pc_add_content": ... }, ... }
    """
    try:
        # 接続文字列を構築
        driver = "{SQL Server}"
        conn_str = (
            f"Driver={driver};"
            f"Server={cfg.mssql_host},{cfg.mssql_port};"
            f"Database={cfg.mssql_database};"
            f"UID={cfg.mssql_user};"
            f"PWD={cfg.mssql_password};"
        )
        
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()
        
        # 最新スナップショットの pc_content を取得
        # system_code ごとに最新の snapshot_date のレコードを取得
        query = """
        WITH LatestSnapshots AS (
            SELECT system_code, MAX(snapshot_date) as max_date
            FROM product_snapshots
            GROUP BY system_code
        )
        SELECT 
            ps.system_code,
            ps.pc_content,
            ps.pc_add_content,
            ps.mobile_add_content
        FROM product_snapshots ps
        INNER JOIN LatestSnapshots ls 
            ON ps.system_code = ls.system_code 
            AND ps.snapshot_date = ls.max_date
        WHERE ps.pc_content IS NOT NULL
           OR ps.pc_add_content IS NOT NULL
           OR ps.mobile_add_content IS NOT NULL
        ORDER BY ps.system_code
        """
        
        cursor.execute(query)
        
        result = {}
        for row in cursor.fetchall():
            system_code = row[0]
            pc_content = row[1] or ""
            pc_add_content = row[2] or ""
            mobile_add_content = row[3] or ""
            
            result[system_code] = {
                "pc_content": pc_content,
                "pc_add_content": pc_add_content,
                "mobile_add_content": mobile_add_content,
            }
        
        cursor.close()
        conn.close()
        
        logger.info("MSSQL から商品説明取得: %d件", len(result))
        return result
        
    except Exception as e:
        logger.error("MSSQL 接続エラー: %s", e)
        return {}


def fetch_consumer_prices(cfg: AppConfig) -> dict[str, int]:
    """
    MSSQL から product_snapshots テーブルの consumer_price を取得。
    戻り値: { system_code: consumer_price, ... }
    """
    try:
        driver = "{SQL Server}"
        conn_str = (
            f"Driver={driver};"
            f"Server={cfg.mssql_host},{cfg.mssql_port};"
            f"Database={cfg.mssql_database};"
            f"UID={cfg.mssql_user};"
            f"PWD={cfg.mssql_password};"
        )
        
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()
        
        # 最新スナップショットの consumer_price を取得（全商品）
        query = """
        WITH LatestSnapshots AS (
            SELECT system_code, MAX(snapshot_date) as max_date
            FROM product_snapshots
            GROUP BY system_code
        )
        SELECT 
            ps.system_code,
            ps.consumer_price
        FROM product_snapshots ps
        INNER JOIN LatestSnapshots ls 
            ON ps.system_code = ls.system_code 
            AND ps.snapshot_date = ls.max_date
        ORDER BY ps.system_code
        """
        
        cursor.execute(query)
        
        result = {}
        for row in cursor.fetchall():
            system_code = row[0]
            consumer_price = row[1] or 0
            if consumer_price > 0:
                result[system_code] = consumer_price
        
        cursor.close()
        conn.close()
        
        logger.info("MSSQL から希望小売価格取得: %d件", len(result))
        return result
        
    except Exception as e:
        logger.error("MSSQL 接続エラー: %s", e)
        return {}


def fetch_product_categories_per_item(cfg: AppConfig) -> dict[str, list[dict[str, str]]]:
    """
    MSSQL から product_snapshot_categories テーブルで、
    各商品（system_code）がどのカテゴリに属しているかを取得。
    戻り値: { system_code: [{ "category_uid": "11", "category_name": "特別SALE" }, ...], ... }
    """
    try:
        driver = "{SQL Server}"
        conn_str = (
            f"Driver={driver};"
            f"Server={cfg.mssql_host},{cfg.mssql_port};"
            f"Database={cfg.mssql_database};"
            f"UID={cfg.mssql_user};"
            f"PWD={cfg.mssql_password};"
        )
        
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()
        
        # 各商品のカテゴリを取得（最新スナップショット日付を使用）
        query = """
        WITH LatestSnapshots AS (
            SELECT system_code, MAX(snapshot_date) as max_date
            FROM product_snapshots
            GROUP BY system_code
        )
        SELECT 
            ps.system_code,
            psc.category_uid,
            psc.category_name,
            psc.is_main_category
        FROM product_snapshot_categories psc
        INNER JOIN product_snapshots ps 
            ON psc.snapshot_id = ps.snapshot_id
        INNER JOIN LatestSnapshots ls
            ON ps.system_code = ls.system_code
            AND ps.snapshot_date = ls.max_date
        ORDER BY ps.system_code, psc.category_uid
        """
        
        cursor.execute(query)
        
        result: dict[str, list[dict[str, str]]] = {}
        for row in cursor.fetchall():
            system_code = row[0]
            category_uid = str(row[1])
            category_name = row[2]
            # is_main_category = row[3]  # フラグが必要な場合は追加可能
            
            if system_code not in result:
                result[system_code] = []
            
            result[system_code].append({
                "category_uid": category_uid,
                "category_name": category_name,
            })
        
        cursor.close()
        conn.close()
        
        logger.info("MSSQL から商品別カテゴリ取得: %d商品", len(result))
        return result
        
    except Exception as e:
        logger.error("MSSQL 商品別カテゴリ取得エラー: %s", e)
        return {}


def fetch_categories(cfg: AppConfig) -> list[dict[str, str]]:
    """
    MSSQL から product_snapshot_categories テーブルの最新スナップショットのすべてのカテゴリを取得。
    戻り値: [{ "category_uid": "11", "category_name": "特別SALE" }, ...]
    """
    try:
        driver = "{SQL Server}"
        conn_str = (
            f"Driver={driver};"
            f"Server={cfg.mssql_host},{cfg.mssql_port};"
            f"Database={cfg.mssql_database};"
            f"UID={cfg.mssql_user};"
            f"PWD={cfg.mssql_password};"
        )
        
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()
        
        # 最新スナップショット日付を取得
        query_max_date = """
        SELECT MAX(snapshot_date) FROM product_snapshots
        """
        cursor.execute(query_max_date)
        max_date = cursor.fetchone()[0]
        
        if not max_date:
            logger.warning("スナップショットが見つかりません")
            return []
        
        # 最新スナップショット日付に属するすべてのカテゴリをユニークに取得
        query = """
        SELECT DISTINCT 
            category_uid,
            category_name
        FROM product_snapshot_categories psc
        INNER JOIN product_snapshots ps 
            ON psc.snapshot_id = ps.snapshot_id
        WHERE ps.snapshot_date = ?
        ORDER BY category_uid
        """
        
        cursor.execute(query, (max_date,))
        
        result = []
        for row in cursor.fetchall():
            result.append({
                "category_uid": str(row[0]),
                "category_name": row[1],
            })
        
        cursor.close()
        conn.close()
        
        logger.info("MSSQL からカテゴリ取得: %d件", len(result))
        return result
        
    except Exception as e:
        logger.error("MSSQL カテゴリ取得エラー: %s", e)
        return []

