# homework 1
# goal: tokenize, index, boolean query
# exports: 
#   student - a populated and instantiated ir4320.Student object
#   Index - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents


# ########################################
# first, create a student object
# ########################################

import cs525
import PorterStemmer
import string
import re
import nltk
from nltk.tokenize import WordPunctTokenizer
import glob
import codecs



MY_NAME = "Jiani Gao"
MY_ANUM  = 206844103 # put your WPI numerical ID here
MY_EMAIL = "jgao4@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [ 
    ('Weixi Liu', 'helped me to solve a problem when using Python dictionary')
    ]

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "I do not lie, cheat or steal, or tolerate those who do."
I_AGREE_HONOR_CODE = True

# this defines the student object
student = cs525.Student(
    MY_NAME,
    MY_ANUM,
    MY_EMAIL,
    COLLABORATORS,
    I_AGREE_HONOR_CODE
    )


# ########################################
# now, write some code
# ########################################

# our index class definition will hold all logic necessary to create and search
# an index created from a directory of text files 
class Index(object):
    def __init__(self):
        # _inverted_index contains terms as keys, with the values as a list of
        # document indexes containing that term
        self._inverted_index = {}
        # _documents contains file names of documents
        self._documents = []
        # example:
        #   given the following documents:
        #     doc1 = "the dog ran"
        #     doc2 = "the cat slept"
        #   _documents = ['doc1', 'doc2']
        #   _inverted_index = {
        #      'the': [0,1],
        #      'dog': [0],
        #      'ran': [0],
        #      'cat': [1],
        #      'slept': [1]
        #      }

        # This dictionary is to help store the document indexes and the corresponding document name.
        # Key: document index; Value: corresponding document name
        self._doc_dic = {}
        


    # index_dir( base_path )
    # purpose: crawl through a nested directory of text files and generate an
    #   inverted index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: glob.glob()
    # parameters:
    #   base_path - a string containing a relative or direct path to a
    #     directory of text files to be indexed
    def index_dir(self, base_path):
        num_files_indexed = 0
        # PUT YOUR CODE HERE
        files = glob.glob(base_path)
        num_files_indexed = len(files)
        index = 0
        for file in files:
            f = codecs.open(file, encoding='UTF-8')
            filename = f.name.split("/")[-1].split(".")[0]
            text = f.read()
            f.close()
            self._documents.append(filename)
            self._doc_dic[index] = filename
            filtered_text = set(self.tokenize(text))
            stemmed_filtered_text = set(self.stemming(filtered_text))
            combined_text = filtered_text | stemmed_filtered_text
            for token in combined_text:
                if token not in self._inverted_index:
                    self._inverted_index[token] = []
                    self._inverted_index[token].append(index)
                else:
                    l = self._inverted_index.get(token)
                    if index not in l:
                        l.append(index)
            index += 1
        # print(self._inverted_index)
        # print(self._documents)
        # print(self._doc_dic)
        return num_files_indexed

    # tokenize( text )
    # purpose: convert a string of terms into a list of tokens.        
    # convert the string of terms in text to lower case and replace each character in text, 
    # which is not an English alphabet (a-z) and a numerical digit (0-9), with whitespace.
    # preconditions: none
    # returns: list of tokens contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        tokens = []
        r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_-`–{|}~]+'
        filtered_text = re.sub(r," ",text)
        filtered_text = filtered_text.lower()
        #print(filtered_text)
        unfiltered_tokens = WordPunctTokenizer().tokenize(filtered_text)
        stop_words = list(string.punctuation)
        tokens = [w for w in unfiltered_tokens if not w in stop_words]
        return tokens

    # purpose: convert a string of terms into a list of tokens.        
    # convert a list of tokens to a list of stemmed tokens,     
    # preconditions: tokenize a string of terms
    # returns: list of stemmed tokens
    # parameters:
    #   tokens - a list of tokens
    def stemming(self, tokens):
        stemmed_tokens = []
        stemmer = PorterStemmer.PorterStemmer()
        for token in tokens:
            stemmed_token = stemmer.stem(token, 0, len(token) - 1)
            # print(stemmed_token)
            stemmed_tokens.append(stemmed_token)
        return stemmed_tokens
    
    # boolean_search( text )
    # purpose: searches for the terms in "text" in our corpus using logical OR or logical AND. 
    # If "text" contains only single term, search it from the inverted index. If "text" contains three
    # terms including "or" or "and", 
    # do OR or AND search depending on the second term ("or" or "and") in the "text".  
    # preconditions: _inverted_index and _documents have been populated from
    #   the corpus.
    # returns: list of document names containing relevant search results
    # parameters:
    #   text - a string of terms
    def boolean_search(self, text):
        tokens = self.tokenize(text)
        results = []
        if len(tokens) == 1:
            results = self.token_search(tokens[0])
        else:
            token_list1 = set(self.token_search(tokens[0]))
            token_list2 = set(self.token_search(tokens[2]))
            if tokens[1] == "and":
                for doc in token_list1 & token_list2:
                    results.append(doc)
            else:
                for doc in token_list1 | token_list2:
                    results.append(doc)
        return results


    # This function helps to find the documents that contain the parameter token and the token stemmed from it.
    # return: a list of document names.
    def token_search(self, token):
        token_list = set()
        stemmed_token = self.stemming([token])
        if token in self._inverted_index.keys():
            for num in self._inverted_index[token]:
                    token_list.add(str(self._doc_dic.get(num)))
        if token != stemmed_token[0] and stemmed_token[0] in self._inverted_index.keys():
                for num in self._inverted_index[stemmed_token[0]]:
                    token_list.add(str(self._doc_dic.get(num)))
        return list(token_list)

# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):    
    print(student)
    index = Index()
    print("starting indexer")
    num_files = index.index_dir('data/*.txt')
    print("indexed %d files" % num_files)
    for term in ('football', 'mike', 'sherman', 'mike OR sherman', 'mike AND sherman'):
        results = index.boolean_search(term)
        print("searching: %s -- results: %s" % (term, ", ".join(results)))
    

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

