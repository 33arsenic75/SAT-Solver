import argparse
from solver import SATSolver
from branch_heuristics import DynamicLargestIndividualSumSolver, JeroslowWangOneSidedSolver, RandomHeuristicsSolver, TwoClauseHeuristicSolver

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Choose heuristics and input file for SAT Solver.')
    parser.add_argument('--heuristics', type=str, required=True, help='Heuristics to use for the solver')
    parser.add_argument('--filename', type=str, required=True, help='Input file for the solver')
    args = parser.parse_args()

    heuristics = args.heuristics
    filename = args.filename

    if heuristics == 'DynamicLargestIndividualSumSolver':
        solver = DynamicLargestIndividualSumSolver(filename)
    elif heuristics == 'JeroslowWangOneSidedSolver':
        solver = JeroslowWangOneSidedSolver(filename)
    elif heuristics == 'RandomHeuristicsSolver':
        solver = RandomHeuristicsSolver(filename)
    elif heuristics == 'TwoClauseHeuristicSolver':
        solver = TwoClauseHeuristicSolver(filename)
    else:
        raise ValueError(f"Unknown heuristics: {heuristics}")


    answer = solver.execute()

    # print(f"File Path: {answer['file']}")
    # print(f"Satisfiability: {answer['satisfiable']}")
    # if answer['satisfiable'] == "SAT":
    #     print(f"Satisfying Assignment: {answer['assignment']}")
    
    # print(f"Time Taken: {answer['time']}")
    # print(f"Decision Count: {answer['decisions']}")
    # print(f"r_value: {answer['r_value']}")
    print(answer['satisfiable'],answer['decisions'])
