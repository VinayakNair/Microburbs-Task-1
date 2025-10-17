#!/usr/bin/env python3
"""
Hedonic Residual Score: Australian Property Investment Metric

This script implements an innovative real estate metric for Australian residential property investors.
Hedonic Residual Score (HRS): Measures the difference between actual transaction prices and
statistically predicted hedonic prices to identify undervalued properties and market inefficiencies.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 60)
    print("HEDONIC RESIDUAL SCORE: PROPERTY INVESTMENT METRIC")
    print("=" * 60)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load data
    print("\n1. Loading property transaction data...")
    df = pd.read_parquet('transactions.parquet')

    print(f"   Dataset loaded: {len(df):,} transactions")
    print(f"   Date range: {df['date_sold'].min()} to {df['date_sold'].max()}")
    print(f"   Price range: ${df['price'].min():,} to ${df['price'].max():,}")

    # Clean data
    df_clean = df.dropna(subset=['price', 'hedonic_price'])
    print(f"   Valid transactions for analysis: {len(df_clean):,}")

    # Calculate residuals
    print("\n2. Calculating Hedonic Residual Score...")
    df_clean['hedonic_residual'] = df_clean['price'] - df_clean['hedonic_price']
    df_clean['hedonic_residual_pct'] = (df_clean['hedonic_residual'] / df_clean['hedonic_price']) * 100

    # Summary statistics
    print(f"   Average residual: ${df_clean['hedonic_residual'].mean():,.0f}")
    print(f"   Average residual %: {df_clean['hedonic_residual_pct'].mean():.2f}%")
    print(f"   Correlation (actual vs predicted): {np.corrcoef(df_clean['hedonic_price'], df_clean['price'])[0,1]:.3f}")

    # Identify opportunities
    print("\n3. Identifying Investment Opportunities...")

    undervalued = df_clean[df_clean['hedonic_residual_pct'] < -10]
    overvalued = df_clean[df_clean['hedonic_residual_pct'] > 10]

    print(f"   Undervalued properties (< -10%): {len(undervalued)} ({len(undervalued)/len(df_clean)*100:.1f}%)")
    print(f"   Overvalued properties (> +10%): {len(overvalued)} ({len(overvalued)/len(df_clean)*100:.1f}%)")

    # Calculate investment scores
    def calculate_investment_score(residual_pct):
        if residual_pct < -15:
            return 100  # Strong Buy
        elif residual_pct < -10:
            return 80   # Consider Buy
        elif residual_pct < -5:
            return 60   # Research Further
        elif residual_pct < 0:
            return 40   # Fair Value
        elif residual_pct < 5:
            return 20   # Hold
        else:
            return 0    # Avoid/Sell

    df_clean['investment_score'] = df_clean['hedonic_residual_pct'].apply(calculate_investment_score)

    high_score_opportunities = df_clean[df_clean['investment_score'] >= 60].sort_values('investment_score', ascending=False)
    print(f"   High-score opportunities (≥60): {len(high_score_opportunities)} ({len(high_score_opportunities)/len(df_clean)*100:.1f}%)")

    # Top opportunities
    print("\n4. Top 15 Investment Opportunities:")
    print("-" * 50)
    top_opps = high_score_opportunities.head(15)[
        ['date_sold', 'suburb', 'price', 'hedonic_price', 'hedonic_residual_pct', 'investment_score']
    ]
    print(top_opps.to_string(index=False, float_format='%.1f'))

    # Suburb analysis
    print("\n5. Suburb-Level Analysis:")
    print("-" * 50)
    suburb_analysis = df_clean.groupby('suburb').agg({
        'hedonic_residual_pct': ['mean', 'count'],
        'price': 'median'
    }).round(2)

    suburb_analysis.columns = ['avg_residual_pct', 'transaction_count', 'median_price']
    suburb_analysis = suburb_analysis.sort_values('avg_residual_pct')

    print(suburb_analysis)

    # Create visualizations
    print("\n6. Creating visualizations...")

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 1. Residual distribution
    axes[0,0].hist(df_clean['hedonic_residual_pct'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0,0].axvline(df_clean['hedonic_residual_pct'].mean(), color='red', linestyle='--',
                      linewidth=2, label=f'Mean: {df_clean["hedonic_residual_pct"].mean():.2f}%')
    axes[0,0].set_title('Distribution of Hedonic Residuals (%)')
    axes[0,0].set_xlabel('Residual Percentage (%)')
    axes[0,0].set_ylabel('Frequency')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)

    # 2. Actual vs Predicted
    axes[0,1].scatter(df_clean['hedonic_price'], df_clean['price'], alpha=0.6, s=20)
    axes[0,1].plot([df_clean['hedonic_price'].min(), df_clean['hedonic_price'].max()],
                   [df_clean['hedonic_price'].min(), df_clean['hedonic_price'].max()],
                   'r--', linewidth=2, label='Perfect Prediction')
    axes[0,1].set_title('Actual vs Predicted Prices')
    axes[0,1].set_xlabel('Predicted Price ($)')
    axes[0,1].set_ylabel('Actual Price ($)')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)

    # 3. Investment score distribution
    score_counts = df_clean['investment_score'].value_counts().sort_index()
    score_labels = ['Avoid', 'Hold', 'Fair Value', 'Research', 'Consider Buy', 'Strong Buy']
    axes[1,0].bar(score_counts.index, score_counts.values, alpha=0.7, color='steelblue')
    axes[1,0].set_title('Investment Score Distribution')
    axes[1,0].set_xlabel('Investment Score')
    axes[1,0].set_ylabel('Number of Properties')
    axes[1,0].set_xticks(range(0, 101, 20))
    axes[1,0].grid(True, alpha=0.3)

    # 4. Suburb comparison
    if len(suburb_analysis) > 0:
        colors = ['red' if x < 0 else 'green' for x in suburb_analysis['avg_residual_pct']]
        axes[1,1].bar(range(len(suburb_analysis)), suburb_analysis['avg_residual_pct'], color=colors, alpha=0.7)
        axes[1,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[1,1].set_title('Average Residual by Suburb')
    axes[1,1].set_xlabel('Suburb')
    axes[1,1].set_ylabel('Average Residual (%)')
    axes[1,1].set_xticks(range(len(suburb_analysis)))
    axes[1,1].set_xticklabels(suburb_analysis.index, rotation=45)
    axes[1,1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('hedonic_residual_analysis.png', dpi=300, bbox_inches='tight')
    print("   Visualization saved: hedonic_residual_analysis.png")

    # Export results
    print("\n7. Exporting results...")

    # Investment opportunities
    export_cols = ['date_sold', 'suburb', 'price', 'hedonic_price',
                   'hedonic_residual', 'hedonic_residual_pct', 'investment_score']
    df_clean[export_cols].sort_values('investment_score', ascending=False).to_csv(
        'investment_opportunities.csv', index=False)
    print("   Investment opportunities exported: investment_opportunities.csv")

    # Summary statistics
    summary_stats = {
        'Metric': [
            'Total Transactions Analyzed',
            'Date Range',
            'Average Hedonic Residual',
            'Average Residual Percentage',
            'Correlation (Actual vs Predicted)',
            'Undervalued Properties (< -10%)',
            'Overvalued Properties (> +10%)',
            'High-Value Opportunities (Score ≥ 60)'
        ],
        'Value': [
            f"{len(df_clean):,}",
            f"{df_clean['date_sold'].min()} to {df_clean['date_sold'].max()}",
            f"${df_clean['hedonic_residual'].mean():,.0f}",
            f"{df_clean['hedonic_residual_pct'].mean():.2f}%",
            f"{np.corrcoef(df_clean['hedonic_price'], df_clean['price'])[0,1]:.3f}",
            f"{len(undervalued):,} ({len(undervalued)/len(df_clean)*100:.1f}%)",
            f"{len(overvalued):,} ({len(overvalued)/len(df_clean)*100:.1f}%)",
            f"{len(high_score_opportunities):,} ({len(high_score_opportunities)/len(df_clean)*100:.1f}%)"
        ]
    }

    summary_df = pd.DataFrame(summary_stats)
    summary_df.to_csv('analysis_summary.csv', index=False)
    print("   Summary statistics exported: analysis_summary.csv")

    # Key insights
    print("\n8. KEY INVESTMENT INSIGHTS")
    print("=" * 50)
    print(f"• Market Efficiency: {np.corrcoef(df_clean['hedonic_price'], df_clean['price'])[0,1]:.1%} correlation between predicted and actual prices")
    print(f"• Average Undervaluation: Properties typically sell ${abs(df_clean['hedonic_residual'].mean()):,.0f} below predicted values")
    print(f"• Opportunity Rate: {len(undervalued)/len(df_clean)*100:.1f}% of properties show significant undervaluation")

    if len(suburb_analysis) > 0:
        best_suburb = suburb_analysis['avg_residual_pct'].idxmin()
        print(f"• Best Suburb: {best_suburb} shows most consistent undervaluation ({suburb_analysis.loc[best_suburb, 'avg_residual_pct']:.2f}% on average)")

    print(f"• High-Value Opportunities: {len(high_score_opportunities)} properties with investment scores ≥ 60")

    avg_savings = abs(df_clean[df_clean['investment_score'] >= 60]['hedonic_residual'].mean())
    print(f"• Potential Savings: Average ${avg_savings:,.0f} below predicted value in high-score opportunities")

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE")
    print("=" * 50)

    return df_clean, suburb_analysis, high_score_opportunities

if __name__ == "__main__":
    df, suburbs, opportunities = main()