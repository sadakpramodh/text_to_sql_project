# multi_table_query_manager.py

import re
from sqlalchemy import text
from llama_index import GPTSQLStructStoreIndex, SQLDatabase
from entity_extraction import extract_entities
from transformers import pipeline

class MultiTableQueryManager:
    def __init__(self, indexes, engine, context_manager, service_context):
        self.indexes = indexes
        self.engine = engine
        self.context_manager = context_manager
        self.service_context = service_context
        self.coref_pipeline = pipeline('coreference-resolution', model='cakiki/bert-base-uncased-squad-v1')

    def query(self, user_query):
        entities = self.context_manager.get_entities()

        # Resolve coreferences
        user_query = self.resolve_coreferences(user_query)

        # Extract entities from the current query
        current_entities = extract_entities(user_query, None, self.engine)

        # Check for ambiguity
        if 'ambiguous_materials' in current_entities:
            materials = current_entities['ambiguous_materials']
            clarification_prompt = "We found multiple materials matching '{}':\n".format(current_entities['material_query'])
            for idx, material in enumerate(materials, start=1):
                clarification_prompt += f"{idx}. {material}\n"
            clarification_prompt += "Please enter the number corresponding to your choice, or type 'all' for all materials."
            print(clarification_prompt)

            # Get user input
            user_choice = input("Your choice: ").strip()
            if user_choice.lower() == 'all':
                entities['material'] = materials
            elif user_choice.isdigit() and 1 <= int(user_choice) <= len(materials):
                entities['material'] = materials[int(user_choice) - 1]
            else:
                print("Invalid choice. Please try again.")
                return self.query(user_query)
        elif 'material_not_found' in current_entities:
            print(f"No materials found matching '{current_entities['material_not_found']}'. Please try again.")
            return None
        else:
            entities.update(current_entities)

        # Augment the query with context
        if self.is_follow_up_question(user_query):
            user_query = self.augment_query_with_context(user_query, entities)

        # Select relevant tables
        tables_needed = self.determine_relevant_tables(user_query, entities)

        # Create a combined index
        combined_db = SQLDatabase(self.engine, include_tables=tables_needed)
        combined_vector_store = None  # For simplicity, we'll skip setting up a combined vector store
        combined_index = GPTSQLStructStoreIndex(
            sql_database=combined_db,
            service_context=self.service_context
        )

        # Generate response
        response = combined_index.query(user_query)

        if response:
            # Add entry to context
            self.context_manager.add_entry(user_query, response.extra_info['sql_query'], response.response)
            return response.response
        else:
            return "I'm sorry, I couldn't find an answer to your question."

    def is_follow_up_question(self, user_query):
        follow_up_words = ['who', 'what', 'where', 'why', 'how', 'which', 'below', 'above', 'that', 'those']
        return any(word in user_query.lower() for word in follow_up_words)

    def augment_query_with_context(self, user_query, entities):
        # Replace pronouns and references with actual entities
        if 'below' in user_query.lower() and 'average_price' in entities:
            price = entities['average_price']
            user_query = re.sub(r'\bbelow\b', f'below {price}', user_query, flags=re.IGNORECASE)
        if 'material' in entities and 'material' not in user_query.lower():
            material = entities['material']
            if isinstance(material, list):
                materials_list = "', '".join(material)
                user_query += f" for materials '{materials_list}'"
            else:
                user_query += f" for material '{material}'"
        return user_query

    def resolve_coreferences(self, user_query):
        resolved = self.coref_pipeline(user_query)
        return resolved['resolved_text']

    def determine_relevant_tables(self, user_query, entities):
        # Simple keyword-based table selection
        tables_needed = set()
        query_lower = user_query.lower()
        if 'product' in query_lower or 'quantity' in query_lower or 'staging' in query_lower:
            tables_needed.add('staging')
        if 'customer' in query_lower or 'purchase date' in query_lower or 'master' in query_lower:
            tables_needed.add('master')
        if 'material' in query_lower or 'cotton' in query_lower or 'materials' in query_lower:
            tables_needed.add('materials')
        # Add more conditions based on your schema
        return list(tables_needed) if tables_needed else list(self.indexes.keys())
