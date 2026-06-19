from PyPDF2 import PdfReader
import streamlit as st  
import os
import pandas as pd
import json
import ollama

def upload_file():
    os.makedirs('uploads', exist_ok=True)
    uploaded_file = st.file_uploader('Choose your PDF file', type="pdf", accept_multiple_files=True)
    if uploaded_file is not None:
        return uploaded_file, True
    else:
        st.write('Waiting for the file....')
        return None, False

def read_file(file_path):
    reader = PdfReader(file_path)
    page = reader.pages[0]
    text = page.extract_text()
    return text
    
def get_info(text):
    lists = (['O', 'A+', 'A', 'B+', 'B', 'C', 'RA', 'SA', 'W', 'U', 'P', 'F', 'AB'],
            [0, 1, 2, 3, 4],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    combinations = [(c, l, n) for c in lists[2] for l in lists[0] for n in lists[2]]
    strings = [' '.join(map(str, comb)) for comb in combinations]

    l = []
    n = 0
    for i in range(len(text)):
        i += n
        if text[i :  i+5] in strings:
            l.append(text[i : i+5])
            n += 5
        elif text[i :  i+6] in strings:
            l.append(text[i :  i+6])
            n += 5
        elif text[i :  i+7] in strings:
            l.append(text[i :  i+6])
            n += 5
        elif text[i :  i+7] in strings:
            l.append(text[i :  i+7])
            n += 5
    return l

def upload_file_in_db(uploaded_file, file_path):
    if uploaded_file is not None:
        upload_dir = "./"
        os.makedirs(upload_dir, exist_ok=True)  
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success('File uploaded', icon="✅")

def find_grade_and_credit(info, course_names):
    credits = []
    grades = []
    for i in info:
        l = i.split(" ")
        grade = int(l[0])
        credit = int(l[-1])
        credits.append(credit)
        grades.append(grade)
    return [grades, credits]

def calculate_sgpa(grades, credits):
    weights = []
    sum_weights = 0
    total_credits = 0
    back_logs = 0
    credits_completed = 0

    for i in range(len(grades)):
        weight = grades[i] * credits[i]
        sum_weights += weight
        weights.append(weight)
    
        total_credits += credits[i]
        if weight != 0:
            credits_completed += credits[i]
        if weight == 0 and grades[i] < 6:
            back_logs += 1
            
    # Prevent DivisionByZero errors just in case
    sgpa = round(sum_weights / credits_completed, 2) if credits_completed > 0 else 0.0
    return sgpa, total_credits, weights, back_logs, sum_weights, credits_completed

def generate_df(weights, course_names, sum_weights, grades):
     course_names = [i.replace('"', "") for i in course_names]
     data = pd.DataFrame()
     weights = [round((i / sum_weights) * 100, 2) if sum_weights > 0 else 0 for i in weights]
     data['weights'] = weights
     data['Subjects'] = course_names
     data["Grades"] = grades
     return data
     
def get_course_names(text):
    system_prompt = """
    You are a data extraction bot. Your ONLY purpose is to extract student data from the provided text and output it strictly in valid JSON format. 
    Do NOT output any conversational text. Do NOT consider course codes.
    
    The JSON must use this exact schema:
    {
      "student_name": "Extracted Name",
      "register_number": "Extracted Reg No",
      "courses": ["Course 1", "Course 2", "Course 3"]
    }
    """

    try:
        response = ollama.chat(
            model="qwen3:latest",
            format="json", # Forces strict JSON mode
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract data from this text: {text}"}
            ]
        )

        raw_output = response['message']['content']
        parsed_data = json.loads(raw_output)

        name = parsed_data.get("student_name", "Unknown")
        reg_no = parsed_data.get("register_number", "Unknown")
        course_names = parsed_data.get("courses", [])

        # Clean up course names formatting
        course_names = [str(course).replace('"', '').replace('\n', ' ').strip() for course in course_names]

        return [course_names, name, reg_no]

    except Exception as e:
        print(f"Error parsing with Ollama: {e}")
        return [[], "Error Parsing", "Error Parsing"]
    
def select_course_names(course_names, credits, grades):
    selected_course_names = st.multiselect("Select the Courses to be excluded", course_names)
    for i in selected_course_names:
        if i in course_names:
            index = course_names.index(i)
            course_names.pop(index)
            credits.pop(index)
            grades.pop(index)
    return selected_course_names, credits, grades  

def get_dict(lst, course_names):
    c = zip(course_names, lst)
    d = dict(tuple(c))
    return d

def get_name(text):
    """
    Upgraded to use strict JSON as well to prevent dictionary parsing crashes.
    """
    system_prompt = """
    Extract the student name and register number from the text. 
    Output ONLY valid JSON matching this schema:
    {"name": "Extracted Name", "number": "Extracted Reg No"}
    """
    try:
        response = ollama.chat(
            model="qwen3:latest",
            format="json",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )
        return json.loads(response['message']['content'])
    except Exception:
        return {"name": "Error", "number": "Error"}