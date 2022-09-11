"""
Flyweight concept, working with large number of objects,
using pointers to share objects data if it's the same, instead of creating many new obj.

basic plan:
class: bees_game        |  function: run_the_game (intrinsic + extrinsic)
                        |  fields: array of intrinsic + extrinsic data, map, and more

class: extrinsic_params |  fields: coordinate, temperature resistance, health, growth stage, object_ID.
classes: Factory        |  return from dictionary new or existed instance of intrinsic class

intrinsic classes: (immutable)
class: egg              |  functions: crack (the shell) chance grow with time
class: Larva            |  functions: grow
class: Pupa             |  functions: grow
class: bee              |  functions: eat, queen lay eggs, kill other queen

flow: (didn't implement = (X))
create only one game class - singleton DP (X)
Init creatures at start, queens, chose number of adults bee, number of eggs, larvas and pupas.
Init factory to create new creature if not existed in Factory
Create intrinsic extrinsic array with threads tending to intrinsic data and extrinsic data creation on separate threads.
Init Game class with the data
Run over all creatures, check growth and other function like move, health(X) and temperature(X) change in night/winter (X)
If new queen appear at "5" growth stage, it would kill all other queens from the list of queens, lay new eggs + 1 queen
If the sole queen too old, it would go away with 30 percent of adult bee colony. (X)
Death events
Using pygame to show all that fun. Pygame need python ver of 3.9.5 at max! (its too bad as 3.10 ver match-case is great)
"""
import sys  # convert class name as a string to object (used in Bee_lifeCycle_Factory class at init)
import uuid  # unique string generator for a pseudo restarting thread
import queue  # get val out of worker thread
import random  # bees type random generator (Female, Male)
import pygame  # visualisation of the colony
import threading
from pygame.locals import *  # using for interactions with user, mouse left click etc
import numpy as np  # arrays
from typing import Dict  # using dictionary in Bee_lifeCycle_Factory
from typing import Union  # declare as correct input -many- types, used in Bee_lifeCycle_Factory
from threading import Thread  # run game and update map in parallel, hopefully do more (e.g. colony/4 etc)
from collections import Counter  # count prints to run faster
from dataclasses import dataclass  # immutable + a struct like behaviour
from scipy.stats import truncnorm  # used for truncated normal distribution


@dataclass(frozen=True)  # Immutable, intrinsic data
class Egg:
    egg_type: str  # types are: FW, FQ, MW. Female/Male + Worker/Queen (no MQ as a male bee cannot be a Queen).

    # "cracking shell" probability get higher with higher growth value
    # return growth progress, and change intrinsic object if growth stage passed the threshold
    def cracking_shell(self, growth: float, intrinsic_factory, int_extrinsic_data, egg_indx, updating_game_map) \
            -> float:
        intrinsic_factory.add_class_print_to_counter(f"{self.egg_type} went for a crack in the shell,"
                                                     f" a test of strength.")
        cracking_success_result = round(random.uniform(0.7, 1.5), 2) * growth  # using round .2f
        if cracking_success_result > 2:  # change intrinsic data
            int_extrinsic_data[egg_indx][0] = intrinsic_factory.get_class_instance(self.egg_type, "Larva")
            updating_game_map[int_extrinsic_data[egg_indx][1].x_coordinate][
                int_extrinsic_data[egg_indx][1].y_coordinate] = 2
            return 2  # "success", apply result to extrinsic growth. Todo use health + temp resistance outside (X)
        return cracking_success_result + growth  # apply result, next time chance would be higher

    def breath_through_the_shell(self) -> None:  # didn't implement (X)
        # todo consider delete, or use action for bee queen movement checking
        #  for its colony citizens action, a "meet" event...
        #  maybe change all action func (for all extrinsic class) to the same name (action) for easier usage instead of
        #  switch case
        print(f"A {self.egg_type} is currently processing oxygen")


@dataclass(frozen=True)  # Immutable, intrinsic data
class Larva:
    larva_type: str  # FW, FQ, MW

    # return growth progress
    def growing_fast(self, growth: float, intrinsic_factory, int_extrinsic_data, larva_indx,
                     updating_game_map) -> float:
        # self.eating()
        growth_by = round(random.uniform(0.7, 1.5), 2) * growth
        if growth_by > 3:
            int_extrinsic_data[larva_indx][0] = intrinsic_factory.get_class_instance(self.larva_type, "Pupa")
            updating_game_map[int_extrinsic_data[larva_indx][1].x_coordinate][
                int_extrinsic_data[larva_indx][1].y_coordinate] = 3
            return 3
        return growth_by + growth

    ''' 
    def eating(self) -> None:  # a rare monument from my old (python 3.10) code... which doesnt work with pygame
        match self.larva_type:
            case "FQ":
                print("Behold! The larva, a future potential queen, is eating a royal jelly!")
            case "FW":
                print("a female worker is eating a worker jelly")
            case "MW":
                print("a male worker is eating a drone jelly")
            case _:
                print("wrong naming! <(#_*)> check out what happened (at larva eating func)")
    '''


@dataclass(frozen=True)  # Immutable, intrinsic data
class Pupa:
    pupa_type: str  # FW, FQ, MW

    # return growth progress
    def pupa_growth(self, growth: int, intrinsic_factory, int_extrinsic_data, pupa_indx, updating_game_map) -> float:
        growth_by = round(random.uniform(0.7, 1.5), 2) * growth
        if growth_by > 4:
            int_extrinsic_data[pupa_indx][0] = intrinsic_factory.get_class_instance(self.pupa_type, "Bee")
            updating_game_map[int_extrinsic_data[pupa_indx][1].x_coordinate][
                int_extrinsic_data[pupa_indx][1].y_coordinate] = 4
            return 4
        self.pupa_action(intrinsic_factory)
        return growth_by + growth

    def pupa_action(self, intrinsic_factory) -> None:
        intrinsic_factory.add_class_print_to_counter(f"A young {self.pupa_type} spin a cocoon around itself and pupate,"
                                                     f"then, it develops into a recognisable bee,"
                                                     f" with wings, legs, head, thorax and abdomen")


@dataclass(frozen=True)  # Immutable, intrinsic data
class Bee:
    bee_type: str  # FW, FQ, MW

    # return growth stage, change object intrinsic if growth passed the threshold
    def eat(self, growth: int, int_extrinsic_data, bee_indx, updating_game_map, eggs_lay_func, intrinsic_factory
            , lst_deaths_ind) -> float:
        if growth == 4:
            intrinsic_factory.add_class_print_to_counter(f"a young adult {self.bee_type} emerging from the "
                                                         f"hexagonal-shaped egg cell, by chewing its way through the "
                                                         f"wax capping.")
            updating_game_map[int_extrinsic_data[bee_indx][1].x_coordinate][int_extrinsic_data[bee_indx][1]
                .y_coordinate] = 5
            return 5
        if growth == 5:
            if self.bee_type == "FQ":  # (Female Queen)
                intrinsic_factory.add_class_print_to_counter(f"Behold! The queen is eating a royal jelly!")
                # didn't implement:
                # if queen old - no eggs, stop killing queens, grow new queens... after new adult queen appeared,
                # old would take 30 percent from colony and move away, by old, lets say > 10

                move(updating_game_map, int_extrinsic_data, bee_indx)  # todo in thread (X)

                eggs_lay_func(bee_indx)  # using bee queen index to not kill itself accidentally
                # todo: kill all queen (V) below age 10 (X),
                # if colony at 70% filled and up, old queen take 30% colony away (X)
                return 6  # apply 6 to growth stage

            intrinsic_factory.add_class_print_to_counter(f"a {self.bee_type} bee is eating a nectar or a pollen")
            move(updating_game_map, int_extrinsic_data, bee_indx)  # todo in thread (X)
            return 6  # apply to growth extrinsic factor

        # death chance grow with the bee, calc outside with more extrinsic data, todo (X). currently only stage matter..
        # if growth higher than 6:
        if growth < 15:
            updating_game_map[int_extrinsic_data[bee_indx][1].x_coordinate] \
                [int_extrinsic_data[bee_indx][1].y_coordinate] = growth
            move(updating_game_map, int_extrinsic_data, bee_indx)
            return 0.1 * growth + growth  # apply to extrinsic growth
        # else, not moving anymore...
        # death:
        if 30 > growth >= 15:  # "> 30" so it wont be counted as death more than once
            lst_deaths_ind.append(bee_indx)
            updating_game_map[int_extrinsic_data[bee_indx][1].x_coordinate] \
                [int_extrinsic_data[bee_indx][1].y_coordinate] = -1  # death event, clear the grid - changing clr black
        return 31  # bee dies
        #  should have been more potential queens way before 15 stage. (currently only 1 instead of e.g. 20) (VX)


def move(updating_game_map, int_extrinsic_data, bee_ind) -> None:
    """
    random choice movement meaning:
    0 = up           map index meaning:       y-=1
    1 = top right    map index meaning: x+=1, y-=1
    2 = right        map index meaning: x+=1,
    3 = button right map index meaning: x+=1, y+=1
    4 = button       map index meaning:       y+=1
    5 = button left  map index meaning: x-=1, y+=1
    6 = left         map index meaning: x-=1,
    7 = top left     map index meaning: x-=1, y-=1
    If at first try, grid is taken (not = -1), bee won't move for current whole colony actions (current for loop...)
    an option, to use list with 8 options, and remove each "move" option (that point to a not free grid) from random
    option, if empty, object won't move. As map big enough, and movement isn't that important, only one try per object.
    """
    move_to = np.random.randint(0, 8, size=None)  # 8 movement options - (0 to 7).
    x_coor = int_extrinsic_data[bee_ind][1].x_coordinate
    y_coor = int_extrinsic_data[bee_ind][1].y_coordinate
    # todo next line, it's not the best, but for now..: (a border patch)
    if x_coor != len(updating_game_map) - 1 and y_coor != len(updating_game_map) - 1 and x_coor != 0 and y_coor != 0:
        if move_to == 0:
            if -1 == updating_game_map[x_coor][y_coor - 1]:
                updating_game_map[x_coor][y_coor - 1] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].y_coordinate -= 1
            return
        elif move_to == 1:
            if -1 == updating_game_map[x_coor + 1][y_coor - 1]:
                updating_game_map[x_coor + 1][y_coor - 1] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].y_coordinate -= 1
                int_extrinsic_data[bee_ind][1].x_coordinate += 1
            return
        elif move_to == 2:
            if -1 == updating_game_map[x_coor + 1][y_coor]:
                updating_game_map[x_coor + 1][y_coor] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].x_coordinate += 1
            return
        elif move_to == 3:
            if -1 == updating_game_map[x_coor + 1][y_coor + 1]:
                updating_game_map[x_coor + 1][y_coor + 1] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].y_coordinate += 1
                int_extrinsic_data[bee_ind][1].x_coordinate += 1
            return
        elif move_to == 4:
            if -1 == updating_game_map[x_coor][y_coor + 1]:
                updating_game_map[x_coor][y_coor + 1] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].y_coordinate += 1
            return
        elif move_to == 5:
            if -1 == updating_game_map[x_coor - 1][y_coor + 1]:
                updating_game_map[x_coor - 1][y_coor + 1] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].y_coordinate += 1
                int_extrinsic_data[bee_ind][1].x_coordinate -= 1
            return
        elif move_to == 6:
            if -1 == updating_game_map[x_coor - 1][y_coor]:
                updating_game_map[x_coor - 1][y_coor] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].x_coordinate -= 1
            return
        elif move_to == 7:
            if -1 == updating_game_map[x_coor - 1][y_coor - 1]:
                updating_game_map[x_coor - 1][y_coor - 1] = int_extrinsic_data[bee_ind][1].growth
                updating_game_map[x_coor][y_coor] = -1
                int_extrinsic_data[bee_ind][1].y_coordinate -= 1
                int_extrinsic_data[bee_ind][1].x_coordinate -= 1
            return
    return


@dataclass
class extrinsic_params:  # easily get and set vars val

    x_coordinate: int
    y_coordinate: int
    health: float
    growth: float
    temperature_resistance: float
    id: int
    # (':' called hints, say what type it should get, work with high python ver(>3.5 if not mistaken))


class Bee_lifeCycle_Factory:
    """
    When the client requests a flyweight (intrinsic class data),
    the factory either returns an existing instance ("pointer"), or creates a new one if it doesn't exist yet.
    """

    _Bee_lifeCycle: Dict[str, Union[Egg, Larva, Pupa, Bee]] = {}  # Union hint to one type of the given types
    _print_summation: Counter({str, int})

    # class_types: FQ, FW, MW. class_indicator: 0, 1, 2, 3 = egg, larva, pupa, bee
    def __init__(self, field_types: list, classes_name: list) -> None:
        for list_set_ind, class_name in enumerate(classes_name):
            for field_type in field_types[list_set_ind]:
                self._Bee_lifeCycle[self.get_key(field_type, class_name)] = self.str_to_class(class_name)(field_type)
        self._print_summation = Counter({"FlyweightFactory: Reusing existing class instance.": 0})

    def str_to_class(self, class_name):
        return getattr(sys.modules[__name__], class_name)

    # create dictionary key with class name + field, returns a Flyweight's string hash for a given state/
    def get_key(self, field_type: str, class_type: str) -> str:
        return "_".join(sorted([field_type, class_type]))

    def add_class_print_to_counter(self, stringy: str):
        self._print_summation[stringy] += 1

    def get_class_instance(self, field_type: str, class_name: str) -> Union[Bee, Larva, Egg, Pupa]:
        """
        Returns an existing Flyweight with a given state or creates a new one.
        """
        key = self.get_key(field_type, class_name)
        if field_type == "FQ" or field_type == "FW" or field_type == "MW":
            if not self._Bee_lifeCycle.get(key):
                self._print_summation[f"FlyweightFactory: Can't find {class_name} class " \
                                      f"with \"{field_type}\" "f"as its field, creating a new one."] += 1
                self._Bee_lifeCycle[key] = self.str_to_class(class_name)(field_type)
                return self._Bee_lifeCycle[key]
            else:
                self._print_summation["FlyweightFactory: Reusing existing class instance."] += 1
            return self._Bee_lifeCycle[key]
        else:
            print(f"{field_type} is a wrong field type. It should be one option from these: FW, MW, FQ.")
            exit(1)

    def list_classes(self) -> None:
        count = len(self._Bee_lifeCycle)
        print(f"bee_classes_Factory: I have {count} classes:")
        print("\n".join(map(str, self._Bee_lifeCycle.keys())), end="")

    def list_print_summation(self) -> None:
        for key, value in self._print_summation.items():
            print("\"" + key + "\" happened", value, "times.")
        self._print_summation.clear()


# game class, holds all the needed data to run the game
class Bees_Game:
    # initiation:
    def __init__(self,
                 intrinsic_extrinsic: np.array,
                 queens_indices: list,
                 game_map: np.array,
                 colony_init_num: int,
                 intrinsic_factory: Bee_lifeCycle_Factory):
        # Extrinsic: x_coordinate, y_coordinate, curr_temperature, health, growth stage, temperature_resistance, id.
        # Intrinsic: gender(M,F) + type(worker\queen) no M+Queen! => FW, MW, FQ.

        self.intrinsic_extrinsic = intrinsic_extrinsic
        self.game_map = game_map
        self.queens_indices = queens_indices
        self.bee_id = colony_init_num  # as I use colony curr num in for loop, cant use it as ID because of death sol
        self.colony_current_num = colony_init_num  # calculate reasonable adding eggs number
        self.intrinsic_factory = intrinsic_factory  # using factory during the game to get existing instance or create.
        self.death_indices = []  # hold indices of deaths (waiting for newborn eggs to refill vacant array cells)
        self.array_upper_bound = self.colony_current_num  # grow by having new eggs higher than death indices lst

    # adult bee queen lay eggs after killing other queens, try filling vacant cell (older bees death) first etc
    def add_eggs_laid_by_queen(self, adult_queen) -> None:
        for i in range(len(self.queens_indices)):  # queen kill other queens event, by changing queens growth to 31
            if self.queens_indices[i] != adult_queen:
                self.intrinsic_extrinsic[self.queens_indices[i]][1].growth = 31
                self.death_indices.append(self.queens_indices[i])
                self.game_map[self.intrinsic_extrinsic[self.queens_indices[i]][1]
                    .x_coordinate][self.intrinsic_extrinsic[self.queens_indices[i]][1].y_coordinate] = -1

        self.queens_indices = [adult_queen]  # only 1 queen stayed alive

        # choosing how much eggs would be laid, open to changes...
        if self.colony_current_num > len(self.death_indices):
            self.colony_current_num -= len(self.death_indices)
            if self.colony_current_num < 8900000:
                added_eggs_num = int(self.colony_current_num * 0.3)
        else:
            added_eggs_num = int(len(self.death_indices) / 2)

        while added_eggs_num and (len(self.death_indices)):  # while both are higher than 0, insert, else add new...
            refill_ind = self.death_indices.pop(0)
            # inserting new eggs into vacant cell left by bees death
            self.intrinsic_extrinsic[refill_ind][0] \
                = self.intrinsic_factory.get_class_instance(random.choice(["FW", "MW"]), "Egg")
            self.intrinsic_extrinsic[refill_ind][1] = \
                extrinsic_params_generator(self.game_map, len(self.game_map) - 1, 1, self.bee_id)
            added_eggs_num -= 1
            self.bee_id += 1
            self.colony_current_num += 1

        add_eggs_beyond_death_count = self.colony_current_num + added_eggs_num
        self.bee_id += added_eggs_num
        # add eggs beyond death list length
        for added_egg_id in range(self.colony_current_num, add_eggs_beyond_death_count):
            self.intrinsic_extrinsic[added_egg_id][0] \
                = self.intrinsic_factory.get_class_instance(random.choice(["FW", "MW"]), "Egg")
            self.intrinsic_extrinsic[added_egg_id][1] = \
                extrinsic_params_generator(self.game_map, len(self.game_map) - 1, 1, added_egg_id)
        self.colony_current_num += added_eggs_num

        # add one queen egg, (can do random/bigger quantity, todo)
        self.array_upper_bound += added_eggs_num
        self.intrinsic_extrinsic[self.array_upper_bound][0] \
            = self.intrinsic_factory.get_class_instance("FQ", "Egg")
        self.intrinsic_extrinsic[self.array_upper_bound][1] \
            = extrinsic_params_generator(self.game_map, len(self.game_map) - 1, 1, self.array_upper_bound)

        # adding to queens lst
        self.queens_indices.append(self.array_upper_bound)
        self.colony_current_num += 1
        self.array_upper_bound += 1
        return

    def run_the_game(self):
        for ind_filled_objects in range(self.array_upper_bound):
            # match case run faster than inheritance (tested at run_time_check.py): update, don't work with pygame ver..
            # currently didn't test times again, so its stay without inheritance
            obj_class = type(self.intrinsic_extrinsic[ind_filled_objects][0]).__name__

            if obj_class == "Egg":  # todo in thread (X)
                additional_egg_growth = self.intrinsic_extrinsic[ind_filled_objects][0].cracking_shell(
                    self.intrinsic_extrinsic[ind_filled_objects][1].growth,  # update growth using current
                    self.intrinsic_factory,  # used if next stage achieved to change intrinsic
                    self.intrinsic_extrinsic,  # intrinsic extrinsic, for changing intrinsic type if needed,
                    # + get x,y from extrinsic
                    ind_filled_objects,  # object index in intrinsic extrinsic array
                    self.game_map  # update if needed
                )
                # (temperature irrelevant here, as eggs doesn't being laid in the winter).
                self.intrinsic_extrinsic[ind_filled_objects][1].growth = additional_egg_growth

            elif obj_class == "Larva":  # todo in thread (X)
                additional_larva_growth = self.intrinsic_extrinsic[ind_filled_objects][0].growing_fast(
                    self.intrinsic_extrinsic[ind_filled_objects][1].growth,  # update growth stage
                    self.intrinsic_factory,  # for changing intrinsic type if needed
                    self.intrinsic_extrinsic,  # and get x,y from extrinsic
                    ind_filled_objects,  # object index in intrinsic extrinsic array
                    self.game_map  # update if needed, if object grew to next stage
                )
                # todo add temperature change event applying to growth, from 0.8 to 1.2 temp multi growth
                self.intrinsic_extrinsic[ind_filled_objects][1].growth = additional_larva_growth

            elif obj_class == "Pupa":  # todo in thread (X)
                additional_pupa_growth = self.intrinsic_extrinsic[ind_filled_objects][0].pupa_growth(
                    self.intrinsic_extrinsic[ind_filled_objects][1].growth,
                    self.intrinsic_factory,
                    self.intrinsic_extrinsic,
                    ind_filled_objects,
                    self.game_map)
                # todo add temperature
                self.intrinsic_extrinsic[ind_filled_objects][1].growth = additional_pupa_growth

            elif obj_class == "Bee":  # todo in thread (X)
                additional_bee_growth = self.intrinsic_extrinsic[ind_filled_objects][0].eat(
                    self.intrinsic_extrinsic[ind_filled_objects][1].growth,
                    self.intrinsic_extrinsic,
                    ind_filled_objects,
                    self.game_map,
                    self.add_eggs_laid_by_queen,  # if queen is big enough, use function
                    self.intrinsic_factory,  # for factory "prints" type counter, as intrinsic obj change needed no more
                    self.death_indices)
                self.intrinsic_extrinsic[ind_filled_objects][1].growth = additional_bee_growth
        intrinsic_data_factory.list_print_summation()
        print("1 generation ended")

    def draw(self):
        pass
        # todo change map per object instead of whole objects at once, using threads


def extrinsic_params_generator(game_map_matrix: np.array, map_length: int, class_growth_stage: int, id: int) ->\
        extrinsic_params:
    """ # a reminder for extrinsic params:
    x_coordinate: int =>
    y_coordinate: int => random (x_coordinate, y_coordinate) while coo'!= -1 (as map init to -1 each cell)
    temperature_resistance : float => didn't implement temperature change, but using winter and summer to move from 0.8
    to 1.2 temperature and down to change growth rate, and determine if bee queen would lay eggs
    (as it doesn't happen in winter), should implement a temperature func, using resistance + health applied to growth
    strategy: higher resistance, health won't change much by winter/hot summer, growth would slow only a little bit in
    winter... death change lower etc (X)
    health      : float # 1-10, higher goes to healthy. lower => higher growth ("growing old",closer to death faster(X))
    growth      : float # egg: 0-2, larva: 2-3, pupa: 3-4, bee: 5-15, 15=too old, death
    id          : bee id => int from 0 and up as more bees being laid
    """
    # generating coordinates per object
    x = random.randint(0, map_length)  # get random integer in range 0->3999 included
    y = random.randint(0, map_length)
    while game_map_matrix[x][y] != -1:  # available grid
        x = random.randint(0, map_length)
        y = random.randint(0, map_length)

    game_map_matrix[x][y] = class_growth_stage

    # high resistance at 9+, lowest at 0+, weather affecting health, affecting death.
    # def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    #    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

    # todo if at runtime a need arise to run the program faster, change to normal instead of truncated (much faster)
    # temperature_resistance = get_truncated_normal(mean=5, sd=1, low=1, upp=9).rvs()

    # using a much faster method (tested) instead of above:
    temperature_resistance = np.random.uniform(low=0.8, high=1.2)
    health = np.random.uniform(low=0.1, high=10)  # todo higher death chance the lower the health is (X)
    return extrinsic_params(x, y, round(health, 2), class_growth_stage, round(temperature_resistance, 2), id)


def create_init_intrinsic_and_extrinsic_data(intrinsic_factory: Bee_lifeCycle_Factory,
                                             variation_per_class_lst: list,
                                             egg_init: int,
                                             larva_init: int,
                                             pupa_init: int,
                                             bee_init: int,
                                             init_overall_num: int) -> np.array:
    """ Flow:
    using np array to hold per object intrinsic + extrinsic data, while extrinsic (x,y) applied to map of 16M cells.
    Objects are randomly placed (probability of falling to same cell or low enough... otherwise could use list indices
    + remove).
    """
    num_columns = 2  # first col for extrinsic, sec col for intrinsic

    # rows length: choosing a starting colony capacity with "space"(>init num) for colony growth
    # (np append create a new array with copied values, so I add space to avoid using append, but not too much
    # if not needed to not use unneeded memory unnecessarily).
    if init_overall_num < 1000:
        num_rows = 100000
    elif 1000 < init_overall_num < 10000:
        num_rows = 1000000
    else:
        num_rows = 10000000

    def thread_lst_comprehention(lst_comprehension_magic, out_thread_val_with_queue):  # needed return val as well...
        out_thread_val_with_queue.put(lst_comprehension_magic)
        return

    out_queue = queue.Queue()
    # extrinsic + intrinsic data holder:
    thread1 = threading.Thread(target=thread_lst_comprehention, args=(
                                   np.array([[0 for i in range(2)] for j in range(num_rows)], dtype=object), out_queue))
    thread1.start()

    """
    map boundaries: assuming max colony num is 10000000, hence map would be 4000*4000, which is higher
                     than max num (10000000) sqrt... that way I get some "moving space" for sure.
    map indices = 16M, max colony = 10M, hence 9999999/16m=0.62, good enough.
    """
    map_size = 4000  # height, width
    thread2 = threading.Thread(target=thread_lst_comprehention, args=(np.array(
        [[-1 for i in range(map_size)] for j in range(map_size)], dtype=object), out_queue))
    thread2.start()

    thread1.join()  # both can finish first, depend on colony init num.
    thread2.join()

    # extrinsic + intrinsic data holder:
    ex_in_array = out_queue.get()
    game_map_matrix = out_queue.get()

    queen_lst_indices = []  # further use to determine queen and more

    # add intrinsic + extrinsic data to first and second column respectively

    # I don't care much if threads would cause the same x,y, even though chance is minuscule.
    # Colony init, add to array, add to map, add FQ if exist to lst, same for other classes.
    # (in func for threads usage)

    def init_egg_intrinsic(ex_in_array, intrinsic_factory, variation_per_class_lst, egg_init):
        for bee_ind in range(egg_init):
            ex_in_array[bee_ind][0] = intrinsic_factory.get_class_instance(variation_per_class_lst[bee_ind], "Egg")

    def init_egg_extrinsic(ex_in_array, extrinsic_params_generator, variation_per_class_lst,
                           game_map_matrix, map_size, queen_lst_indices, egg_init):
        for bee_ind in range(egg_init):
            ex_in_array[bee_ind][1] = extrinsic_params_generator(game_map_matrix, map_size - 1, 1, bee_ind)
            if variation_per_class_lst[bee_ind] == "FQ":
                queen_lst_indices.append(bee_ind)

    def init_larva_intrinsic(ex_in_array, intrinsic_factory, variation_per_class_lst, egg_init,
                             larva_init):
        for bee_ind in range(egg_init, egg_init + larva_init):
            ex_in_array[bee_ind][0] = intrinsic_factory.get_class_instance(variation_per_class_lst[bee_ind], "Larva")

    def init_larva_extrinsic(ex_in_array, extrinsic_params_generator, variation_per_class_lst, game_map_matrix,
                             map_size, queen_lst_indices, egg_init, larva_init):
        for bee_ind in range(egg_init, egg_init + larva_init):
            ex_in_array[bee_ind][1] = extrinsic_params_generator(game_map_matrix, map_size - 1, 2, bee_ind)
            if variation_per_class_lst[bee_ind] == "FQ":
                queen_lst_indices.append(bee_ind)

    def init_pupa_intrinsic(ex_in_array, intrinsic_factory, variation_per_class_lst, egg_init, larva_init, pupa_init):
        for bee_ind in range(egg_init + larva_init, egg_init + larva_init + pupa_init):
            ex_in_array[bee_ind][0] = intrinsic_factory.get_class_instance(variation_per_class_lst[bee_ind], "Pupa")

    def init_pupa_extrinsic(ex_in_array, extrinsic_params_generator, variation_per_class_lst, game_map_matrix, map_size,
                            queen_lst_indices, egg_init, larva_init, pupa_init):
        for bee_ind in range(egg_init + larva_init, egg_init + larva_init + pupa_init):
            ex_in_array[bee_ind][1] = extrinsic_params_generator(game_map_matrix, map_size - 1, 3, bee_ind)
            if variation_per_class_lst[bee_ind] == "FQ":
                queen_lst_indices.append(bee_ind)

    def init_bee_intrinsic(ex_in_array, intrinsic_factory, variation_per_class_lst, egg_init, larva_init, pupa_init,
                           bee_init):
        for bee_ind in range(pupa_init + egg_init + larva_init, egg_init + larva_init + pupa_init + bee_init):
            ex_in_array[bee_ind][0] = intrinsic_factory.get_class_instance(variation_per_class_lst[bee_ind], "Bee")

    def init_bee_extrinsic(ex_in_array, extrinsic_params_generator, variation_per_class_lst, game_map_matrix, map_size,
                           queen_lst_indices, egg_init, larva_init, pupa_init, bee_init):
        for bee_ind in range(pupa_init + egg_init + larva_init, egg_init + larva_init + pupa_init + bee_init):
            ex_in_array[bee_ind][1] = extrinsic_params_generator(game_map_matrix, map_size - 1, 4, bee_ind)
            if variation_per_class_lst[bee_ind] == "FQ":
                queen_lst_indices.append(bee_ind)

    # data in lst before input to threads:
    cln_dt = [ex_in_array,                 # both      [0]
              intrinsic_factory,           # intrinsic [1]
              extrinsic_params_generator,  # extrinsic [2]
              variation_per_class_lst,     # both      [3]
              game_map_matrix,             # extrinsic [4]
              map_size,                    # extrinsic [5]
              queen_lst_indices,           # extrinsic [6]
              egg_init]                    # both      [7]

    # egg intrinsic
    thread3 = threading.Thread(target=init_egg_intrinsic(cln_dt[0], cln_dt[1], cln_dt[3], cln_dt[7]))
    thread3.start()
    # egg extrinsic
    thread4 = threading.Thread(
        target=init_egg_extrinsic(cln_dt[0], cln_dt[2], cln_dt[3], cln_dt[4], cln_dt[5], cln_dt[6], cln_dt[7]))
    thread4.start()

    # larva intrinsic
    thread5 = threading.Thread(target=init_larva_intrinsic(cln_dt[0], cln_dt[1], cln_dt[3], cln_dt[7], larva_init))
    thread5.start()
    # larva extrinsic
    thread6 = threading.Thread(target=init_larva_extrinsic(cln_dt[0], cln_dt[2], cln_dt[3], cln_dt[4], cln_dt[5],
                                                           cln_dt[6], cln_dt[7], larva_init))
    thread6.start()

    # pupa intrinsic
    thread7 = threading.Thread(
        target=init_pupa_intrinsic(cln_dt[0], cln_dt[1], cln_dt[3], cln_dt[7], larva_init, pupa_init))
    thread7.start()
    # pupa extrinsic
    thread8 = threading.Thread(target=init_pupa_extrinsic(cln_dt[0], cln_dt[2], cln_dt[3], cln_dt[4], cln_dt[5],
                                                          cln_dt[6], cln_dt[7], larva_init, pupa_init))
    thread8.start()

    # bee intrinsic
    thread9 = threading.Thread(target=init_bee_intrinsic(cln_dt[0], cln_dt[1], cln_dt[3], cln_dt[7],
                                                         larva_init, pupa_init, bee_init))
    thread9.start()
    # bee extrinsic
    thread10 = threading.Thread(target=init_bee_extrinsic(cln_dt[0], cln_dt[2], cln_dt[3], cln_dt[4], cln_dt[5],
                                                          cln_dt[6], cln_dt[7], larva_init, pupa_init, bee_init))
    thread10.start()

    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()
    thread7.join()
    thread8.join()
    thread9.join()
    thread10.join()

    intrinsic_factory.list_print_summation()
    return ex_in_array, queen_lst_indices, game_map_matrix


# using pygame to show window to usr, asking for init data
def get_parameters_from_user(text_to_show):
    X = 1760  # win size
    Y = 900
    pygame.init()
    screen = pygame.display.set_mode((X, Y))
    pygame.display.set_caption('Show Text')
    font = pygame.font.Font(None, 30)
    text = font.render(text_to_show, True, WHITE, BLUE)
    textRect = text.get_rect()
    textRect.center = (880, 350)
    input = ''
    while True:
        for evt in pygame.event.get():
            if evt.type == KEYDOWN:
                if evt.key == pygame.K_RETURN:
                    if input != "" and (input == "a" or input == "m") and "Select operation" in text_to_show:
                        block = font.render("thinking... it may take a while", True, (255, 255, 255))
                    screen.fill(BLUE)
                    screen.blit(text, textRect)
                    rect = block.get_rect()
                    rect.center = screen.get_rect().center
                    screen.blit(block, rect)
                    pygame.display.flip()
                    return input
                elif evt.key == pygame.K_BACKSPACE:
                    input = input[:-1]
                else:
                    input += evt.unicode
            elif evt.type == QUIT:
                return
        screen.fill(BLUE)
        screen.blit(text, textRect)
        block = font.render(input, True, (255, 255, 255))
        rect = block.get_rect()
        rect.center = screen.get_rect().center
        screen.blit(block, rect)
        pygame.display.flip()


def drawGrid(g_map, draw_color_stage):  # given a matrix, draw matrix on screen
    block_size = 5  # the size of a cell
    i = 0  # start from row zero
    j = 0  # start from column zero
    screen_egg_counter = 0
    screen_larva_counter = 0
    screen_pupa_counter = 0
    screen_bee_counter = 0
    screen_old_bee_counter = 0

    object_counter = np.array([0, screen_egg_counter, screen_larva_counter, screen_pupa_counter, screen_bee_counter,
                               screen_bee_counter, screen_old_bee_counter, screen_old_bee_counter,
                               screen_old_bee_counter, screen_old_bee_counter, screen_old_bee_counter,
                               screen_old_bee_counter
                                  , screen_old_bee_counter, screen_old_bee_counter, screen_old_bee_counter,
                               screen_old_bee_counter])

    for y in range(2, WINDOW_HEIGHT - 5, block_size):
        for x in range(2, WINDOW_WIDTH - 5, block_size):
            rect = pygame.Rect(x, y, block_size, block_size)
            if 0 < g_map[i][j] < 16:
                pygame.draw.rect(SCREEN, draw_color_stage[int(g_map[i][j])], rect)
                object_counter[int(g_map[i][j])] += 1
            else:
                pygame.draw.rect(SCREEN, BLACK, rect)

            j = j + 1  # next column
        j = 0  # return to the start of the column
        i = i + 1  # next line

    pygame.font.init()  # you have to call this at the start, if you want to use this module.
    my_font = pygame.font.SysFont('Comic Sans MS', 20)

    egg = my_font.render(f'Egg            - {object_counter[1]}', False, RED)
    larva = my_font.render(f'Larva         - {object_counter[2]}', False, GREEN)
    pupa = my_font.render(f'Pupa           - {object_counter[3]}', False, BLUE)
    adult_bees_5_6 = my_font.render(f'Adult bees - {object_counter[4] + object_counter[5]}', False, ORANGE)
    older_bees = my_font.render(f'Older bees - {sum(object_counter[6:])}', False, LAVENDER)

    SCREEN.blit(egg, (5, 0))
    SCREEN.blit(larva, (5, 26))
    SCREEN.blit(pupa, (5, 52))
    SCREEN.blit(adult_bees_5_6, (5, 78))
    SCREEN.blit(older_bees, (5, 104))


if __name__ == "__main__":

    # define params for visualize:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    WINDOW_HEIGHT = 900
    WINDOW_WIDTH = 1760
    RED = (200, 10, 10)  # egg
    GREEN = (0, 175, 0)  # larva
    BLUE = (0, 102, 255)  # pupa
    ORANGE = (255, 174, 66)  # adult bees 5-6
    LAVENDER = (230, 230, 250)  # older bees

    # default init colony params value:
    egg_num = 50000
    larva_num = 50000
    pupa_num = 50000
    bee_num = 50000

    while True:
        choice = get_parameters_from_user('Eggs, Larva, Pupa and Bee init to 50K each.'
                                          ' Would you like to use default parameters? (y/n)')
        choice = choice.lower()
        if choice == 'n':
            egg_num = abs(int(get_parameters_from_user('Overall colony number should be from 30 to 10M, Please choose'
                                                       ' from 0 and up, how many eggs the game would start with')))
            larva_num = abs(int(
                get_parameters_from_user('Please choose how many larvas the game would start with')))
            pupa_num = abs(int(
                get_parameters_from_user('Please choose how many pupas the game would start with')))
            bee_num = abs(
                int(get_parameters_from_user('Please choose how many bees the game would start with')))
            if 10000000 > egg_num + larva_num + pupa_num + bee_num > 29:
                break
        if choice == 'y':
            break

    auto_movement = get_parameters_from_user('Select operation mode: a - auto, m - single step with mouse left click '
                                             '(a/m)')
    auto_movement = auto_movement.lower()
    if auto_movement == "a":
        auto_movement = True
    else:
        auto_movement = False

    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()

    #  sum to generate the random, and chose how many queens to develop (up to 20)
    colony_init_num = egg_num + larva_num + pupa_num + bee_num

    # bee type options:
    bee_type_options = ["FW", "MW"]  # Female Worker, Male Worker
    # check how many queens are appropriate to develop
    if colony_init_num > 1000:
        bees_variation = [random.choice(bee_type_options) for _ in range(colony_init_num - 20)]
        bees_variation += ["FQ" for i in range(20)]
    elif 29 < colony_init_num <= 1000:
        bees_variation = [random.choice(bee_type_options) for _ in range(colony_init_num - 3)]
        bees_variation += ["FQ" for i in range(3)]

    random.shuffle(bees_variation)  # shuffling queens positions, relevant to factory init creation

    # checking init factory types per class
    egg_num_factory_types = set(bees_variation[0:egg_num])
    larva_num_factory_types = set(bees_variation[egg_num: egg_num + larva_num])
    pupa_num_factory_types = set(bees_variation[egg_num + larva_num: egg_num + larva_num + pupa_num])
    bee_num_factory_types = set(
        bees_variation[egg_num + larva_num + pupa_num: egg_num + larva_num + pupa_num + bee_num])

    # prepare input args to factory initiation
    lst_set_classes_types = [egg_num_factory_types, larva_num_factory_types, pupa_num_factory_types,
                             bee_num_factory_types]
    classes_names = ["Egg", "Larva", "Pupa", "Bee"]

    # init factory object:
    intrinsic_data_factory = Bee_lifeCycle_Factory(lst_set_classes_types, classes_names)

    """ # Factory usage example:
    a = intrinsic_data_factory.get_class_instance("FQ", "Egg")  # Reusing existing class instance/creating new instance
    b = intrinsic_data_factory.get_class_instance("MQ", "Bee")  # Wrong type
    
    # showing all intrinsic "saved" classes in init:
    intrinsic_data_factory.list_classes()
    """

    # init game data, starting with creation of extrinsic data per intrinsic object, apply to intrinsic_extrinsic_arr
    # save queen indices, update map to show colony objects coordinates
    intrinsic_extrinsic_arr, queens_indices, game_map = \
        create_init_intrinsic_and_extrinsic_data(intrinsic_data_factory,
                                                 bees_variation,
                                                 egg_num,
                                                 larva_num,
                                                 pupa_num,
                                                 bee_num,
                                                 colony_init_num)

    game = Bees_Game(intrinsic_extrinsic_arr, queens_indices, game_map, colony_init_num, intrinsic_data_factory)

    print("Starting the game")

    generations = 50  # to terminate the game

    # pseudo restarting thread that run the game once per showing update on screen. Threads couldn't be restarted
    uniq_threads_name = []
    for i in range(generations):
        uniq_threads_name.append(uuid.uuid4().hex[:6].upper())

    uniq_threads_name[generations - 1] = threading.Thread(target=game.run_the_game())
    uniq_threads_name[generations - 1].start()

    # using to chose color per object stage according to cell index
    draw_stage = np.array([BLACK, RED, GREEN, BLUE, ORANGE, ORANGE, LAVENDER, LAVENDER, LAVENDER, LAVENDER,
                           LAVENDER, LAVENDER, LAVENDER, LAVENDER, LAVENDER, LAVENDER])  # stage color util array
    finish = False
    while not finish:
        drawGrid(game_map, draw_stage)  # draw map
        for event in pygame.event.get():  # find if window close button is pressed
            if event.type == pygame.QUIT:
                finish = True
        pygame.display.update()

        if not auto_movement:
            pressed = False  # using mouse press to move step
            while not pressed:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pressed = True

        uniq_threads_name[generations - 1].join()
        pygame.display.update()
        generations -= 1
        uniq_threads_name[generations - 1] = threading.Thread(target=game.run_the_game())
        uniq_threads_name[generations - 1].start()

        print("gen num in main:", generations)
        if generations == 0:
            print("50 generations is up, time to finish")
            finish = True

    # todo consider add listener to temperature change...
    # todo add singleton to game class, and to factory class
    # todo add threads, even at printing with factory print counter, and inside run the game, and at move function
    # todo clean code, utility.py, classes.py shorten code using threads pool and more...
    # todo thread for queen bee movement with printing any object action it see after moving
    # todo queen functionality could be much more interesting as been writen
