
"""User interaction utilities (sound, display, robot motion)."""
import pygame
from . import config

def play_sound(sound: pygame.mixer.Sound) -> None:
    """Play a pygame sound object."""
    sound.play()

def notify_stretch(m5, joints) -> None:
    """Display stretch message & move camera up."""
    try:
        m5.set_display_text("Stretch now!")
    except Exception as e:
        print(f"[WARN] Failed to set display text: {e}")
    # Attempt to tilt camera up a bit
    try:
        joints.move_joint_positions(pan=0.0, tilt=-0.3)
    except Exception as e:
        print(f"[WARN] Failed to move joints: {e}")

def notify_sitting(m5) -> None:
    """Display sitting reminder."""
    try:
        m5.set_display_text("Time to stand up!")
    except Exception as e:
        print(f"[WARN] Failed to set display text: {e}")
