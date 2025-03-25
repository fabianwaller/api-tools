import sys
import json
import math
import re
import os
from generate_random_orders import create_orders

print ("Loading domains..."),
sys.stdout.flush()

import planning_domains_api as api

suites = []
domains_in_suite = []

BOUND = 0.25

# 12 is the collection for all STRIPS IPC domains
domains = {}
collection_id = 12
for dom in api.get_domains(collection_id, "classical"):
    # get a single domain
    #dom = api.get_domain(52, "classical")

    # print(json.dumps(dom, indent=4))

    # Turn the links into relative paths for this machine
    probs = api.get_problems(dom['domain_id'], "classical")

    # Map the domain name to the list of domain-problem pairs
    domains[dom['domain_name']] = []
    for p in probs:
        domains[dom['domain_name']].append((p['domain_path'], p['problem_path'], p['lower_bound']))

for dom in domains:
    print(dom)
    for i in range(len(domains[dom]) - 1):
        domain = domains[dom][i][0]
        problem = domains[dom][i][1]
        lower_bound = domains[dom][i][2]
        # print("----------------")
        # print("domain", domain)
        # print("problem", problem)

        try:
            with open(problem, 'r', encoding='utf-8') as file:
                content = file.read()
                goal_match = re.search(r'\(:goal\s+\(AND(.*?)\)\s*\)', content, re.DOTALL | re.IGNORECASE)
                if not goal_match:
                    goal_match = re.search(r'\(:goal\s+(.*?)\s*\)', content, re.DOTALL | re.IGNORECASE)
                if not goal_match:
                    raise ValueError(f"No goal section found in problem file: {problem}")

                else:
                    goal_content = goal_match.group(1)
                    goal_content += ")"
                    # print(goal_content)
                    # find all expressions in parentheses that don't contain nested parentheses
                    goal_predicates = re.findall(r'\([^()]+\)', goal_content)


                    problem_dir = os.path.dirname(problem)
                    problem_base = os.path.basename(problem)
                    problem_name = os.path.splitext(problem_base)[0]

                    if lower_bound is None:
                        print(f"Skipping problem {problem_name} without lower bound")
                        continue
                    if len(goal_predicates) <= 1:
                        print(f"Skipping problem {problem_name} with {len(goal_predicates)} goals")
                        continue

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
                    all_partial_orders = create_orders(goals)

                    for i in range(len(all_partial_orders)):
                        partial_order = all_partial_orders[i]
                        preferences = {
                            "partial_order": partial_order
                        }

                        if len(goals) != 1 and partial_order == []:
                            raise ValueError(f"No partial order generated")

                        #print(json.dumps(preferences, indent=4))
                        
                        preferences_file = os.path.join(problem_dir, f"{problem_name}-preferences-{i}.json")
                        
                        with open(preferences_file, 'w') as file:
                            json.dump(preferences, file, indent=2)

                        # print(f"Created {preferences_file} with partial order constraints")

                    domain_name = os.path.basename(problem_dir)
                    problem_filename = os.path.basename(problem)
                    rounded_lower_bound = math.ceil(BOUND * lower_bound)
                    suites.append(f"{domain_name}:{problem_filename}:{rounded_lower_bound}")
                    domains_in_suite.append(domain_name)
        except FileNotFoundError:
            print("The specified file does not exist.")
        except IOError:
            print("An error occurred while reading the file.")

suites = sorted(list(set(suites)))
print("\nDone! Generated preferences for the following problems:")
print(suites)
print(f"Total number of problems: {len(suites)}")

output_file = "domains_in_suite.txt"
with open(output_file, 'w') as f:
    f.write(f"{sorted(list(set(domains_in_suite)))}\n")
print(f"\nWrote used domains to {output_file}")


output_file = "suite.txt"
with open(output_file, 'w') as f:
    for instance in suites:
        f.write(f"{instance}\n")
print(f"\nWrote suites to {output_file}")
