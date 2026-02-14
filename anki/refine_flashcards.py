
import json
import re
import os

INPUT_FILE = "consolidated_commands.json"
OUTPUT_FILE = "finetuned_flashcards.json"

# Knowledge Base: (Regex Pattern, Section, Question, Notes)
# Tuple: (Pattern, Syllabus Section, Question Template, Notes Template)
# Capture groups in regex can be used in templates if needed (complex), but we keep it simple for now.

KNOWLEDGE_BASE = [
    # --- Cluster Architecture ---
    (r"etcdctl.*snapshot save", "Cluster Architecture, Installation & Configuration", 
     "How do you backup the etcd cluster data?", 
     "Use 'etcdctl snapshot save <path>'. \nEssential flags: --cacert, --cert, --key, --endpoints. \nRun this on the control plane node."),
    (r"etcdctl.*snapshot restore", "Cluster Architecture, Installation & Configuration",
     "How do you restore an etcd cluster from a snapshot?", 
     "Use 'etcdctl snapshot restore <path> --data-dir <new-dir>'. \nAfter restore, update the etcd static pod manifest 'hostPath' to point to the new data directory."),
     (r"etcdctl.*endpoint health", "Cluster Architecture, Installation & Configuration",
     "How do you check the health of etcd cluster members?",
     "Use 'etcdctl endpoint health'. \nRequires the same TLS certificate flags as other commands to authenticate with the members."),
    (r"kubeadm upgrade plan", "Cluster Architecture, Installation & Configuration",
     "How do you check available versions before upgrading a cluster?",
     "Run 'kubeadm upgrade plan'. \nIt checks the current version and lists available upgrades for the control plane components."),
    (r"kubeadm upgrade apply", "Cluster Architecture, Installation & Configuration",
     "How do you apply a specific version upgrade to the control plane?",
     "Run 'kubeadm upgrade apply <version>'. \nThis upgrades the API Server, Controller Manager, and Scheduler on the control plane node."),
     (r"kubeadm.*token create", "Cluster Architecture, Installation & Configuration",
     "How do you generate a new join token for worker nodes?",
     "Use 'kubeadm token create --print-join-command'. \nGenerates the full 'kubeadm join' command with the token and CA hash needed for a worker to join."),
     (r"kubectl.*drain", "Cluster Architecture, Installation & Configuration",
     "How do you safely remove all workloads from a node for maintenance?",
     "Use 'kubectl drain <node> --ignore-daemonsets'. \nCordons the node and evicts pods. --ignore-daemonsets is required for system pods."),
     (r"kubectl.*uncordon", "Cluster Architecture, Installation & Configuration",
     "How do you make a node schedulable again after maintenance?",
     "Use 'kubectl uncordon <node>'. \nRemoves the SchedulingDisabled taint so new pods can be placed on the node."),
     
    # --- Workloads & Scheduling ---
    (r"kubectl run.*--image=.*--restart=Never", "Workloads & Scheduling",
     "How do you imperatively create a single Pod?",
     "Use 'kubectl run <name> --image=<imgRef> --restart=Never'. \nGreat for quick tests or debugging tools. Add '--dry-run=client -o yaml' to generate a manifest."),
    (r"kubectl run.*--image=.*-o yaml", "Workloads & Scheduling",
     "How do you generate a Pod YAML without creating it?",
     "Use 'kubectl run <name> --image=<imgRef> --dry-run=client -o yaml'. \nStandard way to create a template manifest during the exam."),
    (r"kubectl create deployment.*--replicas", "Workloads & Scheduling",
     "How do you imperatively create a Deployment with specific replicas?",
     "Use 'kubectl create deployment <name> --image=<imgRef> --replicas=<N>'. \nFastest way to spin up a stateless application."),
    (r"kubectl scale deployment", "Workloads & Scheduling",
     "How do you scale an existing deployment?",
     "Use 'kubectl scale deployment <name> --replicas=<N>'. \nImmediate imperative scaling. For declarative scaling, edit the YAML spec.replicas field."),
    (r"kubectl set image deployment", "Workloads & Scheduling",
     "How do you update the image of a running deployment?",
     "Use 'kubectl set image deployment/<name> <container>=<new-image>'. \nTriggers a rolling update. Monitor with 'kubectl rollout status'."),
    (r"kubectl rollout undo", "Workloads & Scheduling",
     "How do you rollback a deployment to the previous version?",
     "Use 'kubectl rollout undo deployment/<name>'. \nReverts to the revision immediately preceding the current one. Use '--to-revision' for specific versions."),
    (r"kubectl.*taint nodes.*NoSchedule", "Workloads & Scheduling",
     "How do you taint a node to restrict scheduling?",
     "Use 'kubectl taint nodes <node> key=value:NoSchedule'. \nOnly pods with a matching toleration can be scheduled on this node."),
    (r"kubectl label nodes", "Workloads & Scheduling",
     "How do you add a label to a node?",
     "Use 'kubectl label nodes <node> <key>=<value>'. \nLabels are used by nodeSelectors and Affinity rules to control pod placement."),
     
    # --- Services & Networking ---
    (r"kubectl expose deployment.*--port", "Services & Networking",
     "How do you expose a deployment as a Service?",
     "Use 'kubectl expose deployment <name> --port=<svc-port> --target-port=<pod-port>'. \nCreates a ClusterIP by default. Use '--type=NodePort' for external node access."),
    (r"kubectl get services", "Services & Networking",
     "How do you list Services and their ClusterIP/Ports?",
     "Use 'kubectl get services'. \nShows the Service type (ClusterIP/NodePort) and the exposed ports."),
    (r"kubectl get ingress", "Services & Networking",
     "How do you list Ingress resources?",
     "Use 'kubectl get ingress'. \nShows the host rules and backend services associated with ingress routing."),
    (r"kubectl get netpol", "Services & Networking",
     "How do you list Network Policies?",
     "Use 'kubectl get netpol'. \nNetwork policies control traffic flow between pods. Default is usually allow-all unless restricted."),
    (r"kubectl run.*busybox.*nslookup", "Services & Networking",
     "How do you debug DNS resolution from within the cluster?",
     "Use 'kubectl run tmp --image=busybox:1.28 --rm -it -- nslookup <target>'. \nTest if a pod can resolve a service name or an external domain."),
     
    # --- Storage ---
    (r"kubectl get pv ", "Storage",
     "How do you list Persistent Volumes?",
     "Use 'kubectl get pv'. \nShows available volumes, capacity, and status (Available/Bound). Sort by capacity with '--sort-by=.spec.capacity.storage'."),
    (r"kubectl get pvc", "Storage",
     "How do you list Persistent Volume Claims?",
     "Use 'kubectl get pvc'. \nShows which claims are bound to which volumes. A 'Pending' status often indicates no matching PV is available."),
    (r"kubectl describe pvc", "Storage",
     "How do you debug a PVC stuck in Pending state?",
     "Use 'kubectl describe pvc <name>'. \nCheck the 'Events' section. Common causes: No default storage class, size mismatch, or selector mismatch."),
     
     # --- Troubleshooting ---
    (r"kubectl logs.*-p|--previous", "Troubleshooting",
     "How do you check logs for a crashed/restarted container?",
     "Use 'kubectl logs <pod> --previous'. \nShows the stdout/stderr of the last crashed instance. Critical for debugging CrashLoopBackOff."),
    (r"kubectl logs.*-c ", "Troubleshooting",
     "How do you get logs from a specific container in a multi-container pod?",
     "Use 'kubectl logs <pod> -c <container>'. \nRequired when a pod has a sidecar or init-container."),
    (r"kubectl top node", "Troubleshooting",
     "How do you check node resource usage (CPU/Mem)?",
     "Use 'kubectl top node'. \nRequires metrics-server. Identifies nodes under pressure or with high load."),
    (r"kubectl top pod", "Troubleshooting",
     "How do you check pod resource usage?",
     "Use 'kubectl top pod'. \nUseful to find 'noisy neighbors' consuming excessive CPU/Memory."),
    (r"kubectl auth can-i", "Troubleshooting",
     "How do you check RBAC permissions for a user?",
     "Use 'kubectl auth can-i <verb> <resource> --as <user>'. \nVerifies if a specific user is authorized to perform an action."),
    (r"journalctl -u kubelet", "Troubleshooting",
     "How do you inspect Kubelet logs on a node?",
     "Use 'journalctl -u kubelet'. \nThe Kubelet is a systemd service, so its logs are in the journal, not in kubectl. Essential for debugging 'NotReady' nodes."),
    (r"crictl ps", "Troubleshooting",
     "How do you check running containers directly on the runtime level?",
     "Use 'crictl ps'. \nBypasses the Kubelet API. Useful if the Kubelet is frozen or stopped to see what containers are actually running."),
     
     # --- Helm & Kustomize ---
    (r"helm repo add", "Helm & Kustomize",
     "How do you register a new Helm chart repository?",
     "Use 'helm repo add <name> <url>'. \nAdds the upstream chart source. Follow with 'helm repo update'."),
    (r"helm install", "Helm & Kustomize",
     "How do you deploy a Helm chart?",
     "Use 'helm install <release-name> <chart>'. \nDeploys the application defined in the chart. Use '--set key=val' to override configuration."),
    (r"helm list", "Helm & Kustomize",
     "How do you view installed Helm releases?",
     "Use 'helm list -A'. \nShows deployed charts across all namespaces, including their revision and status."),
    (r"helm uninstall", "Helm & Kustomize",
     "How do you delete a Helm release?",
     "Use 'helm uninstall <name>'. \nRemoves all Kubernetes resources associated with the release."),
    (r"kubectl kustomize", "Helm & Kustomize",
     "How do you render a Kustomize overlay to stdout?",
     "Use 'kubectl kustomize <dir>'. \nBuilds the final manifest from the base and overlay without applying it."),
    (r"kubectl apply -k", "Helm & Kustomize",
     "How do you apply a Kustomize configuration?",
     "Use 'kubectl apply -k <dir>'. \nBuilds and applies the kustomization.yaml found in the directory."),
     
     # --- Misc / RBAC ---
     (r"kubectl create role ", "Cluster Architecture, Installation & Configuration",
      "How do you imperative create a Role?",
      "Use 'kubectl create role <name> --verb=<verbs> --resource=<res>'. \nNamespace-scoped permissions."),
     (r"kubectl create clusterrole ", "Cluster Architecture, Installation & Configuration",
      "How do you imperative create a ClusterRole?",
      "Use 'kubectl create clusterrole <name> --verb=<verbs> --resource=<res>'. \nCluster-wide permissions."),
      (r"kubectl create serviceaccount", "Cluster Architecture, Installation & Configuration",
      "How do you create a ServiceAccount?",
      "Use 'kubectl create serviceaccount <name>'. \nIdentity for Pods to talk to the API Server."),
]

def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def match_knowledge_base(cmd, kb):
    for pattern, section, question, notes in kb:
        if re.search(pattern, cmd, re.IGNORECASE):
            return section, question, notes
    return None, None, None

def refine_flashcards():
    raw_cards = load_data(INPUT_FILE)
    if not raw_cards:
        return

    finetuned = []
    seen_intents = set()
    
    # Priority: Knowledge Base matches first
    # We loop through raw cards. If a card matches a KB pattern:
    # Check if we already have this KB pattern (Intent) in our finetuned list.
    # If NO, add the Best Version (from KB) and mark intent as seen.
    # If YES, skip (Deduplication).
    
    # However, raw_cards might carry specific useful command flags not in KB.
    # But user wants "One unique card". So KB version is preferred as canonical.
    
    for item in raw_cards:
        cmd_raw = item["command"]
        
        # 1. Check against Knowledge Base
        section, kb_q, kb_n = match_knowledge_base(cmd_raw, KNOWLEDGE_BASE)
        
        if section:
            # Identifier for the intent is the Question (since KB questions are unique per concept)
            intent_id = kb_q
            
            if intent_id not in seen_intents:
                finetuned.append({
                    "section": section,
                    "question": kb_q,
                    "command": cmd_raw, # We keep the specific command example from source or we could use a canonical one?
                                        # User asked "rephrase question... check existing notes".
                                        # Let's use the command from the source as the 'Answer' but if there are multiple,
                                        # we pick the first one matching the intent.
                    "notes": kb_n
                })
                seen_intents.add(intent_id)
            else:
                # If we already have this intent, maybe this command is slightly different?
                # User wants to remove duplicates. 'kubectl get pods' vs 'kubectl get pods -n dev' -> same intent.
                pass
        else:
            # Command didn't match KB. It might be generic.
            # We add it, but we need to ensure it's not "similar" to others.
            # This is the "tail" of the distribution.
            
            # Heuristic dedupe: verb + resource
            # e.g. "kubectl create configmap"
            
            # Only add if it looks unique enough?
            # Or assume KB covers 80% coverage and include the rest with generic logic?
            # Let's include with generic logic but try to basic dedupe.
            
            parts = cmd_raw.split()
            if len(parts) > 2:
               key = f"{parts[0]}-{parts[1]}" # kubectl-create
               if key not in seen_intents: # Very loose dedupe
                   # But this might be too aggressive. kubectl create deployment != kubectl create secret
                   pass
            
            # Simple approach for specific non-kb items:
            # Just clean them up.
            finetuned.append({
                "section": "Miscellaneous", # Will be fixed by categorized or manual map
                "question": item.get("question", f"Run: {cmd_raw[:20]}..."),
                "command": cmd_raw,
                "notes": item.get("notes", "Refer to documentation.")
            })
            
    # Now, the 'tail' (non-KB) might be messy. The User complained about "duplicates or similar".
    # By strictly using the KB for the vast majority of 'standard' commands, we filter out noise.
    # But we might lose some niche commands not in KB.
    # Given the user's focus on "Section" grouping, let's try to map the tails to sections.
    
    # Improve: Iterate KB entries and find the best match in raw_cards for the 'command' field if we want to be dynamic,
    # OR just use the KB entries as the Golden Source of truth? 
    # The user said "Read all flashcards... Identify duplicates... Keep one unique...".
    # This implies we must source the command strings from the files.
    
    # Revised Loop:
    # 1. Create a map of KB_Index -> List of Matching Raw Commands.
    # 2. For each KB index, pick the 'best' command string (probably longest or most descriptive).
    # 3. Create the card.
    
    kb_matches = {i: [] for i in range(len(KNOWLEDGE_BASE))}
    unmatched = []
    
    for item in raw_cards:
        cmd = item["command"]
        matched_idx = -1
        for i, (pattern, _, _, _) in enumerate(KNOWLEDGE_BASE):
             if re.search(pattern, cmd, re.IGNORECASE):
                 matched_idx = i
                 break
        
        if matched_idx >= 0:
            kb_matches[matched_idx].append(cmd)
        else:
            unmatched.append(item)
            
    final_output = []
    
    # Process KB Matches
    for i, cmds in kb_matches.items():
        if not cmds: continue
        # We have at least one command matching this intent.
        # Pick the most representative.
        # Heuristic: Pick the one that closely matches the pattern but isn't too long/short.
        # Actually, let's just pick the first one, or the one with flags?
        # Let's picking the longest one often gives 'kubectl ... --dry-run ...' which is good for CKA.
        best_cmd = max(cmds, key=len)
        
        pattern, section, question, notes = KNOWLEDGE_BASE[i]
        final_output.append({
            "section": section,
            "question": question,
            "command": best_cmd,
            "notes": notes
        })
        
    print(f"Processed {len(final_output)} unique cards from Knowledge Base.")
    print(f"Remaining unmatched cards: {len(unmatched)}")
    
    # Process Unmatched - try to salvage good ones
    # Filter out trash or very similar ones
    for item in unmatched:
        # If it's a known resource type but missed regex?
        # e.g. "kubectl top pods" (maybe matched regex 'top pod' but we had 'top node')
        # We'll skip for now to ensure quality (User wants duplicates removed).
        # OR: We add them to "Miscellaneous" section if they look like valid commands.
        
        if "kubectl" in item["command"] or "docker" in item["command"]:
             # Quick dedupe by question text similarity?
             final_output.append({
                 "section": "Miscellaneous",
                 "question": item["question"],
                 "command": item["command"],
                 "notes": item["notes"]
             })
             
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2)
        
    print(f"Saved {len(final_output)} cards to {OUTPUT_FILE}")

if __name__ == "__main__":
    refine_flashcards()
