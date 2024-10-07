import spacy

class NLPProcessor:
    def __init__(self):
        self.nlp_fr = spacy.load("fr_core_news_sm")
        self.nlp_en = spacy.load("en_core_web_sm")

    def process_text(self, text, language):
        nlp = self.nlp_fr if language == 'fr' else self.nlp_en
        doc = nlp(text)
        return {
            'tokens': [token.text for token in doc],
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'noun_chunks': [chunk.text for chunk in doc.noun_chunks],
        }

    def calculate_similarity(self, text1, text2, language):
        nlp = self.nlp_fr if language == 'fr' else self.nlp_en
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        return doc1.similarity(doc2)