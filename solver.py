import os
import time
from collections import deque
T = 1
F = 0
UNASSIGN = -1

class SATSolver:
    def __init__(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"No such file or directory: '{file_path}'")
        self.file_path = file_path
        self.clauses, self.variables = self.parse_cnf(file_path)
        self.assignments = {var: UNASSIGN for var in self.variables}
        self.implication_graph = {var: ImplicationNode(var, UNASSIGN) for var in self.variables}
        self.decision_level, self.decision_count = 0, 0
        self.decision_vars, self.learned_clauses = set(), set()
        self.decision_history, self.propagation_history = {}, {}

    def execute(self):
        start_time = time.time()
        is_satisfiable = self.solve()
        elapsed_time = time.time() - start_time
        result = ' '.join(['{}{}'.format('' if val == 1 else '-', var) for var, val in self.assignments.items()])
        return {
            'file': self.file_path,
            'satisfiable': "SAT" if is_satisfiable else "UNSAT",
            'time': elapsed_time,
            'assignment': result,
            'decisions': self.decision_count,
            'r_value': self.r_value
        }

    def preprocess(self):
        pass

    # def solve(self):
    #     self.preprocess()
    #     while not self.all_vars_assigned():
    #         conflict_clause = self.unit_propagation()
    #         if conflict_clause is not None:
    #             learned_clause, backtrack_level = self.analyze_conflict(conflict_clause)
    #             if backtrack_level < 0:
    #                 return False
    #             self.learned_clauses.add(learned_clause)
    #             self.backtrack(backtrack_level)
    #             self.decision_level = backtrack_level
    #         elif self.all_vars_assigned():
    #             break
    #         else:
    #             self.decision_count += 1
    #             self.decision_level += 1
    #             decision_val, decision_var = self.select_decision_variable()
    #             self.decision_vars.add(decision_var)
    #             self.decision_history[self.decision_level], self.assignments[decision_var], self.propagation_history[self.decision_level] = decision_var, decision_val, deque()
    #             self.update_implication_graph(decision_var)
    #     return True
    def solve(self):
        self.preprocess()

        while True:
            if self.all_vars_assigned():
                break
            
            conflict_clause = self.unit_propagation()
            if conflict_clause is not None:
                learned_clause, backtrack_level = self.analyze_conflict(conflict_clause)
                if backtrack_level < 0:
                    return False
                self.learned_clauses.add(learned_clause)
                self.backtrack(backtrack_level)
                self.decision_level = backtrack_level
            else:
                self.decision_count += 1
                self.decision_level += 1
                decision_val, decision_var = self.select_decision_variable()
                self.decision_vars.add(decision_var)
                self.decision_history[self.decision_level] = decision_var
                self.assignments[decision_var] = decision_val
                self.propagation_history[self.decision_level] = deque()
                self.update_implication_graph(decision_var)

        return True


    def pick_branching_variable(self):
        for var in self.variables:
            if self.assignments[var] == UNASSIGN:
                return var, T
                
    def parse_cnf(self, file_path):
        with open(file_path) as file:
            lines = [ line.strip().split() for line in file.readlines() if not (line.startswith('c') or line.startswith('%') or line.startswith('0')) and line != '\n']

        if lines[0][:2] == ['p', 'cnf']:
            num_literals, num_clauses = map(int, lines[0][-2:])
            self.r_value = num_clauses/num_literals
        else:
            raise OSError('Invalid CNF file format.')

        literals, clauses = set(), set()
        for line in lines[1:]:
            if line[-1] != '0':
                raise OSError('Each clause line must end with 0.')
            clause = frozenset(map(int, line[:-1]))
            literals.update(map(abs, clause))
            clauses.add(clause)

        return clauses, literals

    def evaluate_literal(self, literal):
        value = self.assignments[abs(literal)]
        return value if value == UNASSIGN else value ^ (literal < 0)

    def evaluate_clause(self, clause):
        if not clause:
            return T
        values = list(map(self.evaluate_literal, clause))
        return UNASSIGN if UNASSIGN in values else max(values)

    def evaluate_cnf(self):
        return min(map(self.evaluate_clause, self.clauses))


    def is_unit_clause(self, clause):
        unassigned_literals = [literal for literal in clause if self.evaluate_literal(literal) == UNASSIGN]
        assigned_count = sum(1 for literal in clause if self.evaluate_literal(literal) == F)

        is_unit = (len(unassigned_literals) == 1 and assigned_count == len(clause) - 1) or \
                (len(clause) == 1 and len(unassigned_literals) == 1)

        return is_unit, unassigned_literals[0] if is_unit else None


    def update_implication_graph(self, var, clause=None):
        node = self.implication_graph[var]
        node.value, node.level = self.assignments[var], self.decision_level

        if clause:
            node.parents.extend(self.implication_graph[abs(lit)] for lit in clause if abs(lit) != var)
            [self.implication_graph[abs(lit)].children.append(node) for lit in clause if abs(lit) != var]
            node.clause = clause

    def unit_propagation(self):
        while True:
            propagation_queue = deque()
            clauses_to_evaluate = self.clauses.union(self.learned_clauses)
            for clause in clauses_to_evaluate:
                clause_value = self.evaluate_clause(clause)
                if clause_value == F:
                    return clause 
                elif clause_value == UNASSIGN:
                    is_unit, unit_literal = self.is_unit_clause(clause)
                    if is_unit:
                        propagation_queue.append((clause, unit_literal))

            if not propagation_queue:
                return None 
            for clause, prop_literal in propagation_queue:
                prop_var = abs(prop_literal)
                self.assignments[prop_var] = T if prop_literal > 0 else F
                self.update_implication_graph(prop_var, clause=clause)
                if self.decision_level in self.propagation_history:
                    self.propagation_history[self.decision_level].append(prop_literal)
                else:
                    self.propagation_history[self.decision_level] = deque([prop_literal])

    
    def all_vars_assigned(self):
        return all(var in self.assignments for var in self.variables) and \
               not any(var for var in self.variables if self.assignments[var] == UNASSIGN)
    
    def select_decision_variable(self):
        var = next(self.unassigned_vars())
        return T, var
    
    def unassigned_vars(self):
        unassigned = []
        for var in self.variables:
            if var in self.assignments and self.assignments[var] == UNASSIGN:
                unassigned.append(var)
        return iter(unassigned)

    
    def get_unit_clauses(self):
        return list(filter(lambda x: x[0], map(self.is_unit_clause, self.clauses)))


    def analyze_conflict(self, conflict_clause):
        def latest_assigned_var(clause):
            for var in reversed(assign_history):
                if -var in clause or var in clause:
                    lst = []
                    for x in clause:
                        if abs(x) != abs(var):
                            lst.append(x)
                    return var, lst

        if self.decision_level == 0:
            return -1, None

        assign_history = [self.decision_history[self.decision_level]] + list(self.propagation_history[self.decision_level])
        pool_literals, processed_literals, current_level_literals, previous_level_literals = conflict_clause, set(), set(), set()
        while True:
            for lit in pool_literals:
                if self.decision_level == self.implication_graph[abs(lit)].level:
                    current_level_literals.add(lit)
                else:
                    previous_level_literals.add(lit)

            if len(current_level_literals) == 1:
                break

            last_assigned, others = latest_assigned_var(current_level_literals)
            current_level_literals = set(others)

            pool_clause = self.implication_graph[abs(last_assigned)].clause
            processed_literals.add(abs(last_assigned))
            pool_literals = [l for l in pool_clause if abs(l) not in processed_literals] if pool_clause else []
        
        backtrack_level = max([self.implication_graph[abs(x)].level for x in previous_level_literals]) if previous_level_literals else self.decision_level - 1
        learned_clause = frozenset(current_level_literals.union(previous_level_literals))
        
        return learned_clause, backtrack_level
    
    def backtrack(self, level):
        for _, node in self.implication_graph.items():
            if node.level <= level:
                new_children = []
                for child in node.children:
                    if child.level <= level:
                        new_children.append(child)
                node.children[:] = new_children
            else:
                node.value = UNASSIGN
                node.level, node.parents, node.children , node.clause = -1, [], [], None
                self.assignments[node.variable] = UNASSIGN


        for var in self.variables:
            if self.assignments[var] != UNASSIGN and not self.implication_graph[var].parents:
                self.decision_vars.add(var)

        for k in list(self.propagation_history.keys()):
            if k > level:
                del self.decision_history[k]
                del self.propagation_history[k]

class ImplicationNode:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value
        self.level = -1
        self.parents, self.children, self.clause = [], [], None

    def all_parents(self):
        parents = set(self.parents)
        for parent in self.parents:
            parents.update(parent.all_parents())
        return list(parents)
