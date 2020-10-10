import gamelib
import random
import math
import warnings
from sys import maxsize
import json

FACTORY_LOCATIONS = [[5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [11, 8], [12, 8], [13, 8], [14, 8], [15, 8], [16, 8], [17, 8], [18, 8], [19, 8], [20, 8], [21, 8], [22, 8], [6, 7], [7, 7], [8, 7], [9, 7], [10, 7], [11, 7], [12, 7], [13, 7], [14, 7], [15, 7], [16, 7], [17, 7], [18, 7], [19, 7], [20, 7], [21, 7], [7, 6], [8, 6], [9, 6], [10, 6], [11, 6], [12, 6], [13, 6], [14, 6], [15, 6], [16, 6], [17, 6], [18, 6], [19, 6], [20, 6], [8, 5], [9, 5], [10, 5], [11, 5], [12, 5], [13, 5], [14, 5], [15, 5], [16, 5], [17, 5], [18, 5], [19, 5], [9, 4], [10, 4], [11, 4], [12, 4], [13, 4], [14, 4], [15, 4], [16, 4], [17, 4], [18, 4], [10, 3], [11, 3], [12, 3], [13, 3], [14, 3], [15, 3], [16, 3], [17, 3], [11, 2], [12, 2], [13, 2], [14, 2], [15, 2], [16, 2], [12, 1], [13, 1], [14, 1], [15, 1], [13, 0], [14, 0]].reverse()


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 3
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, FACTORY, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        FACTORY = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)
        self.ab_strategy(game_state)
        game_state.submit_turn()

    def create_strategy_list(self, game_state):
        '''

        :param game_state:
        :return: list of strategy to be searched
        '''
        self.current_game_map = game_state.game_map.copy()
        self.current_state = game_state.copy()
        self.current_serial_string = json.loads(game_state.serialized_string)
        current_sp = self.current_state.get_resource(SP)
        current_mp = self.current_state.get_resource(MP)
        strategies = []
        strategy = {}

        strategies = self.factory_upgrade(self, game_state, current_sp)
        strategies = self.factory_spawn_locations(self, game_state, strategies)
        strategies = self.turret_spawn(self, game_state, strategies)
        upgrade_turret, current_sp = self.turret_upgrade()
        spawn_wall, current_sp = self.wall_spawn

    def create_strategy(self, game_state, current):

    def factory_upgrade(self, game_state, cur_sp, strategies):
        '''
        :param game_state:
        :return: possible locations to upgrade factory
        '''
        # strategies = []
        #
        # current_sp = cur_sp
        # current_factories = self.current_serial_string['p1Units'][0]
        # m = len(current_factories)
        # res = []
        # if current_sp > 10:
        #     n = int((current_sp / 9))
        #     mean = min(n, m)
        #     i = 0
        #     # for i in range(mean):
        #     #     strategy = {}
        #     #     candidate = current_factories[i]
        #     #     if not candidate.upgraded:
        #     #         res.append(candidate)
        #     #         current_sp -= 9
        #     #         strategy['upgrade_factory'] = res
        # return res, current_sp, strategies

    def factory_upgrade(self, game_state, cur_sp):
        '''
        :param game_state:
        :return: possible locations to upgrade factory
        '''
        strategies = []

        current_sp = cur_sp
        current_factories = self.current_serial_string['p1Units'][0]
        m = len(current_factories)
        res = []
        strategy = {}
        if current_sp > 10:
            n = int((current_sp / 9))
            n = min(n, m)
            i = 0

            strategy['upgrade_factory'] = res.copy()
            strategies.append([strategy.copy(), current_sp])

            while i <= n:
                candidate = current_factories[i]
                i = i + 1
                if not candidate.upgraded:
                    res.append(candidate)
                    current_sp -= 9
                    strategy['upgrade_factory'] = res.copy()
                    strategies.append([strategy.copy(), current_sp])
        return strategies.reverse()

    def factory_spawn_locations(self, game_state, strategies):
        '''
        :param game_state:
        :return: a list of possible locations to spawn factory
        '''
        new_strategies = []
        for strategy_ in strategies:
            strategy, current_sp = strategy_
            res = []
            strategy['spawn_factory'] = res.copy()
            new_strategies.append(strategy.copy(), current_sp)
            if current_sp > 10:
                n = int((current_sp / 9))
                i = 0
                j = 0
                while (i <= n) and (j <= len(FACTORY_LOCATIONS)):
                    candidate = FACTORY_LOCATIONS[j]
                    if game_state.can_spawn(FACTORY, candidate):
                        i += 1
                        current_sp -= 9
                        res.append(candidate)
                        strategy['spawn_factory'] = res.copy()
                        new_strategies.append([strategy.copy(), current_sp])
                    else:
                        pass
                    j += 1
        return new_strategies

    def turret_spawn(self, game_state, strategies):
        '''
        :param game_state:
        :param cur_sp:
        :return: locations to upgrade turrets
        '''
        new_strategies = []
        for strategy_ in strategies:
            strategy, current_sp = strategy_
            res = []
            strategy['spawn_factory'] = res.copy()
            new_strategies.append(strategy.copy(), current_sp)
            if current_sp > 10:
                n = int((current_sp / 9))
                i = 0
                j = 0
                while (i <= n) and (j <= len(TURRET_LOCATIONS)):
                    candidate = TURRET_LOCATIONS[j]
                    if game_state.can_spawn(TURRET, candidate):
                        i += 1
                        current_sp -= 2
                        res.append(candidate)
                        strategy['spawn_factory'] = res.copy()
                        new_strategies.append([strategy.copy(), current_sp])
                    else:
                        pass
                    j += 1
        return new_strategies


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with interceptors and wait to see enemy's base
        if game_state.turn_number < 2:
            if game_state.turn_number==0:
                game_state.attempt_spawn(FACTORY,[[13,0],[14,0]])
                game_state.attempt_spawn(INTERCEPTOR,[[8,5],[12,1],[18,4],[22,8],[27,13]])
                game_state.attempt_spawn(TURRET,[[4,12]])
                game_state.attempt_upgrade([[13,0]])
            if game_state.turn_number==1:
                if SP<9:
                    game_state.attempt_spawn(TURRET,[[9,12],[23,12]])
                    game_state.attempt_spawn(WALL,[[9,13]])
                if SP>=9:
                    game_state.attempt_upgrade([[14,0]])
                    if (SP-9)>=2:
                        game_state.attempt_spawn(TURRET,[[23,12]])
                    game_state.attempt_spawn(INTERCEPTOR,[[8,5],[12,1],[18,4],[22,8],[27,13],[0,13]])
        else:
            pass

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        turret_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(TURRET, turret_locations)
        
        # Place walls in front of turrets to soak up damage for them
        wall_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(WALL, wall_locations)
        # upgrade walls so they soak more damage
        game_state.attempt_upgrade(wall_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    def eval_def(self,game_state):
        edge_point =dict.fromkeys([range(-2,29)],0)
        game_dict= json.loads(game_state.serialized_string)
        my_turret = game_dict['p1Units'][2]
        for i in my_turret:
            x = i[0]
            y = i[1]
            location = [x,y]
            tur_upgraded = location.upgraded
            tur_hp = i[2]
            check_even=(x+y)%2==0
            sum_xy = x+y
            diff_xy = x-y
            normal_def=5
            up_def = 15
            if tur_upgraded == False:
                if check_even==True:
                    #add def power to right edge
                    edge_point[(sum_xy+14)/2] += normal_def
                    edge_point[(sum_xy+14)/2+1] += normal_def
                    edge_point[(sum_xy+14)/2+2] += normal_def/2
                    edge_point[(sum_xy+14)/2-1] += normal_def
                    edge_point[(sum_xy+14)/2-2] += normal_def/2

                    #add def power to left edge
                    edge_point[(13+(diff_xy+1))/2]+=normal_def
                    edge_point[(13+(diff_xy-1))/2]+=normal_def
                    edge_point[(13+(diff_xy+1))/2+1]+=normal_def
                    edge_point[(13+(diff_xy-1))/2-1]+=normal_def

                else:
                    #add def power to right edge
                    edge_point[(sum_xy+1+14)/2]+=normal_def
                    edge_point[(sum_xy-1+14)/2]+=normal_def
                    edge_point[(sum_xy+1+14)/2+1]+=normal_def
                    edge_point[(sum_xy-1+14)/2-1]+=normal_def

                    #add def power to left edge
                    edge_point[(13+diff_xy)/2]+=normal_def
                    edge_point[(13+diff_xy)/2+1]+=normal_def
                    edge_point[(13+diff_xy)/2+2]+=normal_def/2
                    edge_point[(13+diff_xy)/2-1]+=normal_def
                    edge_point[(13+diff_xy)/2-2]+=normal_def/2
            else:
                #the turret was upgraded
                if check_even==True:
                    #add def power to right edge
                    edge_point[(sum_xy+14)/2] += up_def
                    edge_point[(sum_xy+14)/2+1] += up_def
                    edge_point[(sum_xy+14)/2+2] += up_def
                    edge_point[(sum_xy+14)/2-1] += up_def
                    edge_point[(sum_xy+14)/2-2] += up_def

                    #add def power to left edge
                    edge_point[(13+(diff_xy+1))/2]+=up_def
                    edge_point[(13+(diff_xy-1))/2]+=up_def
                    edge_point[(13+(diff_xy+1))/2+1]+=up_def
                    edge_point[(13+(diff_xy-1))/2-1]+=up_def
                    edge_point[(13+(diff_xy+1))/2+2]+=up_def/2
                    edge_point[(13+(diff_xy-1))/2-2]+=up_def/2
                else:
                    #the turret was upgraded and sum is odd
                    #add def power to right edge
                    edge_point[(sum_xy+1+14)/2]+=up_def
                    edge_point[(sum_xy-1+14)/2]+=up_def
                    edge_point[(sum_xy+1+14)/2+1]+=up_def
                    edge_point[(sum_xy-1+14)/2-1]+=up_def
                    edge_point[(sum_xy+1+14)/2+2]+=up_def/2
                    edge_point[(sum_xy-1+14)/2-2]+=up_def/2                 

                    #add def power to left edge
                    edge_point[(13+diff_xy)/2]+=up_def
                    edge_point[(13+diff_xy)/2+1]+=up_def
                    edge_point[(13+diff_xy)/2+2]+=up_def
                    edge_point[(13+diff_xy)/2-1]+=up_def
                    edge_point[(13+diff_xy)/2-2]+=up_def
        return edge_point








    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        # Remove locations that are blocked by our own structures 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        # While we have remaining MP to spend lets send out interceptors randomly.
        while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]
            
            game_state.attempt_spawn(INTERCEPTOR, deploy_location)
            """
            We don't have to remove the location since multiple mobile 
            units can occupy the same space.
            """

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, FACTORY]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))

    ################################################################################################################
    def ab_strategy_result(self,game_state):
        
	# Give 4 seconds, max depth = 20
        time_left = 4.0
        depth = 20
        
	# IDAB Search for best strategy 
        strategy,_ = self.id_alphabeta_advance(game_state, time_left, depth)
        # given strategy
        game_state.attempt_spawn(FACTORY,strategy['FACTORY'])
        game_state.attempt_spawn(INTERCEPTOR,strategy['INTERCEPTOR'])
        game_state.attempt_spawn(TURRET,strategy['TURRET'])
        game_state.attempt_spawn(SCOUT ,strategy['SCOUT'])
        game_state.attempt_spawn(WALL,strategy['WALL'])
        game_state.attempt_spawn(DEMOLISHER,strategy['DEMOLISHER'])        
        game_state.attempt_upgrade(strategy['UPGRADE'])         
        

    def id_alphabeta_advance(self, game, time_left, depth, alpha=float("-inf"), beta=float("inf"), my_turn=True):
	# game is the game_state
	# time_left control time
	# Iterate over given max depth
	
        # current_strategy and current_val is just used to prevent losing Memory of Previous best and can check time out easily
	# We can use the global Ordered_Nodes here to help us store more and save time
        best_strategy, best_val, current_strategy, current_val = None, None, None, None
        time_start = time.time()

        # We evaluate the results only at 2 turns finished
        for i in range(2, depth, 2):
            time_left = time.time()-time_start
            if time_left <= 0.01:
                print((best_strategy, best_val))
                return (best_strategy, best_val)
            current_strategy, current_val = self.helper_advance(game, time_left, i, alpha, beta, True)
            # print(i,current_strategy,current_val)
            # Update it or directly return
            if current_strategy != 'No Time':
                best_strategy, best_val = current_strategy, current_val
            else:
                # print(Ordered_Nodes)
                # print('No time left!! at depth',i)
                print((best_strategy, best_val))
                return (best_strategy, best_val)
        print((best_strategy, best_val))
        # print(Ordered_Nodes)
        return (best_strategy, best_val)
    #
    
    def helper_advance(self, game, time_left, depth, alpha, beta, my_turn):
        def max_value_alphabeta(current_game, d, time_left, alpha, beta):
            
            # Ordered nodes can store the best strategy for certain situation in previous search
            
            time_start = time.time()
            best_move = None
            best_val = float('inf')
            current_val = None
            current_move = None
    
            # Check time left
            if time_left <= 0.01:
                return ('No Time', None)
            # Reach at the maximum nodes
            if d <= 0:
                # return current_game.get_player_position(player),player.eval_fn.score(current_game, player)  board game
                # return the current strategy and evaluation result
                return 0, 0
    
            # Then we can do the next moves which is the next strategies
            #Temp = Ordered_Nodes.get((current_game.print_board(), 'Max'))  get the best move stored
            Temp = None
            if Temp is None:
                # print('No')
                next_moves = Generate_Strategies(game)
            else:
                # print('Yes')
                temp = []
                temp.append(Temp)
                temp.extend([i for i in Generate_Strategies(game) if i != Temp])
                next_moves = temp.copy()
            
            move_value_pair = []
            for next_move in next_moves:

		# Update time_left every iteration
                time_left -=  time.time()-time_start
                # Get forecasting for the next game and is over
                next_game, is_over = 0,0
                # If we are going to over
                if is_over:
                    # Judge who is over, if opponent over, then set to +inf, or us over set to -inf
                    current_val = 0
                else:
                    current_move, current_val = min_value_alphabeta(next_game,d - 1, time_left, alpha, beta)
    
                # if current_val is not None and current_move != 'No Time':
                # move_value_pair.append([next_move, current_val])
    
                #  if out of running time, return!
                if current_strategy == 'No Time':
                    return ('No Time', None)
    
                # AB pruning
                if best_val < current_val:
                    best_move = next_move
                    best_val = current_val
    
                if best_val >= beta:
                    # maybe we can store the best strategy
                    #Ordered_Nodes[(current_game.print_board(), 'Max')] = best_move
                    return (best_move, best_val)
    
                alpha = max(alpha, best_val)

            if best_move is not None:
                #Ordered_Nodes[(current_game.print_board(), 'Max')] = best_strategy
                pass
            # print((best_move,best_val),d)
            return (best_strategy, best_val)
    
        def min_value_alphabeta(current_game, d, time_left, alpha, beta):
            
            temp_start = time.time()
            best_move = None
            best_val = float('inf')
            current_val = None
            current_move = None
    
            if time_left <= 0.01:
                return ('No Time', None)
            if d <= 0:
                # return current_game.get_player_position(player),player.eval_fn.score(current_game, player)
                return 0, 0
    
            #Temp = Ordered_Nodes.get((current_game.print_board(), 'Min'))
            Temp = None
            if Temp is None:
                # print('No')
                #next_moves = current_game.get_opponent_moves(player)
                next_moves = Generate_Strategies(game)
            else:
                # print('Yes')
                temp = []
                temp.append(Temp)
                temp.extend([i for i in Generate_Strategies(game) if i != Temp])
                next_moves = temp.copy()
            # next_moves = current_game.get_opponent_moves(player)
    
            # move_value_pair = []
            for next_move in next_moves:
                
                time_left -=  time.time()-time_start
                
                next_game, is_over = 0,0
    
                if is_over:
                    # current_val = player.eval_fn.score(next_game, player)
                    current_val = 0
                    current_move = next_move
                else:
                    current_move, current_val = max_value_alphabeta(next_game, d - 1, time_left, alpha, beta)
    
                # if current_val is not None and current_move != 'No Time':
                # move_value_pair.append([next_move, current_val])
    
                if current_move == 'No Time':
                    return ('No Time', None)
    
                if best_val > current_val:
                    best_move = next_move
                    best_val = current_val
    
                if best_val <= alpha:
                    Ordered_Nodes[(current_game.print_board(), 'Min')] = best_move
                    return (best_move, best_val)
                beta = min(beta, best_val)

            if best_move is not None:
                #Ordered_Nodes[(current_game.print_board(), 'Min')] = best_move
                pass
            # print((best_move,best_val),d)
            return (best_move, best_val)
    
        best_move, best_score = max_value_alphabeta(game depth, time_left, alpha, beta)
        return (best_move, best_score, Ordered_Nodes)
    #################################################################################################################   
if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
