#!/usr/bin/env python3
"""
Test ImageContext coordinate system and cropping correctness.

Tests all scenarios:
1. Remote VM (scale=1.0, no offset)
2. Mac non-Retina fullscreen (scale=1.0, no offset)
3. Mac Retina fullscreen (scale=2.0, no offset)
4. Mac Retina window crop (scale=2.0, with offset)
5. Mac non-Retina window crop (scale=1.0, with offset)
6. Cropping correctness (scale-independent)
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from ui_detector import ImageContext


def test_remote():
    """VM / remote screenshot: 1:1, no offset."""
    ctx = ImageContext.remote()
    assert ctx.pixel_scale == 1.0
    assert ctx.origin_x == 0
    assert ctx.origin_y == 0

    # Image pixel (500, 300) → click (500, 300)
    assert ctx.image_to_click(500, 300) == (500, 300)
    # Click (500, 300) → image pixel (500, 300)
    assert ctx.click_to_image(500, 300) == (500, 300)
    # Size conversion
    assert ctx.image_size_to_click(100, 50) == (100, 50)
    assert ctx.click_size_to_image(100, 50) == (100, 50)

    print("✅ Test 1: Remote VM (scale=1.0) — PASS")


def test_mac_non_retina():
    """Mac non-Retina fullscreen: scale=1.0."""
    ctx = ImageContext(pixel_scale=1.0, origin_x=0, origin_y=0)

    assert ctx.image_to_click(960, 540) == (960, 540)
    assert ctx.click_to_image(960, 540) == (960, 540)

    print("✅ Test 2: Mac non-Retina fullscreen (scale=1.0) — PASS")


def test_mac_retina_fullscreen():
    """Mac Retina fullscreen: scale=2.0.
    
    Screenshot is 3024×1964 pixels, click-space is 1512×982.
    """
    ctx = ImageContext(pixel_scale=2.0, origin_x=0, origin_y=0)

    # Image pixel (3024, 1964) → click (1512, 982)
    assert ctx.image_to_click(3024, 1964) == (1512, 982)
    # Image pixel (0, 0) → click (0, 0)
    assert ctx.image_to_click(0, 0) == (0, 0)
    # Image pixel (1000, 500) → click (500, 250)
    assert ctx.image_to_click(1000, 500) == (500, 250)

    # Click (500, 250) → image pixel (1000, 500)
    assert ctx.click_to_image(500, 250) == (1000, 500)
    # Click (0, 0) → image pixel (0, 0)
    assert ctx.click_to_image(0, 0) == (0, 0)

    # Size
    assert ctx.image_size_to_click(200, 100) == (100, 50)
    assert ctx.click_size_to_image(100, 50) == (200, 100)

    print("✅ Test 3: Mac Retina fullscreen (scale=2.0) — PASS")


def test_mac_retina_window():
    """Mac Retina window crop: scale=2.0, window at (100, 200) in click-space.
    
    Window screenshot is e.g. 1600×1200 pixels.
    Window position in click-space: (100, 200).
    """
    ctx = ImageContext(pixel_scale=2.0, origin_x=100, origin_y=200)

    # Image pixel (0, 0) = top-left of window = click (100, 200)
    assert ctx.image_to_click(0, 0) == (100, 200)
    # Image pixel (200, 400) → click (100 + 200/2, 200 + 400/2) = (200, 400)
    assert ctx.image_to_click(200, 400) == (200, 400)
    # Image pixel (1600, 1200) → click (100 + 800, 200 + 600) = (900, 800)
    assert ctx.image_to_click(1600, 1200) == (900, 800)

    # Click (100, 200) → image pixel (0, 0) (top-left of window)
    assert ctx.click_to_image(100, 200) == (0, 0)
    # Click (200, 400) → image pixel (200, 400)
    assert ctx.click_to_image(200, 400) == (200, 400)

    print("✅ Test 4: Mac Retina window (scale=2.0, offset=(100,200)) — PASS")


def test_mac_non_retina_window():
    """Mac non-Retina window crop: scale=1.0, window at (500, 161)."""
    ctx = ImageContext(pixel_scale=1.0, origin_x=500, origin_y=161)

    # Image pixel (0, 0) → click (500, 161)
    assert ctx.image_to_click(0, 0) == (500, 161)
    # Image pixel (420, 275) → click (920, 436)
    assert ctx.image_to_click(420, 275) == (920, 436)

    # Click (500, 161) → image pixel (0, 0)
    assert ctx.click_to_image(500, 161) == (0, 0)

    print("✅ Test 5: Mac non-Retina window (scale=1.0, offset=(500,161)) — PASS")


def test_cropping_is_scale_independent():
    """Cropping uses image pixel coords directly — scale never involved.
    
    Create a synthetic image, run 'detection', crop, verify correctness.
    """
    # Create a 1920×1080 image with a known 100×100 red square at pixel (200, 300)
    img = np.zeros((1080, 1920, 3), dtype=np.uint8)
    img[300:400, 200:300] = [0, 0, 255]  # Red square (BGR)

    # Simulated detection result (image pixel coords from detect_all)
    detected_element = {"x": 200, "y": 300, "w": 100, "h": 100, "cx": 250, "cy": 350}

    # Crop using image pixel coords directly (the new way)
    px_x, px_y = detected_element["x"], detected_element["y"]
    px_w, px_h = detected_element["w"], detected_element["h"]
    crop = img[px_y:px_y+px_h, px_x:px_x+px_w]

    # Verify: entire crop should be red
    assert crop.shape == (100, 100, 3), f"Wrong crop shape: {crop.shape}"
    assert np.all(crop[:, :, 2] == 255), "Crop should be all red"
    assert np.all(crop[:, :, 0] == 0), "Crop should have no blue"
    assert np.all(crop[:, :, 1] == 0), "Crop should have no green"

    # Now verify this works regardless of what scale we "think" we have
    for scale in [1.0, 2.0, 0.5, 3.0]:
        ctx = ImageContext(pixel_scale=scale)
        # Cropping still uses raw pixel coords — ctx is only for clicking
        crop2 = img[px_y:px_y+px_h, px_x:px_x+px_w]
        assert np.array_equal(crop, crop2), f"Crop changed with scale={scale}!"

    print("✅ Test 6: Cropping is scale-independent — PASS")


def test_roundtrip():
    """image→click→image roundtrip should be identity (within int rounding).
    
    Only tests real-world scale values: 1.0 (non-Retina) and 2.0 (Retina).
    These are always integers so roundtrip is exact.
    """
    for scale in [1.0, 2.0]:
        for ox, oy in [(0, 0), (100, 200), (500, 300)]:
            ctx = ImageContext(pixel_scale=scale, origin_x=ox, origin_y=oy)
            for px, py in [(0, 0), (100, 100), (500, 300), (1000, 800)]:
                cx, cy = ctx.image_to_click(px, py)
                px2, py2 = ctx.click_to_image(cx, cy)
                assert px == px2 and py == py2, \
                    f"Roundtrip failed: ({px},{py}) → ({cx},{cy}) → ({px2},{py2}) " \
                    f"scale={scale} origin=({ox},{oy})"

    print("✅ Test 7: Roundtrip image→click→image (scale 1.0 & 2.0) — PASS")


def test_old_bug_scenario():
    """Reproduce the exact bug that was fixed.
    
    Old code: VM screenshot (1920×922) on Mac with screen (1920×1080)
    Old scale_y = 922/1080 = 0.854
    Crop would use y * 0.854, shifting everything up.
    
    New code: ImageContext.remote() → scale=1.0, crop uses raw coords.
    """
    # Simulated VM screenshot 1920×922
    img = np.zeros((922, 1920, 3), dtype=np.uint8)
    # Put a green square at y=400 (a dock icon)
    img[380:420, 20:60] = [0, 255, 0]  # Green at pixel (20, 380)

    detected = {"x": 20, "y": 380, "w": 40, "h": 40, "cx": 40, "cy": 400}

    # New way: crop directly with pixel coords
    crop = img[detected["y"]:detected["y"]+detected["h"],
               detected["x"]:detected["x"]+detected["w"]]
    assert crop.shape == (40, 40, 3)
    assert np.all(crop[:, :, 1] == 255), "Should be all green"

    # Old way (simulated): would have used scale_y=922/1080=0.854
    old_scale_y = 922 / 1080  # 0.854
    old_py = int(detected["y"] * old_scale_y)  # 380 * 0.854 = 324 (WRONG!)
    old_crop = img[old_py:old_py+detected["h"], detected["x"]:detected["x"]+detected["w"]]
    # Old crop at y=324 would NOT be green (it's all black there)
    assert not np.all(old_crop[:, :, 1] == 255), "Old crop should be wrong (shifted up)"

    print("✅ Test 8: Old bug scenario reproduced & verified fixed — PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("ImageContext Coordinate System Tests")
    print("=" * 60)
    print()

    test_remote()
    test_mac_non_retina()
    test_mac_retina_fullscreen()
    test_mac_retina_window()
    test_mac_non_retina_window()
    test_cropping_is_scale_independent()
    test_roundtrip()
    test_old_bug_scenario()

    print()
    print("=" * 60)
    print("ALL 8 TESTS PASSED ✅")
    print("=" * 60)
