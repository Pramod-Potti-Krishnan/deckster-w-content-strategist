"""
Quality metrics and performance testing for Layout Architect.

Measures and validates quality of generated layouts and system performance.
"""

import asyncio
import pytest
import time
import statistics
from typing import Dict, Any, List, Tuple
from datetime import datetime
import json
import os

from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    LayoutGenerationRequest,
    MVPLayout
)
from .test_synthetic_data import SyntheticDataGenerator, get_complete_test_scenario


class QualityMetrics:
    """Calculate quality metrics for layouts."""
    
    @staticmethod
    def calculate_visual_balance(layout: MVPLayout) -> Dict[str, float]:
        """Calculate visual balance metrics."""
        if not layout.containers:
            return {"balance_score": 0, "symmetry_score": 0}
        
        # Calculate center of mass
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        for container in layout.containers:
            pos = container.position
            # Assume equal weight for simplicity (could use visual_weight if available)
            weight = 1.0
            
            center_x = pos.leftInset + pos.width / 2
            center_y = pos.topInset + pos.height / 2
            
            weighted_x += center_x * weight
            weighted_y += center_y * weight
            total_weight += weight
        
        if total_weight == 0:
            return {"balance_score": 0, "symmetry_score": 0}
        
        com_x = weighted_x / total_weight
        com_y = weighted_y / total_weight
        
        # Calculate balance score (distance from center)
        ideal_x = 80  # Center of 160 grid
        ideal_y = 45  # Center of 90 grid
        
        distance = ((com_x - ideal_x)**2 + (com_y - ideal_y)**2)**0.5
        max_distance = (80**2 + 45**2)**0.5
        
        balance_score = 1.0 - (distance / max_distance)
        
        # Calculate symmetry score
        symmetry_score = QualityMetrics._calculate_symmetry(layout.containers)
        
        return {
            "balance_score": balance_score,
            "symmetry_score": symmetry_score,
            "center_of_mass": (com_x, com_y)
        }
    
    @staticmethod
    def _calculate_symmetry(containers) -> float:
        """Calculate horizontal symmetry score."""
        if not containers:
            return 0
        
        center_x = 80  # Center of grid
        left_area = 0
        right_area = 0
        
        for container in containers:
            pos = container.position
            area = pos.width * pos.height
            container_center = pos.leftInset + pos.width / 2
            
            if container_center < center_x:
                left_area += area
            else:
                right_area += area
        
        total_area = left_area + right_area
        if total_area == 0:
            return 1.0
        
        # Calculate symmetry as 1 - normalized difference
        diff = abs(left_area - right_area) / total_area
        return 1.0 - diff
    
    @staticmethod
    def calculate_alignment_quality(layout: MVPLayout) -> Dict[str, Any]:
        """Calculate alignment quality metrics."""
        if not layout.containers:
            return {"alignment_score": 1.0, "issues": []}
        
        issues = []
        aligned_count = 0
        total_checks = 0
        
        # Check horizontal alignment
        x_positions = {}
        for container in layout.containers:
            left = container.position.leftInset
            right = left + container.position.width
            
            # Group by position
            if left not in x_positions:
                x_positions[left] = []
            x_positions[left].append(container.id)
            
            if right not in x_positions:
                x_positions[right] = []
            x_positions[right].append(container.id)
        
        # Check vertical alignment
        y_positions = {}
        for container in layout.containers:
            top = container.position.topInset
            bottom = top + container.position.height
            
            if top not in y_positions:
                y_positions[top] = []
            y_positions[top].append(container.id)
            
            if bottom not in y_positions:
                y_positions[bottom] = []
            y_positions[bottom].append(container.id)
        
        # Count aligned edges
        for pos, containers in x_positions.items():
            if len(containers) > 1:
                aligned_count += len(containers) - 1
            total_checks += max(0, len(containers) - 1)
        
        for pos, containers in y_positions.items():
            if len(containers) > 1:
                aligned_count += len(containers) - 1
            total_checks += max(0, len(containers) - 1)
        
        alignment_score = aligned_count / total_checks if total_checks > 0 else 1.0
        
        return {
            "alignment_score": alignment_score,
            "aligned_edges": aligned_count,
            "total_edges": total_checks
        }
    
    @staticmethod
    def calculate_spacing_consistency(layout: MVPLayout) -> Dict[str, Any]:
        """Calculate spacing consistency metrics."""
        if len(layout.containers) < 2:
            return {"consistency_score": 1.0, "variations": []}
        
        # Calculate all gaps
        horizontal_gaps = []
        vertical_gaps = []
        
        containers = sorted(layout.containers, key=lambda c: (c.position.topInset, c.position.leftInset))
        
        for i, c1 in enumerate(containers):
            for c2 in containers[i+1:]:
                # Horizontal gap
                if c1.position.topInset == c2.position.topInset:
                    gap = c2.position.leftInset - (c1.position.leftInset + c1.position.width)
                    if gap > 0:
                        horizontal_gaps.append(gap)
                
                # Vertical gap
                if c1.position.leftInset == c2.position.leftInset:
                    gap = c2.position.topInset - (c1.position.topInset + c1.position.height)
                    if gap > 0:
                        vertical_gaps.append(gap)
        
        # Calculate consistency
        all_gaps = horizontal_gaps + vertical_gaps
        if not all_gaps:
            return {"consistency_score": 1.0, "variations": []}
        
        avg_gap = statistics.mean(all_gaps)
        if avg_gap == 0:
            return {"consistency_score": 1.0, "variations": []}
        
        variations = [abs(gap - avg_gap) / avg_gap for gap in all_gaps]
        consistency_score = 1.0 - min(statistics.mean(variations), 1.0)
        
        return {
            "consistency_score": consistency_score,
            "average_gap": avg_gap,
            "gap_count": len(all_gaps),
            "variations": variations
        }
    
    @staticmethod
    def calculate_readability_score(layout: MVPLayout) -> float:
        """Calculate readability score based on text container sizes."""
        text_containers = [c for c in layout.containers if c.type == "text"]
        
        if not text_containers:
            return 1.0
        
        scores = []
        for container in text_containers:
            area = container.position.width * container.position.height
            
            # Score based on minimum readable area (arbitrary thresholds)
            if area < 200:  # Too small
                scores.append(0.3)
            elif area < 500:  # Acceptable
                scores.append(0.7)
            elif area < 2000:  # Good
                scores.append(1.0)
            else:  # Might be too large
                scores.append(0.8)
        
        return statistics.mean(scores) if scores else 1.0


class PerformanceProfiler:
    """Profile performance of Layout Architect components."""
    
    def __init__(self):
        self.timings = {}
        self.memory_usage = {}
    
    async def profile_agent_performance(self, orchestrator, test_scenarios: int = 10):
        """Profile performance of individual agents."""
        generator = SyntheticDataGenerator(seed=42)
        
        agent_timings = {
            "theme": [],
            "structure": [],
            "layout": [],
            "total": []
        }
        
        for i in range(test_scenarios):
            slide = generator.generate_slide(f"perf_{i}", i+1, "content_heavy")
            
            start_total = time.time()
            
            # We can't directly time individual agents in orchestrator
            # So we'll time the whole process
            request = LayoutGenerationRequest(slide=slide)
            result = await orchestrator.generate_layout(request)
            
            total_time = time.time() - start_total
            agent_timings["total"].append(total_time)
            
            if result.success:
                # Extract timing from metrics if available
                metrics = result.generation_metrics
                if "theme_generation_time" in metrics:
                    agent_timings["theme"].append(metrics["theme_generation_time"])
                if "structure_analysis_time" in metrics:
                    agent_timings["structure"].append(metrics["structure_analysis_time"])
                if "layout_generation_time" in metrics:
                    agent_timings["layout"].append(metrics["layout_generation_time"])
        
        # Calculate statistics
        stats = {}
        for agent, timings in agent_timings.items():
            if timings:
                stats[agent] = {
                    "mean": statistics.mean(timings),
                    "median": statistics.median(timings),
                    "stdev": statistics.stdev(timings) if len(timings) > 1 else 0,
                    "min": min(timings),
                    "max": max(timings),
                    "samples": len(timings)
                }
        
        return stats
    
    async def profile_scaling(self, orchestrator, slide_counts: List[int] = [1, 5, 10, 20]):
        """Profile how performance scales with number of slides."""
        generator = SyntheticDataGenerator(seed=42)
        scaling_results = {}
        
        for count in slide_counts:
            slides = [
                generator.generate_slide(f"scale_{i}", i, "content_heavy")
                for i in range(count)
            ]
            
            start_time = time.time()
            results = await orchestrator.generate_batch(slides=slides)
            total_time = time.time() - start_time
            
            successful = sum(1 for r in results if r.success)
            
            scaling_results[count] = {
                "total_time": total_time,
                "per_slide_time": total_time / count,
                "success_rate": successful / count,
                "successful_count": successful
            }
        
        return scaling_results


class TestQualityMetrics:
    """Test quality metrics for generated layouts."""
    
    @pytest.fixture
    def orchestrator(self):
        return LayoutArchitectOrchestrator()
    
    @pytest.fixture
    def quality_metrics(self):
        return QualityMetrics()
    
    @pytest.mark.asyncio
    async def test_visual_balance_metrics(self, orchestrator, quality_metrics):
        """Test visual balance across different slide types."""
        generator = SyntheticDataGenerator()
        
        slide_types = ["title_slide", "content_heavy", "visual_heavy", "data_driven"]
        balance_results = {}
        
        for slide_type in slide_types:
            slide = generator.generate_slide("balance_test", 1, slide_type)
            request = LayoutGenerationRequest(slide=slide)
            result = await orchestrator.generate_layout(request)
            
            if result.success:
                balance = quality_metrics.calculate_visual_balance(result.layout)
                balance_results[slide_type] = balance
                
                print(f"\n{slide_type}:")
                print(f"  Balance score: {balance['balance_score']:.3f}")
                print(f"  Symmetry score: {balance['symmetry_score']:.3f}")
                
                # Quality assertions
                assert balance["balance_score"] > 0.5, f"Poor balance for {slide_type}"
                
                # Title slides should be well-centered
                if slide_type == "title_slide":
                    assert balance["balance_score"] > 0.7
    
    @pytest.mark.asyncio
    async def test_alignment_quality(self, orchestrator, quality_metrics):
        """Test alignment quality of generated layouts."""
        slides = [
            get_complete_test_scenario()["strawman"].slides[i]
            for i in range(3)
        ]
        
        alignment_scores = []
        
        for slide in slides:
            request = LayoutGenerationRequest(slide=slide)
            result = await orchestrator.generate_layout(request)
            
            if result.success:
                alignment = quality_metrics.calculate_alignment_quality(result.layout)
                alignment_scores.append(alignment["alignment_score"])
                
                print(f"\nSlide {slide.slide_id}:")
                print(f"  Alignment score: {alignment['alignment_score']:.3f}")
                print(f"  Aligned edges: {alignment['aligned_edges']}/{alignment['total_edges']}")
                
                # Should have good alignment
                assert alignment["alignment_score"] > 0.6
        
        # Average alignment should be high
        avg_alignment = statistics.mean(alignment_scores) if alignment_scores else 0
        assert avg_alignment > 0.7, f"Poor average alignment: {avg_alignment:.3f}"
    
    @pytest.mark.asyncio
    async def test_spacing_consistency(self, orchestrator, quality_metrics):
        """Test spacing consistency in layouts."""
        slide = SyntheticDataGenerator().generate_slide(
            "spacing_test", 1, "content_heavy"
        )
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        if result.success:
            spacing = quality_metrics.calculate_spacing_consistency(result.layout)
            
            print(f"\nSpacing consistency:")
            print(f"  Score: {spacing['consistency_score']:.3f}")
            print(f"  Average gap: {spacing.get('average_gap', 0):.1f} units")
            print(f"  Gap count: {spacing.get('gap_count', 0)}")
            
            # Should have consistent spacing
            assert spacing["consistency_score"] > 0.5
    
    @pytest.mark.asyncio
    async def test_readability_scores(self, orchestrator, quality_metrics):
        """Test readability scores for text-heavy slides."""
        slide = SyntheticDataGenerator().generate_slide(
            "readability_test", 1, "content_heavy"
        )
        slide.key_points = [
            "This is a longer point that requires more space to display properly",
            "Another detailed point with important information",
            "Third point with substantial content"
        ]
        
        request = LayoutGenerationRequest(slide=slide)
        result = await orchestrator.generate_layout(request)
        
        if result.success:
            readability = quality_metrics.calculate_readability_score(result.layout)
            
            print(f"\nReadability score: {readability:.3f}")
            
            # Content-heavy slides should have good readability
            assert readability > 0.6
    
    @pytest.mark.asyncio
    async def test_quality_by_industry(self, orchestrator, quality_metrics):
        """Test quality metrics across different industries."""
        industries = ["healthcare", "finance", "education", "technology"]
        generator = SyntheticDataGenerator()
        
        industry_scores = {}
        
        for industry in industries:
            slide = generator.generate_slide("industry_test", 1, "content_heavy", industry)
            request = LayoutGenerationRequest(
                slide=slide,
                user_context={"industry": industry}
            )
            
            result = await orchestrator.generate_layout(request)
            
            if result.success:
                balance = quality_metrics.calculate_visual_balance(result.layout)
                alignment = quality_metrics.calculate_alignment_quality(result.layout)
                
                industry_scores[industry] = {
                    "balance": balance["balance_score"],
                    "alignment": alignment["alignment_score"],
                    "white_space": result.layout.white_space_ratio
                }
                
                print(f"\n{industry.capitalize()}:")
                print(f"  Balance: {balance['balance_score']:.3f}")
                print(f"  Alignment: {alignment['alignment_score']:.3f}")
                print(f"  White space: {result.layout.white_space_ratio:.2%}")
        
        # All industries should maintain quality
        for industry, scores in industry_scores.items():
            assert scores["balance"] > 0.5
            assert scores["alignment"] > 0.6
            assert 0.25 <= scores["white_space"] <= 0.55


class TestPerformanceMetrics:
    """Test performance metrics for Layout Architect."""
    
    @pytest.fixture
    def orchestrator(self):
        return LayoutArchitectOrchestrator()
    
    @pytest.fixture
    def profiler(self):
        return PerformanceProfiler()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_agent_performance_profile(self, orchestrator, profiler):
        """Profile performance of individual agents."""
        stats = await profiler.profile_agent_performance(orchestrator, test_scenarios=5)
        
        print("\n📊 Agent Performance Profile:")
        for agent, metrics in stats.items():
            print(f"\n{agent.upper()}:")
            print(f"  Mean: {metrics['mean']:.3f}s")
            print(f"  Median: {metrics['median']:.3f}s")
            print(f"  Std Dev: {metrics['stdev']:.3f}s")
            print(f"  Range: {metrics['min']:.3f}s - {metrics['max']:.3f}s")
        
        # Performance assertions
        if "total" in stats:
            assert stats["total"]["mean"] < 15.0, "Average generation too slow"
            assert stats["total"]["max"] < 30.0, "Worst case too slow"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_scaling_performance(self, orchestrator, profiler):
        """Test how performance scales with slide count."""
        scaling = await profiler.profile_scaling(orchestrator, slide_counts=[1, 5, 10])
        
        print("\n📈 Scaling Performance:")
        for count, metrics in scaling.items():
            print(f"\n{count} slides:")
            print(f"  Total time: {metrics['total_time']:.2f}s")
            print(f"  Per slide: {metrics['per_slide_time']:.2f}s")
            print(f"  Success rate: {metrics['success_rate']:.1%}")
        
        # Scaling assertions
        if 1 in scaling and 10 in scaling:
            # Per-slide time shouldn't increase too much
            time_increase = scaling[10]["per_slide_time"] / scaling[1]["per_slide_time"]
            assert time_increase < 2.0, f"Poor scaling: {time_increase:.1f}x slower per slide"
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, orchestrator):
        """Test memory efficiency with large presentations."""
        # This is a simple test - real memory profiling would use memory_profiler
        generator = SyntheticDataGenerator()
        
        # Generate a large presentation
        slides = [
            generator.generate_slide(f"mem_{i}", i, "content_heavy")
            for i in range(20)
        ]
        
        # Process in batch
        start_time = time.time()
        results = await orchestrator.generate_batch(slides=slides)
        batch_time = time.time() - start_time
        
        successful = sum(1 for r in results if r.success)
        
        print(f"\n💾 Memory efficiency test:")
        print(f"  Processed: {len(slides)} slides")
        print(f"  Successful: {successful}")
        print(f"  Time: {batch_time:.2f}s")
        print(f"  Rate: {len(slides)/batch_time:.1f} slides/s")
        
        assert successful == len(slides), "Some slides failed in batch processing"


class TestQualityReports:
    """Generate quality reports for analysis."""
    
    @pytest.fixture
    def output_dir(self, test_output_dir):
        return test_output_dir
    
    @pytest.mark.asyncio
    async def test_generate_quality_report(self, output_dir):
        """Generate comprehensive quality report."""
        orchestrator = LayoutArchitectOrchestrator()
        quality_metrics = QualityMetrics()
        generator = SyntheticDataGenerator()
        
        # Test various scenarios
        test_cases = [
            ("Simple Title", "title_slide", "technology"),
            ("Complex Content", "content_heavy", "healthcare"),
            ("Visual Heavy", "visual_heavy", "education"),
            ("Data Dashboard", "data_driven", "finance")
        ]
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_cases": []
        }
        
        for name, slide_type, industry in test_cases:
            slide = generator.generate_slide("report_test", 1, slide_type, industry)
            request = LayoutGenerationRequest(
                slide=slide,
                user_context={"industry": industry}
            )
            
            result = await orchestrator.generate_layout(request)
            
            if result.success:
                # Calculate all metrics
                balance = quality_metrics.calculate_visual_balance(result.layout)
                alignment = quality_metrics.calculate_alignment_quality(result.layout)
                spacing = quality_metrics.calculate_spacing_consistency(result.layout)
                readability = quality_metrics.calculate_readability_score(result.layout)
                
                case_data = {
                    "name": name,
                    "slide_type": slide_type,
                    "industry": industry,
                    "containers": len(result.layout.containers),
                    "white_space": result.layout.white_space_ratio,
                    "balance_score": balance["balance_score"],
                    "symmetry_score": balance["symmetry_score"],
                    "alignment_score": alignment["alignment_score"],
                    "spacing_consistency": spacing["consistency_score"],
                    "readability_score": readability,
                    "generation_metrics": result.generation_metrics
                }
                
                report_data["test_cases"].append(case_data)
                
                print(f"\n✅ {name}:")
                print(f"   Overall quality: {(balance['balance_score'] + alignment['alignment_score']) / 2:.2%}")
        
        # Save report
        report_path = os.path.join(output_dir, "quality_report.json")
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Quality report saved to: {report_path}")


if __name__ == "__main__":
    # Run quality tests
    pytest.main([__file__, "-v", "-k", "quality"])