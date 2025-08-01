"""
Comprehensive tests for the Ethical Recommendation System API
"""

import requests
import json
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30


class APITester:
    """Comprehensive API testing class"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            status = "PASS" if result else "FAIL"
            duration = f"{end_time - start_time:.2f}s"
            
            self.test_results.append({
                "test": test_name,
                "status": status,
                "duration": duration
            })
            
            print(f"Result: {status} ({duration})")
            return result
            
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            })
            print(f"Result: ERROR - {e}")
            return False
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data.get('status')}")
                print(f"Service: {data.get('service')}")
                print(f"YouTube API: {data.get('youtube_api')}")
                print(f"Version: {data.get('version')}")
                return True
            else:
                print(f"Health check failed with status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Health check request failed: {e}")
            return False
    
    def test_api_info(self) -> bool:
        """Test API info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api-info", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"API Name: {data.get('api_name')}")
                print(f"Features: {len(data.get('features', []))}")
                print(f"Security Features: {len(data.get('security_features', []))}")
                return True
            else:
                print(f"API info failed with status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"API info request failed: {e}")
            return False
    
    def test_get_items(self) -> bool:
        """Test getting all items"""
        try:
            response = self.session.get(f"{self.base_url}/items", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                print(f"Total items: {data.get('total_count')}")
                print(f"Categories: {len(data.get('categories', []))}")
                print(f"Sample item: {items[0]['title'] if items else 'None'}")
                return len(items) > 0
            else:
                print(f"Get items failed with status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Get items request failed: {e}")
            return False
    
    def test_get_categories(self) -> bool:
        """Test getting categories"""
        try:
            response = self.session.get(f"{self.base_url}/categories", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                print(f"Categories found: {categories}")
                return len(categories) > 0
            else:
                print(f"Get categories failed with status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Get categories request failed: {e}")
            return False
    
    def test_user_preferences(self) -> bool:
        """Test setting and getting user preferences"""
        try:
            # Set preferences
            preferences_data = {
                "user_id": "test_user_123",
                "categories": ["Programming", "Data Science"],
                "keywords": ["python", "machine learning"]
            }
            
            response = self.session.post(
                f"{self.base_url}/user/preferences",
                json=preferences_data,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"Set preferences failed with status: {response.status_code}")
                return False
            
            # Get preferences
            response = self.session.get(
                f"{self.base_url}/user/test_user_123/preferences",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Retrieved preferences: {data}")
                return data.get('categories') == preferences_data['categories']
            else:
                print(f"Get preferences failed with status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"User preferences request failed: {e}")
            return False
    
    def test_recommendations(self) -> bool:
        """Test getting recommendations"""
        try:
            request_data = {
                "user_id": "test_user_123",
                "num_recommendations": 3
            }
            
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=request_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get('recommendations', [])
                print(f"Recommendations received: {len(recommendations)}")
                print(f"Status: {data.get('status')}")
                print(f"Total count: {data.get('total_count')}")
                
                if recommendations:
                    print(f"Sample recommendation: {recommendations[0].get('title', 'N/A')}")
                
                return len(recommendations) > 0
            else:
                print(f"Recommendations failed with status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"Recommendations request failed: {e}")
            return False
    
    def test_recommendation_feedback(self) -> bool:
        """Test recommendation feedback"""
        try:
            feedback_data = {
                "user_id": "test_user_123",
                "item_id": "1",
                "feedback_type": "like",
                "rating": 4.5
            }
            
            response = self.session.post(
                f"{self.base_url}/recommendations/feedback",
                params=feedback_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Feedback recorded: {data.get('message')}")
                return True
            else:
                print(f"Feedback failed with status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Feedback request failed: {e}")
            return False
    
    def test_youtube_quota_status(self) -> bool:
        """Test YouTube quota status (if configured)"""
        try:
            response = self.session.get(f"{self.base_url}/youtube/quota-status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                quota_status = data.get('quota_status', {})
                print(f"Quota used: {quota_status.get('quota_used', 0)}")
                print(f"Quota limit: {quota_status.get('quota_limit', 0)}")
                return True
            elif response.status_code == 503:
                print("YouTube API not configured (expected)")
                return True
            else:
                print(f"Quota status failed with status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Quota status request failed: {e}")
            return False
    
    def test_input_validation(self) -> bool:
        """Test input validation and security"""
        try:
            # Test with malicious input
            malicious_data = {
                "user_id": "<script>alert('xss')</script>",
                "num_recommendations": -1
            }
            
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=malicious_data,
                timeout=10
            )
            
            # Should return validation error
            if response.status_code == 422:
                print("Input validation working correctly")
                return True
            else:
                print(f"Input validation failed - accepted malicious input")
                return False
                
        except requests.RequestException as e:
            print(f"Input validation test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive API Tests")
        print("="*80)
        
        # Core functionality tests
        core_tests = [
            ("Health Check", self.test_health_check),
            ("API Information", self.test_api_info),
            ("Get Items", self.test_get_items),
            ("Get Categories", self.test_get_categories),
            ("User Preferences", self.test_user_preferences),
            ("Recommendations", self.test_recommendations),
            ("Recommendation Feedback", self.test_recommendation_feedback),
            ("Input Validation", self.test_input_validation),
        ]
        
        # YouTube tests (optional)
        youtube_tests = [
            ("YouTube Quota Status", self.test_youtube_quota_status),
        ]
        
        # Run core tests
        print("\n📋 Core Functionality Tests")
        for test_name, test_func in core_tests:
            self.run_test(test_name, test_func)
        
        # Run YouTube tests
        print("\n🎥 YouTube Integration Tests")
        for test_name, test_func in youtube_tests:
            self.run_test(test_name, test_func)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*80)
        print("📊 TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 80)
        
        for result in self.test_results:
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌", 
                "ERROR": "⚠️"
            }.get(result["status"], "❓")
            
            duration = result.get("duration", "N/A")
            error = result.get("error", "")
            
            print(f"{status_emoji} {result['test']:<30} {result['status']:<6} ({duration})")
            if error:
                print(f"   Error: {error}")
        
        print("\n" + "="*80)
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! API is working correctly.")
        elif passed_tests > total_tests * 0.8:
            print("✨ Most tests passed. Check failed tests for issues.")
        else:
            print("⚠️  Multiple test failures detected. Please review the API.")


def main():
    """Main test runner"""
    print("Ethical Recommendation System API - Test Suite")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly.")
            print("Please start the server with: python run_server.py")
            return
    except requests.RequestException:
        print("❌ Cannot connect to the server.")
        print("Please start the server with: python run_server.py")
        return
    
    # Run tests
    tester = APITester(BASE_URL)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
