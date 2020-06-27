def telephone_matcher(paragraf):
    telephone_match \
    = re.search(r'(\d{3,5}[-\.\s]??\d{3,5}[-\.\s]??\d{3,5}|\(\d{3,5}\)'
    			 '\s*\d{3,5}[-\.\s]??\d{3,5}|\d{3,5}[-\.\s]??\d{3,5})',\
                                   paragraf)
    if telephone_match is not None:
        print("Phone Number: %s" % telephone_match.group(0))
        return 1
    else:
        return 0