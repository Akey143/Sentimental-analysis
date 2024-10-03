from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import emoji
import random
import time
from docx import Document
import cleantext
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

# Define emoji mappings
emoji_mapping = {
    "positive": "🙂 Positive",
    "neutral": "😐 Neutral",
    "negative": "☹️ Negative"
}

# Function to analyze text sentiment
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "positive", emoji_mapping["positive"]
    elif sentiment == 0:
        return "neutral", emoji_mapping["neutral"]
    else:
        return "negative", emoji_mapping["negative"]

# Function to perform text analysis
def analyze_text(rawtext):
    start = time.time()
    summary = ''
    polarity_count = {"positive": 0, "neutral": 0, "negative": 0}

    if rawtext:
        sentiment, emoji = analyze_sentiment(rawtext)
        polarity_count[sentiment] += 1
        blob = TextBlob(rawtext)
        received_text = str(blob)
        words = blob.words
        number_of_tokens = len(words)
        nouns = [word for (word, tag) in blob.tags if tag == 'NN']
        summary = ', '.join(random.sample(nouns, min(len(nouns), 5))) if nouns else 'No nouns found'

    end = time.time()
    final_time = end - start

    return received_text, number_of_tokens, polarity_count, summary, final_time, emoji

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        text = request.form.get("text")
        if text:
            received_text, number_of_tokens, polarity_count, summary, final_time, emoji = analyze_text(text)
            return render_template("results.html", received_text=received_text, number_of_tokens=number_of_tokens,
                                   polarity_count=polarity_count, summary=summary, final_time=final_time, emoji=emoji)
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files.get("file")
    if uploaded_file:
        if uploaded_file.filename.endswith('.docx'):
            docx = Document(uploaded_file)
            received_text = '\n'.join([paragraph.text for paragraph in docx.paragraphs])
        elif uploaded_file.filename.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            received_text = df.to_string()

        received_text, number_of_tokens, polarity_count, summary, final_time, emoji = analyze_text(received_text)
        return render_template("results.html", received_text=received_text, number_of_tokens=number_of_tokens,
                               polarity_count=polarity_count, summary=summary, final_time=final_time, emoji=emoji)
    flash("No file uploaded or unsupported format.")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
