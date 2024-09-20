# main.py

import sys
from sqlalchemy import create_engine
from conversation_context import ConversationContext
from multi_table_query_manager import MultiTableQueryManager
from llama_index import (
    LLMPredictor,
    ServiceContext,
    GPTSQLStructStoreIndex,
    SQLDatabase
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.vector_stores import ChromaVectorStore
from llama_index.storage.storage_context import StorageContext
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def main():
    # Define your SQL Server connection details
    server = 'YOUR_SERVER_NAME'     # e.g., 'localhost' or 'SERVER\\INSTANCE'
    database_name = 'YOUR_DATABASE_NAME'
    username = 'YOUR_USERNAME'
    password = 'YOUR_PASSWORD'
    driver = 'ODBC Driver 17 for SQL Server'  # Ensure this driver is installed

    # Create the connection string
    connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database_name}?driver={driver.replace(' ', '+')}"

    # Create the SQLAlchemy engine
    engine = create_engine(connection_string)

    # Initialize the conversation context
    context_manager = ConversationContext(engine)

    # Initialize the LLM Predictor
    model_name = 'TheBloke/LLama-2-7B-Chat-HF'  # Replace with your chosen LLaMA model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map='auto',
        low_cpu_mem_usage=True
    )
    generator = pipeline(
        'text-generation',
        model=model,
        tokenizer=tokenizer,
        max_length=512,
        temperature=0.7,
        do_sample=True
    )
    llm_predictor = LLMPredictor(llm=generator)

    # Initialize the embedding model
    embedding_model = HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2')

    # Create service context
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        embed_model=embedding_model
    )

    # Create indexes for each table
    indexes = {}
    tables = ['staging', 'master', 'materials']  # Add your table names here
    for table in tables:
        database = SQLDatabase(engine, include_tables=[table])
        vector_store = ChromaVectorStore(
            embedding=embedding_model,
            persist_directory=f'chroma_{table}',
            collection_name=f'{table}_collection'
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = GPTSQLStructStoreIndex(
            sql_database=database,
            storage_context=storage_context,
            service_context=service_context
        )
        indexes[table] = index

    # Initialize the query manager
    query_manager = MultiTableQueryManager(indexes, engine, context_manager, service_context)

    # Start the interaction loop
    print("Welcome to the Text-to-SQL application. Type 'exit' to quit.")
    while True:
        user_query = input("\nUser: ").strip()
        if user_query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            sys.exit()
        response = query_manager.query(user_query)
        if response:
            print(f"Assistant: {response}")

if __name__ == '__main__':
    main()
