# query_manager.py

from llama_index.indices.struct_store.sql_query import NLSQLTableQueryEngine

class QueryManager:
    def __init__(self, index, context_manager):
        self.index = index
        self.context_manager = context_manager

    def query(self, user_query):
        # Get entities from context
        entities = self.context_manager.get_entities()

        # Handle follow-up questions
        user_query = self.augment_query_with_context(user_query, entities)

        # Create a query engine
        query_engine = NLSQLTableQueryEngine(self.index)

        # Execute the query
        try:
            response = query_engine.query(user_query)
            # Add to conversation context
            self.context_manager.add_entry(user_query, response.extra_info['sql_query'], response.response)
            return response.response
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def augment_query_with_context(self, user_query, entities):
        # Replace pronouns and references with actual entities
        if 'it' in user_query.lower() and 'material' in entities:
            material = entities['material']
            user_query = user_query.replace('it', material)
        return user_query
