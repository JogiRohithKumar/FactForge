# tests/test_pipeline.py
from utils.text_processor import clean_text

def test_text_cleaning_pipeline_lowercasing():
    """Validates that strings are transformed completely to lower case structures."""
    assert clean_text("FACTFORGE PRO") == "factforge pro"

def test_text_cleaning_pipeline_punctuation():
    """Validates that high-frequency punctuation items are completely omitted."""
    assert clean_text("news, headline! breaking.") == "news headline breaking"

def test_text_cleaning_pipeline_stopwords():
    """Validates that conversational English stopwords are correctly removed."""
    # 'the' and 'is' should be removed, leaving only 'report'
    assert clean_text("the report is") == "report"