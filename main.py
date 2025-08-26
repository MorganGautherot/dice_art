from PIL import Image, ImageDraw
import numpy as np
import os

def image_to_dice(input_path, output_svg="dice_art.svg", output_png="dice_preview.png",
                  cell=24, scale_factor=4):
    """
    Convertit une image en mosaïque de dés (SVG + PNG preview).
    
    input_path   : chemin de l'image d'entrée
    output_svg   : chemin de sortie du fichier SVG
    output_png   : chemin de sortie du fichier PNG preview
    cell         : taille d'un dé en pixels
    scale_factor : multiplicateur pour la taille finale de l'image
    """
    # 1. Charger image et convertir en niveaux de gris
    img = Image.open(input_path).convert("L")
    W, H = img.size
    nx, ny = W // cell, H // cell
    arr = np.array(img)

    # 2. Moyenne de gris par bloc
    means = np.zeros((ny, nx), dtype=float)
    for j in range(ny):
        for i in range(nx):
            block = arr[j*cell:(j+1)*cell, i*cell:(i+1)*cell]
            means[j, i] = block.mean()

    # 3. Quantification en 6 niveaux → faces de dé
    bins = np.linspace(0, 256, 7)
    faces = np.digitize(means, bins)  # 1..6

    # 4. Fonctions utilitaires pour SVG
    def pip_positions(face, s):
        """Retourne positions des points pour un dé face=1..6"""
        left, midx, right = s*0.25, s*0.5, s*0.75
        top, midy, bottom = s*0.25, s*0.5, s*0.75
        pos = {
            1: [(midx, midy)],
            2: [(left, top), (right, bottom)],
            3: [(left, top), (midx, midy), (right, bottom)],
            4: [(left, top), (right, top), (left, bottom), (right, bottom)],
            5: [(left, top), (right, top), (midx, midy), (left, bottom), (right, bottom)],
            6: [(left, top), (left, midy), (left, bottom),
                (right, top), (right, midy), (right, bottom)]
        }
        return pos[face]

    def svg_rect(x, y, w, h, rx=4, ry=4, fill="#ffffff", stroke="#000000"):
        return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>\n'

    def svg_circle(cx, cy, r, fill="#000000"):
        return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" />\n'

    # 5. Créer SVG
    svg_w, svg_h = nx*cell*scale_factor, ny*cell*scale_factor
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">\n']
    svg.append('<rect width="100%" height="100%" fill="white"/>\n')

    for j in range(ny):
        for i in range(nx):
            face = int(faces[j, i])
            x, y = i*cell*scale_factor, j*cell*scale_factor
            pad = cell * 0.07 * scale_factor
            w = h = (cell - 2*(cell*0.07)) * scale_factor
            # Couleur du dé uniforme
            fill = "rgb(240,240,245)"
            svg.append(svg_rect(x+pad, y+pad, w, h, rx=cell*0.12*scale_factor, ry=cell*0.12*scale_factor,
                                fill=fill, stroke="#222"))
            pip_r = max(1.8, cell*0.06*scale_factor)
            for (px, py) in pip_positions(face, w):
                cx, cy = x+pad+px, y+pad+py
                svg.append(svg_circle(cx, cy, pip_r))

    svg.append("</svg>")
    with open(output_svg, "w", encoding="utf-8") as f:
        f.write("".join(svg))

    # 6. Générer un PNG preview avec PIL
    preview = Image.new("RGB", (svg_w, svg_h), "white")
    draw = ImageDraw.Draw(preview)
    for j in range(ny):
        for i in range(nx):
            face = int(faces[j, i])
            x, y = i*cell*scale_factor, j*cell*scale_factor
            pad = cell*0.07*scale_factor
            w = h = (cell - 2*(cell*0.07))*scale_factor
            draw.rounded_rectangle([x+pad, y+pad, x+pad+w, y+pad+h],
                                   radius=int(cell*0.12*scale_factor),
                                   fill=(240, 240, 245), outline=(30, 30, 30))
            pip_r = max(1.8, cell*0.06*scale_factor)
            for (px, py) in pip_positions(face, w):
                cx, cy = x+pad+px, y+pad+py
                draw.ellipse([cx-pip_r, cy-pip_r, cx+pip_r, cy+pip_r], fill=(10, 10, 10))

    preview.save(output_png)
    total_dice = nx * ny
    print(f"✅ Fini ! SVG: {output_svg}, PNG preview: {output_png}")
    print(f"🎲 Nombre de dés nécessaires : {total_dice}")

if __name__ == "__main__":
    # Remplacez "1710150656226.jpeg" par le nom de votre image
    image_to_dice("1710150656226.jpeg", "dice_art.svg", "dice_preview.png", cell=3, scale_factor=9)
