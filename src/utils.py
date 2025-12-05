import logging
import os

def setup_logger(name=__name__):
    """
    Sets up a logger with a standard format.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # Add file handler to avoid garbled logs
        fh = logging.FileHandler("app_debug.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def remove_stopwords(text):

    stop_words = {
        "a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "with", "of",
        "in", "out", "as", "if", "when", "while", "then", "than", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "can", "could", "will", "would", "shall", "should",
        "may", "might", "must", "it", "its", "this", "that", "these", "those", "i", "you", "he", "she", "we",
        "they", "me", "him", "her", "us", "them", "my", "your", "his", "their", "our", "mine", "yours", "hers",
        "theirs", "ours", "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves"
    }
    
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return " ".join(filtered_words)
