import sys
import os

def process_command():
    args = sys.argv
    addr = args[1]
    lower = int(args[2])
    upper = int(args[3])
    tags = args[4:]
    return addr, lower, upper, tags

def process_file(file_path, lower_bound, upper_bound, tag_list):
    id_to_obj = {}
    with open(file_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
    for item in data:
        id_to_obj[item["id"]] = item
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