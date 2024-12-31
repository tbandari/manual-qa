from flask import Flask, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

os.environ["OPENAI_API_KEY"] = "your-key"

# Filepaths for the manual and FAISS index
manual_filepath = "manual.pdf"
faiss_index_filepath = "faiss_index"

# Load the PDF and split it into sections
def load_and_process_manual(filepath):
    loader = PyPDFLoader(filepath)
    documents = loader.load()
    
    # Split text into manageable chunks with overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = text_splitter.split_documents(documents)
    return split_docs

# Create or Load the FAISS Vector Store
def get_vector_store(documents=None, index_path="faiss_index"):
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    if os.path.exists(index_path):
        # Load existing FAISS index with trusted deserialization
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    else:
        if documents is None:
            raise ValueError("Documents must be provided to create the FAISS index.")
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(index_path)  # Save the index for future use
    return vector_store

# Build the RetrievalQA Chain
def create_qa_chain(vector_store):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4"),
        chain_type="stuff",
        retriever=retriever
    )
    return qa_chain

# Pre-load data and initialize QA system
def initialize_qa_system():
    if not os.path.exists(faiss_index_filepath):
        # Load and process the manual
        split_docs = load_and_process_manual(manual_filepath)
        
        # Create or load the vector store
        vector_store = get_vector_store(split_docs, faiss_index_filepath)
    else:
        # Load the FAISS index
        vector_store = get_vector_store(index_path=faiss_index_filepath)

    
    # Initialize RetrievalQA chain
    qa_chain = create_qa_chain(vector_store)
    return qa_chain

qa_system = initialize_qa_system()

@app.route("/query", methods=["POST"])
def query():
    try:
        data = request.json
        query_text = data.get("query", "")

        if not query_text:
            return jsonify({"error": "Query cannot be empty"}), 400

        # Get the response from the QA system
        response = qa_system.run(query_text)
        print(response)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e), "message": "An error occurred while processing the request."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)