
import re
import json
import os

SOURCES = [
    "CKA Prep.txt",
    "cka-commands.txt",
    "ckad-commands.txt"
]

OUTPUT_JSON = "consolidated_commands.json"

# Heuristic: Valid command prefixes
VALID_PREFIXES = (
    "kubectl", "kubeadm", "helm", "etcdctl", "etcdutl", "docker", 
    "crictl", "systemctl", "journalctl", "openssl", "minikube", "alias"
)

def is_command(text):
    text = text.strip()
    return text.lower().startswith(VALID_PREFIXES)

def normalize_command(cmd):
    # Remove ticks, trailing commas, extra spaces
    cmd = cmd.strip()
    cmd = cmd.replace("`", "")
    cmd = cmd.rstrip(",")
    return re.sub(r'\s+', ' ', cmd).strip()

def generate_natural_question(cmd):
    # Generate a question based on the command structure
    parts = cmd.split()
    if not parts:
        return "What does this command do?"
    
    verb = parts[0] # usually tool name
    action = ""
    resource = ""
    
    if len(parts) > 1:
        action = parts[1]
    
    if len(parts) > 2:
        # heuristic for kubectl get/delete/create [resource]
        if parts[0] == "kubectl" and parts[1] in ["get", "delete", "describe", "edit", "create", "apply", "replace", "patch", "label", "annotate", "scale", "rollout", "expose", "autoscale"]:
            # kubectl get pods -> List pods
            obj = parts[2]
            
            mapping = {
                "get": "List or get details of",
                "delete": "Delete",
                "describe": "Show details of",
                "edit": "Edit",
                "create": "Create",
                "apply": "Apply configuration for",
                "replace": "Replace",
                "patch": "Patch",
                "label": "Label",
                "annotate": "Annotate",
                "scale": "Scale",
                "rollout": "Manage rollout of",
                "expose": "Expose",
                "autoscale": "Autoscale"
            }
            
            prefix = mapping.get(parts[1], parts[1].capitalize())
            return f"Command to {prefix.lower()} {obj}?"

        if parts[0] == "helm":
            if parts[1] == "install": return "Command to install a helm chart?"
            if parts[1] == "list": return "Command to list helm releases?"
            if parts[1] == "uninstall": return "Command to uninstall a helm release?"
            if parts[1] == "repo": return f"Command to manage helm repositories ({parts[2]})?"

        if parts[0] == "docker":
             return f"Docker command to {parts[1]}?"

    return f"What is the command to run: {cmd[:30]}...?"

def generate_explanation(cmd):
    # Generates a detailed 2-3 line explanation for the command
    parts = cmd.split()
    if not parts: return "Kubernetes command."
    
    verb = parts[0]
    sub_cmd = parts[1] if len(parts) > 1 else ""
    
    # Kubectl Commands
    if verb == "kubectl":
        if sub_cmd == "get":
            return ("Lists resources in the current context/namespace.\n"
                    "Use '-o wide' for more stats or '-o yaml' to export.\n"
                    "Essential for verifying the state of objects.")
        if sub_cmd == "describe":
            return ("Shows detailed status and events for a resource.\n"
                    "Use this to debug issues like Pending pods or Crashing containers.\n"
                    "Look at the 'Events' section at the bottom.")
        if sub_cmd == "logs":
            return ("Fetches logs from a container in a Pod.\n"
                    "Use '-p' for previous instance logs or '-f' to follow.\n"
                    "Vital for application debugging.")
        if sub_cmd == "run":
            return ("Imperatively creates a Pod.\n"
                    "Fastest way to spin up a single instance (vs Deployment).\n"
                    "Use '--dry-run=client -o yaml' to generate manifests quickly.")
        if sub_cmd == "create":
            if "deployment" in cmd:
                return ("Creates a Deployment to manage stateless apps.\n"
                        "Automatically manages ReplicaSets and Pods.\n"
                        "Preferred over creating bare Pods for production.")
            if "service" in cmd:
                return ("Exposes an application to the network.\n"
                        "ClusterIP is internal, NodePort is external access.\n"
                        "Ensures stable networking for dynamic pods.")
            return ("Creates a resource from the command line.\n"
                    "Useful for RBAC roles, Secrets, and ConfigMaps.\n"
                    "Faster than writing YAML from scratch for simple objects.")
        if sub_cmd == "apply":
            return ("Declaratively manages resources from a file.\n"
                    "Updates existing live resources with local file changes.\n"
                    "The standard method for GitOps workflows.")
        if sub_cmd == "delete":
             return ("Deletes resources from the cluster.\n"
                     "Use '--force --grace-period=0' for immediate removal (careful!).\n"
                     "Can delete by file (-f) or name.")
        if sub_cmd == "exec":
            return ("Executes a command inside a running container.\n"
                    "Commonly used with '-it -- /bin/sh' for interactive shell.\n"
                    "Allows direct file inspection and network testing.")
        if sub_cmd == "config":
            return ("Manages kubeconfig files (clusters, users, contexts).\n"
                    "Use 'use-context' to switch environments.\n"
                    "Crucial for multi-cluster management.")
        if sub_cmd == "drain":
            return ("Safely evicts all pods from a node for maintenance.\n"
                    "Use '--ignore-daemonsets' to proceed if DaemonSets exist.\n"
                    "Marks the node as unschedulable (cordon).")
        if sub_cmd == "uncordon":
            return ("Marks a node as schedulable again.\n"
                    "Run this after node maintenance is complete.\n"
                    "Allows the scheduler to place new pods on the node.")
        if sub_cmd == "taint":
            return ("Applies restriction logic to nodes.\n"
                    "Prevents pods from scheduling unless they tolerate the taint.\n"
                    "Format: key=value:Effect (NoSchedule, NoExecute).")
        if sub_cmd == "label":
            return ("Updates labels on a resource.\n"
                    "Labels are used for selectors by Services and Deployments.\n"
                    "Use '--overwrite' to change an existing label.")
        if sub_cmd == "rollout":
            return ("Manages Deployment rollouts.\n"
                    "Check status, history, or undo a failed update.\n"
                    "Essential for zero-downtime application updates.")
        if sub_cmd == "scale":
            return ("Updates the replica count of a controller.\n"
                    "Works for Deployments, ReplicaSets, and StatefulSets.\n"
                    "Imperative scaling; generally prefer HPA for auto-scaling.")
        if sub_cmd == "top":
            return ("Displays resource usage (CPU/Memory).\n"
                    "Requires Metrics Server to be installed.\n"
                    "Use to identify resource-heavy pods or nodes.")
        if sub_cmd == "auth":
            return ("Checks RBAC permissions.\n"
                    "Use 'can-i' to verify if a user/serviceaccount can perform actions.\n"
                    "Great for debugging 'Forbidden' errors.")
                    
    # Helm Commands
    if verb == "helm":
        if sub_cmd == "install":
            return ("Installs a chart archive.\n"
                    "Deploys packages to Kubernetes with versioning.\n"
                    "Use '--set' or '-f' to customize values.")
        if sub_cmd == "list":
             return ("Lists all releases in the current namespace.\n"
                     "Shows status (deployed/failed) and revision.\n"
                     "Use '-A' for all namespaces.")
        if sub_cmd == "repo":
             return ("Manages chart repositories.\n"
                     "'add' to register, 'update' to sync index.\n"
                     "Prerequisite for installing third-party charts.")
                     
    # Etcd Commands
    if "etcdctl" in cmd:
        return ("Command line client for etcd.\n"
                "Used for taking snapshots (backup) and restoring data.\n"
                "Requires certificate authentication paths.")
                
    # Docker Commands
    if verb == "docker":
        return ("Container runtime command.\n"
                "Used to build, push, or inspect images manually.\n"
                "Note: Kubernetes may use containerd, so crictl is often preferred on nodes.")
                
    # Default fallback
    return f"Executes: {cmd}.\nCheck official docs for flags and options.\nEnsure logical context (namespace/cluster) is correct."


def parse_cka_prep(filename):
    commands = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.split('\t')
                if len(parts) >= 2:
                    q = parts[0].strip()
                    a = normalize_command(parts[1])
                    n = parts[2].strip() if len(parts) > 2 else generate_explanation(a)
                    if not n: n = generate_explanation(a)
                    
                    # Only keep if Answer looks like a command
                    if is_command(a):
                        commands.append({
                            "command": a,
                            "question": q,
                            "notes": n,
                            "source": filename
                        })
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
    return commands

def parse_command_list(filename):
    commands = []
    current_header = ""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                # Check headers
                if line.startswith("###") or line.startswith("**"):
                    current_header = line.replace("#", "").replace("*", "").strip()
                    continue
                
                # Extract code in backticks or just lines (if formatted as list)
                matches = re.findall(r'`([^`]+)`', line)
                if matches:
                    for cmd in matches:
                        normalized = normalize_command(cmd)
                        if is_command(normalized):
                             commands.append({
                                "command": normalized,
                                "question": generate_natural_question(normalized),
                                "notes": generate_explanation(normalized),
                                "source": filename
                            })
                else:
                    # Try raw line if it starts with valid prefix
                    normalized = normalize_command(line)
                    # remove list markers if any "1. kubectl"
                    if re.match(r'^\d+\.\s+', normalized):
                         normalized = re.sub(r'^\d+\.\s+', '', normalized)
                    elif re.match(r'^[\*\-]\s+', normalized):
                         normalized = re.sub(r'^[\*\-]\s+', '', normalized)
                         
                    if is_command(normalized):
                         commands.append({
                                "command": normalized,
                                "question": generate_natural_question(normalized),
                                "notes": generate_explanation(normalized),
                                "source": filename
                            })

    except FileNotFoundError:
         print(f"Warning: {filename} not found")
    return commands


def main():
    all_commands = []
    
    # 1. Parse all files
    all_commands.extend(parse_cka_prep(SOURCES[0]))
    all_commands.extend(parse_command_list(SOURCES[1]))
    all_commands.extend(parse_command_list(SOURCES[2]))
    
    print(f"Total raw commands found: {len(all_commands)}")
    
    # 2. Deduplicate
    unique_map = {}
    
    for item in all_commands:
        cmd = item["command"]
        if cmd not in unique_map:
            unique_map[cmd] = item
        else:
            # If existing is from 'list', and new is from 'Prep', prefer Prep (better Q/N)
            # Actually, CKA Prep has manual notes, so it's valuable.
            if item["source"] == "CKA Prep.txt":
                unique_map[cmd] = item
                
    deduplicated_list = list(unique_map.values())
    print(f"Unique commands after deduplication: {len(deduplicated_list)}")
    
    # 3. Save to JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(deduplicated_list, f, indent=2)
        
    print(f"Saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
