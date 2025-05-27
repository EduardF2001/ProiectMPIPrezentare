import time
from collections import defaultdict

class DPLLSolver:
    def __init__(self, cnf):
        self.original_cnf = cnf
        self.decisions = 0
        self.conflicts = 0

    def solve(self):
        self.start_time = time.perf_counter()
        result = self.dpll(self.original_cnf[:], {})
        elapsed = time.perf_counter() - self.start_time
        return {
            "satisfiable": result is not False,
            "assignment": result if result else {},
            "decisions": self.decisions,
            "conflicts": self.conflicts,
            "time": elapsed
        }

    def dpll(self, cnf, assignment):
        cnf = self.unit_propagation(cnf, assignment)
        if cnf is False:
            self.conflicts += 1
            return False

        cnf = self.pure_literal_elimination(cnf, assignment)
        if cnf is False:
            self.conflicts += 1
            return False
        if not cnf:
            return assignment

        var = self.select_unassigned_variable(cnf, assignment)
        self.decisions += 1
        for value in [True, False]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            simplified = self.simplify(cnf, var, value)
            result = self.dpll(simplified, new_assignment)
            if result is not False:
                return result

        self.conflicts += 1
        return False

    def unit_propagation(self, cnf, assignment):
        changed = True
        while changed:
            changed = False
            unit_clauses = [c for c in cnf if len(c) == 1]
            for unit in unit_clauses:
                lit = unit[0]
                var = abs(lit)
                val = lit > 0
                if var in assignment:
                    if assignment[var] != val:
                        return False
                    continue
                assignment[var] = val
                cnf = self.simplify(cnf, var, val)
                if cnf is False:
                    return False
                changed = True
        return cnf

    def pure_literal_elimination(self, cnf, assignment):
        literal_counts = defaultdict(int)
        for clause in cnf:
            for lit in clause:
                literal_counts[lit] += 1

        assigned = set()
        for lit in literal_counts:
            var = abs(lit)
            if var in assignment or var in assigned:
                continue
            if -lit not in literal_counts:
                assignment[var] = lit > 0
                assigned.add(var)
                cnf = self.simplify(cnf, var, lit > 0)
                if cnf is False:
                    return False
        return cnf

    def simplify(self, cnf, var, value):
        new_cnf = []
        for clause in cnf:
            if (value and var in clause) or (not value and -var in clause):
                continue
            new_clause = [l for l in clause if l != -var and l != var]
            if not new_clause:
                return False
            new_cnf.append(new_clause)
        return new_cnf

    def select_unassigned_variable(self, cnf, assignment):
        for clause in cnf:
            for literal in clause:
                var = abs(literal)
                if var not in assignment:
                    return var
        return None

def read_dimacs(filename):
    cnf = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('p') or line.startswith('c') or line.strip() == '':
                continue
            clause = list(map(int, line.strip().split()))
            if clause[-1] == 0:
                clause = clause[:-1]
            cnf.append(clause)
    return cnf

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]

    cnf = read_dimacs(filename)
    solver = DPLLSolver(cnf)
    result = solver.solve()

    print("Satisfiable:", result["satisfiable"])
    print("Assignment:", result["assignment"])
    print("Decisions:", result["decisions"])
    print("Conflicts:", result["conflicts"])
    print(f"Time taken (s): {result['time']:.6f}")
