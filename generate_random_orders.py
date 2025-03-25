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
    
    # Group goals by priority
    priority_groups = {}
    for goal, priority in priorities.items():
        if priority not in priority_groups:
            priority_groups[priority] = []
        priority_groups[priority].append(goal)
    
    sorted_priorities = sorted(priority_groups.keys())
    
    relations = []
        
    # between adjacent priority levels
    for i in range(len(sorted_priorities)-1):
        current_level = sorted_priorities[i]
        next_level = sorted_priorities[i+1]

        lower_goal = priority_groups[current_level][0]
        higher_goal = priority_groups[next_level][0]
        relations.append([lower_goal, higher_goal])
        
    # goals with same priority
    for priority in sorted_priorities:
        group = priority_groups[priority]
        if len(group) > 1:
            for i in range(len(group)):
                for j in range(len(group)):
                    if i != j:
                        relations.append([group[i], group[j]])
    
    return relations

def create_orders(goals, count = 5):
    
    result = []

    for i in range(count):
        partial_orders = create_total_order(goals)
        result.append(partial_orders)
    
    return result