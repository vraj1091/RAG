# app/services/chart_generator.py
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import base64
from typing import Dict, Any, List, Optional

class ChartGenerator:
    """Generate matplotlib/seaborn charts and return as base64 images"""
    
    def __init__(self):
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def generate_chart(self, chart_type: str, data: Dict[str, Any]) -> str:
        """Generate chart and return base64 image"""
        
        # Create DataFrame from data
        df = pd.DataFrame(data)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'heatmap':
            self._create_heatmap(df, ax)
        elif chart_type == 'violin':
            self._create_violin(df, ax)
        elif chart_type == 'box':
            self._create_boxplot(df, ax)
        elif chart_type == 'histogram':
            self._create_histogram(df, ax)
        elif chart_type == 'scatter_matrix':
            self._create_scatter_matrix(df)
        elif chart_type == 'correlation':
            self._create_correlation_matrix(df, ax)
        elif chart_type == 'distribution':
            self._create_distribution(df, ax)
        elif chart_type == 'regression':
            self._create_regression(df, ax)
        elif chart_type == 'swarm':
            self._create_swarm(df, ax)
        elif chart_type == 'strip':
            self._create_strip(df, ax)
        else:
            # Fallback to simple bar
            self._create_bar(df, ax)
        
        # Convert to base64
        return self._fig_to_base64(fig)
    
    def _create_heatmap(self, df, ax):
        """Correlation heatmap"""
        corr = df.select_dtypes(include=[np.number]).corr()
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
        ax.set_title('Correlation Heatmap')
    
    def _create_violin(self, df, ax):
        """Violin plot"""
        if len(df.columns) >= 2:
            sns.violinplot(data=df, x=df.columns[0], y=df.columns[1], ax=ax)
            ax.set_title('Violin Plot')
    
    def _create_boxplot(self, df, ax):
        """Box plot"""
        df.select_dtypes(include=[np.number]).plot(kind='box', ax=ax)
        ax.set_title('Box Plot')
    
    def _create_histogram(self, df, ax):
        """Histogram with KDE"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            sns.histplot(data=df, x=numeric_cols[0], kde=True, ax=ax)
            ax.set_title('Distribution Histogram')
    
    def _create_scatter_matrix(self, df):
        """Scatter matrix for multiple variables"""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) >= 2:
            pd.plotting.scatter_matrix(numeric_df, alpha=0.7, figsize=(12, 12))
            plt.suptitle('Scatter Matrix')
    
    def _create_correlation_matrix(self, df, ax):
        """Enhanced correlation matrix"""
        corr = df.select_dtypes(include=[np.number]).corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', 
                   center=0, square=True, linewidths=1, ax=ax)
        ax.set_title('Correlation Matrix')
    
    def _create_distribution(self, df, ax):
        """Distribution plot with multiple series"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:  # Max 3 distributions
            sns.kdeplot(data=df[col], label=col, ax=ax)
        ax.legend()
        ax.set_title('Distribution Plot')
    
    def _create_regression(self, df, ax):
        """Regression plot"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            sns.regplot(data=df, x=numeric_cols[0], y=numeric_cols[1], ax=ax)
            ax.set_title('Regression Plot')
    
    def _create_swarm(self, df, ax):
        """Swarm plot"""
        if len(df.columns) >= 2:
            sns.swarmplot(data=df, x=df.columns[0], y=df.columns[1], ax=ax)
            ax.set_title('Swarm Plot')
    
    def _create_strip(self, df, ax):
        """Strip plot"""
        if len(df.columns) >= 2:
            sns.stripplot(data=df, x=df.columns[0], y=df.columns[1], ax=ax)
            ax.set_title('Strip Plot')
    
    def _create_bar(self, df, ax):
        """Simple bar chart"""
        if len(df.columns) >= 2:
            df.plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax)
            ax.set_title('Bar Chart')
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"

# Global instance
chart_generator = ChartGenerator()
