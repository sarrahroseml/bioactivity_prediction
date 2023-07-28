#Import modules

import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle 



#def desc_calc():
    #bashCommand = "java -Xms1G -Xmx1G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    #subprocess.Popen is a function that can execute a command in a new process. 
    #stdout=subprocess.PIPE means that the output of the command will be piped to a special location that can be accessed by the Python script
    #process = subprocess.Popen(bashCommand.split(),stdout=subprocess.PIPE)
    #Waits for the process to complete. 
    # If the process ends by producing an error, that error is captured and stored in output.error.
    #output,error = process.communicate()
    #Removes the file molecule.smi from the current directory
    #os.remove('molecule.smi')


def desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

#File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download = "prediction.csv">Download Predictions</a>'
    return href 

def build_model(input_data):
    load_model = pickle.load(open('acetylcholinesterase_model.pkl', 'rb'))
    prediction = load_model.predict(input_data)
    st.header('**Prediction output**')
    #Creating a panda series of predictions of pIC50 values
    prediction_output = pd.Series(prediction, name='pIC50')
    #Creating another panda series from 2nd col of load_data obj
    molecule_name= pd.Series(load_data[1],name='molecule_name') #Chembl ID
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    #Creating a download link for the output CSV file 
    st.markdown(filedownload(df),unsafe_allow_html=True)

image = Image.open('logo.png')
st.image(image, use_column_width=True)

st.markdown("""
# Bioactivity Prediction App (Acetylcholinesterase)

This app allows you to predict the bioactivity towards inhibiting the Acetylcholinesterase enzyme.
            Acetylcholinesterase is a drug target for Alzheimer's disease
            """)

#Sidebar

with st.sidebar.header('1. Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type = ['txt'])
    st.sidebar.markdown("""
[Example input file]  #Insert here                      
    """)

#Creates predict button
if st.sidebar.button('Predict'):

    #Reads in user-inputted file and converts into a csv file 'molecule_smi'
    load_data= pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule_smi',sep = '\t',header= False, index= False)

    if os.path.isfile('molecule.smi'):
        os.remove('molecule.smi')
    else:
        st.write("File molecule.smi does not exist")

    #Displays user-inputted data on main webpage in a table format
    st.header('**Original Input Data**')
    st.write(load_data)

    #Spinner object (yellow message box) while calculating
    with st.spinner("Calculating descriptors..."):
        desc_calc()

    #Read in calculated descriptors and display df
    st.header('**Calculated molecular descriptors**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape) #display the shape 

    #Using the subset of descriptors from previously_built model
    st.header('**Subset of descriptors from previously built model')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    #Apply trained model to make a prediction on a query compound
    build_model(desc_subset)
else:
    st.info('Upload input data in sidebar to start!')
    
