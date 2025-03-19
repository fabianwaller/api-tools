import random
import copy

def create_total_order(goals):
    """
    Creates a random total order of goals.
    """
    if not goals or len(goals) <= 1:
        return []
    
    # Randomly assign priorities
    priority_levels = random.randint(1, len(goals))
    priorities = {}
    
    for goal in goals:
        priorities[goal] = random.randint(0, priority_levels-1)
    
    relations = []
    for i in range(len(goals)):
        for j in range(len(goals)):
            if i == j:
                relations.append([goals[i], goals[j]])
                relations.append([goals[j], goals[i]])
            elif i != j and priorities[goals[i]] < priorities[goals[j]]:
                relations.append([goals[i], goals[j]])
    
    return relations

def create_orders(goals):
    
    result = []

    for i in range(3):
        partial_orders = create_total_order(goals)
        result.append(partial_orders)
    
    return result