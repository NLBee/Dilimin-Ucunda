from flask import Flask, render_template, url_for, request
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import time
import torch
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)
df = pd.read_csv("beyazperde_sinemalar_birleşim.csv", index_col=False)

df["oyuncu+yönetmen"] = df["oyuncular_y"] + ", " + df["yönetmen_y"]
df = df.fillna("")

# model ile daha önce oluşturulan embeddingleri alma
embeddings_df = pd.read_csv("average_model4_embeddings4.csv", index_col=0)

model = AutoModelForTokenClassification.from_pretrained("savasy/bert-base-turkish-ner-cased")
tokenizer = AutoTokenizer.from_pretrained("savasy/bert-base-turkish-ner-cased")
ner = pipeline('ner', model=model, tokenizer=tokenizer)


model4_embeddings = torch.tensor([embeddings_df.iloc[i].astype(np.float32) for i in range(len(df["başlık"]))])

model4 = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2", device="cpu")

def scores(querry, description_embeddings, model):
    query_embeddings = torch.tensor(model.encode(querry))
    hits = util.semantic_search(query_embeddings, description_embeddings, score_function=util.dot_score, top_k=150)
    return hits



@app.route('/', methods=["POST", "GET"])

def index():
    if request.method == "POST":
        desc = request.form["description"].lower()
        if desc.strip() == "":
            return render_template("index.html")
        results = get_results(df, model, desc, model4_embeddings, 20)
        return render_template("results.html", desc=desc, result_list=results)
    else:
        return render_template("index.html")


def get_results(df, model, query, description_embeddings, k):
    score4 = scores(query, model4_embeddings, model4)
    score4_np = [i for i in score4[0]]

    indexes = [i["corpus_id"] for i in score4_np]

    movie_names = [np.array(df["başlık"])[i] for i in indexes]

    scores_np = np.array([i["score"] for i in score4_np]) / 1.8

    oyuncu_yönetmen = [np.array(df["oyuncu+yönetmen"])[i] for i in indexes]

    new_df = pd.DataFrame({"isim": movie_names, "score": scores_np, "oyuncu+yönetmen": oyuncu_yönetmen})

    ner_results = ner(query)

    array = []
    start = 0
    end = 0
    kontrol = 0
    for result in ner_results:
        if (result['entity'] == 'B-PER'):
            if kontrol == 0:
                kontrol += 1
                start = result['start']
                end = result['end']
            else:
                array.append(query[start:end])
                start = result['start']
                end = result['end']

        elif (result['entity'] == 'I-PER'):
            end = result['end']
    array.append(query[start:end])

    s = ''
    for x in array:
        s += " " + x

    s = s.strip()

    def create_dataframe(matrix, tokens):
        doc_names = [f'doc_{i + 1}' for i, _ in enumerate(matrix)]
        df = pd.DataFrame(data=matrix, index=doc_names, columns=tokens)
        return (df)

    idx = []
    values = []
    for x in range(len(new_df["isim"])):
        a = [new_df["oyuncu+yönetmen"][x], s]
        count_vectorizer = CountVectorizer()
        vector_matrix = count_vectorizer.fit_transform(a)
        tokens = count_vectorizer.get_feature_names()
        vector_matrix.toarray()
        create_dataframe(vector_matrix.toarray(), tokens)
        cosine_similarity_matrix = cosine_similarity(vector_matrix)
        cosine = (create_dataframe(cosine_similarity_matrix, [str(x), 'query']))
        scores_np[x] += 1.2 * cosine.iloc[0, 1]



    scores_with_index = list(zip(indexes, scores_np))


    scores_sorted = sorted(scores_with_index, key=lambda x: x[1])[::-1]


    results = [[df["başlık"][idx], df["tür_x"][idx], df["oyuncular_x"][idx], df["resim_link"][idx], df["vizyon_tarihi"][idx]] for idx, score in scores_sorted[0:k]]
    return results


@app.route('/nlbee')
def nlbee():
    return render_template("nlbee.html")

if __name__ == "__main__":
    app.run(debug=True)
