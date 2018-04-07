# homework 4
# goal: k-means clustering on vectors of TF-IDF values,
#   normalized for every document.
# exports: 
#   student - a populated and instantiated cs525.Student object
#   Clustering - a class which encapsulates the necessary logic for
#       clustering a set of documents by tf-idf 


# ########################################
# first, create a student object
# ########################################

import cs525
MY_NAME = "Jiani Gao"
MY_ANUM  = 206844103 # put your UID here
MY_EMAIL = "jgao4@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [ 
    ]

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


# Our Clustering object will contain all logic necessary to crawl a local
# directory of text files, tokenize them, calculate tf-idf vectors on their
# contents then cluster them according to k-means. The Clustering class should
# select r random restarts to ensure getting good clusters and then use RSS, an
# internal metric, to calculate best clusters.  The details are left to the
# student.

import re
from glob import glob
import numpy as np
from numpy import *
import sys

class Clustering(object):
    # hint: create something here to hold your dictionary and tf-idf for every
    #   term in every document
    def __init__(self):
        self._index = {}
        self._documents = []
        self._tdidf_vecs = {}

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

    def index_dir(self, base_path):
        num_files_indexed = 0
        for fn in glob("%s/*" % base_path):
            if fn not in self._documents:
                self._documents.append(fn)
            num_files_indexed += 1
            for line in open(fn,encoding="utf8"):
                doc_idx = self._documents.index(fn)
                for t in self.tokenize(line):
                    if t not in self._index:
                        self._index[t] = set()
                    if doc_idx not in self._index[t]:
                        self._index[t].add(doc_idx)
        # print(self._documents)
        # print(self._index)
        return num_files_indexed

    # Clean the path and get files name
    def get_doc_name(self, path):
        return path.split("/")[-1].split(".")[0]

    # Calculate the term frequency in a document of a term
    def cal_term_freq(self, term, fn):
        term_freq = 0
        for line in open(fn, encoding="utf8"):
            for t in self.tokenize(line):
                if t == term:
                    term_freq += 1
        return term_freq

    # Calculate TF-IDF for each document in a collection
    def cal_tfidf(self):
        n = len(self._documents)
        for fn in self._documents:
            doc_idx = self._documents.index(fn)
            fn_vector = zeros((1, len(self._index)))
            i = 0
            for t in self._index:
                term_freq = self.cal_term_freq(t, fn)
                df = len(self._index[t])
                if term_freq == 0:
                    weight = log2(n / df)
                else:
                    weight = (1 + log2(term_freq)) * log2(n / df)
                fn_vector[0][i] = weight
                i += 1
            self._tdidf_vecs[doc_idx] = fn_vector.tolist()
        # print(self._tdidf_vecs)
        return self._tdidf_vecs


    # consume_dir( path, k )
    # purpose: accept a path to a directory of files which need to be clustered
    # preconditions: none
    # returns: list of documents, clustered into k clusters
    #   structured as follows:
    #   [
    #       [ first, cluster, of, docs, ],
    #       [ second, cluster, of, docs, ],
    #       ...
    #   ]
    #   each cluster list above should contain the document name WITHOUT the
    #   preceding path.  JUST The Filename.
    # parameters:
    #   path - string path to directory of documents to cluster
    #   k - number of clusters to generate
    def consume_dir(self, path, k):
        import random
        self.index_dir(path)
        self.cal_tfidf()
        n = len(self._documents)
        min_rss = sys.maxsize
        max_times = 10
        for i in range(int(log2(n))):
            # randomly choose k centroids from documents
            list = random.sample(range(n), k)
            centroid_list = []
            for indx in list:
                centroid_list.append(self._tdidf_vecs[indx])
            cluster_list = self.get_docs_by_centroids(centroid_list)
            centroid_list = self.recalculate_centroid(cluster_list)
            last_rss = self.cal_rss(cluster_list, centroid_list)
            for times in range(max_times):
                cluster_list = self.get_docs_by_centroids(centroid_list)
                centroid_list = self.recalculate_centroid(cluster_list)
                rss = self.cal_rss(cluster_list, centroid_list)
                if last_rss == rss:
                    break
                last_rss = rss
            if rss < min_rss:
                min_rss = rss
                result = cluster_list
        result_doc = []
        for l in result:
            doc_names = []
            for doc_idx in l:
                doc_names.append(self.get_doc_name(self._documents[doc_idx]))
            result_doc.append(doc_names)

        print(result_doc)

    def difference(self, last_list, centroid_list):
        difference = 0
        for i in range(len(last_list)):
            last_vec = last_list[i]
            cur_vec = centroid_list[i]
            difference += np.linalg.norm((np.array(cur_vec) - np.array(last_vec)), 2)
        return difference

    # Calculate the RSS
    def cal_rss(self, cluster_list, centroid_list):
        rss = 0
        for i in range(len(centroid_list)):
            centroid = centroid_list[i]
            docs = cluster_list[i]
            rssk = 0
            for doc in docs:
                rssk += np.linalg.norm((np.array(centroid) - np.array(self._tdidf_vecs[doc])), 2) ** 2
            rss += rssk
        return rss

    # Assign documents to clusters
    def get_docs_by_centroids(self, centroid_list):
        temp_dic = {}
        for doc in self._tdidf_vecs.keys():
            min_distance = sys.maxsize
            for centroid in centroid_list:
                distance = np.linalg.norm((np.array(centroid) - np.array(self._tdidf_vecs[doc])), 2)
                if distance < min_distance:
                    min_distance = distance
                    doc_centroid = centroid
            centroid_index = centroid_list.index(doc_centroid)
            if centroid_index not in temp_dic.keys():
                temp_dic[centroid_index] = []
            temp_dic[centroid_index].append(doc)
        return list(temp_dic.values())

    # recalculate centroids of each cluster
    def recalculate_centroid(self, cluster_list):
        centroid_list = []
        for list in cluster_list:
            vector = zeros((1, len(self._index)))
            for doc in list:
                doc_vect = np.array(self._tdidf_vecs[doc])
                vector += doc_vect
            centroid = (1 / len(list)) * vector
            centroid_list.append(centroid.tolist())
        return centroid_list

# now, we'll define our main function which actually starts the clusterer
def main(args):
    print(student)
    clustering = Clustering()
    print("test 10 documents")
    print(clustering.consume_dir('test10/', 5))
    print("test 50 documents")
    print(clustering.consume_dir('test50/', 5))


# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

