import streamlit as st 
import os 
from langchain_groq import ChatGroq 
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
# from langchain_community.vectorstores import FAISS 
from langchain_objectbox.vectorstores import ObjectBox 
from langchain_community.document_loaders import PyPDFDirectoryLoader
import time
from dotenv import load_dotenv
load_dotenv()

#load Groq api key
groq_api=os.getenv('GROQ_API_KEY')

st.title("Chat GROQ With Llama 3 Demo")

llm=ChatGroq(groq_api_key=groq_api,
             model_name='Llama3-8b-8192')

prompt=ChatPromptTemplate.from_template(
    """
    Answer the questions based on provided context only.
    Please provide teh mose acurate response based on the question
    <context>
    {context}
    </context>
    Question:{input}
    """
)

def vector_embeddings():
    if "vectors" not in st.session_state:
        st.session_state.embeddings=OllamaEmbeddings()
        st.session_state.loader=PyPDFDirectoryLoader('./us_census')     #data ingestion
        st.session_state.docs=st.session_state.loader.load()            #document loading
        st.session_state.text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)       #chunk creation
        st.session_state.final_documents=st.session_state.text_splitter.split_documents(st.session_state.docs[:30])     #splitting
        st.session_state.vectors=ObjectBox.from_documents(st.session_state.final_documents, st.session_state.embeddings, embedding_dimensions=786)    #vector store creation
    
    

prompt1=st.text_input("Enter your question from documents")

if st.button("Start Document Embedding"):
    vector_embeddings()
    st.write("ObjectBox DB is ready!")
    


if prompt1:
    start=time.process_time()
    document_chain=create_stuff_documents_chain(llm,prompt)
    retriever=st.session_state.vectors.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    response=retrieval_chain.invoke({'input':prompt1})
    print("Response time:", time.process_time()-start)
    st.write(response['answer'])
    
    #display from where in the document the response is generated
    with st.expander("Document similarity serch"):
        #finding relevant chunks
        for i,doc in enumerate(response['context']):
            st.write(doc.page_content)
            st.write("----------------------------------------")