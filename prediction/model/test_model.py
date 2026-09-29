from prediction.ai_model import predict_disease


image_path = "test_leaf.jpg"

result = predict_disease(
    image_path
)

print("\nPrediction:")
print(
    "Disease:",
    result["disease_name"]
)

print(
    "Confidence:",
    result["confidence"],
    "%"
)

print(
    "Severity:",
    result["severity"]
)

print("\nTop predictions:")

for item in result[
    "top_predictions"
]:

    print(
        item["disease"],
        "=>",
        item["confidence"],
        "%"
    )