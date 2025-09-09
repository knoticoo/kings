"""
Rotation logic for fair MVP and winner assignments
"""

import logging
from typing import List, Dict, Any
from .database import DatabaseManager

logger = logging.getLogger(__name__)

class RotationLogic:
    """Handles fair rotation logic for MVP and winner assignments"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def can_assign_mvp(self) -> bool:
        """
        Check if MVP can be assigned (all non-excluded players have been MVP at least once)
        """
        query = """
            SELECT 
                COUNT(*) as total_players,
                COUNT(CASE WHEN mvp_count > 0 THEN 1 END) as players_with_mvp
            FROM players 
            WHERE is_excluded = 0
        """
        result = await self.db_manager.execute_query(query)
        
        if result:
            data = result[0]
            total_players = data['total_players']
            players_with_mvp = data['players_with_mvp']
            
            # Can assign if all players have been MVP at least once
            can_assign = players_with_mvp >= total_players
            logger.info(f"MVP rotation check: {players_with_mvp}/{total_players} players have been MVP")
            return can_assign
        
        return False
    
    async def get_eligible_players(self) -> List[Dict[str, Any]]:
        """
        Get players eligible for MVP assignment (prioritizing those with fewer MVP awards)
        """
        query = """
            SELECT * FROM players 
            WHERE is_excluded = 0 
            ORDER BY mvp_count ASC, name ASC
        """
        return await self.db_manager.execute_query(query)
    
    async def can_assign_winner(self) -> bool:
        """
        Check if winner can be assigned (all alliances have won at least once)
        """
        query = """
            SELECT 
                COUNT(*) as total_alliances,
                COUNT(CASE WHEN win_count > 0 THEN 1 END) as alliances_with_wins
            FROM alliances
        """
        result = await self.db_manager.execute_query(query)
        
        if result:
            data = result[0]
            total_alliances = data['total_alliances']
            alliances_with_wins = data['alliances_with_wins']
            
            # Can assign if all alliances have won at least once
            can_assign = alliances_with_wins >= total_alliances
            logger.info(f"Winner rotation check: {alliances_with_wins}/{total_alliances} alliances have won")
            return can_assign
        
        return False
    
    async def get_eligible_alliances(self) -> List[Dict[str, Any]]:
        """
        Get alliances eligible for winner assignment (prioritizing those with fewer wins)
        """
        query = """
            SELECT * FROM alliances 
            ORDER BY win_count ASC, name ASC
        """
        return await self.db_manager.execute_query(query)
    
    async def get_rotation_status(self) -> Dict[str, Any]:
        """
        Get comprehensive rotation status for both MVP and winner assignments
        """
        mvp_can_assign = await self.can_assign_mvp()
        winner_can_assign = await self.can_assign_winner()
        
        eligible_players = await self.get_eligible_players() if mvp_can_assign else []
        eligible_alliances = await self.get_eligible_alliances() if winner_can_assign else []
        
        # Get rotation statistics
        mvp_stats_query = """
            SELECT 
                COUNT(*) as total_players,
                COUNT(CASE WHEN mvp_count > 0 THEN 1 END) as players_with_mvp,
                AVG(mvp_count) as avg_mvp_count,
                MAX(mvp_count) as max_mvp_count,
                MIN(mvp_count) as min_mvp_count
            FROM players 
            WHERE is_excluded = 0
        """
        
        winner_stats_query = """
            SELECT 
                COUNT(*) as total_alliances,
                COUNT(CASE WHEN win_count > 0 THEN 1 END) as alliances_with_wins,
                AVG(win_count) as avg_win_count,
                MAX(win_count) as max_win_count,
                MIN(win_count) as min_win_count
            FROM alliances
        """
        
        mvp_stats = await self.db_manager.execute_query(mvp_stats_query)
        winner_stats = await self.db_manager.execute_query(winner_stats_query)
        
        return {
            'mvp': {
                'can_assign': mvp_can_assign,
                'eligible_players': eligible_players,
                'stats': mvp_stats[0] if mvp_stats else {}
            },
            'winner': {
                'can_assign': winner_can_assign,
                'eligible_alliances': eligible_alliances,
                'stats': winner_stats[0] if winner_stats else {}
            }
        }
    
    async def assign_mvp(self, player_id: int, event_id: int) -> bool:
        """
        Assign MVP to a player for an event with rotation logic
        """
        try:
            # Check if assignment is allowed
            if not await self.can_assign_mvp():
                logger.warning("MVP assignment blocked by rotation logic")
                return False
            
            # Get eligible players
            eligible_players = await self.get_eligible_players()
            if not any(p['id'] == player_id for p in eligible_players):
                logger.warning(f"Player {player_id} not eligible for MVP assignment")
                return False
            
            # Remove current MVP status from all players
            await self.db_manager.execute_update(
                "UPDATE players SET is_current_mvp = 0"
            )
            
            # Create MVP assignment
            await self.db_manager.execute_update(
                "INSERT INTO mvp_assignments (player_id, event_id, assigned_at) VALUES (?, ?, datetime('now'))",
                (player_id, event_id)
            )
            
            # Update player status
            await self.db_manager.execute_update(
                "UPDATE players SET is_current_mvp = 1, mvp_count = mvp_count + 1 WHERE id = ?",
                (player_id,)
            )
            
            # Update event status
            await self.db_manager.execute_update(
                "UPDATE events SET has_mvp = 1 WHERE id = ?",
                (event_id,)
            )
            
            logger.info(f"Successfully assigned MVP: Player {player_id} for Event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign MVP: {e}")
            return False
    
    async def assign_winner(self, alliance_id: int, event_id: int) -> bool:
        """
        Assign winning alliance for an event with rotation logic
        """
        try:
            # Check if assignment is allowed
            if not await self.can_assign_winner():
                logger.warning("Winner assignment blocked by rotation logic")
                return False
            
            # Get eligible alliances
            eligible_alliances = await self.get_eligible_alliances()
            if not any(a['id'] == alliance_id for a in eligible_alliances):
                logger.warning(f"Alliance {alliance_id} not eligible for winner assignment")
                return False
            
            # Check if event already has winner
            existing_winner = await self.db_manager.execute_query(
                "SELECT id FROM winner_assignments WHERE event_id = ?",
                (event_id,)
            )
            if existing_winner:
                logger.warning(f"Event {event_id} already has a winner assigned")
                return False
            
            # Remove current winner status from all alliances
            await self.db_manager.execute_update(
                "UPDATE alliances SET is_current_winner = 0"
            )
            
            # Create winner assignment
            await self.db_manager.execute_update(
                "INSERT INTO winner_assignments (alliance_id, event_id, assigned_at) VALUES (?, ?, datetime('now'))",
                (alliance_id, event_id)
            )
            
            # Update alliance status
            await self.db_manager.execute_update(
                "UPDATE alliances SET is_current_winner = 1, win_count = win_count + 1 WHERE id = ?",
                (alliance_id,)
            )
            
            # Update event status
            await self.db_manager.execute_update(
                "UPDATE events SET has_winner = 1 WHERE id = ?",
                (event_id,)
            )
            
            logger.info(f"Successfully assigned winner: Alliance {alliance_id} for Event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign winner: {e}")
            return False