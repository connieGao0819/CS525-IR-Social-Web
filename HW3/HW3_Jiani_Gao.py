# homework 4
# goal: ranked retrieval, PageRank, crawling
# exports:
#   student - a populated and instantiated cs525.Student object
#   PageRankIndex - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents and providing a
#     ranked result set

# ########################################
# first, create a student object
# ########################################

import cs525

MY_NAME = "Jiani Gao"
MY_ANUM  = 206844103 # put your UID here
MY_EMAIL = "jgao4@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = []

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "An Aggie does not lie, cheat or steal, or tolerate those who do."
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

# import bs4 as BeautifulSoup  # you will want this for parsing html documents
import urllib.request
from bs4 import BeautifulSoup
import re
import queue
import numpy as np
from numpy import *

# our index class definition will hold all logic necessary to create and search
# an index created from a web directory
#
# NOTE - if you would like to subclass your original Index class from homework
# 1 or 2, feel free, but it's not required.  The grading criteria will be to
# call the index_url(...) and ranked_search(...) functions and to examine their
# output.  The index_url(...) function will also be examined to ensure you are
# building the index sanely.

class PageRankIndex(object):
    def __init__(self):
        # you'll want to create something here to hold your index, and other
        # necessary data members

        self.url = ""
        self.url_index = {}
        self.content_index = {}
        self.corpus = set()
        self.page_rank = None


    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at
    def index_url(self, url):
        # ADD CODE HERE
        self.url = url
        self.corpus = self.set_corpus(url)
        q = queue.Queue()
        for link in self.corpus:
            q.put(link)
        while not q.empty():
            cur_html = q.get()
            if cur_html not in self.url_index:
                self.url_index[cur_html] = set()
                # build the index of content in each doc
                with urllib.request.urlopen(cur_html) as f:
                    html_doc = f.read().decode('utf-8')
                    doc_idx = cur_html.split("/")[-1].split(".")[0]
                    tokens = self.tokenize(html_doc)
                    for term in tokens:
                        if term not in self.content_index:
                            self.content_index[term] = set()
                        if doc_idx not in self.content_index[term]:
                            self.content_index[term].add(doc_idx)

                    # build the index of hyperlinks in each doc
                    soup = BeautifulSoup(html_doc, "html.parser")
                    for link in soup.find_all('a'):
                        link_url = url.replace(str(url.split("/")[-1]), str(link.get('href')))
                        self.url_index[cur_html].add(link_url)
                        if link_url in self.corpus and link_url not in self.url_index:
                            q.put(link_url)
        # print(self.url_index)
        # print(self.content_index)
        # print("num of documents indexed: %d" % len(self.corpus))
        return len(self.corpus)

    def set_corpus(self, url):
        self.corpus.add(url)
        with urllib.request.urlopen(url) as f:
            html = f.read().decode('utf-8')
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all('a'):
                link_url = url.replace(str(url.split("/")[-1]), str(link.get('href')))
                self.corpus.add(link_url)
        return self.corpus

    # tokenize( text )
    # purpose: convert a string of terms into a list of terms 
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        # ADD CODE HERE
        clean_string = re.sub('[^a-z0-9 ]', ' ', text.lower())
        tokens = clean_string.split()
        return tokens

    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms
    def ranked_search(self, text):
        # ADD CODE HERE
        self.rank_pages()
        tokens = self.tokenize(text)
        doc_set = set()
        for url in self.corpus:
            doc_set.add(url.split("/")[-1].split(".")[0])

        # retrieve the documents that contain all the terms in the query
        last_set = doc_set
        for token in tokens:
            current_set = set(self.content_index[token]).intersection(last_set)
            last_set = current_set

        # retrieve the top ranked documents
        page_dic = {}
        for page in current_set:
            page_url = self.url.replace(str(self.url.split("/")[-1].split(".")[0]), page)
            if page == "index":
                page_dic[page_url] = self.page_rank[0][0]
            else:
                page_dic[page_url] = self.page_rank[0][int(page[2]) + 1]
        page_dic = sorted(page_dic.items(), key=lambda item: item[1], reverse=True)
        if len(page_dic) > 10:
            return page_dic[0 : 10]
        return page_dic


    def rank_pages(self):

        # set up the Transition probability matrix
        mat_len = len(self.corpus)
        tp_matrix = zeros((mat_len, mat_len))
        for key in self.url_index:
            key_idx = self.get_page_index(key)
            value_num = len(self.url_index[key])
            for value in self.url_index[key]:
                if value in self.corpus:
                    value_idx = self.get_page_index(value)
                    tp_matrix[key_idx, value_idx] = 1 / value_num

        # set up the Teleporting Matrix
        teleporting_matrix = zeros((mat_len, mat_len))
        teleporting_matrix_value = 1 / mat_len
        for i in range(0, mat_len):
            for j in range(0, mat_len):
                teleporting_matrix[i][j] = teleporting_matrix_value

        # set up the Transition matrix with teleporting
        matrix = 0.1 * tp_matrix + 0.9 * teleporting_matrix

        # calculate the page rank
        initial_state = zeros((1, mat_len))
        initial_state[0][0] = 1
        current_state = initial_state
        next_state = np.dot(current_state, matrix)
        # while np.linalg.norm((next_state - current_state), 2) > 10 ** (-4):
        while not np.linalg.norm((next_state - current_state), 2) == 0:
            current_state = next_state
            next_state = np.dot(current_state, matrix)
        # print(next_state)
        self.page_rank = next_state
        return self.page_rank

    def get_page_index(self, url):
        idx = url.split("/")[-1].split(".")[0]
        if idx == "index":
            num_idx = 0
        else:
            num_idx = int(idx[2:]) + 1
        return num_idx


# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = PageRankIndex()
    url = 'http://web.cs.wpi.edu/~kmlee/cs525/new10/index.html'
    num_files = index.index_url(url)
    search_queries = (
       'palatial', 'college ', 'palatial college', 'college supermarket', 'famous aggie supermarket'
        )
    for q in search_queries:
        results = index.ranked_search(q)
        print("searching: %s -- results: %s" % (q, results))

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

