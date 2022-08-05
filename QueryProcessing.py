def query_processing(query):
    import os
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer
    from nltk.corpus import stopwords
    from collections import defaultdict
    from operator import itemgetter

    stop_words = stopwords.words('english')
    empty_list = []

    class query_index:
        def __init__(self):
            self.index = {}
            self.titleIndex = {}
            self.term_freq = {}
            self.inverse_doc_freq = {}
            self.doc_count = 0

        def write_to_file(self, result):
            fileWrite = open(os.path.join("data", "Results.txt"), 'w')
            for i in result:
                st = str(i) + '\n'
                fileWrite.write(st)

        def read_indexfile(self):
            print("Reading data from index file")
            f = open(os.path.join("data", "index.txt"), 'r')
            self.doc_count = int(f.readline().rstrip())

            for line in f:
                line = line.rstrip()
                term, doc_ids, term_freq, inverse_doc_freq = line.split('|')
                doc_ids = doc_ids.split(';')
                postings = [int(x) for x in doc_ids]
                self.index[term] = postings
                term_freq = term_freq.split(',')
                self.term_freq[term] = [float(i) for i in term_freq]
                self.inverse_doc_freq[term] = float(inverse_doc_freq)

            print("Index file reading completed")

        def rank_documents(self, query_terms, doc_id):
            doc_vectors = defaultdict(lambda: [0] * len(query_terms))
            for term_order, term in enumerate(query_terms):
                if term not in self.index:
                    continue

                for docIndex, doc in enumerate(self.index[term]):
                    if doc in doc_id:
                        doc_vectors[doc][term_order] = self.term_freq[term][docIndex] * self.inverse_doc_freq[term]

            doc_scores = [[sum(curDocVec), doc_id] for doc_id, curDocVec in
                          doc_vectors.items()]

            sorted_docs = sorted(doc_scores, key=itemgetter(0), reverse=True)
            result_docid = [x[1] for x in sorted_docs][:20]
            self.write_to_file(result_docid)

        def query_index_rank(self, query_terms, query):
            if (len(query_terms)) == 1:
                if query_terms[0] not in self.index:
                    print(f'Search -{query} - did not match any documents. Try more general or different keywords')
                    self.write_to_file(empty_list)
                else:
                    docid_list = self.index[query_terms[0]]
                    self.rank_documents(query_terms, docid_list)
            else:
                id_list = []
                for term in query_terms:
                    if term in self.index:
                        postings = self.index[term]
                        if (len(id_list) == 0):
                            id_list = postings
                        else:
                            id_list = id_list + postings
                if len(id_list) == 0:
                    print(f'Search -{query} - did not match any documents. Try more general or different keywords')
                    self.write_to_file(str(empty_list))
                else:
                    self.rank_documents(query_terms, id_list)

    def preprocess_query(query):
        stemmer = PorterStemmer()
        query = query.replace('-', "\t")
        tokens = word_tokenize(query.lower())
        word_list = [word for word in tokens if word.isalpha()]
        big_words = [word for word in word_list if len(word) > 2]
        good_words = []
        for w in big_words:
            if w not in stop_words:
                good_words.append(stemmer.stem((w)))
        return (good_words)

    q = query_index()
    q_terms = preprocess_query(query)
    print(q_terms)
    if len(q_terms) == 0:
        print(f'Search -{query} - did not match any documents. Try more general or different keywords')
        q.write_to_file(str(empty_list))
    else:
        q.read_indexfile()
        q.query_index_rank(q_terms, query)