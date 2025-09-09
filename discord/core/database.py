"""
Database utilities and connection management
"""

import aiosqlite
import logging
from typing import List, Dict, Any, Optional, Union
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with proper cleanup"""
        conn = None
        try:
            conn = await aiosqlite.connect(self.db_path)
            conn.row_factory = aiosqlite.Row
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                await conn.close()
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return cursor.rowcount
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries in a transaction"""
        async with self.get_connection() as conn:
            cursor = await conn.executemany(query, params_list)
            await conn.commit()
            return cursor.rowcount
    
    async def execute_script(self, script: str) -> None:
        """Execute a SQL script"""
        async with self.get_connection() as conn:
            await conn.executescript(script)
            await conn.commit()
    
    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = await self.execute_query(query, (table_name,))
        return len(result) > 0
    
    async def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get information about a table's columns"""
        query = f"PRAGMA table_info({table_name})"
        return await self.execute_query(query)
    
    async def validate_database(self) -> bool:
        """Validate that all required tables exist"""
        required_tables = [
            'players', 'alliances', 'events', 'mvp_assignments', 
            'winner_assignments', 'guides', 'guide_categories', 'blacklist'
        ]
        
        for table in required_tables:
            if not await self.check_table_exists(table):
                logger.error(f"Required table '{table}' not found in database")
                return False
        
        logger.info("Database validation successful")
        return True

class DatabaseHelper:
    """Static helper methods for common database operations"""
    
    @staticmethod
    async def get_players(db_manager: DatabaseManager, include_excluded: bool = False) -> List[Dict[str, Any]]:
        """Get all players from database"""
        query = "SELECT * FROM players"
        if not include_excluded:
            query += " WHERE is_excluded = 0"
        query += " ORDER BY name ASC"
        
        return await db_manager.execute_query(query)
    
    @staticmethod
    async def get_alliances(db_manager: DatabaseManager) -> List[Dict[str, Any]]:
        """Get all alliances from database"""
        query = "SELECT * FROM alliances ORDER BY name ASC"
        return await db_manager.execute_query(query)
    
    @staticmethod
    async def get_events(db_manager: DatabaseManager, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get events from database"""
        query = "SELECT * FROM events ORDER BY event_date DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        return await db_manager.execute_query(query)
    
    @staticmethod
    async def get_guides(db_manager: DatabaseManager, category_id: Optional[int] = None, 
                        search_term: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get guides from database with optional filtering"""
        query = """
            SELECT g.*, gc.name as category_name 
            FROM guides g 
            LEFT JOIN guide_categories gc ON g.category_id = gc.id 
            WHERE g.is_published = 1
        """
        params = []
        
        if category_id:
            query += " AND g.category_id = ?"
            params.append(category_id)
        
        if search_term:
            query += " AND (g.title LIKE ? OR g.content LIKE ? OR g.excerpt LIKE ?)"
            search_param = f"%{search_term}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY g.created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return await db_manager.execute_query(query, tuple(params))
    
    @staticmethod
    async def get_blacklist_entries(db_manager: DatabaseManager) -> List[Dict[str, Any]]:
        """Get all blacklist entries"""
        query = "SELECT * FROM blacklist ORDER BY created_at DESC"
        return await db_manager.execute_query(query)
    
    @staticmethod
    async def get_current_mvp(db_manager: DatabaseManager) -> Optional[Dict[str, Any]]:
        """Get current MVP player"""
        query = "SELECT * FROM players WHERE is_current_mvp = 1 LIMIT 1"
        result = await db_manager.execute_query(query)
        return result[0] if result else None
    
    @staticmethod
    async def get_current_winner(db_manager: DatabaseManager) -> Optional[Dict[str, Any]]:
        """Get current winning alliance"""
        query = "SELECT * FROM alliances WHERE is_current_winner = 1 LIMIT 1"
        result = await db_manager.execute_query(query)
        return result[0] if result else None
    
    @staticmethod
    async def get_stats(db_manager: DatabaseManager) -> Dict[str, int]:
        """Get basic statistics"""
        queries = {
            'total_players': "SELECT COUNT(*) as count FROM players",
            'total_alliances': "SELECT COUNT(*) as count FROM alliances", 
            'total_events': "SELECT COUNT(*) as count FROM events",
            'total_guides': "SELECT COUNT(*) as count FROM guides WHERE is_published = 1",
            'total_blacklist': "SELECT COUNT(*) as count FROM blacklist"
        }
        
        stats = {}
        for key, query in queries.items():
            result = await db_manager.execute_query(query)
            stats[key] = result[0]['count'] if result else 0
        
        return stats