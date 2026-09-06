import os
import cv2
import numpy as np

class FaceEngine:
    def __init__(self):
        # Paths to the ONNX models
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.detector_path = os.path.join(base_dir, "models", "face_detection_yunet_2023mar.onnx")
        self.recognizer_path = os.path.join(base_dir, "models", "face_recognition_sface_2021dec.onnx")
        
        # Initialize recognizer
        self.recognizer = cv2.FaceRecognizerSF.create(self.recognizer_path, "")

    def _get_detector(self, image_shape):
        height, width = image_shape[:2]
        return cv2.FaceDetectorYN.create(
            self.detector_path,
            "",
            (width, height),
            score_threshold=0.5,
            nms_threshold=0.3,
            top_k=5000
        )

    def detect_face(self, image_path: str):
        """
        Detects faces in an image and returns the count.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"success": False, "error": "Image not found or invalid format"}
                
            detector = self._get_detector(img.shape)
            faces = detector.detect(img)
            
            if faces[1] is None:
                return {"success": True, "faces_detected": 0}
                
            return {
                "success": True,
                "faces_detected": len(faces[1])
            }
        except Exception as e:
             return {
                "success": False,
                "error": str(e)
             }

    def _extract_feature(self, img_path):
        img = cv2.imread(img_path)
        if img is None:
            return None
        detector = self._get_detector(img.shape)
        faces = detector.detect(img)
        if faces[1] is None:
            return None
        
        # Align and extract feature for the first face
        face_aligned = self.recognizer.alignCrop(img, faces[1][0])
        face_feature = self.recognizer.feature(face_aligned)
        return face_feature

    def verify_match(self, img1_path: str, img2_path: str):
        """
        Compares two faces using SFace cosine distance with Dynamic Thresholding.
        """
        try:
            feat1 = self._extract_feature(img1_path)
            feat2 = self._extract_feature(img2_path)
            
            if feat1 is None or feat2 is None:
                 return {"success": False, "error": "Face not detected in one of the images"}
                 
            # Calculate Cosine similarity score (higher is more similar).
            score = self.recognizer.match(feat1, feat2, cv2.FaceRecognizerSF_FR_COSINE)
            distance = 1.0 - score
            
            # --- DYNAMIC THRESHOLDING ENHANCEMENT ---
            # Check the resolution of the candidate image (img2)
            img2 = cv2.imread(img2_path)
            h, w = img2.shape[:2]
            
            # If the candidate is a tiny, blurry thumbnail from Google Lens, 
            # we lower the threshold slightly to prevent false rejections.
            if w < 150 or h < 150:
                dynamic_threshold = 0.300
            elif w < 300 or h < 300:
                dynamic_threshold = 0.330
            else:
                dynamic_threshold = 0.363 # Default strict SFace threshold
                
            verified = score >= dynamic_threshold
            
            return {
                "success": True,
                "verified": bool(verified),
                "distance": float(distance),
                "score": float(score),
                "threshold_used": float(dynamic_threshold)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
