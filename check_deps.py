try:
    import flask
    import numpy
    import pandas
    import yfinance
    import sklearn
    import keras
    import google.generativeai
    print("All dependencies are present.")
except ImportError as e:
    print(f"Missing dependency: {e}")
