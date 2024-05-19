import streamlit as st

st.write("Ahoj Kateřino")
# st.button('Hit me')
# st.checkbox('Check me out')
# st.radio('Pick one:', ['nose','ear'])
# st.selectbox('Select', [1,2,3])
# st.multiselect('Multiselect', [1,2,3])
# st.slider('Slide me', min_value=0, max_value=10)
# st.select_slider('Slide to select', options=[1,'2'])
# st.text_input('Enter some text')
# st.number_input('Enter a number')
# st.text_area('Area for textual entry')
# st.date_input('Date input')
# st.time_input('Time entry')
# st.file_uploader('File uploader')
# st.color_picker('Pick a color')
#
#
# st.text('Fixed width text')
# st.markdown('_Markdown_') # see #*
# st.caption('Balloons. Hundreds of them...')
# st.latex(r''' e^{i\pi} + 1 = 0 ''')
# st.write('Most objects') # df, err, func, keras!
# st.write(['st', 'is <', 3]) # see *
# st.title('My title')
# st.header('My header')
# st.subheader('My sub')
# st.code('for i in range(8): foo()')
#
# # Insert containers separated into tabs:
# tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
# tab1.write("this is tab 1")
# tab2.write("this is tab 2")

import streamlit as st

# Conversion functions
def convert_length(value, from_unit, to_unit):
    conversion_factors = {
        'meters': 1,
        'feet': 3.28084,
        'inches': 39.3701,
        'kilometers': 0.001,
        'miles': 0.000621371
    }
    return value * conversion_factors[from_unit] / conversion_factors[to_unit]

def convert_weight(value, from_unit, to_unit):
    conversion_factors = {
        'kilograms': 1,
        'grams': 0.001, # 1 gram = 0.001 kilograms
        'pounds': 0.453592, # 1 pound = 0.453592 kilograms
        'ounces': 0.0283495 # 1 ounce = 0.0283495 kilograms
    }
    value_in_kg = value * conversion_factors[from_unit]
    return value_in_kg / conversion_factors[to_unit]

def convert_temperature(value, from_unit, to_unit):
    if from_unit == 'Celsius' and to_unit == 'Fahrenheit':
        return value * 9/5 + 32
    elif from_unit == 'Fahrenheit' and to_unit == 'Celsius':
        return (value - 32) * 5/9
    elif from_unit == 'Celsius' and to_unit == 'Kelvin':
        return value + 273.15
    elif from_unit == 'Kelvin' and to_unit == 'Celsius':
        return value - 273.15
    elif from_unit == 'Fahrenheit' and to_unit == 'Kelvin':
        return (value - 32) * 5/9 + 273.15
    elif from_unit == 'Kelvin' and to_unit == 'Fahrenheit':
        return (value - 273.15) * 9/5 + 32
    else:
        return value

# Streamlit app
st.title("Unit Converter")

conversion_type = st.selectbox("Select conversion type:", ["Length", "Weight", "Temperature"])

if conversion_type == "Length":
    value = st.number_input("Enter the value:")
    from_unit = st.selectbox("From unit:", ["meters", "feet", "inches", "kilometers", "miles"])
    to_unit = st.selectbox("To unit:", ["meters", "feet", "inches", "kilometers", "miles"])
    result = convert_length(value, from_unit, to_unit)
    st.write(f"{value} {from_unit} is equal to {result:.2f} {to_unit}")

elif conversion_type == "Weight":
    value = st.number_input("Enter the value:")
    from_unit = st.selectbox("From unit:", ["kilograms", "grams", "pounds", "ounces"])
    to_unit = st.selectbox("To unit:", ["kilograms", "grams", "pounds", "ounces"])
    result = convert_weight(value, from_unit, to_unit)
    st.write(f"{value} {from_unit} is equal to {result:.2f} {to_unit}")

elif conversion_type == "Temperature":
    value = st.number_input("Enter the value:")
    from_unit = st.selectbox("From unit:", ["Celsius", "Fahrenheit", "Kelvin"])
    to_unit = st.selectbox("To unit:", ["Celsius", "Fahrenheit", "Kelvin"])
    result = convert_temperature(value, from_unit, to_unit)
    st.write(f"{value} {from_unit} is equal to {result:.2f} {to_unit}")
