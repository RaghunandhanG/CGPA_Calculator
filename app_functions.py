from PyPDF2 import PdfReader
import streamlit as st  
import os
import pandas
import numpy as np
import re
import time 

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
    combinations = ['U 0' , 'U 1', 'U 2', 'U 3', 'U 4','O 0' , 'O 1', 'O 2', 'O 3', 'O 4','A+ 0', 'A+ 1', 'A+ 2', 'A+ 3', 'A+ 4','A 0' ,'A 1', 'A 2', 'A 3', 'A 4','B+ 0', 'B+ 1', 'B+ 2', 'B+ 3', 'B+ 4','B 0' ,'B 1', 'B 2', 'B 3', 'B 4', 'C 0' , 'C 1', 'C 2', 'C 3', 'C 4', 'AB 0' , 'AB 1', 'AB 2', 'AB 3', 'AB 4','RA 0' , 'RA 1', 'RA 2', 'RA 3', 'RA 4','W 0', 'W 1', 'W 2', 'W 3', 'W 4','P 0' ,'P 0' , 'P 1', 'P 2', 'P 3', 'P 4', 'F 0' , 'F 1', 'F 2', 'F 3', 'F 4']
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
            st.write(str1)
            info.append(str1)
        elif str2 in combinations:
            n = n + 1 
            st.write(str2)
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



def find_grade_and_credit(info , course_names):
    
    credits = []
    grade = []
    for i in info:
        credits.append(i.split(" ")[1])
        grade.append(i.split(" ")[0])
    dct = {'AB':0 , 'B':6 , 'O':10, 'A':8, 'A+':9,'B+':7,'C':5 , "RA":0 , "W":0 , "P" : 0 , "F":0 , "U":0}
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
        
        
        total_credits += credits[i]
        if weight == 0 and grades[i] < 6 :
            back_logs += 1
    return round(sum / total_credits , 2) , total_credits , weights , back_logs , sum



def generate_df(weights , course_names , sum , grades):
    
     course_names = [i.replace('"' , "") for i in course_names]
     data = pandas.DataFrame()
     weights = [round(i/sum* 100 , 2) for i in weights]
     data['weights'] = weights
     data['Subjects'] = course_names
     data["Grades"] = grades
     
     return data
     
     
     
def get_course_names(text):
    

        from together import Together

        client = Together(api_key="9a61e2798de6101e801d7784c4ccdd6baab3384475b91b2b5114f925c74339c2")

        response = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": f"extract  the course names in a python list and also extract the name and register number in a dictionary {text}. IMPORTANT : DO NOT CONSIDER THE COURSE CODES AND DO NOT PROVIDE CODE AND JUST KEEP IT SIMPLE BY ONLY PROVIDING THE LISTS AND DICTIONARY."}],)
        


        # st.write(name_reg)
        msg = response.choices[0].message.content
        name_reg = extract_name_reg(msg)
        course_names = msg.replace("\n" , " ")
        course_names = extract(course_names)
        course_names = course_names.split(",")
        course_names = [i.replace("\n" , " ") for i in course_names]
        name = list(name_reg.values())[0]
        reg_no = list(name_reg.values())[1]

        return course_names , name , reg_no


def extract(text):
  res = []
  start = text.find('[') + 1
  end = text.find(']')

  return text[start:end]


def plot(data):
    import plotly.graph_objects as go
    import plotly.express as px
    fig = px.bar(data, x='Subjects', y='Grades', title='Grades in each Course' , color='Subjects',labels={'Grades': 'Grade'})
    fig.update_layout(
        width=1000,  # Set the width of the figure
        height=600,  # Set the height of the figure
        xaxis_title='Subjects',  # Label for x-axis
        yaxis_title='Grade'  # Label for y-axis
    )
    for i, row in data.iterrows():
        fig.add_annotation(x=row['Subjects'], y=row['Grades'], text=str(row['Grades']), showarrow=False)
    fig.update_xaxes(tickvals=[90])
    st.write(fig)
    fig = px.pie(data, values='weights', names='Subjects', title='Weightage of each Course in %')
    st.write(fig)
        
    
    
def select_course_names(course_names,credits , grades ):

   

        selected_course_names =  st.multiselect("Select the Courese to be excluded",course_names)

        for i in selected_course_names:
            if i in course_names:
                index = course_names.index(i)
                course_names.pop(index)
                credits.pop(index)
                grades.pop(index)
    
    

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

def get_dict(a , b):

    c = zip(a,b)
    d  = dict(tuple(c))
    return d



def get_name(text):

    
        from together import Together

        client = Together(api_key="c2bfddf8883ac6b65b328e3e447017a63ead0fe7550f653770a4def525ae20db ")
        time.sleep(1)
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B",
            messages=[{"role": "user", "content": f"Extract the student name and the Register number in a dictionary format from this text '{text}.IMPORTANT:I only want the dictionary and i don't want any other text and the output should be like 'name':'Raghunandhan G' , 'number':'22BME078'"}])
        name_reg = response.choices[0].message.content
        get_name(name_reg)
        name_reg = name_reg.split(',')
        name_reg = [i.split(":") for i in name_reg]
        get_name(name_reg)



def extract_name_reg(text):

    extracted_text = ""
    for i in range(len(text)):
        if "{" not in text[i:] and "}" in text[i:]:
            if text[i] != "}":
                extracted_text += text[i]
    text = extracted_text
    text = text.split(',')
    text = [i.split(":") for i in text]
    a = text[0]
    a = [i.replace('"' , "") for i in a]
    b = text[1]
    b = [i.replace("'" , "") for i in b]
    d = dict()
    d[a[0]] = a[1]
    d[b[0]] = b[1]
    return d
