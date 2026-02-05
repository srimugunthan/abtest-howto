import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Experiment parameters
n_days = 14
daily_users_per_variant = 12_500_000  # 2.5% of 500M daily traffic
total_users_per_variant = n_days * daily_users_per_variant

# Baseline metrics (Control - Orange Button)
baseline_buy_now_rate = 0.0500  # 5.0%
baseline_purchase_completion = 0.82  # 82% complete after clicking Buy Now
baseline_add_to_cart_rate = 0.15  # 15% add to cart
baseline_bounce_rate = 0.35  # 35% bounce
baseline_aov = 67.50  # Average order value

# Treatment effect (Green Button)
# Simulating a 2.8% relative lift in Buy Now rate
treatment_lift = 0.028  # 2.8% relative improvement
treatment_buy_now_rate = baseline_buy_now_rate * (1 + treatment_lift)

# Generate daily aggregated data
days = []
for day in range(n_days):
    date = datetime(2025, 2, 4) + timedelta(days=day)
    
    # Add day-of-week seasonality
    dow_factor = 1.0
    if date.weekday() >= 5:  # Weekend
        dow_factor = 1.15  # 15% more traffic on weekends
    
    # Control group
    control_views = int(daily_users_per_variant * dow_factor)
    control_buy_now_clicks = np.random.binomial(control_views, baseline_buy_now_rate)
    control_purchases = np.random.binomial(control_buy_now_clicks, baseline_purchase_completion)
    control_add_to_cart = np.random.binomial(control_views, baseline_add_to_cart_rate)
    control_bounces = np.random.binomial(control_views, baseline_bounce_rate)
    control_revenue = control_purchases * np.random.gamma(shape=4, scale=baseline_aov/4)
    
    # Treatment group (with learning effect - novelty wears off first 3 days)
    novelty_penalty = max(0, (3 - day) * 0.015)  # -1.5% per day for first 3 days
    actual_treatment_rate = treatment_buy_now_rate * (1 - novelty_penalty)
    
    treatment_views = int(daily_users_per_variant * dow_factor)
    treatment_buy_now_clicks = np.random.binomial(treatment_views, actual_treatment_rate)
    treatment_purchases = np.random.binomial(treatment_buy_now_clicks, baseline_purchase_completion)
    treatment_add_to_cart = np.random.binomial(treatment_views, baseline_add_to_cart_rate * 0.98)  # Slight cannibalization
    treatment_bounces = np.random.binomial(treatment_views, baseline_bounce_rate * 0.97)  # Slight improvement
    treatment_revenue = treatment_purchases * np.random.gamma(shape=4, scale=baseline_aov/4)
    
    days.append({
        'date': date,
        'day_number': day + 1,
        'day_of_week': date.strftime('%A'),
        'control_views': control_views,
        'control_buy_now_clicks': control_buy_now_clicks,
        'control_purchases': control_purchases,
        'control_add_to_cart': control_add_to_cart,
        'control_bounces': control_bounces,
        'control_revenue': control_revenue,
        'treatment_views': treatment_views,
        'treatment_buy_now_clicks': treatment_buy_now_clicks,
        'treatment_purchases': treatment_purchases,
        'treatment_add_to_cart': treatment_add_to_cart,
        'treatment_bounces': treatment_bounces,
        'treatment_revenue': treatment_revenue
    })

df_daily = pd.DataFrame(days)

# Calculate daily rates
df_daily['control_buy_now_rate'] = df_daily['control_buy_now_clicks'] / df_daily['control_views']
df_daily['treatment_buy_now_rate'] = df_daily['treatment_buy_now_clicks'] / df_daily['treatment_views']
df_daily['control_conversion_rate'] = df_daily['control_purchases'] / df_daily['control_views']
df_daily['treatment_conversion_rate'] = df_daily['treatment_purchases'] / df_daily['treatment_views']

print("=" * 80)
print("DAILY EXPERIMENT DATA")
print("=" * 80)
print(df_daily[['day_number', 'day_of_week', 'control_buy_now_rate', 
                'treatment_buy_now_rate', 'control_conversion_rate', 
                'treatment_conversion_rate']].to_string(index=False))
print("\n")