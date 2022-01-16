from bs4 import BeautifulSoup
import re
import time
import os
from ast import literal_eval # pandas store list as string; need to convert back
from collections import Counter
import numpy as np

import pandas as pd
pd.set_option('max_colwidth',None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 0)

import spacy
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher


# !pip install wordcloud
from wordcloud import WordCloud
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


# Source: file:///C:/Users/clair/Desktop/Thesis/masterThesis2022/Model/2.%20Preprocessing_part2.html
def identify_MDA(file_name, save=True):
    """save the raw text of identifyed MDA section in a txt file"""

    with open(file_name) as f:
        soup_html = BeautifulSoup(f, 'html.parser')

    # CAN'T remove all tables first since ITEM 7. Management... is sometimes wrapped in a table...
    for table in soup_html.find_all('table'):
        if len(table.find_all('tr')) > 3:
            table.decompose()

    soup_text = soup_html.get_text(strip=False,separator=' ')  # keep sentences from different spans separated with a space
    # soup_text = soup_html.get_text(strip=True)
    # soup_text = soup_text.replace('\xa0', '').replace('\n', '')

    pattern_toc = re.compile(r"(table of contents)|(index)", flags=re.IGNORECASE)
    toc = re.search(pattern_toc, soup_text)
    ix = len(soup_html.find_all('ix:header'))

    pattern_start = re.compile(
        r"(?<![\"|“|'])Item\s?\d?.?\s*Management[’|\']s[\s]*Discussion[\s]*and[\s]*Analysis[\s]*of[\s]*Financial[\s]*Condition[\s]*and[\s]*Results[\s]*of[\s]*Operations",
        flags=re.IGNORECASE)  # Management's Discussion and Analysis of")
    starts = [*re.finditer(pattern_start, soup_text)]

    if len(starts) == 0:
        pattern_start = re.compile(
            r"(?<![\"|“|'])Management[’|']s[\s]*Discussion[\s]*and[\s]*Analysis[\s]*of[\s]*Financial[\s]*Condition[\s]*and Results[\s]*of[\s]*Operations",
            flags=re.IGNORECASE)  # Management's Discussion and Analysis of")
        starts = [*re.finditer(pattern_start, soup_text)]

    if len(starts) == 1:
        start = starts[0].start()

    elif len(starts) > 1:
        if toc:
            start = starts[1].start()
        else:
            start = 0
    #            print('\n>>>>>>NO TOC and MORE THAN 1 START POSITIONS!!!<<<<<<\n')

    else:
        start = 0
    #        print('\n>>>>>>COULD NOT FIND ANY START POSITION!!!<<<<<<\n')

    pattern_end = re.compile(
        r"(?<![\"|“|'])Item\s?\d[A-Z]?.?\s*Quantitative[\s]*and[\s]*Qualitative[\s]*Disclosure[s]?[\s]*about[\s]*Market",
        flags=re.IGNORECASE)
    ends = [*re.finditer(pattern_end, soup_text)]
    if len(ends) == 0:
        pattern_end = re.compile(
            r"(?<![\"|“|'])Quantitative[\s]*and[\s]*Qualitative[\s]*Disclosure[s]?[\s]*about[\s]*Market",
            flags=re.IGNORECASE)
        ends = [*re.finditer(pattern_end, soup_text)]

    if len(ends) == 1:
        end = ends[0].start()

    elif len(ends) > 1:
        if toc:
            end = ends[1].start()
        else:
            for i in range(len(ends)):  ### CORRECTION HERE!
                if ends[i].start() > start + 10000:
                    end = ends[i].start()
                    break
    #                print('\n>>>>>>NO TOC and MORE THAN 1 END POSITIONS!!!<<<<<<\n')

    else:
        end = 0

    if save and start != 0 and end != 0:
        raw_mda = soup_text[start:end]
        save_file = file_name[:file_name.rfind('/') + 1] + 'raw_mda.txt'
        with open(save_file, 'w') as f:
            f.write(raw_mda)
    else:
        raw_mda = None

    return ix, start, end, raw_mda


def get_filename(download_path, ticker, type_, doc):
    """
    download_path: str, where the downloaded documents are saved
    ticker: str, company's unique ticker
    type: '10-K' or '10-Q'
    doc: name of the folder (cik-yy-num) where the document filing_details.html are saved
    return: file_name pointing to the document
    """
    folder = download_path + ticker + "/" + type_ + "/" + doc + "/"
    file = os.listdir(folder)[0]
    file_name = folder + "/" + file

    return file_name


def process_doc(df_company, download_path, save_path):
    """
    ### Transform df_company (each row represents a company) into df_doc (each row represents a document)
    ### identify MD&A section and save as raw.txt in the same folder
    df_company: master df with ticker as index
    download_path: where the downloaded financial documents are saved
    """
    df_company.set_index('ticker',inplace=True)
    temp = []

    for ticker in df_company.index:
        for doc in literal_eval(df_company.loc[ticker, '10K_files']):
            if len(doc) != 0:
                d = {}
                type_ = '10-K'
                d['ticker'] = ticker
                d['type'] = type_
                d['file'] = doc
                _,year,num = doc.split('-')
                d['year'] = year
                d['num'] = num
                file_name = get_filename(download_path,ticker,type_,doc)
                d['ix'], d['start'], d['end'],raw = identify_MDA(file_name)
                temp.append(d)

        for doc in literal_eval(df_company.loc[ticker, '10Q_files']):
            if len(doc) != 0:
                d = {}
                type_ = '10-Q'
                d['ticker'] = ticker
                d['type'] = type_
                d['file'] = doc
                _,year,num = doc.split('-')
                d['year'] = year
                d['num'] = num
                file_name = get_filename(download_path, ticker, type_, doc)
                d['ix'], d['start'], d['end'], raw = identify_MDA(file_name)
                temp.append(d)

    df_doc = pd.DataFrame(temp)
    df_doc.to_pickle(save_path + 'df_doc.pkl')

    return df_doc






# set spacy model parameters

nlp = spacy.load("en_core_web_lg")
#nlp.select_pipes(disable=["ner"]) # excluding any of the others won't work


causal_indicators = {'CvE':['drive', 'affect', 'impact', 'cause', 'result','attribute'],
                     'EvC':['reflect'], 'nonverbs':['due to', 'because','since','attributable to']}

matcher_verbs = Matcher(nlp.vocab)
for k in ['CvE','EvC']:
    pattern=[]
    pattern.append({'LEMMA': {'IN':causal_indicators[k]}, 'POS': 'VERB'})
    matcher_verbs.add(k, [pattern])

matcher_nonverbs = PhraseMatcher(nlp.vocab, attr="LEMMA") # need token.lemma_ = token.lemma_.lower()
for k in ['nonverbs']:
    nonverb_patterns = [nlp(x) for x in causal_indicators[k]]
    matcher_nonverbs.add(k, nonverb_patterns)

topics = ['revenue','sale','cost','margin','profit','income'] #,'business','market demand'] # AS NOUNS
matcher_topics = PhraseMatcher(nlp.vocab, attr="LEMMA") # need token.lemma_ = token.lemma_.lower()
topic_patterns = [nlp(topic) for topic in topics]
matcher_topics.add("topics", topic_patterns)



def filter_(text, matcher_topics, matcher_verbs,matcher_nonverbs ):
    """check if the input fulfills the following criteria:
        - is a full sentence i.e. filter off headings, page numbers, bullet points, etc.
        - casual indicator is present - likely to contain a causal relationship
        - contains words in the topic of interest - narrow down the search space
    """

    # nlp = spacy.load("en_core_web_sm", exclude=["ner"])
    if isinstance(text, str):
        if len(text)<50 or len(text) > 500:
            return # reject raw text which is too short or too long
        sent = nlp(text)

    if sent[:].root.pos_ != 'VERB' and sent[:].root.pos_ != 'AUX' :
        return  # discard if not a full sentence

    causal = []
    causal.extend(matcher_verbs(sent))
    causal.extend(matcher_nonverbs(sent))

    if len(causal) == 0:
        return  # discard if none of the causal indicators are present

    topic = matcher_topics(sent)
    if len(topic) == 0:
        return

    d = {'sent': sent, 'topic':[], 'causal': {},'idx':[]}
    for y in topic:
        d['topic'].append(sent[y[1]:y[2]].text)
    for x in causal:
        if x[2] == len(sent):
            continue
        if nlp.vocab.strings[x[0]] not in d['causal'].keys():
            d['causal'][nlp.vocab.strings[x[0]]] = [(sent[x[1]:x[2]].text,sent[x[1]:x[2]][0].tag_, (sent[x[1]].i, sent[x[2]].i))] #sent[start:end] is a span, to get the token = span[0]
        else:
            d['causal'][nlp.vocab.strings[x[0]]].extend([(sent[x[1]:x[2]].text,sent[x[1]:x[2]][0].tag_, (sent[x[1]].i, sent[x[2]].i))]) #sent[start:end] is a span, to get the token = span[0]
        d['idx'].append((x[1],x[2]))

    d['idx'].sort() #ascending order in place

    return d


def locate_boundary(all_idx, current_idx):
    start = 0
    end = -1
    # Case 1: only one
    if len(all_idx) == 1:
        return (start,end)

    i = all_idx.index(current_idx)
    # Case 2: the first one
    if i == 0:
        end = all_idx[i+1][0]
        return (start,end)
    # Case 3: the last one
    if i == len(all_idx)-1:
        start = all_idx[i-1][-1]
        return (start, end)

    # Case 4: anything in between
    start = all_idx[i - 1][-1]
    end = all_idx[i + 1][0]
    return (start, end)



def extract_(d):
    sent = d['sent']
    EC_pairs = []
    for k in d['causal'].keys():
        for v in d['causal'][k]:
            start, end = locate_boundary(d['idx'], v[2])
            if (k == 'CvE' and v[1] == 'VBN') or (k == 'EvC' and v[1] != 'VBN') or k == 'nonverbs': # VBN: past participle
                cause = sent[v[2][-1]:end].text
                effect = sent[start:v[2][0]].text
                #print('if... >> causal=',v[0],' >> effect=',effect,' >> cause=',cause)
            else:
                cause = sent[start:v[2][0]].text
                effect = sent[v[2][-1]:end].text
                #print('else... >> causal=',v[0],' >> effect=',effect,' >> cause=',cause)
            EC_pairs.append((effect, cause))
    return EC_pairs


def model_(text):
    """
        text: raw text string, a sentence or a segment of a sentence
        return: a model with nodes representing nouns and noun-phrases (noun_chunks stripped of adj det, etc.), links representing everything in between two noun phrases (including adj. verb, etc)
    """
    doc = nlp(text)

    if len(doc)==0:
        return

    x = []
    if doc[0].pos_ in ["NOUN","PROPN"]:
        x.append({'noun':''})
    else:
        x.append({'link':''})
    for token in doc:
        if token.pos_ in ["NOUN","PROPN"]:
            if 'noun' in x[-1].keys():
                x[-1]['noun']+=' '+token.lemma_
            else:
                x.append({'noun':token.lemma_})
        else:
            if 'link' in x[-1].keys():
                x[-1]['link']+=' '+token.text
            else:
                x.append({'link':token.text})
    return x


def get_nouns(model_text):
    """
    :param model_text: output from model_(text) as a list of dictionaries e.g., [{'link': ' largely by the'}, {'noun': 'COVID-19'}, {'link': 'pandemic coupled with unfavorable'}, {'noun': 'discount rates'}, {'link': 'in the'}, {'noun': 'United States'}, {'link': 'in the first'}, {'noun': 'quarter'}, {'link': 'of 2021'}]
    :return: list of nouns, string
    """
    nouns = []
    for d in model_text:
        if 'noun' in d.keys():
            nouns.append(d['noun'])
    return nouns


def vectorize_spacy(nouns,nlp):
    """
    :param nouns: a list of nouns or noun-phrases, string
    :param nlp: nlp = spacy.load("en_core_web_lg") #full vector package 300
    :return: numpy array of vectors nx300
    """
    x = []
    for n in nouns:
        vec = np.array([t.vector for t in nlp(n)])
        avg = np.mean(vec,axis=0)
        x.append(avg)
    return np.array(x)


def get_fildpath(path_root, ticker, type_, file):
    """
    path_root: str, root folder where the downloaded financial documents are saved
    ticker: str, company's unique ticker
    type: '10-K' or '10-Q'
    file: name of the folder (cik-yy-num) where the document filing_details.html are saved
    return: file_path pointing to the folder containing the current file
    """
    file_path = path_root + ticker + "/" + type_ + "/" + file + "/"

    return file_path


def get_MDA(file_name):
    """
    file_name: str, path pointing where the raw.txt is saved
    return: raw txt containing the MDA
    """
    try:
        with open(file_name) as f:
            text = f.read()
    except OSError:
        text = None

    return text



# copied from 2.Preprocessing_part3.ipynb cell#86
# def get_MDA(row):
#     global data_root
#
#     ticker = str(row['ticker'])
#     type_ = str(row['type'])
#     file = str(row['file'])
#
#     folder = data_root + 'Samples/' + ticker + "/" + type_ + "/" + file + "/"
#     file_name = folder + "raw_mda.txt"
#
#     try:
#         with open(file_name) as f:
#             text = f.read()
#     except OSError:
#         text = ''
#
#     return text


def get_sentences(text):
    sentences = re.split(r'\. ', text)
    return sentences


### Modified!!!

def transfer_sentences(df_sent, df_doc, path_root, save=True):
    """
    :param df_sent:
    :param df_doc: dataframe containing each unique document as a row
    :param path_root: file path where the raw MDA txt are saved
    :param save: save selected sentences containing causality as a json file
    :return:
    """
    for index, row in df_doc.iterrows():
        # each row represents a document

        ticker = str(row['ticker'])
        type_ = str(row['type'])
        file = str(row['file'])
        file_path = get_fildpath(path_root, ticker, type_, file)
        file_name = file_path + "raw_mda.txt"
        text = get_MDA(file_name)

        if text:
            df_ = pd.DataFrame()
            df_['sentence'] = get_sentences(text) #string
            # df_['p-1'] = df_['sentence'].shift(1) # previous sentence for context TODO
            # df_['p+1'] = df_['sentence'].shift(-1) # next sentence for context TODO
            df_['ticker'] = ticker
            df_['file'] = file

            df_['d'] = df_['sentence'].apply(lambda sentence: filter_(sentence, matcher_topics, matcher_verbs, matcher_nonverbs))
            df_['topic'] = df_['d'].apply(lambda d:d['topic'] if d else None)
            df_['causal'] = df_['d'].apply(lambda d:d['causal'] if d else None)

            df_['EC_pairs'] = df_['d'].apply(lambda d:extract_(d) if isinstance(d,dict) else None)
            df_['e_raw'] = df_['EC_pairs'].apply(lambda EC_pairs: [ec[0] for ec in EC_pairs] if EC_pairs else None) #Need further processing TODO
            df_['c_raw'] = df_['EC_pairs'].apply(lambda EC_pairs: [ec[1] for ec in EC_pairs] if EC_pairs else None)
            df_['c_model'] = df_['c_raw'].apply(lambda c_raw: [model_(c) for c in c_raw] if c_raw else None)
            df_['c_noun'] = df_['c_model'].apply(lambda c_model: [get_nouns(c) for c in c_model if c] if c_model else None)

            df_.drop(columns=['d','EC_pairs'], inplace=True)
            df = df_[df_['causal'].notna()]

            if save:
                df.to_json(file_path+'causal_sent.json')

            df_sent = df_sent.append(df, ignore_index=True)

            print((ticker, type_, file), 'num of sentences:', len(df_), '->', len(df))
            # sum([x for x in df_['c_noun'] if x], [])

    return df_sent




def vectorize_spacy(nouns,nlp):
    """
    :param nouns: a list of nouns or noun-phrases, string
    :param nlp: nlp = spacy.load("en_core_web_lg") #full vector package 300
    :return: numpy array of vectors nx300
    """
    x = []
    for n in nouns:
        vec = np.array([t.vector for t in nlp(n)])
        avg = np.mean(vec,axis=0)
        x.append(avg)
    return np.array(x)



# visualization using TSNE
def TSNE_vis(data, X, yhat, annotation=False,font=8):
    # from sklearn.manifold import TSNE
    # import matplotlib.pyplot as plt

    tsne = TSNE(n_components=2, verbose=1, random_state=0)
    Y = tsne.fit_transform(X)

    df = pd.DataFrame({'text': data, 'cluster': yhat, 'y0': Y[:, 0], 'y1': Y[:, 1], })
    # df['text'] = df['span'].apply(lambda x: x.text)

    fig, ax = plt.subplots(figsize=(20,20))
    for i, cluster in enumerate(np.unique(yhat)):
        y0 = df['y0'][df['cluster'] == cluster].astype('float')
        y1 = df['y1'][df['cluster'] == cluster].astype('float')
        # c = colors[cluster]
        ax.plot(y0, y1, 'o', color='C'+str(i))
    ax.set_title('Sample phrases by cluster')
    ax.set_yticklabels([])  # Hide ticks
    ax.set_xticklabels([])  # Hide ticks

    if annotation:
        for i, word in enumerate(data):
            plt.annotate(word, xy=(Y[i, 0], Y[i, 1]), fontsize=font)
    plt.show()

