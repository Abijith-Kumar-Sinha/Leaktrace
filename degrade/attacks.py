"""Post-capture attacks an adversary (or a messaging app) may apply to a leaked photo."""
import numpy as np, cv2

def apply_post(img, kind, p):
    if kind == "rotate":                       # arbitrary in-plane rotation, canvas expanded
        h, w = img.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), p, 1.0)
        c, s = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * s + w * c), int(h * c + w * s)
        M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
        return cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_CUBIC, borderValue=55)
    if kind == "rot90":
        return np.ascontiguousarray(np.rot90(img, int(p) // 90))
    if kind == "rescale":                      # shrink by factor p then enlarge back (lossy re-sampling)
        small = cv2.resize(img, None, fx=p, fy=p, interpolation=cv2.INTER_AREA)
        return cv2.resize(small, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
    if kind == "jpeg":
        return cv2.imdecode(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, int(p)])[1], 0)
    if kind == "median":
        return cv2.medianBlur(img, int(p))
    if kind == "unsharp":
        b = cv2.GaussianBlur(img, (0, 0), 2.0); return cv2.addWeighted(img, 1 + p, b, -p, 0)
    if kind == "contrast":
        return np.clip((img.astype(np.float32) - 128) * p + 128, 0, 255).astype(np.uint8)
    raise ValueError(kind)
