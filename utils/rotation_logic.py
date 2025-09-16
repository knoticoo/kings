"""
Rotation Logic Utility Module

This module implements the core rotation logic for MVP and winner assignments.

Key Rules:
1. MVP Rotation: Players with the fewest MVP wins are prioritized for selection
2. Alliance Rotation: Alliances with the fewest wins are prioritized for selection
3. Auto-cycling: When all players/alliances have won at least once, the cycle resets
   and those with the minimum count become eligible again

This ensures fair distribution while allowing continuous assignments without locks.
"""

# Import models dynamically to avoid circular imports
def get_models():
    from models import Player, Alliance, MVPAssignment, WinnerAssignment
    return Player, Alliance, MVPAssignment, WinnerAssignment

def can_assign_mvp(user_id=None):
    """
    Check if we can assign MVP based on rotation logic
    
    Args:
        user_id: User ID for data isolation (required)
    
    Returns:
        bool: True if MVP can be assigned, False otherwise
    
    Logic:
        - If no active (non-excluded) players exist, return False
        - MVP assignments are always allowed - rotation cycles automatically
        - When all active players have been MVP, eligible players are those with minimum MVP count
    """
    try:
        if not user_id:
            return False
            
        from database_manager import query_user_data
        Player, Alliance, MVPAssignment, WinnerAssignment = get_models()
        
        # Get all active (non-excluded) players for this user
        all_active_players = query_user_data(Player, user_id, is_excluded=False)
        
        if not all_active_players:
            return False  # No active players to assign MVP to
        
        # Check if any MVP assignments have been made for this user
        total_assignments = len(query_user_data(MVPAssignment, user_id))
        
        if total_assignments == 0:
            return True  # First assignment is always allowed
        
        # Always allow MVP assignment - rotation handles fairness automatically
        return True
        
    except Exception as e:
        print(f"Error in can_assign_mvp: {str(e)}")
        return False

def get_eligible_players(user_id=None):
    """
    Get list of players eligible for MVP assignment
    
    Args:
        user_id: User ID for data isolation (required)
    
    Returns:
        list: List of Player objects eligible for MVP assignment
    
    Logic:
        - Excludes players where is_excluded = True from MVP rotation
        - If this is the first round (not all active players have been MVP), 
          return active players who haven't been MVP yet
        - If all active players have been MVP, return active players with the minimum MVP count
    """
    try:
        if not user_id:
            return []
            
        from database_manager import query_user_data
        Player, Alliance, MVPAssignment, WinnerAssignment = get_models()
        
        # Get only active (non-excluded) players for this user
        all_active_players = query_user_data(Player, user_id, is_excluded=False)
        
        if not all_active_players:
            return []
        
        # Check if we're in the first round (not all active players have been MVP)
        active_players_with_mvp = query_user_data(Player, user_id, is_excluded=False)
        active_players_with_mvp = [p for p in active_players_with_mvp if p.mvp_count > 0]
        
        if len(active_players_with_mvp) < len(all_active_players):
            # First round: return active players who haven't been MVP yet
            return [p for p in all_active_players if p.mvp_count == 0]
        else:
            # Subsequent rounds: return active players with minimum MVP count
            min_mvp_count = min(player.mvp_count for player in all_active_players)
            return [p for p in all_active_players if p.mvp_count == min_mvp_count]
            
    except Exception as e:
        print(f"Error in get_eligible_players: {str(e)}")
        return []

def can_assign_winner(user_id=None):
    """
    Check if we can assign alliance winner based on rotation logic
    
    Args:
        user_id: User ID for data isolation (required)
    
    Returns:
        bool: True if winner can be assigned, False otherwise
    
    Logic:
        - If no alliances exist, return False
        - Winner assignments are always allowed - rotation cycles automatically
        - When all alliances have won, eligible alliances are those with minimum win count
    """
    try:
        if not user_id:
            return False
            
        from database_manager import query_user_data
        Player, Alliance, MVPAssignment, WinnerAssignment = get_models()
        
        # Get all alliances for this user
        all_alliances = query_user_data(Alliance, user_id)
        
        if not all_alliances:
            return False  # No alliances to assign winner to
        
        # Check if any winner assignments have been made for this user
        total_assignments = len(query_user_data(WinnerAssignment, user_id))
        
        if total_assignments == 0:
            return True  # First assignment is always allowed
        
        # Always allow winner assignment - rotation handles fairness automatically
        return True
        
    except Exception as e:
        print(f"Error in can_assign_winner: {str(e)}")
        return False

def get_eligible_alliances(user_id=None):
    """
    Get list of alliances eligible for winner assignment
    
    Args:
        user_id: User ID for data isolation (required)
    
    Returns:
        list: List of Alliance objects eligible for winner assignment
    
    Logic:
        - If this is the first round (not all alliances have won), 
          return alliances that haven't won yet
        - If all alliances have won, return alliances with the minimum win count
    """
    try:
        if not user_id:
            return []
            
        from database_manager import query_user_data
        Player, Alliance, MVPAssignment, WinnerAssignment = get_models()
        
        all_alliances = query_user_data(Alliance, user_id)
        
        if not all_alliances:
            return []
        
        # Check if we're in the first round (not all alliances have won)
        alliances_with_wins = [a for a in all_alliances if a.win_count > 0]
        
        if len(alliances_with_wins) < len(all_alliances):
            # First round: return alliances that haven't won yet
            return [a for a in all_alliances if a.win_count == 0]
        else:
            # Subsequent rounds: return alliances with minimum win count
            min_win_count = min(alliance.win_count for alliance in all_alliances)
            return [a for a in all_alliances if a.win_count == min_win_count]
            
    except Exception as e:
        print(f"Error in get_eligible_alliances: {str(e)}")
        return []

def get_rotation_status():
    """
    Get comprehensive rotation status for both MVP and winner assignments
    
    Returns:
        dict: Dictionary containing rotation status information
    """
    try:
        Player, Alliance, MVPAssignment, WinnerAssignment = get_models()
        
        status = {
            'mvp': {
                'can_assign': can_assign_mvp(),
                'eligible_players': [p.to_dict() for p in get_eligible_players()],
                'total_players': Player.query.count(),
                'players_with_mvp': Player.query.filter(Player.mvp_count > 0).count(),
                'current_mvp': None
            },
            'winner': {
                'can_assign': can_assign_winner(),
                'eligible_alliances': [a.to_dict() for a in get_eligible_alliances()],
                'total_alliances': Alliance.query.count(),
                'alliances_with_wins': Alliance.query.filter(Alliance.win_count > 0).count(),
                'current_winner': None
            }
        }
        
        # Get current MVP
        current_mvp = Player.query.filter_by(is_current_mvp=True).first()
        if current_mvp:
            status['mvp']['current_mvp'] = current_mvp.to_dict()
        
        # Get current winner
        current_winner = Alliance.query.filter_by(is_current_winner=True).first()
        if current_winner:
            status['winner']['current_winner'] = current_winner.to_dict()
        
        return status
        
    except Exception as e:
        print(f"Error in get_rotation_status: {str(e)}")
        return {
            'mvp': {'can_assign': False, 'eligible_players': [], 'error': str(e)},
            'winner': {'can_assign': False, 'eligible_alliances': [], 'error': str(e)}
        }

def reset_mvp_rotation():
    """
    Reset MVP rotation - useful for testing or manual resets
    
    This will:
    - Clear all current MVP flags
    - Reset all MVP counts to 0
    - Delete all MVP assignments
    
    WARNING: This is destructive and should be used carefully!
    """
    try:
        from database import db
        from models import Event
        Player, Alliance, MVPAssignment, WinnerAssignment = get_models()
        
        # Clear current MVP flags
        Player.query.update({'is_current_mvp': False, 'mvp_count': 0})
        
        # Delete all MVP assignments
        MVPAssignment.query.delete()
        
        # Update events to reflect no MVP assignments
        Event.query.update({'has_mvp': False})
        
        db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Error in reset_mvp_rotation: {str(e)}")
        from database import db
        db.session.rollback()
        return False

def reset_winner_rotation():
    """
    Reset winner rotation - useful for testing or manual resets
    
    This will:
    - Clear all current winner flags
    - Reset all win counts to 0
    - Delete all winner assignments
    
    WARNING: This is destructive and should be used carefully!
    """
    try:
        from database import db
        from models import Event
        Player, Alliance, MVPAssignment, WinnerAssignment = get_models()
        
        # Clear current winner flags
        Alliance.query.update({'is_current_winner': False, 'win_count': 0})
        
        # Delete all winner assignments
        WinnerAssignment.query.delete()
        
        # Update events to reflect no winner assignments
        Event.query.update({'has_winner': False})
        
        db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Error in reset_winner_rotation: {str(e)}")
        from database import db
        db.session.rollback()
        return False