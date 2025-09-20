"""
Multi-Objective Genetics Optimization Engine
Implements NSGA-II for virtue-weighted genetic variant + therapy optimization
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class OptimizationVariable:
    """Single optimization variable (TF level, therapy dose, etc.)"""
    name: str
    current_value: float
    min_value: float
    max_value: float
    variable_type: str  # continuous, discrete, binary

@dataclass
class OptimizationObjective:
    """Single optimization objective"""
    name: str
    objective_type: str  # minimize, maximize
    weight: float
    current_value: float

@dataclass
class OptimizationConstraint:
    """Hard constraint on system behavior"""
    name: str
    constraint_type: str  # <=, >=, ==
    limit_value: float
    current_value: float
    violation: float

class GeneticsOptimizer:
    """NSGA-II multi-objective optimizer for genetics + therapeutics"""
    
    def __init__(self, population_size: int = 100, generations: int = 50):
        self.population_size = population_size
        self.generations = generations
        self.variables = []
        self.objectives = []
        self.constraints = []
        
    def add_variable(self, variable: OptimizationVariable):
        """Add optimization variable"""
        self.variables.append(variable)
        
    def add_objective(self, objective: OptimizationObjective):
        """Add optimization objective"""
        self.objectives.append(objective)
        
    def add_constraint(self, constraint: OptimizationConstraint):
        """Add hard constraint"""
        self.constraints.append(constraint)
        
    def evaluate_individual(self, individual: np.ndarray) -> Tuple[List[float], List[float]]:
        """Evaluate objectives and constraints for one individual"""
        
        objectives = []
        constraint_violations = []
        
        # Example objectives (would integrate with genetics simulation):
        # 1. Task error (protein folding fidelity)
        fidelity = np.random.uniform(0.5, 0.95)  # Simulate based on individual
        objectives.append(1.0 - fidelity)  # Minimize error
        
        # 2. Energy cost (ATP consumption)
        energy_cost = np.sum(individual) * 0.1  # Simple cost model
        objectives.append(energy_cost)
        
        # 3. Overload risk (proteostasis capacity)
        overload_risk = max(0, np.sum(individual) - 5.0) * 0.2
        objectives.append(overload_risk)
        
        # 4. DNA damage (oxidative stress)
        dna_damage = np.sum(individual ** 2) * 0.05
        objectives.append(dna_damage)
        
        # 5. Policy complexity (regulatory program size)
        complexity = len([x for x in individual if x > 0.1])
        objectives.append(complexity)
        
        # Constraint violations
        for i, var in enumerate(self.variables):
            if individual[i] < var.min_value:
                constraint_violations.append(var.min_value - individual[i])
            elif individual[i] > var.max_value:
                constraint_violations.append(individual[i] - var.max_value)
            else:
                constraint_violations.append(0.0)
        
        return objectives, constraint_violations
        
    def run_optimization(self) -> List[Dict[str, Any]]:
        """Run NSGA-II optimization and return Pareto front"""
        
        # Initialize population
        population = self._initialize_population()
        
        for generation in range(self.generations):
            # Evaluate population
            objectives_list = []
            violations_list = []
            
            for individual in population:
                obj, viol = self.evaluate_individual(individual)
                objectives_list.append(obj)
                violations_list.append(viol)
            
            # Non-dominated sorting
            fronts = self._non_dominated_sort(objectives_list, violations_list)
            
            # Crowding distance
            if fronts and len(fronts[0]) > 0:
                crowding_distances = self._calculate_crowding_distance(fronts[0], objectives_list)
            else:
                crowding_distances = [1.0] * len(population)
            
            # Selection, crossover, mutation
            population = self._evolve_population(population, fronts, crowding_distances)
        
        # Return Pareto-optimal solutions
        return self._extract_pareto_solutions(population, objectives_list, violations_list)
        
    def _initialize_population(self) -> np.ndarray:
        """Initialize random population"""
        population = []
        
        for _ in range(self.population_size):
            individual = []
            for var in self.variables:
                value = np.random.uniform(var.min_value, var.max_value)
                individual.append(value)
            population.append(np.array(individual))
        
        return population
        
    def _non_dominated_sort(self, objectives: List[List[float]], 
                          violations: List[List[float]]) -> List[List[int]]:
        """Implement non-dominated sorting for NSGA-II"""
        
        n = len(objectives)
        fronts = []
        
        # Calculate domination
        domination_count = [0] * n
        dominated_solutions = [[] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    if self._dominates(objectives[i], objectives[j], violations[i], violations[j]):
                        dominated_solutions[i].append(j)
                    elif self._dominates(objectives[j], objectives[i], violations[j], violations[i]):
                        domination_count[i] += 1
        
        # First front
        first_front = [i for i in range(n) if domination_count[i] == 0]
        fronts.append(first_front)
        
        # Subsequent fronts
        while len(fronts[-1]) > 0:
            next_front = []
            for i in fronts[-1]:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)
            if next_front:
                fronts.append(next_front)
            else:
                break
        
        return fronts[:-1] if not fronts[-1] else fronts
        
    def _dominates(self, obj1: List[float], obj2: List[float], 
                  viol1: List[float], viol2: List[float]) -> bool:
        """Check if solution 1 dominates solution 2"""
        
        # Constraint violation check
        total_viol1 = sum(viol1)
        total_viol2 = sum(viol2)
        
        if total_viol1 < total_viol2:
            return True
        elif total_viol1 > total_viol2:
            return False
        
        # Objective comparison (minimization)
        at_least_one_better = False
        for o1, o2 in zip(obj1, obj2):
            if o1 > o2:
                return False
            if o1 < o2:
                at_least_one_better = True
        
        return at_least_one_better
        
    def _calculate_crowding_distance(self, front: List[int], 
                                   objectives: List[List[float]]) -> List[float]:
        """Calculate crowding distance for diversity preservation"""
        
        if len(front) <= 2:
            return [float('inf')] * len(front)
        
        distances = [0.0] * len(front)
        num_objectives = len(objectives[0]) if objectives else 1
        
        for m in range(num_objectives):
            # Sort by objective m
            front_sorted = sorted(front, key=lambda x: objectives[x][m])
            
            # Boundary points have infinite distance
            distances[front.index(front_sorted[0])] = float('inf')
            distances[front.index(front_sorted[-1])] = float('inf')
            
            # Calculate distances for intermediate points
            obj_range = objectives[front_sorted[-1]][m] - objectives[front_sorted[0]][m]
            if obj_range > 0:
                for i in range(1, len(front_sorted) - 1):
                    idx = front.index(front_sorted[i])
                    if distances[idx] != float('inf'):
                        distance = (objectives[front_sorted[i+1]][m] - 
                                  objectives[front_sorted[i-1]][m]) / obj_range
                        distances[idx] += distance
        
        return distances
        
    def _evolve_population(self, population: List[np.ndarray], 
                          fronts: List[List[int]], 
                          crowding_distances: List[float]) -> List[np.ndarray]:
        """Evolve population using selection, crossover, and mutation"""
        
        # Simple evolution - in practice would implement proper NSGA-II operators
        new_population = []
        
        # Keep best solutions from first front
        if fronts and len(fronts[0]) > 0:
            for idx in fronts[0][:self.population_size//2]:
                if idx < len(population):
                    new_population.append(population[idx].copy())
        
        # Generate new solutions
        while len(new_population) < self.population_size:
            # Simple random generation (would implement crossover/mutation)
            individual = []
            for var in self.variables:
                value = np.random.uniform(var.min_value, var.max_value)
                individual.append(value)
            new_population.append(np.array(individual))
        
        return new_population[:self.population_size]
        
    def _extract_pareto_solutions(self, population: List[np.ndarray], 
                                objectives: List[List[float]], 
                                violations: List[List[float]]) -> List[Dict[str, Any]]:
        """Extract Pareto-optimal solutions"""
        
        solutions = []
        
        for i, individual in enumerate(population):
            if i < len(objectives):
                solution = {
                    'variables': individual.tolist(),
                    'objectives': objectives[i],
                    'violations': violations[i],
                    'total_violation': sum(violations[i]),
                    'weighted_objective': sum(objectives[i])
                }
                solutions.append(solution)
        
        # Sort by weighted objective
        solutions.sort(key=lambda x: x['weighted_objective'])
        
        return solutions
