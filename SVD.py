import streamlit as st
import os
import PIL.Image
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# --- PILLOW FIX FOR MOVIEPY ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# --- APP CONFIG ---
st.set_page_config(page_title="Jigsaw Assembler Pro", layout="wide")
st.title("🎬 Jigsaw Assembler: Terminal Mode")

# --- UI LAYOUT ---
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


# --- MAIN LOGIC ---
if start_btn and uploaded_files:
    write_to_terminal("📌 ระบบ Jigsaw Assembler กำลังเริ่มต้น...")
    clips = []
    temp_files = []

    try:
        for uploaded_file in uploaded_files:
            write_to_terminal(f"📥 กำลังจัดเตรียม: {uploaded_file.name}")

            # สร้างไฟล์ชั่วคราว
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_files.append(temp_path)

            # โหลดคลิปและปรับขนาด
            clip = VideoFileClip(temp_path).resize(height=1080)

            # สร้าง Text Overlay (ใช้ Font มาตรฐาน Linux เพื่อความปลอดภัยบน Cloud)
            txt = TextClip(
                sub_header,
                fontsize=60,
                color='cyan',
                font='DejaVu-Sans-Bold',
                bg_color='black'
            ).set_opacity(0.7)

            txt = txt.set_position(('center', 100)).set_duration(clip.duration)

            # รวมคลิปกับข้อความ
            combined = CompositeVideoClip([clip, txt])
            clips.append(combined)
            write_to_terminal(f"✅ เตรียมไฟล์ {uploaded_file.name} เรียบร้อย")

        if clips:
            write_to_terminal("🎬 กำลังรวมคลิปและ Rendering Final Video... (ขั้นตอนนี้ใช้เวลาครู่หนึ่ง)")

            # รวมคลิปทั้งหมดเข้าด้วยกัน
            final = concatenate_videoclips(clips, method="compose")

            output_file = "Jigsaw_Series_Final.mp4"

            # สั่งเขียนไฟล์ (aac สำหรับเสียง และ libx264 สำหรับวิดีโอ)
            final.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

            write_to_terminal(f"🎊 การประกอบเสร็จสิ้น! ไฟล์: {output_file}")
            st.success("✅ รวมคลิปสำเร็จ!")

            # แสดงวิดีโอผลลัพธ์
            with open(output_file, 'rb') as v:
                st.video(v.read())
                st.download_button(
                    label="📥 ดาวน์โหลดวิดีโอ (Click to Download)",
                    data=v,
                    file_name=output_file,
                    mime="video/mp4"
                )

    except Exception as e:
        write_to_terminal(f"❌ ERROR: {str(e)}")
        st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")

    finally:
        # --- CLEANUP: ปิดไฟล์และลบ Temp เพื่อคืน Memory ให้ Server ---
        write_to_terminal("🧹 กำลังทำความสะอาดระบบ...")
        for c in clips:
            try:
                c.close()
            except:
                pass

        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        write_to_terminal("✨ ระบบพร้อมสำหรับงานถัดไป")

else:
    if start_btn:
        st.warning("กรุณาอัปโหลดไฟล์วิดีโอก่อนกดปุ่มครับ")