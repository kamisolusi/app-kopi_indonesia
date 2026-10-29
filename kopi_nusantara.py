"""
Jejak Kopi Nusantara
Dashboard Streamlit tentang daerah asal kopi di Indonesia.

Cara menjalankan:
    pip install streamlit pandas numpy plotly
    streamlit run kopi_nusantara.py

Catatan: koordinat dan ketinggian adalah perkiraan, sedangkan skor rasa
dan volume panen adalah data ilustrasi untuk latihan.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Konfigurasi halaman
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Jejak Kopi Nusantara",
    page_icon="☕",
    layout="wide",
)

# Palet warna
SAGE = "#E6ECE3"     # latar
DAUN = "#2F5D46"     # hijau daun kopi
CERI = "#A8322D"     # merah buah kopi matang
SANGRAI = "#5B3A29"  # cokelat biji sangrai
EMAS = "#C9A227"     # aksen kecil
TINTA = "#1E2B24"    # teks

# ------------------------------------------------------------------
# CSS khusus
# ------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Young+Serif&family=Instrument+Sans:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Instrument Sans', system-ui, sans-serif;
        color: {TINTA};
    }}
    .stApp {{ background: {SAGE}; }}

    h1, h2, h3 {{
        font-family: 'Young Serif', Georgia, serif !important;
        color: {TINTA} !important;
        letter-spacing: -0.01em;
    }}

    section[data-testid="stSidebar"] {{
        background: {DAUN};
    }}
    section[data-testid="stSidebar"] * {{
        color: #F2F5EF !important;
    }}

    .hero-judul {{
        font-family: 'Young Serif', Georgia, serif;
        font-size: clamp(2.6rem, 6vw, 4.8rem);
        line-height: 1.0;
        margin: 0.2rem 0 0.6rem 0;
        color: {SANGRAI};
    }}
    .hero-teks {{
        font-size: 1.1rem;
        max-width: 60ch;
        line-height: 1.55;
        opacity: 0.85;
    }}

    .strip {{
        display: flex;
        flex-wrap: wrap;
        border-top: 2px solid {SANGRAI};
        border-bottom: 1px solid rgba(91,58,41,0.3);
        margin: 1.2rem 0 1.8rem 0;
    }}
    .strip div {{
        flex: 1 1 160px;
        padding: 0.9rem 1rem;
        border-right: 1px solid rgba(91,58,41,0.2);
    }}
    .strip div:last-child {{ border-right: none; }}
    .strip b {{
        display: block;
        font-family: 'Young Serif', Georgia, serif;
        font-size: 2rem;
        font-weight: 400;
        color: {CERI};
    }}
    .strip span {{ font-size: 0.9rem; opacity: 0.8; }}

    .kartu-asal {{
        background: #FFFFFF;
        border-left: 6px solid {CERI};
        padding: 1.2rem 1.4rem;
        border-radius: 4px;
    }}
    .kartu-asal h3 {{ margin: 0 0 0.3rem 0; }}
    .kartu-asal p {{ margin: 0.2rem 0; line-height: 1.5; }}

    .catatan {{
        font-size: 0.85rem;
        opacity: 0.7;
        margin-top: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Data
# ------------------------------------------------------------------
@st.cache_data
def muat_data():
    asal = pd.DataFrame(
        [
            # nama, provinsi, lat, lon, ketinggian, jenis, catatan rasa
            ["Gayo", "Aceh", 4.60, 96.85, 1400, "Arabika", "Rempah, cokelat, body tebal"],
            ["Mandailing", "Sumatera Utara", 0.90, 99.60, 1200, "Arabika", "Herbal, earthy, manis karamel"],
            ["Kerinci", "Jambi", -1.70, 101.30, 1500, "Arabika", "Buah merah, asam cerah"],
            ["Lampung", "Lampung", -5.00, 104.50, 600, "Robusta", "Cokelat pahit, kacang"],
            ["Java Preanger", "Jawa Barat", -7.10, 107.60, 1400, "Arabika", "Gula aren, floral lembut"],
            ["Temanggung", "Jawa Tengah", -7.30, 110.10, 800, "Robusta", "Tembakau, cokelat, pekat"],
            ["Ijen", "Jawa Timur", -8.00, 114.20, 1300, "Arabika", "Jeruk, teh hitam"],
            ["Kintamani", "Bali", -8.25, 115.35, 1200, "Arabika", "Jeruk segar, asam tinggi"],
            ["Bajawa", "NTT", -8.80, 120.98, 1300, "Arabika", "Vanila, tembakau manis"],
            ["Toraja", "Sulawesi Selatan", -3.00, 119.90, 1500, "Arabika", "Rempah, buah gelap"],
            ["Wamena", "Papua", -4.10, 138.95, 1600, "Arabika", "Bersih, manis, cokelat susu"],
        ],
        columns=["Asal", "Provinsi", "lat", "lon", "Ketinggian", "Jenis", "Karakter"],
    )

    # Skor rasa ilustrasi (skala 1-10)
    skor = {
        "Gayo":          [6.5, 8.5, 7.0, 8.0, 7.5],
        "Mandailing":    [5.5, 8.0, 7.5, 7.0, 7.0],
        "Kerinci":       [8.0, 6.5, 7.5, 7.5, 7.0],
        "Lampung":       [4.0, 8.5, 5.5, 6.0, 6.5],
        "Java Preanger": [6.5, 7.0, 8.0, 7.5, 7.0],
        "Temanggung":    [4.5, 9.0, 6.0, 6.5, 7.0],
        "Ijen":          [7.5, 6.5, 7.0, 7.5, 7.0],
        "Kintamani":     [8.5, 6.0, 7.0, 8.0, 6.5],
        "Bajawa":        [6.5, 7.5, 8.0, 8.0, 7.5],
        "Toraja":        [6.5, 8.0, 7.0, 8.0, 8.0],
        "Wamena":        [6.0, 7.0, 8.5, 7.5, 8.0],
    }
    aspek = ["Keasaman", "Body", "Manis", "Aroma", "Aftertaste"]
    rasa = pd.DataFrame(skor, index=aspek).T.reset_index(names="Asal")
    asal = asal.merge(rasa, on="Asal")
    asal["Skor"] = asal[aspek].mean(axis=1).round(2)

    # Volume panen bulanan ilustrasi (ton)
    rng = np.random.default_rng(7)
    bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
             "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    baris = []
    for i, nama in enumerate(asal["Asal"]):
        puncak = (4 + i) % 12
        dasar = 400 if asal.loc[i, "Jenis"] == "Robusta" else 180
        for b in range(12):
            jarak = min(abs(b - puncak), 12 - abs(b - puncak))
            nilai = dasar * np.exp(-(jarak ** 2) / 6) + rng.normal(15, 8)
            baris.append([nama, bulan[b], b, max(nilai, 5)])
    panen = pd.DataFrame(baris, columns=["Asal", "Bulan", "urut", "Ton"])
    return asal, panen, aspek


asal, panen, ASPEK = muat_data()

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ☕ Saring kebun")
    jenis = st.multiselect(
        "Jenis kopi",
        options=["Arabika", "Robusta"],
        default=["Arabika", "Robusta"],
    )
    rentang = st.slider(
        "Ketinggian kebun (mdpl)",
        min_value=500, max_value=1700, value=(500, 1700), step=50,
    )

data = asal[asal["Jenis"].isin(jenis) & asal["Ketinggian"].between(*rentang)]

with st.sidebar:
    if data.empty:
        pilihan = None
    else:
        pilihan = st.selectbox("Lihat profil rasa", data["Asal"].tolist())
    st.markdown("---")
    st.caption("Geser filter di atas, peta dan grafik ikut berubah.")

# ------------------------------------------------------------------
# Hero
# ------------------------------------------------------------------
st.markdown('<div class="hero-judul">Jejak Kopi<br>Nusantara</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-teks">Dari dataran tinggi Gayo sampai lembah Baliem, '
    "setiap kebun memberi rasa yang berbeda. Jelajahi asal kopi Indonesia "
    "berdasarkan ketinggian, jenis, dan profil rasanya.</p>",
    unsafe_allow_html=True,
)

if data.empty:
    st.warning("Tidak ada kebun yang cocok dengan filter. Perlebar rentang ketinggian atau pilih jenis kopi lain.")
    st.stop()

# Ringkasan angka
st.markdown(
    f"""
    <div class="strip">
        <div><b>{len(data)}</b><span>daerah asal</span></div>
        <div><b>{data['Provinsi'].nunique()}</b><span>provinsi</span></div>
        <div><b>{int(data['Ketinggian'].mean()):,}</b><span>rata-rata mdpl</span></div>
        <div><b>{data.loc[data['Skor'].idxmax(), 'Asal']}</b><span>skor rasa tertinggi</span></div>
    </div>
    """.replace(",", "."),
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Peta
# ------------------------------------------------------------------
peta = px.scatter_geo(
    data,
    lat="lat",
    lon="lon",
    size="Ketinggian",
    color="Jenis",
    hover_name="Asal",
    hover_data={"Provinsi": True, "Ketinggian": True, "Karakter": True,
                "lat": False, "lon": False, "Jenis": False},
    color_discrete_map={"Arabika": CERI, "Robusta": SANGRAI},
    size_max=28,
)
peta.update_geos(
    lataxis_range=[-11.5, 7],
    lonaxis_range=[94, 142],
    showland=True, landcolor="#CBD8C6",
    showocean=True, oceancolor=SAGE,
    showcountries=False, showcoastlines=True, coastlinecolor="#9FB39A",
    showframe=False, bgcolor="rgba(0,0,0,0)",
)
peta.update_layout(
    height=430,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", y=1.02, x=0, title=None,
                font=dict(family="Instrument Sans", size=13)),
)
st.plotly_chart(peta, use_container_width=True)

# ------------------------------------------------------------------
# Profil rasa
# ------------------------------------------------------------------
st.markdown("## Profil rasa")
kiri, kanan = st.columns([2, 3], gap="large")

baris = data[data["Asal"] == pilihan].iloc[0]

with kiri:
    st.markdown(
        f"""
        <div class="kartu-asal">
            <h3>{baris['Asal']}</h3>
            <p><b>{baris['Provinsi']}</b>, {baris['Ketinggian']:,} mdpl</p>
            <p>Jenis: {baris['Jenis']}</p>
            <p>Karakter: {baris['Karakter']}</p>
            <p>Skor rata-rata: <b>{baris['Skor']}</b> / 10</p>
        </div>
        """.replace(",", ".", 1),
        unsafe_allow_html=True,
    )

with kanan:
    rata = data[ASPEK].mean()
    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=list(rata) + [rata.iloc[0]],
        theta=ASPEK + [ASPEK[0]],
        name="Rata-rata pilihan",
        line=dict(color="#9FB39A", width=2, dash="dot"),
    ))
    nilai = [baris[a] for a in ASPEK]
    radar.add_trace(go.Scatterpolar(
        r=nilai + [nilai[0]],
        theta=ASPEK + [ASPEK[0]],
        name=baris["Asal"],
        fill="toself",
        fillcolor="rgba(168,50,45,0.25)",
        line=dict(color=CERI, width=3),
    ))
    radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 10], showticklabels=False, gridcolor="#B9C7B4"),
            angularaxis=dict(gridcolor="#B9C7B4",
                             tickfont=dict(family="Instrument Sans", size=13, color=TINTA)),
        ),
        height=360,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.1, font=dict(family="Instrument Sans")),
    )
    st.plotly_chart(radar, use_container_width=True)

# ------------------------------------------------------------------
# Tab: musim panen dan perbandingan
# ------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Musim panen", "Ketinggian vs rasa", "Tabel lengkap"])

with tab1:
    musim = panen[panen["Asal"] == pilihan].sort_values("urut")
    grafik = px.area(musim, x="Bulan", y="Ton")
    grafik.update_traces(line=dict(color=DAUN, width=3),
                         fillcolor="rgba(47,93,70,0.25)")
    grafik.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#C9D4C5", title="Volume (ton)"),
        xaxis=dict(title=None),
        font=dict(family="Instrument Sans", color=TINTA),
    )
    st.plotly_chart(grafik, use_container_width=True)
    puncak = musim.loc[musim["Ton"].idxmax(), "Bulan"]
    st.write(f"Panen **{pilihan}** mencapai puncaknya sekitar bulan **{puncak}**.")

with tab2:
    sebar = px.scatter(
        data, x="Ketinggian", y="Keasaman", size="Skor", color="Jenis",
        text="Asal", color_discrete_map={"Arabika": CERI, "Robusta": SANGRAI},
        size_max=22,
    )
    sebar.update_traces(textposition="top center",
                        textfont=dict(family="Instrument Sans", size=12))
    sebar.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#C9D4C5", title="Ketinggian (mdpl)"),
        yaxis=dict(gridcolor="#C9D4C5", title="Skor keasaman"),
        legend=dict(title=None),
        font=dict(family="Instrument Sans", color=TINTA),
    )
    st.plotly_chart(sebar, use_container_width=True)
    st.write("Semakin tinggi kebun, biasanya keasaman kopi semakin cerah.")

with tab3:
    st.dataframe(
        data[["Asal", "Provinsi", "Jenis", "Ketinggian", "Karakter", "Skor"]]
        .sort_values("Skor", ascending=False),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Ketinggian": st.column_config.NumberColumn("Ketinggian", format="%d mdpl"),
            "Skor": st.column_config.ProgressColumn(
                "Skor rasa", min_value=0, max_value=10, format="%.2f"
            ),
        },
    )
    st.download_button(
        "Unduh data (CSV)",
        data=data.drop(columns=["lat", "lon"]).to_csv(index=False).encode("utf-8"),
        file_name="kopi_nusantara.csv",
        mime="text/csv",
    )

st.markdown(
    '<p class="catatan">Koordinat dan ketinggian adalah perkiraan. '
    "Skor rasa dan volume panen adalah data ilustrasi untuk latihan, bukan data resmi.</p>",
    unsafe_allow_html=True,
)
