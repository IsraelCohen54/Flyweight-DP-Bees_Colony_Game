# Flyweight-Design-pattern-Bees_Colony_Game
Implementing Flyweight DP to play with hundred thousands of objects simultaneously (or more with a bit more investment) with Pygame library
The DP point is to point to shared memory for many objects, instead of creating it in memory for each. Hence, The DP contain extrinsix - data uniqe to specific object, e.g. like coordinates, and intrinsic, e.g. it's class type X with input Z, which is generic and had many more such X(Z) class objects that any point to the same.
Factory that return instance of class if already exist in database (e.g. from dictionary) or create a new one, add it to factory, and return pointer to it.
