"""
Quick test script for IndexTTS emotion parser

Run with: PYTHONPATH="$PYTHONPATH:." uv run indextts_app/test_emotion.py
"""

from indextts_app.emotion import parse_emotion_tags_to_vectors, parse_emotion_tags


def test_emotion_parser():
    """Test basic emotion parsing"""
    print("\n" + "="*70)
    print("TEST 1: Basic Emotion Parsing")
    print("="*70)
    
    text = "[Happy:80]Great news! [Calm:60]Take your time. [Angry:90]This is unacceptable!"
    print(f"Input: {text}\n")
    
    segments, plain_text = parse_emotion_tags(text)
    
    print(f"Segments found: {len(segments)}\n")
    for i, seg in enumerate(segments, 1):
        print(f"Segment {i}:")
        print(f"  Text: '{seg.text}'")
        print(f"  Emotions: {seg.emotions}")
        print()
    
    print(f"Plain text: '{plain_text}'\n")


def test_emotion_vectors():
    """Test emotion vector conversion"""
    print("="*70)
    print("TEST 2: Emotion Vector Conversion")
    print("="*70)
    
    text = "[Calm:60,Happy:40]Now I've been waiting [Angry:30] It's been 2 weeks!"
    print(f"Input: {text}\n")
    
    segments, plain_text = parse_emotion_tags_to_vectors(text)
    
    emotion_names = ["happy", "angry", "sad", "afraid", "disgusted", "melancholic", "surprised", "calm"]
    
    print(f"Segments with emotion vectors:\n")
    for i, (text_seg, emotion_vec) in enumerate(segments, 1):
        print(f"Segment {i}:")
        print(f"  Text: '{text_seg.strip()}'")
        print(f"  Vector: {[f'{v:.2f}' for v in emotion_vec]}")
        
        active_emotions = [f"{emotion_names[j]}={v:.2f}" for j, v in enumerate(emotion_vec) if v > 0]
        print(f"  Active emotions: {', '.join(active_emotions)}")
        print()


def test_complex_emotions():
    """Test complex emotion scenarios"""
    print("="*70)
    print("TEST 3: Complex Emotion Scenarios")
    print("="*70)
    
    test_cases = [
        # Single emotion
        "[Happy:100]I'm so happy!",
        
        # Multiple emotions in one tag
        "[Happy:70,Calm:50]This is nice and peaceful",
        
        # Emotions with 0 intensity
        "[Happy:0]I'm not happy",
        
        # Extreme intensity
        "[Angry:100,Hate:100]UNACCEPTABLE!!!",
        
        # No emotions (plain text)
        "This is plain text",
        
        # Multiple tags
        "[Happy:60]Start happy [Angry:80]then angry [Calm:40]end calm",
    ]
    
    emotion_names = ["happy", "angry", "sad", "afraid", "disgusted", "melancholic", "surprised", "calm"]
    
    for i, text in enumerate(test_cases, 1):
        print(f"Test case {i}: {text}")
        segments, plain_text = parse_emotion_tags_to_vectors(text)
        
        if not segments:
            print("  → No emotions detected")
        else:
            for text_seg, emotion_vec in segments:
                active = [f"{emotion_names[j]}={v:.2f}" for j, v in enumerate(emotion_vec) if v > 0.01]
                if active:
                    print(f"  → {', '.join(active)}")
                else:
                    print(f"  → No active emotions")
        print()


def test_edge_cases():
    """Test edge cases"""
    print("="*70)
    print("TEST 4: Edge Cases")
    print("="*70)
    
    edge_cases = [
        # Invalid intensity values
        "[Happy:150]Over 100",  # Should clamp to 100
        "[Angry:-50]Negative",  # Should clamp to 0
        
        # Malformed tags
        "[Invalid:50]Bad emotion name",
        "[Happy]Missing intensity",
        "[Happy:abc]Non-numeric intensity",
        
        # Empty tag
        "[]Empty tag",
        
        # Nested tags (not supported)
        "[[Happy:50]]Nested",
    ]
    
    for i, text in enumerate(edge_cases, 1):
        print(f"Edge case {i}: {text}")
        try:
            segments, plain_text = parse_emotion_tags_to_vectors(text)
            print(f"  ✓ Parsed successfully ({len(segments)} segments)")
            for text_seg, _ in segments:
                print(f"    - '{text_seg.strip()}'")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()


def main():
    """Run all tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  IndexTTS Emotion Parser Tests".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        test_emotion_parser()
        test_emotion_vectors()
        test_complex_emotions()
        test_edge_cases()
        
        print("="*70)
        print("✓ All tests completed!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
