import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

st.sidebar.header('Input Patient Details')

st.markdown(
   """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 500px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with open('HeartFailure_classifier_RF.pkl', 'rb') as f:
    model = pickle.load(f)

age = st.sidebar.slider('Select Age ', 0, 100, 75)

anaemia = st.sidebar.selectbox("Has Anaemia (Yes, No)",["Yes","No"])

creatinine_phosphokinase = st.sidebar.number_input("Creatinine Phosphokinase(U/L)", 0, 10000, 582)

diabetes = st.sidebar.selectbox("Has Diabetes? (Yes, No)",["Yes","No"])

ejection_fraction = st.sidebar.number_input("Ejection Fraction(%)", 0, 100, 20)
    
high_blood_pressure = st.sidebar.selectbox(" Has High Blood Pressure? (Yes, No)",["Yes","No"])

platelets = st.sidebar.number_input("Platelets(mcL)", 0, 500000, 265000)

serum_creatinine = st.sidebar.number_input('Serum Creatinine(mg/dL)', 0.0, 10.0, 1.9)

serum_sodium = st.sidebar.number_input('Serum Sodium(mEq/L)', 0, 200, 130)

sex = st.sidebar.selectbox("Select Gender(Male, Female)",["Male","Female"])
    
smoking = st.sidebar.selectbox("Is Smoking? (Yes, No)",["Yes","No"])

time = st.sidebar.number_input('Time period in days', 0, 100000, 4)

#preprocess binary

if anaemia == 'Yes':
    anaemia = 1
else:
    anaemia = 0

if diabetes == 'Yes':
    diabetes = 1
else:
    diabetes = 0

if high_blood_pressure == 'Yes':
    high_blood_pressure = 1
else:
    high_blood_pressure = 0

if sex == 'Yes':
    sex = 1
else:
    sex = 0

if smoking == 'Yes':
    smoking = 1
else:
    smoking = 0


def prediction(age,anaemia,creatinine_phosphokinase,diabetes,ejection_fraction,high_blood_pressure,platelets,serum_sodium,serum_creatinine,sex,smoking,time):   
    # Making predictions 
    prediction = model.predict( 
        [[age,anaemia,creatinine_phosphokinase,diabetes,ejection_fraction,high_blood_pressure,platelets,serum_creatinine,serum_sodium,sex,smoking,time]])
     
    if prediction == 0:
        pred = 'No Chance of death'
    else:
        pred = 'Chance of Death'
    return pred

html_temp = """ 
    <div style ="background-color:#5dc9b6;padding:5px"> 
    <h1 style ="color:black;text-align:center;">Heart Failure Prediction Results</h1> 
    </div> 
    """
      
# display the front end aspect
st.markdown(html_temp, unsafe_allow_html = True) 

if st.sidebar.button("Predict"): 
    predval = prediction(age,anaemia,creatinine_phosphokinase,diabetes,ejection_fraction,high_blood_pressure,platelets,serum_sodium,serum_creatinine,sex,smoking,time)
    st.success(predval)

    heart_raw = pd.read_csv('heart_failure_clinical_records_dataset.csv')
    df = pd.DataFrame(heart_raw)

    st.title('Data Distribution')

    df1 = df.head(200)
    fig = px.scatter(df1, x="platelets", y="age",
    size="serum_creatinine", color="ejection_fraction",
    hover_name="age", log_x=True, size_max=30)
    st.plotly_chart(fig)


    normal_up = [500, 70, 150, 56.10]
    normal_down = [81, 20, 107, 1.0]
    current = [creatinine_phosphokinase,ejection_fraction,serum_sodium,serum_creatinine]

    names = ['creatinine phosphokinase', 'ejection fraction', 'serum sodium','serum_creatinine']

    li = [normal_up, normal_down, current]
    chart_data = pd.DataFrame({'Upper Limit': normal_up,
                                   'Lower Limit': normal_down,
                                   'Current Position': current})

    st.subheader('')

    st.title('Range of Safety')
    fig = go.Figure(data=[
    go.Bar(name='Upper Limit', x=names, y=normal_up),
    go.Bar(name='Lower Limit', x=names, y=normal_down),
    go.Bar(name='Current Position', x=names, y=current)])
    fig.update_layout(title={
            'text': "Range  of Safty ",
            'y': 0.9,
            'x': 0.4,
            'xanchor': 'center',
            'yanchor': 'top'}, font=dict(
            family="Courier New, monospace",
            size=13,
            color="black"
    ))
    st.plotly_chart(fig)

    st.title('Diabetes and Survival')

    labels = ['No Diabetes','Diabetes']
    diabetes_yes = heart_raw[heart_raw['diabetes']==1]
    diabetes_no = heart_raw[heart_raw['diabetes']==0]
    values = [len(diabetes_no), len(diabetes_yes)]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    st.plotly_chart(fig)

    surv = heart_raw[heart_raw['DEATH_EVENT']==0]['serum_creatinine']
    not_surv = heart_raw[heart_raw['DEATH_EVENT']==1]['serum_creatinine']
    hist_data = [surv,not_surv]
    group_labels = ['Survived', 'Not Survived']
    fig = ff.create_distplot(hist_data, group_labels, bin_size=0.5)
    fig.update_layout(
        title_text="Analysis in Serum Creatinine on Survival Status")
    st.plotly_chart(fig)

