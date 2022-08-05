def indexing():
    from collections import defaultdict
    from array import array
    import os
    import json
    import math
    import nltk
    nltk.download('punkt')
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer
    from nltk.corpus import stopwords
    import os
    import json

    def pre_processing(doc):
        print("-----inside pre pro-----")
        stop_words = stopwords.words('english')
        stemmer = PorterStemmer()
        doc = doc.replace('-', "\t")
        tokens = word_tokenize(doc.lower())
        word_list = [ word for word in tokens if word.isalpha() ]
        big_words = [ word for word in word_list if len(word) > 2 ]
        good_words = [ ]
        for w in big_words:
            if w not in stop_words:
               good_words.append(stemmer.stem((w)))
        return (good_words)

    def load_data_fromjson() -> dict:
        if os.path.isfile(os.path.join("data", "output.json")):
            with open(os.path.join("data", "output.json"), "r") as read_file:
                print("----data loaded----")
                return json.load(read_file)
        return dict()

    print("Loading data from json for for indexing")
    data = load_data_fromjson()
    class Index_dic:
        def __init__(self):
            self.index = defaultdict(list)
            self.title = {}
            self.termfreq = defaultdict(list)
            self.docfreq = defaultdict(int)
            self.doccount = 0
            print("---indexing--priyanka---")

        def write_data_tofile(self):
            print("Writing index to the file ")
            f = open(os.path.join("data","index.txt"),"w")
            f.write(str(self.doccount) + '\n')
            for term in self.index.keys():
                docIdList=[]
                for p in self.index[ term ]:
                    docIdList.append(str(p[0]))
                posting_data = ';'.join(docIdList)
                tfData = ','.join(map(str, self.termfreq[ term ]))
                idfData = '%.4f' % (math.log((self.doccount / self.docfreq[ term ]), 10))
                f.write('|'.join((term, posting_data, tfData, idfData)) + '\n')

            f.close()


    self=Index_dic()
    print("Data pre-processing started")
    print("---print len docid---")
    len_doc = len(data["doc_id"])
    for docNum in range(0,(len_doc-1)):

        terms = pre_processing(data['content'][docNum])
        term_dict_page = {}
        for position, term in enumerate(terms):
            try:
                term_dict_page[term][1].append(position)
            except:
                term_dict_page[term] = [docNum, array('I', [position])]

        for term, posting in term_dict_page.items():
            self.termfreq[term].append('%.4f' % (math.log(len(posting[ 1 ]) + 1, 10)))
            self.docfreq[ term ] += 1
        for dic_term, term_postings in term_dict_page.items():
            self.index[ dic_term ].append(term_postings)
        self.doccount += 1
    print("Data pre-processing completed")
    print("Index created ")
    self.write_data_tofile()