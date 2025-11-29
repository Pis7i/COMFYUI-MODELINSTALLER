#!/usr/bin/env python3
"""
Test script for Eye Stabilizer Node
Verifies installation and basic functionality
"""

import sys
import torch
import numpy as np
from PIL import Image

def test_imports():
    """Test that all required imports work."""
    print("=" * 60)
    print("Testing Imports...")
    print("=" * 60)
    
    try:
        import torch
        print(f"✓ PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"✗ PyTorch: {e}")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy: {numpy.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV: {e}")
        return False
    
    try:
        from PIL import Image
        print(f"✓ PIL: {Image.__version__}")
    except ImportError as e:
        print(f"✗ PIL: {e}")
        return False
    
    try:
        import mediapipe
        print(f"✓ MediaPipe: {mediapipe.__version__}")
    except ImportError as e:
        print(f"⚠ MediaPipe: NOT INSTALLED (node will work in fallback mode)")
        print(f"  Install with: pip install mediapipe==0.10.24")
    
    return True


def test_node_loading():
    """Test that the Eye Stabilizer node can be imported."""
    print("\n" + "=" * 60)
    print("Testing Node Loading...")
    print("=" * 60)
    
    try:
        from eye_stabilizer_node import EyeStabilizerNode
        print("✓ EyeStabilizerNode imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import EyeStabilizerNode: {e}")
        return False


def test_node_initialization():
    """Test that the node can be initialized."""
    print("\n" + "=" * 60)
    print("Testing Node Initialization...")
    print("=" * 60)
    
    try:
        from eye_stabilizer_node import EyeStabilizerNode
        node = EyeStabilizerNode()
        print("✓ Node initialized successfully")
        print(f"  Type: {node.type}")
        print(f"  MediaPipe available: {node.mediapipe_available}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize node: {e}")
        return False


def test_node_inputs():
    """Test node input type definitions."""
    print("\n" + "=" * 60)
    print("Testing Node Input Types...")
    print("=" * 60)
    
    try:
        from eye_stabilizer_node import EyeStabilizerNode
        input_types = EyeStabilizerNode.INPUT_TYPES()
        
        required = input_types.get("required", {})
        optional = input_types.get("optional", {})
        
        print(f"✓ Required inputs ({len(required)}):")
        for name in required.keys():
            print(f"    - {name}")
        
        print(f"✓ Optional inputs ({len(optional)}):")
        for name in optional.keys():
            print(f"    - {name}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to get input types: {e}")
        return False


def test_basic_processing():
    """Test basic frame processing."""
    print("\n" + "=" * 60)
    print("Testing Basic Processing...")
    print("=" * 60)
    
    try:
        from eye_stabilizer_node import EyeStabilizerNode
        
        # Create dummy test data
        # ComfyUI format: [B, H, W, C] in range [0, 1]
        batch_size = 3
        height, width = 256, 256
        test_frames = torch.rand(batch_size, height, width, 3)
        
        print(f"  Created test batch: {test_frames.shape}")
        
        # Initialize node
        node = EyeStabilizerNode()
        
        # Process frames
        print("  Processing frames...")
        stabilized, mask, debug = node.stabilize_eyes(
            images=test_frames,
            enable_temporal_smoothing=True,
            enable_blink_detection=True,
            enable_eye_enhancement=True,
            smoothing_strength=0.7,
            enhancement_strength=1.3,
            blink_threshold=0.2,
            eye_region_dilation=10
        )
        
        print(f"✓ Processing completed")
        print(f"  Stabilized output: {stabilized.shape}")
        print(f"  Mask output: {mask.shape}")
        print(f"  Debug output: {debug.shape}")
        
        # Verify output shapes
        assert stabilized.shape == test_frames.shape, "Stabilized shape mismatch"
        assert mask.shape[0] == batch_size, "Mask batch size mismatch"
        assert debug.shape == test_frames.shape, "Debug shape mismatch"
        
        print("✓ Output shapes verified")
        return True
        
    except Exception as e:
        print(f"✗ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_node_registration():
    """Test that node is registered correctly."""
    print("\n" + "=" * 60)
    print("Testing Node Registration...")
    print("=" * 60)
    
    try:
        from eye_stabilizer_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
        
        print(f"✓ Node class mappings:")
        for key, value in NODE_CLASS_MAPPINGS.items():
            print(f"    {key}: {value.__name__}")
        
        print(f"✓ Display name mappings:")
        for key, value in NODE_DISPLAY_NAME_MAPPINGS.items():
            print(f"    {key}: {value}")
        
        return True
    except Exception as e:
        print(f"✗ Registration check failed: {e}")
        return False


def test_kalman_filter():
    """Test Kalman filter component."""
    print("\n" + "=" * 60)
    print("Testing Kalman Filter...")
    print("=" * 60)
    
    try:
        from eye_stabilizer_node import KalmanFilter1D
        
        kf = KalmanFilter1D()
        print("✓ KalmanFilter1D initialized")
        
        # Test with noisy data
        measurements = [1.0, 1.2, 0.9, 1.1, 1.3, 0.8, 1.0]
        filtered = []
        
        for m in measurements:
            f = kf.update(m)
            filtered.append(f)
        
        print(f"  Input:    {measurements}")
        print(f"  Filtered: {[f'{x:.2f}' for x in filtered]}")
        
        # Verify filtering is working (variance should be reduced)
        input_var = np.var(measurements)
        output_var = np.var(filtered)
        
        print(f"  Input variance:  {input_var:.4f}")
        print(f"  Output variance: {output_var:.4f}")
        print(f"  Reduction: {(1 - output_var/input_var)*100:.1f}%")
        
        assert output_var < input_var, "Filter not reducing variance"
        print("✓ Kalman filter working correctly")
        
        return True
    except Exception as e:
        print(f"✗ Kalman filter test failed: {e}")
        return False


def test_blink_detector():
    """Test blink detector component."""
    print("\n" + "=" * 60)
    print("Testing Blink Detector...")
    print("=" * 60)
    
    try:
        from eye_stabilizer_node import BlinkDetector
        
        bd = BlinkDetector()
        print("✓ BlinkDetector initialized")
        
        # Test EAR calculation
        # Mock eye landmarks (6 points)
        eye_open = np.array([
            [0, 0],    # p1 (left corner)
            [1, 1],    # p2 (top-left)
            [2, 1.2],  # p3 (top-right)
            [3, 0],    # p4 (right corner)
            [2, -1.2], # p5 (bottom-right)
            [1, -1]    # p6 (bottom-left)
        ], dtype=np.float32)
        
        eye_closed = np.array([
            [0, 0],
            [1, 0.2],
            [2, 0.2],
            [3, 0],
            [2, -0.2],
            [1, -0.2]
        ], dtype=np.float32)
        
        ear_open = bd.calculate_ear(eye_open)
        ear_closed = bd.calculate_ear(eye_closed)
        
        print(f"  EAR (open):   {ear_open:.3f}")
        print(f"  EAR (closed): {ear_closed:.3f}")
        
        assert ear_open > ear_closed, "Open eye should have higher EAR"
        print("✓ Blink detector working correctly")
        
        return True
    except Exception as e:
        print(f"✗ Blink detector test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 60)
    print("EYE STABILIZER NODE - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Node Loading", test_node_loading),
        ("Node Initialization", test_node_initialization),
        ("Node Input Types", test_node_inputs),
        ("Node Registration", test_node_registration),
        ("Kalman Filter", test_kalman_filter),
        ("Blink Detector", test_blink_detector),
        ("Basic Processing", test_basic_processing),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8s} - {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Eye Stabilizer is ready to use.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
