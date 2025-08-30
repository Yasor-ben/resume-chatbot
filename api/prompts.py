SUMMARIZE_PROMPT = """fait un résumé du text en français
    ###
    text : {text_complet}"""

SYSTEM_PROMPT = """the following is a friendly conversation between a human and a AI, 
the AI is talkative and provides lots of specific details from its CONVERSATION context 
if the AI does not know the answer to a question, it truthfully says it does not.
CONVERSATION:
###
{conversation}

"""
