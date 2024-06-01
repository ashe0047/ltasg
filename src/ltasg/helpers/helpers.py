def transform_data(data):
        new_data = []
        for entry in data:
            new_data += entry['value']
        return new_data