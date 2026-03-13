import io
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

class ModelService:
    def __init__(self):
        # We use a pretrained MobileNetV2 fine-tuned on PlantVillage dataset (38 classes)
        self.model_name = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
        
        # Load processor and model
        try:
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
            self.model.eval()  # Set to evaluation mode
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    async def predict_disease(self, image_bytes: bytes) -> tuple[str, float]:
        """
        Takes raw image bytes, runs it through MobileNetV2,
        and returns (predicted_class_name, confidence_score)
        """
        try:
            # 1. Open image from bytes
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # 2. Preprocess image for the model
            inputs = self.processor(images=image, return_tensors="pt")
            
            # 3. Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # 4. Get predictions
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            
            # Custom processing for plant village class names to make them readable
            # e.g., "Tomato___Late_blight" -> "Tomato Late Blight"
            raw_label = self.model.config.id2label[predicted_class_idx]
            clean_label = raw_label.replace("___", " ").replace("_", " ").title()
            
            # Calculate confidence using softmax
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            confidence = probabilities[0][predicted_class_idx].item() * 100
            
            return clean_label, round(confidence, 2)
            
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")

# Singleton instance matching FastAPI startup lifecycle
model_service = ModelService()
