import sqlite3

conn = sqlite3.connect(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\content_engine.db")
c = conn.cursor()

c.execute("""
    UPDATE story_parts
    SET status = 'COMPLETED',
        raw_video_path = 'C:\\TheNaughtyDuo_Automation\\the-naughty-duo-autonomous-content-engine\\data\\raw_clips\\ep_18_scene_01.mp4'
    WHERE story_id = 'ep_18_magic_freeze_remote' AND part_number = 1
""")

c.execute("""
    UPDATE story_parts
    SET status = 'COMPLETED',
        raw_video_path = 'C:\\TheNaughtyDuo_Automation\\the-naughty-duo-autonomous-content-engine\\data\\raw_clips\\ep_18_scene_02.mp4'
    WHERE story_id = 'ep_18_magic_freeze_remote' AND part_number = 2
""")

c.execute("""
    UPDATE story_parts
    SET status = 'COMPLETED',
        raw_video_path = 'C:\\TheNaughtyDuo_Automation\\the-naughty-duo-autonomous-content-engine\\data\\raw_clips\\ep_18_scene_03.mp4'
    WHERE story_id = 'ep_18_magic_freeze_remote' AND part_number = 3
""")

c.execute("""
    UPDATE stories
    SET state = 'COMPLETED'
    WHERE id = 'ep_18_magic_freeze_remote'
""")

conn.commit()
conn.close()
print("DB updated successfully for Episode 18 (All 3 scenes COMPLETED)!")
