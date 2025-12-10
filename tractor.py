import sys
import os
import json
graph = {}
digraph = {}
module_count = {}
def process_command():
    args = sys.argv
    addr = args[1]
    lower = int(args[2])
    upper = int(args[3])
    tags = args[4:]
    return addr, lower, upper, tags

def add_edge(source, target):
    if source not in graph:
        graph[source] = []
        digraph[source] = []
    if target not in graph:
        graph[target] = []
        digraph[target] = []
    graph[source].append(target)
    graph[target].append(source)
    digraph[source].append(target)
    return


def find_connected_subgraphs(adj, min_size, max_size):
    """Enumerate all connected subgraphs with size in [min_size, max_size]."""
    results = []
    seen = set()  # store tuple(sorted(ids)) to deduplicate
    nodes = sorted(adj.keys())

    for root in nodes:
        # Only build subgraphs where root is the smallest id to avoid duplicates
        def grow(current_set, frontier):
            # record if size is within bounds
            if min_size <= len(current_set) <= max_size:
                key = tuple(sorted(current_set))
                if key not in seen:
                    seen.add(key)
                    results.append(list(current_set))

            if len(current_set) == max_size:
                return

            # expand using a snapshot of frontier to avoid mutation during iteration
            for node in list(frontier):
                if node <= root:
                    continue  # enforce root is the minimal id in the subgraph

                new_set = current_set | {node}
                # frontier update: remove chosen node, add its neighbors
                new_frontier = (frontier - {node}) | {nbr for nbr in adj[node] if nbr not in new_set and nbr > root}
                grow(new_set, new_frontier)

        initial_frontier = {nbr for nbr in adj[root] if nbr > root}
        grow({root}, initial_frontier)

    return results

def write_to_file(file_path, component, id_to_obj, size, file_index):
    """根据命名规则写入文件"""
    # 从原文件路径提取文件名（不含扩展名）
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_stem = os.path.splitext(file_name)[0]  # 去掉 .json 扩展名
    
    # 构造输出文件名：module_abc_5_2.json
    output_name = f"module_{file_stem}_{size}_{file_index}.json"
    output_path = os.path.join(dir_path, output_name)
    
    # 构造输出内容
    res = []
    for node in component:
        obj = id_to_obj[node]
        res.append(obj)
    
    # 写入文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=4, ensure_ascii=False)
        print(f"  Generated {output_name}")
    except Exception as e:
        print(f"  Error writing {output_path}: {e}")

def process_file(file_path, lower_bound, upper_bound, tag_list):
    # reset global graphs for each file
    graph.clear()
    digraph.clear()

    id_to_obj = {}
    with open(file_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
    for item in data:
        id_to_obj[item["id"]] = item
    #build an id to obj map
    for item in data:
        for key,value in item.items():
            if key == "id":
                continue
            
            # 处理 list 类型（如 "wires"）
            if isinstance(value, list):
                for element in value:
                    if isinstance(element, str) and element in id_to_obj:
                        add_edge(item["id"], element)
                    elif isinstance(element, list):
                        # 处理嵌套的列表（如 wires[0] 中的元素）
                        for sub_element in element:
                            if isinstance(sub_element, str) and sub_element in id_to_obj:
                                add_edge(item["id"], sub_element)
            # 处理非 list 类型的值
            elif isinstance(value, str) and value in id_to_obj:
                add_edge(item["id"], value)
    # enumerate all connected subgraphs within [lower_bound, upper_bound]
    subgraphs = find_connected_subgraphs(graph, lower_bound, upper_bound)

    # 按大小分组并输出，编号从 1 开始
    size_groups = {}
    for comp in subgraphs:
        size_groups.setdefault(len(comp), []).append(comp)

    for size in sorted(size_groups.keys()):
        for idx, comp in enumerate(size_groups[size], 1):
            write_to_file(file_path, comp, id_to_obj, size, idx)

    return 
    
def process_directory(dir_path, lower_bound, upper_bound, tag_list):
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            process_file(item_path, lower_bound, upper_bound, tag_list)
    return
    
def main():
    print("Entering command")
    address, lower_bound, upper_bound, tag_list = process_command()
    if not os.path.exists(address):
        print(f"Error: Address {address} does not exist.")
        sys.exit(1)
    if os.path.isfile(address):
        print("Processing file")
        process_file(address, lower_bound, upper_bound, tag_list)
        
            
    
    
    
    elif os.path.isdir(address):
        print("Processing directory")
        process_directory(address, lower_bound, upper_bound, tag_list)
    
    
    return     
if __name__ == "__main__":
    main()