import re
import json
import uuid
import os
import glob
import chardet
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_encoding(file_path):
    """Detect the encoding of a file using chardet."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def parse_markdown_to_jsonl(markdown_file, output_jsonl):
    encoding = detect_encoding(markdown_file)
    if not encoding:
        print(f"Error: Could not detect encoding for {markdown_file}. Skipping.")
        return

    content = None
    try:
        with open(markdown_file, 'r', encoding=encoding) as f:
            content = f.read()
    except UnicodeDecodeError:
        for enc in ('utf-8-sig', 'utf-16'):
            try:
                with open(markdown_file, 'r', encoding=enc) as f:
                    content = f.read()
                print(f"Successfully read {markdown_file} with encoding {enc}")
                break
            except UnicodeDecodeError:
                continue

    if content is None:
        print(f"Error: Unable to decode {markdown_file} with any supported encoding. Skipping.")
        return

    print(f"Preview of {markdown_file} (first 500 characters):\n{content[:500]}\n")

    entries = []

    system_match = re.search(r'## What Our Application Does\n([\s\S]*?)\n## Overview', content)
    if system_match:
        system_desc = system_match.group(1).strip()
        entries.append({
            "prompt": "What is the purpose of the Recruitment Management System?",
            "completion": system_desc
        })

    role_sections = re.finditer(r'### (\d+\. [A-Za-z]+)\n([\s\S]*?)(?=(### \d+\. [A-Za-z]+|$))', content)
    for role_section in role_sections:
        role_name = role_section.group(1).split('. ')[1]
        role_content = role_section.group(2).strip()
        tables_match = re.search(r'- \*\*Accessed Tables\*\*:\n\s*- (.*?)\n', role_content, re.DOTALL)
        tables = tables_match.group(1).split(', ') if tables_match else []
        perms_match = re.search(r'- \*\*Permissions\*\*:\n\s*- (.*?)\n', role_content)
        permissions = perms_match.group(1) if perms_match else ""
        func_match = re.search(r'- \*\*Functionality\*\*:\n([\s\S]*?)(?=- \*\*|$)', role_content)
        functionality = func_match.group(1).strip() if func_match else ""
        entries.append({
            "prompt": f"What can the {role_name} role do in the Recruitment Management System?",
            "completion": f"The {role_name} role can access the following tables: {', '.join(tables)}. "
                          f"Permissions include: {permissions}. Functionality: {functionality}"
        })

        entries.append({
            "prompt": f"Which tables can the {role_name} role access?",
            "completion": f"The {role_name} role can access the following tables: {', '.join(tables)}."
        })

        entries.append({
            "prompt": f"What permissions does the {role_name} role have?",
            "completion": f"The {role_name} role has the following permissions: {permissions}."
        })

    task_match = re.search(r'### Creating a Request Form\n([\s\S]*?)\n## Getting Started', content)
    if task_match:
        task_content = task_match.group(1).strip()
        entries.append({
            "prompt": "How can I create a Request Form in the Recruitment Management System?",
            "completion": task_content
        })

        who_match = re.search(r'- \*\*Who Can Create a Request Form\?\*\*\n\s*- (.*?)\n', task_content)
        if who_match:
            who_can = who_match.group(1)
            entries.append({
                "prompt": "Who can create a Request Form in the Recruitment Management System?",
                "completion": who_can
            })

    table_sections = re.finditer(r'### ([A-Za-z\s]+ Table)\n([\s\S]*?)(?=(### [A-Za-z\s]+ Table|$))', content)
    for table_section in table_sections:
        table_name = table_section.group(1).replace(" Table", "").strip()
        table_content = table_section.group(2).strip()

        columns_match = re.search(r'- \*\*Columns\*\*:\s*(.*?)\n', table_content)
        columns = columns_match.group(1).strip() if columns_match else "Not specified"

        description_match = re.search(r'- \*\*Description\*\*:\s*(.*?)(?=\n|$)', table_content)
        description = description_match.group(1).strip() if description_match else "Not specified"

        entries.append({
            "prompt": f"What is the {table_name} table in the Recruitment Management System?",
            "completion": f"The {table_name} table has the following columns: {columns}. Description: {description}."
        })

        entries.append({
            "prompt": f"What are the columns in the {table_name} table?",
            "completion": f"The columns in the {table_name} table are: {columns}."
        })

        entries.append({
            "prompt": f"What is the purpose of the {table_name} table?",
            "completion": f"The {table_name} table is used to: {description}."
        })

    table_definitions = re.finditer(r'CREATE TABLE\s*(?:\[dbo\]\.\[)?([^\]\s(]+)(?:\])?\s*\(\s*([\s\S]*?)\)\s*(?:ON \[PRIMARY\])?', content, re.IGNORECASE)
    for table_def in table_definitions:
        table_name = table_def.group(1).strip()
        table_body = table_def.group(2).strip()

        columns = []
        column_lines = re.findall(r'\[([^\]]+)\]\s*\[([^\]]+)\](.*?)(?=(,\s*\[|$))', table_body)
        for col in column_lines:
            col_name = col[0].strip()
            col_type = col[1].strip()
            col_constraints = col[2].strip()
            constraints = []
            if "IDENTITY" in col_constraints:
                constraints.append("Auto-increment")
            if "NOT NULL" in col_constraints:
                constraints.append("Required")
            if "NULL" in col_constraints and "NOT NULL" not in col_constraints:
                constraints.append("Optional")
            if "PRIMARY KEY" in table_body and col_name in table_body.split("PRIMARY KEY")[1]:
                constraints.append("Primary Key")
            col_desc = f"{col_name} ({col_type}"
            if constraints:
                col_desc += f", {', '.join(constraints)}"
            col_desc += ")"
            columns.append(col_desc)

        defaults = []
        default_matches = re.finditer(r'ALTER TABLE\s*(?:\[dbo\]\.\[)?' + re.escape(table_name) + r'(?:\])?\s*ADD\s*DEFAULT\s*\(\((.*?)\)\)\s*FOR\s*\[([^\]]+)\]', content, re.IGNORECASE)
        for default_match in default_matches:
            default_value = default_match.group(1).strip()
            default_col = default_match.group(2).strip()
            defaults.append(f"{default_col} defaults to {default_value}")

        purpose = f"Stores information related to {table_name.lower().replace(' ', '_')}."
        if "User" in table_name or "Employee" in table_name:
            purpose = f"Stores user or employee data for the Recruitment Management System."
        elif "Job" in table_name or "Sourcing" in table_name or "Request" in table_name:
            purpose = f"Manages job postings, sourcing forms, or requests in the Recruitment Management System."
        elif "Feedback" in table_name:
            purpose = f"Handles feedback data for candidates in the Recruitment Management System."

        entries.append({
            "prompt": f"What is the {table_name} table in the Recruitment Management System?",
            "completion": f"The {table_name} table has the following columns: {', '.join(columns)}. {purpose}"
        })

        entries.append({
            "prompt": f"What are the columns in the {table_name} table?",
            "completion": f"The columns in the {table_name} table are: {', '.join(columns)}."
        })

        entries.append({
            "prompt": f"What is the purpose of the {table_name} table?",
            "completion": f"The {table_name} table is used to: {purpose}"
        })

        if defaults:
            entries.append({
                "prompt": f"What are the default values for columns in the {table_name} table?",
                "completion": f"The {table_name} table has the following default values: {', '.join(defaults)}."
            })

    view_definitions = re.finditer(r'CREATE VIEW\s*(?:\[dbo\]\.\[)?([^\]\s(]+)(?:\])?\s*AS\s*([\s\S]*?)(?=GO|$)', content, re.IGNORECASE)
    for view_def in view_definitions:
        view_name = view_def.group(1).strip()
        view_body = view_def.group(2).strip()
        view_body = re.sub(r'\s+', ' ', view_body).strip()

        purpose = f"Provides a view of {view_name.lower().replace('vwget', '').replace('vw', '')} data."
        if "Feedback" in view_name:
            purpose = f"Retrieves feedback-related data for the Recruitment Management System."
        elif "RequestForm" in view_name or "SourcingForm" in view_name:
            purpose = f"Displays request or sourcing form details in the Recruitment Management System."
        elif "User" in view_name or "Recruiter" in view_name or "Interviewer" in view_name:
            purpose = f"Shows user, recruiter, or interviewer details in the Recruitment Management System."

        entries.append({
            "prompt": f"What does the {view_name} view do in the Recruitment Management System?",
            "completion": f"The {view_name} view {purpose} It is defined as: {view_body}"
        })

    insert_statements = re.finditer(r'INSERT\s*(?:INTO\s*)?(?:\[dbo\]\.\[)?([^\]\s(]+)(?:\])?\s*\(\s*([\s\S]*?)\s*\)\s*VALUES\s*\(\s*([\s\S]*?)\s*\)(?=\s*(?:GO|$|;|\nSET|\nINSERT))', content, re.IGNORECASE)
    for insert_stmt in insert_statements:
        table_name = insert_stmt.group(1).strip()
        columns = insert_stmt.group(2).strip()
        values = insert_stmt.group(3).strip()

        print(f"Matched INSERT for table {table_name}: Columns={columns}, Values={values}")

        try:
            columns_list = [col.strip().strip('[]') for col in columns.split(',')]
            values_list = []
            current_value = ""
            in_cast = 0
            in_quotes = False
            for char in values:
                if char == ',' and in_cast == 0 and not in_quotes:
                    values_list.append(current_value.strip())
                    current_value = ""
                else:
                    current_value += char
                    if char == "'":
                        in_quotes = not in_quotes
                    elif char == '(':
                        in_cast += 1
                    elif char == ')':
                        in_cast -= 1
            values_list.append(current_value.strip())
            cleaned_values = []
            for val in values_list:
                val = val.strip()
                val = re.sub(r"^N'", "", val)
                val = re.sub(r"'$", "", val)
                val = re.sub(r"CAST\(N'([^']+)'\s+AS\s+DateTime\)", r"\1", val)
                if val.upper() == "NULL":
                    val = "NULL"
                cleaned_values.append(val)
            if len(columns_list) != len(cleaned_values):
                print(f"Error: Mismatch between columns ({len(columns_list)}) and values ({len(cleaned_values)}) for table {table_name}. Skipping.")
                continue
            data_description = ", ".join([f"{col}: {val}" for col, val in zip(columns_list, cleaned_values)])

            entries.append({
                "prompt": f"What data is inserted into the {table_name} table in the Recruitment Management System?",
                "completion": f"The {table_name} table has the following data inserted: {data_description}."
            })

        except Exception as e:
            print(f"Error processing INSERT for table {table_name}: {str(e)}. Skipping.")
    print(f"Extracted {len(entries)} entries from {markdown_file}")

    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        if not entries:
            print(f"No entries extracted for {markdown_file}. Writing empty JSONL file.")
            f.write('')
        else:
            for entry in entries:
                entry["completion"] = re.sub(r'\*\*([^\*]+)\*\*', r'\1', entry["completion"])
                entry["completion"] = re.sub(r'\n\s*-\s*', r'\n', entry["completion"]).strip()
                f.write(json.dumps(entry) + '\n')

def parse_resume_to_jsonl(resume_file, output_jsonl):
    """Convert resume text to JSONL format."""
    encoding = detect_encoding(resume_file)
    try:
        with open(resume_file, 'r', encoding=encoding) as f:
            content = f.read().strip()
    except Exception as e:
        logger.error(f"Error reading {resume_file}: {str(e)}")
        return

    if not content:
        logger.warning(f"No content in {resume_file}")
        return

    entries = [
        {
            "prompt": f"Summarize the following resume in 100 words or less:\n{content[:2000]}",
            "completion": "This resume belongs to a candidate with [insert summary based on content, e.g., 5 years of software engineering experience, skilled in Python and Java]."
        },
        {
            "prompt": f"Extract key skills from the following resume:\n{content[:2000]}",
            "completion": "Key skills: [list skills, e.g., Python, Java, SQL, Project Management]."
        }
    ]

    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    logger.info(f"Extracted {len(entries)} entries from {resume_file} to {output_jsonl}")

def process_all_files():
    """Process markdown and resume files."""
    # Get the directory of the script (ChatBot_BE/scripts)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to ChatBot_BE
    base_dir = os.path.dirname(script_dir)

    # Process markdown files
    docs_dir = os.path.join(base_dir, "docs")  # ChatBot_BE/docs
    output_dir = os.path.join(base_dir, "data/jsonl")  # ChatBot_BE/data/jsonl
    os.makedirs(output_dir, exist_ok=True)
    markdown_files = glob.glob(os.path.join(docs_dir, "*.markdown")) + glob.glob(os.path.join(docs_dir, "*.txt"))
    for markdown_file in markdown_files:
        filename = os.path.splitext(os.path.basename(markdown_file))[0]
        output_jsonl = os.path.join(output_dir, f"{filename}_finetune.jsonl")
        logger.info(f"Processing {markdown_file} -> {output_jsonl}")
        parse_markdown_to_jsonl(markdown_file, output_jsonl)

    # Process resume text files
    resume_text_dir = os.path.join(base_dir, "data/resume_text")  # ChatBot_BE/data/resume_text
    resume_files = glob.glob(os.path.join(resume_text_dir, "*.txt"))
    for resume_file in resume_files:
        filename = os.path.splitext(os.path.basename(resume_file))[0]
        output_jsonl = os.path.join(output_dir, f"{filename}_finetune.jsonl")
        logger.info(f"Processing {resume_file} -> {output_jsonl}")
        parse_resume_to_jsonl(resume_file, output_jsonl)

if __name__ == "__main__":
    process_all_files()