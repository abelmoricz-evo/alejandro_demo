import os
import textwrap
import inspect
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine
from streamlit.logger import get_logger


def show_code(demo):
    show_code = st.sidebar.checkbox("Show code", True)  # """Showing the code of the demo."""
    if show_code:
        st.markdown("""<div style='margin-top:500px;'></div> 
        <h1>the actual code making the page run</h1>""", unsafe_allow_html=True)  # Showing the code of the demo.
        sourcelines, _ = inspect.getsourcelines(demo)
        st.code(textwrap.dedent("".join(sourcelines[1:])), line_numbers=True)


load_dotenv()
st.set_page_config(layout='wide')


def main_app():

    st.header("Determination of fungal conidia or blastospore concentration in liquid samples ", divider='green')

    st.markdown("""
### 1. Purpose
Determination of the concentration of fungal spores (conidia or blastospores) in liquid spore suspensions, which cannot be enumerated by scanning due to the small size of the spores, using a hemocytometer and a microscope. 
    """)

    st.markdown("""
### 6. Prodedure

##### Enumeration
    """, unsafe_allow_html=True)

    st.code("""
5. Use the pipette to load the counting chambers
    a. Hold the pipette vertically  
    b. Position the tip of the pipette next to the cover glass (marked in Figure 5 with x) 
    c. Transfer 10-15 µL of one of your aliquotes to the counting chambers and let it be pulled underneath the cover glass by capillary forces  

6. Place the hemocytometer under the microscope 

7. Bring the lens with 40x magnification/ Phase 2 over the sample tray and select the phase-contrast filter “Phase 2” 

8. Adjust the focus of the microscope so that you can see the counting grid clearly 

9. Let the spores sediment for 3-5 min 

10. If there are less than 50 spores in one middle square continue with step 11. If there are more than 50 spores in one middle square, continue with step 11 (dilution).  

11. Dilution:  
    a. Label a 2 mL centrifugation tube with D-1.  
    b. Fill 900 µL DI-water into the tube (D-1) using pipette and pipette tips.  
    c. Vortex the sample container for 10 sec. 
    d. Add 100 µL sample aliquote from the sample container using the pipette and pipette tips.  
    e. Close the centrifugation tube and vortex for 10 sec (Dilution -1; Dilution factor = 1) 
    f. Label another 2 mL centrifugation tube with D-2.  
    g. Fill 900 µL DI-water into the tube (D-2) using pipette and pipette tips.  
    h. Add 100 µL aliquote of Dilution 1 (D-1) using the pipette and pipette tips.  
    i. Close the centrifugation tube and vortex for 10 sec (Dilution -2; Dilution factor = 2) 
    j. Repeat the steps above until < 50 spores are in one middle square.  
    k. Continue with step 12.  

    """, language=None, wrap_lines=True)

    dilution_factor = st.number_input("what dilution did you use 0, 1, or 2", value=0,)
    if dilution_factor == 0 or dilution_factor == 1 or dilution_factor == 2:
        st.badge(f"The current dilution is {dilution_factor}", color='green')
    else:
        st.badge(f"dilution factor can not be {dilution_factor}, try again", color='red')

    st.code("""
12. Count the spores within all 16 middle squares of the counting chamber using a handheld counter. This counts as one measurement replicate of one analytical replicate.  
    a. Start with the top left middle square and work your way down in a zig-zag pattern 
    b. ?????
    c. If mycelial fragments impair the vision in one or more middle square, exclude the spores in those middle squares from the overall count and note the number of middle squares counted for the final calculation.  

    """, language=None, wrap_lines=True)

    col1, col2 = st.columns(2)
    with col1:
        squares_counted = st.number_input("how many squares did you count in total", value=2)
        st.badge(f"squares_counted: {squares_counted}", color='green')
    with col2:
        spores_counted = st.number_input("how many spores did you count in total", value=78)
        st.badge(f"squares_counted: {spores_counted}", color='green')

    st.header("data for 1 replicate", divider='grey')
    df = pd.DataFrame([{
        'timestamp':datetime.now(),
        'dilution_factor':dilution_factor,
        'squares_counted':squares_counted,
        'spores_counted':spores_counted,
        }])
    #df = df.T
    st.dataframe(df)

    dfs = []
    if st.button("finalize replicate run"):
        engine = create_engine(str(os.environ['PSQL']).replace('postgres://', 'postgresql://'))
        df.to_sql("alejandro_test", if_exists='append', index=False, con=engine)


    st.header("data for ALL replicate", divider='grey')
    engine = create_engine(str(os.environ['PSQL']).replace('postgres://', 'postgresql://'))
    ddf = pd.read_sql(f""" SELECT 
            * from alejandro_test
            """, con=engine)
    ddf['timestamp'] = pd.to_datetime(ddf['timestamp'])
    ddf['spore_per_square_replicate'] = ddf['squares_counted'] / ddf['spores_counted']
    ddf['average_spore_of_middle_square'] = ddf['spore_per_square_replicate'].mean()
    st.write(ddf)

    #engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")
    #df.to_sql(f"alejandro_test", con=engine, index=False, if_exists='append')
    #st.write(df.head(3))

if __name__ == "__main__":

    main_app()

    show_code(main_app)
    