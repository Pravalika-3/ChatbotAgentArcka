import json
import os
import glob

def convert_to_messages(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            for i, line in enumerate(infile, 1):
                try:
                    data = json.loads(line.strip())
                    prompt = data.get("prompt", "")
                    completion = data.get("completion", "")
                    if not prompt or not completion:
                        print(f"Warning: Skipping line {i} due to missing prompt or completion in {input_file}")
                        continue
                    messages = {
                        "messages": [
                            {"role": "system", "content": "You are an expert in the Recruitment Management System and RBAC."},
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": completion}
                        ]
                    }
                    json.dump(messages, outfile, ensure_ascii=False)
                    outfile.write('\n')
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON in line {i} of {input_file}: {line.strip()}\n{e}")
                except Exception as e:
                    print(f"Error processing line {i} in {input_file}: {line.strip()}\n{e}")
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error during conversion of {input_file}: {e}")

def process_all_jsonl_files():
    input_dir = "data/jsonl"
    output_dir = "data/messages"
    if not os.path.exists(input_dir):
        print(f"Error: {input_dir} directory not found")
        return
    jsonl_files = glob.glob(os.path.join(input_dir, "*.jsonl"))
    if not jsonl_files:
        print(f"No JSONL files found in {input_dir}")
        return
    for input_file in jsonl_files:
        filename = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_dir, f"{filename}_messages.jsonl")
        print(f"Converting {input_file} -> {output_file}")
        convert_to_messages(input_file, output_file)

if __name__ == "__main__":
    process_all_jsonl_files()