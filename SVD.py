import streamlit as st
import os
import PIL.Image
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# --- FIX PILLOW ANTIALIAS ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

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

# --- MAIN ENGINE ---
if start_btn and uploaded_files:
    write_to_terminal("📌 เริ่มต้นกระบวนการ Jigsaw Assembler...")
    clips = []
    temp_files = []

    try:
        for uploaded_file in uploaded_files:
            write_to_terminal(f"📥 เตรียมไฟล์: {uploaded_file.name}")
            
            # สร้าง Temp File
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_files.append(temp_path)

            # โหลดคลิป
            clip = VideoFileClip(temp_path).resize(height=1080)
            
            # --- TextClip Fix (แก้ปัญหา Security Policy บน Cloud) ---
            # เราจะไม่ใช้ bg_color และใช้ Font มาตรฐานของ Linux
            txt = TextClip(
                sub_header, 
                fontsize=70, 
                color='cyan', 
                font='DejaVu-Sans-Bold'
            ).set_duration(clip.duration).set_position(('center', 100))

            # รวมคลิป
            combined = CompositeVideoClip([clip, txt])
            clips.append(combined)
            write_to_terminal(f"✅ ประมวลผล {uploaded_file.name} สำเร็จ")

        if clips:
            write_to_terminal("🎬 กำลัง Render วิดีโอรวม... (อาจใช้เวลาหลายนาที)")
            
            final = concatenate_videoclips(clips, method="compose")
            output_file = "Jigsaw_Final_Output.mp4"
            
            # Render ไฟล์
            final.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

            write_to_terminal(f"🎊 สำเร็จ! ไฟล์อยู่ที่: {output_file}")
            st.success("✅ รวมวิดีโอเรียบร้อย!")
            
            # แสดงและให้ดาวน์โหลด
            with open(output_file, 'rb') as v:
                st.video(v.read())
                st.download_button("📥 Download Video", data=v, file_name=output_file, mime="video/mp4")

    except Exception as e:
        write_to_terminal(f"❌ ERROR: {str(e)}")
        st.error(f"เกิดข้อผิดพลาด: {e}")

    finally:
        # ล้างระบบ
        write_to_terminal("🧹 กำลังล้างไฟล์ชั่วคราว...")
        for c in clips:
            try: c.close()
            except: pass
        
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except: pass
        write_to_terminal("✨ ระบบพร้อมทำงานใหม่แล้ว")

else:
    if start_btn:
        st.warning("กรุณาเลือกไฟล์วิดีโอก่อนครับ")
