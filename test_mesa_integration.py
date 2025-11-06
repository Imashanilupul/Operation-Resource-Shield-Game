"""
Test Mesa Framework Integration
Run this to verify Mesa is properly installed and working
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mesa_model import create_game_model, OperationGuardianModel


def test_mesa_installation():
    """Test that Mesa is installed"""
    try:
        import mesa
        print(f"✓ Mesa {mesa.__version__} installed successfully!")
        return True
    except ImportError as e:
        print(f"✗ Mesa installation failed: {e}")
        return False


def test_model_creation():
    """Test creating a Mesa model"""
    try:
        model = create_game_model("easy")
        assert model is not None
        assert isinstance(model, OperationGuardianModel)
        print("✓ Model creation successful")
        return True
    except Exception as e:
        print(f"✗ Model creation failed: {e}")
        return False


def test_scheduler():
    """Test scheduler functionality"""
    try:
        model = create_game_model("medium")
        assert model.scheduler is not None
        print(f"✓ Scheduler created successfully")
        return True
    except Exception as e:
        print(f"✗ Scheduler creation failed: {e}")
        return False


def test_game_state():
    """Test getting game state"""
    try:
        model = create_game_model("hard")
        state = model.get_game_state()
        assert isinstance(state, dict)
        print(f"✓ Game state retrieval successful")
        print(f"  - Difficulty: {state.get('difficulty')}")
        print(f"  - Step count: {state.get('step')}")
        return True
    except Exception as e:
        print(f"✗ Game state retrieval failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Mesa Framework Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Mesa Installation", test_mesa_installation),
        ("Model Creation", test_model_creation),
        ("Scheduler", test_scheduler),
        ("Game State", test_game_state),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All Mesa integration tests passed!")
        print("\nNext steps:")
        print("1. Read MESA_QUICK_START.md for overview")
        print("2. Read MESA_OVERVIEW.md for concepts")
        print("3. Read MESA_IMPLEMENTATION_GUIDE.md for detailed steps")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review above.")
        return 1


if __name__ == "__main__":
    exit(main())
