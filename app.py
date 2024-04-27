import streamlit as st
from PyPDF2 import PdfReader
from app_functions import *
import os
import time

st.title("SGPA CALCULATOR")
    st.session_state.load_state = False
uploaded_file , res = upload_file()
if res:
            file_path = os.path.join("uploads", uploaded_file.name)
            upload_file_in_db(uploaded_file , file_path)
            text = read_file(file_path)

            info = get_info(text)
            course_names = get_course_names(text)
            grades , credits = find_grade_and_credit(info , course_names)

            selected_course_names ,credits, grades , res = select_course_names(course_names , credits , grades)
            
                 
            sgpa , total_credits ,weights , back_logs , sum = calculate_sgpa(grades , credits)

            with st.spinner('Calculating...'):
                time.sleep(3)
            col1, col2 ,col3= st.columns(3)
            col1.metric(f":blue[SGPA]",sgpa)
            col2.metric(f":green[Credits Completed]",total_credits)
            col3.metric(f':red[Back Logs]' , back_logs)
                #generate_report(weights)
            data = generate_df(weights , course_names , sum , grades)

            plot(data)









 
