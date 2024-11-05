# constants.py

# Initialize the constant with a default value
VECTORSTORE_IP = None

def set_vectorstore_ip(value):
    global VECTORSTORE_IP
    VECTORSTORE_IP = value

def get_vectorstore_ip():
    return VECTORSTORE_IP