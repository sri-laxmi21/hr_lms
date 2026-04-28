import sys
import traceback

try:
    from app.models import *
    print("Models loaded successfully!")
except Exception as e:
    print("ERROR:", str(e))
    traceback.print_exc()
