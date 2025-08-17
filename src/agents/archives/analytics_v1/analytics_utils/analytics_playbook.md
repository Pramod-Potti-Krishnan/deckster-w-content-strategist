{
  "version": "1.1",
  "default_library": "matplotlib",
  "charts": [
    {
      "name": "Line Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Trend over time or ordered x",
        "Up to ~5 series for easy comparison",
        "Show seasonality, spikes, anomalies"
      ],
      "data_requirements": [
        {"role": "x", "type": "time|ordered_category"},
        {"role": "y", "type": "numeric"},
        {"role": "series", "type": "category", "optional": true}
      ],
      "plotting_api": {"function": "plt.plot", "required_params": ["x","y"], "optional_params": ["label","linewidth","marker","linestyle"]},
      "useful_data_points": ["moving_average","event_markers","min_max_points"],
      "synthetic_data_features": {
        "rows": 100,
        "num_series": 1,
        "x_frequency": "daily",
        "y_pattern": "linear_trend|seasonal(sine)+noise",
        "noise_level": "low|medium",
        "anomalies": {"count": 3, "magnitude": "2-3x std"},
        "missing_rate": 0.02
      }
    },
    {
      "name": "Step Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "State changes or inventory levels",
        "Values change at discrete points",
        "Queue size, feature flags, pricing tiers"
      ],
      "data_requirements": [
        {"role": "x", "type": "time|ordered_category"},
        {"role": "y", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.step", "required_params": ["x","y"], "optional_params": ["where","linewidth"]},
      "useful_data_points": ["threshold_lines","last_value"],
      "synthetic_data_features": {
        "rows": 60,
        "x_frequency": "hourly",
        "y_pattern": "piecewise_constant",
        "num_steps": 6,
        "noise_level": "none",
        "missing_rate": 0.0
      }
    },
    {
      "name": "Area Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Single series magnitude over time",
        "Emphasize volume or accumulation",
        "Forecast vs actual (band)"
      ],
      "data_requirements": [
        {"role": "x", "type": "time|ordered_category"},
        {"role": "y", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.fill_between", "required_params": ["x","y1"], "optional_params": ["y2","alpha"]},
      "useful_data_points": ["cumulative_total","min_max_range"],
      "synthetic_data_features": {
        "rows": 80,
        "x_frequency": "weekly",
        "y_pattern": "increasing_trend+seasonal",
        "noise_level": "low",
        "missing_rate": 0.0
      }
    },
    {
      "name": "Stacked Area Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Composition over time (parts-of-whole)",
        "2–5 categories, relative shares matter",
        "Total magnitude also important"
      ],
      "data_requirements": [
        {"role": "x", "type": "time|ordered_category"},
        {"role": "ys", "type": "numeric_list"}
      ],
      "plotting_api": {"function": "plt.stackplot", "required_params": ["x","ys"], "optional_params": ["labels","alpha"]},
      "useful_data_points": ["category_shares","total_line"],
      "synthetic_data_features": {
        "rows": 52,
        "x_frequency": "weekly",
        "num_series": 4,
        "series_pattern": "dirichlet_proportions * total_trend",
        "total_trend": "slow_growth",
        "noise_level": "low",
        "missing_rate": 0.0
      }
    },
    {
      "name": "Bar Chart (Vertical)",
      "renderer": "matplotlib",
      "when_to_use": [
        "Compare categories at a point in time",
        "<= 12 categories, short labels",
        "Rank or top-N comparisons"
      ],
      "data_requirements": [
        {"role": "category", "type": "category"},
        {"role": "value", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.bar", "required_params": ["x","height"], "optional_params": ["width","label"]},
      "useful_data_points": ["sorted_by_value","value_labels"],
      "synthetic_data_features": {
        "num_categories": 8,
        "category_names": "auto",
        "value_distribution": "lognormal|uniform",
        "outliers": {"prob": 0.1, "multiplier": 2.5}
      }
    },
    {
      "name": "Bar Chart (Horizontal)",
      "renderer": "matplotlib",
      "when_to_use": [
        "Long category labels",
        "Many categories (10–30) with scrolling",
        "Ranked comparisons"
      ],
      "data_requirements": [
        {"role": "category", "type": "category"},
        {"role": "value", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.barh", "required_params": ["y","width"], "optional_params": ["height","label"]},
      "useful_data_points": ["top_n_filter","value_labels"],
      "synthetic_data_features": {
        "num_categories": 15,
        "value_distribution": "normal|exponential",
        "sorted": true
      }
    },
    {
      "name": "Grouped Bar Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Compare subcategories within each category",
        "Small number of groups (<= 8) and subgroups (<= 4)",
        "Side-by-side comparisons"
      ],
      "data_requirements": [
        {"role": "category", "type": "category"},
        {"role": "subgroup", "type": "category"},
        {"role": "value", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.bar (offset groups)", "required_params": ["x_positions_per_group","heights"], "optional_params": ["bar_width","labels","legend"]},
      "useful_data_points": ["relative_diff","group_totals"],
      "synthetic_data_features": {
        "num_groups": 6,
        "num_subgroups": 3,
        "value_distribution": "normal",
        "inter_group_variation": "medium",
        "inter_subgroup_variation": "medium"
      }
    },
    {
      "name": "Stacked Bar Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Part-to-whole per category",
        "Show composition and totals together",
        "Prefer <= 8 categories"
      ],
      "data_requirements": [
        {"role": "category", "type": "category"},
        {"role": "segments", "type": "numeric_list"}
      ],
      "plotting_api": {"function": "plt.bar (bottom stacking)", "required_params": ["x","segment_heights"], "optional_params": ["labels","percent_mode"]},
      "useful_data_points": ["segment_shares","category_totals"],
      "synthetic_data_features": {
        "num_categories": 7,
        "num_segments": 4,
        "segment_shares": "dirichlet",
        "total_scale": "uniform(100,500)"
      }
    },
    {
      "name": "Histogram",
      "renderer": "matplotlib",
      "when_to_use": [
        "Distribution of a numeric variable",
        "Detect skewness, multimodality, outliers",
        "Choose bins carefully"
      ],
      "data_requirements": [
        {"role": "values", "type": "numeric_list"}
      ],
      "plotting_api": {"function": "plt.hist", "required_params": ["values"], "optional_params": ["bins","density","range","cumulative"]},
      "useful_data_points": ["bin_edges","mean_median_lines"],
      "synthetic_data_features": {
        "n": 1000,
        "distribution": "normal|lognormal|mixture(2)",
        "outliers": {"prob": 0.02, "multiplier": 4.0},
        "range_override": null
      }
    },
    {
      "name": "Box Plot",
      "renderer": "matplotlib",
      "when_to_use": [
        "Compare spread across groups",
        "Highlight medians and outliers",
        "Robust to skew"
      ],
      "data_requirements": [
        {"role": "values", "type": "numeric_list"},
        {"role": "groups", "type": "category", "optional": true}
      ],
      "plotting_api": {"function": "plt.boxplot", "required_params": ["data"], "optional_params": ["labels","vert","showfliers"]},
      "useful_data_points": ["quartiles","whiskers","outlier_count"],
      "synthetic_data_features": {
        "num_groups": 4,
        "group_sizes": "uniform(80,120)",
        "group_distributions": "normal with varying std",
        "outliers": {"prob": 0.03, "multiplier": 3.5}
      }
    },
    {
      "name": "Violin Plot",
      "renderer": "matplotlib",
      "when_to_use": [
        "Distribution shape across groups",
        "Show multimodality better than box plots",
        "Use when sample sizes are moderate/large"
      ],
      "data_requirements": [
        {"role": "values", "type": "numeric_list"},
        {"role": "groups", "type": "category", "optional": true}
      ],
      "plotting_api": {"function": "plt.violinplot", "required_params": ["dataset"], "optional_params": ["showmeans","showmedians","vert"]},
      "useful_data_points": ["median","iqr","density_peaks"],
      "synthetic_data_features": {
        "num_groups": 3,
        "group_distributions": "mixture normals with different modes",
        "n_per_group": 150
      }
    },
    {
      "name": "Scatter Plot",
      "renderer": "matplotlib",
      "when_to_use": [
        "Relationship between two metrics",
        "Detect correlation, clusters, outliers",
        "Small to medium sample size (<= 5k)"
      ],
      "data_requirements": [
        {"role": "x", "type": "numeric"},
        {"role": "y", "type": "numeric"},
        {"role": "group", "type": "category", "optional": true}
      ],
      "plotting_api": {"function": "plt.scatter", "required_params": ["x","y"], "optional_params": ["s","alpha","label","marker"]},
      "useful_data_points": ["trendline_coeffs","correlation","highlight_outliers"],
      "synthetic_data_features": {
        "n": 400,
        "correlation": 0.6,
        "clusters": 0,
        "outliers": {"count": 6, "offset_std": 4},
        "groups": {"k": 0}
      }
    },
    {
      "name": "Bubble Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "3 variables: x, y, and size as magnitude",
        "Top-N labeling for biggest bubbles",
        "Use alpha to reduce overplotting"
      ],
      "data_requirements": [
        {"role": "x", "type": "numeric"},
        {"role": "y", "type": "numeric"},
        {"role": "size", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.scatter", "required_params": ["x","y","s"], "optional_params": ["alpha","label"]},
      "useful_data_points": ["size_legend","top_n_labels"],
      "synthetic_data_features": {
        "n": 200,
        "x_distribution": "uniform(0,100)",
        "y_distribution": "uniform(0,100)",
        "size_distribution": "gamma(k=2,theta=20)",
        "label_top_n": 10
      }
    },
    {
      "name": "Hexbin",
      "renderer": "matplotlib",
      "when_to_use": [
        "Very dense scatter (>5k points)",
        "2D density patterns",
        "Alternative to scatter for big data"
      ],
      "data_requirements": [
        {"role": "x", "type": "numeric"},
        {"role": "y", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.hexbin", "required_params": ["x","y"], "optional_params": ["gridsize","C","reduce_C_function"]},
      "useful_data_points": ["colorbar","density_peaks"],
      "synthetic_data_features": {
        "n": 20000,
        "clusters": 3,
        "cluster_spread": "different sigmas",
        "background_noise": "low"
      }
    },
    {
      "name": "Heatmap",
      "renderer": "matplotlib",
      "when_to_use": [
        "Magnitude across 2D grid",
        "Category x category or time x category",
        "Spot clusters or high/low bands"
      ],
      "data_requirements": [
        {"role": "matrix", "type": "numeric_2d"},
        {"role": "x_labels", "type": "category|time"},
        {"role": "y_labels", "type": "category"}
      ],
      "plotting_api": {"function": "plt.imshow", "required_params": ["matrix"], "optional_params": ["aspect","interpolation","vmin","vmax"]},
      "useful_data_points": ["colorbar","value_labels","row_col_totals"],
      "synthetic_data_features": {
        "shape": [12, 10],
        "value_distribution": "normal",
        "row_col_structure": "block_clusters(2x2)",
        "missing_rate": 0.03
      }
    },
    {
      "name": "Error Bar Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Show mean with variability",
        "Confidence intervals or std dev around means",
        "Few categories/points for clarity"
      ],
      "data_requirements": [
        {"role": "x", "type": "category|numeric|time"},
        {"role": "y", "type": "numeric"},
        {"role": "yerr", "type": "numeric|tuple_list"}
      ],
      "plotting_api": {"function": "plt.errorbar", "required_params": ["x","y","yerr"], "optional_params": ["fmt","capsize"]},
      "useful_data_points": ["confidence_level","sample_size"],
      "synthetic_data_features": {
        "num_points": 10,
        "means_distribution": "uniform(20,80)",
        "errors_distribution": "uniform(2,10)",
        "confidence_level": 0.95
      }
    },
    {
      "name": "Waterfall",
      "renderer": "matplotlib",
      "when_to_use": [
        "Explain additive/deductive contributions",
        "From start value to end value via stages",
        "Finance, funnel diagnostics"
      ],
      "data_requirements": [
        {"role": "stages", "type": "ordered_category"},
        {"role": "delta_values", "type": "numeric_list"}
      ],
      "plotting_api": {"function": "plt.bar (manual bottoms)", "required_params": ["x","heights","bottoms"], "optional_params": ["color_scheme_for_pos_neg"]},
      "useful_data_points": ["start_value","end_value","running_total_labels"],
      "synthetic_data_features": {
        "num_stages": 8,
        "start_value": 1000,
        "deltas_distribution": "normal(mean=0,sd=150)",
        "balance_bias": "slightly_negative"
      }
    },
    {
      "name": "Pareto",
      "renderer": "matplotlib",
      "when_to_use": [
        "Ranked bars with cumulative line",
        "Identify vital few (80/20)",
        "Defect categories, cause analysis"
      ],
      "data_requirements": [
        {"role": "category", "type": "category"},
        {"role": "value", "type": "numeric"}
      ],
      "plotting_api": {"function": "plt.bar + ax.twinx().plot", "required_params": ["sorted_x","sorted_height","cumulative_percent"], "optional_params": ["reference_line_80"]},
      "useful_data_points": ["top_20_percent_cutoff","cumulative_table"],
      "synthetic_data_features": {
        "num_categories": 12,
        "value_distribution": "power_law",
        "ensure_sorted": true
      }
    },
    {
      "name": "Gantt (Timeline Bars)",
      "renderer": "matplotlib",
      "when_to_use": [
        "Tasks with start and duration",
        "Schedule comparison across teams",
        "Milestones/overlaps"
      ],
      "data_requirements": [
        {"role": "task", "type": "category"},
        {"role": "start", "type": "time"},
        {"role": "duration", "type": "numeric_time_delta"}
      ],
      "plotting_api": {"function": "ax.broken_barh", "required_params": ["xranges","yrange"], "optional_params": ["facecolors"]},
      "useful_data_points": ["milestones","critical_path_highlight"],
      "synthetic_data_features": {
        "num_tasks": 12,
        "start_window_days": 60,
        "duration_distribution": "uniform(3,14) days",
        "overlap_ratio": 0.4,
        "milestone_density": 0.15
      }
    },
    {
      "name": "Radar (Spider) Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Compare entities across 3–10 metrics",
        "Metrics on same scale",
        "Show strengths/weaknesses profiles"
      ],
      "data_requirements": [
        {"role": "metrics", "type": "ordered_category"},
        {"role": "values", "type": "numeric_list"},
        {"role": "entity", "type": "category", "optional": true}
      ],
      "plotting_api": {"function": "polar_axes.plot/fill", "required_params": ["angles","values"], "optional_params": ["fill_alpha","gridlines"]},
      "useful_data_points": ["normalized_scales","target_band"],
      "synthetic_data_features": {
        "num_metrics": 6,
        "num_entities": 3,
        "value_range": [0,100],
        "correlations": "none",
        "normalization": "minmax_0_100"
      }
    },
    {
      "name": "Control Chart",
      "renderer": "matplotlib",
      "when_to_use": [
        "Process stability monitoring over time",
        "Show mean and UCL/LCL",
        "Detect rule violations"
      ],
      "data_requirements": [
        {"role": "time", "type": "time"},
        {"role": "value", "type": "numeric"},
        {"role": "ucl_lcl", "type": "numeric_pair", "optional": true}
      ],
      "plotting_api": {"function": "plt.plot + plt.fill_between", "required_params": ["x","y"], "optional_params": ["mean_line","ucl","lcl"]},
      "useful_data_points": ["violations_count","runs_test"],
      "synthetic_data_features": {
        "rows": 60,
        "x_frequency": "daily",
        "process_mean": 50,
        "process_sd": 4,
        "special_causes": {"count": 4, "offset_sd": 3.5},
        "ucl_lcl_method": "mean±3sd"
      }
    },
    {
      "name": "Funnel (Approximation)",
      "renderer": "matplotlib",
      "when_to_use": [
        "Stage-wise drop-off through pipeline",
        "Highlight conversion rates",
        "Small number of stages (4–8)"
      ],
      "data_requirements": [
        {"role": "stages", "type": "ordered_category"},
        {"role": "counts", "type": "numeric_list"}
      ],
      "plotting_api": {"function": "plt.barh (centered, decreasing widths)", "required_params": ["y","widths"], "optional_params": ["left_offsets","percent_labels"]},
      "useful_data_points": ["stage_conversion_rates","overall_conversion"],
      "synthetic_data_features": {
        "num_stages": 6,
        "start_count": 10000,
        "conversion_pattern": "multiplicative [0.6,0.7,0.8,0.75,0.85]",
        "random_jitter": "low"
      }
    },
    {
      "name": "Pie Chart",
      "renderer": "mermaid",
      "when_to_use": [
        "Single snapshot part-to-whole",
        "Few categories (3–6) with large differences",
        "Percentages must sum to 100%"
      ],
      "data_requirements": [
        {"role": "label", "type": "category"},
        {"role": "value", "type": "numeric (non-negative)"}
      ],
      "plotting_api": {
        "mermaid_type": "pie",
        "syntax_hint": "pie title <Title>\\n\"Label A\" : 40\\n\"Label B\" : 60"
      },
      "useful_data_points": ["percent_labels","sorted_desc","highlight_slice"],
      "synthetic_data_features": {
        "num_slices": 4,
        "values_distribution": "dirichlet scaled to 100",
        "min_slice_percent": 5,
        "enforce_sum_100": true
      }
    }
  ]
}
