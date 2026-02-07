"""
Visualization Module - Generate maps and charts for medical desert analysis
"""
import json
from typing import List, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter
import pandas as pd


class MedicalDesertVisualizer:
    """
    Create visualizations for:
    1. Regional coverage heatmaps
    2. Capability distribution charts
    3. Medical desert severity maps
    4. Trend analysis over capabilities
    """
    
    # Ghana regions coordinates (approximate centroids for visualization)
    GHANA_REGIONS = {
        'Greater Accra': {'lat': 5.6037, 'lon': -0.1870, 'x': 0.6, 'y': 0.3},
        'Ashanti': {'lat': 6.7467, 'lon': -1.5233, 'x': 0.5, 'y': 0.5},
        'Eastern': {'lat': 6.1667, 'lon': -0.5000, 'x': 0.65, 'y': 0.4},
        'Western': {'lat': 5.2833, 'lon': -2.0000, 'x': 0.3, 'y': 0.3},
        'Central': {'lat': 5.5600, 'lon': -1.0000, 'x': 0.45, 'y': 0.35},
        'Volta': {'lat': 6.6000, 'lon': 0.4700, 'x': 0.8, 'y': 0.45},
        'Northern': {'lat': 9.4000, 'lon': -0.8400, 'x': 0.5, 'y': 0.8},
        'Upper East': {'lat': 10.7200, 'lon': -0.9800, 'x': 0.65, 'y': 0.9},
        'Upper West': {'lat': 10.3000, 'lon': -2.3000, 'x': 0.35, 'y': 0.85},
        'Brong Ahafo': {'lat': 7.5000, 'lon': -1.5000, 'x': 0.45, 'y': 0.6},
        'Western North': {'lat': 6.0000, 'lon': -2.5000, 'x': 0.25, 'y': 0.45},
        'Savannah': {'lat': 9.0833, 'lon': -1.8167, 'x': 0.4, 'y': 0.75},
        'North East': {'lat': 10.5000, 'lon': -0.3000, 'x': 0.7, 'y': 0.85},
        'Bono East': {'lat': 7.7500, 'lon': -1.0500, 'x': 0.55, 'y': 0.65},
        'Ahafo': {'lat': 7.0000, 'lon': -2.0000, 'x': 0.4, 'y': 0.55},
        'Oti': {'lat': 7.9000, 'lon': 0.0500, 'x': 0.75, 'y': 0.6}
    }
    
    SEVERITY_COLORS = {
        'critical': '#dc3545',
        'severe': '#fd7e14',
        'moderate': '#ffc107',
        'minimal': '#28a745',
        'none': '#17a2b8'
    }
    
    def __init__(self):
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_medical_deserts_map(
        self,
        desert_analysis: Dict,
        output_path: str = 'output/medical_deserts_map.png'
    ):
        """
        Create a map visualization of medical deserts
        
        Args:
            desert_analysis: Output from MedicalDesertDetector.analyze_all_regions()
            output_path: Where to save the visualization
        """
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Title
        ax.set_title(
            'Ghana Medical Desert Analysis\nCritical Healthcare Capability Gaps by Region',
            fontsize=18,
            fontweight='bold',
            pad=20
        )
        
        # Create severity map
        severity_map = {
            region['region']: region['severity']
            for region in desert_analysis['all_regions']
        }
        
        # Plot regions
        for region_name, coords in self.GHANA_REGIONS.items():
            if region_name in severity_map:
                severity = severity_map[region_name]
                color = self.SEVERITY_COLORS.get(severity, '#cccccc')
                
                # Plot region circle
                circle = plt.Circle(
                    (coords['x'], coords['y']),
                    0.08,
                    color=color,
                    alpha=0.7,
                    edgecolor='white',
                    linewidth=2
                )
                ax.add_patch(circle)
                
                # Add region name
                ax.text(
                    coords['x'], coords['y'] - 0.12,
                    region_name,
                    ha='center',
                    va='top',
                    fontsize=9,
                    fontweight='bold'
                )
        
        # Legend
        legend_elements = [
            mpatches.Patch(facecolor=color, edgecolor='white', label=severity.title())
            for severity, color in self.SEVERITY_COLORS.items()
            if severity != 'none'
        ]
        ax.legend(
            handles=legend_elements,
            loc='upper right',
            title='Severity',
            fontsize=10
        )
        
        # Add statistics
        stats_text = (
            f"Total Regions: {desert_analysis['total_regions']}\n"
            f"Medical Deserts: {desert_analysis['desert_regions_count']}\n"
            f"Coverage: {((desert_analysis['total_regions'] - desert_analysis['desert_regions_count']) / desert_analysis['total_regions'] * 100):.1f}%"
        )
        ax.text(
            0.02, 0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        # Formatting
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Medical deserts map saved to: {output_path}")
    
    def plot_capability_coverage(
        self,
        desert_analysis: Dict,
        output_path: str = 'output/capability_coverage.png'
    ):
        """
        Create bar chart of capability coverage across regions
        """
        # Extract capability gaps
        if 'most_common_gaps' not in desert_analysis:
            print("No capability gap data available")
            return
        
        capabilities = []
        gap_counts = []
        
        for cap, count in desert_analysis['most_common_gaps'][:10]:
            capabilities.append(cap.replace('_', ' ').title())
            gap_counts.append(count)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.barh(capabilities, gap_counts, color='#667eea', alpha=0.8)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(
                width + 0.1,
                bar.get_y() + bar.get_height()/2,
                f'{int(width)} regions',
                ha='left',
                va='center',
                fontweight='bold'
            )
        
        ax.set_xlabel('Number of Regions with Gap', fontsize=12, fontweight='bold')
        ax.set_title(
            'Most Common Healthcare Capability Gaps\nAcross Ghana Regions',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Capability coverage chart saved to: {output_path}")
    
    def plot_region_comparison(
        self,
        desert_analysis: Dict,
        output_path: str = 'output/region_comparison.png'
    ):
        """
        Create comparison chart of regions by coverage percentage
        """
        # Extract region data
        regions = []
        coverage_percentages = []
        severities = []
        
        for region in desert_analysis['all_regions']:
            regions.append(region['region'])
            coverage_percentages.append(region['coverage_percentage'])
            severities.append(region['severity'])
        
        # Sort by coverage
        data = sorted(zip(regions, coverage_percentages, severities), key=lambda x: x[1])
        regions, coverage_percentages, severities = zip(*data)
        
        # Color by severity
        colors = [self.SEVERITY_COLORS[s] for s in severities]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        bars = ax.barh(regions, coverage_percentages, color=colors, alpha=0.8)
        
        # Add value labels
        for i, (bar, coverage) in enumerate(zip(bars, coverage_percentages)):
            ax.text(
                coverage + 1,
                bar.get_y() + bar.get_height()/2,
                f'{coverage:.1f}%',
                ha='left',
                va='center',
                fontweight='bold'
            )
        
        ax.set_xlabel('Critical Capability Coverage (%)', fontsize=12, fontweight='bold')
        ax.set_title(
            'Healthcare Capability Coverage by Region\nPercentage of Critical Capabilities Available',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.set_xlim(0, 110)
        ax.grid(axis='x', alpha=0.3)
        
        # Add reference line at 50%
        ax.axvline(x=50, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.text(50, len(regions), '50% threshold', ha='center', va='bottom', fontsize=9, color='red')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Region comparison chart saved to: {output_path}")
    
    def create_summary_dashboard(
        self,
        desert_analysis: Dict,
        output_dir: str = 'output'
    ):
        """
        Create comprehensive dashboard with multiple visualizations
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n📊 Generating visualization dashboard...")
        
        # 1. Medical deserts map
        self.plot_medical_deserts_map(
            desert_analysis,
            f'{output_dir}/medical_deserts_map.png'
        )
        
        # 2. Capability coverage
        self.plot_capability_coverage(
            desert_analysis,
            f'{output_dir}/capability_coverage.png'
        )
        
        # 3. Region comparison
        self.plot_region_comparison(
            desert_analysis,
            f'{output_dir}/region_comparison.png'
        )
        
        print(f"\n✅ Dashboard visualizations saved to {output_dir}/")
        print("   - medical_deserts_map.png")
        print("   - capability_coverage.png")
        print("   - region_comparison.png")


if __name__ == "__main__":
    # Test visualization with sample data
    sample_analysis = {
        'total_regions': 3,
        'desert_regions_count': 2,
        'desert_regions': [
            {
                'region': 'Upper East',
                'severity': 'critical',
                'missing_capabilities': ['icu', 'surgery', 'dialysis']
            }
        ],
        'all_regions': [
            {
                'region': 'Greater Accra',
                'severity': 'minimal',
                'coverage_percentage': 88.9
            },
            {
                'region': 'Upper East',
                'severity': 'critical',
                'coverage_percentage': 33.3
            },
            {
                'region': 'Northern',
                'severity': 'severe',
                'coverage_percentage': 44.4
            }
        ],
        'most_common_gaps': [
            ('icu', 2),
            ('dialysis', 2),
            ('surgery', 1)
        ]
    }
    
    visualizer = MedicalDesertVisualizer()
    visualizer.create_summary_dashboard(sample_analysis)
