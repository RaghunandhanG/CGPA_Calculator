import streamlit as st
from PyPDF2 import PdfReader
from app_functions import *
import os
import time
import random

st.title("SGPA CALCULATOR")

uploaded_file , res = upload_file()
if res:
            file_path = os.path.join("uploads", uploaded_file.name)
            upload_file_in_db(uploaded_file , file_path)
            text = read_file(file_path)
            text = text.replace(',' , "")
            info = get_info(text.replace(f',' , ""))
            course_names , name , reg_no = get_course_names(text)

            reg_no_color = random.choice(["red", "green", "blue","magenta", "yellow"])

            reg_no_font_size = "25px"
            name_font_size = "35px"
            additional_text_font_size = "25px"
            reg_no = reg_no.replace('"' , "")
            st.write(f'<h1> <span style="font-size:{additional_text_font_size};">Hi,</span><span style="font-size:{name_font_size};">{name}</span> <span style="font-size:{reg_no_font_size}; color:{reg_no_color};">{reg_no}</span></h1>', unsafe_allow_html=True)
            grades , credits = find_grade_and_credit(info , course_names)
            selected_course_names ,credits, grades , res = select_course_names(course_names , credits , grades)
            
            sgpa , total_credits ,weights , back_logs , sum ,credits_completed= calculate_sgpa(grades , credits)

            with st.spinner('Calculating...'):
                time.sleep(3)
            col1, col2 ,col3,col4= st.columns(4)
            col1.metric(f":blue[SGPA]",sgpa)
            col2.metric(f":green[Total Credits]",total_credits)
            col3.metric(f':blue[Credits Completed]' , credits_completed)
            col4.metric(f':red[Back Logs]' , back_logs)

            data = generate_df(weights , course_names , sum , grades)

            plot(data)
            st.write("## Developer Info")
            st.write(
        """
        - **Developer**: Raghunandhan G 
        - **Contact**: 
            - Email: [raghunandhan.22me@kct.ac.in](mailto:raghunandhan.22me@kct.ac.in)
            - LinkedIn: [Raghunandhan G](https://www.linkedin.com/in/raghunandhan-g-92a28025a)
        - **GitHub**: [RaghunandhanG GitHUB](https://github.com/RaghunandhanG)
        """
    )
            st.write("**Made with ❤️ in iQube**")
