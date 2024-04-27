from PyPDF2 import PdfReader
import streamlit as st  
import os
import pandas
import numpy as np
import re


def upload_file():

    uploaded_file = st.file_uploader(f'Choose your PDF file', type="pdf")
    if uploaded_file is not None:
        return uploaded_file , True
    else:
        st.write('Waiting for the file....')
        return None , False





def read_file(file_path):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    page = reader.pages[0]
    text = page.extract_text()
    return text
    
def get_info(text):
    combinations = ['O 1', 'O 2', 'O 3', 'O 4', 'A+ 1', 'A+ 2', 'A+ 3', 'A+ 4', 'A 1', 'A 2', 'A 3', 'A 4', 'B+ 1', 'B+ 2', 'B+ 3', 'B+ 4', 'B 1', 'B 2', 'B 3', 'B 4', 'C 1', 'C 2', 'C 3', 'C 4', 'AB 1', 'AB 2', 'AB 3', 'AB 4', 'RA 1', 'RA 2', 'RA 3', 'RA 4', 'W 1', 'W 2', 'W 3', 'W 4', 'P 1', 'P 2', 'P 3', 'P 4', 'F 1', 'F 2', 'F 3', 'F 4']
    info = []
    n = 0
    for i in range(len(text)):
        
        i = i + (n * 5)
        if i >= len(text) - 5:
            break
        str1 = text[i] + text[i+1] + text[i+2] + text[i+3]
        str2 =  text[i] + text[i+1] + text[i+2]
        if str1 in  combinations :
            n = n + 1
            info.append(str1)
        elif str2 in combinations:

            n = n + 1 
            info.append(str2)
    
    
    return info


def upload_file_in_db(uploaded_file,file_path):

    if uploaded_file is not None:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)  

        # Create the directory if it doesn't exist
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        

        # Can be used wherever a "file-like" object is accepted:
        st.success('File uploaded', icon="✅")



def find_grade_and_credit(info):
    
    credits = []
    grade = []
    for i in info:
        credits.append(i.split(" ")[1])
        grade.append(i.split(" ")[0])
    dct = {'AB':0 , 'B':6 , 'O':10, 'A':8, 'A+':9,'B+':7,'C':5 , "RA":0 , "W":0 , "P" : 0 , "F":0}
    grade = [dct[i] for i in grade]
    credits = [int(i) for i in credits]
        
    return grade , credits

def calculate_sgpa(grades , credits):
    weights = []
    sum = 0
    total_credits = 0
    back_logs = 0
    for i in range(len(grades)):
        weight = grades[i] * credits[i]
        sum += weight
        weights.append(weight)
        
        if weight != 0:
            total_credits += credits[i]
        else:
            back_logs += 1
    return round(sum / total_credits , 2) , total_credits , weights , back_logs



def generate_df(weights , course_names):
    
     data = pandas.DataFrame()
     data['weights'] = weights
     data['Subjects'] = course_names
     
     return data
     
     
     
def get_course_names(text):
    

  


        import google.generativeai as genai

        genai.configure(api_key="AIzaSyAbEwy660KBFDw9qpfKCtNoNK6m5Ozhssg")

        # Set up the model
        generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
        }

        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)

        prompt_parts = [
        "The user will input the text containing the course names of a semester. Output the course names in a python like text format. The order of the ourse names should be in the same order as in the text provided by the user.\n\n\nIMPORTANT: The extraction of the COURSE NAMES should be in the same order as the in the text. Output only the course names not the course code and the output should only be in text format like a python list\nNOTE:The output format should be a text not  a CODE!!",
        "input : Sd/.. Controller of ExaminationEnd Semester Examination - Dec-2023 Student Name: RAGHUNANDHAN G Reg. No.: 22BME078 Semester: ODD UG�R21 Gender: Male Program: B.E�MECHANICAL ENGINEERING ODD UG�R21 U18TLR2001-TAMILS AND TECHNOLOGY7 B+ 1 Pass ODD UG�R21 U18MEI3201-METAL CUTTING AND COMPUTER AIDED MANUFACTURING8 A 4 Pass ODD UG�R21 U18MEP3006-MACHINE DRAWING LABORATORY10 O 1 Pass ODD UG�R21 U18MET3002-ENGINEERING MECHANICS8 A 3 Pass ODD UG�R21 U18MET3003-ENGINEERING THERMODYNAMICS8 A 3 Pass ODD UG�R21 U18MET3004-COMPUTER AIDED DESIGN9 A+ 3 Pass ODD UG�R21 U18MET3005-MACHINE DRAWING 8 A 2 Pass ODD UG�R21 U18INI3600-ENGINEERING CLINIC -III 10 O 3 Pass ODD UG�R21 U18MAT3101-PARTIAL DIFFERENTIAL EQUATIONS AND TRANSFORMS9 A+ 4 Pass Credit Registered : 24 Credit Completed : 24Semest er Cour se NameGrade pointGrade Credit Result status",
        "output : ['TAMILS AND TECHNOLOGY', 'METAL CUTTING AND COMPUTER AIDED MANUFACTURING', 'MACHINE DRAWING LABORATORY', 'ENGINEERING MECHANICS', 'ENGINEERING THERMODYNAMICS', 'COMPUTER AIDED DESIGN', 'MACHINE DRAWING', 'ENGINEERING CLINIC -III', 'PARTIAL DIFFERENTIAL EQUATIONS AND TRANSFORMS'] ",
        f"input: {text}",
        "output: ",
        ]



        response = model.generate_content(prompt_parts)
        course_names = response.text
        course_names = course_names.replace("\n" , " ")
        course_names = extract(course_names)
        course_names = course_names.split(",")
        course_names = [i.replace("\n" , " ") for i in course_names]
        

        return course_names


def extract(text):
  res = []
  start = text.find('[') + 1
  end = text.find(']')

  return text[start:end]


def plot(data):
    import plotly.graph_objects as go

    # Sample data

    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=data["Subjects"],  # Categories on x-axis
        y=data["weights"]      # Values on y-axis
    )])

    # Customize layout
    fig.update_layout(
        title="Weightage of each Course",
        yaxis_title="Values",
        width=1000,  # Set the width of the figure
        height=600, # Set the height of the figure
    )

    # Show plot
    st.write(fig)
    
    
    
def select_course_names(course_names,credits , grades):

    with st.form("my_form"):

        selected_course_names =  st.multiselect("Select the Courese to be excluded",course_names)

        for i in selected_course_names:
            if i in course_names:
                index = course_names.index(i)
                course_names.pop(index)
                credits.pop(index)
                grades.pop(index)
        submitted = st.form_submit_button("Submit")
    
    

    if len(selected_course_names) != 0:
        return selected_course_names ,credits , grades , True 

    else:
        return selected_course_names , credits , grades, False
    



def get_dict(lst , course_names):
    d = dict()
    a = lst
    b = course_names
    c = zip(b,a)
    d = dict(tuple(c))
    return d