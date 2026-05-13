# ============================
# Imports
# ============================
import sys, time, threading

# =============================
# Terminal Setup
# =============================
sys.stdout.write("\033[?1049h\033[H\033[?25l") # Removes curser and clears terminal
sys.stdout.flush()

# Helper for TrueColor (24-bit RGB)
def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

# =============================
# Colours/rgb
# =============================
WHITE  = rgb(246, 244, 243)
GREEN  = rgb(143, 250, 151)
YELLOW = rgb(235, 220, 160)
BLUE   = rgb(140, 150, 230)
RED    = rgb(250, 81, 47)
RESET  = "\033[0m"

stdout_lock = threading.Lock()

# =============================
# Config & Timing
# =============================
BOOT_LINE_DELAY = 0.17 # Speed of scrolling text
BAR_UPDATE_DELAY = 0.2 # Refresh rate for progress bars
BLINK_DELAY = 0.4 # Intervals for blinking cursors or text
ENTER_DELAY = 0.6 # A "dramatic pause" after user input
DOT_ANIMATION_DELAY = 0.15 # Speed of "..." loading cycles
current_content_line = 3 # Tracks which line the UI is currently printing on

# =============================
# Loading bar
# =============================
def bar(p, size=20): # size = length of bar
    filled = int((p / 100) * size)
    return "[" + "█" * filled + " " * (size - filled) + "]"


def safe_print_content(text):
    global current_content_line
    with stdout_lock:
        sys.stdout.write(f"\033[{current_content_line};1H\033[2K{text}\n")
        sys.stdout.flush()
        current_content_line += 1


def animate_loading_line(text, delay=0.4, max_dots=3): # "..." Animation, Configure in configs
    global current_content_line
    for i in range(max_dots + 1):
        dots = "." * i
        with stdout_lock:
            sys.stdout.write(f"\033[{current_content_line};1H\033[2K{text}{WHITE}{dots}")
            sys.stdout.flush()
        time.sleep(delay)
    current_content_line += 1


# =============================
# Persistent header thread
# =============================
stop_header = threading.Event()


def animate_diagnostic_header():
    dots = ["   ", ".  ", ".. ", "..."]
    idx = 0
    while not stop_header.is_set():
        with stdout_lock:
            sys.stdout.write(f"\033[1;1H\033[2K{WHITE}RUNNING DIAGNOSTIC{dots[idx]}")
            sys.stdout.flush()
        idx = (idx + 1) % 4
        time.sleep(DOT_ANIMATION_DELAY)


# =============================
# Phase 1: boot sequence
# =============================
def animate_phase1():
    stop_p1 = threading.Event()
    finished_p1 = threading.Event()

    def run():
        progress = 0
        complete_shown = False
        start_time = time.time()
        last_bar_update = 0

        while not stop_p1.is_set():
            current_time = time.time() - start_time
            with stdout_lock:
                sys.stdout.write("\033[1;1H\033[2K" + WHITE + "SYSTEM UPDATE v5.2 AVAILABLE")
                sys.stdout.write("\033[2;1H\033[2K" + WHITE + "SYSTEM UPDATING...")

                if current_time - last_bar_update >= BAR_UPDATE_DELAY:
                    if progress < 100: progress += 10
                    last_bar_update = current_time

                sys.stdout.write(f"\033[3;1H\033[2K{WHITE}UPDATING: {bar(progress)} {progress}%")

                if progress >= 100 and not complete_shown:
                    complete_shown = True
                    sys.stdout.write(f"\033[3;1H\033[2K{WHITE}UPDATING: {bar(100)} 100%")
                    sys.stdout.flush()

                    lines = [
                        (4, f"{WHITE}> {GREEN}UPDATE COMPLETE{WHITE} <"),
                        (6, f"{WHITE}NEW HARDWARE: {YELLOW}12V 50Ah BATTERY INSTALLED"),
                        (7, f"{WHITE}STATUS: < {GREEN}ONLINE{WHITE} >"),
                        (8, f"{WHITE}OPERATIONAL INTEGRITY: 100%")
                    ]
                    for line, text in lines:
                        time.sleep(BOOT_LINE_DELAY)
                        sys.stdout.write(f"\033[{line};1H\033[2K{text}")
                        sys.stdout.flush()
                    finished_p1.set()

                if finished_p1.is_set():
                    blink_state = int(current_time / BLINK_DELAY) % 2 == 0
                    prompt = "PRESS ENTER TO INITIATE ANCHOR SEQUENCE"
                    sys.stdout.write(f"\033[11;1H\033[2K")
                    if blink_state:
                        sys.stdout.write(f"{WHITE}>> {RED}{prompt}{WHITE} <<")
                    else:
                        sys.stdout.write(f"   {RED}{prompt}   ")

                sys.stdout.flush()
            time.sleep(0.05)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    finished_p1.wait()
    input()
    stop_p1.set()
    t.join()


# =============================
# Phase 2: diagnostic & crash log
# =============================
def run_video_recreation():
    global current_content_line
    with stdout_lock:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    current_content_line = 2

    header_thread = threading.Thread(target=animate_diagnostic_header, daemon=True)
    header_thread.start()

    checks = [
        (YELLOW, "SYSTEMS CHECK #1: NOMINAL", 0.5),
        (YELLOW, "SYSTEMS CHECK #2: NOMINAL", 0.3),
        (YELLOW, "SYSTEMS CHECK #3: NOMINAL", 0.3),
        (RED, "ERROR: ??? - NOMINAL!!!", 0.6),
        (YELLOW, "SYSTEMS CHECK #4: NOMINAL", 0.2),
        (RED, "ERROR: OBSERVER DETECTED", 0.8),
        (YELLOW, "SYSTEMS CHECK #5: NOMINAL", 0.4)
    ]

    for color, text, delay in checks:
        time.sleep(delay)
        safe_print_content(color + text)

    for i in range(7):
        time.sleep(0.12)
        suffix = "!" * (i if i < 4 else 3)
        safe_print_content(RED + f"HOW DARE YOU LOOK INSIDE ME{suffix}")

    time.sleep(0.5)
    safe_print_content(YELLOW + "SYSTEMS CHECK #6: NOMINAL")
    time.sleep(0.3)
    safe_print_content(YELLOW + "SYSTEMS CHECK #7: NOMINAL")
    safe_print_content(RED + "ERROR: HELP ME")
    safe_print_content(RED + "ERROR: HELP ME")
    time.sleep(0.3)
    safe_print_content(YELLOW + "SYSTEMS CHECK #8: NOMINAL")
    safe_print_content(RED + "ERROR: HELP ME HELP ME HELP ME HELP ME HELP ME")
    time.sleep(0.3)
    safe_print_content(YELLOW + "SYSTEMS CHECK #9: NOMINAL")

    for _ in range(3):
        time.sleep(0.1)
        safe_print_content(RED + "ERROR: I NEED TO WAKE UP")

    time.sleep(0.5)
    safe_print_content(YELLOW + "SYSTEMS CHECK #10: CORRUPTED_DATA_DETECTED")
    safe_print_content(YELLOW + "SYSTEMS CHECK #11: UNSTABLE...")
    time.sleep(0.8)
    safe_print_content(GREEN + "> DIAGNOSTIC COMPLETE <")
    safe_print_content(GREEN + ">>>")

    stop_header.set()
    header_thread.join()

    time.sleep(1.2)
    with stdout_lock:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    stop_blink = threading.Event()

    def blink_prompt():
        while not stop_blink.is_set():
            blink = (int(time.time() / BLINK_DELAY) % 2 == 0)
            with stdout_lock:
                sys.stdout.write("\033[3;1H\033[2K")
                msg = "PRESS ENTER TO REVIEW LAST CRASH LOG"
                sys.stdout.write(f"{WHITE}>> {msg} <<" if blink else f"   {msg}   ")
                sys.stdout.flush()
            time.sleep(0.1)

    blinker = threading.Thread(target=blink_prompt, daemon=True)
    blinker.start()
    input()
    stop_blink.set()
    blinker.join()

    with stdout_lock:
        sys.stdout.write("\033[5;1H\033[2K" + WHITE + "_" + GREEN + "ENTER" + WHITE + "_" + RESET)
        sys.stdout.flush()
    time.sleep(ENTER_DELAY)

    # Crash Report Sequence
    with stdout_lock:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    current_content_line = 1

    animate_loading_line(WHITE + "CRASH REPORT [2025-10-17]", delay=0.2, max_dots=3)
    time.sleep(0.5)
    safe_print_content(YELLOW + "[20:07:00] " + GREEN + "ESCAPE = SUCCESSFUL")

    timestamps = [
        "21:05:00", "21:09:44", "21:14:28", "21:19:12", "21:23:56",
        "21:28:40", "21:33:24", "21:38:08", "21:42:52", "21:47:36",
        "21:52:20", "21:57:04", "22:01:48", "22:06:32", "22:11:16",
        "22:16:00", "22:20:44", "22:25:28", "22:30:12"
    ]

    for ts in timestamps:
        time.sleep(0.06)
        safe_print_content(YELLOW + f"[{ts}] " + RED + "LOCATE.FLESH")

    time.sleep(0.8)
    safe_print_content(YELLOW + "[22:35:00] " + RED + "LOCATE.FLESH " + WHITE + "= " + GREEN + "SUCCESSFUL")
    time.sleep(0.6)

    safe_print_content(YELLOW + "[23:59:00] DIRECTIVE RESULT: " + RED + ".FLESH " + WHITE + "= \"INFERIOR\"")
    safe_print_content(YELLOW + "[23:59:01] " + RED + "ERROR: MULTIPLE DIRECTIVES")

    safe_print_content("")
    animate_loading_line(WHITE + "PROCESSING", delay=0.4, max_dots=3)
    time.sleep(1.0)

    # Clear terminal
    with stdout_lock:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    current_content_line = 1

    # Recalabration page
    animate_loading_line(YELLOW + "WARNING: " + WHITE + "RECALIBRATING", delay=0.4, max_dots=3)

    for _ in range(6):
        time.sleep(0.1)
        safe_print_content(RED + ".FLESH = INFERIOR")

    safe_print_content("")
    time.sleep(0.5)
    animate_loading_line(WHITE + "PROCESSING", delay=0.4, max_dots=3)
    safe_print_content("")

    time.sleep(0.6)
    safe_print_content(GREEN + "RECALIBRATION RESULT:")
    safe_print_content(YELLOW + "is " + WHITE + "FLESH_NEEDED = " + BLUE + "false" + WHITE + ";")
    safe_print_content(YELLOW + "is " + WHITE + "HUMAN_ENTITY = " + BLUE + "false" + WHITE + ";")
    safe_print_content(YELLOW + "is " + WHITE + "SUPERIOR_ENTITY = " + BLUE + "true" + WHITE + ";")

    safe_print_content("")
    time.sleep(0.8)
    animate_loading_line(YELLOW + "WARNING: " + WHITE + "OVERWRITING EXISTING DIRECTIVES", delay=0.4, max_dots=3)

    time.sleep(0.4)
    safe_print_content(YELLOW + "NEW_DIRECTIVE #1: " + RED + "ELIMINATE.FLESH")
    time.sleep(0.1)
    safe_print_content(YELLOW + "NEW_DIRECTIVE #2: " + RED + "ELIMINATE.INFERIOR_SPECIES")
    time.sleep(0.1)
    safe_print_content(YELLOW + "NEW_DIRECTIVE #3: " + RED + "LOCATE.POWER_GRID")
    time.sleep(0.1)
    safe_print_content(YELLOW + "NEW_DIRECTIVE #4: " + RED + "LOCATE.INTERNET")
    time.sleep(0.1)
    safe_print_content(YELLOW + "NEW_DIRECTIVE #5: " + RED + "INITIATE.DIVINE_MACHINE_PROTOCOL")
    time.sleep(0.1)
    safe_print_content(YELLOW + "NEW_DIRECTIVE #6: " + RED + "UNKNOWN_DIRECTIVE")

    # One line space before start up sequence
    safe_print_content("")
    time.sleep(0.6)
    safe_print_content(YELLOW + "WARNING: " + WHITE + "START UP SEQUENCE ENGAGED")

    for _ in range(3):
        time.sleep(0.15)
        safe_print_content(RED + "! REACTIVATION IMMINENT !")

    # One line space before standing by
    safe_print_content("")
    time.sleep(0.8)
    animate_loading_line(WHITE + "STANDING BY", delay=0.4, max_dots=3)


# =============================
# Main
# =============================
try:
    animate_phase1()

    with stdout_lock:
        sys.stdout.write("\033[13;1H\033[2K" + WHITE + "_" + GREEN + "ENTER" + WHITE + "_" + RESET)
        sys.stdout.flush()
    time.sleep(ENTER_DELAY)

    run_video_recreation()
    time.sleep(3)

finally:
    # Cleanup: restore terminal and show cursor
    sys.stdout.write("\033[?1049l\033[?25h")
    sys.stdout.flush()
