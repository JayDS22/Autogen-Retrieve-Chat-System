"""
Performance analysis utilities for AutoGen RetrieveChat system
Author: Jay Guwalani
"""

import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Data class for performance metrics"""
    execution_time: float
    success: bool
    question_length: int
    response_length: int
    conversation_turns: int = 0
    error_message: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class PerformanceAnalyzer:
    """Comprehensive performance analysis for the RetrieveChat system"""
    
    def __init__(self):
        self.metrics_history = []
        self.thresholds = {
            "excellent": 1.0,
            "good": 3.0,
            "acceptable": 5.0
        }
        logger.info("PerformanceAnalyzer initialized")
    
    def record_metric(self, metrics: Dict[str, Any]):
        """Record a performance metric"""
        try:
            metric = PerformanceMetrics(
                execution_time=metrics.get("execution_time", 0),
                success=metrics.get("success", True),
                question_length=metrics.get("question_length", 0),
                response_length=metrics.get("response_length", 0),
                conversation_turns=metrics.get("conversation_turns", 0),
                error_message=metrics.get("error"),
                timestamp=metrics.get("timestamp", time.time())
            )
            self.metrics_history.append(metric)
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    def analyze_all_results(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Analyze results from all test scenarios"""
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE PERFORMANCE ANALYSIS")
        print(f"{'='*80}")
        
        overall_stats = {
            "total_scenarios": 0,
            "total_execution_time": 0,
            "success_rate": 0,
            "performance_distribution": {}
        }
        
        for scenario_type, scenario_results in results.items():
            if not scenario_results:
                continue
                
            print(f"\n📊 {scenario_type.upper()} ANALYSIS:")
            print("-" * 50)
            
            stats = self._analyze_scenario(scenario_results)
            overall_stats["total_scenarios"] += stats["count"]
            overall_stats["total_execution_time"] += stats["total_time"]
            
            self._print_scenario_stats(stats)
        
        # Calculate overall metrics
        if overall_stats["total_scenarios"] > 0:
            overall_stats["average_execution_time"] = (
                overall_stats["total_execution_time"] / overall_stats["total_scenarios"]
            )
        
        self._print_overall_summary(overall_stats)
        return overall_stats
    
    def _analyze_scenario(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze a specific scenario type"""
        
        execution_times = []
        success_count = 0
        
        for result in results:
            # Extract execution time from various possible locations
            exec_time = self._extract_execution_time(result)
            if exec_time:
                execution_times.append(exec_time)
            
            # Check success status
            if self._is_successful(result):
                success_count += 1
        
        if not execution_times:
            return {"count": 0, "total_time": 0}
        
        stats = {
            "count": len(results),
            "total_time": sum(execution_times),
            "avg_time": np.mean(execution_times),
            "min_time": np.min(execution_times),
            "max_time": np.max(execution_times),
            "std_time": np.std(execution_times),
            "p95_time": np.percentile(execution_times, 95),
            "success_rate": success_count / len(results),
            "performance_grades": self._classify_performance(execution_times)
        }
        
        return stats
    
    def _extract_execution_time(self, result: Dict) -> Optional[float]:
        """Extract execution time from result object"""
        # Try different possible locations for execution time
        if "execution_time" in result:
            return result["execution_time"]
        elif "response_time" in result:
            return result["response_time"]
        elif "result" in result and "metrics" in result["result"]:
            return result["result"]["metrics"].get("execution_time")
        elif "metrics" in result:
            return result["metrics"].get("execution_time")
        return None
    
    def _is_successful(self, result: Dict) -> bool:
        """Check if result indicates success"""
        if "error" in result:
            return False
        if "result" in result and result["result"] is None:
            return False
        return True
    
    def _classify_performance(self, execution_times: List[float]) -> Dict[str, int]:
        """Classify performance into categories"""
        classification = {
            "excellent": 0,
            "good": 0,
            "acceptable": 0,
            "needs_optimization": 0
        }
        
        for time_val in execution_times:
            if time_val < self.thresholds["excellent"]:
                classification["excellent"] += 1
            elif time_val < self.thresholds["good"]:
                classification["good"] += 1
            elif time_val < self.thresholds["acceptable"]:
                classification["acceptable"] += 1
            else:
                classification["needs_optimization"] += 1
        
        return classification
    
    def _print_scenario_stats(self, stats: Dict[str, Any]):
        """Print statistics for a scenario"""
        if stats["count"] == 0:
            print("   No data available")
            return
        
        print(f"   Total Operations: {stats['count']}")
        print(f"   Average Time: {stats['avg_time']:.2f}s")
        print(f"   Time Range: {stats['min_time']:.2f}s - {stats['max_time']:.2f}s")
        print(f"   95th Percentile: {stats['p95_time']:.2f}s")
        print(f"   Success Rate: {stats['success_rate']:.1%}")
        print(f"   Standard Deviation: {stats['std_time']:.2f}s")
        
        # Performance distribution
        grades = stats["performance_grades"]
        print(f"   Performance Distribution:")
        print(f"     Excellent (<1s): {grades['excellent']}")
        print(f"     Good (1-3s): {grades['good']}")
        print(f"     Acceptable (3-5s): {grades['acceptable']}")
        print(f"     Needs Optimization (>5s): {grades['needs_optimization']}")
    
    def _print_overall_summary(self, stats: Dict[str, Any]):
        """Print overall performance summary"""
        print(f"\n🎯 OVERALL SYSTEM PERFORMANCE:")
        print("-" * 50)
        print(f"   Total Scenarios Executed: {stats['total_scenarios']}")
        print(f"   Total Execution Time: {stats['total_execution_time']:.2f}s")
        
        if stats["total_scenarios"] > 0:
            avg_time = stats["total_execution_time"] / stats["total_scenarios"]
            print(f"   Average Response Time: {avg_time:.2f}s")
            
            # Overall performance grade
            if avg_time < 1.0:
                grade = "EXCELLENT"
                recommendation = "System performing optimally"
            elif avg_time < 3.0:
                grade = "GOOD"
                recommendation = "System performing well"
            elif avg_time < 5.0:
                grade = "ACCEPTABLE"
                recommendation = "Consider optimization for better performance"
            else:
                grade = "NEEDS OPTIMIZATION"
                recommendation = "System requires performance tuning"
            
            print(f"   Overall Grade: {grade}")
            print(f"   Recommendation: {recommendation}")
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        if not self.metrics_history:
            return {"message": "No performance data available"}
        
        execution_times = [m.execution_time for m in self.metrics_history]
        success_count = sum(1 for m in self.metrics_history if m.success)
        
        report = {
            "summary": {
                "total_operations": len(self.metrics_history),
                "success_rate": success_count / len(self.metrics_history),
                "avg_execution_time": np.mean(execution_times),
                "min_execution_time": np.min(execution_times),
                "max_execution_time": np.max(execution_times),
                "p95_execution_time": np.percentile(execution_times, 95),
                "p99_execution_time": np.percentile(execution_times, 99)
            },
            "performance_distribution": self._classify_performance(execution_times),
            "trends": self._analyze_trends(),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(self.metrics_history) < 5:
            return {"message": "Insufficient data for trend analysis"}
        
        # Split into chunks for trend analysis
        chunk_size = max(5, len(self.metrics_history) // 3)
        chunks = [
            self.metrics_history[i:i + chunk_size] 
            for i in range(0, len(self.metrics_history), chunk_size)
        ]
        
        chunk_averages = [
            np.mean([m.execution_time for m in chunk]) 
            for chunk in chunks if chunk
        ]
        
        if len(chunk_averages) >= 2:
            trend = "improving" if chunk_averages[-1] < chunk_averages[0] else "degrading"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "chunk_averages": chunk_averages,
            "chunks_analyzed": len(chunks)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if not self.metrics_history:
            return ["No data available for recommendations"]
        
        avg_time = np.mean([m.execution_time for m in self.metrics_history])
        success_rate = sum(1 for m in self.metrics_history if m.success) / len(self.metrics_history)
        
        if avg_time > 5.0:
            recommendations.append("Consider optimizing document chunking strategy")
            recommendations.append("Evaluate vector database performance")
            recommendations.append("Review model selection for faster inference")
        
        if success_rate < 0.95:
            recommendations.append("Improve error handling and recovery mechanisms")
            recommendations.append("Add retry logic for failed operations")
        
        if avg_time > 3.0:
            recommendations.append("Implement caching for frequently accessed documents")
            recommendations.append("Consider parallel processing for multiple queries")
        
        # Add default recommendations if none generated
        if not recommendations:
            recommendations.append("System performing well - maintain current configuration")
            recommendations.append("Monitor performance regularly for early detection of issues")
        
        return recommendations
