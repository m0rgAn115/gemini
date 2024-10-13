from .getActions import getActionText
from .getAnalysis import getAnalysisData
from .SpendingShield import getRecomendationsSpends

def register_endpoints(app):
    """Register all endpoints for the Gemini API."""
    
    #finished
    getActionText(app)

    #not fished
    getAnalysisData(app)

    #finished
    getRecomendationsSpends(app)