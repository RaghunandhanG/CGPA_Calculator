import streamlit as st
from PyPDF2 import PdfReader
from app_functions import *
import os
import time
import random
from itertools import chain

st.title("CGPA CALCULATOR")
text = '''This app is still in testing stage.
Encountered an issue? Let us know! Your feedback helps us improve.
Use the email below to let us know '''
st.caption(text)
uploaded_files , uploaded = upload_file()
if uploaded:
            file_paths = []
            for uploaded_file in uploaded_files:
                    file_path = os.path.join("uploads", uploaded_file.name)
                    file_paths.append(file_path)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.read())
            course_names = []
            grades = []
            credits = []
            reg_no = []
            name = []
            try:
                for file_path in set(file_paths):
                    text = read_file(file_path)
                    text = text.replace(',' , "")
                    info = get_info(text.replace(f',' , ""))
                    lst = find_grade_and_credit(info , course_names)
                    grades = grades + lst[0]
                    credits = credits + lst[1]
                    lst = get_course_names(text)
                    course_names += lst[0]
                    reg_no.append(lst[2])
                    name.append(lst[1])
                if len(set(name)) == 1:
                    
                    flat_list = list(chain.from_iterable(course_names))
                    selected_course_names ,credits, grades = select_course_names(course_names , credits , grades)
                    if len(credits) != 0:
                        sgpa , total_credits ,weights , back_logs , sum ,credits_completed= calculate_sgpa(grades , credits)

                        reg_no_color = random.choice(["red", "green", "blue","magenta", "yellow"])

                        reg_no_font_size = "25px"
                        name_font_size = "35px"
                        additional_text_font_size = "25px"
                        reg_no = reg_no[0]
                        reg_no = reg_no.replace('"' , "")
                        st.write(f'<h1> <span style="font-size:{additional_text_font_size};">Hi,</span><span style="font-size:{name_font_size};">{name[0]}</span> <span style="font-size:{reg_no_font_size}; color:{reg_no_color};">{reg_no}</span></h1>', unsafe_allow_html=True)

                        with st.spinner('Calculating...'):
                            time.sleep(1)
                        col1, col2 ,col3,col4= st.columns(4)
                        col1.metric(f":blue[CGPA]",sgpa)
                        col2.metric(f":green[Total Credits]",total_credits)
                        col3.metric(f':blue[Credits Completed]' , credits_completed)
                        col4.metric(f':red[Back Logs]' , back_logs)

                        data = generate_df(weights , course_names , sum , grades)
                elif len(set(name)) > 1:
                        st.toast("You have uploaded results of different person!!")
                        name = list()
            except:
                  st.toast("Invalid file !")

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
else:
    st.write("Waiting for Files....")
