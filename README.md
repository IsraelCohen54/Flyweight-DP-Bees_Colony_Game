# Flyweight-Design-pattern-Bees_Colony_Game
Implementing Flyweight DP to play with hundreds of thousands of objects simultaneously (or more with a bit more investment) with the Pygame library. <br>
The design pattern’s main idea is to point to shared memory for many objects, instead of creating it in memory for each. <br>
Hence, the DP contains extrinsic - data unique to a specific object, e.g., coordinates, and intrinsic, e.g., its class type X with input Z, which is generic and had many more such X(Z) class objects that point to the same object in memory. <br>
In addition, Flyweight DP has a Factory class that returns an instance of the class if already exists in the database (e.g. from the dictionary) or creates a new one, adds it to the factory, and returns a pointer to it.

Threads are pretty much a must.

Added file with run time complexity test for Flyweight project.
