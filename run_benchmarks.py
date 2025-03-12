import sys
import json
import os
import re
import subprocess
import planning_domains_api as api

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def extract_search_time(output):
    search_time_match = re.search(r'Search time: (\d+\.\d+)s', output)
    if search_time_match:
        return float(search_time_match.group(1))
    return None

def extract_mugs(output):
    mugs_count_match = re.search(r'#MUGS: (\d+)', output)
    if not mugs_count_match:
        return None
    
    mugs_count = int(mugs_count_match.group(1))
    atoms_match = re.search(r'\*+\n((?:Atom[^\n]*\n)+)', output)
    
    result = {
        'count': mugs_count,
        'atoms': []
    }
        
    if atoms_match:
        atoms_text = atoms_match.group(1).strip()
        atoms_lines = atoms_text.split('\n')
        result['atoms'] = [line.strip() for line in atoms_lines if line.strip()]
    
    result['mugs'] = []
    for i in range(len(result['atoms'])):
        result['mugs'].append({
            'atoms': result['atoms'][i]
        })
    
    return result

def run_problem(command):
    print(command)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            shell=True
        )
        
        if result.returncode != 0:
            print(f"Return code: {result.returncode}")
            print("Error occurred:")
            print(result.stderr)
        else:
            # print(f"Command executed successfully (Code {result.returncode})")
            # print(result.stdout)
            search_time = extract_search_time(result.stdout)
            if search_time:
                print(bcolors.OKGREEN + f"Search time: {search_time}s" + bcolors.ENDC)
            else:
                print("Search time not found in output")

            mugs = extract_mugs(result.stdout)
            if mugs:
                print(f"Found {mugs['count']} MUGs:")
                # for i, mugs in enumerate(mugs_info['mugs'], 1):
                #     print(mugs['atoms'])
            else:
                print("No MUGSs found in output")
    
    except Exception as e:
        print(f"Failed to execute command: {e}")
    

print("Loading domains...")
sys.stdout.flush()

# Path to fast-downward.py
FAST_DOWNWARD_PATH = "/Users/fabianwaller/Developer/symbolic-xaip/fast-downward.py"

# 12 is the collection for all STRIPS IPC domains
domains = {}
# print(json.dumps(api.get_collections("classical"), indent=4))
# get all domains
for dom in api.get_domains(9, "classical"):
    # print(json.dumps(dom, indent=4))
    print(dom["domain_name"])
# Get a single domain
# dom = api.get_domain(50, "classical") # visitall
# dom = api.get_domain(12, "classical")
    domain_id = dom['domain_id']
    domain_name = dom['domain_name']
    domain_description = dom['description']

    print(f"Processing domain: {domain_name} (ID: {domain_id})")
    print(domain_description)

    # Turn the links into relative paths for this machine
    probs = api.get_problems(domain_id, "classical")

    # Map the domain name to the list of domain-problem pairs
    domains[domain_name] = []
    for p in probs:
        domains[domain_name].append((p['domain_path'], p['problem_path'], p['lower_bound']))

    # Iterate through each domain-problem pair
    tests_per_domain = 1
    tests_count = 0
    for domain_path, problem_path, lower_bound in domains[domain_name]:
        print("=" * 60)
        print(f"Running fast-downward for:")
        print(f"Domain: {domain_path}")
        print(f"Problem: {problem_path}")
        
        bounds = [0.25, 0.5, 0.75]

        for bound in bounds:
            normal = f"{FAST_DOWNWARD_PATH} --build release64 {domain_path} {problem_path} --search \"sfw(non_stop=true, bound={bound * lower_bound}, all_soft_goals=true, quickxplain=false)\""
            run_problem(normal)    

            # Extract base filename without extension
            problem_base_path = os.path.splitext(problem_path)[0]

            for i in range(5):
                preferences_path = f"{problem_base_path}-preferences-{i}.json"
                quick = f"{FAST_DOWNWARD_PATH} --build release64 {domain_path} {problem_path} {preferences_path} --search \"sfw(non_stop=true, bound={bound * lower_bound}, all_soft_goals=true, quickxplain=true)\""
                run_problem(quick)    
            print("-" * 15)
        print("-" * 60)


        tests_count += 1
        if(tests_count >= tests_per_domain):
            break


print("All domains processed!")


