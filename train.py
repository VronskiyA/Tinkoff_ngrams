import argparse
import string
import random
import pickle

def tokenize(text):
    for s in string.punctuation.replace('.', ''):
        text = text.replace(s, '')
    text = text.replace('.', ' . ')
    text = text.lower()
    return text.split()

def get_ngrams(n, tokens):
    tokens = ['<begin>'] * (n-1) + tokens
    return [(tuple([tokens[i-p-1] for p in reversed(range(n-1))]), tokens[i]) for i in range(n-1, len(tokens))]
    
class NGramModel:
    def __init__(self, n):
        self.context = {}
        self.ngram_counter = {}
        self.n = n

    def fit(self, text):
        text = text.split('.')
        text.pop(-1)
        #print(text)
        for sentence in text:
            sentence += '.'
            #print(sentence)
            self.update(sentence)
    
    def update(self, sentence):
        ngrams = get_ngrams(self.n, tokenize(sentence))
        for ngram in ngrams:
            if ngram in self.ngram_counter:
                self.ngram_counter[ngram] += 1.0
            else:
                self.ngram_counter[ngram] = 1.0

            context_words, next_word = ngram
            if context_words in self.context:
                self.context[context_words].append(next_word)
            else:
                self.context[context_words] = [next_word]
        
    def prob(self, context, candidate):
        try:
            cnt_ngram = self.ngram_counter[(context, candidate)]
            cnt_context = float(len(self.context[context]))
            result = cnt_ngram / cnt_context

        except KeyError:
            result = 0.0
        return result

    def random_token(self, context):
        r = random.random()
        probs = {}
        candidates = self.context[context]
        for candidate in candidates:
            probs[candidate] = self.prob(context, candidate)

        summ = 0
        for candidate in sorted(probs):
            summ += probs[candidate]
            if summ >= r:
                return candidate

    def generate(self, cnt_token: int):
        #print(self.context)
        #print(self.ngram_counter)
        n = self.n
        context_queue = (n - 1) * ['<begin>']
        result = []
        for i in range(cnt_token):
            token = self.random_token(tuple(context_queue))
            result.append(token)
            if n > 1:
                context_queue.pop(0)
                if token == '.':
                    context_queue = (n - 1) * ['<begin>']
                else:
                    context_queue.append(token)
        return ' '.join(result).replace(' .', '.')
        

if __name__ == '__main__':
    text = ''
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=str, default='', help='.txt input file directory')
    parser.add_argument('--model', type=str, default='', help='.pkl output file directory')
    args = parser.parse_args()
    
    if args.input_dir != '':
        text = open(args.input_dir).read()
    else:
        text = input()
        
    model = NGramModel(4)
    model.fit(text)
    
    if args.model != '':
        pickle.dump(model, open(model, 'wb'))
    else:
        pickle.dump(model, open('model.pkl', 'wb'))
    print("Model saved.")
    