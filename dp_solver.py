import sys
import time
from collections import Counter

def read_cnf(filename):
    clauses = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('c') or line.startswith('p') or not line.strip():
                continue
            literals = list(map(int, line.strip().split()))
            if literals[-1] == 0:
                literals.pop()
            clauses.append(set(literals))
    return clauses

def get_variables(clauses):
    return set(abs(lit) for clause in clauses for lit in clause)

def has_unit_clause(clauses):
    return any(len(c) == 1 for c in clauses)

def has_pure_literal(clauses):
    counter = Counter(lit for clause in clauses for lit in clause)
    for lit in counter:
        if -lit not in counter:
            return True
    return False

def eliminate_unit_clauses(clauses, assignment):
    changed = True
    while changed:
        changed = False
        unit_clauses = [next(iter(c)) for c in clauses if len(c) == 1]
        for unit in unit_clauses:
            var = abs(unit)
            val = unit > 0
            if var in assignment:
                if assignment[var] != val:
                    return None  # conflict
                continue
            assignment[var] = val
            new_clauses = []
            for clause in clauses:
                if unit in clause:
                    continue  #  satisfied
                if -unit in clause:
                    new_clause = clause - {-unit}
                    if not new_clause:
                        return None  # conflict
                    new_clauses.append(new_clause)
                else:
                    new_clauses.append(clause)
            clauses = new_clauses
            changed = True
    return clauses

def eliminate_pure_literals(clauses, assignment):
    counter = Counter(lit for clause in clauses for lit in clause)
    assigned = set()
    for lit in counter:
        if -lit not in counter:
            var = abs(lit)
            val = lit > 0
            if var not in assignment:
                assignment[var] = val
                assigned.add(lit)

    if not assigned:
        return clauses

    new_clauses = []
    for clause in clauses:
        if clause & assigned:
            continue  # clause is satisfied
        new_clauses.append(clause)
    return new_clauses

def resolve(ci, cj, var):
    res_clauses = set()
    for li in ci:
        if abs(li) == var:
            for lj in cj:
                if abs(lj) == var and li != lj:
                    new_clause = (ci - {li}) | (cj - {lj})
                    if not any(-lit in new_clause for lit in new_clause):
                        res_clauses.add(frozenset(new_clause))
    return res_clauses

def dp_algorithm(clauses):
    clauses = [set(clause) for clause in clauses]
    assignment = {}
    steps = 0

    # Aplică UCE doar dacă există clauze unitare
    if has_unit_clause(clauses):
        clauses = eliminate_unit_clauses(clauses, assignment)
        if clauses is None:
            return "UNSAT", steps

    # Aplică PLE doar dacă există literali puri
    if has_pure_literal(clauses):
        clauses = eliminate_pure_literals(clauses, assignment)

    clauses = set(frozenset(c) for c in clauses)
    vars = get_variables(clauses)

    for var in vars:
        if var in assignment:
            continue
        steps += 1
        pos = {c for c in clauses if var in c}
        neg = {c for c in clauses if -var in c}

        new_clauses = set()
        for ci in pos:
            for cj in neg:
                resolvents = resolve(ci, cj, var)
                new_clauses.update(resolvents)

        clauses = clauses - pos - neg
        clauses.update(new_clauses)

        if frozenset() in clauses:
            return "UNSAT", steps

        if not clauses:
            return "SAT", steps

    return "UNKNOWN", steps

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dp_solver.py input.cnf")
        sys.exit(1)

    input_file = sys.argv[1]
    clauses = read_cnf(input_file)

    start_time = time.perf_counter()
result, steps = dp_algorithm(clauses)
end_time = time.perf_counter()

print(f"Rezultat: {result}")
print(f"Număr de variabile alese (pași): {steps}")
print(f"Timp de execuție: {end_time - start_time:.6f} secunde")
