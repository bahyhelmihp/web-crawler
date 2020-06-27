def refund_policy_matcher(paragraf):
    keyword_refund = ['refunds', 'refund', 'refund policy', 'return', 'returns', 'return policy', 'pengembalian', 'pengembalian dana', 'mengembalikan dana', 'dikembalikan', 'pengembalian', 'mengembalikan', 'retur', 'tukar', 'penukaran']
    
    ## Tokenizing & cleaning paragraf into words
    try:
        lang = 'indonesian' if tb(paragraf).detect_language() == 'id' else 'english'
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(paragraf)

        ## Removing stop words
        stop_words = nltk.corpus.stopwords.words(lang)

        cleaned_words = []
        for word in words:
            if word not in stop_words:
                cleaned_words.append(word)
                
    except Exception as e:
        print(e)
        cleaned_words = ""

    mask = pd.Series(cleaned_words).str.contains("|".join(keyword_refund))

    count_refund = np.count_nonzero(mask)
    if count_refund > 0:
        return 1           
    else:
        return 0