import sys, zipfile, cv2
from embed.typeset import rasterise
from degrade.simulate import Degrade, photograph
zpath, centre, out = sys.argv[1:4]
page = rasterise(zipfile.ZipFile(zpath).read(f"copies/{centre}.pdf"))[0]
img, _ = photograph(page, Degrade(out_width=1600, persp=0.3, blur=1.0, noise=3, jpeg=85, whatsapp=True, seed=5), [595.28, 841.89])
cv2.imwrite(out, img); print("wrote", out)
