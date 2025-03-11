import sys
import json
import re
import os

print ("Loading domains..."),
sys.stdout.flush()

import planning_domains_api as api

# 12 is the collection for all STRIPS IPC domains
domains = {}
for dom in api.get_domains(12, "classical"):
    # get a single domain
    #dom = api.get_domain(52, "classical")

    # print(json.dumps(dom, indent=4))

    # Turn the links into relative paths for this machine
    probs = api.get_problems(dom['domain_id'], "classical")

    # Map the domain name to the list of domain-problem pairs
    domains[dom['domain_name']] = []
    for p in probs:
        domains[dom['domain_name']].append((p['domain_path'], p['problem_path']))

    for dom in domains:
        for i in range(len(domains[dom]) - 1):
            domain = domains[dom][i][0]
            problem = domains[dom][i][1]
            print("----------------")
            print("domain", domain)
            print("problem", problem)

            try:
                with open(problem, 'r', encoding='utf-8') as file:
                    content = file.read()
                    #print(content)
                    goal_match = re.search(r'\(:goal\s+\(AND(.*?)\)\s*\)', content, re.DOTALL | re.IGNORECASE)
                    if not goal_match:
                        print("\nNo goal section found in the file.")
                        print(json.dumps(dom, indent=4))
                        raise ValueError(f"No goal section found in problem file: {problem}")

                    else:
                        goal_content = goal_match.group(1)
                        goal_content += ")"
                        # print(goal_content)
                        # find all expressions in parentheses that don't contain nested parentheses
                        goal_predicates = re.findall(r'\([^()]+\)', goal_content)

                        # print("\nExtracted goals:")
                        # print(goal_predicates)

                        goals = []

                        # print("\nTransformed to prefix notation:")
                        for i, pred in enumerate(goal_predicates):
                            # Remove parentheses and split by spaces
                            pred_clean = pred.strip('() ')
                            parts = pred_clean.split()
                            
                            # Get predicate name and arguments
                            if len(parts) >= 1:
                                predicate_name = parts[0]
                                arguments = parts[1:]
                                
                                prefix_notation = f"{predicate_name}({', '.join(arguments)})"
                                goals.append(prefix_notation)
                        
                        # Create partial order constraints where each item >= next item
                        partial_order = []
                        for i in range(len(goals) - 1):
                            partial_order.append([goals[i], goals[i+1]])

                        # Create the preferences structure
                        preferences = {
                            "partial_order": partial_order
                        }

                        if len(goals) != 1 and partial_order == []:
                            raise ValueError(f"No partial order generated")

                        #print(json.dumps(preferences, indent=4))

                        problem_dir = os.path.dirname(problem)
                        problem_base = os.path.basename(problem)
                        problem_name = os.path.splitext(problem_base)[0]
                        
                        preferences_file = os.path.join(problem_dir, f"{problem_name}-preferences.json")
                        
                        with open(preferences_file, 'w') as file:
                            json.dump(preferences, file, indent=2)

                        print(f"Created {preferences_file} with partial order constraints")
            except FileNotFoundError:
                print("The specified file does not exist.")
            except IOError:
                print("An error occurred while reading the file.")


        print ("done!")
