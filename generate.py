import argparse
import string
import random
import pickle

class NGramModel:
    def __init__(self, n):
        self.context = {}
        self.ngram_counter = {}
        self.n = n

    def fit(self, path):
        with open(path) as f:
            text = f.read()
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
    parser.add_argument('--length', type=int, default=20, help='how many words will be generated')
    parser.add_argument('--model', type=str, default='', help='.pkl input file directory')
    args = parser.parse_args()
        
    
    loaded_model = pickle.load(open('model.pkl' if args.model == '' else model, 'rb'))
    print(loaded_model.generate(args.length))