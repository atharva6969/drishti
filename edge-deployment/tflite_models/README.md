# TFLite Models Directory

Place your TensorFlow Lite models here:

| File | Model | Size | Source |
|------|-------|------|--------|
| `face_detection.tflite` | BlazeFace | ~0.5 MB | [MediaPipe](https://google.github.io/mediapipe/solutions/face_detection.html) |
| `face_embedding.tflite` | MobileFaceNet | ~2 MB | [OpenGait releases](https://github.com/yule-BUAA/MobileFaceNet-TensorFlow) |
| `person_detection.tflite` | EfficientDet-Lite | ~4 MB | [TFLite model zoo](https://www.tensorflow.org/lite/models) |
| `embeddings.json` | Active cases cache | varies | Synced from central API |

## Updating Embedding Cache

The central DRISHTI API pushes a fresh embedding cache to edge devices every hour.
You can also pull manually:

```bash
curl -H "X-Edge-API-Key: YOUR_KEY" \
     https://api.drishti.police.gov.in/api/v1/edge/embeddings-cache \
     -o embeddings.json
```
