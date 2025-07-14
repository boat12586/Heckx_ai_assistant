#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Tests all endpoints and performance metrics
"""
import requests
import time
import json
from datetime import datetime

def test_endpoint(url, method='GET', timeout=30):
    """Test a single endpoint"""
    try:
        start_time = time.time()
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, timeout=timeout)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_time': round(response_time, 3),
            'content_length': len(response.content),
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'response_time': None
        }

def run_deployment_tests(base_url):
    """Run comprehensive deployment tests"""
    
    print(f"🚀 Testing Heckx AI deployment at: {base_url}")
    print("=" * 60)
    
    tests = [
        {'name': 'Home Page', 'url': f'{base_url}/', 'method': 'GET'},
        {'name': 'Health Check', 'url': f'{base_url}/health', 'method': 'GET'},
        {'name': 'Quote API', 'url': f'{base_url}/api/quote', 'method': 'GET'},
        {'name': 'Test API', 'url': f'{base_url}/api/test', 'method': 'POST'},
        {'name': 'Performance API', 'url': f'{base_url}/api/performance', 'method': 'GET'},
    ]
    
    results = []
    
    for test in tests:
        print(f"Testing {test['name']}... ", end="")
        result = test_endpoint(test['url'], test['method'])
        results.append({**test, **result})
        
        if result['success']:
            print(f"✅ {result['response_time']}s")
        else:
            print(f"❌ {result.get('error', 'Failed')}")
    
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"✅ Successful tests: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Performance analysis
    response_times = [r['response_time'] for r in results if r['response_time']]
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        print(f"⚡ Average response time: {avg_response_time:.3f}s")
        print(f"🐌 Slowest response: {max_response_time:.3f}s")
        
        if avg_response_time < 0.5:
            print("🏆 EXCELLENT performance!")
        elif avg_response_time < 1.0:
            print("✅ Good performance")
        elif avg_response_time < 2.0:
            print("⚠️  Acceptable performance")
        else:
            print("🚨 Performance needs optimization")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    print("-" * 60)
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['name']}: {result.get('response_time', 'N/A')}s")
        if not result['success']:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Health check analysis
    health_result = next((r for r in results if r['name'] == 'Health Check'), None)
    if health_result and health_result['success'] and health_result['data']:
        print("\n🏥 HEALTH CHECK DETAILS:")
        print("-" * 40)
        health_data = health_result['data']
        print(f"App: {health_data.get('app', 'Unknown')}")
        print(f"Version: {health_data.get('version', 'Unknown')}")
        
        if 'system' in health_data:
            system = health_data['system']
            print(f"Memory usage: {system.get('memory_percent', 'N/A')}%")
            print(f"CPU usage: {system.get('cpu_percent', 'N/A')}%")
            print(f"Available memory: {system.get('memory_available_gb', 'N/A')} GB")
        
        if 'performance' in health_data:
            perf = health_data['performance']
            print(f"Workers: {perf.get('workers', 'N/A')}")
            print(f"Environment: {perf.get('environment', 'Unknown')}")
        
        if 'warnings' in health_data:
            print(f"⚠️  Warnings: {', '.join(health_data['warnings'])}")
    
    return {
        'success_rate': success_rate,
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'average_response_time': avg_response_time if response_times else None,
        'max_response_time': max_response_time if response_times else None,
        'timestamp': datetime.now().isoformat(),
        'results': results
    }

if __name__ == '__main__':
    # For Railway deployment testing
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        # Default to localhost for local testing
        base_url = 'http://localhost:8000'
    
    try:
        summary = run_deployment_tests(base_url)
        
        # Save results
        with open('deployment_test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to deployment_test_results.json")
        
        # Exit code based on success rate
        if summary['success_rate'] >= 100:
            print("🎉 ALL TESTS PASSED! Deployment is PERFECT!")
            sys.exit(0)
        elif summary['success_rate'] >= 80:
            print("✅ Deployment is working well with minor issues")
            sys.exit(0)
        else:
            print("🚨 Deployment has significant issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        sys.exit(1)