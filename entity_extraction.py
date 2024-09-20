# entity_extraction.py

from sqlalchemy import text

def extract_entities(user_query, result, engine):
    entities = {}
    lower_query = user_query.lower()

    # Example for average price queries
    if 'average price of' in lower_query:
        item = lower_query.split('average price of')[-1].strip('. ').strip()
        entities['item'] = item
        # Assuming result contains the average price
        entities['average_price'] = extract_average_price(result)

    # Example for material queries
    if 'details about' in lower_query or 'information on' in lower_query or 'material' in lower_query:
        material_query = lower_query.split('details about')[-1].strip('. ').strip()
        entities['material_query'] = material_query
        matching_materials = find_matching_materials(material_query, engine)
        if len(matching_materials) == 1:
            entities['material'] = matching_materials[0]
        elif len(matching_materials) > 1:
            entities['ambiguous_materials'] = matching_materials
        else:
            entities['material_not_found'] = material_query

    # Add more extraction rules as needed
    return entities

def extract_average_price(result):
    # Implement logic to extract average price from the result
    # For simplicity, we'll assume the result is the average price
    return result

def find_matching_materials(material_query, engine):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT material_name FROM materials
            WHERE material_name LIKE :material_query
        """), {'material_query': f'%{material_query}%'}).fetchall()
    matching_materials = [row[0] for row in result]
    return matching_materials
