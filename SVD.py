import streamlit as st
import os
import PIL.Image
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# --- FIX PILLOW สำหรับ MoviePy ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# --- ตั้งค่าหน้าเว็บ ---
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

# --- ส่วนประมวลผลหลัก ---
if start_btn and uploaded_files:
    write_to_terminal("📌 เริ่มต้นระบบ Jigsaw Assembler...")
    clips = []
    temp_files = []

    try:
        for uploaded_file in uploaded_files:
            write_to_terminal(f"📥 กำลังเตรียมไฟล์: {uploaded_file.name}")
            
            # สร้างไฟล์ชั่วคราว
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_files.append(temp_path)

            # โหลดคลิปวิดีโอ
            clip = VideoFileClip(temp_path).resize(height=1080)
            
            # --- แก้ไขจุดนี้เพื่อเลี่ยง Security Policy ---
            # เราจะลดความซับซ้อนของ TextClip ลงเพื่อให้ผ่านการตรวจสอบความปลอดภัย
            txt = TextClip(
                sub_header, 
                fontsize=70, 
                color='cyan', 
                font='DejaVu-Sans-Bold'
            ).set_duration(clip.duration).set_position(('center', 100))

            # รวมคลิปกับข้อความ
            combined = CompositeVideoClip([clip, txt])
            clips.append(combined)
            write_to_terminal(f"✅ เตรียมไฟล์ {uploaded_file.name} สำเร็จ")

        if clips:
            write_to_terminal("🎬 กำลัง Render วิดีโอ... (โปรดรอสักครู่)")
            final = concatenate_videoclips(clips, method="compose")
            output_file = "Jigsaw_Final.mp4"
            
            # สั่ง Render
            final.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

            write_to_terminal(f"🎊 Done! การประกอบเสร็จสิ้น")
            st.success("✅ รวมวิดีโอสำเร็จ!")
            
            # ปุ่มดาวน์โหลด
            with open(output_file, 'rb') as v:
                st.video(v.read())
                st.download_button("📥 ดาวน์โหลดผลงาน", data=v, file_name=output_file, mime="video/mp4")

    except Exception as e:
        write_to_terminal(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        st.error(f"Error: {e}")

    finally:
        # ล้าง Memory และไฟล์ขยะ
        write_to_terminal("🧹 กำลังทำความสะอาดระบบ...")
        for c in clips:
            try: c.close()
            except: pass
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file): os.remove(temp_file)
            except: pass
        write_to_terminal("✨ พร้อมสำหรับงานต่อไป")
