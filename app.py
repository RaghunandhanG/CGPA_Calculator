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
            info = get_info(text)
            course_names , name , reg_no = get_course_names(text)

            reg_no_color = random.choice([
    "red", "green", "blue", "orange", "purple", "pink", "brown", 
    "teal", "navy", "olive", "maroon", "lime", "aqua", "fuchsia", 
    "silver", "gray", "black", "white", "coral", "indigo", "gold",
    "violet", "turquoise", "salmon", "khaki", "orchid", "steelblue",
    "tomato", "thistle", "sienna", "rosybrown", "slategray", "peru"
]
)
            reg_no = reg_no.replace('"' , "")
            reg_no_font_size = "25px"
            name_font_size = "35px"
            additional_text_font_size = "25px"
            st.write(f'<h1><span style="font-size:{additional_text_font_size};">Hi,</span><span style="font-size:{name_font_size}; color:black;">{name}</span> <span style="font-size:{reg_no_font_size}; color:{reg_no_color};">{reg_no}</span></h1>', unsafe_allow_html=True)
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
