import streamlit as st
import numpy as np
from PIL import Image
import scipy.ndimage as ndimage
from collections import Counter

st.set_page_config(page_title="Pixel Magic", page_icon="pixel art", layout="centered")
st.title("Pixel Magic")
st.markdown("### Trasforma foto in pixel art con colori limitati e pulizia intelligente")

with st.sidebar:
    st.header("Impostazioni")
    max_colors = st.slider("Max colori", 2, 500, 16)
    target_width = st.slider("Larghezza (px)", 10, 800, 100)
    min_size = st.slider("Min pixel contigui", 1, 20, 3)
    st.markdown("---")
    st.caption("Carica → Regola → Converti → Scarica")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Originale")
    uploaded = st.file_uploader("Trascina foto", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    orig_ph = st.empty()
with col2:
    st.subheader("Risultato")
    res_ph = st.empty()

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    orig_ph.image(img, use_column_width=True, caption=f"Originale: {img.width}×{img.height}")
    if st.button("CONVERTI ORA", type="primary", use_container_width=True):
        with st.spinner("Elaborazione..."):
            ratio = target_width / img.width
            h = int(img.height * ratio)
            img = img.resize((target_width, h), Image.Resampling.LANCZOS)
            img = img.convert("P", palette=Image.ADAPTIVE, colors=max_colors).convert("RGB")
            if min_size > 1:
                arr = np.array(img)
                arr = remove_small_regions(arr, min_size)
                img = Image.fromarray(arr)
            res_ph.image(img, use_column_width=True, caption=f"Risultato: {img.width}×{img.height}")
            from io import BytesIO
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.download_button("Scarica (PNG)", buf.getvalue(), f"pixelart_{target_width}px_{max_colors}c.png", "image/png", use_container_width=True)
else:
    st.info("Carica un'immagine per iniziare!")

def remove_small_regions(img_array, min_size):
    h, w, _ = img_array.shape
    flat = img_array.reshape(-1, 3)
    colors, inv = np.unique(flat, axis=0, return_inverse=True)
    labels = inv.reshape(h, w)
    struct = ndimage.generate_binary_structure(2, 2)
    labeled, n = ndimage.label(labels, struct)
    sizes = ndimage.sum(np.ones_like(labels), labeled, range(1, n+1))
    small = np.where(sizes < min_size)[0] + 1
    mask = np.isin(labeled, small)
    result = img_array.copy()
    for y in range(h):
        for x in range(w):
            if mask[y, x]:
                neigh = []
                for dy in [-1,0,1]:
                    for dx in [-1,0,1]:
                        ny, nx = y+dy, x+dx
                        if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx]:
                            neigh.append(tuple(img_array[ny, nx]))
                if neigh:
                    result[y, x] = Counter(neigh).most_common(1)[0][0]
    return result

st.markdown("---")
st.caption("Fatto con amore su Linux")
