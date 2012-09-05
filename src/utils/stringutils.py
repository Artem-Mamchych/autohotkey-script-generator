import diff_match_patch as dm

defaultCommentStartSequence='#'

def trimComments(text, commentStartSequence=defaultCommentStartSequence):
    if text.startswith(commentStartSequence):
        return ""
    text = text.split(commentStartSequence)
    if len(text) >= 1:
        return text[0].strip()
    else:
        return ""

