import PIL.Image
# แก้ปัญหา Pillow 10.0.0+ ที่ไม่มี ANTIALIAS
if not hasattr(PIL.Image, 'ANTIALIAS'):
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
import streamlit as st
import os
import numpy as np
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip

# --- APP CONFIG ---
st.set_page_config(page_title="Jigsaw Assembler Pro", layout="wide")
st.title("🎬 Jigsaw Assembler: Terminal Mode")

col1, col2 = st.columns([1, 1])
with col1:
    st.header("📁 Upload & Settings")
    sub_header = st.text_input("Sub-header Text", "THE JIGSAW CHRONICLES: EP.01")
    uploaded_files = st.file_uploader("Add MP4 Files", type=["mp4"], accept_multiple_files=True)
    start_btn = st.button("🚀 Start Assembly")

with col2:
    st.header("📟 Terminal Output")
    terminal_log = st.empty()
    log_content = ""

def write_to_terminal(text):
    global log_content
    log_content += text + "\n"
    terminal_log.code(log_content)

# --- ฟังก์ชันวาด Text ด้วย Pillow (เลี่ยง ImageMagick Policy) ---
def create_text_image(text, width, height):
    # สร้างภาพโปร่งใส
    img = PIL.Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = PIL.ImageDraw.Draw(img)
    
    # พยายามโหลด Font (Linux Cloud มักมีฟอนต์นี้)
    try:
        font = PIL.ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = PIL.ImageFont.load_default()

    # วาดพื้นหลังดำจางๆ (แทน bg_color)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    
    padding = 20
    rect_x0 = (width - tw) // 2 - padding
    rect_y0 = 100 - padding
    rect_x1 = (width + tw) // 2 + padding
    rect_y1 = 100 + th + padding
    
    draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(0, 0, 0, 160)) # สีดำจางๆ
    draw.text(((width - tw) // 2, 100), text, font=font, fill=(0, 255, 255, 255)) # สี Cyan
    
    return np.array(img)

# --- MAIN LOGIC ---
if start_btn and uploaded_files:
    write_to_terminal("📌 เริ่มต้นระบบเลี่ยง Security Policy...")
    clips = []
    temp_files = []

    try:
        for uploaded_file in uploaded_files:
            write_to_terminal(f"📥 เตรียมไฟล์: {uploaded_file.name}")
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_files.append(temp_path)

            # โหลดคลิป
            clip = VideoFileClip(temp_path).resize(height=1080)
            w, h = clip.size

            # สร้าง Text ด้วย Pillow แทน TextClip
            txt_img = create_text_image(sub_header, w, h)
            txt_clip = ImageClip(txt_img).set_duration(clip.duration).set_position('center')

            combined = CompositeVideoClip([clip, txt_clip])
            clips.append(combined)
            write_to_terminal(f"✅ เตรียม {uploaded_file.name} สำเร็จ (Pillow Render)")

        if clips:
            write_to_terminal("🎬 กำลัง Render Final Video...")
            final = concatenate_videoclips(clips, method="compose")
            output_file = "Jigsaw_Final.mp4"
            final.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

            write_to_terminal("🎊 เสร็จสมบูรณ์!")
            st.success("✅ รวมวิดีโอสำเร็จ!")
            with open(output_file, 'rb') as v:
                st.video(v.read())
                st.download_button("📥 ดาวน์โหลด", data=v, file_name=output_file)

    except Exception as e:
        write_to_terminal(f"❌ ERROR: {str(e)}")
        st.error(f"เกิดข้อผิดพลาด: {e}")

    finally:
        for c in clips:
            try: c.close()
            except: pass
        for f in temp_files:
            try: os.remove(f)
            except: pass
        write_to_terminal("✨ ระบบล้างไฟล์เรียบร้อย")
