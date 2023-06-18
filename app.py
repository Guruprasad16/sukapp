from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
import openai
import requests
from flask import render_template
from pandas import DataFrame
# import tiktoken




app = Flask(__name__, static_folder='static')

# Stores the latest uploaded dataframe.
uploaded_data = None

@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_data
    file = request.files['file']
    if not file:
        return "No file"

    filename = "uploaded.xlsx"
    file.save(filename)

    uploaded_data = pd.read_excel(filename, sheet_name=None, header = None)
    sheets = list(uploaded_data.keys())

    return jsonify(sheets)

import numpy as np

@app.route('/sheet', methods=['POST'])
def select_sheet():
    global uploaded_data
    sheet = request.json['sheet']
    df = uploaded_data[sheet]
    df.columns = df.iloc[df.notnull().all(axis=1).idxmax()]
    df = df[df.index > df.columns.name]

    # Replace NaN values with null or a string representation
    df = df.replace({np.nan: None})  # Replace NaN with null
    # df = df.fillna('')  # Replace NaN with an empty string

    # Convert all data to strings
    df = df.astype(str)

    data_preview = df.head(5).to_dict(orient='records')
    column_names = df.columns.tolist()

    return jsonify({
        'data_preview': data_preview,
        'column_names': column_names
    })


    
    
unique_values_df = None


@app.route('/unique_values', methods=['GET', 'POST'])
def unique_values():
    global uploaded_data
    global unique_values_df

    if request.method == 'POST':
        sheet = request.json['sheet']
        column = request.json['column']
        df = uploaded_data[sheet]

        unique_values = df[column].unique().tolist()
        unique_values_df = pd.DataFrame(unique_values, columns=[column])

        # Convert unique values into a list of strings
        unique_values = [str(val) for val in unique_values]

        return render_template("unique_values.html", column_name=column, unique_values=unique_values)

    elif request.method == 'GET' and unique_values_df is not None:
        column = unique_values_df.columns[0]
        unique_values = unique_values_df[column].tolist()

        return render_template("unique_values.html", column_name=column, unique_values=unique_values)

    else:
        return "No unique values available."


@app.route('/column', methods=['POST'])
def select_column():
    global uploaded_data
    global unique_values_df
    sheet = request.json['sheet']
    column = request.json['column']
    df = uploaded_data[sheet]

    unique_values = df[column].unique()[1:].tolist()
    unique_values_df = DataFrame(unique_values, columns=[column])
    unique_values_count = df[column].nunique()/5


    return jsonify({"status": "success", "unique_values": unique_values, "unique_values_count": unique_values_count})
    
    
# Set up OpenAI API key and model

#OPENAI_API_KEY = "sk-mzrkqNYSwexV0Ol0FQtxMT3BlbkFJAprzTNUvJ0hl2u6cfdzyp"
OPENAI_API_KEY = "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"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
#os.environ['OPENAI_API_BASE'] = OPENAI_API_BASE
openai.api_key = os.getenv("OPENAI_API_KEY")
#openai.api_base = os.getenv("OPENAI_API_BASE")
#model_engine = "gpt-3.5-turbo"
model_engine = "text-davinci-003"
#model_engine = "text-curie-001"
#model_engine = "text-ada-001"
    

@app.route('/api', methods=['POST'])
def make_api_request():
    global unique_values_df
    global column
    
    prompt = request.json['prompt']
    prompt_tokens = len(prompt.split())*4
    print("This is your Tokens" + str(prompt_tokens))
    print("This is your prompt" + prompt)
    total_tokens = 4097
    max_tokens = int(total_tokens - prompt_tokens)
    
    
    # Call OpenAI GPT-3 API to generate the response
    
    response = openai.Completion.create(
        model=model_engine,
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        #stop=None,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["Human: ", "AI: "]
    )
   
    # Extract the response from the API
    response_text = response.choices[0].text.strip()

    return jsonify(response_text)


   



@app.route('/')
def home():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(port=5000)
