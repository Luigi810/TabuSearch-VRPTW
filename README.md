# Tabu Search for VRPTW
This repository hosts the code for a Tabu Search based solution for the Solomon benchmarks of VRPTW type R1, as a project for the exam of Ricerca Operativa in Università Federico II.
The code is divided in 4 modules:
  * one for Tabu Search which is the main module,
  * a module for the implementation of the class Customers and functions to read data from a file (formatted as .txt files in this repository) and for the creation of the initial solution,
  * a module for the implementation of the 2 used objective functions f1 and f2,
  * a module for other utility functions
    
## How to execute
First you should decide which algorithm to use for the initial solution between the 3 possibilities implemented : simple_init, greedy_init and cw_modificato (a modified version of Clarke and Wright which should be improved as written in the documentation of the project in the pdf file).

After that the program should be launched as follows (Usage): 

python TabuSearchVRPTW_v1.3.py <input_file.txt> <vehicle_capacity> <#customers>

where 
 * **input_file.txt** is the name of the file containing the problem instance,
 * **vehicle_capacity** is a number defining the capacity of the vehicles of the problem instance (in Solomon Benchmarks is allways 200)
 * **#customers** is the number of customers in the problem (the project could be simply modified to get this number during the reading of the data from the problem .txt file)

