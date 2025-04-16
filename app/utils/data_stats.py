import pandas as pd
import numpy as np
from scipy import stats
import json

def get_basic_stats(df):
    """
    Generate basic statistics for a DataFrame
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Dictionary of statistics
    """
    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    stats_data = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "column_stats": {}
    }
    
    # Calculate stats for numeric columns
    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            stats_data["column_stats"][col] = {
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "std": float(col_data.std()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "q1": float(col_data.quantile(0.25)),
                "q3": float(col_data.quantile(0.75)),
                "missing": int(df[col].isna().sum()),
                "missing_percent": float(df[col].isna().mean() * 100)
            }
    
    # Calculate stats for categorical columns
    for col in categorical_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            value_counts = col_data.value_counts()
            stats_data["column_stats"][col] = {
                "unique_values": int(len(value_counts)),
                "top_values": value_counts.nlargest(5).to_dict(),
                "missing": int(df[col].isna().sum()),
                "missing_percent": float(df[col].isna().mean() * 100)
            }
    
    return stats_data

def check_correlations(df, threshold=0.5):
    """
    Find correlations between numeric columns
    
    Args:
        df: Pandas DataFrame
        threshold: Correlation coefficient threshold
        
    Returns:
        List of significant correlations
    """
    # Get numeric columns only
    numeric_df = df.select_dtypes(include=['number'])
    
    if len(numeric_df.columns) < 2:
        return []
    
    # Calculate correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Find significant correlations
    correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            corr = corr_matrix.iloc[i, j]
            
            if abs(corr) > threshold:
                correlations.append({
                    "column1": col1,
                    "column2": col2,
                    "correlation": float(corr),
                    "strength": "strong positive" if corr > 0.8 else (
                               "moderate positive" if corr > 0.5 else (
                               "strong negative" if corr < -0.8 else "moderate negative"))
                })
    
    return correlations

def detect_outliers(df, method='zscore', threshold=3):
    """
    Detect outliers in numeric columns
    
    Args:
        df: Pandas DataFrame
        method: 'zscore' or 'iqr'
        threshold: Z-score threshold or IQR multiplier
        
    Returns:
        Dictionary with outlier counts per column
    """
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    outliers = {}
    
    for col in numeric_cols:
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            continue
            
        if method == 'zscore':
            # Z-score method
            z_scores = np.abs(stats.zscore(col_data))
            outlier_mask = z_scores > threshold
            outlier_count = outlier_mask.sum()
        else:
            # IQR method
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - (threshold * iqr)
            upper_bound = q3 + (threshold * iqr)
            outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
            outlier_count = outlier_mask.sum()
        
        if outlier_count > 0:
            outliers[col] = {
                "count": int(outlier_count),
                "percent": float((outlier_count / len(col_data)) * 100)
            }
    
    return outliers

def generate_stats_summary(file_path):
    """
    Generate a comprehensive statistical summary for a CSV file
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Markdown formatted summary text
    """
    try:
        # Load data
        df = pd.read_csv(file_path)
        
        # Generate statistics
        basic_stats = get_basic_stats(df)
        correlations = check_correlations(df) if len(df) > 5 else []
        outliers = detect_outliers(df) if len(df) > 5 else {}
        
        # Create markdown summary
        summary = f"""## Statistical Summary

### Dataset Overview
- **Rows**: {basic_stats['row_count']}
- **Columns**: {basic_stats['column_count']}
- **Numeric Columns**: {', '.join(basic_stats['numeric_columns']) or 'None'}
- **Categorical Columns**: {', '.join(basic_stats['categorical_columns']) or 'None'}

### Column Statistics
"""
        
        # Add numeric column stats
        for col in basic_stats['numeric_columns']:
            if col in basic_stats['column_stats']:
                stats = basic_stats['column_stats'][col]
                summary += f"""
#### {col}
- **Mean**: {stats['mean']:.2f}
- **Median**: {stats['median']:.2f}
- **Standard Deviation**: {stats['std']:.2f}
- **Min**: {stats['min']:.2f}
- **Max**: {stats['max']:.2f}
- **Q1 (25%)**: {stats['q1']:.2f}
- **Q3 (75%)**: {stats['q3']:.2f}
- **Missing Values**: {stats['missing']} ({stats['missing_percent']:.1f}%)
"""
        
        # Add categorical column stats
        for col in basic_stats['categorical_columns']:
            if col in basic_stats['column_stats']:
                stats = basic_stats['column_stats'][col]
                top_values = [f"'{k}': {v}" for k, v in stats['top_values'].items()]
                summary += f"""
#### {col}
- **Unique Values**: {stats['unique_values']}
- **Top Values**: {', '.join(top_values) if top_values else 'None'}
- **Missing Values**: {stats['missing']} ({stats['missing_percent']:.1f}%)
"""
        
        # Add correlations
        if correlations:
            summary += "\n### Significant Correlations\n"
            for corr in correlations:
                summary += f"- **{corr['column1']}** and **{corr['column2']}**: {corr['correlation']:.2f} ({corr['strength']})\n"
        
        # Add outliers
        if outliers:
            summary += "\n### Potential Outliers\n"
            for col, data in outliers.items():
                summary += f"- **{col}**: {data['count']} outliers ({data['percent']:.1f}% of values)\n"
        
        return summary
        
    except Exception as e:
        return f"Error generating statistics: {str(e)}"