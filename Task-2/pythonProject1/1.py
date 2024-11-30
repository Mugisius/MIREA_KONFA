import subprocess
import sys
import re
import http.client

def get_dependencies(package, depth, repo_url, current_depth=0):
    if current_depth >= depth:
        return []

    try:
        conn = http.client.HTTPSConnection(repo_url.split("//")[1])  # Extract hostname
        conn.request("GET", f"/dists/stable/main/binary-amd64/Packages") # Assuming amd64 architecture
        res = conn.getresponse()
        data = res.read().decode("utf-8")
    except Exception as e:
        print(f"Error fetching package information: {e}", file=sys.stderr)
        return []

    package_info = ""
    in_package_block = False
    for line in data.splitlines():
        if line.startswith("Package: " + package):
            in_package_block = True
        elif in_package_block:
            if line.startswith("Package: "): # End of current package block
                break;
            package_info += line + "\n"


    dependencies = []
    matches = re.findall(r"Depends: ([^\n]+)", package_info)
    if matches:
        for dep_line in matches:
            for dep in dep_line.split(','):
                dep = dep.strip().split()[0] # Get package name, ignoring version
                dependencies.append(dep)



    transitive_deps = []
    for dep in dependencies:
        transitive_deps.extend(get_dependencies(dep, depth, repo_url, current_depth + 1))

    return dependencies + transitive_deps



def generate_dot(package, dependencies):
    dot = f"digraph {package} {{\n"
    dot += f'  "{package}" [shape=box];\n'  # Mark the main package
    for dep in dependencies:
      dot += f'  "{package}" -> "{dep}";\n'
    dot += "}\n"
    return dot

def main():
    if len(sys.argv) != 5:
        print("Usage: python script.py <graphviz_path> <package_name> <depth> <repo_url>", file=sys.stderr)
        sys.exit(1)

    graphviz_path = sys.argv[1]
    package = sys.argv[2]
    depth = int(sys.argv[3])
    repo_url = sys.argv[4]


    dependencies = get_dependencies(package, depth, repo_url)
    dependencies = list(set(dependencies)) # remove duplicates

    dot = generate_dot(package, dependencies)

    try:
      process = subprocess.Popen([graphviz_path, "-Tpng"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
      output, error = process.communicate(dot.encode('utf-8'))
      if error:
          print(f"Graphviz error: {error.decode('utf-8')}", file=sys.stderr)
          sys.exit(1)

      sys.stdout.buffer.write(output) # Output image to stdout

    except FileNotFoundError:
      print(f"Error: Graphviz executable not found at {graphviz_path}", file=sys.stderr)
      sys.exit(1)



if __name__ == "__main__":
    main()