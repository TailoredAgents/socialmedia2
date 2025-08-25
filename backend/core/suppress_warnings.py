"""
Suppress third-party library warnings that we cannot control
This module should be imported as early as possible in the application
"""
import warnings
import sys

def suppress_third_party_warnings():
    """
    Suppress warnings from third-party libraries that use deprecated patterns
    but are outside our control to fix directly.
    """
    
    # Tweepy library - uses invalid escape sequences in docstrings and deprecated modules
    # This is a known issue with Tweepy and Python 3.12+
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="tweepy")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="tweepy")
    warnings.filterwarnings("ignore", message=".*imghdr.*deprecated.*")
    warnings.filterwarnings("ignore", message=".*OAuthHandler.*deprecated.*")
    
    # pysbd library - uses regex patterns with deprecated escape sequences
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd.segmenter")
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd.lang.arabic")
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd.lang.persian")
    
    # ChromaDB uses deprecated Pydantic v1 patterns
    # They are migrating to Pydantic v2 but haven't completed yet
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="chromadb")
    warnings.filterwarnings("ignore", message=".*model_fields.*attribute.*deprecated.*")
    
    # Pydantic v2 migration warnings from dependencies
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
    warnings.filterwarnings("ignore", message=".*model_fields.*")
    warnings.filterwarnings("ignore", message=".*class-based `config`.*")
    warnings.filterwarnings("ignore", message=".*min_items.*")
    warnings.filterwarnings("ignore", message=".*max_items.*")
    warnings.filterwarnings("ignore", message="Valid config keys have changed in V2")
    
    # SQLAlchemy 2.0 migration warnings
    warnings.filterwarnings("ignore", message=".*declarative_base.*deprecated.*")
    warnings.filterwarnings("ignore", message=".*MovedIn20Warning.*")
    
    # Billiard/Celery warnings about forking in multi-threaded processes
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="billiard")
    warnings.filterwarnings("ignore", message=".*multi-threaded.*fork.*deadlocks.*")
    
    # Suppress import-time SyntaxWarnings if running Python 3.12+
    if sys.version_info >= (3, 12):
        warnings.filterwarnings("ignore", category=SyntaxWarning)
        # Re-enable our own SyntaxWarnings
        warnings.filterwarnings("default", category=SyntaxWarning, module="backend")
        warnings.filterwarnings("default", category=SyntaxWarning, module="app")

# Call this function when module is imported
suppress_third_party_warnings()