"""压缩 D:\my-world\images\ 里的大图片
- 长边缩到 900 像素
- 转 JPG 质量 85（画质几乎无损）
- PNG 直接转成 JPG（删原 PNG）
- 已经小于 500KB 的跳过
"""
from PIL import Image
from pathlib import Path

img_dir = Path(r"D:\my-world\images")
MAX_LONG_EDGE = 900
JPG_QUALITY = 85
SKIP_UNDER = 500 * 1024  # 500KB 以下不动

print(f"{'文件':<15} {'原大小':>10} → {'新大小':>10}  {'压缩率':>8}")
print("-" * 55)

for f in sorted(img_dir.iterdir()):
    if f.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        continue
    before = f.stat().st_size
    if before < SKIP_UNDER and f.suffix.lower() == '.jpg':
        print(f"{f.name:<15} {before/1024:>7.0f} KB   [已够小，跳过]")
        continue

    img = Image.open(f)
    # PNG 有透明通道，JPG 不支持，先铺白底
    if img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # 长边超 900 就等比缩小
    w, h = img.size
    long_edge = max(w, h)
    if long_edge > MAX_LONG_EDGE:
        scale = MAX_LONG_EDGE / long_edge
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # 统一存成 .jpg
    target = f.with_suffix('.jpg')
    img.save(target, 'JPEG', quality=JPG_QUALITY, optimize=True)
    if f.suffix.lower() == '.png' and target != f:
        f.unlink()  # 删原 PNG

    after = target.stat().st_size
    ratio = after / before * 100
    print(f"{f.name:<15} {before/1024:>7.0f} KB → {after/1024:>7.0f} KB   {ratio:>6.1f}%")

print("\n✅ 全部完成")
