import pandas as pd
import numpy as np
import networkx as nx

def build_transaction_graph(df_tx: pd.DataFrame) -> nx.DiGraph:
    """
    Constructs a multi-attributed directed graph where each edge contains:
    - frequency: number of transactions
    - total_amount: sum of transaction amounts
    - mean_amount: average transaction amount
    - amount_variance: standard deviation of amounts
    - timestamps: list of transaction epoch timestamps
    - time_velocity: mean inter-arrival time in hours
    - reciprocal_amount_ratio (RAR): min(A_ij, A_ji) / max(A_ij, A_ji)
    """
    G = nx.DiGraph()
    
    # First pass: aggregate edge transactions
    edge_txs = {}
    for _, row in df_tx.iterrows():
        src = str(row['vendor_id'])
        dst = str(row['counterparty_id'])
        amt = float(row['amount'])
        ts = pd.to_datetime(row['timestamp']).timestamp() if 'timestamp' in row else 0.0
        
        edge_key = (src, dst)
        if edge_key not in edge_txs:
            edge_txs[edge_key] = {'amounts': [], 'timestamps': []}
        edge_txs[edge_key]['amounts'].append(amt)
        edge_txs[edge_key]['timestamps'].append(ts)
        
    # Populate edges with multi-attributed features
    for (src, dst), data in edge_txs.items():
        amts = np.array(data['amounts'])
        timestamps = sorted(data['timestamps'])
        
        freq = len(amts)
        tot_amt = float(np.sum(amts))
        mean_amt = float(np.mean(amts))
        amt_var = float(np.std(amts)) if freq > 1 else 0.0
        
        # Time velocity: mean delta between consecutive transactions (in hours)
        if freq > 1 and timestamps[-1] > timestamps[0]:
            deltas_hr = np.diff(timestamps) / 3600.0
            time_velocity = float(np.mean(deltas_hr))
        else:
            time_velocity = 24.0
            
        G.add_edge(
            src, dst,
            weight=tot_amt,
            total_amount=tot_amt,
            frequency=freq,
            count=freq,
            mean_amount=round(mean_amt, 2),
            amount_variance=round(amt_var, 2),
            time_velocity=round(time_velocity, 2),
            reciprocal_amount_ratio=0.0
        )
        
    # Second pass: compute reciprocal amount ratio (RAR)
    for u, v in list(G.edges()):
        if G.has_edge(v, u):
            amt_uv = G[u][v]['total_amount']
            amt_vu = G[v][u]['total_amount']
            max_amt = max(amt_uv, amt_vu)
            rar = float(min(amt_uv, amt_vu) / max_amt) if max_amt > 0 else 0.0
            G[u][v]['reciprocal_amount_ratio'] = round(rar, 4)
            G[v][u]['reciprocal_amount_ratio'] = round(rar, 4)
            
    return G

def analyze_vendor_graph(G: nx.DiGraph, vendor_id: str, rar_threshold: float = 0.50) -> dict:
    """
    Performs multi-attributed cycle search and collusion detection for a vendor.
    Searches for cycles in the subgraph of edges meeting RAR > rar_threshold.
    """
    if not G.has_node(vendor_id):
        return {
            'has_cycles': False,
            'cycle_count': 0,
            'cycles': [],
            'reciprocal_count': 0,
            'max_rar': 0.0,
            'collusion_cycles': [],
            'graph_evidence': []
        }
        
    evidence = []
    cycles_found = []
    collusion_cycles = []
    max_rar = 0.0
    reciprocal_nodes = []
    
    # Check 1-hop and 2-hop neighborhood
    try:
        sub_nodes = set([vendor_id])
        for n1 in G.successors(vendor_id):
            sub_nodes.add(n1)
            for n2 in G.successors(n1):
                sub_nodes.add(n2)
        subG = G.subgraph(sub_nodes)
        
        # General simple cycles of length 2 to 5
        all_cycles = list(nx.simple_cycles(subG))
        for c in all_cycles:
            if vendor_id in c and 2 <= len(c) <= 5:
                cycles_found.append(c)
                
        # Targeted collusion cycle search: only edges with RAR >= rar_threshold
        collusion_edges = [
            (u, v) for u, v, d in subG.edges(data=True) 
            if d.get('reciprocal_amount_ratio', 0.0) >= rar_threshold or d.get('count', 1) >= 3
        ]
        collusion_subG = nx.DiGraph()
        collusion_subG.add_edges_from(collusion_edges)
        if collusion_subG.has_node(vendor_id):
            for cc in nx.simple_cycles(collusion_subG):
                if vendor_id in cc and 2 <= len(cc) <= 5:
                    collusion_cycles.append(cc)
    except Exception:
        pass
        
    # Check successors with reciprocal edges and track RAR
    for succ in G.successors(vendor_id):
        if G.has_edge(succ, vendor_id):
            reciprocal_nodes.append(succ)
            edge_rar = G[vendor_id][succ].get('reciprocal_amount_ratio', 0.0)
            if edge_rar > max_rar:
                max_rar = edge_rar
                
    if len(collusion_cycles) > 0:
        c_str = ' -> '.join(collusion_cycles[0])
        evidence.append(f'High-confidence collusion ring detected (RAR >= {rar_threshold}): {c_str}')
    elif len(cycles_found) > 0:
        c_str = ' -> '.join(cycles_found[0])
        evidence.append(f'Circular transaction loop detected: {c_str}')
        
    if len(reciprocal_nodes) > 0:
        evidence.append(f'Reciprocal bidirectional payment flow with {len(reciprocal_nodes)} counterparty(ies) (Max RAR: {max_rar:.2f})')
        
    return {
        'has_cycles': len(cycles_found) > 0 or len(collusion_cycles) > 0,
        'cycle_count': len(cycles_found),
        'cycles': cycles_found[:3],
        'collusion_cycles': collusion_cycles[:3],
        'reciprocal_count': len(reciprocal_nodes),
        'max_rar': round(float(max_rar), 4),
        'graph_evidence': evidence
    }

