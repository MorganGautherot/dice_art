from PIL import Image, ImageDraw
import numpy as np
import os
from conf import DICE_COLORS

def image_to_dice(input_path, output_svg="dice_art.svg", output_png="dice_preview.png",
                  cell=24, scale_factor=4, black_only=False):
    """
    Convertit une image en mosaïque de dés (SVG + PNG preview).
    
    input_path   : chemin de l'image d'entrée
    output_svg   : chemin de sortie du fichier SVG
    output_png   : chemin de sortie du fichier PNG preview
    cell         : taille d'un dé en pixels
    scale_factor : multiplicateur pour la taille finale de l'image
    black_only   : utilise uniquement des dés noirs (True/False)
    """
    # 1. Charger image (garder les couleurs)
    img_color = Image.open(input_path).convert("RGB")
    img_gray = img_color.convert("L")
    W, H = img_gray.size
    nx, ny = W // cell, H // cell
    arr_gray = np.array(img_gray)
    arr_color = np.array(img_color)

    # 2. Moyenne de gris et couleur par bloc
    means = np.zeros((ny, nx), dtype=float)
    colors = np.zeros((ny, nx, 3), dtype=int)
    for j in range(ny):
        for i in range(nx):
            block_gray = arr_gray[j*cell:(j+1)*cell, i*cell:(i+1)*cell]
            block_color = arr_color[j*cell:(j+1)*cell, i*cell:(i+1)*cell]
            means[j, i] = block_gray.mean()
            colors[j, i] = block_color.mean(axis=(0, 1))

    # 3. Quantification en 6 niveaux → faces de dé
    bins = np.linspace(0, 256, 7)
    faces = np.digitize(means, bins)  # 1..6
    
    # 3.5. Couleurs de dés disponibles (importées depuis conf.py)
    # Compteur des dés par couleur
    dice_count = {color_name: 0 for color_name in DICE_COLORS.keys()}
    
    def find_closest_color(rgb):
        """Trouve la couleur de dé la plus proche"""
        r, g, b = rgb
        min_distance = float('inf')
        closest_color = DICE_COLORS["white"]  # blanc par défaut
        
        for color_rgb in DICE_COLORS.values():
            cr, cg, cb = color_rgb
            # Distance euclidienne dans l'espace RGB
            distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_color = color_rgb
        
        return closest_color
    
    def get_color_name(color_rgb):
        """Trouve le nom de couleur correspondant au RGB"""
        for color_name, rgb_value in DICE_COLORS.items():
            if rgb_value == color_rgb:
                return color_name
        return "unknown"

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
            # Couleur du dé
            if black_only:
                closest_color = DICE_COLORS["black"]
            else:
                original_color = colors[j, i]
                closest_color = find_closest_color(original_color)
            # Compter les dés par couleur
            color_name = get_color_name(closest_color)
            dice_count[color_name] += 1
            r, g, b = closest_color
            fill = f"rgb({r},{g},{b})"
            svg.append(svg_rect(x+pad, y+pad, w, h, rx=cell*0.12*scale_factor, ry=cell*0.12*scale_factor,
                                fill=fill, stroke="#222"))
            pip_r = max(1.8, cell*0.06*scale_factor)
            # Couleur des points : blanc sauf si fond blanc alors noir
            pip_color = "black" if closest_color == DICE_COLORS["white"] else "white"
            for (px, py) in pip_positions(face, w):
                cx, cy = x+pad+px, y+pad+py
                svg.append(svg_circle(cx, cy, pip_r, fill=pip_color))

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
            # Couleur du dé
            if black_only:
                closest_color = DICE_COLORS["black"]
            else:
                original_color = colors[j, i]
                closest_color = find_closest_color(original_color)
            draw.rounded_rectangle([x+pad, y+pad, x+pad+w, y+pad+h],
                                   radius=int(cell*0.12*scale_factor),
                                   fill=closest_color, outline=(30, 30, 30))
            pip_r = max(1.8, cell*0.06*scale_factor)
            # Couleur des points : blanc sauf si fond blanc alors noir
            pip_color = (10, 10, 10) if closest_color == DICE_COLORS["white"] else (255, 255, 255)
            for (px, py) in pip_positions(face, w):
                cx, cy = x+pad+px, y+pad+py
                draw.ellipse([cx-pip_r, cy-pip_r, cx+pip_r, cy+pip_r], fill=pip_color)

    preview.save(output_png)
    total_dice = nx * ny
    print(f"✅ Fini ! SVG: {output_svg}, PNG preview: {output_png}")
    print(f"🎲 Nombre de dés par couleur :")
    for color_name, count in dice_count.items():
        if count > 0:  # Afficher seulement les couleurs utilisées
            print(f"   {color_name}: {count} dés")
    print(f"   Total: {total_dice} dés")

if __name__ == "__main__":
    # Remplacez "1710150656226.jpeg" par le nom de votre image
    image_to_dice("pika.avif", "dice_art.svg", "dice_preview.png", cell=5, scale_factor=8, black_only=True)
