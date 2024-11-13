import operator
import random
from solver import SATSolver
TRUE = 1
FALSE = 0
UNASSIGN = -1


class RandomHeuristicsSolver(SATSolver):
    def select_decision_variable(self):
        unassigned_vars = [v for v in self.variables if self.assignments[v] == UNASSIGN]
        if not unassigned_vars:
            return None
        selected_var = random.choice(unassigned_vars)
        return random.choice([TRUE, FALSE]), selected_var
    

class TwoClauseHeuristicSolver(SATSolver):
    def preprocess(self):
        self.two_clause_count = {x: 0 for x in self.variables if self.assignments[x] == UNASSIGN}
        for clause in self.clauses:
            unassigned_vars_in_clause = [v for v in clause if self.assignments[abs(v)] == UNASSIGN]
            if len(unassigned_vars_in_clause) == 2:
                for v in unassigned_vars_in_clause:
                    self.two_clause_count[abs(v)] += 1

    def select_decision_variable(self):
        unassigned_vars = [v for v in self.variables if self.assignments[v] == UNASSIGN]
        if not unassigned_vars:
            return None
        count = {v: self.two_clause_count[v] for v in unassigned_vars}
        max_count = max(count.values(), default=0)
        if max_count == 0:
            selected_var = random.choice(unassigned_vars)
            return random.choice([TRUE, FALSE]), selected_var
        candidates = [v for v, occur in count.items() if occur == max_count]
        selected_var = random.choice(candidates)
        return random.choice([TRUE, FALSE]), selected_var

    

class DynamicLargestIndividualSumSolver(SATSolver):
    def all_unresolved_clauses(self):
        return filter(lambda c: self.evaluate_clause(c) == UNASSIGN, self.clauses)

    def select_decision_variable(self):
        v_pos = {x: 0 for x in self.variables if self.assignments[x] == UNASSIGN}
        v_neg= {x: 0 for x in self.variables if self.assignments[x] == UNASSIGN}
        for clause in self.all_unresolved_clauses():
            for v in clause:
                try:
                    if v > 0:
                        v_pos[v] += 1
                    else:
                        v_neg[abs(v)] += 1
                except KeyError:
                    pass

        pos_count = max(v_pos.items(), key=operator.itemgetter(1))
        neg_count = max(v_neg.items(), key=operator.itemgetter(1))
        if pos_count[1] > neg_count[1]:
            # print(f"DynamicLargestIndividualSumSolver picked variable: {pos_count[0]}")
            return TRUE, pos_count[0]
        else:
            # print(f"DynamicLargestIndividualSumSolver picked variable: {neg_count[0]}")
            return FALSE, neg_count[0]


class JeroslowWangOneSidedSolver(SATSolver):
    def preprocess(self):
        self.jw_scores = {x: 0 for x in self.variables}
        for clause in self.clauses:
            for v in clause:
                self.jw_scores[abs(v)] += 2 ** -len(clause)

    def select_decision_variable(self):
        unassigned_vars = filter(lambda v: self.assignments[v] == UNASSIGN, self.variables)
        best_var = max(unassigned_vars, key=lambda v: self.jw_scores[v])
        # print(f"JeroslowWangOneSidedSolver picked variable: {best_var}")
        return random.sample([TRUE, FALSE], 1)[0], best_var
