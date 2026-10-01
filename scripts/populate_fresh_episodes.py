import json
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager

FRESH_EPISODES = [
    {
        "id": "ep_18_magic_freeze_remote",
        "title": "Mummy Ka Magic Remote! 🎮😂 Sab Freeze Ho Gaye! #TheNaughtyDuo #shorts",
        "concept": "Kaartik uses a toy video game controller shouting Freeze! Pinki comically freezes like a statue carrying laundry until Kaavya tickles her.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Freeze Game",
                "prompt_text": "Pixar 3D animated comedy. Modern Indian living room. Exactly ONE Kaartik (5, yellow polo) holds up a toy game controller pointing at Pinki (25, powder-blue kurti) and shouts: 'Freeze Mummy!' Kaavya (3, pink frock) watches with sparkling giggly eyes. (All character voices and exclamations in cheerful Hindi)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Statue Mummy",
                "prompt_text": "Pixar 3D animation. Pinki comically freezes mid-step holding a basket of soft folded towels, wobbling with funny cartoon wide eyes! Kaartik tiptoes around her examining his 'living statue' triumphantly with cheeky giggles. (All spoken dialogue in joyful Hindi)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Tickle Attack",
                "prompt_text": "Pixar 3D comedy. Kaavya runs over and tickles Pinki's waist! Pinki bursts into laughter unfreezing, dropping soft pillows over both kids into a giant joyful family cuddle on the rug. (All laughter and Hindi cheering)."
            }
        ]
    },
    {
        "id": "ep_19_giant_soap_bubble",
        "title": "Ghar Me Aaya Giant Bubble! 🫧😱 Kaartik Bubble Ke Andar?! #TheNaughtyDuo #shorts",
        "concept": "Kaartik and Kaavya blow a massive iridescent soap bubble with a big plastic ring that floats and lands gently on Pinki's head like an astronaut helmet.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Giant Bubble Wand",
                "prompt_text": "Pixar 3D animated comedy. Sunlit Indian veranda. Kaartik (5, yellow polo) dips a giant circular toy bubble wand into soapy water and waves it gently, creating a massive shimmering rainbow bubble that floats into living room! Kaavya (3, pink dress) claps in awe. (Joyful Hindi exclamations)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Astronaut Helmet",
                "prompt_text": "Pixar 3D animation. Pinki sits on sofa reading when the giant rainbow bubble slowly floats down and envelops her hair like a shiny astronaut bubble helmet! Pinki's eyes cross comically looking up at the soap film: 'Ye kya ho gaya?!' (Funny Hindi cartoon dialogue)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Pop and Giggle",
                "prompt_text": "Pixar 3D comedy. Kaavya pokes the giant bubble with her tiny index finger! 'POP!' Gentle sparkling soap droplets spray like confetti. Pinki shakes her wet curls laughing warmly and sprinkles water droplets back onto Kaartik and Kaavya as they giggle in circles. (Hindi family comedy)."
            }
        ]
    },
    {
        "id": "ep_20_pillow_fort_castle",
        "title": "Kaartik Ka Pillow Fort Castle! 🏰👑 Mummy Bani Monster! #TheNaughtyDuo #shorts",
        "concept": "Kaartik and Kaavya build an enormous living room pillow fort castle. Pinki plays a playful monster trying to enter, tickling their feet.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Fort Construction",
                "prompt_text": "Pixar 3D animation. Modern Indian living room. Kaartik (5, yellow polo) and Kaavya (3, pink frock) proudly sit inside an elaborate castle made of colorful sofa cushions and bed blankets, waving wooden toy flags. (Cheerful Hindi kids speech)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Monster Attack",
                "prompt_text": "Pixar 3D comedy. Pinki (25, powder-blue kurti) crawls playfully toward the fort wearing a goofy cartoon dinosaur oven mitt, roaring funny fake monster sounds: 'Main fort tod dungi!' Kaartik defends the cushion gate throwing soft plushies! (Hilarious Hindi comedy)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Pillow Avalanche",
                "prompt_text": "Pixar 3D comedy. Pinki tickles Kaartik's tummy through the pillows! The cushion wall gently topples down over all three of them in a soft, cozy pile. They pop their heads out laughing joyfully together. (Warm Hindi family cuddle)."
            }
        ]
    },
    {
        "id": "ep_21_kaavya_doctor_injection",
        "title": "Kaavya Bani Doctor Sahab! 🩺😂 Mummy Ko Laga Nakli Injection! #TheNaughtyDuo #shorts",
        "concept": "3-year-old Kaavya with cute pink toy stethoscope checks Pinki's heartbeat and comically gives Kaartik a giant plastic cartoon injection.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Doctor Kaavya",
                "prompt_text": "Pixar 3D animated comedy. Kaavya (3, pink frock) wearing oversized plastic doctor glasses and pink stethoscope listens to Pinki's tummy solemnly, making serious cute doctor faces. Kaartik (5, yellow polo) watches giggling behind sofa. (Cute Hindi toddler dialogue)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Giant Toy Injection",
                "prompt_text": "Pixar 3D animation. Kaavya pulls out a giant colorful plastic spring-loaded toy injection syringe and marches toward Kaartik with an innocent grin: 'Bhaiya, ab aapki baari!' Kaartik's eyes pop wide in hilarious cartoon panic, backing up onto sofa cushions! (Funny Hindi exclamations)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Toy Tiger Cure",
                "prompt_text": "Pixar 3D comedy. Kaavya gently gives the harmless squeaky toy injection to Kaartik's plush tiger instead. The toy tiger squeaks, Kaartik breathes a funny exaggerated sigh of relief, and Pinki awards Kaavya a gold star sticker on her forehead! (Happy Hindi family laughter)."
            }
        ]
    },
    {
        "id": "ep_22_chhota_chef_pancake",
        "title": "Chhota Chef Ka Giant Dosa! 🥞🧑‍🍳 Tawa Se Bada Dosa! #TheNaughtyDuo #shorts",
        "concept": "Kaartik wearing a big chef hat tries to flip a golden crispy toy dosa in the kitchen. It flips in mid-air and lands right on his chef hat.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Little Masterchef",
                "prompt_text": "Pixar 3D animated comedy. Bright modern Indian kitchen. Kaartik (5, yellow polo) wearing an oversized white chef hat holds a wooden spatula beside Pinki (25, powder-blue kurti). On the kitchen island sits a toy pan with golden crispy toy pancake. (Excited Hindi kids dialogue)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: High Flying Flip",
                "prompt_text": "Pixar 3D animation. Kaartik enthusiastically flips the toy pan with dramatic superhero flair! The pancake launches high into the air, spinning in slow-motion, and lands perfectly flat right on top of Kaartik's puffy chef hat! Kaartik looks up cross-eyed puzzled: 'Mera dosa kaha gaya?!' (Hilarious Hindi comedy)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Sweet Kitchen Treat",
                "prompt_text": "Pixar 3D comedy. Kaavya points at Kaartik's head in uncontrolled giggles! Pinki takes the pancake off his hat laughing warmly and hands both kids real sweet honey slices on plates. Family toast plates together with big smiles. (Cheerful Hindi celebration)."
            }
        ]
    },
    {
        "id": "ep_23_water_pichkari_ambush",
        "title": "Pani Ka Flying Pichkari Battle! 🔫💦 Mummy Bachao! #TheNaughtyDuo #shorts",
        "concept": "Sunny garden courtyard water-pistol battle. Kaartik and Kaavya ambush Mummy with cute tiny splash water pistols on a hot afternoon.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Water Squirt Ambush",
                "prompt_text": "Pixar 3D animated comedy. Sunlit lush green backyard garden. Kaartik (5, yellow polo) and Kaavya (3, pink frock) hide behind rose bushes holding bright colorful plastic water squirt pistols, whispering with mischievous grins. Pinki walks out holding a watering can. (Playful Hindi whisper)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Gentle Splash",
                "prompt_text": "Pixar 3D animation. Kaartik pops out: 'Surprise Mummy!' and shoots a gentle thin water arc that hits Pinki's floral kurti! Pinki gasps in dramatic comedy shock, drops the watering can, and grabs the garden hose pretending to charge back! (Funny cartoon Hindi battle cry)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Rainbow Lawn Dance",
                "prompt_text": "Pixar 3D comedy. Pinki sprays a gentle fine mist into the sunlight creating a beautiful sparkling mini-rainbow over the lawn! Kaartik and Kaavya jump through the mist splashing their sneakers in pure childhood bliss. (Vibrant Hindi family joy)."
            }
        ]
    },
    {
        "id": "ep_24_tricycle_grand_prix",
        "title": "Kaavya Ki Chhoti Cycle Race! 🚲💨 Kaartik Piche Reh Gaya! #TheNaughtyDuo #shorts",
        "concept": "Living room tricycle grand prix. Kaavya on her cute 3-wheel pink trike zooming past Kaartik who is carrying giant balloons.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Race Starting Line",
                "prompt_text": "Pixar 3D animation. Colorful hallway. Kaavya (3, pink dress) sits proudly on her pink-and-white toy tricycle with shiny handlebar bells. Kaartik (5, yellow polo) waves a checkered flag on the rug shouting: 'Ready, steady, GO!' (Energetic Hindi race countdown)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Nitro Toddler Speed",
                "prompt_text": "Pixar 3D comedy. Kaavya pedals furiously with adorable chubby knees, ringing her tricycle bell 'Tring-Tring!' as cartoon speed lines zoom past her! Kaartik tries to run beside her carrying a bunch of party balloons, but gets tangled comically in the balloon strings! (High-energy Hindi cartoon comedy)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Champion Kaavya",
                "prompt_text": "Pixar 3D comedy. Kaavya crosses the finish ribbon into Pinki's waiting arms! Pinki places a gold paper crown on Kaavya's head. Kaartik arrives laughing, giving his sister a high-five and a balloon. (Sweet Hindi brother-sister bond)."
            }
        ]
    },
    {
        "id": "ep_25_toy_robot_dinosaur",
        "title": "Ghar Me Aaya Toy Robot Dinosaur! 🦖🤖 Mummy Ka Hilarious Reaction! #TheNaughtyDuo #shorts",
        "concept": "Kaartik winds up a cute stomping cartoon green toy dino with squeaky roaring sounds that marches right into the kitchen towards Pinki's slippers.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Robot Dino Release",
                "prompt_text": "Pixar 3D animated comedy. Modern Indian living room. Kaartik (5, yellow polo) winds up a bright green plastic robot dinosaur with flashing LED eyes. It stomps forward on wheels with cute mechanical squeaks toward kitchen doorway. Kaavya giggles hiding behind couch. (Playful Hindi dialogue)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Dino Stomps in Kitchen",
                "prompt_text": "Pixar 3D animation. The toy dino marches into kitchen and softly taps Pinki's slipper, releasing a funny squeaky cartoon roar: 'RAWR-SQUEAK!' Pinki looks down, does an exaggerated comical hopping dance holding a stainless steel bowl! (Hilarious Hindi cartoon screams)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Dino Pet Treat",
                "prompt_text": "Pixar 3D comedy. Kaartik and Kaavya rush in laughing: 'Dino bhaiya ko bhookh lagi hai!' Pinki feeds the toy dino a pretend carrot slice. All three roar like baby dinos in rolling laughter together. (Warm Hindi family comedy)."
            }
        ]
    },
    {
        "id": "ep_26_chocolate_treasure_hunt",
        "title": "Mummy Ka Surprise Treasure Hunt! 🍫🗺️ Kaartik Ne Dhundh Liya! #TheNaughtyDuo #shorts",
        "concept": "Pinki draws a treasure map for Kaartik and Kaavya. Clues hidden under cushions and behind flower pots lead to a shiny box of chocolates.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Secret Treasure Map",
                "prompt_text": "Pixar 3D animation. Cozy living room. Pinki (25, powder-blue kurti) hands a colorful hand-drawn treasure map on parchment paper to Kaartik and Kaavya. Kaartik examines it through a magnifying glass with big excited detective eyes. (Intriguing Hindi kids narration)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Clue Hunting Chaos",
                "prompt_text": "Pixar 3D comedy. Kaartik and Kaavya crawl on knees looking under sofa pillows, lifting rug corners, and peeking behind indoor palm plants! Kaavya accidentally pulls a couch throw over Kaartik's head making him stumble like a friendly ghost! (Funny Hindi cartoon moments)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Treasure Found",
                "prompt_text": "Pixar 3D comedy. Inside a decorative golden box behind TV cabinet, they find shiny wrapped chocolates! Kaartik breaks one in half sharing with Kaavya, and both give Pinki sweet chocolate kisses on her cheeks. (Heartwarming Hindi family ending)."
            }
        ]
    },
    {
        "id": "ep_27_mummy_saree_superhero",
        "title": "Kaartik Bana Saree Superhero! 🦸‍♂️😂 Mummy Ki Dupatta Flying! #TheNaughtyDuo #shorts",
        "concept": "Kaartik ties Pinki's vibrant red dupatta as a superhero cape, running in circles pretending to fly until he lands safely in Mummy's lap.",
        "parts": [
            {
                "part_number": 1,
                "scene_label": "Hook: Superhero Cape",
                "prompt_text": "Pixar 3D animated comedy. Sunlit bedroom. Kaartik (5, yellow polo) ties Pinki's bright red embroidered dupatta over his shoulders as a fluttering superhero cape, striking heroic cartoon poses in front of mirror. Kaavya wears a toy crown cheering him on. (Enthusiastic Hindi superhero shouts)."
            },
            {
                "part_number": 2,
                "scene_label": "Prank: Living Room Flight",
                "prompt_text": "Pixar 3D animation. Kaartik zooms through the hallway making airplane flying sounds: 'Main Super-Kaartik hu!' The red cape flutters majestically behind him as he zooms past Pinki who is carrying folded clothes, swirling the breeze around her! (Dynamic Hindi action comedy)."
            },
            {
                "part_number": 3,
                "scene_label": "Resolution: Superhero Landing",
                "prompt_text": "Pixar 3D comedy. Kaartik does a dramatic slow-motion superhero jump right into the center of the big soft bed into Pinki's open arms! Pinki tickles her 'superhero' son while Kaavya jumps on the mattress clapping with joy. (Heartwarming Hindi family love)."
            }
        ]
    }
]

def main():
    db = DatabaseManager()
    
    # 1. Mark all existing old episodes in DB as PUBLISHED so they never get queued
    with db.get_connection() as conn:
        conn.execute("UPDATE stories SET state = 'PUBLISHED', priority = 99")
        print("[✓] Marked all old existing catalog stories as PUBLISHED (never duplicate).")

    # 2. Register fresh 10 unreleased episodes
    added = 0
    for ep in FRESH_EPISODES:
        try:
            db.register_story(
                story_id=ep["id"],
                title=ep["title"],
                concept=ep["concept"],
                structure="PROBLEM_ATTEMPT_PAYOFF",
                parts=ep["parts"],
                priority=1
            )
            print(f"[+] REGISTERED BRAND NEW: {ep['id']} -> {ep['title'][:45]}...")
            added += 1
        except Exception as e:
            print(f"[-] Notice on {ep['id']}: {e}")

    # 3. Update live production status file for dashboard
    first_fresh = FRESH_EPISODES[0]
    status_file = Path(BASE_DIR) / "data" / "live_production_status.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump({
            "active_id": first_fresh["id"],
            "active_title": first_fresh["title"],
            "active_account": "/u/0/ (TecHWirE9999@gmail.com)",
            "active_scene": "Scene 1 of 3: Hook (Magic Freeze Remote)",
            "percentage": 0,
            "parts_text": "0 of 3 Scenes Done",
            "stage": "Brand New Fresh Episode Queued"
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Loaded {added} 100% BRAND NEW, UNRELEASED episodes into Active Queue!")

if __name__ == "__main__":
    main()
