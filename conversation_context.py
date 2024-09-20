# conversation_context.py

class ConversationContext:
    def __init__(self, engine):
        self.history = []
        self.entities = {}
        self.engine = engine

    def add_entry(self, user_query, sql_query, result):
        self.history.append({
            'user_query': user_query,
            'sql_query': sql_query,
            'result': result
        })
        self.extract_entities(user_query, result)

    def extract_entities(self, user_query, result):
        from entity_extraction import extract_entities
        extracted_entities = extract_entities(user_query, result, self.engine)
        self.entities.update(extracted_entities)

    def get_entities(self):
        return self.entities

    def get_last_result(self):
        if self.history:
            return self.history[-1]['result']
        return None
