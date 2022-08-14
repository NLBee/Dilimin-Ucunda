from flask import Flask, render_template, url_for, request
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util


app = Flask(__name__)
df = pd.read_csv("filmler.csv")

# model ile daha önce oluşturulan embeddingleri alma
embeddings_df = pd.read_csv("distiluse-base-multilingual-cased-v2.csv")
description_embeddings = [embeddings_df.iloc[i].astype(np.float32) for i in range(len(df["başlık"]))]

# modeli tanımlama
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

@app.route('/', methods=["POST", "GET"])

def index():
    if request.method == "POST":
        desc = request.form["description"].lower()
        if desc.strip() == "":
            return render_template("index.html")
        results = get_results(df, model, desc, description_embeddings, 20)
        return render_template("results.html", desc=desc, result_list=results)
    else:
        return render_template("index.html")


def get_results(df, model, query, description_embeddings, k):
    query_embedding = model.encode(query)
    scores = np.array(util.cos_sim(query_embedding, description_embeddings)).reshape(-1)
    scores_with_index = list(enumerate(scores))
    scores_sorted = sorted(scores_with_index, key= lambda x: x[1])[::-1]
    results = [[df["başlık"][idx], df["tür"][idx], df["oyuncular"][idx], df["resim_link"][idx], df["vizyon_tarihi"][idx]] for idx, score in scores_sorted[0:k]]
    return results


@app.route('/nlbee')
def nlbee():
    return render_template("nlbee.html")

if __name__ == "__main__":
    app.run(debug=True)
