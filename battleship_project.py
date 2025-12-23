# B351 Group 16 Project

import numpy as np
import heapq
import time

######################
# classes
######################
class Board:

    def __init__(self, size = 10, ships = None):
        self.size = size
        self.grid = np.zeros((size,size), dtype = int) # makes grid of given size of 0s (0 = water, 1 = miss, 2 = hit)
        self.ships = ships or []
        self.opponent_info = np.zeros((size,size), dtype = int)
        self.ship_map = np.full((size,size), None, dtype = object)

    def in_bounds(self, r, c):
        if 0 <= r < self.size and 0 <= c < self.size:
            return True
        return False
    
    def get_cell(self, r, c):
        return self.grid[r,c]
    
    def set_cell(self, r, c, val):
        self.grid[r,c] = val

    def get_known_cell(self, r, c):
        return self.opponent_info[r,c]
    
    def set_known_cell(self, r, c, val):
        self.opponent_info[r,c] = val

    #checks if the AI has already tried to hit that cell
    def already_tried(self, r, c):
        if self.opponent_info[r,c] == 1 or self.opponent_info[r,c] == 2:
            return True
        return False

    def print_board_with_ships(self):
        for r in range(self.size):
            row_str = ""
            for c in range(self.size):
                cell = self.grid[r,c]
                if cell == 0:
                    row_str += "~ "
                elif cell == 1:
                    row_str += "* " 
                elif cell == 2:
                    row_str += "X "  
                elif cell == 3:
                    row_str += "O "  
            print(row_str)
    
    # in case a player wants to play without seeing ships
    def print_board(self):
        for r in range(self.size):
            row_str = ""
            for c in range(self.size):
                cell = self.grid[r,c]
                if cell == 0 or cell == 3:
                    row_str += "~ " 
                elif cell == 1:
                    row_str += "O " 
                elif cell == 2:
                    row_str += "X "  
            print(row_str)


class Ship:

    def __init__(self, size, coordinates):
        self.size = size
        self.coordinates = coordinates 
        self.hit_areas = set() 
        self.is_sunk = False

    # list of coordinates the ship is positioned at
    def set_coordinates(self, coordinate_list):
        self.coordinates = coordinate_list

    # checks if the ship was hit form a shot at target coordinate
    def hit_register(self, coordinate):
        if coordinate in self.coordinates:
            self.hit_areas.add(coordinate)
            self.sink_check()
            return True
        return False
    
    # updates if the ship has sunk or not
    def sink_check(self):
        if len(self.hit_areas) == self.size:
            self.is_sunk = True


class AIState:

    def __init__(self, ship_sizes = [5,4,3,3,2]):
        self.ship_sizes = ship_sizes.copy()
        self.remaining_ships = ship_sizes.copy()
        self.target_queue = []
        self.shots_taken = 0

    def ship_sunk(self, size):
        if size in self.remaining_ships:
            self.remaining_ships.remove(size)
    
    def add_targets(self, board, r, c):
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if board.in_bounds(nr, nc) and not board.already_tried(nr, nc):
                priority = self.calculate_target_priority(board, nr, nc)
                heapq.heappush(self.target_queue, (priority, (nr, nc)))

    # calculates priority for targeting a cell using a min heap
    def calculate_target_priority(self, board, r, c):
        priority = 0 
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if board.in_bounds(nr, nc) and board.get_known_cell(nr, nc) == 2:
                priority -= 10 
                nnr, nnc = nr + dr, nc + dc
                if board.in_bounds(nnr, nnc) and board.get_known_cell(nnr, nnc) == 2:
                    priority -= 20   
        return priority
    

##########################
# game functions
##########################

# attempts a shot at (r,c) on the given board
def shoot(board, r, c):
    if not board.in_bounds(r,c):
        return "out of bounds"
    cell_val = board.get_cell(r,c)
    ship = board.ship_map[r,c]
    if ship is not None:
        board.set_cell(r,c,2)
        ship.hit_register((r,c))
        if ship.is_sunk:
            return "sunk"
        return "hit"
    elif cell_val == 0:
        board.set_cell(r,c,1)
        return "miss"
    else:
        return "already tried"
    
# checks if all ships are sunk
def game_over(ships):
    for ship in ships:
        if not ship.is_sunk:
            return False
    return True

# puts ships on the board
def populate_board(board, ship_list):
    for ship in ship_list:
        for (r,c) in ship.coordinates:
            board.set_cell(r,c,3)
            board.ship_map[r,c] = ship

# crates random ship placements on the board
def create_random_ships(board_size=10, ship_sizes=[5, 4, 3, 3, 2]):
    ships = []
    occupied_cells = set() 
    for size in ship_sizes:
        max_attempts = 1000
        attempts = 0
        placed = False
        while not placed and attempts < max_attempts:
            attempts += 1
            horizontal = np.random.choice([True, False])

            if horizontal:
                row = np.random.randint(0, board_size)
                col = np.random.randint(0, board_size - size + 1)
                coordinates = [(row, col + i) for i in range(size)]
            else:
                row = np.random.randint(0, board_size - size + 1)
                col = np.random.randint(0, board_size)
                coordinates = [(row + i, col) for i in range(size)]
            
            if not any(coord in occupied_cells for coord in coordinates):
                ship = Ship(size, coordinates)
                ships.append(ship)
                occupied_cells.update(coordinates)
                placed = True
        if not placed:
            raise Exception(f"Could not place ship of size {size} after {max_attempts} attempts")
    return ships

# runs a full simulation of a game with the given algorithm
def run_simulation(algo_name, algo_function, board_size=10, ship_sizes=[5,4,3,3,2]):
    board = Board(size = board_size)
    ships = create_random_ships(board_size, ship_sizes)
    populate_board(board, ships)
    ai_state = AIState(ship_sizes=ship_sizes)
    
    bfs_queue = []
    if algo_name == "BFS":
        for r in range(board_size):
            for c in range(board_size):
                bfs_queue.append((r,c))
        np.random.shuffle(bfs_queue)

    shots = 0
    hits = 0
    start_time = time.time() 

    while not game_over(ships):
        shots += 1
        if algo_name == "Random":
            _, _, result = ai_random_shot(board)
        elif algo_name == "BFS":
            # BFS needs special handling to not reset queue every time
            if bfs_queue:
                r, c = bfs_queue.pop(0)
                result = shoot(board, r, c)
                if result == "hit" or result == "sunk":
                    board.set_known_cell(r,c,2)
                else:
                    board.set_known_cell(r,c,1)
        else:
            # A* and Checkerboard use ai_state
            _, _, result = algo_function(board, ai_state)
            
        if result == "hit" or result == "sunk":
            hits += 1

    # Calculate Stats
    end_time = time.time()
    duration = end_time - start_time
    misses = shots - hits
    accuracy = round((hits / shots) * 100, 2)
    
    return {
        "Name": algo_name,
        "Shots": shots,
        "Misses": misses,
        "Accuracy": f"{accuracy}%",
        "Time": f"{duration:.5f}s"
    }
        
    
############################
# A* Search Algorithm
############################

# helper function to check if a ship can be placed at a given position
def is_valid_placement(board, start_r, start_c, ship_size, horizontal):
    for i in range(ship_size):
        if horizontal:
            r, c = start_r, start_c + i
        else:
            r, c = start_r + i, start_c
        if not board.in_bounds(r, c):
            return False
        if board.get_known_cell(r, c) == 1:
            return False
    return True

# check if we already calculated the map for this specific turn
def get_cached_probability_map(board, state):
    if hasattr(state, 'cached_map') and state.map_turn == state.shots_taken:
        return state.cached_map
    prob_map = np.zeros((board.size, board.size), dtype=float)
    for size in state.remaining_ships:
        for c in range(board.size - size + 1):
            window = board.opponent_info[:, c : c + size]
            valid_rows = ~np.any(window == 1, axis=1)
            prob_map[valid_rows, c : c + size] += 1
        for r in range(board.size - size + 1):
            window = board.opponent_info[r : r + size, :]
            valid_cols = ~np.any(window == 1, axis=0)
            prob_map[r : r + size, valid_cols] += 1
    state.cached_map = prob_map
    state.map_turn = state.shots_taken
    return prob_map

# heuristic function to evaluate the desirability of shooting at (r,c)
def calculate_heuristic(board, r, c, state):
    score = 0.0
    prob_map = get_cached_probability_map(board, state)
    score = prob_map[r, c]
    
    # find the smallest remaining ship size, and favor cells that skip spaces accordingly
    if state.remaining_ships:
        smallest_ship = min(state.remaining_ships)
        if (r + c) % smallest_ship == 0:
            score *= 1.1
    
    # favor center positions, since ships have more possible positions in the middle
    center = board.size // 2
    distance_to_center = abs(r - center) + abs(c - center)
    center_factor = 1 + (0.1 * (board.size - distance_to_center))
    score *= center_factor
    return score

# shooting function using A* search strategy
def ai_astar_shot(board, ai_state):
    ai_state.shots_taken += 1

    # use targets if we have them from previous hits
    if ai_state.target_queue:
        # remove already-tried cells from queue
        while ai_state.target_queue:
            _, (r, c) = heapq.heappop(ai_state.target_queue)
            if not board.already_tried(r, c):
                result = shoot(board, r, c)
                
                # update board knowledge
                if result == "hit":
                    board.set_known_cell(r, c, 2)
                    ai_state.add_targets(board, r, c)
                elif result == "sunk":
                    board.set_known_cell(r, c, 2)
                    ship = board.ship_map[r, c]
                    if ship:
                        ai_state.ship_sunk(ship.size)
                elif result == "miss":
                    board.set_known_cell(r, c, 1)
                
                return (r, c, result)
    
    # use heuristic to find best unexplored cell
    priority_queue = []
    for r in range(board.size):
        for c in range(board.size):
            if not board.already_tried(r, c):
                h_score = calculate_heuristic(board, r, c, ai_state)
                f_score = -h_score
                heapq.heappush(priority_queue, (f_score, r, c))
    
    # get best cell
    if priority_queue:
        _, r, c = heapq.heappop(priority_queue)
        result = shoot(board, r, c)
        # update board knowledge
        if result == "hit":
            board.set_known_cell(r, c, 2)
            ai_state.add_targets(board, r, c)
        elif result == "sunk":
            board.set_known_cell(r, c, 2)
            ship = board.ship_map[r, c]
            if ship:
                ai_state.ship_sunk(ship.size)
        elif result == "miss":
            board.set_known_cell(r, c, 1)
        return (r, c, result)

####################################
# Standard "human like" strategy
####################################

def ai_standard_shot(board, ai_state):
    ai_state.shots_taken += 1

    # finding best cell from previous hits
    if ai_state.target_queue:
        while ai_state.target_queue:
            _, (r, c) = heapq.heappop(ai_state.target_queue)
            if not board.already_tried(r, c):
                result = shoot(board, r, c)
                if result == "hit":
                    board.set_known_cell(r, c, 2)
                    ai_state.add_targets(board, r, c)
                elif result == "sunk":
                    board.set_known_cell(r, c, 2)
                    ship = board.ship_map[r, c]
                    if ship:
                        ai_state.ship_sunk(ship.size)
                elif result == "miss":
                    board.set_known_cell(r, c, 1)
                return (r, c, result)
            
    # random shooting until we get target
    size = board.size
    attempts = 0
    while attempts < 1000:
        r = np.random.randint(0, size)
        c = np.random.randint(0, size)
        if (r + c) % 2 == 0 and not board.already_tried(r,c):
            result = shoot(board, r, c)
            if result == "hit":
                board.set_known_cell(r, c, 2)
                ai_state.add_targets(board, r, c)
            elif result == "sunk":
                board.set_known_cell(r, c, 2)
                ship = board.ship_map[r, c]
                if ship:
                    ai_state.ship_sunk(ship.size)
            elif result == "miss":
                board.set_known_cell(r, c, 1)
            return (r, c, result)
        attempts += 1
        
#####################
# BFS and random search algorithm
#####################

def BFS(board, size):
    visited = set()
    queue = []
    for r in range(size):
        for c in range(size):
            if not board.already_tried(r,c):
                queue.append((r,c))
    np.random.shuffle(queue)
    while queue:
        r, c = queue.pop(0)
        if (r,c) not in visited:
            visited.add((r,c))
            result = shoot(board, r, c)
            if result == "hit" or result == "sunk":
                board.set_known_cell(r,c,2)
            elif result == "miss":
                board.set_known_cell(r,c,1)
            return (r, c, result)
    return None

def ai_random_shot(board):
    size = board.size
    while True:
        r = np.random.randint(0, size)
        c = np.random.randint(0, size)
        if not board.already_tried(r,c):
            result = shoot(board, r, c)
            if result == "hit" or result == "sunk":
                board.set_known_cell(r,c,2)
            elif result == "miss":
                board.set_known_cell(r,c,1)
            return (r, c, result)


##########################
# Simulation and statistics
##########################

CUSTOM_BOARD_SIZE = 30
CUSTOM_SHIP_LIST = [20,15,14,13,12,11,10,5]
print(f"BENCHMARK: {CUSTOM_BOARD_SIZE}x{CUSTOM_BOARD_SIZE} Board with {len(CUSTOM_SHIP_LIST)} Ships")
print(f"{'ALGORITHM':<20} | {'SHOTS':<10} | {'MISSES':<10} | {'ACCURACY':<10} | {'TIME':<10}")
print("-" * 70)

# 1. Run Random
stats_random = run_simulation("Random", ai_random_shot, CUSTOM_BOARD_SIZE, CUSTOM_SHIP_LIST)
print(f"{stats_random['Name']:<20} | {stats_random['Shots']:<10} | {stats_random['Misses']:<10} | {stats_random['Accuracy']:<10} | {stats_random['Time']:<10}")

# 2. Run BFS
stats_bfs = run_simulation("BFS", None, CUSTOM_BOARD_SIZE, CUSTOM_SHIP_LIST)
print(f"{stats_bfs['Name']:<20} | {stats_bfs['Shots']:<10} | {stats_bfs['Misses']:<10} | {stats_bfs['Accuracy']:<10} | {stats_bfs['Time']:<10}")

# 3. Run Standard "human like"
stats_standard = run_simulation("Standard", ai_standard_shot, CUSTOM_BOARD_SIZE, CUSTOM_SHIP_LIST)
print(f"{stats_standard['Name']:<20} | {stats_standard['Shots']:<10} | {stats_standard['Misses']:<10} | {stats_standard['Accuracy']:<10} | {stats_standard['Time']:<10}")

# 4. Run A* (Heuristic)
stats_astar = run_simulation("A*", ai_astar_shot, CUSTOM_BOARD_SIZE, CUSTOM_SHIP_LIST)
print(f"{stats_astar['Name']:<20} | {stats_astar['Shots']:<10} | {stats_astar['Misses']:<10} | {stats_astar['Accuracy']:<10} | {stats_astar['Time']:<10}")

######################
# 1v1 Game Simulation
######################
'''
player_board = Board()
opponent_board = Board()
ai_state = AIState(ship_sizes = [5,4,3,3,2])
player_ships = create_random_ships()
opponent_ships = create_random_ships()
populate_board(player_board, player_ships)
populate_board(opponent_board, opponent_ships)

while game_over(player_ships) == False and game_over(opponent_ships) == False:

    # Player's turn
    r, c = input("Enter your shot coordinates (row col): ").split(" ")
    r = int(r)
    c = int(c)
    result = shoot(opponent_board, r, c)
    print(f"Player shot at ({r}, {c}) and result was: {result}")

    # AI's turn
    r, c, result = ai_astar_shot(player_board, ai_state)
    print(f"AI shot at ({r}, {c}) and result was: {result}")
    
    print("Player Board: ")
    player_board.print_board_with_ships()
    print("Opponent Board: ")
    opponent_board.print_board()
    
if game_over(player_ships):
    print("AI wins!")
elif game_over(opponent_ships):
    print("Player wins!")

 '''
