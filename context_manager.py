# context_manager.py

class ConversationContext:
    def __init__(self):
        self.history = []
        self.entities = {}

    def add_entry(self, user_query, sql_query, result):
        self.history.append({
            'user_query': user_query,
            'sql_query': sql_query,
            'result': result
        })
        self.extract_entities(user_query, result)

    def extract_entities(self, user_query, result):
        # Implement entity extraction logic
        extracted_entities = {}
        # Example: Extracting the material from the query
        if 'material' in user_query.lower():
            material = user_query.lower().split('material')[-1].strip()
            extracted_entities['material'] = material
        self.entities.update(extracted_entities)

    def get_entities(self):
        return self.entities
