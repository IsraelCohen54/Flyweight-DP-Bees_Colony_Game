# Flyweight-Design-pattern-Bees_Colony_Game
Implementing Flyweight DP to play with hundred thousands of objects simultaneously (or more with a bit more investment) with Pygame library. <br>
The DP main idea, is to point to shared memory for many objects, instead of creating it in memory for each. <br>
Hence, the DP contain extrinsix - data uniqe to specific object, e.g. like coordinates, and intrinsic, e.g. it's class type X with input Z, which is generic and had many more such X(Z) class objects that pointing to the same object in memory.
In addition, Flyweight DP has Factory class that return instance of class if already exist in database (e.g. from dictionary) or create a new one, add it to factory, and return pointer to it.

Threads usage are pretty much a must.
