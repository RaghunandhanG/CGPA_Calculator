from PyPDF2 import PdfReader
import streamlit as st  
import os
import pandas
import numpy as np
import re
import time 

def upload_file():

    uploaded_file = st.file_uploader(f'Choose your PDF file', type="pdf", accept_multiple_files=True)
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
    grades = []
    for i in info:
        l = i.split(" ")
        grade = int(l[0])
        credit = int(l[-1])
        credits.append(credit)
        grades.append(grade)
    return [grades , credits]

def calculate_sgpa(grades , credits):
    weights = []
    sum = 0
    total_credits = 0
    back_logs = 0
    credits_completed = 0

    for i in range(len(grades)):
        weight = grades[i] * credits[i]
        sum += weight
        weights.append(weight)
    
        total_credits += credits[i]
        if weight != 0 :
            credits_completed += credits[i]
        if weight == 0 and grades[i] < 6 :
            back_logs += 1
    return round(sum / credits_completed , 2) , total_credits , weights , back_logs , sum ,credits_completed



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
        course_names = [course_name.replace('"' , "") for course_name in course_names]
        return [course_names , name , reg_no]


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

   

        selected_course_names =  st.multiselect("Select the Courses to be excluded",course_names)

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
