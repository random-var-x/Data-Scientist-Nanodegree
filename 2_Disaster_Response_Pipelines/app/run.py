import json
import plotly
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar, Heatmap
from sklearn.externals import joblib
from sqlalchemy import create_engine

app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens

# load data
engine = create_engine('sqlite:///../data/disaster_response.db')
df = pd.read_sql_table('disaster_response', engine)

# load model
model = joblib.load("../models/classifier.pkl")

# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    category = df.drop(['id', 'message', 'original', 'genre'], axis=1).astype(float)
    category_names = category.columns.values
    category_counts = [sum(category[x]) for x in category_names]
    corr = df.corr()
    labels = df.columns.values[:-3] # Too many to show all...
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=category_names,
                    y=category_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Message Categories',
                'xaxis': {
                    'title': "Genre",
                },
                'yaxis': {
                    'title': "Count",
                },
                'margin': dict(
                    l = 70,
                    r = 30, 
                    b = 180,
                    t = 30,
                    pad = 2
                    ),
            }
        },
        {
            'data': [
                Heatmap(
                    z=corr.values,
                    x=labels,
                    y=labels
                )
            ],

            'layout': {
                'title': 'Category Correlation',
                'height': 800,
                'margin': dict(
                    l = 150,
                    r = 30, 
                    b = 160,
                    t = 30,
                    pad = 4
                    ),
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '') 

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file. 
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
