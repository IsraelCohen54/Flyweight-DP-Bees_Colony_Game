"""
checking runtime of dictionary vs array.
I have thought about using dictionary to check for Move function if Key exist (coordinate, dictionary inside dictionary)
, a bee can't move there otherwise it can, but deleting and creating new key after each move as it would seem is
more costly than appending the array to extend it, and changing extrinsic data in array (same index), and apply
change to map (with dictionary I theoretically could hold exactly the key without a need to check in map,
in array I need to run over extrinsic, than check in map, hence in memory usage, arrays are probably worse,
but in runtime it would probably be faster)
"""
import random
from dataclasses import dataclass
import numpy as np
import time

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~  dictionary  ~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #
from scipy.stats import truncnorm

start_timer = time.perf_counter()
myDict = {x: x for x in range(10000000)}
end_timer = time.perf_counter()
sum_dictionary_time = end_timer - start_timer
print("dictionary creation 0-10000000, key(=val):  ", sum_dictionary_time)

start_timer = time.perf_counter()
for i in range(10000000, 20000000):
    myDict[i] = i

end_timer = time.perf_counter()
sum_dictionary_time += end_timer - start_timer
print("    dictionary adding 10000000 keys(=val):  ", end_timer - start_timer)

start_timer = time.perf_counter()
for key in range(10000000):
    # myDict.pop(key, None) # worse...
    del myDict[key]
end_timer = time.perf_counter()
sum_dictionary_time += end_timer - start_timer
print("          dictionary delete 10000000 keys:  ", end_timer - start_timer)
print("                  overall dictionary time: ~", sum_dictionary_time, "~\n")

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~~   array   ~~~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #

start_timer = time.perf_counter()
np_array = np.arange(10000000)
end_timer = time.perf_counter()
sum_array_time = end_timer - start_timer
print("np.arange(10000000), increasing val from 0-10M:  ", sum_array_time)

start_timer = time.perf_counter()
lst = [x for x in range(10000000, 20000000)]
end_timer = time.perf_counter()
sum_array_time += end_timer - start_timer
print("  creating list lst(10-20)M, then add to array:  ", end_timer - start_timer)

start_timer = time.perf_counter()
np_array = np.append(np_array, lst)
end_timer = time.perf_counter()
sum_array_time += end_timer - start_timer
print("                        np array appending lst:  ", end_timer - start_timer)

start_timer = time.perf_counter()
np_array = np.delete(np_array, lst)
end_timer = time.perf_counter()
sum_array_time += end_timer - start_timer
print("      np array deleting lst indices from array:  ", end_timer - start_timer)
print("                            overall array time: ~", sum_array_time, "~")

print("\n                        sleep 10 sec, check out results...\n\n")
time.sleep(10)

print("         ~~~      ~~~         ~~~         ~~~      ~~~")
print("               another check with class as input")
print("         ~~~      ~~~         ~~~         ~~~      ~~~")


@dataclass(frozen=True)  # Immutable, intrinsic data
class Bee:
    bee_type: str  # 3 options

    def eat(self, growth: int) -> float:  # return growth stage
        match growth:
            case 4:
                print(f"a young adult {self.bee_type} emerging from the hexagonal-shaped egg cell,"
                      " by chewing its way through the wax capping.")
                return 5  # todo point/create to older bee with same type
            case 5:
                if self.bee_type == "FQ":
                    print("Behold! The queen are eating a royal jelly!")
                    # todo check stage+type to use "lay_eggs"(if not winter currently), save index,
                    #  kill other queens if not old (last in index, should be easy... as it before laying eggs)
                    #  return older new queen pointer
                    #  if queen old - no eggs, stop killing, grow new queens
                    return 66  # apply 6 to growth, kill other queens todo
                print("a bee is eating a nectar or a pollen")
                return 6  # apply to growth extrinsic factor

            # death chance grow with the bee, calculated outside with more extrinsic data # todo
            # if growth higher than 6: (case _: is default, so it can get e.g. 0, but by program logic it shouldn't).
            case _:
                if growth < 15:
                    return 0.1 * growth + growth  # apply to extrinsic growth
                return 15  # bee dies, if a bee queen, dev more queens. todo

    # todo add functionality to bee female and bee male, meybe by move, let x eat...
    def bee_defend_queen_by_sting_attacker(self, growth: int) -> float:  # todo consider delete
        if self.bee_type != "FQ" and growth < 10:
            return growth + 0.5  # todo add to growth higher chance to die next "cycle"
            # todo change growth/growth_rate to age.


#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~  dictionary  ~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #
start_timer = time.perf_counter()
myDict = {x: {x: Bee(random.choice(['FW', 'MW']))} for x in range(100000)}
end_timer = time.perf_counter()
sum_dictionary_time = end_timer - start_timer
print("\ncoordinates nested dictionary creation len 100000,\n inner dict val=Bee(random.choice([\'FW\', \'MW\'])): ",
      sum_dictionary_time)
time.sleep(10)

start_timer = time.perf_counter()
for x, y in myDict.items():
    # print("coordinate x, y:", x, " ", y)
    for key in y:
        # print("y val:", y[key])
        y[key].eat(4)
end_timer = time.perf_counter()
sum_dictionary_time += end_timer - start_timer
print("\nusing a bee class method to print using dictionary:  ", end_timer - start_timer)

print("                           overall dictionary time: ~", sum_dictionary_time, "~\n")
print("\n                   sleep 10 sec, check out results...")
time.sleep(10)

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~~   array   ~~~~~~~~~~~~~~~~~  #
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #

start_timer = time.perf_counter()
# np_array = np.array([Bee(np.random["FW,MW"]), for coordinate in range(10)])
num_columns = 2
num_rows = 100000
np_array = np.array([[(Bee(random.choice(['FW', 'MW']))) if i == 1 else i for i in range(num_columns)]
                     for j in range(num_rows)])

end_timer = time.perf_counter()
sum_array_time = end_timer - start_timer
print("2d np array, sec place hold bee class: ", sum_array_time)

start_timer = time.perf_counter()
for i in np_array:
    i[1].eat(4)
end_timer = time.perf_counter()
sum_array_time += end_timer - start_timer
print("\nlooping through a 2d np array, and using a bee class method:  ", end_timer - start_timer)

print("                                         overall array time: ~", sum_array_time, "~")
print("\nConclusion: np array perform better, and at the last test np.arr held more data space to allow extrinsic data"
      " as well as intrinsic class. \nMoreover, dictionary would probably fare worse than np array,"
      " with the deletion and addition of keys to dict using move function vs checking 2d np array indices.")

print("another little test as I'm curious :), np.array VS np.empty_like:")
start_timer = time.perf_counter()
k = np.array([[i for i in range(2)] for j in range(num_rows)], dtype=object)
end_timer = time.perf_counter()
print("\nnp.array      creation time: ", end_timer - start_timer)
start_timer = time.perf_counter()
k = np.empty_like([[i for i in range(2)] for j in range(num_rows)], dtype=object)
end_timer = time.perf_counter()
print("np.empty_like creation time: ", end_timer - start_timer)
print("result: np.array Win! a little bit faster.\n")

print("another important test for choosing inheritance and overridden any unneeded method vs 'if' instance class type:")


# inheritance:
# preparing classes:
@dataclass(frozen=True)  # Immutable, intrinsic data
class Egg:
    type: str  # types are: FW, FQ, MW. Female/Male + Worker/Queen (no MQ as a male bee cannot be a Queen).

    # "cracking shell" probability get higher with higher growth value
    # return growth progress
    def cracking_shell(self, growth: int):
        print("crack")
        cracking_success_result = np.random.randint(0.1, high=1, size=None, dtype=int) * growth
        if cracking_success_result > 2:
            return 2  # success, apply result to extrinsic growth, and change intrinsic type to Larva #todo
        return cracking_success_result + growth  # apply res, next time chance would be higher # todo

    def breath_through_the_shell(self) -> None:  # todo consider delete
        print(f"A {self.type} currently processing oxygen")

    def growing_fast(self, growth: float):
        pass


@dataclass(frozen=True)  # Immutable, intrinsic data
class Larva(Egg):  # pythonic inheritance

    # override:
    def cracking_shell(self, growth: float):
        pass  # do nothing

    def breath_through_the_shell(self) -> None:
        pass

    # return growth progress
    def growing_fast(self, growth: int):
        self.eating()
        growth_by = np.random.randint(0.1, high=1, size=None, dtype=int) * growth
        if growth_by > 3:
            return 3  # change intrinsic to Pupa, apply to growth extrinsic val #todo
        return growth_by + growth

    def eating(self) -> None:
        match self.type:
            case "FQ":
                print("Behold! The larva, a future potential queen, are eating a royal jelly!")
            case "FW":
                print("a female worker is eating a worker jelly")
            case "MW":
                print("a male worker is eating a drone jelly")
            case _:
                print("wrong naming! <(#_*)> check out what happened")


# data holder:
x = np.array([Egg("FW"), Egg("FW"), Egg("FW"), Egg("FW"), Larva("FW"), Larva("FW"), Larva("FW"), Larva("FW")])

start_timer = time.perf_counter()  # as I'm trying to avoid using if statement as much as I can, I do all functions
for i in x:
    i.cracking_shell(0)
    i.breath_through_the_shell()
    i.growing_fast(2)
end_timer = time.perf_counter()
print("\nusing all functions: ", end_timer - start_timer)
start_timer = time.perf_counter()
for i in x:
    match type(i).__name__:
        case "Egg":
            i.cracking_shell(0), i.breath_through_the_shell()
        case "Larva":
            i.growing_fast(2)
        case _:
            print("wrong naming! <(#_*)> check out what happened")
end_timer = time.perf_counter()
print("using switch case statement to check class type: ", end_timer - start_timer)
print("result: switch case Win by 2 whole orders!!! a big win, hence I would work with it instead of inheritance and"
      "saying as well that if i dont want to check any type to use function, then I need a class to hold all functions"
      " then using pass notation to do nothing in the wring class, which doesn't sound correct programmatically"
      "I might consider using inheritance + switch case. ")  # todo

print("curios check :) sum 4 numbers with + or sum function")
egg_num = 9999999
larva_num = 12345678
pupa_num = 8472957
bee_num = 919144488
start_timer = time.perf_counter()
colony_init_num = egg_num + larva_num + pupa_num + bee_num
end_timer = time.perf_counter()
print("\nusing + instead of built in sum function: ", end_timer - start_timer)

start_timer = time.perf_counter()
colony_init_num = sum([egg_num, larva_num, pupa_num, bee_num])
end_timer = time.perf_counter()
print("\nusing built in sum function (over list of same data): ", end_timer - start_timer)
print("Gryffindor win! ;) '+' win by one order.")

print("\nRandom function comparison, truncated_normal VS random.uniform:")


def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


start_timer = time.perf_counter()
temperature_resistance = get_truncated_normal(mean=5, sd=1, low=1, upp=9).rvs()
end_timer = time.perf_counter()
print("truncated_normal: ", end_timer - start_timer)

start_timer = time.perf_counter()
health = np.random.uniform(low=0.1, high=10)
end_timer = time.perf_counter()
print("random.uniform: ", end_timer - start_timer)
# todo, read line below!
print("random.uniform super fast(e-06) VS 0.001, consider using it instead of truncated! ", end_timer - start_timer)

print("\ncurious check, does irrelevant arguments (size & dtype, which is optional as it return the very same val in my"
      "case, as I work with default values...) change runtime")
# actually, default val is int, so it should be same and in prog it should be without anyway if wishing for int as val
start_timer = time.perf_counter()
for i in range(100):  # avg...
    cracking_success_result = np.random.randint(0.1, high=1, size=None, dtype=int)
end_timer = time.perf_counter()
a = end_timer - start_timer

start_timer = time.perf_counter()
for i in range(100):
    cracking_success_result = np.random.randint(0.1, high=1)
end_timer = time.perf_counter()
b = end_timer - start_timer

start_timer = time.perf_counter()
for i in range(100):
    cracking_success_result = np.random.randint(0.1, 1, size=None)
end_timer = time.perf_counter()
c = end_timer - start_timer

start_timer = time.perf_counter()
for i in range(100):
    cracking_success_result = np.random.randint(0.1, 1, dtype=int)
end_timer = time.perf_counter()
d = end_timer - start_timer

print(a, "random with dtype=int (which is default val) and size=None")
print(b, "random without dtype val and without size arg")
print(c, "random without dtype val and with size arg")
print(d, "random with dtype val and without size arg")
print("min val:", min(a, b, c, d), "max val:", max(a, b, c, d))
print("res: without the 2 unneeded arguments, it is actually faster (tested many times). other 3 options isn't clear,"
      " probably with size=None arg without dtype is in general a little bit better, but negligible..."
      "anyway, good to know.")

print("\n float random check, with round 2.f or without:")

start_timer = time.perf_counter()
round(random.uniform(0.1, 1), 2)
end_timer = time.perf_counter()
print("with round 2.f: ", end_timer - start_timer)
aa = end_timer - start_timer

start_timer = time.perf_counter()
random.uniform(0.1, 1)
end_timer = time.perf_counter()
print("without round 2.f: ", end_timer - start_timer)
bb = end_timer - start_timer
print(f"winner is: {max(aa, bb)}")
