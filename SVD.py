import streamlit as st
import os
import sys
import PIL.Image
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# แก้ปัญหา Pillow
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

st.set_page_config(page_title="Jigsaw Assembler Pro", layout="wide")

st.title("🎬 Jigsaw Assembler: Terminal Mode")

# --- UI Layout ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📁 Upload & Settings")
    sub_header = st.text_input("Sub-header Text", "THE JIGSAW CHRONICLES: EP.01")
    uploaded_files = st.file_uploader("Add MP4 Files", type=["mp4"], accept_multiple_files=True)
    start_btn = st.button("🚀 Start Assembly")

with col2:
    st.header("📟 Terminal Output")
    # สร้างช่องว่างสำหรับแสดง Log เหมือนใน Terminal
    terminal_log = st.empty()
    log_content = ""


# --- ฟังก์ชันสำหรับ Update Terminal บนหน้าเว็บ ---
def write_to_terminal(text):
    global log_content
    log_content += text + "\n"
    # แสดงผลในรูปแบบ Code Block เพื่อให้เหมือน Terminal
    terminal_log.code(log_content)


if start_btn and uploaded_files:
    write_to_terminal("📌 เริ่มต้นระบบ Jigsaw Assembler...")

    clips = []
    try:
        for uploaded_file in uploaded_files:
            write_to_terminal(f"📥 กำลังโหลดไฟล์: {uploaded_file.name}")

            # เซฟไฟล์ชั่วคราว
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ประมวลผลแต่ละคลิป
            clip = VideoFileClip(temp_path).resize(height=1080)

            txt = TextClip(sub_header, fontsize=58, color='cyan', font='DejaVu-Sans-Bold',
                           bg_color='black').set_opacity(0.6)
            txt = txt.set_position(('center', 100)).set_duration(clip.duration)

            combined = CompositeVideoClip([clip, txt])
            clips.append(combined)
            write_to_terminal(f"✅ ประมวลผล {uploaded_file.name} สำเร็จ")

            os.remove(temp_path)

        if clips:
            write_to_terminal("🎬 กำลังรวมคลิปและ Rendering (ขั้นตอนนี้ใช้เวลานิดนึง)...")
            final = concatenate_videoclips(clips, method="compose")

            # สั่ง Render และให้มันบอกสถานะ
            output_file = "Jigsaw_Series_Final.mp4"
            final.write_videofile(output_file, fps=24, codec="libx264", logger='bar')

            write_to_terminal(f"🎊 Done! ไฟล์พร้อมใช้งานที่: {output_file}")
            st.success("✅ รวมคลิปสำเร็จ!")

            # แสดงวิดีโอผลลัพธ์
            with open(output_file, 'rb') as v:
                st.video(v.read())

    except Exception as e:
        write_to_terminal(f"❌ ERROR: {str(e)}")
        st.error(f"เกิดข้อผิดพลาด: {e}")

        for uploaded_file in uploaded_files:
            write_to_terminal(f"📥 กำลังโหลดไฟล์: {uploaded_file.name}")

            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ใช้ context manager หรือสั่งปิดคลิปหลังประมวลผล
            clip = VideoFileClip(temp_path).resize(height=1080)

            txt = TextClip(sub_header, fontsize=58, color='cyan', font='DejaVu-Sans-Bold',
                           bg_color='black').set_opacity(0.6)
            txt = txt.set_position(('center', 100)).set_duration(clip.duration)

            combined = CompositeVideoClip([clip, txt])
            clips.append(combined)

            # --- จุดสำคัญ: เราจะยังไม่ลบไฟล์ที่นี่ เพราะ MoviePy ต้องใช้จนกว่าจะ Render เสร็จ ---
            write_to_terminal(f"✅ เตรียมไฟล์ {uploaded_file.name} สำเร็จ")

        if clips:
            write_to_terminal("🎬 กำลัง Render... (ขั้นตอนนี้ MoviePy กำลังอ่านไฟล์ชั่วคราวอยู่)")
            final = concatenate_videoclips(clips, method="compose")
            output_file = "Jigsaw_Series_Final.mp4"
            final.write_videofile(output_file, fps=24, codec="libx264")

            # --- ย้ายมาลบไฟล์ทั้งหมดหลัง Render เสร็จแล้ว ---
            for clip in clips:
                clip.close()  # สั่งปิดไฟล์ทั้งหมด

            for uploaded_file in uploaded_files:
                try:
                    os.remove(f"temp_{uploaded_file.name}")
                except:
                    pass  # กันเหนียวถ้าไฟล์ยังล็อคอยู่

            write_to_terminal(f"🎊 Done! ไฟล์อยู่ที่: {output_file}")
            st.success("✅ รวมคลิปสำเร็จ!")