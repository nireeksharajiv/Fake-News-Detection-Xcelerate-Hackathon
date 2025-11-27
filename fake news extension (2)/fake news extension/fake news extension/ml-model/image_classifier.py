import json
import base64
from groq import Groq

# ========== CORE FUNCTIONS ==========

def encode_image_to_base64(image_path):
    """
    Convert local image file to base64
    
    Args:
        image_path (str): Path to JPG/PNG file
    
    Returns:
        str: Base64 encoded string
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"[IMAGE ERROR] {e}")
        return None


def get_image_media_type(image_path):
    """Get media type from file extension"""
    ext = image_path.lower().split('.')[-1]
    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp"
    }
    return media_types.get(ext, "image/jpeg")


def analyze_image_with_vlm(image_path, api_key, context=""):
    """
    Analyze image using Groq's Vision Language Model
    
    Args:
        image_path (str): Path to image file
        api_key (str): Groq API key
        context (str): Optional context (tweet text, caption, etc.)
    
    Returns:
        tuple: (fake_probability, verdict, reason, details)
    """
    client = Groq(api_key=api_key)
    
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return 50, "error", "Failed to load image", {}
    
    media_type = get_image_media_type(image_path)
    
    context_info = f"\nContext/Caption: {context}" if context else ""
    
    prompt = f"""You are an expert image forensic analyst. Analyze this image for signs of manipulation, AI generation, or misleading content.

Check for:
1. **AI Generation Signs**: Unnatural textures, weird fingers/hands, distorted text, artificial patterns, too-perfect symmetry
2. **Photoshop/Editing Signs**: Inconsistent lighting, warped edges, mismatched shadows, cloning artifacts, unnatural blur
3. **Deepfake Signs**: Facial inconsistencies, unnatural skin, weird eye reflections, hair anomalies
4. **Misleading Content**: Out-of-context image, fake screenshots, manipulated text/headlines, fake watermarks
5. **Image Quality**: Compression artifacts that hide manipulation, suspicious cropping
{context_info}

Respond ONLY with JSON (no markdown, no extra text):
{{
    "fake_probability": <0-100>,
    "verdict": "<fake|manipulated|ai_generated|misleading|uncertain|likely_real|real>",
    "reason": "<2-3 sentence explanation>",
    "detected_issues": ["<issue1>", "<issue2>"],
    "confidence": "<low|medium|high>"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=500,
        )
        
        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        data = json.loads(result)
        
        return (
            data.get("fake_probability", 50),
            data.get("verdict", "uncertain"),
            data.get("reason", "No reason provided"),
            {
                "detected_issues": data.get("detected_issues", []),
                "confidence": data.get("confidence", "medium")
            }
        )
    
    except Exception as e:
        print(f"[VLM ERROR] {e}")
        return 50, "error", f"VLM analysis failed: {str(e)}", {}


def classify_image(image_path, api_key, context=""):
    """
    Main function - call this from your code
    
    Args:
        image_path (str): Path to uploaded JPG/PNG file
        api_key (str): Groq API key
        context (str): Optional context (tweet text, caption)
    
    Returns:
        dict: classification result
    """
    # Analyze with VLM
    fake_prob, verdict, reason, details = analyze_image_with_vlm(image_path, api_key, context)
    
    # Final classification
    if fake_prob >= 70:
        classification = "FAKE"
    elif fake_prob >= 40:
        classification = "SUSPICIOUS"
    else:
        classification = "REAL"
    
    return {
        "image_path": image_path,
        "classification": classification,
        "fake_probability": fake_prob,
        "verdict": verdict,
        "reason": reason,
        "detected_issues": details.get("detected_issues", []),
        "confidence": details.get("confidence", "medium")
    }