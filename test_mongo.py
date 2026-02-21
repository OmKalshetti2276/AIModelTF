from database import predictions_collection

doc = {"test": "mongo working"}

result = predictions_collection.insert_one(doc)

print("Inserted ID:", result.inserted_id)