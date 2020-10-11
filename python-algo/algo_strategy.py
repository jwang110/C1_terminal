import gamelib
import random
import math
import warnings
from sys import maxsize
import json
from copy import deepcopy
import time
from gamelib.game_state import GameState
# Give a better locations
FACTORY_LOCATIONS = [[5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [11, 8], [12, 8],
                     [13, 8], [14, 8], [15, 8], [16, 8], [17, 8], [18, 8], [19, 8], [20, 8], [21, 8], [22, 8], [6, 7],
                     [7, 7], [8, 7],
                     [9, 7], [10, 7], [11, 7], [12, 7], [13, 7], [14, 7], [15, 7], [16, 7], [17, 7], [18, 7], [19, 7],
                     [20, 7], [21, 7], [7, 6], [8, 6], [9, 6],
                     [10, 6], [11, 6], [12, 6], [18, 4], [13, 6], [14, 6], [15, 6], [16, 6], [17, 6], [18, 6], [19, 6],
                     [20, 6], [8, 5], [9, 5], [10, 5], [11, 5],
                     [12, 5], [13, 5], [14, 5], [15, 5], [16, 5], [17, 5], [18, 5], [19, 5], [9, 4], [10, 4], [10, 3],
                     [11, 4], [12, 4], [13, 4], [14, 4], [15, 4],
                     [16, 4], [16, 2], [17, 4], [11, 3], [12, 3], [13, 3], [14, 3], [15, 3], [16, 3], [17, 3], [11, 2],
                     [12, 1], [15, 1], [15, 2], [12, 2], [13, 2],
                     [14, 2], [14, 1], [13, 1], [13, 0], [14, 0]]
FACTORY_LOCATIONS.reverse()
TURRET_LOCATIONS = [[2, 12], [3, 12], [4, 12], [5, 12], [6, 12], [7, 12], [8, 12], [9, 12], [10, 12],
                    [11, 12], [12, 12], [13, 12], [14, 12], [15, 12], [16, 12], [17, 12], [18, 12], [19, 12], [20, 12],
                    [21, 12],
                    [22, 12], [23, 12], [24, 12], [25, 12]]
WALL_LOCATIONS = [[1, 13], [2, 13], [3, 13], [4, 13], [5, 13], [6, 13], [7, 13], [8, 13], [9, 13], [10, 13],
                  [11, 13],
                  [12, 13], [13, 13], [14, 13], [15, 13], [16, 13], [17, 13], [18, 13], [19, 13], [20, 13], [21, 13],
                  [22, 13],
                  [23, 13], [24, 13], [25, 13], [26, 13]]

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
        self.they_scored_on_locations = []

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
        game_state.suppress_warnings(True)  # Comment or remove this line to enable warnings.

        # self.starter_strategy(game_state)
        self.test(game_state)
        game_state.submit_turn()

    def create_defense_strategy_list(self, game_state):
        '''

        :param game_state:
        :return: list of strategy to be searched
        '''
        self.current_game_map = game_state.game_map
        self.current_state = game_state
        self.current_serial_string = json.loads(game_state.serialized_string)
        current_sp = self.current_state.get_resource(SP)
        current_mp = self.current_state.get_resource(MP)
        strategies = []
        strategy = {}

        strategies = self.factory_upgrade(game_state, current_sp)
        strategies = self.factory_spawn_locations(game_state, strategies)
        strategies = self.turret_spawn(game_state, strategies)
        strategies = self.turret_upgrade(game_state, strategies)
        strategies = self.wall_spawn(game_state, strategies)
        strategies = self.wall_upgrade(game_state, strategies)




        strategies = self.interceptor_spawn(game_state, current_mp, strategies)
        strategies = self.demolisher_spawn(game_state, strategies)
        strategies = self.scout_spawn(game_state, strategies)
        # gamelib.debug_write('The current first strategy is {}'.format(strategies))
        #gamelib.debug_write(strategies)


        G = {}
        for strategy_ in strategies:
            strategy, _ = strategy_
            temp =(tuple(strategy['upgrade_factory']),tuple(strategy['spawn_factory']),
                        tuple(strategy['spawn_turret']), tuple(strategy['upgrade_turret']), tuple(strategy['spawn_wall']), tuple(strategy['upgrade_wall']))
            G[temp] = G.get(temp, [])
            G[temp].append([strategy['spawn_interceptor'], strategy['spawn_demolisher'], strategy['spawn_scout']])

        gamelib.debug_write(len(G))

        return G

    def test(self, game_state):
        #strategy = self.create_defense_strategy_list(game_state)[-1][0]
        strategy = self.search_greedy_best_strategy(game_state, self.create_defense_strategy_list(game_state))
        #gamelib.debug_write(strategy)
        if len(strategy['spawn_factory']) != 0:
            game_state.attempt_spawn(FACTORY, strategy['spawn_factory'])
        if len(strategy['spawn_turret']) != 0:
            game_state.attempt_spawn(TURRET, strategy['spawn_turret'])
        if len(strategy['spawn_wall']) != 0:
            game_state.attempt_spawn(WALL, strategy['spawn_wall'])
        if len(strategy['upgrade_wall'] + strategy['upgrade_turret'] + strategy['upgrade_factory']) != 0:
            game_state.attempt_upgrade(
                strategy['upgrade_wall'] + strategy['upgrade_turret'] + strategy['upgrade_factory'])
        if len(strategy['spawn_interceptor']) != 0:
            game_state.attempt_spawn(INTERCEPTOR, strategy['spawn_interceptor'])
        if len(strategy['spawn_scout']) != 0:
            game_state.attempt_spawn(INTERCEPTOR, strategy['spawn_interceptor'])
        if len(strategy['spawn_demolisher']) != 0:
            game_state.attempt_spawn(INTERCEPTOR, strategy['spawn_interceptor'])
        #gamelib.debug_write(self.search_greedy_best_strategy(game_state, self.create_defense_strategy_list(game_state)))


    def factory_upgrade(self, game_state, cur_sp):
        '''
        :param game_state:
        :return: possible locations to upgrade factory
        '''
        strategies = []

        current_sp = cur_sp
        #gamelib.debug_write(current_sp)
        current_factories = self.current_serial_string['p1Units'][1]
        m = len(current_factories)
        res = []
        strategy = {}
        strategy['upgrade_factory'] = res.copy()
        strategies.append([strategy.copy(), current_sp])
        if current_sp > 10:
            n = int((current_sp / 9))
            #gamelib.debug_write(n)
            n = min(n, m)
            i = 0
            #gamelib.debug_write(n)
            while i < n:
                candidate_location = current_factories[i][0:2]
                i = i + 1
                if not game_state.game_map[candidate_location[0], candidate_location[1]][0].upgraded:
                    res.append(candidate_location)
                    current_sp -= 9
                    strategy['upgrade_factory'] = res.copy()
                    strategies.append([strategy.copy(), current_sp])

        #gamelib.debug_write(strategies)
        return strategies

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
            new_strategies.append([strategy.copy(), current_sp])
            if current_sp > 10:
                n = int((current_sp / 9))
                i = 0
                j = 0
                while (i < n) and (j < len(FACTORY_LOCATIONS)):
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

        #gamelib.debug_write(new_strategies)
        return new_strategies

    def turret_spawn(self, game_state, strategies):
        '''
        :param game_state:
        :param cur_sp:
        :return: locations to upgrade turrets
        '''
        new_strategies = []
        # gamelib.debug_write('3')
        for strategy_ in strategies:
            strategy, current_sp = strategy_
            new_factories = strategy['spawn_factory']
            res = []
            strategy['spawn_turret'] = res.copy()
            new_strategies.append([strategy.copy(), current_sp])
            if current_sp < 2:
                continue
            else:
                n = int((current_sp / 2))
                turret_candidate_ = []
                for new_factory in new_factories:
                    turret_candidate_ += self.find_turret_location(new_factory)
                temp = [i for i in TURRET_LOCATIONS if i not in turret_candidate_]
                turret_candidate_.extend(temp)

                i = 0
                j = 0
                while (i < n) and (j < len(turret_candidate_)):
                    candidate = turret_candidate_[j]
                    if game_state.can_spawn(TURRET, candidate):
                        i += 1
                        current_sp -= 2
                        res.append(candidate)
                        strategy['spawn_turret'] = res.copy()
                        new_strategies.append([strategy.copy(), current_sp])
                    else:
                        pass
                    j += 1
        #gamelib.debug_write(new_strategies)
        return new_strategies

    def find_turret_location(self, location):
        '''
        :param location:
        :return: two best location to put turret that cover the factories at location
        '''
        x = location[0]
        y = location[1]
        return [[x + 12 - y, 12], [x - 12 + y, 12]]

    def turret_upgrade(self, game_state, strategies):
        '''

        :param game_state:
        :param strategies:
        :return:
        '''
        new_strategies = []

        # gamelib.debug_write(strategies)
        for strategy_ in strategies:
            strategy, current_sp = strategy_
            # gamelib.debug_write(strategy)
            res = []
            strategy['upgrade_turret'] = res.copy()
            new_strategies.append([strategy.copy(), current_sp])
            current_turrets = self.current_serial_string['p1Units'][2]
            # gamelib.debug_write(current_turrets)
            m = len(current_turrets)
            # gamelib.debug_write(m)
            res = []
            if current_sp > 4:
                n = int((current_sp / 4))
                n = min(n, m)
                i = 0
                j = 0
                while i < n:
                    candidate_location = current_turrets[i][0:2]
                    i = i + 1
                    # gamelib.debug_write(candidate_location)
                    # candidate = game_state.game_map[candidate_location[0], candidate_location[1]]
                    # gamelib.debug_write(candidate)
                    if not game_state.game_map[candidate_location[0], candidate_location[1]][0].upgraded:
                        res.append(candidate_location)
                        current_sp -= 4
                        strategy['upgrade_turret'] = res.copy()
                        new_strategies.append([strategy.copy(), current_sp])

        return new_strategies

    def wall_spawn(self, game_state, strategies):
        new_strategies = []
        # gamelib.debug_write(strategies)
        # gamelib.debug_write('5')
        for strategy_ in strategies:
            strategy, current_sp = strategy_
            #gamelib.debug_write(strategy)
            res = []
            strategy['spawn_wall'] = res.copy()
            new_strategies.append([strategy.copy(), current_sp])
            new_turrets = strategy['spawn_turret']
            if current_sp < 1:
                continue
            else:
                n = int(current_sp)
                wall_candidate_ = []
                for new_turret in new_turrets:
                    wall_candidate_ += self.find_wall_location(new_turret)
                temp = [i for i in WALL_LOCATIONS if i not in wall_candidate_]
                wall_candidate_.extend(temp)

                i = 0
                j = 0
                while (i < n) and (j < len(wall_candidate_)):
                    candidate = wall_candidate_[j]
                    if game_state.can_spawn(TURRET, candidate):
                        i += 1
                        current_sp -= 1
                        res.append(candidate)
                        strategy['spawn_wall'] = res.copy()
                        new_strategies.append([strategy.copy(), current_sp])
                    else:
                        pass
                    j += 1
        return new_strategies

    def wall_upgrade(self, game_state, strategies):
        new_strategies = []
        #

        # gamelib.debug_write('6#')
        for strategy_ in strategies:
            strategy, current_sp = strategy_
            res = []
            strategy['upgrade_wall'] = res.copy()
            new_strategies.append([strategy.copy(), current_sp])
            current_walls = self.current_serial_string['p1Units'][0]
            m = len(current_walls)
            res = []
            if current_sp > 2:
                n = int((current_sp / 2))
                n = min(n, m)
                i = 0
                j = 0

                while i < n:
                    candidate_location = current_walls[j][0:2]
                    i = i + 1
                    if not game_state.game_map[candidate_location[0], candidate_location[1]][0].upgraded:
                        res.append(candidate_location)
                        current_sp -= 2
                        strategy['upgrade_wall'] = res.copy()
                        new_strategies.append([strategy.copy(), current_sp])

        return new_strategies

    # def find_turret_location(self, location):
    #     '''
    #     :param location:
    #     :return: two best location to put turret that cover the factories at location
    #     '''
    #     x = location[0]
    #     y = location[1]
    #     return [[x+12-y, 12], [x-12+y, 12]]
    def find_wall_location(self, location):
        x, y = location
        return [[x, y + 1]]

    def search_greedy_best_strategy(self, game_state, strategies):
        '''
        :param game_state:
        :param strategies:
        :return: the best strategy available based on current board
        '''

        G = strategies
        for k in G.keys():
            defense_strategy = k.split('r')
            gamelib.debug_write(defense_strategy)



        best_strategy = None
        best_score = -1
        gamelib.debug_write(len(strategies))
        i = 0
        for strategy_ in strategies:
            i+=1
            if i % 10 == 0:
                 gamelib.debug_write('hahahha')
            current_game_state = deepcopy(self.current_state)
            #gamelib.debug_write(current_game_state.game_map[13,0])
            #gamelib.debug_write(current_game_state.serialized_string)
            #current_frame_state = deepcopy(self.current_serial_string)
            #current_game_map = deepcopy(self.current_game_map)
            strategy, current_sp = strategy_
            #gamelib.debug_write(current_game_state.serialized_string)
            current_game_state = self.update_game_map(current_game_state, strategy)

            # if len(strategy['spawn_factory']) != 0:
            #     current_game_state.attempt_spawn(FACTORY, strategy['spawn_factory'])
            # if len(strategy['spawn_turret']) != 0:
            #     current_game_state.attempt_spawn(TURRET, strategy['spawn_turret'])
            # if len(strategy['spawn_wall']) != 0:
            #     current_game_state.attempt_spawn(WALL, strategy['spawn_wall'])
            # if len(strategy['upgrade_wall'] + strategy['upgrade_turret'] + strategy['upgrade_factory']) != 0:
            #     current_game_state.attempt_upgrade(
            #         strategy['upgrade_wall'] + strategy['upgrade_turret'] + strategy['upgrade_factory'])
            # if len(strategy['spawn_interceptor']) != 0:
            #     game_state.attempt_spawn(INTERCEPTOR, strategy['spawn_interceptor'])
            # if len(strategy['spawn_scout']) != 0:
            #     game_state.attempt_spawn(INTERCEPTOR, strategy['spawn_interceptor'])
            # if len(strategy['spawn_demolisher']) != 0:
            #     game_state.attempt_spawn(INTERCEPTOR, strategy['spawn_interceptor'])
            # for [x, y] in TURRET_LOCATIONS:
            #     if current_game_state.game_map[x, y] != self.current_state.game_map[x,y]:
            #         gamelib.debug_write(current_game_state.game_map[x, y][0])
            #         gamelib.debug_write(self.current_state.game_map[x, y])

            #gamelib.debug_write(self.current_state.serialized_string == current_game_state.serialized_string)
            cur_score = self.evaluate_defense(current_game_state) + self.evaluate_offense(current_game_state, strategy) + self.evaluate_prod(current_game_state)
            #cur_score = self.evaluate_strategy(strategy, game_state)
            if cur_score > best_score:
                best_score = cur_score
                best_strategy = strategy

        return best_strategy

    # def evaluate_strategy(self, strategy, game_state):
    #     heuristic = 0
    #     serialized_string = json.loads(game_state.serialized_string)
    #     my_factories = serialized_string['p1Units'][2]
    #     my_turrets = serialized_string['p1Units'][1]
    #     my_walls = serialized_string['p1Units'][0]
    #     enemy_factories = serialized_string['p2Units'][2]
    #     enemy_turrets = serialized_string['p2Units'][1]
    #     enemy_walls = serialized_string['p2Units'][0]
    #
    #     heuristic = 100*len(strategy['upgrade_factory']) + 40*len(strategy['spawn_factory']) + \
    #         20*len(my_factories)*len(strategy['upgrade_turret']) + 5*len(my_factories)*len(strategy['spawn_turret']) + 2*len(my_walls)*len(my_turrets)*len(strategy['upgrade_wall'])+\
    #         2*len(my_turrets)*len(strategy['spawn_wall']) + 50*len(strategy['spawn_interceptor'])+ 20*len(enemy_turrets)*len(strategy['spawn_demolisher'])+10*1/(1+len(enemy_turrets))*len(strategy['spawn_scout'])
    #     return heuristic


    def update_game_map(self, game_state, strategy):
        '''

        :param game_state:
        :param strategy:
        :return:
        '''
        #gamelib.debug_write(game_state.serialized_string)
        serialized_string = json.loads(game_state.serialized_string)
        #gamelib.debug_write(serialized_string)
        #defense
        for factory_location in strategy['spawn_factory']:
            serialized_string['p1Units'][1].append([factory_location[0], factory_location[1], 30, str(random.randint(1000, 10000))])
        for turret_location in strategy['spawn_turret']:
            serialized_string['p1Units'][2].append([turret_location[0], turret_location[1], 100, str(random.randint(1000, 10000))])
        for wall_location in strategy['spawn_wall']:
            serialized_string['p1Units'][0].append([int(wall_location[0]), int(wall_location[1]), 75, str(random.randint(100, 1000))])
        for factory_location in strategy['upgrade_factory']:
            serialized_string['p1Units'][7].append([factory_location[0], factory_location[1], 30, str(random.randint(1000, 10000)) ])
        for turret_location in strategy['upgrade_turret']:
            serialized_string['p1Units'][7].append([turret_location[0], turret_location[1], 200, str(random.randint(1000, 10000))])
        for wall_location in strategy['upgrade_wall']:
            serialized_string['p1Units'][7].append([wall_location[0], wall_location[1], 300, str(random.randint(1000, 10000))])

        # #offense
        # for scout_location in strategy['spawn_scout']:
        #     serialized_string['p1Units'][3].append([scout_location[0], scout_location[1], 15, str(random.randint(1000, 10000))])
        # for demolisher_location in strategy['spawn_demolisher']:
        #     serialized_string['p1Units'][4].append([demolisher_location[0], demolisher_location[1], 5, str(random.randint(1000, 10000))])
        # for interceptor_location in strategy['spawn_interceptor']:
        #     serialized_string['p1Units'][5].append([interceptor_location[0], interceptor_location[1], 40, str(random.randint(1000, 10000))])

        #gamelib.debug_write(json.dumps(serialized_string))
        new_game_state = GameState(self.config, json.dumps(serialized_string))
        return new_game_state

    def evaluate_offense(self, game_state, strategy):
        '''
        :param game_state:
        :return:
        '''
        # Get the three locations

        my_scout = strategy['spawn_scout']
        my_demolisher = strategy['spawn_demolisher']
        #gamelib.debug_write(my_demolisher)
        my_it = strategy['spawn_interceptor']
        #gamelib.debug_write(my_it)
        value = 0
        G = self.eval_off(game_state)

        for i in my_scout:
            path_temp = game_state.find_path_to_edge(i)
            if path_temp is not None:
                #gamelib.debug_write(path_temp)
                value += 1 / (G[path_temp[-1][0]] + 0.001)

        for i in my_demolisher:
            path_temp = game_state.find_path_to_edge(i)

            if path_temp is not None:
                value += 4 / (G[path_temp[-1][0]] + 0.001)
        for i in my_it:
            path_temp = game_state.find_path_to_edge(i)
            if path_temp is not None:
                value += 1 / (G[path_temp[-1][0]] + 0.001)

        return value

    # def evaluate_defense(self, game_state):
    #     '''
    #     :param game_state:
    #     :return:
    #     '''
    #     # serialized_string = json.loads(game_state.serialized_string)
    #     # my_factories = serialized_string['p1Units'][2]
    #     # my_turrets = serialized_string['p1Units'][1]
    #     # my_walls = serialized_string['p1Units'][0]
    #     # heuristic = 1
    #     # if not my_factories == []:
    #     #     for factory in my_factories:
    #     #         location = factory[0:2]
    #     #         if game_state.game_map[location[0], location[1]][0].upgraded:
    #     #             heuristic += 20
    #     #         else:
    #     #             heuristic += 10
    #     heuristic = 1
    #     return heuristic

    def evaluate_defense(self, game_state):
        '''
        :param game_state:
        :return:
        '''
        serialized_string = json.loads(game_state.serialized_string)
        my_turret = serialized_string['p1Units'][1]
        my_wall = serialized_string['p1Units'][0]
        my_factories = serialized_string['p1Units'][2]
        heuristic = 0
        G = self.get_def_point_by_turret(my_turret, game_state)
        D = dict()
        for i in G.keys():
            D[i] = 1
        for i in my_factories:
            D[i[0]] = 2
        for i in self.scored_on_locations:
            D[i[0]] = 5

        for i in G.keys():
            heuristic += D[i] * G[i]

        return heuristic

    def evaluate_prod(self, game_state):
        heuristic = 0
        serialized_string = json.loads(game_state.serialized_string)
        my_factories = serialized_string['p1Units'][2]
        if not my_factories == []:
            for factory in my_factories:
                location = factory[0:2]
                if game_state.game_map[location[0], location[1]][0].upgraded:
                    heuristic += 10
                else:
                    heuristic += 1

        return heuristic

    # """
    # NOTE: All the methods after this point are part of the sample starter-algo
    # strategy and can safely be replaced for your custom algo.
    # """
    #
    # def starter_strategy(self, game_state):
    #     """
    #     For defense we will use a spread out layout and some interceptors early on.
    #     We will place turrets near locations the opponent managed to score on.
    #     For offense we will use long range demolishers if they place stationary units near the enemy's front.
    #     If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
    #     """
    #     # First, place basic defenses
    #     self.build_defences(game_state)
    #     # Now build reactive defenses based on where the enemy scored
    #     self.build_reactive_defense(game_state)
    #
    #     # If the turn is less than 5, stall with interceptors and wait to see enemy's base
    #     if game_state.turn_number < 2:
    #         if game_state.turn_number == 0:
    #             game_state.attempt_spawn(FACTORY, [[13, 0], [14, 0]])
    #             game_state.attempt_spawn(INTERCEPTOR, [[8, 5], [12, 1], [18, 4], [22, 8], [27, 13]])
    #             game_state.attempt_spawn(TURRET, [[4, 12]])
    #             game_state.attempt_upgrade([[13, 0]])
    #         if game_state.turn_number == 1:
    #             if SP < 9:
    #                 game_state.attempt_spawn(TURRET, [[9, 12], [23, 12]])
    #                 game_state.attempt_spawn(WALL, [[9, 13]])
    #             if SP >= 9:
    #                 game_state.attempt_upgrade([[14, 0]])
    #                 if (SP - 9) >= 2:
    #                     game_state.attempt_spawn(TURRET, [[23, 12]])
    #                 game_state.attempt_spawn(INTERCEPTOR, [[8, 5], [12, 1], [18, 4], [22, 8], [27, 13], [0, 13]])
    #     else:
    #         pass
    #
    # def build_defences(self, game_state):
    #     """
    #     Build basic defenses using hardcoded locations.
    #     Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
    #     """
    #     # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
    #     # More community tools available at: https://terminal.c1games.com/rules#Download
    #
    #     # Place turrets that attack enemy units
    #     turret_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
    #     # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
    #     game_state.attempt_spawn(TURRET, turret_locations)
    #
    #     # Place walls in front of turrets to soak up damage for them
    #     wall_locations = [[8, 12], [19, 12]]
    #     game_state.attempt_spawn(WALL, wall_locations)
    #     # upgrade walls so they soak more damage
    #     game_state.attempt_upgrade(wall_locations)
    #
    # def build_reactive_defense(self, game_state):
    #     """
    #     This function builds reactive defenses based on where the enemy scored on us from.
    #     We can track where the opponent scored by looking at events in action frames
    #     as shown in the on_action_frame function
    #     """
    #     for location in self.scored_on_locations:
    #         # Build turret one space above so that it doesn't block our own edge spawn locations
    #         build_location = [location[0], location[1] + 1]
    #         game_state.attempt_spawn(TURRET, build_location)

    def eval_def(self, game_state):
        game_dict = json.loads(game_state.serialized_string)
        my_turret = game_dict['p1Units'][2]
        edge_point = self.get_def_point_by_turret(my_turret, game_state)
        return edge_point

    def get_def_point_by_turret(self, my_turret, game_state, is_enemy = 0, upgraded_tur=None):
        edge_range = range(-2, 30)
        edge_point = dict.fromkeys(edge_range, 0)
        #gamelib.debug_write(my_turret)
        for i in my_turret:

            x = i[0]
            y = i[1]
            if upgraded_tur == None:
                #gamelib.debug_write(game_state.game_map[x,y])
                if is_enemy == 1:
                    tur_upgraded = game_state.game_map[x, 27-y][0].upgraded
                else:
                    tur_upgraded = game_state.game_map[x, y][0].upgraded


            else:
                tur_upgraded = i in upgraded_tur
            check_even = (x + y) % 2 == 0
            sum_xy = x + y
            diff_xy = x - y
            normal_def = 5
            up_def = 15
            if tur_upgraded == False:
                if check_even == True:
                    # add def power to right edge
                    edge_point[(sum_xy + 14) / 2] += normal_def
                    edge_point[(sum_xy + 14) / 2 + 1] += normal_def
                    edge_point[(sum_xy + 14) / 2 + 2] += normal_def / 2
                    edge_point[(sum_xy + 14) / 2 - 1] += normal_def
                    edge_point[(sum_xy + 14) / 2 - 2] += normal_def / 2

                    # add def power to left edge
                    edge_point[(13 + (diff_xy + 1)) / 2] += normal_def
                    edge_point[(13 + (diff_xy - 1)) / 2] += normal_def
                    edge_point[(13 + (diff_xy + 1)) / 2 + 1] += normal_def
                    edge_point[(13 + (diff_xy - 1)) / 2 - 1] += normal_def

                else:
                    # add def power to right edge
                    edge_point[(sum_xy + 1 + 14) / 2] += normal_def
                    edge_point[(sum_xy - 1 + 14) / 2] += normal_def
                    edge_point[(sum_xy + 1 + 14) / 2 + 1] += normal_def
                    edge_point[(sum_xy - 1 + 14) / 2 - 1] += normal_def

                    # add def power to left edge
                    edge_point[(13 + diff_xy) / 2] += normal_def
                    edge_point[(13 + diff_xy) / 2 + 1] += normal_def
                    edge_point[(13 + diff_xy) / 2 + 2] += normal_def / 2
                    edge_point[(13 + diff_xy) / 2 - 1] += normal_def
                    edge_point[(13 + diff_xy) / 2 - 2] += normal_def / 2
            else:
                # the turret was upgraded
                if check_even == True:
                    # add def power to right edge
                    edge_point[(sum_xy + 14) / 2] += up_def
                    edge_point[(sum_xy + 14) / 2 + 1] += up_def
                    edge_point[(sum_xy + 14) / 2 + 2] += up_def
                    edge_point[(sum_xy + 14) / 2 - 1] += up_def
                    edge_point[(sum_xy + 14) / 2 - 2] += up_def

                    # add def power to left edge
                    edge_point[(13 + (diff_xy + 1)) / 2] += up_def
                    edge_point[(13 + (diff_xy - 1)) / 2] += up_def
                    edge_point[(13 + (diff_xy + 1)) / 2 + 1] += up_def
                    edge_point[(13 + (diff_xy - 1)) / 2 - 1] += up_def
                    edge_point[(13 + (diff_xy + 1)) / 2 + 2] += up_def / 2
                    edge_point[(13 + (diff_xy - 1)) / 2 - 2] += up_def / 2
                else:
                    # the turret was upgraded and sum is odd
                    # add def power to right edge
                    edge_point[(sum_xy + 1 + 14) / 2] += up_def
                    edge_point[(sum_xy - 1 + 14) / 2] += up_def
                    edge_point[(sum_xy + 1 + 14) / 2 + 1] += up_def
                    edge_point[(sum_xy - 1 + 14) / 2 - 1] += up_def
                    edge_point[(sum_xy + 1 + 14) / 2 + 2] += up_def / 2
                    edge_point[(sum_xy - 1 + 14) / 2 - 2] += up_def / 2

                    # add def power to left edge
                    edge_point[(13 + diff_xy) / 2] += up_def
                    edge_point[(13 + diff_xy) / 2 + 1] += up_def
                    edge_point[(13 + diff_xy) / 2 + 2] += up_def
                    edge_point[(13 + diff_xy) / 2 - 1] += up_def
                    edge_point[(13 + diff_xy) / 2 - 2] += up_def
        del edge_point[-2]
        del edge_point[-1]
        del edge_point[28]
        del edge_point[29]
        return edge_point

    def get_location_from_x(self, x_list):
        location = []
        for x in x_list:
            if x <= 13:
                location.append([x, 13 - x])
            else:
                location.append([x, x - 14])
        return location

    def interceptor_spawn(self, game_state, my_mp, strategies):

        new_strategies = []
        edge_point = self.eval_def(game_state)
        inter_add = 10

        for strategy_ in strategies:
            strategy, _ = strategy_
            #gamelib.debug_write(strategy)

            res = []
            strategy['spawn_interceptor'] = res.copy()
            new_strategies.append([strategy.copy(), my_mp])

            if my_mp < 1:
                continue
            else:
                new_def = self.get_def_point_by_turret(strategy['spawn_turret'], game_state, upgraded_tur=strategy['upgrade_turret'])
                for i in range(0, 28):
                    new_def[i] = edge_point[i] + new_def[i]

                curr_mp = my_mp
                while curr_mp > 0:
                    curr_mp -= 1
                    min_def_index = sorted(new_def, key=edge_point.get)
                    res.append(self.get_location_from_x([min_def_index[0]])[0])
                    new_def[min_def_index[0]] += inter_add

                    if len(res) >= 5:
                        strategy['spawn_interceptor'] = res.copy()
                        new_strategies.append([strategy.copy(), curr_mp])
        return new_strategies

    def scout_spawn(self, game_state, strategies):
        # Start from the bottom
        scout_location = [[i, 13-i] for i in range(2, 12)] + [[25-i, 11-i] for i in range(10)]
        new_strategies = []

        for strategy_ in strategies:
            strategy, current_mp = strategy_
            res = []
            strategy['spawn_scout'] = res.copy()
            new_strategies.append([strategy.copy(), current_mp])
            if current_mp > 0:
                for i in scout_location:
                    strategy['spawn_scout'] = [i for j in range(int(current_mp))]
                    new_strategies.append([strategy.copy(), 0])
        return new_strategies

    def demolisher_spawn(self, game_state, strategies):
        demolisher_location = [[i, 13-i ] for i in range(2, 12)] + [[25-i, 11- i] for i in range(10)]
        new_strategies = []

        for strategy_ in strategies:
            strategy, current_mp = strategy_
            res = []
            strategy['spawn_demolisher'] = res.copy()
            new_strategies.append([strategy.copy(), current_mp])
            if current_mp > 0:
                for i in demolisher_location:
                    strategy['spawn_demolisher'] = [i for j in range(int(current_mp))]
                    new_strategies.append([strategy.copy(), 0])
        return new_strategies

    def eval_off(self, game_state):
        game_dict = json.loads(game_state.serialized_string)
        oppo_turret = game_dict['p2Units'][2]
        for i in oppo_turret:
            i[1] = 27 - i[1]
        edge_point = self.get_def_point_by_turret(oppo_turret, game_state, is_enemy=1)
        return edge_point

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

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
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET,
                                                                                             game_state.config).damage_i
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (
                            valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
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
                gamelib.debug_write("Me got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All my bleed locations: {}".format(self.scored_on_locations))
            else:
                gamelib.debug_write("Enemy got scored on at: {}".format(location))
                self.they_scored_on_locations.append(location)
                gamelib.debug_write("All enemy bleed locations: {}".format(self.they_scored_on_locations))

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
