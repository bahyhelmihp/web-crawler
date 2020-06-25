def email_matcher(paragraf):
    email_match = re.search(r'[\w\.-]+(@|\[at])[\w\.-]+', paragraf)

    if email_match is not None:
        print("Email: %s" % email_match.group(0))
        return 1
    else:
        return 0