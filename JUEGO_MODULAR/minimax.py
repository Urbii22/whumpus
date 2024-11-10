# minimax.py
from game_logic import TableroWumpus
import math

def miniMax(state: TableroWumpus, depth: int, max_player: bool, alpha: float, beta: float):
    """Implementación del algoritmo Minimax con poda alfa-beta."""
    if depth == 0 or state.is_game_over():
        return state.utility(), state

    if max_player:
        max_eval = -math.inf
        best_state = None
        for move in state.get_available_moves():
            new_state = state.simulate_move(move)
            eval, _ = miniMax(new_state, depth - 1, False, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_state = new_state
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Poda beta
        return max_eval, best_state
    else:
        min_eval = math.inf
        best_state = None
        for move in state.get_available_moves_min():
            new_state = state.simulate_move_min(move)
            eval, _ = miniMax(new_state, depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_state = new_state
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Poda alfa
        return min_eval, best_state
